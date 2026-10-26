"""Where and how each agent stores MCP server configs.

Paths and shapes follow each tool's documentation (cross-checked against
neondatabase/add-mcp):

    agent           project file              global file                          key
    claude-code     .mcp.json                 `claude mcp --scope user` (CLI)      mcpServers
    vscode          .vscode/mcp.json          <VS Code user dir>/User/mcp.json     servers
    cursor          .cursor/mcp.json          ~/.cursor/mcp.json                   mcpServers
    codex           .codex/config.toml        $CODEX_HOME/config.toml              mcp_servers
    gemini-cli      .gemini/settings.json     ~/.gemini/settings.json              mcpServers
    opencode        opencode.json(c)          ~/.config/opencode/opencode.json(c)  mcp
    github-copilot  .mcp.json                 $COPILOT_HOME/mcp-config.json        mcpServers
    windsurf        (global only)             ~/.codeium/windsurf/mcp_config.json  mcpServers

Safety rules: a file is only modified if it parses cleanly (JSON with comments is
never rewritten; the snippet to add by hand is reported instead), writes are
atomic with a `.bak`, TOML is edited by appending/removing only the server's own
table and re-parsed to verify, and Claude Code's ~/.claude.json is left to the
`claude` CLI.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from skillpack.agents_registry import _codex_home, _home, _vscode_user_dir, _xdg_config
from skillpack.safeio import (
    ConfigFileError,
    read_json_object,
    real_target,
    write_json_atomic,
    write_text_atomic,
)

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

CLAUDE_CLI = "claude mcp (user scope)"


class McpTargetError(RuntimeError):
    """A target could not be updated (reported to the user, other targets continue)."""


# --- placeholders ------------------------------------------------------------
# Source configs use the portable `${NAME}` form (Claude Code / .mcp.json). Each
# tool spells environment references differently, so they are rewritten per target.

_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_BEARER_VAR = re.compile(r"Bearer \$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _translate(cfg: dict, template: str) -> dict:
    """Rewrite `${NAME}` in command, args, url, env and header values using template."""

    def sub(value: str) -> str:
        return _VAR.sub(lambda m: template.format(m.group(1)), value)

    out = dict(cfg)
    for key in ("command", "url"):
        if key in out:
            out[key] = sub(out[key])
    if "args" in out:
        out["args"] = [sub(a) for a in out["args"]]
    for key in ("env", "headers"):
        if key in out:
            out[key] = {k: sub(v) for k, v in out[key].items()}
    return out


def _has_placeholder(value) -> bool:
    if isinstance(value, str):
        return "${" in value
    if isinstance(value, list):
        return any(_has_placeholder(v) for v in value)
    if isinstance(value, dict):
        return any(_has_placeholder(v) for v in value.values())
    return False


# --- config shapes -----------------------------------------------------------


def _is_remote(cfg: dict) -> bool:
    return "url" in cfg


def _transport(cfg: dict) -> str:
    return cfg.get("type", "http") if _is_remote(cfg) else "stdio"


def _stdio(cfg: dict, **extra) -> dict:
    out = {**extra, "command": cfg["command"], "args": list(cfg.get("args", []))}
    if cfg.get("env"):
        out["env"] = dict(cfg["env"])
    return out


def _remote(cfg: dict, url_key: str = "url", headers_key: str = "headers", **extra) -> dict:
    out = {**extra, url_key: cfg["url"]}
    if cfg.get("headers"):
        out[headers_key] = dict(cfg["headers"])
    return out


def shape_standard(cfg: dict) -> dict:  # Claude Code, Copilot CLI project (.mcp.json)
    return _remote(cfg, type=_transport(cfg)) if _is_remote(cfg) else _stdio(cfg)


def shape_vscode(cfg: dict) -> dict:
    return _remote(cfg, type=_transport(cfg)) if _is_remote(cfg) else _stdio(cfg, type="stdio")


def shape_cursor(cfg: dict) -> dict:
    return _remote(cfg) if _is_remote(cfg) else _stdio(cfg)


def shape_codex(cfg: dict) -> dict:
    """
    Codex does not expand `${VAR}` in values; it forwards variables by name:
    `env_vars` (stdio), `bearer_token_env_var` and `env_http_headers` (HTTP).
    """
    if _is_remote(cfg):
        out = {"url": cfg["url"]}
        headers = dict(cfg.get("headers", {}))
        m = _BEARER_VAR.fullmatch(headers.get("Authorization", ""))
        if m:
            out["bearer_token_env_var"] = m.group(1)
            del headers["Authorization"]
        from_env = {}
        for h, v in headers.items():
            m = _VAR.fullmatch(v)
            if m:
                from_env[h] = m.group(1)
        static = {h: v for h, v in headers.items() if h not in from_env}
        if static:
            out["http_headers"] = static
        if from_env:
            out["env_http_headers"] = from_env
        return out
    out = {"command": cfg["command"], "args": list(cfg.get("args", []))}
    env = cfg.get("env", {})
    passthrough = [k for k, v in env.items() if v == f"${{{k}}}"]
    static = {k: v for k, v in env.items() if k not in passthrough}
    if static:
        out["env"] = static
    if passthrough:
        out["env_vars"] = passthrough
    return out


def shape_gemini(cfg: dict) -> dict:
    if not _is_remote(cfg):
        return _stdio(cfg)
    # Gemini CLI: `url` is SSE, `httpUrl` is streamable HTTP
    return _remote(cfg, url_key="url" if _transport(cfg) == "sse" else "httpUrl")


def shape_opencode(cfg: dict) -> dict:
    if _is_remote(cfg):
        return _remote(cfg, type="remote", enabled=True)
    out = {"type": "local", "command": [cfg["command"], *cfg.get("args", [])], "enabled": True}
    if cfg.get("env"):
        out["environment"] = dict(cfg["env"])
    return out


def shape_copilot_global(cfg: dict) -> dict:
    out = _remote(cfg, type=_transport(cfg)) if _is_remote(cfg) else _stdio(cfg, type="stdio")
    out["tools"] = ["*"]
    return out


def shape_windsurf(cfg: dict) -> dict:
    return _remote(cfg, url_key="serverUrl") if _is_remote(cfg) else _stdio(cfg)


# --- targets -----------------------------------------------------------------


def _first_existing(candidates: list[Path], default: Path) -> Path:
    return next((p for p in candidates if p.exists()), default)


def _opencode_project(cwd: Path) -> Path:
    names = [
        "opencode.jsonc",
        "opencode.json",
        ".opencode/opencode.jsonc",
        ".opencode/opencode.json",
    ]
    return _first_existing([cwd / n for n in names], cwd / "opencode.json")


def _opencode_global() -> Path:
    base = _xdg_config() / "opencode"
    return _first_existing(
        [base / "opencode.jsonc", base / "opencode.json"], base / "opencode.json"
    )


def _copilot_home() -> Path:
    return Path(os.environ.get("COPILOT_HOME", "").strip() or _home() / ".copilot")


@dataclass(frozen=True)
class McpTarget:
    agent: str
    display: str
    key: str
    fmt: str  # "json" or "toml"
    project: Callable[[Path], Path] | None  # cwd -> file
    global_: Callable[[], Path] | None  # -> file, or None (no global support)
    shape: Callable[[dict], dict]
    shape_global: Callable[[dict], dict] | None = None
    project_marker: Callable[[Path], Path] | None = None  # exists => agent used here
    global_via_cli: bool = False  # Claude Code: `claude mcp`
    placeholder: str | None = None  # how this tool spells ${NAME}, e.g. "${{env:{}}}"
    placeholder_verified: bool = True  # False: we could not confirm ${NAME} is expanded

    def path(self, global_: bool, cwd: Path) -> Path | None:
        if global_:
            return self.global_() if self.global_ else None
        return self.project(cwd) if self.project else None

    def config(self, cfg: dict, global_: bool) -> dict:
        if self.placeholder:
            cfg = _translate(cfg, self.placeholder)
        return (self.shape_global if global_ and self.shape_global else self.shape)(cfg)

    def caveats(self, cfg: dict, global_: bool) -> list[str]:
        """Things in cfg this tool may not handle (reported, not fatal)."""
        if not _has_placeholder(cfg):
            return []
        if self.fmt == "toml":
            if _has_placeholder(self.config(cfg, global_)):
                return [
                    f"{self.display} does not expand ${{VAR}} in this position; "
                    "edit the value after install"
                ]
            return []
        if not self.placeholder_verified:
            return [f"{self.display}: check that ${{VAR}} placeholders are expanded"]
        return []

    def used_in_project(self, cwd: Path) -> bool:
        return self.project_marker is None or self.project_marker(cwd).exists()


TARGETS: dict[str, McpTarget] = {
    t.agent: t
    for t in [
        McpTarget(
            "claude-code",
            "Claude Code",
            "mcpServers",
            "json",
            lambda cwd: cwd / ".mcp.json",
            lambda: _home() / ".claude.json",
            shape_standard,
            global_via_cli=True,
        ),
        McpTarget(
            "vscode",
            "VS Code",
            "servers",
            "json",
            lambda cwd: cwd / ".vscode" / "mcp.json",
            lambda: _vscode_user_dir() / "User" / "mcp.json",
            shape_vscode,
            project_marker=lambda cwd: cwd / ".vscode",
            placeholder="${{env:{}}}",
        ),
        McpTarget(
            "cursor",
            "Cursor",
            "mcpServers",
            "json",
            lambda cwd: cwd / ".cursor" / "mcp.json",
            lambda: _home() / ".cursor" / "mcp.json",
            shape_cursor,
            project_marker=lambda cwd: cwd / ".cursor",
            placeholder="${{env:{}}}",
        ),
        McpTarget(
            "codex",
            "Codex",
            "mcp_servers",
            "toml",
            lambda cwd: cwd / ".codex" / "config.toml",
            lambda: _codex_home() / "config.toml",
            shape_codex,
            project_marker=lambda cwd: cwd / ".codex",
        ),
        McpTarget(
            "gemini-cli",
            "Gemini CLI",
            "mcpServers",
            "json",
            lambda cwd: cwd / ".gemini" / "settings.json",
            lambda: _home() / ".gemini" / "settings.json",
            shape_gemini,
            project_marker=lambda cwd: cwd / ".gemini",
            placeholder_verified=False,
        ),
        McpTarget(
            "opencode",
            "OpenCode",
            "mcp",
            "json",
            _opencode_project,
            _opencode_global,
            shape_opencode,
            placeholder="{{env:{}}}",
            project_marker=lambda cwd: (
                _opencode_project(cwd) if _opencode_project(cwd).exists() else cwd / ".opencode"
            ),
        ),
        McpTarget(
            "github-copilot",
            "GitHub Copilot CLI",
            "mcpServers",
            "json",
            lambda cwd: _first_existing(
                [cwd / ".mcp.json", cwd / ".github" / "mcp.json"], cwd / ".mcp.json"
            ),
            lambda: _copilot_home() / "mcp-config.json",
            shape_standard,
            shape_global=shape_copilot_global,
            project_marker=lambda cwd: _first_existing(
                [cwd / ".mcp.json", cwd / ".github" / "mcp.json"], cwd / ".mcp.json"
            ),
        ),
        McpTarget(
            "windsurf",
            "Windsurf",
            "mcpServers",
            "json",
            None,
            lambda: _home() / ".codeium" / "windsurf" / "mcp_config.json",
            shape_windsurf,
            placeholder_verified=False,
        ),
    ]
}


@dataclass
class Placement:
    target: McpTarget
    file: Path | None  # None for Claude's global CLI
    global_: bool = False
    root: Path | None = None  # project root: reads/writes must stay inside it

    @property
    def label(self) -> str:
        return CLAUDE_CLI if self.file is None else str(self.file)


def plan(
    agents: list[str], global_: bool, cwd: Path, explicit: bool
) -> tuple[list[Placement], list[str]]:
    """
    Where to write an MCP server for these agents. Returns (placements, notes).

    Agents sharing one file (Claude Code and Copilot CLI use .mcp.json) get one
    placement. Without `explicit` agent selection, project files are only created
    for agents already set up in the project.
    """
    placements, notes, seen = [], [], set()
    for agent in agents:
        t = TARGETS.get(agent)
        if t is None:
            notes.append(f"{agent}: no MCP support in skillpack; skipped")
            continue
        if global_ and t.global_via_cli:
            file = None
        else:
            file = t.path(global_, cwd)
            if file is None:
                notes.append(f"{t.display}: no {'global' if global_ else 'project'} MCP config")
                continue
            if not global_ and not explicit and not t.used_in_project(cwd):
                notes.append(f"{t.display}: not set up in this project; skipped (use -a {agent})")
                continue
        key = (str(file), t.key)
        if key in seen:
            continue
        seen.add(key)
        placements.append(Placement(t, file, global_, None if global_ else cwd))
    return placements, notes


# --- reading / writing -------------------------------------------------------


def _claude(args: list[str]) -> subprocess.CompletedProcess:
    if not shutil.which("claude"):
        raise McpTargetError("needs the `claude` CLI on PATH (it manages ~/.claude.json)")
    return subprocess.run(["claude", *args], capture_output=True, text=True, timeout=60)


def _servers_json(p: Placement) -> tuple[dict, dict]:
    real_target(p.file, p.root)  # a project file must not lead outside the project
    data = read_json_object(p.file)  # raises ConfigFileError for JSONC/invalid files
    servers = data.setdefault(p.target.key, {})
    if not isinstance(servers, dict):
        raise ConfigFileError(f"{p.file}: '{p.target.key}' is not an object; not modifying it")
    return data, servers


def _toml_load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        raise ConfigFileError(
            f"{path} is not valid TOML ({e}); skillpack will not modify it"
        ) from e


def _toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        # JSON escapes (\\", \\\\, \\uXXXX for controls) are valid TOML basic strings;
        # other characters, including emoji, are written as-is
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return (
            "{ "
            + ", ".join(
                f"{json.dumps(k, ensure_ascii=False)} = {_toml_value(x)}" for k, x in v.items()
            )
            + " }"
        )
    raise McpTargetError(f"unsupported TOML value: {v!r}")


def _toml_block(table: str, name: str, cfg: dict) -> str:
    lines = [f"[{table}.{json.dumps(name, ensure_ascii=False)}]"]
    lines += [f"{k} = {_toml_value(v)}" for k, v in cfg.items()]
    return "\n".join(lines) + "\n"


def _toml_header_re(table: str, name: str) -> re.Pattern:
    quoted = "|".join(re.escape(q) for q in (json.dumps(name), f"'{name}'", name))
    return re.compile(rf"^\s*\[\s*{re.escape(table)}\s*\.\s*(?:{quoted})\s*(?:\..*)?\]\s*(#.*)?$")


def _toml_remove_block(text: str, table: str, name: str) -> str:
    """Remove `[table.name]` and its sub-tables; other content is untouched."""
    header = _toml_header_re(table, name)
    out, skipping = [], False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("[") and not stripped.startswith("[["):
            skipping = bool(header.match(line))
        elif stripped.startswith("[["):
            skipping = False
        if not skipping:
            out.append(line)
    return "".join(out)


def exists(p: Placement, name: str) -> bool:
    """True if a server called `name` is already configured at this placement."""
    if p.file is None:
        return _claude(["mcp", "get", name]).returncode == 0
    if p.target.fmt == "toml":
        real_target(p.file, p.root)
        return name in (_toml_load(p.file).get(p.target.key) or {})
    return name in _servers_json(p)[1]


def server_names(p: Placement) -> list[str]:
    """Names of the MCP servers configured at a placement (file-based targets only)."""
    if p.target.fmt == "toml":
        real_target(p.file, p.root)
        return list(_toml_load(p.file).get(p.target.key) or {})
    return list(_servers_json(p)[1])


def snippet(p: Placement, name: str, cfg: dict) -> str:
    """What to add by hand if skillpack can't edit the file."""
    shaped = p.target.config(cfg, p.global_)
    if p.target.fmt == "toml":
        return _toml_block(p.target.key, name, shaped)
    return json.dumps({p.target.key: {name: shaped}}, indent=2)


