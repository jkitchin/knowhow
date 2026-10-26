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
            "skillin will not overwrite it."
        ) from e
    if not isinstance(data, dict):
        raise ConfigFileError(f"{path} must contain a JSON object; skillin will not overwrite it.")
    return data


def write_json_atomic(path: Path, data, backup: bool = True) -> None:
    """
    Write JSON to `path` atomically (temp file + rename in the same directory).

    With `backup`, the previous contents are kept at `<path>.bak`.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        shutil.copy2(path, path.with_name(path.name + ".bak"))
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        if path.exists():
            shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def safe(text, max_len: int | None = None) -> str:
    """Repo-controlled text for a Rich table cell or message: one line, no escapes or markup."""
    from rich.markup import escape

    text = strip_controls("" if text is None else str(text), keep_newlines=False)
    if max_len is not None and len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return escape(text)
