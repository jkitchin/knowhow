# FAIRChem Quick Reference

## Installation

```bash
pip install fairchem-core
pip install fairchem-core[gpu]     # For GPU support
pip install fairchem-core[extras]  # For multi-GPU (Ray)

# Required: Hugging Face authentication
pip install huggingface-hub
huggingface-cli login
```

## Model Loading

```python
from fairchem.core import pretrained_mlip

# Standard loading
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# Latest small model (recommended for speed)
predictor = pretrained_mlip.get_predict_unit("uma-s-1p2")

# Turbo mode (faster inference)
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",
    inference_settings="turbo"
)

# UMA-S maximum speed (triton kernels)
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2",
    inference_settings="turbo_umas"
)

# Specify GPU
predictor = pretrained_mlip.get_predict_unit(
    "uma-m-1p1",
    device="cuda:0"
)

# Higher precision
import torch
predictor = pretrained_mlip.get_predict_unit(
    "uma-m-1p1",
    base_precision_dtype=torch.float64
)

# Load local checkpoint
predictor = pretrained_mlip.get_predict_unit(
    "/path/to/checkpoint.pt"
)
```

## Calculator Setup

```python
from fairchem.core import FAIRChemCalculator

# Basic calculator
calc = FAIRChemCalculator(
    predictor,
    task_name="oc20"  # Choose task
)

# Multi-GPU (requires fairchem-core[extras])
calc = FAIRChemCalculator(
    predictor,
    task_name="omat",
    workers=4  # Use 4 GPUs
)

# Convenience one-step method
calc = FAIRChemCalculator.from_model_checkpoint(
    "uma-m-1p1",
    task_name="omat",
    inference_settings="turbo"
)
```

## Available Models

| Model | Parameters | Speed | Accuracy | Notes |
|-------|-----------|-------|----------|-------|
| `uma-s-1p2` | 6.6M/290M | Fastest | Good | **Recommended small**, supports oc22/oc25 |
| `uma-s-1p1` | 6.6M/150M | Fast | Good | Previous generation |
| `uma-m-1p1` | 50M/1.4B | Slower | Best | Highest accuracy |

## Task Selection

| Task Name | Domain | Use For | Model Support |
|-----------|--------|---------|---------------|
| `oc20` | Catalysis | Surfaces + adsorbates | All |
| `oc22` | Oxide catalysis | Oxide surfaces | uma-s-1p2 only |
| `oc25` | Electrocatalysis | Electrochemical surfaces | uma-s-1p2 only |
| `omat` | Materials | Bulk crystals, defects | All |
| `omol` | Molecules | Organic chemistry, polymers | All |
| `odac` | MOFs | Metal-organic frameworks | All |
| `omc` | Molecular crystals | Ice, organic crystals | All |

## Basic Usage Patterns

### Energy Calculation

```python
atoms.calc = calc
energy = atoms.get_potential_energy()  # eV
forces = atoms.get_forces()            # eV/Å
stress = atoms.get_stress()            # eV/Å³
```

### Geometry Optimization

```python
from ase.optimize import LBFGS, FIRE

# LBFGS (fast convergence)
opt = LBFGS(atoms, trajectory="opt.traj")
opt.run(fmax=0.05)

# FIRE (robust for difficult systems)
opt = FIRE(atoms, trajectory="opt.traj")
opt.run(fmax=0.05)
```

### Cell Optimization (Lattice Parameters)

```python
from ase.filters import FrechetCellFilter
from ase.optimize import FIRE

# Optimize both positions and cell
ucf = FrechetCellFilter(atoms)
opt = FIRE(ucf)
opt.run(fmax=0.05)
```

## Domain-Specific Examples

### Catalysis (oc20)

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import fcc111, add_adsorbate
from ase.optimize import LBFGS
from ase.constraints import FixAtoms

# Setup
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")
calc = FAIRChemCalculator(predictor, task_name="oc20")

# Build slab
slab = fcc111("Pt", size=(4, 4, 4), vacuum=10.0)
add_adsorbate(slab, "O", height=2.0, position="fcc")

