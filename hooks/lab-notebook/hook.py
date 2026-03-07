#!/usr/bin/env python3
"""Lab notebook hook - Generate lab notebook entries from Claude Code sessions."""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_transcript(transcript_path: str) -> list[dict[str, Any]]:
    """Load and parse the JSONL transcript file."""
    entries = []
    path = Path(transcript_path)

    if not path.exists():
        return entries

    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass

    return entries


def extract_session_data(transcript: list[dict[str, Any]]) -> dict[str, Any]:
    """Extract relevant data from the transcript."""
    user_prompts = []
    files_modified = set()
    files_read = set()
    commands_run = []
    tool_uses = []

    for entry in transcript:
        entry_type = entry.get("type", "")

        # Extract user messages
        if entry_type == "human" or entry_type == "user":
            content = entry.get("message", {}).get("content", "")
            if isinstance(content, str) and content.strip():
                user_prompts.append(content.strip())
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "").strip()
                        if text:
                            user_prompts.append(text)

        # Extract tool uses
        elif entry_type == "tool_use":
            tool_name = entry.get("name", "")
            tool_input = entry.get("input", {})

            tool_uses.append({"tool": tool_name, "input": tool_input})

            if tool_name in ("Write", "Edit"):
                file_path = tool_input.get("file_path", "")
                if file_path:
                    files_modified.add(file_path)

            elif tool_name == "Read":
                file_path = tool_input.get("file_path", "")
                if file_path:
                    files_read.add(file_path)

            elif tool_name == "Bash":
                command = tool_input.get("command", "")
                if command:
                    commands_run.append(command)

    return {
        "user_prompts": user_prompts,
        "files_modified": sorted(files_modified),
        "files_read": sorted(files_read),
        "commands_run": commands_run,
        "tool_uses": tool_uses,
    }


