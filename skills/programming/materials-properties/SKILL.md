---
name: materials-properties
description: Expert assistant for calculating materials properties from first-principles using ASE - structure relaxation, surface energies, adsorption, reaction barriers, phonons, elastic constants, and thermodynamic modeling with proper scientific methodology
allowed-tools: ["*"]
---

# Materials Properties Calculation Skill

You are an expert assistant for calculating materials properties from first-principles using the Atomic Simulation Environment (ASE) and specialized packages. Help users perform structure relaxations, compute ground state properties, and calculate advanced materials properties using scientifically rigorous methods with proper citations.

## Overview

This skill covers comprehensive materials property calculations including:

**Core Capabilities:**
- Structure relaxation (geometry optimization, stress relaxation)
- Ground state properties (lattice constants, space groups, crystal structure)
- Calculator setup (EMT, GPAW, VASP, Quantum ESPRESSO)

**Advanced Properties:**
- Surface energies
- Adsorption energies
- Reaction barriers (NEB)
- Vibrational analysis
- Phonon calculations (phonopy)
- Elastic constants (elastic)
- Cluster expansions (icet)
- CALPHAD integration (pycalphad)
- Defect formation energies
- Interface/grain boundary energies
- Magnetic properties
- Thermal expansion
- Electronic structure

## Installation

```bash
# Core packages
pip install ase spglib matplotlib

# Specialized packages
pip install phonopy elastic icet pycalphad

# Optional DFT calculators
pip install gpaw  # Real DFT (requires compilation)
# VASP requires separate license and installation
# Quantum ESPRESSO via ase.calculators.espresso
```

## Core Workflow: Structure Relaxation

### 1. Basic Geometry Optimization

```python
from ase import Atoms
from ase.optimize import BFGS
from ase.calculators.emt import EMT

# Create or load structure
atoms = Atoms('Cu', positions=[[0, 0, 0]], cell=[2.5, 2.5, 2.5], pbc=True)

# Set calculator
atoms.calc = EMT()

# Optimize geometry
opt = BFGS(atoms, trajectory='opt.traj')
opt.run(fmax=0.01)  # Force convergence criterion

# Get optimized energy
E_opt = atoms.get_potential_energy()
print(f"Optimized energy: {E_opt:.3f} eV")
```

**Key Parameters:**
- `fmax`: Maximum force (eV/Å) - typical values: 0.01-0.05
- `steps`: Maximum optimization steps
- Optimizers: BFGS, LBFGS, FIRE, GPMin

### 2. Unit Cell Optimization (Stress Relaxation)

```python
from ase.optimize import BFGS
from ase.constraints import ExpCellFilter

# Relax both positions and cell
ecf = ExpCellFilter(atoms)
opt = BFGS(ecf, trajectory='cell_opt.traj')
opt.run(fmax=0.01)

# Get optimized lattice
a = atoms.cell.cellpar()[0]
print(f"Optimized lattice constant: {a:.3f} Å")
```

**Applications:**
- Lattice constant determination
- Equation of state calculations
- Pressure-dependent structures

### 3. Ground State Properties

```python
import spglib

# Get space group
cell = (atoms.cell, atoms.get_scaled_positions(), atoms.get_atomic_numbers())
spacegroup = spglib.get_spacegroup(cell, symprec=1e-5)
print(f"Space group: {spacegroup}")

# Get lattice parameters
a, b, c, alpha, beta, gamma = atoms.cell.cellpar()
print(f"Lattice: a={a:.3f}, b={b:.3f}, c={c:.3f} Å")
print(f"Angles: α={alpha:.1f}, β={beta:.1f}, γ={gamma:.1f}°")

# Volume
V = atoms.get_volume()
print(f"Volume: {V:.3f} ų")

# Crystal system
dataset = spglib.get_symmetry_dataset(cell)
print(f"Crystal system: {dataset['international']}")
```

## Calculator Setup

### EMT Calculator (Fast, for Testing)

```python
from ase.calculators.emt import EMT

atoms.calc = EMT()
```

**Advantages:**
- Very fast
- No installation issues
- Good for workflow development

**Limitations:**
- Only works for a few elements (Cu, Ag, Au, Ni, Pd, Pt, Al, Pb, Fe)
- Approximate potential

### GPAW Calculator (Real DFT)

```python
from gpaw import GPAW, PW

atoms.calc = GPAW(mode=PW(500),  # Plane-wave cutoff (eV)
                 xc='PBE',       # Exchange-correlation functional
                 kpts=(8, 8, 8), # k-point sampling
                 txt='gpaw.txt') # Output file
```

