"""Merge command - detect and propose skill merges for overlapping skills.

Inspired by CASCADE (arxiv:2512.23880): Cumulative Agentic Skill Creation through
Autonomous Development and Evolution. Implements the skill evolution phase where
skills are combined, deduplicated, and reorganized.
"""

import click
import yaml
from rich.console import Console
from rich.panel import Panel

from cli.commands.optimize import _run_claude_cli
from cli.config import Config
from cli.utils import find_skill_directories

console = Console()

OVERLAP_PROMPT = """You are an expert at analyzing AI assistant skill libraries for redundancy.

Below are {n} skills with their names and descriptions. Analyze them for:

1. **Overlapping skills** - Skills that cover substantially the same domain and could be merged
2. **Complementary skills** - Skills that naturally work together and could
benefit from cross-references
3. **Hierarchy candidates** - Skills that could be organized as parent/child (skill + subskills)

Skills:
{skills_text}

For each group of related skills, provide:

## Group N: Theme Name
**Skills:** skill-name-1, skill-name-2, ...
**Relationship:** overlap | complementary | hierarchy
**Recommendation:** merge | cross-reference | reorganize
**Rationale:** Brief explanation.
**Proposed action:** Specific suggestion for what to do.

If no significant overlaps or relationships exist, say "No significant overlaps detected."

Focus on actionable recommendations. Minor keyword overlaps don't count."""

MERGE_PROMPT = """You are an expert at creating AI assistant skill definitions.

Merge these two skills into a single, comprehensive skill:

## Skill 1: {name1}
{content1}

## Skill 2: {name2}
{content2}

Create a merged SKILL.md that:
1. Combines the best elements of both skills
2. Eliminates redundancy
3. Has clear YAML frontmatter (name, description, allowed-tools: ["*"])
4. Maintains all unique guidance from both originals
5. Uses the name: {merged_name}

Output ONLY the complete merged SKILL.md (starting with ---).
Do not wrap in code blocks or add explanation."""


def _get_all_skills_summary(config: Config) -> list[dict]:
    """Get name and description for all skills."""
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        return []

    skills_dir = repo_path / "skills"
    skill_dirs = find_skill_directories(skills_dir)

    summaries = []
    for sd in skill_dirs:
        skill_md = sd / "SKILL.md"
        if skill_md.exists():
            try:
                content = skill_md.read_text()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        fm = yaml.safe_load(parts[1])
                        summaries.append(
                            {
                                "name": fm.get("name", sd.name),
                                "description": str(fm.get("description", "")),
                                "path": str(sd),
                                "category": sd.parent.name,
                            }
                        )
            except Exception:
                continue
    return summaries


def _format_skills_for_analysis(summaries: list[dict]) -> str:
    """Format skill summaries for the analysis prompt."""
    lines = []
    for s in summaries:
        lines.append(f"- **{s['name']}** ({s['category']}): {s['description'][:200]}")
    return "\n".join(lines)


def _detect_overlaps(config: Config) -> str | None:
    """Use Claude to analyze all skills for overlaps."""
    summaries = _get_all_skills_summary(config)
    if not summaries:
        return None

    skills_text = _format_skills_for_analysis(summaries)
    prompt = OVERLAP_PROMPT.format(n=len(summaries), skills_text=skills_text)
    return _run_claude_cli(prompt, timeout=180)


@click.command()
@click.option("--detect", is_flag=True, default=True, help="Detect overlapping skills (default)")
@click.option(
    "--execute", nargs=2, metavar="SKILL1 SKILL2", help="Merge two specific skills interactively"
)
@click.option("--merged-name", help="Name for the merged skill (with --execute)")
@click.option("--dry-run", is_flag=True, help="Show analysis without making changes")
@click.pass_context
def merge(ctx, detect, execute, merged_name, dry_run):
    """
    Detect overlapping skills and propose merges.

    Analyzes the skill library to find redundancies, complementary skills,
    and hierarchy opportunities. Inspired by CASCADE (arxiv:2512.23880).

    Examples:

        # Detect overlaps across all skills
        skillz merge

        # Merge two specific skills
        skillz merge --execute python-jax python-numpy --merged-name python-array-computing

        # Preview merge without saving
        skillz merge --execute skill-a skill-b --dry-run
    """
    config = Config()

    if execute:
        _execute_merge(config, execute[0], execute[1], merged_name, dry_run)
        return

    # Default: detect overlaps
    console.print("\n[bold]Analyzing skill library for overlaps...[/bold]\n")

    analysis = _detect_overlaps(config)
    if not analysis:
        console.print(
            "[red]Failed to analyze skills. Check repository path and "
            "Claude CLI availability.[/red]"
        )
        raise click.Abort()

    if "No significant overlaps" in analysis:
        console.print("[green]No significant overlaps detected.[/green]")
        return

    console.print(Panel(analysis, title="Overlap Analysis", border_style="cyan"))

    if dry_run:
        console.print("\n[dim]Dry run: no changes made.[/dim]")


def _execute_merge(config: Config, name1: str, name2: str, merged_name: str | None, dry_run: bool):
    """Execute a merge of two specific skills."""
    repo_path = config.get_repository_path()
    if not repo_path:
        console.print("[red]Repository path not set.[/red]")
        raise click.Abort()

    skills_dir = repo_path / "skills"
    skill_dirs = find_skill_directories(skills_dir)

    # Find both skills
    path1 = path2 = None
    for sd in skill_dirs:
        if sd.name == name1:
            path1 = sd
        elif sd.name == name2:
            path2 = sd

    if not path1:
        console.print(f"[red]Skill '{name1}' not found.[/red]")
        raise click.Abort()
    if not path2:
        console.print(f"[red]Skill '{name2}' not found.[/red]")
        raise click.Abort()

    content1 = (path1 / "SKILL.md").read_text()
    content2 = (path2 / "SKILL.md").read_text()

    if not merged_name:
        merged_name = click.prompt("Name for merged skill", default=name1)

    console.print(
        f"\n[yellow]Generating merged skill '{merged_name}' "
        f"from '{name1}' + '{name2}'...[/yellow]\n"
    )

    prompt = MERGE_PROMPT.format(
        name1=name1,
        content1=content1[:4000],
        name2=name2,
        content2=content2[:4000],
        merged_name=merged_name,
    )
    merged_content = _run_claude_cli(prompt, timeout=180)

    if not merged_content:
        console.print("[red]Failed to generate merged skill.[/red]")
        raise click.Abort()

    console.print(
        Panel(
            merged_content[:3000] + ("..." if len(merged_content) > 3000 else ""),
            title=f"Merged: {merged_name}",
            border_style="green",
        )
    )

    if dry_run:
        console.print("\n[dim]Dry run: no files created.[/dim]")
        return

    from cli.utils import confirm_action

    if not confirm_action(f"Save merged skill '{merged_name}'?", default=True):
        console.print("[yellow]Merge cancelled.[/yellow]")
        return

    # Save merged skill in the same category as skill1
    category = path1.parent.name
    merged_dir = skills_dir / category / merged_name
    merged_dir.mkdir(parents=True, exist_ok=True)
    (merged_dir / "SKILL.md").write_text(merged_content)
    console.print(f"[green]Created: {merged_dir / 'SKILL.md'}[/green]")
    console.print("[dim]Original skills preserved. Remove manually if desired:[/dim]")
    console.print(f"[dim]  rm -r {path1}[/dim]")
    console.print(f"[dim]  rm -r {path2}[/dim]")
