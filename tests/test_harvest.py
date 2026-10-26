"""Tests for the harvest command."""

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from knowhow.commands.harvest import (
    _find_transcripts,
    _read_transcript,
    harvest,
)


@pytest.fixture
def transcript_file(temp_dir):
    """Create a mock transcript file."""
    t_file = temp_dir / "session.jsonl"
    entries = [
        {"role": "user", "content": "Help me write a Python script for data analysis"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I'll create a data analysis script using pandas."}
            ],
        },
        {"role": "user", "content": "Now add visualization with matplotlib"},
        {"role": "assistant", "content": "Here's the visualization code..."},
    ]
    with open(t_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    return t_file


class TestFindTranscripts:
    def test_returns_empty_for_nonexistent_dir(self, temp_dir):
        result = _find_transcripts(temp_dir / "nonexistent")
        assert result == []

    def test_finds_jsonl_files(self, temp_dir):
        (temp_dir / "session1.jsonl").write_text("{}\n")
        (temp_dir / "session2.jsonl").write_text("{}\n")
        result = _find_transcripts(temp_dir)
        assert len(result) == 2

    def test_ignores_non_jsonl(self, temp_dir):
        (temp_dir / "readme.md").write_text("# Hello\n")
        (temp_dir / "session.jsonl").write_text("{}\n")
        result = _find_transcripts(temp_dir)
        assert len(result) == 1


class TestReadTranscript:
    def test_reads_user_messages(self, transcript_file):
        result = _read_transcript(transcript_file)
        assert "[user]:" in result
        assert "data analysis" in result

    def test_reads_assistant_text_blocks(self, transcript_file):
        result = _read_transcript(transcript_file)
        assert "[assistant]:" in result
        assert "pandas" in result

    def test_handles_missing_file(self, temp_dir):
        result = _read_transcript(temp_dir / "nonexistent.jsonl")
        assert result == ""

    def test_respects_max_lines(self, transcript_file):
        result = _read_transcript(transcript_file, max_lines=1)
        # Should only read first line
        lines = [line for line in result.split("\n") if line.strip()]
        assert len(lines) <= 1

    def test_handles_malformed_json(self, temp_dir):
        bad_file = temp_dir / "bad.jsonl"
        bad_file.write_text("not json\n{}\n")
        result = _read_transcript(bad_file)
        # Should not crash
        assert isinstance(result, str)


class TestHarvestCommand:
    def test_no_transcripts_found(self, temp_dir):
        runner = CliRunner()
        with patch("knowhow.commands.harvest._find_transcripts", return_value=[]):
            result = runner.invoke(harvest, [])
        assert result.exit_code != 0

    def test_with_specific_transcript(self, transcript_file):
        runner = CliRunner()
        mock_proposals = "## Skill 1: data-pipeline\n**Name:** data-pipeline\n"
        with patch("knowhow.commands.harvest._run_claude_cli", return_value=mock_proposals):
            result = runner.invoke(harvest, ["-t", str(transcript_file)])
        assert result.exit_code == 0
        assert "data-pipeline" in result.output

    def test_no_skills_found(self, transcript_file):
        runner = CliRunner()
        with patch(
            "knowhow.commands.harvest._run_claude_cli",
            return_value="No reusable skills identified in this session.",
        ):
            result = runner.invoke(harvest, ["-t", str(transcript_file)])
        assert result.exit_code == 0

    def test_dry_run(self, transcript_file):
        runner = CliRunner()
        mock_proposals = "## Skill 1: test-skill\n"
        with patch("knowhow.commands.harvest._run_claude_cli", return_value=mock_proposals):
            result = runner.invoke(harvest, ["-t", str(transcript_file), "--generate", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.output
