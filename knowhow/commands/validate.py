"""Validate a skill repository before publishing it."""

from pathlib import Path

import click
from rich.console import Console
from rich.markup import escape

from knowhow.extras import discover_extras
from knowhow.spec import Finding, check_repo

console = Console()


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--strict", is_flag=True, help="Exit non-zero on warnings too")
@click.option("--quiet", "-q", is_flag=True, help="Only print errors and the summary")
def validate(path, strict, quiet):
    """
    Check a skill repository (or one skill) for compatibility problems.

    Checks every SKILL.md against the Agent Skills specification
    (agentskills.io), and checks that `knowhow add` / `npx skills add` will
    find and install each skill as intended. Commands, subagents, hooks and
    MCP servers are checked too.

    Exits with status 1 if there are errors (or warnings, with --strict),
    so it can run in CI:

    \b
      uvx knowhow validate .
    """
    findings, n_skills = check_repo(path)
    extra_warnings: list[str] = []
    extras = discover_extras(path.resolve(), warnings=extra_warnings)
    findings += [Finding("warning", "extras", w) for w in extra_warnings]
    n_extras = sum(len(v) for v in extras.values())

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]
    for f in sorted(findings, key=lambda f: (f.path, f.level != "error")):
        if quiet and f.level != "error":
            continue
        style = "red" if f.level == "error" else "yellow"
        console.print(f"[{style}]{f.level:7}[/{style}] {escape(f.path)}: {escape(f.message)}")

    summary = (
        f"{n_skills} skill(s), {n_extras} other item(s): "
        f"{len(errors)} error(s), {len(warnings)} warning(s)"
    )
    if errors or (strict and warnings):
        console.print(f"[red]✗ {summary}[/red]")
        raise SystemExit(1)
    console.print(f"[green]✓ {summary}[/green]")
