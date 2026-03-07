---
name: python-multiobjective-optimization
description: Expert guidance for multiobjective optimization in Python - Pareto optimality, evolutionary algorithms (NSGA-II, NSGA-III, MOEA/D), scalarization methods, Pareto front analysis, and implementation with pymoo, platypus, and DEAP
allowed-tools: ["*"]
---

# Python Multiobjective Optimization

## Overview

Master multiobjective optimization where you must simultaneously optimize multiple conflicting objectives. Unlike single-objective optimization that finds one optimal solution, multiobjective optimization discovers a **Pareto front** - a set of trade-off solutions where improving one objective worsens another.

**Core value:** Find optimal trade-offs between competing objectives (cost vs. performance, risk vs. return, speed vs. accuracy) and enable informed decision-making across the Pareto frontier.

## When to Use

Use multiobjective optimization when:
- Optimizing multiple conflicting objectives simultaneously
- Need trade-off analysis between competing goals
- Decision-makers must choose from Pareto-optimal alternatives
- No single "best" solution exists without preference information

**Examples:**
- Portfolio optimization: maximize return, minimize risk
- Engineering design: minimize cost, maximize performance, minimize weight
- Manufacturing: maximize throughput, minimize defects, minimize energy
- Drug design: maximize efficacy, minimize toxicity, maximize bioavailability
- Vehicle routing: minimize distance, minimize time, minimize vehicles

**Don't use when:**
- Only one objective exists (use single-objective optimization)
- Objectives can be combined into single metric with known weights
- One objective is vastly more important than others

## Key Concepts

### Pareto Dominance

Solution **x** dominates solution **y** if:
1. **x** is no worse than **y** in all objectives
2. **x** is strictly better than **y** in at least one objective

```python
def dominates(obj_x, obj_y, minimize=True):
    """
    Check if obj_x dominates obj_y (for minimization).

    Returns True if obj_x dominates obj_y.
    """
    if minimize:
        # For minimization: x dominates y if all x_i <= y_i and at least one x_i < y_i
        better_or_equal = all(x <= y for x, y in zip(obj_x, obj_y))
        strictly_better = any(x < y for x, y in zip(obj_x, obj_y))
    else:
        # For maximization: x dominates y if all x_i >= y_i and at least one x_i > y_i
        better_or_equal = all(x >= y for x, y in zip(obj_x, obj_y))
        strictly_better = any(x > y for x, y in zip(obj_x, obj_y))

    return better_or_equal and strictly_better
```

### Pareto Front (Pareto Frontier)

The **Pareto front** is the set of all non-dominated solutions - solutions where you cannot improve one objective without worsening another.

**Properties:**
- All points on the Pareto front are equally "optimal" from mathematical perspective
- Choosing among Pareto solutions requires preference information
- Moving along the front trades one objective for another

### Utopia and Nadir Points

- **Utopia point**: Best possible value for each objective (usually infeasible)
- **Nadir point**: Worst value among Pareto-optimal solutions for each objective

## Methods Overview

### Scalarization Approaches

Convert multiobjective problem to series of single-objective problems.

**1. Weighted Sum**
- Combine objectives with weights: minimize w₁f₁(x) + w₂f₂(x)
- Pros: Simple, uses any single-objective solver
- Cons: Cannot find non-convex Pareto fronts, sensitive to scaling

**2. Weighted Metrics (Lp-norm)**
- Minimize ||f(x) - ideal||ₚ with weights
- Pros: Can find non-convex fronts (p=∞)
- Cons: Requires ideal point estimation

**3. ε-Constraint Method**
- Minimize one objective, constrain others: min f₁(x) s.t. f₂(x) ≤ ε
- Pros: Finds entire Pareto front including non-convex regions
- Cons: Many single-objective solves, requires constraint bounds

**4. Goal Programming**
- Minimize deviation from target goals
- Pros: Intuitive when targets known
- Cons: Requires setting goals

### Evolutionary Algorithms

Population-based metaheuristics that evolve Pareto front approximations.

**1. NSGA-II (Non-dominated Sorting Genetic Algorithm II)**
- Most popular multiobjective evolutionary algorithm
- Fast non-dominated sorting + crowding distance
- Pros: Robust, well-tested, handles 2-3 objectives well
- Cons: Degrades with many objectives (>3)

