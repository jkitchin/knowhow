# Scientific Workflows - Quick Reference

## Decision Flowchart

```
┌─────────────────────────────────────────────────────────┐
│ What do you need to do?                                 │
└─────────────────────────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
    ┌────────┐    ┌──────────┐   ┌──────────┐
    │ Cache  │    │ Parallel │   │ Complex  │
    │ Results│    │ Tasks    │   │ Workflow │
    └────────┘    └──────────┘   └──────────┘
         │              │              │
         ▼              ▼              ▼
    ┌────────┐    ┌──────────┐   ┌──────────┐
    │joblib  │    │  Where?  │   │   DAG?   │
    │.Memory │    └──────────┘   └──────────┘
    └────────┘         │              │
                  ┌────┴─────┐    ┌───┴────┐
                  │          │    │        │
                  ▼          ▼    ▼        ▼
             ┌─────────┐┌─────┐ ┌───┐  ┌────┐
             │  Local  ││ HPC │ │Yes│  │ No │
             └─────────┘└─────┘ └───┘  └────┘
                  │         │     │       │
                  ▼         ▼     ▼       ▼
             ┌────────┐┌───────┐┌────┐┌────┐
             │joblib  ││Parsl  ││Pref││Loop│
             │.Parallel││       │ect││with│
             └────────┘└───────┘└────┘│deps│
                                      └────┘

Materials Science?
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐┌────────┐
│ quacc  ││FireWorks│
│(modern)││(legacy) │
└────────┘└────────┘
```

## At-a-Glance Tool Selection

### Your Situation → Tool

| If you need... | Use this | Why |
|----------------|----------|-----|
| Avoid recomputing same function calls | **joblib.Memory** | Dead simple caching |
| Run 10-100 tasks on laptop | **joblib.Parallel** | Built-in, no setup |
| Run 100+ tasks on HPC | **Parsl** | HPC-aware, implicit parallelism |
| Complex DAG with retries | **Prefect** | Modern, Pythonic, great UI |
| Cloud deployment | **Prefect Cloud** | Managed orchestration |
| Materials DFT workflows | **quacc** | Pre-built recipes, modern |
| Production materials workflows | **FireWorks** | Battle-tested, Materials Project |

## Quick Syntax Reference

### joblib - Caching

```python
from joblib import Memory

memory = Memory("./cache_dir", verbose=0)

@memory.cache
def slow_function(x, y):
    # Expensive computation
    return x + y

result = slow_function(1, 2)  # Computed
result = slow_function(1, 2)  # Cached!
```

### joblib - Parallel

```python
from joblib import Parallel, delayed

def process(item):
    return item ** 2

results = Parallel(n_jobs=4)(
    delayed(process)(i) for i in range(100)
)
```

### Prefect - Workflow

```python
from prefect import flow, task

@task(retries=2)
def extract_data():
    return data

@task
def transform_data(data):
    return transformed

@flow
def etl_pipeline():
    data = extract_data()
    result = transform_data(data)
    return result

etl_pipeline()
```

### Parsl - HPC

```python
import parsl
from parsl.app.app import python_app
from parsl.config import Config
from parsl.executors import HighThroughputExecutor

config = Config(
    executors=[HighThroughputExecutor()]
)
parsl.load(config)

@python_app
def compute(x):
    return x ** 2

futures = [compute(i) for i in range(100)]
results = [f.result() for f in futures]
```

### quacc - Materials

```python
from ase.build import bulk
from quacc.recipes.emt.core import relax_job

atoms = bulk("Cu")
result = relax_job(atoms)

print(result["atoms"])  # Relaxed structure
print(result["results"]["energy"])  # Final energy
```

## Feature Quick Lookup

### Need Caching?
- ✓ joblib.Memory (best)
- ✓ Prefect (basic)
- ✓ Parsl (basic)

### Need Parallel Execution?
- ✓ All tools support it
- → joblib: Simplest for local
- → Parsl: Best for HPC
- → Prefect: Best with dependencies

### Need Error Recovery?
- ✗ joblib
- ✓ Prefect (excellent)
- ✓ Parsl (good)
- ✓ FireWorks (excellent)

