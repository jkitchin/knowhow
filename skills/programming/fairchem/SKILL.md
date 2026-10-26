---
name: fairchem
description: Expert guidance for Meta's FAIRChem library - machine learning methods for materials science and quantum chemistry using pretrained UMA models with ASE integration for fast, accurate predictions
allowed-tools: ["*"]
---

# FAIRChem Skill

This skill provides expert guidance for using FAIRChem (formerly OCP - Open Catalyst Project), Meta's FAIR Chemistry library of machine learning methods for materials science and quantum chemistry.

## When to Use This Skill

Use this skill when:
- Using ML potentials for materials and molecular simulations
- Running fast geometry optimizations with pretrained models
- Performing large-scale MD simulations
- Calculating energies and forces without DFT
- Working with the UMA (Universal Materials Algebra) models
- Needing predictions for catalysis, molecules, crystals, or MOFs
- Integrating ML models with ASE workflows
- Scaling calculations across multiple GPUs

## Batch scripting vs. interactive steering (fairchem-mcp)

This skill covers the **batch** workflow: write a Python script, run it, read the
output. That is the right default for reproducible, unattended calculations.

For **interactive, agent-steered** simulation, there is a companion MCP server,
**`fairchem-mcp`** (https://github.com/jkitchin/fairchem-mcp). It keeps the model
resident, runs relaxations/MD in the background, and lets you watch a job and
steer it *mid-flight*. Prefer it when:
- You want to **monitor** a long relaxation/MD and react to a `trend` verdict
  (`decreasing` / `plateaued` / `stuck` / `diverging`).
- You want to **change strategy mid-run** — switch optimizer when FIRE stalls,
  tighten/loosen `fmax`, change temperature, pause or abort — without restarting.
- You want the model **loaded once** and reused across many quick calls.
- You want to **introspect the installed API or live objects** (`introspect`) or
  drop to raw Python on the same live `Atoms` (`execute` / `inspect_expr`).

Key tools: `attach_emt` / `load_model` / `attach_lammps` (LAMMPS classical
potentials as the force engine), `build_structure`, `start_relaxation` /
`start_md`, `start_neb` (reaction barriers, steer `set_climb` near convergence)
and `start_phonons` (frequencies + imaginary-mode/stability check),
`start_minima_search` (multiple distinct relaxed geometries via deflation/flooding
— adsorption sites, cluster isomers, conformers),
`start_eos_scan` (strain scan → equation-of-state fit: V0, E0, bulk modulus),
`start_elastic_scan` (stress-vs-strain → elastic tensor C_ij, VRH moduli, Born
stability), `start_convex_hull` (formation energies → phase stability / energy
above hull, e.g. alloy design),
transition-state searches `start_saddle_search` (dimer, Hessian-free),
`start_sella_search` (Sella RFO), and `start_pounce_saddles` (enumerate saddles by
Morse index), `get_status`, `get_results`, `steer`, `introspect`. Register it with
`{"mcpServers": {"fairchem": {"command": "fairchem-mcp"}}}`. Use plain batch
scripts (below) when you don't need live observation or steering.

## What is FAIRChem?

FAIRChem is Meta's machine learning framework for chemistry that provides:
- **Pretrained UMA models** (`uma-s-1p2`, `uma-m-1p1`) for universal predictions
- **Domain-specific tasks**: catalysis (oc20, oc22, oc25), materials (omat), molecules (omol), MOFs (odac), crystals (omc)
- **ASE integration** via `FAIRChemCalculator`
- **Multi-GPU support** for distributed inference via Ray
- **Fast predictions**: 100-1000× faster than DFT

### Key Advantage
FAIRChem allows you to use the same model across different chemistry domains by simply changing the `task_name` parameter.

## Core Concepts

### 1. UMA Models
Universal Materials Algebra models trained on diverse datasets:
- `uma-s-1p2`: Small model (6.6M/290M parameters) - fastest inference, best small model
- `uma-s-1p1`: Small model (6.6M/150M parameters) - previous generation
- `uma-m-1p1`: Medium model (50M/1.4B parameters) - highest accuracy

### 2. Task Names (Domains)
Specify the chemistry domain for domain-specific predictions:
- `oc20`: Catalysis (surfaces with adsorbates)
- `oc22`: Oxide catalysis (uma-s-1p2 only)
- `oc25`: Electrocatalysis (uma-s-1p2 only)
- `omat`: Inorganic materials (crystals, bulk)
- `omol`: Molecules (organic chemistry, polymers)
- `odac`: Metal-organic frameworks (MOFs)
- `omc`: Molecular crystals

### 3. FAIRChemCalculator
ASE calculator interface that wraps UMA models:
- Drop-in replacement for DFT calculators
- Supports all ASE workflows
- Provides energies, forces, and stresses
- Compatible with optimization, MD, NEB

### 4. Inference Settings
Performance optimization modes:
- `default`: Balanced speed and accuracy
- `turbo`: Faster inference, slightly reduced accuracy
- `turbo_umas`: Maximum speed for UMA-S models (uses triton kernels)
- Execution modes: `general`, `umas_fast_pytorch`, `umas_fast_gpu`

## Installation

```bash
# Install fairchem
pip install fairchem-core

# For GPU support
pip install fairchem-core[gpu]

# For multi-GPU support (Ray)
pip install fairchem-core[extras]

# Hugging Face login (required for UMA models)
pip install huggingface-hub
huggingface-cli login
```

**Note**: You must have a Hugging Face account and request access to the UMA model repository at `facebook/UMA`.

## Basic Usage Pattern

### Standard Workflow

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import bulk
from ase.optimize import LBFGS

# 1. Load pretrained model
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# 2. Create calculator for specific domain
calc = FAIRChemCalculator(
    predictor,
    task_name="omat"  # Choose domain
)

# 3. Use with ASE
atoms = bulk("Cu", "fcc", a=3.6)
atoms.calc = calc

# 4. Calculate properties
energy = atoms.get_potential_energy()
forces = atoms.get_forces()

# 5. Optimize structure
opt = LBFGS(atoms)
opt.run(fmax=0.05)
```

### Convenience Method

```python
from fairchem.core import FAIRChemCalculator

# One-step calculator creation
calc = FAIRChemCalculator.from_model_checkpoint(
    "uma-m-1p1",
    task_name="omat",
    inference_settings="turbo"
)
```

## Common Workflows

### Workflow 1: Catalysis - Surface Adsorption

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import fcc111, add_adsorbate
from ase.optimize import LBFGS
from ase.constraints import FixAtoms

# Load model
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# Create calculator for catalysis
calc = FAIRChemCalculator(
    predictor,
    task_name="oc20"  # Catalysis domain
)

# Build slab with adsorbate
slab = fcc111("Cu", size=(4, 4, 4), vacuum=10.0)
add_adsorbate(slab, "CO", height=2.0, position="fcc")

# Fix bottom layers
n_atoms_per_layer = 16
constraint = FixAtoms(indices=range(n_atoms_per_layer * 2))
slab.set_constraint(constraint)

# Attach calculator and optimize
slab.calc = calc
opt = LBFGS(slab, trajectory="slab_opt.traj")
opt.run(fmax=0.05)

# Get results
E = slab.get_potential_energy()
forces = slab.get_forces()
```

### Workflow 2: Bulk Materials - Lattice Optimization

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import bulk
from ase.optimize import FIRE
from ase.filters import FrechetCellFilter

# Load model
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# Calculator for materials
calc = FAIRChemCalculator(
    predictor,
    task_name="omat"  # Materials domain
)

# Create bulk structure
atoms = bulk("Fe", "bcc", a=2.87)
atoms.calc = calc

# Optimize both positions and cell
# FrechetCellFilter allows cell parameters to change
ucf = FrechetCellFilter(atoms)
opt = FIRE(ucf)
opt.run(fmax=0.05)

# Results
optimized_lattice = atoms.cell.cellpar()[0]
print(f"Optimized lattice constant: {optimized_lattice:.3f} Å")
```

### Workflow 3: Molecular Dynamics

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import bulk
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.langevin import Langevin
from ase import units

# Load with turbo settings for speed
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",  # Use latest small model for MD
    inference_settings="turbo_umas"  # Maximum speed for UMA-S
)

# Calculator for MD with multi-GPU
calc = FAIRChemCalculator(
    predictor,
    task_name="omat",
    workers=4  # Multi-GPU for large systems
)

# Large system
atoms = bulk("C", "diamond", a=3.57) * (10, 10, 10)
atoms.calc = calc

# Initialize velocities
MaxwellBoltzmannDistribution(atoms, temperature_K=300)

# Run NVT dynamics
dyn = Langevin(
    atoms,
    timestep=1.0 * units.fs,
    temperature_K=300,
    friction=0.002
)

# Run
from ase.io.trajectory import Trajectory
traj = Trajectory("md.traj", "w", atoms)
dyn.attach(traj.write, interval=10)
dyn.run(5000)
```

### Workflow 4: Molecular Systems

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import molecule
from ase.optimize import LBFGS

# Load model
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# Calculator for molecules
calc = FAIRChemCalculator(
    predictor,
    task_name="omol"  # Molecular domain
)

# Build molecule
mol = molecule("H2O")
mol.center(vacuum=10.0)

# Set spin and charge for omol (defaults: charge=0, spin=1)
mol.info.update({"spin": 1, "charge": 0})

mol.calc = calc

# Optimize
opt = LBFGS(mol, trajectory="mol_opt.traj")
opt.run(fmax=0.05)

# Get properties
E = mol.get_potential_energy()
forces = mol.get_forces()
```

### Workflow 5: NEB Calculations

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.neb import NEB
from ase.optimize import BFGS
from ase.io import read

# Load model
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# Calculator
calc = FAIRChemCalculator(
    predictor,
    task_name="oc20"
)

# Load initial and final states
initial = read("initial.traj")
final = read("final.traj")

# Create NEB
images = [initial]
images += [initial.copy() for i in range(5)]
images += [final]

neb = NEB(images)
neb.interpolate()

# Attach calculator to intermediate images
for image in images[1:-1]:
    image.calc = calc

# Optimize
opt = BFGS(neb, trajectory="neb.traj")
opt.run(fmax=0.05)

# Analyze
energies = [img.get_potential_energy() for img in images]
barrier = max(energies) - energies[0]
print(f"Barrier: {barrier:.3f} eV")
```

### Workflow 6: Formation Energy Calculation

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator

# FormationEnergyCalculator computes formation energies with optional corrections
from fairchem.core import FormationEnergyCalculator

predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")
calc = FormationEnergyCalculator(
    predictor,
    task_name="omat"
)

atoms.calc = calc
formation_energy = atoms.get_potential_energy()
```

**Warning**: UMA models use DFT/DFT+U total energy labels that are NOT compatible with Materials Project MP2020 corrections. Do not use MP2020 corrections with OMat24-trained models.

## Model Loading Options

### Load Pretrained UMA Model

```python
from fairchem.core import pretrained_mlip

# Standard loading
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# With turbo mode (faster, slight accuracy trade-off)
predictor = pretrained_mlip.get_predict_unit(
    "uma-m-1p1",
    inference_settings="turbo"
)

# UMA-S specific turbo (maximum speed with triton kernels)
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",
    inference_settings="turbo_umas"
)

