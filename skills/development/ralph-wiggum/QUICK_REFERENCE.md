# Ralph Wiggum Mode - Quick Reference

## Setup (One-Time)

```bash
# Install skill and hooks
skillpack install ralph-wiggum
skillpack hooks install ralph-safety-check
skillpack hooks install ralph-cost-monitor
```

## Project Setup

```bash
# Initialize Ralph in project
./ralph-init.sh

# Or manually copy files
cp ~/.claude/skills/ralph-wiggum/scripts/* .
cp ~/.claude/skills/ralph-wiggum/templates/* .
chmod +x ralph.sh ralph-sandbox.sh
```

## Running Ralph

```bash
# Set API key
export ANTHROPIC_API_KEY=your-key

# Run with Docker sandbox (recommended)
./ralph-sandbox.sh              # Unlimited iterations
./ralph-sandbox.sh . 20         # Max 20 iterations
./ralph-sandbox.sh . 5 plan     # Planning mode

# Monitor progress (in another terminal)
tail -f ralph.log
git log --oneline -10
```

## Key Files

| File | Purpose |
|------|---------|
| `RALPH_PROMPT.md` | Instructions for each iteration |
| `IMPLEMENTATION_PLAN.md` | Task list (update this!) |
| `specs/` | Put requirements here |
| `ralph.log` | Iteration logs |

## Task Markers

```markdown
- [ ] Pending task
- [~] In progress
- [x] Completed
- [!] Blocked
```

## Environment Variables

```bash
export ANTHROPIC_API_KEY=...     # Optional (not needed with Claude Code subscription)
export RALPH_MODEL=opus        # Model (sonnet/opus/haiku)
export RALPH_COST_LIMIT=50.00    # Budget in USD
```

## Safety

- **Always use `./ralph-sandbox.sh`** (not `./ralph.sh` directly)
- Ralph refuses to run outside Docker
- Network is disabled in sandbox
- Set iteration limits for cost control

## Troubleshooting

```bash
# Check logs
tail -100 ralph.log

# Check Docker
docker ps
docker logs ralph-*

# Check costs
cat .ralph-costs.json | jq '.summary'

# Reset
rm ralph.log .ralph-costs.json
git checkout IMPLEMENTATION_PLAN.md
```

## Quick Tips

1. **Small tasks** - One task per iteration works best
2. **Specific prompts** - Tell Claude exactly what to do
3. **Monitor costs** - Check `.ralph-costs.json` periodically
4. **Review output** - Always review before merging
5. **Use planning mode** - Run `plan` before `build` for complex features
