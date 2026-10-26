"""Careful file and terminal I/O for content that comes from untrusted repositories.

- strip_controls: remove terminal escape sequences / control characters before
  printing repo-controlled text (names, paths, script previews).
- read_json_object / write_json_atomic: edit users' JSON config files
  (settings.json, .mcp.json, lock files) without ever silently replacing a file
  we could not parse, and without leaving a half-written file behind.
"""

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

import click

# CSI, OSC (BEL or ST terminated), other ESC sequences, then remaining C0/C1 controls
_ESCAPES_RE = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]"
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?"
    r"|\x1b[PX^_][^\x1b]*(?:\x1b\\)?"
    r"|\x1b[@-Z\\-_]?"
)
_CONTROLS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def strip_controls(text: str, keep_newlines: bool = True) -> str:
    """Remove escape sequences and control characters (keeps \\n and \\t if asked)."""
    text = _ESCAPES_RE.sub("", str(text))
    text = _CONTROLS_RE.sub("", text)
    if not keep_newlines:
        text = text.replace("\n", " ").replace("\t", " ")
    return text


class ConfigFileError(click.ClickException):
    """A config file exists but cannot be safely read or updated."""


def read_json_object(path: Path) -> dict:
    """
    Read a JSON object from `path`; a missing or empty file is `{}`.

    Raises ConfigFileError (and changes nothing) if the file is not valid JSON or
    not an object, so callers never overwrite a file they could not parse.
    """
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise ConfigFileError(f"Cannot read {path}: {e}") from e
    if not text.strip():
        return {}
    try:
        data = json.loads(text)
    except ValueError as e:
        raise ConfigFileError(
            f"{path} is not valid JSON ({e}). Fix it (or move it aside) and retry; "
            "knowhow will not overwrite it."
        ) from e
    if not isinstance(data, dict):
        raise ConfigFileError(f"{path} must contain a JSON object; knowhow will not overwrite it.")
    return data


_BACKED_UP: set[str] = set()


def real_target(path: Path, confine: Path | None = None) -> Path:
    """
    The file a write to `path` should change: symlinks are followed (dotfiles
    setups keep working), but with `confine` the result must stay inside that
    directory, so a link planted in a project can't redirect writes elsewhere.
    """
    real = Path(os.path.realpath(path))
    if confine is not None:
        root = Path(os.path.realpath(confine))
        if real != root and root not in real.parents:
            raise ConfigFileError(
                f"{path} points outside {confine} (to {real}); knowhow will not modify it"
            )
    return real


def backup_once(real: Path) -> None:
    """Keep `<file>.bak` as the file was before this knowhow command first changed it."""
    if real.exists() and str(real) not in _BACKED_UP:
        shutil.copy2(real, real.with_name(real.name + ".bak"))
        _BACKED_UP.add(str(real))


def write_text_atomic(
    path: Path, text: str, backup: bool = True, confine: Path | None = None
) -> None:
    """Write text atomically (temp file + rename) to path's real target."""
    real = real_target(path, confine)
    real.parent.mkdir(parents=True, exist_ok=True)
    if backup:
        backup_once(real)
    fd, tmp = tempfile.mkstemp(prefix=f".{real.name}.", suffix=".tmp", dir=real.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        if real.exists():
            shutil.copymode(real, tmp)
        os.replace(tmp, real)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_json_atomic(path: Path, data, backup: bool = True, confine: Path | None = None) -> None:
    """
    Write JSON atomically to `path` (following symlinks, see real_target).

    With `backup`, the file as it was before this command is kept at `<file>.bak`.
    Non-ASCII text is written as-is.
    """
    write_text_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", backup, confine)


def safe(text, max_len: int | None = None) -> str:
    """Repo-controlled text for a Rich table cell or message: one line, no escapes or markup."""
    from rich.markup import escape

    text = strip_controls("" if text is None else str(text), keep_newlines=False)
    if max_len is not None and len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return escape(text)
