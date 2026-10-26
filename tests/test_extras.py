"""Tests for commands, subagents, hooks and MCP servers via `skillin add` (phase 2)."""

import json
import os
import shutil
import subprocess

import pytest
from click.testing import CliRunner

from skillin.commands import add as add_module
from skillin.extras import discover_extras
from skillin.main import cli
from skillin.utils import find_skill_directories

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def git(cwd, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


HOOK_MD = """---
name: fmt
description: Format files
event: PostToolUse
matcher: Edit|Write
timeout: 30
---
# fmt
"""


def make_repo(repo):
    (repo / "commands" / "sub").mkdir(parents=True)
    (repo / "commands" / "commit.md").write_text("---\ndescription: Commit\n---\nDo it\n")
    (repo / "commands" / "sub" / "review.md").write_text("Review\n")
    (repo / "commands" / "README.md").write_text("ignored\n")
    (repo / "agents").mkdir()
    (repo / "agents" / "reviewer.md").write_text(
        "---\nname: reviewer\ndescription: Reviews code\n---\nYou review.\n"
    )
    (repo / "agents" / "broken.md").write_text("no frontmatter\n")
    (repo / "hooks" / "fmt").mkdir(parents=True)
    (repo / "hooks" / "fmt" / "HOOK.md").write_text(HOOK_MD)
    (repo / "hooks" / "fmt" / "hook.py").write_text("print('hi')\n")
    (repo / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "fs": {"command": "npx", "args": ["server"], "description": "Files"},
                    "web": {"type": "http", "url": "https://example.com/mcp"},
                    "bad": {"type": "stdio"},
                }
            }
        )
    )
    git(repo, "init", "-q")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "init")


