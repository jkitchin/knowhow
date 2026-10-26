"""Install skills (and commands, hooks, subagents, MCP servers) from any source.

Skills follow `npx skills` conventions (layout, install paths, lock files).
Commands, hooks, subagents and MCP servers follow skillin / Claude Code
conventions and are installed for Claude Code.

    skillin add owner/repo --skill name
    skillin add owner/repo --command review --subagent code-reviewer
    skillin add owner/repo --hook black-on-save --mcp github
    skillin add ./my-skills --list
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

import click
from rich.console import Console
from rich.markup import escape
from rich.syntax import Syntax
from rich.table import Table

from skillin.agents_registry import AGENTS, build_registry, default_agents, resolve_agent_names
from skillin.config import Config
from skillin.discovery import DiscoveredSkill, discover_skills, install_dir_name
from skillin.extras import (
    LOCK_KEYS,
    Extra,
    ExtraError,
    claude_dir,
    discover_extras,
    install_extra,
    preview,
    target_path,
    uninstall_extra,
)
from skillin.fetch import FetchError, fetch_source, git_tree_hash, github_tree
from skillin.installer import (
    copy_skill_tree,
    find_installed,
    install_skill,
    planned_paths,
    uninstall_skill,
)
from skillin.lock import (
    compute_folder_hash,
    portable_local_source,
    read_extras_lock,
    read_lock,
    record_extra,
    record_install,
    remove_entry,
    remove_extra,
    resolve_local_source,
)
from skillin.sources import Source, SourceError, parse_source

console = Console()

EXTRA_LABELS = {"command": "Command", "subagent": "Subagent", "hook": "Hook", "mcp": "MCP server"}


def _split_names(values: tuple[str, ...]) -> list[str]:
    """Accept `-s a -s b` and `-s a,b`."""
    names = []
    for v in values:
        names.extend(n.strip() for n in v.split(",") if n.strip())
    return names


def _match_skills(skills: list[DiscoveredSkill], names: list[str]) -> list[DiscoveredSkill]:
    if "*" in names:
        return skills
    by_key = {}
    for s in skills:
        for key in (s.name.lower(), install_dir_name(s.name), s.path.name.lower()):
            by_key.setdefault(key, s)
    selected, missing = [], []
    for n in names:
        s = by_key.get(n.lower())
        if s is None:
            missing.append(n)
        elif s not in selected:
            selected.append(s)
    if missing:
        available = ", ".join(s.name for s in skills) or "(none)"
        raise click.ClickException(
            f"Skill(s) not found: {', '.join(missing)}\nAvailable: {available}"
        )
    return selected


def _match_extras(kind: str, extras: list[Extra], names: list[str]) -> list[Extra]:
    if "*" in names:
        if kind in ("hook", "mcp"):
            raise click.ClickException(f"Name {kind}s explicitly; '*' is not allowed for them")
        return extras
    by_name = {e.name.lower(): e for e in extras}
    missing = [n for n in names if n.lower() not in by_name]
    if missing:
        available = ", ".join(e.name for e in extras) or "(none)"
        raise click.ClickException(
            f"{EXTRA_LABELS[kind]}(s) not found: {', '.join(missing)}\nAvailable: {available}"
        )
    selected = []
    for n in names:
        if by_name[n.lower()] not in selected:
            selected.append(by_name[n.lower()])
    return selected


def _truncate(text: str, n: int = 90) -> str:
    return text if len(text) <= n else text[: n - 3] + "..."


def _print_listing(skills, extras, source: Source, kinds=None) -> None:
    table = Table(title=f"Contents of {escape(source.lock_source)}")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Path", style="yellow")
    table.add_column("Description")
    if kinds is None or "skill" in kinds:
        for s in skills:
            table.add_row(
                "skill", escape(s.name), escape(s.rel_path or "."), escape(_truncate(s.description))
            )
    for kind, items in extras.items():
        if kinds is not None and kind not in kinds:
            continue
        for e in items:
            table.add_row(
                kind, escape(e.name), escape(e.rel_path), escape(_truncate(e.description))
            )
    console.print(table)


def _prompt_selection(skills: list[DiscoveredSkill]) -> list[DiscoveredSkill]:
    for i, s in enumerate(skills, 1):
        console.print(f"  [cyan]{i:3d}[/cyan]  {escape(s.name)}")
    answer = click.prompt("Select skills (numbers or names, comma-separated, or 'all')")
    if answer.strip().lower() in ("all", "*"):
        return skills
    picks = []
    for token in (t.strip() for t in answer.split(",") if t.strip()):
        if token.isdigit() and 1 <= int(token) <= len(skills):
            picks.append(skills[int(token) - 1].name)
        else:
            picks.append(token)
    return _match_skills(skills, picks)


def _hash_for(skill_dir: Path, rel_dir: str, checkout, global_: bool) -> str:
    """npx stores the git tree SHA globally and a content SHA-256 for projects."""
    if global_ and checkout.is_git:
        tree = git_tree_hash(checkout.root, rel_dir)
        if tree:
            return tree
    return compute_folder_hash(skill_dir)


def _lock_source(source: Source, global_: bool, cwd: Path) -> str:
    if source.is_local and not global_:
        return portable_local_source(source.url, cwd)
    return source.lock_source


def _lock_entry(source: Source, skill: DiscoveredSkill, checkout, global_: bool, cwd: Path):
    h = _hash_for(skill.path, skill.rel_path, checkout, global_)
    if global_:
        return {
            "source": source.lock_source,
            "sourceType": source.type,
            "sourceUrl": source.url,
            "ref": source.ref,
            "skillPath": skill.skill_md_path,
            "skillFolderHash": h,
            "pluginName": skill.plugin_name,
        }
    return {
        "source": _lock_source(source, global_, cwd),
        "sourceUrl": source.url if source.type in ("git", "gitlab") else None,
        "ref": source.ref,
        "sourceType": source.type,
        "skillPath": None if source.is_local else skill.skill_md_path,
        "computedHash": h,
    }


def _extra_entry(source: Source, extra: Extra, global_: bool, cwd: Path) -> dict:
    return {
        "source": _lock_source(source, global_, cwd),
        "sourceType": source.type,
        "sourceUrl": None if source.is_local else source.url,
        "ref": source.ref,
        "path": extra.rel_path,
        "hash": extra.content_hash(),
    }


def _confirm_code(extra: Extra, yes: bool) -> None:
    """Show what a hook / MCP server will run and require confirmation."""
    if extra.kind not in ("hook", "mcp"):
        return
    console.print(
        f"\n[bold yellow]⚠ {EXTRA_LABELS[extra.kind]} '{escape(extra.name)}' runs code "
        "with your user privileges. Review it:[/bold yellow]"
    )
    lexer = "json" if extra.kind == "mcp" else "text"
    console.print(Syntax(preview(extra), lexer, word_wrap=True))
    if yes:
        return
    if not sys.stdin.isatty():
        raise click.ClickException(f"Refusing to install {extra.kind} non-interactively without -y")
    if not click.confirm(f"Install {extra.kind} '{extra.name}'?", default=False):
        raise click.Abort()


@click.command()
@click.argument("source")
@click.option("--skill", "-s", "skill_names", multiple=True, help="Skill(s) to install ('*' = all)")
@click.option("--command", "command_names", multiple=True, help="Slash command(s) ('*' = all)")
@click.option("--subagent", "subagent_names", multiple=True, help="Subagent(s) ('*' = all)")
@click.option("--hook", "hook_names", multiple=True, help="Hook(s) to install (by name)")
@click.option("--mcp", "mcp_names", multiple=True, help="MCP server(s) to install (by name)")
@click.option(
    "--agent",
    "-a",
    "agent_names",
    multiple=True,
    help=f"Agent(s) to install skills for ('*' = all). Built in: {', '.join(AGENTS)}, "
    "plus platforms defined in config.yaml. Default: `default_platform`, else detected agents",
)
@click.option("--global", "-g", "global_", is_flag=True, help="Install for the user, not project")
@click.option("--list", "-l", "list_only", is_flag=True, help="List the source's contents and exit")
@click.option("--all", "all_skills", is_flag=True, help="Install every skill without prompting")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
@click.option("--copy", is_flag=True, help="Copy skills into each agent dir instead of symlinking")
@click.option("--full-depth", is_flag=True, help="Search all subdirectories for skills")
@click.option("--dry-run", is_flag=True, help="Show what would be installed")
def add(
    source,
    skill_names,
    command_names,
    subagent_names,
    hook_names,
    mcp_names,
    agent_names,
    global_,
    list_only,
    all_skills,
    yes,
    copy,
    full_depth,
    dry_run,
):
    """
    Install skills and other items from a git repository or local directory.

    SOURCE may be owner/repo (GitHub), owner/repo/sub/path, owner/repo@skill,
    a GitHub/GitLab URL (optionally with /tree/<ref>/<path>), any git URL,
    a local path, or an alias from `skillin config set alias.NAME SOURCE`.

    Skills install for the detected agents (or --agent). Commands, subagents,
    hooks and MCP servers install for Claude Code. --all selects skills only;
    hooks and MCP servers must be named and are shown for review first.

    \b
    Examples:
      uvx skillin add jkitchin/skillz --skill fairchem
      skillin add jkitchin/skillz --list
      skillin add jkitchin/skillz -s pycse -s python-plotting -g -y
      skillin add jkitchin/skillz --command commit --subagent code-reviewer
      skillin add jkitchin/skillz --hook black-on-save
    """
    try:
        config = Config()
        src = parse_source(source, config.get_aliases())
    except SourceError as e:
        raise click.ClickException(str(e)) from e

    names = _split_names(skill_names)
    if src.skill_filter:
        names.append(src.skill_filter)
    extra_names = {
        "command": _split_names(command_names),
        "subagent": _split_names(subagent_names),
        "hook": _split_names(hook_names),
        "mcp": _split_names(mcp_names),
    }
    wants_extras = any(extra_names.values())
    if all_skills:
        names = ["*"]

    try:
        registry = build_registry(config)
        agents = (
            resolve_agent_names(agent_names, registry)
            if agent_names
            else default_agents(config, registry)
        )
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    cwd = Path.cwd()
    scope = "global" if global_ else f"project ({cwd})"
    console.print(f"Fetching [bold]{escape(src.lock_source)}[/bold]...")

    try:
        with fetch_source(src) as checkout:
            warnings: list[str] = []
            skills = discover_skills(
                checkout.root,
                src.subpath,
                full_depth=full_depth,
                include_internal=bool(names) and "*" not in names,
                warnings=warnings,
            )
            extras = discover_extras(checkout.root, src.subpath, warnings)
            for w in warnings:
                console.print(f"[yellow]Warning: {escape(w)}[/yellow]")

            if list_only:
                if not skills and not any(extras.values()):
                    raise click.ClickException("Nothing installable found")
                _print_listing(skills, extras, src)
                return

            # Choose skills
            if names:
                selected = _match_skills(skills, names)
            elif wants_extras:
                selected = []
            elif not skills:
                raise click.ClickException("No skills (SKILL.md with name/description) found")
            elif len(skills) == 1:
                selected = skills
            elif sys.stdin.isatty() and not yes:
                _print_listing(skills, {}, src)
                selected = _prompt_selection(skills)
            else:
                _print_listing(skills, {}, src)
                raise click.ClickException("Multiple skills found; choose with --skill or --all")

            chosen_extras = [
                e
                for kind, wanted in extra_names.items()
                if wanted
                for e in _match_extras(kind, extras[kind], wanted)
            ]

            # Plan
            if selected:
                console.print(
                    f"Installing {len(selected)} skill(s) to {scope} for: "
                    f"{', '.join(registry[a].display_name for a in agents)}"
                )
            for s in selected:
                canon, targets, _ = planned_paths(s, agents, global_, copy, cwd, registry)
                where = [str(p) for p in ([canon] if canon else []) + targets]
                console.print(f"  [green]{escape(s.name)}[/green] -> {escape(', '.join(where))}")
            for e in chosen_extras:
                dest = target_path(e, global_, cwd)
                where = "claude mcp (user scope)" if e.kind == "mcp" and global_ else str(dest)
                console.print(f"  [green]{e.kind} {escape(e.name)}[/green] -> {escape(where)}")

            if dry_run:
                console.print("[yellow]Dry run - nothing installed[/yellow]")
                return
            for e in chosen_extras:
                _confirm_code(e, yes)
            if not yes and sys.stdin.isatty() and not click.confirm("Proceed?", default=True):
                raise click.Abort()

            for s in selected:
                install_skill(
                    s, agents, checkout.root, global_=global_, copy=copy, cwd=cwd, registry=registry
                )
                record_install(s.name, _lock_entry(src, s, checkout, global_, cwd), global_, cwd)
            for e in chosen_extras:
                install_extra(e, checkout.root, global_, cwd)
                record_extra(
                    LOCK_KEYS[e.kind],
                    e.name,
                    _extra_entry(src, e, global_, cwd),
                    claude_dir(global_, cwd),
                )
            total = len(selected) + len(chosen_extras)
            console.print(f"[green]✓ Installed {total} item(s)[/green]")
    except FetchError as e:
        raise click.ClickException(f"Could not fetch {src.lock_source}: {e}") from e
    except ExtraError as e:
        raise click.ClickException(str(e)) from e


@click.command()
@click.argument("names", nargs=-1)
@click.option("--command", "command_names", multiple=True, help="Slash command(s) to remove")
@click.option("--subagent", "subagent_names", multiple=True, help="Subagent(s) to remove")
@click.option("--hook", "hook_names", multiple=True, help="Hook(s) to remove")
@click.option("--mcp", "mcp_names", multiple=True, help="MCP server(s) to remove")
@click.option("--global", "-g", "global_", is_flag=True, help="Remove global installs")
@click.option("--agent", "-a", "agent_names", multiple=True, help="Only remove for these agents")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def remove(names, command_names, subagent_names, hook_names, mcp_names, global_, agent_names, yes):
    """
    Remove installed items.

    NAMES are skill names, or a source (e.g. owner/repo) to remove every skill,
    command, subagent, hook and MCP server installed from it.

    \b
    Examples:
      skillin remove fairchem
      skillin remove --command commit --hook black-on-save
      skillin remove jkitchin/skillz -g
    """
    cwd = Path.cwd()
    cdir = claude_dir(global_, cwd)
    lock = read_lock(global_, cwd)
    extras_lock = read_extras_lock(cdir)

    def matches_source(entry, n):
        src = entry.get("source")
        if src == n:
            return True
        return entry.get("sourceType") == "local" and resolve_local_source(src or "", cwd) == str(
            Path(n).expanduser().resolve()
        )

    skill_targets = []
    extra_targets = [
        (kind, n)
        for kind, values in (
            ("command", command_names),
            ("subagent", subagent_names),
            ("hook", hook_names),
            ("mcp", mcp_names),
        )
        for n in _split_names(values)
    ]
    for n in names:
        from_source = [k for k, v in lock["skills"].items() if matches_source(v, n)]
        extras_from_source = [
            (kind, k)
            for kind, key in LOCK_KEYS.items()
            for k, v in extras_lock[key].items()
            if matches_source(v, n)
        ]
        if from_source or extras_from_source:
            skill_targets.extend(from_source)
            extra_targets.extend(extras_from_source)
        else:
            skill_targets.append(n)

    if not skill_targets and not extra_targets:
        raise click.UsageError("Give skill names, a source, or --command/--subagent/--hook/--mcp")

    try:
        registry = build_registry(Config())
        agents = resolve_agent_names(agent_names, registry) if agent_names else None
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    labels = skill_targets + [f"{k} {n}" for k, n in extra_targets]
    if not yes and sys.stdin.isatty():
        if not click.confirm(f"Remove {', '.join(labels)}?", default=False):
            raise click.Abort()

    for name in skill_targets:
        removed = uninstall_skill(name, global_, agents, cwd, registry)
        if not agents or set(agents) >= set(AGENTS):
            remove_entry(name, global_, cwd)
        if removed:
            console.print(f"[green]✓ Removed {escape(name)}[/green] ({len(removed)} path(s))")
        else:
            console.print(f"[yellow]{escape(name)} is not installed here[/yellow]")

    for kind, name in extra_targets:
        try:
            removed = uninstall_extra(kind, name, global_, cwd)
        except ExtraError as e:
            raise click.ClickException(str(e)) from e
        remove_extra(LOCK_KEYS[kind], name, cdir)
        if removed:
            console.print(f"[green]✓ Removed {kind} {escape(name)}[/green]")
        else:
            console.print(f"[yellow]{kind} {escape(name)} is not installed here[/yellow]")


# --- check / upgrade ---------------------------------------------------------


def _entry_source(entry: dict, lock_dir: Path) -> Source:
    """Rebuild the Source a lock entry was installed from."""
    if entry.get("sourceType") == "local":
        return Source(type="local", url=resolve_local_source(entry["source"], lock_dir))
    url = entry.get("sourceUrl")
    src = parse_source(url) if url else parse_source(entry["source"])
    src.ref = entry.get("ref") or src.ref
    if entry.get("sourceType") == "github" and "/" in str(entry.get("source")):
        src.owner_repo = entry["source"]
    return src


def _collect_items(global_: bool, cwd: Path, only: tuple[str, ...]) -> list[tuple]:
    """(kind, name, entry) for everything recorded in this scope's lock files."""
    items = [
        ("skill", n, e)
        for n, e in read_lock(global_, cwd)["skills"].items()
        if not only or n in only
    ]
    extras_lock = read_extras_lock(claude_dir(global_, cwd))
    for kind, key in LOCK_KEYS.items():
        items += [(kind, n, e) for n, e in extras_lock[key].items() if not only or n in only]
    return items


