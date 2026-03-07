"""Harvest command - extract reusable skills from Claude Code session transcripts.

Inspired by CASCADE (arxiv:2512.23880): Cumulative Agentic Skill Creation through
Autonomous Development and Evolution. Implements the skill creation/accumulation
phase where agents extract generalizable solutions from specific problem instances.
"""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from cli.commands.optimize import _run_claude_cli
from cli.config import Config
from cli.utils import confirm_action, validate_name

console = Console()

HARVEST_PROMPT = """\
You are an expert at extracting reusable AI skills from session transcripts.

Analyze this Claude Code session transcript and identify reusable skills that could be
extracted. A good skill is:
- Generalizable (not specific to one project)
- Reusable (likely to be needed again)
- Self-contained (can be described as a standalone capability)
- Non-trivial (not just "read a file" but a multi-step workflow)

Session transcript:
```
{transcript}
```

For each potential skill you identify, provide:

## Skill N: skill-name

**Name:** lowercase-with-hyphens (e.g., "data-pipeline-debugging")
**Description:** A concise description (1-3 sentences) of what the skill does and when to use it.
**Category:** One of: programming, research, development, creative, technical,
scientific, laboratory, academic, productivity, communication, python
**Key Patterns:** The core workflow or patterns this skill captures.
**Trigger Phrases:** Example user requests that should activate this skill.

If no reusable skills can be extracted, say "No reusable skills identified in this session."

Focus on quality over quantity. Only suggest skills that would genuinely be reused."""

GENERATE_SKILL_PROMPT = """You are an expert at creating AI assistant skill definitions.

Create a complete SKILL.md file for the following skill:

Name: {name}
Description: {description}
Category: {category}
Key Patterns: {patterns}

The SKILL.md must have:
1. YAML frontmatter with name, description, and allowed-tools: ["*"]
2. A comprehensive markdown body that teaches an AI assistant how to perform this skill
3. Clear workflow steps
4. Common pitfalls to avoid
5. Examples where appropriate

Output ONLY the complete SKILL.md content (starting with ---).
Do not wrap it in code blocks or add any explanation."""


def _find_transcripts(directory: Path | None = None) -> list:
    """Find Claude Code session transcript files."""
    if directory:
        search_dir = directory
    else:
        search_dir = Path.home() / ".claude" / "projects"

    transcripts = []
    if search_dir.exists():
        for f in search_dir.rglob("*.jsonl"):
            transcripts.append(f)

    return sorted(transcripts, key=lambda p: p.stat().st_mtime, reverse=True)


def _read_transcript(path: Path, max_lines: int = 200) -> str:
    """Read a transcript file, extracting key content."""
    lines = []
    try:
        with open(path) as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                try:
                    entry = json.loads(line.strip())
                    # Extract user messages and assistant text
                    role = entry.get("role", "")
                    if role in ("user", "assistant"):
                        content = entry.get("content", "")
                        if isinstance(content, str):
                            lines.append(f"[{role}]: {content[:500]}")
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    lines.append(f"[{role}]: {block['text'][:500]}")
                except (json.JSONDecodeError, KeyError):
                    continue
    except Exception:
        pass

    return "\n".join(lines)


def _extract_skill_proposals(transcript_text: str) -> str | None:
    """Use Claude to analyze transcript and propose skills."""
    prompt = HARVEST_PROMPT.format(transcript=transcript_text[:8000])
    return _run_claude_cli(prompt, timeout=180)


def _generate_skill_content(
    name: str, description: str, category: str, patterns: str
) -> str | None:
    """Use Claude to generate a complete SKILL.md."""
    prompt = GENERATE_SKILL_PROMPT.format(
        name=name, description=description, category=category, patterns=patterns
    )
    return _run_claude_cli(prompt, timeout=180)


