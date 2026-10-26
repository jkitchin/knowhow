# Contributing to Claude Skills

Thank you for your interest in contributing to Claude Skills! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- `uv` (recommended) or `pip`

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/jkitchin/skillz.git
cd skillz
```

2. Install in development mode with dev dependencies:
```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

3. Configure the repository path:
```bash
skillin config set repository "$(pwd)"
```

## Development Workflow

### Running Tests

Run the full test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=skillin --cov-report=html
```

Run specific tests:
```bash
pytest tests/test_validator.py
pytest tests/test_config.py::TestConfig::test_default_config
```

### Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Run tests
pytest

# Lint and check formatting (or just `pre-commit run --all-files`)
ruff check .
ruff format --check .
```

Auto-format your code:
```bash
ruff format .
```

## Contributing Guidelines

### Creating a New Skill

1. Create a directory in the appropriate category under `skills/`:
   ```
   skills/[category]/[skill-name]/
   ```

2. Add a `SKILL.md` file with proper frontmatter:
   ```markdown
   ---
   name: skill-name
   description: Clear description of what the skill does and when to use it
   allowed-tools: "*"  # or ["Tool1", "Tool2"]
   ---

   # Skill Name

   Detailed instructions for Claude...
   ```

3. Check that it is discovered and installs (warnings point at frontmatter problems):
   ```bash
   skillin add . --list
   skillin add . --skill skill-name --dry-run
   ```
   CI (`.github/workflows/validate-skills.yml`) also runs the strict `SkillValidator`
   (lowercase hyphenated `name`, known `allowed-tools`) on every skill.

### Creating a New Command

1. Create a markdown file in the appropriate category under `commands/`:
   ```
   commands/[category]/command-name.md
   ```

2. Add optional frontmatter:
   ```markdown
   ---
   description: Brief description for /help
   model: sonnet  # Optional: sonnet, opus, or haiku
   argument-hint: <your-arg>
   ---

   # Command instructions

   Use $ARGUMENTS or $1, $2 for parameters...
   ```

### Skill/Command Requirements

**Skills:**
- Name: lowercase, hyphens/numbers only, max 64 chars
- Description: max 1024 chars
- Must have `SKILL.md` in skill directory
- Should include README.md with usage examples
- Consider adding QUICK_REFERENCE.md for common patterns
- Add example code in `examples/` subdirectory

**Commands:**
- Must be `.md` files
- Description (if provided): max 256 chars
- Use `$ARGUMENTS` or `$1, $2, ...` for parameters
- Model must be: sonnet, opus, or haiku

### Pull Request Process

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes:
   - Add tests for new functionality
   - Update documentation
   - Follow existing code style

4. Commit with clear messages:
   ```bash
   git commit -m "Add: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request with:
   - Clear description of changes
   - Reference any related issues
   - Screenshots/examples if applicable

### Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: new feature or file`
- `Fix: bug fix`
- `Update: modify existing feature`
- `Docs: documentation changes`
- `Test: add or modify tests`
- `Refactor: code restructuring`

## Code Style

### Python Code

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small

### Documentation

- Write clear, concise descriptions
- Include examples where helpful
- Update README.md for new features
- Document any breaking changes

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Use fixtures for common setup
- Aim for >80% coverage for new code

Example test structure:
```python
def test_feature_name(fixture):
    """Test description."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

## Skills and Commands Best Practices

### Skill Guidelines

1. **One capability per skill**: Keep skills focused
2. **Clear descriptions**: Explain what it does AND when to use it
3. **Include examples**: Show real-world usage
4. **Document tools**: Specify required tools if restricted
5. **Test thoroughly**: Ensure instructions are clear

### Command Guidelines

1. **Be specific**: Commands should have clear, single purposes
2. **Use parameters**: Leverage `$ARGUMENTS` for flexibility
3. **Document well**: Use description and argument-hint
4. **Keep it simple**: Complex workflows might be better as skills

## Getting Help

- Check existing issues: https://github.com/jkitchin/skillz/issues
- Ask questions in discussions
- Review documentation: README.md and docs/

## Recognition

Contributors will be recognized in:
- Git commit history
- Release notes
- Project documentation

Thank you for contributing to Claude Skills!
