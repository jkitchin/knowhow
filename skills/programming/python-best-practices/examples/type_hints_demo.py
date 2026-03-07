"""Comprehensive demonstration of Python type hints and static typing.

This module showcases:
- Basic type annotations
- Collection types
- Optional and Union types
- Generic types
- Protocols (structural subtyping)
- Type aliases
- Callable types
- TypeVar and Generic classes
- Literal types
- Final types
"""

from collections.abc import Callable, Iterator, Sequence, Mapping
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Protocol, TypeAlias, Literal, Final, TypedDict, overload


# Basic type hints
def greet(name: str) -> str:
    """Simple function with basic types."""
    return f"Hello, {name}!"


def calculate_total(prices: list[float], tax_rate: float = 0.1) -> float:
    """Calculate total with tax."""
    subtotal = sum(prices)
    return subtotal * (1 + tax_rate)


# Collection types (Python 3.9+ syntax)
def process_scores(scores: dict[str, int]) -> list[tuple[str, int]]:
    """Process and sort scores."""
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def filter_items(items: set[str], exclude: frozenset[str]) -> set[str]:
    """Filter items excluding certain values."""
    return items - exclude


# Optional types (can be None)
def find_user(user_id: int) -> dict[str, Any] | None:
    """Find user by ID, return None if not found."""
    # Implementation...
    return None


def get_config_value(key: str, default: str | None = None) -> str | None:
    """Get configuration value with optional default."""
    # Implementation...
    return default


# Union types (multiple possible types)
def parse_value(value: str | int | float) -> float:
    """Parse value to float from various types."""
    return float(value)


# Use typing.Union for Python < 3.10
# from typing import Union
# def parse_value(value: Union[str, int, float]) -> float:
#     return float(value)


# Type aliases for complex types
UserId: TypeAlias = int
UserData: TypeAlias = dict[str, Any]
Coordinates: TypeAlias = tuple[float, float]
JsonValue: TypeAlias = str | int | float | bool | None | dict[str, Any] | list[Any]


def get_user_location(user_id: UserId) -> Coordinates:
    """Get user coordinates."""
    return (0.0, 0.0)


def parse_json(data: str) -> JsonValue:
    """Parse JSON data."""
    import json

    return json.loads(data)


# Callable types (functions as parameters)
def apply_operation(values: list[int], operation: Callable[[int], int]) -> list[int]:
    """Apply operation to each value."""
    return [operation(x) for x in values]


def create_multiplier(factor: int) -> Callable[[int], int]:
    """Create a function that multiplies by factor."""

    def multiply(x: int) -> int:
        return x * factor

    return multiply


# More complex callable signatures
def apply_binary_op(a: int, b: int, operation: Callable[[int, int], int]) -> int:
    """Apply binary operation."""
    return operation(a, b)


# Generic TypeVar
T = TypeVar("T")


def first_element(items: Sequence[T]) -> T | None:
    """Get first element from sequence."""
    return items[0] if items else None


def last_element(items: list[T]) -> T | None:
    """Get last element from list."""
    return items[-1] if items else None


# Constrained TypeVar
NumberT = TypeVar("NumberT", int, float)


def add_numbers(a: NumberT, b: NumberT) -> NumberT:
    """Add two numbers of same type."""
    return a + b  # type: ignore


# Bounded TypeVar
class Comparable(Protocol):
    """Protocol for comparable objects."""

    def __lt__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...


CT = TypeVar("CT", bound=Comparable)


def get_max(items: Sequence[CT]) -> CT:
    """Get maximum value from sequence."""
    return max(items)


# Generic classes
class Stack(Generic[T]):
    """Generic stack implementation."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Add item to stack."""
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return top item."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T | None:
        """View top item without removing."""
        return self._items[-1] if self._items else None

    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._items) == 0

    def __len__(self) -> int:
        """Get stack size."""
        return len(self._items)


# Usage of generic stack
def demo_generic_stack() -> None:
    """Demonstrate generic stack usage."""
    int_stack: Stack[int] = Stack()
    int_stack.push(1)
    int_stack.push(2)
    value: int = int_stack.pop()  # Type checker knows this is int

    str_stack: Stack[str] = Stack()
    str_stack.push("hello")
    text: str = str_stack.pop()  # Type checker knows this is str


# Protocols (structural subtyping / duck typing)
class Drawable(Protocol):
    """Protocol for objects that can be drawn."""

    def draw(self) -> str:
        """Draw the object."""
        ...

    def get_position(self) -> tuple[int, int]:
        """Get object position."""
        ...


class Circle:
    """Circle implementation (doesn't explicitly inherit Drawable)."""

    def __init__(self, x: int, y: int, radius: int):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self) -> str:
        """Draw circle."""
        return f"Circle at ({self.x}, {self.y}) with radius {self.radius}"

    def get_position(self) -> tuple[int, int]:
        """Get circle position."""
        return (self.x, self.y)


