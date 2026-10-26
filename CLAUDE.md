# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Skillpack (formerly skillz; repo renamed from `jkitchin/skillz`) is a CLI tool for managing AI assistant skills and slash commands across multiple LLM platforms (Claude Code, OpenCode, Codex, Gemini, Cursor, Copilot). Its headline feature is `uvx skillpack add owner/repo --skill name`: install skills (npx-skills compatible), commands, subagents, hooks and MCP servers from any git repo without installing skillpack or cloning anything. The repo also hosts a collection of skills, commands, hooks and agents, plus commands to create, validate and evolve them.

## Development Commands

### Setup
```bash
# Install with development dependencies (preferred)
uv pip install -e ".[dev]"

# Alternative with pip
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=skillpack --cov-report=html

# Run specific test file
pytest tests/test_validator.py
```

### Linting and Formatting
```bash
# Check code style
ruff check .
ruff format --check .

# Format code
ruff format .
```

### Running the CLI
```bash
# Via entry point (after installation)
skillpack --help

# Via Python module (during development)
python -m skillpack.main --help
```

## Architecture

### Core Components

**CLI Module (`skillpack/`)** — published as `skillpack` (PyPI `skillz` is taken); console scripts `skillpack` and `skillz`
- `main.py` - Click-based CLI entry point with command registration
- `sources.py`, `fetch.py`, `discovery.py`, `agents_registry.py`, `installer.py`, `lock.py` - remote install pipeline used by `add`/`remove`/`check`/`upgrade` (`commands/add.py`), compatible with `npx skills` (vercel-labs/skills) layout, install paths and lock files
- `config.py` - Configuration management using YAML (`~/.config/skillz/config.yaml`)
- `validator.py` - Validation logic for skills (SKILL.md) and commands (.md files)
- `utils.py` - Shared utilities (name validation, file operations, search functions)
- `commands/` - Individual CLI command implementations (install, uninstall, list, search, info, update, create)

**Skills Repository (`skills/`)**
Each skill is a directory containing:
- `SKILL.md` - Required file with YAML frontmatter (name, description, allowed-tools) and markdown content
- Supporting files: README.md, QUICK_REFERENCE.md, examples/, references/, assets/, scripts/

**Commands Repository (`commands/`)**
Standalone markdown files with optional YAML frontmatter (description, model, allowed-tools, argument-hint).

**Hooks Repository (`hooks/`)**
Each hook is a directory containing:
- `HOOK.md` - Required file with YAML frontmatter (name, description, event, matcher, type, timeout)
- `hook.py` or `hook.sh` - The executable hook script
- Hooks are shell commands that execute at various points in Claude Code's lifecycle

**Agents Repository (`agents/`)**
Standalone markdown files for Claude Code subagents:
- Each agent is a single `.md` file with YAML frontmatter (name, description, tools, model)
- Agents are specialized AI assistants that handle specific tasks independently
- They run in isolated context and return results to the main conversation

**Templates (`templates/`)**
- `SKILL_TEMPLATE.md` - Template for creating new skills
- `COMMAND_TEMPLATE.md` - Template for creating new commands
- `HOOK_TEMPLATE.md` - Template for creating new hooks
- `AGENT_TEMPLATE.md` - Template for creating new agents

### Configuration Flow

