---
name: fairchem
description: Expert guidance for using Meta's FAIRChem library - machine learning methods for materials science and quantum chemistry with pretrained UMA models and ASE integration
---

# FAIRChem Skill

Expert assistance for using Meta's [FAIRChem](https://github.com/FAIR-Chem/fairchem) (formerly Open Catalyst Project) - a machine learning library for ultra-fast materials science and quantum chemistry calculations.

## What This Skill Does

This skill enhances Claude Code with deep knowledge of FAIRChem, enabling it to help you:

- **Use ML potentials** - Replace slow DFT with 100-1000× faster ML predictions
- **Run multi-domain calculations** - Same model for catalysis, materials, molecules, MOFs
- **Scale to large systems** - Handle 1000s of atoms with multi-GPU support
- **Integrate with ASE** - Drop-in replacement for traditional calculators
- **Optimize structures** - Fast geometry optimization and MD simulations
- **Screen candidates** - High-throughput workflows for materials discovery

## When to Use This Skill

Claude will automatically use this skill when you're working with FAIRChem. You can also explicitly request it:

- "Using the fairchem skill, help me set up a catalyst screening workflow"
- "How do I use UMA models for molecular dynamics?"
- "Show me how to optimize a bulk crystal with FAIRChem"

## What You Get

### 1. Complete Working Examples

Get production-ready code for all FAIRChem use cases:

```python
# Example: "Help me optimize a Cu slab with CO adsorbate"
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import fcc111, add_adsorbate
from ase.optimize import LBFGS

# Load UMA model
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# Create calculator for catalysis
calc = FAIRChemCalculator(
    predictor,
    task_name="oc20"  # Catalysis domain
)

# Build and optimize
slab = fcc111("Cu", size=(4, 4, 4), vacuum=10.0)
add_adsorbate(slab, "CO", height=2.0)
slab.calc = calc

opt = LBFGS(slab)
opt.run(fmax=0.05)
```

### 2. Domain-Specific Guidance

FAIRChem uses task names for different chemistry domains:

| Task | Domain | Use For | Model Support |
|------|--------|---------|---------------|
| `oc20` | Catalysis | Surfaces + adsorbates | All |
| `oc22` | Oxide catalysis | Oxide surfaces | uma-s-1p2 only |
| `oc25` | Electrocatalysis | Electrochemical surfaces | uma-s-1p2 only |
| `omat` | Materials | Bulk crystals, defects | All |
| `omol` | Molecules | Organic chemistry, polymers | All |
| `odac` | MOFs | Metal-organic frameworks | All |
| `omc` | Crystals | Molecular crystals | All |

### 3. Performance Optimization

- Multi-GPU scaling with `workers=N` (requires `fairchem-core[extras]`)
- Turbo mode and `turbo_umas` for maximum speed with UMA-S models
- Model selection guidance (uma-s-1p2 vs uma-m-1p1)
- Memory optimization tips

### 4. Complete Workflows

- Surface adsorption energy calculations
- Bulk lattice optimization
- Molecular dynamics simulations
- NEB reaction barriers
- Formation energy calculations
- High-throughput screening

## Key Features

### Universal Models (UMA)
- **One model, many domains** - Switch domains with `task_name`
- **`uma-s-1p2`** - Small, fastest (6.6M/290M params) — recommended for speed
- **`uma-s-1p1`** - Small, fast (6.6M/150M params) — previous generation
- **`uma-m-1p1`** - Medium, highest accuracy (50M/1.4B params)

### ASE Integration
- Drop-in replacement for DFT calculators
- Works with all ASE tools (optimization, MD, NEB, etc.)
- Familiar interface for ASE users

### Speed
- **100-1000× faster than DFT**
- Multi-GPU support for large systems
- Turbo and `turbo_umas` modes for maximum performance
- ~1 ns/day with 100k+ atom systems using multi-GPU

### Scale
- Handle 1000s of atoms
- Distributed inference across GPUs via Ray
- LAMMPS integration for very large-scale MD
- Efficient for high-throughput screening

## Installation Requirements

```bash
# Install FAIRChem
pip install fairchem-core

# For GPU support
pip install fairchem-core[gpu]

# For multi-GPU support (Ray)
pip install fairchem-core[extras]

# Hugging Face authentication (required!)
pip install huggingface-hub
huggingface-cli login
```

**Important**: You must:
1. Have a Hugging Face account
2. Request access to UMA models at `facebook/UMA`
3. Log in with your token

## Example Interactions

