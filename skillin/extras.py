"""Discover and install non-skill items from a source: commands, hooks, subagents, MCP servers.

`npx skills` only handles skills. These follow skillin / Claude Code conventions
and install for Claude Code:

    kind        found in                                     installed to (.claude/ or ~/.claude/)
    command     commands/**/*.md, .claude/commands/**/*.md   commands/<name>.md
    subagent    agents/**/*.md, .claude/agents/**/*.md       agents/<name>.md
    hook        hooks/**/HOOK.md, .claude/hooks/**/HOOK.md   hooks/<name>/ + settings.json
    mcp         .mcp.json, mcp/**/*.json ("mcpServers")      every selected agent's MCP config
                                                             (see mcp_targets.py)
"""

import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from skillin import mcp_targets
from skillin.agents_registry import _claude_home
from skillin.discovery import SKIP_DIRS, install_dir_name, sanitize_text
from skillin.installer import copy_skill_tree, remove_path
from skillin.lock import compute_file_hash, compute_folder_hash
from skillin.safeio import ConfigFileError, strip_controls
from skillin.validator import AgentValidator, CommandValidator, HookValidator

KINDS = ("command", "subagent", "hook", "mcp")
LOCK_KEYS = {"command": "commands", "subagent": "subagents", "hook": "hooks", "mcp": "mcp"}
_SKIP_MD = {"readme.md", "template.md", "skill.md", "hook.md", "changelog.md", "license.md"}
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class ExtraError(RuntimeError):
    """Raised when an extra cannot be installed."""


@dataclass
class Extra:
    kind: str
    name: str
    description: str
    path: Path  # file (command/subagent/mcp json) or directory (hook)
    rel_path: str  # repo-relative path
    config: dict = field(default_factory=dict)  # HOOK.md metadata or MCP server config

    def content_hash(self) -> str:
        if self.kind == "mcp":
            import hashlib

            return hashlib.sha256(json.dumps(self.config, sort_keys=True).encode()).hexdigest()
        if self.kind == "hook":
            return compute_folder_hash(self.path)
        return compute_file_hash(self.path)


def claude_dir(global_: bool, cwd: Path | None = None) -> Path:
    """`.claude/` in the project, or the user's Claude config dir."""
    return _claude_home() if global_ else (cwd or Path.cwd()) / ".claude"


def _md_files(dirs: list[Path]) -> list[Path]:
    files = []
    for d in dirs:
        if not d.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = sorted(n for n in dirnames if n not in SKIP_DIRS)
            for fn in sorted(filenames):
                if fn.endswith(".md") and fn.lower() not in _SKIP_MD:
                    files.append(Path(dirpath) / fn)
    return files


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _str_map(value) -> bool:
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def _valid_mcp_config(cfg) -> bool:
    """A stdio ({command, args?, env?}) or remote ({type?, url, headers?}) server config."""
    if not isinstance(cfg, dict):
        return False
    if "args" in cfg and not (
        isinstance(cfg["args"], list) and all(isinstance(a, str) for a in cfg["args"])
    ):
        return False
    for key in ("env", "headers"):
        if key in cfg and not _str_map(cfg[key]):
            return False
    if isinstance(cfg.get("command"), str) and cfg["command"]:
        return cfg.get("type", "stdio") == "stdio" and "url" not in cfg
    return (
        isinstance(cfg.get("url"), str)
        and cfg["url"].startswith(("https://", "http://"))
        and cfg.get("type", "http") in ("http", "sse")
    )


