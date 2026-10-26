"""Check skills against the Agent Skills specification and knowhow's install rules.

Spec: https://agentskills.io/specification. On top of the spec this flags things
that work on paper but break when a skill is installed with `knowhow add` or
`npx skills add` (files dropped on install, symlinks out of the repo, Git LFS
pointers, skills hidden from discovery, duplicate names).
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from knowhow.discovery import SKIP_DIRS, discover_skills
from knowhow.installer import EXCLUDE_NAMES

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_LINES = 500
MAX_BODY_TOKENS = 5000  # approximate: 4 characters per token
LARGE_FILE = 10 * 1024 * 1024
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_CODE_RE = re.compile(r"(^|\n)(```|~~~).*?\n\2[^\n]*|`[^`\n]*`", re.DOTALL)
_FRONTMATTER_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.DOTALL)


@dataclass
class Finding:
    level: str  # "error" or "warning"
    path: str  # repo-relative path
    message: str


def _rel(path: Path, root: Path) -> str:
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)
    return rel or "."


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (frontmatter, body, error)."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None, text, "SKILL.md must start with YAML frontmatter between '---' lines"
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return None, text[m.end() :], f"Invalid YAML frontmatter: {e}"
    if not isinstance(data, dict):
        return None, text[m.end() :], "Frontmatter must be a YAML mapping"
    return data, text[m.end() :], None


def check_skill(skill_dir: Path, root: Path, is_repo_root: bool = False) -> list[Finding]:
    """Check one skill directory (containing SKILL.md)."""
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    where = _rel(skill_md, root)

    def err(msg, path=where):
        findings.append(Finding("error", path, msg))

    def warn(msg, path=where):
        findings.append(Finding("warning", path, msg))

    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        err("SKILL.md is not valid UTF-8")
        return findings
    fm, body, problem = split_frontmatter(text)
    if problem:
        err(problem)
        return findings

    # name
    name = fm.get("name")
    if not isinstance(name, str) or not name:
        err("'name' is required and must be a string")
    else:
        if len(name) > 64:
            err(f"'name' is {len(name)} characters (max 64)")
        if not NAME_RE.match(name):
            err(
                f"'name' {name!r} must use only a-z, 0-9 and single hyphens, "
                "and not start or end with a hyphen"
            )
        if name != skill_dir.name:
            msg = f"'name' {name!r} does not match the directory name {skill_dir.name!r}"
            if is_repo_root:
                warn(msg + " (fine for a single-skill repo; installs use 'name')")
            else:
                err(msg + " (the spec requires them to match)")

    # description
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err("'description' is required and must be a non-empty string")
    else:
        if len(desc) > 1024:
            err(f"'description' is {len(desc)} characters (max 1024)")
        if not re.search(r"\b(use|when|whenever|trigger)\b", desc, re.IGNORECASE):
            warn("'description' should say when to use the skill (e.g. 'Use when ...')")

    # optional spec fields
    if "license" in fm and not isinstance(fm["license"], str):
        err("'license' must be a string")
    if "compatibility" in fm:
        comp = fm["compatibility"]
        if not isinstance(comp, str) or not 1 <= len(comp) <= 500:
            err("'compatibility' must be a string of 1-500 characters")
    if "metadata" in fm:
        meta = fm["metadata"]
        if not isinstance(meta, dict):
            err("'metadata' must be a mapping")
        else:
            # `internal: true` is a boolean by convention (npx skills checks `=== true`)
            bad = [
                str(k)
                for k, v in meta.items()
                if not isinstance(v, str) and not (k == "internal" and isinstance(v, bool))
            ]
            if bad:
                warn(
                    f"'metadata' values should be strings; quote {', '.join(bad)} "
                    '(e.g. version: "1.0")'
                )
    if "allowed-tools" in fm:
        tools = fm["allowed-tools"]
        if isinstance(tools, list):
            warn(
                "'allowed-tools' is a list; the spec uses a space-separated string "
                "(e.g. allowed-tools: Read Grep Bash(git:*))"
            )
        elif not isinstance(tools, str):
            err("'allowed-tools' must be a space-separated string")
    extra = sorted(set(map(str, fm)) - SPEC_FIELDS)
    if extra:
        warn(f"Fields not in the Agent Skills spec (other agents ignore them): {', '.join(extra)}")

    # body size
    lines = body.count("\n") + 1
    if not body.strip():
        warn("SKILL.md has no instructions after the frontmatter")
    if lines > MAX_LINES:
        warn(
            f"SKILL.md body is {lines} lines; keep it under {MAX_LINES} "
            "and move detail to references/"
        )
    tokens = len(body) // 4
    if tokens > MAX_BODY_TOKENS:
        warn(f"SKILL.md body is ~{tokens} tokens; the spec recommends under {MAX_BODY_TOKENS}")

    # relative links
    for target in LINK_RE.findall(_CODE_RE.sub(" ", body)):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#"):
            continue
        rel = target.split("#", 1)[0]
        if not rel:
            continue
        resolved = (skill_dir / rel).resolve()
        try:
            resolved.relative_to(skill_dir.resolve())
        except ValueError:
            warn(f"Link to {target!r} points outside the skill directory and won't be installed")
            continue
        if not resolved.exists():
            warn(f"Broken link: {target!r} does not exist")

    # files that behave differently once installed
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for fn in filenames + [d for d in dirnames if (Path(dirpath) / d).is_symlink()]:
            p = Path(dirpath) / fn
            here = _rel(p, root)
            if fn in EXCLUDE_NAMES:
                warn(f"'{fn}' is not copied when the skill is installed", here)
            if p.is_symlink():
                try:
                    p.resolve().relative_to(root.resolve())
                except ValueError:
                    warn("Symlink points outside the repository and is skipped on install", here)
                    continue
                if p.is_dir():
                    warn("Directory symlinks are skipped on install; copy the files instead", here)
                continue
            if not p.is_file():
                continue
            size = p.stat().st_size
            if size > LARGE_FILE:
                warn(f"Large file ({size // (1024 * 1024)} MB); keep skills small", here)
            elif size < 200:
                try:
                    if p.read_bytes().startswith(b"version https://git-lfs"):
                        warn("Git LFS pointer: installs get the pointer, not the file", here)
                except OSError:
                    pass
    return findings


def find_skill_files(root: Path) -> list[Path]:
    """Every SKILL.md under root (directories of skills), skipping vendored dirs."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        if "SKILL.md" in filenames:
            found.append(Path(dirpath))
    return found


