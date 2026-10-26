"""Validation for skills and commands."""

import re
from pathlib import Path

import yaml

from skillin.utils import validate_description, validate_name


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class SkillValidator:
    """Validator for skill directories and SKILL.md files."""

    REQUIRED_FRONTMATTER_FIELDS = ["name", "description"]
    OPTIONAL_FRONTMATTER_FIELDS = ["allowed-tools"]
    VALID_TOOLS = {
        "Bash",
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "Task",
        "WebFetch",
        "WebSearch",
        "TodoWrite",
        "AskUserQuestion",
        "Skill",
        "SlashCommand",
        "NotebookEdit",
        "BashOutput",
        "KillShell",
    }

    @classmethod
    def validate_skill_directory(cls, skill_path: Path) -> tuple[bool, list[str]]:
        """
        Validate a skill directory.

        Args:
            skill_path: Path to skill directory

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check if directory exists
        if not skill_path.exists():
            errors.append(f"Directory does not exist: {skill_path}")
            return False, errors

        if not skill_path.is_dir():
            errors.append(f"Path is not a directory: {skill_path}")
            return False, errors

        # Check for SKILL.md
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"Missing SKILL.md in {skill_path}")
            return False, errors

        # Validate SKILL.md content
        valid, file_errors = cls.validate_skill_file(skill_file)
        errors.extend(file_errors)

        return len(errors) == 0, errors

    @classmethod
    def validate_skill_file(cls, skill_file: Path) -> tuple[bool, list[str]]:
        """
        Validate a SKILL.md file.

        Args:
            skill_file: Path to SKILL.md file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            with open(skill_file) as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return False, errors

        # Parse frontmatter
        frontmatter = cls._parse_frontmatter(content)
        if frontmatter is None:
            errors.append("Missing or invalid YAML frontmatter")
            return False, errors

        # Validate required fields
        for field in cls.REQUIRED_FRONTMATTER_FIELDS:
            if field not in frontmatter:
                errors.append(f"Missing required field: {field}")

        # Validate name
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not validate_name(name):
                errors.append(
                    f"Invalid name '{name}': must be lowercase with hyphens/numbers only, "
                    f"max 64 chars"
                )

        # Validate description
        if "description" in frontmatter:
            desc = frontmatter["description"]
            if not validate_description(desc):
                errors.append("Description too long: max 1024 characters")

        # Validate allowed-tools
        if "allowed-tools" in frontmatter:
            tools = frontmatter["allowed-tools"]
            # Allow "*" as string or ["*"] as list to mean "all tools"
            if tools and tools != "*" and tools != ["*"]:
                if isinstance(tools, list):
                    for tool in tools:
                        if tool not in cls.VALID_TOOLS:
                            errors.append(f"Unknown tool: {tool}")
                else:
                    errors.append("allowed-tools must be a list or '*'")

        return len(errors) == 0, errors

    @staticmethod
    def _parse_frontmatter(content: str) -> dict | None:
        """
        Parse YAML frontmatter from markdown content.

        Args:
            content: Markdown content

        Returns:
            Dictionary of frontmatter or None if invalid
        """
        # Match frontmatter between --- delimiters
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return None

        frontmatter_str = match.group(1)
        try:
            return yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None


