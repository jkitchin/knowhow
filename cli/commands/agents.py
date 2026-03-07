"""Agents command group for skillz."""

import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from cli.config import Config, InvalidPlatformError, validate_platform
from cli.utils import (
    PathTraversalError,
    confirm_action,
    copy_file,
    find_agent_files,
    safe_path_join,
)
from cli.validator import AgentValidator

console = Console()


@click.group()
def agents():
    """Manage Claude Code agents (subagents)."""
    pass


@agents.command("list")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project", "repo"]),
    default="personal",
    help="Which agents to list",
)
@click.option(
    "--platform",
    "-p",
    default="claude",
    help="Target platform (claude, opencode, codex, gemini)",
)
@click.pass_context
def list_agents(ctx, target, platform):
    """List installed agents or available agents in repository."""
    config = Config()

    if target == "repo":
        # List agents from repository
        repo_path = config.get_repository_path()
        if not repo_path or not repo_path.exists():
            console.print("[red]Error: Repository path not configured.[/red]")
            console.print("Run: skillz config set repository <path>")
            return

        agents_dir = repo_path / "agents"
        if not agents_dir.exists():
            console.print("[yellow]No agents directory in repository[/yellow]")
            return

        agent_files = find_agent_files(agents_dir)
    else:
        # List installed agents
        agents_dir = config.get_agents_dir(target, platform)
        if not agents_dir.exists():
            console.print(f"[yellow]No agents installed ({agents_dir})[/yellow]")
            return

        agent_files = find_agent_files(agents_dir)

    if not agent_files:
        console.print("[yellow]No agents found[/yellow]")
        return

    # Create table
    table = Table(title=f"Agents ({target})")
    table.add_column("Name", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Tools", style="yellow")
    table.add_column("Description", style="white")

    for agent_file in agent_files:
        metadata = AgentValidator.get_agent_metadata(agent_file)
        if metadata:
            tools = metadata.get("tools", "*")
            if isinstance(tools, list):
                tools = ", ".join(tools[:3]) + ("..." if len(tools) > 3 else "")
            table.add_row(
                metadata.get("name", agent_file.stem),
                metadata.get("model", "inherit"),
                str(tools)[:20],
                _truncate(metadata.get("description", ""), 35),
            )
        else:
            table.add_row(agent_file.stem, "-", "-", "[dim]Invalid agent[/dim]")

    console.print(table)


@agents.command()
@click.argument("name")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Installation target",
)
@click.option(
    "--platform",
    "-p",
    default="claude",
    help="Target platform (claude, opencode, codex, gemini)",
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing agent")
@click.option("--dry-run", is_flag=True, help="Preview without making changes")
@click.pass_context
def install(ctx, name, target, platform, force, dry_run):
    """Install an agent from the repository."""
    config = Config()
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # Validate platform (security: prevent arbitrary paths)
    try:
        platform = validate_platform(platform)
    except InvalidPlatformError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()

    # Get repository path
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        console.print("[red]Error: Repository path not configured.[/red]")
        console.print("Run: skillz config set repository <path>")
        raise click.Abort()

    # Find agent in repository
    source_path = _find_agent(repo_path, name)
    if not source_path:
        console.print(f"[red]Error: Agent '{name}' not found in repository[/red]")
        raise click.Abort()

    # Validate agent
    valid, errors = AgentValidator.validate_agent_file(source_path)
    if not valid:
        console.print("[red]Error: Invalid agent:[/red]")
        for error in errors:
            console.print(f"  - {error}")
        raise click.Abort()

    # Get destination using safe_path_join (security: prevent path traversal)
    dest_dir = config.get_agents_dir(target, platform)
    try:
        dest_path = safe_path_join(dest_dir, source_path.name)
    except PathTraversalError as e:
        console.print(f"[red]Security error: {e}[/red]")
        raise click.Abort()

    if verbose:
        console.print(f"Source: {source_path}")
        console.print(f"Destination: {dest_path}")

    # Check if already exists
    if dest_path.exists() and not force:
        if not confirm_action(f"Agent '{name}' already exists. Overwrite?", default=False):
            console.print("[yellow]Installation cancelled[/yellow]")
            return

    # Dry run
    if dry_run:
        console.print(f"[blue]Would install agent '{name}' to {dest_path}[/blue]")
        return

    # Install agent file
    dest_dir.mkdir(parents=True, exist_ok=True)
    success = copy_file(source_path, dest_path, force=True)

    if not success:
        console.print(f"[red]Failed to install agent '{name}'[/red]")
        raise click.Abort()

    console.print(f"[green]Successfully installed agent '{name}'[/green]")
    console.print(f"[dim]Agent file: {dest_path}[/dim]")


@agents.command()
@click.argument("name")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Uninstall target",
)
@click.option("--platform", "-p", default="claude", help="Target platform")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.pass_context
def uninstall(ctx, name, target, platform, force):
    """Uninstall an agent."""
    config = Config()

    agents_dir = config.get_agents_dir(target, platform)

    # Find agent file
    agent_file = agents_dir / f"{name}.md"
    if not agent_file.exists():
        # Try without extension
        agent_file = agents_dir / name
        if not agent_file.exists():
            console.print(f"[red]Error: Agent '{name}' is not installed[/red]")
            raise click.Abort()

    if not force:
        if not confirm_action(f"Uninstall agent '{name}'?", default=False):
            console.print("[yellow]Uninstall cancelled[/yellow]")
            return

    # Remove agent file
    try:
        agent_file.unlink()
    except Exception as e:
        console.print(f"[red]Error removing agent: {e}[/red]")
        raise click.Abort()

    console.print(f"[green]Successfully uninstalled agent '{name}'[/green]")


