---
name: planning
description: |
  Structured planning and project breakdown using proven methodologies for goals, projects,
  and strategic initiatives. Use when users need to create plans, break down complex projects,
  set milestones, estimate timelines, identify dependencies, or develop action plans.
  Triggers include 'help me plan,' 'create a roadmap for,' 'break down this project,'
  'what are the steps to,' or 'how should I approach.'
allowed-tools: ["*"]
---

# Planning & Project Breakdown Skill

Guide users through structured, realistic planning for projects, goals, and strategic initiatives using proven project management frameworks.

## Quick Start Workflow

When a planning request arrives, follow this systematic approach:

1. **Clarify**: Understand goal, constraints, deadline, resources
2. **Choose Approach**: Select planning methodology based on project type
3. **Decompose**: Break down into phases, milestones, and tasks
4. **Sequence**: Identify dependencies and critical path
5. **Estimate**: Set realistic timelines with buffers (20-30% for uncertain work)
6. **Define Success**: Establish milestones and success criteria
7. **Identify Risks**: Anticipate obstacles and plan mitigation
8. **Document**: Create clear, actionable plan

## When to Use This Skill

Activate for requests involving:
- "Help me plan..." / "Create a roadmap for..."
- "Break down this project..." / "What are the steps to..."
- "How should I approach..." / "Build a timeline for..."
- Strategic planning, project kickoff, goal setting

## Clarification Phase

Before planning, gather essential information:

**Goal & Scope**:
- What are you trying to achieve? (clear end state)
- What's in/out of scope?
- What would success look like?

**Constraints**:
- Deadline? Fixed or flexible?
- Resources available? (people, budget, tools)
- Dependencies? (external factors, approvals)
- Non-negotiables?

**Context**:
- Stakeholders? Decision makers?
- Past lessons learned?
- Similar projects to reference?

**Don't skip this**: 5 minutes of clarification saves hours later.

## Planning Approach Selector

Choose methodology based on project characteristics:

### Work Breakdown Structure (WBS)
**Use when**: Large, complex projects; scope unclear; need comprehensive task inventory

**Process**: Top-down decomposition (Project → Phases → Deliverables → Tasks)

**Best for**: Construction, IT projects, events, product launches

### Backward Planning
**Use when**: Fixed deadline; event planning; goal clear but path uncertain

**Process**: Start from end goal, work backwards identifying prerequisites

**Best for**: Event planning, product launches, campaigns, deadline-driven work

### Agile/Iterative Planning
**Use when**: Uncertain requirements; need flexibility; can deliver incrementally

**Process**: Plan in short iterations (sprints), adapt based on learning

**Best for**: Software development, research, new product development

### Phased/Milestone Planning
**Use when**: Long project (3+ months); need checkpoints; staged delivery

**Process**: Divide into phases with gates, plan phase-by-phase

**Best for**: Research, construction, strategic initiatives, transformation

### Hybrid Approach
**Combine methods**: WBS for decomposition + Agile for execution, etc.

See `references/frameworks-detailed.md` for detailed guides on each methodology.

## Core Frameworks (Concise)

### Work Breakdown Structure (WBS)

Hierarchical decomposition of work:

**Levels**: Project → Phases (3-7) → Deliverables → Tasks (1-3 days each) → Sub-tasks (if needed)

**100% Rule**: Each level represents 100% of parent's work

**Tips**:
- Nouns for deliverables, verbs for tasks
- Stop when tasks are 1-3 days
- 3-4 levels usually sufficient

### Backward Planning

**Process**:
1. Define end goal (what, when, success criteria)
2. Ask: "What must happen right before this?"
3. Continue backwards to present
4. Reverse sequence for forward plan
5. Add parallel tasks and dependencies
6. Estimate durations

**Key**: Be thorough with prerequisites - missing steps are common

### Critical Path Method

Identify longest sequence of dependent tasks (determines minimum duration):

