"""Tests for hooks functionality."""

import pytest

from knowhow.validator import HookValidator


@pytest.fixture
def mock_hooks_dir(temp_dir):
    """Create a mock hooks directory with a sample hook."""
    hooks_dir = temp_dir / "hooks"
    hooks_dir.mkdir()

    # Create a valid hook
    hook_dir = hooks_dir / "test-hook"
    hook_dir.mkdir()

    hook_md = hook_dir / "HOOK.md"
    hook_md.write_text("""---
name: test-hook
description: A test hook for unit testing
event: PostToolUse
matcher: Edit|Write
type: command
timeout: 30
---

# Test Hook

This is a test hook.
""")

    hook_py = hook_dir / "hook.py"
    hook_py.write_text("""#!/usr/bin/env python3
import sys
sys.exit(0)
""")

    return hooks_dir


@pytest.fixture
def mock_repository_with_hooks(temp_dir):
    """Create a mock repository with skills, commands, and hooks."""
    repo_dir = temp_dir / "repository"
    repo_dir.mkdir()

    # Create hooks directory
    hooks_dir = repo_dir / "hooks"
    hooks_dir.mkdir()

    # Create a sample hook
    hook_dir = hooks_dir / "sample-hook"
    hook_dir.mkdir()

    hook_md = hook_dir / "HOOK.md"
    hook_md.write_text("""---
name: sample-hook
description: A sample hook for testing
event: PreToolUse
matcher: Bash
type: command
timeout: 60
---

# Sample Hook
""")

    hook_py = hook_dir / "hook.py"
    hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

    return repo_dir


