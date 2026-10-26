"""Hooks command group for knowhow."""

import os
import shlex
import shutil
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from knowhow.config import Config, platform_option
from knowhow.safeio import (
    ConfigFileError,
    read_json_object,
    real_target,
    safe,
    strip_controls,
    write_json_atomic,
)
from knowhow.utils import (
    PathTraversalError,
    check_name_arg,
    confirm_action,
    copy_directory,
    find_hook_directories,
    safe_path_join,
)
from knowhow.validator import HookValidator

console = Console()


@click.group()
def hooks():
    """Manage Claude Code hooks."""
    pass


@hooks.command("list")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project", "repo"]),
    default="personal",
    help="Which hooks to list",
)
@platform_option("Target platform")
@click.pass_context
def list_hooks(ctx, target, platform):
    """List installed hooks or available hooks in repository."""
    config = Config()

    if target == "repo":
        # List hooks from repository
        repo_path = config.get_repository_path()
        if not repo_path or not repo_path.exists():
            console.print("[red]Error: Repository path not configured.[/red]")
            console.print("Run: knowhow config set repository <path>")
            return

        hooks_dir = repo_path / "hooks"
        if not hooks_dir.exists():
            console.print("[yellow]No hooks directory in repository[/yellow]")
            return

        hook_dirs = find_hook_directories(hooks_dir)
    else:
        # List installed hooks
        hooks_dir = config.get_hooks_dir(target, platform)
        if not hooks_dir.exists():
            console.print(f"[yellow]No hooks installed ({hooks_dir})[/yellow]")
            return

        hook_dirs = find_hook_directories(hooks_dir)

    if not hook_dirs:
        console.print("[yellow]No hooks found[/yellow]")
        return

    # Create table
    table = Table(title=f"Hooks ({target})")
    table.add_column("Name", style="cyan")
    table.add_column("Event", style="green")
    table.add_column("Matcher", style="yellow")
    table.add_column("Description", style="white")

    for hook_path in hook_dirs:
        metadata = HookValidator.get_hook_metadata(hook_path)
        if metadata:
            table.add_row(
                safe(metadata.get("name", hook_path.name)),
                safe(metadata.get("event", "-")),
                safe(metadata.get("matcher", "*")),
                safe(_truncate(str(metadata.get("description", "")), 40)),
            )
        else:
            table.add_row(safe(hook_path.name), "-", "-", "[dim]Invalid hook[/dim]")

    console.print(table)