# Specify device
predictor = pretrained_mlip.get_predict_unit(
    "uma-m-1p1",
    device="cuda:0"
)

# Load local checkpoint
predictor = pretrained_mlip.get_predict_unit(
    "/path/to/checkpoint.pt",
    device="cuda"
)
```

### Available Models

- `uma-s-1p2`: Small, fastest, improved accuracy (6.6M/290M params) — **recommended small model**
- `uma-s-1p1`: Small, fast (6.6M/150M params)
- `uma-m-1p1`: Medium, highest accuracy (50M/1.4B params)

## Task Selection Guide

| Domain | Task Name | Use For | Model Support |
|--------|-----------|---------|---------------|
| Catalysis | `oc20` | Surfaces + adsorbates | All models |
| Oxide Catalysis | `oc22` | Oxide surfaces | uma-s-1p2 only |
| Electrocatalysis | `oc25` | Electrochemical surfaces | uma-s-1p2 only |
| Materials | `omat` | Bulk crystals, defects | All models |
| Molecules | `omol` | Organic molecules, polymers | All models |
| MOFs | `odac` | Metal-organic frameworks | All models |
| Crystals | `omc` | Molecular crystals | All models |

## Performance Optimization

### Multi-GPU Inference

```python
# Use multiple GPUs automatically (requires fairchem-core[extras])
calc = FAIRChemCalculator(
    predictor,
    task_name="omat",
    workers=8  # Use 8 GPUs
)