@agents.command()
@click.argument("name")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project", "repo"]),
    default="repo",
    help="Where to look for the agent",
)
@click.option("--platform", "-p", default="claude", help="Target platform")
@click.pass_context
def info(ctx, name, target, platform):
    """Show detailed information about an agent."""
    config = Config()

    if target == "repo":
        repo_path = config.get_repository_path()
        if not repo_path:
            console.print("[red]Error: Repository path not configured.[/red]")
            raise click.Abort()
        agent_file = _find_agent(repo_path, name)
    else:
        agents_dir = config.get_agents_dir(target, platform)
        agent_file = agents_dir / f"{name}.md"
        if not agent_file.exists():
            agent_file = None

    if not agent_file or not agent_file.exists():
        console.print(f"[red]Error: Agent '{name}' not found[/red]")
        raise click.Abort()

    # Validate
    valid, errors = AgentValidator.validate_agent_file(agent_file)
    metadata = AgentValidator.get_agent_metadata(agent_file)

    console.print(f"\n[bold cyan]Agent: {name}[/bold cyan]")
    console.print(f"[dim]File: {agent_file}[/dim]\n")

    if metadata:
        console.print(f"[green]Model:[/green] {metadata.get('model', 'inherit')}")

        tools = metadata.get("tools", "*")
        if isinstance(tools, list):
            tools = ", ".join(tools)
        console.print(f"[green]Tools:[/green] {tools}")

        disallowed = metadata.get("disallowedTools")
        if disallowed:
            if isinstance(disallowed, list):
                disallowed = ", ".join(disallowed)
            console.print(f"[green]Disallowed:[/green] {disallowed}")

        console.print(f"\n[green]Description:[/green]\n{metadata.get('description', '-')}")

    if not valid:
        console.print("\n[red]Validation errors:[/red]")
        for error in errors:
            console.print(f"  - {error}")