@click.command()
@click.option(
    "--transcript",
    "-t",
    type=click.Path(exists=True),
    help="Path to a specific session transcript (.jsonl)",
)
@click.option(
    "--recent", "-r", default=5, show_default=True, help="Number of recent transcripts to analyze"
)
@click.option(
    "--generate", "-g", is_flag=True, help="Interactively generate SKILL.md for proposed skills"
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory for generated skills (default: repo skills/)",
)
@click.option("--dry-run", is_flag=True, help="Show proposals without generating files")
@click.pass_context
def harvest(ctx, transcript, recent, generate, output_dir, dry_run):
    """
    Harvest reusable skills from Claude Code session transcripts.

    Analyzes session transcripts to identify patterns that could be extracted
    into reusable skills. Inspired by CASCADE (arxiv:2512.23880).

    Examples:

        # Analyze recent sessions
        skillz harvest

        # Analyze a specific transcript
        skillz harvest -t ~/.claude/projects/.../session.jsonl

        # Analyze and generate skill files
        skillz harvest --generate

        # Preview without creating files
        skillz harvest --generate --dry-run
    """
    config = Config()

    if transcript:
        transcripts = [Path(transcript)]
    else:
        transcripts = _find_transcripts()
        if not transcripts:
            console.print("[red]No session transcripts found.[/red]")
            console.print("[dim]Expected in ~/.claude/projects/*/*.jsonl[/dim]")
            raise click.Abort()
        transcripts = transcripts[:recent]

    console.print(f"\n[bold]Harvesting skills from {len(transcripts)} transcript(s)...[/bold]\n")

    all_proposals = []
    for i, t_path in enumerate(transcripts, 1):
        console.print(
            f"[yellow]Analyzing transcript {i}/{len(transcripts)}: {t_path.name}...[/yellow]"
        )

        transcript_text = _read_transcript(t_path)
        if not transcript_text:
            console.print("  [dim]Empty or unreadable, skipping.[/dim]")
            continue

        proposals = _extract_skill_proposals(transcript_text)
        if proposals and "No reusable skills" not in proposals:
            all_proposals.append(proposals)
            console.print(
                Panel(proposals, title=f"Proposals from {t_path.name}", border_style="cyan")
            )
        else:
            console.print("  [dim]No reusable skills identified.[/dim]")

    if not all_proposals:
        console.print("\n[yellow]No skill candidates found across all transcripts.[/yellow]")
        return

    if not generate or dry_run:
        if dry_run:
            console.print("\n[dim]Dry run: no files created.[/dim]")
        else:
            console.print(
                "\n[dim]Use --generate to create SKILL.md files for these proposals.[/dim]"
            )
        return

    # Interactive generation
    dest_dir = Path(output_dir) if output_dir else None
    if not dest_dir:
        repo_path = config.get_repository_path()
        if repo_path:
            dest_dir = repo_path / "skills"
        else:
            dest_dir = Path.cwd() / "skills"

    console.print(f"\n[bold]Generating skills to: {dest_dir}[/bold]\n")

    for proposal_text in all_proposals:
        # Parse proposals for skill names/descriptions
        console.print("[yellow]Enter skill details to generate (or press Enter to skip):[/yellow]")
        name = click.prompt("Skill name (lowercase-with-hyphens)", default="", show_default=False)
        if not name:
            continue

        if not validate_name(name):
            console.print(
                "[red]Invalid name. Use lowercase letters, numbers, and hyphens only.[/red]"
            )
            continue

        description = click.prompt("Description", default="")
        category = click.prompt("Category", default="programming")
        patterns = click.prompt("Key patterns (from proposal above)", default="")

        console.print(f"\n[yellow]Generating SKILL.md for '{name}'...[/yellow]")
        content = _generate_skill_content(name, description, category, patterns)

        if not content:
            console.print("[red]Failed to generate skill content.[/red]")
            continue

        console.print(
            Panel(
                content[:2000] + ("..." if len(content) > 2000 else ""),
                title=f"Generated: {name}",
                border_style="green",
            )
        )

        if not confirm_action(f"Save skill '{name}'?", default=True):
            console.print("[yellow]Skipped.[/yellow]")
            continue

        skill_dir = dest_dir / category / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(content)
        console.print(f"[green]Created: {skill_dir / 'SKILL.md'}[/green]")
