# Slash Command Template

This template helps you create custom slash commands for Claude Code.

## Quick Reference

**File Location:**
- Personal: `~/.claude/commands/command-name.md`
- Project: `.claude/commands/command-name.md`

**Naming:**
- Filename becomes the command: `deploy.md` → `/deploy`
- Use subdirectories for namespaces: `frontend/build.md` → `/build` (with namespace indicator)

**Key Characteristics:**
- User-invoked: Explicit command execution with `/command-name`
- Single markdown file with optional YAML frontmatter
- Best for frequently-used, single-file prompts

---

## Basic Template (No Arguments)

Copy this for simple commands without parameters:

```markdown
---
description: Brief explanation shown in /help
---

[Your prompt/instructions here]

Tell the user exactly what you'll do, then proceed with the task.
```

---

## Template with Arguments

Copy this for commands that accept parameters:

```markdown
---
description: Brief explanation shown in /help
argument-hint: <arg1> <arg2>
---

You are executing a command with these arguments:
- First argument: $1
- Second argument: $2
- All arguments: $ARGUMENTS

[Your prompt/instructions using the arguments]
```

---

## Template with File References

Copy this for commands that work with specific files:

```markdown
---
description: Brief explanation shown in /help
argument-hint: <file>
---

You are working with the file: $1

Read the file contents using @$1 reference, then [instructions for what to do with it].
```

---

## Template with Bash Execution

Copy this for commands that need to run shell commands:

```markdown
---
description: Brief explanation shown in /help
allowed-tools: Bash, Read, Write
---

Before executing the main task, run these commands:
!ls -la
!git status

Then proceed with: [instructions for the main task]
```

---

## Template with Tool Restrictions

Copy this for commands with restricted tool access:

```markdown
---
description: Brief explanation shown in /help
allowed-tools: Read, Grep
---

This is a read-only command. You can only use Read and Grep tools.

[Your prompt/instructions here]
```

---

## Template with Specific Model

Copy this for commands that need a particular model:

```markdown
---
description: Brief explanation shown in /help
model: opus
---

This command will use Claude Opus specifically.

[Your prompt/instructions here]
```

---

## Full Template (All Options)

Complete template with all available metadata:

```markdown
---
description: Brief one-line description for /help menu
argument-hint: <required-arg> [optional-arg]
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
model: opus
disable-model-invocation: false
---

# [Command Name]

## Context
[Explain what this command does and when to use it]

## Arguments
- `$1`: [Description of first argument]
- `$2`: [Description of second argument]
- `$ARGUMENTS`: [All arguments as a single string]

## File References
Use @filename to include file contents:
- @$1 : Include first argument as file path
- @README.md : Include specific file

## Pre-execution Commands
!command1
!command2

## Instructions
[Detailed instructions for Claude to follow]

### Step 1: [Task]
[Specific instructions]

### Step 2: [Task]
[Specific instructions]

### Step 3: [Task]
[Specific instructions]

## Output Format
[Specify how results should be presented]

## Error Handling
[How to handle common errors or edge cases]
```

---

## Metadata Field Reference

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `description` | string | Brief explanation shown in /help | `"Deploy to production server"` |
| `argument-hint` | string | Shows during autocomplete | `"<environment> [branch]"` |
| `allowed-tools` | string | Comma-separated tool list | `"Read, Edit, Write, Bash"` |
| `model` | string | Specific model to use | `"opus"` |
| `disable-model-invocation` | boolean | Prevent SlashCommand tool use | `false` |

All fields are optional. If omitted:
- `description`: First line of prompt is used
- `allowed-tools`: Inherits from conversation (all tools)
- `model`: Uses conversation model
- Other fields: Default behavior

---

## Parameter Handling

### Using $ARGUMENTS (all parameters as one string)

```markdown
---
description: Create a component with a given name
---

Create a React component named: $ARGUMENTS

The component should be a functional component with TypeScript.
```

Usage: `/create-component MyButton` → `$ARGUMENTS` = "MyButton"

### Using Positional Parameters ($1, $2, etc.)

```markdown
---
description: Deploy to environment with branch
argument-hint: <environment> [branch]
---

Deploy to environment: $1
Using branch: ${2:-main}

If branch is not provided, default to 'main'.
```

Usage:
- `/deploy staging feature-x` → `$1`="staging", `$2`="feature-x"
- `/deploy staging` → `$1`="staging", `$2` is empty (use default)

### Default Values

