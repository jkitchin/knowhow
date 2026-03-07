# Design Selection Guide

## Decision Framework

Selecting the right experimental design requires matching your constraints to the appropriate methodology. Use this guide to systematically narrow your options.

## Primary Decision: Sequential vs Batch

**Can you observe results before choosing the next experiment?**

- **Yes** -> Sequential methods (Bayesian optimization, active learning, model-driven sequential)
- **No** -> Batch methods (factorial, response surface, space-filling)
- **Partially** -> Hybrid (staged experiments with batch phases)

## Batch Design Selection

### Screening (Identify Important Factors)

| Factors | Budget   | Recommended Design        | Runs Required    |
|---------|----------|---------------------------|------------------|
| 2-5     | Generous | Full factorial (2^k)      | 4-32             |
| 4-8     | Moderate | Fractional factorial      | 8-16             |
| 6-15    | Tight    | Plackett-Burman           | 12-20            |
| 5-12    | Moderate | Definitive Screening (DSD)| 2k+1 runs        |

```python
import pyDOE3 as pyd

# Fractional factorial: 6 factors in 16 runs (2^(6-2))
design = pyd.fracfact('a b c d ab cd')

# Plackett-Burman: screen 7 factors in 8 runs
design = pyd.pbdesign(8)
```

### Optimization (Find Best Settings)

| Factors | Design              | Runs   | Best When                    |
|---------|---------------------|--------|------------------------------|
| 2-3     | Central Composite   | 13-20  | Need rotatability            |
| 3-5     | Box-Behnken         | 13-46  | Avoid extreme corners        |
| 2-5     | Full factorial + center | varies | Simple, interpretable     |

```python
# Central Composite Design for 3 factors
ccd = pyd.ccdesign(3, center=(4, 4), face='ccf')

# Box-Behnken for 3 factors
bbd = pyd.bbdesign(3, center=3)
```

### Exploration (Map Unknown Space)

| Knowledge  | Design             | Spacing     | Use Case                   |
|------------|--------------------|-------------|----------------------------|
| None       | Latin Hypercube    | Space-fill  | Initial survey             |
| Some       | Augmented LHS      | Adaptive    | Build on existing data     |
| Mixture    | Simplex lattice    | Constrained | Components sum to 1        |

```python
# Latin Hypercube: 5 factors, 50 runs
lhs = pyd.lhs(5, samples=50, criterion='maximin')
```

## Sequential Design Selection

| Situation                        | Method                | Key Advantage           |
|----------------------------------|-----------------------|-------------------------|
| Expensive black-box optimization | Bayesian Optimization | Minimizes total runs    |
| Have mechanistic model           | D-optimal sequential  | Best parameter estimates|
| Need accurate surrogate          | Active learning       | Targeted data collection|
| Multiple competing models        | T-optimal / KL-design | Model discrimination    |

## Factor Type Considerations

- **All continuous** -> Any design works
- **Mix of continuous + categorical** -> D-optimal, split-plot
- **All categorical** -> Full/fractional factorial
- **Mixture (sum to 1)** -> Simplex designs, mixture regression
- **Constrained region** -> D-optimal with constraints, candidate-based

## Quick Checklist Before Starting

1. Define measurable response variable(s)
2. List all factors and their ranges
3. Identify any constraints or forbidden combinations
4. Determine budget (max runs)
5. Decide if sequential execution is feasible
6. Check for blocking factors (day, batch, operator)
7. Plan replication strategy for error estimation
