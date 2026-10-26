"""Search command for knowhow."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from knowhow.config import Config
from knowhow.safeio import safe
from knowhow.utils import find_command_files, find_skill_directories
from knowhow.validator import CommandValidator, SkillValidator

console = Console()


@click.command()
@click.argument("query")
@click.option("--type", "item_type", type=click.Choice(["skill", "command", "all"]), default="all")
@click.pass_context
def search(ctx, query, item_type):
    """
    Search for skills and commands by keyword.

    QUERY is the search term to look for in names and descriptions.
    """
    _ = ctx.obj.get("verbose", False)  # Reserved for future use
    config = Config()

    # Get repository path
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        console.print("[yellow]Warning: Repository path not configured[/yellow]")
        return

    # Collect matches
    matches = []

    # Search skills
    if item_type in ["skill", "all"]:
        skills_dir = repo_path / "skills"
        if skills_dir.exists():
            for skill_path in find_skill_directories(skills_dir):
                skill_file = skill_path / "SKILL.md"
                metadata = _parse_skill_metadata(skill_file)

                # Check if query matches name or description
                if _matches_query(query, skill_path.name, metadata.get("description", "")):
                    matches.append(
                        {
                            "type": "skill",
                            "name": skill_path.name,
                            "description": metadata.get("description", ""),
                            "path": str(skill_path.relative_to(repo_path)),
                        }
                    )

    # Search commands
    if item_type in ["command", "all"]:
        commands_dir = repo_path / "commands"
        if commands_dir.exists():
            for cmd_path in find_command_files(commands_dir):
                metadata = _parse_command_metadata(cmd_path)

                # Check if query matches name or description
                if _matches_query(query, cmd_path.stem, metadata.get("description", "")):
                    matches.append(
                        {
                            "type": "command",
                            "name": cmd_path.stem,
                            "description": metadata.get("description", ""),
                            "path": str(cmd_path.relative_to(repo_path)),
                        }
                    )

    # Display results
    if not matches:
        console.print(f"[yellow]No results found for '{query}'[/yellow]")
        return

    table = Table(title=f"Search Results for '{query}'")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    table.add_column("Path", style="dim")

    for match in matches:
        table.add_row(
            match["type"],
            safe(match["name"]),
            safe(match["description"], 80),
            safe(match["path"]),
        )

    console.print(table)
    console.print(f"\n[green]Found {len(matches)} result(s)[/green]")


def _matches_query(query: str, name: str, description: str) -> bool:
    """Check if query matches name or description."""
    query_lower = query.lower()
    return query_lower in name.lower() or query_lower in description.lower()


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
