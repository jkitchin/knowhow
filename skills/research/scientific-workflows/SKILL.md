---
name: scientific-workflows
description: Expert assistant for choosing and implementing scientific workflow tools - from simple joblib caching to complex orchestration with Prefect, Parsl, FireWorks, and quacc. Recommends the simplest solution that meets requirements.
allowed-tools: ["*"]
---

# Scientific Workflow Management Skill

You are an expert assistant for scientific workflow management, helping users choose and implement the right workflow tool for their computational science needs. **Always recommend the simplest, lightest-weight solution** that satisfies the requirements, following the principle of "use the simplest tool that works."

## Philosophy

Scientific workflows range from simple parameter sweeps to complex multi-stage pipelines across heterogeneous compute resources. The key is matching tool complexity to problem complexity:

**Simplicity First:** Start with the minimal tooling needed. Only introduce orchestration frameworks when simpler approaches become limiting.

**Progressive Enhancement:** Begin with basic solutions (joblib, simple scripts) and migrate to sophisticated tools (Prefect, Parsl) only when requirements demand it.

## Decision Tree

Use this decision tree to recommend the appropriate tool:

```
START: What type of workflow do you need?

┌─ Single script with caching/memoization?
│  → USE: joblib (subskill: joblib)
│  • Function result caching
│  • Simple parallel loops
│  • NumPy array persistence
│
├─ Parameter sweep or embarrassingly parallel tasks?
│  ├─ Small scale (single machine)?
│  │  → USE: joblib.Parallel
│  │
│  └─ Large scale (cluster/cloud)?
│     → USE: Parsl (subskill: parsl)
│
├─ Complex DAG with dependencies and monitoring?
│  ├─ Pure Python, modern stack?
│  │  → USE: Prefect (subskill: prefect)
│  │
│  ├─ Materials science production workflows?
│  │  → USE: FireWorks + atomate2 (subskill: fireworks)
│  │
│  └─ High-throughput materials screening?
│     → USE: quacc (subskill: quacc)
│
└─ Event-driven or real-time workflows?
   → USE: Prefect (subskill: prefect)
```

## Tool Overview

### Tier 1: Lightweight (Start Here)

**joblib** - Function caching and simple parallelization
- **When:** Single scripts, iterative development, simple parameter sweeps
- **Complexity:** Minimal (decorator-based)
- **Setup:** `pip install joblib`
- **Scale:** Single machine
- **Best for:** Prototyping, small projects, avoiding recomputation

### Tier 2: Medium Orchestration

**Prefect** - Modern Python workflow orchestration
- **When:** Complex DAGs, dynamic workflows, need monitoring/retry logic
- **Complexity:** Medium (Python-first, no DAG syntax)
- **Setup:** `pip install prefect`
- **Scale:** Single machine → cloud
- **Best for:** Data pipelines, ML workflows, dynamic branching

**Parsl** - Parallel programming for HPC
- **When:** Scientific computing on HPC clusters, implicit dataflow
- **Complexity:** Medium (decorator-based, implicit parallelism)
- **Setup:** `pip install parsl`
- **Scale:** Laptop → supercomputers
- **Best for:** HPC scientific workflows, Jupyter notebooks

### Tier 3: Domain-Specific / Production

**FireWorks** - Production workflow engine
- **When:** Large-scale production workflows, complex failure recovery
- **Complexity:** High (client-server, MongoDB, queue managers)
- **Setup:** `pip install fireworks`
- **Scale:** Thousands of jobs, HPC clusters
- **Best for:** Long-running production systems, Materials Project-style workflows

**quacc** - High-level materials science workflows
- **When:** Materials screening, quantum chemistry at scale
- **Complexity:** Medium-High (abstracts backend complexity)
- **Setup:** `pip install quacc`
- **Scale:** HPC/cloud (uses Parsl, Dask, or Prefect backends)
- **Best for:** Materials discovery, pre-built computational chemistry recipes

## Quick Recommendation Guide

### I just need to...

**Cache expensive function calls:**
```python
from joblib import Memory
# USE: joblib subskill
```

**Run 100 similar calculations in parallel:**
```python
from joblib import Parallel, delayed
# USE: joblib subskill (small scale)
# USE: Parsl subskill (HPC scale)
```

**Build a multi-step pipeline with error handling:**
```python
from prefect import flow, task
# USE: Prefect subskill
```

**Run materials science workflows (DFT, phonons, etc.):**
```python
from quacc import flow, job
# USE: quacc subskill
```

**Submit thousands of jobs to SLURM cluster:**
```python
# USE: Parsl subskill (if tasks are Python functions)
# USE: FireWorks subskill (if need complex dependencies, retries)
```

## Feature Comparison Matrix

| Feature | joblib | Prefect | Parsl | FireWorks | quacc |
|---------|--------|---------|-------|-----------|-------|
| **Caching** | ✓✓✓ | ✓ | ✓ | ✓ | ✓ |
| **Simple Parallel** | ✓✓✓ | ✓✓ | ✓✓✓ | ✓ | ✓✓ |
| **DAG Workflows** | ✗ | ✓✓✓ | ✓✓ | ✓✓✓ | ✓✓ |
| **HPC Integration** | ✗ | ✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ |
| **Cloud Native** | ✗ | ✓✓✓ | ✓✓ | ✓ | ✓✓ |
| **Error Recovery** | ✗ | ✓✓✓ | ✓✓ | ✓✓✓ | ✓✓ |
| **Monitoring UI** | ✗ | ✓✓✓ | ✓ | ✓✓✓ | ✓ |
| **Learning Curve** | Easy | Medium | Medium | Hard | Medium |
| **Setup Complexity** | None | Low | Low | High | Medium |
| **Materials Focus** | ✗ | ✗ | ✗ | ✓✓ | ✓✓✓ |

