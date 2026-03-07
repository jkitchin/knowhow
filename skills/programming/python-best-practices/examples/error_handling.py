"""Comprehensive demonstration of Python error handling best practices.

This module showcases:
- Custom exception hierarchies
- Proper exception handling patterns
- Context managers for resource management
- Error logging
- Recovery strategies
- Validation and defensive programming
"""

import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypeAlias
from collections.abc import Iterator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# 1. Custom Exception Hierarchy
class ApplicationError(Exception):
    """Base exception for all application errors.

    All application-specific exceptions should inherit from this.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize exception.

        Args:
            message: Human-readable error message
            details: Optional additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(ApplicationError):
    """Raised when data validation fails."""

    def __init__(self, field: str, message: str, value: Any = None):
        """Initialize validation error.

        Args:
            field: Name of field that failed validation
            message: Validation error message
            value: The invalid value (optional)
        """
        details = {"field": field, "value": value}
        super().__init__(f"Validation failed for '{field}': {message}", details)
        self.field = field
        self.value = value


class ResourceNotFoundError(ApplicationError):
    """Raised when a required resource cannot be found."""

    def __init__(self, resource_type: str, resource_id: str):
        """Initialize resource not found error.

        Args:
            resource_type: Type of resource (e.g., 'user', 'file')
            resource_id: Identifier for the resource
        """
        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(f"{resource_type} not found: {resource_id}", details)


class DatabaseError(ApplicationError):
    """Raised for database-related errors."""

    pass


class ConfigurationError(ApplicationError):
    """Raised for configuration-related errors."""

    pass


# 2. Validation Functions
def validate_email(email: str) -> str:
    """Validate email address.

    Args:
        email: Email address to validate

    Returns:
        Validated email address

    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError("email", "Email cannot be empty", email)

    if "@" not in email:
        raise ValidationError("email", "Email must contain @", email)

    parts = email.split("@")
    if len(parts) != 2:
        raise ValidationError("email", "Email must have exactly one @", email)

    local, domain = parts
    if not local or not domain:
        raise ValidationError("email", "Email parts cannot be empty", email)

    if "." not in domain:
        raise ValidationError("email", "Domain must contain a dot", email)

    return email.lower()


def validate_age(age: int) -> int:
    """Validate age value.

    Args:
        age: Age to validate

    Returns:
        Validated age

    Raises:
        ValidationError: If age is invalid
    """
    if not isinstance(age, int):
        raise ValidationError("age", "Age must be an integer", age)

    if age < 0:
        raise ValidationError("age", "Age cannot be negative", age)

    if age > 150:
        raise ValidationError("age", "Age is unrealistically high", age)

    return age


# 3. Error Handling Patterns
def safe_divide(a: float, b: float) -> float | None:
    """Safely divide two numbers.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Result of division, or None if division fails

    Example:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0)
        None
    """
    try:
        return a / b
    except ZeroDivisionError:
        logger.warning(f"Division by zero attempted: {a} / {b}")
        return None
    except TypeError as e:
        logger.error(f"Type error in division: {e}")
        return None


def read_file_safe(filepath: Path) -> str | None:
    """Safely read file content.

    Args:
        filepath: Path to file

    Returns:
        File content or None if reading fails
    """
    try:
        return filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return None
    except PermissionError:
        logger.error(f"Permission denied reading: {filepath}")
        return None
    except UnicodeDecodeError:
        logger.error(f"Failed to decode file as UTF-8: {filepath}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error reading {filepath}")
        return None


def process_file_with_recovery(filepath: Path) -> dict[str, Any]:
    """Process file with error recovery.

    Args:
        filepath: Path to file to process

    Returns:
        Processing results

    Raises:
        ApplicationError: If processing fails critically
    """
    try:
        if not filepath.exists():
            raise ResourceNotFoundError("file", str(filepath))

        content = filepath.read_text(encoding="utf-8")

        # Process content
        lines = [line.strip() for line in content.splitlines()]
        return {"status": "success", "lines": len(lines), "size": filepath.stat().st_size}

    except ResourceNotFoundError:
        # This is expected, re-raise
        raise

    except PermissionError as e:
        logger.error(f"Permission denied: {filepath}")
        raise ApplicationError(f"Cannot access file: {filepath}") from e

    except UnicodeDecodeError as e:
        logger.error(f"Encoding error in {filepath}")
        # Try recovery with different encoding
        try:
            content = filepath.read_text(encoding="latin-1")
            logger.info(f"Successfully recovered using latin-1 encoding")
            return {
                "status": "recovered",
                "lines": len(content.splitlines()),
                "size": filepath.stat().st_size,
                "encoding": "latin-1",
            }
        except Exception as recovery_error:
            raise ApplicationError(f"Failed to read file with any encoding: {filepath}") from e

    except Exception as e:
        logger.exception(f"Unexpected error processing {filepath}")
        raise ApplicationError(f"Processing failed: {filepath}") from e


# 4. Context Managers for Resource Management
@contextmanager
def open_file_safe(filepath: Path, mode: str = "r") -> Iterator[Any]:
    """Context manager for safe file handling.

    Args:
        filepath: Path to file
        mode: File mode ('r', 'w', etc.)

    Yields:
        File handle

    Raises:
        ApplicationError: If file operations fail
    """
    file_handle = None
    try:
        file_handle = filepath.open(mode, encoding="utf-8")
        logger.debug(f"Opened file: {filepath}")
        yield file_handle

    except FileNotFoundError as e:
        raise ResourceNotFoundError("file", str(filepath)) from e

    except PermissionError as e:
        raise ApplicationError(f"Permission denied: {filepath}") from e

    finally:
        if file_handle is not None:
            try:
                file_handle.close()
                logger.debug(f"Closed file: {filepath}")
            except Exception as e:
                logger.error(f"Error closing file {filepath}: {e}")


