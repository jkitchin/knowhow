---
name: python-ase
description: Expert assistance with the Atomic Simulation Environment (ASE) Python library for atomistic simulations, including structure building, calculator setup, optimization, dynamics, and analysis
allowed-tools: ["*"]
---

# Python ASE (Atomic Simulation Environment) Skill

This skill provides expert guidance for working with the Atomic Simulation Environment (ASE), a Python library for setting up, manipulating, running, visualizing, and analyzing atomistic simulations.

## When to Use This Skill

Use this skill when:
- Building atomic structures (molecules, surfaces, bulk crystals, nanoparticles)
- Setting up and running DFT calculations (VASP, GPAW, Quantum ESPRESSO, etc.)
- Performing geometry optimizations or molecular dynamics
- Analyzing trajectories and simulation results
- Working with ASE Atoms objects and calculators
- Converting between different structure formats
- Calculating properties (energies, forces, stress, bands, DOS)
- Writing automation scripts for materials simulations

## Core ASE Concepts

### 1. Atoms Objects
The fundamental ASE object representing atomic structures:
- Contains atomic positions, cell parameters, periodic boundary conditions
- Can be modified, visualized, and used with calculators
- Supports constraints for selective dynamics

### 2. Calculators
Interface to quantum chemistry and materials science codes:
- EMT (Effective Medium Theory) - fast, for testing
- VASP - plane-wave DFT
- GPAW - real-space/plane-wave DFT
- Quantum ESPRESSO, CASTEP, NWChem, etc.
- Must be attached to Atoms objects: `atoms.calc = calculator`

### 3. Optimizers
Geometry optimization algorithms:
- BFGS, LBFGS - quasi-Newton methods
- FIRE - fast inertial relaxation
- MDMin - molecular dynamics minimization

### 4. Dynamics
Molecular dynamics simulations:
- VelocityVerlet - NVE ensemble
- Langevin - NVT with friction
- NPT - constant pressure and temperature

## Common Patterns and Workflows

### Building Structures

```python
from ase import Atoms
from ase.build import bulk, molecule, surface, add_adsorbate

# Bulk crystals
atoms = bulk('Cu', 'fcc', a=3.6)
atoms = bulk('Si', 'diamond', a=5.43)

# Molecules
atoms = molecule('H2O')
atoms = molecule('CH4')

# Surfaces
slab = surface('Au', (1, 1, 1), size=(4, 4, 4), vacuum=10.0)

# Add adsorbate to surface
add_adsorbate(slab, 'O', height=1.5, position='fcc')
```

### Setting Up Calculators

```python
# EMT calculator (for testing)
from ase.calculators.emt import EMT
atoms.calc = EMT()

# VASP calculator
from ase.calculators.vasp import Vasp
calc = Vasp(
    xc='PBE',
    encut=400,
    kpts=(4, 4, 4),
    ismear=1,
    sigma=0.1,
    ibrion=2,
    nsw=100,
    ediff=1e-5,
)
atoms.calc = calc

# GPAW calculator
from gpaw import GPAW, PW
calc = GPAW(
    mode=PW(400),
    xc='PBE',
    kpts=(4, 4, 4),
    txt='output.txt'
)
atoms.calc = calc
```

### Geometry Optimization

```python
from ase.optimize import BFGS, LBFGS, FIRE

# Basic optimization
opt = BFGS(atoms, trajectory='opt.traj')
opt.run(fmax=0.05)  # converge until forces < 0.05 eV/Å

# With constraints (fix bottom layers)
from ase.constraints import FixAtoms
mask = [atom.position[2] < 10.0 for atom in atoms]
atoms.set_constraint(FixAtoms(mask=mask))
opt = BFGS(atoms)
opt.run(fmax=0.05)

# Log optimization progress
opt = BFGS(atoms, logfile='opt.log', trajectory='opt.traj')
opt.run(fmax=0.01, steps=100)
```

### Molecular Dynamics

```python
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.langevin import Langevin
from ase import units

# Set initial velocities
MaxwellBoltzmannDistribution(atoms, temperature_K=300)

# NVT dynamics with Langevin thermostat
dyn = Langevin(
    atoms,
    timestep=1.0 * units.fs,
    temperature_K=300,
    friction=0.002
)

# Run with trajectory output
from ase.io.trajectory import Trajectory
traj = Trajectory('md.traj', 'w', atoms)
dyn.attach(traj.write, interval=10)
dyn.run(5000)  # 5000 steps
```

### Analyzing Results

```python
from ase.io import read, write

# Read trajectory
traj = read('opt.traj', ':')  # ':' reads all frames
final = traj[-1]  # last frame

# Extract energies
energies = [atoms.get_potential_energy() for atoms in traj]

# Analyze forces
forces = final.get_forces()
max_force = max(np.linalg.norm(forces, axis=1))

# Calculate distances
from ase.geometry import get_distances
d = atoms.get_distance(0, 1)  # distance between atoms 0 and 1

# Write to various formats
write('structure.cif', atoms)
write('structure.xyz', atoms)
write('POSCAR', atoms)  # VASP format
```

### Band Structure Calculations

```python
from ase.dft.kpoints import bandpath

# Get high-symmetry k-point path
atoms = bulk('Si', 'diamond', a=5.43)
path = atoms.cell.bandpath('GXWLG', npoints=100)

# Calculate bands (example with GPAW)
calc = GPAW(
    mode=PW(400),
    xc='PBE',
    kpts={'path': path, 'density': 10}
)
atoms.calc = calc
atoms.get_potential_energy()  # run calculation

# Plot bands
bs = calc.band_structure()
bs.plot(filename='bands.png', show=True)
```

## Best Practices

