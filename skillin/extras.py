"""Discover and install non-skill items from a source: commands, hooks, subagents, MCP servers.

`npx skills` only handles skills. These follow skillin / Claude Code conventions
and install for Claude Code:

    kind        found in                                     installed to (.claude/ or ~/.claude/)
    command     commands/**/*.md, .claude/commands/**/*.md   commands/<name>.md
    subagent    agents/**/*.md, .claude/agents/**/*.md       agents/<name>.md
    hook        hooks/**/HOOK.md, .claude/hooks/**/HOOK.md   hooks/<name>/ + settings.json
    mcp         .mcp.json, mcp/**/*.json ("mcpServers")      ./.mcp.json, or `claude mcp add-json
                                                             --scope user` with --global
"""

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from skillin.agents_registry import _claude_home
from skillin.discovery import SKIP_DIRS, install_dir_name, sanitize_text
from skillin.installer import copy_skill_tree, remove_path
from skillin.lock import compute_file_hash, compute_folder_hash
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


def _valid_mcp_config(cfg) -> bool:
    if not isinstance(cfg, dict):
        return False
    if isinstance(cfg.get("command"), str):
        return cfg.get("type", "stdio") == "stdio"
    return isinstance(cfg.get("url"), str) and cfg.get("type", "http") in ("http", "sse")


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
    if global_:
        return Path.home() / ".claude.json"  # managed by `claude mcp`
    return (cwd or Path.cwd()) / ".mcp.json"


def preview(extra: Extra, max_lines: int = 40) -> str:
    """Text to show before installing something that runs code."""
    if extra.kind == "mcp":
        return json.dumps({extra.name: extra.config}, indent=2)
    if extra.kind == "hook":
        parts = [f"event: {extra.config.get('event')}  matcher: {extra.config.get('matcher', '*')}"]
        for script in sorted(extra.path.iterdir()):
            if script.suffix in (".py", ".sh") and script.is_file():
                lines = script.read_text(errors="replace").splitlines()
                more = (
                    f"\n... ({len(lines) - max_lines} more lines)" if len(lines) > max_lines else ""
                )
                parts.append(f"── {script.name} ──\n" + "\n".join(lines[:max_lines]) + more)
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


def _claude_cli(args: list[str]) -> None:
    if not shutil.which("claude"):
        raise ExtraError(
            "Global MCP install needs the `claude` CLI on PATH (it manages ~/.claude.json)"
        )
    result = subprocess.run(["claude", *args], capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise ExtraError(result.stderr.strip() or f"claude {' '.join(args)} failed")


def _update_mcp_json(path: Path, name: str, cfg: dict | None) -> None:
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except ValueError as e:
            raise ExtraError(f"{path} is not valid JSON") from e
    servers = data.setdefault("mcpServers", {})
    if cfg is None:
        servers.pop(name, None)
    else:
        servers[name] = cfg
    path.write_text(json.dumps(data, indent=2) + "\n")


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
        copy_skill_tree(extra.path, dest, source_root)
        for script in list(dest.glob("*.py")) + list(dest.glob("*.sh")):
            os.chmod(script, 0o755)
        _add_hook_to_settings(claude_dir(global_, cwd) / "settings.json", dest, extra.config)
    elif global_:
        cfg = {k: v for k, v in extra.config.items() if k != "description"}
        try:  # `claude mcp add-json` refuses to overwrite an existing server
            _claude_cli(["mcp", "remove", "--scope", "user", extra.name])
        except ExtraError:
            pass
        _claude_cli(["mcp", "add-json", "--scope", "user", extra.name, json.dumps(cfg)])
    else:
        cfg = {k: v for k, v in extra.config.items() if k != "description"}
        _update_mcp_json(dest, extra.name, cfg)
    return dest


def uninstall_extra(kind: str, name: str, global_: bool = False, cwd: Path | None = None) -> bool:
    """Remove an installed extra. Returns True if something was removed."""
    from skillin.commands.hooks import _remove_hook_from_settings

    cwd = cwd or Path.cwd()
    base = claude_dir(global_, cwd)
    if kind == "command":
        p = base / "commands" / f"{name}.md"
    elif kind == "subagent":
        p = base / "agents" / f"{install_dir_name(name)}.md"
    elif kind == "hook":
        p = base / "hooks" / install_dir_name(name)
        if p.is_dir():
            meta = HookValidator.get_hook_metadata(p) or {}
            _remove_hook_from_settings(base / "settings.json", p, meta)
    elif global_:
        _claude_cli(["mcp", "remove", "--scope", "user", name])
        return True
    else:
        path = cwd / ".mcp.json"
        if not path.exists() or name not in json.loads(path.read_text()).get("mcpServers", {}):
            return False
        _update_mcp_json(path, name, None)
        return True
    if p.exists() or p.is_symlink():
        remove_path(p)
        return True
    return False
