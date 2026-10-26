"""Create command for knowhow."""

import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from knowhow.config import Config
from knowhow.utils import confirm_action, validate_description, validate_name

console = Console()


@click.command()
@click.option("--type", "item_type", type=click.Choice(["skill", "command"]), required=True)
@click.option("--name", "-n", help="Name of the skill or command")
@click.option("--interactive", "-i", is_flag=True, default=True, help="Interactive mode")
@click.option(
    "--prompt",
    "-p",
    help="Description prompt - use Claude to generate skill/command content",
)
@click.pass_context
def create(ctx, item_type, name, interactive, prompt):
    """
    Create a new skill or command from a template.

    Creates a new skill or command with proper structure and frontmatter.
    Use --prompt to generate content using Claude CLI.
    """
    verbose = ctx.obj.get("verbose", False)
    config = Config()

    console.print(f"\n[bold]Creating a new {item_type}[/bold]\n")

    # Get name
    if not name:
        if interactive:
            name = Prompt.ask(
                "Enter name (lowercase, hyphens only)",
                default="my-" + item_type,
            )
        else:
            console.print("[red]Error: --name is required in non-interactive mode[/red]")
            raise click.Abort()

    # Validate name
    if not validate_name(name):
        console.print(
            "[red]Error: Invalid name. Use lowercase letters, numbers, and hyphens only[/red]"
        )
        raise click.Abort()

    # If using AI generation, skip description prompt
    if prompt:
        description = None
    else:
        # Get description
        if interactive:
            description = Prompt.ask("Enter description")
            while not validate_description(description):
                console.print("[red]Description too long (max 1024 chars)[/red]")
                description = Prompt.ask("Enter description")
        else:
            description = f"A {item_type} for Claude Code"

    # Get location
    if interactive and not prompt:
        use_repo = Confirm.ask(
            "Create in repository? (no = create in current directory)", default=True
        )
    else:
        # For AI-generated content, default to current directory
        use_repo = not prompt

    if use_repo:
        repo_path = config.get_repository_path()
        if not repo_path or not repo_path.exists():
            console.print("[red]Error: Repository path not configured[/red]")
            raise click.Abort()

        if item_type == "skill":
            base_path = repo_path / "skills"
        else:
            base_path = repo_path / "commands"
    else:
        base_path = Path.cwd()

    # Create the item
    if item_type == "skill":
        if prompt:
            _create_skill_with_ai(base_path, name, prompt, verbose)
        else:
            _create_skill(base_path, name, description, verbose)
    else:
        if prompt:
            _create_command_with_ai(base_path, name, prompt, verbose)
        else:
            _create_command(base_path, name, description, verbose)

    console.print(f"\n[green]Successfully created {item_type} '{name}'![/green]")


def _create_skill(base_path: Path, name: str, description: str, verbose: bool):
    """Create a new skill directory and SKILL.md."""
    skill_path = base_path / name
    skill_path.mkdir(parents=True, exist_ok=True)

    skill_file = skill_path / "SKILL.md"

    content = f"""---
name: {name}
description: {description}
---

# {name.replace("-", " ").title()}

{description}

## Usage

When to use this skill:
- TODO: Describe when Claude should use this skill

## Instructions

TODO: Add detailed instructions for how to use this skill

## Examples

TODO: Add examples of using this skill
"""

    skill_file.write_text(content)

    if verbose:
        console.print(f"Created: {skill_file}")


def _create_command(base_path: Path, name: str, description: str, verbose: bool):
    """Create a new command file."""
    cmd_file = base_path / f"{name}.md"
    cmd_file.parent.mkdir(parents=True, exist_ok=True)

    content = f"""---
description: {description}
---

# {name.replace("-", " ").title()} Command

TODO: Add the command prompt content here.

You can use:
- `$ARGUMENTS` - All arguments passed to the command
- `$1`, `$2`, etc. - Individual positional arguments
- `@filename` - Include file content
- `!command` - Execute bash commands (requires Bash in allowed-tools)

## Example Usage

```
/{name} <arguments>
```
"""

    cmd_file.write_text(content)

    if verbose:
        console.print(f"Created: {cmd_file}")


