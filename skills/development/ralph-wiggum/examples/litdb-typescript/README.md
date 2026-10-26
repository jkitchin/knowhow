# Ralph Wiggum Example: Converting litdb to TypeScript

This example demonstrates how to use Ralph Wiggum mode to autonomously convert [litdb](https://github.com/jkitchin/litdb), a Python literature database tool, into a standalone TypeScript library and CLI with high test coverage.

## Project Overview

**Original Project:** [jkitchin/litdb](https://github.com/jkitchin/litdb)
- Python-based literature database for researchers
- 43 CLI commands for managing academic papers
- Vector search, full-text search, and hybrid search
- Integration with OpenAlex, DOIs, ORCIDs
- SQLite/LibSQL storage with embeddings

**Target:** `litdb-ts`
- TypeScript library (`@litdb/core`)
- CLI tool (`litdb` command)
- 90%+ test coverage
- Modern Node.js architecture (ESM)
- Same feature set as Python version

## Why This is a Good Ralph Project

1. **Well-defined scope** - Clear Python reference to port
2. **Measurable progress** - Tests and coverage provide feedback
3. **Incremental** - Can implement command-by-command
4. **Long-running** - Too big for a single session, perfect for overnight runs

## Prerequisites

```bash
# Install Ralph Wiggum skill
skillin install ralph-wiggum
skillin hooks install ralph-safety-check
skillin hooks install ralph-cost-monitor

# Ensure Docker is installed
docker --version
```

## Step-by-Step Setup

### Step 1: Create Project Directory

```bash
mkdir litdb-ts
cd litdb-ts
git init
```

### Step 2: Initialize Ralph

```bash
# Copy Ralph files (or run ralph-init.sh)
cp ~/.claude/skills/ralph-wiggum/scripts/*.sh .
cp ~/.claude/skills/ralph-wiggum/templates/* .
chmod +x *.sh
```

### Step 3: Copy Example Specifications

```bash
# Copy the specifications from this example
cp -r ~/.claude/skills/ralph-wiggum/examples/litdb-typescript/specs .
cp ~/.claude/skills/ralph-wiggum/examples/litdb-typescript/IMPLEMENTATION_PLAN.md .
cp ~/.claude/skills/ralph-wiggum/examples/litdb-typescript/RALPH_PROMPT.md .
cp ~/.claude/skills/ralph-wiggum/examples/litdb-typescript/Dockerfile.ralph .
```

### Step 4: Verify Claude Code Authentication

```bash
# Claude Code subscription users - already authenticated!
claude --version

# API key users (alternative) - set this only if not using subscription
# export ANTHROPIC_API_KEY=your-key-here
```

### Step 5: Run Ralph

```bash
# Start with planning mode (optional, recommended)
./ralph-sandbox.sh . 5 plan

# Review the plan, then run build mode
./ralph-sandbox.sh . 50 build

# Or run unlimited overnight
./ralph-sandbox.sh
```

### Step 6: Monitor Progress

In another terminal:

```bash
# Watch the log
tail -f ralph.log

# Check git commits
watch -n 10 'git log --oneline -10'

# Check test coverage
cat coverage/coverage-summary.json 2>/dev/null | jq '.total'

# Check costs
cat .ralph-costs.json | jq '.summary'
```

### Step 7: Review Results

```bash
# See what Ralph accomplished
git log --oneline

# Check implementation status
cat IMPLEMENTATION_PLAN.md

# Run tests manually to verify
npm test

# Check coverage report
open coverage/lcov-report/index.html
```

## Expected Timeline

With Claude Opus (the default), expect roughly:

| Phase | Iterations | Estimated Time |
|-------|------------|----------------|
| Project setup | 2-3 | 15 min |
| Core database layer | 5-8 | 1 hour |
| Search functionality | 8-12 | 2 hours |
| CLI commands (43 total) | 40-60 | 6-8 hours |
| Test coverage boost | 10-20 | 2 hours |
| Polish & docs | 5-10 | 1 hour |

**Total: ~80-110 iterations, 12-14 hours**

This is ideal for an overnight run. Start Ralph at 6 PM, wake up to a working TypeScript port.

## Cost Estimation

**Claude Code Subscription:** Included in your subscription - no per-token costs!

**API Key Users:** Rough estimate with Claude Opus ($5/$25 per 1M tokens):
- ~100 iterations
- ~50k input tokens + ~20k output tokens per iteration
- Cost: ~$40-75 total (less with prompt caching)
- Set `RALPH_COST_LIMIT=100` to cap spending

## Customization

### Adjust Iterations Per Session

```bash
# Quick test (5 iterations)
./ralph-sandbox.sh . 5

# Medium run (20 iterations)
./ralph-sandbox.sh . 20

# Full overnight (unlimited)
./ralph-sandbox.sh
```

### Use Different Model

```bash
# Faster, cheaper (but less capable)
RALPH_MODEL=haiku ./ralph-sandbox.sh . 50

# Mid-tier cost alternative to the default opus
RALPH_MODEL=sonnet ./ralph-sandbox.sh . 30
```

### Enable Network for npm install

Edit `ralph-sandbox.sh` to allow specific registries:

```bash
# Change --network none to:
--network bridge \
```

Or pre-install dependencies before running Ralph.

## Monitoring & Control

Ralph runs autonomously, but you maintain full visibility and control.

### Real-Time Monitoring

Open a second terminal to watch Ralph's progress:

```bash
# Live log stream
tail -f ralph.log

# Watch commits appear
watch -n 5 'git log --oneline -10'

# Task completion counter
watch -n 30 'echo "Done: $(grep -c "^\- \[x\]" IMPLEMENTATION_PLAN.md) / $(grep -c "^\- \[" IMPLEMENTATION_PLAN.md)"'

# Test status (if tests are running)
watch -n 60 'npm test 2>&1 | tail -10'

# Coverage progress
watch -n 120 'cat coverage/coverage-summary.json 2>/dev/null | jq ".total.lines.pct" || echo "No coverage yet"'
```

### Stopping Ralph

```bash
# Graceful stop - Ctrl+C in Ralph's terminal
# Waits for current operation to finish

# Force stop - find and kill container
docker ps | grep ralph
docker kill <container-id>

# Or kill all ralph containers
docker kill $(docker ps -q --filter "name=ralph-")
```

### Redirecting Mid-Run

Since all state is in files, you can guide Ralph between iterations:

```bash
# Add urgent guidance to the prompt
cat >> RALPH_PROMPT.md << 'EOF'

## URGENT (added mid-run)
- Stop adding new features
- Focus only on fixing failing tests
- Do not modify src/db/client.ts
EOF

# Mark a task as blocked
sed -i 's/- \[ \] Implement auth/- [!] BLOCKED: Implement auth - needs human review/' IMPLEMENTATION_PLAN.md

# Add a note for Ralph
cat >> IMPLEMENTATION_PLAN.md << 'EOF'

## Human Notes
- The OpenAlex API is rate-limited, use mocks for now
- Skip the PDF extraction feature for v1
EOF
```

### Pause/Resume Pattern

Add this convention to your `RALPH_PROMPT.md`:

```markdown
## Pause Check
At the start of each iteration, check:
- If file `PAUSE` exists, stop gracefully and exit
- If file `RESUME_NOTES.md` exists, read it for guidance
```

Then control Ralph with:

```bash
# Pause Ralph after current iteration
touch PAUSE

# Add instructions for when Ralph resumes
cat > RESUME_NOTES.md << 'EOF'
When resuming:
1. The auth module has a bug - check src/auth/token.ts line 45
2. Skip vector search for now, focus on FTS
3. Run `npm run lint` before committing
EOF

# Resume by removing pause file
rm PAUSE
```

### Checkpointing Strategy

Use git branches for safe experimentation:

```bash
# Before starting Ralph
git checkout -b ralph-run-1

# After Ralph runs, if satisfied
git checkout main
git merge ralph-run-1

# If Ralph went off track
git checkout main
git checkout -b ralph-run-2  # Fresh start

# Cherry-pick good work from failed run
git cherry-pick abc123 def456
```

### Progress Dashboard

Create a simple status check:

```bash
# One-liner status
echo "Tasks: $(grep -c '^\- \[x\]' IMPLEMENTATION_PLAN.md)/$(grep -c '^\- \[' IMPLEMENTATION_PLAN.md) | Commits: $(git rev-list --count HEAD) | Tests: $(npm test 2>&1 | grep -oP '\d+ passed' || echo 'N/A')"
```

Or use the helper script:

```bash
./run-example.sh status
```

### When to Intervene

**Let Ralph continue if:**
- Tests are passing
- Commits are appearing regularly
- Task count is increasing

**Intervene if:**
- No commits for 30+ minutes (might be stuck)
- Same test failing repeatedly in logs
- Ralph is modifying files outside the project
- Error messages repeating in ralph.log

## Troubleshooting

### Ralph Gets Stuck

Check `ralph.log` for errors. Common issues:
- Missing dependencies (pre-run `npm install`)
- Test failures blocking progress
- Context filling up on large files

Solution: Add blockers to `IMPLEMENTATION_PLAN.md` and restart.

### Tests Keep Failing

Ralph should fix failing tests, but if stuck:
1. Review the failing tests in `ralph.log`
2. Add specific guidance in `RALPH_PROMPT.md`
3. Restart Ralph

### Cost Limit Reached

```bash
# Check current spend
cat .ralph-costs.json | jq '.summary.estimated_cost_usd'

# Increase limit and continue
RALPH_COST_LIMIT=100 ./ralph-sandbox.sh
```

## Files in This Example

```
examples/litdb-typescript/
├── README.md                    # This file
├── IMPLEMENTATION_PLAN.md       # Phased task list
├── RALPH_PROMPT.md             # Custom prompt for this project
├── Dockerfile.ralph            # Node.js sandbox container
└── specs/
    ├── overview.md             # High-level architecture
    ├── database.md             # Database schema spec
    ├── search.md               # Search functionality spec
    ├── cli-commands.md         # CLI command specifications
    ├── testing.md              # Testing requirements
    └── api-reference.md        # Public API design
```

## Success Criteria

Ralph is "done" when:
- [ ] All 43 CLI commands implemented
- [ ] `npm test` passes
- [ ] Coverage > 90%
- [ ] `npm run build` produces working dist/
- [ ] `litdb --help` shows all commands
- [ ] Basic smoke test: add paper, search, export bibtex

## Next Steps After Ralph

1. **Human review** - Review all generated code
2. **Integration tests** - Add end-to-end tests
3. **Documentation** - Expand README, add JSDoc
4. **Publishing** - Set up npm publishing workflow
5. **CI/CD** - Add GitHub Actions

---

*This example demonstrates Ralph's ability to tackle large, well-defined porting projects. The key is thorough specifications and a clear implementation plan.*
