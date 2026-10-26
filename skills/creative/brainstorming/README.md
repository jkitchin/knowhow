# Brainstorming & Ideation Facilitation Skill

Expert guidance for structured, productive brainstorming sessions using proven creativity frameworks.

## Overview

This skill enables Claude to facilitate professional-grade brainstorming and ideation sessions using established creativity techniques. Whether you need to generate ideas, break through creative blocks, explore solutions, or make better decisions, this skill provides structured approaches and facilitation expertise.

## When to Use

Use this skill when you need:
- Many ideas quickly
- Creative solutions to problems
- To break through mental blocks
- Structured ideation facilitation
- Help choosing between options
- Innovation and new perspectives
- Systematic idea exploration

## Triggers

The skill activates for requests like:
- "Help me brainstorm..."
- "Generate ideas for..."
- "What are creative solutions to..."
- "I need alternatives for..."
- "Think of different ways to..."
- "Break through creative block"
- "Innovative approaches to..."

## Core Techniques

### 1. SCAMPER Framework
Systematic idea generation through:
- **S**ubstitute - Replace elements
- **C**ombine - Merge ideas
- **A**dapt - Borrow from elsewhere
- **M**odify - Change attributes
- **P**ut to another use - Repurpose
- **E**liminate - Remove components
- **R**everse - Flip or invert

**Best for**: Product/service innovation, improving existing solutions

### 2. Six Thinking Hats
Explore from six perspectives:
- **White**: Facts and information
- **Red**: Emotions and intuition
- **Black**: Critical judgment
- **Yellow**: Optimism and benefits
- **Green**: Creativity and alternatives
- **Blue**: Process control

**Best for**: Complex decisions, comprehensive analysis

### 3. Mind Mapping
Visual exploration of:
- Central concepts
- Related themes
- Connections
- Hierarchies

**Best for**: Understanding complex topics, organizing thoughts

### 4. Rapid Ideation
High-intensity generation:
- Maximum quantity in minimum time
- No judgment during generation
- Push past obvious ideas
- 20-30 ideas in 10 minutes

**Best for**: Breaking blocks, getting unstuck quickly

### 5. Reverse Brainstorming
Problem inversion:
- "How could we make this worse?"
- Generate "bad" ideas
- Flip each to solutions
- Reveals blind spots

**Best for**: Identifying risks, fresh perspectives

### 6. Constraint-Based Creativity
Force innovation through limitations:
- Zero budget
- Extreme timelines
- Different users
- No technology
- 10x scale changes

**Best for**: Breaking assumptions, radical thinking

## Additional Resources

### References Directory

**techniques-detailed.md**
- Step-by-step guides for each technique
- Detailed facilitation instructions
- Examples and variations
- 25+ pages of technique expertise

**evaluation-frameworks.md**
- Impact vs Effort Matrix
- Weighted Scoring
- Feasibility Analysis
- Priority Matrices
- Group decision methods
- Complete guide to converging from many ideas to few

**prompts-library.md**
- 100+ creativity prompts
- 12 categories
- Organized by type
- Examples and usage guidance

### Scripts Directory

**random_prompt.py**
- Generate random creativity prompts
- Filter by category
- Command-line usage
- Perfect for breaking blocks

```bash
python scripts/random_prompt.py                 # Random prompt
python scripts/random_prompt.py constraint      # Constraint prompt
python scripts/random_prompt.py --list          # Show categories
python scripts/random_prompt.py --multiple 5    # Get 5 prompts
```

## Typical Session Flow

1. **Understand** (2-3 min)
   - Clarify the challenge
   - Define success
   - Set goals

2. **Choose Technique** (1 min)
   - Select based on situation
   - Can combine multiple

3. **Diverge** (10-20 min)
   - Generate many ideas
   - No evaluation
   - Quantity over quality
   - Push past obvious

4. **Organize** (3-5 min)
   - Group similar ideas
   - Count what you have
   - Identify themes

5. **Converge** (10-15 min)
   - Apply evaluation framework
   - Narrow to top options
   - Make decisions

6. **Action** (2-3 min)
   - Choose 1-3 to pursue
   - Define next steps
   - Document decisions

## Example Applications

### Product Development
- Feature brainstorming with SCAMPER
- Prioritization with Impact/Effort Matrix
- Risk assessment with Reverse Brainstorming

### Problem Solving
- Mind Mapping to understand
- Rapid Ideation to generate
- Six Hats for analysis

### Strategic Planning
- Six Thinking Hats for comprehensive view
- Constraint-based to challenge assumptions
- Weighted Scoring for decisions

### Innovation Challenges
- Constraint prompts to break conventions
- SCAMPER for systematic exploration
- Industry Transfer for cross-pollination

## Key Principles

**Diverge → Converge**
- Separate generation from evaluation
- Complete divergence before converging
- Never mix these phases

**Quantity First**
- More ideas = more good ideas
- Push past obvious (ideas 15-30 are gold)
- No idea is too wild

**Defer Judgment**
- Evaluation kills creativity
- "Yes, and..." not "Yes, but..."
- Build on everything

**Structure Helps**
- Frameworks guide thinking
- Constraints spark creativity
- Process reduces overwhelm

## Installation

```bash
# Install to personal directory
knowhow install brainstorming

# Install to project
knowhow install brainstorming --target project

# View detailed info
knowhow info brainstorming
```

## Usage Examples

### Quick Ideation
```
"Help me brainstorm marketing ideas for our product launch"
→ Rapid Ideation + Impact/Effort Matrix
```

### Complex Decision
```
"We need to decide our Q4 strategy - help me think through options"
→ Six Thinking Hats + Weighted Scoring
```

### Creative Block
```
"I'm stuck on how to improve our onboarding - nothing seems right"
→ Reverse Brainstorming + Constraint prompts
```

### Feature Development
```
"What could we do to make our app more engaging?"
→ SCAMPER + Evaluation frameworks
```

## Tips for Success

1. **Trust the process**: Follow the structure even when it feels awkward
2. **Commit to divergence**: Really generate quantity before evaluating
3. **Use time limits**: Time pressure focuses thinking
4. **Mix techniques**: Combine methods for richer results
5. **Document everything**: Even "bad" ideas spark good ones
6. **End with action**: Always conclude with concrete next steps

## Skill Structure

```
brainstorming/
├── SKILL.md                          # Main skill instructions (this is what Claude reads)
├── README.md                         # This file
├── references/
│   ├── techniques-detailed.md        # Deep dives on each technique
│   ├── evaluation-frameworks.md      # Complete evaluation guide
│   └── prompts-library.md            # 100+ creativity prompts
├── scripts/
│   └── random_prompt.py              # Random prompt generator
└── examples/
    └── sample-session.md             # Example brainstorming session
```

## Credits

Based on established creativity and brainstorming methodologies including:
- SCAMPER (Bob Eberle)
- Six Thinking Hats (Edward de Bono)
- Mind Mapping (Tony Buzan)
- Rapid Ideation techniques
- Constraint-based creativity research

## License

This skill is part of the knowhow repository and follows the repository's MIT license.

## Support

For issues, suggestions, or contributions:
- Repository: https://github.com/jkitchin/knowhow
- Issues: https://github.com/jkitchin/knowhow/issues
- Category: creative/brainstorming