def write(p: Placement, name: str, cfg: dict) -> None:
    """Add or replace one server. Raises ConfigFileError/McpTargetError on failure."""
    shaped = p.target.config(cfg, p.global_)
    if p.file is None:
        # add-json won't overwrite, so an existing server must be removed first
        replacing = _claude(["mcp", "get", name]).returncode == 0
        if replacing:
            r = _claude(["mcp", "remove", "--scope", "user", name])
            if r.returncode != 0:
                raise McpTargetError(r.stderr.strip() or "claude mcp remove failed")
        r = _claude(["mcp", "add-json", "--scope", "user", name, json.dumps(shaped)])
        if r.returncode != 0:
            msg = r.stderr.strip() or "claude mcp add-json failed"
            if replacing:
                msg += f" (the previous '{name}' server was removed; re-add it if needed)"
            raise McpTargetError(msg)
        return
    if p.target.fmt == "toml":
        _write_toml(p.file, p.target.key, name, shaped, p.root)
        return
    data, servers = _servers_json(p)
    servers[name] = shaped
    write_json_atomic(p.file, data, confine=p.root)


def _write_toml(
    path: Path, table: str, name: str, cfg: dict | None, confine: Path | None = None
) -> bool:
    path = real_target(path, confine)  # follow dotfile symlinks, but not out of a project
    _toml_load(path)  # refuse invalid files before touching them
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    new = _toml_remove_block(text, table, name)
    removed = new != text
    if cfg is not None:
        if new and not new.endswith("\n"):
            new += "\n"
        new += ("\n" if new.strip() else "") + _toml_block(table, name, cfg)
    elif not removed:
        return False
    try:
        parsed = tomllib.loads(new)
    except tomllib.TOMLDecodeError as e:
        raise McpTargetError(f"could not safely edit {path}: {e}") from e
    present = name in (parsed.get(table) or {})
    if present != (cfg is not None):
        raise McpTargetError(f"could not safely edit {path} (server defined in another form?)")
    write_text_atomic(path, new)
    return True