def check_repo(root: Path) -> tuple[list[Finding], int]:
    """Check every skill in a repository. Returns (findings, number of skills)."""
    root = root.resolve()
    candidates = find_skill_files(root)
    findings: list[Finding] = []
    if not candidates:
        return [Finding("error", ".", "No SKILL.md files found")], 0

    is_git_root = (root / ".git").exists()
    for skill_dir in candidates:
        findings += check_skill(skill_dir, root, is_repo_root=is_git_root and skill_dir == root)

    # How knowhow / npx skills will actually see the repo
    discovered = discover_skills(root, include_internal=True)
    found_paths = {s.path.resolve() for s in discovered}
    names: dict[str, Path] = {}
    for skill_dir in candidates:
        fm, _, problem = split_frontmatter((skill_dir / "SKILL.md").read_text(errors="replace"))
        name = fm.get("name") if fm else None
        duplicate = False
        if isinstance(name, str):
            if name in names:
                duplicate = True
                findings.append(
                    Finding(
                        "error",
                        _rel(skill_dir / "SKILL.md", root),
                        f"Duplicate name {name!r} (also {_rel(names[name], root)}); "
                        "only the first is installable",
                    )
                )
            else:
                names[name] = skill_dir
        if problem or duplicate or skill_dir.resolve() in found_paths:
            continue
        if (root / "SKILL.md").exists() and skill_dir != root:
            reason = "the repo root has a SKILL.md, so only that skill is offered"
        else:
            reason = "it is nested inside another skill or deeper than the search limits"
        findings.append(
            Finding(
                "warning",
                _rel(skill_dir / "SKILL.md", root),
                f"Not discovered by `knowhow add` / `npx skills add`: {reason} "
                "(users would need --full-depth)",
            )
        )
    return findings, len(candidates)
