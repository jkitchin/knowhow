"""Tests for the optimize command."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from knowhow.commands.optimize import (
    _find_skill_path,
    _read_skill_description,
    _run_claude_cli,
    _update_skill_description,
    optimize,
)

VALID_SKILL_CONTENT = """---
name: test-skill
description: A test skill for unit testing. Use when testing.
allowed-tools:
  - Read
  - Write
---

# Test Skill

This is a test skill used for unit testing.

## When to Use

Use this skill when running tests.

## Instructions

Follow the test instructions.
"""


@pytest.fixture
def skill_dir(temp_dir):
    """Create a skill directory with a valid SKILL.md."""
    d = temp_dir / "skills" / "test-skill"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(VALID_SKILL_CONTENT)
    return d


class TestRunClaudeCli:
    def test_returns_output_on_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="output text", stderr="")
            result = _run_claude_cli("test prompt")
        assert result == "output text"

    def test_returns_none_on_nonzero_exit(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            result = _run_claude_cli("test prompt")
        assert result is None

    def test_returns_none_when_claude_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = _run_claude_cli("test prompt")
        assert result is None

    def test_returns_none_on_timeout(self):
        import subprocess as sp

        with patch("subprocess.run", side_effect=sp.TimeoutExpired("claude", 120)):
            result = _run_claude_cli("test prompt")
        assert result is None


class TestReadSkillDescription:
    def test_reads_description(self, skill_dir):
        desc = _read_skill_description(skill_dir / "SKILL.md")
        assert desc is not None
        assert "test skill" in desc.lower()

    def test_returns_none_for_missing_file(self, temp_dir):
        result = _read_skill_description(temp_dir / "nonexistent.md")
        assert result is None

    def test_returns_none_for_no_frontmatter(self, temp_dir):
        f = temp_dir / "SKILL.md"
        f.write_text("# No frontmatter here\n")
        result = _read_skill_description(f)
        assert result is None


class TestUpdateSkillDescription:
    def test_updates_description(self, skill_dir):
        skill_md = skill_dir / "SKILL.md"
        success = _update_skill_description(skill_md, "New improved description.")
        assert success is True
        new_desc = _read_skill_description(skill_md)
        assert new_desc == "New improved description."

    def test_preserves_body_content(self, skill_dir):
        skill_md = skill_dir / "SKILL.md"
        _update_skill_description(skill_md, "Updated description.")
        content = skill_md.read_text()
        assert "## When to Use" in content
        assert "## Instructions" in content

    def test_returns_false_for_no_frontmatter(self, temp_dir):
        f = temp_dir / "SKILL.md"
        f.write_text("# No frontmatter\n")
        result = _update_skill_description(f, "New desc")
        assert result is False


class TestFindSkillPath:
    def test_finds_skill_in_repo(self, temp_dir):
        repo = temp_dir / "repo"
        skill_dir = repo / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")

        config = MagicMock()
        config.get_repository_path.return_value = repo
        config.get_skills_dir.return_value = temp_dir / "nonexistent"

        result = _find_skill_path("my-skill", config)
        assert result == skill_dir

    def test_returns_none_when_not_found(self, temp_dir):
        config = MagicMock()
        config.get_repository_path.return_value = temp_dir / "nonexistent"
        config.get_skills_dir.return_value = temp_dir / "nonexistent"

        result = _find_skill_path("no-such-skill", config)
        assert result is None

    def test_finds_skill_in_installed_dir(self, temp_dir):
        install_dir = temp_dir / "installed" / "skills" / "my-skill"
        install_dir.mkdir(parents=True)
        (install_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")

        config = MagicMock()
        config.get_repository_path.return_value = temp_dir / "nonexistent"
        config.get_skills_dir.return_value = install_dir.parent

        result = _find_skill_path("my-skill", config)
        assert result == install_dir


class TestOptimizeCommand:
    def test_skill_not_found(self, temp_dir):
        runner = CliRunner()
        with patch("knowhow.commands.optimize.Config") as mock_config:
            mock_config.return_value.get_repository_path.return_value = temp_dir / "nonexistent"
            mock_config.return_value.get_skills_dir.return_value = temp_dir / "nonexistent"
            result = runner.invoke(optimize, ["no-such-skill"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_evals_only_exits_after_evals(self, skill_dir):
        runner = CliRunner()
        mock_evals = "## Should-Trigger Queries\n1. test query\n"
        with patch("knowhow.commands.optimize._find_skill_path", return_value=skill_dir):
            with patch("knowhow.commands.optimize._run_claude_cli", return_value=mock_evals):
                result = runner.invoke(optimize, ["test-skill", "--evals-only"])
        assert result.exit_code == 0
        assert "test query" in result.output
        # Should not ask about saving
        assert "Save" not in result.output

    def test_dry_run_does_not_save(self, skill_dir):
        runner = CliRunner()
        mock_evals = "## Should-Trigger Queries\n1. query one\n"
        mock_desc = "Improved description text."
        with patch("knowhow.commands.optimize._find_skill_path", return_value=skill_dir):
            with patch(
                "knowhow.commands.optimize._run_claude_cli",
                side_effect=[mock_evals, mock_desc],
            ):
                result = runner.invoke(optimize, ["test-skill", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.output
        # Original description should be unchanged
        desc = _read_skill_description(skill_dir / "SKILL.md")
        assert "Improved description" not in desc

    def test_claude_cli_failure_aborts(self, skill_dir):
        runner = CliRunner()
        with patch("knowhow.commands.optimize._find_skill_path", return_value=skill_dir):
            with patch("knowhow.commands.optimize._run_claude_cli", return_value=None):
                result = runner.invoke(optimize, ["test-skill"])
        assert result.exit_code != 0

    def test_full_optimize_saves_description(self, skill_dir):
        runner = CliRunner()
        mock_evals = "## Should-Trigger Queries\n1. query\n"
        mock_desc = "Brand new optimized description."
        with patch("knowhow.commands.optimize._find_skill_path", return_value=skill_dir):
            with patch(
                "knowhow.commands.optimize._run_claude_cli",
                side_effect=[mock_evals, mock_desc],
            ):
                with patch("knowhow.commands.optimize.confirm_action", return_value=True):
                    result = runner.invoke(optimize, ["test-skill"])
        assert result.exit_code == 0
        assert "updated" in result.output
        desc = _read_skill_description(skill_dir / "SKILL.md")
        assert desc == "Brand new optimized description."

    def test_cancelled_by_user_does_not_save(self, skill_dir):
        runner = CliRunner()
        mock_evals = "## Should-Trigger Queries\n1. query\n"
        mock_desc = "Proposed description."
        with patch("knowhow.commands.optimize._find_skill_path", return_value=skill_dir):
            with patch(
                "knowhow.commands.optimize._run_claude_cli",
                side_effect=[mock_evals, mock_desc],
            ):
                with patch("knowhow.commands.optimize.confirm_action", return_value=False):
                    result = runner.invoke(optimize, ["test-skill"])
        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()
        desc = _read_skill_description(skill_dir / "SKILL.md")
        assert "Proposed" not in desc
