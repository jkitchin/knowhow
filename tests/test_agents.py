"""Tests for agents functionality."""

import pytest

from knowhow.validator import AgentValidator


@pytest.fixture
def mock_agents_dir(temp_dir):
    """Create a mock agents directory with sample agents."""
    agents_dir = temp_dir / "agents"
    agents_dir.mkdir()

    # Create a valid agent
    agent_file = agents_dir / "test-agent.md"
    agent_file.write_text("""---
name: test-agent
description: A test agent for unit testing
tools: Read, Write, Edit, Grep, Glob
model: sonnet
---

# Test Agent

This is a test agent that helps with testing.

## When to Use

Use this agent when testing.

## Instructions

Just run the tests.
""")

    return agents_dir


@pytest.fixture
def mock_repository_with_agents(temp_dir):
    """Create a mock repository with skills, commands, hooks, and agents."""
    repo_dir = temp_dir / "repository"
    repo_dir.mkdir()

    # Create agents directory
    agents_dir = repo_dir / "agents"
    agents_dir.mkdir()

    # Create sample agents
    agent1 = agents_dir / "sample-agent.md"
    agent1.write_text("""---
name: sample-agent
description: A sample agent for testing
tools: Read, Grep
model: haiku
---

# Sample Agent
""")

    agent2 = agents_dir / "code-reviewer.md"
    agent2.write_text("""---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Grep, Glob
model: sonnet
---

# Code Reviewer Agent
""")

    return repo_dir


class TestAgentValidator:
    """Tests for AgentValidator."""

    def test_valid_agent(self, mock_agents_dir):
        """Test validation of a valid agent."""
        agent_file = mock_agents_dir / "test-agent.md"
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_agent_file(self, temp_dir):
        """Test validation fails when file doesn't exist."""
        agent_file = temp_dir / "nonexistent.md"
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("does not exist" in error for error in errors)

    def test_wrong_file_extension(self, temp_dir):
        """Test validation fails when file is not .md."""
        agent_file = temp_dir / "agent.txt"
        agent_file.write_text("---\nname: test\ndescription: test\n---\n")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any(".md" in error for error in errors)

    def test_missing_frontmatter(self, temp_dir):
        """Test validation fails when frontmatter is missing."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("# Just content, no frontmatter\n")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("frontmatter" in error.lower() for error in errors)

    def test_missing_name(self, temp_dir):
        """Test validation fails when name is missing."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
description: Agent without name
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("name" in error.lower() for error in errors)

    def test_missing_description(self, temp_dir):
        """Test validation fails when description is missing."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("description" in error.lower() for error in errors)

    def test_invalid_name_uppercase(self, temp_dir):
        """Test validation fails with uppercase in name."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
name: InvalidAgent
description: This has uppercase letters
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("name" in error.lower() for error in errors)

    def test_invalid_name_spaces(self, temp_dir):
        """Test validation fails with spaces in name."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
name: invalid agent
description: This has spaces
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("name" in error.lower() for error in errors)

    def test_description_too_long(self, temp_dir):
        """Test validation fails when description exceeds 1024 chars."""
        agent_file = temp_dir / "test-agent.md"
        long_description = "x" * 1025
        agent_file.write_text(f"""---
name: test-agent
description: {long_description}
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("1024" in error for error in errors)

    def test_invalid_model(self, temp_dir):
        """Test validation fails with invalid model."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
description: Invalid model value
model: gpt-4
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("model" in error.lower() for error in errors)

    def test_valid_models(self, temp_dir):
        """Test validation succeeds for all valid models."""
        valid_models = ["sonnet", "opus", "haiku"]

        for model in valid_models:
            agent_file = temp_dir / f"agent-{model}.md"
            agent_file.write_text(f"""---
name: agent-{model}
description: Testing {model} model
model: {model}
---

# Test
""")
            is_valid, errors = AgentValidator.validate_agent_file(agent_file)
            assert is_valid is True, f"Model {model} should be valid, got errors: {errors}"

    def test_valid_tools_string(self, temp_dir):
        """Test validation succeeds with comma-separated tools string."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
description: Agent with tools string
tools: Read, Write, Edit
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is True

    def test_valid_tools_list(self, temp_dir):
        """Test validation succeeds with tools as list."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
description: Agent with tools list
tools:
  - Read
  - Write
  - Edit
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is True

    def test_invalid_tool(self, temp_dir):
        """Test validation fails with invalid tool."""
        agent_file = temp_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
description: Agent with invalid tool
tools: Read, InvalidTool, Write
---

# Test
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is False
        assert any("InvalidTool" in error for error in errors)

    def test_get_agent_metadata(self, mock_agents_dir):
        """Test extracting metadata from an agent."""
        agent_file = mock_agents_dir / "test-agent.md"
        metadata = AgentValidator.get_agent_metadata(agent_file)

        assert metadata is not None
        assert metadata["name"] == "test-agent"
        assert metadata["description"] == "A test agent for unit testing"
        assert metadata["model"] == "sonnet"
        assert "tools" in metadata

    def test_get_agent_metadata_missing_file(self, temp_dir):
        """Test get_agent_metadata returns None for missing file."""
        agent_file = temp_dir / "nonexistent.md"
        metadata = AgentValidator.get_agent_metadata(agent_file)
        assert metadata is None

    def test_minimal_valid_agent(self, temp_dir):
        """Test validation succeeds with minimal required fields."""
        agent_file = temp_dir / "minimal-agent.md"
        agent_file.write_text("""---
name: minimal-agent
description: A minimal agent with just required fields
---

# Minimal Agent
""")
        is_valid, errors = AgentValidator.validate_agent_file(agent_file)
        assert is_valid is True


class TestAgentUtils:
    """Tests for agent utility functions."""

    def test_find_agent_files(self, mock_agents_dir):
        """Test finding agent files."""
        from knowhow.utils import find_agent_files

        agents = find_agent_files(mock_agents_dir)
        assert len(agents) == 1
        assert agents[0].name == "test-agent.md"

    def test_find_agent_files_empty(self, temp_dir):
        """Test finding agents in empty directory."""
        from knowhow.utils import find_agent_files

        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        agents = find_agent_files(empty_dir)
        assert len(agents) == 0

    def test_find_agent_files_excludes_readme(self, temp_dir):
        """Test that README.md is excluded from agent files."""
        from knowhow.utils import find_agent_files

        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()

        # Create a valid agent
        agent_file = agents_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
description: Test agent
---
# Test
""")

        # Create a README that should be excluded
        readme = agents_dir / "README.md"
        readme.write_text("# Agents\n\nThis is a readme.")

        agents = find_agent_files(agents_dir)
        assert len(agents) == 1
        assert agents[0].name == "test-agent.md"

    def test_find_agent_files_multiple(self, mock_repository_with_agents):
        """Test finding multiple agent files."""
        from knowhow.utils import find_agent_files

        agents_dir = mock_repository_with_agents / "agents"
        agents = find_agent_files(agents_dir)
        assert len(agents) == 2
        agent_names = {a.name for a in agents}
        assert "sample-agent.md" in agent_names
        assert "code-reviewer.md" in agent_names
