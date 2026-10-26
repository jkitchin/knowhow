"""Tests for `skillpack validate` and the Agent Skills spec checks."""

from click.testing import CliRunner

from skillpack.main import cli
from skillpack.spec import check_repo, check_skill
from skillpack.validator import SkillValidator

GOOD = """---
name: {name}
description: Extracts tables from PDFs. Use when the user mentions PDFs or tables.
license: MIT
metadata:
  author: someone
  version: "1.0"
allowed-tools: Read Grep Bash(git:*)
---

# PDF tables

See [the reference](references/REFERENCE.md).
"""


def make(path, text=None, name=None):
    name = name or path.name
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(text if text is not None else GOOD.format(name=name))
    return path


def messages(findings, level=None):
    return [f.message for f in findings if level is None or f.level == level]


def test_good_skill_is_clean(tmp_path):
    skill = make(tmp_path / "skills" / "pdf-tables")
    (skill / "references").mkdir()
    (skill / "references" / "REFERENCE.md").write_text("ref")
    assert check_skill(skill, tmp_path) == []


def test_name_rules(tmp_path):
    for bad in ("PDF-tables", "-pdf", "pdf-", "pdf--tables", "a" * 65):
        skill = make(tmp_path / bad[:60], name=bad)
        errors = messages(check_skill(skill, tmp_path), "error")
        assert any("'name'" in m for m in errors), bad


def test_name_must_match_directory(tmp_path):
    skill = make(tmp_path / "skills" / "folder", name="other-name")
    assert any("does not match" in m for m in messages(check_skill(skill, tmp_path), "error"))
    # ...but only a warning for a single-skill repo whose root is the skill
    (tmp_path / ".git").mkdir()
    make(tmp_path, name="my-skill")
    findings, _ = check_repo(tmp_path)
    root = [f for f in findings if f.path == "SKILL.md" and "does not match" in f.message]
    assert root and root[0].level == "warning"


def test_missing_and_invalid_frontmatter(tmp_path):
    skill = make(tmp_path / "a", text="# no frontmatter\n")
    assert messages(check_skill(skill, tmp_path), "error")
    skill = make(tmp_path / "b", text="---\nname: b\n---\nbody\n")
    assert any("description" in m for m in messages(check_skill(skill, tmp_path), "error"))
    skill = make(tmp_path / "c", text="---\nname: [c\n---\n")
    assert any("YAML" in m for m in messages(check_skill(skill, tmp_path), "error"))


def test_field_warnings(tmp_path):
    text = (
        "---\nname: x\ndescription: Does things\nmetadata:\n  version: 1.0\n"
        "allowed-tools: [Read]\nmodel: opus\n---\nbody\n"
    )
    found = " ".join(messages(check_skill(make(tmp_path / "x", text=text), tmp_path), "warning"))
    for expected in ("when to use", "quote version", "space-separated", "not in the Agent"):
        assert expected in found


def test_body_size_and_links(tmp_path):
    body = "\n".join(f"line {i}" for i in range(600))
    body += "\n[missing](refs/nope.md) [web](https://x.y) [up](../outside.md)\n"
    body += "```\n![](in-code.png)\n```\n"
    text = GOOD.format(name="big").split("# PDF")[0] + body
    found = " ".join(messages(check_skill(make(tmp_path / "big", text=text), tmp_path)))
    assert "lines; keep it under 500" in found
    assert "refs/nope.md" in found
    assert "outside the skill" in found
    assert "https" not in found and "in-code.png" not in found


def test_install_hazards(tmp_path):
    skill = make(tmp_path / "skills" / "h")
    (skill / "metadata.json").write_text("{}")
    (skill / "data.bin").write_text("version https://git-lfs.github.com/spec/v1\noid sha256:x\n")
    outside = tmp_path.parent / f"{tmp_path.name}-secret.txt"
    outside.write_text("s")
    (skill / "leak").symlink_to(outside)
    found = " ".join(messages(check_skill(skill, tmp_path)))
    assert "not copied" in found and "LFS" in found and "outside the repository" in found


def test_repo_duplicates_and_hidden_skills(tmp_path):
    make(tmp_path / "skills" / "a" / "dup", name="dup")
    make(tmp_path / "skills" / "b" / "dup", name="dup")
    make(tmp_path / "skills" / "outer")
    make(tmp_path / "skills" / "outer" / "inner")  # hidden by its parent skill
    findings, n = check_repo(tmp_path)
    assert n == 4
    assert any("Duplicate name 'dup'" in m for m in messages(findings, "error"))
    hidden = [f for f in findings if "Not discovered" in f.message]
    assert [f.path for f in hidden] == ["skills/outer/inner/SKILL.md"]


def test_no_skills(tmp_path):
    findings, n = check_repo(tmp_path)
    assert n == 0 and messages(findings, "error")


def test_cli_exit_codes(tmp_path):
    make(
        tmp_path / "skills" / "pdf-tables",
        text=GOOD.format(name="pdf-tables").replace(
            "See [the reference](references/REFERENCE.md).", "Body."
        ),
    )
    runner = CliRunner()
    r = runner.invoke(cli, ["validate", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert "1 skill(s)" in r.output

    (tmp_path / "skills" / "pdf-tables" / "SKILL.md").write_text(
        "---\nname: pdf-tables\ndescription: Tables. Use when needed.\nmodel: x\n---\nok\n"
    )
    assert runner.invoke(cli, ["validate", str(tmp_path)]).exit_code == 0
    assert runner.invoke(cli, ["validate", str(tmp_path), "--strict"]).exit_code == 1

    make(tmp_path / "skills" / "Bad", name="Bad")
    assert runner.invoke(cli, ["validate", str(tmp_path)]).exit_code == 1


def test_strict_validator_accepts_spec_allowed_tools(tmp_path):
    skill = make(tmp_path / "pdf-tables")
    valid, errors = SkillValidator.validate_skill_directory(skill)
    assert valid, errors
    (skill / "SKILL.md").write_text(
        "---\nname: pdf-tables\ndescription: d\nallowed-tools: Read Nope\n---\n"
    )
    valid, errors = SkillValidator.validate_skill_directory(skill)
    assert not valid and errors == ["Unknown tool: Nope"]