# Fix bottom layers
n_atoms_per_layer = 16
constraint = FixAtoms(indices=range(n_atoms_per_layer * 2))
slab.set_constraint(constraint)

# Optimize
slab.calc = calc
opt = LBFGS(slab)
opt.run(fmax=0.05)
```

### Bulk Materials (omat)

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import bulk
from ase.optimize import FIRE
from ase.filters import FrechetCellFilter

# Setup
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")
calc = FAIRChemCalculator(predictor, task_name="omat")

# Build bulk
atoms = bulk("Fe", "bcc", a=2.87)
atoms.calc = calc

# Optimize structure and cell
ucf = FrechetCellFilter(atoms)
opt = FIRE(ucf)
opt.run(fmax=0.05)
```

### Molecules (omol)

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import molecule
from ase.optimize import LBFGS

# Setup
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")
calc = FAIRChemCalculator(predictor, task_name="omol")

# Build molecule
mol = molecule("H2O")
mol.center(vacuum=10.0)

# Set spin and charge for omol (defaults: charge=0, spin=1)
mol.info.update({"spin": 1, "charge": 0})

mol.calc = calc

# Optimize
opt = LBFGS(mol)
opt.run(fmax=0.05)
```

### Molecular Dynamics

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.langevin import Langevin
from ase import units
from ase.io.trajectory import Trajectory

# Setup with turbo_umas for maximum speed
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2", inference_settings="turbo_umas"
)
calc = FAIRChemCalculator(
    predictor,
    task_name="omat",
    workers=4  # Multi-GPU
)

# Attach calculator
atoms.calc = calc

# Initialize velocities
MaxwellBoltzmannDistribution(atoms, temperature_K=300)

# NVT dynamics
dyn = Langevin(
    atoms,
    timestep=1.0 * units.fs,
    temperature_K=300,
    friction=0.002
)

# Run with trajectory
traj = Trajectory("md.traj", "w", atoms)
dyn.attach(traj.write, interval=10)
dyn.run(5000)
```

### NEB (Reaction Barriers)

```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.neb import NEB
from ase.optimize import BFGS
from ase.io import read

# Setup
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")
calc = FAIRChemCalculator(predictor, task_name="oc20")

# Load states
initial = read("initial.traj")
final = read("final.traj")

# Create NEB
images = [initial]
images += [initial.copy() for i in range(5)]  # 5 intermediate images
images += [final]

neb = NEB(images)
neb.interpolate()

# Attach calculator
for img in images[1:-1]:
    img.calc = calc

# Optimize
opt = BFGS(neb, trajectory="neb.traj")
opt.run(fmax=0.05)

# Get barrier
energies = [img.get_potential_energy() for img in images]
barrier = max(energies) - energies[0]
```

## Performance Optimization

### Model Selection

```python
# For screening/MD (maximum speed)
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2", inference_settings="turbo_umas"
)

# For production (highest accuracy)
predictor = pretrained_mlip.get_predict_unit("uma-m-1p1")

# For very large systems
predictor = pretrained_mlip.get_predict_unit("uma-s-1p2")
calc = FAIRChemCalculator(predictor, ..., workers=8)
```

### Multi-GPU Setup

```python
# Automatic distribution across GPUs (requires fairchem-core[extras])
calc = FAIRChemCalculator(
    predictor,
    task_name="omat",
    workers=8  # Number of GPUs/processes
)

# Speedup: ~10× on 8× H100 GPUs
# ~1 ns/day with 100k+ atom systems
```

### Inference Settings

| Setting | Speed | Accuracy | Notes |
|---------|-------|----------|-------|
| `"default"` | Baseline | Best | Standard inference |
| `"turbo"` | Faster | Slightly reduced | General turbo mode |
| `"turbo_umas"` | Fastest | Slightly reduced | UMA-S only, triton kernels |

## Common Workflows

### Adsorption Energy

