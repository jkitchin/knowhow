"""Stats command - track and display skill usage metrics.

Inspired by CASCADE (arxiv:2512.23880): Cumulative Agentic Skill Creation through
Autonomous Development and Evolution. Implements the quality-based selection phase
where skills are evaluated on usage frequency, success signals, and applicability.
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import click
import yaml
from rich.console import Console
from rich.table import Table

from cli.config import Config
from cli.utils import find_skill_directories

console = Console()

STATS_DIR = Path.home() / ".config" / "skillz" / "stats"
USAGE_LOG = STATS_DIR / "usage.jsonl"


def _ensure_stats_dir():
    """Create stats directory if it doesn't exist."""
    STATS_DIR.mkdir(parents=True, exist_ok=True)


def log_skill_usage(skill_name: str, triggered: bool = True, source: str = "manual") -> None:
    """Log a skill usage event.

    Args:
        skill_name: Name of the skill
        triggered: Whether the skill was actually used (True) or just matched (False)
        source: How the usage was detected ('manual', 'scan', 'hook')
    """
    _ensure_stats_dir()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "skill": skill_name,
        "triggered": triggered,
        "source": source,
    }
    with open(USAGE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _load_usage_log() -> List[Dict]:
    """Load all usage log entries."""
    entries = []
    if USAGE_LOG.exists():
        with open(USAGE_LOG) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return entries


def _scan_transcripts_for_skills(skills: List[str], max_transcripts: int = 20) -> Counter:
    """Scan recent transcripts to estimate skill usage from mentions."""
    mention_counts = Counter()
    transcript_dir = Path.home() / ".claude" / "projects"

    if not transcript_dir.exists():
        return mention_counts

    transcripts = sorted(
        transcript_dir.rglob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:max_transcripts]

    for t_path in transcripts:
        try:
            content = t_path.read_text(errors="ignore")
            for skill_name in skills:
                if skill_name in content:
                    mention_counts[skill_name] += 1
        except Exception:
            continue

    return mention_counts


def _get_all_skill_names(config: Config) -> List[str]:
    """Get all skill names from repository."""
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        return []

    skills_dir = repo_path / "skills"
    skill_dirs = find_skill_directories(skills_dir)

    names = []
    for sd in skill_dirs:
        names.append(sd.name)
    return names


def _get_skill_metadata(config: Config) -> Dict[str, Dict]:
    """Get metadata for all skills."""
    repo_path = config.get_repository_path()
    if not repo_path or not repo_path.exists():
        return {}

    skills_dir = repo_path / "skills"
    skill_dirs = find_skill_directories(skills_dir)

    metadata = {}
    for sd in skill_dirs:
        skill_md = sd / "SKILL.md"
        if skill_md.exists():
            try:
                content = skill_md.read_text()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        fm = yaml.safe_load(parts[1])
                        desc = str(fm.get("description", ""))
                        # Estimate skill size
                        body = parts[2] if len(parts) > 2 else ""
                        metadata[sd.name] = {
                            "description": desc[:80],
                            "size": len(body),
                            "path": str(sd),
                        }
            except Exception:
                pass
    return metadata


def _compute_stats(config: Config, scan: bool = False) -> Tuple[Dict, Counter]:
    """Compute usage statistics.

    Returns:
        Tuple of (metadata dict, usage counts)
    """
    metadata = _get_skill_metadata(config)
    usage_entries = _load_usage_log()

    # Count from usage log
    usage_counts = Counter()
    for entry in usage_entries:
        if entry.get("triggered", True):
            usage_counts[entry["skill"]] += 1

    # Optionally scan transcripts
    if scan:
        skill_names = list(metadata.keys())
        mention_counts = _scan_transcripts_for_skills(skill_names)
        for name, count in mention_counts.items():
            usage_counts[name] += count

    return metadata, usage_counts


@click.command()
@click.option("--scan", is_flag=True, help="Scan recent session transcripts for skill mentions")
@click.option(
    "--sort",
    "sort_by",
    type=click.Choice(["usage", "name", "size"]),
    default="usage",
    show_default=True,
    help="Sort results by",
)
@click.option("--unused", is_flag=True, help="Show only unused skills")
@click.option("--top", default=0, help="Show only top N skills")
@click.option("--log", "log_skill", help="Manually log a skill usage event")
@click.option("--reset", is_flag=True, help="Reset usage statistics")
@click.pass_context
def stats(ctx, scan, sort_by, unused, top, log_skill, reset):
    """
    Track and display skill usage statistics.

    Monitors which skills are used, how often, and identifies unused skills
    that may need optimization or removal. Inspired by CASCADE (arxiv:2512.23880).

    Examples:

        # Show usage stats
        skillz stats

        # Scan transcripts for skill mentions
        skillz stats --scan

        # Show unused skills
        skillz stats --unused

        # Show top 10 most used
        skillz stats --top 10

        # Manually log a skill usage
        skillz stats --log python-jax

        # Reset all statistics
        skillz stats --reset
    """
    config = Config()

    if reset:
        if confirm_action("Reset all usage statistics?"):
            if USAGE_LOG.exists():
                USAGE_LOG.unlink()
            console.print("[green]Usage statistics reset.[/green]")
        return

    if log_skill:
        log_skill_usage(log_skill, triggered=True, source="manual")
        console.print(f"[green]Logged usage for '{log_skill}'.[/green]")
        return

    metadata, usage_counts = _compute_stats(config, scan=scan)

    if not metadata:
        console.print(
            "[red]No skills found. Set repository path with: "
            "skillz config set repository /path/to/repo[/red]"
        )
        return

    # Build table data
    rows = []
    for name, meta in metadata.items():
        count = usage_counts.get(name, 0)
        rows.append((name, meta["description"], count, meta["size"]))

    # Filter
    if unused:
        rows = [(n, d, c, s) for n, d, c, s in rows if c == 0]

    # Sort
    if sort_by == "usage":
        rows.sort(key=lambda r: r[2], reverse=True)
    elif sort_by == "name":
        rows.sort(key=lambda r: r[0])
    elif sort_by == "size":
        rows.sort(key=lambda r: r[3], reverse=True)

    # Limit
    if top > 0:
        rows = rows[:top]

    # Display
    table = Table(title="Skill Usage Statistics")
    table.add_column("Skill", style="cyan", no_wrap=True)
    table.add_column("Description", max_width=50)
    table.add_column("Usage", justify="right", style="green")
    table.add_column("Size", justify="right", style="dim")

    for name, desc, count, size in rows:
        size_str = f"{size // 1024}K" if size >= 1024 else f"{size}B"
        count_style = "green" if count > 0 else "red"
        table.add_row(name, desc, f"[{count_style}]{count}[/{count_style}]", size_str)

    console.print(table)

    total = len(metadata)
    used = sum(1 for n in metadata if usage_counts.get(n, 0) > 0)
    console.print(f"\n[dim]Total: {total} skills | " f"Used: {used} | Unused: {total - used}[/dim]")

    if scan:
        console.print(
            "[dim]Note: Transcript scan counts are approximate " "(based on name mentions).[/dim]"
        )


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(message + suffix).lower().strip()
    if not response:
        return default
    return response in ("y", "yes")
