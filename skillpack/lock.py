"""Lock files recording installed skills, compatible with `npx skills`.

- Global installs: `~/.agents/.skill-lock.json` (or
  `$XDG_STATE_HOME/skills/.skill-lock.json`), version 3, keyed by skill name.
- Project installs: `./skills-lock.json`, version 1, meant to be committed.

Unknown top-level keys and entry fields are preserved on rewrite so skillpack does
not clobber data written by `npx skills`.

Commands, hooks, subagents and MCP servers (which `npx skills` does not know about) are
tracked separately in `skillpack-lock.json` inside the Claude config directory
(`.claude/` or `~/.claude/`), next to the files it describes.
"""

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

from skillpack.safeio import ConfigFileError, read_json_object, write_json_atomic

GLOBAL_LOCK_VERSION = 3
LOCAL_LOCK_VERSION = 1
LOCAL_LOCK_FILE = "skills-lock.json"
EXTRAS_LOCK_FILE = "skillpack-lock.json"
LEGACY_EXTRAS_LOCK_FILE = "skillin-lock.json"  # name used by pre-release builds
EXTRAS_LOCK_VERSION = 1
EXTRA_KINDS = ("commands", "hooks", "subagents", "mcp")


def global_lock_path() -> Path:
    xdg_state = os.environ.get("XDG_STATE_HOME")
    if xdg_state:
        return Path(xdg_state) / "skills" / ".skill-lock.json"
    return Path.home() / ".agents" / ".skill-lock.json"


def local_lock_path(cwd: Path | None = None) -> Path:
    return (cwd or Path.cwd()) / LOCAL_LOCK_FILE


def portable_local_source(source: str, lock_dir: Path) -> str:
    """Relative `./path` form npx writes for local sources in project lock files."""
    rel = os.path.relpath(source, lock_dir)
    if os.path.isabs(rel):
        return Path(rel).as_posix()
    rel = Path(rel).as_posix()
    if rel == ".":
        return "."
    return rel if rel == ".." or rel.startswith("../") else f"./{rel}"


def resolve_local_source(source: str, lock_dir: Path) -> str:
    """Absolute path for a (possibly relative) local lock source."""
    return str((lock_dir / source).resolve()) if not os.path.isabs(source) else source


def lock_path(global_: bool, cwd: Path | None = None) -> Path:
    return global_lock_path() if global_ else local_lock_path(cwd)


def _read_lock_file(path: Path, key: str) -> dict | None:
    """
    Parsed lock file, None if absent; raise if it exists but is unusable.

    A damaged lock file (e.g. a merge conflict) is never silently replaced:
    that would drop entries written by other tools such as npx skills.
    """
    data = read_json_object(path)  # ConfigFileError on invalid JSON / non-object
    if not data:
        return None
    if key in data and not isinstance(data[key], dict):
        raise ConfigFileError(f"{path}: '{key}' is not an object; fix or move the file aside")
    return data


def read_lock(global_: bool, cwd: Path | None = None) -> dict:
    """Read a skills lock file (empty structure if missing; raises if damaged)."""
    version = GLOBAL_LOCK_VERSION if global_ else LOCAL_LOCK_VERSION
    data = _read_lock_file(lock_path(global_, cwd), "skills")
    if data is None:
        return {"version": version, "skills": {}}
    data.setdefault("version", version)
    data.setdefault("skills", {})
    return data


def write_lock(data: dict, global_: bool, cwd: Path | None = None) -> None:
    if not global_:
        data["skills"] = dict(sorted(data["skills"].items()))
    confine = None if global_ else (cwd or Path.cwd())
    write_json_atomic(lock_path(global_, cwd), data, backup=False, confine=confine)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def record_install(name: str, entry: dict, global_: bool, cwd: Path | None = None) -> None:
    """Add or update a skill entry, keeping fields we don't manage."""
    data = read_lock(global_, cwd)
    old = data["skills"].get(name, {})
    new = {**old, **{k: v for k, v in entry.items() if v is not None}}
    if global_:
        new.setdefault("installedAt", _now())
        new["updatedAt"] = _now()
    data["skills"][name] = new
    write_lock(data, global_, cwd)


def remove_entry(name: str, global_: bool, cwd: Path | None = None) -> bool:
    data = read_lock(global_, cwd)
    if name not in data["skills"]:
        return False
    del data["skills"][name]
    write_lock(data, global_, cwd)
    return True


