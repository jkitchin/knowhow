"""Install command for skillpack."""

from pathlib import Path

import click
from rich.console import Console

from skillpack.config import Config, platform_option
from skillpack.utils import (
    check_name_arg,
    confirm_action,
    copy_directory,
    copy_file,
    find_command_files,
    find_skill_directories,
)
from skillpack.validator import CommandValidator, SkillValidator

console = Console()


@click.command()
@click.argument("name", required=False, callback=check_name_arg)
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Installation target (personal or project)",
)
@platform_option("Target platform")
@click.option("--type", "item_type", type=click.Choice(["skill", "command"]), help="Item type")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--dry-run", is_flag=True, help="Preview without making changes")
@click.option("--all", "install_all", is_flag=True, help="Install all skills and commands")
@click.pass_context
def install(ctx, name, target, platform, item_type, force, dry_run, install_all):
    """
    Install a skill or command.

    NAME is the name of the skill or command to install (or use --all to install everything).
    """
    verbose = ctx.obj.get("verbose", False)
    config = Config()

    # Validate arguments
    if install_all and name:
        console.print("[red]Error: Cannot specify both NAME and --all[/red]")
        raise click.Abort()
    if not install_all and not name:
        console.print("[red]Error: Must specify either NAME or --all[/red]")
        raise click.Abort()

    # Get repository path
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        repo_path = _setup_default_config(config)
        if not repo_path:
            console.print("[red]Error: Repository path not configured or does not exist.[/red]")
            console.print("Run: skillpack config set repository <path>")
            raise click.Abort()

    # Handle --all flag
    if install_all:
        _install_all_items(repo_path, config, target, platform, force, dry_run, verbose)
        return

    # Determine item type if not specified
    if not item_type:
        item_type = _detect_item_type(repo_path, name)
        if not item_type:
            console.print(f"[red]Error: Could not find skill or command '{name}'[/red]")
            raise click.Abort()

    # Find source
    if item_type == "skill":
        source_path = _find_skill(repo_path, name)
        if not source_path:
            console.print(f"[red]Error: Skill '{name}' not found in repository[/red]")
            raise click.Abort()

        # Validate skill
        valid, errors = SkillValidator.validate_skill_directory(source_path)
        if not valid:
            console.print("[red]Error: Invalid skill:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise click.Abort()

        # Get destination
        dest_dir = config.get_skills_dir(target, platform)
        dest_path = dest_dir / name

    else:  # command
        source_path = _find_command(repo_path, name)
        if not source_path:
            console.print(f"[red]Error: Command '{name}' not found in repository[/red]")
            raise click.Abort()

        # Validate command
        valid, errors = CommandValidator.validate_command_file(source_path)
        if not valid:
            console.print("[red]Error: Invalid command:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise click.Abort()

        # Get destination
        dest_dir = config.get_commands_dir(target, platform)
        dest_path = dest_dir / source_path.name

    if verbose:
        console.print(f"Source: {source_path}")
        console.print(f"Destination: {dest_path}")

    # Check if already exists
    if dest_path.exists() and not force:
        if not confirm_action(
            f"{item_type.capitalize()} '{name}' already exists. Overwrite?", default=False
        ):
            console.print("[yellow]Installation cancelled[/yellow]")
            return

    # Dry run
    if dry_run:
        console.print(f"[blue]Would install {item_type} '{name}' to {dest_path}[/blue]")
        return

    # Install
    dest_dir.mkdir(parents=True, exist_ok=True)

    if item_type == "skill":
        success = copy_directory(source_path, dest_path, force=True)
    else:
        success = copy_file(source_path, dest_path, force=True)

    if success:
        console.print(f"[green]Successfully installed {item_type} '{name}'[/green]")
    else:
        console.print(f"[red]Failed to install {item_type} '{name}'[/red]")


def _detect_item_type(repo_path: Path, name: str) -> str:
    """Detect whether name is a skill or command."""
    if _find_skill(repo_path, name):
        return "skill"
    if _find_command(repo_path, name):
        return "command"
    return None


def _find_skill(repo_path: Path, name: str) -> Path:
    """Find a skill by name in repository."""
    skills_dir = repo_path / "skills"
    if not skills_dir.exists():
        return None

    # Search for skill directory
    for skill_path in skills_dir.rglob("SKILL.md"):
        if skill_path.parent.name == name:
            return skill_path.parent

    return None


def _find_command(repo_path: Path, name: str) -> Path:
    """Find a command by name in repository."""
    commands_dir = repo_path / "commands"
    if not commands_dir.exists():
        return None

    # Search for command file
    for cmd_path in commands_dir.rglob("*.md"):
        if cmd_path.stem == name:
            return cmd_path

    return None


def _install_all_items(
    repo_path: Path,
    config: Config,
    target: str,
    platform: str,
    force: bool,
    dry_run: bool,
    verbose: bool,
):
    """Install all skills and commands from repository."""
    # Discovery phase
    skills = _discover_all_skills(repo_path)
    commands = _discover_all_commands(repo_path)

    console.print(f"Found {len(skills)} skills and {len(commands)} commands")

    # Dry run preview
    if dry_run:
        console.print("[blue]Would install the following items:[/blue]")

        console.print(f"\nSkills ({len(skills)}):")
        for skill_path in skills:
            dest = config.get_skills_dir(target, platform) / skill_path.name
            status = "exists" if dest.exists() else "new"
            if dest.exists() and force:
                status += " (overwrite)"
            console.print(f"  - {skill_path.name} [{status}]")

        console.print(f"\nCommands ({len(commands)}):")
        for cmd_path in commands:
            dest = config.get_commands_dir(target, platform) / cmd_path.name
            status = "exists" if dest.exists() else "new"
            if dest.exists() and force:
                status += " (overwrite)"
            console.print(f"  - {cmd_path.stem} [{status}]")

        return

    # Installation phase - skills first
    for skill_path in skills:
        name = skill_path.name
        dest_dir = config.get_skills_dir(target, platform)
        dest_path = dest_dir / name

        # Skip if already exists and not forced
        if dest_path.exists() and not force:
            console.print(f"[yellow]Skipping skill '{name}' (already installed)[/yellow]")
            continue

        # Validate
        valid, errors = SkillValidator.validate_skill_directory(skill_path)
        if not valid:
            console.print(f"[red]Error: Invalid skill '{name}'[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise click.Abort()

        # Install
        dest_dir.mkdir(parents=True, exist_ok=True)
        is_reinstall = dest_path.exists() and force
        success = copy_directory(skill_path, dest_path, force=True)
        if success:
            if is_reinstall:
                console.print(f"[green]Reinstalled skill '{name}'[/green]")
            else:
                console.print(f"[green]Installed skill '{name}'[/green]")
        else:
            console.print(f"[red]Failed to install skill '{name}'[/red]")
            raise click.Abort()

    # Installation phase - commands
    for cmd_path in commands:
        name = cmd_path.stem
        dest_dir = config.get_commands_dir(target, platform)
        dest_path = dest_dir / cmd_path.name

        # Skip if already exists and not forced
        if dest_path.exists() and not force:
            console.print(f"[yellow]Skipping command '{name}' (already installed)[/yellow]")
            continue

        # Validate
        valid, errors = CommandValidator.validate_command_file(cmd_path)
        if not valid:
            console.print(f"[red]Error: Invalid command '{name}'[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise click.Abort()

        # Install
        dest_dir.mkdir(parents=True, exist_ok=True)
        is_reinstall = dest_path.exists() and force
        success = copy_file(cmd_path, dest_path, force=True)
        if success:
            if is_reinstall:
                console.print(f"[green]Reinstalled command '{name}'[/green]")
            else:
                console.print(f"[green]Installed command '{name}'[/green]")
        else:
            console.print(f"[red]Failed to install command '{name}'[/red]")
            raise click.Abort()


def _discover_all_skills(repo_path: Path) -> list:
    """Discover all skills in repository."""
    skills_dir = repo_path / "skills"
    if not skills_dir.exists():
        return []

    return list(find_skill_directories(skills_dir))


def _discover_all_commands(repo_path: Path) -> list:
    """Discover all commands in repository."""
    commands_dir = repo_path / "commands"
    if not commands_dir.exists():
        return []

    return list(find_command_files(commands_dir))


def _setup_default_config(config: Config) -> Path:
    """Detect and setup default config if in a valid repository.

    Walks up from the current working directory to find a directory
    that looks like a skillpack repository (contains both ``skills`` and
    ``commands`` subdirectories).

    Returns the repository path if setup was successful, None otherwise.
    """
    cwd = Path.cwd()

    # Walk up the directory tree: cwd, parents[0], parents[1], ...
    candidates = [cwd] + list(cwd.parents)
    for candidate in candidates:
        if _is_valid_repo(candidate):
            console.print("[yellow]Repository path not configured.[/yellow]")
            console.print(f"Detected repository: {candidate}")

            # Prompt user for confirmation
            if confirm_action("Use this directory as the repository?", default=True):
                config.set_repository_path(candidate)
                console.print(f"[green]Repository path set to: {candidate}[/green]")
                return candidate

    return None


def _is_valid_repo(path: Path) -> bool:
    """Check if a directory is a valid skillpack repository."""
    return (path / "skills").exists() and (path / "commands").exists()
