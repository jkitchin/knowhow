---
name: python-best-practices
description: |
  Expert guidance for writing professional Python code following industry best practices
  including PEP 8 compliance, testing, type hints, error handling, and modern tooling.

  Use this skill when writing new Python code, refactoring existing code, setting up
  Python projects, implementing tests, or ensuring code quality and maintainability.

  Emphasizes: PEP 8, modularity, DRY principle, TDD, virtual environments (uv),
  and modern tooling (Ruff, Black, Mypy).
allowed-tools: ["Read", "Edit", "Write", "Bash", "Grep", "Glob"]
---

# Python Best Practices Skill

This skill provides expert guidance for writing professional, maintainable Python code that follows industry best practices and standards.

## When to Use This Skill

Use this skill when:
- Writing new Python functions, classes, or modules
- Refactoring existing Python code for better quality
- Setting up a new Python project with proper structure
- Implementing unit tests or adopting TDD
- Adding type hints for better code clarity
- Configuring linting, formatting, and type checking tools
- Managing dependencies and virtual environments
- Improving code readability and maintainability
- Following PEP 8 style guidelines

## Core Principles

### 1. PEP 8: Style Guide for Python Code

**Key Guidelines:**
- **Indentation**: Use 4 spaces per indentation level (never tabs)
- **Line Length**: Limit lines to 79 characters (99 for code, 72 for docstrings/comments)
- **Blank Lines**: 2 blank lines between top-level functions/classes, 1 within classes
- **Imports**:
  - One import per line
  - Order: standard library, third-party, local (each group separated by blank line)
  - Avoid wildcard imports (`from module import *`)
- **Naming Conventions**:
  - `snake_case` for functions, variables, methods
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - Leading underscore `_private` for internal use
- **Whitespace**:
  - No trailing whitespace
  - One space around operators: `x = 1`, not `x=1`
  - No space before function parentheses: `func(x)`, not `func (x)`

**Example:**
```python
"""Module docstring describing purpose."""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from mypackage.module import MyClass

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30


class DataProcessor:
    """Process and analyze data sets.

    Attributes:
        name: Processor name
        threshold: Minimum value threshold
    """

    def __init__(self, name: str, threshold: float = 0.5):
        """Initialize processor.

        Args:
            name: Name of the processor
            threshold: Threshold value for filtering (default: 0.5)
        """
        self.name = name
        self.threshold = threshold

    def process_data(self, data: list[float]) -> list[float]:
        """Process data by filtering values below threshold.

        Args:
            data: List of numeric values to process

        Returns:
            Filtered list containing only values >= threshold

        Raises:
            ValueError: If data is empty
        """
        if not data:
            raise ValueError("Data cannot be empty")

        return [x for x in data if x >= self.threshold]
```

### 2. Readability and Clarity

**Write Self-Documenting Code:**
```python
# Bad: unclear variable names
def calc(x, y, z):
    return x * y / z

# Good: descriptive names
def calculate_unit_price(total_cost: float, quantity: int, tax_rate: float) -> float:
    """Calculate price per unit including tax."""
    return total_cost * (1 + tax_rate) / quantity
```

**Use Docstrings:**
```python
def fetch_user_data(user_id: int, include_history: bool = False) -> dict:
    """Fetch user data from the database.

    Args:
        user_id: Unique identifier for the user
        include_history: Whether to include transaction history

    Returns:
        Dictionary containing user information with keys:
            - 'name': User's full name
            - 'email': User's email address
            - 'history': List of transactions (if include_history=True)

    Raises:
        UserNotFoundError: If user_id doesn't exist
        DatabaseError: If connection fails

    Example:
        >>> user = fetch_user_data(123, include_history=True)
        >>> print(user['name'])
        'John Doe'
    """
    # Implementation...
```

**Prefer Explicit Over Implicit:**
```python
# Bad: implicit behavior
def process(items):
    return [x for x in items if x]

# Good: explicit intention
def filter_non_empty_items(items: list) -> list:
    """Remove None and empty string values from items."""
    return [item for item in items if item is not None and item != ""]
```

### 3. Modularity and Reusability (DRY Principle)

