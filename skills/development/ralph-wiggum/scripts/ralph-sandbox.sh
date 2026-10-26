#!/bin/bash
# ralph-sandbox.sh - Run Ralph Wiggum mode safely in Docker
#
# Usage: ./ralph-sandbox.sh [project-dir] [max-iterations] [mode]
#
# Arguments:
#   project-dir     - Path to project (default: current directory)
#   max-iterations  - Maximum iterations, 0 for unlimited (default: 0)
#   mode           - "build" or "plan" (default: build)
#
# Environment variables:
#   ANTHROPIC_API_KEY  - Optional: Only needed if not using Claude Code subscription
#   RALPH_MODEL        - Optional: Model to use (default: opus)

set -euo pipefail

PROJECT_DIR="${1:-.}"
MAX_ITERATIONS="${2:-0}"
MODE="${3:-build}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Ralph Sandbox Launcher${NC}"
echo ""

# Check project directory
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo -e "${RED}Error: Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

PROJECT_DIR="$(realpath "$PROJECT_DIR")"

# Check for required files
if [[ ! -f "$PROJECT_DIR/ralph.sh" ]]; then
    echo -e "${RED}Error: ralph.sh not found in $PROJECT_DIR${NC}"
    echo "Run ralph-init.sh first to set up Ralph in your project."
    exit 1
fi

if [[ ! -f "$PROJECT_DIR/RALPH_PROMPT.md" ]]; then
    echo -e "${RED}Error: RALPH_PROMPT.md not found in $PROJECT_DIR${NC}"
    echo "Run ralph-init.sh first to set up Ralph in your project."
    exit 1
fi

# Build sandbox image if needed
IMAGE_NAME="ralph-sandbox"
DOCKERFILE="$PROJECT_DIR/Dockerfile.ralph"

if [[ -f "$DOCKERFILE" ]]; then
    echo "Building sandbox image from $DOCKERFILE..."
    docker build -t "$IMAGE_NAME" -f "$DOCKERFILE" "$PROJECT_DIR"
elif ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "Building default sandbox image..."
    docker build -t "$IMAGE_NAME" - << 'DOCKERFILE'
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

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

# Create non-root user
RUN useradd -m -s /bin/bash -u 1000 ralph && \
    mkdir -p /workspace && \
    chown -R ralph:ralph /workspace

USER ralph
WORKDIR /workspace

CMD ["./ralph.sh"]
DOCKERFILE
fi

echo ""
echo -e "${GREEN}Starting Ralph in sandbox...${NC}"
echo "   Project: $PROJECT_DIR"
echo "   Mode: $MODE"
echo "   Max iterations: ${MAX_ITERATIONS:-unlimited}"
echo "   Network: disabled"
echo "   Memory limit: 4GB"
echo "   CPU limit: 2 cores"
echo ""

# Build docker run arguments
DOCKER_ARGS=(
    --rm -it
    --name "ralph-$(date +%s)"
    --network none
    --memory 4g
    --cpus 2
    --pids-limit 100
    --cap-drop ALL
    --security-opt no-new-privileges:true
    -v "$PROJECT_DIR:/workspace"
    -e "RALPH_MODEL=${RALPH_MODEL:-opus}"
)

# Pass API key if set (optional - Claude Code subscription doesn't need it)
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    DOCKER_ARGS+=(-e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY")
fi

# Run in sandbox
docker run "${DOCKER_ARGS[@]}" \
    "$IMAGE_NAME" \
    ./ralph.sh "$MODE" "$MAX_ITERATIONS"

echo ""
echo -e "${GREEN}Ralph sandbox session ended.${NC}"
echo "Check $PROJECT_DIR/ralph.log for details."