### Example 1: Catalyst Screening
```
You: Help me screen 10 different metals for CO adsorption using FAIRChem

Claude: I'll help you set up a high-throughput screening workflow with FAIRChem...
[Provides complete workflow with UMA model, oc20 task, batch processing]
```

### Example 2: Molecular Dynamics
```
You: Set up a 10ps MD simulation of a 2000-atom system

Claude: I'll use FAIRChem's turbo_umas mode and multi-GPU support for fast MD...
[Provides optimized MD setup with worker configuration]
```

### Example 3: Lattice Optimization
```
You: Find the equilibrium lattice constant of iron

Claude: I'll use the omat task for bulk materials optimization...
[Provides code with FrechetCellFilter for cell optimization]
```

### Example 4: Reaction Barriers
```
You: Calculate the diffusion barrier for O on Pt(111)

Claude: I'll set up a NEB calculation with FAIRChem's oc20 model...
[Provides NEB workflow with FAIRChemCalculator]
```

## FAIRChem vs DFT

| Aspect | FAIRChem | DFT |
|--------|----------|-----|
| **Speed** | 100-1000× faster | Baseline |
| **Accuracy** | ~0.1 eV error | Reference |
| **System size** | 1000s of atoms | 10-100s atoms |
| **GPU scaling** | Linear | Limited |
| **Best for** | Screening, MD, large systems | High accuracy, validation |

## When to Use FAIRChem

**Use FAIRChem for:**
- Initial screening of many candidates
- Long molecular dynamics simulations
- Large systems (>500 atoms)
- High-throughput workflows
- Rapid prototyping

**Use DFT for:**
- Final validation of results
- Highest accuracy requirements
- Novel chemistries outside training data
- Electronic structure analysis

## Important Caveats

- **Energy labels**: UMA models use DFT/DFT+U total energy labels NOT compatible with Materials Project MP2020 corrections
- **Spin/charge**: For `omol` task, set via `atoms.info.update({"spin": 1, "charge": 0})`
- **v2 breaking change**: FAIRChem v2 is not compatible with v1 models or code

## Skill Contents

- **SKILL.md** - Complete FAIRChem reference
  - Model loading and configuration
  - Task selection guide
  - Complete workflows for all domains
  - Performance optimization
  - Best practices and troubleshooting

- **QUICK_REFERENCE.md** - Condensed cheat sheet
  - Model loading patterns
  - Task selection table
  - Common code snippets
  - Performance tips

- **examples/** - Working example scripts
  - `catalyst_screening.py` - High-throughput adsorption energy screening

## Tips for Best Results

1. **Choose the right task** - Match `task_name` to your chemistry domain
2. **Start with turbo_umas** - Use `turbo_umas` for UMA-S initial screening
3. **Validate critical results** - Compare ML predictions with DFT for important cases
4. **Use appropriate model** - `uma-s-1p2` for speed, `uma-m-1p1` for accuracy
5. **Leverage GPUs** - Use `workers=N` for large batches

## Common Questions

**Q: Which model should I use?**
- Screening/MD: `uma-s-1p2` + turbo_umas
- Production: `uma-m-1p1`
- Very large systems: `uma-s-1p2` + workers
- Oxide/electrocatalysis: `uma-s-1p2` (only model supporting oc22/oc25)

**Q: How accurate is FAIRChem?**
- Typical error: ~0.1 eV (0.05-0.2 eV range)
- Good for screening and ranking
- Validate critical results with DFT

**Q: Can I use my own trained model?**
- Yes, use `pretrained_mlip.get_predict_unit("/path/to/checkpoint.pt")`

**Q: What about uncertainty?**
- UMA models don't provide uncertainty estimates
- Test on similar known systems first
- Validate against DFT for critical results

## Version Requirements

- FAIRChem >= 2.0 (for UMA models)
- ASE >= 3.22
- Python >= 3.9
- CUDA >= 11.8 (for GPU)

**Important**: FAIRChem v2 is a breaking change from v1. Old models and code are not compatible. For v1: `pip install fairchem-core==1.10.0`.

## Related Skills

- `python-ase` - ASE fundamentals and workflows
- `pymatgen` - Materials analysis and structure manipulation
- `eln` - Documenting computational experiments

## Resources

- [FAIRChem GitHub](https://github.com/FAIR-Chem/fairchem)
- [Official Documentation](https://fair-chem.github.io/core/)
- [UMA Models on HuggingFace](https://huggingface.co/facebook/UMA)

## License

This skill documentation is part of the knowhow project (MIT License).
