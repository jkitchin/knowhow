"""Configuration management for skillz."""

import os
from pathlib import Path

import yaml

# Hardcoded whitelist of valid platforms for security
VALID_PLATFORMS = {"claude", "opencode", "codex", "gemini"}


class InvalidPlatformError(Exception):
    """Raised when an invalid platform is specified."""

    pass


def validate_platform(platform: str) -> str:
    """
    Validate that a platform is in the allowed whitelist.

    Args:
        platform: The platform name to validate

    Returns:
        The validated platform name (lowercase)

    Raises:
        InvalidPlatformError: If the platform is not in the whitelist
    """
    platform_lower = platform.lower()
    if platform_lower not in VALID_PLATFORMS:
        raise InvalidPlatformError(
            f"Invalid platform '{platform}'. Must be one of: {', '.join(sorted(VALID_PLATFORMS))}"
        )
    return platform_lower


class Config:
    """Configuration manager for skillz."""

    DEFAULT_CONFIG = {
        "personal_skills_dir": "~/.claude/skills",
        "personal_commands_dir": "~/.claude/commands",
        "personal_hooks_dir": "~/.claude/hooks",
        "personal_agents_dir": "~/.claude/agents",
        "project_skills_dir": ".claude/skills",
        "project_commands_dir": ".claude/commands",
        "project_hooks_dir": ".claude/hooks",
        "project_agents_dir": ".claude/agents",
        "repository_path": None,  # Path to the local clone of skills repository
        "default_target": "personal",  # personal or project
        "default_platform": "claude",  # Default platform: claude, opencode, codex, gemini
        "platforms": {
            "claude": {
                "skills_dir": "~/.claude/skills",
                "commands_dir": "~/.claude/commands",
                "hooks_dir": "~/.claude/hooks",
                "agents_dir": "~/.claude/agents",
                "settings_file": "~/.claude/settings.json",
            },
            "opencode": {
                "skills_dir": "~/.config/opencode/skills",
                "commands_dir": "~/.config/opencode/command",
                "hooks_dir": "~/.config/opencode/hooks",
                "agents_dir": "~/.config/opencode/agents",
                "settings_file": "~/.config/opencode/settings.json",
            },
            "codex": {
                "skills_dir": "~/.codex/skills",
                "commands_dir": "~/.codex/commands",
                "hooks_dir": "~/.codex/hooks",
                "agents_dir": "~/.codex/agents",
                "settings_file": "~/.codex/settings.json",
            },
            "gemini": {
                "skills_dir": "~/.config/gemini/skills",
                "commands_dir": "~/.config/gemini/commands",
                "hooks_dir": "~/.config/gemini/hooks",
                "agents_dir": "~/.config/gemini/agents",
                "settings_file": "~/.config/gemini/settings.json",
            },
        },
    }

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration."""
        self.config_path = config_path or self._default_config_path()
        self.config = self._load_config()

    @staticmethod
    def _default_config_path() -> Path:
        """Get the default configuration file path."""
        return Path.home() / ".config" / "skillz" / "config.yaml"

    def _load_config(self) -> dict:
        """Load configuration from file or use defaults."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                user_config = yaml.safe_load(f) or {}
                # Deep merge with defaults
                config = self._deep_merge(self.DEFAULT_CONFIG.copy(), user_config)
                return config
        return self.DEFAULT_CONFIG.copy()

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries, with override taking precedence."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)

    def get_skills_dir(self, target: str = "personal", platform: str = "claude") -> Path:
        """Get the skills directory for a given target and platform."""
        if target == "personal":
            if platform in self.config["platforms"]:
                path = self.config["platforms"][platform]["skills_dir"]
            else:
                path = self.config["personal_skills_dir"]
        else:  # project
            path = self.config["project_skills_dir"]

        return Path(os.path.expanduser(path))

    def get_commands_dir(self, target: str = "personal", platform: str = "claude") -> Path:
        """Get the commands directory for a given target and platform."""
        if target == "personal":
            if platform in self.config["platforms"]:
                path = self.config["platforms"][platform]["commands_dir"]
            else:
                path = self.config["personal_commands_dir"]
        else:  # project
            path = self.config["project_commands_dir"]

        return Path(os.path.expanduser(path))

    def get_repository_path(self) -> Path | None:
        """Get the repository path."""
        repo_path = self.config.get("repository_path")
        if repo_path:
            return Path(os.path.expanduser(repo_path))
        return None

    def set_repository_path(self, path: Path) -> None:
        """Set the repository path."""
        self.config["repository_path"] = str(path)
        self.save_config()

    def get_hooks_dir(self, target: str = "personal", platform: str = "claude") -> Path:
        """Get the hooks directory for a given target and platform."""
        if target == "personal":
            if platform in self.config["platforms"]:
                path = self.config["platforms"][platform].get(
                    "hooks_dir", self.config.get("personal_hooks_dir", "~/.claude/hooks")
                )
            else:
                path = self.config.get("personal_hooks_dir", "~/.claude/hooks")
        else:  # project
            path = self.config.get("project_hooks_dir", ".claude/hooks")

        return Path(os.path.expanduser(path))

    def get_settings_file(self, target: str = "personal", platform: str = "claude") -> Path:
        """Get the settings.json file path for a given target and platform."""
        if target == "personal":
            if platform in self.config["platforms"]:
                path = self.config["platforms"][platform].get(
                    "settings_file", "~/.claude/settings.json"
                )
            else:
                path = "~/.claude/settings.json"
        else:  # project
            path = ".claude/settings.json"

        return Path(os.path.expanduser(path))

    def get_agents_dir(self, target: str = "personal", platform: str = "claude") -> Path:
        """Get the agents directory for a given target and platform."""
        if target == "personal":
            if platform in self.config["platforms"]:
                path = self.config["platforms"][platform].get(
                    "agents_dir", self.config.get("personal_agents_dir", "~/.claude/agents")
                )
            else:
                path = self.config.get("personal_agents_dir", "~/.claude/agents")
        else:  # project
            path = self.config.get("project_agents_dir", ".claude/agents")

        return Path(os.path.expanduser(path))
