# Skillin

<img src="skillin.svg" alt="skillin logo: SKILLIN' above a terminal running uvx skillin add" width="300">

[![Tests](https://github.com/jkitchin/skillz/actions/workflows/test.yml/badge.svg)](https://github.com/jkitchin/skillz/actions/workflows/test.yml)
[![Lint](https://github.com/jkitchin/skillz/actions/workflows/lint.yml/badge.svg)](https://github.com/jkitchin/skillz/actions/workflows/lint.yml)
[![codecov](https://codecov.io/gh/jkitchin/skillz/graph/badge.svg)](https://codecov.io/gh/jkitchin/skillz)


Install AI agent skills, slash commands, subagents, hooks and MCP servers from any git
repository with one command. There's nothing to install first and no repository to clone.
Works with Claude Code, Codex, OpenCode, Gemini CLI, Cursor, GitHub Copilot and more.

> **Note:** Currently only tested on Claude Code and OpenCode. Please report issues for other agents.

This repository is both the `skillin` tool and a collection of 44 skills, plus commands, hooks
and agents, for scientific computing, materials science, lab automation and research workflows.

## Install skills from any repo (no setup)

```bash
# List what a repository offers, then install a skill into this project
uvx skillin add jkitchin/skillz --list
uvx skillin add jkitchin/skillz --skill fairchem

# Install for your user (all projects), several skills, no prompts
uvx skillin add jkitchin/skillz -s pycse -s python-plotting -g -y

# Any compatible repo, URL or local path works
uvx skillin add someone/their-skills@their-skill
uvx skillin add https://github.com/o/r/tree/main/skills/foo

# Slash commands, subagents, hooks and MCP servers (installed for Claude Code)
uvx skillin add jkitchin/skillz --command commit --subagent code-reviewer
uvx skillin add jkitchin/skillz --hook black-on-save   # shows the script for review first
uvx skillin add someone/repo --mcp their-server         # from the repo's .mcp.json

uvx skillin find plotting   # search skills.sh / GitHub
uvx skillin check           # any upstream changes?
uvx skillin upgrade         # apply them
uvx skillin remove fairchem
```

Until `skillin` is published on PyPI, use
`uvx --from git+https://github.com/jkitchin/skillz skillin add ...`.

- **Compatible with [`npx skills`](https://github.com/vercel-labs/skills):** skills use the same
  repository layout, install locations and lock files, so the two tools can be mixed. A skill
  is copied once to `.agents/skills/<name>`, which Codex, OpenCode, Gemini CLI, Cursor and
  Copilot read directly, and symlinked into `.claude/skills/<name>`. With `-g` the same
  happens under `~/`.
- **Tracked:** installs are recorded in `skills-lock.json` (commit it) and
  `.claude/skillin-lock.json`. `check` and `upgrade` use these to find upstream changes.
- **Publish your own:** any git repo with `SKILL.md` files works. Follow the
  [guide to creating compatible skill repositories](docs/publishing-skills.md) and
  check your repo with `uvx skillin validate .`.
- **Shortcuts:** `skillin config set alias.kitchin jkitchin/skillz` lets you write
  `skillin add kitchin -s pycse`.

The `skillz` command still works as an alias of `skillin`.

## Features

- **Remote install**: `add` skills, commands, subagents, hooks and MCP servers from GitHub, GitLab, any git URL or a local path
- **Updates**: `check` and `upgrade` against lock files; `remove` by name or by source
- **Search**: `find` searches skills.sh and GitHub; `search` searches a local skills repository
- **Create**: interactive wizard or AI-assisted creation of skills, commands, hooks and agents
- **Validate**: `skillin validate` checks a repo against the Agent Skills spec and how installers will see it (CI-friendly exit codes)
- **Multi-agent**: Claude Code, Codex, OpenCode, Gemini CLI, Cursor, GitHub Copilot, Goose, Windsurf
- **Hooks**: lifecycle hooks for Claude Code (formatting, logging, security, notifications)
- **Skill evolution**: harvest, optimize, A/B test and merge skills (see [docs/cascade.md](docs/cascade.md))

## Installation

You don't need to install anything to use `uvx skillin ...`. To keep `skillin` on your PATH:

```bash
uv tool install skillin          # or: pipx install skillin
# before the PyPI release:
uv tool install git+https://github.com/jkitchin/skillz
```

For development, from a clone of this repository:

```bash
uv pip install -e ".[dev]"
```

## Working with a local skills repository

The commands below work from a local clone of a skills repository, such as this one. Use
them when you are developing skills. For plain installs, `skillin add` (above) is simpler.

### Configure Repository Path

```bash
skillin config set repository /path/to/your/clone
```

### List Available Skills

```bash
# List all skills and commands
skillin list

# List only skills
skillin list --type skill

# List only from repository
skillin list --source repository
```

### Install a Skill

```bash
# Install to Claude Code (default)
skillin install skill-name

# Install to OpenCode
skillin install skill-name --platform opencode

# Install to project directory (.claude/skills/)
skillin install skill-name --target project

# Preview before installing
skillin install skill-name --dry-run
```

### Search for Skills

```bash
skillin search python
skillin search "lab notebook"
```

### Create a New Skill

```bash
# Interactive mode
skillin create --type skill

# With name specified
skillin create --type skill --name my-awesome-skill

# AI-assisted creation using Claude CLI
skillin create --type skill --name my-skill --prompt "A skill for analyzing Python code style"
```

### Uninstall a Skill

```bash
skillin uninstall skill-name
```

### Manage Hooks

```bash
# List available hooks
skillin hooks list --target repo

# Install a hook
skillin hooks install lab-notebook

# Create a hook (with AI)
skillin hooks create my-hook --event PostToolUse --prompt "Format Python with black"
```

### Manage Agents

```bash
# List available agents
skillin agents list --target repo

# Install an agent
skillin agents install code-reviewer

# Create an agent (with AI)
skillin agents create my-agent --prompt "An agent that reviews security vulnerabilities"
```

## Configuration

Configuration is stored in `~/.config/skillz/config.yaml` (the path keeps the original name
so existing setups keep working).

Default configuration:

```yaml
default_platform: claude

personal_skills_dir: ~/.claude/skills
personal_commands_dir: ~/.claude/commands
project_skills_dir: .claude/skills
project_commands_dir: .claude/commands
default_target: personal
aliases: {}            # e.g. {kitchin: jkitchin/skillz} for `skillin add kitchin ...`

platforms:
  claude:
    skills_dir: ~/.claude/skills
    commands_dir: ~/.claude/commands
  opencode:
    skills_dir: ~/.config/opencode/skills
    commands_dir: ~/.config/opencode/command
  codex:
    skills_dir: ~/.codex/skills
    commands_dir: ~/.codex/commands
  gemini:
    skills_dir: ~/.config/gemini/skills
    commands_dir: ~/.config/gemini/commands
```

## Skills Format

Skills are directories containing a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: my-skill
description: A clear description of what this skill does and when to use it
allowed-tools: ["*"]  # Optional: restrict available tools
---

# Skill Content

Detailed instructions for Claude on how to use this skill...
```

### Requirements

- `name`: lowercase, hyphens only, max 64 characters
- `description`: clear explanation, max 1024 characters
- Directory must contain `SKILL.md`

## Commands Format

Commands are markdown files with optional YAML frontmatter:

```markdown
---
description: Brief description for /help
model: sonnet  # Optional: sonnet, opus, or haiku
allowed-tools: ["*"]  # Optional
argument-hint: <your-arg>  # Optional: autocomplete help
---

# Command Content

Command prompt content here...

Use $ARGUMENTS or $1, $2, etc. for parameters.
```

## Hooks Format

Hooks are directories containing a `HOOK.md` file and a script (`hook.py` or `hook.sh`):

```markdown
---
name: my-hook
description: Brief description of what this hook does
event: PostToolUse  # PreToolUse, PostToolUse, Stop, SessionStart, SessionEnd, etc.
matcher: Write      # Optional: filter by tool name
timeout: 30         # Optional: timeout in seconds
---

# Hook Documentation

Details about when and how this hook runs...
```

### Available Hook Events

- `PreToolUse` / `PostToolUse`: Before/after tool execution
- `UserPromptSubmit`: When user submits a prompt
- `Stop`: When Claude needs user input
- `SessionStart` / `SessionEnd`: Session lifecycle
- `Notification`: For notifications

## Agents Format

Agents are markdown files with YAML frontmatter:

```markdown
---
name: my-agent
description: Clear description of what this agent does
tools: Read, Write, Edit, Grep, Glob
model: sonnet  # sonnet, opus, or haiku
---

# Agent Instructions

Detailed instructions for this specialized agent...
```

## Project Structure

```
skillz/                     # repository (the tool is published as `skillin`)
├── skillin/               # Python CLI package
│   ├── commands/          # CLI command implementations (add.py = add/remove/check/upgrade/find)
│   ├── sources.py         # Parse owner/repo, URLs, local paths
│   ├── fetch.py           # Shallow git clone / GitHub API
│   ├── discovery.py       # Find SKILL.md skills (npx-skills compatible)
│   ├── extras.py          # Commands, subagents, hooks, MCP servers
│   ├── installer.py       # Canonical copy + agent symlinks
│   ├── lock.py            # Lock files
│   ├── agents_registry.py # Supported agents and their paths
│   ├── config.py          # Configuration management
│   ├── validator.py       # Skill/command/hook/agent validation
│   └── utils.py           # Helper functions
├── skills/                # Skill repository
│   ├── academic/
│   ├── programming/
│   └── research/
├── commands/              # Command repository
├── hooks/                 # Hooks repository
│   ├── lab-notebook/
│   ├── prettier-on-save/
│   └── ...
├── agents/                # Agents repository
│   ├── code-reviewer.md
│   ├── debugger.md
│   └── ...
├── templates/             # Templates for new skills/hooks/agents
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to automatically run linting and formatting checks before each commit. The hooks will:

- Run `ruff check --fix` to fix linting issues
- Run `ruff format` to format code

If any changes are made by the hooks, the commit will fail. Simply stage the changes and commit again.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=skillin --cov-report=html
```

### Linting and Formatting

We use [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting:

```bash
# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Check formatting
ruff format --check .

# Format code
ruff format .
```

## Available Skills

See the `skills/` directory, or run `uvx skillin add jkitchin/skillz --list`:

- **Programming & materials science**: ASE, pymatgen, VASP, FAIRChem, pycalphad, IDAES, JAX, materials properties, Python best practices, plotting, optimization (single and multiobjective), regression & statistics, Emacs Lisp, Claude-Light
- **Laboratory automation**: Opentrons (API, gripper, heater-shaker, thermocycler, temperature module, magnetic block, absorbance reader)
- **Research**: literature review, scientific data extraction, scientific reviewer, materials databases, scientific workflows, electronic lab notebooks, citation verification, design of experiments, pycse
- **Communication & creative**: scientific writing, presentations, image generation, video storytelling, ElevenLabs audio, brainstorming
- **Development & productivity**: version control, code review, TDD, Ralph Wiggum autonomous loop, troubleshooting, planning
- **Academic**: PhD qualifier review

## Available Hooks

See the `hooks/` directory for available hooks:

- **lab-notebook**: Generate lab notebook entries from Claude Code sessions
- **prettier-on-save**: Auto-format JS/TS/CSS/JSON files with Prettier
- **black-on-save**: Auto-format Python files with Black
- **protect-secrets**: Block writes to sensitive files like .env
- **bash-logger**: Log all bash commands for audit
- **notify-done**: Desktop notification when Claude needs input

## Available Agents

See the `agents/` directory for available agents:

- **code-reviewer**: Analyzes code for quality, security issues, and best practices
- **debugger**: Traces issues through code, analyzes errors, suggests fixes
- **literature-searcher**: Searches academic papers and technical resources
- **test-writer**: Generates comprehensive test cases and suites
- **doc-writer**: Creates documentation, READMEs, and API docs

## Available Commands

See the `commands/` directory for slash commands:

### Git & Workflow
- **/commit**: Generate commit message from staged changes
- **/pr**: Generate PR description from branch commits
- **/changelog**: Generate changelog entry for recent changes

### Code Quality
- **/review**: Quick code review of file or selection
- **/explain**: Explain what code does in plain English
- **/refactor**: Suggest refactoring improvements
- **/fix**: Diagnose and fix a specific error

### Documentation
- **/doc**: Generate docstrings/comments for code
- **/readme**: Generate or update README content
- **/api**: Generate API documentation

### Research
- **/cite**: Format citation from URL or DOI
- **/lab-entry**: Create formatted lab notebook entry
- **/summarize**: Summarize file, PR, or conversation

### Analysis
- **/deps**: Analyze project dependencies
- **/todo**: Extract TODOs from codebase
- **/find-usage**: Find where function/class is used

## Contributing

Contributions are welcome! Please:

1. Follow the skill/command format requirements
2. Add tests for new functionality
3. Update documentation
4. Run linters before submitting

## License

MIT License - see LICENSE file for details

## Support

- Report issues: https://github.com/jkitchin/skillz/issues
- Documentation: https://github.com/jkitchin/skillz#readme

## Related Projects

### Supported Platforms

Skillin manages skills and commands for these AI coding assistants:

- **[OpenCode](https://github.com/sst/opencode)** - The AI coding agent built for the terminal. Open-source, provider-agnostic, with 30k+ GitHub stars.
- **[Claude Code](https://github.com/anthropics/claude-code)** - Anthropic's agentic coding tool that lives in your terminal. Understands your codebase and helps you code faster.
- **[Codex CLI](https://github.com/openai/codex)** - OpenAI's lightweight coding agent that runs in your terminal. See [OpenAI adopts "skills"](https://simonwillison.net/2025/Dec/12/openai-skills/) for details on their skills implementation.
- **Gemini** - Google's AI assistant.
- Cursor, GitHub Copilot, Goose and Windsurf are supported targets for `skillin add` skills.

### Related Skills Projects

- **[npx skills](https://github.com/vercel-labs/skills)** - Vercel's Node CLI and the [skills.sh](https://skills.sh) directory. `skillin add` follows its layout, install paths and lock files.
- **[openskills](https://github.com/numman-ali/openskills)** - Another universal skills loader (I have not tried this yet).
- **[opencode-skills](https://www.npmjs.com/package/opencode-skills)** - With OpenCode you may get better performance with this plugin (this is what I use). See also the [OpenCode feature request](https://github.com/sst/opencode/issues/3235).

- **[Superpowers](https://github.com/obra/superpowers)** - A complete software development workflow framework for Claude Code with composable skills for design, TDD, code review, and integration. This project was an early motivation to develop this project.

## Credits

Created by John Kitchin for managing AI assistant skills across different LLM platforms.