Use bash-style defaults:
- `${1:-default}` - Use "default" if $1 is empty
- `${2:-main}` - Use "main" if $2 is empty

---

## File Reference Syntax

Use `@filename` to include file contents:

```markdown
---
description: Review code in a file
---

Review the code in this file:

@$1

Provide feedback on:
1. Code quality
2. Potential bugs
3. Performance improvements
```

Usage: `/review src/main.py` → Includes contents of src/main.py

---

## Bash Execution

Prefix commands with `!` to run before main prompt:

```markdown
---
description: Run tests and show results
allowed-tools: Bash, Read
---

!pytest tests/ -v
!coverage report

Analyze the test results above and provide a summary.
```

**Important:**
- Must include `Bash` in `allowed-tools`
- Output is included in context
- Commands run before prompt processing

---

## Example Commands

### Example 1: Simple Command (No Arguments)

**File:** `.claude/commands/review-pr.md`

```markdown
---
description: Review the current PR for code quality
---

Review the current pull request:

1. Check git diff for changes
2. Analyze code quality and potential issues
3. Suggest improvements
4. Check for test coverage

Provide a structured review with sections for each aspect.
```

Usage: `/review-pr`

### Example 2: Command with Arguments

**File:** `.claude/commands/create-test.md`

```markdown
---
description: Create a test file for a given module
argument-hint: <module-path>
---

Create a comprehensive test file for: $1

Include:
- Unit tests for all exported functions
- Edge case testing
- Mock external dependencies
- Clear test descriptions

Follow the project's testing conventions.
```

Usage: `/create-test src/utils/parser.py`

### Example 3: Command with File Reference

**File:** `.claude/commands/optimize.md`

```markdown
---
description: Optimize code in a specific file
argument-hint: <file>
---

Optimize the code in this file:

@$1

Focus on:
- Performance improvements
- Memory efficiency
- Readability
- Best practices

Show before and after comparisons.
```

Usage: `/optimize src/main.py`

### Example 4: Command with Multiple Arguments

**File:** `.claude/commands/migrate.md`

```markdown
---
description: Migrate code from old pattern to new pattern
argument-hint: <file> <old-pattern> <new-pattern>
---

Migrate code in file: $1
From pattern: $2
To pattern: $3

Steps:
1. Read the file: @$1
2. Find all instances of: $2
3. Replace with: $3
4. Ensure functionality is preserved
5. Show a diff of changes
```

Usage: `/migrate src/app.js var let`

### Example 5: Command with Bash Pre-execution

**File:** `.claude/commands/test-coverage.md`

```markdown
---
description: Run tests and analyze coverage
allowed-tools: Bash, Read, Grep
---

!pytest --cov=. --cov-report=term-missing
!coverage report

Analyze the test coverage results above:
1. Identify files with low coverage (<80%)
2. Suggest where to add tests
3. Highlight critical uncovered code paths
```

Usage: `/test-coverage`

### Example 6: Command with Tool Restrictions

**File:** `.claude/commands/search-logs.md`

```markdown
---
description: Search logs for error patterns
argument-hint: <pattern>
allowed-tools: Read, Grep
---

Search for pattern: $1

Use Grep to search log files for the pattern.
Then summarize:
- Number of occurrences
- Time distribution
- Common error contexts
- Potential root causes

This is a read-only operation.
```

Usage: `/search-logs "HTTP 500"`

---

## Organizing Commands

### Flat Structure
```
.claude/commands/
├── deploy.md
├── test.md
├── review.md
└── build.md
```

Usage: `/deploy`, `/test`, `/review`, `/build`

### Namespaced Structure
```
.claude/commands/
├── frontend/
│   ├── build.md
│   ├── deploy.md
│   └── test.md
└── backend/
    ├── migrate.md
    └── seed.md
```

Usage: `/build` (shows as "project:frontend"), `/migrate` (shows as "project:backend")

**Note:** Namespace doesn't change command name, only adds context indicator.

---

## Validation Checklist

Before deploying your command, verify:

- [ ] File is saved as `.md` in commands directory
- [ ] YAML frontmatter is valid (if used)
- [ ] `description` is clear and concise
- [ ] `argument-hint` matches actual parameter usage
- [ ] `allowed-tools` includes all tools used in prompt
- [ ] If using `!` commands, `Bash` is in `allowed-tools`
- [ ] Parameter references ($1, $2, etc.) are correct
- [ ] File references (@filename) use correct paths
- [ ] Instructions are clear and actionable
- [ ] Default values for optional parameters are specified