def _fast_github_status(items, src: Source) -> dict | None:
    """Status per skill from the GitHub Trees API, or None if unavailable."""
    if src.type != "github" or not src.owner_repo:
        return None
    if any(k != "skill" or len(e.get("skillFolderHash") or "") != 40 for k, _, e in items):
        return None
    tree = github_tree(src.owner_repo, src.ref)
    if tree is None:
        return None
    status = {}
    for _, name, e in items:
        rel = Path(e.get("skillPath") or "SKILL.md").parent.as_posix()
        current = tree.get("" if rel == "." else rel)
        if current is None:
            status[name] = "missing upstream"
        else:
            status[name] = "up to date" if current == e["skillFolderHash"] else "update available"
    return status


def _check_scope(global_: bool, apply: bool, only: tuple[str, ...], yes: bool):
    cwd = Path.cwd()
    lock_dir = cwd  # project lock files live in the project root
    cdir = claude_dir(global_, cwd)
    groups = defaultdict(list)
    for kind, name, e in _collect_items(global_, cwd, only):
        key = (e.get("source"), e.get("sourceType"), e.get("sourceUrl"), e.get("ref"))
        groups[key].append((kind, name, e))

    results = []
    for items in groups.values():
        try:
            src = _entry_source(items[0][2], lock_dir)
        except SourceError as e:
            results += [(k, n, f"error: {e}") for k, n, _ in items]
            continue

        fast = _fast_github_status(items, src) if global_ else None
        if fast is not None and (not apply or all(s == "up to date" for s in fast.values())):
            results += [(k, n, fast[n]) for k, n, _ in items]
            continue

        try:
            with fetch_source(src) as checkout:
                skills = {s.name: s for s in discover_skills(checkout.root, full_depth=True)}
                extras = discover_extras(checkout.root)
                for kind, name, entry in items:
                    if kind == "skill":
                        status = _check_skill(
                            name, entry, skills, src, checkout, global_, apply, cwd
                        )
                    else:
                        status = _check_extra(
                            kind, name, entry, extras, src, checkout, global_, apply, yes, cwd, cdir
                        )
                    results.append((kind, name, status))
        except FetchError as e:
            results += [(k, n, f"fetch failed: {e}") for k, n, _ in items]
    return results


