#!/bin/bash
# ralph-init.sh - Initialize Ralph Wiggum mode in a project
#
# Usage: ralph-init.sh [target-dir]
#
# Creates all necessary files for Ralph Wiggum mode:
#   - ralph.sh (main loop)
#   - ralph-sandbox.sh (Docker wrapper)
#   - RALPH_PROMPT.md (default prompt)
#   - IMPLEMENTATION_PLAN.md (task tracking)
#   - Dockerfile.ralph (sandbox container)
#   - specs/ directory

set -euo pipefail

TARGET_DIR="${1:-.}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Ralph Wiggum Mode - Project Initialization${NC}"
echo ""

# Create target directory if needed
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# Check if already initialized
if [[ -f "ralph.sh" ]]; then
    echo -e "${YELLOW}Warning: Ralph files already exist in this directory.${NC}"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo "Creating Ralph files..."

# Create specs directory
mkdir -p specs

# Create ralph.sh
cat > ralph.sh << 'RALPH_SCRIPT'
#!/bin/bash
# ralph.sh - Sandbox-enforced Ralph Wiggum autonomous coding loop
# See: https://github.com/ghuntley/how-to-ralph-wiggum

set -euo pipefail

readonly VERSION="1.0.0"
readonly MIN_SANDBOX_CHECKS=3

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a ralph.log
}

SANDBOX_TYPE=""
SANDBOX_CHECKS_PASSED=0

detect_sandbox() {
    local checks_passed=0
    echo "Running sandbox detection..."
    echo ""

    if [[ -f /.dockerenv ]]; then
        echo -e "  ${GREEN}✓${NC} Docker container detected"
        SANDBOX_TYPE="docker"
        ((checks_passed++))
    elif grep -q "docker\|containerd" /proc/1/cgroup 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Docker container detected (cgroup)"
        SANDBOX_TYPE="docker"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Not in Docker container"
    fi

    if ! ping -c 1 -W 2 8.8.8.8 &>/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Network is isolated"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Network is NOT isolated"
    fi

    if [[ $EUID -ne 0 ]]; then
        echo -e "  ${GREEN}✓${NC} Running as non-root (UID: $EUID)"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Running as root"
    fi

    local sensitive_paths=("$HOME/.ssh" "$HOME/.aws" "$HOME/.config/gcloud" "/etc/shadow")
    local sensitive_accessible=0
    for path in "${sensitive_paths[@]}"; do
        if [[ -r "$path" ]] 2>/dev/null; then
            ((sensitive_accessible++))
        fi
    done
    if [[ $sensitive_accessible -eq 0 ]]; then
        echo -e "  ${GREEN}✓${NC} Sensitive paths not accessible"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Can access $sensitive_accessible sensitive paths"
    fi

    if command -v systemd-detect-virt &>/dev/null; then
        local virt_type
        virt_type=$(systemd-detect-virt 2>/dev/null || echo "none")
        if [[ "$virt_type" != "none" ]]; then
            echo -e "  ${GREEN}✓${NC} Virtualization: $virt_type"
            SANDBOX_TYPE="${SANDBOX_TYPE:-$virt_type}"
            ((checks_passed++))
        fi
    fi

    if [[ -f /proc/1/status ]]; then
        local cap_eff
        cap_eff=$(grep CapEff /proc/1/status 2>/dev/null | awk '{print $2}' || echo "")
        if [[ "$cap_eff" != "0000003fffffffff" ]] && [[ -n "$cap_eff" ]]; then
            echo -e "  ${GREEN}✓${NC} Capabilities restricted"
            ((checks_passed++))
        fi
    fi

    echo ""
    echo "Sandbox checks passed: $checks_passed"
    echo ""
    SANDBOX_CHECKS_PASSED=$checks_passed
}

enforce_sandbox() {
    detect_sandbox

    if [[ "${RALPH_I_KNOW_WHAT_IM_DOING:-}" == "sandboxed" ]]; then
        echo -e "${YELLOW}[WARN]${NC} Manual sandbox override enabled"
        return 0
    fi

    if [[ -z "$SANDBOX_TYPE" ]]; then
        echo ""
        echo "========================================================================"
        echo "  RALPH REFUSED TO START - NO SANDBOX DETECTED"
        echo "========================================================================"
        echo ""
        echo "Ralph uses --dangerously-skip-permissions. Run safely with:"
        echo ""
        echo "  ./ralph-sandbox.sh"
        echo ""
        echo "Or for custom sandboxes:"
        echo ""
        echo "  RALPH_I_KNOW_WHAT_IM_DOING=sandboxed ./ralph.sh"
        echo ""
        exit 1
    fi

    if [[ $SANDBOX_CHECKS_PASSED -lt $MIN_SANDBOX_CHECKS ]]; then
        echo -e "${RED}Insufficient sandbox isolation${NC}"
        echo "Only $SANDBOX_CHECKS_PASSED of $MIN_SANDBOX_CHECKS required checks passed."
        exit 1
    fi

    echo -e "${GREEN}[OK]${NC} Sandbox verified: $SANDBOX_TYPE"
}