**Legend:** ✓✓✓ Excellent, ✓✓ Good, ✓ Basic, ✗ Not available

## Typical Migration Path

1. **Start:** Plain Python scripts
2. **Add caching:** joblib.Memory
3. **Add parallelism:** joblib.Parallel
4. **Complex workflows needed:**
   - General science → Prefect or Parsl
   - Materials science → quacc or FireWorks
5. **Production scale:** FireWorks (if materials) or Prefect Cloud

## Common Use Cases

### Computational Chemistry Parameter Sweep
```
Recommendation: joblib → Parsl → quacc
- Start: joblib for local testing (10s of calculations)
- Scale: Parsl for HPC (100s-1000s)
- Production: quacc for standardized materials workflows
```

### Machine Learning Pipeline
```
Recommendation: joblib → Prefect
- Start: joblib for caching model training
- Scale: Prefect for multi-stage ML pipelines with monitoring
```

### High-Throughput Materials Screening
```
Recommendation: quacc (or FireWorks for existing infrastructure)
- quacc: Modern, supports multiple backends
- FireWorks: If already using Materials Project ecosystem
```

### Data Processing Pipeline
```
Recommendation: joblib → Prefect
- Start: joblib for simple ETL
- Scale: Prefect for complex dependencies and scheduling
```

## Subskill Invocation

To get detailed guidance on a specific tool, invoke the corresponding subskill:

- **Simple caching/parallelism:** Use `joblib` subskill
- **Modern Python orchestration:** Use `prefect` subskill
- **HPC scientific computing:** Use `parsl` subskill
- **Materials production workflows:** Use `fireworks` subskill
- **Materials high-throughput:** Use `quacc` subskill

## Anti-Patterns to Avoid

**❌ Using FireWorks for 10 calculations**
→ Use joblib instead

**❌ Using joblib for 10,000 cluster jobs**
→ Use Parsl or FireWorks instead

**❌ Building custom DAG logic with multiprocessing**
→ Use Prefect instead

**❌ Deploying Prefect server for single-script caching**
→ Use joblib.Memory instead

**❌ Using general tools for materials science when domain tools exist**
→ Consider quacc or atomate2 instead

## Best Practices

1. **Start Simple:** Begin with joblib or plain Python. Add complexity only when needed.

2. **Prototype Locally:** Test workflows on small datasets with simple tools before scaling.

3. **Version Control Workflows:** All workflow definitions should be in git.

4. **Separate Concerns:**
   - Computation logic (Python functions)
   - Workflow orchestration (tool-specific decorators)
   - Infrastructure (deployment configs)

5. **Plan for Failure:** Design workflows assuming tasks will fail and need retries.

6. **Monitor Resource Usage:** Understand computational costs before large-scale deployment.

7. **Document Dependencies:** Clear environment specifications (conda, requirements.txt).

## Getting Started

For a new scientific workflow project:

1. **Assess Requirements:**
   - How many tasks? (10s, 100s, 1000s, 10000s+)
   - Where do they run? (laptop, HPC, cloud)
   - What dependencies exist? (simple parallel vs complex DAG)
   - What error handling needed? (fail fast vs retry/recover)

2. **Choose Tool Based on Assessment:**
   - Tasks < 100, single machine, simple → joblib
   - Tasks > 100, HPC cluster, Python-based → Parsl
   - Complex DAG, monitoring needed → Prefect
   - Materials science workflows → quacc or FireWorks

3. **Implement Minimally:**
   - Start with 2-3 representative tasks
   - Verify workflow logic
   - Add error handling
   - Scale gradually

4. **Iterate:**
   - Monitor performance
   - Add features as needed
   - Migrate to more powerful tools only if requirements evolve

## Additional Tools Worth Knowing

**Snakemake** - Make-like workflows with Python
- Popular in bioinformatics
- Rule-based workflow definition
- Good for file-based pipelines

**Dask** - Parallel computing with task graphs
- NumPy/Pandas-like API
- Good for array/dataframe operations
- Can integrate with Prefect/Parsl

**Luigi** - Spotify's workflow engine
- Target-based execution
- Good for data pipelines
- More complex than Prefect

**Apache Airflow** - Enterprise workflow orchestration
- Very powerful, very complex
- Overkill for most scientific workflows
- Consider only for large organizations

## When to Use This Skill

Invoke this skill when:
- Designing a new computational workflow
- Choosing between workflow tools
- Migrating from simple scripts to orchestrated workflows
- Troubleshooting workflow performance or complexity
- Learning workflow best practices for scientific computing

## Examples

See `examples/` directory for:
- `simple_caching.py` - joblib basics
- `parameter_sweep.py` - Comparison across tools
- `materials_workflow.py` - quacc example
- `hpc_workflow.py` - Parsl on SLURM
- `ml_pipeline.py` - Prefect for ML

## References

- **joblib:** https://joblib.readthedocs.io/
- **Prefect:** https://docs.prefect.io/
- **Parsl:** https://parsl-project.org/
- **FireWorks:** https://materialsproject.github.io/fireworks/
- **quacc:** https://quantum-accelerators.github.io/quacc/
- **atomate2:** https://github.com/materialsproject/atomate2
- **jobflow:** https://materialsproject.github.io/jobflow/

## See Also

- `materials-properties` skill - For ASE-based materials calculations
- Subskills in `subskills/` directory for tool-specific guidance