def _generate_skill_with_claude(name: str, prompt: str) -> str | None:
    """Generate skill content using Claude CLI."""
    generation_prompt = f"""Generate a SKILL.md file for a Claude Code skill \
with the following requirements:

Name: {name}
Description/Purpose: {prompt}

The skill file must follow this format:
1. Start with YAML frontmatter between --- delimiters
2. Required frontmatter fields:
   - name: {name}
   - description: |
       (multi-line, max 1024 chars total — see description requirements below)
3. Optional frontmatter fields:
   - allowed-tools: List of tools (Bash, Read, Write, Edit, Glob, Grep, WebFetch, etc.)
4. After frontmatter, include markdown content (keep under 400 lines total):
   - A heading with the skill name
   - Purpose section (what it does and why)
   - When to Use section with specific trigger conditions
   - Step-by-step instructions that explain WHY each step matters
   - Key examples
   - Reference to references/ subdirectory for extended docs (if needed)

DESCRIPTION REQUIREMENTS (this is the most important part):
The description must be "pushy" — assertive about when Claude should trigger this skill.
LLMs tend to undertrigger skills (fail to use them when they should). A weak description
makes this worse. Write a description that:
- Opens with what the skill does (1 sentence)
- Has an assertive "Use this skill when the user..." block with SPECIFIC trigger conditions:
  * Concrete verbs (asks to, wants to, needs to)
  * Specific nouns (file types, tool names, library names, concepts)
  * Example user phrasings in quotes if helpful
- Optionally adds "Do NOT use when..." for disambiguation from similar skills
- Optionally lists dependencies ("Requires: package-name")

Example of a pushy description:
  Expert guidance for pandas DataFrames — cleaning, transforming, and analyzing tabular data.

  Use this skill when the user:
  - imports pandas or asks about DataFrames, Series, or tabular data
  - asks to read CSV/Excel/JSON files into pandas
  - needs to filter, group, merge, or reshape data
  - says things like "how do I pivot this?", "clean up missing values", "groupby example"

  Do NOT use for general Python questions unrelated to tabular data.

INSTRUCTIONS PHILOSOPHY:
Instead of bare imperatives ("NEVER skip X", "ALWAYS do Y"), explain the reasoning:
- Bad: "ALWAYS validate inputs first."
- Good: "Validate inputs before processing — this surfaces the real error (bad input)
  rather than a confusing downstream failure."

Output ONLY the SKILL.md content, no explanations or markdown code blocks."""

    try:
        console.print("[yellow]Generating skill with Claude...[/yellow]")
        result = subprocess.run(
            ["claude", "-p", generation_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            console.print(f"[red]Error generating skill: {result.stderr}[/red]")
            return None
    except FileNotFoundError:
        console.print("[red]Error: Claude CLI not found. Please install it first.[/red]")
        return None
    except subprocess.TimeoutExpired:
        console.print("[red]Error: Claude CLI timed out.[/red]")
        return None


def _generate_command_with_claude(name: str, prompt: str) -> str | None:
    """Generate command content using Claude CLI."""
    generation_prompt = f"""Generate a command markdown file for a Claude Code \
slash command with the following requirements:

Name: {name}
Description/Purpose: {prompt}

The command file must follow this format:
1. Start with YAML frontmatter between --- delimiters
2. Required frontmatter fields:
   - description: A clear one-line description (max 256 chars)
     Unlike skills, commands are user-invoked (explicit /command-name) so the
     description just needs to be clear and informative — it appears in /help.
     It does NOT need to be "pushy" about when to trigger.
3. Optional frontmatter fields:
   - model: sonnet, opus, or haiku
   - allowed-tools: List of tools (Bash, Read, Write, Edit, Glob, Grep, etc.)
   - argument-hint: Hint for autocomplete (e.g., "<filename> [options]")
4. After frontmatter, include the command prompt content with:
   - Clear context/purpose explanation
   - Step-by-step instructions for Claude to follow
   - Output format specification
   - Error handling guidance for invalid/missing arguments

Available variables in command content:
- $ARGUMENTS - All arguments passed to the command
- $1, $2, etc. - Individual positional arguments
- @filename - Include file content inline
- !command - Execute bash commands before the prompt (requires Bash in allowed-tools)

INSTRUCTIONS QUALITY:
Write instructions that explain WHY each step matters, not just WHAT to do.
This produces more adaptive behavior than bare imperatives like "ALWAYS" or "NEVER".

Output ONLY the command .md content, no explanations or markdown code blocks."""

    try:
        console.print("[yellow]Generating command with Claude...[/yellow]")
        result = subprocess.run(
            ["claude", "-p", generation_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            console.print(f"[red]Error generating command: {result.stderr}[/red]")
            return None
    except FileNotFoundError:
        console.print("[red]Error: Claude CLI not found. Please install it first.[/red]")
        return None
    except subprocess.TimeoutExpired:
        console.print("[red]Error: Claude CLI timed out.[/red]")
        return None


def _create_skill_with_ai(base_path: Path, name: str, prompt: str, verbose: bool):
    """Create a skill using AI-generated content."""
    content = _generate_skill_with_claude(name, prompt)
    if not content:
        console.print("[red]Failed to generate skill content.[/red]")
        raise click.Abort()

    # Security: Show preview and ask for confirmation
    console.print("\n[bold yellow]⚠ AI-Generated Content Preview[/bold yellow]")
    console.print("[dim]Review the generated content before saving.[/dim]\n")
    console.print("[bold cyan]── SKILL.md ──[/bold cyan]")
    # Show first 60 lines or entire content if smaller
    lines = content.split("\n")
    preview_lines = lines[:60]
    console.print("\n".join(preview_lines))
    if len(lines) > 60:
        console.print(f"[dim]... ({len(lines) - 60} more lines)[/dim]")
    console.print()

    if not confirm_action("Save this skill?", default=True):
        console.print("[yellow]Creation cancelled[/yellow]")
        raise click.Abort()

    skill_path = base_path / name
    skill_path.mkdir(parents=True, exist_ok=True)
    skill_file = skill_path / "SKILL.md"
    skill_file.write_text(content)

    if verbose:
        console.print(f"Created: {skill_file}")


def _create_command_with_ai(base_path: Path, name: str, prompt: str, verbose: bool):
    """Create a command using AI-generated content."""
    content = _generate_command_with_claude(name, prompt)
    if not content:
        console.print("[red]Failed to generate command content.[/red]")
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

    if not confirm_action("Save this command?", default=True):
        console.print("[yellow]Creation cancelled[/yellow]")
        raise click.Abort()

    cmd_file = base_path / f"{name}.md"
    cmd_file.parent.mkdir(parents=True, exist_ok=True)
    cmd_file.write_text(content)

    if verbose:
        console.print(f"Created: {cmd_file}")