def get_git_info(cwd: str) -> dict[str, str] | None:
    """Get git repository information."""
    try:
        # Check if in a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None

        # Get branch name
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        # Get status summary
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        uncommitted = (
            len(status_result.stdout.strip().split("\n")) if status_result.stdout.strip() else 0
        )

        # Get last commit
        log_result = subprocess.run(
            ["git", "log", "-1", "--format=%h %s"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        last_commit = log_result.stdout.strip() if log_result.returncode == 0 else ""

        return {
            "branch": branch,
            "uncommitted_files": uncommitted,
            "last_commit": last_commit,
        }
    except Exception:
        return None


def generate_markdown(
    session_id: str,
    cwd: str,
    session_data: dict[str, Any],
    git_info: dict[str, str] | None,
) -> str:
    """Generate a markdown lab notebook entry."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Lab Notebook Entry",
        "",
        f"**Date**: {date_str}",
        f"**Session**: `{session_id[:12] if len(session_id) > 12 else session_id}`",
        f"**Project**: `{cwd}`",
    ]

    if git_info:
        lines.append(f"**Git Branch**: `{git_info['branch']}`")

    lines.extend(["", "## Objective", ""])

    # First user prompt as objective
    if session_data["user_prompts"]:
        objective = session_data["user_prompts"][0]
        # Truncate if too long
        if len(objective) > 500:
            objective = objective[:500] + "..."
        lines.append(objective)
    else:
        lines.append("_No objective recorded_")

    lines.extend(["", "## Work Performed", ""])

    # User prompts
    if session_data["user_prompts"]:
        lines.append("### User Prompts")
        for i, prompt in enumerate(session_data["user_prompts"], 1):
            # Truncate long prompts
            display_prompt = prompt[:200] + "..." if len(prompt) > 200 else prompt
            display_prompt = display_prompt.replace("\n", " ")
            lines.append(f"{i}. {display_prompt}")
        lines.append("")

    # Files modified
    if session_data["files_modified"]:
        lines.append("### Files Modified")
        for f in session_data["files_modified"]:
            lines.append(f"- `{f}`")
        lines.append("")

    # Files read
    if session_data["files_read"]:
        lines.append("### Files Read")
        for f in session_data["files_read"][:20]:  # Limit to 20
            lines.append(f"- `{f}`")
        if len(session_data["files_read"]) > 20:
            lines.append(f"- _... and {len(session_data['files_read']) - 20} more_")
        lines.append("")

    # Commands executed
    if session_data["commands_run"]:
        lines.append("### Commands Executed")
        lines.append("```bash")
        for cmd in session_data["commands_run"][:30]:  # Limit to 30
            lines.append(cmd)
        if len(session_data["commands_run"]) > 30:
            lines.append(f"# ... and {len(session_data['commands_run']) - 30} more commands")
        lines.append("```")
        lines.append("")

    # Git status
    if git_info:
        lines.extend(
            [
                "## Git Status",
                "",
                f"- **Branch**: {git_info['branch']}",
                f"- **Uncommitted changes**: {git_info['uncommitted_files']} files",
            ]
        )
        if git_info["last_commit"]:
            lines.append(f"- **Last commit**: {git_info['last_commit']}")
        lines.append("")

    lines.extend(
        [
            "---",
            f"_Generated automatically by lab-notebook hook at {date_str}_",
        ]
    )

    return "\n".join(lines)


def generate_json(
    session_id: str,
    cwd: str,
    session_data: dict[str, Any],
    git_info: dict[str, str] | None,
) -> str:
    """Generate a JSON lab notebook entry."""
    now = datetime.now()

    entry = {
        "timestamp": now.isoformat(),
        "session_id": session_id,
        "project": cwd,
        "git": git_info,
        "objective": session_data["user_prompts"][0] if session_data["user_prompts"] else None,
        "prompts": session_data["user_prompts"],
        "files_modified": session_data["files_modified"],
        "files_read": session_data["files_read"],
        "commands": session_data["commands_run"],
    }

    return json.dumps(entry, indent=2)


def generate_org(
    session_id: str,
    cwd: str,
    session_data: dict[str, Any],
    git_info: dict[str, str] | None,
) -> str:
    """Generate an org-mode lab notebook entry."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    org_date = now.strftime("[%Y-%m-%d %a %H:%M]")

    # Build title from first prompt (truncated) or default
    prompts = session_data["user_prompts"]
    title = prompts[0][:50] if prompts else "Session"
    lines = [
        f"* {date_str} Claude Session: {title}",
        ":PROPERTIES:",
        f":SESSION_ID: {session_id}",
        f":PROJECT: {cwd}",
        f":CREATED: {org_date}",
    ]

    if git_info:
        lines.append(f":GIT_BRANCH: {git_info['branch']}")

    lines.extend([":END:", ""])

    # Objective
    lines.append("** Objective")
    if session_data["user_prompts"]:
        lines.append(session_data["user_prompts"][0])
    lines.append("")

    # Files modified
    if session_data["files_modified"]:
        lines.append("** Files Modified")
        for f in session_data["files_modified"]:
            lines.append(f"- [[file:{f}][{Path(f).name}]]")
        lines.append("")

    # Commands
    if session_data["commands_run"]:
        lines.append("** Commands Executed")
        lines.append("#+BEGIN_SRC bash")
        for cmd in session_data["commands_run"][:20]:
            lines.append(cmd)
        lines.append("#+END_SRC")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main hook entry point."""
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract relevant fields
    session_id = input_data.get("session_id", "unknown")
    transcript_path = input_data.get("transcript_path", "")
    cwd = input_data.get("cwd", os.getcwd())

    # Configuration from environment
    notebook_dir = os.environ.get("LAB_NOTEBOOK_DIR", "~/lab-notebook/claude-sessions")
    notebook_dir = os.path.expanduser(notebook_dir)
    output_format = os.environ.get("LAB_NOTEBOOK_FORMAT", "markdown").lower()
    include_git = os.environ.get("LAB_NOTEBOOK_GIT_INFO", "true").lower() == "true"

    # Load and parse transcript
    transcript = load_transcript(transcript_path) if transcript_path else []
    session_data = extract_session_data(transcript)

    # Skip if no meaningful content
    if not session_data["user_prompts"] and not session_data["files_modified"]:
        print("No meaningful session content to log", file=sys.stderr)
        sys.exit(0)

    # Get git info if enabled
    git_info = get_git_info(cwd) if include_git else None

    # Generate output
    if output_format == "json":
        content = generate_json(session_id, cwd, session_data, git_info)
        ext = "json"
    elif output_format == "org":
        content = generate_org(session_id, cwd, session_data, git_info)
        ext = "org"
    else:
        content = generate_markdown(session_id, cwd, session_data, git_info)
        ext = "md"

    # Save to file
    Path(notebook_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    short_id = session_id[:8] if len(session_id) > 8 else session_id
    filename = f"{date_str}_{short_id}.{ext}"
    output_path = Path(notebook_dir) / filename

    try:
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Lab notebook entry saved: {output_path}")
    except Exception as e:
        print(f"Error saving notebook entry: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
