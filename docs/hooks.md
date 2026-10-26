# Claude Code Hooks

Hooks are custom scripts that run at specific points during Claude Code sessions. They allow you to extend Claude Code's functionality with automated actions like formatting code, logging commands, protecting sensitive files, and sending notifications.

## What Are Hooks?

Hooks are executable scripts (Python or shell) that Claude Code runs automatically in response to specific events. They receive context about the current operation via stdin (as JSON) and can:

- **Observe**: Log activity, generate reports, send notifications
- **Transform**: Modify tool inputs or outputs
- **Block**: Prevent operations that match certain criteria (security guardrails)

## Hook Events

Claude Code supports 10 hook event types:

| Event | Description | Blocking |
|-------|-------------|----------|
| `PreToolUse` | Before a tool is executed | Yes |
| `PostToolUse` | After a tool completes | No |
| `PermissionRequest` | When Claude requests permission | Yes |
| `UserPromptSubmit` | When user submits a prompt | Yes |
| `Notification` | When Claude sends a notification | No |
| `Stop` | When Claude stops (waiting for input) | No |
| `SubagentStop` | When a subagent completes | No |
| `PreCompact` | Before context compaction | No |
| `SessionStart` | When a session begins | No |
| `SessionEnd` | When a session ends | No |

### Event Details

**PreToolUse** - Runs before tools like Bash, Edit, Write, etc. Can block operations by exiting with code 2. Useful for security guardrails.

**PostToolUse** - Runs after tool completion. Cannot block but can perform follow-up actions like formatting files.

**Stop** - Runs when Claude finishes responding and is waiting for user input. Perfect for notifications.

**SessionStart/SessionEnd** - Run at session boundaries. Useful for logging and documentation.

## How Hooks Work

### Input

Hooks receive JSON on stdin with contextual information:

```json
{
  "session_id": "abc123def",
  "cwd": "/home/user/project",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/home/user/project/src/main.py",
    "old_string": "...",
    "new_string": "..."
  },
  "transcript_path": "/path/to/transcript.jsonl"
}
```

The exact fields depend on the event type:

- **PreToolUse/PostToolUse**: Include `tool_name` and `tool_input`
- **SessionEnd**: Includes `transcript_path` for accessing the full session log
- **All events**: Include `session_id` and `cwd`

### Output

Hooks communicate via:

- **stdout**: Informational messages displayed to the user
- **stderr**: Error messages and diagnostics
- **Exit codes**:
  - `0` = Success (allow operation to proceed)
  - `1` = Error (logged but operation continues)
  - `2` = Block (for PreToolUse - prevents the operation)

### Example: Blocking a Write Operation

```python
#!/usr/bin/env python3
import json
import sys

input_data = json.load(sys.stdin)
file_path = input_data.get("tool_input", {}).get("file_path", "")

if file_path.endswith(".env"):
    print("BLOCKED: Cannot write to .env files", file=sys.stderr)
    sys.exit(2)  # Exit 2 = block

sys.exit(0)  # Exit 0 = allow
```

## HOOK.md Format

Each hook is a directory containing a `HOOK.md` file and an executable script. The `HOOK.md` file uses YAML frontmatter to configure the hook:

```markdown
---
name: my-hook
description: What this hook does
event: PostToolUse
matcher: Edit|Write
type: command
timeout: 30
---

# My Hook

Documentation for the hook...
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Hook identifier (lowercase, hyphens, max 64 chars) |
| `description` | Yes | Brief description (max 256 chars) |
| `event` | Yes | Event type that triggers the hook |
| `matcher` | No | Regex pattern for tool names (default: `*` matches all) |
| `type` | No | `command` (default) or `prompt` |
| `timeout` | No | Max execution time in seconds (default: 60) |

### Matcher Examples

- `*` - Match all tools (default)
- `Edit` - Only match Edit tool
- `Edit|Write` - Match Edit or Write
- `Bash` - Only match Bash commands

## Installing Hooks with Knowhow

### List Available Hooks

```bash
# List hooks in repository
knowhow hooks list --target repo

# List installed hooks
knowhow hooks list --target personal
knowhow hooks list --target project
```

### Install a Hook

```bash
# Install to personal directory (~/.claude/)
knowhow hooks install lab-notebook

# Install to project directory (.claude/)
knowhow hooks install protect-secrets --target project

# Preview without installing
knowhow hooks install bash-logger --dry-run

# Overwrite existing
knowhow hooks install prettier-on-save --force
```

### Uninstall a Hook

```bash
knowhow hooks uninstall lab-notebook
knowhow hooks uninstall protect-secrets --target project
```

### Get Hook Information

```bash
knowhow hooks info lab-notebook
knowhow hooks search formatting
```

## Creating Hooks with Knowhow

### Create from Template

```bash
# Create a new hook
knowhow hooks create my-hook --event PreToolUse

# Create in project directory
knowhow hooks create my-hook --target project --event PostToolUse
```

This creates:
- `my-hook/HOOK.md` - Metadata and documentation
- `my-hook/hook.py` - Python script template

### Manual Creation

1. Create a directory with your hook name
2. Add a `HOOK.md` file with proper frontmatter
3. Add an executable script (`hook.py` or `hook.sh`)

Example structure:
```
my-hook/
  HOOK.md
  hook.py
```

## Hook Installation Locations

Hooks can be installed to:

- **Personal**: `~/.claude/hooks/` - Available in all sessions
- **Project**: `.claude/hooks/` - Only in current project

The knowhow CLI also updates `settings.json` to register the hook with Claude Code.

## Available Hooks

The knowhow repository includes several ready-to-use hooks:

| Hook | Event | Purpose |
|------|-------|---------|
| [lab-notebook](hooks/lab-notebook.md) | SessionEnd | Generate session documentation |
| [prettier-on-save](hooks/formatting-hooks.md) | PostToolUse | Auto-format JS/TS/CSS files |
| [black-on-save](hooks/formatting-hooks.md) | PostToolUse | Auto-format Python files |
| [protect-secrets](hooks/security-hooks.md) | PreToolUse | Block writes to sensitive files |
| [bash-logger](hooks/security-hooks.md) | PreToolUse | Log all bash commands |
| [notify-done](hooks/notify-done.md) | Stop | Desktop notifications |

## Best Practices

1. **Keep hooks fast**: Use appropriate timeouts and avoid long-running operations
2. **Handle errors gracefully**: Don't crash on unexpected input
3. **Be careful with blocking**: Only use exit code 2 when truly necessary
4. **Log to stderr**: Use stderr for errors, stdout for user-visible messages
5. **Respect configuration**: Use environment variables for customization
6. **Test thoroughly**: Hooks run automatically, so bugs can be disruptive

## Troubleshooting

### Hook Not Running

1. Check that `settings.json` contains the hook configuration
2. Verify the hook script is executable (`chmod +x hook.py`)
3. Check the event type matches when you expect it to run

### Hook Errors

1. Check stderr output in Claude Code
2. Test the hook manually: `echo '{}' | python hook.py`
3. Verify JSON parsing handles edge cases

### Hook Blocking Unexpectedly

1. Check the matcher pattern
2. Review the blocking logic in PreToolUse hooks
3. Use `PROTECT_SECRETS_ALLOW` or similar env vars to whitelist files
