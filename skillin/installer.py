"""Install discovered skills into agent skill directories.

Default (symlink) mode copies the skill once into the canonical directory
(`.agents/skills/<name>` or `~/.agents/skills/<name>`) and links each agent's
skills directory to it. Copy mode writes an independent copy per agent.
"""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from skillin.agents_registry import AGENTS, agent_skills_dir, canonical_dir
from skillin.discovery import DiscoveredSkill, install_dir_name

EXCLUDE_NAMES = {".git", "__pycache__", "__pypackages__", "metadata.json", ".DS_Store"}


@dataclass
class InstallResult:
    name: str
    canonical: Path | None
    linked: list[Path] = field(default_factory=list)
    copied: list[Path] = field(default_factory=list)
    skipped_agents: list[str] = field(default_factory=list)


def copy_skill_tree(src: Path, dst: Path, boundary: Path) -> None:
    """
    Copy a skill directory, replacing dst.

    Symlinks are dereferenced only if they resolve inside `boundary` (the source
    checkout); others are skipped so a skill cannot pull in files from elsewhere
    on the machine.
    """
    boundary = boundary.resolve()

    def inside(p: Path) -> bool:
        try:
            p.resolve().relative_to(boundary)
            return True
        except (ValueError, OSError):
            return False

    def ignore(directory, names):
        skipped = set()
        for n in names:
            p = Path(directory) / n
            if n in EXCLUDE_NAMES or (p.is_symlink() and not inside(p)):
                skipped.add(n)
        return skipped

    remove_path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, symlinks=False, ignore=ignore, ignore_dangling_symlinks=True)


def remove_path(p: Path) -> None:
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p)


def _link(target: Path, link: Path) -> bool:
    """Create a relative symlink link -> target. Returns False on failure."""
    try:
        remove_path(link)
        link.parent.mkdir(parents=True, exist_ok=True)
        rel = os.path.relpath(target, link.parent.resolve())
        link.symlink_to(rel, target_is_directory=True)
        return True
    except OSError:
        return False


def _skip_project_agent(agent: str, cwd: Path, registry=None) -> bool:
    """Skip non-universal agents whose config dir is absent from the project (npx rule)."""
    a = (registry or AGENTS)[agent]
    if a.is_universal or agent == "claude-code" or a.copy_only:
        return False  # configured platforms were chosen explicitly
    return not (cwd / a.project_dir.split("/")[0]).exists()


def planned_paths(
    skill: DiscoveredSkill,
    agents: list[str],
    global_: bool,
    copy: bool,
    cwd: Path,
    registry=None,
) -> tuple[Path | None, list[Path], set[Path]]:
    """
    Return (canonical path or None, per-agent paths, paths to copy rather than link)
    without touching disk.
    """
    registry = registry or AGENTS
    dirname = install_dir_name(skill.name)
    # Only symlink agents need the canonical copy
    if all(registry[a].copy_only for a in agents):
        copy = True
    # install_dir_name() strips separators and leading dots, so plain joins are safe
    canon = None if copy else canonical_dir(global_, cwd) / dirname
    targets, copy_paths = [], set()
    for agent in agents:
        a = registry[agent]
        if a.is_universal and not copy:
            continue  # served by the canonical dir (project or global)
        if not global_ and _skip_project_agent(agent, cwd, registry):
            continue
        base = canonical_dir(global_, cwd) if a.is_universal and global_ else None
        base = base or agent_skills_dir(agent, global_, cwd, registry)
        path = base / dirname
        if a.copy_only or copy:
            copy_paths.add(path)
        if path not in targets:
            targets.append(path)
    return canon, targets, copy_paths


def install_skill(
    skill: DiscoveredSkill,
    agents: list[str],
    source_root: Path,
    global_: bool = False,
    copy: bool = False,
    cwd: Path | None = None,
    registry=None,
) -> InstallResult:
    """Install one skill for the given agents."""
    cwd = cwd or Path.cwd()
    canon, targets, copy_paths = planned_paths(skill, agents, global_, copy, cwd, registry)
    result = InstallResult(name=skill.name, canonical=canon)
    result.skipped_agents = [
        a for a in agents if not global_ and _skip_project_agent(a, cwd, registry)
    ]

    if canon is not None:
        copy_skill_tree(skill.path, canon, source_root)

    for path in targets:
        if canon is not None and path not in copy_paths and _link(canon, path):
            result.linked.append(path)
        else:
            copy_skill_tree(skill.path, path, source_root)
            result.copied.append(path)
    return result


def _agent_bases(global_: bool, cwd: Path, registry) -> list[Path]:
    """Skills dirs of every agent in the registry that has one for this scope."""
    bases = []
    for agent, a in registry.items():
        if (global_ and a.global_dir is None) or (not global_ and a.project_dir is None):
            continue
        bases.append(agent_skills_dir(agent, global_, cwd, registry))
    return bases


def find_installed(name: str, global_: bool, cwd: Path | None = None, registry=None) -> list[Path]:
    """All places a skill directory/symlink named `name` exists for known agents."""
    cwd = cwd or Path.cwd()
    registry = registry or AGENTS
    dirname = install_dir_name(name)
    bases = [canonical_dir(global_, cwd)] + _agent_bases(global_, cwd, registry)
    found = []
    for base in bases:
        p = base / dirname
        if (p.is_symlink() or (p / "SKILL.md").is_file()) and p not in found:
            found.append(p)
    return found


def uninstall_skill(
    name: str,
    global_: bool,
    agents: list[str] | None = None,
    cwd: Path | None = None,
    registry=None,
) -> list[Path]:
    """
    Remove a skill. With `agents`, only those agents' entries are removed (and the
    canonical copy is kept unless every agent was selected). Returns removed paths.
    """
    cwd = cwd or Path.cwd()
    registry = registry or AGENTS
    dirname = install_dir_name(name)
    if agents:
        bases = [
            agent_skills_dir(a, global_, cwd, registry)
            for a in agents
            if not registry[a].is_universal
        ]
        if set(agents) >= set(AGENTS):
            bases.append(canonical_dir(global_, cwd))
        paths = [b / dirname for b in bases if (b / dirname).is_symlink() or (b / dirname).exists()]
    else:
        paths = find_installed(name, global_, cwd, registry)
    for p in paths:
        remove_path(p)
    return paths
