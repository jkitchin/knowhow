# Hook Template

This template helps you create a new Claude Code hook that follows the specifications.

## Quick Reference

**File Location:**
- Personal: `~/.claude/hooks/hook-name/`
- Project: `.claude/hooks/hook-name/`

**Naming Rules:**
- Lowercase letters, numbers, and hyphens only
- Maximum 64 characters
- Example: `lab-notebook`, `prettier-on-save`, `protect-secrets`

**Hook Events:**
- `PreToolUse` - Before tool calls (can block)
- `PostToolUse` - After tool completes
- `PermissionRequest` - When permission dialogs appear (can block)
- `UserPromptSubmit` - When user submits prompt (can block)
- `Notification` - When Claude sends notifications
- `Stop` - When Claude finishes responding (can block)
- `SubagentStop` - When subagent completes (can block)
- `PreCompact` - Before context compaction
- `SessionStart` - When session starts
- `SessionEnd` - When session ends

---

## HOOK.md Template

Copy the content below to create your hook:

```markdown
---
name: hook-name
description: Short description of what this hook does (max 256 chars)
event: PreToolUse
matcher: Bash|Edit|Write
type: command
timeout: 60
---

# Hook Name

## Purpose

[What this hook does and why it's useful]

## Configuration

When installed, this hook will be added to your Claude Code settings with the following configuration:

- **Event**: [PreToolUse/PostToolUse/etc.]
- **Matcher**: [Tool pattern to match, e.g., "Bash", "Edit|Write", or "*" for all]
- **Type**: [command or prompt]
- **Timeout**: [Timeout in seconds]

## Behavior

[Describe what the hook does when triggered]

### Input

The hook receives JSON via stdin:
```json
{
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "tool_name": "Bash",
  "tool_input": { ... }
}
```

### Output

[Describe exit codes and any JSON output]

- Exit 0: [Success behavior]
- Exit 2: [Blocking behavior, if applicable]

## Requirements

[List any dependencies]

- Python 3.8+
- [Other requirements]

## Examples

[Show example scenarios]

## Limitations

[Note any limitations]
```

---

## Hook Script Template (Python)

```python
#!/usr/bin/env python3
"""Hook description."""

import json
import sys
from pathlib import Path

def main():
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract relevant fields
    session_id = input_data.get("session_id", "")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    cwd = input_data.get("cwd", "")
    transcript_path = input_data.get("transcript_path", "")

    # Your hook logic here
    # ...

    # Exit codes:
    # 0 = success (allow operation)
    # 2 = block operation (for PreToolUse, PermissionRequest, UserPromptSubmit)
    # Other = non-blocking error

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Hook Script Template (Bash)

```bash
#!/bin/bash
# Hook description

# Read JSON input
INPUT=$(cat)

# Extract fields using jq
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

# Your hook logic here
# ...

# Exit codes:
# 0 = success (allow operation)
# 2 = block operation
exit 0
```

---

## Exit Codes Reference

| Code | Meaning | Use Case |
|------|---------|----------|
| 0 | Success | Allow operation, optionally output JSON for control |
| 2 | Block | Deny operation (PreToolUse, PermissionRequest, etc.) |
| Other | Error | Non-blocking error, shown in verbose mode |

---

## JSON Output Structure (Exit 0)

For advanced control, output JSON to stdout:

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Optional warning message",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Auto-approved by hook",
    "additionalContext": "Extra context for Claude"
  }
}
```

---

## Environment Variables

Available in all hooks:
- `$CLAUDE_PROJECT_DIR` - Absolute path to project root
- `$CLAUDE_CODE_REMOTE` - "true" if running remotely

SessionStart only:
- `$CLAUDE_ENV_FILE` - File to persist environment variables

---

## Validation Checklist

Before deploying your hook:

- [ ] `name` uses only lowercase, numbers, and hyphens
- [ ] `name` is 64 characters or less
- [ ] `description` is 256 characters or less
- [ ] `event` is a valid hook event
- [ ] `matcher` is valid (regex pattern or "*")
- [ ] `type` is "command" or "prompt"
- [ ] Script is executable (`chmod +x`)
- [ ] Script handles JSON input correctly
- [ ] Exit codes are used appropriately
- [ ] Dependencies are documented

---

## Testing Your Hook

1. **Test the script directly:**
   ```bash
   echo '{"tool_name": "Bash", "tool_input": {"command": "ls"}}' | ./hook.py
   echo $?  # Check exit code
   ```

2. **Install and test with Claude Code:**
   ```bash
   skillpack hooks install your-hook-name
   claude --debug  # See hook execution in logs
   ```

3. **Check settings.json:**
   ```bash
   cat ~/.claude/settings.json | jq '.hooks'
   ```
