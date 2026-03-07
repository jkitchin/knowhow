# CASCADE-Inspired Skill Evolution

Skillz includes a suite of tools for autonomous skill improvement, inspired by the
**CASCADE** framework (Cumulative Agentic Skill Creation through Autonomous Development
and Evolution) described in [arxiv:2512.23880](https://arxiv.org/abs/2512.23880).

CASCADE demonstrates that AI agents can autonomously create, accumulate, select, and
evolve reusable skills over time, leading to measurably better performance. Skillz
implements these concepts through five commands:

| CASCADE Phase | Skillz Command | What It Does |
|---------------|----------------|--------------|
| **Creation** | `skillz harvest` | Extract skills from session transcripts |
| **Evolution** | `skillz optimize` | Improve descriptions via eval feedback |
| **Selection** | `skillz ab-test` | Compare description variants, pick the best |
| **Quality Metrics** | `skillz stats` | Track usage frequency and identify gaps |
| **Composition** | `skillz merge` | Detect overlaps and combine skills |

## Quick Start

```bash
# See what skills you have and how they're used
skillz stats --scan

# Improve a skill's triggering accuracy
skillz optimize python-jax

# Compare multiple description variants
skillz ab-test python-jax

# Extract new skills from your work sessions
skillz harvest

# Find and fix redundant skills
skillz merge
```

## Commands

### `skillz harvest` - Skill Creation from Sessions

Analyzes Claude Code session transcripts to identify reusable patterns that could
become new skills. This implements CASCADE's **creation and accumulation** phase.

```bash
# Analyze 5 most recent sessions (default)
skillz harvest

# Analyze a specific transcript
skillz harvest -t ~/.claude/projects/.../session.jsonl

# Analyze more sessions
skillz harvest -r 10

# Generate SKILL.md files for proposals
skillz harvest --generate

# Preview without creating files
skillz harvest --generate --dry-run

# Output to specific directory
skillz harvest --generate -o ./my-skills/
```

**How it works:**
1. Reads Claude Code session transcripts (`.jsonl` files)
2. Sends transcript content to Claude for analysis
3. Claude identifies generalizable patterns and proposes skill definitions
4. Optionally generates complete SKILL.md files with interactive input

**Transcript locations:**
- Default: `~/.claude/projects/*/*.jsonl`
- Custom: Use `-t` flag to specify a specific file

**Tips:**
- Sessions with diverse problem-solving tend to yield better skill proposals
- Review proposals carefully — not every solution is worth generalizing
- Use `--dry-run` first to see what would be proposed
- Generated skills may need manual refinement before installation

---

### `skillz optimize` - Skill Evolution

Improves a skill's description for better triggering accuracy. This implements
CASCADE's **evolution** phase where skills are refined through feedback.

```bash
# Optimize a single skill
skillz optimize python-jax

# Optimize all skills in the repository (batch mode)
skillz optimize --all

# Preview without saving
skillz optimize python-jax --dry-run

# Generate eval queries only (useful for debugging)
skillz optimize python-jax --evals-only

# Batch mode, dry run
skillz optimize --all --dry-run
```

**How it works:**
1. Reads the skill's SKILL.md content
2. Generates 15 evaluation queries (8-10 should-trigger, 5-7 should-not-trigger)
3. Uses the evals to identify triggering gaps in the current description
4. Proposes an improved description that addresses the gaps
5. Shows both descriptions for comparison
6. Saves the improved version (with confirmation)

**Batch mode (`--all`):**
- Iterates through every skill in the repository
- Shows proposals one at a time with confirmation prompts
- Can skip individual skills or abort the batch
- Tracks succeeded/failed/skipped counts

**Tips:**
- Use `--evals-only` to verify that the eval queries make sense before optimizing
- Use `--dry-run` with `--all` to preview changes across the entire library
- Skills with vague descriptions benefit most from optimization
- Run after creating new skills to improve their discoverability

---

### `skillz ab-test` - Quality-Based Selection

Generates multiple description variants and scores each against evaluation queries
to find the best performer. This implements CASCADE's **selection** phase.

```bash
# Test 3 variants (default)
skillz ab-test python-jax

# Test more variants for higher confidence
skillz ab-test python-jax -n 5

# Preview without saving
skillz ab-test python-jax --dry-run
```

**How it works:**
1. Generates evaluation queries (same as optimize)
2. Scores the current description against the evals
3. Generates N variant descriptions, each with a different emphasis:
   - Variant 1: Focus on specific trigger phrases
   - Variant 2: Focus on distinguishing from similar skills
   - Variant 3: Focus on breadth of coverage
4. Scores each variant against the same evals
5. Displays a comparison table with scores
6. Recommends the winner and offers to apply it

**Scoring dimensions:**
- **Should-Trigger Correct:** How many valid queries would trigger the skill
- **Should-Not-Trigger Correct:** How many invalid queries would be rejected
- **Total Score:** Combined accuracy
- **Weaknesses:** What the description misses

**Tips:**
- Use more variants (`-n 5` or `-n 7`) for important skills
- If the current description wins, it's already well-optimized
- Variants with different emphases may reveal blind spots
- Combine with `skillz stats` to prioritize which skills to A/B test

---

### `skillz stats` - Usage Tracking & Quality Metrics

Tracks which skills are used, how often, and identifies unused skills that may need
optimization or removal. This implements CASCADE's **quality metrics** for selection.

```bash
# Show usage statistics
skillz stats

# Scan transcripts for skill mentions (more accurate)
skillz stats --scan

# Show only unused skills
skillz stats --unused

# Show top 10 most-used skills
skillz stats --top 10

# Sort by name or size instead of usage
skillz stats --sort name
skillz stats --sort size

# Manually log a skill usage event
skillz stats --log python-jax

# Reset all statistics
skillz stats --reset
```

**How it works:**
- Maintains a usage log at `~/.config/skillz/stats/usage.jsonl`
- Records skill name, timestamp, and source for each usage event
- With `--scan`, also searches recent session transcripts for skill name mentions
- Displays a sortable table with usage counts and skill sizes

**Data sources:**
1. **Manual logging:** Use `--log` to record when you use a skill
2. **Transcript scanning:** `--scan` checks recent `.jsonl` files for mentions
3. **Hook integration:** (future) Automatically log via Claude Code hooks

**Tips:**
- Run `skillz stats --scan` periodically to get usage estimates
- Use `--unused` to find skills that may need better descriptions
- Skills with zero usage are candidates for optimization or removal
- High usage + large size = skills worth investing in quality

---

### `skillz merge` - Skill Composition

Detects overlapping skills and proposes merges or reorganizations. This implements
CASCADE's **composition** phase where skills are combined and deduplicated.

```bash
# Detect overlaps across all skills
skillz merge

# Preview only (no changes)
skillz merge --dry-run

# Merge two specific skills
skillz merge --execute python-jax python-numpy --merged-name python-array-computing

# Merge with dry run
skillz merge --execute skill-a skill-b --dry-run
```

**How it works:**

**Detection mode (default):**
1. Reads names and descriptions of all skills in the repository
2. Sends to Claude for overlap analysis
3. Reports groups of related skills with recommendations:
   - **Overlap:** Skills covering the same domain → merge
   - **Complementary:** Skills that work together → cross-reference
   - **Hierarchy:** Parent/child relationships → reorganize

**Execution mode (`--execute`):**
1. Reads full content of both skills
2. Generates a merged SKILL.md combining the best of both
3. Shows the merged content for review
4. Saves to the repository (in the same category as the first skill)
5. Preserves originals — you remove them manually

**Tips:**
- Run detection first to see what Claude recommends
- Not all overlaps need merging — complementary skills can coexist
- Always review merged content before accepting
- After merging, run `skillz optimize` on the merged skill
- Consider hierarchy (subskills) as an alternative to full merges

---

## The Skill Lifecycle

These five commands form a complete skill lifecycle:

```
                    ┌──────────────┐
            ┌──────│   HARVEST    │──────┐
            │      │  (Creation)  │      │
            │      └──────────────┘      │
            │                            │
            ▼                            │
    ┌──────────────┐            ┌──────────────┐
    │   OPTIMIZE   │◄──────────│    STATS     │
    │  (Evolution) │            │  (Metrics)   │
    └──────────────┘            └──────────────┘
            │                            ▲
            ▼                            │
    ┌──────────────┐            ┌──────────────┐
    │   AB-TEST    │───────────►│    MERGE     │
    │ (Selection)  │            │(Composition) │
    └──────────────┘            └──────────────┘
```

**Typical workflow:**

1. **Work normally** with Claude Code — sessions are recorded as transcripts
2. **Harvest** new skills from sessions: `skillz harvest`
3. **Track** which skills get used: `skillz stats --scan`
4. **Optimize** underperforming skills: `skillz optimize --all`
5. **A/B test** important skills: `skillz ab-test python-jax`
6. **Merge** redundant skills: `skillz merge`
7. Repeat — skills improve over time through this evolutionary cycle

## Prerequisites

All CASCADE commands require the `claude` CLI to be installed and available in your
PATH. Install it from https://claude.ai/code.

The commands use Claude to analyze transcripts, generate proposals, score descriptions,
and create merged skills. Each invocation makes 1-5 Claude CLI calls depending on the
command and options.

## References

- **CASCADE Paper:** Chen, Y. et al. (2024). "CASCADE: Cumulative Agentic Skill
  Creation through Autonomous Development and Evolution."
  [arxiv:2512.23880](https://arxiv.org/abs/2512.23880)
- **Skillz Repository:** https://github.com/jkitchin/skillz