**2. NSGA-III**
- Extension of NSGA-II for many objectives (4+)
- Reference point-based selection
- Pros: Scales to many objectives
- Cons: More complex parameter tuning

**3. MOEA/D (Multiobjective Evolutionary Algorithm based on Decomposition)**
- Decomposes problem into scalar subproblems
- Pros: Efficient, good for many objectives
- Cons: Requires careful decomposition setup

**4. Other Algorithms**
- SPEA2, PAES, GDE3, SMS-EMOA, etc.

### Comparison

| Method | Objectives | Pareto Front Type | Pros | Cons |
|--------|-----------|-------------------|------|------|
| Weighted Sum | 2-3 | Convex only | Simple, fast | Misses non-convex regions |
| ε-Constraint | 2-3 | Any | Complete coverage | Many solves needed |
| NSGA-II | 2-3 | Any | Robust, popular | Poor for many objectives |
| NSGA-III | 4+ | Any | Handles many objectives | Complex tuning |
| MOEA/D | 4+ | Any | Efficient | Decomposition setup |

## Library Selection

### pymoo - Recommended

**Use when:**
- Need modern, comprehensive multiobjective optimization
- Want evolutionary algorithms (NSGA-II, NSGA-III, MOEA/D)
- Need built-in performance indicators
- Want clean, object-oriented API

**Strengths:**
- Actively maintained
- Extensive algorithm library
- Built-in test problems
- Performance indicators (hypervolume, etc.)
- Good documentation

**Installation:**
```bash
pip install pymoo
```

### platypus

**Use when:**
- Need pure Python implementation
- Want simple API
- Lightweight dependency footprint

**Strengths:**
- Pure Python (no compilation)
- Simple interface
- Multiple algorithms

**Installation:**
```bash
pip install platypus-opt
```

### DEAP

**Use when:**
- Need general evolutionary computation framework
- Want customization flexibility
- Already using DEAP for other tasks

**Strengths:**
- Highly flexible
- Large community
- General-purpose evolutionary algorithms

**Cons:**
- More complex API
- Less specialized for multiobjective

**Installation:**
```bash
pip install deap
```

### scipy.optimize

**Use when:**
- Only need scalarization approaches
- Want minimal dependencies
- Already using scipy

**Limitations:**
- No built-in evolutionary algorithms
- Manual Pareto front construction
- Limited multiobjective-specific tools

## Implementation Patterns

### Pattern 1: NSGA-II with pymoo

```python
import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter

# Define problem
class MyProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=2,           # Number of decision variables
            n_obj=2,           # Number of objectives
            n_ieq_constr=0,    # Number of inequality constraints
            xl=np.array([0, 0]),    # Lower bounds
            xu=np.array([1, 1])     # Upper bounds
        )

    def _evaluate(self, x, out, *args, **kwargs):
        """
        Evaluate objectives for population x.

        x: array of shape (pop_size, n_var)
        out["F"]: objectives of shape (pop_size, n_obj)
        out["G"]: constraints of shape (pop_size, n_constr) [optional]
        """
        # Objective 1: minimize (x1 - 0.5)^2 + (x2 - 0.5)^2
        f1 = (x[:, 0] - 0.5)**2 + (x[:, 1] - 0.5)**2

        # Objective 2: minimize (x1 - 0.2)^2 + (x2 - 0.8)^2
        f2 = (x[:, 0] - 0.2)**2 + (x[:, 1] - 0.8)**2

        out["F"] = np.column_stack([f1, f2])

# Create problem instance
problem = MyProblem()

# Configure algorithm
algorithm = NSGA2(
    pop_size=100,           # Population size
    eliminate_duplicates=True
)

# Solve
res = minimize(
    problem,
    algorithm,
    ('n_gen', 200),         # Termination: 200 generations
    seed=1,
    verbose=True
)

# Results
print(f"Number of Pareto solutions: {len(res.F)}")
print(f"Objective values (first 5):\n{res.F[:5]}")
print(f"Decision variables (first 5):\n{res.X[:5]}")

# Visualize Pareto front
plot = Scatter()
plot.add(res.F, label="Pareto Front")
plot.show()
```

