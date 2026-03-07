# joblib Subskill

## Overview

joblib provides lightweight pipelining tools for Python, focusing on **caching** and **simple parallelization**. It's the simplest workflow tool and should be your first choice for:
- Function result caching (memoization)
- Embarrassingly parallel tasks on a single machine
- Fast persistence of NumPy arrays

**Philosophy:** Minimal code changes, maximum benefit.

## Core Features

### 1. Memory (Caching)

Cache expensive function results to disk automatically.

**Basic Usage:**
```python
from joblib import Memory

# Create cache directory
memory = Memory("./cachedir", verbose=0)

@memory.cache
def expensive_function(param1, param2):
    """This function's results will be cached."""
    import time
    time.sleep(2)  # Simulate expensive computation
    return param1 + param2

# First call: computed (takes 2 seconds)
result = expensive_function(10, 20)

# Second call: cached (instant)
result = expensive_function(10, 20)
```

**When to Use:**
- Iterative development (avoid recomputing during debugging)
- Parameter sweeps where some parameters repeat
- Long-running functions that might fail partway through

**Cache Management:**
```python
# Clear specific function cache
expensive_function.clear()

# Clear all cache
memory.clear()

# Get cache location
print(memory.location)

# Reduce cache size (keep only N recent)
memory = Memory("./cache", verbose=0, bytes_limit=1e9)  # 1GB limit
```

### 2. Parallel (Simple Parallelization)

Execute embarrassingly parallel tasks across CPU cores.

**Basic Pattern:**
```python
from joblib import Parallel, delayed

def process_item(item):
    """Function to parallelize."""
    return item ** 2

# Sequential (baseline)
results_seq = [process_item(i) for i in range(100)]

# Parallel (automatic load balancing)
results_par = Parallel(n_jobs=4)(
    delayed(process_item)(i) for i in range(100)
)
```

**Key Parameters:**
```python
Parallel(
    n_jobs=-1,           # -1 = use all CPUs
    verbose=10,          # Progress reporting
    backend='loky',      # 'loky', 'threading', 'multiprocessing'
    batch_size='auto',   # Tasks per worker dispatch
    pre_dispatch='2*n_jobs'  # Tasks to pre-allocate
)
```

**Backends:**
- **loky** (default): Process-based, robust, works with most code
- **threading**: Thread-based, good for I/O-bound tasks
- **multiprocessing**: Process-based, legacy option

**When to Use:**
- 10-1000 independent tasks
- Single machine execution
- Simple parallelism (no complex dependencies)

### 3. Persistence (Fast Saving)

Efficiently save/load NumPy arrays and complex objects.

```python
from joblib import dump, load
import numpy as np

# Save
data = {'arrays': [np.random.rand(1000, 1000)],
        'params': {'alpha': 0.1}}
dump(data, 'results.pkl')

# Load
data_loaded = load('results.pkl')
```

**Advantages over pickle:**
- Faster for NumPy arrays
- Better compression
- Memory-mapped loading for large arrays

## Common Patterns

### Pattern 1: Parameter Sweep with Caching

```python
from joblib import Memory, Parallel, delayed

memory = Memory("./cache")

@memory.cache
def simulate(param1, param2, seed):
    """Expensive simulation."""
    import numpy as np
    np.random.seed(seed)
    # Complex simulation...
    return result

# Run parameter sweep (cached)
param_grid = [(p1, p2, s) for p1 in [0.1, 0.5, 1.0]
                          for p2 in [1, 2, 3]
                          for s in range(10)]

results = Parallel(n_jobs=-1)(
    delayed(simulate)(*params) for params in param_grid
)
```

### Pattern 2: Resumable Workflow

```python
from joblib import Memory

memory = Memory("./cache")

@memory.cache
def stage1(data):
    # Long computation
    return processed_data

@memory.cache
def stage2(data):
    # Another long computation
    return analyzed_data

# If script crashes after stage1, stage1 won't rerun
data = load_data()
step1_result = stage1(data)  # Cached if already done
step2_result = stage2(step1_result)  # Cached if already done
```

### Pattern 3: Nested Parallelism

```python
from joblib import Parallel, delayed

def process_group(group_id, items):
    """Process group of items in parallel."""
    return Parallel(n_jobs=2)(
        delayed(process_item)(item) for item in items
    )

# Outer parallel loop over groups
groups = [range(10*i, 10*(i+1)) for i in range(5)]
results = Parallel(n_jobs=5)(
    delayed(process_group)(i, group) for i, group in enumerate(groups)
)
```

### Pattern 4: Progress Monitoring

```python
from joblib import Parallel, delayed
import time

def slow_task(i):
    time.sleep(1)
    return i * 2

# With progress bar
results = Parallel(n_jobs=4, verbose=10)(
    delayed(slow_task)(i) for i in range(20)
)

# Output shows:
# [Parallel(n_jobs=4)]: Done   1 tasks      | elapsed:    1.0s
# [Parallel(n_jobs=4)]: Done   4 tasks      | elapsed:    1.0s
# ...
```