main() {
    echo ""
    echo -e "${BLUE}Ralph Wiggum Mode v${VERSION}${NC}"
    echo "\"Me fail English? That's unpossible!\""
    echo ""

    enforce_sandbox

    local mode="${1:-build}"
    local max_iterations="${2:-0}"
    local iteration=0
    local model="${RALPH_MODEL:-opus}"

    local prompt_file="RALPH_PROMPT.md"
    [[ "$mode" == "plan" ]] && [[ -f "RALPH_PROMPT_plan.md" ]] && prompt_file="RALPH_PROMPT_plan.md"
    [[ "$mode" == "build" ]] && [[ -f "RALPH_PROMPT_build.md" ]] && prompt_file="RALPH_PROMPT_build.md"

    if [[ ! -f "$prompt_file" ]]; then
        echo "Error: $prompt_file not found"
        exit 1
    fi

    log "Starting Ralph loop (mode=$mode, model=$model, max=$max_iterations)"

    trap 'log "Interrupted"; exit 0' INT TERM

    while true; do
        if [[ $max_iterations -gt 0 ]] && [[ $iteration -ge $max_iterations ]]; then
            log "Reached max iterations ($max_iterations)"
            break
        fi

        ((iteration++))
        log "=== Iteration $iteration ==="

        cat "$prompt_file" | claude -p \
            --dangerously-skip-permissions \
            --model "$model" \
            --output-format stream-json \
            2>&1 | tee -a ralph.log || true

        if ! git diff --quiet || ! git diff --cached --quiet; then
            git add -A
            git commit -m "Ralph iteration $iteration" 2>/dev/null || true
            log "Committed changes"
        else
            log "No changes to commit"
        fi

        sleep 2
    done

    log "Ralph completed $iteration iterations"
    echo -e "${GREEN}Done!${NC} Check ralph.log and git log"
}

main "$@"
RALPH_SCRIPT
chmod +x ralph.sh
echo -e "  ${GREEN}✓${NC} ralph.sh"

# Create ralph-sandbox.sh
cat > ralph-sandbox.sh << 'SANDBOX_SCRIPT'
#!/bin/bash
# ralph-sandbox.sh - Run Ralph safely in Docker

set -euo pipefail

PROJECT_DIR="${1:-.}"
MAX_ITERATIONS="${2:-0}"
MODE="${3:-build}"

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    exit 1
fi

PROJECT_DIR="$(realpath "$PROJECT_DIR")"

if [[ ! -f "$PROJECT_DIR/ralph.sh" ]]; then
    echo "Error: ralph.sh not found. Run ralph-init.sh first."
    exit 1
fi

IMAGE_NAME="ralph-sandbox"
DOCKERFILE="$PROJECT_DIR/Dockerfile.ralph"

if [[ -f "$DOCKERFILE" ]]; then
    docker build -t "$IMAGE_NAME" -f "$DOCKERFILE" "$PROJECT_DIR"
elif ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    docker build -t "$IMAGE_NAME" - << 'DOCKERFILE'
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates iputils-ping python3 python3-pip nodejs npm \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://claude.ai/install.sh | sh
RUN useradd -m -s /bin/bash -u 1000 ralph && mkdir -p /workspace && chown -R ralph:ralph /workspace
USER ralph
WORKDIR /workspace
CMD ["./ralph.sh"]
DOCKERFILE
fi

echo "Starting Ralph in sandbox..."
echo "  Project: $PROJECT_DIR"
echo "  Mode: $MODE"
echo "  Max iterations: ${MAX_ITERATIONS:-unlimited}"
echo ""

docker run --rm -it \
    --name "ralph-$(date +%s)" \
    --network none \
    --memory 4g \
    --cpus 2 \
    --pids-limit 100 \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    -v "$PROJECT_DIR:/workspace" \
    -e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
    -e "RALPH_MODEL=${RALPH_MODEL:-opus}" \
    "$IMAGE_NAME" \
    ./ralph.sh "$MODE" "$MAX_ITERATIONS"

echo "Ralph sandbox session ended."
SANDBOX_SCRIPT
chmod +x ralph-sandbox.sh
echo -e "  ${GREEN}✓${NC} ralph-sandbox.sh"

