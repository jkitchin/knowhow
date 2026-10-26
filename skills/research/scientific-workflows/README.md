# Scientific Workflows Skill

Expert guidance for choosing and implementing scientific workflow management tools.

## Overview

This skill helps you select the right workflow tool for your scientific computing needs, following the principle: **use the simplest tool that works**. It covers tools ranging from lightweight caching (joblib) to sophisticated orchestration platforms (Prefect, Parsl, FireWorks, quacc).

## Quick Start

### Installation

Install tools as needed based on your requirements:

**Lightweight (start here):**
```bash
pip install joblib
```

**Medium orchestration:**
```bash
# Modern Python workflows
pip install prefect

# HPC scientific computing
pip install parsl
```

**Domain-specific:**
```bash
# Materials science production
pip install fireworks
pip install atomate2

# Materials high-throughput
pip install quacc
```

## Decision Framework

### I need to...

**Cache expensive computations**
→ Use: `joblib` subskill
```python
from joblib import Memory
memory = Memory("./cache")

@memory.cache
def expensive_function(param):
    # Your computation
    return result
```

**Run parallel tasks on my laptop**
→ Use: `joblib` subskill
```python
from joblib import Parallel, delayed

results = Parallel(n_jobs=4)(
    delayed(compute)(i) for i in range(100)
)
```

**Build complex workflows with monitoring**
→ Use: `prefect` subskill
```python
from prefect import flow, task

@task
def process_data(x):
    return x * 2

@flow
def my_workflow():
    result = process_data(5)
    return result
```

**Run on HPC cluster (SLURM, PBS)**
→ Use: `parsl` subskill
```python
import parsl
from parsl.app.app import python_app

@python_app
def compute(x):
    return x**2

future = compute(10)
result = future.result()
```

**Materials science workflows**
→ Use: `quacc` or `fireworks` subskill
```python
from quacc import flow, job
# Pre-built materials science recipes
```

## Tool Comparison

| Tool | Best For | Complexity | Scale |
|------|----------|------------|-------|
| **joblib** | Caching, simple parallel | Minimal | Single machine |
| **Prefect** | Python DAGs, monitoring | Medium | Single → cloud |
| **Parsl** | HPC scientific computing | Medium | Laptop → supercomputer |
| **FireWorks** | Production materials workflows | High | HPC clusters |
| **quacc** | Materials screening | Medium | HPC/cloud |

## Typical Workflow Evolution

1. **Start:** Plain Python script
2. **Add:** joblib caching (avoid recomputation)
3. **Scale:** joblib.Parallel (local parallelism)
4. **Orchestrate:** Prefect/Parsl (complex dependencies, HPC)
5. **Production:** Domain tools (quacc/FireWorks for materials)

## Learning Path

### Beginner
1. Start with `joblib` for caching
2. Add `joblib.Parallel` for simple parallelism
3. Read `examples/simple_caching.py`

### Intermediate
1. Learn Prefect for DAG workflows
2. Try Parsl for HPC if applicable
3. Read `examples/parameter_sweep.py`

### Advanced
1. Explore domain-specific tools (quacc, FireWorks)
2. Study `examples/materials_workflow.py`
3. Design production-scale systems

## Common Patterns

### Parameter Sweep

**Small scale (joblib):**
```python
from joblib import Parallel, delayed

parameters = [1, 2, 3, 4, 5]
results = Parallel(n_jobs=-1)(
    delayed(simulate)(p) for p in parameters
)
```

**Large scale (Parsl on HPC):**
```python
@python_app
def simulate(param):
    # Heavy computation
    return result

futures = [simulate(p) for p in parameters]
results = [f.result() for f in futures]
```

### Multi-Stage Pipeline

**Prefect:**
```python
from prefect import flow, task

@task
def stage1(data):
    return processed_data

@task
def stage2(data):
    return analyzed_data

@flow
def pipeline():
    data = load_data()
    processed = stage1(data)
    result = stage2(processed)
    return result
```

### Materials Workflow

**quacc:**
```python
from quacc.recipes.emt.core import relax_job

# High-level recipe
result = relax_job(atoms)
```

## File Organization

```
scientific-workflows/
├── SKILL.md              # Main skill with decision tree
├── README.md             # This file
├── QUICK_REFERENCE.md    # Quick decision flowchart
├── subskills/
│   ├── joblib.md         # Simple caching/parallel
│   ├── prefect.md        # Modern orchestration
│   ├── parsl.md          # HPC workflows
│   ├── fireworks.md      # Materials production
│   └── quacc.md          # Materials high-throughput
├── examples/
│   ├── simple_caching.py
│   ├── parameter_sweep.py
│   ├── ml_pipeline.py
│   ├── hpc_workflow.py
│   └── materials_workflow.py
└── references/
    └── comparison_guide.md
```

## When to Use This Skill

- Designing a new computational workflow
- Choosing between workflow tools
- Scaling from scripts to production
- Troubleshooting workflow complexity
- Learning workflow best practices

## Subskills

Invoke specific subskills for detailed guidance:

- `joblib` - Function caching and simple parallelism
- `prefect` - Modern Python workflow orchestration
- `parsl` - HPC scientific computing workflows
- `fireworks` - Production materials science workflows
- `quacc` - High-throughput materials screening

## Resources

**Official Documentation:**
- joblib: https://joblib.readthedocs.io/
- Prefect: https://docs.prefect.io/
- Parsl: https://parsl-project.org/
- FireWorks: https://materialsproject.github.io/fireworks/
- quacc: https://quantum-accelerators.github.io/quacc/

**Tutorials:**
- Examples in `examples/` directory
- Tool-specific guides in `subskills/`
- Comparison matrix in `references/`

## Contributing

This skill is designed to recommend the simplest solution that works. If you find cases where simpler tools are appropriate, please contribute!

## License

Part of the skillpack repository.
