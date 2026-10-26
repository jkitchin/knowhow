"""Install skills (and commands, hooks, subagents, MCP servers) from any source.

Skills follow `npx skills` conventions (layout, install paths, lock files).
Commands, hooks and subagents follow knowhow / Claude Code conventions and are
installed for Claude Code. MCP servers are installed into each selected agent's
own config (see mcp_targets.py).

    knowhow add owner/repo --skill name
    knowhow add owner/repo --command review --subagent code-reviewer
    knowhow add owner/repo --hook black-on-save --mcp github
    knowhow add ./my-skills --list
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

from knowhow import mcp_targets
from knowhow.agents_registry import AGENTS, build_registry, default_agents, resolve_agent_names
from knowhow.config import Config
from knowhow.discovery import DiscoveredSkill, discover_skills, install_dir_name
from knowhow.extras import (
    LOCK_KEYS,
    Extra,
    ExtraError,
    claude_dir,
    discover_extras,
    extra_exists,
    install_extra,
    install_mcp,
    mcp_placements_for,
    preview,
    target_path,
    uninstall_extra,
    uninstall_mcp,
)
from knowhow.fetch import FetchError, fetch_source, git_tree_hash, github_tree
from knowhow.installer import (
    _skip_project_agent,
    copy_skill_tree,
    find_installed,
    install_conflicts,
    install_skill,
    planned_paths,
    uninstall_skill,
)
from knowhow.lock import (
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
from knowhow.safeio import ConfigFileError, safe, strip_controls
from knowhow.sources import Source, SourceError, parse_source

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
                "skill", safe(s.name), safe(s.rel_path or "."), safe(_truncate(s.description))
            )
    for kind, items in extras.items():
        if kinds is not None and kind not in kinds:
            continue
        for e in items:
            table.add_row(kind, safe(e.name), safe(e.rel_path), safe(_truncate(e.description)))
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


def _extra_entry(
    source: Source, extra: Extra, global_: bool, cwd: Path, placements: list | None = None
) -> dict:
    entry = {
        "source": _lock_source(source, global_, cwd),
        "sourceType": source.type,
        "sourceUrl": None if source.is_local else source.url,
        "ref": source.ref,
        "path": extra.rel_path,
        "hash": extra.content_hash(),
    }
    if placements is not None:  # MCP: every agent config the server was written to
        entry["targets"] = [mcp_targets.to_record(p) for p in placements]
    return entry


def _report_mcp_failures(name: str, failed: list) -> None:
    for p, err, snippet in failed:
        console.print(
            f"[yellow]MCP {safe(name)}: skipped {p.target.display} ({safe(p.label)}): "
            f"{safe(err)}[/yellow]"
        )
        console.print("[dim]Add this by hand if you want it there:[/dim]")
        console.print(Syntax(strip_controls(snippet), "toml" if p.target.fmt == "toml" else "json"))


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


def _is_managed_skill(name: str, lock: dict) -> bool:
    """True if a skill with this name (or install dir name) is in the lock file."""
    key = install_dir_name(name)
    return any(n == name or install_dir_name(n) == key for n in lock.get("skills", {}))


def _add_conflicts(skills, extras, agents, global_, copy, cwd, registry, mcp_places) -> list[str]:
    """Human-readable descriptions of unmanaged things an install would replace."""
    lock = read_lock(global_, cwd)
    extras_lock = read_extras_lock(claude_dir(global_, cwd))
    out = []
    for s in skills:
        for path in install_conflicts(
            s, agents, global_, copy, cwd, _is_managed_skill(s.name, lock), registry
        ):
            out.append(f"skill {s.name}: {path}")
    for e in extras:
        if e.name in extras_lock[LOCK_KEYS[e.kind]]:
            continue
        if e.kind == "mcp":
            for p in mcp_places.get(e.name, []):
                if mcp_targets.exists(p, e.name):
                    out.append(f"mcp {e.name}: {p.label}")
        elif extra_exists(e, global_, cwd):
            out.append(f"{e.kind} {e.name}: {target_path(e, global_, cwd)}")
    return out


@click.command()
@click.argument("source")
@click.option("--skill", "-s", "skill_names", multiple=True, help="Skill(s) to install ('*' = all)")
@click.option("--command", "command_names", multiple=True, help="Slash command(s) ('*' = all)")
@click.option("--subagent", "subagent_names", multiple=True, help="Subagent(s) ('*' = all)")
@click.option("--hook", "hook_names", multiple=True, help="Hook(s) to install (by name)")
@click.option(
    "--mcp",
    "mcp_names",
    multiple=True,
    help="MCP server(s) to install for the selected agents (by name)",
)
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
@click.option("--all", "all_skills", is_flag=True, help="Install every skill (no selection prompt)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
@click.option("--copy", is_flag=True, help="Copy skills into each agent dir instead of symlinking")
@click.option("--full-depth", is_flag=True, help="Search all subdirectories for skills")
@click.option("--dry-run", is_flag=True, help="Show what would be installed")
@click.option(
    "--force",
    is_flag=True,
    help="Replace existing files/servers that knowhow did not install (normally refused)",
)
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
    force,
):
    """
    Install skills and other items from a git repository or local directory.

    SOURCE may be owner/repo (GitHub), owner/repo/sub/path, owner/repo@skill,
    a GitHub/GitLab URL (optionally with /tree/<ref>/<path>), any git URL,
    a local path, or an alias from `knowhow config set alias.NAME SOURCE`.

    Skills and MCP servers install for the detected agents (or --agent);
    commands, subagents and hooks install for Claude Code. --all selects skills
    only; hooks and MCP servers must be named and are shown for review first.

    \b
    Examples:
      uvx knowhow add jkitchin/knowhow --skill fairchem
      knowhow add jkitchin/knowhow --list
      knowhow add jkitchin/knowhow -s pycse -s python-plotting -g -y
      knowhow add jkitchin/knowhow --command commit --subagent code-reviewer
      knowhow add jkitchin/knowhow --hook black-on-save
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
                console.print(f"[yellow]Warning: {safe(w)}[/yellow]")

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

            # MCP servers go to every selected agent that supports MCP
            mcp_places, mcp_unusable = {}, []
            mcp_extras = [e for e in chosen_extras if e.kind == "mcp"]
            if mcp_extras:
                base, notes = mcp_targets.plan(agents, global_, cwd, explicit=bool(agent_names))
                for n in notes:
                    console.print(f"[dim]MCP: {safe(n)}[/dim]")
                for e in mcp_extras:
                    cfg = {k: v for k, v in e.config.items() if k != "description"}
                    usable = []
                    for p in base:
                        try:
                            mcp_targets.exists(p, e.name)  # can we read (and so edit) it?
                            usable.append(p)
                        except (ConfigFileError, mcp_targets.McpTargetError) as err:
                            snippet = mcp_targets.snippet(p, e.name, cfg)
                            mcp_unusable.append((e.name, p, str(err), snippet))
                    mcp_places[e.name] = usable
                for name, p, err, snippet in mcp_unusable:
                    _report_mcp_failures(name, [(p, err, snippet)])
                for e in mcp_extras:
                    cfg = {k: v for k, v in e.config.items() if k != "description"}
                    for p in mcp_places[e.name]:
                        for c in p.target.caveats(cfg, global_):
                            console.print(f"[yellow]MCP {safe(e.name)}: {safe(c)}[/yellow]")
                stuck = [e.name for e in mcp_extras if not mcp_places[e.name]]
                if stuck:
                    raise click.ClickException(
                        f"No agent config can take MCP server(s) {', '.join(stuck)}. "
                        "Choose agents with -a, or fix the files reported above."
                    )

            # Plan
            if selected:
                console.print(
                    # agents first: a long project path must not push them off screen
                    f"Installing {len(selected)} skill(s) for "
                    f"{', '.join(registry[a].display_name for a in agents)} "
                    f"({safe(scope)})"
                )
            skipped = [a for a in agents if not global_ and _skip_project_agent(a, cwd, registry)]
            if selected and skipped:
                names = ", ".join(registry[a].display_name for a in skipped)
                console.print(f"[dim]Skipping {names}: not set up in this project[/dim]")
            for s in selected:
                canon, targets, _ = planned_paths(s, agents, global_, copy, cwd, registry)
                where = [str(p) for p in ([canon] if canon else []) + targets]
                console.print(f"  [green]{escape(s.name)}[/green] -> {escape(', '.join(where))}")
            for e in chosen_extras:
                if e.kind == "mcp":
                    where = ", ".join(f"{p.target.display}: {p.label}" for p in mcp_places[e.name])
                else:
                    where = str(target_path(e, global_, cwd))
                console.print(f"  [green]{e.kind} {safe(e.name)}[/green] -> {safe(where)}")

            hooks_chosen = [e for e in chosen_extras if e.kind == "hook"]
            if hooks_chosen:
                from knowhow.commands.hooks import check_settings_file

                # checked up front so a bad settings.json can't leave a half-installed hook
                check_settings_file(
                    claude_dir(global_, cwd) / "settings.json", None if global_ else cwd
                )

            conflicts = _add_conflicts(
                selected, chosen_extras, agents, global_, copy, cwd, registry, mcp_places
            )
            if conflicts:
                verb = "Replacing" if force else "Refusing to replace"
                console.print(f"[yellow]{verb} items that knowhow did not install:[/yellow]")
                for c in conflicts:
                    console.print(f"  [yellow]{safe(c)}[/yellow]")
                if not force and not dry_run:
                    raise click.ClickException(
                        "These already exist and are not in a knowhow/npx lock file. "
                        "Remove or rename them, or pass --force to replace them."
                    )

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
            failed_mcp = []
            for e in chosen_extras:
                placements = None
                if e.kind == "mcp":
                    placements, failed = install_mcp(e, mcp_places[e.name])
                    _report_mcp_failures(e.name, failed)
                    if not placements:
                        failed_mcp.append(e.name)
                        continue
                else:
                    install_extra(e, checkout.root, global_, cwd)
                record_extra(
                    LOCK_KEYS[e.kind],
                    e.name,
                    _extra_entry(src, e, global_, cwd, placements),
                    claude_dir(global_, cwd),
                )
            total = len(selected) + len(chosen_extras) - len(failed_mcp)
            console.print(f"[green]✓ Installed {total} item(s)[/green]")
            if failed_mcp:
                raise click.ClickException(f"MCP server(s) not installed: {', '.join(failed_mcp)}")
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
@click.option(
    "--force",
    is_flag=True,
    help="Also remove items that knowhow did not install (not in a lock file)",
)
@click.option(
    "--all",
    "all_items",
    is_flag=True,
    help="Remove everything knowhow installed in this scope (project, or global with -g)",
)
def remove(
    names,
    command_names,
    subagent_names,
    hook_names,
    mcp_names,
    global_,
    agent_names,
    yes,
    force,
    all_items,
):
    """
    Remove installed items.

    NAMES are skill names, or a source (e.g. owner/repo) to remove every skill,
    command, subagent, hook and MCP server installed from it.

    \b
    Examples:
      knowhow remove fairchem
      knowhow remove --command commit --hook black-on-save
      knowhow remove jkitchin/knowhow -g
      knowhow remove --all          # everything knowhow installed in this project
      knowhow remove --all -g       # ... or for your user

    See what is installed with `knowhow installed`.
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

    def lock_key(n):
        """The lock entry for a skill given by name or install dir name, if any."""
        if n in lock["skills"]:
            return n
        key = install_dir_name(n)
        return next((k for k in lock["skills"] if install_dir_name(k) == key), None)

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
            skill_targets.append(lock_key(n) or n)

    if all_items:
        if skill_targets or extra_targets:
            raise click.UsageError("--all cannot be combined with names")
        skill_targets = list(lock["skills"])
        extra_targets = [(k, n) for k, key in LOCK_KEYS.items() for n in extras_lock[key]]
        if not skill_targets and not extra_targets:
            scope = "global" if global_ else "project"
            console.print(f"[yellow]Nothing installed by knowhow ({scope} scope)[/yellow]")
            return

    if not skill_targets and not extra_targets:
        raise click.UsageError(
            "Give skill names, a source, --command/--subagent/--hook/--mcp, or --all"
        )

    try:
        registry = build_registry(Config())
        agents = resolve_agent_names(agent_names, registry) if agent_names else None
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    # Subagents and hooks may be named by display name or install dir name
    def extra_key(kind, n):
        table = extras_lock[LOCK_KEYS[kind]]
        if n in table or kind in ("command", "mcp"):
            return n
        key = install_dir_name(n)
        return next((k for k in table if install_dir_name(k) == key), n)

    extra_targets = [(k, extra_key(k, n)) for k, n in extra_targets]

    # Only remove what knowhow (or npx skills) recorded installing, unless --force
    unmanaged = [n for n in skill_targets if n not in lock["skills"]] + [
        f"{k} {n}" for k, n in extra_targets if n not in extras_lock[LOCK_KEYS[k]]
    ]
    if unmanaged and not force:
        scope = "global" if global_ else "project"
        raise click.ClickException(
            f"Not installed by knowhow ({scope} scope): {', '.join(unmanaged)}. "
            "Nothing was removed. See what knowhow installed with `knowhow installed`; "
            "use -g for global installs, or --force to remove these anyway."
        )

    labels = skill_targets + [f"{k} {n}" for k, n in extra_targets]
    if not yes:
        if not sys.stdin.isatty():
            raise click.ClickException("No terminal to confirm removal; pass -y to proceed.")
        if not click.confirm(f"Remove {', '.join(labels)}?", default=False):
            raise click.Abort()

    shared = [a for a in agents or [] if registry[a].is_universal]
    if shared and set(agents) < set(registry):
        console.print(
            f"[dim]{', '.join(registry[a].display_name for a in shared)} read the shared "
            ".agents/skills copy; `knowhow remove NAME` without -a removes it for all "
            "agents.[/dim]"
        )
    for name in skill_targets:
        removed = uninstall_skill(name, global_, agents, cwd, registry)
        if not agents or set(agents) >= set(AGENTS):
            remove_entry(name, global_, cwd)
        if removed:
            console.print(f"[green]✓ Removed {safe(name)}[/green] ({len(removed)} path(s))")
        else:
            console.print(f"[yellow]{escape(name)} is not installed here[/yellow]")

    for kind, name in extra_targets:
        if kind == "mcp":
            entry = extras_lock["mcp"].get(name)
            try:
                removed, failed = uninstall_mcp(name, mcp_placements_for(entry, global_, cwd))
            except ExtraError as e:
                console.print(f"[red]Could not remove mcp {safe(name)}: {safe(e)}[/red]")
                continue
            for p, err in failed:
                console.print(
                    f"[red]Could not remove mcp {safe(name)} from {p.target.display} "
                    f"({safe(p.label)}): {safe(err)}[/red]"
                )
            if failed and entry:
                # keep only the places it is still configured, so it can be retried
                still = [mcp_targets.to_record(p) for p, _ in failed]
                record_extra("mcp", name, {"targets": still}, cdir)
            else:
                remove_extra("mcp", name, cdir)
            if removed:
                console.print(f"[green]✓ Removed mcp {safe(name)}[/green]")
            elif not failed:
                console.print(f"[yellow]mcp {safe(name)} is not installed here[/yellow]")
            continue
        try:
            removed = uninstall_extra(kind, name, global_, cwd)
        except ExtraError as e:
            # Still installed: keep its lock entry so it can be retried
            console.print(f"[red]Could not remove {kind} {safe(name)}: {safe(e)}[/red]")
            continue
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
                            name, entry, skills, src, checkout, global_, apply, cwd, yes
                        )
                    else:
                        status = _check_extra(
                            kind, name, entry, extras, src, checkout, global_, apply, yes, cwd, cdir
                        )
                    results.append((kind, name, status))
        except FetchError as e:
            results += [(k, n, f"fetch failed: {e}") for k, n, _ in items]
    return results


SCRIPT_SUFFIXES = {".sh", ".bash", ".zsh", ".py", ".js", ".mjs", ".ts", ".rb", ".pl", ".ps1"}


def _file_digests(root: Path) -> dict[str, tuple[str, bool]]:
    """relpath -> (sha256, executable) for every regular file under root."""
    import hashlib

    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.is_file():
                rel = p.relative_to(root).as_posix()
                out[rel] = (hashlib.sha256(p.read_bytes()).hexdigest(), os.access(p, os.X_OK))
    return out


def _skill_changes(old_dir: Path | None, new_dir: Path) -> tuple[list, list, list, list]:
    """(added, changed, removed, of which runnable) between an installed copy and upstream."""
    old = _file_digests(old_dir) if old_dir and old_dir.is_dir() else {}
    new = _file_digests(new_dir)
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(f for f in set(new) & set(old) if new[f] != old[f])
    runnable = [f for f in added + changed if Path(f).suffix in SCRIPT_SUFFIXES or new[f][1]]
    return added, changed, removed, runnable


def _check_skill(name, entry, skills, src, checkout, global_, apply, cwd, yes=False) -> str:
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
    # project hashes written by knowhow <= 0.1 used codepoint file order
    legacy = None if global_ else compute_folder_hash(skill.path, npx_order=False)
    if stored in (current, legacy):
        return "up to date"
    if not apply:
        return "update available"
    config = Config()
    registry = build_registry(config)
    installed = find_installed(name, global_, cwd, registry)
    copy_now = next((p for p in installed if (p / "SKILL.md").is_file()), None)
    added, changed, removed, runnable = _skill_changes(copy_now, skill.path)
    summary = ", ".join(
        f"{label} {', '.join(files)}"
        for label, files in (("+", added), ("~", changed), ("-", removed))
        if files
    )
    console.print(f"[cyan]{safe(name)}[/cyan]: {safe(summary) or 'metadata only'}")
    if runnable and not yes:
        console.print(
            f"[yellow]  scripts/executables changed: {safe(', '.join(runnable))}[/yellow]"
        )
        if not sys.stdin.isatty():
            return "skipped (scripts changed; rerun with -y after reviewing)"
        if not click.confirm(f"  Update {name}?", default=False):
            return "skipped"
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
    if kind == "mcp":
        where = ", ".join(p.label for p in mcp_placements_for(entry, global_, cwd))
        console.print(f"MCP {safe(name)} will be updated in: {safe(where)}")
    try:
        _confirm_code(extra, yes)
    except click.Abort:
        return "skipped"
    if kind == "mcp":
        placements = mcp_placements_for(entry, global_, cwd)
        written, failed = install_mcp(extra, placements)
        _report_mcp_failures(name, failed)
        if not written:
            return "error: no agent config could be updated"
        record_extra(
            LOCK_KEYS[kind], name, _extra_entry(src, extra, global_, cwd, placements), cdir
        )
        return "updated" if not failed else "partly updated"
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
    req = urllib.request.Request(url, headers={"User-Agent": "knowhow", **(headers or {})})
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
    from knowhow.discovery import sanitize_text

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
                escape(f"knowhow add {source}@{name}"),
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
    console.print("[dim]List a repo's contents with: knowhow add <repo> --list[/dim]")