def _check_skill(name, entry, skills, src, checkout, global_, apply, cwd) -> str:
    stored = entry.get("skillFolderHash") if global_ else entry.get("computedHash")
    skill = skills.get(name)
    if skill is None and entry.get("skillPath"):
        rel = Path(entry["skillPath"]).parent.as_posix()
        rel = "" if rel == "." else rel
        skill = next((s for s in skills.values() if s.rel_path == rel), None)
    if skill is None:
        return "missing upstream"
    current = _hash_for(skill.path, skill.rel_path, checkout, global_)
    if not stored:
        return "unknown (no hash recorded)"
    if stored == current:
        return "up to date"
    if not apply:
        return "update available"
    config = Config()
    registry = build_registry(config)
    installed = find_installed(name, global_, cwd, registry)
    for path in installed:
        if not path.is_symlink():
            copy_skill_tree(skill.path, path, checkout.root)
    if not installed:
        install_skill(
            skill,
            default_agents(config, registry),
            checkout.root,
            global_,
            cwd=cwd,
            registry=registry,
        )
    record_install(name, _lock_entry(src, skill, checkout, global_, cwd), global_, cwd)
    return "updated"


def _check_extra(kind, name, entry, extras, src, checkout, global_, apply, yes, cwd, cdir) -> str:
    extra = next((e for e in extras[kind] if e.name == name), None)
    if extra is None:
        return "missing upstream"
    if entry.get("hash") == extra.content_hash():
        return "up to date"
    if not apply:
        return "update available"
    try:
        _confirm_code(extra, yes)
    except click.Abort:
        return "skipped"
    try:
        install_extra(extra, checkout.root, global_, cwd)
    except ExtraError as e:
        return f"error: {e}"
    record_extra(LOCK_KEYS[kind], name, _extra_entry(src, extra, global_, cwd), cdir)
    return "updated"