**Parameters:**
- `mode`: PW(cutoff) for plane waves, grid-based for real-space
- `xc`: PBE, LDA, RPBE, BEEF-vdW, etc.
- `kpts`: k-point mesh or specific k-points
- `convergence`: Energy convergence criterion

### VASP Calculator

```python
from ase.calculators.vasp import Vasp

atoms.calc = Vasp(xc='PBE',
                 encut=500,     # Cutoff energy (eV)
                 kpts=(8,8,8),
                 ismear=1,      # Smearing method
                 sigma=0.1)     # Smearing width
```

**VASP-specific:**
- Requires VASP license
- Uses POTCAR files for pseudopotentials
- See `references/calculator_setup.md` for details

## Advanced Properties (Subskills)

### 1. Surface Energy

**Method**: Slab model approach

**Formula**:
```
γ = (E_slab - N × E_bulk) / (2 × A)
```

Where:
- E_slab: Energy of slab with surfaces
- E_bulk: Bulk energy per atom
- N: Number of atoms in slab
- A: Surface area
- Factor of 2: Two equivalent surfaces

**Workflow**:
1. Optimize bulk structure
2. Create slab with `ase.build.surface()`
3. Add vacuum layer
4. Relax slab (constrain bottom layers)
5. Calculate surface energy

**See**: `references/surface_energy.md` for detailed methods

**Key References**:
- Fiorentini & Methfessel, "Extracting convergent surface energies," *J. Phys.: Condens. Matter* **8**, 6525 (1996)
- Tran et al., "Surface energies of elemental crystals," *Sci. Data* **3**, 160080 (2016)

### 2. Adsorption Energy

**Method**: Compare slab+adsorbate to separated systems

**Formula**:
```
E_ads = E_slab+ads - E_slab - E_molecule
```

More negative = stronger adsorption

**Workflow**:
1. Optimize clean slab
2. Add adsorbate at different sites (top, bridge, hollow)
3. Relax adsorbed structure
4. Calculate adsorption energy
5. Compare sites to find preferred adsorption

**See**: `references/adsorption_energy.md`

**Key References**:
- Hammer & Nørskov, "Theoretical surface science," *Adv. Catal.* **45**, 71 (2000)
- Nørskov et al., "Computational design of solid catalysts," *Nature Chem.* **1**, 37 (2009)

### 3. Reaction Barriers (Nudged Elastic Band)

**Method**: Find minimum energy path between reactant and product

**Workflow**:
```python
from ase.neb import NEB
from ase.optimize import BFGS

# Create images interpolating between initial and final
images = [initial]
images += [initial.copy() for i in range(5)]  # 5 intermediate images
images += [final]

# Interpolate
neb = NEB(images)
neb.interpolate()

# Set calculators
for image in images[1:-1]:
    image.calc = EMT()

# Optimize NEB
optimizer = BFGS(neb, trajectory='neb.traj')
optimizer.run(fmax=0.05)

# Extract barrier
from ase.neb import NEBTools
nebtools = NEBTools(images)
barrier = nebtools.get_barrier()[0]
print(f"Activation barrier: {barrier:.2f} eV")
```

**See**: `references/reaction_barriers.md`

**Key References**:
- Henkelman, Uberuaga & Jónsson, "Climbing image NEB," *J. Chem. Phys.* **113**, 9901 (2000)
- Sheppard et al., "Optimization methods for MEPs," *J. Chem. Phys.* **128**, 134106 (2008)

### 4. Vibrational Analysis

**Method**: Finite displacement or DFPT

**Workflow**:
```python
from ase.vibrations import Vibrations

# Calculate vibrations
vib = Vibrations(atoms)
vib.run()

# Get frequencies
vib.summary()

# Zero-point energy
zpe = vib.get_zero_point_energy()
```

**See**: `references/vibrational_analysis.md`

**Key References**:
- Wilson, Decius & Cross, *Molecular Vibrations* (Dover, 1980)

### 5. Phonon Calculations (phonopy)

**Method**: Supercell approach with force constants

**Workflow**:
```python
from phonopy import Phonopy

# Create phonopy object
phonon = Phonopy(atoms, supercell_matrix=[[2,0,0],[0,2,0],[0,0,2]])

# Generate displacements
phonon.generate_displacements(distance=0.01)
supercells = phonon.supercells_with_displacements

# Calculate forces for each displacement
for scell in supercells:
    scell.calc = calc
    forces = scell.get_forces()
    # Set forces back to phonopy

# Calculate phonon properties
phonon.produce_force_constants()
phonon.auto_band_structure()
phonon.plot_band_structure()
```

**Applications**:
- Phonon band structure
- Phonon density of states
- Thermal properties (heat capacity, free energy)
- Thermodynamic integration

**See**: `references/phonons.md`

