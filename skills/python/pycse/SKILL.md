---
name: pycse
description: Use when performing regression analysis with confidence intervals, solving ODEs, fitting models to experimental data, or caching expensive scientific computations - provides convenient wrappers around scipy that automatically calculate confidence intervals and prediction bounds for linear, nonlinear, and polynomial regression
allowed-tools: ["*"]
---

# pycse - Python Computations in Science and Engineering

## Overview

**pycse** extends numpy/scipy with convenience functions that automatically return confidence intervals for regression, making statistical analysis faster and less error-prone. Instead of manually extracting covariance matrices and calculating confidence intervals, pycse returns them directly.

**Core value:** Turn 100+ lines of scipy boilerplate into 10 lines of clear, reusable code.

## When to Use

Use pycse when:
- Fitting models to experimental data and need parameter confidence intervals
- Performing regression analysis (linear, nonlinear, polynomial)
- Comparing models with statistical criteria (BIC, R²)
- Generating predictions with error bounds
- Caching expensive computational results
- Reading data from Google Sheets into pandas
- Solving ODEs (wraps scipy with convenient interface)

**Don't use when:**
- scipy alone meets your needs (both are valid)
- You need custom optimization beyond least squares
- Working with models pycse doesn't support

## Quick Reference

| Task | pycse Function | Returns |
|------|---------------|---------|
| Linear regression | `regress(A, y, alpha=0.05)` | `p, pint, se` |
| Nonlinear regression | `nlinfit(model, x, y, p0, alpha=0.05)` | `p, pint, se` |
| Polynomial fit | `polyfit(x, y, deg, alpha=0.05)` | `p, pint, se` |
| Prediction intervals | `predict(X, y, pars, XX, alpha=0.05)` | `prediction, intervals` |
| Nonlinear predict | `nlpredict(X, y, model, loss, popt, xnew)` | `prediction, bounds` |
| Model comparison | `bic(x, y, model, popt)` | `bic_value` |
| Linear BIC | `lbic(X, y, popt)` | `bic_value` |
| R-squared | `Rsquared(y, Y)` | `r2_value` |
| ODE solver | `ivp(f, tspan, y0, **kwargs)` | `solution` |

**All regression functions return:** `(p, pint, se)` where:
- `p` = fitted parameters
- `pint` = confidence intervals for parameters
- `se` = standard errors

## Common Patterns

### Nonlinear Regression with Confidence Intervals

```python
import numpy as np
import pycse

# Data
time = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
concentration = np.array([100, 82, 67, 55, 45, 37, 30, 25, 20, 17, 14])

# Model: C(t) = C0 * exp(-k * t)
def model(t, C0, k):
    return C0 * np.exp(-k * t)

# Fit with 95% confidence intervals
p, pint, se = pycse.nlinfit(model, time, concentration, [100, 0.1])

print(f"C0 = {p[0]:.2f} ± {pint[0,1] - p[0]:.2f}")
print(f"k = {p[1]:.4f} ± {pint[1,1] - p[1]:.4f}")

# That's it! No manual covariance extraction or t-distribution calculations.
```

**Compare to scipy:** Would require extracting covariance, calculating standard errors, looking up t-distribution, computing intervals manually (~50+ lines).

### Linear Regression

```python
import numpy as np
import pycse

# Data matrix A and observations y
A = np.array([[1, 2], [1, 3], [1, 4], [1, 5]])  # [intercept, x]
y = np.array([3, 5, 7, 9])

# Fit: y = p[0] + p[1]*x
p, pint, se = pycse.regress(A, y)

print(f"Intercept: {p[0]:.2f}, 95% CI: [{pint[0,0]:.2f}, {pint[0,1]:.2f}]")
print(f"Slope: {p[1]:.2f}, 95% CI: [{pint[1,0]:.2f}, {pint[1,1]:.2f}]")
```

### Polynomial Fitting

```python
import numpy as np
import pycse

x = np.array([1, 2, 3, 4, 5, 6, 7, 8])
y = np.array([1.5, 3.8, 8.2, 14.9, 23.5, 34.8, 48.2, 64.1])

# Fit quadratic: y = p[0] + p[1]*x + p[2]*x^2
p, pint, se = pycse.polyfit(x, y, deg=2)

print(f"Coefficients: {p}")
print(f"95% CI: {pint}")
```

### Prediction with Error Bounds

