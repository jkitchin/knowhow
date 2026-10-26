# Security Hooks

Protect sensitive files and maintain audit trails of Claude Code activity.

## Protect Secrets

Block writes to files containing secrets, credentials, or sensitive configuration.

### Overview

| Field | Value |
|-------|-------|
| Name | `protect-secrets` |
| Event | `PreToolUse` |
| Matcher | `Edit\|Write` |
| Type | `command` |
| Timeout | 5 seconds |

### Purpose

This security guardrail prevents Claude from accidentally writing to or modifying files that may contain secrets, API keys, credentials, or sensitive configuration. It acts as a safety net to prevent accidental exposure or modification of sensitive data.

### Protected Patterns

By default, the hook blocks writes to:

#### Environment Files
- `.env`, `.env.*`, `*.env`
- `.env.local`, `.env.production`, `.env.development`

#### Credential Files
- `credentials.json`, `credentials.yaml`, `credentials.yml`
- `secrets.json`, `secrets.yaml`, `secrets.yml`
- `secret.json`, `secret.yaml`, `secret.yml`

#### Private Keys
- `*.pem`, `*.key`, `*.p12`, `*.pfx`
- `id_rsa`, `id_rsa.*`
- `id_ed25519`, `id_ed25519.*`
- `id_ecdsa`, `id_dsa` (and variants)

#### Cloud Provider Configs
- AWS: `~/.aws/credentials`, `~/.aws/config`
- GCP: `gcloud/credentials.db`, `application_default_credentials.json`
- Azure: `.azure/` directory

#### SSH/Git
- `~/.ssh/config`, `~/.ssh/known_hosts`, `~/.ssh/authorized_keys`
- `.git-credentials`, `.gitconfig`, `.netrc`

#### Container/Orchestration
- `.docker/config.json`
- `kubeconfig`, `.kube/config`

#### Package Managers
- `.npmrc`
- `.pypirc`

#### Infrastructure
- `*.tfvars`
- `terraform.tfstate`, `terraform.tfstate.backup`

### Configuration

Customize behavior with environment variables:

```bash
# Add additional protected patterns (comma-separated)
export PROTECT_SECRETS_EXTRA="*.secret,my-credentials.txt,config/prod/*"

# Allow specific files (bypass protection)
export PROTECT_SECRETS_ALLOW=".env.example,.env.template"
```

### Behavior

1. Triggered before Edit/Write tool executes
2. Extracts file path from tool input
3. Checks file against protected patterns
4. If match found:
   - Exits with code 2 (blocks the operation)
   - Sends descriptive error to Claude
5. If no match: exits 0 (operation proceeds)

### Error Message

When a write is blocked, Claude sees:

```
BLOCKED: Cannot write to protected file.

File: /home/user/project/.env
Matched pattern: .env

This file appears to contain secrets or sensitive configuration.
To proceed, please:
1. Ask the user to manually edit this file, OR
2. Use a template file (e.g., .env.example) instead

Set PROTECT_SECRETS_ALLOW=".env" to allow this file.
```

### Notes

- **Blocking hook**: Actively prevents dangerous operations
- **Pattern matching**: Uses fnmatch-style glob patterns
- **User bypass**: Users can allow specific files via environment variable
- **Fast execution**: 5-second timeout ensures quick response

### Installation

```bash
# Recommended: install to project for team-wide protection
knowhow hooks install protect-secrets --target project

# Or install personally
knowhow hooks install protect-secrets
```

---

## Bash Logger

Log all bash commands executed by Claude for audit, review, and debugging.

### Overview

| Field | Value |
|-------|-------|
| Name | `bash-logger` |
| Event | `PreToolUse` |
| Matcher | `Bash` |
| Type | `command` |
| Timeout | 5 seconds |

### Purpose

Maintains a complete audit trail of all bash commands executed during Claude Code sessions. This is useful for:

- **Security auditing**: Review what commands were run
- **Debugging**: Trace issues back to specific commands
- **Compliance**: Meet requirements for AI activity logging
- **Learning**: Review past sessions to understand workflows
- **Incident response**: Investigate unexpected behavior

### Log Format

The hook supports three output formats:

#### Full Format (Default)

```
[2024-01-15 14:30:22] [session:abc123def456] [cwd:/home/user/project]
Command: npm test
Description: Run test suite
---
[2024-01-15 14:30:45] [session:abc123def456] [cwd:/home/user/project]
Command: git status
Description: Show working tree status
---
```

#### Compact Format

```
[2024-01-15 14:30:22] [abc123de] npm test
[2024-01-15 14:30:45] [abc123de] git status
```

#### JSON Format

```json
{"timestamp": "2024-01-15T14:30:22.123456", "session_id": "abc123def456", "cwd": "/home/user/project", "command": "npm test", "description": "Run test suite"}
{"timestamp": "2024-01-15T14:30:45.789012", "session_id": "abc123def456", "cwd": "/home/user/project", "command": "git status", "description": "Show working tree status"}
```

### Log Location

Default: `~/.claude/logs/bash-commands.log`

### Configuration

```bash
# Custom log file location
export BASH_LOGGER_FILE="~/my-logs/claude-commands.log"

# Log format: full (default), compact, json
export BASH_LOGGER_FORMAT="full"

# Exclude certain commands (regex pattern)
export BASH_LOGGER_EXCLUDE="^(ls|pwd|echo)"
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASH_LOGGER_FILE` | `~/.claude/logs/bash-commands.log` | Log file path |
| `BASH_LOGGER_FORMAT` | `full` | Output format |
| `BASH_LOGGER_EXCLUDE` | (none) | Regex pattern for commands to skip |

### Behavior

1. Triggered before Bash tool executes
2. Extracts command and description from tool input
3. Checks against exclusion pattern (if configured)
4. Formats log entry based on configured format
5. Appends to log file (creates directory if needed)
6. Rotates log when it exceeds 10MB (keeps 5 backups)
7. Exits 0 (never blocks commands)

### Log Rotation

The hook automatically rotates logs:

- Triggers when log exceeds 10MB
- Keeps 5 backup files
- Naming: `bash-commands.log.1`, `bash-commands.log.2`, etc.

### Notes

- **Non-blocking**: Never prevents command execution
- **Automatic rotation**: Prevents unbounded log growth
- **Configurable exclusions**: Skip noisy commands like `ls` or `pwd`
- **Fast execution**: 5-second timeout, typically completes instantly

### Installation

```bash
knowhow hooks install bash-logger
```

### Analyzing Logs

```bash
# View recent commands
tail -50 ~/.claude/logs/bash-commands.log

# Search for specific commands
grep "git commit" ~/.claude/logs/bash-commands.log

# Count commands by type (with JSON format)
cat ~/.claude/logs/bash-commands.log | jq -r '.command' | cut -d' ' -f1 | sort | uniq -c | sort -rn

# Find commands from a specific session
grep "session:abc123" ~/.claude/logs/bash-commands.log
```

---

## Using Both Security Hooks

For comprehensive security, install both hooks:

```bash
knowhow hooks install protect-secrets --target project
knowhow hooks install bash-logger
```

This gives you:
- **Prevention**: Block accidental secret exposure
- **Detection**: Full audit trail of all commands

## Security Considerations

1. **Log file permissions**: Ensure log files are readable only by you
   ```bash
   chmod 600 ~/.claude/logs/bash-commands.log
   ```

2. **Log rotation**: Logs contain command history; rotate and archive appropriately

3. **Exclusion patterns**: Be careful not to exclude security-relevant commands

4. **Protected patterns**: Review defaults and add project-specific patterns as needed
