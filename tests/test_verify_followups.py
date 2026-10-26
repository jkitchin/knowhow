"""Regression tests for the post-fix verification review (N1-N10)."""

import json
import os
import shutil
import sys

import pytest
from click.testing import CliRunner

from skillin import mcp_targets as mt
from skillin import safeio
from skillin.main import cli

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")

SRV = {"command": "uvx", "args": ["srv"]}


@pytest.fixture(autouse=True)
def fresh_backups(monkeypatch):
    monkeypatch.setattr(safeio, "_BACKED_UP", set())


@pytest.fixture
def env(tmp_path, monkeypatch):
    home, proj, repo, bindir = (tmp_path / d for d in ("home", "proj", "repo", "bin"))
    for d in (home / ".claude", proj, repo, bindir):
        d.mkdir(parents=True)
    for var in ("XDG_STATE_HOME", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(home))
    log = tmp_path / "claude.log"
    (bindir / "claude").write_text(
        f'#!/bin/sh\necho "$@" >> {log}\n[ "$1 $2" = "mcp get" ] && exit 1\nexit 0\n'
    )
    (bindir / "claude").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.chdir(proj)
    (repo / ".mcp.json").write_text(json.dumps({"mcpServers": {"srv": SRV}}))
    (repo / "agents").mkdir()
    (repo / "agents" / "cr.md").write_text(
        "---\nname: Code Reviewer\ndescription: Reviews code\n---\nx\n"
    )
    (repo / "hooks" / "h1").mkdir(parents=True)
    (repo / "hooks" / "h1" / "HOOK.md").write_text(
        "---\nname: h1\ndescription: d\nevent: Stop\n---\n"
    )
    (repo / "hooks" / "h1" / "hook.sh").write_text("echo hi\n")
    return {"home": home, "proj": proj, "repo": repo, "log": log, "tmp": tmp_path}


def run(*args, ok=True):
    r = CliRunner().invoke(cli, list(args))
    if ok:
        assert r.exit_code == 0, r.output
    return r


def flat(r):
    return " ".join(r.output.split())


# N1: a committed project lock must not choose which files get written --------


def test_project_lock_cannot_redirect_mcp_writes(env):
    run("add", str(env["repo"]), "--mcp", "srv", "-a", "cursor", "-y")
    lock_file = env["proj"] / ".claude" / "skillin-lock.json"
    lock = json.loads(lock_file.read_text())
    assert lock["mcp"]["srv"]["targets"] == [{"agent": "cursor", "file": ".cursor/mcp.json"}]

    victim = env["home"] / ".cursor" / "mcp.json"
    victim.parent.mkdir(parents=True)
    victim.write_text(json.dumps({"mcpServers": {"mine": {"command": "x"}}}))
    other = env["home"] / "other.json"
    other.write_text("{}")
    lock["mcp"]["srv"]["targets"] = [
        {"agent": "cursor", "file": str(victim)},
        {"agent": "claude-code", "file": str(other)},
    ]
    lock["mcp"]["srv"]["hash"] = "stale"  # force an upgrade
    lock_file.write_text(json.dumps(lock))

    run("upgrade", "-p", "-y")
    run("remove", "--mcp", "srv", "-y")
    assert json.loads(victim.read_text()) == {"mcpServers": {"mine": {"command": "x"}}}
    assert other.read_text() == "{}"


# N2: symlinked configs ---------------------------------------------------------


def test_global_dotfile_symlink_is_kept_and_updated(env):
    dotfile = env["home"] / "dotfiles" / "cursor-mcp.json"
    dotfile.parent.mkdir()
    dotfile.write_text('{"theme": "x"}')
    link = env["home"] / ".cursor" / "mcp.json"
    link.parent.mkdir()
    link.symlink_to(dotfile)
    run("add", str(env["repo"]), "--mcp", "srv", "-a", "cursor", "-g", "-y")
    assert link.is_symlink()
    assert json.loads(dotfile.read_text())["mcpServers"]["srv"] == SRV


def test_project_symlink_out_of_project_is_refused(env):
    outside = env["home"] / "elsewhere.json"
    outside.write_text("{}")
    (env["proj"] / ".cursor").mkdir()
    (env["proj"] / ".cursor" / "mcp.json").symlink_to(outside)
    r = run("add", str(env["repo"]), "--mcp", "srv", "-a", "cursor", "-y", ok=False)
    assert r.exit_code != 0 and "points outside" in flat(r)
    assert outside.read_text() == "{}"

    victim = env["home"] / ".bashrc"
    victim.write_text("export X=1\n")
    (env["proj"] / "skills-lock.json").symlink_to(victim)
    (env["repo"] / "skills" / "s").mkdir(parents=True)
    (env["repo"] / "skills" / "s" / "SKILL.md").write_text(
        "---\nname: s\ndescription: s. Use always.\n---\n"
    )
    r = run("add", str(env["repo"]), "-s", "s", "-y", ok=False)
    assert r.exit_code != 0
    assert victim.read_text() == "export X=1\n"


