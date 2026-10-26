"""Update command for skillin."""

from pathlib import Path

import click
from rich.console import Console

from skillin.config import Config, platform_option
from skillin.utils import (
    copy_directory,
    copy_file,
    find_command_files,
    find_skill_directories,
)
from skillin.validator import CommandValidator, SkillValidator

console = Console()


@click.command()
@click.argument("name", required=False)
@click.option("--all", "update_all", is_flag=True, help="Update all installed items")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Target location to update",
)
@platform_option("Target platform")
@click.option("--dry-run", is_flag=True, help="Preview without making changes")
@click.pass_context
def update(ctx, name, update_all, target, platform, dry_run):
    """
    Update installed skills and commands from the repository.

    NAME is the name of a specific item to update, or use --all to update everything.
    """
    verbose = ctx.obj.get("verbose", False)
    config = Config()

    if update_all and name:
        console.print("[red]Error: Cannot specify both NAME and --all[/red]")
        raise click.Abort()
    if not update_all and not name:
        console.print("[red]Error: Specify a name or use --all[/red]")
        raise click.Abort()

    # Get repository path
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        console.print("[red]Error: Repository path not configured or does not exist.[/red]")
        console.print("Run: skillin config set repository <path>")
        raise click.Abort()

    if update_all:
        _update_all_items(repo_path, config, target, platform, dry_run, verbose)
    else:
        _update_single_item(repo_path, config, name, target, platform, dry_run, verbose)