# Achieves ~10× speedup on 8× H100 GPUs
# ~1 ns/day with 100k+ atom systems
```

### Turbo Mode

```python
# Standard turbo
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",
    inference_settings="turbo"
)

# UMA-S specific maximum speed (triton kernels)
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",
    inference_settings="turbo_umas"
)

# Good for:
# - MD simulations
# - Large systems
# - Initial screening
```

### Higher Precision

```python
import torch

# FP64 for higher precision calculations
predictor = pretrained_mlip.get_predict_unit(
    "uma-m-1p1",
    base_precision_dtype=torch.float64
)
```

### Hessian Calculation

```python
# Enable gradient-based Hessian computation
predictor = pretrained_mlip.get_predict_unit(
    "uma-m-1p1",
    predict_untrained_hessian=True
)
```

### Batch Predictions

```python
# For multiple similar calculations, iterate over structures
results = []
for atoms in [atoms1, atoms2, atoms3]:
    atoms.calc = calc
    results.append({
        'energy': atoms.get_potential_energy(),
        'forces': atoms.get_forces()
    })
```

## Best Practices

### 1. Task Selection
Always choose the appropriate task for your system:
- **Surfaces with adsorbates** → `oc20`
- **Oxide catalysis** → `oc22` (uma-s-1p2 only)
- **Electrocatalysis** → `oc25` (uma-s-1p2 only)
- **Bulk materials** → `omat`
- **Isolated molecules** → `omol`
- **MOFs** → `odac`
- **Molecular crystals** → `omc`

### 2. Model Selection
- **Initial screening**: Use `uma-s-1p2` + turbo_umas
- **Production calculations**: Use `uma-m-1p1`
- **Very large systems**: Use `uma-s-1p2` + workers
- **New tasks (oc22, oc25)**: Must use `uma-s-1p2`

### 3. Spin and Charge for Molecules
When using `omol` task, set spin and charge via `atoms.info`:
```python
atoms.info.update({"spin": 1, "charge": 0})  # defaults
```

### 4. Validation
ML models have different error characteristics than DFT:
```python
# Always validate critical results
# Compare ML prediction with DFT for representative cases
ml_energy = atoms.get_potential_energy()  # FAIRChem
atoms.calc = Vasp(...)  # Switch to DFT
dft_energy = atoms.get_potential_energy()
error = abs(ml_energy - dft_energy)
```

### 5. Energy Label Compatibility
UMA models trained on OMat24 use DFT/DFT+U total energy labels. These are NOT compatible with Materials Project MP2020 corrections. Do not mix.

### 6. Memory Management
For large systems:
```python
# Use latest small model with turbo
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",
    inference_settings="turbo_umas"
)