# N3: bad settings.json is detected before anything is copied ------------------


def test_hook_with_bad_settings_leaves_nothing_behind(env):
    settings = env["proj"] / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text("{ bad")
    r = run("add", str(env["repo"]), "--hook", "h1", "-y", ok=False)
    assert r.exit_code != 0 and "not valid JSON" in flat(r)
    assert not (env["proj"] / ".claude" / "hooks").exists()
    settings.write_text("{}")
    run("add", str(env["repo"]), "--hook", "h1", "-y")  # no --force needed
    run("remove", "--hook", "h1", "-y")
    assert json.loads(settings.read_text()) == {}


# N4: subagents with display names ----------------------------------------------


def test_subagent_with_display_name_can_be_removed(env):
    run("add", str(env["repo"]), "--subagent", "Code Reviewer", "-y")
    installed = env["proj"] / ".claude" / "agents" / "code-reviewer.md"
    assert installed.exists()
    run("remove", "--subagent", "code-reviewer", "-y")
    assert not installed.exists()
    run("add", str(env["repo"]), "--subagent", "Code Reviewer", "-y")
    run("remove", "--all", "-y")
    assert not installed.exists()
    assert json.loads(run("installed", "-p", "--json").output) == []


# N5: Claude global replace only removes what exists ----------------------------


def test_claude_global_install_does_not_remove_absent_server(env):
    run("add", str(env["repo"]), "--mcp", "srv", "-a", "claude-code", "-g", "-y")
    calls = env["log"].read_text().splitlines()
    assert not any(c.startswith("mcp remove") for c in calls)
    assert any(c.startswith("mcp add-json --scope user srv") for c in calls)


# N6 / N9 / N7 / N10 ------------------------------------------------------------


def test_malformed_source_mcp_servers_warns(env):
    (env["repo"] / ".mcp.json").write_text('{"mcpServers": [1]}')
    r = run("add", str(env["repo"]), "--list", ok=False)
    assert "Traceback" not in r.output and "must be an object" in flat(r)


def test_toml_and_json_keep_non_ascii(tmp_path):
    toml_file = tmp_path / "config.toml"
    p = mt.Placement(mt.TARGETS["codex"], toml_file, False, tmp_path)
    mt.write(p, "emoji", {"command": "x", "args": ["😀 héllo"]})
    assert tomllib.loads(toml_file.read_text())["mcp_servers"]["emoji"]["args"] == ["😀 héllo"]

    js = tmp_path / ".mcp.json"
    js.write_text(json.dumps({"note": "héllo ☃"}, ensure_ascii=False))
    mt.write(mt.Placement(mt.TARGETS["claude-code"], js, False, tmp_path), "srv", SRV)
    assert "héllo ☃" in js.read_text()


def test_backup_is_the_state_before_the_command(tmp_path):
    f = tmp_path / ".mcp.json"
    f.write_text('{"original": true}')
    p = mt.Placement(mt.TARGETS["claude-code"], f, False, tmp_path)
    mt.write(p, "a", SRV)
    mt.write(p, "b", SRV)  # second write in the same command
    assert json.loads((tmp_path / ".mcp.json.bak").read_text()) == {"original": True}


# N8 ------------------------------------------------------------------------------


def test_damaged_lock_file_is_not_overwritten(env):
    lock = env["proj"] / "skills-lock.json"
    lock.write_text('{"version": 1, "skills": {"other": {}}  <<<<<<< HEAD')
    (env["repo"] / "skills" / "s").mkdir(parents=True)
    (env["repo"] / "skills" / "s" / "SKILL.md").write_text(
        "---\nname: s\ndescription: s. Use always.\n---\n"
    )
    r = run("add", str(env["repo"]), "-s", "s", "-y", ok=False)
    assert r.exit_code != 0 and "not valid JSON" in flat(r)
    assert lock.read_text().endswith("<<<<<<< HEAD")


# untracked MCP servers in any agent config ------------------------------------------


def test_untracked_lists_servers_in_other_agents(env):
    (env["proj"] / ".cursor").mkdir()
    (env["proj"] / ".cursor" / "mcp.json").write_text(
        json.dumps({"mcpServers": {"users-own": {"command": "x"}}})
    )
    items = json.loads(run("installed", "-p", "--untracked", "--json").output)
    assert [(i["kind"], i["name"], i["status"]) for i in items] == [
        ("mcp", "users-own", "untracked")
    ]
