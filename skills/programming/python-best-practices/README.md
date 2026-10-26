# Python Best Practices Skill

A comprehensive Claude Code skill for writing professional, maintainable Python code following industry best practices.

## Overview

This skill provides expert guidance on:

- **PEP 8 Compliance**: Official Python style guide adherence
- **Code Quality**: Readability, clarity, and self-documenting code
- **Architecture**: Modularity, reusability, and the DRY principle
- **Testing**: Unit tests, TDD methodology, and test automation
- **Error Handling**: Proper exception handling and resource management
- **Virtual Environments**: Modern dependency management with uv
- **Tooling**: Ruff, Black, Mypy, and other quality assurance tools
- **Type Hints**: Static type checking for improved code safety

## When to Use This Skill

The skill is automatically invoked when you:

- Write new Python functions, classes, or modules
- Refactor existing Python code
- Set up a new Python project
- Need to implement tests or follow TDD
- Want to add type hints to your code
- Configure linting, formatting, or type checking
- Need guidance on Python best practices

## Features

### 1. Code Style and Formatting

- Complete PEP 8 guidelines with examples
- Naming conventions for all Python constructs
- Import organization and formatting
- Line length and code layout best practices

### 2. Modern Python Tooling

**Ruff**: Fast, Rust-based linter and formatter
```bash
ruff check --fix .    # Lint and auto-fix
ruff format .         # Format code
```

**Black**: Opinionated code formatter
```bash
black .               # Format all files
```

**Mypy**: Static type checker
```bash
mypy src/             # Check types
```

**uv**: Modern, fast package manager
```bash
uv venv               # Create virtual environment
uv pip install pkg    # Install packages
```

### 3. Testing and TDD

- Unit testing with pytest
- Test-driven development methodology
- Fixtures and parametrized tests
- Mocking and patching
- Code coverage reporting

### 4. Type Hints

- Basic and advanced type annotations
- Generic types and protocols
- Callable and Iterator types
- Type checking configuration

### 5. Best Practice Patterns

- Configuration management
- Logging setup
- CLI argument parsing
- Context managers
- Dataclasses
- Custom exceptions

## File Structure

```
python-best-practices/
├── SKILL.md              # Main skill instructions for Claude
├── QUICK_REFERENCE.md    # Quick lookup guide
├── README.md            # This file
└── examples/
    ├── project_structure.py      # Well-structured module
    ├── testing_examples.py       # Test examples
    ├── type_hints_demo.py        # Type hints showcase
    └── error_handling.py         # Exception handling
```

## Installation

### For Personal Use

```bash
# Using skillin CLI
skillin install python-best-practices

# Or manually
mkdir -p ~/.claude/skills/python-best-practices
cp -r . ~/.claude/skills/python-best-practices/
```

### For Project Use

```bash
# Using skillin CLI
skillin install python-best-practices --target project

# Or manually
mkdir -p .claude/skills/python-best-practices
cp -r . .claude/skills/python-best-practices/
```

## Quick Start

### Setting Up a New Python Project

1. **Create project structure:**
```bash
mkdir my_project
cd my_project
```

2. **Initialize virtual environment:**
```bash
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

3. **Create pyproject.toml:**
```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[tool.ruff]
line-length = 99
select = ["E", "F", "I", "N", "W", "B"]

[tool.mypy]
strict = true
```

4. **Install development tools:**
```bash
uv pip install --dev pytest ruff mypy
```

5. **Create source structure:**
```bash
mkdir -p src/my_project tests
touch src/my_project/__init__.py
touch tests/__init__.py
```

### Daily Development Workflow

1. **Write or modify code** with proper type hints and docstrings
2. **Run linter:** `ruff check --fix .`
3. **Format code:** `ruff format .`
4. **Check types:** `mypy src/`
5. **Run tests:** `pytest`
6. **Check coverage:** `pytest --cov=src`

## Examples

### Well-Structured Function

```python
from pathlib import Path

