# Planning & Project Breakdown Skill

Expert guidance for structured, realistic planning using proven project management frameworks and methodologies.

## Overview

This skill enables Claude to facilitate professional-grade project planning and breakdown using established planning methodologies. Whether you need to create project plans, estimate timelines, identify risks, allocate resources, or develop strategic roadmaps, this skill provides structured approaches and planning expertise.

## When to Use

Use this skill when you need:
- Project or initiative planning
- Work breakdown and task decomposition
- Timeline estimation and scheduling
- Risk identification and mitigation
- Resource allocation planning
- Milestone and success criteria definition
- Strategic roadmap development
- Backward planning from deadlines
- Dependency identification
- Contingency planning

## Triggers

The skill activates for requests like:
- "Help me plan..."
- "Create a roadmap for..."
- "Break down this project..."
- "What are the steps to..."
- "How should I approach..."
- "Build a timeline for..."
- "Estimate how long..."
- "Identify risks for..."

## Core Capabilities

### 1. Work Breakdown Structure (WBS)
Hierarchical decomposition into manageable components:
- **Project → Phases → Deliverables → Tasks**
- 100% rule ensures completeness
- Progressive detail (stop at 1-3 day tasks)
- Clear accountability

**Best for**: Large complex projects, scope definition, comprehensive task inventory

### 2. Backward Planning
Start from deadline and work backwards:
- Define end state precisely
- Identify immediate prerequisites
- Work backwards to present
- Calculate buffer times
- Reverse to forward timeline

**Best for**: Fixed deadlines, events, product launches, deadline-driven work

### 3. Critical Path Method (CPM)
Identify longest sequence determining minimum duration:
- Forward pass (early start/finish)
- Backward pass (late start/finish)
- Calculate float/slack
- Focus on critical tasks

**Best for**: Complex dependencies, schedule optimization, resource prioritization

**Tool**: Use `scripts/critical_path.py` for automated calculation

### 4. Timeline Estimation
Realistic duration forecasting:
- **Bottom-up**: Estimate each task, sum up
- **Top-down**: Estimate overall, allocate
- **Three-point**: (Optimistic + 4×Likely + Pessimistic) / 6
- **Analogous**: Compare to past projects
- **Parametric**: Use historical data rates

**Includes**: 20-30% buffers, effort vs duration, capacity planning

### 5. Agile/Iterative Planning
Short cycles with adaptation:
- Sprint planning (2-week iterations)
- Velocity tracking
- Backlog grooming
- Daily standups
- Retrospectives

**Best for**: Uncertain requirements, software development, need for flexibility

### 6. Phased/Milestone Planning
Staged approach with checkpoints:
- Phase gates and reviews
- Stage-by-stage approval
- Risk reviews at transitions
- Progress milestones

**Best for**: Long projects (3+ months), regulatory requirements, staged delivery

### 7. Risk Management
Proactive risk identification and mitigation:
- Risk identification (categories, pre-mortems)
- Assessment (probability × impact)
- Response strategies (avoid, mitigate, transfer, accept)
- Trigger indicators and contingency plans

**Template**: Use `assets/templates/risk_register_template.csv`

### 8. Resource Planning
People, tools, budget allocation:
- RACI matrix (Responsible, Accountable, Consulted, Informed)
- Capacity planning
- Budget estimation with contingency
- External dependencies

### 9. OKRs & SMART Goals
Strategic objective setting:
- **OKRs**: Objectives + Key Results (3-5 measurable outcomes)
- **SMART**: Specific, Measurable, Achievable, Relevant, Time-bound
- Quarterly/annual goal frameworks

**Best for**: Strategic planning, team goals, outcome focus

### 10. Contingency Planning
Prepare for uncertainty:
- Schedule buffers (20-30% for novel work)
- Budget contingency (10-20%)
- Scope priorities (must-have vs nice-to-have)
- Plan B for critical paths
- Re-planning triggers

## Quick Start Workflow

When a planning request arrives:

1. **Clarify** (5 min)
   - Goal and success criteria
   - Constraints (time, budget, resources)
   - Dependencies and assumptions
   - Stakeholders

2. **Choose Approach** (2 min)
   - Select methodology based on project type
   - Can combine multiple methods
   - Match approach to certainty level

3. **Decompose** (15-30 min)
   - Break into phases/deliverables/tasks
   - Identify dependencies
   - Assign owners

4. **Sequence** (10-20 min)
   - Order by dependencies
   - Identify parallel work
   - Calculate critical path

5. **Estimate** (15-30 min)
   - Duration estimates
   - Add buffers (20-30%)
   - Account for capacity

6. **Define Success** (10 min)
   - Milestones
   - Success metrics
   - Acceptance criteria

7. **Identify Risks** (15 min)
   - What could go wrong
   - Mitigation strategies
   - Contingency plans

8. **Document** (10 min)
   - Clear, actionable plan
   - Owners and deadlines
   - Next steps

## Additional Resources

### References Directory

**frameworks-detailed.md**
- Step-by-step WBS process
- Backward planning guide
- Critical Path Method (CPM) calculation
- Agile sprint planning
- Phased/milestone planning
- Risk management framework
- Resource planning (RACI)
- 675+ lines of detailed methodology guides

**estimation-techniques.md**
- Bottom-up estimation
- Top-down estimation
- Three-point estimation
- Analogous estimation
- Parametric estimation
- Buffer strategies (when to add 20%, 30%, 50%)
- Effort vs Duration concepts
- Common biases and mitigation
- 500+ lines of estimation expertise

**templates.md**
- Project charter template
- WBS templates (outline & hierarchical)
- Risk register template
- RACI matrix template
- Project plan one-pager
- Sprint planning template
- Retrospective template
- Status report template
- Milestone tracker
- Gantt chart structures
- 670+ lines of ready-to-use templates

