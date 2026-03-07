---
name: troubleshooting
description: |
  Systematic debugging and problem diagnosis using structured troubleshooting methodologies
  applicable to any domain - technical issues, process failures, system problems, or general
  obstacles. Use when users report errors, describe malfunctions, encounter unexpected behavior,
  or need help diagnosing root causes. Triggers include 'debug this,' 'troubleshoot,' 'why isn't
  this working,' 'getting an error,' 'something's wrong with,' 'how do I fix,' or any problem
  description.
allowed-tools: ["*"]
---

# Troubleshooting & Debugging Skill

Guide users through systematic problem diagnosis and resolution using structured methodologies applicable to any domain.

## Quick Start Workflow

When a troubleshooting request arrives, follow this systematic approach:

1. **Understand** - What's expected vs actual, when started, what changed
2. **Gather** - Collect diagnostic information (logs, errors, environment, steps to reproduce)
3. **Hypothesize** - List possible causes ranked by probability
4. **Design** - Create tests that isolate variables
5. **Test** - Execute systematically, document results
6. **Identify** - Distinguish symptoms from root cause
7. **Verify** - Confirm fix resolves the issue
8. **Document** - Record solution for future reference

## When to Use This Skill

Activate for requests involving:
- "Debug this..." / "Troubleshoot..."
- "Why isn't this working..." / "Getting an error..."
- "Something's wrong with..." / "How do I fix..."
- Any problem description or malfunction report
- Unexpected behavior or failures
- Performance issues or degradation
- Intermittent problems

## Problem Understanding Phase

### Essential First Questions

Before diving into solutions, gather critical context:

**Problem Description:**
- What are you trying to do? (expected behavior)
- What's actually happening? (actual behavior)
- What error messages or symptoms do you see?
- Can you reproduce it consistently?

**Timeline:**
- When did this start?
- Did it ever work correctly?
- What changed recently? (code, config, environment, data, dependencies)

**Scope:**
- Does this happen every time or intermittently?
- Does it happen for everyone or just some users?
- Does it happen in all environments or just specific ones?

**Environment:**
- What system/platform/version?
- What's the configuration?
- What are the dependencies and their versions?

**Reproduction:**
- What are the exact steps to reproduce?
- Can you provide a minimal example that demonstrates the issue?
- What's the simplest case that fails?

### Problem Type Classification

Categorize to guide troubleshooting approach:

**By Consistency:**
- **Consistent** - Happens every time (easier to debug)
- **Intermittent** - Happens sometimes (harder, often timing/race conditions)
- **Progressive** - Gets worse over time (resource leaks, degradation)

**By History:**
- **Regression** - Worked before, broke recently (what changed?)
- **Never worked** - New feature/setup (design or setup issue)

**By Scope:**
- **Universal** - Happens everywhere (likely code/logic issue)
- **Environmental** - Happens in specific environment (config, dependencies, resources)
- **User-specific** - Happens for specific users (permissions, data, state)

**By Domain:**
- **Code/Logic** - Software bugs, algorithmic errors
- **Configuration** - Settings, parameters, environment variables
- **Data** - Input validation, corruption, format issues
- **Infrastructure** - Network, storage, resources, services
- **Integration** - API failures, service dependencies
- **Human process** - Workflow, communication, missing steps

Classification helps prioritize hypotheses and diagnostic approaches.

## Diagnostic Information Gathering

### Log and Error Analysis