@hooks.command()
@click.argument("name", callback=check_name_arg)
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Installation target",
)
@platform_option("Target platform")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing hook")
@click.option("--dry-run", is_flag=True, help="Preview without making changes")
@click.option("--yes", "-y", is_flag=True, help="Skip script preview confirmation")
@click.pass_context
def install(ctx, name, target, platform, force, dry_run, yes):
    """Install a hook from the repository."""
    config = Config()
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # Platform was validated by platform_option (built-in or configured)

    # Get repository path
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        console.print("[red]Error: Repository path not configured.[/red]")
        console.print("Run: knowhow config set repository <path>")
        raise click.Abort()

    # Find hook in repository
    source_path = _find_hook(repo_path, name)
    if not source_path:
        console.print(f"[red]Error: Hook '{name}' not found in repository[/red]")
        raise click.Abort()

    # Validate hook
    valid, errors = HookValidator.validate_hook_directory(source_path)
    if not valid:
        console.print("[red]Error: Invalid hook:[/red]")
        for error in errors:
            console.print(f"  - {error}")
        raise click.Abort()

    # Get metadata
    metadata = HookValidator.get_hook_metadata(source_path)
    if not metadata:
        console.print("[red]Error: Could not read hook metadata[/red]")
        raise click.Abort()

    # Get destination using safe_path_join (security: prevent path traversal)
    dest_dir = config.get_hooks_dir(target, platform)
    try:
        dest_path = safe_path_join(dest_dir, name)
    except PathTraversalError as e:
        console.print(f"[red]Security error: {e}[/red]")
        raise click.Abort()

    if verbose:
        console.print(f"Source: {source_path}")
        console.print(f"Destination: {dest_path}")

    # Security: Show script preview before installation
    if not yes and not dry_run:
        console.print("\n[bold yellow]⚠ Hook Script Preview[/bold yellow]")
        console.print(
            "[dim]Hooks execute with your user privileges. Review before installing.[/dim]\n"
        )

        # Show script contents
        for script in list(source_path.glob("*.py")) + list(source_path.glob("*.sh")):
            console.print(f"[bold cyan]── {safe(script.name)} ──[/bold cyan]")
            content = script.read_text(errors="replace")
            # Show first 50 lines or entire file if smaller. Escape sequences are
            # stripped so a script can't rewrite the preview on screen.
            lines = content.split("\n")
            preview_lines = lines[:50]
            console.print(Text(strip_controls("\n".join(preview_lines))))
            if len(lines) > 50:
                console.print(f"[dim]... ({len(lines) - 50} more lines)[/dim]")
            console.print()

        if not confirm_action("Install this hook?", default=False):
            console.print("[yellow]Installation cancelled[/yellow]")
            return

    # Check if already exists
    if dest_path.exists() and not force:
        if not confirm_action(f"Hook '{name}' already exists. Overwrite?", default=False):
            console.print("[yellow]Installation cancelled[/yellow]")
            return

    # Dry run
    if dry_run:
        console.print(f"[blue]Would install hook '{name}' to {dest_path}[/blue]")
        console.print("[blue]Would update settings.json with hook configuration[/blue]")
        return

    # Install hook files
    dest_dir.mkdir(parents=True, exist_ok=True)
    success = copy_directory(source_path, dest_path, force=True)

    if not success:
        console.print(f"[red]Failed to install hook '{name}'[/red]")
        raise click.Abort()

    # Make scripts executable
    for script in dest_path.glob("*.py"):
        os.chmod(script, 0o755)
    for script in dest_path.glob("*.sh"):
        os.chmod(script, 0o755)

    # Update settings.json
    settings_file = config.get_settings_file(target, platform)
    _add_hook_to_settings(
        settings_file, dest_path, metadata, Path.cwd() if target == "project" else None
    )

    console.print(f"[green]Successfully installed hook '{name}'[/green]")
    console.print(f"[dim]Hook files: {dest_path}[/dim]")
    console.print(f"[dim]Settings updated: {settings_file}[/dim]")


@hooks.command()
@click.argument("name", callback=check_name_arg)
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Uninstall target",
)
@platform_option("Target platform")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.pass_context
def uninstall(ctx, name, target, platform, force):
    """Uninstall a hook."""
    config = Config()

    hooks_dir = config.get_hooks_dir(target, platform)
    hook_path = hooks_dir / name

    if not hook_path.exists():
        console.print(f"[red]Error: Hook '{name}' is not installed[/red]")
        raise click.Abort()

    # Get metadata before removal
    metadata = HookValidator.get_hook_metadata(hook_path)

    if not force:
        if not confirm_action(f"Uninstall hook '{name}'?", default=False):
            console.print("[yellow]Uninstall cancelled[/yellow]")
            return

    # Unregister first, so a failure below can't leave settings.json pointing
    # at a deleted script
    settings_file = config.get_settings_file(target, platform)
    _remove_hook_from_settings(
        settings_file, hook_path, metadata, Path.cwd() if target == "project" else None
    )

    # Remove hook directory
    try:
        shutil.rmtree(hook_path)
    except Exception as e:
        console.print(f"[red]Error removing hook: {e}[/red]")
        raise click.Abort()

    console.print(f"[green]Successfully uninstalled hook '{name}'[/green]")


@hooks.command()
@click.argument("name", callback=check_name_arg)
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project", "repo"]),
    default="repo",
    help="Where to look for the hook",
)
@platform_option("Target platform")
@click.pass_context
def info(ctx, name, target, platform):
    """Show detailed information about a hook."""
    config = Config()

    if target == "repo":
        repo_path = config.get_repository_path()
        if not repo_path:
            console.print("[red]Error: Repository path not configured.[/red]")
            raise click.Abort()
        hook_path = _find_hook(repo_path, name)
    else:
        hooks_dir = config.get_hooks_dir(target, platform)
        hook_path = hooks_dir / name

    if not hook_path or not hook_path.exists():
        console.print(f"[red]Error: Hook '{name}' not found[/red]")
        raise click.Abort()

    # Validate
    valid, errors = HookValidator.validate_hook_directory(hook_path)
    metadata = HookValidator.get_hook_metadata(hook_path)

    console.print(f"\n[bold cyan]Hook: {name}[/bold cyan]")
    console.print(f"[dim]Path: {hook_path}[/dim]\n")

    if metadata:
        console.print(f"[green]Event:[/green] {safe(metadata.get('event', '-'))}")
        console.print(f"[green]Matcher:[/green] {safe(metadata.get('matcher', '*'))}")
        console.print(f"[green]Type:[/green] {safe(metadata.get('type', 'command'))}")
        console.print(f"[green]Timeout:[/green] {safe(metadata.get('timeout', 60))}s")
        console.print(f"\n[green]Description:[/green]\n{safe(metadata.get('description', '-'))}")

    # List files
    console.print("\n[green]Files:[/green]")
    for f in sorted(hook_path.iterdir()):
        if f.is_file():
            console.print(f"  - {f.name}")

    if not valid:
        console.print("\n[red]Validation errors:[/red]")
        for error in errors:
            console.print(f"  - {error}")