### Pattern 2: NSGA-III for Many Objectives

```python
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions

# Problem with many objectives (e.g., 4)
class ManyObjectiveProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=10,
            n_obj=4,           # 4 objectives
            xl=-5,
            xu=5
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # Define 4 conflicting objectives
        f1 = np.sum(x[:, :5]**2, axis=1)
        f2 = np.sum((x[:, :5] - 1)**2, axis=1)
        f3 = np.sum(x[:, 5:]**2, axis=1)
        f4 = np.sum((x[:, 5:] - 2)**2, axis=1)

        out["F"] = np.column_stack([f1, f2, f3, f4])

# Create reference directions for 4 objectives
ref_dirs = get_reference_directions("das-dennis", 4, n_partitions=12)

# NSGA-III algorithm
algorithm = NSGA3(
    ref_dirs=ref_dirs,
    pop_size=92  # Must match reference directions
)

# Solve
problem = ManyObjectiveProblem()
res = minimize(
    problem,
    algorithm,
    ('n_gen', 300),
    seed=1,
    verbose=True
)

print(f"Number of Pareto solutions: {len(res.F)}")
```

### Pattern 3: With Constraints

```python
class ConstrainedProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,    # 2 inequality constraints
            xl=np.array([0, 0]),
            xu=np.array([5, 5])
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # Objectives
        f1 = x[:, 0]**2 + x[:, 1]**2
        f2 = (x[:, 0] - 3)**2 + (x[:, 1] - 3)**2

        # Inequality constraints: g(x) <= 0
        g1 = x[:, 0] + x[:, 1] - 5      # x1 + x2 <= 5
        g2 = -(x[:, 0] + 2*x[:, 1] - 6)  # x1 + 2*x2 >= 6

        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2])

# Solve with NSGA-II (handles constraints automatically)
problem = ConstrainedProblem()
algorithm = NSGA2(pop_size=100)
res = minimize(problem, algorithm, ('n_gen', 200), seed=1)

# Check constraint violations
print(f"Max constraint violation: {np.max(res.CV)}")  # Should be ~0
```

### Pattern 4: Weighted Sum (Scalarization)

```python
from scipy.optimize import minimize as scipy_minimize

def objectives(x):
    """Return tuple of objectives"""
    f1 = x[0]**2 + x[1]**2
    f2 = (x[0] - 1)**2 + (x[1] - 1)**2
    return f1, f2

def scalarized_objective(x, weights):
    """Weighted sum of objectives"""
    f1, f2 = objectives(x)
    return weights[0] * f1 + weights[1] * f2

# Generate Pareto front by varying weights
weights_list = np.linspace(0, 1, 11)
pareto_front = []

for w in weights_list:
    weights = [w, 1 - w]

    result = scipy_minimize(
        scalarized_objective,
        x0=[0.5, 0.5],
        args=(weights,),
        method='SLSQP',
        bounds=[(0, 2), (0, 2)]
    )

    if result.success:
        f1, f2 = objectives(result.x)
        pareto_front.append({
            'x': result.x,
            'f1': f1,
            'f2': f2,
            'weights': weights
        })

# Convert to arrays
F = np.array([[p['f1'], p['f2']] for p in pareto_front])
X = np.array([p['x'] for p in pareto_front])

print(f"Found {len(pareto_front)} Pareto solutions")
```

### Pattern 5: ε-Constraint Method

```python
from scipy.optimize import minimize as scipy_minimize

def objective1(x):
    return x[0]**2 + x[1]**2

def objective2(x):
    return (x[0] - 1)**2 + (x[1] - 1)**2

# ε-constraint: minimize f1, subject to f2 <= epsilon
def solve_epsilon_constraint(epsilon):
    """Solve for given epsilon constraint on f2"""

    constraint = {
        'type': 'ineq',
        'fun': lambda x: epsilon - objective2(x)  # f2(x) <= epsilon
    }

    result = scipy_minimize(
        objective1,
        x0=[0.5, 0.5],
        method='SLSQP',
        constraints=[constraint],
        bounds=[(0, 2), (0, 2)]
    )

    return result

# Vary epsilon to trace Pareto front
epsilon_values = np.linspace(0.01, 2.0, 20)
pareto_front = []

for eps in epsilon_values:
    result = solve_epsilon_constraint(eps)

    if result.success:
        pareto_front.append({
            'x': result.x,
            'f1': objective1(result.x),
            'f2': objective2(result.x),
            'epsilon': eps
        })

print(f"Found {len(pareto_front)} Pareto solutions")
```