class TestHookValidator:
    """Tests for HookValidator."""

    def test_valid_hook(self, mock_hooks_dir):
        """Test validation of a valid hook."""
        hook_dir = mock_hooks_dir / "test-hook"
        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_hook_md(self, temp_dir):
        """Test validation fails when HOOK.md is missing."""
        hook_dir = temp_dir / "invalid-hook"
        hook_dir.mkdir()
        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("HOOK.md" in error for error in errors)

    def test_missing_script(self, temp_dir):
        """Test validation fails when no script file exists."""
        hook_dir = temp_dir / "no-script-hook"
        hook_dir.mkdir()
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text("""---
name: no-script-hook
description: Hook without script
event: PostToolUse
---

# Test
""")
        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("script" in error.lower() for error in errors)

    def test_invalid_name_uppercase(self, temp_dir):
        """Test validation fails with uppercase in name."""
        hook_dir = temp_dir / "InvalidHook"
        hook_dir.mkdir()
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text("""---
name: InvalidHook
description: This has uppercase letters
event: PostToolUse
---

# Test
""")
        hook_py = hook_dir / "hook.py"
        hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("name" in error.lower() for error in errors)

    def test_missing_event(self, temp_dir):
        """Test validation fails when event is missing."""
        hook_dir = temp_dir / "test-hook"
        hook_dir.mkdir()
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text("""---
name: test-hook
description: Missing event field
---

# Test
""")
        hook_py = hook_dir / "hook.py"
        hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("event" in error.lower() for error in errors)

    def test_invalid_event(self, temp_dir):
        """Test validation fails with invalid event."""
        hook_dir = temp_dir / "test-hook"
        hook_dir.mkdir()
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text("""---
name: test-hook
description: Invalid event value
event: InvalidEvent
---

# Test
""")
        hook_py = hook_dir / "hook.py"
        hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("InvalidEvent" in error for error in errors)

    def test_valid_events(self, temp_dir):
        """Test validation succeeds for all valid events."""
        valid_events = [
            "PreToolUse",
            "PostToolUse",
            "PermissionRequest",
            "UserPromptSubmit",
            "Notification",
            "Stop",
            "SubagentStop",
            "PreCompact",
            "SessionStart",
            "SessionEnd",
        ]

        for event in valid_events:
            hook_dir = temp_dir / f"hook-{event.lower()}"
            hook_dir.mkdir()
            hook_md = hook_dir / "HOOK.md"
            hook_md.write_text(f"""---
name: hook-{event.lower()}
description: Testing {event} event
event: {event}
---

# Test
""")
            hook_py = hook_dir / "hook.py"
            hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

            is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
            assert is_valid is True, f"Event {event} should be valid, got errors: {errors}"

    def test_description_too_long(self, temp_dir):
        """Test validation fails when description exceeds 256 chars."""
        hook_dir = temp_dir / "test-hook"
        hook_dir.mkdir()
        long_description = "x" * 257
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text(f"""---
name: test-hook
description: {long_description}
event: PostToolUse
---

# Test
""")
        hook_py = hook_dir / "hook.py"
        hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("256" in error for error in errors)

    def test_invalid_type(self, temp_dir):
        """Test validation fails with invalid type."""
        hook_dir = temp_dir / "test-hook"
        hook_dir.mkdir()
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text("""---
name: test-hook
description: Invalid type value
event: PostToolUse
type: invalid
---

# Test
""")
        hook_py = hook_dir / "hook.py"
        hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("type" in error.lower() for error in errors)

    def test_valid_types(self, temp_dir):
        """Test validation succeeds for valid types."""
        for hook_type in ["command", "prompt"]:
            hook_dir = temp_dir / f"hook-{hook_type}"
            hook_dir.mkdir()
            hook_md = hook_dir / "HOOK.md"
            hook_md.write_text(f"""---
name: hook-{hook_type}
description: Testing {hook_type} type
event: PostToolUse
type: {hook_type}
---

# Test
""")
            hook_py = hook_dir / "hook.py"
            hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

            is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
            assert is_valid is True, f"Type {hook_type} should be valid"

    def test_invalid_timeout(self, temp_dir):
        """Test validation fails with invalid timeout."""
        hook_dir = temp_dir / "test-hook"
        hook_dir.mkdir()
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text("""---
name: test-hook
description: Invalid timeout value
event: PostToolUse
timeout: -10
---

# Test
""")
        hook_py = hook_dir / "hook.py"
        hook_py.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is False
        assert any("timeout" in error.lower() for error in errors)

    def test_get_hook_metadata(self, mock_hooks_dir):
        """Test extracting metadata from a hook."""
        hook_dir = mock_hooks_dir / "test-hook"
        metadata = HookValidator.get_hook_metadata(hook_dir)

        assert metadata is not None
        assert metadata["name"] == "test-hook"
        assert metadata["description"] == "A test hook for unit testing"
        assert metadata["event"] == "PostToolUse"
        assert metadata["matcher"] == "Edit|Write"
        assert metadata["type"] == "command"
        assert metadata["timeout"] == 30

    def test_get_hook_metadata_missing_file(self, temp_dir):
        """Test get_hook_metadata returns None for missing HOOK.md."""
        hook_dir = temp_dir / "no-hook"
        hook_dir.mkdir()
        metadata = HookValidator.get_hook_metadata(hook_dir)
        assert metadata is None

    def test_shell_script_valid(self, temp_dir):
        """Test validation succeeds with shell script instead of Python."""
        hook_dir = temp_dir / "shell-hook"
        hook_dir.mkdir()
        hook_md = hook_dir / "HOOK.md"
        hook_md.write_text("""---
name: shell-hook
description: Hook using shell script
event: PostToolUse
---

# Test
""")
        hook_sh = hook_dir / "hook.sh"
        hook_sh.write_text("#!/bin/bash\nexit 0\n")

        is_valid, errors = HookValidator.validate_hook_directory(hook_dir)
        assert is_valid is True


class TestHookUtils:
    """Tests for hook utility functions."""

    def test_find_hook_directories(self, mock_hooks_dir):
        """Test finding hook directories."""
        from knowhow.utils import find_hook_directories

        hooks = find_hook_directories(mock_hooks_dir)
        assert len(hooks) == 1
        assert hooks[0].name == "test-hook"

    def test_find_hook_directories_empty(self, temp_dir):
        """Test finding hooks in empty directory."""
        from knowhow.utils import find_hook_directories

        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        hooks = find_hook_directories(empty_dir)
        assert len(hooks) == 0

    def test_find_hook_directories_nested(self, temp_dir):
        """Test finding nested hook directories."""
        from knowhow.utils import find_hook_directories

        hooks_dir = temp_dir / "hooks"
        hooks_dir.mkdir()

        # Create nested hook
        nested = hooks_dir / "category" / "nested-hook"
        nested.mkdir(parents=True)
        hook_md = nested / "HOOK.md"
        hook_md.write_text("---\nname: nested-hook\ndescription: test\nevent: Stop\n---\n# Test\n")

        hooks = find_hook_directories(hooks_dir)
        assert len(hooks) == 1
        assert hooks[0].name == "nested-hook"
