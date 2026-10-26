"""Optimize command for skillpack - improve skill descriptions for better triggering.

Inspired by CASCADE (arxiv:2512.23880): Cumulative Agentic Skill Creation through
Autonomous Development and Evolution. Implements the skill evolution phase where
descriptions are iteratively refined based on evaluation feedback.
"""

import subprocess
from pathlib import Path

import click
import yaml
from rich.console import Console

from skillpack.config import Config
from skillpack.utils import confirm_action, find_skill_directories
from skillpack.validator import SkillValidator

console = Console()


def _run_claude_cli(prompt: str, timeout: int = 120) -> str | None:
    """Run claude CLI with a prompt and return output."""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            console.print(f"[red]Error from Claude CLI: {result.stderr}[/red]")
            return None
    except FileNotFoundError:
        console.print(
            "[red]Error: 'claude' CLI not found in PATH. "
            "Install it from https://claude.ai/code[/red]"
        )
        return None
    except subprocess.TimeoutExpired:
        console.print("[red]Error: Claude CLI timed out.[/red]")
        return None


def _find_skill_path(name: str, config: Config) -> Path | None:
    """Find a skill directory by name, checking repo and installed locations."""
    search_paths = []

    repo_path = config.get_repository_path()
    if repo_path and repo_path.exists():
        search_paths.append(repo_path / "skills")

    for target in ("personal", "project"):
        try:
            skills_dir = config.get_skills_dir(target=target)
            if skills_dir and skills_dir.exists():
                search_paths.append(skills_dir)
        except Exception:
            pass

    for base in search_paths:
        candidate = base / name
        if candidate.exists() and (candidate / "SKILL.md").exists():
            return candidate

    return None


def _read_skill_description(skill_md: Path) -> str | None:
    """Extract description from SKILL.md frontmatter."""
    try:
        content = skill_md.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1])
                return str(fm.get("description", ""))
    except Exception:
        pass
    return None


def _update_skill_description(skill_md: Path, new_description: str) -> bool:
    """Update the description field in SKILL.md frontmatter."""
    try:
        content = skill_md.read_text()
        if not content.startswith("---"):
            return False

        parts = content.split("---", 2)
        if len(parts) < 3:
            return False

        fm = yaml.safe_load(parts[1])
        fm["description"] = new_description

        new_fm = yaml.dump(fm, default_flow_style=False, allow_unicode=True)
        new_content = f"---\n{new_fm}---{parts[2]}"
        skill_md.write_text(new_content)
        return True
    except Exception as e:
        console.print(f"[red]Error updating description: {e}[/red]")
        return False


def _generate_evals(skill_name: str, skill_content: str) -> str | None:
    """Generate eval queries for a skill to test triggering accuracy."""
    prompt = f"""You are an expert at evaluating AI skill triggering.

Given this skill definition:
```
{skill_content}
```

Generate exactly 15 evaluation queries to test whether this skill should trigger:

- 8-10 SHOULD-TRIGGER queries: diverse phrasings a user might say that should invoke this skill
  - Include casual and formal phrasings
  - Include specific details (file names, library names, error messages, context)
  - Include indirect requests that still clearly need this skill
  - Vary sentence structure (questions, statements, fragments)

- 5-7 SHOULD-NOT-TRIGGER queries: near-misses that share keywords but should NOT use this skill
  - These should be plausible confusions, not obviously unrelated topics

Format your response exactly as:

## Should-Trigger Queries
1. [query]
2. [query]
...

## Should-Not-Trigger Queries
1. [query]
2. [query]
...

Be specific and realistic. Think about how real users phrase requests."""

    return _run_claude_cli(prompt, timeout=120)


def _generate_improved_description(
    skill_name: str, skill_content: str, evals: str, current_description: str
) -> str | None:
    """Generate an improved description based on eval queries and current weaknesses."""
    prompt = f"""You are an expert at optimizing AI skill descriptions for precise triggering.

Skills are loaded into an LLM's context with their description. The LLM decides whether to
invoke a skill based solely on the description. Two failure modes exist:
- UNDERTRIGGERING: The LLM doesn't invoke the skill when it should (most common problem)
- OVERTRIGGERING: The LLM invokes the skill when it shouldn't

Current skill name: {skill_name}

Current description:
{current_description}

Evaluation queries that reveal triggering gaps:
{evals}

Full skill content for context:
```
{skill_content[:2000]}
```

Write an improved description (max 1024 characters) that:
1. Opens with what the skill does (1 sentence)
2. Has an assertive "Use this skill when the user..." block with SPECIFIC conditions:
   - Concrete verbs and nouns from the should-trigger queries
   - Specific library/tool/file-type names that signal this skill is needed
   - Example user phrasings in quotes if they reveal a pattern
3. Optionally adds "Do NOT use when..." to handle should-not-trigger near-misses
4. Optionally lists dependencies ("Requires: package-name")

Output ONLY the improved description text.
Do NOT include YAML markers, quotes, or any explanation.
The text will go directly into the YAML `description: |` field."""

    return _run_claude_cli(prompt, timeout=120)


