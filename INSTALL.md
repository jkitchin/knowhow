# Installation Guide

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (recommended), or Python 3.10+ with `pip`/`pipx`
- Git (used to fetch skill repositories)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Option 1: No install (uvx)

Run `skillin` on demand. uv downloads and caches it:

```bash
uvx skillin add jkitchin/skillz --list
uvx skillin add jkitchin/skillz --skill python-ase
```

Before `skillin` is published on PyPI, use the git URL:

```bash
uvx --from git+https://github.com/jkitchin/skillz skillin add jkitchin/skillz --list
```

## Option 2: Install the command

```bash
uv tool install skillin                                   # or: pipx install skillin
uv tool install git+https://github.com/jkitchin/skillz    # before the PyPI release
```

This installs two commands, `skillin` and its alias `skillz`.

## Option 3: Development install

```bash
git clone https://github.com/jkitchin/skillz.git
cd skillz
uv pip install -e ".[dev]"       # or: pip install -e ".[dev]"
pre-commit install
```

To run the local-repository commands (`list`, `install`, `search`, `info`, `update`, `hooks`,
`agents`, and the CASCADE commands) against your clone:

```bash
skillin config set repository "$(pwd)"
```

## Verify

```bash
skillin --version
skillin --help
skillin add jkitchin/skillz --list
```

## Where things are installed

`skillin add` installs into the current project by default, and for your user with `-g`:

| | Project (default) | Global (`-g`) |
|---|---|---|
| Skills (canonical copy) | `.agents/skills/<name>` | `~/.agents/skills/<name>` |
| Skills for Claude Code | `.claude/skills/<name>` (symlink) | `~/.claude/skills/<name>` (symlink) |
| Commands / subagents / hooks | `.claude/commands`, `.claude/agents`, `.claude/hooks` | same under `~/.claude` |
| MCP servers | `./.mcp.json` | `claude mcp add-json --scope user` |
| Lock files | `skills-lock.json`, `.claude/skillin-lock.json` | `~/.agents/.skill-lock.json`, `~/.claude/skillin-lock.json` |

- Codex, OpenCode, Gemini CLI, Cursor and GitHub Copilot read `.agents/skills` directly.
- Choose agents with `-a`, for example `-a claude-code -a codex`.
- Use `--copy` to get real copies instead of symlinks.
- `CLAUDE_CONFIG_DIR`, `CODEX_HOME` and `XDG_CONFIG_HOME` are respected.

The older `skillin install --platform ...` command copies from a local repository into the
per-platform directories set in `~/.config/skillz/config.yaml` (see
[example-config.yaml](example-config.yaml)).

Other agents can be added as **custom platforms** under `platforms:` in the config, then
used with `--platform NAME` or `-a NAME`. Set `default_platform` to use one by default.
Skills are copied, not symlinked, into a custom platform's directories. See
[README: Custom platforms](README.md#custom-platforms).

## Configuration

Configuration lives in `~/.config/skillz/config.yaml`. The path keeps the original name so
existing setups keep working. Everything is optional:

```bash
skillin config set repository /path/to/clone        # for local-repository commands
skillin config set alias.kitchin jkitchin/skillz    # then: skillin add kitchin -s pycse
skillin config get
```

Set `GITHUB_TOKEN` (or `GH_TOKEN`) to raise GitHub API rate limits for `check` and `find`.
Private repositories work wherever `git clone` works for you.

## Troubleshooting

- **`skillin: command not found`**: use `uvx skillin ...`, or make sure `~/.local/bin` (uv
  tool / pipx) is on your `PATH`.
- **`skillz` commands broke after upgrading**: the Python package was renamed from `cli`
  to `skillin`. Reinstall your editable install with `uv pip install -e ".[dev]"`.
- **`No skills found`**: run `skillin add <source> --list` to see what was discovered, and
  `--full-depth` to search every directory. See
  [docs/publishing-skills.md](docs/publishing-skills.md) for the layout rules.
- **`list` shows nothing from the repository**: set the repository path with
  `skillin config set repository /path/to/clone`.
- **A hook or MCP server won't install non-interactively**: these run code, so pass `-y`
  once you have reviewed them.
- **`Refusing to replace items that skillin did not install`**: something with the same
  name already exists, for example your own `.claude/skills/<name>`. Rename or remove it,
  or pass `--force` to replace it.
- **`Not installed by skillin`** from `remove`: the name isn't in a skillin lock file for
  this scope. Add `-g` for global installs, or `--force` to remove it anyway.
- **`... is not valid JSON; skillin will not overwrite it`**: fix the file mentioned
  (often a trailing comma in `settings.json`) and retry. skillin never rewrites a file it
  can't parse.

## Uninstallation

```bash
skillin installed                       # what skillin installed, project + global
skillin remove <skill>                  # or: skillin remove owner/repo  (everything from a source)
skillin remove --command <name> --hook <name> --mcp <name>
skillin remove --all                    # everything skillin installed in this project
skillin remove --all -g                 # ... and for your user
uv tool uninstall skillin               # or: pipx uninstall skillin
rm -rf ~/.config/skillz                 # optional: remove configuration
```

See [README: Seeing and removing what's installed](README.md#seeing-and-removing-whats-installed)
for exactly what each removal deletes.

## Next Steps

- [README.md](README.md): overview and commands
- [docs/publishing-skills.md](docs/publishing-skills.md): make your own skill repository
- [CONTRIBUTING.md](CONTRIBUTING.md): contribute skills to this repository
- [docs/cascade.md](docs/cascade.md): skill evolution commands

## Getting Help

- Check [GitHub Issues](https://github.com/jkitchin/skillz/issues)
- Contact: jkitchin@andrew.cmu.edu