```python
import numpy as np
import pycse

# After fitting (see above examples)
x_new = np.array([11, 12, 13])

# Linear prediction
X_new = np.column_stack([np.ones(len(x_new)), x_new])
y_pred, intervals = pycse.predict(A, y, p, X_new)

print(f"Predictions: {y_pred}")
print(f"95% intervals: {intervals}")

# Nonlinear prediction
y_pred_nl, bounds = pycse.nlpredict(time, concentration, model,
                                     lambda p: np.sum((concentration - model(time, *p))**2),
                                     p, x_new)
```

### Model Comparison

```python
import pycse

# Fit two models
p1, _, _ = pycse.polyfit(x, y, deg=1)  # Linear
p2, _, _ = pycse.polyfit(x, y, deg=2)  # Quadratic

# Compare with BIC (lower is better)
bic1 = pycse.lbic(X1, y, p1)
bic2 = pycse.lbic(X2, y, p2)

print(f"Linear BIC: {bic1:.2f}")
print(f"Quadratic BIC: {bic2:.2f}")
print(f"Better model: {'Quadratic' if bic2 < bic1 else 'Linear'}")

# R-squared for goodness of fit
r2 = pycse.Rsquared(y, model(x, *p))
print(f"R² = {r2:.4f}")
```

## Unique Features

### Persistent Hash-based Caching

Cache expensive computations to disk - especially valuable for molecular dynamics, DFT calculations, or long-running simulations.

```python
from pycse.hashcache import HashCache, JsonCache, SqlCache

# Decorator approach
@HashCache()
def expensive_simulation(param1, param2):
    # Long-running computation
    result = complex_calculation(param1, param2)
    return result

# First call: runs computation and caches
result1 = expensive_simulation(1.0, 2.0)

# Second call with same args: retrieves from cache (instant)
result2 = expensive_simulation(1.0, 2.0)

# SqlCache supports searching cached results
@SqlCache(name='my_sim_cache')
def simulation(x, y):
    return complex_calc(x, y)

# Search cache
cache = SqlCache(name='my_sim_cache')
results = cache.search({'x': 1.0})  # Find all cached results where x=1.0
```

**Cache types:**
- `HashCache`: Pickle-based (fastest)
- `JsonCache`: JSON format (human-readable, maggma-compatible)
- `SqlCache`: SQLite with search() capability

### Google Sheets Integration

```python
from pycse.utils import read_gsheet

# Read Google Sheet directly into pandas DataFrame
url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
df = pycse.utils.read_gsheet(url)

# Now use with pycse functions
x = df['time'].values
y = df['concentration'].values
p, pint, se = pycse.nlinfit(model, x, y, p0)
```

### Fuzzy Comparisons

For floating-point comparisons with tolerance:

```python
from pycse.utils import feq, fgt, flt, fge, fle

# Check if value is "close enough" to target
if pycse.utils.feq(calculated_pi, np.pi, epsilon=1e-6):
    print("Converged!")

# Fuzzy comparisons
if pycse.utils.fgt(value, threshold, epsilon=1e-8):
    print("Value exceeds threshold (within tolerance)")
```

## Installation

```bash
pip install pycse
```

**Requirements:** Python 3.6+, numpy, scipy

## Common Mistakes

**❌ Forgetting initial guess for nonlinear fit:**
```python
# Will fail - nlinfit needs initial parameter guess
p, pint, se = pycse.nlinfit(model, x, y)  # Missing p0!
```

**✅ Correct:**
```python
p, pint, se = pycse.nlinfit(model, x, y, p0=[100, 0.1])
```

**❌ Wrong shape for regress():**
```python
# regress expects A to be 2D with shape (n_observations, n_parameters)
A = x  # 1D array - wrong!
p, pint, se = pycse.regress(A, y)
```

**✅ Correct:**
```python
# Add column for intercept
A = np.column_stack([np.ones(len(x)), x])  # Shape: (n, 2)
p, pint, se = pycse.regress(A, y)
```

## When pycse vs scipy

**Use pycse when:**
- You need confidence intervals (pycse returns them automatically)
- Doing many regressions in a workflow (consistent interface)
- Want prediction intervals with error bounds
- Need caching for expensive computations
- Integrating with Google Sheets

**Use scipy when:**
- You need custom optimization methods
- Doing complex constrained optimization
- Need features pycse doesn't expose
- Building low-level computational tools

**Both are valid!** pycse wraps scipy for convenience, not replacement.

## Additional Resources

- GitHub: https://github.com/jkitchin/pycse
- Documentation: https://kitchingroup.cheme.cmu.edu/pycse/
- Examples: 400+ pages in the pycse book covering scientific computing topics
