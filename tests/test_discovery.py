"""Tests for npx-compatible skill discovery."""

import json

from skillin.discovery import discover_skills, install_dir_name


def make_skill(path, name, description="A skill", extra=""):
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n# {name}\n"
    )
    return path


def names(skills):
    return sorted(s.name for s in skills)


def test_root_skill_returns_only_root(tmp_path):
    make_skill(tmp_path, "root-skill")
    make_skill(tmp_path / "skills" / "other", "other")
    assert names(discover_skills(tmp_path)) == ["root-skill"]
    assert names(discover_skills(tmp_path, full_depth=True)) == ["other", "root-skill"]


def test_nested_category_layout(tmp_path):
    make_skill(tmp_path / "skills" / "programming" / "fairchem", "fairchem")
    make_skill(tmp_path / "skills" / "citation-verifier", "citation-verifier")
    skills = discover_skills(tmp_path)
    assert names(skills) == ["citation-verifier", "fairchem"]
    fc = next(s for s in skills if s.name == "fairchem")
    assert fc.skill_md_path == "skills/programming/fairchem/SKILL.md"


def test_agent_dirs_and_root_children(tmp_path):
    make_skill(tmp_path / ".claude" / "skills" / "a", "a")
    make_skill(tmp_path / "b", "b")
    make_skill(tmp_path / "examples" / "deep" / "c", "c")  # too deep for root walk
    assert names(discover_skills(tmp_path)) == ["a", "b"]


def test_fallback_recursive(tmp_path):
    make_skill(tmp_path / "x" / "y" / "z", "deep")
    assert names(discover_skills(tmp_path)) == ["deep"]


def test_name_from_frontmatter_and_duplicates(tmp_path):
    make_skill(tmp_path / "skills" / "dir-a", "same")
    make_skill(tmp_path / "skills" / "dir-b", "same")
    warnings = []
    skills = discover_skills(tmp_path, warnings=warnings)
    assert [s.path.name for s in skills] == ["dir-a"]
    assert any("Duplicate" in w for w in warnings)


def test_lenient_frontmatter(tmp_path):
    # Fields skillin's strict validator would reject are fine for installation
    make_skill(
        tmp_path / "skills" / "x",
        "Mixed Case Name",
        extra="allowed-tools: Read, Bash(git:*)\nlicense: MIT\n",
    )
    (tmp_path / "skills" / "bad").mkdir()
    (tmp_path / "skills" / "bad" / "SKILL.md").write_text("no frontmatter")
    warnings = []
    skills = discover_skills(tmp_path, warnings=warnings)
    assert names(skills) == ["Mixed Case Name"]
    assert install_dir_name(skills[0].name) == "mixed-case-name"
    assert warnings


def test_internal_hidden(tmp_path):
    make_skill(tmp_path / "skills" / "hidden", "hidden", extra="metadata:\n  internal: true\n")
    assert discover_skills(tmp_path) == []
    assert names(discover_skills(tmp_path, include_internal=True)) == ["hidden"]


def test_plugin_manifest(tmp_path):
    make_skill(tmp_path / "plugins" / "p1" / "skills" / "s1", "s1")
    make_skill(tmp_path / "plugins" / "p1" / "extra" / "s2", "s2")
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(
            {"plugins": [{"name": "p1", "source": "./plugins/p1", "skills": ["./extra/s2"]}]}
        )
    )
    skills = discover_skills(tmp_path)
    assert names(skills) == ["s1", "s2"]
    assert {s.plugin_name for s in skills} == {"p1"}


def test_subpath(tmp_path):
    make_skill(tmp_path / "skills" / "a" / "one", "one")
    make_skill(tmp_path / "skills" / "b" / "two", "two")
    assert names(discover_skills(tmp_path, "skills/b")) == ["two"]


def test_install_dir_name():
    assert install_dir_name("../evil") == "evil"
    assert install_dir_name(".hidden") == "hidden"
    assert install_dir_name("") == "unnamed-skill"
