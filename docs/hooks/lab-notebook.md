# Lab Notebook Hook

Generate structured lab notebook entries from Claude Code sessions for documentation and reproducibility.

## Overview

| Field | Value |
|-------|-------|
| Name | `lab-notebook` |
| Event | `SessionEnd` |
| Type | `command` |
| Timeout | 30 seconds |

## Purpose

The lab-notebook hook automatically creates a detailed record of your Claude Code sessions when they end. It captures:

- Session metadata (ID, timestamp, project path)
- User prompts and objectives
- Files modified and read during the session
- Commands executed
- Git repository status

## Use Cases

- **Research Documentation**: Track AI-assisted experiments and analysis
- **Code Review**: Document what changes were made and why
- **Learning**: Review past sessions to learn from them
- **Compliance**: Maintain audit trails of AI-assisted work
- **Collaboration**: Share session summaries with teammates
- **Debugging**: Review what happened during a session

## Configuration

Configure the hook using environment variables:

```bash
# Output directory (default: ~/lab-notebook/claude-sessions)
export LAB_NOTEBOOK_DIR="~/lab-notebook"

# Output format: markdown (default), json, or org
export LAB_NOTEBOOK_FORMAT="markdown"

# Include git status information (default: true)
export LAB_NOTEBOOK_GIT_INFO="true"
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LAB_NOTEBOOK_DIR` | `~/lab-notebook/claude-sessions` | Where to save entries |
| `LAB_NOTEBOOK_FORMAT` | `markdown` | Output format (markdown, json, org) |
| `LAB_NOTEBOOK_GIT_INFO` | `true` | Include git branch and status |

## Output Location

Entries are saved to:
```
~/lab-notebook/claude-sessions/YYYY-MM-DD_SESSION-ID.{md,json,org}
```

For example:
```
~/lab-notebook/claude-sessions/2024-01-15_abc123de.md
```

## Output Formats

### Markdown (Default)

Human-readable format with clear sections:

```markdown
# Lab Notebook Entry

**Date**: 2024-01-15 14:30
**Session**: `abc123de`
**Project**: `/home/user/myproject`
**Git Branch**: `feature/new-api`

## Objective

Implement user authentication for the REST API

## Work Performed

### User Prompts
1. Add JWT authentication to the Flask API
2. Create tests for the auth endpoints

### Files Modified
- `src/auth.py`
- `src/routes/users.py`
- `tests/test_auth.py`

### Files Read
- `src/config.py`
- `requirements.txt`

### Commands Executed
```bash
pytest tests/test_auth.py
git diff
pip install pyjwt
```

## Git Status

- **Branch**: feature/new-api
- **Uncommitted changes**: 3 files
- **Last commit**: abc1234 Add initial auth module

---
_Generated automatically by lab-notebook hook at 2024-01-15 14:30_
```

### JSON

Structured format for tooling and analysis:

```json
{
  "timestamp": "2024-01-15T14:30:22.123456",
  "session_id": "abc123def456",
  "project": "/home/user/myproject",
  "git": {
    "branch": "feature/new-api",
    "uncommitted_files": 3,
    "last_commit": "abc1234 Add initial auth module"
  },
  "objective": "Implement user authentication for the REST API",
  "prompts": [
    "Add JWT authentication to the Flask API",
    "Create tests for the auth endpoints"
  ],
  "files_modified": [
    "src/auth.py",
    "src/routes/users.py",
    "tests/test_auth.py"
  ],
  "files_read": [
    "src/config.py",
    "requirements.txt"
  ],
  "commands": [
    "pytest tests/test_auth.py",
    "git diff",
    "pip install pyjwt"
  ]
}
```

### Org-mode

For Emacs users, entries are formatted as org-mode:

```org
* 2024-01-15 14:30 Claude Session: Implement user authentication for th...
:PROPERTIES:
:SESSION_ID: abc123def456
:PROJECT: /home/user/myproject
:CREATED: [2024-01-15 Mon 14:30]
:GIT_BRANCH: feature/new-api
:END:

** Objective
Implement user authentication for the REST API

** Files Modified
- [[file:src/auth.py][auth.py]]
- [[file:src/routes/users.py][users.py]]
- [[file:tests/test_auth.py][test_auth.py]]

** Commands Executed
#+BEGIN_SRC bash
pytest tests/test_auth.py
git diff
pip install pyjwt
#+END_SRC
```

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

## Behavior

1. Triggered when a Claude Code session ends
2. Reads the session transcript from the provided `transcript_path`
3. Parses user prompts, tool uses, and Claude responses
4. Optionally collects git repository information
5. Generates a formatted notebook entry
6. Saves to the configured output directory
7. Prints confirmation message to stdout

### Handling Edge Cases

- **Empty sessions**: Skips logging if no meaningful content (no prompts or file changes)
- **Missing git**: Gracefully handles non-git directories
- **Long content**: Truncates very long prompts and limits file lists

## Installation

```bash
# Install to personal directory
knowhow hooks install lab-notebook

# Install to project directory
knowhow hooks install lab-notebook --target project

# Preview what would be installed
knowhow hooks install lab-notebook --dry-run
```

## Tips

### Organizing Entries

Set different directories for different projects:

```bash
# In your project's .envrc or shell profile
export LAB_NOTEBOOK_DIR="$HOME/notes/projects/$(basename $PWD)"
```

### Analyzing JSON Entries

Use jq to analyze your session history:

```bash
# Find sessions that modified a specific file
cat ~/lab-notebook/claude-sessions/*.json | jq 'select(.files_modified[] | contains("auth.py"))'

# Count sessions by month
ls ~/lab-notebook/claude-sessions/*.json | cut -d'_' -f1 | sort | uniq -c
```

### Integrating with Note-Taking Apps

- **Obsidian**: Point `LAB_NOTEBOOK_DIR` to your vault
- **Logseq**: Use org-mode format for better compatibility
- **Notion**: Use JSON format and import via API
