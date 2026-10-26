"""Configuration management command for knowhow."""

import click
from rich.console import Console

from knowhow.config import Config

console = Console()


@click.group()
def config():
    """Manage configuration settings."""
    pass


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Set a configuration value."""
    cfg = Config()

    if key == "repository":
        from pathlib import Path

        repo_path = Path(value).expanduser()
        if not repo_path.exists():
            console.print(f"[red]Error: Path does not exist: {repo_path}[/red]")
            raise click.Abort()
        cfg.set_repository_path(repo_path)
        console.print(f"[green]Repository path set to: {repo_path}[/green]")
    elif key.startswith("alias."):
        name = key[len("alias.") :]
        if not name or "/" in name or "@" in name:
            console.print(f"[red]Error: Invalid alias name: {name}[/red]")
            raise click.Abort()
        cfg.set_alias(name, value)
        console.print(f"[green]Alias {name} -> {value}[/green]")
    else:
        console.print(f"[red]Error: Unknown configuration key: {key}[/red]")
        raise click.Abort()


@config.command()
@click.argument("key", required=False)
def get(key):
    """Get a configuration value."""
    cfg = Config()

    if not key:
        # Show all configuration
        console.print("[bold]Configuration:[/bold]")
        for k, v in cfg.config.items():
            console.print(f"  {k}: {v}")
        return

    if key == "repository":
        repo_path = cfg.get_repository_path()
        if repo_path:
            console.print(f"Repository path: {repo_path}")
        else:
            console.print("[yellow]Repository path not configured[/yellow]")
    else:
        value = cfg.config.get(key)
        if value is not None:
            console.print(f"{key}: {value}")
        else:
            console.print(f"[yellow]Key not found: {key}[/yellow]")
