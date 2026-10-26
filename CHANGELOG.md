# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Breaking:** an unknown `--platform` name is now an error listing the valid ones. Previously it silently installed into the Claude directories (#6).
- `--platform` defaults to `default_platform` from the config, which was previously ignored. `skillin add` uses it too when it's set to something other than `claude`; otherwise `add` still auto-detects agents (#6).
- Renamed the tool to **skillin**, because the name `skillz` on PyPI belongs to an unrelated project. The Python package `cli` is now `skillin`. The `skillz` command remains as an alias, and the config path `~/.config/skillz` is unchanged.

### Added
- Custom platforms (#6): any name under `platforms:` in config.yaml works with `--platform` and `skillin add -a`. `skillin add` copies skills into its `skills_dir` / `project_skills_dir`. Commands that need an unconfigured directory say which key to set. Changed paths for built-in platforms override `skillin add`'s defaults.
- `skillin add <source>`: install skills from GitHub/GitLab/any git URL/local path without installing skillin (`uvx skillin add owner/repo --skill name`). Layout, install paths (`.agents/skills` + symlinks) and lock files are compatible with `npx skills`.
- `--command`, `--subagent`, `--hook` and `--mcp` install slash commands, subagents, hooks and MCP servers for Claude Code. Hooks and MCP servers are previewed and must be confirmed.
- `skillin remove`, `check`, `upgrade` and `find` (skills.sh / GitHub search); source aliases via `skillin config set alias.NAME SOURCE`.
- `docs/publishing-skills.md`: a guide to creating skill repositories compatible with skillin, `npx skills` and the Agent Skills spec. Also a PyPI publish workflow.
- `skillin validate [PATH]`: checks skills against the Agent Skills spec and against how installers will see the repo (hidden or duplicate skills, broken links, files dropped on install, Git LFS pointers). Exits non-zero on errors; `--strict` also fails on warnings.
- The strict `SkillValidator` accepts the spec's space-separated `allowed-tools` string, scoped tools like `Bash(git:*)` and `mcp__*` tools.

### Fixed
- Skills installed as symlinks are now seen by `list`, `search`, `stats`, `optimize` and `merge`.
- Initial release of Claude Skills CLI tool
- Complete CLI for managing skills and commands
- 6 initial skills:
  - `python-ase`: Atomic Simulation Environment helper
  - `python-best-practices`: Python coding standards
  - `emacs-lisp`: Emacs Lisp development assistant
  - `fairchem`: Fair chemistry tools
  - `eln`: Electronic lab notebook management
  - `phd-qualifier`: PhD qualifier review
- Commands: install, uninstall, list, search, info, update, create
- Validation system for skills and commands
- Multi-platform support (Claude, Codex, Gemini)
- Configuration management
- Template system for creating new skills/commands
- Comprehensive test suite (44 tests)

## [0.1.0] - 2024-11-05

### Added
- Initial project structure
- Basic CLI framework with Click
- Configuration system with YAML
- Skill and command validators
- File operations utilities
- Rich terminal output
- MIT License
- Documentation (README.md, CONTRIBUTING.md)

[Unreleased]: https://github.com/jkitchin/skillz/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jkitchin/skillz/releases/tag/v0.1.0
