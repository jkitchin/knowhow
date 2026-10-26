"""Install discovered skills into agent skill directories.

Default (symlink) mode copies the skill once into the canonical directory
(`.agents/skills/<name>` or `~/.agents/skills/<name>`) and links each agent's
skills directory to it. Copy mode writes an independent copy per agent.
"""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from skillpack.agents_registry import AGENTS, agent_skills_dir, canonical_dir
from skillpack.discovery import DiscoveredSkill, install_dir_name

EXCLUDE_NAMES = {".git", "__pycache__", "__pypackages__", "metadata.json", ".DS_Store"}


@dataclass
class InstallResult:
    name: str
    canonical: Path | None
    linked: list[Path] = field(default_factory=list)
    copied: list[Path] = field(default_factory=list)
    skipped_agents: list[str] = field(default_factory=list)


def _inside(p: Path, boundary: Path) -> bool:
    try:
        Path(os.path.realpath(p)).relative_to(boundary)
        return True
    except ValueError:
        return False


def _copy_dir(src: Path, dst: Path, boundary: Path) -> None:
    """Copy src into a new directory dst (see copy_skill_tree for the rules)."""
    dst.mkdir()
    shutil.copystat(src, dst, follow_symlinks=False)
    for entry in sorted(os.scandir(src), key=lambda e: e.name):
        if entry.name in EXCLUDE_NAMES:
            continue
        path, out = Path(entry.path), dst / entry.name
        if entry.is_symlink():
            # A symlink resolves relative to its own directory. Copy the file it
            # points to if that is inside the source checkout; skip directory
            # symlinks (loops) and anything pointing elsewhere on the machine.
            real = Path(os.path.realpath(path))
            if _inside(real, boundary) and real.is_file():
                shutil.copy2(real, out)
        elif entry.is_dir(follow_symlinks=False):
            _copy_dir(path, out, boundary)
        elif entry.is_file(follow_symlinks=False):
            shutil.copy2(path, out)
        # sockets, FIFOs and devices are skipped


def copy_skill_tree(src: Path, dst: Path, boundary: Path) -> None:
    """
    Copy a skill directory, replacing dst.

    Files symlinked from inside `boundary` (the source checkout) are copied as
    real files; directory symlinks and symlinks pointing outside it are skipped,
    so a skill cannot pull in files from elsewhere on the machine. The copy is
    built next to dst and swapped in at the end, so a failure leaves the
    previous install untouched.
    """
    boundary = Path(os.path.realpath(boundary))
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.parent / f".{dst.name}.skillpack-tmp"
    remove_path(tmp)
    try:
        _copy_dir(src, tmp, boundary)
        remove_path(dst)
        os.replace(tmp, dst)
    except BaseException:
        remove_path(tmp)
        raise


def remove_path(p: Path) -> None:
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p)


def same_location(a: Path, b: Path) -> bool:
    """True if a and b are the same directory once symlinks are resolved."""
    return os.path.realpath(a) == os.path.realpath(b)


def _link(target: Path, link: Path) -> bool:
    """Create a relative symlink link -> target. Returns False on failure."""
    # e.g. ~/.claude/skills itself symlinked to ~/.agents/skills: the "link" path
    # already is the target, and removing it would delete the installed copy.
    if (link.exists() or link.is_symlink()) and same_location(link, target):
        return True
    try:
        remove_path(link)
        link.parent.mkdir(parents=True, exist_ok=True)
        rel = os.path.relpath(target, os.path.realpath(link.parent))
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
        if canon is not None and same_location(path, canon):
            continue  # agent dir is (a symlink to) the canonical dir
        if canon is not None and path not in copy_paths and _link(canon, path):
            result.linked.append(path)
        else:
            copy_skill_tree(skill.path, path, source_root)
            result.copied.append(path)
    return result


def install_conflicts(
    skill: DiscoveredSkill,
    agents: list[str],
    global_: bool,
    copy: bool,
    cwd: Path,
    managed: bool,
    registry=None,
) -> list[Path]:
    """
    Existing paths an install would replace that skillpack does not manage.

    `managed` is True when the skill name is recorded in the lock file for this
    scope (installed by skillpack or npx skills); then everything is replaceable.
    A symlink already pointing at the canonical copy is never a conflict.
    """
    if managed:
        return []
    canon, targets, _ = planned_paths(skill, agents, global_, copy, cwd, registry)
    conflicts = []
    for path in ([canon] if canon else []) + targets:
        if not (path.exists() or path.is_symlink()):
            continue
        if canon is not None and path != canon and same_location(path, canon):
            continue  # symlink to (or through) the canonical copy; canon itself is checked
        if path not in conflicts:
            conflicts.append(path)
    return conflicts


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
