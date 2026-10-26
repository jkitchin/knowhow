#!/bin/bash
# ralph.sh - Sandbox-enforced Ralph Wiggum autonomous coding loop
#
# Usage: ./ralph.sh [mode] [max_iterations]
#   mode: "build" (default) or "plan"
#   max_iterations: 0 for unlimited (default), or positive integer
#
# Environment variables:
#   ANTHROPIC_API_KEY     - Optional: Not needed with Claude Code subscription
#   RALPH_MODEL           - Optional: Model to use (default: opus)
#   RALPH_I_KNOW_WHAT_IM_DOING=sandboxed - Override sandbox check (dangerous)

set -euo pipefail

#######################################
# CONFIGURATION
#######################################

readonly VERSION="1.0.0"
readonly MIN_SANDBOX_CHECKS=3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#######################################
# LOGGING
#######################################

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a ralph.log
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >> ralph.log
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

#######################################
# SANDBOX DETECTION
#######################################

SANDBOX_TYPE=""
SANDBOX_CHECKS_PASSED=0

detect_sandbox() {
    local checks_passed=0

    echo "Running sandbox detection..."
    echo ""

    # Check 1: Docker container
    if [[ -f /.dockerenv ]]; then
        echo -e "  ${GREEN}✓${NC} Docker container detected (/.dockerenv exists)"
        SANDBOX_TYPE="docker"
        ((checks_passed++))
    elif grep -q "docker\|containerd" /proc/1/cgroup 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Docker container detected (cgroup)"
        SANDBOX_TYPE="docker"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Not in Docker container"
    fi

    # Check 2: Network isolation
    if ! ping -c 1 -W 2 8.8.8.8 &>/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Network is isolated (cannot reach internet)"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Network is NOT isolated (can reach internet)"
    fi

    # Check 3: Running as non-root
    if [[ $EUID -ne 0 ]]; then
        echo -e "  ${GREEN}✓${NC} Running as non-root user (UID: $EUID)"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Running as root (dangerous!)"
    fi

    # Check 4: No access to sensitive directories
    local sensitive_paths=("$HOME/.ssh" "$HOME/.aws" "$HOME/.config/gcloud" "/etc/shadow")
    local sensitive_accessible=0
    for path in "${sensitive_paths[@]}"; do
        if [[ -r "$path" ]] 2>/dev/null; then
            ((sensitive_accessible++))
        fi
    done
    if [[ $sensitive_accessible -eq 0 ]]; then
        echo -e "  ${GREEN}✓${NC} Sensitive paths not accessible (.ssh, .aws, etc.)"
        ((checks_passed++))
    else
        echo -e "  ${RED}✗${NC} Can access $sensitive_accessible sensitive paths"
    fi

    # Check 5: Virtualization detection
    if command -v systemd-detect-virt &>/dev/null; then
        local virt_type
        virt_type=$(systemd-detect-virt 2>/dev/null || echo "none")
        if [[ "$virt_type" != "none" ]]; then
            echo -e "  ${GREEN}✓${NC} Virtualization detected: $virt_type"
            SANDBOX_TYPE="${SANDBOX_TYPE:-$virt_type}"
            ((checks_passed++))
        fi
    fi

    # Check 6: Limited capabilities (Linux only)
    if [[ -f /proc/1/status ]]; then
        local cap_eff
        cap_eff=$(grep CapEff /proc/1/status 2>/dev/null | awk '{print $2}' || echo "")
        # Full capabilities is typically 0000003fffffffff or similar
        if [[ "$cap_eff" != "0000003fffffffff" ]] && [[ -n "$cap_eff" ]]; then
            echo -e "  ${GREEN}✓${NC} Capabilities are restricted"
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

    # Manual override for custom sandboxes
    if [[ "${RALPH_I_KNOW_WHAT_IM_DOING:-}" == "sandboxed" ]]; then
        log_warn "Manual sandbox override enabled"
        echo "   You've asserted this environment is sandboxed."
        echo "   Proceeding with caution..."
        echo ""
        return 0
    fi

    # Must be in a container/VM
    if [[ -z "$SANDBOX_TYPE" ]]; then
        print_sandbox_error
        exit 1
    fi

    # Must pass minimum checks
    if [[ $SANDBOX_CHECKS_PASSED -lt $MIN_SANDBOX_CHECKS ]]; then
        echo -e "${RED}Insufficient sandbox isolation${NC}"
        echo "Only $SANDBOX_CHECKS_PASSED of $MIN_SANDBOX_CHECKS required checks passed."
        echo ""
        echo "Please ensure:"
        echo "  - Network is disabled (--network none)"
        echo "  - Running as non-root user"
        echo "  - No access to ~/.ssh, ~/.aws, etc."
        exit 1
    fi

    log_success "Sandbox verified: $SANDBOX_TYPE (${SANDBOX_CHECKS_PASSED} checks passed)"
}

