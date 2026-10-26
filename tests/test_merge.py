"""Tests for the merge command."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from knowhow.commands.merge import (
    _format_skills_for_analysis,
    _get_all_skills_summary,
    merge,
)

SKILL1_CONTENT = """---
name: skill-one
description: First test skill
allowed-tools: ["*"]
---

# Skill One

Content for skill one.
"""

SKILL2_CONTENT = """---
name: skill-two
description: Second test skill
allowed-tools: ["*"]
---

# Skill Two

Content for skill two.
"""


@pytest.fixture
def skill_repo(temp_dir):
    """Create a repository with two skills."""
    skills_dir = temp_dir / "skills" / "programming"
    skills_dir.mkdir(parents=True)

    s1 = skills_dir / "skill-one"
    s1.mkdir()
    (s1 / "SKILL.md").write_text(SKILL1_CONTENT)

    s2 = skills_dir / "skill-two"
    s2.mkdir()
    (s2 / "SKILL.md").write_text(SKILL2_CONTENT)

    return temp_dir


class TestGetAllSkillsSummary:
    def test_returns_summaries(self, skill_repo):
        config = MagicMock()
        config.get_repository_path.return_value = skill_repo
        summaries = _get_all_skills_summary(config)
        assert len(summaries) == 2
        names = {s["name"] for s in summaries}
        assert "skill-one" in names
        assert "skill-two" in names

    def test_returns_empty_for_no_repo(self):
        config = MagicMock()
        config.get_repository_path.return_value = None
        summaries = _get_all_skills_summary(config)
        assert summaries == []


class TestFormatSkillsForAnalysis:
    def test_formats_skills(self):
        summaries = [
            {"name": "test", "description": "A test skill", "category": "dev"},
        ]
        result = _format_skills_for_analysis(summaries)
        assert "**test**" in result
        assert "A test skill" in result


class TestMergeCommand:
    def test_detect_overlaps(self, skill_repo):
        runner = CliRunner()
        mock_analysis = "## Group 1: Testing\n**Skills:** skill-one, skill-two\n"
        with patch("knowhow.commands.merge.Config") as mock_config:
            mock_config.return_value.get_repository_path.return_value = skill_repo
            with patch("knowhow.commands.merge._run_claude_cli", return_value=mock_analysis):
                result = runner.invoke(merge, [])
        assert result.exit_code == 0
        assert "skill-one" in result.output

    def test_no_overlaps_found(self, skill_repo):
        runner = CliRunner()
        with patch("knowhow.commands.merge.Config") as mock_config:
            mock_config.return_value.get_repository_path.return_value = skill_repo
            with patch(
                "knowhow.commands.merge._run_claude_cli",
                return_value="No significant overlaps detected.",
            ):
                result = runner.invoke(merge, [])
        assert result.exit_code == 0
        assert "No significant overlaps" in result.output

    def test_dry_run(self, skill_repo):
        runner = CliRunner()
        mock_analysis = "## Group 1: Testing\n"
        with patch("knowhow.commands.merge.Config") as mock_config:
            mock_config.return_value.get_repository_path.return_value = skill_repo
            with patch("knowhow.commands.merge._run_claude_cli", return_value=mock_analysis):
                result = runner.invoke(merge, ["--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.output

    def test_execute_merge_skill_not_found(self, skill_repo):
        runner = CliRunner()
        with patch("knowhow.commands.merge.Config") as mock_config:
            mock_config.return_value.get_repository_path.return_value = skill_repo
            result = runner.invoke(merge, ["--execute", "nonexistent", "skill-one"])
        assert result.exit_code != 0