# Distribute across GPUs
calc = FAIRChemCalculator(
    predictor,
    task_name="omat",
    workers=4
)
```

## Common Patterns

### Energy Calculation

```python
atoms.calc = calc
energy = atoms.get_potential_energy()  # eV
forces = atoms.get_forces()  # eV/Å
stress = atoms.get_stress()  # eV/Å³
```

### Geometry Optimization

```python
from ase.optimize import LBFGS, FIRE, BFGS

# Fast convergence
opt = LBFGS(atoms, trajectory="opt.traj")
opt.run(fmax=0.05)

# For difficult systems
opt = FIRE(atoms)
opt.run(fmax=0.05)
```

### Cell Optimization

```python
from ase.filters import FrechetCellFilter

# Optimize both atoms and cell
ucf = FrechetCellFilter(atoms)
opt = FIRE(ucf)
opt.run(fmax=0.05)
```

## Integration with ASE

FAIRChemCalculator is a full ASE calculator:

```python
# All ASE functionality works
from ase.vibrations import Vibrations
from ase.thermochemistry import IdealGasThermo
from ase.eos import calculate_eos

# Vibrational analysis
vib = Vibrations(atoms)
vib.run()

# Thermochemistry
thermo = IdealGasThermo(...)

# Equation of state
eos = calculate_eos(atoms)
```

## LAMMPS Integration

For very large-scale MD simulations, FAIRChem supports LAMMPS integration with multi-GPU support. This is recommended for systems with 100k+ atoms.

## Troubleshooting

### Hugging Face Authentication

```bash
# Login to Hugging Face
huggingface-cli login