def _update_single_item(
    repo_path: Path,
    config: Config,
    name: str,
    target: str,
    platform: str,
    dry_run: bool,
    verbose: bool,
):
    """Update a single installed skill or command."""
    # Check if it's an installed skill
    skills_dir = config.get_skills_dir(target, platform)
    skill_dest = skills_dir / name
    is_skill = skill_dest.exists() and (skill_dest / "SKILL.md").exists()

    # Check if it's an installed command
    commands_dir = config.get_commands_dir(target, platform)
    cmd_dest = commands_dir / f"{name}.md"
    is_command = cmd_dest.exists()

    if not is_skill and not is_command:
        console.print(f"[red]Error: '{name}' is not installed in {target} for {platform}[/red]")
        raise click.Abort()

    if is_skill:
        source = _find_repo_skill(repo_path, name)
        if not source:
            console.print(f"[red]Error: Skill '{name}' not found in repository[/red]")
            raise click.Abort()

        valid, errors = SkillValidator.validate_skill_directory(source)
        if not valid:
            console.print(f"[red]Error: Invalid skill '{name}' in repository:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise click.Abort()

        if dry_run:
            console.print(f"[blue]Would update skill '{name}'[/blue]")
            return

        if verbose:
            console.print(f"Source: {source}")
            console.print(f"Destination: {skill_dest}")

        success = copy_directory(source, skill_dest, force=True)
        if success:
            console.print(f"[green]Updated skill '{name}'[/green]")
        else:
            console.print(f"[red]Failed to update skill '{name}'[/red]")

    if is_command:
        source = _find_repo_command(repo_path, name)
        if not source:
            console.print(f"[red]Error: Command '{name}' not found in repository[/red]")
            raise click.Abort()

        valid, errors = CommandValidator.validate_command_file(source)
        if not valid:
            console.print(f"[red]Error: Invalid command '{name}' in repository:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise click.Abort()

        if dry_run:
            console.print(f"[blue]Would update command '{name}'[/blue]")
            return

        if verbose:
            console.print(f"Source: {source}")
            console.print(f"Destination: {cmd_dest}")

        success = copy_file(source, cmd_dest, force=True)
        if success:
            console.print(f"[green]Updated command '{name}'[/green]")
        else:
            console.print(f"[red]Failed to update command '{name}'[/red]")


def _update_all_items(
    repo_path: Path,
    config: Config,
    target: str,
    platform: str,
    dry_run: bool,
    verbose: bool,
):
    """Update all installed skills and commands from repository."""
    skills_dir = config.get_skills_dir(target, platform)
    commands_dir = config.get_commands_dir(target, platform)

    # Build repo index for matching
    repo_skills = {p.name: p for p in _discover_repo_skills(repo_path)}
    repo_commands = {p.stem: p for p in _discover_repo_commands(repo_path)}

    # Find installed skills
    installed_skills = []
    if skills_dir.exists():
        for path in sorted(skills_dir.iterdir()):
            if path.is_dir() and (path / "SKILL.md").exists():
                installed_skills.append(path.name)

    # Find installed commands
    installed_commands = []
    if commands_dir.exists():
        for path in sorted(commands_dir.iterdir()):
            if path.is_file() and path.suffix == ".md":
                installed_commands.append(path.stem)

    if not installed_skills and not installed_commands:
        console.print("[yellow]No installed items found to update[/yellow]")
        return

    console.print(
        f"Found {len(installed_skills)} installed skills "
        f"and {len(installed_commands)} installed commands"
    )

    updated = 0
    skipped = 0
    errors = 0

    # Update skills
    for name in installed_skills:
        source = repo_skills.get(name)
        if not source:
            console.print(f"[yellow]Skipping skill '{name}' (not found in repository)[/yellow]")
            skipped += 1
            continue

        valid, errs = SkillValidator.validate_skill_directory(source)
        if not valid:
            console.print(f"[red]Skipping invalid skill '{name}':[/red]")
            for err in errs:
                console.print(f"  - {err}")
            errors += 1
            continue

        dest = skills_dir / name
        if dry_run:
            console.print(f"[blue]Would update skill '{name}'[/blue]")
            updated += 1
            continue

        if verbose:
            console.print(f"Updating skill '{name}': {source} -> {dest}")

        success = copy_directory(source, dest, force=True)
        if success:
            console.print(f"[green]Updated skill '{name}'[/green]")
            updated += 1
        else:
            console.print(f"[red]Failed to update skill '{name}'[/red]")
            errors += 1

    # Update commands
    for name in installed_commands:
        source = repo_commands.get(name)
        if not source:
            console.print(f"[yellow]Skipping command '{name}' (not found in repository)[/yellow]")
            skipped += 1
            continue

        valid, errs = CommandValidator.validate_command_file(source)
        if not valid:
            console.print(f"[red]Skipping invalid command '{name}':[/red]")
            for err in errs:
                console.print(f"  - {err}")
            errors += 1
            continue

        dest = commands_dir / f"{name}.md"
        if dry_run:
            console.print(f"[blue]Would update command '{name}'[/blue]")
            updated += 1
            continue

        if verbose:
            console.print(f"Updating command '{name}': {source} -> {dest}")

        success = copy_file(source, dest, force=True)
        if success:
            console.print(f"[green]Updated command '{name}'[/green]")
            updated += 1
        else:
            console.print(f"[red]Failed to update command '{name}'[/red]")
            errors += 1

    # Summary
    action = "Would update" if dry_run else "Updated"
    console.print(f"\n{action} {updated} items, skipped {skipped}, errors {errors}")


def _find_repo_skill(repo_path: Path, name: str) -> Path | None:
    """Find a skill by name in repository."""
    skills_dir = repo_path / "skills"
    if not skills_dir.exists():
        return None
    for skill_path in skills_dir.rglob("SKILL.md"):
        if skill_path.parent.name == name:
            return skill_path.parent
    return None


def _find_repo_command(repo_path: Path, name: str) -> Path | None:
    """Find a command by name in repository."""
    commands_dir = repo_path / "commands"
    if not commands_dir.exists():
        return None
    for cmd_path in commands_dir.rglob("*.md"):
        if cmd_path.stem == name:
            return cmd_path
    return None


def _discover_repo_skills(repo_path: Path) -> list:
    """Discover all skills in repository."""
    skills_dir = repo_path / "skills"
    if not skills_dir.exists():
        return []
    return list(find_skill_directories(skills_dir))


def _discover_repo_commands(repo_path: Path) -> list:
    """Discover all commands in repository."""
    commands_dir = repo_path / "commands"
    if not commands_dir.exists():
        return []
    return list(find_command_files(commands_dir))
