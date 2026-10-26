"""Uninstall command for skillin."""

import shutil

import click
from rich.console import Console

from skillin.config import Config
from skillin.utils import confirm_action

console = Console()


@click.command()
@click.argument("name")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Target location (personal or project)",
)
@click.option(
    "--platform",
    "-p",
    default="claude",
    help="Target platform (claude, opencode, codex, gemini)",
)
@click.option("--type", "item_type", type=click.Choice(["skill", "command"]), help="Item type")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.option("--dry-run", is_flag=True, help="Preview without making changes")
@click.pass_context
def uninstall(ctx, name, target, platform, item_type, force, dry_run):
    """
    Uninstall a skill or command.

    NAME is the name of the skill or command to uninstall.
    """
    verbose = ctx.obj.get("verbose", False)
    config = Config()

    # Try to find the item
    found_items = []

    if not item_type or item_type == "skill":
        skills_dir = config.get_skills_dir(target, platform)
        skill_path = skills_dir / name
        if skill_path.exists() and (skill_path / "SKILL.md").exists():
            found_items.append(("skill", skill_path))

    if not item_type or item_type == "command":
        commands_dir = config.get_commands_dir(target, platform)
        # Try both with and without .md extension
        cmd_path = commands_dir / f"{name}.md" if not name.endswith(".md") else commands_dir / name
        if cmd_path.exists():
            found_items.append(("command", cmd_path))

    if not found_items:
        console.print(f"[red]Error: '{name}' not found in {target} for {platform}[/red]")
        raise click.Abort()

    if len(found_items) > 1:
        console.print("[yellow]Multiple items found. Please specify --type[/yellow]")
        for item_type, path in found_items:
            console.print(f"  - {item_type}: {path}")
        raise click.Abort()

    item_type, item_path = found_items[0]

    if verbose:
        console.print(f"Found {item_type}: {item_path}")

    # Confirmation
    if not force:
        if not confirm_action(f"Uninstall {item_type} '{name}'?", default=False):
            console.print("[yellow]Uninstall cancelled[/yellow]")
            return

    # Dry run
    if dry_run:
        console.print(f"[blue]Would uninstall {item_type} '{name}' from {item_path}[/blue]")
        return

    # Uninstall
    try:
        if item_path.is_dir():
            shutil.rmtree(item_path)
        else:
            item_path.unlink()
        console.print(f"[green]Successfully uninstalled {item_type} '{name}'[/green]")
    except Exception as e:
        console.print(f"[red]Error uninstalling {item_type}: {e}[/red]")
        raise click.Abort()
