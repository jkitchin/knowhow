"""Parse skill source specifiers (owner/repo, URLs, local paths).

The accepted syntax follows the `npx skills` CLI (vercel-labs/skills) so the
same source strings work with both tools:

    owner/repo                      GitHub repository
    owner/repo/sub/path             subdirectory of a GitHub repository
    owner/repo@skill-name           GitHub repository, filtered to one skill
    owner/repo#ref                  branch, tag or commit
    github:owner/repo, gitlab:group/repo
    https://github.com/o/r/tree/<ref>/<path>
    https://gitlab.com/g/r/-/tree/<ref>/<path>
    https://host/any.git, git@host:o/r.git
    ./local/path, /abs/path, ~/path
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path


class SourceError(ValueError):
    """Raised when a source string cannot be parsed or is unsafe."""


@dataclass
class Source:
    """A parsed skill source."""

    type: str  # "github", "gitlab", "git" or "local"
    url: str  # clone URL, or absolute path for local sources
    ref: str | None = None
    subpath: str | None = None
    skill_filter: str | None = None
    owner_repo: str | None = None  # "owner/repo" for github/gitlab

    @property
    def lock_source(self) -> str:
        """The `source` value recorded in lock files (npx-compatible)."""
        return self.owner_repo or self.url

    @property
    def is_local(self) -> bool:
        return self.type == "local"


_SHORTHAND_RE = re.compile(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)((?:/[^@#\s]+)*)$")


def _check_subpath(subpath: str | None) -> str | None:
    """Normalize a repo subpath and reject traversal."""
    if not subpath:
        return None
    parts = [p for p in subpath.strip("/").split("/") if p and p != "."]
    if any(p == ".." for p in parts):
        raise SourceError(f"Unsafe subpath (contains '..'): {subpath}")
    return "/".join(parts) or None


def _split_fragment(spec: str) -> tuple[str, str | None, str | None]:
    """Split `spec#ref@skill` into (spec, ref, skill)."""
    ref = skill = None
    if "#" in spec:
        spec, frag = spec.split("#", 1)
        if "@" in frag:
            frag, skill = frag.split("@", 1)
        ref = frag or None
    return spec, ref, skill or None


def _is_local(spec: str) -> bool:
    return (
        spec in (".", "..")
        or spec.startswith(("./", "../", "/", "~"))
        or bool(re.match(r"^[A-Za-z]:[\\/]", spec))
    )


def parse_source(spec: str, aliases: dict[str, str] | None = None) -> Source:
    """
    Parse a source specifier.

    Args:
        spec: The source string given on the command line
        aliases: Optional mapping of short names to source strings (from config)

    Returns:
        A Source

    Raises:
        SourceError: If the spec is empty, unrecognized or unsafe
    """
    spec = spec.strip()
    if not spec:
        raise SourceError("Empty source")

    # Config aliases: `kitchin` or `kitchin@skill` -> `jkitchin/skillz[@skill]`
    if aliases:
        head, sep, tail = spec.partition("@")
        if head in aliases:
            spec = aliases[head] + (sep + tail if sep else "")

    if _is_local(spec):
        path = Path(os.path.expanduser(spec)).resolve()
        return Source(type="local", url=str(path))

    spec, ref, frag_skill = _split_fragment(spec)

    if spec.startswith("github:"):
        spec = spec[len("github:") :]
    elif spec.startswith("gitlab:"):
        spec = "https://gitlab.com/" + spec[len("gitlab:") :]

    # GitHub web URLs
    m = re.match(
        r"^https?://(?:www\.)?github\.com/([^/]+)/([^/#?]+?)(?:\.git)?"
        r"(?:/tree/([^/]+)(/.*)?)?/?$",
        spec,
    )
    if m:
        owner, repo, tree_ref, path = m.groups()
        return Source(
            type="github",
            url=f"https://github.com/{owner}/{repo}.git",
            ref=ref or tree_ref,
            subpath=_check_subpath(path),
            skill_filter=frag_skill,
            owner_repo=f"{owner}/{repo}",
        )

    # GitLab web URLs (any host) with /-/tree/<ref>[/path]
    m = re.match(r"^(https?://[^/]+)/(.+?)/-/tree/([^/]+)(/.*)?$", spec)
    if m:
        host, project, tree_ref, path = m.groups()
        return Source(
            type="gitlab",
            url=f"{host}/{project}.git",
            ref=ref or tree_ref,
            subpath=_check_subpath(path),
            skill_filter=frag_skill,
            owner_repo=project if "gitlab.com" in host else None,
        )

    m = re.match(r"^https?://(?:www\.)?gitlab\.com/([^#?]+?)(?:\.git)?/?$", spec)
    if m:
        project = m.group(1)
        return Source(
            type="gitlab",
            url=f"https://gitlab.com/{project}.git",
            ref=ref,
            skill_filter=frag_skill,
            owner_repo=project,
        )

    # Any other git URL (https, ssh, git@)
    if re.match(r"^(https?|ssh|git|file)://", spec) or re.match(r"^[\w.-]+@[\w.-]+:", spec):
        return Source(type="git", url=spec, ref=ref, skill_filter=frag_skill)

    # owner/repo[/path][@skill]
    skill_filter = frag_skill
    if "@" in spec:
        spec, skill_filter = spec.rsplit("@", 1)
    m = _SHORTHAND_RE.match(spec)
    if m:
        owner, repo, path = m.groups()
        repo = repo.removesuffix(".git")
        return Source(
            type="github",
            url=f"https://github.com/{owner}/{repo}.git",
            ref=ref,
            subpath=_check_subpath(path),
            skill_filter=skill_filter or None,
            owner_repo=f"{owner}/{repo}",
        )

    raise SourceError(f"Unrecognized source '{spec}'. Use owner/repo, a git URL, or a local path.")