@agents.command()
@click.argument("query", required=False)
@click.pass_context
def search(ctx, query):
    """Search for agents in the repository."""
    config = Config()

    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        console.print("[red]Error: Repository path not configured.[/red]")
        console.print("Run: skillz config set repository <path>")
        raise click.Abort()

    agents_dir = repo_path / "agents"
    if not agents_dir.exists():
        console.print("[yellow]No agents directory in repository[/yellow]")
        return

    agent_files = find_agent_files(agents_dir)

    if not agent_files:
        console.print("[yellow]No agents found in repository[/yellow]")
        return

    # Filter by query if provided
    results = []
    for agent_file in agent_files:
        metadata = AgentValidator.get_agent_metadata(agent_file)
        if metadata:
            name = metadata.get("name", agent_file.stem)
            desc = metadata.get("description", "")
            tools = str(metadata.get("tools", ""))

            if not query or _matches_query(query, name, desc, tools):
                results.append((agent_file, metadata))

    if not results:
        console.print(f"[yellow]No agents matching '{query}'[/yellow]")
        return

    # Display results
    table = Table(title="Search Results")
    table.add_column("Name", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Description", style="white")

    for agent_file, metadata in results:
        table.add_row(
            metadata.get("name", agent_file.stem),
            metadata.get("model", "inherit"),
            _truncate(metadata.get("description", ""), 50),
        )

    console.print(table)


@agents.command()
@click.argument("name")
@click.option(
    "--target",
    "-t",
    type=click.Choice(["personal", "project"]),
    default="personal",
    help="Where to create the agent",
)
@click.option("--platform", "-p", default="claude", help="Target platform")
@click.option(
    "--model",
    "-m",
    type=click.Choice(["sonnet", "opus", "haiku"]),
    default="sonnet",
    help="Model for the agent",
)
@click.option(
    "--tools",
    default="Read, Grep, Glob, Bash",
    help="Comma-separated list of allowed tools",
)
@click.option(
    "--prompt",
    help="Description prompt - use Claude to generate agent content",
)
@click.pass_context
def create(ctx, name, target, platform, model, tools, prompt):
    """Create a new agent from template or AI-generated.

    If --prompt is provided, uses Claude CLI to generate the agent content
    based on your description.
    """
    config = Config()

    agents_dir = config.get_agents_dir(target, platform)
    agent_file = agents_dir / f"{name}.md"

    if agent_file.exists():
        console.print(f"[red]Error: Agent '{name}' already exists at {agent_file}[/red]")
        raise click.Abort()

    # Create agents directory
    agents_dir.mkdir(parents=True, exist_ok=True)

    if prompt:
        # Use Claude to generate the agent
        content = _generate_agent_with_claude(name, prompt, model, tools)
        if not content:
            console.print("[red]Failed to generate agent with Claude[/red]")
            raise click.Abort()

        # Security: Show preview and ask for confirmation
        console.print("\n[bold yellow]⚠ AI-Generated Content Preview[/bold yellow]")
        console.print("[dim]Review the generated content before saving.[/dim]\n")
        console.print(f"[bold cyan]── {name}.md ──[/bold cyan]")
        # Show first 60 lines or entire content if smaller
        lines = content.split("\n")
        preview_lines = lines[:60]
        console.print("\n".join(preview_lines))
        if len(lines) > 60:
            console.print(f"[dim]... ({len(lines) - 60} more lines)[/dim]")
        console.print()

        if not confirm_action("Save this agent?", default=True):
            console.print("[yellow]Creation cancelled[/yellow]")
            raise click.Abort()
    else:
        # Create from template
        content = f"""---
name: {name}
description: |
  Description of what this agent does.
  Use proactively when [specific trigger conditions].
tools: {tools}
model: {model}
---

# {name.replace("-", " ").title()}

You are a specialized agent for [purpose].

## When to Use

This agent should be invoked when:
- [Trigger condition 1]
- [Trigger condition 2]

## Instructions

When invoked:
1. [First step]
2. [Second step]
3. [Third step]

## Output Format

Provide results in the following format:
- [Format description]
"""

    agent_file.write_text(content)

    console.print(f"[green]Created agent '{name}' at {agent_file}[/green]")
    if not prompt:
        console.print("\n[dim]Edit the file to customize the agent, then install it:[/dim]")
        console.print(f"  skillz agents install {name} --target {target}")


# Helper functions


def _find_agent(repo_path: Path, name: str) -> Path | None:
    """Find an agent by name in repository."""
    agents_dir = repo_path / "agents"
    if not agents_dir.exists():
        return None

    # Try exact match first
    agent_file = agents_dir / f"{name}.md"
    if agent_file.exists():
        return agent_file

    # Search by name in frontmatter
    for agent_path in agents_dir.rglob("*.md"):
        metadata = AgentValidator.get_agent_metadata(agent_path)
        if metadata and metadata.get("name") == name:
            return agent_path

    # Try stem match
    for agent_path in agents_dir.rglob("*.md"):
        if agent_path.stem == name:
            return agent_path

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


def _generate_agent_with_claude(name: str, prompt: str, model: str, tools: str) -> str | None:
    """Use Claude CLI to generate agent content."""
    generation_prompt = f"""Generate a Claude Code agent (subagent) markdown file for the following:

Name: {name}
Description/Purpose: {prompt}
Model: {model}
Tools: {tools}

Create a complete agent file with:
1. YAML frontmatter with name, description, tools, and model
2. Clear instructions for when to use this agent
3. Step-by-step process the agent should follow
4. Expected output format

Output ONLY the markdown content, starting with --- for the frontmatter.
Do not include any explanation, just the agent file content."""

    try:
        result = subprocess.run(
            ["claude", "-p", generation_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0 and result.stdout.strip():
            content = result.stdout.strip()
            # Ensure it starts with frontmatter
            if not content.startswith("---"):
                content = "---\n" + content
            return content
        else:
            console.print(f"[yellow]Claude CLI error: {result.stderr}[/yellow]")
            return None

    except FileNotFoundError:
        console.print("[yellow]Claude CLI not found. Install it or create agent manually.[/yellow]")
        return None
    except subprocess.TimeoutExpired:
        console.print("[yellow]Claude CLI timed out[/yellow]")
        return None
    except Exception as e:
        console.print(f"[yellow]Error running Claude CLI: {e}[/yellow]")
        return None