### Pattern 6: Using platypus

```python
from platypus import NSGAII, Problem, Real

def evaluate(x):
    """
    Evaluation function returning list of objectives.

    Note: platypus expects function that returns list.
    """
    f1 = x[0]**2 + x[1]**2
    f2 = (x[0] - 1)**2 + (x[1] - 1)**2
    return [f1, f2]

# Define problem
problem = Problem(2, 2)  # 2 variables, 2 objectives
problem.types[:] = [Real(0, 1), Real(0, 1)]  # Variable bounds
problem.function = evaluate

# Solve with NSGA-II
algorithm = NSGAII(problem, population_size=100)
algorithm.run(10000)  # 10000 function evaluations

# Extract results
F = np.array([[s.objectives[0], s.objectives[1]] for s in algorithm.result])
X = np.array([[s.variables[0], s.variables[1]] for s in algorithm.result])

print(f"Number of Pareto solutions: {len(F)}")
```

### Pattern 7: Using DEAP

```python
import random
from deap import base, creator, tools, algorithms
import numpy as np

# Setup DEAP
creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  # Minimize both
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_float, n=2)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    """Evaluation function returning tuple of objectives"""
    x = individual
    f1 = x[0]**2 + x[1]**2
    f2 = (x[0] - 1)**2 + (x[1] - 1)**2
    return f1, f2

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
toolbox.register("select", tools.selNSGA2)

# Initialize population
pop = toolbox.population(n=100)

# Run NSGA-II
algorithms.eaMuPlusLambda(
    pop, toolbox,
    mu=100,
    lambda_=100,
    cxpb=0.9,
    mutpb=0.1,
    ngen=100,
    verbose=False
)

# Extract Pareto front
pareto_front = tools.sortNondominated(pop, len(pop), first_front_only=True)[0]
F = np.array([ind.fitness.values for ind in pareto_front])
X = np.array([list(ind) for ind in pareto_front])

print(f"Number of Pareto solutions: {len(F)}")
```

## Pareto Analysis

### Non-dominated Sorting

```python
def is_dominated(obj_a, obj_b, minimize=True):
    """Check if obj_a is dominated by obj_b"""
    if minimize:
        better = all(b <= a for a, b in zip(obj_a, obj_b))
        strictly_better = any(b < a for a, b in zip(obj_a, obj_b))
    else:
        better = all(b >= a for a, b in zip(obj_a, obj_b))
        strictly_better = any(b > a for a, b in zip(obj_a, obj_b))
    return better and strictly_better

def find_pareto_front(F, minimize=True):
    """
    Find Pareto front from objective values.

    F: array of shape (n_solutions, n_objectives)
    Returns: indices of non-dominated solutions
    """
    n = len(F)
    pareto_indices = []

    for i in range(n):
        dominated = False
        for j in range(n):
            if i != j and is_dominated(F[i], F[j], minimize):
                dominated = True
                break
        if not dominated:
            pareto_indices.append(i)

    return np.array(pareto_indices)

# Example usage
F = np.random.rand(100, 2)  # 100 solutions, 2 objectives
pareto_idx = find_pareto_front(F, minimize=True)
pareto_F = F[pareto_idx]

print(f"Pareto front contains {len(pareto_F)} solutions out of {len(F)}")
```

### Hypervolume Indicator

Measures quality of Pareto front approximation.

```python
from pymoo.indicators.hv import HV

# Hypervolume indicator
ref_point = np.array([1.1, 1.1])  # Reference point (should dominate all solutions)
ind = HV(ref_point=ref_point)

# Calculate hypervolume
hypervolume = ind(res.F)
print(f"Hypervolume: {hypervolume:.4f}")

# Compare two Pareto fronts
hv1 = ind(pareto_front_1)
hv2 = ind(pareto_front_2)
print(f"Front 1 is better: {hv1 > hv2}")
```