### Need Monitoring UI?
- ✗ joblib
- ✓ Prefect (excellent)
- ◐ Parsl (basic)
- ✓ FireWorks (excellent)

### Need HPC Integration?
- ✗ joblib
- ◐ Prefect (via workers)
- ✓ Parsl (excellent)
- ✓ FireWorks (excellent)

## Installation Commands

```bash
# Minimal
pip install joblib

# Modern orchestration
pip install prefect

# HPC workflows
pip install parsl

# Materials science
pip install quacc
pip install fireworks atomate2
```

## Common Anti-Patterns

| ❌ Don't Do This | ✓ Do This Instead |
|------------------|-------------------|
| Use FireWorks for 10 calculations | Use joblib |
| Build custom retry logic | Use Prefect or Parsl |
| Use joblib for 10K cluster jobs | Use Parsl or FireWorks |
| Deploy Prefect server for caching | Use joblib.Memory |
| Write custom DAG scheduler | Use Prefect |
| Hardcode SLURM commands | Use Parsl with config |

## Complexity vs Features

```
Low Complexity                              High Complexity
│                                                          │
joblib ────→ Prefect ────→ Parsl ────→ FireWorks
                           ↓
                         quacc

Low Features                              High Features
```

**Recommendation:** Start at the left, move right only when needed.

## Migration Paths

### Script → joblib
```diff
- def compute(x):
+ from joblib import Memory
+ memory = Memory("./cache")
+
+ @memory.cache
+ def compute(x):
      return heavy_computation(x)
```

### joblib → Prefect
```diff
- from joblib import Parallel, delayed
+ from prefect import flow, task

- def compute(x):
+ @task
+ def compute(x):
      return x ** 2

- results = Parallel(n_jobs=4)(delayed(compute)(i) for i in range(10))
+ @flow
+ def workflow():
+     results = [compute(i) for i in range(10)]
+     return results
+
+ workflow()
```

### Script → Parsl (HPC)
```diff
+ import parsl
+ from parsl.app.app import python_app
+
+ @python_app
  def compute(x):
      return x ** 2

- results = [compute(i) for i in range(100)]
+ futures = [compute(i) for i in range(100)]
+ results = [f.result() for f in futures]
```

## Decision Table

| Requirement | joblib | Prefect | Parsl | FireWorks |
|-------------|--------|---------|-------|-----------|
| Caching | ✓✓✓ | ✓ | ✓ | ✓ |
| Simple parallel | ✓✓✓ | ✓✓ | ✓✓✓ | ✓ |
| DAG workflows | ✗ | ✓✓✓ | ✓✓ | ✓✓✓ |
| HPC (SLURM/PBS) | ✗ | ✓ | ✓✓✓ | ✓✓✓ |
| Cloud native | ✗ | ✓✓✓ | ✓✓ | ✓ |
| Error recovery | ✗ | ✓✓✓ | ✓✓ | ✓✓✓ |
| Monitoring | ✗ | ✓✓✓ | ✓ | ✓✓✓ |
| Setup complexity | None | Low | Low | High |
| Learning curve | Easy | Med | Med | Hard |

**Legend:** ✓✓✓ Excellent, ✓✓ Good, ✓ Basic, ✗ No

## When to Escalate Complexity

### Stay with joblib if:
- < 100 tasks
- Single machine
- No dependencies between tasks
- Just need caching or simple parallelism

### Move to Prefect if:
- Need complex task dependencies
- Want monitoring and retry logic
- Building data pipelines
- Deploying to cloud

### Move to Parsl if:
- Running on HPC cluster
- Need implicit dataflow
- Working in Jupyter notebooks
- Want "write once, run anywhere"

### Move to FireWorks if:
- Production materials workflows
- Need complex failure recovery
- Already using Materials Project ecosystem
- Running thousands of interdependent jobs

## Resources

- Full decision tree: See `SKILL.md`
- Detailed guides: See `subskills/` directory
- Code examples: See `examples/` directory
- Tool comparison: See `references/comparison_guide.md`
