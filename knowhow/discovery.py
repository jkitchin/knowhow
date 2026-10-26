"""Discover skills (SKILL.md directories) in a repository.

The search order mirrors `npx skills` (vercel-labs/skills, src/skills.ts) so a
repository laid out for one tool works with the other:

1. A SKILL.md at the search path itself (returns immediately unless full_depth).
2. Known container directories: the root (1 level deep), then `skills/`,
   `skills/.curated`, `skills/.experimental`, `skills/.system` and agent dirs
   such as `.claude/skills` and `.agents/skills` (up to 3 levels deep, which
   covers `skills/<category>/<name>/SKILL.md`).
3. Skill directories declared in `.claude-plugin/marketplace.json` or
   `.claude-plugin/plugin.json` (1 level deep).
4. If nothing was found (or full_depth), a recursive search up to 5 levels.

Skills are named by their frontmatter `name`, not their directory. The first
skill found with a given name wins.
"""

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from knowhow.validator import SkillValidator

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__"}
CONTAINER_DEPTH = 3
FALLBACK_DEPTH = 5

AGENT_PROJECT_SKILL_DIRS = [
    ".agents/skills",
    ".claude/skills",
    ".cline/skills",
    ".codex/skills",
    ".continue/skills",
    ".github/skills",
    ".goose/skills",
    ".kiro/skills",
    ".opencode/skills",
    ".roo/skills",
    ".windsurf/skills",
]

_CONTROL_RE = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]"  # CSI
    r"|\x1b\][^\x07]*(\x07|\x1b\\)"  # OSC
    r"|[\x00-\x1f\x7f-\x9f]"  # C0/C1 controls
)


@dataclass
class DiscoveredSkill:
    """A skill found in a source checkout."""

    name: str
    description: str
    path: Path  # directory containing SKILL.md
    rel_path: str  # path of the directory relative to the repo root ("" for root)
    metadata: dict = field(default_factory=dict)
    plugin_name: str | None = None

    @property
    def skill_md_path(self) -> str:
        """Repo-relative path to SKILL.md (npx `skillPath`)."""
        return f"{self.rel_path}/SKILL.md" if self.rel_path else "SKILL.md"

    @property
    def internal(self) -> bool:
        return self.metadata.get("internal") is True


def sanitize_text(text: str) -> str:
    """Strip terminal escapes/control chars and collapse whitespace for display."""
    return " ".join(_CONTROL_RE.sub(" ", text).split())


def install_dir_name(name: str) -> str:
    """Directory name for an installed skill (same rules as npx `sanitizeName`)."""
    s = re.sub(r"[^a-z0-9._]+", "-", name.lower())
    s = re.sub(r"^[.\-]+|[.\-]+$", "", s)
    return s[:255] or "unnamed-skill"


def parse_skill_dir(skill_dir: Path, root: Path, warnings: list[str] | None = None):
    """Parse `skill_dir/SKILL.md` leniently. Returns a DiscoveredSkill or None."""
    skill_md = skill_dir / "SKILL.md"
    try:
        frontmatter = SkillValidator._parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as e:
        if warnings is not None:
            warnings.append(f"{skill_md}: {e}")
        return None
    if not isinstance(frontmatter, dict):
        if warnings is not None:
            warnings.append(f"{skill_md}: missing or invalid YAML frontmatter")
        return None
    name, desc = frontmatter.get("name"), frontmatter.get("description")
    if not isinstance(name, str) or not isinstance(desc, str) or not name or not desc:
        if warnings is not None:
            warnings.append(f"{skill_md}: frontmatter needs string 'name' and 'description'")
        return None
    metadata = frontmatter.get("metadata")
    rel = skill_dir.resolve().relative_to(root.resolve()).as_posix()
    return DiscoveredSkill(
        name=sanitize_text(name),
        description=sanitize_text(desc),
        path=skill_dir,
        rel_path="" if rel == "." else rel,
        metadata=metadata if isinstance(metadata, dict) else {},
    )


def _is_relative_dot_path(p) -> bool:
    return isinstance(p, str) and p.startswith("./")


