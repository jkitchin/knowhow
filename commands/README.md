# Slash Commands

This directory contains slash commands for Claude Code and other LLM platforms.

## What are Slash Commands?

Slash commands are user-invoked shortcuts that provide Claude with specific instructions. Unlike skills (which Claude invokes automatically), commands are explicitly called by users.

## Usage

```bash
# List available commands
claude-skills list --type command

# Install a command
claude-skills install summarize --type command

# View command details
claude-skills info explain-code --type command
```

## Command Format

Commands are markdown files with optional YAML frontmatter:

```markdown
---
description: Brief description for /help
model: opus  # Optional: sonnet, opus, or haiku
argument-hint: <your-arg>  # Optional: autocomplete help
allowed-tools: ["Read", "Write"]  # Optional: restrict tools
---

# Command Content

Instructions for Claude...

Use $ARGUMENTS or $1, $2, etc. for parameters.
```

## Directory Structure

```
commands/
├── examples/          # Example commands
│   ├── summarize.md
│   ├── explain-code.md
│   └── review-pr.md
└── [category]/       # Organize by category
    └── command.md
```

## Available Commands

### Examples Category

- **summarize** - Summarize files or content
- **explain-code** - Detailed code explanations
- **review-pr** - Code review with best practices

## Creating Commands

1. Create a `.md` file in the appropriate category
2. Add frontmatter (optional but recommended)
3. Write clear instructions
4. Use parameters: `$ARGUMENTS`, `$1`, `$2`, etc.
5. Validate: `claude-skills validate commands/your-command.md`

### Command Requirements

- **File Extension**: Must be `.md`
- **Description**: Max 256 characters (if provided)
- **Model**: Must be `sonnet`, `opus`, or `haiku` (if specified)
- **Name**: Derived from filename (use lowercase with hyphens)

### Best Practices

1. **Be Specific**: Commands should have clear, focused purposes
2. **Use Parameters**: Make commands flexible with `$ARGUMENTS`
3. **Document Well**: Use `description` and `argument-hint`
4. **Test First**: Validate before committing
5. **Keep Simple**: Complex workflows might be better as skills

### Example Command

```markdown
---
description: Format code according to style guide
argument-hint: <file-pattern>
model: opus
allowed-tools: ["Read", "Edit", "Bash"]
---

# Format Code

Please format the following files according to best practices: $ARGUMENTS

For Python files:
- Use Black for formatting
- Run Ruff for linting
- Check with mypy

For other files, apply appropriate language-specific formatters.
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing commands.

## See Also

- [Skills Directory](../skills/) - Auto-invoked agent skills
- [Templates](../templates/) - Templates for creating new items
- [CLI Documentation](../README.md) - Full CLI documentation