class CommandValidator:
    """Validator for command files."""

    OPTIONAL_FRONTMATTER_FIELDS = [
        "description",
        "allowed-tools",
        "model",
        "argument-hint",
        "disable-model-invocation",
    ]

    @classmethod
    def validate_command_file(cls, command_file: Path) -> tuple[bool, list[str]]:
        """
        Validate a command file.

        Args:
            command_file: Path to command markdown file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not command_file.exists():
            errors.append(f"File does not exist: {command_file}")
            return False, errors

        if not command_file.suffix == ".md":
            errors.append(f"Command file must be a .md file: {command_file}")
            return False, errors

        try:
            with open(command_file) as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return False, errors

        # Parse optional frontmatter
        frontmatter = cls._parse_frontmatter(content)

        # Validate frontmatter if present
        if frontmatter:
            # Validate description length
            if "description" in frontmatter:
                desc = frontmatter["description"]
                if not validate_description(desc, max_length=256):
                    errors.append("Description too long: max 256 characters for commands")

            # Validate model
            if "model" in frontmatter:
                model = frontmatter["model"]
                valid_models = ["sonnet", "opus", "haiku"]
                if model not in valid_models:
                    errors.append(f"Invalid model '{model}': must be one of {valid_models}")

            # Validate allowed-tools
            if "allowed-tools" in frontmatter:
                tools = frontmatter["allowed-tools"]
                # Allow "*" as string or ["*"] as list to mean "all tools"
                if tools and tools != "*" and tools != ["*"]:
                    if not isinstance(tools, list):
                        errors.append("allowed-tools must be a list or '*'")

        # Check content is not empty (excluding frontmatter)
        content_without_frontmatter = cls._remove_frontmatter(content)
        if not content_without_frontmatter.strip():
            errors.append("Command content is empty")

        return len(errors) == 0, errors

    @staticmethod
    def _parse_frontmatter(content: str) -> dict | None:
        """Parse YAML frontmatter from markdown content."""
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return None

        frontmatter_str = match.group(1)
        try:
            return yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None

    @staticmethod
    def _remove_frontmatter(content: str) -> str:
        """Remove frontmatter from content."""
        pattern = r"^---\s*\n.*?\n---\s*\n"
        return re.sub(pattern, "", content, count=1, flags=re.DOTALL)


class HookValidator:
    """Validator for hook directories and HOOK.md files."""

    REQUIRED_FRONTMATTER_FIELDS = ["name", "description", "event"]
    OPTIONAL_FRONTMATTER_FIELDS = ["matcher", "type", "timeout"]

    VALID_EVENTS = {
        "PreToolUse",
        "PostToolUse",
        "PermissionRequest",
        "UserPromptSubmit",
        "Notification",
        "Stop",
        "SubagentStop",
        "PreCompact",
        "SessionStart",
        "SessionEnd",
    }

    VALID_HOOK_TYPES = {"command", "prompt"}

    @classmethod
    def validate_hook_directory(cls, hook_path: Path) -> tuple[bool, list[str]]:
        """
        Validate a hook directory.

        Args:
            hook_path: Path to hook directory

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check if directory exists
        if not hook_path.exists():
            errors.append(f"Directory does not exist: {hook_path}")
            return False, errors

        if not hook_path.is_dir():
            errors.append(f"Path is not a directory: {hook_path}")
            return False, errors

        # Check for HOOK.md
        hook_file = hook_path / "HOOK.md"
        if not hook_file.exists():
            errors.append(f"Missing HOOK.md in {hook_path}")
            return False, errors

        # Validate HOOK.md content
        valid, file_errors = cls.validate_hook_file(hook_file)
        errors.extend(file_errors)

        # Check for at least one script file
        script_files = list(hook_path.glob("*.py")) + list(hook_path.glob("*.sh"))
        if not script_files:
            errors.append(f"No hook script (*.py or *.sh) found in {hook_path}")

        return len(errors) == 0, errors

    @classmethod
    def validate_hook_file(cls, hook_file: Path) -> tuple[bool, list[str]]:
        """
        Validate a HOOK.md file.

        Args:
            hook_file: Path to HOOK.md file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            with open(hook_file) as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return False, errors

        # Parse frontmatter
        frontmatter = cls._parse_frontmatter(content)
        if frontmatter is None:
            errors.append("Missing or invalid YAML frontmatter")
            return False, errors

        # Validate required fields
        for field in cls.REQUIRED_FRONTMATTER_FIELDS:
            if field not in frontmatter:
                errors.append(f"Missing required field: {field}")

        # Validate name
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not validate_name(name):
                errors.append(
                    f"Invalid name '{name}': must be lowercase with hyphens/numbers only, "
                    f"max 64 chars"
                )

        # Validate description (shorter limit for hooks)
        if "description" in frontmatter:
            desc = frontmatter["description"]
            if not validate_description(desc, max_length=256):
                errors.append("Description too long: max 256 characters for hooks")

        # Validate event
        if "event" in frontmatter:
            event = frontmatter["event"]
            if event not in cls.VALID_EVENTS:
                errors.append(f"Invalid event '{event}': must be one of {sorted(cls.VALID_EVENTS)}")

        # Validate type (optional, defaults to "command")
        if "type" in frontmatter:
            hook_type = frontmatter["type"]
            if hook_type not in cls.VALID_HOOK_TYPES:
                errors.append(
                    f"Invalid type '{hook_type}': must be one of {sorted(cls.VALID_HOOK_TYPES)}"
                )

        # Validate timeout (optional)
        if "timeout" in frontmatter:
            timeout = frontmatter["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                errors.append("Timeout must be a positive number")

        return len(errors) == 0, errors

    @staticmethod
    def _parse_frontmatter(content: str) -> dict | None:
        """
        Parse YAML frontmatter from markdown content.

        Args:
            content: Markdown content

        Returns:
            Dictionary of frontmatter or None if invalid
        """
        # Match frontmatter between --- delimiters
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return None

        frontmatter_str = match.group(1)
        try:
            return yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None

    @classmethod
    def get_hook_metadata(cls, hook_path: Path) -> dict | None:
        """
        Extract metadata from a hook's HOOK.md file.

        Args:
            hook_path: Path to hook directory

        Returns:
            Dictionary of frontmatter or None if invalid
        """
        hook_file = hook_path / "HOOK.md"
        if not hook_file.exists():
            return None

        try:
            with open(hook_file) as f:
                content = f.read()
            return cls._parse_frontmatter(content)
        except Exception:
            return None


class AgentValidator:
    """Validator for agent files (subagents)."""

    REQUIRED_FRONTMATTER_FIELDS = ["name", "description"]
    OPTIONAL_FRONTMATTER_FIELDS = ["tools", "model", "disallowedTools"]

    VALID_MODELS = {"sonnet", "opus", "haiku"}

    VALID_TOOLS = {
        "Bash",
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "Task",
        "WebFetch",
        "WebSearch",
        "TodoWrite",
        "AskUserQuestion",
        "Skill",
        "SlashCommand",
        "NotebookEdit",
        "BashOutput",
        "KillShell",
    }

    @classmethod
    def validate_agent_file(cls, agent_file: Path) -> tuple[bool, list[str]]:
        """
        Validate an agent markdown file.

        Args:
            agent_file: Path to agent .md file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check if file exists
        if not agent_file.exists():
            errors.append(f"File does not exist: {agent_file}")
            return False, errors

        if not agent_file.suffix == ".md":
            errors.append(f"Agent file must be a .md file: {agent_file}")
            return False, errors

        try:
            with open(agent_file) as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return False, errors

        # Parse frontmatter
        frontmatter = cls._parse_frontmatter(content)
        if frontmatter is None:
            errors.append("Missing or invalid YAML frontmatter")
            return False, errors

        # Validate required fields
        for field in cls.REQUIRED_FRONTMATTER_FIELDS:
            if field not in frontmatter:
                errors.append(f"Missing required field: {field}")

        # Validate name
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not validate_name(name):
                errors.append(
                    f"Invalid name '{name}': must be lowercase with hyphens/numbers only, "
                    f"max 64 chars"
                )

        # Validate description
        if "description" in frontmatter:
            desc = frontmatter["description"]
            if not validate_description(desc):
                errors.append("Description too long: max 1024 characters")

        # Validate model
        if "model" in frontmatter:
            model = frontmatter["model"]
            if model not in cls.VALID_MODELS:
                errors.append(f"Invalid model '{model}': must be one of {sorted(cls.VALID_MODELS)}")

        # Validate tools (can be string or list)
        if "tools" in frontmatter:
            tools = frontmatter["tools"]
            if isinstance(tools, str):
                # Parse comma-separated string
                tool_list = [t.strip() for t in tools.split(",")]
            elif isinstance(tools, list):
                tool_list = tools
            else:
                tool_list = []
                errors.append("tools must be a comma-separated string or list")

            for tool in tool_list:
                if tool and tool != "*" and tool not in cls.VALID_TOOLS:
                    errors.append(f"Unknown tool: {tool}")

        # Validate disallowedTools
        if "disallowedTools" in frontmatter:
            disallowed = frontmatter["disallowedTools"]
            if isinstance(disallowed, str):
                disallowed_list = [t.strip() for t in disallowed.split(",")]
            elif isinstance(disallowed, list):
                disallowed_list = disallowed
            else:
                disallowed_list = []
                errors.append("disallowedTools must be a comma-separated string or list")

            for tool in disallowed_list:
                if tool and tool not in cls.VALID_TOOLS:
                    errors.append(f"Unknown disallowed tool: {tool}")

        # Check content is not empty (excluding frontmatter)
        content_without_frontmatter = cls._remove_frontmatter(content)
        if not content_without_frontmatter.strip():
            errors.append("Agent content is empty (needs instructions after frontmatter)")

        return len(errors) == 0, errors

    @staticmethod
    def _parse_frontmatter(content: str) -> dict | None:
        """Parse YAML frontmatter from markdown content."""
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return None

        frontmatter_str = match.group(1)
        try:
            return yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None

    @staticmethod
    def _remove_frontmatter(content: str) -> str:
        """Remove frontmatter from content."""
        pattern = r"^---\s*\n.*?\n---\s*\n"
        return re.sub(pattern, "", content, count=1, flags=re.DOTALL)

    @classmethod
    def get_agent_metadata(cls, agent_file: Path) -> dict | None:
        """
        Extract metadata from an agent file.

        Args:
            agent_file: Path to agent .md file

        Returns:
            Dictionary of frontmatter or None if invalid
        """
        if not agent_file.exists():
            return None

        try:
            with open(agent_file) as f:
                content = f.read()
            return cls._parse_frontmatter(content)
        except Exception:
            return None