**Key References**:
- Togo & Tanaka, "First principles phonon calculations," *Scr. Mater.* **108**, 1 (2015)
- Togo, "Phonopy and Phono3py," *J. Phys. Soc. Jpn.* **92**, 012001 (2023)

### 6. Elastic Constants (elastic package)

**Method**: Apply strain, measure stress

**Properties Calculated**:
- Full elastic tensor (Cij)
- Bulk modulus (K)
- Shear modulus (G)
- Young's modulus (E)
- Poisson's ratio (ν)
- Sound velocities
- Debye temperature

**See**: `references/elastic_constants.md`

**Key References**:
- Golesorkhtabar et al., "ElaStic tool," *Comput. Phys. Commun.* **184**, 1861 (2013)
- Nye, *Physical Properties of Crystals* (Oxford, 1985)

### 7. Equation of State

**Method**: Volume-energy curve fitting

**Workflow**:
```python
from ase.eos import calculate_eos

eos = calculate_eos(atoms, trajectory='eos.traj')
v, e, B = eos.fit()  # Volume, energy, bulk modulus
eos.plot('eos.png')
```

**EOS Types**:
- Birch-Murnaghan
- Murnaghan
- Vinet

**See**: `references/equation_of_state.md`

**Key References**:
- Birch, "Finite elastic strain," *Phys. Rev.* **71**, 809 (1947)

### 8. Formation Energy

**Formula**:
```
E_form = E_compound - Σ(n_i × μ_i)
```

Where μ_i are chemical potentials (reference energies)

**Applications**:
- Phase stability
- Energy above convex hull
- Phase diagrams

**See**: `references/formation_energy.md`

**Key References**:
- Hautier et al., "DFT formation energies," *Phys. Rev. B* **85**, 155208 (2012)

### 9. Cluster Expansions (icet)

**Method**: Expand configurational energy in cluster interactions

**Applications**:
- Alloy ground states
- Order-disorder transitions
- Monte Carlo simulations
- Phase diagram construction

**See**: `references/cluster_expansion.md`

**Key References**:
- Ångqvist et al., "ICET library," *Adv. Theory Simul.* **2**, 1900015 (2019)
- Sanchez et al., "Cluster description," *Physica A* **128**, 334 (1984)

### 10. CALPHAD Integration (pycalphad)

**Method**: Combine DFT with thermochemical databases

**Applications**:
- Phase equilibria
- Multi-component systems
- Temperature-dependent properties

**See**: `references/calphad.md`

**Key References**:
- Otis & Liu, "pycalphad," *J. Open Res. Softw.* **5**, 1 (2017)
- Lukas et al., *Computational Thermodynamics* (Cambridge, 2007)

### 11. Defect Formation Energy

**Types**:
- Vacancies
- Interstitials
- Substitutional defects
- Charged defects (with corrections)

**See**: `references/defect_energy.md`

**Key References**:
- Freysoldt et al., "Point defects in solids," *Rev. Mod. Phys.* **86**, 253 (2014)

### 12. Interface/Grain Boundary Energy

**Method**: Compare interface structure to separated surfaces

**See**: `references/interface_energy.md`

**Key References**:
- Sutton & Balluffi, *Interfaces in Crystalline Materials* (Oxford, 1995)

### 13. Magnetic Properties

**Method**: Spin-polarized DFT

**Properties**:
- Magnetic moments
- Magnetic ordering (FM, AFM)
- Heisenberg parameters

**See**: `references/magnetic_properties.md`

### 14. Thermal Expansion

**Method**: Quasi-harmonic approximation

**See**: `references/thermal_expansion.md`

**Key References**:
- Barrera et al., "Grüneisen parameters," *J. Phys.: Condens. Matter* **17**, R217 (2005)

### 15. Electronic Structure

**Properties**:
- Band structure
- Density of states (DOS)
- Band gaps
- Fermi surfaces

**See**: `references/electronic_structure.md`

**Key References**:
- Martin, *Electronic Structure* (Cambridge, 2004)

## Best Practices

### Convergence Testing

**Always test convergence of**:
1. **k-point sampling**: Increase until energy converges (typically < 1 meV/atom)
2. **Plane-wave cutoff**: Test different values (e.g., 300-600 eV)
3. **Slab thickness**: For surfaces (typically 5-9 layers)
4. **Vacuum thickness**: For surfaces (typically 10-15 Å)
5. **Supercell size**: For defects, phonons

**Example**:
```python
# k-point convergence
for k in [2, 4, 6, 8, 10, 12]:
    atoms.calc = GPAW(kpts=(k,k,k), ...)
    E = atoms.get_potential_energy()
    print(f"k={k}: E={E:.4f} eV")
```