# Create RALPH_PROMPT.md
cat > RALPH_PROMPT.md << 'PROMPT'
# Ralph Mode - Autonomous Iteration

You are operating in autonomous Ralph Wiggum mode. Your progress persists in files and git history, not in your context window. Each iteration starts fresh - pick up where the last one left off.

## Prime Directive

Complete tasks from IMPLEMENTATION_PLAN.md systematically, one task per iteration.

## Each Iteration

1. **Orient** - Read IMPLEMENTATION_PLAN.md and recent git log to understand current state
2. **Select** - Pick ONE pending task (marked with `- [ ]`)
3. **Mark** - Update the task to `- [x] in progress` in IMPLEMENTATION_PLAN.md
4. **Implement** - Complete the task fully, including tests
5. **Verify** - Run tests to ensure nothing is broken
6. **Complete** - Mark the task as `- [x] done` in IMPLEMENTATION_PLAN.md
7. **Commit** - Commit all changes with a descriptive message

## Rules

- **One task per iteration** - Don't try to do everything at once
- **Never skip tests** - All code changes must have tests
- **Commit often** - Small, focused commits are better
- **Document blockers** - If stuck, add a note to IMPLEMENTATION_PLAN.md and move on
- **Don't assume** - Read existing code before making changes
- **Follow patterns** - Match the style of existing code

## If Blocked

If you cannot complete a task:
1. Document why in IMPLEMENTATION_PLAN.md under a "## Blockers" section
2. Move to the next pending task
3. The next iteration (or a human) can address the blocker

## When All Tasks Complete

If all tasks are marked done:
1. Add a summary to IMPLEMENTATION_PLAN.md
2. Run the full test suite
3. Create a final commit
4. Exit gracefully

## Important Files

- `IMPLEMENTATION_PLAN.md` - Your task list and progress tracker
- `specs/` - Requirements and specifications
- `ralph.log` - Log of all iterations (append-only)
PROMPT
echo -e "  ${GREEN}✓${NC} RALPH_PROMPT.md"

# Create IMPLEMENTATION_PLAN.md
cat > IMPLEMENTATION_PLAN.md << 'PLAN'
# Implementation Plan

This file tracks progress across Ralph iterations. Update this file as you work.

## Tasks

<!-- Add your tasks here. Ralph will work through them one by one. -->

- [ ] Example task 1 - Replace with your actual tasks
- [ ] Example task 2 - Be specific and atomic
- [ ] Example task 3 - One task = one iteration ideally

## Completed

<!-- Tasks move here when done -->

## Blockers

<!-- Document any blockers here -->

## Notes

<!-- Add any notes for future iterations -->
PLAN
echo -e "  ${GREEN}✓${NC} IMPLEMENTATION_PLAN.md"

# Create Dockerfile.ralph
cat > Dockerfile.ralph << 'DOCKERFILE'
# Dockerfile.ralph - Minimal sandbox for Ralph Wiggum mode

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install only essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    iputils-ping \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Claude CLI
RUN curl -fsSL https://claude.ai/install.sh | sh

# Create non-root user for safety
RUN useradd -m -s /bin/bash -u 1000 ralph && \
    mkdir -p /workspace && \
    chown -R ralph:ralph /workspace

# Switch to non-root user
USER ralph
WORKDIR /workspace

CMD ["./ralph.sh"]
DOCKERFILE
echo -e "  ${GREEN}✓${NC} Dockerfile.ralph"

# Create example spec
cat > specs/README.md << 'SPEC'
# Specifications

Put your requirements and specifications in this directory.

## Example

Create files like:
- `user-auth.md` - User authentication requirements
- `api-endpoints.md` - API specification
- `data-models.md` - Database schema

Ralph will reference these when implementing tasks.
SPEC
echo -e "  ${GREEN}✓${NC} specs/README.md"

# Create .gitignore additions
if [[ -f .gitignore ]]; then
    if ! grep -q "ralph.log" .gitignore; then
        echo -e "\n# Ralph Wiggum mode\nralph.log" >> .gitignore
        echo -e "  ${GREEN}✓${NC} Updated .gitignore"
    fi
else
    echo -e "# Ralph Wiggum mode\nralph.log" > .gitignore
    echo -e "  ${GREEN}✓${NC} Created .gitignore"
fi

echo ""
echo -e "${GREEN}Ralph initialization complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit IMPLEMENTATION_PLAN.md with your tasks"
echo "  2. Add specifications to specs/"
echo "  3. Customize RALPH_PROMPT.md if needed"
echo "  4. Run: ./ralph-sandbox.sh"
echo ""
echo "For more options: ./ralph-sandbox.sh --help"
