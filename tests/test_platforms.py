"""Custom platforms and default_platform (issue #6)."""

import copy
import shutil
import subprocess

import pytest
import yaml
from click.testing import CliRunner

from skillin.config import Config, InvalidPlatformError, PlatformConfigError, validate_platform
from skillin.main import cli


def write_config(home, data):
    path = home / ".config" / "skillz" / "config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data))
    return path


@pytest.fixture
def env(tmp_path, monkeypatch):
    home, proj, repo = tmp_path / "home", tmp_path / "proj", tmp_path / "repo"
    (home / ".claude").mkdir(parents=True)
    proj.mkdir()
    for var in ("XDG_STATE_HOME", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(proj)
    skill = repo / "skills" / "sample"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: sample\ndescription: A sample. Use always.\n---\nx\n"
    )
    (repo / "commands").mkdir()
    (repo / "commands" / "hello.md").write_text("---\ndescription: Say hi\n---\nHi\n")
    pico = tmp_path / "picoclaw"
    return {"home": home, "proj": proj, "repo": repo, "pico": pico, "tmp": tmp_path}


def pico_config(env, **extra):
    data = {
        "repository_path": str(env["repo"]),
        "platforms": {
            "picoclaw": {
                "skills_dir": str(env["pico"] / "skills"),
                "commands_dir": str(env["pico"] / "commands"),
                "project_skills_dir": "workspace/skills",
            }
        },
    }
    data.update(extra)
    return write_config(env["home"], data)


def run(*args, ok=True):
    r = CliRunner().invoke(cli, list(args))
    if ok:
        assert r.exit_code == 0, r.output
    return r


# --- config ---------------------------------------------------------------


def test_custom_platform_paths(env):
    pico_config(env)
    c = Config()
    assert "picoclaw" in c.known_platforms()
    assert c.get_skills_dir("personal", "picoclaw") == env["pico"] / "skills"
    assert str(c.get_skills_dir("project", "picoclaw")) == "workspace/skills"
    with pytest.raises(PlatformConfigError, match="project_commands_dir"):
        c.get_commands_dir("project", "picoclaw")
    with pytest.raises(PlatformConfigError, match="hooks_dir"):
        c.get_hooks_dir("personal", "picoclaw")


def test_unknown_platform_errors_instead_of_falling_back(env):
    c = Config()
    with pytest.raises(InvalidPlatformError, match="typo"):
        c.get_skills_dir("personal", "typo")
    with pytest.raises(InvalidPlatformError):
        validate_platform("pico/../etc", {"pico/../etc"})


def test_builtin_paths_unchanged(env):
    c = Config()
    assert str(c.get_skills_dir("project", "opencode")) == ".claude/skills"
    assert c.get_skills_dir("personal", "opencode").name == "skills"
    assert str(c.get_settings_file("project")) == ".claude/settings.json"


def test_default_platform(env):
    pico_config(env, default_platform="picoclaw")
    c = Config()
    assert c.resolve_platform() == "picoclaw"
    assert c.resolve_platform("claude") == "claude"
    assert c.explicit_default_platform() == "picoclaw"


def test_saved_full_config_is_not_an_override(env):
    c = Config()
    c.set_alias("k", "o/r")  # save_config() writes every default to disk
    c = Config()
    assert c.explicit_default_platform() is None
    assert c.platform_overrides() == {}


def test_defaults_not_mutated(env):
    before = copy.deepcopy(Config.DEFAULT_CONFIG)
    Config().set_alias("k", "o/r")
    assert Config.DEFAULT_CONFIG == before


# --- install / list / uninstall (local repository) -------------------------


def test_install_to_custom_platform(env):
    pico_config(env)
    run("install", "sample", "--platform", "picoclaw", "--force")
    assert (env["pico"] / "skills" / "sample" / "SKILL.md").exists()
    run("install", "hello", "--platform", "picoclaw", "--force")
    assert (env["pico"] / "commands" / "hello.md").exists()
    assert (
        "sample" in run("list", "--source", "installed", "-p", "picoclaw", "-t", "personal").output
    )


def test_install_uses_default_platform(env):
    pico_config(env, default_platform="picoclaw")
    run("install", "sample", "--force")
    assert (env["pico"] / "skills" / "sample").exists()
    assert not (env["home"] / ".claude" / "skills" / "sample").exists()


