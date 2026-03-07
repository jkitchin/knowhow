# Model-Driven Design of Experiments

## Overview

When you have a mechanistic or parametric model, you can design experiments that are statistically optimal for parameter estimation, model discrimination, or prediction accuracy. The key tool is the **Fisher Information Matrix (FIM)**.

## Fisher Information Matrix

The FIM quantifies how much information an experiment provides about model parameters.

```python
import numpy as np
from scipy.linalg import det, inv

def compute_fim(design_points, model_jacobian, params, sigma=1.0):
    """
    Compute Fisher Information Matrix.

    Parameters
    ----------
    design_points : array, shape (n, d)
        Experimental conditions
    model_jacobian : callable
        Returns Jacobian (sensitivity) matrix at given conditions
    params : array
        Current parameter estimates
    sigma : float
        Measurement noise std

    Returns
    -------
    FIM : array, shape (p, p)
    """
    J = model_jacobian(design_points, params)  # (n, p)
    FIM = J.T @ J / sigma**2
    return FIM
```

## Optimality Criteria

| Criterion | Objective               | Minimizes             | Best For                |
|-----------|-------------------------|-----------------------|-------------------------|
| D-optimal | max det(FIM)            | Volume of CI ellipsoid| General parameter est.  |
| A-optimal | min trace(FIM^-1)       | Average variance      | When all params matter  |
| E-optimal | max min eigenvalue(FIM) | Worst-case variance   | Balanced precision      |
| T-optimal | max discrimination      | Model confusion       | Model selection         |

## D-Optimal Design Example

```python
from scipy.optimize import minimize
from scipy.linalg import det

def kinetic_model(t, k):
    """First-order: C = C0 * exp(-k1*t) + k2*(1 - exp(-k3*t))"""
    return k[0] * np.exp(-k[1] * t) + k[2] * (1 - np.exp(-k[3] * t))

def jacobian(t_points, k):
    """Sensitivity of model to each parameter."""
    n = len(t_points)
    J = np.zeros((n, 4))
    for i, t in enumerate(t_points):
        J[i, 0] = np.exp(-k[1] * t)
        J[i, 1] = -k[0] * t * np.exp(-k[1] * t)
        J[i, 2] = 1 - np.exp(-k[3] * t)
        J[i, 3] = k[2] * t * np.exp(-k[3] * t)
    return J

def neg_log_det_fim(t_flat, k_guess):
    J = jacobian(t_flat, k_guess)
    FIM = J.T @ J
    d = det(FIM)
    if d <= 0:
        return 1e10
    return -np.log(d)

# Find 6 optimal time points in [0, 100]
k_guess = [1.0, 0.05, 0.5, 0.1]
n_points = 6
t0 = np.linspace(5, 95, n_points)

result = minimize(neg_log_det_fim, t0, args=(k_guess,),
                  bounds=[(0.1, 100)] * n_points, method='L-BFGS-B')

optimal_times = np.sort(result.x)
print(f"Optimal measurement times: {optimal_times}")
```

## Sequential Model-Driven Design

Update the design as you learn more about parameters.

```python
from scipy.optimize import curve_fit

def sequential_d_optimal(model_func, jacobian_func, bounds, k_init,
                         n_initial=3, n_sequential=10):
    """Sequential D-optimal design with parameter updating."""
    # Phase 1: initial space-filling
    t_data = np.linspace(bounds[0], bounds[1], n_initial)
    y_data = np.array([run_experiment(t) for t in t_data])
    k_est = k_init.copy()

    for step in range(n_sequential):
        # Fit model to current data
        try:
            k_est, _ = curve_fit(model_func, t_data, y_data, p0=k_est)
        except RuntimeError:
            pass  # keep previous estimate

        # Find next optimal point given current estimates
        candidates = np.linspace(bounds[0], bounds[1], 200)
        best_val, best_t = -np.inf, None
        for t_new in candidates:
            t_trial = np.append(t_data, t_new)
            J = jacobian_func(t_trial, k_est)
            d = det(J.T @ J)
            if d > best_val:
                best_val, best_t = d, t_new

        # Run experiment and update
        y_new = run_experiment(best_t)
        t_data = np.append(t_data, best_t)
        y_data = np.append(y_data, y_new)
        print(f"Step {step+1}: t={best_t:.2f}, params={k_est}")

    return t_data, y_data, k_est
```

## Model Discrimination (T-Optimal)

Choose experiments that best distinguish between competing models.

```python
def discrimination_criterion(t_point, model1, model2, params1, params2):
    """Maximize squared difference between model predictions."""
    y1 = model1(t_point, *params1)
    y2 = model2(t_point, *params2)
    return (y1 - y2)**2

# Find the measurement time that most distinguishes two models
from scipy.optimize import minimize_scalar
result = minimize_scalar(
    lambda t: -discrimination_criterion(t, model_A, model_B, pA, pB),
    bounds=(0, 100), method='bounded'
)
print(f"Best discriminating time: {result.x:.2f}")
```

## Confidence Intervals from FIM

```python
def parameter_confidence(FIM, alpha=0.05):
    """Approximate confidence intervals from FIM."""
    from scipy.stats import norm
    cov = inv(FIM)
    z = norm.ppf(1 - alpha/2)
    std_errors = np.sqrt(np.diag(cov))
    return std_errors * z

# Usage
FIM = compute_fim(optimal_times, jacobian, k_est)
ci = parameter_confidence(FIM)
for i, (k, c) in enumerate(zip(k_est, ci)):
    print(f"k{i}: {k:.4f} +/- {c:.4f}")
```

## When to Use Model-Driven DOE

- You have a differential equation or algebraic model for the system
- Goal is precise parameter estimation
- Can iterate: estimate parameters, redesign, re-estimate
- Need to choose between competing mechanistic models
