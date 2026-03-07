# pycse Integration for DOE

## Overview

The [pycse](https://github.com/jkitchin/pycse) library provides integrated response surface methodology (RSM) tools that combine design generation, analysis, and visualization in a streamlined workflow.

## Installation

```bash
pip install pycse
```

## Response Surface Design

```python
from pycse import design_sr, analyze_sr, sr_parity
import numpy as np

# Define factor bounds
bounds = np.array([
    [300, 400],   # Temperature (K)
    [1, 5],       # Pressure (atm)
    [0.1, 1.0],   # Catalyst loading (wt%)
])

# Generate surface response design
design = design_sr(
    bounds,
    inputs=['Temperature', 'Pressure', 'Catalyst'],
    outputs=['Yield', 'Selectivity']
)

print(design)
# Exports as DataFrame ready for experimental execution
design.to_csv('experiment_plan.csv', index=False)
```

## Running and Recording Results

```python
import pandas as pd

# Load plan and add results after experiments
design = pd.read_csv('experiment_plan.csv')

# Add measured responses
design['Yield'] = [78, 82, 75, 88, 91, 85, 79, 83, 87, 84,
                   90, 86, 77, 89, 81, 85, 84, 86]
design['Selectivity'] = [92, 88, 95, 85, 82, 90, 93, 89, 86, 88,
                         83, 87, 94, 84, 91, 88, 87, 88]
```

## Analysis

```python
# Analyze response surface
anova_results = analyze_sr(design)
print(anova_results)
# Shows coefficient estimates, p-values, R-squared
```

## Parity Plot (Model Fit Quality)

```python
# Visual check: predicted vs actual
sr_parity(design, show=True)
# Points near diagonal = good fit
# Systematic deviations = model inadequacy
```

## Combining pycse with Optimization

```python
from scipy.optimize import minimize

# After fitting, optimize using the response surface
def objective(x):
    temp, pres, cat = x
    # Use the fitted model from analyze_sr
    # (extract coefficients from analysis)
    return -predicted_yield(temp, pres, cat)

result = minimize(
    objective,
    x0=[350, 3, 0.5],
    bounds=[(300, 400), (1, 5), (0.1, 1.0)]
)
print(f"Optimal: T={result.x[0]:.0f}, P={result.x[1]:.1f}, C={result.x[2]:.2f}")
```

## pycse Regression Utilities

pycse also provides regression tools useful for DOE analysis.

```python
from pycse import regress
import numpy as np

# Linear regression with confidence intervals
x = np.array([1, 2, 3, 4, 5])
y = np.array([2.1, 3.9, 6.2, 7.8, 10.1])

# regress returns parameters and confidence intervals
p, pint, se = regress(x, y, alpha=0.05)
print(f"Slope: {p[0]:.3f} +/- {pint[0][1] - p[0]:.3f}")
print(f"Intercept: {p[1]:.3f} +/- {pint[1][1] - p[1]:.3f}")
```

## pycse with Nonlinear Models

For model-driven DOE where you fit kinetic models:

```python
from pycse import nlinfit
import numpy as np

def model(x, k1, k2):
    return k1 * (1 - np.exp(-k2 * x))

t = np.array([0, 1, 2, 5, 10, 20])
C = np.array([0, 0.18, 0.33, 0.63, 0.86, 0.98])

p, pint, se = nlinfit(model, t, C, [1.0, 0.1], alpha=0.05)
print(f"k1 = {p[0]:.3f} [{pint[0][0]:.3f}, {pint[0][1]:.3f}]")
print(f"k2 = {p[1]:.3f} [{pint[1][0]:.3f}, {pint[1][1]:.3f}]")
```

## Typical Workflow with pycse

1. **Design**: `design_sr()` generates coded and real-valued experiment matrix
2. **Execute**: Run experiments, record results in the DataFrame
3. **Analyze**: `analyze_sr()` fits quadratic model, reports ANOVA
4. **Validate**: `sr_parity()` checks predicted vs actual
5. **Optimize**: Use fitted model with scipy.optimize
6. **Confirm**: Run confirmation experiments at predicted optimum

## Advantages of pycse for DOE

- Integrated design + analysis in one library
- Automatic ANOVA table generation
- Built-in parity plots for quick validation
- Confidence intervals on regression parameters
- Nonlinear fitting with `nlinfit` for mechanistic models
- Designed for engineering and scientific workflows

## Resources

- Documentation: https://kitchingroup.cheme.cmu.edu/pycse/
- Source: https://github.com/jkitchin/pycse
- Examples: https://kitchingroup.cheme.cmu.edu/pycse/pycse.html
