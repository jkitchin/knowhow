# Active Learning for Experimental Design

## Overview

Active learning selects the most informative experiments to run next, building an accurate surrogate model with fewer data points. Instead of optimizing a response, the goal is to **reduce model uncertainty** across the input space.

## Key Query Strategies

| Strategy              | Selects Point With        | Best For                    |
|-----------------------|---------------------------|-----------------------------|
| Uncertainty sampling  | Highest predicted variance| General model building      |
| Query-by-committee    | Most disagreement among models | Ensemble approaches   |
| Expected model change | Largest expected gradient | Sensitive regions           |
| Information density   | High uncertainty + representative | Clustered data      |

## Basic Active Learning with modAL

```python
import numpy as np
from modAL.models import ActiveLearner
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern

# Define candidate pool (where we could experiment)
X_pool = np.random.uniform(low=[0, 0], high=[10, 10], size=(500, 2))

# Initial random sample
n_initial = 5
idx = np.random.choice(len(X_pool), n_initial, replace=False)
X_init = X_pool[idx]
y_init = np.array([run_experiment(x) for x in X_init])
X_pool = np.delete(X_pool, idx, axis=0)

# Create learner
learner = ActiveLearner(
    estimator=GaussianProcessRegressor(kernel=Matern(nu=2.5)),
    X_training=X_init,
    y_training=y_init,
)

# Active learning loop
for i in range(30):
    query_idx, query_point = learner.query(X_pool)
    y_new = run_experiment(query_point[0])
    learner.teach(query_point, [y_new])
    X_pool = np.delete(X_pool, query_idx, axis=0)

    # Track model quality
    y_pred, y_std = learner.predict(X_pool, return_std=True)
    print(f"Iter {i+1}: max uncertainty = {y_std.max():.4f}")
```

## Custom Query Strategy with scikit-learn GP

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

class ActiveExperimenter:
    def __init__(self, bounds, kernel=None):
        self.bounds = np.array(bounds)
        self.kernel = kernel or RBF() + WhiteKernel()
        self.gp = GaussianProcessRegressor(kernel=self.kernel, n_restarts_optimizer=5)
        self.X_train = []
        self.y_train = []

    def initialize(self, n_points=5):
        """Latin Hypercube initial sampling."""
        from pyDOE3 import lhs
        X = lhs(len(self.bounds), samples=n_points)
        for i, (lo, hi) in enumerate(self.bounds):
            X[:, i] = X[:, i] * (hi - lo) + lo
        return X

    def suggest_next(self, n_candidates=1000):
        """Suggest point with highest predicted uncertainty."""
        self.gp.fit(np.array(self.X_train), np.array(self.y_train))
        candidates = np.random.uniform(
            self.bounds[:, 0], self.bounds[:, 1], size=(n_candidates, len(self.bounds))
        )
        _, std = self.gp.predict(candidates, return_std=True)
        best_idx = np.argmax(std)
        return candidates[best_idx]

    def add_observation(self, x, y):
        self.X_train.append(x)
        self.y_train.append(y)

    def predict(self, X):
        return self.gp.predict(X, return_std=True)

# Usage
exp = ActiveExperimenter(bounds=[(0, 10), (0, 10), (0, 5)])
X_init = exp.initialize(n_points=5)
for x in X_init:
    y = run_experiment(x)
    exp.add_observation(x, y)

for i in range(25):
    x_next = exp.suggest_next()
    y_next = run_experiment(x_next)
    exp.add_observation(x_next, y_next)
```

## Batch Active Learning

When you can run multiple experiments in parallel per round:

```python
def batch_query(gp, candidates, batch_size=5):
    """Select a batch using greedy diversity + uncertainty."""
    selected = []
    remaining = list(range(len(candidates)))

    for _ in range(batch_size):
        _, std = gp.predict(candidates[remaining], return_std=True)
        best_local = np.argmax(std)
        best_idx = remaining[best_local]
        selected.append(best_idx)
        remaining.remove(best_idx)

    return candidates[selected]
```

## Stopping Criteria

Deciding when to stop collecting data:

```python
def should_stop(gp, X_test, threshold=0.05, coverage=0.95):
    """Stop when uncertainty is low across most of the space."""
    _, std = gp.predict(X_test, return_std=True)
    fraction_below = np.mean(std < threshold)
    return fraction_below >= coverage
```

Common stopping rules:
1. **Max uncertainty below threshold** across a test grid
2. **Diminishing returns**: improvement per iteration drops below threshold
3. **Cross-validation error** stabilizes
4. **Budget exhausted**: fixed number of experiments

## Comparison: Active Learning vs Bayesian Optimization

| Aspect           | Active Learning           | Bayesian Optimization    |
|------------------|---------------------------|--------------------------|
| Goal             | Accurate model everywhere | Find optimum             |
| Sampling bias    | Uniform coverage          | Concentrated near optimum|
| Query strategy   | Uncertainty-based         | Acquisition function     |
| Output           | Surrogate model           | Best point found         |
| When to use      | Need predictions anywhere | Only need the best       |

## Tips

- Start with Latin Hypercube (space-filling) for initial points
- Use Matern 5/2 kernel as default -- less smooth than RBF, more realistic
- Monitor GP hyperparameters; re-optimize periodically
- Validate with leave-one-out cross-validation
- Consider input-dependent noise if measurement precision varies
