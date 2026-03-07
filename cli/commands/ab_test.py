"""A/B test command - compare skill description variants for triggering accuracy.

Inspired by CASCADE (arxiv:2512.23880): Cumulative Agentic Skill Creation through
Autonomous Development and Evolution. Implements quality-based selection through
comparative evaluation of skill description variants.
"""

from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.commands.optimize import (
    _find_skill_path,
    _generate_evals,
    _read_skill_description,
    _run_claude_cli,
    _update_skill_description,
)
from cli.config import Config
from cli.validator import SkillValidator

console = Console()

SCORE_PROMPT = """You are an expert at evaluating AI skill descriptions for triggering accuracy.

A skill description is shown to an LLM, which decides whether to invoke that skill
based on the description. Score how well this description would perform.

Skill name: {name}

Description being evaluated:
```
{description}
```

Evaluation queries (ground truth):
{evals}

For each query, assess whether the description would cause the LLM to correctly:
- TRIGGER on should-trigger queries
- NOT TRIGGER on should-not-trigger queries

Score format (output ONLY this, nothing else):

SHOULD_TRIGGER_CORRECT: X/Y
SHOULD_NOT_TRIGGER_CORRECT: X/Y
TOTAL_SCORE: X/Y
WEAKNESSES: Brief note on what the description misses or over-matches."""


def _score_description(name: str, description: str, evals: str) -> Optional[dict]:
    """Score a description against eval queries."""
    prompt = SCORE_PROMPT.format(name=name, description=description, evals=evals)
    result = _run_claude_cli(prompt, timeout=120)
    if not result:
        return None

    scores = {}
    for line in result.strip().split("\n"):
        line = line.strip()
        if line.startswith("SHOULD_TRIGGER_CORRECT:"):
            scores["trigger"] = line.split(":", 1)[1].strip()
        elif line.startswith("SHOULD_NOT_TRIGGER_CORRECT:"):
            scores["no_trigger"] = line.split(":", 1)[1].strip()
        elif line.startswith("TOTAL_SCORE:"):
            scores["total"] = line.split(":", 1)[1].strip()
        elif line.startswith("WEAKNESSES:"):
            scores["weaknesses"] = line.split(":", 1)[1].strip()

    return scores if scores else None


def _generate_variant(
    name: str, skill_content: str, evals: str, current: str, variant_num: int
) -> Optional[str]:
    """Generate a description variant with different emphasis."""
    emphasis_prompts = [
        "Focus on SPECIFIC trigger phrases and concrete use cases.",
        "Focus on DISTINGUISHING this skill from similar skills. Emphasize what makes it unique.",
        "Focus on BREADTH - ensure all valid use cases are covered by the description.",
    ]
    emphasis = emphasis_prompts[variant_num % len(emphasis_prompts)]

    prompt = f"""You are an expert at optimizing AI skill descriptions for precise triggering.

Current skill name: {name}

Current description:
{current}

Evaluation queries showing triggering gaps:
{evals}

Full skill content:
```
{skill_content[:2000]}
```

EMPHASIS FOR THIS VARIANT: {emphasis}

Write an improved description (max 1024 characters) that addresses the evaluation gaps.
Focus on: {emphasis}

Output ONLY the description text. No YAML, no quotes, no explanation."""

    return _run_claude_cli(prompt, timeout=120)