**Single Responsibility Principle:**
```python
# Bad: function does too much
def process_and_save_report(data):
    # Process data
    cleaned = [x.strip() for x in data]
    filtered = [x for x in cleaned if len(x) > 0]

    # Calculate statistics
    total = sum(len(x) for x in filtered)
    avg = total / len(filtered)

    # Format report
    report = f"Total: {total}, Average: {avg}"

    # Save to file
    with open('report.txt', 'w') as f:
        f.write(report)

    return report

# Good: separate concerns
def clean_data(data: list[str]) -> list[str]:
    """Remove whitespace and empty strings."""
    cleaned = [item.strip() for item in data]
    return [item for item in cleaned if item]

def calculate_statistics(data: list[str]) -> dict:
    """Calculate length statistics for strings."""
    lengths = [len(item) for item in data]
    return {
        'total': sum(lengths),
        'average': sum(lengths) / len(lengths) if lengths else 0,
        'count': len(lengths)
    }

def format_report(stats: dict) -> str:
    """Format statistics as a readable report."""
    return f"Total: {stats['total']}, Average: {stats['average']:.2f}"

def save_report(content: str, filepath: Path) -> None:
    """Save report content to file."""
    filepath.write_text(content)

# Usage
cleaned = clean_data(data)
stats = calculate_statistics(cleaned)
report = format_report(stats)
save_report(report, Path('report.txt'))
```

**Avoid Duplication:**
```python
# Bad: repeated logic
def calculate_circle_area(radius):
    return 3.14159 * radius * radius

def calculate_circle_circumference(radius):
    return 2 * 3.14159 * radius

# Good: reusable constants and functions
import math

def calculate_circle_area(radius: float) -> float:
    """Calculate area of circle."""
    return math.pi * radius ** 2

def calculate_circle_circumference(radius: float) -> float:
    """Calculate circumference of circle."""
    return 2 * math.pi * radius

def calculate_circle_properties(radius: float) -> dict:
    """Calculate all circle properties."""
    return {
        'area': calculate_circle_area(radius),
        'circumference': calculate_circle_circumference(radius)
    }
```

**Use Classes for Related Functionality:**
```python
class DataValidator:
    """Validate data according to defined rules."""

    def __init__(self, min_length: int = 0, max_length: int = 100):
        self.min_length = min_length
        self.max_length = max_length

    def validate_length(self, value: str) -> bool:
        """Check if string length is within bounds."""
        return self.min_length <= len(value) <= self.max_length

    def validate_email(self, email: str) -> bool:
        """Check if email format is valid."""
        return '@' in email and '.' in email.split('@')[1]

    def validate_all(self, data: dict) -> dict[str, bool]:
        """Validate all fields in data dictionary."""
        return {
            'email': self.validate_email(data.get('email', '')),
            'name': self.validate_length(data.get('name', ''))
        }
```

### 4. Testing and TDD

**Write Testable Code:**
```python
# Bad: hard to test (depends on external state)
def get_config_value(key):
    with open('/etc/myapp/config.ini') as f:
        for line in f:
            if line.startswith(key):
                return line.split('=')[1].strip()

# Good: testable with dependency injection
def get_config_value(key: str, config_path: Path) -> str:
    """Get configuration value from file."""
    content = config_path.read_text()
    for line in content.splitlines():
        if line.startswith(key):
            return line.split('=')[1].strip()
    raise KeyError(f"Config key '{key}' not found")
```

**Unit Test Structure:**
```python
import pytest
from mymodule import calculate_unit_price, UserNotFoundError


class TestCalculateUnitPrice:
    """Test suite for calculate_unit_price function."""

    def test_basic_calculation(self):
        """Test basic price calculation without tax."""
        result = calculate_unit_price(100.0, 10, 0.0)
        assert result == 10.0

    def test_with_tax(self):
        """Test price calculation with tax included."""
        result = calculate_unit_price(100.0, 10, 0.2)
        assert result == 12.0

    def test_zero_quantity_raises_error(self):
        """Test that zero quantity raises ValueError."""
        with pytest.raises(ZeroDivisionError):
            calculate_unit_price(100.0, 0, 0.1)

    @pytest.mark.parametrize("total,qty,tax,expected", [
        (100, 10, 0.0, 10.0),
        (100, 10, 0.1, 11.0),
        (50, 5, 0.2, 12.0),
    ])
    def test_multiple_scenarios(self, total, qty, tax, expected):
        """Test multiple calculation scenarios."""
        assert calculate_unit_price(total, qty, tax) == pytest.approx(expected)
```

