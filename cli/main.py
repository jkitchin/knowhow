"""Main CLI entry point for skillz."""

import click
from rich.console import Console

from cli.commands import (
    ab_test,
    agents,
    config,
    create,
    harvest,
    hooks,
    info,
    install,
    merge,
    optimize,
    search,
    stats,
    uninstall,
    update,
)
from cli.commands.list import list_skills

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="skillz")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """
    Skillz - Manage AI assistant skills and slash commands.

    A CLI tool for installing, managing, and creating skills and commands
    for Claude Code, OpenCode, and other LLM platforms.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# Register commands
cli.add_command(config.config)
cli.add_command(install.install)
cli.add_command(uninstall.uninstall)
cli.add_command(list_skills)
cli.add_command(search.search)
cli.add_command(info.info)
cli.add_command(update.update)
cli.add_command(create.create)
cli.add_command(hooks.hooks)
cli.add_command(agents.agents)
cli.add_command(optimize.optimize)
cli.add_command(harvest.harvest)
cli.add_command(stats.stats)
cli.add_command(merge.merge)
cli.add_command(ab_test.ab_test)


if __name__ == "__main__":
    cli()