def process_data_file(
    input_path: Path,
    output_path: Path,
    *,
    validate: bool = True,
    encoding: str = "utf-8"
) -> dict[str, int]:
    """Process data file and generate statistics.

    Args:
        input_path: Path to input data file
        output_path: Path for processed output
        validate: Whether to validate data before processing
        encoding: File encoding (default: utf-8)

    Returns:
        Dictionary with processing statistics:
            - 'lines_processed': Number of lines processed
            - 'errors': Number of errors encountered

    Raises:
        FileNotFoundError: If input_path doesn't exist
        ValueError: If validation fails

    Example:
        >>> stats = process_data_file(
        ...     Path("data.txt"),
        ...     Path("output.txt"),
        ...     validate=True
        ... )
        >>> print(stats['lines_processed'])
        100
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Implementation...
    return {'lines_processed': 100, 'errors': 0}
```

### Test-Driven Development

```python
# 1. Write the test first
def test_parse_config():
    """Test configuration parsing."""
    config = parse_config({"timeout": "30", "debug": "true"})
    assert config.timeout == 30
    assert config.debug is True

# 2. Implement minimal code to pass
from dataclasses import dataclass

@dataclass
class Config:
    timeout: int
    debug: bool

def parse_config(data: dict) -> Config:
    return Config(
        timeout=int(data['timeout']),
        debug=data['debug'].lower() == 'true'
    )

# 3. Refactor while keeping tests green
```

## Configuration

### Recommended pyproject.toml

See `QUICK_REFERENCE.md` for a complete pyproject.toml template with all tool configurations.

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
uv pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Integration with Claude Code

When Claude Code uses this skill, it will:

1. **Enforce PEP 8** in all code suggestions
2. **Add type hints** to function signatures automatically
3. **Include docstrings** for all public functions
4. **Suggest appropriate tests** when implementing new features
5. **Recommend proper error handling** patterns
6. **Format code** according to Black/Ruff standards
7. **Structure projects** following best practices
8. **Use modern Python features** (3.11+)

## Best Practices Checklist

When reviewing code, this skill ensures:

- ✅ PEP 8 compliant (naming, spacing, imports)
- ✅ All functions have type hints
- ✅ Public functions have comprehensive docstrings
- ✅ No code duplication (DRY principle)
- ✅ Single responsibility per function/class
- ✅ Appropriate error handling
- ✅ Tests exist for new functionality
- ✅ Code is formatted consistently
- ✅ Type checking passes
- ✅ Dependencies properly managed

## Resources

### Official Documentation
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Type Hints - PEP 484](https://peps.python.org/pep-0484/)

### Tools
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [Black](https://github.com/psf/black) - Code formatter
- [Mypy](https://mypy-lang.org/) - Type checker
- [uv](https://github.com/astral-sh/uv) - Fast package manager
- [Pytest](https://pytest.org/) - Testing framework

### Learning Resources
- [Real Python - PEP 8](https://realpython.com/python-pep8/)
- [Python Type Checking Guide](https://realpython.com/python-type-checking/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

## Contributing

To improve this skill:

1. Test with various Python projects
2. Update examples with new patterns
3. Add edge cases and common pitfalls
4. Keep tool versions current
5. Incorporate community feedback

## License

This skill is part of the skillin repository and follows the same license.

## Support

For issues or suggestions:
- Report bugs in the main skillin repository
- Submit pull requests with improvements
- Share your experience using this skill

## Version History

- **0.1.0** (Initial Release)
  - Complete PEP 8 guidelines
  - Modern tooling (Ruff, Black, Mypy, uv)
  - Comprehensive type hints examples
  - Testing patterns and TDD guidance
  - Error handling best practices
  - Quick reference guide

## Acknowledgments

Based on:
- Official Python Enhancement Proposals (PEPs)
- Community best practices
- Modern Python tooling ecosystem
- Real-world project experience