class Rectangle:
    """Rectangle implementation."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self) -> str:
        """Draw rectangle."""
        return f"Rectangle at ({self.x}, {self.y}) size {self.width}x{self.height}"

    def get_position(self) -> tuple[int, int]:
        """Get rectangle position."""
        return (self.x, self.y)


def render(shape: Drawable) -> None:
    """Render any drawable object."""
    print(shape.draw())


def render_all(shapes: Sequence[Drawable]) -> None:
    """Render multiple shapes."""
    for shape in shapes:
        render(shape)


# TypedDict for structured dictionaries
class UserDict(TypedDict):
    """Type definition for user dictionary."""

    username: str
    email: str
    age: int
    is_admin: bool


class UserDictOptional(TypedDict, total=False):
    """User dict with optional fields."""

    username: str
    email: str
    age: int
    phone: str  # This field is optional


def create_user(username: str, email: str, age: int) -> UserDict:
    """Create user dictionary."""
    return {"username": username, "email": email, "age": age, "is_admin": False}


def process_user(user: UserDict) -> str:
    """Process user data."""
    # Type checker knows all required fields exist
    return f"{user['username']} ({user['email']})"


# Literal types (specific values only)
Status: TypeAlias = Literal["pending", "approved", "rejected"]
LogLevel: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


def set_status(item_id: int, status: Status) -> None:
    """Set item status (only specific values allowed)."""
    print(f"Setting status of {item_id} to {status}")


def log_message(message: str, level: LogLevel = "INFO") -> None:
    """Log message with specific level."""
    print(f"[{level}] {message}")


# Final - cannot be overridden/reassigned
MAX_SIZE: Final = 100
API_KEY: Final[str] = "secret-key"


class BaseConfig:
    """Base configuration class."""

    MAX_CONNECTIONS: Final = 50  # Cannot be overridden in subclasses

    # Final method (cannot be overridden)
    def get_version(self) -> str:
        """Get version (cannot be overridden)."""
        return "1.0.0"


# Overload - multiple signatures
@overload
def process(value: int) -> str: ...


@overload
def process(value: str) -> int: ...


def process(value: int | str) -> str | int:
    """Process value (different return type based on input)."""
    if isinstance(value, int):
        return str(value)
    else:
        return len(value)


# Complex generic with multiple type parameters
KT = TypeVar("KT")
VT = TypeVar("VT")


class BiMap(Generic[KT, VT]):
    """Bidirectional map."""

    def __init__(self) -> None:
        self._forward: dict[KT, VT] = {}
        self._reverse: dict[VT, KT] = {}

    def set(self, key: KT, value: VT) -> None:
        """Set key-value pair."""
        self._forward[key] = value
        self._reverse[value] = key

    def get_by_key(self, key: KT) -> VT | None:
        """Get value by key."""
        return self._forward.get(key)

    def get_by_value(self, value: VT) -> KT | None:
        """Get key by value."""
        return self._reverse.get(value)


# Iterator and Generator types
def count_up(n: int) -> Iterator[int]:
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


def fibonacci(n: int) -> Iterator[int]:
    """Generate first n Fibonacci numbers."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# Complex return type
def split_by_type(items: Sequence[int | str]) -> tuple[list[int], list[str]]:
    """Split items into integers and strings."""
    integers: list[int] = []
    strings: list[str] = []

    for item in items:
        if isinstance(item, int):
            integers.append(item)
        elif isinstance(item, str):
            strings.append(item)

    return integers, strings


# Dataclass with type hints
@dataclass
class Point:
    """2D point with type annotations."""

    x: float
    y: float

    def distance_from_origin(self) -> float:
        """Calculate distance from origin."""
        return (self.x**2 + self.y**2) ** 0.5


@dataclass
class Circle2:
    """Circle with center point."""

    center: Point
    radius: float

    def area(self) -> float:
        """Calculate circle area."""
        import math

        return math.pi * self.radius**2


# Context manager with type hints
from contextlib import contextmanager
from collections.abc import Iterator as IteratorType


@contextmanager
def temporary_file(path: str) -> IteratorType[str]:
    """Context manager for temporary file."""
    # Setup
    with open(path, "w") as f:
        f.write("temp")

    try:
        yield path
    finally:
        # Cleanup
        import os

        os.remove(path)


# Class with type hints for all methods
class Database:
    """Database connection with full type annotations."""

    def __init__(self, connection_string: str, timeout: int = 30) -> None:
        """Initialize database connection."""
        self.connection_string = connection_string
        self.timeout = timeout
        self._connected: bool = False

    def connect(self) -> bool:
        """Establish connection."""
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Close connection."""
        self._connected = False

    def execute(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute query and return results."""
        if parameters is None:
            parameters = {}
        # Implementation...
        return []

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected


# Using type hints with async code
async def fetch_data(url: str) -> dict[str, Any]:
    """Async function to fetch data."""
    # Implementation...
    return {}


async def fetch_multiple(urls: Sequence[str]) -> list[dict[str, Any]]:
    """Fetch data from multiple URLs concurrently."""
    # Implementation...
    return []


# Type narrowing with isinstance
def process_input(value: str | int | list[str]) -> str:
    """Process different input types with type narrowing."""
    if isinstance(value, str):
        # Type checker knows value is str here
        return value.upper()
    elif isinstance(value, int):
        # Type checker knows value is int here
        return str(value * 2)
    else:
        # Type checker knows value is list[str] here
        return ", ".join(value)


# Self type for fluent interfaces
from typing import Self


class Builder:
    """Builder with fluent interface."""

    def __init__(self) -> None:
        self._value: str = ""

    def add(self, text: str) -> Self:
        """Add text and return self."""
        self._value += text
        return self

    def build(self) -> str:
        """Build final string."""
        return self._value


# Usage demonstrates type safety:
# builder = Builder()
# result: str = builder.add("Hello").add(" World").build()


if __name__ == "__main__":
    # Demonstrate various type-safe operations
    print(greet("World"))
    print(calculate_total([10.0, 20.0, 30.0]))

    # Generic stack
    demo_generic_stack()

    # Protocols
    shapes: list[Drawable] = [Circle(10, 10, 5), Rectangle(20, 20, 10, 15)]
    render_all(shapes)

    # Literal types
    set_status(1, "approved")
    log_message("Application started", "INFO")