### Generational Distance (GD)

Measures convergence to true Pareto front.

```python
from pymoo.indicators.gd import GD

# Requires true Pareto front (if known)
true_pf = np.array([...])  # True Pareto front

ind = GD(true_pf)
gd = ind(res.F)
print(f"Generational Distance: {gd:.4f}")  # Lower is better
```

### Inverted Generational Distance (IGD)

Measures both convergence and diversity.

```python
from pymoo.indicators.igd import IGD

ind = IGD(true_pf)
igd = ind(res.F)
print(f"Inverted Generational Distance: {igd:.4f}")  # Lower is better
```

### Spacing

Measures uniformity of distribution along Pareto front.

```python
def spacing(F):
    """
    Calculate spacing metric.

    Lower values indicate more uniform distribution.
    """
    distances = []
    for i in range(len(F)):
        # Find minimum distance to other solutions
        min_dist = np.min([np.linalg.norm(F[i] - F[j])
                          for j in range(len(F)) if i != j])
        distances.append(min_dist)

    d_bar = np.mean(distances)
    spacing_metric = np.sqrt(np.sum((distances - d_bar)**2) / len(distances))

    return spacing_metric

sp = spacing(res.F)
print(f"Spacing: {sp:.4f}")  # Lower is better
```

## Visualization

### 2D Pareto Front

```python
import matplotlib.pyplot as plt

def plot_pareto_front_2d(F, X=None, labels=None):
    """
    Plot 2D Pareto front.

    F: Objective values, shape (n, 2)
    X: Decision variables (optional)
    labels: Axis labels (optional)
    """
    fig, axes = plt.subplots(1, 2 if X is not None else 1, figsize=(12, 5))

    if X is None:
        axes = [axes]

    # Plot objective space
    axes[0].scatter(F[:, 0], F[:, 1], alpha=0.7)
    axes[0].set_xlabel(labels[0] if labels else 'Objective 1')
    axes[0].set_ylabel(labels[1] if labels else 'Objective 2')
    axes[0].set_title('Pareto Front (Objective Space)')
    axes[0].grid(True, alpha=0.3)

    # Plot decision space
    if X is not None:
        axes[1].scatter(X[:, 0], X[:, 1], alpha=0.7)
        axes[1].set_xlabel('x1')
        axes[1].set_ylabel('x2')
        axes[1].set_title('Pareto Set (Decision Space)')
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# Usage
plot_pareto_front_2d(res.F, res.X, labels=['Cost', 'Performance'])
```

### 3D Pareto Front

```python
def plot_pareto_front_3d(F, labels=None):
    """Plot 3D Pareto front"""
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(F[:, 0], F[:, 1], F[:, 2], alpha=0.6)
    ax.set_xlabel(labels[0] if labels else 'Objective 1')
    ax.set_ylabel(labels[1] if labels else 'Objective 2')
    ax.set_zlabel(labels[2] if labels else 'Objective 3')
    ax.set_title('Pareto Front')

    plt.show()

# Usage
plot_pareto_front_3d(res.F, labels=['Cost', 'Time', 'Quality'])
```

### Parallel Coordinates (Many Objectives)

```python
from pymoo.visualization.pcp import PCP

# For many objectives (4+)
plot = PCP()
plot.add(res.F, label="Pareto Front")
plot.show()
```

### Trade-off Visualization

```python
def plot_tradeoff_curves(F, ref_idx=0):
    """
    Plot trade-off curves showing how objectives change along Pareto front.

    ref_idx: Reference solution index
    """
    n_obj = F.shape[1]

    # Sort by first objective
    sorted_idx = np.argsort(F[:, 0])
    F_sorted = F[sorted_idx]

    fig, axes = plt.subplots(n_obj - 1, 1, figsize=(10, 4 * (n_obj - 1)))
    if n_obj == 2:
        axes = [axes]

    for i in range(1, n_obj):
        axes[i-1].plot(F_sorted[:, 0], F_sorted[:, i], 'o-', alpha=0.7)
        axes[i-1].set_xlabel('Objective 1')
        axes[i-1].set_ylabel(f'Objective {i+1}')
        axes[i-1].grid(True, alpha=0.3)
        axes[i-1].set_title(f'Trade-off: Obj 1 vs Obj {i+1}')

    plt.tight_layout()
    plt.show()

plot_tradeoff_curves(res.F)
```