# Request access to UMA models at:
# https://huggingface.co/facebook/UMA
```

### GPU Memory Issues

```python
# Use smaller model
predictor = pretrained_mlip.get_predict_unit("uma-s-1p2")

# Use turbo mode
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",
    inference_settings="turbo_umas"
)

# Distribute across GPUs
calc = FAIRChemCalculator(predictor, task_name="omat", workers=4)
```

### Slow Inference

```python
# Enable turbo mode
inference_settings="turbo_umas"  # For UMA-S models

# Use multiple GPUs
workers=N

# Use latest small model
"uma-s-1p2"
```

### Wrong Task Selection

```python
# Symptoms: Poor predictions, unphysical results
# Solution: Verify task matches your system

# For surfaces + adsorbates:
task_name="oc20"  # NOT "omat" or "omol"

# For bulk materials:
task_name="omat"  # NOT "oc20"
```

## Version Compatibility

**Important**: FAIRChem v2 is a breaking change from v1
- v2 code is NOT compatible with v1 models
- v1 code is NOT compatible with v2 models
- UMA models require FAIRChem >= 2.0
- For v1 compatibility: `pip install fairchem-core==1.10.0`

```python
# Check version
import fairchem
print(fairchem.__version__)  # Should be >= 2.0 for UMA
```

## Comparison with DFT

| Aspect | FAIRChem | DFT |
|--------|----------|-----|
| Speed | 100-1000× faster | Slower |
| Accuracy | ~0.1 eV | Reference |
| Scaling | Linear, multi-GPU | Cubic |
| System size | 1000s of atoms | 10-100s atoms |
| Use case | Screening, MD | High accuracy |

## When to Use FAIRChem vs DFT

**Use FAIRChem for:**
- Initial screening of many structures
- Long MD simulations
- Large systems (>500 atoms)
- Rapid prototyping
- High-throughput workflows

**Use DFT for:**
- Final validation
- Novel chemistries outside training data
- When highest accuracy needed
- Electronic structure analysis
- Magnetic properties

## Resources

When suggesting FAIRChem solutions:
- Specify correct task_name for the domain
- Recommend appropriate model (s-1p2 vs m-1p1)
- Suggest performance optimizations (turbo_umas, workers)
- Include validation against known results
- Mention Hugging Face authentication requirement
- Provide complete working examples
- Note v2 compatibility requirements
- Set spin/charge for omol calculations

## Example Response Pattern

When helping with FAIRChem:
1. Identify the chemistry domain (catalysis, materials, molecules, etc.)
2. Select appropriate task_name
3. Choose model based on accuracy/speed requirements
4. Provide complete code with imports
5. Suggest performance optimizations if needed
6. Recommend validation steps
7. Note any domain-specific considerations (spin/charge for omol, energy labels for omat)
