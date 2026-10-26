"""`skillin installed`: offline inventory of everything skillin (or npx skills) installed."""

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from skillin import mcp_targets
from skillin.agents_registry import build_registry, canonical_dir
from skillin.config import Config
from skillin.discovery import install_dir_name
from skillin.extras import KINDS, LOCK_KEYS, Extra, claude_dir, mcp_placements_for, target_path
from skillin.installer import _agent_bases, find_installed
from skillin.lock import read_extras_lock, read_lock
from skillin.safeio import ConfigFileError, safe

console = Console()


@dataclass
class Item:
    scope: str  # "project" or "global"
    kind: str  # "skill", "command", "subagent", "hook", "mcp"
    name: str
    source: str
    status: str  # "ok", "missing", "registered", "untracked"
    paths: list[str] = field(default_factory=list)


def _mcp_status(name: str, entry: dict, global_: bool, cwd: Path) -> tuple[str, list[str]]:
    """Check each agent config the server was written to (Claude's CLI store is not read)."""
    statuses, labels = [], []
    for p in mcp_placements_for(entry, global_, cwd):
        labels.append(f"{p.target.display}: {p.label}")
        if p.file is None:
            statuses.append("registered")  # in ~/.claude.json via `claude mcp`
            continue
        try:
            statuses.append("ok" if mcp_targets.exists(p, name) else "missing")
        except (ConfigFileError, mcp_targets.McpTargetError):
            statuses.append("unreadable")
    for bad in ("unreadable", "missing"):
        if bad in statuses:
            return bad, labels
    return ("ok" if "ok" in statuses else "registered"), labels


def _extra_status(
    kind: str, name: str, global_: bool, cwd: Path, entry=None
) -> tuple[str, list[str]]:
    if kind == "mcp":
        return _mcp_status(name, entry or {}, global_, cwd)
    path = target_path(Extra(kind, name, "", Path(), ""), global_, cwd)
    exists = path.exists() or path.is_symlink()
    return ("ok" if exists else "missing"), [str(path)]


def collect(global_: bool, cwd: Path, registry=None, untracked: bool = False) -> list[Item]:
    """Items recorded in this scope's lock files, checked against disk."""
    scope = "global" if global_ else "project"
    registry = registry or build_registry(Config())
    items = []
    lock = read_lock(global_, cwd)
    for name, entry in sorted(lock["skills"].items()):
        found = find_installed(name, global_, cwd, registry)
        if not found:
            status = "missing"
        elif all((p / "SKILL.md").is_file() for p in found):
            status = "ok"
        else:
            status = "broken"  # e.g. an agent symlink whose canonical copy was deleted
        items.append(
            Item(scope, "skill", name, entry.get("source", ""), status, [str(p) for p in found])
        )
    extras_lock = read_extras_lock(claude_dir(global_, cwd))
    for kind in KINDS:
        for name, entry in sorted(extras_lock[LOCK_KEYS[kind]].items()):
            status, paths = _extra_status(kind, name, global_, cwd, entry)
            items.append(Item(scope, kind, name, entry.get("source", ""), status, paths))
    if untracked:
        items += _untracked(global_, cwd, registry, lock, extras_lock)
    return items


def _untracked(global_, cwd, registry, lock, extras_lock) -> list[Item]:
    """Items in agent directories that no lock file accounts for."""
    scope = "global" if global_ else "project"
    known = {install_dir_name(n) for n in lock["skills"]}
    found: dict[str, list[str]] = {}
    for base in [canonical_dir(global_, cwd)] + _agent_bases(global_, cwd, registry):
        if not base.is_dir():
            continue
        for p in sorted(base.iterdir()):
            if p.name not in known and (p / "SKILL.md").is_file():
                found.setdefault(p.name, []).append(str(p))
    items = [Item(scope, "skill", n, "", "untracked", ps) for n, ps in sorted(found.items())]

    cdir = claude_dir(global_, cwd)
    for kind, sub, suffix in (("command", "commands", ".md"), ("subagent", "agents", ".md")):
        tracked = {install_dir_name(n) for n in extras_lock[LOCK_KEYS[kind]]}
        for p in sorted((cdir / sub).glob(f"*{suffix}")) if (cdir / sub).is_dir() else []:
            if p.stem not in tracked and install_dir_name(p.stem) not in tracked:
                items.append(Item(scope, kind, p.stem, "", "untracked", [str(p)]))
    tracked_hooks = {install_dir_name(n) for n in extras_lock["hooks"]}
    hooks_dir = cdir / "hooks"
    for p in sorted(hooks_dir.iterdir()) if hooks_dir.is_dir() else []:
        if p.is_dir() and p.name not in tracked_hooks:
            items.append(Item(scope, "hook", p.name, "", "untracked", [str(p)]))
    # MCP servers in every agent's config (Claude's ~/.claude.json is not read)
    seen_files = set()
    for t in mcp_targets.TARGETS.values():
        if global_ and t.global_via_cli:
            continue
        p = mcp_targets.Placement(t, t.path(global_, cwd), global_, None if global_ else cwd)
        if p.file is None or not p.file.exists() or (str(p.file), t.key) in seen_files:
            continue
        seen_files.add((str(p.file), t.key))
        try:
            names = mcp_targets.server_names(p)
        except (ConfigFileError, mcp_targets.McpTargetError):
            continue
        for n in sorted(names):
            if n not in extras_lock["mcp"]:
                items.append(Item(scope, "mcp", n, "", "untracked", [f"{t.display}: {p.file}"]))
    return items


@click.command()
@click.option("--global", "-g", "global_", is_flag=True, help="Only global (user) installs")
@click.option("--project", "-p", is_flag=True, help="Only installs in the current project")
@click.option(
    "--untracked", is_flag=True, help="Also list items in agent dirs that skillin didn't install"
)
@click.option("--json", "as_json", is_flag=True, help="Print JSON instead of a table")
def installed(global_, project, untracked, as_json):
    """
    Show everything skillin installed (offline, from lock files).

    Lists skills, slash commands, subagents, hooks and MCP servers for the
    current project and for your user, where each one lives, and whether it is
    still there. Remove items with `skillin remove`, or everything in a scope
    with `skillin remove --all [-g]`.
    """
    cwd = Path.cwd()
    scopes = [True] if global_ else [False] if project else [False, True]
    registry = build_registry(Config())
    items = [i for g in scopes for i in collect(g, cwd, registry, untracked)]

    if as_json:
        json.dump([asdict(i) for i in items], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    if not items:
        console.print("[yellow]Nothing installed by skillin here[/yellow]")
        return
    table = Table(title="Installed by skillin" + (" (+ untracked)" if untracked else ""))
    for col in ("Scope", "Type", "Name", "Source", "Location", "Status"):
        table.add_column(col)
    colors = {
        "ok": "green",
        "registered": "green",
        "missing": "red",
        "broken": "red",
        "unreadable": "red",
        "untracked": "yellow",
    }
    for i in items:
        table.add_row(
            i.scope,
            i.kind,
            safe(i.name),
            safe(i.source, 40),
            safe("\n".join(i.paths) or "-"),
            f"[{colors.get(i.status, 'white')}]{i.status}[/]",
        )
    console.print(table)
    if any(i.status in ("missing", "broken") for i in items):
        console.print(
            "[dim]missing: recorded but not on disk; broken: a link points at a deleted copy. "
            "Reinstall with `skillin add`, or clean up with `skillin remove NAME`.[/dim]"
        )
