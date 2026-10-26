"""VS Code as a skill target."""

import shutil

import pytest
from click.testing import CliRunner

from skillin.agents_registry import AGENTS, detect_agents, resolve_agent_names
from skillin.main import cli

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


@pytest.fixture
def env(tmp_path, monkeypatch):
    home, proj, repo = tmp_path / "home", tmp_path / "proj", tmp_path / "repo"
    home.mkdir()
    proj.mkdir()
    for var in ("XDG_STATE_HOME", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME", "APPDATA"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(proj)
    skill = repo / "skills" / "sample"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: sample\ndescription: A sample. Use always.\n---\nx\n"
    )
    return {"home": home, "proj": proj, "repo": repo}


def run(*args):
    r = CliRunner().invoke(cli, list(args))
    assert r.exit_code == 0, r.output
    return r


def test_vscode_is_a_universal_target():
    assert AGENTS["vscode"].is_universal
    assert resolve_agent_names(["code"]) == ["vscode"]


def test_detects_vscode(env):
    assert "vscode" not in detect_agents()
    (env["home"] / ".vscode").mkdir()
    assert detect_agents() == ["vscode"]


def test_project_install_for_vscode(env):
    run("add", str(env["repo"]), "-s", "sample", "-a", "vscode", "-y")
    installed = env["proj"] / ".agents" / "skills" / "sample"
    assert (installed / "SKILL.md").is_file() and not installed.is_symlink()
    assert not (env["proj"] / ".claude").exists()


def test_global_install_for_vscode(env):
    run("add", str(env["repo"]), "-s", "sample", "-a", "vscode", "-g", "-y")
    assert (env["home"] / ".agents" / "skills" / "sample" / "SKILL.md").is_file()
    assert not (env["home"] / ".claude").exists()


def test_vscode_only_user_gets_no_claude_dir(env):
    (env["home"] / ".vscode").mkdir()
    out = run("add", str(env["repo"]), "-s", "sample", "-y").output
    assert "VS Code" in out
    assert (env["proj"] / ".agents" / "skills" / "sample").is_dir()
    assert not (env["proj"] / ".claude").exists()
    run("remove", "sample", "-y")
    assert not (env["proj"] / ".agents" / "skills" / "sample").exists()
