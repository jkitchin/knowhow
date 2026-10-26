# Troubleshooting & Debugging Skill

Systematic problem diagnosis and resolution using structured methodologies applicable to any domain.

## Overview

This skill enables Claude to guide users through professional troubleshooting using established diagnostic methodologies. Whether debugging code, diagnosing system issues, resolving configuration problems, or investigating process failures, this skill provides systematic approaches and proven techniques.

## When to Use

Use this skill when encountering:
- Errors, exceptions, or failures
- Unexpected behavior or wrong output
- Performance degradation
- Intermittent problems
- System malfunctions
- Process breakdowns
- "Why isn't this working?"

## Core Methodology

### Universal Troubleshooting Workflow

1. **Understand** - Expected vs actual, timeline, scope
2. **Gather** - Logs, errors, environment, reproduction steps
3. **Hypothesize** - List possible causes ranked by likelihood
4. **Design** - Create tests that isolate variables
5. **Test** - Execute systematically, document results
6. **Identify** - Distinguish symptoms from root cause
7. **Verify** - Confirm fix resolves issue
8. **Document** - Record solution for future reference

### Key Principles

**Change one thing at a time** - Know what fixed it
**Verify assumptions** - Don't assume anything works
**Reproduce before fixing** - Can't verify fix without reproduction
**Document everything** - For yourself and others
**Follow the data** - Believe evidence over intuition
**Know when to escalate** - Time-box investigation

## Diagnostic Frameworks

###  5 Whys Method
Dig to root cause by asking "why" repeatedly (typically 5 times).

**Example:**
1. Why? → Database connection failed
2. Why? → Connection pool exhausted
3. Why? → Connections not being released
4. Why? → Missing connection.close() in error path
5. Why? → Developer unaware of finally blocks

**Root cause:** Missing training + code review checklist