### 1. Structure Validation
Always check your structure before running expensive calculations:
```python
# Visualize structure
from ase.visualize import view
view(atoms)  # requires GUI

# Check for overlapping atoms
from ase.geometry import get_distances
distances = get_distances(atoms.positions)[1]
min_distance = distances[distances > 0].min()
print(f"Minimum distance: {min_distance:.3f} Å")

# Verify cell and PBC
print(f"Cell: {atoms.cell}")
print(f"PBC: {atoms.pbc}")
```

### 2. Calculator Management
```python
# Always attach calculator before accessing properties
if atoms.calc is None:
    raise RuntimeError("No calculator attached")

# Reuse calculator for multiple structures
calc = Vasp(xc='PBE', encut=400)
for structure in structures:
    structure.calc = calc
    energy = structure.get_potential_energy()
```

### 3. Error Handling
```python
from ase.calculators.calculator import CalculationFailed

try:
    energy = atoms.get_potential_energy()
except CalculationFailed as e:
    print(f"Calculation failed: {e}")
    # Handle error or retry with different parameters
```

### 4. Performance Tips
```python
# Use trajectory files efficiently
from ase.io import read
# Don't read entire trajectory if you only need specific frames
last_frame = read('md.traj', -1)  # only last frame
every_10th = read('md.traj', '::10')  # every 10th frame

# For VASP: use selective dynamics for large systems
from ase.constraints import FixAtoms
# Fix bulk atoms, only relax surface/adsorbate
```

## Common Workflows

### Workflow 1: Surface Adsorption Energy

```python
from ase.build import fcc111, add_adsorbate
from ase.optimize import BFGS

# 1. Create and optimize clean surface
slab = fcc111('Pt', size=(4, 4, 4), vacuum=10.0)
slab.calc = EMT()
opt = BFGS(slab)
opt.run(fmax=0.05)
E_slab = slab.get_potential_energy()

# 2. Add adsorbate and optimize
add_adsorbate(slab, 'O', height=2.0, position='fcc')
opt = BFGS(slab)
opt.run(fmax=0.05)
E_slab_ads = slab.get_potential_energy()

# 3. Calculate isolated adsorbate energy
from ase import Atoms
adsorbate = Atoms('O', positions=[(0, 0, 0)])
adsorbate.center(vacuum=10.0)
adsorbate.calc = EMT()
E_ads = adsorbate.get_potential_energy()

# 4. Adsorption energy
E_adsorption = E_slab_ads - E_slab - E_ads
print(f"Adsorption energy: {E_adsorption:.3f} eV")
```

### Workflow 2: Lattice Constant Optimization

```python
from ase.build import bulk
from ase.eos import calculate_eos
import numpy as np

atoms = bulk('Cu', 'fcc', a=3.6)
atoms.calc = EMT()

# Method 1: Manual scan
cell_params = np.linspace(3.4, 3.8, 10)
energies = []
for a in cell_params:
    atoms = bulk('Cu', 'fcc', a=a)
    atoms.calc = EMT()
    energies.append(atoms.get_potential_energy())

# Method 2: Using EOS
eos = calculate_eos(atoms, trajectory='eos.traj')
v, e, B = eos.fit()  # volume, energy, bulk modulus
eos.plot('eos.png')
```

### Workflow 3: Nudged Elastic Band (NEB)

```python
from ase.neb import NEB
from ase.optimize import BFGS

# Initial and final states
initial = read('initial.traj')
final = read('final.traj')

# Create intermediate images
images = [initial]
images += [initial.copy() for i in range(5)]  # 5 intermediate images
images += [final]

# Interpolate
neb = NEB(images)
neb.interpolate()

# Set calculator for intermediate images
for image in images[1:-1]:
    image.calc = EMT()

# Optimize
opt = BFGS(neb, trajectory='neb.traj')
opt.run(fmax=0.05)

# Get barrier
energies = [image.get_potential_energy() for image in images]
barrier = max(energies) - energies[0]
print(f"Activation barrier: {barrier:.3f} eV")
```

## Debugging Tips

### Check calculation status
```python
# Did calculation run?
print(atoms.calc.get_property('energy', atoms))

# Check forces
print(atoms.get_forces())

# Verify calculator parameters
print(atoms.calc.parameters)
```

### Visualization debugging
```python
# Quick plot without GUI
from ase.io import write
write('temp.png', atoms, rotation='10x,10y,10z')

# Check trajectory
traj = read('opt.traj', ':')
print(f"Number of steps: {len(traj)}")
for i, atoms in enumerate(traj):
    print(f"Step {i}: E = {atoms.get_potential_energy():.3f} eV")
```

## Important Notes

1. **Units**: ASE uses eV for energy, Å for length, and eV/Å for forces by default
2. **PBC**: Always set periodic boundary conditions correctly: `atoms.pbc = [True, True, False]`
3. **Vacuum**: For surfaces/molecules, add sufficient vacuum (typically 10-15 Å)
4. **k-points**: Increase k-point density for accurate total energies; fewer k-points OK for geometry optimization
5. **Convergence**: Test encut/k-points convergence for production calculations
6. **Constraints**: Remember to fix appropriate atoms (e.g., bottom layers of slabs)

## Resources

When suggesting ASE solutions:
- Reference official ASE documentation for specific modules
- Show complete, runnable examples
- Include appropriate error handling
- Mention calculator-specific requirements (VASP POTCAR files, GPAW setups, etc.)
- Suggest convergence testing for critical parameters
- Recommend visualization checks before expensive calculations

## Example Response Pattern

When helping with ASE:
1. Understand the specific task (structure building, calculation setup, analysis)
2. Provide complete code example with imports
3. Explain key parameters and their typical values
4. Suggest validation/checking steps
5. Mention common pitfalls for that task
6. Recommend convergence tests if applicable
