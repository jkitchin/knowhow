"""Tests for source specifier parsing."""

import pytest

from skillin.sources import SourceError, parse_source


@pytest.mark.parametrize(
    "spec,type_,url,ref,subpath,skill",
    [
        ("jkitchin/skillz", "github", "https://github.com/jkitchin/skillz.git", None, None, None),
        (
            "jkitchin/skillz/skills/programming",
            "github",
            "https://github.com/jkitchin/skillz.git",
            None,
            "skills/programming",
            None,
        ),
        (
            "jkitchin/skillz@fairchem",
            "github",
            "https://github.com/jkitchin/skillz.git",
            None,
            None,
            "fairchem",
        ),
        (
            "jkitchin/skillz#dev@fairchem",
            "github",
            "https://github.com/jkitchin/skillz.git",
            "dev",
            None,
            "fairchem",
        ),
        ("github:o/r", "github", "https://github.com/o/r.git", None, None, None),
        (
            "https://github.com/o/r/tree/main/skills/foo",
            "github",
            "https://github.com/o/r.git",
            "main",
            "skills/foo",
            None,
        ),
        ("https://github.com/o/r.git", "github", "https://github.com/o/r.git", None, None, None),
        (
            "https://gitlab.com/g/sub/r/-/tree/v1/skills",
            "gitlab",
            "https://gitlab.com/g/sub/r.git",
            "v1",
            "skills",
            None,
        ),
        ("gitlab:g/r", "gitlab", "https://gitlab.com/g/r.git", None, None, None),
        ("git@example.com:o/r.git", "git", "git@example.com:o/r.git", None, None, None),
        ("https://example.com/r.git#v2", "git", "https://example.com/r.git", "v2", None, None),
    ],
)
def test_parse_remote(spec, type_, url, ref, subpath, skill):
    s = parse_source(spec)
    assert (s.type, s.url, s.ref, s.subpath, s.skill_filter) == (type_, url, ref, subpath, skill)


def test_owner_repo_lock_source():
    assert parse_source("https://github.com/o/r/tree/main/x").lock_source == "o/r"


def test_local_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for spec in (".", "./x", str(tmp_path)):
        s = parse_source(spec)
        assert s.type == "local"
        assert s.is_local


def test_alias():
    s = parse_source("kitchin@pycse", aliases={"kitchin": "jkitchin/skillz"})
    assert s.owner_repo == "jkitchin/skillz"
    assert s.skill_filter == "pycse"


@pytest.mark.parametrize("spec", ["", "o/r/../../etc", "notasource"])
def test_invalid(spec):
    with pytest.raises(SourceError):
        parse_source(spec)
