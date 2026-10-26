"""Tests for config module."""

from pathlib import Path

import yaml

from skillin.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_default_config(self, temp_dir, monkeypatch):
        """Test that default config is loaded when no file exists."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)

        assert config.config["personal_skills_dir"] == "~/.claude/skills"
        assert config.config["default_target"] == "personal"
        assert config.config["default_platform"] == "claude"
        assert "claude" in config.config["platforms"]
        assert "opencode" in config.config["platforms"]

    def test_load_existing_config(self, temp_dir):
        """Test loading an existing config file."""
        config_path = temp_dir / "config.yaml"
        user_config = {
            "personal_skills_dir": "~/custom/skills",
            "repository_path": "/custom/repo",
            "default_target": "project",
        }

        with open(config_path, "w") as f:
            yaml.safe_dump(user_config, f)

        config = Config(config_path)
        assert config.config["personal_skills_dir"] == "~/custom/skills"
        assert config.config["repository_path"] == "/custom/repo"
        assert config.config["default_target"] == "project"

    def test_save_config(self, temp_dir):
        """Test saving config to file."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)
        config.config["repository_path"] = "/new/repo/path"
        config.save_config()

        # Load and verify
        with open(config_path) as f:
            saved_config = yaml.safe_load(f)
        assert saved_config["repository_path"] == "/new/repo/path"

    def test_get_skills_dir_personal(self, temp_dir, monkeypatch):
        """Test getting personal skills directory."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)

        # Mock home directory
        monkeypatch.setenv("HOME", str(temp_dir))
        # Test Claude Code (default platform)
        skills_dir = config.get_skills_dir("personal", "claude")
        assert ".claude/skills" in str(skills_dir)

        # Test OpenCode platform
        opencode_skills_dir = config.get_skills_dir("personal", "opencode")
        assert "opencode/skills" in str(opencode_skills_dir)

    def test_get_skills_dir_project(self, temp_dir):
        """Test getting project skills directory."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)

        # Default platform uses .claude
        skills_dir = config.get_skills_dir("project", "claude")
        assert skills_dir == Path(".claude/skills")

    def test_get_commands_dir_personal(self, temp_dir, monkeypatch):
        """Test getting personal commands directory."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)

        monkeypatch.setenv("HOME", str(temp_dir))
        # Test Claude Code (default platform)
        commands_dir = config.get_commands_dir("personal", "claude")
        assert ".claude/commands" in str(commands_dir)

        # Test OpenCode platform
        opencode_commands_dir = config.get_commands_dir("personal", "opencode")
        assert "opencode/command" in str(opencode_commands_dir)

    def test_get_repository_path(self, temp_dir):
        """Test getting repository path."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)

        # Initially None
        assert config.get_repository_path() is None

        # Set and verify
        repo_path = temp_dir / "my-repo"
        config.set_repository_path(repo_path)
        assert config.get_repository_path() == repo_path

    def test_set_repository_path(self, temp_dir):
        """Test setting repository path."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)

        repo_path = temp_dir / "repo"
        config.set_repository_path(repo_path)

        assert config.config["repository_path"] == str(repo_path)
        assert config_path.exists()

    def test_platform_specific_dirs(self, temp_dir):
        """Test getting platform-specific directories."""
        config_path = temp_dir / "config.yaml"
        config = Config(config_path)

        claude_skills = config.get_skills_dir("personal", "claude")
        codex_skills = config.get_skills_dir("personal", "codex")

        assert ".claude/skills" in str(claude_skills)
        assert ".codex/skills" in str(codex_skills)
