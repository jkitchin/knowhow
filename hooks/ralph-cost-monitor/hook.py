#!/usr/bin/env python3
"""Ralph cost monitor hook - Track API costs during Ralph mode."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Token pricing per 1M tokens (as of July 2026: Opus 5, Sonnet 4.6, Haiku 4.5)
PRICING = {
    "sonnet": {"input": 3.00, "output": 15.00},
    "opus": {"input": 5.00, "output": 25.00},
    "haiku": {"input": 1.00, "output": 5.00},
    # Fallback for unknown models
    "default": {"input": 5.00, "output": 25.00},
}


def get_pricing(model: str) -> dict:
    """Get pricing for a model."""
    model_lower = model.lower()
    for key in PRICING:
        if key in model_lower:
            return PRICING[key]
    return PRICING["default"]


def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate cost in USD for given token counts."""
    pricing = get_pricing(model)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 4)


def load_cost_file(filepath: Path) -> dict:
    """Load existing cost tracking file or create new one."""
    if filepath.exists():
        try:
            with open(filepath) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Create new tracking structure
    return {
        "session_id": f"ralph-{int(datetime.now().timestamp())}",
        "started_at": datetime.now().isoformat(),
        "model": os.environ.get("RALPH_MODEL", "opus"),
        "limit_usd": float(os.environ.get("RALPH_COST_LIMIT", "50.00")),
        "summary": {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "iterations": 0,
        },
        "iterations": [],
    }


def save_cost_file(filepath: Path, data: dict) -> None:
    """Save cost tracking file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def main():
    """Main hook entry point."""
    # Configuration
    cost_file = Path(os.environ.get("RALPH_COST_FILE", ".ralph-costs.json"))
    cost_limit = float(os.environ.get("RALPH_COST_LIMIT", "50.00"))
    warn_pct = float(os.environ.get("RALPH_COST_WARN_PCT", "80"))
    cost_action = os.environ.get("RALPH_COST_ACTION", "warn").lower()
    model = os.environ.get("RALPH_MODEL", "opus")

    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Not valid JSON, might be a simple notification
        sys.exit(0)

    # Try to extract token usage from notification
    # The exact structure depends on Claude's notification format
    notification = input_data.get("notification", {})
    usage = notification.get("usage", {})

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    # If no token data, nothing to track
    if input_tokens == 0 and output_tokens == 0:
        sys.exit(0)

    # Load or create cost tracking
    costs = load_cost_file(cost_file)

    # Calculate cost for this iteration
    iteration_cost = calculate_cost(input_tokens, output_tokens, model)

    # Update summary
    costs["summary"]["total_input_tokens"] += input_tokens
    costs["summary"]["total_output_tokens"] += output_tokens
    costs["summary"]["estimated_cost_usd"] += iteration_cost
    costs["summary"]["iterations"] += 1

    # Add iteration record
    costs["iterations"].append(
        {
            "iteration": costs["summary"]["iterations"],
            "timestamp": datetime.now().isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": iteration_cost,
        }
    )

    # Save updated costs
    save_cost_file(cost_file, costs)

    # Check against limits
    total_cost = costs["summary"]["estimated_cost_usd"]
    warn_threshold = cost_limit * (warn_pct / 100)

    if total_cost >= cost_limit:
        message = f"""COST LIMIT REACHED

Total spent: ${total_cost:.2f} / ${cost_limit:.2f} limit
Iterations: {costs["summary"]["iterations"]}
Input tokens: {costs["summary"]["total_input_tokens"]:,}
Output tokens: {costs["summary"]["total_output_tokens"]:,}

{"Halting Ralph mode." if cost_action == "halt" else "Consider stopping Ralph or increasing RALPH_COST_LIMIT."}
"""
        print(message, file=sys.stderr)

        if cost_action == "halt":
            sys.exit(2)  # Block further operations
        sys.exit(0)

    elif total_cost >= warn_threshold:
        message = f"""COST WARNING: Approaching limit

Spent: ${total_cost:.2f} / ${cost_limit:.2f} ({total_cost / cost_limit * 100:.1f}%)
Iterations: {costs["summary"]["iterations"]}
Remaining budget: ${cost_limit - total_cost:.2f}
"""
        print(message, file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
