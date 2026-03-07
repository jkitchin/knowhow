# Design of Experiments (DOE) Skill

Comprehensive experimental design guidance with interactive, goal-driven approach.

## Quick Start

**Don't start with a method—start with questions:**

1. What's your goal? (screening, optimization, exploration, robustness)
2. Can you run sequentially or batch only?
3. How expensive are experiments?
4. How many factors?
5. Do you have prior knowledge or a model?

Based on answers, get personalized design recommendations.

## Structure

- **SKILL.md** - Main file with decision trees, quick starts, and workflows
- **references/** - Detailed guides for each approach
- **scripts/** - Tested Python implementations

## Quick Reference

| Your Situation | Use This | Tool |
|----------------|----------|------|
| Batch, 2-5 factors, optimize | CCD or Box-Behnken | pyDOE3, pycse |
| Sequential, expensive, optimize | Bayesian Optimization | BoTorch, skopt, Ax |
| Have mechanistic model | Model-driven D-optimal | Custom FIM |
| Build surrogate, sequential | Active Learning + GP | modAL |
| Many factors, screening | Fractional factorial | pyDOE3 |

## Installation

```bash
pip install pyDOE3 dexpy pycse scikit-optimize statsmodels scipy scikit-learn modAL GPy matplotlib seaborn
```

## Key Insight

**Sequential > Batch** when:
- Experiments are expensive
- Can get results quickly
- Unknown landscape

**Batch > Sequential** when:
- Parallel equipment available
- Setup cost dominates
- Well-understood system

## Files Included

Main skill file providing interactive guidance and quick starts.

See `SKILL.md` for complete documentation.