# Approximates JavaScript's String.prototype.localeCompare (ICU root collation),
# which `npx skills` uses to order files before hashing: whitespace and punctuation
# sort before digits, digits before letters, letters case-insensitively first and
# lowercase-before-uppercase only to break ties.
_PUNCT_ORDER = "_-,;:!?.'\"()[]{}@*/\\&#%`^+<=>|~$"


def _collation_key(s: str):
    primary, tertiary = [], []
    for ch in s:
        if ch.isspace():
            primary.append((0, 0, ""))
        elif ch in _PUNCT_ORDER:
            primary.append((1, _PUNCT_ORDER.index(ch), ""))
        elif ch.isdigit():
            primary.append((3, int(ch) if ch.isascii() else ord(ch), ""))
        elif ch.isalpha():
            primary.append((4, 0, ch.casefold()))
        else:
            primary.append((2, ord(ch), ""))
        tertiary.append(1 if ch.isupper() else 0)
    return primary, tertiary


def compute_folder_hash(skill_dir: Path, npx_order: bool = True) -> str:
    """
    SHA-256 over sorted relative paths and contents (npx `computedHash`).

    Skips `.git` and `node_modules` directories. Files are ordered like npx
    (`localeCompare`); `npx_order=False` gives the codepoint order used by
    skillpack <= 0.1, which `check` still accepts for older lock entries.
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for fn in filenames:
            full = Path(dirpath) / fn
            if full.is_file() and not full.is_symlink():
                files.append((full.relative_to(skill_dir).as_posix(), full))
    files.sort(key=(lambda f: _collation_key(f[0])) if npx_order else (lambda f: f[0]))
    h = hashlib.sha256()
    for rel, full in files:
        h.update(rel.encode("utf-8"))
        h.update(full.read_bytes())
    return h.hexdigest()


def compute_file_hash(path: Path) -> str:
    """SHA-256 of a single file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extras_lock_path(claude_dir: Path) -> Path:
    return claude_dir / EXTRAS_LOCK_FILE


def _extras_lock_source(claude_dir: Path) -> Path:
    """The lock file to read: the current name, else a pre-release `skillin-lock.json`."""
    path = extras_lock_path(claude_dir)
    legacy = claude_dir / LEGACY_EXTRAS_LOCK_FILE
    return legacy if not path.exists() and legacy.is_file() else path


def read_extras_lock(claude_dir: Path) -> dict:
    """Read the commands/hooks/subagents/MCP lock (empty if missing; raises if damaged)."""
    source = _extras_lock_source(claude_dir)
    data = read_json_object(source) or {"version": EXTRAS_LOCK_VERSION}
    for kind in EXTRA_KINDS:
        if kind in data and not isinstance(data[kind], dict):
            raise ConfigFileError(f"{source}: '{kind}' is not an object")
        data.setdefault(kind, {})
    return data


def write_extras_lock(data: dict, claude_dir: Path) -> None:
    for kind in EXTRA_KINDS:
        data[kind] = dict(sorted(data[kind].items()))
    # a project's .claude/ lock must not be redirected outside the project
    from skillpack.agents_registry import _claude_home

    is_global = os.path.realpath(claude_dir) == os.path.realpath(_claude_home())
    confine = None if is_global else claude_dir.parent
    migrating = _extras_lock_source(claude_dir) != extras_lock_path(claude_dir)
    write_json_atomic(extras_lock_path(claude_dir), data, backup=False, confine=confine)
    if migrating:
        (claude_dir / LEGACY_EXTRAS_LOCK_FILE).unlink()  # its entries were read into `data`


def record_extra(kind: str, name: str, entry: dict, claude_dir: Path) -> None:
    data = read_extras_lock(claude_dir)
    old = data[kind].get(name, {})
    new = {**old, **{k: v for k, v in entry.items() if v is not None}}
    new.setdefault("installedAt", _now())
    new["updatedAt"] = _now()
    data[kind][name] = new
    write_extras_lock(data, claude_dir)


def remove_extra(kind: str, name: str, claude_dir: Path) -> bool:
    data = read_extras_lock(claude_dir)
    if name not in data[kind]:
        return False
    del data[kind][name]
    write_extras_lock(data, claude_dir)
    return True