def _contained(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def plugin_skill_dirs(base: Path) -> list[tuple[Path, str | None]]:
    """Directories to scan declared by Claude plugin manifests, with plugin names."""
    dirs: list[tuple[Path, str | None]] = []

    def add(plugin_base: Path, skills, plugin_name):
        if not _contained(plugin_base, base):
            return
        for sp in skills or []:
            if _is_relative_dot_path(sp):
                d = (plugin_base / sp).parent
                if _contained(d, base):
                    dirs.append((d, plugin_name))
        dirs.append((plugin_base / "skills", plugin_name))

    try:
        manifest = json.loads((base / ".claude-plugin" / "marketplace.json").read_text())
        root = (manifest.get("metadata") or {}).get("pluginRoot")
        if root is None or _is_relative_dot_path(root):
            for plugin in manifest.get("plugins") or []:
                src = plugin.get("source")
                if src is not None and not _is_relative_dot_path(src):
                    continue  # remote plugin sources are not followed
                add(base / (root or "") / (src or ""), plugin.get("skills"), plugin.get("name"))
    except (OSError, ValueError, AttributeError):
        pass

    try:
        manifest = json.loads((base / ".claude-plugin" / "plugin.json").read_text())
        add(base, manifest.get("skills"), manifest.get("name"))
    except (OSError, ValueError, AttributeError):
        pass

    return dirs


def discover_skills(
    root: Path,
    subpath: str | None = None,
    full_depth: bool = False,
    include_internal: bool = False,
    warnings: list[str] | None = None,
) -> list[DiscoveredSkill]:
    """
    Find skills in a checkout.

    Args:
        root: Repository root
        subpath: Optional subdirectory of root to search
        full_depth: Search all subdirectories even if a root SKILL.md exists
        include_internal: Include skills with `metadata.internal: true`
        warnings: If given, collects messages about skipped SKILL.md files

    Returns:
        Skills in discovery order, unique by name
    """
    search = root / subpath if subpath else root
    if not _contained(search, root):
        raise ValueError(f"Subpath escapes repository: {subpath}")

    include_internal = include_internal or os.environ.get("INSTALL_INTERNAL_SKILLS") == "1"
    skills: list[DiscoveredSkill] = []
    seen_names: set[str] = set()
    seen_paths: set[Path] = set()

    def try_add(skill_dir: Path, plugin_name: str | None = None) -> bool:
        """Add the skill at skill_dir if present. Returns True if a SKILL.md exists."""
        if not (skill_dir / "SKILL.md").is_file():
            return False
        resolved = skill_dir.resolve()
        if resolved in seen_paths:
            return True
        seen_paths.add(resolved)
        skill = parse_skill_dir(skill_dir, root, warnings)
        if skill is None or (skill.internal and not include_internal):
            return True
        if skill.name in seen_names:
            if warnings is not None:
                warnings.append(f"Duplicate skill name '{skill.name}' at {skill_dir} (skipped)")
            return True
        skill.plugin_name = plugin_name
        skills.append(skill)
        seen_names.add(skill.name)
        return True

    def walk(directory: Path, max_depth: int, depth: int = 1, plugin_name=None):
        try:
            entries = sorted(p for p in directory.iterdir() if p.is_dir())
        except OSError:
            return
        for child in entries:
            if try_add(child, plugin_name) or depth >= max_depth or child.name in SKIP_DIRS:
                continue
            walk(child, max_depth, depth + 1, plugin_name)

    if try_add(search) and not full_depth:
        return skills

    containers = ["skills", "skills/.curated", "skills/.experimental", "skills/.system"]
    walk(search, 1)
    for rel in containers + AGENT_PROJECT_SKILL_DIRS:
        walk(search / rel, CONTAINER_DEPTH)
    for directory, plugin_name in plugin_skill_dirs(search):
        walk(directory, 1, plugin_name=plugin_name)

    if not skills or full_depth:

        def recurse(directory: Path, depth: int):
            if depth > FALLBACK_DEPTH:
                return
            try_add(directory)
            try:
                children = sorted(p for p in directory.iterdir() if p.is_dir())
            except OSError:
                return
            for child in children:
                if child.name not in SKIP_DIRS:
                    recurse(child, depth + 1)

        recurse(search, 0)

    return skills
