# Formatting Hooks

Auto-format code after Claude edits files. These hooks ensure consistent code style without manual intervention.

## Prettier on Save

Automatically format JavaScript, TypeScript, CSS, and other web files with Prettier.

### Overview

| Field | Value |
|-------|-------|
| Name | `prettier-on-save` |
| Event | `PostToolUse` |
| Matcher | `Edit\|Write` |
| Type | `command` |
| Timeout | 30 seconds |

### Purpose

When Claude writes or edits a file that Prettier supports, this hook automatically formats it. This ensures your code always follows consistent formatting rules without requiring manual intervention.

### Supported File Types

| Extension | Language |
|-----------|----------|
| `.js`, `.jsx` | JavaScript |
| `.ts`, `.tsx` | TypeScript |
| `.css`, `.scss`, `.less` | Stylesheets |
| `.json` | JSON |
| `.md`, `.mdx` | Markdown |
| `.html`, `.htm` | HTML |
| `.yaml`, `.yml` | YAML |
| `.graphql`, `.gql` | GraphQL |
| `.vue` | Vue |
| `.svelte` | Svelte |

### Requirements

- Node.js installed
- Prettier installed (global or project-local)

```bash
# Global installation
npm install -g prettier

# Project-local (recommended)
npm install --save-dev prettier
```

### Configuration

The hook respects your project's Prettier configuration:

- `.prettierrc`
- `.prettierrc.json`
- `.prettierrc.yaml`
- `prettier.config.js`
- `package.json` (prettier key)

It also respects `.prettierignore` files.

### Behavior

1. Receives file path from Edit/Write tool input
2. Checks if file extension is supported by Prettier
3. Runs `npx prettier --write <file>` (falls back to global `prettier` if npx fails)
4. Prints success message or error to appropriate stream

### Notes

- **Non-blocking**: Runs after the file is written (PostToolUse)
- **Silent on missing Prettier**: If Prettier isn't installed, fails silently
- **Timeout**: 25-second timeout per file to prevent hangs
- **Project-aware**: Uses local Prettier config when available

### Installation

```bash
knowhow hooks install prettier-on-save
```

---

## Black on Save

Automatically format Python files with Black (the uncompromising code formatter).

### Overview

| Field | Value |
|-------|-------|
| Name | `black-on-save` |
| Event | `PostToolUse` |
| Matcher | `Edit\|Write` |
| Type | `command` |
| Timeout | 30 seconds |

### Purpose

When Claude writes or edits a Python file, this hook automatically formats it with Black. This ensures your Python code always follows PEP 8 style guidelines with Black's opinionated formatting.

### Requirements

- Python 3.8+
- Black installed

```bash
pip install black

# Optional: isort for import sorting
pip install isort
```

### Configuration

The hook respects your project's Black configuration:

- `pyproject.toml` (under `[tool.black]`)
- `setup.cfg`
- `.black.toml`

Example `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''
```

### Behavior

1. Receives file path from Edit/Write tool input
2. Checks if file is a Python file (`.py` extension)
3. Runs `isort` first (if available) to sort imports
4. Runs `black` on the file
5. Prints success message or error to appropriate stream

### Notes

- **Non-blocking**: Runs after the file is written (PostToolUse)
- **Silent on missing Black**: If Black isn't installed, fails silently
- **isort integration**: Automatically runs isort before Black if installed
- **Timeout**: 25-second timeout to prevent hangs on large files

### Installation

```bash
knowhow hooks install black-on-save
```

---

## Using Both Hooks Together

You can install both formatting hooks for full-stack projects:

```bash
knowhow hooks install prettier-on-save
knowhow hooks install black-on-save
```

Each hook only triggers for its respective file types, so there's no conflict.

## Troubleshooting

### Files Not Being Formatted

1. **Check installation**: Verify the formatter is installed
   ```bash
   prettier --version
   black --version
   ```

2. **Check file extension**: Ensure the file type is supported

3. **Check ignores**: Look for `.prettierignore` or Black excludes in config

### Formatting Errors

1. **Syntax errors**: The formatters may fail on invalid syntax
2. **Config issues**: Invalid config files can cause failures
3. **Check stderr**: Hook prints error messages to stderr

### Slow Formatting

1. **Large files**: Consider increasing timeout
2. **npx overhead**: Install Prettier globally for faster execution
3. **Network**: npx may try to download packages if not cached
