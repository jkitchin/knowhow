"""Tests for the stats command."""

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from skillpack.commands.stats import (
    _load_usage_log,
    log_skill_usage,
    stats,
)


@pytest.fixture
def mock_usage_log(temp_dir):
    """Create a temporary usage log."""
    log_file = temp_dir / "usage.jsonl"
    entries = [
        {
            "timestamp": "2024-01-01T00:00:00",
            "skill": "python-jax",
            "triggered": True,
            "source": "manual",
        },
        {
            "timestamp": "2024-01-02T00:00:00",
            "skill": "python-jax",
            "triggered": True,
            "source": "scan",
        },
        {
            "timestamp": "2024-01-03T00:00:00",
            "skill": "scientific-writing",
            "triggered": True,
            "source": "manual",
        },
    ]
    with open(log_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    return log_file


class TestLogSkillUsage:
    def test_creates_log_entry(self, temp_dir):
        log_file = temp_dir / "test_usage.jsonl"
        with (
            patch("skillpack.commands.stats.USAGE_LOG", log_file),
            patch("skillpack.commands.stats.STATS_DIR", temp_dir),
        ):
            log_skill_usage("test-skill", triggered=True, source="test")

        entries = []
        with open(log_file) as f:
            for line in f:
                entries.append(json.loads(line))

        assert len(entries) == 1
        assert entries[0]["skill"] == "test-skill"
        assert entries[0]["triggered"] is True
        assert entries[0]["source"] == "test"


class TestLoadUsageLog:
    def test_loads_entries(self, mock_usage_log):
        with patch("skillpack.commands.stats.USAGE_LOG", mock_usage_log):
            entries = _load_usage_log()
        assert len(entries) == 3
        assert entries[0]["skill"] == "python-jax"

    def test_handles_missing_file(self, temp_dir):
        with patch("skillpack.commands.stats.USAGE_LOG", temp_dir / "nonexistent.jsonl"):
            entries = _load_usage_log()
        assert entries == []

    def test_handles_malformed_json(self, temp_dir):
        log_file = temp_dir / "bad.jsonl"
        log_file.write_text("not json\n{}\n")
        with patch("skillpack.commands.stats.USAGE_LOG", log_file):
            entries = _load_usage_log()
        # Should skip bad lines but not crash
        assert isinstance(entries, list)


class TestStatsCommand:
    def test_no_repo_configured(self):
        runner = CliRunner()
        with patch("skillpack.commands.stats.Config") as mock_config:
            mock_config.return_value.get_repository_path.return_value = None
            result = runner.invoke(stats, [])
        assert "no skills found" in result.output.lower() or "not set" in result.output.lower()

    def test_log_skill(self, temp_dir):
        runner = CliRunner()
        log_file = temp_dir / "usage.jsonl"
        with (
            patch("skillpack.commands.stats.USAGE_LOG", log_file),
            patch("skillpack.commands.stats.STATS_DIR", temp_dir),
        ):
            result = runner.invoke(stats, ["--log", "test-skill"])
        assert result.exit_code == 0
        assert "Logged" in result.output

    def test_reset_stats(self, temp_dir):
        runner = CliRunner()
        log_file = temp_dir / "usage.jsonl"
        log_file.write_text("{}\n")
        with (
            patch("skillpack.commands.stats.USAGE_LOG", log_file),
            patch("skillpack.commands.stats.STATS_DIR", temp_dir),
        ):
            result = runner.invoke(stats, ["--reset"], input="y\n")
        assert result.exit_code == 0
        assert not log_file.exists()
