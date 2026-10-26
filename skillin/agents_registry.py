"""Agent install targets for skills (paths match `npx skills`, src/agents.ts).

"Universal" agents read project skills from `.agents/skills`, which is also the
canonical install location, so they need no extra symlink.
"""

import os
from dataclasses import dataclass
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
    project_dir: str  # relative to the project root
    _global_dir: object  # callable returning the global skills dir
    _detect: object  # callable returning the path whose existence means "installed"

    @property
    def global_dir(self) -> Path:
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


def resolve_agent_names(names: tuple[str, ...] | list[str]) -> list[str]:
    """Expand '*' and platform aliases; raise ValueError on unknown names."""
    if not names:
        return []
    if "*" in names:
        return list(AGENTS)
    result = []
    for n in names:
        n = PLATFORM_ALIASES.get(n.lower(), n.lower())
        if n not in AGENTS:
            raise ValueError(f"Unknown agent '{n}'. Known agents: {', '.join(AGENTS)}")
        if n not in result:
            result.append(n)
    return result


def detect_agents() -> list[str]:
    """Names of agents that appear to be installed; defaults to claude-code."""
    found = [name for name, agent in AGENTS.items() if agent.detected()]
    return found or ["claude-code"]


def canonical_dir(global_: bool, cwd: Path | None = None) -> Path:
    """The canonical skills directory (`.agents/skills` or `~/.agents/skills`)."""
    if global_:
        return _home() / ".agents" / "skills"
    return (cwd or Path.cwd()) / CANONICAL_PROJECT_DIR


def agent_skills_dir(agent: str, global_: bool, cwd: Path | None = None) -> Path:
    a = AGENTS[agent]
    return a.global_dir if global_ else (cwd or Path.cwd()) / a.project_dir
