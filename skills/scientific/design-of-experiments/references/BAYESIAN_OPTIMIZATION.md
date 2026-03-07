# Bayesian Optimization

## Overview

Bayesian optimization (BO) uses a probabilistic surrogate model (typically a Gaussian Process) to guide sequential experimentation. It balances exploration (sampling uncertain regions) with exploitation (sampling near current best).

**Note:** GPyOpt is deprecated and no longer maintained. Use **BoTorch** (with Ax) or **scikit-optimize** instead.

## Recommended Libraries

| Library          | Best For                          | Complexity |
|------------------|-----------------------------------|------------|
| scikit-optimize  | Simple BO, quick prototyping      | Low        |
| Ax (ax-platform) | Production use, multi-objective   | Medium     |
| BoTorch          | Custom acquisition, research      | High       |

## scikit-optimize (Simplest)

```python
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.plots import plot_convergence, plot_objective

space = [
    Real(300, 400, name='temperature'),
    Real(1, 5, name='pressure'),
    Integer(1, 10, name='catalyst_amount'),
]

def objective(params):
    temp, pressure, cat = params
    result = run_experiment(temp, pressure, cat)
    return -result  # minimize negative = maximize

result = gp_minimize(
    objective, space,
    n_calls=30, n_random_starts=5,
    acq_func='EI',  # Expected Improvement
    random_state=42
)

print(f"Best: {result.fun:.4f} at {result.x}")
plot_convergence(result)
```

## Ax Platform (Meta's Adaptive Experimentation)

```python
from ax.service.ax_client import AxClient

ax_client = AxClient()
ax_client.create_experiment(
    name="process_optimization",
    parameters=[
        {"name": "temperature", "type": "range", "bounds": [300.0, 400.0]},
        {"name": "pressure", "type": "range", "bounds": [1.0, 5.0]},
        {"name": "catalyst", "type": "range", "bounds": [0.1, 1.0]},
    ],
    objective_name="yield",
    minimize=False,
)

for i in range(25):
    parameters, trial_index = ax_client.get_next_trial()
    result = run_experiment(**parameters)
    ax_client.complete_trial(trial_index=trial_index, raw_data={"yield": result})

best_parameters, values = ax_client.get_best_parameters()
print(f"Best parameters: {best_parameters}")
```

## BoTorch (Advanced / Custom)

```python
import torch
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition import ExpectedImprovement
from botorch.optim import optimize_acq_function
from gpytorch.mlls import ExactMarginalLogLikelihood

# Initial data (5 random points in [0,1]^2)
train_X = torch.rand(5, 2)
train_Y = torch.tensor([[objective(x)] for x in train_X])

for i in range(20):
    # Fit GP model
    gp = SingleTaskGP(train_X, train_Y)
    mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
    fit_gpytorch_mll(mll)

    # Acquisition function
    EI = ExpectedImprovement(model=gp, best_f=train_Y.max())
    candidate, acq_value = optimize_acq_function(
        EI, bounds=torch.tensor([[0.0, 0.0], [1.0, 1.0]]),
        q=1, num_restarts=5, raw_samples=20,
    )

    # Evaluate and update
    new_Y = torch.tensor([[objective(candidate[0])]])
    train_X = torch.cat([train_X, candidate])
    train_Y = torch.cat([train_Y, new_Y])
```

## Acquisition Functions

| Function                  | Behavior                           | Use When              |
|---------------------------|------------------------------------|-----------------------|
| Expected Improvement (EI) | Balance explore/exploit            | Default choice        |
| Upper Confidence Bound    | Tunable exploration (beta param)   | Want more exploration |
| Probability of Improvement| Conservative, exploit-heavy        | Near convergence      |
| Knowledge Gradient        | Value of information               | Very expensive expts  |

## Multi-Objective BO (BoTorch)

```python
from botorch.acquisition.multi_objective import ExpectedHypervolumeImprovement
from botorch.models import SingleTaskGP
from botorch.utils.multi_objective.pareto import is_non_dominated

# Fit model for each objective
model = SingleTaskGP(train_X, train_Y)  # train_Y has 2+ columns

# Get Pareto front
pareto_mask = is_non_dominated(train_Y)
pareto_points = train_Y[pareto_mask]
```

## Practical Tips

1. **Initial points:** Use 5-10 Latin Hypercube samples, not pure random
2. **Normalization:** Standardize inputs to [0,1] and outputs to zero mean
3. **Kernel choice:** Matern 5/2 is a robust default; RBF assumes very smooth functions
4. **Stopping criteria:** Stop when EI < threshold or improvement plateaus for 5+ iterations
5. **Batch BO:** Use q-EI in BoTorch to suggest multiple points simultaneously
6. **Constraints:** Ax supports outcome constraints natively
7. **Categorical variables:** Ax handles mixed parameter types well

## Installation

```bash
# Simple option
pip install scikit-optimize

# Full-featured option
pip install ax-platform

# Advanced/research option
pip install botorch torch gpytorch
```
