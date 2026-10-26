"""Fetch skill sources into a temporary checkout."""

import io
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from skillin.sources import Source

# Limits for the tarball fallback (used when git is not installed)
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
MAX_EXTRACT_FILES = 5000


class FetchError(RuntimeError):
    """Raised when a source cannot be fetched."""


@dataclass
class Checkout:
    """A fetched source on local disk."""

    root: Path  # repository root
    commit: str | None = None  # resolved commit SHA, when known
    is_git: bool = False


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ALLOW_PROTOCOL"] = "https:http:ssh:git:file"
    env["GIT_LFS_SKIP_SMUDGE"] = "1"
    return env


def _git(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=_git_env(),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise FetchError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _looks_like_sha(ref: str) -> bool:
    return 7 <= len(ref) <= 40 and all(c in "0123456789abcdef" for c in ref.lower())


def git_clone(url: str, dest: Path, ref: str | None = None) -> str:
    """Shallow-clone `url` into `dest` and return the HEAD commit SHA."""
    if ref and _looks_like_sha(ref):
        dest.mkdir(parents=True, exist_ok=True)
        _git(["init", "-q"], cwd=dest)
        _git(["remote", "add", "origin", url], cwd=dest)
        _git(["fetch", "-q", "--depth", "1", "origin", ref], cwd=dest)
        _git(["checkout", "-q", "FETCH_HEAD"], cwd=dest)
    else:
        args = ["clone", "-q", "--depth", "1"]
        if ref:
            args += ["--branch", ref]
        _git([*args, url, str(dest)])
    return _git(["rev-parse", "HEAD"], cwd=dest)


def git_tree_hash(repo: Path, rel_dir: str) -> str | None:
    """
    Return the git tree SHA of `rel_dir` at HEAD.

    For GitHub repos this equals the tree SHA from the GitHub Trees API, which is
    what `npx skills` stores as `skillFolderHash` in its global lock file.
    """
    spec = "HEAD^{tree}" if rel_dir in ("", ".") else f"HEAD:{rel_dir}"
    try:
        return _git(["rev-parse", spec], cwd=repo)
    except FetchError:
        return None


def _download_github_tarball(owner_repo: str, ref: str | None, dest: Path) -> None:
    """Download and safely extract a GitHub tarball (fallback when git is missing)."""
    url = f"https://codeload.github.com/{owner_repo}/tar.gz/{ref or 'HEAD'}"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read(MAX_DOWNLOAD_BYTES + 1)
    except OSError as e:
        raise FetchError(f"Download failed for {url}: {e}") from e
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise FetchError(f"Download exceeds {MAX_DOWNLOAD_BYTES} bytes: {url}")

    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        members = tar.getmembers()
        if len(members) > MAX_EXTRACT_FILES:
            raise FetchError(f"Archive has too many files ({len(members)})")
        if hasattr(tarfile, "data_filter"):
            tar.extractall(dest, filter="data")
        else:  # Python < 3.10.12: reject absolute paths, traversal and links ourselves
            for m in members:
                target = (dest / m.name).resolve()
                if not str(target).startswith(str(dest.resolve())) or m.issym() or m.islnk():
                    raise FetchError(f"Unsafe archive member: {m.name}")
            tar.extractall(dest)

    # GitHub tarballs contain a single top-level "<repo>-<sha>/" directory
    entries = [p for p in dest.iterdir() if p.is_dir()]
    if len(entries) == 1:
        for child in entries[0].iterdir():
            shutil.move(str(child), dest / child.name)
        entries[0].rmdir()


@contextmanager
def fetch_source(source: Source) -> Iterator[Checkout]:
    """
    Make `source` available on local disk for the duration of the context.

    Local sources are used in place. Remote sources are cloned into a temporary
    directory that is removed on exit.
    """
    if source.is_local:
        root = Path(source.url)
        if not root.exists():
            raise FetchError(f"Path does not exist: {root}")
        is_git = (root / ".git").exists()
        commit = None
        if is_git and shutil.which("git"):
            try:
                commit = _git(["rev-parse", "HEAD"], cwd=root)
            except FetchError:
                is_git = False
        yield Checkout(root=root, commit=commit, is_git=is_git)
        return

    tmp = Path(tempfile.mkdtemp(prefix="skillin-"))
    try:
        dest = tmp / "repo"
        if shutil.which("git"):
            commit = git_clone(source.url, dest, source.ref)
            yield Checkout(root=dest, commit=commit, is_git=True)
        elif source.type == "github" and source.owner_repo:
            dest.mkdir()
            _download_github_tarball(source.owner_repo, source.ref, dest)
            yield Checkout(root=dest)
        else:
            raise FetchError("git is required to fetch this source but was not found on PATH")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def github_tree(owner_repo: str, ref: str | None = None) -> dict[str, str] | None:
    """
    Map of repo path -> tree SHA for every directory, via the GitHub Trees API.

    Lets `check` compare global skills (whose lock hash is the folder's tree SHA)
    without cloning. Uses GITHUB_TOKEN / GH_TOKEN when set. Returns None on any
    failure (rate limit, private repo, truncated tree) so callers fall back to cloning.
    """
    import json

    url = f"https://api.github.com/repos/{owner_repo}/git/trees/{ref or 'HEAD'}?recursive=1"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read(MAX_DOWNLOAD_BYTES))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("truncated") or "tree" not in data:
        return None
    tree = {t["path"]: t["sha"] for t in data["tree"] if t.get("type") == "tree"}
    tree[""] = data.get("sha", "")
    return tree