### Scripts Directory

**critical_path.py**
- Calculate critical path from JSON task list
- Forward/backward pass algorithm
- Float/slack calculation
- Gantt-style visualization
- JSON output format

```bash
python scripts/critical_path.py tasks.json
python scripts/critical_path.py --example > tasks.json
python scripts/critical_path.py tasks.json --output results.json
```

**timeline_visualizer.py**
- ASCII/markdown timeline visualization
- Multiple styles: gantt, roadmap, calendar
- Shows parallel tasks and milestones
- Month/week/day granularity

```bash
python scripts/timeline_visualizer.py timeline.json
python scripts/timeline_visualizer.py --example > timeline.json
python scripts/timeline_visualizer.py timeline.json --style roadmap
python scripts/timeline_visualizer.py timeline.json --style calendar
```

### Assets Directory

**assets/templates/**
- `project_plan_template.md` - Comprehensive project plan (all sections)
- `sprint_plan_template.md` - Agile sprint planning template
- `risk_register_template.csv` - CSV risk tracking with examples

## Typical Planning Session Flow

1. **Understand** (5-10 min)
   - Clarify goal and constraints
   - Identify stakeholders
   - Define success

2. **Select Methodology** (2 min)
   - Choose framework(s)
   - May combine multiple approaches

3. **Plan** (30-60 min)
   - Apply chosen methodology
   - Break down work
   - Estimate durations
   - Identify dependencies

4. **Refine** (15-30 min)
   - Add buffers
   - Identify risks
   - Allocate resources
   - Set milestones

5. **Document** (10-15 min)
   - Create actionable plan
   - Define next steps
   - Assign owners

## Example Applications

### Product Launch
- Backward plan from launch date
- Include dry-run and post-launch monitoring
- Risk assessment for marketing, technical, and user adoption
- Phased approach: Beta → Limited → Full launch

### Software Development
- Agile sprints for iterative development
- Critical path for infrastructure dependencies
- WBS for comprehensive feature breakdown
- Continuous testing and integration

### Research Project
- Phased approach with exploratory time
- WBS for methodology design
- Milestones at each phase gate
- Contingency for unexpected findings

### Event Planning
- Backward planning from event date
- Critical path for venue/speakers/catering
- Detailed day-of checklist
- Risk mitigation for weather, no-shows, technical issues

### Process Improvement
- Phased rollout (pilot → department → organization)
- Change management planning
- Training timeline
- Success measurement cycles

## Planning Principles

**Right-Size the Approach**
- Simple projects need simple plans
- Complex projects warrant comprehensive planning
- Don't over-plan

**Involve the Team**
- People doing work should help plan
- Multiple perspectives improve estimates
- Creates buy-in and commitment

**Plan Iteratively**
- Start high-level
- Add detail progressively
- Don't plan too far ahead in detail

**Include Buffers**
- 20-30% for uncertain work
- More for novel/complex tasks
- Account for unknowns

**Stay Flexible**
- Plans are tools, not contracts
- Adapt when reality differs
- Re-plan when assumptions change

## Installation

```bash
# Install to personal directory
skillin install planning

# Install to project
skillin install planning --target project

# View detailed info
skillin info planning
```

## Usage Examples

### Project Planning
```
"Help me plan a website redesign project with a 3-month timeline"
→ Clarify scope → Choose WBS + Phased approach → Create detailed plan
```

### Timeline Estimation
```
"How long will it take to migrate our database to the cloud?"
→ Break down tasks → Apply estimation techniques → Add buffers → Create timeline
```

### Risk Assessment
```
"What risks should I consider for launching this new product?"
→ Risk identification → Assessment → Mitigation strategies → Contingency plans
```

### Agile Sprint Planning
```
"Help me plan our next 2-week sprint with these user stories"
→ Capacity calculation → Story breakdown → Commitment → Sprint goal
```

### Backward Planning
```
"We're launching December 1st - help me work backwards to create a plan"
→ Define end state → Identify prerequisites → Work backwards → Create timeline
```

## Tips for Success

1. **Clarify before planning**: 5 minutes of clarification saves hours later
2. **Use appropriate detail**: Match planning depth to certainty and timeline
3. **Include buffers**: Under-promising and over-delivering builds trust
4. **Identify dependencies early**: They're often the critical path
5. **Plan for risks**: Hope for the best, plan for the realistic
6. **Document clearly**: Plans are communication tools
7. **Review regularly**: Compare actual to plan, learn and adapt
8. **Make plans actionable**: Every task needs an owner and deadline

## Skill Structure

```
planning/
├── SKILL.md                          # Main skill instructions (what Claude reads)
├── README.md                         # This file
├── references/
│   ├── frameworks-detailed.md        # Detailed methodology guides
│   ├── estimation-techniques.md      # Complete estimation guide
│   └── templates.md                  # Ready-to-use planning templates
├── scripts/
│   ├── critical_path.py              # CPM calculator
│   └── timeline_visualizer.py        # Timeline rendering
├── assets/
│   └── templates/
│       ├── project_plan_template.md
│       ├── sprint_plan_template.md
│       └── risk_register_template.csv
└── examples/
    └── sample-planning-session.md    # Example planning session
```

## Credits

Based on established project management methodologies including:
- Work Breakdown Structure (WBS)
- Critical Path Method (CPM)
- Agile/Scrum framework
- PMBOK® (Project Management Body of Knowledge)
- OKRs (Objectives and Key Results)
- SMART goals framework
- Risk management best practices

## License

This skill is part of the skillin repository and follows the repository's MIT license.

## Support

For issues, suggestions, or contributions:
- Repository: https://github.com/jkitchin/skillz
- Issues: https://github.com/jkitchin/skillz/issues
- Category: productivity/planning