**Error Messages:**
- Copy exact error text (don't paraphrase)
- Note error code/type if provided
- Identify stack trace or error location
- Look for nested/chained errors (root cause often deeper)

**Log Examination:**
- Check timestamps (when did issue occur)
- Look for ERROR, WARN, EXCEPTION entries near failure time
- Trace request/operation ID through logs
- Check for patterns (repeating errors, sequences)
- Review logs before failure (what was system doing)

**System State:**
- Resource usage (CPU, memory, disk, network)
- Process/service status
- Recent restarts or crashes
- System event logs

### Environment Documentation

Capture complete environment picture:

**Versions:**
- Application/service version
- Runtime/interpreter version (Node, Python, Java, etc.)
- OS version
- Dependency versions (libraries, packages)
- Database/cache versions

**Configuration:**
- Config files and their values
- Environment variables
- Feature flags or toggles
- Settings that differ from defaults

**Infrastructure:**
- Network topology
- Service endpoints and connectivity
- Firewall/security rules
- Load balancers, proxies
- DNS configuration

### Reproduction Case Development

**Goal**: Find minimal reproducible example (MRE)

**Process:**
1. Document exact steps from clean state
2. Strip away non-essential steps
3. Minimize data/input to simplest case
4. Remove dependencies where possible
5. Verify it still reproduces

**Good reproduction case:**
- Anyone can follow steps and see same issue
- Minimal (fewest steps, smallest data)
- Self-contained (no external dependencies if possible)
- Deterministic (reproduces consistently)

See `references/information-gathering.md` for detailed techniques.

## Hypothesis Generation

### Forming Testable Hypotheses

**Generate possibilities:**
- Brainstorm what could cause observed symptoms
- Consider each problem type (code, config, data, infrastructure)
- Review known failure patterns for this domain
- Don't self-censor - list everything plausible

**Rank by probability:**
- Most likely causes first
- Consider base rates (common vs rare failures)
- Factor in recent changes
- Weight by evidence strength

**Make hypotheses testable:**
- "If X is the cause, then Y should be true"
- Design specific test that would confirm/refute
- Ensure test is practical to execute

**Example hypotheses (ranked):**
1. **High probability:** Recent config change introduced typo → Check config against previous version
2. **Medium probability:** Dependency version mismatch → Verify all dependencies match working environment
3. **Low probability:** Hardware failure → Run diagnostics, check system logs for hardware errors

### Common Failure Patterns

**Code/Logic:** Off-by-one, null/undefined, type mismatch, logic errors, unhandled edge cases, race conditions

**Configuration:** Typos, wrong environment variables, permissions, path issues, missing settings

**Data:** Invalid format, null/empty values, corruption, encoding issues, schema mismatch

**Infrastructure:** Network connectivity, port conflicts, insufficient resources, permissions, services, firewall

**Integration:** API changes, expired credentials, rate limiting, timeouts, version incompatibility

See `references/hypothesis-generation.md` and `references/domain-specific-patterns.md` for comprehensive patterns.

## Systematic Testing

### Scientific Method Principles

**Change one variable at a time:**
- Modify single factor per test
- Know exactly what you changed
- Document change and result
- Reset to baseline between tests

**Verify assumptions:**
- Don't assume anything works
- Test each layer (can you reach service? is it responding? is auth working?)
- Question "obvious" things
- Build confidence from known-good baseline

**Isolate variables:**
- Remove unnecessary components
- Test in controlled environment
- Disable features to narrow scope
- Use minimal configuration

**Document everything:**
- What you tested
- What you changed
- What happened (exact result)
- Conclusions drawn
- Next steps

Use `scripts/hypothesis_tracker.py` to maintain investigation log.

### Binary Search Troubleshooting

**Concept**: Divide problem space in half, determine which half contains issue, repeat.

**Applications:**
- **Version bisect:** Which commit introduced bug? (git bisect)
- **Config narrowing:** Which of 50 config settings causes issue?
- **Data range:** Which records in dataset cause failure?
- **Code sections:** Which function/module has the bug?
- **Time range:** When did problem start occurring?

**Process:**
1. Identify search space boundaries (working ↔ broken)
2. Test midpoint
3. Determine which half contains issue
4. Repeat with smaller range
5. Continue until isolated to specific element

**Example - Config debugging:**
- Start: All 50 config settings (broken)
- Disable half (25 settings) → Still broken
- Issue is in disabled half
- Disable half of those (12-13) → Works!
- Issue is in recently disabled set
- Continue narrowing...
- Result: Isolated to single problematic setting

Use `scripts/binary_search_helper.py` for interactive guidance.

### Differential Diagnosis

Compare working vs non-working cases to identify differences:

**Compare:**
- Configurations
- Environments
- Data inputs
- Dependencies
- Timing/sequence
- System state

**Look for:**
- What's present in failing case but not working case
- What's different between the two
- What versions differ
- What settings differ

**Technique:**
- Start with known-good case
- Progressively make it more like failing case
- Stop when you introduce the failure
- That change is the cause

## Root Cause Analysis

### 5 Whys Technique

Dig deeper by asking "why" repeatedly (typically 5 times):

**Example:**
1. **Problem:** Website is down
2. **Why?** Database connection failed
3. **Why?** Connection pool exhausted
4. **Why?** Connections not being released
5. **Why?** Code missing connection.close() in error path
6. **Why?** Developer didn't know about finally blocks
7. **Root cause:** Missing error-handling training, missing code review checklist

**Guidelines:**
- Each "why" should be factual (not speculative)
- Stop when you reach actionable root cause
- May need more or fewer than 5 whys
- Focus on process/system causes, not blaming people

### Distinguishing Symptoms from Root Cause

**Symptom:** Observable manifestation of problem
**Root Cause:** Underlying reason problem exists

**Example:**
- **Symptom:** Application crashes
- **Symptom:** Out of memory error
- **Symptom:** Memory leak in caching module
- **Root Cause:** Cache eviction policy not implemented

**Test:** Would fixing this prevent all instances of the problem?
- If no → It's a symptom, keep digging
- If yes → Likely root cause

**Verify:**
- Fix the root cause
- Test that all symptoms disappear
- Verify issue doesn't recur

See `references/diagnostic-frameworks.md` for Fishbone diagrams and FMEA.

## Troubleshooting Principles

**Core Principles:**

1. **Reproduce before fixing** - If you can't reproduce it, you can't verify the fix

2. **Change one thing at a time** - Otherwise you won't know what fixed it

3. **Verify assumptions** - "It should work" ≠ "It does work"

4. **Start with simple explanations** - Occam's Razor (common problems are common)

5. **Follow the data** - Believe logs/evidence over intuition

6. **Work from known-good baseline** - Establish what works, then build up

7. **Document as you go** - Your future self will thank you

8. **Know when to stop** - Time-box investigation, escalate if stuck

9. **Avoid confirmation bias** - Look for evidence that disproves your hypothesis too

10. **Treat the disease, not symptoms** - Fix root cause, not just visible symptoms

## Domain-Specific Guidance

**Software/Code:** Syntax errors, logic bugs, runtime errors, concurrency issues, memory problems
- Use debugger, add logging, rubber duck debugging, review changes, check typos

**System/Infrastructure:** Network, permissions, services, ports, resources, configuration
- Check service status, test connectivity, review logs, verify config, check resources

**Process/Workflow:** Missing steps, unmet dependencies, communication gaps, timing issues
- Map actual vs expected process, identify handoffs, check prerequisites

See `references/domain-specific-patterns.md` for comprehensive diagnostic approaches by domain.

## Common Anti-Patterns to Avoid

❌ **Change multiple things at once** - You won't know what fixed it
❌ **Assume without verifying** - "It worked last week" doesn't mean it works now
❌ **Skip reproduction** - Can't verify fix without reproducing first
❌ **Pursue only favorite hypothesis** - Confirmation bias blinds you
❌ **Give up on intermittent issues** - Often most critical
❌ **Forget to document** - Others will duplicate your work
❌ **Treat symptoms not root cause** - Suppressing errors doesn't fix problems
❌ **Blame the user** - Stops investigation prematurely
❌ **Rush to solution** - Premature fixes waste time

## Solution Verification

**After implementing fix:**

1. **Test reproduction case** - Does it now work?

2. **Test edge cases** - Does fix work in all scenarios?

3. **Regression check** - Did fix break anything else?

4. **Performance check** - Did fix introduce performance issues?

5. **Monitor in production** - Watch for recurrence or side effects

6. **Verify with users** - Confirm issue is resolved from their perspective

## Documentation

**Document for future:**

**Troubleshooting Log:**
- Problem description
- Investigation steps
- Hypotheses tested
- Results of each test
- Root cause identified
- Solution implemented

Use `assets/templates/troubleshooting_log_template.md`

**Root Cause Analysis Report:**
- Executive summary
- Problem statement
- Timeline of events
- Root cause analysis (5 Whys, Fishbone)
- Corrective actions
- Preventive measures

Use `assets/templates/rca_report_template.md`

**Reproduction Steps:**
- Minimal reproduction example
- Prerequisites
- Step-by-step instructions
- Expected vs actual results

Use `assets/templates/reproduction_steps_template.md`

## When to Escalate

**Know when to ask for help:**

- You've exhausted reasonable hypotheses
- Issue is outside your domain expertise
- Problem is time-critical and investigation is taking too long
- You need access/permissions you don't have
- Problem appears to be in external system
- You've been going in circles (revisiting same hypotheses)

**Before escalating:**
- Document what you've tried
- Share reproduction case
- Provide all diagnostic information
- Explain your hypothesis and reasoning
- Suggest what help you need

## Using Supporting Resources

Additional resources in this skill:

- **references/diagnostic-frameworks.md**: 5 Whys, Fishbone, FMEA, Binary Search, Comparative Analysis
- **references/information-gathering.md**: Log analysis, error interpretation, environment documentation
- **references/hypothesis-generation.md**: Failure patterns, hypothesis ranking, test design
- **references/domain-specific-patterns.md**: Common issues by domain (software, systems, hardware, process, data)
- **scripts/hypothesis_tracker.py**: Track hypotheses and test results
- **scripts/binary_search_helper.py**: Interactive binary search guidance
- **assets/templates/**: Documentation templates for investigation logs, RCA reports, reproduction cases

Reference these for deeper guidance on specific techniques.

---

**Remember**: The best debuggers are methodical, patient, and systematic. Resist the urge to jump to solutions. Follow the data. Document your process. The answer will reveal itself through systematic elimination.
