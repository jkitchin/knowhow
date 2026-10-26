"""Utility functions for claude-skills."""

import os
import re
import shutil
from pathlib import Path

from rich.console import Console

console = Console()


class PathTraversalError(Exception):
    """Raised when a path traversal attack is detected."""

    pass


def safe_path_join(base: Path, name: str) -> Path:
    """
    Safely join a base path with a name, preventing path traversal attacks.

    Args:
        base: The base directory path
        name: The name to join (e.g., skill name, hook name)

    Returns:
        The resolved path

    Raises:
        PathTraversalError: If the resulting path would escape the base directory
    """
    # Resolve the base to an absolute path
    base_resolved = base.resolve()

    # Join and resolve the result
    result = (base / name).resolve()

    # Check if the result is within the base directory
    try:
        result.relative_to(base_resolved)
    except ValueError:
        raise PathTraversalError(f"Path traversal detected: '{name}' would escape base directory")

    # Additional check for symlinks pointing outside base
    if result.is_symlink():
        real_path = result.resolve()
        try:
            real_path.relative_to(base_resolved)
        except ValueError:
            raise PathTraversalError(
                f"Symlink traversal detected: '{name}' points outside base directory"
            )

    return result


def validate_name(name: str, max_length: int = 64) -> bool:
    """
    Validate a skill or command name.

    Names must be lowercase, with numbers and hyphens only, max 64 chars.
    """
    pattern = r"^[a-z0-9-]+$"
    return isinstance(name, str) and bool(re.match(pattern, name) and len(name) <= max_length)


def validate_description(description: str, max_length: int = 1024) -> bool:
    """Validate a description is a string within the length limit."""
    return isinstance(description, str) and len(description) <= max_length


def copy_directory(src: Path, dst: Path, force: bool = False) -> bool:
    """
    Copy a directory from src to dst (symlink-safe).

    Args:
        src: Source directory
        dst: Destination directory
        force: If True, overwrite existing files

    Returns:
        True if successful, False otherwise

    Security:
        - Does not follow symlinks (copies symlink as-is or ignores)
        - Ignores dangling symlinks
    """
    try:
        if dst.exists() and not force:
            console.print(f"[yellow]Warning: {dst} already exists[/yellow]")
            return False

        if dst.exists():
            # Use onerror handler for safer removal
            shutil.rmtree(dst, ignore_errors=False)

        # Copy without following symlinks for security
        shutil.copytree(src, dst, symlinks=True, ignore_dangling_symlinks=True)
        return True
    except Exception as e:
        console.print(f"[red]Error copying directory: {e}[/red]")
        return False


def copy_file(src: Path, dst: Path, force: bool = False) -> bool:
    """
    Copy a file from src to dst.

    Args:
        src: Source file
        dst: Destination file
        force: If True, overwrite existing file

    Returns:
        True if successful, False otherwise
    """
    try:
        if dst.exists() and not force:
            console.print(f"[yellow]Warning: {dst} already exists[/yellow]")
            return False

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        console.print(f"[red]Error copying file: {e}[/red]")
        return False


def find_skill_directories(base_path: Path) -> list[Path]:
    """
    Find all skill directories (containing SKILL.md) in a base path.

    Args:
        base_path: Base directory to search

    Returns:
        List of paths to skill directories
    """
    skills = []
    if not base_path.exists():
        return skills

    # Follow symlinks: `skillin add` installs agent skills as symlinks to .agents/skills
    seen = set()
    for dirpath, dirnames, filenames in os.walk(base_path, followlinks=True):
        real = os.path.realpath(dirpath)
        if real in seen:
            dirnames[:] = []
            continue
        seen.add(real)
        if "SKILL.md" in filenames:
            skills.append(Path(dirpath))

    return sorted(skills)


def find_command_files(base_path: Path) -> list[Path]:
    """
    Find all command files (*.md) in a base path.

    Args:
        base_path: Base directory to search

    Returns:
        List of paths to command files
    """
    commands = []
    if not base_path.exists():
        return commands

    for item in base_path.rglob("*.md"):
        # Skip SKILL.md files
        if item.name != "SKILL.md":
            commands.append(item)

    return sorted(commands)


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.

    Args:
        message: Message to display
        default: Default response if user just presses enter

    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(message + suffix).lower().strip()

    if not response:
        return default

    return response in ("y", "yes")


def find_hook_directories(base_path: Path) -> list[Path]:
    """
    Find all hook directories (containing HOOK.md) in a base path.

    Args:
        base_path: Base directory to search

    Returns:
        List of paths to hook directories
    """
    hooks = []
    if not base_path.exists():
        return hooks

    for item in base_path.rglob("HOOK.md"):
        hooks.append(item.parent)

    return sorted(hooks)


def find_agent_files(base_path: Path) -> list[Path]:
    """
    Find all agent files (*.md) in a base path.

    Args:
        base_path: Base directory to search

    Returns:
        List of paths to agent files
    """
    agents = []
    if not base_path.exists():
        return agents

    for item in base_path.rglob("*.md"):
        # Skip template files and READMEs
        if item.name.upper() in ("README.MD", "TEMPLATE.MD"):
            continue
        agents.append(item)

    return sorted(agents)


_ITEM_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


def check_name_arg(ctx, param, value):
    """Click callback: an item name must be a single safe path component."""
    if value is None:
        return value
    if not _ITEM_NAME_RE.match(value) or ".." in value:
        import click

        raise click.BadParameter(f"invalid name {value!r} (letters, digits, '.', '_', '-')")
    return value