@contextmanager
def transaction_scope(connection: Any) -> Iterator[None]:
    """Context manager for database transactions.

    Args:
        connection: Database connection

    Yields:
        None (transaction is active)

    Raises:
        DatabaseError: If transaction fails
    """
    try:
        logger.info("Starting transaction")
        # connection.begin()
        yield

        # If no exception, commit
        # connection.commit()
        logger.info("Transaction committed")

    except Exception as e:
        # On any error, rollback
        logger.error(f"Transaction failed, rolling back: {e}")
        # connection.rollback()
        raise DatabaseError("Transaction failed") from e


# 5. Retry Logic
def retry_on_failure(func: Any, max_attempts: int = 3, delay: float = 1.0) -> Any:
    """Retry function on failure.

    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds

    Returns:
        Function result

    Raises:
        Exception: Last exception if all retries fail
    """
    import time

    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Attempt {attempt} of {max_attempts}")
            return func()

        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt} failed: {e}", exc_info=attempt == max_attempts)

            if attempt < max_attempts:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("All retry attempts failed")

    raise last_exception


# 6. Input Validation and Sanitization
def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename

    Raises:
        ValidationError: If filename is invalid
    """
    if not filename:
        raise ValidationError("filename", "Filename cannot be empty", filename)

    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove special characters
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    sanitized = "".join(c if c in allowed_chars else "_" for c in filename)

    if not sanitized or sanitized in (".", ".."):
        raise ValidationError("filename", "Invalid filename after sanitization", filename)

    return sanitized


def validate_user_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate user input data.

    Args:
        data: User input dictionary

    Returns:
        Validated and sanitized data

    Raises:
        ValidationError: If validation fails
    """
    validated = {}

    # Required fields
    required_fields = ["username", "email", "age"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(field, "Required field missing")

    # Validate username
    username = data["username"]
    if not isinstance(username, str) or not username.strip():
        raise ValidationError("username", "Username must be non-empty string", username)
    if len(username) < 3:
        raise ValidationError("username", "Username must be at least 3 characters", username)
    if len(username) > 50:
        raise ValidationError("username", "Username too long (max 50)", username)
    validated["username"] = username.strip()

    # Validate email
    validated["email"] = validate_email(data["email"])

    # Validate age
    validated["age"] = validate_age(data["age"])

    return validated


# 7. Error Recovery Strategies
class DataProcessor:
    """Data processor with comprehensive error handling."""

    def __init__(self, strict_mode: bool = True):
        """Initialize processor.

        Args:
            strict_mode: If True, fail on first error. If False, collect errors.
        """
        self.strict_mode = strict_mode
        self.errors: list[tuple[str, Exception]] = []

    def process_batch(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process batch of items with error handling.

        Args:
            items: List of items to process

        Returns:
            List of successfully processed items

        Raises:
            ApplicationError: If strict_mode and any item fails
        """
        results = []
        self.errors = []

        for i, item in enumerate(items):
            try:
                result = self._process_item(item)
                results.append(result)

            except ValidationError as e:
                error_context = f"Item {i}"
                self.errors.append((error_context, e))

                if self.strict_mode:
                    raise ApplicationError(f"Batch processing failed at item {i}") from e
                else:
                    logger.warning(f"Skipping invalid item {i}: {e}")

            except Exception as e:
                error_context = f"Item {i}"
                self.errors.append((error_context, e))

                if self.strict_mode:
                    raise ApplicationError(f"Unexpected error at item {i}") from e
                else:
                    logger.error(f"Error processing item {i}: {e}", exc_info=True)

        if self.errors:
            logger.info(f"Processed {len(results)} items successfully, {len(self.errors)} errors")

        return results

    def _process_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Process single item.

        Args:
            item: Item to process

        Returns:
            Processed item

        Raises:
            ValidationError: If item is invalid
        """
        # Validate required fields
        if "id" not in item:
            raise ValidationError("id", "Missing required field")

        # Process...
        return {"id": item["id"], "processed": True}


# 8. Logging Best Practices
def demo_logging_levels():
    """Demonstrate different logging levels."""
    # DEBUG: Detailed information for debugging
    logger.debug("Detailed debug information")

    # INFO: General informational messages
    logger.info("Operation completed successfully")

    # WARNING: Warning messages for unexpected but handled situations
    logger.warning("Resource usage is high")

    # ERROR: Error messages for failures that are handled
    logger.error("Failed to process item, skipping")

    # CRITICAL: Critical errors that may cause application failure
    logger.critical("Database connection lost")

    # Log with exception info
    try:
        raise ValueError("Example error")
    except ValueError:
        logger.exception("Error occurred during processing")


# 9. Main execution with error handling
def main() -> int:
    """Main entry point with error handling.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Main application logic
        logger.info("Application started")

        # Example operations
        result = process_file_with_recovery(Path("example.txt"))
        logger.info(f"Processing result: {result}")

        logger.info("Application completed successfully")
        return 0

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return 1

    except ResourceNotFoundError as e:
        logger.error(f"Resource not found: {e}")
        return 2

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return 3

    except ApplicationError as e:
        logger.error(f"Application error: {e}")
        if e.details:
            logger.error(f"Error details: {e.details}")
        return 4

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 130

    except Exception as e:
        logger.exception("Unexpected error occurred")
        return 99


if __name__ == "__main__":
    sys.exit(main())