def _run_check(names, global_, project, apply, yes=False):
    scopes = [True] if global_ else [False] if project else [False, True]
    table = Table(title="Updates" if apply else "Status")
    table.add_column("Scope", style="cyan")
    table.add_column("Type")
    table.add_column("Name", style="green")
    table.add_column("Status")
    colors = {"up to date": "green", "updated": "green", "update available": "yellow"}
    rows = 0
    for g in scopes:
        for kind, name, status in _check_scope(g, apply, names, yes):
            table.add_row(
                "global" if g else "project",
                kind,
                escape(name),
                f"[{colors.get(status, 'red')}]{escape(status)}[/]",
            )
            rows += 1
    if rows:
        console.print(table)
    else:
        console.print("[yellow]Nothing recorded in lock files[/yellow]")


@click.command()
@click.argument("names", nargs=-1)
@click.option("--global", "-g", "global_", is_flag=True, help="Only global installs")
@click.option("--project", "-p", is_flag=True, help="Only project installs")
def check(names, global_, project):
    """Check installed items for upstream changes (no changes made)."""
    _run_check(names, global_, project, apply=False)


@click.command()
@click.argument("names", nargs=-1)
@click.option("--global", "-g", "global_", is_flag=True, help="Only global installs")
@click.option("--project", "-p", is_flag=True, help="Only project installs")
@click.option("--yes", "-y", is_flag=True, help="Don't ask before updating hooks/MCP servers")
def upgrade(names, global_, project, yes):
    """Update installed items to their latest upstream version."""
    _run_check(names, global_, project, apply=True, yes=yes)