```python
# 1. Clean surface
slab = fcc111("Pt", size=(4, 4, 4), vacuum=10.0)
slab.calc = calc
E_slab = slab.get_potential_energy()

# 2. Surface + adsorbate
add_adsorbate(slab, "O", height=2.0)
slab.calc = calc
E_slab_ads = slab.get_potential_energy()

# 3. Isolated adsorbate
from ase import Atoms
ads = Atoms("O", positions=[(0, 0, 0)])
ads.center(vacuum=10.0)
ads.calc = calc
E_ads = ads.get_potential_energy()

# 4. Adsorption energy
E_adsorption = E_slab_ads - E_slab - E_ads
```

### Lattice Constant Scan

```python
import numpy as np

a_values = np.linspace(2.8, 3.0, 10)
energies = []

for a in a_values:
    atoms = bulk("Fe", "bcc", a=a)
    atoms.calc = calc
    energies.append(atoms.get_potential_energy())

# Find minimum
opt_a = a_values[np.argmin(energies)]
```

### Equation of State

```python
from ase.eos import calculate_eos

atoms = bulk("Cu", "fcc", a=3.6)
atoms.calc = calc

eos = calculate_eos(atoms, trajectory="eos.traj")
v0, e0, B = eos.fit()  # optimal volume, energy, bulk modulus

print(f"Bulk modulus: {B / 1e9:.2f} GPa")
```

## Troubleshooting

### Hugging Face Login

```bash
# If authentication fails
huggingface-cli logout
huggingface-cli login

# Request access at:
# https://huggingface.co/facebook/UMA
```

### GPU Memory Issues

```python
# Use smaller model
predictor = pretrained_mlip.get_predict_unit("uma-s-1p2")

# Enable turbo
predictor = pretrained_mlip.get_predict_unit(
    "uma-s-1p2", inference_settings="turbo_umas"
)

# Reduce system size or use multi-GPU
calc = FAIRChemCalculator(predictor, ..., workers=4)
```

### Wrong Task Selection

```python
# Symptoms: Poor predictions, unphysical results

# Fix: Match task to system type
# Surfaces + adsorbates → task_name="oc20"
# Oxide catalysis → task_name="oc22" (uma-s-1p2 only)
# Electrocatalysis → task_name="oc25" (uma-s-1p2 only)
# Bulk materials → task_name="omat"
# Molecules → task_name="omol"
# MOFs → task_name="odac"
# Molecular crystals → task_name="omc"
```

### Energy Label Warning

UMA models use DFT/DFT+U total energy labels NOT compatible with Materials Project MP2020 corrections. Do not mix OMat24-trained model energies with MP correction schemes.

## Model Recommendations

| Use Case | Model | Settings | Workers |
|----------|-------|----------|---------|
| Screening | uma-s-1p2 | turbo_umas | 1-4 |
| Production | uma-m-1p1 | default | 1-2 |
| MD (small) | uma-s-1p2 | turbo_umas | 1 |
| MD (large) | uma-s-1p2 | turbo_umas | 4-8 |
| Validation | uma-m-1p1 | default | 1 |
| Oxide catalysis | uma-s-1p2 | turbo | 1-4 |

## Speed Comparison

| System Size | DFT (VASP) | FAIRChem (CPU) | FAIRChem (GPU) |
|-------------|------------|----------------|----------------|
| 100 atoms | 1-10 hours | 1-5 minutes | 10-30 seconds |
| 500 atoms | Days | 5-15 minutes | 1-2 minutes |
| 2000 atoms | N/A | 30-60 minutes | 5-10 minutes |

## Version Check

```python
import fairchem
print(fairchem.__version__)  # Should be >= 2.0 for UMA

import ase
print(ase.__version__)  # Should be >= 3.22
```

## Common Errors

### Version Mismatch
```
Error: fairchem v2 required
Solution: pip install --upgrade fairchem-core
```

### Hugging Face Access
```
Error: Access denied to model repository
Solution: Request access at huggingface.co/facebook/UMA, then login
```

### GPU Out of Memory
```
Error: CUDA out of memory
Solution: Use turbo_umas mode, smaller model, or multi-GPU
```

### Wrong Task
```
Error: Poor predictions / unphysical results
Solution: Check task_name matches your system type
```
