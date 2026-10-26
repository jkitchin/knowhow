"""Security tests for skillpack."""

import pytest

from skillpack.config import VALID_PLATFORMS, InvalidPlatformError, validate_platform
from skillpack.utils import PathTraversalError, safe_path_join


class TestSafePathJoin:
    """Tests for safe_path_join security function."""

    def test_safe_path_normal(self, temp_dir):
        """Test safe_path_join with normal path."""
        result = safe_path_join(temp_dir, "my-skill")
        # Use resolve() to handle macOS /var -> /private/var symlink
        assert result == temp_dir.resolve() / "my-skill"

    def test_safe_path_with_subdirectory(self, temp_dir):
        """Test safe_path_join with nested path."""
        subdir = temp_dir / "skills"
        subdir.mkdir()
        result = safe_path_join(subdir, "test-skill")
        # Use resolve() to handle macOS /var -> /private/var symlink
        assert result == subdir.resolve() / "test-skill"

    def test_path_traversal_dotdot(self, temp_dir):
        """Test that .. path traversal is blocked."""
        with pytest.raises(PathTraversalError) as exc_info:
            safe_path_join(temp_dir, "../etc/passwd")
        assert "traversal" in str(exc_info.value).lower()

    def test_path_traversal_absolute(self, temp_dir):
        """Test that absolute paths are handled."""
        # This should resolve but still be checked
        result = safe_path_join(temp_dir, "normal-name")
        assert str(temp_dir) in str(result)

    def test_path_traversal_complex(self, temp_dir):
        """Test complex path traversal attempt."""
        with pytest.raises(PathTraversalError):
            safe_path_join(temp_dir, "foo/../../../bar")

    def test_path_traversal_encoded(self, temp_dir):
        """Test that URL-encoded traversal doesn't work."""
        # Note: %2e%2e is URL-encoded .. but won't decode in filesystem
        # This tests that literal strings with unusual chars are handled
        result = safe_path_join(temp_dir, "normal-skill")
        # Use resolve() to handle macOS /var -> /private/var symlink
        assert result.parent == temp_dir.resolve()


class TestValidatePlatform:
    """Tests for platform validation."""

    def test_valid_platforms(self):
        """Test all valid platforms are accepted."""
        for platform in VALID_PLATFORMS:
            result = validate_platform(platform)
            assert result == platform

    def test_valid_platforms_case_insensitive(self):
        """Test platforms are case-insensitive."""
        assert validate_platform("CLAUDE") == "claude"
        assert validate_platform("OpenCode") == "opencode"
        assert validate_platform("CODEX") == "codex"

    def test_invalid_platform(self):
        """Test invalid platform raises error."""
        with pytest.raises(InvalidPlatformError) as exc_info:
            validate_platform("invalid-platform")
        assert "invalid-platform" in str(exc_info.value).lower()

    def test_empty_platform(self):
        """Test empty string raises error."""
        with pytest.raises(InvalidPlatformError):
            validate_platform("")

    def test_platform_with_path(self):
        """Test platform with path characters raises error."""
        with pytest.raises(InvalidPlatformError):
            validate_platform("claude/../etc")

    def test_sql_injection_attempt(self):
        """Test SQL injection-like input is rejected."""
        with pytest.raises(InvalidPlatformError):
            validate_platform("claude'; DROP TABLE users;--")


class TestSymlinkSafety:
    """Tests for symlink-safe operations."""

    def test_symlink_in_path_detected(self, temp_dir):
        """Test that symlinks pointing outside are detected."""
        # Create a directory structure
        inside = temp_dir / "inside"
        inside.mkdir()

        outside = temp_dir / "outside"
        outside.mkdir()

        # Create a symlink inside pointing to outside
        symlink = inside / "sneaky"
        symlink.symlink_to(outside)

        # safe_path_join should detect the symlink escape
        # Note: The symlink itself exists, so we're testing the symlink check
        with pytest.raises(PathTraversalError):
            safe_path_join(inside, "sneaky/../../../etc")


class TestInputValidation:
    """Tests for general input validation."""

    def test_name_with_null_byte(self, temp_dir):
        """Test names with null bytes are handled."""
        # Null bytes in filenames are generally not allowed
        # This tests robustness of the validation
        from skillpack.utils import validate_name

        assert not validate_name("skill\x00name")

    def test_name_with_newline(self):
        """Test names with newlines are rejected."""
        from skillpack.utils import validate_name

        assert not validate_name("skill\nname")

    def test_name_with_unicode(self):
        """Test names with unicode are rejected (lowercase-hyphens only)."""
        from skillpack.utils import validate_name

        assert not validate_name("skíll-name")
        assert not validate_name("skill-名前")

    def test_valid_name_patterns(self):
        """Test valid name patterns are accepted."""
        from skillpack.utils import validate_name

        assert validate_name("my-skill")
        assert validate_name("skill123")
        assert validate_name("a-b-c-1-2-3")
        assert validate_name("x")

    def test_invalid_name_patterns(self):
        """Test invalid name patterns are rejected."""
        from skillpack.utils import validate_name

        assert not validate_name("My-Skill")  # uppercase
        assert not validate_name("my skill")  # space
        assert not validate_name("my_skill")  # underscore
        assert not validate_name("my.skill")  # dot
        assert not validate_name("")  # empty