## Common Problem Types

### Portfolio Optimization

```python
class PortfolioProblem(Problem):
    """
    Multiobjective portfolio optimization.

    Objectives:
    1. Maximize expected return
    2. Minimize risk (variance)
    """
    def __init__(self, mu, Sigma):
        """
        mu: Expected returns (n_assets,)
        Sigma: Covariance matrix (n_assets, n_assets)
        """
        self.mu = mu
        self.Sigma = Sigma
        n = len(mu)

        super().__init__(
            n_var=n,
            n_obj=2,
            n_ieq_constr=0,
            xl=0.0,  # No short selling
            xu=1.0   # Maximum allocation
        )

    def _evaluate(self, X, out, *args, **kwargs):
        # Normalize weights to sum to 1
        W = X / X.sum(axis=1, keepdims=True)

        # Expected return (maximize -> negate for minimization)
        returns = -(W @ self.mu)

        # Risk (variance)
        risk = np.array([w @ self.Sigma @ w for w in W])

        out["F"] = np.column_stack([returns, risk])

# Example usage
np.random.seed(42)
n_assets = 10
mu = np.random.rand(n_assets) * 0.2  # Returns 0-20%
Sigma = np.random.rand(n_assets, n_assets)
Sigma = Sigma @ Sigma.T  # Make positive definite

problem = PortfolioProblem(mu, Sigma)
algorithm = NSGA2(pop_size=100)
res = minimize(problem, algorithm, ('n_gen', 200), seed=1)

# Plot efficient frontier
plt.scatter(-res.F[:, 0], res.F[:, 1])  # Negate return back to positive
plt.xlabel('Expected Return')
plt.ylabel('Risk (Variance)')
plt.title('Efficient Frontier')
plt.grid(True)
plt.show()
```

### Engineering Design

```python
class EngineeringDesign(Problem):
    """
    Example: Beam design

    Objectives:
    1. Minimize weight
    2. Minimize deflection

    Constraints:
    - Maximum stress
    - Geometric constraints
    """
    def __init__(self):
        super().__init__(
            n_var=3,      # width, height, length
            n_obj=2,      # weight, deflection
            n_ieq_constr=2,
            xl=np.array([0.1, 0.1, 1.0]),
            xu=np.array([1.0, 1.0, 10.0])
        )

    def _evaluate(self, X, out, *args, **kwargs):
        w, h, L = X[:, 0], X[:, 1], X[:, 2]

        # Material properties
        E = 200e9  # Young's modulus (Pa)
        rho = 7850  # Density (kg/m^3)
        F = 10000  # Applied force (N)
        sigma_max = 250e6  # Maximum allowable stress (Pa)

        # Objectives
        weight = rho * w * h * L
        I = (w * h**3) / 12  # Second moment of area
        deflection = (F * L**3) / (3 * E * I)

        # Constraints
        sigma = (F * L * h) / (2 * I)
        g1 = sigma - sigma_max  # Stress constraint: sigma <= sigma_max
        g2 = deflection - 0.01  # Deflection constraint: deflection <= 0.01 m

        out["F"] = np.column_stack([weight, deflection])
        out["G"] = np.column_stack([g1, g2])

problem = EngineeringDesign()
algorithm = NSGA2(pop_size=100)
res = minimize(problem, algorithm, ('n_gen', 300), seed=1)

print(f"Pareto solutions found: {len(res.F)}")
print(f"Max constraint violation: {np.max(res.CV):.2e}")
```

### Feature Selection

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

