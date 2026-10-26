"""End-to-end tests for `skillin add/remove/check/upgrade` using local git repos."""

import json
import shutil
import subprocess

import pytest
from click.testing import CliRunner

from skillin.lock import compute_folder_hash
from skillin.main import cli

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def git(cwd, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def write_skill(path, name, body="body"):
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: d {name}\n---\n{body}\n")


@pytest.fixture
def env(tmp_path, monkeypatch):
    home, proj, repo = tmp_path / "home", tmp_path / "proj", tmp_path / "repo"
    (home / ".claude").mkdir(parents=True)
    proj.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.chdir(proj)
    write_skill(repo / "skills" / "cat" / "alpha", "alpha")
    write_skill(repo / "skills" / "beta", "beta")
    git(repo, "init", "-q")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "init")
    return {"home": home, "proj": proj, "repo": repo, "url": f"file://{repo}"}


def run(*args):
    result = CliRunner().invoke(cli, list(args), catch_exceptions=False)
    return result


def test_list(env):
    r = run("add", env["url"], "--list")
    assert r.exit_code == 0
    assert "alpha" in r.output and "beta" in r.output


def test_project_install_symlink_and_lock(env):
    r = run("add", env["url"], "-s", "alpha", "-y")
    assert r.exit_code == 0, r.output
    canon = env["proj"] / ".agents" / "skills" / "alpha"
    link = env["proj"] / ".claude" / "skills" / "alpha"
    assert (canon / "SKILL.md").is_file()
    assert link.is_symlink() and link.resolve() == canon.resolve()
    assert not (canon / ".git").exists()

    lock = json.loads((env["proj"] / "skills-lock.json").read_text())
    entry = lock["skills"]["alpha"]
    assert entry["sourceType"] == "git"
    assert entry["skillPath"] == "skills/cat/alpha/SKILL.md"
    assert entry["computedHash"] == compute_folder_hash(canon)


def test_global_install_copy(env):
    r = run("add", env["url"], "--all", "-g", "--copy", "-a", "claude-code")
    assert r.exit_code == 0, r.output
    for name in ("alpha", "beta"):
        p = env["home"] / ".claude" / "skills" / name
        assert (p / "SKILL.md").is_file() and not p.is_symlink()
    lock = json.loads((env["home"] / ".agents" / ".skill-lock.json").read_text())
    assert lock["version"] == 3
    assert len(lock["skills"]["alpha"]["skillFolderHash"]) == 40  # git tree SHA


def test_unknown_skill_and_multiple_without_selection(env):
    r = CliRunner().invoke(cli, ["add", env["url"], "-s", "nope", "-y"])
    assert r.exit_code != 0 and "not found" in r.output
    r = CliRunner().invoke(cli, ["add", env["url"], "-y"])
    assert r.exit_code != 0 and "--skill" in r.output


def test_check_upgrade_remove(env):
    run("add", env["url"], "-s", "alpha", "-y")
    assert "up to date" in run("check").output

    write_skill(env["repo"] / "skills" / "cat" / "alpha", "alpha", body="changed")
    git(env["repo"], "commit", "-qam", "change")
    assert "update available" in run("check").output

    assert "updated" in run("upgrade").output
    canon = env["proj"] / ".agents" / "skills" / "alpha"
    assert "changed" in (canon / "SKILL.md").read_text()
    assert "up to date" in run("check").output

    r = run("remove", "alpha", "-y")
    assert r.exit_code == 0
    assert not canon.exists()
    assert not (env["proj"] / ".claude" / "skills" / "alpha").is_symlink()
    assert json.loads((env["proj"] / "skills-lock.json").read_text())["skills"] == {}


def test_preserves_foreign_lock_fields(env):
    lock_file = env["proj"] / "skills-lock.json"
    lock_file.write_text(
        json.dumps({"version": 1, "skills": {"other": {"source": "x/y", "sourceType": "github"}}})
    )
    run("add", env["url"], "-s", "beta", "-y")
    lock = json.loads(lock_file.read_text())
    assert set(lock["skills"]) == {"beta", "other"}


def test_symlink_outside_source_not_copied(env, tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("secret")
    (env["repo"] / "skills" / "beta" / "leak").symlink_to(secret)
    git(env["repo"], "add", ".")
    git(env["repo"], "commit", "-qm", "symlink")
    run("add", str(env["repo"]), "-s", "beta", "-y")
    assert not (env["proj"] / ".agents" / "skills" / "beta" / "leak").exists()