def _optimize_single_skill(skill_name, config, dry_run, evals_only, interactive=True):
    """Optimize a single skill. Returns True if successful."""
    skill_path = _find_skill_path(skill_name, config)
    if not skill_path:
        console.print(f"[red]Error: Skill '{skill_name}' not found.[/red]")
        return False

    is_valid, errors = SkillValidator.validate_skill_directory(skill_path)
    if not is_valid:
        console.print(f"[red]Skill '{skill_name}' has validation errors:[/red]")
        for error in errors:
            console.print(f"  [red]- {error}[/red]")
        return False

    skill_md = skill_path / "SKILL.md"
    skill_content = skill_md.read_text()
    current_description = _read_skill_description(skill_md) or ""

    console.print(f"\n[bold]Optimizing skill: [cyan]{skill_name}[/cyan][/bold]")
    console.print(f"[dim]Path: {skill_path}[/dim]\n")

    console.print("[yellow]Generating evaluation queries...[/yellow]")
    evals = _generate_evals(skill_name, skill_content)
    if not evals:
        console.print("[red]Failed to generate eval queries.[/red]")
        return False

    if evals_only:
        console.print("\n[bold cyan]── Evaluation Queries ──[/bold cyan]")
        console.print(evals)
        console.print()
        return True

    console.print("[yellow]Generating improved description...[/yellow]")
    new_description = _generate_improved_description(
        skill_name, skill_content, evals, current_description
    )
    if not new_description:
        console.print("[red]Failed to generate improved description.[/red]")
        return False

    console.print("\n[bold cyan]── Current Description ──[/bold cyan]")
    console.print(current_description.strip())
    console.print("\n[bold cyan]── Proposed Description ──[/bold cyan]")
    console.print(new_description.strip())
    console.print()

    if dry_run:
        console.print("[dim]Dry run: no changes saved.[/dim]")
        return True

    if interactive:
        if not confirm_action("Save the improved description?", default=True):
            console.print("[yellow]Optimization cancelled.[/yellow]")
            return True

    if _update_skill_description(skill_md, new_description):
        console.print(f"\n[green]Description updated for skill '{skill_name}'![/green]")
        return True
    else:
        console.print("[red]Failed to update description.[/red]")
        return False


def _optimize_all_skills(config, dry_run, evals_only):
    """Optimize all skills in the repository."""
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        console.print("[red]Repository path not set or doesn't exist.[/red]")
        console.print("[dim]Set it with: skillpack config set repository /path/to/repo[/dim]")
        raise click.Abort()

    skills_dir = repo_path / "skills"
    skill_dirs = find_skill_directories(skills_dir)

    if not skill_dirs:
        console.print("[yellow]No skills found in repository.[/yellow]")
        return

    console.print(f"\n[bold]Batch optimizing {len(skill_dirs)} skills...[/bold]\n")

    succeeded = 0
    failed = 0
    skipped = 0

    for i, sd in enumerate(skill_dirs, 1):
        skill_name = sd.name
        console.print(f"\n[bold]{'=' * 60}[/bold]")
        console.print(f"[bold]  [{i}/{len(skill_dirs)}] {skill_name}[/bold]")
        console.print(f"[bold]{'=' * 60}[/bold]")

        try:
            success = _optimize_single_skill(
                skill_name, config, dry_run, evals_only, interactive=True
            )
            if success:
                succeeded += 1
            else:
                failed += 1
        except (click.Abort, KeyboardInterrupt):
            console.print(f"\n[yellow]Skipping {skill_name}...[/yellow]")
            skipped += 1

            # Ask if user wants to continue
            try:
                if not confirm_action("Continue with remaining skills?", default=True):
                    break
            except (KeyboardInterrupt, EOFError):
                break

    console.print("\n[bold]Batch optimization complete:[/bold]")
    console.print(f"  [green]Succeeded: {succeeded}[/green]")
    if failed:
        console.print(f"  [red]Failed: {failed}[/red]")
    if skipped:
        console.print(f"  [yellow]Skipped: {skipped}[/yellow]")


@click.command()
@click.argument("skill_name", required=False)
@click.option("--all", "optimize_all", is_flag=True, help="Optimize all skills in the repository")
@click.option("--dry-run", is_flag=True, help="Show proposal without saving")
@click.option(
    "--evals-only",
    is_flag=True,
    help="Generate and display eval queries only, then exit",
)
@click.pass_context
def optimize(ctx, skill_name, optimize_all, dry_run, evals_only):
    """
    Optimize skill description(s) for better triggering accuracy.

    Generates eval queries and proposes improved descriptions that reduce
    undertriggering (Claude not using the skill when it should).
    Inspired by CASCADE (arxiv:2512.23880).

    Requires 'claude' CLI in PATH.

    Examples:

        # Optimize a single skill
        skillpack optimize python-jax

        # Optimize all skills
        skillpack optimize --all

        # Preview without saving
        skillpack optimize python-jax --dry-run

        # Generate evals only
        skillpack optimize python-jax --evals-only
    """
    if not skill_name and not optimize_all:
        console.print("[red]Error: Provide a SKILL_NAME or use --all.[/red]")
        raise click.Abort()

    config = Config()

    if optimize_all:
        _optimize_all_skills(config, dry_run, evals_only)
    else:
        success = _optimize_single_skill(skill_name, config, dry_run, evals_only)
        if not success:
            raise click.Abort()