@hooks.command()
@click.argument("query", required=False)
@click.pass_context
def search(ctx, query):
    """Search for hooks in the repository."""
    config = Config()

    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        console.print("[red]Error: Repository path not configured.[/red]")
        console.print("Run: knowhow config set repository <path>")
        raise click.Abort()

    hooks_dir = repo_path / "hooks"
    if not hooks_dir.exists():
        console.print("[yellow]No hooks directory in repository[/yellow]")
        return

    hook_dirs = find_hook_directories(hooks_dir)

    if not hook_dirs:
        console.print("[yellow]No hooks found in repository[/yellow]")
        return

    # Filter by query if provided
    results = []
    for hook_path in hook_dirs:
        metadata = HookValidator.get_hook_metadata(hook_path)
        if metadata:
            name = metadata.get("name", hook_path.name)
            desc = metadata.get("description", "")
            event = metadata.get("event", "")

            if not query or _matches_query(query, name, desc, event):
                results.append((hook_path, metadata))

    if not results:
        console.print(f"[yellow]No hooks matching '{query}'[/yellow]")
        return

    # Display results
    table = Table(title="Search Results")
    table.add_column("Name", style="cyan")
    table.add_column("Event", style="green")
    table.add_column("Description", style="white")

    for hook_path, metadata in results:
        table.add_row(
            safe(metadata.get("name", hook_path.name)),
            safe(metadata.get("event", "-")),
            safe(_truncate(str(metadata.get("description", "")), 50)),
        )

    console.print(table)


@hooks.command()
@click.argument("name", callback=check_name_arg)
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Where to create the hook",
)
@platform_option("Target platform")
@click.option(
    "--event",
    "-e",
    type=click.Choice(
        [
            "PreToolUse",
            "PostToolUse",
            "PermissionRequest",
            "UserPromptSubmit",
            "Notification",
            "Stop",
            "SubagentStop",
            "PreCompact",
            "SessionStart",
            "SessionEnd",
        ]
    ),
    default="PostToolUse",
    help="Hook event type",
)
@click.option(
    "--prompt",
    help="Description prompt - use Claude to generate hook content",
)
@click.pass_context
def create(ctx, name, target, platform, event, prompt):
    """Create a new hook from template or AI-generated.

    If --prompt is provided, uses Claude CLI to generate the hook content
    based on your description.
    """
    config = Config()

    hooks_dir = config.get_hooks_dir(target, platform)
    hook_path = hooks_dir / name

    if hook_path.exists():
        console.print(f"[red]Error: Hook '{name}' already exists at {hook_path}[/red]")
        raise click.Abort()

    # Create hook directory
    hook_path.mkdir(parents=True, exist_ok=True)

    if prompt:
        # Use Claude to generate the hook
        hook_md, hook_script = _generate_hook_with_claude(name, prompt, event)
        if not hook_md or not hook_script:
            console.print("[red]Failed to generate hook with Claude[/red]")
            # Clean up empty directory
            hook_path.rmdir()
            raise click.Abort()
    else:
        # Create from template
        hook_md = f"""---
name: {name}
description: Description of what this hook does
event: {event}
matcher: "*"
type: command
timeout: 60
---

# {name.replace("-", " ").title()}

## Purpose

[Describe what this hook does]

## Behavior

[Describe the hook's behavior]

## Requirements

- Python 3.8+
"""
        hook_script = f'''#!/usr/bin/env python3
"""{name} hook for Claude Code."""

import json
import sys


def main():
    """Main hook entry point."""
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {{e}}", file=sys.stderr)
        sys.exit(1)

    # Extract relevant fields
    session_id = input_data.get("session_id", "")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {{}})
    cwd = input_data.get("cwd", "")

    # Your hook logic here
    # ...

    # Exit codes:
    # 0 = success (allow operation)
    # 2 = block operation (for PreToolUse, etc.)
    sys.exit(0)


if __name__ == "__main__":
    main()
'''

    (hook_path / "HOOK.md").write_text(hook_md)
    script_path = hook_path / "hook.py"
    script_path.write_text(hook_script)
    os.chmod(script_path, 0o755)

    console.print(f"[green]Created hook '{name}' at {hook_path}[/green]")
    console.print("\nFiles created:")
    console.print(f"  - {hook_path / 'HOOK.md'}")
    console.print(f"  - {hook_path / 'hook.py'}")
    if not prompt:
        console.print("\n[dim]Edit these files, then run:[/dim]")
        console.print(f"  knowhow hooks install {name} --target {target}")


