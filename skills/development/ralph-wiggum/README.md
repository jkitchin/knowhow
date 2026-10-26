# Ralph Wiggum Mode

> "Me fail English? That's unpossible!" - Ralph Wiggum

Ralph Wiggum Mode is an autonomous AI coding loop that enables Claude Code to work continuously on tasks without human intervention. Named after the persistently optimistic Simpsons character, this technique lets Claude work "overnight shifts" while you sleep.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Security Model](#security-model)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Overview

### The Problem

Traditional Claude Code workflow requires constant human presence:

```
You: "Implement feature X"
Claude: [works until context fills]
You: "continue"
Claude: [works more]
You: "keep going"
Claude: [context full, forgets everything]
You: [frustrated, starts over]
```

### The Solution

Ralph Wiggum mode creates an external loop that:

1. Feeds a consistent prompt to Claude each iteration
2. Lets Claude work until context fills or task completes
3. Commits progress to git
4. Restarts with fresh context
5. New Claude instance picks up from filesystem state

**Key principle:** Progress persists in files and git, not in the LLM's context window.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL BASH LOOP                            │
│                                                                  │
│   while :; do                                                    │
│       ┌─────────────────────────────────────────────────────┐   │
│       │           CLAUDE SESSION                             │   │
│       │                                                      │   │
│       │  1. Read RALPH_PROMPT.md                            │   │
│       │  2. Check IMPLEMENTATION_PLAN.md                    │   │
│       │  3. Pick a task, implement it                       │   │
│       │  4. Run tests, commit changes                       │   │
│       │  5. Context fills → Session ends                    │   │
│       └─────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│       Git commit saves progress                                  │
│       Loop restarts with fresh context                           │
│   done                                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Install the Skill

```bash
skillpack install ralph-wiggum
```

### Install Safety Hooks (Recommended)

```bash
skillpack hooks install ralph-safety-check
skillpack hooks install ralph-cost-monitor
```

### Prerequisites

- Docker (for sandboxed execution)
- Claude CLI installed
- `ANTHROPIC_API_KEY` environment variable set

## Quick Start

### 1. Initialize Ralph in Your Project

```bash
# Copy Ralph files to your project
cd your-project
cp -r ~/.claude/skills/ralph-wiggum/scripts/* .
cp ~/.claude/skills/ralph-wiggum/templates/* .

# Or use the init script
./ralph-init.sh
```

### 2. Define Your Work

```bash
# Create specifications
mkdir -p specs
cat > specs/my-feature.md << 'EOF'
## Feature: User Authentication

### Requirements
- Users can register with email/password
- Users can log in and receive JWT
- Passwords are hashed with bcrypt
EOF

# Update the implementation plan
cat > IMPLEMENTATION_PLAN.md << 'EOF'
# Implementation Plan

## Tasks

- [ ] Create User model
- [ ] Add registration endpoint
- [ ] Add login endpoint
- [ ] Implement JWT generation
- [ ] Write tests
EOF
```

### 3. Run Ralph (In Sandbox)

```bash
# Set your API key
export ANTHROPIC_API_KEY=your-key-here

# Start Ralph
./ralph-sandbox.sh

# Or with iteration limit
./ralph-sandbox.sh . 20
```

### 4. Monitor Progress

```bash
# In another terminal
tail -f ralph.log
git log --oneline -10
cat IMPLEMENTATION_PLAN.md
```

### 5. Review Results

```bash
# Check what Ralph did
git log --oneline

# Verify tests pass
pytest  # or your test command

# Review the code
git diff main..HEAD
```

## Security Model

**CRITICAL: Ralph requires a sandboxed environment.**

Ralph uses `--dangerously-skip-permissions` which bypasses all safety prompts. Without sandboxing, this is genuinely dangerous.

### Required Isolation

Ralph will refuse to start unless it detects:

| Check | Description |
|-------|-------------|
| Container | Running in Docker/Kubernetes |
| Network | Cannot reach external hosts |
| User | Running as non-root |
| Paths | No access to ~/.ssh, ~/.aws, etc. |

### Defense in Depth

```
Layer 1: ralph.sh sandbox enforcement
    ↓
Layer 2: Docker container isolation
    ↓
Layer 3: Network disabled (--network none)
    ↓
Layer 4: ralph-safety-check hook (blocks dangerous commands)
    ↓
Layer 5: Resource limits (memory, CPU, PIDs)
```

### Manual Override (Dangerous)

Only use this if you've set up your own sandbox:

```bash
RALPH_I_KNOW_WHAT_IM_DOING=sandboxed ./ralph.sh
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | optional | API key (not needed with Claude Code subscription) |
| `RALPH_MODEL` | `opus` | Claude model to use |
| `RALPH_COST_LIMIT` | `50.00` | Max spend in USD |
| `RALPH_I_KNOW_WHAT_IM_DOING` | unset | Override sandbox check |

### Files

| File | Purpose |
|------|---------|
| `ralph.sh` | Main loop with sandbox enforcement |
| `ralph-sandbox.sh` | Docker wrapper |
| `RALPH_PROMPT.md` | Prompt for each iteration |
| `IMPLEMENTATION_PLAN.md` | Task tracking |
| `Dockerfile.ralph` | Sandbox container |
| `specs/` | Requirements directory |
| `ralph.log` | Iteration logs |

### Customizing the Prompt

Edit `RALPH_PROMPT.md` for your use case:

**For bug fixing:**
```markdown
Focus on fixing bugs in IMPLEMENTATION_PLAN.md.
Add regression tests for each fix.
Document root cause in commit messages.
```

**For test coverage:**
```markdown
Increase test coverage to 80%.
Run `pytest --cov` to check coverage.
Write tests for uncovered code paths.
```

## Best Practices

### Task Decomposition

Break large tasks into small, atomic pieces:

```markdown
## Bad
- [ ] Implement user authentication

## Good
- [ ] Create User model with email, password_hash
- [ ] Add POST /api/register endpoint
- [ ] Add POST /api/login endpoint
- [ ] Add password reset flow
- [ ] Add JWT middleware
- [ ] Write auth tests
```

### Prompt Engineering

1. **Be specific** - Tell Claude exactly what to do
2. **Single task focus** - "Pick ONE task" prevents bloat
3. **Require tests** - Include testing in the prompt
4. **Track progress** - Use IMPLEMENTATION_PLAN.md

### Monitoring

```bash
# Watch iterations
tail -f ralph.log

# Check commits
watch -n 5 'git log --oneline -10'

# Monitor resources
docker stats

# Check costs
cat .ralph-costs.json | jq '.summary'
```

## Troubleshooting

### Ralph Won't Start

**Symptom:** "NO SANDBOX DETECTED" error

**Fix:** Run via Docker wrapper:
```bash
./ralph-sandbox.sh
```

### Ralph Gets Stuck

**Symptom:** Same task attempted repeatedly

**Fix:**
1. Check `ralph.log` for errors
2. Update `IMPLEMENTATION_PLAN.md` with clarification
3. Add notes to `RALPH_PROMPT.md`

### High Costs

**Symptom:** API bill higher than expected

**Fix:**
1. Set iteration limits: `./ralph-sandbox.sh . 20`
2. Install cost monitor: `skillpack hooks install ralph-cost-monitor`
3. Set budget: `export RALPH_COST_LIMIT=25.00`

### Docker Build Fails

**Symptom:** Dockerfile.ralph won't build

**Fix:** Ensure Docker is running and you have network access:
```bash
docker build -t ralph-sandbox -f Dockerfile.ralph .
```

## References

- [Original Ralph Wiggum Technique](https://github.com/ghuntley/how-to-ralph-wiggum) by Geoffrey Huntley
- [Geoffrey Huntley's Blog](https://ghuntley.com/ralph/)
- [VentureBeat Coverage](https://venturebeat.com/technology/how-ralph-wiggum-went-from-the-simpsons-to-the-biggest-name-in-ai-right-now)
- [Vercel Ralph Loop Agent](https://github.com/vercel-labs/ralph-loop-agent)

## License

This skill is part of the skillpack project and follows its license.

---

*"I'm learnding!" - Ralph Wiggum*