def test_install_unknown_platform_fails(env):
    pico_config(env)
    r = run("install", "sample", "--platform", "typo", "--force", ok=False)
    assert r.exit_code != 0
    assert "Invalid platform 'typo'" in r.output and "picoclaw" in r.output
    assert not (env["home"] / ".claude" / "skills" / "sample").exists()


def test_hooks_install_needs_configured_dir(env):
    pico_config(env)
    hook = env["repo"] / "hooks" / "fmt"
    hook.mkdir(parents=True)
    (hook / "HOOK.md").write_text("---\nname: fmt\ndescription: d\nevent: Stop\n---\n")
    (hook / "hook.py").write_text("print(1)\n")
    r = run("hooks", "install", "fmt", "-p", "picoclaw", "-y", ok=False)
    assert r.exit_code != 0 and "platforms.picoclaw.hooks_dir" in r.output


# --- skillin add -----------------------------------------------------------

needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


@needs_git
def test_add_to_custom_platform_copies(env):
    pico_config(env)
    run("add", str(env["repo"]), "-s", "sample", "-a", "picoclaw", "-y")
    project_copy = env["proj"] / "workspace" / "skills" / "sample"
    assert (project_copy / "SKILL.md").exists() and not project_copy.is_symlink()
    assert not (env["proj"] / ".agents").exists()  # no canonical copy needed

    run("add", str(env["repo"]), "-s", "sample", "-a", "picoclaw", "-g", "-y")
    global_copy = env["pico"] / "skills" / "sample"
    assert (global_copy / "SKILL.md").exists() and not global_copy.is_symlink()

    run("remove", "sample", "-g", "-y")
    assert not global_copy.exists()


@needs_git
def test_add_mixed_agents_links_builtin_and_copies_custom(env):
    pico_config(env)
    run("add", str(env["repo"]), "-s", "sample", "-a", "claude-code", "-a", "picoclaw", "-y")
    assert (env["proj"] / ".claude" / "skills" / "sample").is_symlink()
    assert not (env["proj"] / "workspace" / "skills" / "sample").is_symlink()


@needs_git
def test_add_uses_default_platform(env):
    pico_config(env, default_platform="picoclaw")
    run("add", str(env["repo"]), "-s", "sample", "-g", "-y")
    assert (env["pico"] / "skills" / "sample").exists()
    assert not (env["home"] / ".claude" / "skills" / "sample").exists()


@needs_git
def test_add_custom_platform_without_project_dir(env):
    write_config(env["home"], {"platforms": {"pico": {"skills_dir": str(env["pico"])}}})
    r = run("add", str(env["repo"]), "-s", "sample", "-a", "pico", "-y", ok=False)
    assert r.exit_code != 0 and "project_skills_dir" in r.output


@needs_git
def test_add_override_builtin_global_dir(env):
    custom = env["tmp"] / "my-claude-skills"
    write_config(env["home"], {"platforms": {"claude": {"skills_dir": str(custom)}}})
    run("add", str(env["repo"]), "-s", "sample", "-a", "claude", "-g", "-y")
    assert (custom / "sample").is_symlink()  # built-ins keep symlinking


@needs_git
def test_add_unknown_agent(env):
    r = run("add", str(env["repo"]), "-s", "sample", "-a", "typo", "-y", ok=False)
    assert r.exit_code != 0 and "Unknown agent 'typo'" in r.output


@needs_git
def test_upgrade_updates_custom_copy(env):
    subprocess.run(["git", "init", "-q"], cwd=env["repo"], check=True)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "."], cwd=env["repo"], check=True)
    subprocess.run([*git, "commit", "-qm", "i"], cwd=env["repo"], check=True)
    pico_config(env)
    url = f"file://{env['repo']}"
    run("add", url, "-s", "sample", "-a", "picoclaw", "-g", "-y")
    (env["repo"] / "skills" / "sample" / "SKILL.md").write_text(
        "---\nname: sample\ndescription: A sample. Use always.\n---\nnew\n"
    )
    subprocess.run([*git, "commit", "-qam", "c"], cwd=env["repo"], check=True)
    assert "updated" in run("upgrade", "-g").output
    assert "new" in (env["pico"] / "skills" / "sample" / "SKILL.md").read_text()
