"""MCP servers across agents (Claude Code, VS Code, Cursor, Codex, Gemini, OpenCode, ...)."""

import json
import os
import shutil
import sys

import pytest
from click.testing import CliRunner

from knowhow import mcp_targets as mt
from knowhow.main import cli

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")

STDIO = {"command": "npx", "args": ["-y", "srv", "--key=${KEY}"], "env": {"TOKEN": "${TOKEN}"}}
HTTP = {"type": "http", "url": "https://x.dev/mcp", "headers": {"Authorization": "Bearer ${KEY}"}}


# --- shapes ------------------------------------------------------------------


def shaped(agent, cfg, global_=False):
    return mt.TARGETS[agent].config(cfg, global_)


def test_shapes_and_placeholders():
    assert shaped("claude-code", STDIO) == STDIO
    assert shaped("vscode", STDIO)["type"] == "stdio"
    assert shaped("vscode", STDIO)["env"] == {"TOKEN": "${env:TOKEN}"}
    assert shaped("cursor", HTTP) == {
        "url": "https://x.dev/mcp",
        "headers": {"Authorization": "Bearer ${env:KEY}"},
    }
    oc = shaped("opencode", STDIO)
    assert oc["type"] == "local" and oc["command"] == ["npx", "-y", "srv", "--key={env:KEY}"]
    assert oc["environment"] == {"TOKEN": "{env:TOKEN}"}
    assert shaped("opencode", HTTP)["type"] == "remote"
    assert shaped("gemini-cli", HTTP)["httpUrl"] == "https://x.dev/mcp"
    assert shaped("gemini-cli", {**HTTP, "type": "sse"})["url"] == "https://x.dev/mcp"
    assert shaped("windsurf", HTTP)["serverUrl"] == "https://x.dev/mcp"
    assert shaped("github-copilot", STDIO, global_=True)["tools"] == ["*"]
    assert "tools" not in shaped("github-copilot", STDIO)


def test_codex_forwards_env_by_name():
    stdio = shaped("codex", STDIO)
    assert stdio["env_vars"] == ["TOKEN"] and "env" not in stdio
    http = shaped("codex", {**HTTP, "headers": {**HTTP["headers"], "X-Org": "${ORG}", "X-A": "b"}})
    assert http["bearer_token_env_var"] == "KEY"
    assert http["env_http_headers"] == {"X-Org": "ORG"}
    assert http["http_headers"] == {"X-A": "b"}
    # `--key=${KEY}` in args can't be expressed for Codex: reported, not hidden
    assert mt.TARGETS["codex"].caveats(STDIO, False)
    assert not mt.TARGETS["codex"].caveats({"command": "x"}, False)


# --- TOML editing -------------------------------------------------------------


def test_toml_append_and_remove_preserve_user_content(tmp_path):
    cfg = tmp_path / "config.toml"
    original = '# keep me\nmodel = "o4"\n\n[mcp_servers.mine]\ncommand = "keep"\n'
    cfg.write_text(original)
    p = mt.Placement(mt.TARGETS["codex"], cfg)
    mt.write(p, "fs", STDIO)
    data = tomllib.loads(cfg.read_text())
    assert data["mcp_servers"]["fs"]["env_vars"] == ["TOKEN"]
    assert data["mcp_servers"]["mine"] == {"command": "keep"}
    assert cfg.read_text().startswith(original)
    mt.write(p, "fs", {"command": "v2"})  # replace, not duplicate
    assert tomllib.loads(cfg.read_text())["mcp_servers"]["fs"] == {"command": "v2", "args": []}
    assert mt.remove(p, "fs")
    assert "fs" not in tomllib.loads(cfg.read_text())["mcp_servers"]
    assert "# keep me" in cfg.read_text() and (tmp_path / "config.toml.bak").exists()
    assert not mt.remove(p, "fs")