---

## Testing Your Command

1. **Install the command:**
   ```bash
   # For personal use
   mkdir -p ~/.claude/commands
   cp your-command.md ~/.claude/commands/

   # For project use
   mkdir -p .claude/commands
   cp your-command.md .claude/commands/
   ```

2. **Test the command:**
   - Start Claude Code
   - Type `/` to see available commands
   - Your command should appear in the list
   - Execute it: `/your-command arg1 arg2`

3. **Debug if needed:**
   - Check YAML frontmatter syntax
   - Verify file location and name
   - Test with different argument combinations
   - Check tool restrictions aren't blocking operations

4. **Iterate:**
   - Refine based on actual usage
   - Add clarifying instructions
   - Improve error handling
   - Update documentation

---

## Skills vs Commands: When to Use Which

| Use This | If You Need |
|----------|-------------|
| **Skill** | Autonomous invocation (Claude decides) |
| **Skill** | Complex multi-file workflows |
| **Skill** | Context-dependent triggering |
| **Command** | Explicit user-triggered action |
| **Command** | Frequently-used single prompt |
| **Command** | Quick automation shortcut |

**Note on undertriggering:** Skills suffer from *undertriggering* — Claude may not invoke
them when it should. Commands don't have this problem because the user explicitly types
`/command-name`. If your automation is being ignored by Claude, consider packaging it as
a slash command instead of a skill. Conversely, if you need Claude to apply guidance
automatically without the user thinking about it, use a skill with a "pushy" description
(see `SKILL_TEMPLATE.md`).

---

## Common Patterns

### Pattern 1: Code Generation
```markdown
---
description: Generate boilerplate code
argument-hint: <type> <name>
---

Generate $1 named $2 with standard boilerplate.
```

### Pattern 2: File Analysis
```markdown
---
description: Analyze file complexity
argument-hint: <file>
---

Analyze: @$1
Report: cyclomatic complexity, LOC, dependencies.
```

### Pattern 3: Batch Operations
```markdown
---
description: Process multiple files
argument-hint: <pattern>
allowed-tools: Glob, Read, Edit
---

Find files matching: $1
Process each file: [instructions]
```

### Pattern 4: Git Workflows
```markdown
---
description: Create feature branch
argument-hint: <branch-name>
allowed-tools: Bash
---

!git checkout -b feature/$1
!git push -u origin feature/$1
```

### Pattern 5: Documentation
```markdown
---
description: Generate API docs for file
argument-hint: <file>
---

Read: @$1
Generate comprehensive API documentation.
```

---

## Tips for Great Commands

1. **Clear Purpose**: Description should immediately convey what it does
2. **Good Defaults**: Provide sensible defaults for optional parameters
3. **Error Guidance**: Include instructions for handling common errors
4. **Consistent Style**: Follow project conventions and patterns
5. **Test Thoroughly**: Try with various argument combinations
6. **Document Assumptions**: State any prerequisites or requirements
7. **Show Examples**: Include example usage in comments
8. **Keep It Focused**: Each command should do one thing well

---

## Common Mistakes to Avoid

1. **Missing Bash in allowed-tools**: Using `!` commands without `Bash` tool access
2. **Incorrect parameter references**: Using `$ARGUMENTS` when you need `$1`, `$2`
3. **Invalid YAML**: Syntax errors in frontmatter block
4. **Too complex**: Command trying to do too many things (use a Skill instead)
5. **Vague description**: User can't tell what the command does
6. **No argument hints**: Users don't know what parameters to provide
7. **File path issues**: Not handling relative vs absolute paths correctly
8. **No error handling**: Not specifying what to do when arguments are invalid

---

## Advanced Tips

### Conditional Logic
```markdown
If $1 is "production", require confirmation before deploying.
If $2 is not provided, use "main" as the default branch.
```

### Multiple File References
```markdown
Compare files:
Source: @$1
Target: @$2
```

### Complex Argument Parsing
```markdown
Parse $ARGUMENTS as key=value pairs:
Example: /config set debug=true verbose=false
```

### Chaining Operations
```markdown
1. Run tests with !pytest
2. If tests pass, build with !npm run build
3. If build succeeds, deploy with !./deploy.sh $1
```

---

## Need Help?

- [Slash Commands Documentation](https://docs.claude.com/en/docs/claude-code/slash-commands.md)
- [Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)
- Type `/help` in Claude Code to see all available commands
- Check `.claude/commands/` examples in your project
