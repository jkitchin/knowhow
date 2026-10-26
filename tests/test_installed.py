"""`skillin installed` inventory and `skillin remove --all`."""

import json
import shutil

import pytest
from click.testing import CliRunner

from skillin.main import cli

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def skill_md(name):
    return f"---\nname: {name}\ndescription: {name}. Use always.\n---\nx\n"


@pytest.fixture
def env(tmp_path, monkeypatch):
    home, proj, repo = tmp_path / "home", tmp_path / "proj", tmp_path / "repo"
    (home / ".claude").mkdir(parents=True)
    proj.mkdir()
    for var in ("XDG_STATE_HOME", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(proj)
    for name in ("alpha", "beta"):
        (repo / "skills" / name).mkdir(parents=True)
        (repo / "skills" / name / "SKILL.md").write_text(skill_md(name))
    (repo / "commands").mkdir()
    (repo / "commands" / "commit.md").write_text("c\n")
    (repo / ".mcp.json").write_text(json.dumps({"mcpServers": {"fs": {"command": "x"}}}))
    return {"home": home, "proj": proj, "repo": repo}


def run(*args):
    r = CliRunner().invoke(cli, list(args))
    assert r.exit_code == 0, r.output
    return r


def inventory(*args):
    return json.loads(run("installed", "--json", *args).output)


def test_inventory_lists_both_scopes_and_all_kinds(env):
    run("add", str(env["repo"]), "-s", "alpha", "--command", "commit", "--mcp", "fs", "-y")
    run("add", str(env["repo"]), "-s", "beta", "-g", "-y")
    items = {(i["scope"], i["kind"], i["name"]): i for i in inventory()}
    assert set(items) == {
        ("project", "skill", "alpha"),
        ("project", "command", "commit"),
        ("project", "mcp", "fs"),
        ("global", "skill", "beta"),
    }
    assert all(i["status"] == "ok" for i in items.values())
    assert [i["name"] for i in inventory("-g")] == ["beta"]
    assert "alpha" in run("installed").output  # table output


def test_inventory_reports_missing_broken_and_untracked(env):
    run("add", str(env["repo"]), "-s", "alpha", "-s", "beta", "-y")
    shutil.rmtree(env["proj"] / ".agents" / "skills" / "alpha")  # leaves a dangling link
    shutil.rmtree(env["proj"] / ".agents" / "skills" / "beta")
    (env["proj"] / ".claude" / "skills" / "beta").unlink()
    mine = env["proj"] / ".claude" / "skills" / "mine"
    mine.mkdir()
    (mine / "SKILL.md").write_text(skill_md("mine"))
    status = {i["name"]: i["status"] for i in inventory("-p", "--untracked")}
    assert status == {"alpha": "broken", "beta": "missing", "mine": "untracked"}


def test_remove_all_removes_only_what_skillin_installed(env):
    run("add", str(env["repo"]), "-s", "alpha", "--command", "commit", "--mcp", "fs", "-y")
    run("add", str(env["repo"]), "-s", "beta", "-g", "-y")
    mine = env["proj"] / ".claude" / "skills" / "mine"
    mine.mkdir(parents=True)
    (mine / "SKILL.md").write_text(skill_md("mine"))
    mcp = env["proj"] / ".mcp.json"
    data = json.loads(mcp.read_text())
    data["mcpServers"]["users-own"] = {"command": "y"}
    mcp.write_text(json.dumps(data))

    run("remove", "--all", "-y")
    assert inventory("-p") == []
    assert mine.exists()  # not installed by skillin
    assert json.loads(mcp.read_text())["mcpServers"] == {"users-own": {"command": "y"}}
    assert [i["name"] for i in inventory("-g")] == ["beta"]  # other scope untouched

    run("remove", "--all", "-g", "-y")
    assert inventory() == []
    assert "Nothing installed" in run("remove", "--all", "-y").output


def test_remove_all_rejects_names(env):
    r = CliRunner().invoke(cli, ["remove", "--all", "alpha", "-y"])
    assert r.exit_code != 0 and "--all" in r.output