**TDD Approach:**
```python
# Step 1: Write the test first
def test_parse_csv_line():
    """Test CSV line parsing."""
    result = parse_csv_line('John,Doe,30')
    assert result == {'first': 'John', 'last': 'Doe', 'age': 30}

# Step 2: Implement minimal code to pass
def parse_csv_line(line: str) -> dict:
    """Parse CSV line into dictionary."""
    parts = line.split(',')
    return {
        'first': parts[0],
        'last': parts[1],
        'age': int(parts[2])
    }

# Step 3: Refactor while keeping tests green
def parse_csv_line(line: str, headers: list[str] = None) -> dict:
    """Parse CSV line into dictionary with optional headers."""
    if headers is None:
        headers = ['first', 'last', 'age']

    parts = line.split(',')
    result = {}

    for i, header in enumerate(headers):
        value = parts[i].strip()
        # Convert to int if header is 'age'
        result[header] = int(value) if header == 'age' else value

    return result
```

### 5. Error Handling

**Use Specific Exceptions:**
```python
# Bad: generic exceptions
def divide(a, b):
    if b == 0:
        raise Exception("Can't divide by zero")
    return a / b

# Good: specific exceptions
class DivisionByZeroError(ValueError):
    """Raised when attempting to divide by zero."""
    pass

def divide(a: float, b: float) -> float:
    """Divide two numbers.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Result of division

    Raises:
        DivisionByZeroError: If denominator is zero
    """
    if b == 0:
        raise DivisionByZeroError(f"Cannot divide {a} by zero")
    return a / b
```

**Proper Exception Handling:**
```python
# Bad: bare except
try:
    result = risky_operation()
except:
    print("Error occurred")

# Good: specific exceptions with context
import logging

logger = logging.getLogger(__name__)

def process_file(filepath: Path) -> dict:
    """Process file and return parsed data."""
    try:
        content = filepath.read_text()
        return parse_content(content)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except PermissionError:
        logger.error(f"Permission denied: {filepath}")
        raise
    except ValueError as e:
        logger.error(f"Invalid content in {filepath}: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing {filepath}")
        raise
```

**Context Managers for Resource Management:**
```python
# Good: automatic cleanup
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def open_database(db_path: Path):
    """Context manager for database connections."""
    conn = connect_to_database(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Usage
with open_database(Path('data.db')) as db:
    results = db.query('SELECT * FROM users')
```

### 6. Virtual Environments and Dependency Management

**Using uv (Modern, Fast Package Manager):**

```bash
# Create new project with uv
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install pandas numpy pytest

# Install with specific version
uv pip install "requests>=2.28.0,<3.0"

# Install development dependencies
uv pip install -e ".[dev]"

# Create requirements file
uv pip freeze > requirements.txt

# Install from requirements
uv pip install -r requirements.txt
```

**Project Structure with pyproject.toml:**
```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A well-structured Python project"
authors = [{name = "Your Name", email = "you@example.com"}]
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 99
target-version = ['py311']

[tool.ruff]
line-length = 99
target-version = "py311"
select = ["E", "F", "I", "N", "W", "B", "C4"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
```

### 7. Modern Python Tooling

**Ruff: Fast Linter and Formatter**
```bash
# Install
uv pip install ruff

# Check code
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .

# Configuration in pyproject.toml
[tool.ruff]
line-length = 99
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = ["E501"]  # line too long (handled by formatter)
```

**Black: Code Formatter**
```bash
# Install
uv pip install black

# Format files
black myproject/

# Check without modifying
black --check myproject/

# Configuration
[tool.black]
line-length = 99
target-version = ['py311']
include = '\.pyi?$'
```

**Mypy: Static Type Checker**
```bash
# Install
uv pip install mypy

# Check types
mypy myproject/

# Configuration
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Type Hints Examples:**
```python
from typing import Protocol, TypeVar, Generic
from collections.abc import Sequence, Callable

