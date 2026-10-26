"""Info command for skillin."""

from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from skillin.config import Config
from skillin.validator import CommandValidator, SkillValidator

console = Console()


@click.command()
@click.argument("name")
@click.option("--type", "item_type", type=click.Choice(["skill", "command"]), help="Item type")
@click.option(
    "--source",
    type=click.Choice(["repository", "installed"]),
    default="repository",
    help="Where to look for the item",
)
@click.option("--show-content", is_flag=True, help="Display full content")
@click.pass_context
def info(ctx, name, item_type, source, show_content):
    """
    Display detailed information about a skill or command.

    NAME is the name of the skill or command to inspect.
    """
    verbose = ctx.obj.get("verbose", False)
    config = Config()

    # Find the item
    item_path = None
    detected_type = None

    if source == "repository":
        repo_path = config.get_repository_path()
        if not repo_path or not repo_path.exists():
            console.print("[red]Error: Repository path not configured[/red]")
            raise click.Abort()

        item_path, detected_type = _find_in_repository(repo_path, name, item_type)

    else:  # installed
        # Try to find in installed locations
        item_path, detected_type = _find_installed(config, name, item_type)

    if not item_path:
        console.print(f"[red]Error: '{name}' not found[/red]")
        raise click.Abort()

    # Display information based on type
    if detected_type == "skill":
        _display_skill_info(item_path, show_content, verbose)
    else:
        _display_command_info(item_path, show_content, verbose)


def _find_in_repository(repo_path: Path, name: str, item_type: str):
    """Find item in repository."""
    # Try skill
    if not item_type or item_type == "skill":
        skills_dir = repo_path / "skills"
        if skills_dir.exists():
            for skill_path in skills_dir.rglob("SKILL.md"):
                if skill_path.parent.name == name:
                    return skill_path.parent, "skill"

    # Try command
    if not item_type or item_type == "command":
        commands_dir = repo_path / "commands"
        if commands_dir.exists():
            for cmd_path in commands_dir.rglob("*.md"):
                if cmd_path.stem == name:
                    return cmd_path, "command"

    return None, None


def _find_installed(config: Config, name: str, item_type: str):
    """Find item in installed locations."""
    # Try personal and project locations
    for target in ["personal", "project"]:
        # Try skill
        if not item_type or item_type == "skill":
            skills_dir = config.get_skills_dir(target, "claude")
            skill_path = skills_dir / name
            if skill_path.exists() and (skill_path / "SKILL.md").exists():
                return skill_path, "skill"

        # Try command
        if not item_type or item_type == "command":
            commands_dir = config.get_commands_dir(target, "claude")
            cmd_path = commands_dir / f"{name}.md"
            if cmd_path.exists():
                return cmd_path, "command"

    return None, None


def _display_skill_info(skill_path: Path, show_content: bool, verbose: bool):
    """Display information about a skill."""
    skill_file = skill_path / "SKILL.md"

    # Validate skill
    valid, errors = SkillValidator.validate_skill_directory(skill_path)

    # Parse metadata
    content = skill_file.read_text()
    metadata = SkillValidator._parse_frontmatter(content)

    # Display metadata panel
    metadata_text = f"[bold cyan]Name:[/bold cyan] {metadata.get('name', 'N/A')}\n"
    metadata_text += f"[bold cyan]Description:[/bold cyan] {metadata.get('description', 'N/A')}\n"
    metadata_text += f"[bold cyan]Location:[/bold cyan] {skill_path}\n"
    metadata_text += "[bold cyan]Type:[/bold cyan] Skill\n"

    if "allowed-tools" in metadata:
        tools = metadata["allowed-tools"]
        if tools == "*":
            metadata_text += "[bold cyan]Allowed Tools:[/bold cyan] All\n"
        else:
            metadata_text += f"[bold cyan]Allowed Tools:[/bold cyan] {', '.join(tools)}\n"

    # Validation status
    if valid:
        metadata_text += "[bold green]Status:[/bold green] ✓ Valid"
    else:
        metadata_text += "[bold red]Status:[/bold red] ✗ Invalid\n"
        for error in errors:
            metadata_text += f"  [red]• {error}[/red]\n"

    console.print(Panel(metadata_text, title="Skill Information", border_style="cyan"))

    # List files in skill directory
    console.print("\n[bold]Files:[/bold]")
    files_table = Table(show_header=True, header_style="bold")
    files_table.add_column("File", style="cyan")
    files_table.add_column("Size", justify="right")
    files_table.add_column("Type")

    for file_path in sorted(skill_path.iterdir()):
        if file_path.is_file():
            size = file_path.stat().st_size
            size_str = _format_size(size)
            file_type = _get_file_type(file_path)
            files_table.add_row(file_path.name, size_str, file_type)

    console.print(files_table)

    # Show content preview or full content
    if show_content:
        console.print("\n[bold]Full Content:[/bold]")
        console.print(Markdown(content))
    else:
        console.print("\n[bold]Content Preview:[/bold]")
        lines = content.split("\n")

        # Skip frontmatter
        start_idx = 0
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker != -1:
                start_idx = content[: end_marker + 3].count("\n")

        # Show first 30 lines
        preview_lines = lines[start_idx : start_idx + 30]
        preview = "\n".join(preview_lines)

        console.print(Markdown(preview))

        if len(lines) > start_idx + 30:
            console.print(
                f"\n[dim]... ({len(lines) - start_idx - 30} more lines) "
                f"Use --show-content to see full content[/dim]"
            )