@pytest.fixture
def env(tmp_path, monkeypatch):
    home, proj, repo = tmp_path / "home", tmp_path / "proj", tmp_path / "repo"
    (home / ".claude").mkdir(parents=True)
    proj.mkdir()
    repo.mkdir()
    for var in ("XDG_STATE_HOME", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(proj)
    make_repo(repo)
    return {"home": home, "proj": proj, "repo": repo, "url": f"file://{repo}", "tmp": tmp_path}


def run(*args):
    return CliRunner().invoke(cli, list(args), catch_exceptions=False)


def test_discover_extras(env):
    warnings = []
    found = discover_extras(env["repo"], warnings=warnings)
    assert sorted(e.name for e in found["command"]) == ["commit", "review"]
    assert [e.name for e in found["subagent"]] == ["reviewer"]
    assert [e.name for e in found["hook"]] == ["fmt"]
    assert sorted(e.name for e in found["mcp"]) == ["fs", "web"]
    assert any("broken.md" in w for w in warnings)
    assert any("'bad'" in w for w in warnings)


def test_list_shows_all_kinds(env):
    out = run("add", env["url"], "--list").output
    for word in ("commit", "reviewer", "fmt", "fs", "web"):
        assert word in out


def test_install_command_subagent_hook(env):
    r = run(
        "add", env["url"], "--command", "commit", "--subagent", "reviewer", "--hook", "fmt", "-y"
    )
    assert r.exit_code == 0, r.output
    claude = env["proj"] / ".claude"
    assert (claude / "commands" / "commit.md").read_text().startswith("---")
    assert (claude / "agents" / "reviewer.md").exists()
    hook_py = claude / "hooks" / "fmt" / "hook.py"
    assert os.access(hook_py, os.X_OK)
    settings = json.loads((claude / "settings.json").read_text())
    commands = [h["command"] for e in settings["hooks"]["PostToolUse"] for h in e["hooks"]]
    # portable: works for anyone who checks out the project
    assert commands == ['"$CLAUDE_PROJECT_DIR"/.claude/hooks/fmt/hook.py']

    lock = json.loads((claude / "skillin-lock.json").read_text())
    assert set(lock["commands"]) == {"commit"}
    assert lock["hooks"]["fmt"]["path"] == "hooks/fmt"
    # no skills were requested, so none were installed
    assert not (env["proj"] / "skills-lock.json").exists()

    r = run("remove", "--hook", "fmt", "--command", "commit", "-y")
    assert r.exit_code == 0
    assert not (claude / "hooks" / "fmt").exists()
    assert json.loads((claude / "settings.json").read_text())["hooks"] == {}
    assert json.loads((claude / "skillin-lock.json").read_text())["commands"] == {}


def test_hook_requires_confirmation_noninteractive(env):
    r = CliRunner().invoke(cli, ["add", env["url"], "--hook", "fmt"])
    assert r.exit_code != 0
    assert "without -y" in r.output
    assert not (env["proj"] / ".claude" / "hooks").exists()


def test_wildcard_not_allowed_for_hooks(env):
    r = CliRunner().invoke(cli, ["add", env["url"], "--hook", "*", "-y"])
    assert r.exit_code != 0 and "explicitly" in r.output


def test_mcp_project_merges(env):
    mcp = env["proj"] / ".mcp.json"
    mcp.write_text(json.dumps({"mcpServers": {"mine": {"command": "x"}}, "other": 1}))
    r = run("add", env["url"], "--mcp", "fs", "-y")
    assert r.exit_code == 0, r.output
    data = json.loads(mcp.read_text())
    assert data["mcpServers"]["fs"] == {"command": "npx", "args": ["server"]}
    assert data["mcpServers"]["mine"] == {"command": "x"} and data["other"] == 1
    run("remove", "--mcp", "fs", "-y")
    assert "fs" not in json.loads(mcp.read_text())["mcpServers"]


def test_mcp_global_uses_claude_cli(env, monkeypatch):
    bindir, log = env["tmp"] / "bin", env["tmp"] / "calls.log"
    bindir.mkdir()
    # like the real CLI: `mcp get` fails for servers that don't exist
    (bindir / "claude").write_text(
        f'#!/bin/sh\necho "$@" >> {log}\n[ "$1 $2" = "mcp get" ] && exit 1\nexit 0\n'
    )
    (bindir / "claude").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")
    r = run("add", env["url"], "--mcp", "web", "-g", "-y")
    assert r.exit_code == 0, r.output
    calls = log.read_text()
    assert (
        'mcp add-json --scope user web {"type": "http", "url": "https://example.com/mcp"}' in calls
    )
    assert not (env["home"] / ".claude.json").exists()


def test_upgrade_command(env):
    run("add", env["url"], "--command", "commit", "-y")
    (env["repo"] / "commands" / "commit.md").write_text("new version\n")
    git(env["repo"], "commit", "-qam", "change")
    assert "update available" in run("check").output
    assert "updated" in run("upgrade", "-y").output
    assert (env["proj"] / ".claude" / "commands" / "commit.md").read_text() == "new version\n"


def test_local_source_is_portable_in_project_lock(env):
    local = env["proj"] / "vendor"
    shutil.copytree(env["repo"], local)
    (local / "skills" / "s").mkdir(parents=True)
    (local / "skills" / "s" / "SKILL.md").write_text("---\nname: s\ndescription: d\n---\n")
    r = run("add", "./vendor", "-s", "s", "-y")
    assert r.exit_code == 0, r.output
    lock = json.loads((env["proj"] / "skills-lock.json").read_text())
    assert lock["skills"]["s"]["source"] == "./vendor"
    assert "up to date" in run("check").output


def test_fast_github_check_skips_clone(env, monkeypatch):
    lock_file = env["home"] / ".agents" / ".skill-lock.json"
    lock_file.parent.mkdir(parents=True)
    sha = "a" * 40
    lock_file.write_text(
        json.dumps(
            {
                "version": 3,
                "skills": {
                    "x": {
                        "source": "o/r",
                        "sourceType": "github",
                        "sourceUrl": "https://github.com/o/r.git",
                        "skillPath": "skills/x/SKILL.md",
                        "skillFolderHash": sha,
                    }
                },
            }
        )
    )
    monkeypatch.setattr(add_module, "github_tree", lambda repo, ref: {"skills/x": "b" * 40})

    def no_fetch(_src):
        raise AssertionError("should not clone")

    monkeypatch.setattr(add_module, "fetch_source", no_fetch)
    assert "update available" in run("check", "-g").output


def test_find_uses_skills_sh_then_github(monkeypatch):
    def fake_get(url, headers=None):
        if "skills.sh" in url:
            return {"skills": [{"id": "o/r/x", "name": "x", "source": "o/r", "installs": 5}]}
        raise AssertionError(url)

    monkeypatch.setattr(add_module, "_get_json", fake_get)
    out = run("find", "plot").output
    assert "skillin add o/r@x" in out

    def fake_get_fail(url, headers=None):
        if "skills.sh" in url:
            raise OSError("down")
        return {"items": [{"full_name": "a/b", "stargazers_count": 3, "description": "d"}]}

    monkeypatch.setattr(add_module, "_get_json", fake_get_fail)
    out = run("find", "plot").output
    assert "a/b" in out


def test_find_skill_directories_follows_symlinks(tmp_path):
    real = tmp_path / "store" / "s"
    real.mkdir(parents=True)
    (real / "SKILL.md").write_text("x")
    skills = tmp_path / "skills"
    skills.mkdir()
    (skills / "s").symlink_to(real, target_is_directory=True)
    (skills / "loop").symlink_to(skills, target_is_directory=True)  # cycle is tolerated
    assert [p.name for p in find_skill_directories(skills)] == ["s"]