# --- find --------------------------------------------------------------------

SKILLS_API = "https://skills.sh"


def _get_json(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers={"User-Agent": "skillin", **(headers or {})})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read(5 * 1024 * 1024))


def _search_skills_sh(query: str, owner: str | None, limit: int) -> list[dict] | None:
    base = os.environ.get("SKILLS_API_URL", SKILLS_API).rstrip("/")
    params = {"q": query, "limit": str(limit)}
    if owner:
        params["owner"] = owner
    try:
        data = _get_json(f"{base}/api/search?{urllib.parse.urlencode(params)}")
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("skills"), list):
        return None
    results = [s for s in data["skills"] if isinstance(s, dict)]
    return sorted(results, key=lambda s: -(s.get("installs") or 0))


def _search_github(query: str, owner: str | None, limit: int) -> list[dict] | None:
    q = f"{query} topic:agent-skills" + (f" user:{owner}" if owner else "")
    params = urllib.parse.urlencode({"q": q, "sort": "stars", "per_page": str(limit)})
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        data = _get_json(f"https://api.github.com/search/repositories?{params}", headers)
    except (OSError, ValueError):
        return None
    return data.get("items") if isinstance(data, dict) else None


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--owner", help="Only results from this GitHub owner")
@click.option(
    "--github", "use_github", is_flag=True, help="Search GitHub repos (topic:agent-skills)"
)
@click.option("--limit", default=15, show_default=True, help="Maximum results")
def find(query, owner, use_github, limit):
    """
    Search for skills to install.

    Searches the skills.sh index (the same one `npx skills find` uses), falling
    back to GitHub repositories tagged `agent-skills`.
    """
    from skillin.discovery import sanitize_text

    q = " ".join(query)
    results = None if use_github else _search_skills_sh(q, owner, limit)
    if results:
        table = Table(title=f"skills.sh results for '{escape(q)}'")
        table.add_column("Skill", style="green")
        table.add_column("Source", style="yellow")
        table.add_column("Installs", justify="right")
        table.add_column("Install with")
        for s in results[:limit]:
            name, source = (
                sanitize_text(str(s.get("name", ""))),
                sanitize_text(str(s.get("source", ""))),
            )
            table.add_row(
                escape(name),
                escape(source),
                str(s.get("installs") or ""),
                escape(f"skillin add {source}@{name}"),
            )
        console.print(table)
        return

    repos = _search_github(q, owner, limit)
    if repos is None:
        raise click.ClickException("Search failed (skills.sh and GitHub unreachable)")
    if not repos:
        console.print(f"[yellow]No results for '{escape(q)}'[/yellow]")
        return
    table = Table(title=f"GitHub repos tagged agent-skills matching '{escape(q)}'")
    table.add_column("Repository", style="green")
    table.add_column("★", justify="right")
    table.add_column("Description")
    for r in repos[:limit]:
        table.add_row(
            escape(sanitize_text(str(r.get("full_name", "")))),
            str(r.get("stargazers_count", "")),
            escape(_truncate(sanitize_text(str(r.get("description") or "")), 70)),
        )
    console.print(table)
    console.print("[dim]List a repo's contents with: skillin add <repo> --list[/dim]")