class FeatureSelectionProblem(Problem):
    """
    Multiobjective feature selection.

    Objectives:
    1. Maximize accuracy (minimize error)
    2. Minimize number of features
    """
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.n_features = X.shape[1]

        super().__init__(
            n_var=self.n_features,
            n_obj=2,
            xl=0,
            xu=1,
            vtype=int,  # Binary: feature selected or not
        )

    def _evaluate(self, X, out, *args, **kwargs):
        errors = []
        n_features = []

        for mask in X:
            # Count selected features
            n_sel = np.sum(mask)

            # Avoid empty feature set
            if n_sel == 0:
                errors.append(1.0)
                n_features.append(0)
                continue

            # Select features
            X_subset = self.X[:, mask.astype(bool)]

            # Evaluate with cross-validation
            clf = RandomForestClassifier(n_estimators=50, random_state=42)
            scores = cross_val_score(clf, X_subset, self.y, cv=3)
            error = 1 - np.mean(scores)

            errors.append(error)
            n_features.append(n_sel)

        out["F"] = np.column_stack([errors, n_features])

# Example usage (commented to avoid long runtime)
# data = load_breast_cancer()
# problem = FeatureSelectionProblem(data.data, data.target)
# algorithm = NSGA2(pop_size=50)
# res = minimize(problem, algorithm, ('n_gen', 100), seed=1)
```

## Best Practices

### 1. Normalize Objectives

```python
class NormalizedProblem(Problem):
    def __init__(self, f1_scale, f2_scale):
        self.f1_scale = f1_scale
        self.f2_scale = f2_scale
        super().__init__(n_var=2, n_obj=2, xl=0, xu=1)

    def _evaluate(self, X, out, *args, **kwargs):
        # Raw objectives
        f1 = X[:, 0]**2 + X[:, 1]**2
        f2 = (X[:, 0] - 1)**2 + (X[:, 1] - 1)**2

        # Normalize to similar scales
        f1_norm = f1 / self.f1_scale
        f2_norm = f2 / self.f2_scale

        out["F"] = np.column_stack([f1_norm, f2_norm])
```

### 2. Set Appropriate Population Size

**Rule of thumb:**
- 2 objectives: pop_size = 50-100
- 3 objectives: pop_size = 100-200
- 4+ objectives: pop_size = 200-500

```python
# Automatically determine population size
n_obj = problem.n_obj
if n_obj == 2:
    pop_size = 100
elif n_obj == 3:
    pop_size = 150
else:
    pop_size = 200 + 50 * (n_obj - 3)

algorithm = NSGA2(pop_size=pop_size)
```

### 3. Use Sufficient Generations

```python
# Monitor convergence
from pymoo.util.display import Display

class MyDisplay(Display):
    def _do(self, problem, evaluator, algorithm):
        super()._do(problem, evaluator, algorithm)
        # Custom metrics
        print(f"Gen {algorithm.n_gen}: HV = {ind.calc(algorithm.pop.get('F')):.4f}")

# Run with monitoring
res = minimize(
    problem,
    algorithm,
    ('n_gen', 500),
    verbose=True,
    display=MyDisplay()
)
```

### 4. Multiple Runs for Robustness

```python
# Run multiple times with different seeds
results = []
hypervolumes = []

for seed in range(10):
    res = minimize(problem, algorithm, ('n_gen', 200), seed=seed, verbose=False)
    results.append(res)
    hypervolumes.append(ind(res.F))

# Select best run
best_idx = np.argmax(hypervolumes)
best_result = results[best_idx]

print(f"Best hypervolume: {hypervolumes[best_idx]:.4f}")
print(f"Mean hypervolume: {np.mean(hypervolumes):.4f} ± {np.std(hypervolumes):.4f}")
```

### 5. Validate Pareto Front

```python
def validate_pareto_front(F):
    """Verify all solutions are non-dominated"""
    n = len(F)
    for i in range(n):
        for j in range(n):
            if i != j:
                if is_dominated(F[i], F[j]):
                    print(f"Warning: Solution {i} is dominated by {j}")
                    return False
    print("✓ All solutions are non-dominated")
    return True

validate_pareto_front(res.F)
```

## Decision Making

After finding Pareto front, decision-maker must choose solution.

### Knee Point

Solution with best trade-off (maximum marginal rate of substitution).

```python
from pymoo.mcdm.pseudo_weights import PseudoWeights