# Helper functions


def _find_hook(repo_path: Path, name: str) -> Path | None:
    """Find a hook by name in repository."""
    hooks_dir = repo_path / "hooks"
    if not hooks_dir.exists():
        return None

    for hook_path in hooks_dir.rglob("HOOK.md"):
        if hook_path.parent.name == name:
            return hook_path.parent

    return None


def _truncate(text: str, max_length: int) -> str:
    """Truncate text to max length."""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def _matches_query(query: str, *fields: str) -> bool:
    """Check if query matches any of the fields."""
    query_lower = query.lower()
    for field in fields:
        if query_lower in field.lower():
            return True
    return False


def _get_hook_command(hook_path: Path) -> str:
    """Get the command to run for a hook."""
    # Prefer Python script, then shell script
    py_script = hook_path / "hook.py"
    sh_script = hook_path / "hook.sh"

    if py_script.exists():
        return str(py_script)
    elif sh_script.exists():
        return str(sh_script)
    elif hook_path.is_dir():
        # Look for any executable
        for f in sorted(hook_path.iterdir()):
            if f.is_file() and f.suffix in (".py", ".sh"):
                return str(f)
    return str(hook_path / "hook.py")


def _hook_command(hook_path: Path, project_root: Path | None = None) -> str:
    """
    The settings.json command for a hook, safe to run through a shell.

    Project hooks use "$CLAUDE_PROJECT_DIR"/... so a committed settings.json works
    for everyone; global hooks use the quoted absolute path.
    """
    script = Path(os.path.abspath(_get_hook_command(hook_path)))
    if project_root is not None:
        try:
            rel = script.relative_to(Path(os.path.abspath(project_root)))
            return '"$CLAUDE_PROJECT_DIR"/' + shlex.quote(rel.as_posix())
        except ValueError:
            pass
    return shlex.quote(str(script))


def _is_hook_command(command, hook_path: Path, project_root: Path | None = None) -> bool:
    """True if a settings.json command runs a script inside hook_path (any form we write)."""
    if not isinstance(command, str):
        return False
    plain = command.replace('"', "").replace("'", "")
    hook_abs = os.path.abspath(hook_path)
    prefixes = {str(hook_path).rstrip(os.sep) + os.sep, hook_abs.rstrip(os.sep) + os.sep}
    if project_root is not None:
        try:
            rel = Path(hook_abs).relative_to(Path(os.path.abspath(project_root))).as_posix()
            prefixes.add(f"$CLAUDE_PROJECT_DIR/{rel}/")
        except ValueError:
            pass
    return any(plain.startswith(p) for p in prefixes)


def _strip_hook(settings: dict, hook_path: Path, project_root: Path | None = None) -> bool:
    """Remove every entry for hook_path from every event. Returns True if any removed."""
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return False
    removed = False
    for event in list(hooks):
        entries = hooks[event]
        if not isinstance(entries, list):
            continue
        kept = []
        for entry in entries:
            inner = entry.get("hooks") if isinstance(entry, dict) else None
            if not isinstance(inner, list):
                kept.append(entry)
                continue
            new_inner = [
                h
                for h in inner
                if not (
                    isinstance(h, dict)
                    and _is_hook_command(h.get("command"), hook_path, project_root)
                )
            ]
            removed |= len(new_inner) != len(inner)
            if new_inner:
                kept.append({**entry, "hooks": new_inner})
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    return removed


