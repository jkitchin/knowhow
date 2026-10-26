# Publishing a skill repository

Any git repository containing `SKILL.md` files can be installed with `skillin`,
with no registry and nothing to install first:

```bash
uvx skillin add your-name/your-repo --list
uvx skillin add your-name/your-repo --skill my-skill
```

The layout rules are the same as [`npx skills`](https://github.com/vercel-labs/skills),
so a repository that works with one tool works with the other.

## Minimal skill

```
my-skill/
└── SKILL.md
```

```markdown
---
name: my-skill
description: What the skill does and when the agent should use it.
---

# My Skill

Instructions for the agent...
```

- `name` and `description` are required and must be strings.
- The installed directory name comes from `name` (lowercased, other characters
  turned into hyphens), not from the folder name.
- Other frontmatter fields (`allowed-tools`, `license`, `metadata`, ...) are
  passed through untouched.
- `metadata.internal: true` hides a skill from listings and `--all`; it can
  still be installed by name.

## Where skills are found

`skillin add` searches, in order:

1. A `SKILL.md` at the repo root or the subpath you gave. If one exists, only that skill is used.
2. Direct children of the repo root (`my-skill/SKILL.md`).
3. Up to three levels inside `skills/`, `skills/.curated`, `skills/.experimental`,
   `skills/.system`, and agent directories such as `.claude/skills` and
   `.agents/skills`. This covers category layouts like `skills/<category>/<name>/SKILL.md`.
4. Skill paths declared in `.claude-plugin/marketplace.json` or `.claude-plugin/plugin.json`.
5. If nothing was found, a recursive search up to five levels deep.

Use `--full-depth` to always run the recursive search. If two skills share a
`name`, the first one found wins and a warning is printed.

## Source syntax

| Source | Meaning |
|---|---|
| `owner/repo` | GitHub repository |
| `owner/repo/skills/foo` | Subdirectory of a repository |
| `owner/repo@my-skill` | Just one skill |
| `owner/repo#v1.2` | Branch, tag or commit |
| `https://github.com/o/r/tree/main/skills/foo` | GitHub URL |
| `https://gitlab.com/g/r/-/tree/main/skills` | GitLab URL |
| `git@host:o/r.git`, `https://host/r.git` | Any git URL |
| `./path`, `/abs/path` | Local directory |
| `myalias` | Alias set with `skillin config set alias.myalias owner/repo` |

Private repositories work whenever `git clone` works for you (SSH keys or a git credential helper).

## Testing your repository

```bash
uvx skillin add ./my-repo --list          # what will be discovered
uvx skillin add ./my-repo -s my-skill --dry-run
```

## Commands, subagents, hooks and MCP servers

`npx skills` only knows about skills. `skillin` can also install these items for
Claude Code from the same repository:

| Type | Put it in | Install with | Installed to (`.claude/` or `~/.claude/` with `-g`) |
|---|---|---|---|
| Slash command | `commands/**/<name>.md` | `--command <name>` | `commands/<name>.md` |
| Subagent | `agents/**/*.md` (frontmatter `name`, `description`) | `--subagent <name>` | `agents/<name>.md` |
| Hook | `hooks/<name>/HOOK.md` + `hook.py`/`hook.sh` | `--hook <name>` | `hooks/<name>/` plus an entry in `settings.json` |
| MCP server | `.mcp.json` or `mcp/*.json` (`{"mcpServers": {...}}`) | `--mcp <name>` | `./.mcp.json`, or `claude mcp add-json --scope user` with `-g` |

The same locations under `.claude/` (for example `.claude/commands/`) are searched too.
`README.md` and `TEMPLATE.md` files are ignored. Hooks must pass skillin's `HOOK.md`
validation, which requires `name`, `description` and a valid `event`.

Hooks and MCP servers run code on the user's machine. They must be requested by
name (`*` is not accepted), and their scripts or config are shown for review before
installing. Non-interactive installs need `-y`.

An MCP server entry is a standard Claude Code server config. An optional `description`
is shown in listings and stripped on install:

```json
{
  "mcpServers": {
    "my-server": {
      "description": "What it does",
      "command": "uvx",
      "args": ["my-mcp-server"],
      "env": {"API_KEY": "${MY_API_KEY}"}
    }
  }
}
```

Don't put secrets in the repository. Use `${VAR}` references, which Claude Code
expands from the environment.

## Where skills are installed

| | Project (default) | Global (`-g`) |
|---|---|---|
| Canonical copy | `.agents/skills/<name>` | `~/.agents/skills/<name>` |
| Claude Code | `.claude/skills/<name>` → symlink | `~/.claude/skills/<name>` → symlink |
| Lock file | `skills-lock.json` (commit it) | `~/.agents/.skill-lock.json` |

Codex, OpenCode, Gemini CLI, Cursor and Copilot read `.agents/skills` directly.
Pass `--copy` for real copies instead of symlinks, and `-a/--agent` to choose agents.
`skillin check` reports upstream changes, and `skillin upgrade` applies them. For global
GitHub skills, `check` asks the GitHub API for folder hashes instead of cloning; set
`GITHUB_TOKEN` to avoid rate limits. The skill lock files use the same format as
`npx skills`. Commands, subagents, hooks and MCP servers are tracked in
`.claude/skillin-lock.json` (or `~/.claude/skillin-lock.json`).

## Being found

`skillin find <query>` searches the [skills.sh](https://skills.sh) index (the one
`npx skills find` uses) and falls back to GitHub repositories with the
`agent-skills` topic. Add that topic to your repository.
