# Classical Design of Experiments

## Full Factorial Designs (2^k)

Test all combinations of k factors at 2 levels. Estimates all main effects and interactions.

```python
import pyDOE3 as pyd
import numpy as np
import pandas as pd

# 2^3 full factorial
design = pyd.ff2n(3)
factors = ['Temperature', 'Pressure', 'Catalyst']
df = pd.DataFrame(design, columns=factors)

# Scale from coded (-1, +1) to real units
ranges = {'Temperature': (300, 400), 'Pressure': (1, 5), 'Catalyst': (0.1, 1.0)}
for col, (lo, hi) in ranges.items():
    df[col] = (df[col] + 1) / 2 * (hi - lo) + lo
```

**Runs required:** 2^k (grows fast -- use fractional designs for k > 5)

## Fractional Factorial Designs (2^(k-p))

Sacrifice higher-order interaction info to reduce runs.

```python
# 2^(5-2) = 8 runs for 5 factors (Resolution III)
design = pyd.fracfact('a b c ab ac')

# Resolution guide:
#   III  - main effects confounded with 2-factor interactions
#   IV   - main effects clear, 2FI confounded with each other
#   V    - main effects and 2FI all estimable
```

## Central Composite Design (CCD)

Fits full quadratic model. Three components: factorial points, axial (star) points, center points.

```python
# CCD for 3 factors
ccd = pyd.ccdesign(3, center=(4, 4), face='ccf')
# face options: 'ccf' (face-centered), 'cci' (inscribed), 'ccc' (circumscribed)

# Typical run count: 2^k + 2k + center = 8 + 6 + 4 = 18 for k=3
```

## Box-Behnken Design

Alternative to CCD that avoids extreme corners. Good when corner conditions are infeasible.

```python
# Box-Behnken for 4 factors
bbd = pyd.bbdesign(4, center=3)
print(f"Runs: {len(bbd)}")  # 27 runs for 4 factors
```

## Plackett-Burman (Screening)

Screen many factors efficiently. Only estimates main effects (Resolution III).

```python
# Screen up to 11 factors in 12 runs
pb = pyd.pbdesign(12)  # 12-run PB design
print(f"Can screen {pb.shape[1]} factors in {pb.shape[0]} runs")
```

## Analysis with statsmodels

```python
import statsmodels.formula.api as smf

# Fit response surface model
df['Y'] = results  # your experimental results
model = smf.ols('Y ~ Temperature * Pressure * Catalyst + '
                'I(Temperature**2) + I(Pressure**2) + I(Catalyst**2)', data=df)
fit = model.fit()
print(fit.summary())

# ANOVA table
from statsmodels.stats.anova import anova_lm
anova = anova_lm(fit)
print(anova)
```

## Diagnostic Checks

```python
import matplotlib.pyplot as plt

residuals = fit.resid
fitted = fit.fittedvalues

# Residuals vs fitted (check constant variance)
plt.scatter(fitted, residuals)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Fitted'); plt.ylabel('Residuals')
plt.title('Residuals vs Fitted')
plt.show()

# Normal Q-Q plot (check normality)
from scipy import stats
stats.probplot(residuals, plot=plt)
plt.show()
```

## Key Assumptions

1. **Normality** of residuals (Q-Q plot, Shapiro-Wilk test)
2. **Constant variance** (residuals vs fitted plot)
3. **Independence** (randomize run order)
4. **Model adequacy** (lack-of-fit test using replicated center points)

## Design Comparison

| Design          | Factors | Runs (k=4) | Model Order | Best For           |
|-----------------|---------|-------------|-------------|--------------------|
| Full factorial  | 2-5     | 16          | All         | Complete picture   |
| Fractional      | 4-8     | 8           | Main + some | Screening          |
| CCD             | 2-5     | 25          | Quadratic   | Optimization       |
| Box-Behnken     | 3-5     | 27          | Quadratic   | No extreme corners |
| Plackett-Burman | 6-15    | 12          | Main only   | Fast screening     |
