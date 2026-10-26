# Creating a compatible skill repository

This guide is for authors who want to publish their own skills in a git repository
so that anyone can install them with one command:

```bash
uvx skillin add your-name/your-repo --skill my-skill
```

A repository that follows this guide also works with:

- [`npx skills`](https://github.com/vercel-labs/skills), using the same layout, install
  locations and lock files;
- any agent that implements the [Agent Skills specification](https://agentskills.io/specification),
  including Claude Code, VS Code (GitHub Copilot), Codex, OpenCode, Gemini CLI and Cursor.

There is no registry to sign up for. A public git repository is enough.

## Quick start

**1. Create the skill.** Make a directory whose name matches the skill's `name`, with a
`SKILL.md` inside:

```
your-repo/
└── skills/
    └── pdf-tables/
        └── SKILL.md
```

```markdown
---
name: pdf-tables
description: Extracts tables from PDF files into CSV or pandas DataFrames. Use when the
  user provides a PDF and asks for its tables, numbers or data, or wants to convert a
  PDF table to a spreadsheet.
---

# PDF tables

1. Try `pdfplumber` first: ...
2. If the PDF is scanned, ...
```

**2. Validate it.** This checks the spec rules and how installers will see your repo:

```bash
uvx skillin validate .
```

**3. Try installing it from your working copy** into a scratch project:

```bash
mkdir /tmp/try && cd /tmp/try
uvx skillin add ~/path/to/your-repo --list
uvx skillin add ~/path/to/your-repo --skill pdf-tables
ls -l .claude/skills .agents/skills
```

**4. Push it, then share the install line**, for example in your README:

```markdown
uvx skillin add your-name/your-repo --skill pdf-tables
# or: npx skills add your-name/your-repo --skill pdf-tables
```

**5. Help people find it.** Add the `agent-skills` topic to the GitHub repository. See
[Sharing and discovery](#sharing-and-discovery).

Until `skillin` is on PyPI, replace `uvx skillin` with
`uvx --from git+https://github.com/jkitchin/skillz skillin`.

## Choosing a layout

All of these layouts are discovered automatically.

| Layout | Use it for | Users install with |
|---|---|---|
| `SKILL.md` at the repo root | A repo that is a single skill | `skillin add you/pdf-tables` |
| `skills/<name>/SKILL.md` | A collection (recommended) | `skillin add you/repo -s <name>` |
| `skills/<category>/<name>/SKILL.md` | Large collections, up to 3 levels inside `skills/` | `skillin add you/repo -s <name>` |
| `<name>/SKILL.md` | A small collection without a `skills/` folder | `skillin add you/repo -s <name>` |
| `tools/agents/skills/<name>/SKILL.md` | Skills inside a larger project | `skillin add you/repo/tools/agents/skills -s <name>` |
| `.claude-plugin/marketplace.json` | Repos that are also Claude Code plugins | `skillin add you/repo -s <name>` |

Things to avoid:

- **A `SKILL.md` at the root of a multi-skill repo.** If the root has one, installers only
  offer that skill and ignore the rest.
- **Skills nested inside other skills.** Discovery stops at the first `SKILL.md` it finds,
  so `skills/a/SKILL.md` hides `skills/a/b/SKILL.md`.
- **Deeply buried skills.** Anything deeper than the limits above, or outside the known
  folders, is only found as a last resort, or with `--full-depth`.
- **Two skills with the same `name`.** Only the first one found can be installed.

`skillin validate` reports each of these.

## Writing SKILL.md

`SKILL.md` is YAML frontmatter followed by Markdown instructions.

### Frontmatter

| Field | Required | Rules |
|---|---|---|
| `name` | yes | 1-64 characters: `a-z`, `0-9` and single hyphens, not at the start or end. Must match the directory name. |
| `description` | yes | 1-1024 characters. What the skill does **and when to use it**. |
| `license` | no | A license name (`MIT`) or the name of a bundled file (`LICENSE.txt`). |
| `compatibility` | no | Up to 500 characters of environment requirements, e.g. `Requires Python 3.11+ and uv`. Most skills don't need it. |
| `metadata` | no | A map of string keys to **string** values. Quote numbers: `version: "1.0"`. |
| `allowed-tools` | no | Experimental. A space-separated string of pre-approved tools: `Read Grep Bash(git:*)`. |

Other fields are allowed but agent-specific. For example, Claude Code reads `model`; other
agents ignore it. Installers copy the frontmatter unchanged.

To hide a work-in-progress skill from `--list` and `--all`, add `internal: true` under
`metadata`, as a YAML boolean, which is what `npx skills` checks for. It can still be
installed by name.

### The description is the trigger

Agents load only `name` and `description` for every installed skill, about 100 tokens
each. They read the rest of SKILL.md only after deciding the skill is relevant. A vague
description means the skill never gets used.

- Say **what** the skill does and **when** to use it, with the words a user would
  actually type: file types, tool names, task names.
- Be specific and assertive: "Use when the user mentions PDFs, forms, or extracting
  tables."

Poor:

```yaml
description: Helps with PDFs.
```

Good:

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges PDFs.
  Use when working with PDF documents or when the user mentions PDFs, forms, or
  document extraction.
```

### Instructions

The body has no required format. What works well is step-by-step instructions, worked
examples of inputs and outputs, and the edge cases you have already tripped over. Write
for an agent that is capable but new to your domain.

## Structuring a skill

```
pdf-tables/
├── SKILL.md            # required: under 500 lines (~5000 tokens)
├── scripts/            # code the agent runs
│   └── extract.py
├── references/         # detail the agent reads only when needed
│   └── SCANNED_PDFS.md
└── assets/             # templates, schemas, example data
    └── output-template.csv
```

- **Progressive disclosure.** Keep SKILL.md focused, and move long reference material
  into `references/` with a link and a sentence saying when to read it. Agents load those
  files on demand, so they cost nothing until they're needed.
- **Use relative paths from the skill directory**, like `[guide](references/SCANNED_PDFS.md)`
  or `scripts/extract.py`, and keep references one level deep. Never assume where the skill
  is installed. It may be `.claude/skills/pdf-tables`, `~/.agents/skills/pdf-tables` or
  somewhere else.
- **Keep everything inside the skill directory.** Installers copy only that folder, so a
  link to `../shared/thing.md` breaks once installed. Duplicate shared files into each
  skill, or symlink the individual files (not directories) from inside the repo; they are
  copied as real files.
- **Scripts** should be self-contained or list their dependencies. A
  [PEP 723](https://peps.python.org/pep-0723/) header plus `uv run scripts/extract.py`
  works well for Python. Print helpful errors, and commit the executable bit
  (`git update-index --chmod=+x scripts/extract.py`); installs preserve it.

## What happens when someone installs your skill

`skillin add` (and `npx skills add`) clones your repository shallowly, finds the skill,
and copies its directory:

- **Directory name.** The installed folder is named from `name`, not from your folder.
  Keeping the two identical avoids confusion.
- **Files not copied:** `.git`, `__pycache__`, `__pypackages__`, `.DS_Store` and
  `metadata.json`. Don't rely on a file called `metadata.json`.
- **Symlinks.** A symlink to a *file* inside your repository is copied as the real file.
  Symlinks to directories, and symlinks pointing outside the repository, are skipped.
- **Git LFS files are not downloaded.** Users get the small pointer file. Keep large
  binaries out of skills, or have a script download them on first use.
- **Size.** Skills are copied for every install, so keep them small. `skillin validate`
  warns about files over 10 MB.
- **Locations:**

| | Project (default) | Global (`-g`) |
|---|---|---|
| Canonical copy | `.agents/skills/<name>` | `~/.agents/skills/<name>` |
| Claude Code | `.claude/skills/<name>`, a symlink to the canonical copy | `~/.claude/skills/<name>`, a symlink |
| Lock file | `skills-lock.json` (users commit it) | `~/.agents/.skill-lock.json` |

VS Code, Codex, OpenCode, Gemini CLI, Cursor and GitHub Copilot read `.agents/skills` directly.
Users can pass `--copy` to get real copies instead of symlinks, and `-a/--agent` to choose
which agents to install for.

## Versioning and updates

- **Pinning.** Users can pin a branch, tag or commit with `#`:
  `skillin add you/repo#v1.2 -s pdf-tables`. Tag releases if people depend on your skills.
- **Updates.** `skillin check` and `skillin upgrade` (and `npx skills update`) compare a
  hash of the installed skill's folder with your repository's. Any change to any file in
  the folder counts as an update. Changes elsewhere in the repo don't.
- **Keep `name` stable.** Installs are tracked by name, so renaming a skill makes it a
  different skill and the old one shows as "missing upstream". Moving the folder within
  the repo is fine.
- **Versions.** Record a version in `metadata` as a string (`version: "1.2"`), and keep a
  changelog in the README if your users care.

## Validate in CI

`skillin validate` checks every `SKILL.md` against the spec. It also checks how
installers will see the repo: hidden or duplicate skills, broken relative links, files
dropped on install, Git LFS pointers and oversized files. It exits with status 1 on
errors; `--strict` also fails on warnings.

```bash
uvx skillin validate .            # errors fail; warnings are advice
uvx skillin validate . --strict   # treat warnings as errors
```

GitHub Actions (`.github/workflows/validate-skills.yml`):

```yaml
name: Validate skills
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v5
      - run: uvx skillin validate .
```

Before the PyPI release, use `uvx --from git+https://github.com/jkitchin/skillz skillin validate .`.
The spec's reference validator, [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)
(`skills-ref validate ./my-skill`), checks frontmatter only.

## Commands, subagents, hooks and MCP servers

`npx skills` only knows about skills. `skillin` can also install these items for
Claude Code from the same repository:

| Type | Put it in | Install with | Installed to (`.claude/` or `~/.claude/` with `-g`) |
|---|---|---|---|
| Slash command | `commands/**/<name>.md` | `--command <name>` | `commands/<name>.md` |
| Subagent | `agents/**/*.md` (frontmatter `name`, `description`) | `--subagent <name>` | `agents/<name>.md` |
| Hook | `hooks/<name>/HOOK.md` + `hook.py`/`hook.sh` | `--hook <name>` | `hooks/<name>/` plus an entry in `settings.json` |
| MCP server | `.mcp.json` or `mcp/*.json` (`{"mcpServers": {...}}`) | `--mcp <name>` | `./.mcp.json`, or `claude mcp add-json --scope user` with `-g` |

- The same locations under `.claude/` (for example `.claude/commands/`) are searched too.
- `README.md` and `TEMPLATE.md` files are ignored.
- Hooks need `name`, `description` and a valid `event` in `HOOK.md`.
- Hooks and MCP servers run code on the user's machine. They must be requested by name
  (`*` is not accepted), and their scripts or config are shown for review before
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

Never commit secrets. Use `${VAR}` references, which Claude Code expands from the
user's environment.

## Sharing and discovery

- Put the install command near the top of your README, and list your skills with their
  descriptions. `uvx skillin add your-name/your-repo --list` prints that table.
- Add the `agent-skills` topic to your GitHub repository. `skillin find` falls back to
  searching it.
- [skills.sh](https://skills.sh) indexes public skills. `skillin find` and `npx skills find`
  search it first.
- Choose a license (the `license` field and/or a `LICENSE` file) so people know they may
  use your skills.

## Checklist

- [ ] Each skill is in its own directory, named exactly like its `name`
- [ ] `name` is lowercase with single hyphens, and unique in the repo
- [ ] `description` says what the skill does and when to use it
- [ ] SKILL.md is under 500 lines; details live in `references/`
- [ ] Links and script paths are relative and stay inside the skill directory
- [ ] No secrets, no Git LFS files, no `metadata.json`, no large binaries
- [ ] `uvx skillin validate .` passes, ideally in CI
- [ ] The README shows the install command; the repo has the `agent-skills` topic and a license

## Reference

### Discovery order

`skillin add` searches in the same order as `npx skills`:

1. A `SKILL.md` at the repo root, or at the subpath given. If one exists, only that skill is used.
2. Direct children of the repo root (`my-skill/SKILL.md`).
3. Up to three levels inside `skills/`, `skills/.curated`, `skills/.experimental`,
   `skills/.system`, and agent directories such as `.claude/skills` and `.agents/skills`.
4. Skill paths declared in `.claude-plugin/marketplace.json` or `.claude-plugin/plugin.json`.
5. If nothing was found, a recursive search up to five levels deep. `--full-depth`
   always runs this search.

### Source syntax

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

Private repositories work wherever `git clone` works for the user (SSH keys or a git
credential helper). For global GitHub installs, `skillin check` uses the GitHub API instead
of cloning. Setting `GITHUB_TOKEN` avoids rate limits.