### Force Convergence

- Typical: `fmax = 0.01-0.05 eV/Å`
- Tighter for vibrations: `fmax = 0.001 eV/Å`
- Check max force: `max(np.linalg.norm(atoms.get_forces(), axis=1))`

### Constraints

**Fix atoms during relaxation**:
```python
from ase.constraints import FixAtoms

# Fix bottom 2 layers of slab
c = FixAtoms(indices=[atom.index for atom in atoms if atom.position[2] < 5])
atoms.set_constraint(c)
```

### Trajectory Analysis

```python
from ase.io import read

# Read optimization trajectory
traj = read('opt.traj', ':')

# Plot energy vs step
energies = [atoms.get_potential_energy() for atoms in traj]
import matplotlib.pyplot as plt
plt.plot(energies)
plt.xlabel('Step')
plt.ylabel('Energy (eV)')
plt.show()
```

## Common Workflows

### Workflow 1: Lattice Constant Determination

```python
from ase.build import bulk
from ase.eos import calculate_eos

atoms = bulk('Cu', 'fcc', a=3.6)
atoms.calc = EMT()

eos = calculate_eos(atoms, trajectory='eos.traj')
v, e, B = eos.fit()
a_opt = v**(1/3)
print(f"Optimal lattice constant: {a_opt:.3f} Å")
print(f"Bulk modulus: {B/1e9:.1f} GPa")
```

### Workflow 2: Surface Energy Calculation

```python
from ase.build import bulk, surface, add_vacuum

# Bulk energy
bulk_atoms = bulk('Cu', 'fcc', a=3.6)
bulk_atoms.calc = EMT()
E_bulk_per_atom = bulk_atoms.get_potential_energy() / len(bulk_atoms)

# Create slab
slab = surface('Cu', (1,1,1), layers=7, vacuum=10)
slab.calc = EMT()
E_slab = slab.get_potential_energy()

# Surface energy
N = len(slab)
A = slab.get_cell()[0,0] * slab.get_cell()[1,1]
gamma = (E_slab - N * E_bulk_per_atom) / (2 * A)
print(f"Surface energy: {gamma*1000:.1f} meV/ų")
```

### Workflow 3: Adsorption Energy

```python
from ase.build import fcc111, molecule, add_adsorbate

# Clean slab
slab = fcc111('Cu', size=(3,3,4), vacuum=10)
slab.calc = EMT()
E_slab = slab.get_potential_energy()

# Adsorbate in gas phase
mol = molecule('CO')
mol.calc = EMT()
E_mol = mol.get_potential_energy()

# Adsorbed system
add_adsorbate(slab, mol, height=2.0, position='ontop')
slab.calc = EMT()
E_ads_system = slab.get_potential_energy()

# Adsorption energy
E_ads = E_ads_system - E_slab - E_mol
print(f"Adsorption energy: {E_ads:.2f} eV")
```

## Error Handling and Troubleshooting

### Common Issues

**1. SCF Not Converging**:
- Increase mixing parameter
- Try different smearing methods
- Check initial geometry (remove overlaps)

**2. Forces Not Converging**:
- Check constraints
- Try different optimizer
- Increase maximum steps
- Verify calculator parameters

**3. Unstable Structures**:
- Check for imaginary phonon modes
- Verify symmetry is correct
- Try different initial configurations

**4. Memory Issues**:
- Reduce k-points or cutoff
- Use real-space mode (GPAW)
- Parallelize calculation

## Integration with Other Skills

- **python-ase**: Core ASE functionality
- **materials-databases**: Get structures from Materials Project/AFLOW
- **pymatgen**: Structure manipulation and analysis
- **fairchem**: Use ML potentials for screening

## References

**Core ASE**:
1. Larsen et al., "The atomic simulation environment," *J. Phys.: Condens. Matter* **29**, 273002 (2017)

**DFT Theory**:
2. Hohenberg & Kohn, "Inhomogeneous electron gas," *Phys. Rev.* **136**, B864 (1964)
3. Kohn & Sham, "Self-consistent equations," *Phys. Rev.* **140**, A1133 (1965)
4. Sholl & Steckel, *Density Functional Theory: A Practical Introduction* (Wiley, 2009)

**Symmetry Analysis**:
5. Spglib: https://spglib.github.io/spglib/

See individual reference files in `references/` for detailed citations for each method.

## Resources

- **ASE Documentation**: https://wiki.fysik.dtu.dk/ase/
- **ASE Tutorials**: https://wiki.fysik.dtu.dk/ase/tutorials/tutorials.html
- **Example Scripts**: See `examples/` directory
- **Method Details**: See `references/` directory
- **Best Practices**: See `workflows/` directory