print_sandbox_error() {
    cat << 'EOF'

========================================================================
  RALPH REFUSED TO START - NO SANDBOX DETECTED
========================================================================

Ralph uses --dangerously-skip-permissions which can:
  - Delete files without confirmation
  - Read credentials (~/.ssh, ~/.aws)
  - Make network requests
  - Run arbitrary commands

To run Ralph safely:

1. Use the sandbox wrapper (recommended):
   ./ralph-sandbox.sh

2. Manual Docker:
   docker run --rm -it --network none \
     -v $(pwd):/workspace ralph-sandbox

3. Custom sandbox (experts only):
   RALPH_I_KNOW_WHAT_IM_DOING=sandboxed ./ralph.sh

========================================================================
EOF
}

#######################################
# MAIN LOOP
#######################################

main() {
    echo ""
    echo -e "${BLUE}Ralph Wiggum Mode v${VERSION}${NC}"
    echo "\"Me fail English? That's unpossible!\""
    echo ""

    # Enforce sandbox FIRST
    enforce_sandbox

    # Parse arguments
    local mode="${1:-build}"
    local max_iterations="${2:-0}"
    local iteration=0
    local model="${RALPH_MODEL:-opus}"

    # Select prompt file
    local prompt_file="RALPH_PROMPT.md"
    if [[ "$mode" == "plan" ]] && [[ -f "RALPH_PROMPT_plan.md" ]]; then
        prompt_file="RALPH_PROMPT_plan.md"
    elif [[ "$mode" == "build" ]] && [[ -f "RALPH_PROMPT_build.md" ]]; then
        prompt_file="RALPH_PROMPT_build.md"
    fi

    if [[ ! -f "$prompt_file" ]]; then
        log_error "Prompt file not found: $prompt_file"
        echo "Run ralph-init.sh first to set up Ralph in your project."
        exit 1
    fi

    log "Starting Ralph loop"
    log "  Mode: $mode"
    log "  Prompt: $prompt_file"
    log "  Model: $model"
    log "  Max iterations: ${max_iterations:-unlimited}"
    echo ""

    # Trap for graceful shutdown
    trap 'log "Received interrupt, finishing current iteration..."; exit 0' INT TERM

    # Main loop
    while true; do
        if [[ $max_iterations -gt 0 ]] && [[ $iteration -ge $max_iterations ]]; then
            log "Reached max iterations ($max_iterations)"
            break
        fi

        ((iteration++))
        log "=== Iteration $iteration ==="

        # Run Claude
        if ! cat "$prompt_file" | claude -p \
            --dangerously-skip-permissions \
            --model "$model" \
            --output-format stream-json \
            2>&1 | tee -a ralph.log; then
            log_warn "Claude exited with error, continuing to next iteration"
        fi

        # Commit progress
        if git diff --quiet && git diff --cached --quiet; then
            log "No changes to commit"
        else
            git add -A
            git commit -m "Ralph iteration $iteration" 2>/dev/null || true
            log "Committed changes"
        fi

        # Brief pause between iterations
        sleep 2
    done

    log "Ralph completed $iteration iterations"
    echo ""
    echo -e "${GREEN}Ralph finished!${NC}"
    echo "   Check ralph.log for details"
    echo "   Check git log for commits"
}

main "$@"