## Advanced Features

### Hashing for Cache Keys

Control what makes results unique:

```python
from joblib import Memory

memory = Memory("./cache")

# Default: all arguments matter
@memory.cache
def compute(data, param):
    return data + param

# Custom: ignore certain arguments
from joblib import hashing

@memory.cache(ignore=['verbose'])
def compute_custom(data, param, verbose=False):
    if verbose:
        print("Computing...")
    return data + param
```

### Memory-Mapped Arrays

For very large arrays, use memory mapping:

```python
from joblib import load
import numpy as np

# Save with memory mapping
dump(large_array, 'data.pkl')

# Load memory-mapped (doesn't load into RAM immediately)
data_mmap = load('data.pkl', mmap_mode='r')
```

### Combining with NumPy

```python
import numpy as np
from joblib import Parallel, delayed

def parallel_dot_product(matrices):
    """Compute dot products in parallel."""
    def compute_dot(A, B):
        return np.dot(A, B)

    results = Parallel(n_jobs=-1)(
        delayed(compute_dot)(matrices[i], matrices[i+1])
        for i in range(0, len(matrices)-1, 2)
    )
    return results
```

## Performance Tips

1. **Batch Size:** For many small tasks, increase batch size:
   ```python
   Parallel(n_jobs=4, batch_size=10)(...)
   ```

2. **Backend Choice:**
   - CPU-bound → `loky` or `multiprocessing`
   - I/O-bound → `threading`
   - Functions with large data → `loky` with memory mapping

3. **Cache Location:** Use fast SSD for cache directory

4. **Avoid Overhead:** Don't parallelize if tasks are too small
   ```python
   # Bad: overhead dominates
   Parallel(n_jobs=4)(delayed(lambda x: x+1)(i) for i in range(10))

   # Good: tasks are substantial
   Parallel(n_jobs=4)(delayed(heavy_computation)(i) for i in range(10))
   ```

## Limitations

**When NOT to use joblib:**
- ❌ Need complex task dependencies (use Prefect)
- ❌ Running on HPC cluster (use Parsl)
- ❌ Need failure recovery (use Prefect/FireWorks)
- ❌ Tasks must run on different machines (use Parsl/Prefect)
- ❌ Need monitoring UI (use Prefect/FireWorks)

## Troubleshooting

**Cache not working:**
```python
# Check if function is actually cached
@memory.cache
def test():
    print("This should only print once")
    return 42

test()  # Prints
test()  # Should NOT print if caching works
```

**Parallel hanging:**
```python
# Try different backend
Parallel(n_jobs=4, backend='threading')(...)

# Or increase timeout
Parallel(n_jobs=4, timeout=300)(...)
```

**Memory issues:**
```python
# Use max_nbytes to limit memory
Parallel(n_jobs=4, max_nbytes='100M')(...)
```

## Migration to Other Tools

### When to Move to Prefect:
```python
# If you find yourself writing:
try:
    result = stage1()
    if result is not None:
        result2 = stage2(result)
except Exception:
    # Manual retry logic
    ...

# → Time to use Prefect with automatic retries
```

### When to Move to Parsl:
```python
# If you need:
from joblib import Parallel, delayed

# Run on SLURM cluster
results = Parallel(n_jobs=100)(  # Won't scale to HPC!
    delayed(compute)(i) for i in range(10000)
)

# → Time to use Parsl
```

## Real-World Example

**Scientific Data Analysis Pipeline:**
```python
from joblib import Memory, Parallel, delayed
import numpy as np

memory = Memory("./analysis_cache", verbose=0)

@memory.cache
def load_and_preprocess(filename):
    """Load and preprocess data file."""
    data = np.loadtxt(filename)
    # Expensive preprocessing
    return preprocessed_data

@memory.cache
def analyze_dataset(data, method='pca'):
    """Perform analysis."""
    if method == 'pca':
        # PCA analysis
        return pca_results
    else:
        # Other analysis
        return other_results

# Main workflow
files = ['data1.txt', 'data2.txt', 'data3.txt']

# Parallel data loading (cached)
datasets = Parallel(n_jobs=3)(
    delayed(load_and_preprocess)(f) for f in files
)

# Parallel analysis (cached)
results = Parallel(n_jobs=3)(
    delayed(analyze_dataset)(data, method='pca')
    for data in datasets
)
```

## References

- Official Docs: https://joblib.readthedocs.io/
- GitHub: https://github.com/joblib/joblib
- Examples: `../examples/simple_caching.py`

## See Also

- Main skill (`../SKILL.md`) - Decision tree for tool selection
- `prefect.md` - For complex workflows with dependencies
- `parsl.md` - For HPC scaling