def discover_extras(
    root: Path, subpath: str | None = None, warnings: list[str] | None = None
) -> dict[str, list[Extra]]:
    """Find commands, subagents, hooks and MCP servers. First name of each kind wins."""
    search = root / subpath if subpath else root
    found: dict[str, list[Extra]] = {k: [] for k in KINDS}
    seen: dict[str, set] = {k: set() for k in KINDS}

    def add(extra: Extra):
        if extra.name in seen[extra.kind]:
            if warnings is not None:
                warnings.append(f"Duplicate {extra.kind} '{extra.name}' at {extra.rel_path}")
            return
        seen[extra.kind].add(extra.name)
        found[extra.kind].append(extra)

    def warn(msg):
        if warnings is not None:
            warnings.append(msg)

    for f in _md_files([search / "commands", search / ".claude" / "commands"]):
        if not _SAFE_NAME.match(f.stem):
            warn(f"Skipping command with unsafe name: {f}")
            continue
        fm = CommandValidator._parse_frontmatter(f.read_text(errors="replace")) or {}
        desc = fm.get("description") if isinstance(fm, dict) else None
        add(Extra("command", f.stem, sanitize_text(str(desc or "")), f, _rel(f, root)))

    for f in _md_files([search / "agents", search / ".claude" / "agents"]):
        fm = AgentValidator._parse_frontmatter(f.read_text(errors="replace"))
        if not isinstance(fm, dict) or not all(
            isinstance(fm.get(k), str) and fm.get(k) for k in ("name", "description")
        ):
            warn(f"Skipping subagent without string name/description: {f}")
            continue
        add(
            Extra(
                "subagent",
                sanitize_text(fm["name"]),
                sanitize_text(fm["description"]),
                f,
                _rel(f, root),
            )
        )

    for d in (search / "hooks", search / ".claude" / "hooks"):
        if not d.is_dir():
            continue
        for hook_md in sorted(d.rglob("HOOK.md")):
            hook_dir = hook_md.parent
            valid, errors = HookValidator.validate_hook_directory(hook_dir)
            meta = HookValidator.get_hook_metadata(hook_dir) or {}
            if not valid:
                warn(f"Skipping invalid hook {hook_dir}: {'; '.join(errors)}")
                continue
            if meta.get("type", "command") != "command":
                warn(f"Skipping hook {hook_dir}: only `type: command` hooks can be installed")
                continue
            name = str(meta.get("name") or hook_dir.name)
            add(
                Extra(
                    "hook",
                    sanitize_text(name),
                    sanitize_text(str(meta.get("description", ""))),
                    hook_dir,
                    _rel(hook_dir, root),
                    meta,
                )
            )

    mcp_files = [search / ".mcp.json"]
    if (search / "mcp").is_dir():
        mcp_files += sorted((search / "mcp").rglob("*.json"))
    for f in mcp_files:
        if not f.is_file():
            continue
        try:
            data = json.loads(f.read_text())
        except (OSError, ValueError) as e:
            warn(f"Skipping unreadable MCP file {f}: {e}")
            continue
        servers = data.get("mcpServers") if isinstance(data, dict) else None
        if servers is not None and not isinstance(servers, dict):
            warn(f"Skipping {f}: 'mcpServers' must be an object")
            continue
        for name, cfg in (servers or {}).items():
            if not _SAFE_NAME.match(str(name)) or not _valid_mcp_config(cfg):
                warn(f"Skipping invalid MCP server '{name}' in {f}")
                continue
            desc = cfg.get("description") or describe_mcp(cfg)
            add(Extra("mcp", name, sanitize_text(str(desc)), f, _rel(f, root), cfg))

    return found


def describe_mcp(cfg: dict) -> str:
    """One-line summary of what an MCP server config runs."""
    if "command" in cfg:
        return " ".join([cfg["command"], *map(str, cfg.get("args", []))])
    return f"{cfg.get('type', 'http')} {cfg['url']}"


def target_path(extra: Extra, global_: bool, cwd: Path | None = None) -> Path:
    """Where an extra will be installed."""
    base = claude_dir(global_, cwd)
    if extra.kind == "command":
        return base / "commands" / f"{extra.name}.md"
    if extra.kind == "subagent":
        return base / "agents" / f"{install_dir_name(extra.name)}.md"
    if extra.kind == "hook":
        return base / "hooks" / install_dir_name(extra.name)
    raise ValueError("MCP servers can have several targets; see mcp_targets.plan")


def preview(extra: Extra, max_lines: int = 40) -> str:
    """
    Text to show before installing something that runs code.

    Escape sequences and control characters are stripped so a malicious script
    cannot rewrite what the user sees.
    """
    return strip_controls(_preview(extra, max_lines))


def _preview(extra: Extra, max_lines: int) -> str:
    if extra.kind == "mcp":
        return json.dumps({extra.name: extra.config}, indent=2)
    if extra.kind == "hook":
        parts = [f"event: {extra.config.get('event')}  matcher: {extra.config.get('matcher', '*')}"]
        scripts = sorted(p for p in extra.path.rglob("*") if p.is_file() and not p.is_symlink())
        others = [
            p.relative_to(extra.path).as_posix() for p in scripts if p.suffix not in (".py", ".sh")
        ]
        if others:
            parts.append("other files: " + ", ".join(others))
        for script in scripts:
            if script.suffix in (".py", ".sh"):
                lines = script.read_text(errors="replace").splitlines()
                more = (
                    f"\n... ({len(lines) - max_lines} more lines)" if len(lines) > max_lines else ""
                )
                rel = script.relative_to(extra.path).as_posix()
                parts.append(f"── {rel} ──\n" + "\n".join(lines[:max_lines]) + more)
        return "\n".join(parts)
    return ""