def _display_command_info(cmd_path: Path, show_content: bool, verbose: bool):
    """Display information about a command."""
    # Validate command
    valid, errors = CommandValidator.validate_command_file(cmd_path)

    # Parse metadata
    content = cmd_path.read_text()
    metadata = CommandValidator._parse_frontmatter(content) or {}

    # Display metadata panel
    metadata_text = f"[bold cyan]Name:[/bold cyan] {cmd_path.stem}\n"
    metadata_text += f"[bold cyan]Description:[/bold cyan] {metadata.get('description', 'N/A')}\n"
    metadata_text += f"[bold cyan]Location:[/bold cyan] {cmd_path}\n"
    metadata_text += "[bold cyan]Type:[/bold cyan] Command\n"

    if "model" in metadata:
        metadata_text += f"[bold cyan]Model:[/bold cyan] {metadata['model']}\n"

    if "argument-hint" in metadata:
        metadata_text += f"[bold cyan]Argument Hint:[/bold cyan] {metadata['argument-hint']}\n"

    if "allowed-tools" in metadata:
        tools = metadata["allowed-tools"]
        if tools == "*":
            metadata_text += "[bold cyan]Allowed Tools:[/bold cyan] All\n"
        else:
            metadata_text += f"[bold cyan]Allowed Tools:[/bold cyan] {', '.join(tools)}\n"

    # Validation status
    if valid:
        metadata_text += "[bold green]Status:[/bold green] ✓ Valid"
    else:
        metadata_text += "[bold red]Status:[/bold red] ✗ Invalid\n"
        for error in errors:
            metadata_text += f"  [red]• {error}[/red]\n"

    console.print(Panel(metadata_text, title="Command Information", border_style="cyan"))

    # Show content
    if show_content:
        console.print("\n[bold]Full Content:[/bold]")
        console.print(Markdown(content))
    else:
        console.print("\n[bold]Content Preview:[/bold]")
        lines = content.split("\n")

        # Skip frontmatter if present
        start_idx = 0
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker != -1:
                start_idx = content[: end_marker + 3].count("\n")

        # Show first 30 lines
        preview_lines = lines[start_idx : start_idx + 30]
        preview = "\n".join(preview_lines)

        console.print(Markdown(preview))

        if len(lines) > start_idx + 30:
            console.print(
                f"\n[dim]... ({len(lines) - start_idx - 30} more lines) "
                f"Use --show-content to see full content[/dim]"
            )


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def _get_file_type(file_path: Path) -> str:
    """Get file type description."""
    suffix = file_path.suffix.lower()
    types = {
        ".md": "Markdown",
        ".py": "Python",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".json": "JSON",
        ".txt": "Text",
        ".sh": "Shell",
    }
    return types.get(suffix, "Unknown")
