"""List command for skillin."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from skillin.config import Config, platform_option
from skillin.safeio import safe
from skillin.utils import find_command_files, find_skill_directories
from skillin.validator import CommandValidator, SkillValidator

console = Console()


@click.command(name="list")
@click.option("--type", "item_type", type=click.Choice(["skill", "command", "all"]), default="all")
@click.option("--source", type=click.Choice(["repository", "installed", "all"]), default="all")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    help="Filter by installation target",
)
@platform_option("Filter by platform")
@click.option("--category", "-c", help="Filter by category")
@click.pass_context
def list_skills(ctx, item_type, source, target, platform, category):
    """
    List available skills and commands.

    By default, lists all items from both repository and installed locations.
    """
    verbose = ctx.obj.get("verbose", False)
    config = Config()

    # Collect items
    items = []

    # From repository
    if source in ["repository", "all"]:
        repo_path = config.get_repository_path()
        if repo_path and repo_path.exists():
            if item_type in ["skill", "all"]:
                items.extend(_list_repository_skills(repo_path, category, verbose))
            if item_type in ["command", "all"]:
                items.extend(_list_repository_commands(repo_path, category, verbose))

    # From installed
    if source in ["installed", "all"]:
        targets = [target] if target else ["personal", "project"]
        for tgt in targets:
            if item_type in ["skill", "all"]:
                items.extend(_list_installed_skills(config, tgt, platform, verbose))
            if item_type in ["command", "all"]:
                items.extend(_list_installed_commands(config, tgt, platform, verbose))

    # Display results
    if not items:
        console.print("[yellow]No items found[/yellow]")
        return

    # Create table
    table = Table(title="Skills and Commands")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Location", style="yellow")
    table.add_column("Description", style="white")

    for item in items:
        table.add_row(
            item["type"],
            safe(item["name"]),
            safe(item["location"]),
            safe(item.get("description", ""), 80),
        )

    console.print(table)


def _list_repository_skills(repo_path: Path, category: str, verbose: bool):
    """List skills from repository."""
    items = []
    skills_dir = repo_path / "skills"
    if not skills_dir.exists():
        return items

    for skill_path in find_skill_directories(skills_dir):
        # Filter by category
        if category:
            rel_path = skill_path.relative_to(skills_dir)
            if not str(rel_path).startswith(category):
                continue

        # Parse skill
        skill_file = skill_path / "SKILL.md"
        metadata = _parse_skill_metadata(skill_file)

        items.append(
            {
                "type": "skill",
                "name": skill_path.name,
                "location": "repository",
                "description": metadata.get("description", ""),
                "path": str(skill_path),
            }
        )

    return items


def _list_repository_commands(repo_path: Path, category: str, verbose: bool):
    """List commands from repository."""
    items = []
    commands_dir = repo_path / "commands"
    if not commands_dir.exists():
        return items

    for cmd_path in find_command_files(commands_dir):
        # Filter by category
        if category:
            rel_path = cmd_path.relative_to(commands_dir)
            if not str(rel_path.parent).startswith(category):
                continue

        # Parse command
        metadata = _parse_command_metadata(cmd_path)

        items.append(
            {
                "type": "command",
                "name": cmd_path.stem,
                "location": "repository",
                "description": metadata.get("description", ""),
                "path": str(cmd_path),
            }
        )

    return items


def _list_installed_skills(config: Config, target: str, platform: str, verbose: bool):
    """List installed skills."""
    items = []
    skills_dir = config.get_skills_dir(target, platform)

    if not skills_dir.exists():
        return items

    for skill_path in find_skill_directories(skills_dir):
        skill_file = skill_path / "SKILL.md"
        metadata = _parse_skill_metadata(skill_file)

        items.append(
            {
                "type": "skill",
                "name": skill_path.name,
                "location": f"{target}/{platform}",
                "description": metadata.get("description", ""),
                "path": str(skill_path),
            }
        )

    return items


def _list_installed_commands(config: Config, target: str, platform: str, verbose: bool):
    """List installed commands."""
    items = []
    commands_dir = config.get_commands_dir(target, platform)

    if not commands_dir.exists():
        return items

    for cmd_path in find_command_files(commands_dir):
        metadata = _parse_command_metadata(cmd_path)

        items.append(
            {
                "type": "command",
                "name": cmd_path.stem,
                "location": f"{target}/{platform}",
                "description": metadata.get("description", ""),
                "path": str(cmd_path),
            }
        )

    return items


def _parse_skill_metadata(skill_file: Path):
    """Parse metadata from SKILL.md."""
    try:
        frontmatter = SkillValidator._parse_frontmatter(skill_file.read_text())
        return frontmatter or {}
    except Exception:
        return {}


def _parse_command_metadata(cmd_file: Path):
    """Parse metadata from command file."""
    try:
        frontmatter = CommandValidator._parse_frontmatter(cmd_file.read_text())
        return frontmatter or {}
    except Exception:
        return {}
