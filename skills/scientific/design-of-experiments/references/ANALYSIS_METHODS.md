# Analysis Methods for DOE

## ANOVA (Analysis of Variance)

Determine which factors have statistically significant effects.

```python
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import pandas as pd

# Example: 2-factor experiment
df = pd.DataFrame({
    'Temperature': [300, 400, 300, 400, 300, 400, 300, 400],
    'Pressure': [1, 1, 5, 5, 1, 1, 5, 5],
    'Yield': [72, 85, 78, 91, 74, 83, 80, 93]
})

model = ols('Yield ~ C(Temperature) * C(Pressure)', data=df).fit()
table = anova_lm(model, typ=2)
print(table)
# Look for p-values < 0.05 to identify significant factors
```

## Regression for Response Surface

```python
import numpy as np
import statsmodels.formula.api as smf

# Fit full quadratic model (CCD or Box-Behnken data)
model = smf.ols(
    'Yield ~ Temperature + Pressure + Catalyst + '
    'Temperature:Pressure + Temperature:Catalyst + Pressure:Catalyst + '
    'I(Temperature**2) + I(Pressure**2) + I(Catalyst**2)',
    data=df
).fit()

print(model.summary())
print(f"\nR-squared: {model.rsquared:.4f}")
print(f"Adj R-squared: {model.rsquared_adj:.4f}")
```

## Effect Significance (Pareto of Effects)

```python
import matplotlib.pyplot as plt

effects = model.params.drop('Intercept')
t_values = model.tvalues.drop('Intercept')

# Sort by absolute t-value
sorted_effects = t_values.abs().sort_values(ascending=True)

plt.figure(figsize=(8, 5))
colors = ['red' if model.pvalues[name] < 0.05 else 'gray'
          for name in sorted_effects.index]
plt.barh(range(len(sorted_effects)), sorted_effects.values, color=colors)
plt.yticks(range(len(sorted_effects)), sorted_effects.index)
plt.axvline(x=2.0, color='blue', linestyle='--', label='t-critical (approx)')
plt.xlabel('|t-value|')
plt.title('Pareto of Standardized Effects')
plt.legend()
plt.tight_layout()
plt.show()
```

## Residual Diagnostics

Always check model assumptions after fitting.

```python
import scipy.stats as stats

residuals = model.resid
fitted = model.fittedvalues

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# 1. Residuals vs Fitted (constant variance)
axes[0, 0].scatter(fitted, residuals)
axes[0, 0].axhline(0, color='r', linestyle='--')
axes[0, 0].set_xlabel('Fitted'); axes[0, 0].set_ylabel('Residuals')
axes[0, 0].set_title('Residuals vs Fitted')

# 2. Normal Q-Q (normality)
stats.probplot(residuals, plot=axes[0, 1])
axes[0, 1].set_title('Normal Q-Q')

# 3. Histogram of residuals
axes[1, 0].hist(residuals, bins='auto', edgecolor='black')
axes[1, 0].set_title('Residual Distribution')

# 4. Residuals vs order (independence)
axes[1, 1].plot(residuals, 'o-')
axes[1, 1].axhline(0, color='r', linestyle='--')
axes[1, 1].set_xlabel('Run Order'); axes[1, 1].set_ylabel('Residuals')
axes[1, 1].set_title('Residuals vs Run Order')

plt.tight_layout()
plt.show()

# Shapiro-Wilk normality test
stat, p = stats.shapiro(residuals)
print(f"Shapiro-Wilk: W={stat:.4f}, p={p:.4f}")
```

## Response Optimization

Find optimal factor settings from a fitted model.

```python
from scipy.optimize import minimize

def predict_response(x):
    """Predict from fitted model (negate for maximization)."""
    temp, pres, cat = x
    df_pred = pd.DataFrame({'Temperature': [temp], 'Pressure': [pres], 'Catalyst': [cat]})
    return -model.predict(df_pred).values[0]

result = minimize(
    predict_response,
    x0=[350, 3, 0.5],
    bounds=[(300, 400), (1, 5), (0.1, 1.0)],
    method='L-BFGS-B'
)
print(f"Optimal: Temp={result.x[0]:.1f}, Pres={result.x[1]:.2f}, Cat={result.x[2]:.3f}")
print(f"Predicted yield: {-result.fun:.2f}")
```

## Contour and Surface Plots

```python
from mpl_toolkits.mplot3d import Axes3D

temp_range = np.linspace(300, 400, 50)
pres_range = np.linspace(1, 5, 50)
T, P = np.meshgrid(temp_range, pres_range)

# Predict at fixed catalyst = 0.5
grid = pd.DataFrame({
    'Temperature': T.ravel(), 'Pressure': P.ravel(), 'Catalyst': 0.5
})
Z = model.predict(grid).values.reshape(T.shape)

# Contour plot
plt.figure(figsize=(8, 6))
cs = plt.contourf(T, P, Z, levels=20, cmap='viridis')
plt.colorbar(cs, label='Yield')
plt.xlabel('Temperature'); plt.ylabel('Pressure')
plt.title('Response Surface (Catalyst = 0.5)')
plt.show()
```

## Lack-of-Fit Test

Tests whether the model form is adequate using replicated points.

```python
# Requires replicate experiments (e.g., center points in CCD)
from statsmodels.stats.anova import anova_lm

# Fit reduced and full models
reduced = ols('Yield ~ Temperature + Pressure', data=df).fit()
full = ols('Yield ~ C(group)', data=df).fit()  # group = unique conditions

lof_table = anova_lm(reduced, full)
print(lof_table)
# If p-value < 0.05, model form is inadequate
```

## Confidence and Prediction Intervals

```python
from statsmodels.sandbox.regression.predstd import wls_prediction_std

# Prediction with intervals
predictions = model.get_prediction(df_new)
summary = predictions.summary_frame(alpha=0.05)
print(summary[['mean', 'mean_ci_lower', 'mean_ci_upper',
               'obs_ci_lower', 'obs_ci_upper']])
```

## Checklist After Analysis

1. Are residuals approximately normal? (Q-Q plot, Shapiro-Wilk)
2. Is variance constant across fitted values? (residuals vs fitted)
3. Are residuals independent? (no patterns vs run order)
4. Is R-squared adequate? (>0.8 for RSM, context-dependent)
5. Are key effects statistically significant? (p < 0.05)
6. Does the model pass lack-of-fit test? (p > 0.05)
7. Do confirmation runs match predictions?