@click.command("ab-test")
@click.argument("skill_name")
@click.option(
    "--variants",
    "-n",
    default=3,
    show_default=True,
    help="Number of description variants to generate",
)
@click.option("--dry-run", is_flag=True, help="Show results without saving")
@click.pass_context
def ab_test(ctx, skill_name, variants, dry_run):
    """
    A/B test skill description variants for triggering accuracy.

    Generates multiple description variants, scores each against eval queries,
    and recommends the best performer. Inspired by CASCADE (arxiv:2512.23880).

    Examples:

        # Test 3 variants (default)
        skillz ab-test python-jax

        # Test 5 variants
        skillz ab-test python-jax -n 5

        # Preview without saving
        skillz ab-test python-jax --dry-run
    """
    config = Config()

    skill_path = _find_skill_path(skill_name, config)
    if not skill_path:
        console.print(f"[red]Skill '{skill_name}' not found.[/red]")
        raise click.Abort()

    is_valid, errors = SkillValidator.validate_skill_directory(skill_path)
    if not is_valid:
        console.print(f"[red]Skill '{skill_name}' has validation errors:[/red]")
        for error in errors:
            console.print(f"  [red]- {error}[/red]")
        raise click.Abort()

    skill_md = skill_path / "SKILL.md"
    skill_content = skill_md.read_text()
    current_description = _read_skill_description(skill_md) or ""

    console.print(f"\n[bold]A/B Testing: [cyan]{skill_name}[/cyan][/bold]\n")

    # Step 1: Generate eval queries
    console.print("[yellow]Step 1: Generating evaluation queries...[/yellow]")
    evals = _generate_evals(skill_name, skill_content)
    if not evals:
        console.print("[red]Failed to generate eval queries.[/red]")
        raise click.Abort()

    console.print(Panel(evals, title="Evaluation Queries", border_style="dim"))

    # Step 2: Score current description
    console.print("\n[yellow]Step 2: Scoring current description...[/yellow]")
    current_score = _score_description(skill_name, current_description, evals)

    # Step 3: Generate and score variants
    console.print(f"\n[yellow]Step 3: Generating {variants} variant(s)...[/yellow]")
    results = []

    # Include current as baseline
    results.append(
        {
            "label": "Current",
            "description": current_description,
            "score": current_score,
        }
    )

    for i in range(variants):
        console.print(f"  [dim]Generating variant {i + 1}/{variants}...[/dim]")
        variant_desc = _generate_variant(skill_name, skill_content, evals, current_description, i)
        if not variant_desc:
            console.print(f"  [red]Failed to generate variant {i + 1}.[/red]")
            continue

        console.print(f"  [dim]Scoring variant {i + 1}...[/dim]")
        variant_score = _score_description(skill_name, variant_desc, evals)

        results.append(
            {
                "label": f"Variant {i + 1}",
                "description": variant_desc,
                "score": variant_score,
            }
        )

    # Step 4: Display comparison
    console.print(f"\n[bold cyan]{'=' * 60}[/bold cyan]")
    console.print("[bold cyan]  A/B Test Results[/bold cyan]")
    console.print(f"[bold cyan]{'=' * 60}[/bold cyan]\n")

    table = Table(title="Score Comparison")
    table.add_column("Variant", style="cyan")
    table.add_column("Trigger", justify="center")
    table.add_column("No-Trigger", justify="center")
    table.add_column("Total", justify="center", style="bold")
    table.add_column("Weaknesses", max_width=40)

    best_idx = 0
    best_total = ""

    for i, r in enumerate(results):
        score = r.get("score") or {}
        trigger = score.get("trigger", "?/?")
        no_trigger = score.get("no_trigger", "?/?")
        total = score.get("total", "?/?")
        weaknesses = score.get("weaknesses", "N/A")

        table.add_row(r["label"], trigger, no_trigger, total, weaknesses)

        # Track best (simple string comparison of fractions)
        if total > best_total:
            best_total = total
            best_idx = i

    console.print(table)

    # Show descriptions
    for r in results:
        console.print(
            Panel(
                r["description"][:500],
                title=r["label"],
                border_style="green" if r["label"] == results[best_idx]["label"] else "dim",
            )
        )

    winner = results[best_idx]
    console.print(f"\n[bold green]Winner: {winner['label']}[/bold green]")

    if best_idx == 0:
        console.print("[green]Current description is already the best![/green]")
        return

    if dry_run:
        console.print("[dim]Dry run: no changes saved.[/dim]")
        return

    from cli.utils import confirm_action

    if not confirm_action(f"Apply winning description ({winner['label']})?", default=True):
        console.print("[yellow]No changes made.[/yellow]")
        return

    if _update_skill_description(skill_md, winner["description"]):
        console.print(f"[green]Description updated with {winner['label']}![/green]")
    else:
        console.print("[red]Failed to update description.[/red]")
        raise click.Abort()