def _copy_file(src: Path, dst: Path, boundary: Path) -> None:
    if src.is_symlink():
        try:
            src.resolve().relative_to(boundary.resolve())
        except ValueError as e:
            raise ExtraError(f"{src} is a symlink outside the source") from e
    dst.parent.mkdir(parents=True, exist_ok=True)
    remove_path(dst)
    shutil.copyfile(src, dst)


def extra_exists(extra: Extra, global_: bool, cwd: Path | None = None) -> bool:
    """True if a command/subagent/hook with this name already exists at its target."""
    if extra.kind == "mcp":
        raise ValueError("use mcp_targets.exists for MCP servers")
    dest = target_path(extra, global_, cwd or Path.cwd())
    return dest.exists() or dest.is_symlink()


def mcp_placements_for(entry: dict | None, global_: bool, cwd: Path) -> list:
    """Where a recorded MCP server was written (legacy entries: Claude Code only)."""
    records = (entry or {}).get("targets")
    if isinstance(records, list) and records:
        places = [mcp_targets.placement_from_record(r, global_, cwd) for r in records]
        return [p for p in places if p is not None]
    return mcp_targets.legacy_placements(global_, cwd)


def install_mcp(extra: Extra, placements: list) -> tuple[list, list]:
    """
    Write an MCP server to each placement.

    Returns (written placements, [(placement, error, snippet to add by hand)]).
    A failure for one agent (e.g. a config file with comments) doesn't stop the others.
    """
    cfg = {k: v for k, v in extra.config.items() if k != "description"}
    written, failed = [], []
    for p in placements:
        try:
            mcp_targets.write(p, extra.name, cfg)
            written.append(p)
        except (ConfigFileError, mcp_targets.McpTargetError) as e:
            failed.append((p, str(e), mcp_targets.snippet(p, extra.name, cfg)))
    return written, failed


def uninstall_mcp(name: str, placements: list) -> tuple[bool, list]:
    """Remove an MCP server from each placement. Returns (removed any, [(placement, error)])."""
    if not _SAFE_NAME.match(name):
        raise ExtraError(f"Invalid mcp name: {name!r}")
    removed, failed = False, []
    for p in placements:
        try:
            removed |= mcp_targets.remove(p, name)
        except (ConfigFileError, mcp_targets.McpTargetError) as e:
            failed.append((p, str(e)))
    return removed, failed


def install_extra(
    extra: Extra, source_root: Path, global_: bool = False, cwd: Path | None = None
) -> Path:
    """Install one extra for Claude Code. Returns the installed path."""
    from skillin.commands.hooks import _add_hook_to_settings

    cwd = cwd or Path.cwd()
    dest = target_path(extra, global_, cwd)
    if extra.kind in ("command", "subagent"):
        _copy_file(extra.path, dest, source_root)
    elif extra.kind == "hook":
        from skillin.commands.hooks import check_settings_file

        # fail before copying anything if settings.json can't be updated
        check_settings_file(claude_dir(global_, cwd) / "settings.json", None if global_ else cwd)
        copy_skill_tree(extra.path, dest, source_root)
        for script in list(dest.glob("*.py")) + list(dest.glob("*.sh")):
            os.chmod(script, 0o755)
        _add_hook_to_settings(
            claude_dir(global_, cwd) / "settings.json",
            dest,
            extra.config,
            None if global_ else cwd,
        )
    else:
        raise ValueError("use install_mcp for MCP servers")
    return dest


def uninstall_extra(kind: str, name: str, global_: bool = False, cwd: Path | None = None) -> bool:
    """Remove an installed extra. Returns True if something was removed."""
    from skillin.commands.hooks import _remove_hook_from_settings

    cwd = cwd or Path.cwd()
    base = claude_dir(global_, cwd)
    # commands are stored under their own name; subagents and hooks under the
    # sanitized install_dir_name (so display names like "Code Reviewer" work)
    stored = name if kind == "command" else install_dir_name(name)
    if not _SAFE_NAME.match(stored):
        raise ExtraError(f"Invalid {kind} name: {name!r}")
    if kind == "command":
        p = base / "commands" / f"{name}.md"
    elif kind == "subagent":
        p = base / "agents" / f"{install_dir_name(name)}.md"
    elif kind == "hook":
        p = base / "hooks" / install_dir_name(name)
        # unregister even if the directory is already gone
        _remove_hook_from_settings(base / "settings.json", p, project_root=None if global_ else cwd)
    else:
        raise ValueError("use uninstall_mcp for MCP servers")
    if p.exists() or p.is_symlink():
        remove_path(p)
        return True
    return False