def check_settings_file(settings_file: Path, project_root: Path | None = None) -> dict:
    """
    Read settings.json, or raise if knowhow could not safely update it (invalid
    JSON, or a project file that links outside the project). Changes nothing.
    """
    real_target(settings_file, project_root)
    return read_json_object(settings_file)


def _add_hook_to_settings(
    settings_file: Path, hook_path: Path, metadata: dict, project_root: Path | None = None
):
    """
    Register a hook in settings.json.

    Refuses (without writing) if the file exists but is not a valid JSON object,
    replaces any earlier registration of this hook under any event, writes
    atomically and keeps the previous file as settings.json.bak. With
    `project_root`, the command is written relative to $CLAUDE_PROJECT_DIR.
    """
    if metadata.get("type", "command") != "command":
        raise click.ClickException(
            f"Hook {hook_path.name}: only `type: command` hooks can be installed by knowhow"
        )
    settings = check_settings_file(settings_file, project_root)
    _strip_hook(settings, hook_path, project_root)
    if not isinstance(settings.get("hooks"), dict):
        settings["hooks"] = {}

    event = metadata.get("event", "PostToolUse")
    hook = {
        "type": "command",
        "command": _hook_command(hook_path, project_root),
        "timeout": metadata.get("timeout", 60),
    }
    entry = {"matcher": metadata.get("matcher", "*"), "hooks": [hook]}
    events = settings["hooks"].setdefault(event, [])
    if not isinstance(events, list):
        raise ConfigFileError(f"{settings_file}: hooks.{event} is not a list; not modifying it")
    events.append(entry)
    write_json_atomic(settings_file, settings, confine=project_root)


def _remove_hook_from_settings(
    settings_file: Path,
    hook_path: Path,
    metadata: dict | None = None,
    project_root: Path | None = None,
):
    """
    Remove every registration of a hook (any event) from settings.json.

    Works after the hook directory has been deleted, and matches commands written
    by any knowhow version. Refuses to rewrite a file that is not valid JSON.
    """
    if not settings_file.exists():
        return
    settings = check_settings_file(settings_file, project_root)
    if _strip_hook(settings, hook_path, project_root):
        if settings.get("hooks") == {}:
            del settings["hooks"]  # don't leave an empty block behind
        write_json_atomic(settings_file, settings, confine=project_root)


def _generate_hook_with_claude(name: str, prompt: str, event: str) -> tuple[str | None, str | None]:
    """Use Claude CLI to generate hook content."""
    generation_prompt = f"""Generate a Claude Code hook for the following:

Name: {name}
Event: {event}
Description/Purpose: {prompt}

Create TWO files:

1. HOOK.md - A markdown file with:
   - YAML frontmatter (name, description, event, matcher, type, timeout)
   - Documentation of what the hook does
   - Requirements section

2. hook.py - A Python script that:
   - Reads JSON input from stdin
   - Implements the hook logic based on the description
   - Uses appropriate exit codes (0=success, 2=block)

Output format - provide BOTH files separated by this exact marker:
===HOOK_SCRIPT===

Start with the HOOK.md content (beginning with ---), then the marker, then the Python script.
Do not include any explanation, just the file contents."""

    try:
        result = subprocess.run(
            ["claude", "-p", generation_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()

            # Split into HOOK.md and hook.py
            if "===HOOK_SCRIPT===" in output:
                parts = output.split("===HOOK_SCRIPT===")
                hook_md = parts[0].strip()
                hook_script = parts[1].strip() if len(parts) > 1 else None

                # Ensure HOOK.md starts with frontmatter
                if not hook_md.startswith("---"):
                    hook_md = "---\n" + hook_md

                # Ensure hook.py has shebang
                if hook_script and not hook_script.startswith("#!"):
                    hook_script = "#!/usr/bin/env python3\n" + hook_script

                return hook_md, hook_script
            else:
                console.print("[yellow]Could not parse Claude output[/yellow]")
                return None, None
        else:
            console.print(f"[yellow]Claude CLI error: {result.stderr}[/yellow]")
            return None, None

    except FileNotFoundError:
        console.print("[yellow]Claude CLI not found. Install it or create hook manually.[/yellow]")
        return None, None
    except subprocess.TimeoutExpired:
        console.print("[yellow]Claude CLI timed out[/yellow]")
        return None, None
    except Exception as e:
        console.print(f"[yellow]Error running Claude CLI: {e}[/yellow]")
        return None, None