**Concepts**:
- **Critical Path**: Tasks with zero slack (can't be delayed)
- **Float/Slack**: Time a task can delay without affecting project

**Use**: Focus management attention on critical path tasks

Use `scripts/critical_path.py` for calculation.

### Timeline Estimation

**Methods**:
- **Bottom-Up**: Estimate each task, sum up (most accurate)
- **Top-Down**: Estimate overall, allocate to phases (faster)
- **Three-Point**: (Optimistic + 4×Most Likely + Pessimistic) / 6
- **Analogous**: Compare to similar past projects

**Key Principles**:
- Include 20-30% buffers for uncertain work
- Distinguish effort vs duration (40 hours work ≠ 40 hours elapsed)
- Account for capacity (people aren't 100% productive)
- Add contingency for risk mitigation

**Avoid**: Planning fallacy (underestimating), optimism bias

See `references/estimation-techniques.md` for detailed methods.

### Milestones & Success Criteria

**Good Milestones**:
- Specific, measurable, meaningful
- Time-bound, visible to stakeholders
- Represent significant progress

**Types**: Deliverable completion, decision point, event, phase completion

**Spacing**: Weekly (short projects), bi-weekly/monthly (medium), monthly/quarterly (long)

### OKR Framework (Objectives & Key Results)

**Structure**: 1 Objective + 3-5 Key Results

**Objective**: Qualitative, aspirational goal (what to achieve)

**Key Results**: Quantitative measures (how to measure success)

**Example**:
- Objective: Launch product successfully to market
- Key Results: 1000 active users first month; NPS 50+; $50K MRR by Q4 end

**Use for**: Strategic planning, not tactical tasks

### SMART Goals

**S**pecific - **M**easurable - **A**chievable - **R**elevant - **T**ime-bound

**Example**: "Increase NPS from 30 to 50 by Q4 end through improved onboarding"

**Use for**: Individual goals, small initiatives

## Dependencies & Sequencing

### Dependency Types

**Finish-to-Start** (most common): B starts when A finishes

**Start-to-Start**: B starts when A starts

**Finish-to-Finish**: B finishes when A finishes

### Identifying Dependencies

**Ask for each task**:
- What must complete before this starts?
- What can run in parallel?
- What's waiting for this?
- Any external dependencies?

**Categories**: Mandatory (technical), Discretionary (preference), External (outside control), Internal (team control)

### Parallelization

**Look for**:
- Tasks with no dependencies
- Tasks with same prerequisites
- Tasks that can be split

**Benefit**: Shorter duration, better resource use

**Caution**: Don't over-parallelize (coordination overhead)

## Risk Management (Brief)

### Identification

**Common categories**: Schedule, Technical, Resource, External, Scope, Quality

**Ask**: "What could go wrong?" Review past issues. Use pre-mortems.

### Assessment

**For each risk**: Probability (1-5) × Impact (1-5) = Risk Score

**Prioritize**: High-score risks for mitigation

### Response Strategies

- **Avoid**: Eliminate risk by changing plan
- **Mitigate**: Reduce probability or impact
- **Transfer**: Shift to another party (insurance, contracts)
- **Accept**: Monitor with contingency plan

See `references/frameworks-detailed.md` for risk register template.

## Resource Planning (Brief)

### Categories

**People**: Roles, skills, time commitment, availability

**Tools**: Software, hardware, procurement time

**Budget**: Personnel, tools, contingency (10-20%)

**Other**: Space, materials, information access

### RACI Matrix

**R**esponsible (does work) - **A**ccountable (ultimately accountable) - **C**onsulted (provides input) - **I**nformed (kept in loop)

See `references/templates.md` for RACI template.

## Planning Horizons

**Strategic** (Annual/Quarterly): Goals, themes, major initiatives. Tools: OKRs, roadmaps. Review quarterly.

**Tactical** (Monthly/Sprint): Deliverables, projects. Tools: WBS, sprint planning. Review weekly.

**Operational** (Weekly/Daily): Immediate tasks. Tools: Task lists, kanban. Review daily.

**Principle**: Plan detail should match certainty - detailed near-term, high-level long-term.

## Agile/Iterative Planning (Brief)

### Sprint Planning (2-week iterations)

1. Review prioritized backlog
2. Select items based on team capacity
3. Break items into tasks
4. Estimate and commit
5. Define sprint goal

### Iteration Reviews

- **Demo**: Show completed work
- **Retrospective**: What went well, what to improve
- **Adapt**: Adjust for next iteration

**Tips**: Keep iterations short (1-2 weeks). Don't skip retrospectives. Protect from disruptions.

See `references/templates.md` for sprint planning template.

## Contingency Planning

### Buffers

**Schedule**: 20-30% for uncertain work, more for novel/complex

**Resource**: 10-20% budget contingency, backup personnel

**Scope**: Prioritize features (must-have vs nice-to-have), have cut list

### Plan B

**For critical paths, ask**:
- What if this takes 2x longer?
- What if resources unavailable?
- What if dependency fails?

**Document**: Trigger points, alternatives, decision makers

### Monitoring & Adaptation

**Track**: Compare actual vs planned, identify variances early

**Re-plan when**: Assumptions wrong, scope changes, resource changes, risks occur

**Remember**: Plans are tools, not contracts. Adapt when reality differs.

## Documentation Formats

### Essential Plan Elements

1. Goal/Objective (what and why)
2. Scope (included/excluded)
3. Timeline (key dates, milestones)
4. Tasks/Phases (work breakdown)
5. Dependencies (critical path)
6. Resources (who, what needed)
7. Risks (identified + responses)
8. Success Criteria (measurements)

### Output Formats

**High-Level Plan**:
```
PROJECT: [Name]
GOAL: [What achieving]
TIMELINE: [Start] - [End]
OWNER: [Person]

PHASES:
1. Phase Name (dates) - Major deliverables
2. Phase Name (dates) - Major deliverables

MILESTONES:
- [Date]: Milestone
- [Date]: Milestone

TOP RISKS:
1. Risk [Mitigation]
2. Risk [Mitigation]
```

**Detailed Task List**:
```
TASK: [Description]
├─ Owner: [Person]
├─ Duration: [Estimate]
├─ Dependencies: [Prerequisites]
├─ Deliverable: [Output]
└─ Status: [Not started/In progress/Complete]
```

Use `scripts/timeline_visualizer.py` for visual timelines.

See `assets/templates/` for ready-to-use formats.

## Common Patterns

**Product Launch**: Backward plan from launch date, include dry-run, post-launch monitoring

**Research Project**: WBS + phased approach, exploratory time, iteration based on findings

**Event Planning**: Backward plan, critical path for venue/speakers, detailed day-of checklist

**Software Dev**: Agile sprints, testing in each iteration, deployment and monitoring

**Process Improvement**: Phased rollout, training/change management, measurement cycles

## Tips for Effective Facilitation

1. **Start with why** - Ensure goal clarity before methodology
2. **Right-size approach** - Don't over-plan simple projects
3. **Involve the team** - People doing work should help plan
4. **Plan iteratively** - Start high-level, refine progressively
5. **Include buffers** - Be realistic about uncertainty
6. **Make it visual** - Diagrams > text walls
7. **Assign ownership** - Every task needs owner
8. **Plan for learning** - First time takes longer
9. **Build in reviews** - Regular check-ins catch issues early
10. **Stay flexible** - Reality trumps plans

## Using Supporting Resources

Additional resources in this skill:

- **references/frameworks-detailed.md**: Step-by-step methodology guides
- **references/estimation-techniques.md**: Complete time estimation methods
- **references/templates.md**: Ready-to-use planning templates
- **scripts/critical_path.py**: Calculate project critical path
- **scripts/timeline_visualizer.py**: Generate visual timelines
- **assets/templates/**: Markdown and CSV templates for immediate use

Reference these for deeper guidance or ready-made formats.

---

**Remember**: The best plan is the one that gets executed. Make plans clear, actionable, and realistic. Perfect planning is the enemy of starting.
