"""Tests for validator module."""

from skillpack.validator import CommandValidator, SkillValidator


class TestSkillValidator:
    """Tests for SkillValidator."""

    def test_valid_skill(self, mock_skills_dir):
        """Test validation of a valid skill."""
        skill_dir = mock_skills_dir / "test-skill"
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_skill_md(self, temp_dir):
        """Test validation fails when SKILL.md is missing."""
        skill_dir = temp_dir / "invalid-skill"
        skill_dir.mkdir()
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is False
        assert any("SKILL.md" in error for error in errors)

    def test_invalid_name_uppercase(self, temp_dir):
        """Test validation fails with uppercase in name."""
        skill_dir = temp_dir / "InvalidSkill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: InvalidSkill
description: This has uppercase letters
---
# Test
""")
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is False

    def test_invalid_name_spaces(self, temp_dir):
        """Test validation fails with spaces in name."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test skill with spaces
description: This has spaces in name
---
# Test
""")
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is False

    def test_missing_description(self, temp_dir):
        """Test validation fails when description is missing."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
---
# Test
""")
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is False
        assert any("description" in error.lower() for error in errors)

    def test_description_too_long(self, temp_dir):
        """Test validation fails when description exceeds 1024 chars."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        long_description = "x" * 1025
        skill_md.write_text(f"""---
name: test-skill
description: {long_description}
---
# Test
""")
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is False

    def test_invalid_allowed_tools(self, temp_dir):
        """Test validation fails with invalid allowed-tools format."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: Test skill
allowed-tools: not a list
---
# Test
""")
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is False

    def test_allowed_tools_all_tools_format(self, temp_dir):
        """Test validation succeeds with ["*"] for all tools."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: Test skill with all tools allowed
allowed-tools: ["*"]
---
# Test
""")
        is_valid, errors = SkillValidator.validate_skill_directory(skill_dir)
        assert is_valid is True
        assert len(errors) == 0


class TestCommandValidator:
    """Tests for CommandValidator."""

    def test_valid_command(self, mock_commands_dir):
        """Test validation of a valid command."""
        cmd_file = mock_commands_dir / "test-command.md"
        is_valid, errors = CommandValidator.validate_command_file(cmd_file)
        assert is_valid is True
        assert len(errors) == 0

    def test_command_without_frontmatter(self, temp_dir):
        """Test validation of command without frontmatter."""
        cmd_file = temp_dir / "test-command.md"
        cmd_file.write_text("# Simple Command\n\nNo frontmatter needed.")
        is_valid, errors = CommandValidator.validate_command_file(cmd_file)
        assert is_valid is True

    def test_invalid_command_extension(self, temp_dir):
        """Test validation fails for non-markdown files."""
        cmd_file = temp_dir / "test-command.txt"
        cmd_file.write_text("---\ndescription: Test\n---\nContent")
        is_valid, errors = CommandValidator.validate_command_file(cmd_file)
        assert is_valid is False

    def test_description_too_long(self, temp_dir):
        """Test validation fails when description exceeds 256 chars."""
        cmd_file = temp_dir / "test-command.md"
        long_description = "x" * 257
        cmd_file.write_text(f"""---
description: {long_description}
---
# Test
""")
        is_valid, errors = CommandValidator.validate_command_file(cmd_file)
        assert is_valid is False

    def test_invalid_model(self, temp_dir):
        """Test validation fails with invalid model value."""
        cmd_file = temp_dir / "test-command.md"
        cmd_file.write_text("""---
description: Test command
model: invalid-model
---
# Test
""")
        is_valid, errors = CommandValidator.validate_command_file(cmd_file)
        assert is_valid is False
