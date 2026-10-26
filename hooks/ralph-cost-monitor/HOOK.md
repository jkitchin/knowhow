---
name: ralph-cost-monitor
description: Track API costs during Ralph mode iterations and warn when approaching budget
event: Notification
matcher: ".*"
type: command
timeout: 5
---

# Ralph Cost Monitor

Tracks Claude API usage during Ralph Wiggum mode iterations and provides warnings when approaching budget limits.

## Purpose

Running Ralph overnight can consume significant API credits. This hook:
- Tracks token usage across iterations
- Estimates costs based on current pricing
- Warns when approaching budget limits
- Can halt Ralph if budget is exceeded

## Configuration

Set environment variables to configure:

```bash
# Maximum spend in USD (default: 50.00)
export RALPH_COST_LIMIT=50.00

# Warning threshold as percentage (default: 80)
export RALPH_COST_WARN_PCT=80

# Cost tracking file (default: .ralph-costs.json)
export RALPH_COST_FILE=.ralph-costs.json

# Action when limit exceeded: "warn" or "halt" (default: warn)
export RALPH_COST_ACTION=warn
```

## Token Pricing

Current pricing (updated July 2026):

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude Sonnet | $3.00 | $15.00 |
| Claude Opus | $5.00 | $25.00 |
| Claude Haiku | $1.00 | $5.00 |

## Usage

The hook automatically tracks costs when installed. View current costs:

```bash
# View cost summary
cat .ralph-costs.json | jq '.summary'

# View per-iteration breakdown
cat .ralph-costs.json | jq '.iterations'
```

## Cost File Format

```json
{
  "session_id": "ralph-1705678900",
  "started_at": "2025-01-19T12:00:00Z",
  "model": "opus",
  "limit_usd": 50.00,
  "summary": {
    "total_input_tokens": 1250000,
    "total_output_tokens": 450000,
    "estimated_cost_usd": 10.50,
    "iterations": 15
  },
  "iterations": [
    {
      "iteration": 1,
      "timestamp": "2025-01-19T12:00:00Z",
      "input_tokens": 85000,
      "output_tokens": 30000,
      "cost_usd": 0.70
    }
  ]
}
```

## Behavior

1. Hook receives notification events from Claude
2. Extracts token usage information
3. Updates cost tracking file
4. Checks against budget limit
5. If over warning threshold: logs warning
6. If over limit and action=halt: exits with code 2 (blocks)

## Notes

- Cost estimates are approximate based on known pricing
- Actual billing may vary slightly
- Hook is informational by default (doesn't block)
- Set `RALPH_COST_ACTION=halt` to enforce hard limits
