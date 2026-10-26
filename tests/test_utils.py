"""Tests for utils module."""

from skillpack.utils import (
    copy_directory,
    copy_file,
    find_command_files,
    find_skill_directories,
    validate_description,
    validate_name,
)


class TestValidateName:
    """Tests for validate_name function."""

    def test_valid_lowercase_name(self):
        """Test valid lowercase name."""
        assert validate_name("my-skill") is True
        assert validate_name("test-skill-123") is True
        assert validate_name("python-ase") is True

    def test_invalid_uppercase(self):
        """Test invalid uppercase letters."""
        assert validate_name("My-Skill") is False
        assert validate_name("TEST") is False

    def test_invalid_spaces(self):
        """Test invalid spaces."""
        assert validate_name("my skill") is False
        assert validate_name("test skill") is False

    def test_invalid_special_chars(self):
        """Test invalid special characters."""
        assert validate_name("my_skill") is False
        assert validate_name("my.skill") is False
        assert validate_name("my@skill") is False

    def test_max_length(self):
        """Test maximum length constraint."""
        assert validate_name("a" * 64) is True
        assert validate_name("a" * 65) is False

    def test_numbers_allowed(self):
        """Test that numbers are allowed."""
        assert validate_name("skill-123") is True
        assert validate_name("123-skill") is True


class TestValidateDescription:
    """Tests for validate_description function."""

    def test_valid_description(self):
        """Test valid descriptions."""
        assert validate_description("A short description") is True
        assert validate_description("x" * 1024) is True

    def test_invalid_too_long(self):
        """Test description exceeding max length."""
        assert validate_description("x" * 1025) is False

    def test_custom_max_length(self):
        """Test custom max length."""
        assert validate_description("test", max_length=10) is True
        assert validate_description("test description", max_length=10) is False


class TestCopyDirectory:
    """Tests for copy_directory function."""

    def test_copy_directory_success(self, temp_dir):
        """Test successful directory copy."""
        src = temp_dir / "src"
        src.mkdir()
        (src / "file.txt").write_text("content")

        dst = temp_dir / "dst"
        result = copy_directory(src, dst)

        assert result is True
        assert dst.exists()
        assert (dst / "file.txt").read_text() == "content"

    def test_copy_directory_exists_no_force(self, temp_dir):
        """Test copy fails when destination exists without force."""
        src = temp_dir / "src"
        src.mkdir()

        dst = temp_dir / "dst"
        dst.mkdir()

        result = copy_directory(src, dst, force=False)
        assert result is False

    def test_copy_directory_exists_with_force(self, temp_dir):
        """Test copy succeeds when destination exists with force."""
        src = temp_dir / "src"
        src.mkdir()
        (src / "file.txt").write_text("new content")

        dst = temp_dir / "dst"
        dst.mkdir()
        (dst / "old.txt").write_text("old content")

        result = copy_directory(src, dst, force=True)
        assert result is True
        assert (dst / "file.txt").exists()
        assert not (dst / "old.txt").exists()


class TestCopyFile:
    """Tests for copy_file function."""

    def test_copy_file_success(self, temp_dir):
        """Test successful file copy."""
        src = temp_dir / "src.txt"
        src.write_text("content")

        dst = temp_dir / "subdir" / "dst.txt"
        result = copy_file(src, dst)

        assert result is True
        assert dst.exists()
        assert dst.read_text() == "content"

    def test_copy_file_exists_no_force(self, temp_dir):
        """Test copy fails when destination exists without force."""
        src = temp_dir / "src.txt"
        src.write_text("content")

        dst = temp_dir / "dst.txt"
        dst.write_text("old content")

        result = copy_file(src, dst, force=False)
        assert result is False
        assert dst.read_text() == "old content"

    def test_copy_file_exists_with_force(self, temp_dir):
        """Test copy succeeds when destination exists with force."""
        src = temp_dir / "src.txt"
        src.write_text("new content")

        dst = temp_dir / "dst.txt"
        dst.write_text("old content")

        result = copy_file(src, dst, force=True)
        assert result is True
        assert dst.read_text() == "new content"


class TestFindSkillDirectories:
    """Tests for find_skill_directories function."""

    def test_find_skills(self, mock_skills_dir):
        """Test finding skill directories."""
        skills = find_skill_directories(mock_skills_dir)
        assert len(skills) == 1
        assert skills[0].name == "test-skill"

    def test_find_skills_nested(self, temp_dir):
        """Test finding skills in nested directories."""
        (temp_dir / "category" / "skill1").mkdir(parents=True)
        (temp_dir / "category" / "skill1" / "SKILL.md").write_text("content")

        (temp_dir / "category" / "skill2").mkdir(parents=True)
        (temp_dir / "category" / "skill2" / "SKILL.md").write_text("content")

        skills = find_skill_directories(temp_dir)
        assert len(skills) == 2

    def test_find_skills_empty(self, temp_dir):
        """Test finding skills in empty directory."""
        skills = find_skill_directories(temp_dir)
        assert len(skills) == 0

    def test_find_skills_nonexistent(self, temp_dir):
        """Test finding skills in non-existent directory."""
        skills = find_skill_directories(temp_dir / "nonexistent")
        assert len(skills) == 0


class TestFindCommandFiles:
    """Tests for find_command_files function."""

    def test_find_commands(self, mock_commands_dir):
        """Test finding command files."""
        commands = find_command_files(mock_commands_dir)
        assert len(commands) == 1
        assert commands[0].name == "test-command.md"

    def test_find_commands_nested(self, temp_dir):
        """Test finding commands in nested directories."""
        (temp_dir / "category").mkdir()
        (temp_dir / "category" / "cmd1.md").write_text("content")
        (temp_dir / "category" / "cmd2.md").write_text("content")

        commands = find_command_files(temp_dir)
        assert len(commands) == 2

    def test_find_commands_ignores_skill_md(self, temp_dir):
        """Test that SKILL.md files are ignored."""
        (temp_dir / "skill").mkdir()
        (temp_dir / "skill" / "SKILL.md").write_text("content")
        (temp_dir / "skill" / "command.md").write_text("content")

        commands = find_command_files(temp_dir)
        assert len(commands) == 1
        assert commands[0].name == "command.md"

    def test_find_commands_empty(self, temp_dir):
        """Test finding commands in empty directory."""
        commands = find_command_files(temp_dir)
        assert len(commands) == 0
