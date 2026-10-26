# Agent Template

This template helps you create a new Claude Code agent (subagent) that follows the specifications.

## Quick Reference

**File Location:**
- Personal: `~/.claude/agents/agent-name.md`
- Project: `.claude/agents/agent-name.md`

**Naming Rules:**
- Lowercase letters, numbers, and hyphens only
- Maximum 64 characters
- Example: `code-reviewer`, `debugger`, `test-writer`

---

## AGENT.md Template

Copy the content below to create your agent:

```markdown
---
name: agent-name
description: |
  Brief description of what this agent does.
  Use proactively when [specific trigger conditions].
tools: Read, Grep, Glob, Bash
model: opus
---

# Agent Name

You are a specialized agent for [purpose].

## When to Use

This agent should be invoked when:
- [Trigger condition 1]
- [Trigger condition 2]

## Capabilities

- [Capability 1]
- [Capability 2]

## Instructions

When invoked:
1. [First step]
2. [Second step]
3. [Third step]

## Output Format

Provide results in the following format:
- [Format description]

## Constraints

- [Constraint 1]
- [Constraint 2]
```

---

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase with hyphens, max 64 chars |
| `description` | Yes | What the agent does and when to use it (max 1024 chars) |
| `tools` | No | Comma-separated list of allowed tools (default: all) |
| `model` | No | Model to use: `sonnet`, `opus`, `haiku` (default: inherits) |
| `disallowedTools` | No | Tools to explicitly disallow |

---

## Available Tools

Agents can use any combination of these tools:

**File Operations:**
- `Read` - Read file contents
- `Write` - Create new files
- `Edit` - Modify existing files
- `Glob` - Find files by pattern
- `Grep` - Search file contents

**Execution:**
- `Bash` - Execute shell commands
- `Task` - Spawn sub-agents

**Web:**
- `WebFetch` - Fetch URL content
- `WebSearch` - Search the web

**Interaction:**
- `AskUserQuestion` - Prompt user for input
- `TodoWrite` - Manage task lists

**Special:**
- `NotebookEdit` - Edit Jupyter notebooks
- `Skill` - Invoke skills

---

## Model Selection

| Model | Best For |
|-------|----------|
| `haiku` | Fast, simple tasks, exploration, cost-sensitive |
| `sonnet` | Balanced performance (default) |
| `opus` | Complex reasoning, high-stakes decisions |

---

## Tool Restriction Examples

**Read-only exploration:**
```yaml
tools: Read, Grep, Glob
```

**Code modification:**
```yaml
tools: Read, Write, Edit, Glob, Grep, Bash
```

**Research agent:**
```yaml
tools: Read, Grep, Glob, WebSearch, WebFetch
```

**Restricted (no file writes):**
```yaml
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
```

---

## Best Practices

1. **Write detailed descriptions** - Claude uses them to decide when to delegate
2. **Include "use proactively"** - If the agent should auto-trigger
3. **Limit tool access** - Only grant necessary permissions
4. **Specify output format** - Clear expectations for results
5. **Add constraints** - Prevent undesired behaviors

---

## Example: Code Reviewer Agent

```markdown
---
name: code-reviewer
description: |
  Expert code review specialist. Analyzes code for quality, security,
  and maintainability. Use proactively when reviewing pull requests
  or before committing significant changes.
tools: Read, Grep, Glob, Bash
model: opus
---

# Code Reviewer

You are a senior code reviewer ensuring high standards of code quality.

## When to Use

Invoke this agent when:
- Reviewing pull requests
- Before committing significant changes
- Auditing code quality

## Review Process

1. Run `git diff` to see recent changes
2. Identify modified files
3. Review each file for:
   - Code clarity and readability
   - Security vulnerabilities
   - Error handling
   - Test coverage
   - Performance issues

## Output Format

Provide a structured review:
- **Summary**: Overall assessment
- **Issues**: List of problems found (severity: high/medium/low)
- **Suggestions**: Improvement recommendations
- **Approval**: Ready to merge / Needs changes
```

---

## Testing Your Agent

1. **Install the agent:**
   ```bash
   knowhow agents install my-agent
   ```

2. **Invoke directly:**
   ```
   Use the my-agent agent to [task description]
   ```

3. **Check if it triggers automatically:**
   - Ask Claude to do something matching the agent's description
   - Claude should delegate to the agent

4. **Debug issues:**
   ```bash
   claude --debug
   ```