### Fishbone/Ishikawa Diagram
Explore all possible causes organized by category (6 M's: Man, Machine, Method, Material, Measurement, Mother Nature).

### Binary Search Troubleshooting
Divide problem space in half repeatedly until isolated.

**Applications:**
- Git bisect (which commit)
- Config narrowing (which setting)
- Data range (which records)
- Time range (when did it start)

Use `scripts/binary_search_helper.py` for interactive guidance.

### Hypothesis-Driven Debugging
Scientific method: observe → hypothesize → predict → experiment → analyze → conclude.

**Good hypothesis:**
- Specific and testable
- Based on evidence
- Falsifiable

Use `scripts/hypothesis_tracker.py` to track investigation.

### Comparative Analysis
Compare working vs non-working cases to identify differences.

See `references/diagnostic-frameworks.md` for detailed guides on each methodology.

## Information Gathering

### Essential Questions

**Problem:** What's expected vs actual? Error messages? Reproducible?
**Timeline:** When did it start? What changed? Did it ever work?
**Scope:** All users or some? All environments or specific?
**Environment:** System, versions, configuration?

### Log Analysis

**Look for:**
- ERROR, FATAL, EXCEPTION entries
- Patterns (repeated errors, sequences)
- Context around failure time
- Stack traces (read bottom-to-top)

### Reproduction Case

**Goal:** Minimal reliable reproduction
- Fewest steps
- Smallest data
- Self-contained
- Documented

See `references/information-gathering.md` for comprehensive techniques.

## Domain-Specific Patterns

### Software/Code
- Syntax errors → Compiler/interpreter tells you
- Null references → Stack trace shows where
- Logic errors → Debug with breakpoints
- Race conditions → Intermittent, timing-dependent
- Memory leaks → Gradual slowdown

### System/Infrastructure
- Network issues → ping, telnet, curl
- Permissions → Check file/user permissions
- Service down → systemctl status, ps
- Resources → top, df, netstat

### Configuration
- Typos → Compare to documentation
- Wrong environment → Compare configs
- Paths → Absolute vs relative

### Data
- Invalid format → Examine actual vs expected
- Null/empty → Missing required fields
- Encoding → UTF-8, Latin-1, etc.

See `references/domain-specific-patterns.md` for comprehensive patterns.

## Using Supporting Tools

### Scripts

**hypothesis_tracker.py** - Track hypotheses and test results
```bash
python hypothesis_tracker.py add "Config typo in DB URL" --priority high
python hypothesis_tracker.py test H001 "Check config.yaml"
python hypothesis_tracker.py result H001 fail "URL is correct"
python hypothesis_tracker.py list
python hypothesis_tracker.py summary
```

**binary_search_helper.py** - Interactive binary search guidance
```bash
python binary_search_helper.py
# Follow interactive prompts to narrow down problem space
```

### Templates

**troubleshooting_log_template.md** - Document investigation process
- Problem description
- Hypotheses tested
- Root cause analysis
- Solution and verification

**rca_report_template.md** - Formal root cause analysis report
- Executive summary
- Timeline
- 5 Whys analysis
- Corrective actions
- Preventive measures

**reproduction_steps_template.md** - Document how to reproduce issue
- Minimal steps
- Prerequisites
- Expected vs actual results
- Environment details

## Example Troubleshooting Session

**Problem:** Users can't log in, getting "Invalid credentials" error

**1. Gather Information**
- When: Started 2 hours ago
- Who: All users affected
- Where: Production only
- What changed: Database migration deployed
- Error: "Invalid credentials" even with correct password

**2. Generate Hypotheses** (ranked)
1. HIGH: Database connection pointing to wrong database
2. MEDIUM: Password hashing algorithm changed
3. LOW: User table was truncated

**3. Test Hypotheses**

**Hypothesis 1:** Database connection to wrong DB
- Test: Check DB_HOST environment variable
- Result: Points to old database that was decommissioned! ✅
- Verify: Check users in old database → Table IS truncated

**ROOT CAUSE FOUND:** Environment variable pointing to wrong database

**4. Fix & Verify**
- Fix: Update DB_HOST to correct database
- Test: Users can now log in ✅
- Verify: Monitor for 1 hour, no issues

**5. Document**
- Update deployment checklist: verify env vars
- Add monitoring alert for failed login rate
- Document in RCA report for team

## Tips for Success

1. **Start with questions** - Understand before diagnosing
2. **Reproduce reliably** - Can't fix what you can't reproduce
3. **One variable at a time** - Know what changed
4. **Document as you go** - You'll forget what you tried
5. **Be systematic** - Follow the methodology
6. **Trust the process** - Resist urge to jump to solutions
7. **Know when to stop** - Time-box and escalate if stuck

## Common Anti-Patterns

❌ Changing multiple things at once
❌ Assuming without verifying
❌ Skipping reproduction
❌ Confirmation bias (only looking for evidence of favorite theory)
❌ Giving up on intermittent issues
❌ Not documenting
❌ Treating symptoms not root cause
❌ Rushing to solution

## Installation

```bash
# Install to personal directory
skillpack install troubleshooting

# Install to project
skillpack install troubleshooting --target project

# View detailed info
skillpack info troubleshooting
```

## Skill Structure

```
troubleshooting/
├── SKILL.md                                # Main skill instructions
├── README.md                               # This file
├── references/
│   ├── diagnostic-frameworks.md            # 5 Whys, Fishbone, FMEA, Binary Search, etc.
│   ├── information-gathering.md            # Log analysis, error interpretation
│   ├── hypothesis-generation.md            # Forming and ranking hypotheses
│   └── domain-specific-patterns.md         # Common issues by domain
├── scripts/
│   ├── hypothesis_tracker.py               # Track investigation process
│   └── binary_search_helper.py             # Interactive binary search guide
└── assets/templates/
    ├── troubleshooting_log_template.md     # Investigation documentation
    ├── rca_report_template.md              # Root cause analysis report
    └── reproduction_steps_template.md      # Reproduction case format
```

## Credits

Based on established troubleshooting and diagnostic methodologies including:
- 5 Whys (Toyota Production System)
- Ishikawa/Fishbone Diagrams (Kaoru Ishikawa)
- FMEA (Failure Mode and Effects Analysis)
- Scientific Method
- Binary Search algorithms
- Software debugging best practices

## License

This skill is part of the skillpack repository and follows the repository's MIT license.

## Support

For issues, suggestions, or contributions:
- Repository: https://github.com/jkitchin/skillpack
- Issues: https://github.com/jkitchin/skillpack/issues
- Category: technical/troubleshooting