1. Config loads from `~/.config/skillz/config.yaml` or uses defaults
2. Config provides paths for personal (default: `~/.claude/`) and project (default: `.claude/`) installations
3. Multi-platform support via `platforms` dict in config: built-ins (claude, opencode, codex, gemini) plus any custom platform defined there (issue #6). `platform_option()` in `skillpack/config.py` resolves `--platform` (default: `default_platform`) and rejects unknown names; `Config._platform_path()` raises `PlatformConfigError` naming the missing key
4. `skillpack add -a` uses `agents_registry.build_registry(config)`: built-in agents plus custom platforms (copy-only targets) and overrides of built-in paths (only values that differ from defaults count, because `save_config()` writes all defaults)

### Validation Logic

**Skills**: Must have valid name (lowercase, hyphens, max 64 chars), description (max 1024 chars), and SKILL.md file with proper YAML frontmatter.

**Commands**: Optional frontmatter, description max 256 chars, valid model values (sonnet/opus/haiku).

**Allowed Tools**: Can be `["*"]` for all tools or list from: Bash, Read, Write, Edit, Glob, Grep, Task, WebFetch, WebSearch, TodoWrite, AskUserQuestion, Skill, SlashCommand, NotebookEdit, BashOutput, KillShell.

**Hooks**: Must have valid name (lowercase, hyphens, max 64 chars), description (max 256 chars), valid event (PreToolUse, PostToolUse, PermissionRequest, UserPromptSubmit, Notification, Stop, SubagentStop, PreCompact, SessionStart, SessionEnd), and at least one script file (*.py or *.sh).

### Discovery and Installation

- `find_skill_directories()`, `find_command_files()`, and `find_hook_directories()` recursively scan repository
- Installation copies from repository to personal/project directories
- Search uses fuzzy matching on names, descriptions, and file contents
- Hook installation also updates `settings.json` with the hook configuration

## Key Conventions

- **Naming**: Skills and commands use lowercase-with-hyphens naming
- **Frontmatter**: YAML between `---` delimiters at file start
- **Tools restriction**: `allowed-tools` field limits which Claude tools the skill/command can use
- **Repository path**: Must be configured via `skillpack config set repository /path/to/repo`

## Remote Install (`skillpack add`)

`uvx skillpack add owner/repo --skill name` clones a repo into a temp dir, discovers SKILL.md
skills (npx-skills search order, name from frontmatter), copies each to `.agents/skills/<name>`
(or `~/.agents/skills` with `-g`) and symlinks agent dirs like `.claude/skills/<name>` to it
(`--copy` to copy). Installs are recorded in `skills-lock.json` / `~/.agents/.skill-lock.json`
(npx format; global hash = git tree SHA, project hash = SHA-256 of files). `check` reports
upstream changes, `upgrade` applies them, `remove` uninstalls, `find` searches skills.sh / GitHub.
`skillpack/extras.py` also installs commands (`--command`), subagents (`--subagent`), hooks (`--hook`)
and MCP servers (`--mcp`, from `.mcp.json` / `mcp/*.json`) for Claude Code, tracked in
`.claude/skillpack-lock.json`. Hooks and MCP servers are previewed and need confirmation or `-y`.
MCP servers: `skillpack/mcp_targets.py` has the per-agent table (file, key, shape, `${VAR}` translation); `extras.install_mcp`/`uninstall_mcp` write to the `Placement`s recorded as `targets` in `.claude/skillpack-lock.json`.
`skillpack installed` (`commands/installed.py`) is the offline inventory from lock files; `remove --all` removes everything in a scope; `add`/`remove` refuse to touch items not in a lock file without `--force` (see `skillpack/safeio.py` for safe JSON edits / output sanitizing).
`skillpack validate [PATH]` (`skillpack/spec.py`) checks skills against the Agent Skills spec (agentskills.io)
plus installability (hidden/duplicate skills, broken links, excluded files, LFS); author guide is
`docs/publishing-skills.md`. Aliases:
`skillpack config set alias.NAME owner/repo`. See `docs/publishing-skills.md`.

## Install --all Feature

The `install --all` command installs all skills and commands from the repository in a single operation:
- Discovers all valid skills and commands from repository
- Validates each before installation
- Provides progress feedback during batch installation
- Supports `--dry-run` to preview what would be installed
- Respects `--target` (personal/project) and `--force` options

## Hooks CLI Commands

The `skillpack hooks` command group manages Claude Code hooks:

```bash
# List available hooks from repository
skillpack hooks list --target repo

# List installed hooks
skillpack hooks list --target personal

# Install a hook
skillpack hooks install lab-notebook

# Uninstall a hook
skillpack hooks uninstall lab-notebook

# Get hook info
skillpack hooks info lab-notebook

# Search for hooks
skillpack hooks search "format"

# Create a new hook from template
skillpack hooks create my-hook --event PostToolUse
```

### Available Hooks

- **lab-notebook**: Generate lab notebook entries from Claude Code sessions (SessionEnd)
- **prettier-on-save**: Auto-format JS/TS/CSS/JSON files with Prettier (PostToolUse)
- **black-on-save**: Auto-format Python files with Black (PostToolUse)
- **protect-secrets**: Block writes to sensitive files like .env (PreToolUse, blocking)
- **bash-logger**: Log all bash commands for audit (PreToolUse)
- **notify-done**: Desktop notification when Claude needs input (Stop)

## Agents CLI Commands

The `skillpack agents` command group manages Claude Code subagents:

```bash
# List available agents from repository
skillpack agents list --target repo

# List installed agents
skillpack agents list --target personal

# Install an agent
skillpack agents install code-reviewer

# Uninstall an agent
skillpack agents uninstall code-reviewer

# Get agent info
skillpack agents info code-reviewer

# Search for agents
skillpack agents search "test"

# Create a new agent from template
skillpack agents create my-agent --model sonnet

# Create an agent using AI (Claude CLI)
skillpack agents create my-agent --prompt "An agent that analyzes code complexity"
```

### Available Agents

- **code-reviewer**: Analyzes code for quality, security issues, and best practices
- **debugger**: Traces issues through code, analyzes errors, suggests fixes
- **literature-searcher**: Searches academic papers and technical resources
- **test-writer**: Generates comprehensive test cases and suites
- **doc-writer**: Creates documentation, READMEs, and API docs

### Agents Validation

Agents must have valid name (lowercase, hyphens, max 64 chars), description (max 1024 chars), valid model (sonnet/opus/haiku), and valid tools list.

## Available Commands

Slash commands for common tasks:

### Git & Workflow
- `/commit` - Generate commit message from staged changes
- `/pr` - Generate PR description from branch commits
- `/changelog` - Generate changelog entry

### Code Quality
- `/review <file>` - Quick code review
- `/explain <file>` - Explain code in plain English
- `/refactor <file>` - Suggest refactoring improvements
- `/fix <error>` - Diagnose and fix errors

### Documentation
- `/doc <file>` - Generate docstrings/comments
- `/readme [section]` - Generate README content
- `/api <module>` - Generate API documentation

### Research
- `/cite <url|doi>` - Format citation
- `/lab-entry <title>` - Create lab notebook entry
- `/summarize <file|url>` - Summarize content

### Analysis
- `/deps` - Analyze project dependencies
- `/todo [path]` - Extract TODOs from codebase
- `/find-usage <name>` - Find where identifier is used

## AI-Assisted Creation

All three types support AI-assisted creation using the Claude CLI:

```bash
# Create a skill using AI
skillpack create --type skill --name my-skill --prompt "A skill for analyzing Python code style"

# Create a hook using AI
skillpack hooks create my-hook --event PostToolUse --prompt "Format Python files with black"

# Create an agent using AI
skillpack agents create my-agent --prompt "An agent that reviews security vulnerabilities"
```

## CASCADE: Skill Evolution Commands

Inspired by CASCADE (arxiv:2512.23880), skillpack includes commands for autonomous skill
improvement. See `docs/cascade.md` for full documentation.

```bash
# Harvest new skills from session transcripts
skillpack harvest
skillpack harvest -t path/to/session.jsonl --generate

# Optimize skill descriptions (single or batch)
skillpack optimize python-jax
skillpack optimize --all --dry-run

# A/B test description variants
skillpack ab-test python-jax -n 5

# Track skill usage statistics
skillpack stats --scan
skillpack stats --unused

# Detect and merge overlapping skills
skillpack merge
skillpack merge --execute skill-a skill-b --merged-name combined-skill
```

## Common Patterns

**Adding a new CLI command**: Create file in `skillpack/commands/`, implement as Click command, import and register in `skillpack/main.py`.

**Creating a skill**: Use `skillpack create --type skill` or manually create directory with SKILL.md containing proper frontmatter.

**Creating a hook**: Use `skillpack hooks create my-hook` or manually create directory with HOOK.md and hook.py.

**Creating an agent**: Use `skillpack agents create my-agent` or manually create .md file with proper frontmatter.

**Validation errors**: SkillValidator, CommandValidator, HookValidator, and AgentValidator all return `(is_valid, list_of_errors)` tuples.

## Git Policy

Never use `--no-verify` with git commands per user's global instructions.
