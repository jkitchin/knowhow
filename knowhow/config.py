"""Configuration management for knowhow."""

import copy
import os
import re
from pathlib import Path

import click
import yaml

# Built-in platforms. More can be defined under `platforms:` in config.yaml.
VALID_PLATFORMS = {"claude", "opencode", "codex", "gemini"}
PLATFORM_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class InvalidPlatformError(click.ClickException):
    """Raised when an unknown or malformed platform name is given."""


class PlatformConfigError(click.ClickException):
    """Raised when a platform lacks a directory needed for an operation."""


def validate_platform(platform: str, extra: set[str] | frozenset[str] = frozenset()) -> str:
    """
    Validate a platform name against the built-in platforms plus `extra`.

    Names are only ever used as keys into the config, never as paths, but they
    are still restricted to lowercase letters, digits and hyphens.

    Args:
        platform: The platform name to validate
        extra: Additional allowed names (platforms defined in config.yaml)

    Returns:
        The validated platform name (lowercase)

    Raises:
        InvalidPlatformError: If the name is malformed or unknown
    """
    platform_lower = (platform or "").lower()
    allowed = VALID_PLATFORMS | set(extra)
    if not PLATFORM_NAME_RE.match(platform_lower) or platform_lower not in allowed:
        raise InvalidPlatformError(
            f"Invalid platform '{platform}'. Must be one of: {', '.join(sorted(allowed))}. "
            "Define new platforms under `platforms:` in ~/.config/skillz/config.yaml"
        )
    return platform_lower


class Config:
    """Configuration manager for knowhow."""

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
        "aliases": {},  # Short names for `knowhow add`, e.g. {"kitchin": "jkitchin/knowhow"}
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
                config = self._deep_merge(copy.deepcopy(self.DEFAULT_CONFIG), user_config)
                return config
        return copy.deepcopy(self.DEFAULT_CONFIG)

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

    def known_platforms(self) -> set[str]:
        """Built-in platforms plus valid names defined under `platforms:`."""
        configured = {str(k).lower() for k in (self.config.get("platforms") or {})}
        return VALID_PLATFORMS | {p for p in configured if PLATFORM_NAME_RE.match(p)}

    def resolve_platform(self, platform: str | None = None) -> str:
        """The platform to use: `platform`, else `default_platform`, else claude."""
        name = platform or self.config.get("default_platform") or "claude"
        return validate_platform(name, self.known_platforms())

    def explicit_default_platform(self) -> str | None:
        """`default_platform` if the user changed it from the built-in default."""
        name = self.config.get("default_platform")
        if not name or name == self.DEFAULT_CONFIG["default_platform"]:
            return None
        return self.resolve_platform(name)

    def platform_settings(self, platform: str) -> dict:
        """The config block for a platform (empty if it has none)."""
        platforms = {str(k).lower(): v for k, v in (self.config.get("platforms") or {}).items()}
        block = platforms.get(platform.lower())
        return block if isinstance(block, dict) else {}

    def platform_overrides(self) -> dict[str, dict]:
        """
        Platform settings that differ from the built-in defaults, by platform name.

        save_config() writes the full merged config, so values equal to the
        defaults are not treated as user choices.
        """
        defaults = self.DEFAULT_CONFIG["platforms"]
        result = {}
        for name in self.known_platforms():
            block = self.platform_settings(name)
            changed = {k: v for k, v in block.items() if defaults.get(name, {}).get(k) != v}
            if changed:
                result[name] = changed
        return result

    def _platform_path(self, kind: str, target: str, platform: str | None) -> Path:
        """
        Resolve a directory (or file) for a platform.

        kind is "skills", "commands", "hooks" or "agents" (looked up as
        `<kind>_dir` / `project_<kind>_dir`), or "settings" (`settings_file` /
        `project_settings_file`). Built-in platforms fall back to the global
        `personal_*` / `project_*` settings (the Claude Code layout); configured
        platforms must define what they use.
        """
        name = self.resolve_platform(platform)
        block = self.platform_settings(name)
        suffix = "file" if kind == "settings" else "dir"
        key = f"{kind}_{suffix}" if target == "personal" else f"project_{kind}_{suffix}"
        path = block.get(key)
        if not path and name in VALID_PLATFORMS:
            if kind == "settings":
                path = (
                    "~/.claude/settings.json" if target == "personal" else ".claude/settings.json"
                )
            else:
                path = self.config.get(
                    f"{'personal' if target == 'personal' else 'project'}_{kind}_dir"
                )
        if not path:
            raise PlatformConfigError(
                f"Platform '{name}' has no {key}. Set platforms.{name}.{key} in {self.config_path}"
            )
        return Path(os.path.expanduser(str(path)))

    def get_skills_dir(self, target: str = "personal", platform: str | None = None) -> Path:
        """Get the skills directory for a given target and platform."""
        return self._platform_path("skills", target, platform)

    def get_commands_dir(self, target: str = "personal", platform: str | None = None) -> Path:
        """Get the commands directory for a given target and platform."""
        return self._platform_path("commands", target, platform)

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

    def get_aliases(self) -> dict[str, str]:
        """Get source aliases used by `knowhow add`."""
        aliases = self.config.get("aliases") or {}
        return {str(k): str(v) for k, v in aliases.items()}

    def set_alias(self, name: str, source: str) -> None:
        """Set a source alias."""
        self.config.setdefault("aliases", {})[name] = source
        self.save_config()

    def get_hooks_dir(self, target: str = "personal", platform: str | None = None) -> Path:
        """Get the hooks directory for a given target and platform."""
        return self._platform_path("hooks", target, platform)

    def get_settings_file(self, target: str = "personal", platform: str | None = None) -> Path:
        """Get the settings.json file path for a given target and platform."""
        return self._platform_path("settings", target, platform)

    def get_agents_dir(self, target: str = "personal", platform: str | None = None) -> Path:
        """Get the agents directory for a given target and platform."""
        return self._platform_path("agents", target, platform)


def _resolve_platform_option(ctx, param, value):
    return Config().resolve_platform(value)


def platform_option(help_text: str = "Target platform"):
    """`--platform/-p` option: defaults to `default_platform`, validated against config."""
    return click.option(
        "--platform",
        "-p",
        default=None,
        callback=_resolve_platform_option,
        help=f"{help_text} (default: `default_platform` from config, else claude)",
    )