# Find knee point
weights = PseudoWeights()
knee_idx = weights.do(res.F)

print(f"Knee point solution:")
print(f"  Objectives: {res.F[knee_idx]}")
print(f"  Variables: {res.X[knee_idx]}")
```

### Compromise Programming

Minimize distance to utopia point.

```python
def find_compromise_solution(F, p=2):
    """
    Find compromise solution using Lp-norm.

    p=1: Manhattan distance
    p=2: Euclidean distance
    p=inf: Chebyshev distance
    """
    # Utopia point (best value for each objective)
    utopia = np.min(F, axis=0)

    # Nadir point (worst value for each objective)
    nadir = np.max(F, axis=0)

    # Normalize
    F_norm = (F - utopia) / (nadir - utopia + 1e-10)

    # Calculate distances
    if p == np.inf:
        distances = np.max(F_norm, axis=1)
    else:
        distances = np.sum(F_norm**p, axis=1)**(1/p)

    # Find minimum distance
    best_idx = np.argmin(distances)

    return best_idx

compromise_idx = find_compromise_solution(res.F, p=2)
print(f"Compromise solution: {res.F[compromise_idx]}")
```

### Interactive Filtering

```python
def filter_solutions(F, X, constraints):
    """
    Filter solutions based on preferences.

    constraints: dict like {'f1_max': 10, 'f2_max': 5}
    """
    mask = np.ones(len(F), dtype=bool)

    if 'f1_max' in constraints:
        mask &= F[:, 0] <= constraints['f1_max']
    if 'f2_max' in constraints:
        mask &= F[:, 1] <= constraints['f2_max']
    # Add more constraints as needed

    return F[mask], X[mask]

# Example: Filter solutions with f1 <= 0.5
F_filtered, X_filtered = filter_solutions(
    res.F, res.X,
    {'f1_max': 0.5}
)
print(f"Filtered to {len(F_filtered)} solutions")
```

## Troubleshooting

| Problem | Symptoms | Solutions |
|---------|----------|-----------|
| Poor convergence | Large gaps in Pareto front | Increase generations, population size |
| Uneven distribution | Clustered solutions | Use NSGA-III or MOEA/D, increase diversity |
| Constraint violations | res.CV > 0 | Adjust constraint handling, feasible initialization |
| Long runtime | Hours for convergence | Reduce pop size, use faster problem evaluation, parallelize |
| Non-convex regions missed | Gaps in weighted sum front | Use ε-constraint or evolutionary algorithms |
| Scaling issues | One objective dominates | Normalize objectives to similar ranges |

## Performance Tips

### Parallelize Evaluations

```python
from multiprocessing.pool import ThreadPool

# Parallelize with threads
pool = ThreadPool(8)
res = minimize(
    problem,
    algorithm,
    ('n_gen', 200),
    seed=1,
    verbose=True,
    elementwise_runner=pool.starmap  # NOTE: elementwise_runner is deprecated in pymoo >= 0.6. Use ElementwiseEvaluation or override _evaluate instead.
)
pool.close()
```

### Warm Start from Previous Run

```python
# Save result
np.save('pareto_front.npy', res.F)
np.save('pareto_set.npy', res.X)

# Load and use as initial population
prev_X = np.load('pareto_set.npy')
from pymoo.core.population import Population

pop = Population.new(X=prev_X)
algorithm.initialization = pop

# Continue optimization
res = minimize(problem, algorithm, ('n_gen', 100), seed=1)
```

## Installation

```bash
# pymoo (recommended)
pip install pymoo

# platypus
pip install platypus-opt

# DEAP
pip install deap

# Visualization
pip install matplotlib
```

## Additional Resources

- **pymoo Documentation:** https://pymoo.org/
- **Multi-Objective Optimization (Deb):** Classic textbook
- **EMO Conference:** Leading conference on evolutionary multiobjective optimization
- **NSGA-II Paper:** Deb et al., "A fast and elitist multiobjective genetic algorithm: NSGA-II"

## Related Skills

- `python-optimization` - Single-objective optimization (scipy, pyomo, cvxpy)
- `python-ase` - Materials optimization with multiple objectives
- `pycse` - Regression and parameter estimation