# Basic type hints
def greet(name: str) -> str:
    return f"Hello, {name}"

# Collections
def process_items(items: list[int]) -> dict[str, int]:
    return {'total': sum(items), 'count': len(items)}

# Optional values
from typing import Optional

def find_user(user_id: int) -> Optional[dict]:
    """Return user dict or None if not found."""
    # ...

# Union types (Python 3.10+)
def parse_value(value: str | int) -> float:
    return float(value)

# Callable
def apply_function(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Generic types
T = TypeVar('T')

def first_element(items: Sequence[T]) -> T | None:
    return items[0] if items else None

# Protocol (structural subtyping)
class Drawable(Protocol):
    def draw(self) -> None:
        ...

def render(obj: Drawable) -> None:
    obj.draw()
```

## Best Practices Workflow

### When Writing New Code:

1. **Start with type hints and docstrings**
2. **Write tests first (TDD)** - define expected behavior
3. **Implement minimal code** to pass tests
4. **Refactor** while keeping tests green
5. **Run linter** (`ruff check`)
6. **Format code** (`ruff format` or `black`)
7. **Check types** (`mypy`)
8. **Run tests** (`pytest`)

### When Refactoring Existing Code:

1. **Add tests** if they don't exist
2. **Run existing tests** to establish baseline
3. **Refactor incrementally** (small changes)
4. **Run tests after each change**
5. **Improve type coverage**
6. **Apply linter fixes**
7. **Update documentation**

## Common Patterns

### Configuration Management:
```python
from dataclasses import dataclass
from pathlib import Path
import tomllib

@dataclass
class Config:
    """Application configuration."""
    database_url: str
    api_key: str
    timeout: int = 30
    debug: bool = False

def load_config(config_path: Path) -> Config:
    """Load configuration from TOML file."""
    with config_path.open('rb') as f:
        data = tomllib.load(f)
    return Config(**data)
```

### Logging:
```python
import logging
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Path | None = None) -> None:
    """Configure application logging."""
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

# Usage
logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

### CLI with argparse:
```python
import argparse
from pathlib import Path

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process data files")
    parser.add_argument('input', type=Path, help="Input file path")
    parser.add_argument('-o', '--output', type=Path, help="Output file path")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    return parser.parse_args()

def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        setup_logging("DEBUG")

    process_file(args.input, args.output)

if __name__ == '__main__':
    main()
```

## Instructions for Code Reviews

When reviewing or generating Python code, check for:

1. **PEP 8 Compliance**:
   - Correct naming conventions
   - Proper indentation (4 spaces)
   - Appropriate line length
   - Correct import ordering

2. **Type Hints**:
   - All function signatures have type hints
   - Return types are specified
   - Complex types use proper typing constructs

3. **Documentation**:
   - All public functions have docstrings
   - Docstrings include Args, Returns, Raises sections
   - Complex logic has explanatory comments

4. **Error Handling**:
   - Specific exceptions are used
   - Resources are properly cleaned up
   - Error messages are informative

5. **Testing**:
   - Tests exist for new functionality
   - Edge cases are covered
   - Tests are clear and maintainable

6. **Code Quality**:
   - No code duplication
   - Functions have single responsibility
   - Magic numbers are replaced with named constants
   - No overly complex functions (consider cyclomatic complexity)

## Resources and Tools

### Essential Tools:
- **uv**: Fast package installer and resolver
- **Ruff**: Fast Python linter and formatter (Rust-based)
- **Black**: Opinionated code formatter
- **Mypy**: Static type checker
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks for code quality

### Official References:
- PEP 8: https://peps.python.org/pep-0008/
- PEP 257: Docstring Conventions
- Python Type Hints: PEP 484, 585, 604
- Python Enhancement Proposals: https://peps.python.org/

## Limitations

This skill focuses on general Python best practices. For specialized domains:
- **Scientific computing**: Consider numpy/scipy conventions
- **Web development**: Framework-specific patterns (Django, FastAPI)
- **Data science**: Jupyter notebook best practices
- **Async programming**: asyncio patterns and best practices

For these specialized areas, combine this skill with domain-specific skills or documentation.