def remove(p: Placement, name: str) -> bool:
    """Remove one server. Returns False if it wasn't there."""
    if p.file is None:
        if _claude(["mcp", "get", name]).returncode != 0:
            return False
        r = _claude(["mcp", "remove", "--scope", "user", name])
        if r.returncode != 0:
            raise McpTargetError(r.stderr.strip() or "claude mcp remove failed")
        return True
    if not p.file.exists():
        return False
    if p.target.fmt == "toml":
        return _write_toml(p.file, p.target.key, name, None, p.root)
    data, servers = _servers_json(p)
    if name not in servers:
        return False
    del servers[name]
    write_json_atomic(p.file, data, confine=p.root)
    return True


def placement_from_record(rec: dict, global_: bool, cwd: Path) -> Placement | None:
    """
    Rebuild a placement from a lock-file record {"agent": ...}.

    The file is recomputed from the agent table, never taken from the record:
    a project lock file is usually committed, so a cloned repository must not
    be able to point skillpack at arbitrary files.
    """
    t = TARGETS.get(rec.get("agent", "")) if isinstance(rec, dict) else None
    if t is None:
        return None
    if global_:
        file = None if t.global_via_cli else (t.global_() if t.global_ else None)
        if file is None and not t.global_via_cli:
            return None
        return Placement(t, file, True)
    file = t.path(False, cwd)
    return Placement(t, file, False, cwd) if file is not None else None


def to_record(p: Placement) -> dict:
    """Lock record: the agent, plus a portable (project-relative) file for display."""
    if p.file is None:
        shown = CLAUDE_CLI
    elif p.root is not None:
        shown = os.path.relpath(p.file, p.root)
    else:
        shown = str(p.file)
    return {"agent": p.target.agent, "file": Path(shown).as_posix()}


# Legacy lock entries (before per-agent MCP) were Claude Code only
def legacy_placements(global_: bool, cwd: Path) -> list[Placement]:
    t = TARGETS["claude-code"]
    return [Placement(t, None if global_ else cwd / ".mcp.json", global_, None if global_ else cwd)]
