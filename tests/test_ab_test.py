"""Tests for the ab-test command."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from skillin.commands.ab_test import (
    _score_description,
    ab_test,
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
"""


@pytest.fixture
def skill_dir(temp_dir):
    """Create a skill directory with a valid SKILL.md."""
    d = temp_dir / "skills" / "test-skill"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(VALID_SKILL_CONTENT)
    return d


class TestScoreDescription:
    def test_parses_scores(self):
        mock_result = (
            "SHOULD_TRIGGER_CORRECT: 8/10\n"
            "SHOULD_NOT_TRIGGER_CORRECT: 5/5\n"
            "TOTAL_SCORE: 13/15\n"
            "WEAKNESSES: Missing edge cases"
        )
        with patch("skillin.commands.ab_test._run_claude_cli", return_value=mock_result):
            scores = _score_description("test", "desc", "evals")
        assert scores["trigger"] == "8/10"
        assert scores["no_trigger"] == "5/5"
        assert scores["total"] == "13/15"
        assert "edge cases" in scores["weaknesses"]

    def test_returns_none_on_failure(self):
        with patch("skillin.commands.ab_test._run_claude_cli", return_value=None):
            scores = _score_description("test", "desc", "evals")
        assert scores is None

    def test_returns_none_on_unparseable(self):
        with patch(
            "skillin.commands.ab_test._run_claude_cli", return_value="Random text with no scores"
        ):
            scores = _score_description("test", "desc", "evals")
        assert scores is None


class TestAbTestCommand:
    def test_skill_not_found(self, temp_dir):
        runner = CliRunner()
        with patch("skillin.commands.ab_test._find_skill_path", return_value=None):
            result = runner.invoke(ab_test, ["no-such-skill"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_evals_generation_failure(self, skill_dir):
        runner = CliRunner()
        with patch("skillin.commands.ab_test._find_skill_path", return_value=skill_dir):
            with patch("skillin.commands.ab_test._generate_evals", return_value=None):
                result = runner.invoke(ab_test, ["test-skill"])
        assert result.exit_code != 0

    def test_dry_run(self, skill_dir):
        runner = CliRunner()
        mock_evals = "## Should-Trigger\n1. test\n## Should-Not-Trigger\n1. other\n"
        mock_score = (
            "SHOULD_TRIGGER_CORRECT: 8/10\n"
            "SHOULD_NOT_TRIGGER_CORRECT: 5/5\n"
            "TOTAL_SCORE: 13/15\n"
            "WEAKNESSES: None"
        )
        mock_variant = "Improved description variant."

        def mock_claude(prompt, timeout=120):
            if "evaluation queries" in prompt.lower() or "eval" in prompt.lower():
                return mock_evals
            if "EMPHASIS" in prompt:
                return mock_variant
            return mock_score

        with patch("skillin.commands.ab_test._find_skill_path", return_value=skill_dir):
            with patch("skillin.commands.ab_test._generate_evals", return_value=mock_evals):
                with patch("skillin.commands.ab_test._run_claude_cli", side_effect=mock_claude):
                    result = runner.invoke(ab_test, ["test-skill", "--dry-run", "-n", "1"])
        assert result.exit_code == 0

    def test_current_wins(self, skill_dir):
        runner = CliRunner()
        mock_evals = "## Should-Trigger\n1. test\n"
        best_score = (
            "SHOULD_TRIGGER_CORRECT: 10/10\n"
            "SHOULD_NOT_TRIGGER_CORRECT: 5/5\n"
            "TOTAL_SCORE: 15/15\n"
            "WEAKNESSES: None"
        )
        worse_score = (
            "SHOULD_TRIGGER_CORRECT: 5/10\n"
            "SHOULD_NOT_TRIGGER_CORRECT: 3/5\n"
            "TOTAL_SCORE: 8/15\n"
            "WEAKNESSES: Many gaps"
        )
        call_count = [0]

        def mock_claude(prompt, timeout=120):
            call_count[0] += 1
            if "EMPHASIS" in prompt:
                return "Worse variant."
            # First score call is for current, second for variant
            if call_count[0] <= 2:
                return best_score
            return worse_score

        with patch("skillin.commands.ab_test._find_skill_path", return_value=skill_dir):
            with patch("skillin.commands.ab_test._generate_evals", return_value=mock_evals):
                with patch("skillin.commands.ab_test._run_claude_cli", side_effect=mock_claude):
                    result = runner.invoke(ab_test, ["test-skill", "-n", "1", "--dry-run"])
        assert result.exit_code == 0