def test_toml_refuses_invalid_or_foreign_forms(tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text("not = [valid\n")
    p = mt.Placement(mt.TARGETS["codex"], cfg)
    with pytest.raises(mt.ConfigFileError):
        mt.write(p, "fs", STDIO)
    assert cfg.read_text() == "not = [valid\n"
    cfg.write_text('[mcp_servers]\nfs = { command = "inline" }\n')  # user's own, inline form
    assert mt.exists(p, "fs")
    with pytest.raises(mt.McpTargetError):
        mt.write(p, "fs", STDIO)
    assert cfg.read_text() == '[mcp_servers]\nfs = { command = "inline" }\n'


# --- planning ----------------------------------------------------------------


def test_plan_markers_dedupe_and_notes(tmp_path):
    (tmp_path / ".cursor").mkdir()
    agents = ["claude-code", "github-copilot", "cursor", "vscode", "windsurf", "goose"]
    places, notes = mt.plan(agents, False, tmp_path, explicit=False)
    labels = [(p.target.agent, p.file.name) for p in places]
    # .mcp.json written once for Claude + Copilot; VS Code not set up here -> skipped
    assert labels == [("claude-code", ".mcp.json"), ("cursor", "mcp.json")]
    joined = " ".join(notes)
    assert "VS Code: not set up" in joined and "Windsurf" in joined and "goose" in joined
    places, _ = mt.plan(["vscode"], False, tmp_path, explicit=True)
    assert places[0].file == tmp_path / ".vscode" / "mcp.json"


# --- CLI end to end ------------------------------------------------------------


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
    (repo / ".mcp.json").write_text(json.dumps({"mcpServers": {"fs": STDIO, "web": HTTP}}))
    return {"home": home, "proj": proj, "repo": repo, "log": log}


def run(*args, ok=True):
    r = CliRunner().invoke(cli, list(args))
    if ok:
        assert r.exit_code == 0, r.output
    return r


AGENTS = ["-a", "claude-code", "-a", "vscode", "-a", "cursor", "-a", "codex", "-a", "opencode"]


def test_install_inventory_remove_across_agents(env):
    proj = env["proj"]
    (proj / "opencode.json").write_text('{"theme": "x"}')
    run("add", str(env["repo"]), "--mcp", "fs", *AGENTS, "-y")
    assert json.loads((proj / ".mcp.json").read_text())["mcpServers"]["fs"] == STDIO
    assert "fs" in json.loads((proj / ".vscode" / "mcp.json").read_text())["servers"]
    assert "fs" in json.loads((proj / ".cursor" / "mcp.json").read_text())["mcpServers"]
    assert "fs" in tomllib.loads((proj / ".codex" / "config.toml").read_text())["mcp_servers"]
    oc = json.loads((proj / "opencode.json").read_text())
    assert oc["theme"] == "x" and "fs" in oc["mcp"]

    lock = json.loads((proj / ".claude" / "knowhow-lock.json").read_text())
    assert {t["agent"] for t in lock["mcp"]["fs"]["targets"]} == {
        "claude-code",
        "vscode",
        "cursor",
        "codex",
        "opencode",
    }
    inv = json.loads(run("installed", "-p", "--json").output)
    assert inv[0]["status"] == "ok" and len(inv[0]["paths"]) == 5

    run("remove", "--mcp", "fs", "-y")
    assert json.loads((proj / ".vscode" / "mcp.json").read_text())["servers"] == {}
    assert json.loads((proj / "opencode.json").read_text()) == {"theme": "x", "mcp": {}}
    assert "fs" not in tomllib.loads((proj / ".codex" / "config.toml").read_text()).get(
        "mcp_servers", {}
    )
    assert json.loads(run("installed", "-p", "--json").output) == []


def test_jsonc_target_is_skipped_with_snippet_others_installed(env):
    gemini = env["proj"] / ".gemini" / "settings.json"
    gemini.parent.mkdir()
    gemini.write_text('{\n  // mine\n  "theme": "dark"\n}\n')
    r = run("add", str(env["repo"]), "--mcp", "web", "-a", "gemini-cli", "-a", "cursor", "-y")
    out = " ".join(r.output.split())
    assert "skipped Gemini CLI" in out and '"httpUrl": "https://x.dev/mcp"' in out
    assert gemini.read_text() == '{\n  // mine\n  "theme": "dark"\n}\n'
    assert "web" in json.loads((env["proj"] / ".cursor" / "mcp.json").read_text())["mcpServers"]


def test_conflict_with_users_own_server_in_another_agent(env):
    cursor = env["proj"] / ".cursor" / "mcp.json"
    cursor.parent.mkdir()
    cursor.write_text(json.dumps({"mcpServers": {"fs": {"command": "mine"}}}))
    r = run("add", str(env["repo"]), "--mcp", "fs", "-a", "cursor", "-y", ok=False)
    assert r.exit_code != 0 and "--force" in r.output
    assert json.loads(cursor.read_text())["mcpServers"]["fs"] == {"command": "mine"}


def test_global_install_uses_each_agents_global_file(env):
    run("add", str(env["repo"]), "--mcp", "fs", "-g", "-a", "claude-code", "-a", "cursor", "-y")
    assert "mcp add-json --scope user fs" in env["log"].read_text()
    cursor = env["home"] / ".cursor" / "mcp.json"
    assert json.loads(cursor.read_text())["mcpServers"]["fs"]["env"] == {"TOKEN": "${env:TOKEN}"}
    run("remove", "--mcp", "fs", "-g", "-y")
    assert json.loads(cursor.read_text())["mcpServers"] == {}


def test_failed_removal_keeps_lock_target(env):
    run("add", str(env["repo"]), "--mcp", "fs", "-a", "claude-code", "-a", "cursor", "-y")
    cursor = env["proj"] / ".cursor" / "mcp.json"
    cursor.write_text("{ broken")
    r = run("remove", "--mcp", "fs", "-y")
    assert "Could not remove" in " ".join(r.output.split())
    lock = json.loads((env["proj"] / ".claude" / "knowhow-lock.json").read_text())
    assert [t["agent"] for t in lock["mcp"]["fs"]["targets"]] == ["cursor"]
    assert json.loads((env["proj"] / ".mcp.json").read_text())["mcpServers"] == {}


def test_legacy_lock_entry_removes_from_claude(env):
    (env["proj"] / ".mcp.json").write_text(json.dumps({"mcpServers": {"fs": STDIO}}))
    (env["proj"] / ".claude" / "knowhow-lock.json").parent.mkdir(exist_ok=True)
    (env["proj"] / ".claude" / "knowhow-lock.json").write_text(
        json.dumps({"version": 1, "mcp": {"fs": {"source": "x", "sourceType": "local"}}})
    )
    run("remove", "--mcp", "fs", "-y")
    assert json.loads((env["proj"] / ".mcp.json").read_text())["mcpServers"] == {}
