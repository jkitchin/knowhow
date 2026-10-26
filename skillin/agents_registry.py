"""Agent install targets for skills (paths match `npx skills`, src/agents.ts).

"Universal" agents read project skills from `.agents/skills`, which is also the
canonical install location, so they need no extra symlink.

Platforms defined under `platforms:` in config.yaml extend this table (see
build_registry): new names become extra targets, and changed `skills_dir` /
`project_skills_dir` values override a built-in agent's paths.
"""

import os
from dataclasses import dataclass, replace
from pathlib import Path

CANONICAL_PROJECT_DIR = ".agents/skills"


def _home() -> Path:
    return Path.home()


def _xdg_config() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or _home() / ".config")


def _claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", "").strip() or _home() / ".claude")


def _codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", "").strip() or _home() / ".codex")


@dataclass(frozen=True)
class AgentTarget:
    name: str
    display_name: str
    project_dir: str | None  # relative to the project root; None = no project installs
    _global_dir: object  # callable returning the global skills dir (or None)
    _detect: object  # callable returning the path whose existence means "installed"
    copy_only: bool = False  # install real copies, never symlinks (custom platforms)

    @property
    def global_dir(self) -> Path | None:
        return self._global_dir()

    @property
    def is_universal(self) -> bool:
        return self.project_dir == CANONICAL_PROJECT_DIR

    def detected(self) -> bool:
        return self._detect().exists()


AGENTS: dict[str, AgentTarget] = {
    a.name: a
    for a in [
        AgentTarget(
            "claude-code",
            "Claude Code",
            ".claude/skills",
            lambda: _claude_home() / "skills",
            _claude_home,
        ),
        AgentTarget(
            "codex",
            "Codex",
            CANONICAL_PROJECT_DIR,
            lambda: _home() / ".agents" / "skills",
            _codex_home,
        ),
        AgentTarget(
            "opencode",
            "OpenCode",
            CANONICAL_PROJECT_DIR,
            lambda: _xdg_config() / "opencode" / "skills",
            lambda: _xdg_config() / "opencode",
        ),
        AgentTarget(
            "gemini-cli",
            "Gemini CLI",
            CANONICAL_PROJECT_DIR,
            lambda: _home() / ".gemini" / "skills",
            lambda: _home() / ".gemini",
        ),
        AgentTarget(
            "cursor",
            "Cursor",
            CANONICAL_PROJECT_DIR,
            lambda: _home() / ".cursor" / "skills",
            lambda: _home() / ".cursor",
        ),
        AgentTarget(
            "github-copilot",
            "GitHub Copilot",
            CANONICAL_PROJECT_DIR,
            lambda: _home() / ".copilot" / "skills",
            lambda: _home() / ".copilot",
        ),
        AgentTarget(
            "goose",
            "Goose",
            ".goose/skills",
            lambda: _xdg_config() / "goose" / "skills",
            lambda: _xdg_config() / "goose",
        ),
        AgentTarget(
            "windsurf",
            "Windsurf",
            ".windsurf/skills",
            lambda: _home() / ".codeium" / "windsurf" / "skills",
            lambda: _home() / ".codeium" / "windsurf",
        ),
    ]
}

# skillin --platform names -> agent names
PLATFORM_ALIASES = {"claude": "claude-code", "gemini": "gemini-cli"}


def _expand(path) -> Path:
    return Path(os.path.expanduser(str(path)))


def build_registry(config=None) -> dict[str, AgentTarget]:
    """
    Built-in agents plus platforms from config.

    A configured platform with a new name becomes a copy-only target installing to
    its `skills_dir` (global) and `project_skills_dir` (project). For built-in
    platforms (claude, codex, ...), only values that differ from the defaults
    override the agent's paths, so the npx-compatible locations stay the default.
    """
    registry = dict(AGENTS)
    if config is None:
        return registry
    overrides = config.platform_overrides()
    for platform in sorted(config.known_platforms()):
        name = PLATFORM_ALIASES.get(platform, platform)
        if name in AGENTS:
            changed = overrides.get(platform, {})
            updates = {}
            if changed.get("skills_dir"):
                updates["_global_dir"] = lambda p=changed["skills_dir"]: _expand(p)
            if changed.get("project_skills_dir"):
                updates["project_dir"] = str(changed["project_skills_dir"])
            if updates:
                registry[name] = replace(AGENTS[name], **updates)
            continue
        block = config.platform_settings(platform)
        global_dir, project_dir = block.get("skills_dir"), block.get("project_skills_dir")
        if not global_dir and not project_dir:
            continue
        registry[name] = AgentTarget(
            name,
            str(block.get("display_name") or name),
            str(project_dir) if project_dir else None,
            (lambda p=global_dir: _expand(p)) if global_dir else (lambda: None),
            lambda: Path("/nonexistent-skillin-platform"),  # never auto-detected
            copy_only=True,
        )
    return registry


def resolve_agent_names(names, registry: dict[str, AgentTarget] | None = None) -> list[str]:
    """Expand '*' and platform aliases; raise ValueError on unknown names."""
    registry = registry or AGENTS
    if not names:
        return []
    if "*" in names:
        return list(registry)
    result = []
    for n in names:
        n = PLATFORM_ALIASES.get(n.lower(), n.lower())
        if n not in registry:
            raise ValueError(f"Unknown agent '{n}'. Known agents: {', '.join(registry)}")
        if n not in result:
            result.append(n)
    return result


def detect_agents() -> list[str]:
    """Names of agents that appear to be installed; defaults to claude-code."""
    found = [name for name, agent in AGENTS.items() if agent.detected()]
    return found or ["claude-code"]


def default_agents(config=None, registry: dict[str, AgentTarget] | None = None) -> list[str]:
    """`default_platform` from config if the user set one, else detected agents."""
    if config is not None:
        platform = config.explicit_default_platform()
        if platform:
            return resolve_agent_names([platform], registry or build_registry(config))
    return detect_agents()


def canonical_dir(global_: bool, cwd: Path | None = None) -> Path:
    """The canonical skills directory (`.agents/skills` or `~/.agents/skills`)."""
    if global_:
        return _home() / ".agents" / "skills"
    return (cwd or Path.cwd()) / CANONICAL_PROJECT_DIR


def agent_skills_dir(
    agent: str,
    global_: bool,
    cwd: Path | None = None,
    registry: dict[str, AgentTarget] | None = None,
) -> Path:
    from skillin.config import PlatformConfigError

    a = (registry or AGENTS)[agent]
    if global_:
        if a.global_dir is None:
            raise PlatformConfigError(
                f"Platform '{agent}' has no skills_dir for global installs. "
                f"Set platforms.{agent}.skills_dir in config.yaml"
            )
        return a.global_dir
    if a.project_dir is None:
        raise PlatformConfigError(
            f"Platform '{agent}' has no project_skills_dir for project installs. "
            f"Set platforms.{agent}.project_skills_dir in config.yaml, or use -g"
        )
    return (cwd or Path.cwd()) / a.project_dir
