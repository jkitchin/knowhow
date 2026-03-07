---
name: pycalphad
description: Expert guidance for pycalphad - computational thermodynamics library implementing the CALPHAD method for calculating phase diagrams, phase equilibria, and thermodynamic properties of multicomponent materials systems using thermodynamic databases (TDB files)
allowed-tools: ["*"]
---

# pycalphad - Computational Thermodynamics in Python

## Overview

**pycalphad** is a Python library for computational thermodynamics within the CALPHAD (CALculation of PHAse Diagrams) framework. It enables users to design thermodynamic models, compute phase diagrams, calculate phase equilibria, and predict thermodynamic properties for multicomponent materials systems.

**Core capabilities:**
- Read and process Thermo-Calc database (TDB) files
- Calculate binary, ternary, and multicomponent phase diagrams
- Perform Gibbs energy minimization for phase equilibrium
- Compute thermodynamic properties (activity, chemical potentials, heat capacity)
- Model ordered phases and systems with charged species
- Calculate driving forces and metastability

**Target users:** Researchers and practitioners in materials science, metallurgy, and computational thermodynamics who want to perform CALPHAD calculations programmatically.

## When to Use This Skill

Use pycalphad when:
- Calculating phase diagrams (binary, ternary, or multicomponent systems)
- Determining phase equilibria at specific temperature/composition/pressure conditions
- Computing thermodynamic properties from CALPHAD databases
- Analyzing metastability and driving forces for phase transformations
- Modeling systems with ordered phases or charged species
- Automating thermodynamic calculations for materials design
- Creating custom thermodynamic models or property frameworks
- Visualizing phase stability regions and property maps

**Don't use when:**
- You need first-principles calculations (use VASP, Quantum ESPRESSO, GPAW instead)
- You need molecular dynamics simulations (use ASE, LAMMPS instead)
- Working with kinetic models (pycalphad is for equilibrium thermodynamics)

## Core Concepts

### 1. Database (TDB Files)
Thermodynamic databases in Thermo-Calc format containing:
- Phase definitions and constituents
- Gibbs energy models for each phase
- Model parameters fitted to experimental data
- Temperature, composition, and pressure ranges

### 2. Components and Species
- **Components**: Independent chemical elements (e.g., Al, Fe, Ni)
- **Species**: Charged or molecular entities in ionic systems

### 3. Phases
Distinct thermodynamic phases with specific crystal structures and energy models:
- Liquid, FCC, BCC, HCP, intermetallic compounds, etc.
- Each phase has a sublattice model defining site occupancy

### 4. State Variables
Conditions that define the system state:
- Temperature (T)
- Pressure (P)
- Composition (mole fractions: X_i, Y_i, etc.)
- Chemical potential (MU)

### 5. Calculate vs Equilibrium
- **calculate()**: Evaluate properties at specified conditions (no equilibrium minimization)
- **equilibrium()**: Find stable phase assemblage by minimizing Gibbs energy

## Quick Reference

| Task | Function | Key Parameters |
|------|----------|----------------|
| Load database | `Database('database.tdb')` | TDB file path |
| Binary phase diagram | `binplot(db, comps, phases, conditions)` | components, phases, T/X ranges |
| Equilibrium calculation | `equilibrium(db, comps, phases, conditions)` | P, T, composition |
| Property calculation | `calculate(db, comps, phases, conditions)` | P, T, composition, output |
| Ternary diagram | Use `equilibrium()` with 3 components | T, P, composition grid |
| Activity calculation | Access from equilibrium dataset | `ACR_*` variables |
| Driving force | `equilibrium()` with metastable phases | Compare energies |

## Installation

```bash
# via pip
pip install pycalphad

# via conda
conda install -c conda-forge pycalphad

# development version
pip install git+https://github.com/pycalphad/pycalphad.git
```

**Dependencies:** Python 3.9+, numpy, scipy, xarray, sympy, matplotlib

## Common Workflows

### 1. Binary Phase Diagram

```python
from pycalphad import Database, binplot
import matplotlib.pyplot as plt

# Load thermodynamic database
db = Database('alzn_mey.tdb')

# Define components and phases
comps = ['AL', 'ZN', 'VA']  # VA = vacancy for gas phase
phases = ['LIQUID', 'FCC_A1', 'HCP_A3']

# Plot isobaric (constant pressure) binary diagram
fig = plt.figure(figsize=(8, 6))
binplot(db, comps, phases,
        conditions={'P': 101325, 'T': (300, 1000, 10), 'X(ZN)': (0, 1, 0.01)})
plt.xlabel('X(ZN)')
plt.ylabel('Temperature (K)')
plt.title('Al-Zn Binary Phase Diagram')
plt.savefig('al-zn-diagram.png')
```

### 2. Equilibrium Calculation at Fixed Conditions

```python
from pycalphad import Database, equilibrium, variables as v
import numpy as np

# Load database
db = Database('nist_ni_al.tdb')

# Define system
comps = ['NI', 'AL', 'VA']
phases = ['LIQUID', 'FCC_L12', 'BCC_B2']

# Calculate equilibrium at 1500K, 1 atm, 50 at% Al
result = equilibrium(db, comps, phases,
                    {v.T: 1500, v.P: 101325, v.X('AL'): 0.5})

# Access results
print("Stable phases:", result.Phase.values.squeeze())
print("Phase fractions:", result.NP.values.squeeze())
print("Compositions:", result.X.values.squeeze())
print("Gibbs energy:", result.GM.values.squeeze())
```

### 3. Property Map (T-X Diagram with Property Overlay)

```python
from pycalphad import Database, equilibrium, variables as v
import numpy as np
import matplotlib.pyplot as plt

db = Database('crfe.tdb')
comps = ['CR', 'FE', 'VA']
phases = ['LIQUID', 'BCC_A2', 'SIGMA']

# Create T-X grid
temps = np.linspace(1000, 2000, 50)
x_cr = np.linspace(0, 1, 50)
T_grid, X_grid = np.meshgrid(temps, x_cr)

# Calculate equilibrium at each point
result = equilibrium(db, comps, phases,
                    {v.T: T_grid.flatten(),
                     v.P: 101325,
                     v.X('CR'): X_grid.flatten()},
                    pdens=500)

# Extract heat capacity
cp = result.CPM.values.reshape(T_grid.shape)

# Plot
plt.contourf(X_grid, T_grid, cp, levels=20, cmap='viridis')
plt.colorbar(label='Heat Capacity (J/mol-atom-K)')
plt.xlabel('X(CR)')
plt.ylabel('Temperature (K)')
plt.title('Cr-Fe Heat Capacity Map')
plt.savefig('crfe_cp_map.png')
```

### 4. Activity Calculation

```python
from pycalphad import Database, equilibrium, variables as v

db = Database('feni.tdb')
comps = ['FE', 'NI', 'VA']
phases = ['FCC_A1']

# Calculate at specific conditions
result = equilibrium(db, comps, phases,
                    {v.T: 1200, v.P: 101325, v.X('NI'): 0.3})

# Extract activities (relative to pure element reference state)
activity_fe = result['ACR_FE'].values.squeeze()
activity_ni = result['ACR_NI'].values.squeeze()

print(f"Activity of Fe: {activity_fe:.4f}")
print(f"Activity of Ni: {activity_ni:.4f}")

# Chemical potentials
mu_fe = result['MU_FE'].values.squeeze()
mu_ni = result['MU_NI'].values.squeeze()

print(f"Chemical potential Fe: {mu_fe:.2f} J/mol")
print(f"Chemical potential Ni: {mu_ni:.2f} J/mol")
```

### 5. Ternary Phase Diagram

```python
from pycalphad import Database, equilibrium, variables as v
from pycalphad.plot.eqplot import eqplot
import numpy as np
import matplotlib.pyplot as plt

db = Database('ternary.tdb')
comps = ['AL', 'CU', 'ZN', 'VA']
phases = ['LIQUID', 'FCC_A1', 'HCP_A3', 'THETA']

# Calculate equilibrium at constant T
result = equilibrium(db, comps, phases,
                    {v.T: 800, v.P: 101325,
                     v.X('CU'): (0, 1, 0.02),
                     v.X('ZN'): (0, 1, 0.02)},
                    pdens=2000)

# Plot using ternary coordinates
fig = plt.figure(figsize=(8, 8))
eqplot(result, x=v.X('CU'), y=v.X('ZN'))
plt.title('Al-Cu-Zn Ternary at 800K')
plt.savefig('alcuzn_ternary.png')
```

### 6. Driving Force for Precipitation

```python
from pycalphad import Database, equilibrium, variables as v
import numpy as np

db = Database('alcu.tdb')
comps = ['AL', 'CU', 'VA']

# Supersaturated parent phase
parent_phases = ['FCC_A1']

# Calculate parent phase energy (metastable)
parent_eq = equilibrium(db, comps, parent_phases,
                       {v.T: 500, v.P: 101325, v.X('CU'): 0.02})
gm_parent = parent_eq.GM.values.squeeze()

# Equilibrium with precipitate phase allowed
all_phases = ['FCC_A1', 'THETA']
eq = equilibrium(db, comps, all_phases,
                {v.T: 500, v.P: 101325, v.X('CU'): 0.02})
gm_stable = eq.GM.values.squeeze()

# Driving force for precipitation
driving_force = gm_parent - gm_stable
print(f"Driving force: {driving_force:.2f} J/mol-atom")
```

### 7. T0 Temperature Calculation

```python
from pycalphad import Database, equilibrium, variables as v
import numpy as np
from scipy.optimize import brentq

db = Database('steel.tdb')
comps = ['FE', 'C', 'VA']

def t0_condition(temp, composition):
    """Calculate GM difference between phases at equal composition"""
    # FCC energy
    fcc_eq = equilibrium(db, comps, ['FCC_A1'],
                        {v.T: temp, v.P: 101325, v.X('C'): composition})
    gm_fcc = fcc_eq.GM.values.squeeze()

    # BCC energy
    bcc_eq = equilibrium(db, comps, ['BCC_A2'],
                        {v.T: temp, v.P: 101325, v.X('C'): composition})
    gm_bcc = bcc_eq.GM.values.squeeze()

    return gm_fcc - gm_bcc

# Find T0 temperature where FCC and BCC have equal energy
composition = 0.01  # 1 at% C
try:
    t0_temp = brentq(t0_condition, 800, 1200, args=(composition,))
    print(f"T0 temperature at X(C)={composition}: {t0_temp:.1f} K")
except ValueError:
    print("T0 not found in temperature range")
```

### 8. Partial Ordering in Phases

```python
from pycalphad import Database, equilibrium, variables as v

# Database with ordering model (e.g., Al-Ni with L12 ordering)
db = Database('alni.tdb')
comps = ['AL', 'NI', 'VA']
phases = ['FCC_L12']  # FCC with L12 ordering capability

# Calculate at composition where ordering occurs
result = equilibrium(db, comps, phases,
                    {v.T: 900, v.P: 101325, v.X('NI'): 0.25})

# Access site fractions to determine ordering
# FCC_L12 has sublattices for corner and face sites
print("Phase composition:")
for phase in result.Phase.values.squeeze():
    if phase != '':
        print(f"  {phase}")

# Site fractions show ordering (corner vs face sites)
print("Site fractions:", result.Y.values.squeeze())
```

## Key Output Variables

### From equilibrium() Dataset (xarray)

**Phase Information:**
- `Phase`: Names of stable phases
- `NP`: Phase fractions (moles)
- `Mode`: Phase mode (for output control)

**Composition:**
- `X`: Overall mole fractions
- `Y`: Site fractions (sublattice model)
- `MU`: Chemical potentials (J/mol)

**Thermodynamic Properties:**
- `GM`: Molar Gibbs energy (J/mol-atom)
- `HM`: Molar enthalpy (J/mol-atom)
- `SM`: Molar entropy (J/mol-atom-K)
- `CPM`: Molar heat capacity (J/mol-atom-K)

**Activity:**
- `ACR_*`: Activity (ratio to reference state)
- Reference states defined in database

**Structure:**
Dataset is indexed by conditions (P, T, X) and has dimensions for phases, components, sublattices.

## Advanced Features

### Custom Models

```python
from pycalphad import Model, Database

# Extend base Model class for custom properties
class ViscosityModel(Model):
    def build_viscosity(self):
        """Add viscosity as a custom property"""
        # Implementation here
        pass

# Use custom model
db = Database('liquid.tdb')
model = ViscosityModel(db, ['AL', 'CU'], 'LIQUID')
```

### xarray Dataset Exploration

```python
# equilibrium() returns xarray Dataset
result = equilibrium(db, comps, phases, conditions)

# Access as xarray
print(result)  # Shows all variables and dimensions

# Select specific conditions
subset = result.sel(T=1200, method='nearest')

# Slice along dimension
temps = result.sel(T=slice(1000, 1500))

# Boolean indexing
liquid_only = result.where(result.Phase == 'LIQUID', drop=True)

# Convert to pandas for further analysis
df = result.to_dataframe()
```

### Mapping API for Advanced Plotting

```python
from pycalphad.mapping.strategy import Strategy

# For complex visualizations beyond binplot
# Allows custom mapping strategies for phase diagram rendering
```

## Best Practices

### 1. Database Management
```python
# Always include vacancy for gas/liquid phases
comps = ['FE', 'C', 'VA']  # Include VA

# Check available phases in database
print(db.phases.keys())

# Verify component names match database
print(db.elements)
```

### 2. Convergence and Performance
```python
# Use pdens parameter to control calculation density
# Lower pdens = faster but less accurate phase boundaries
result = equilibrium(db, comps, phases, conditions, pdens=500)

# For production: pdens=2000 or higher
# For testing: pdens=100-500
```

### 3. Error Handling
```python
try:
    result = equilibrium(db, comps, phases, conditions)
except Exception as e:
    print(f"Calculation failed: {e}")
    # Common issues:
    # - Missing phases in database
    # - Invalid composition ranges
    # - Temperature out of database range
```

### 4. Validation
```python
# Always validate results
# Check for physical reasonableness
assert np.all(result.NP >= 0), "Negative phase fractions!"
assert np.allclose(result.NP.sum(), 1.0), "Phase fractions don't sum to 1!"

# Verify composition conservation
total_x = (result.NP * result.X).sum(dim='Phase')
# Should equal input composition
```

### 5. Visualization
```python
# Use binplot for quick binary diagrams
# For custom plots, extract from equilibrium dataset

# Example: Custom property plot
import matplotlib.pyplot as plt

temps = np.linspace(300, 1500, 100)
results = equilibrium(db, comps, phases, {v.T: temps, v.P: 101325, v.X('AL'): 0.5})

plt.plot(temps, results.GM.values.squeeze())
plt.xlabel('Temperature (K)')
plt.ylabel('Gibbs Energy (J/mol)')
plt.show()
```

## Common Pitfalls

**Missing vacancy component:**
```python
# Wrong - will fail for phases with vacancy
comps = ['FE', 'C']

# Correct
comps = ['FE', 'C', 'VA']
```

**Incorrect phase names:**
```python
# Must match exact names in database (case-sensitive)
# Check database first
print(list(db.phases.keys()))

# Use exact names
phases = ['FCC_A1']  # not 'FCC' or 'fcc_a1'
```

**Composition not summing to 1:**
```python
# For multicomponent, remember dependent component
# If specifying X(A) and X(B), X(C) is determined automatically

# For 3 components A, B, C
# Specify only n-1 compositions
{v.X('A'): 0.3, v.X('B'): 0.5}  # X(C) = 0.2 automatically
```

**Temperature/pressure units:**
```python
# pycalphad uses SI units
# Temperature: Kelvin (not Celsius)
# Pressure: Pascals (not atm)

{v.T: 1273}  # 1273 K (1000°C)
{v.P: 101325}  # 101325 Pa (1 atm)
```

**Ignoring metastability:**
```python
# equilibrium() finds global minimum
# May miss metastable states

# To study metastability:
# 1. Exclude certain phases
# 2. Compare energies
# 3. Calculate driving forces
```

## Debugging Tips

### Check calculation status
```python
# Verify output
print(result)
print(result.dims)
print(result.coords)

# Check for failed points (NaN values)
print(result.GM.isnull().sum())
```

### Visualization for debugging
```python
# Quick phase stability check
print(result.Phase.values)
print(result.NP.values)

# Plot Gibbs energy curves
from pycalphad import calculate

# Calculate all phases (not equilibrium)
calc_result = calculate(db, comps, phases,
                       {v.T: 1000, v.P: 101325, v.X('AL'): (0, 1, 0.01)})

# Plot GM for each phase
for phase in phases:
    phase_data = calc_result.where(calc_result.Phase == phase, drop=True)
    plt.plot(phase_data.X.sel(component='AL'), phase_data.GM, label=phase)
plt.legend()
plt.show()
```

### Database troubleshooting
```python
# Inspect database content
print("Elements:", db.elements)
print("Species:", db.species)
print("Phases:", list(db.phases.keys()))

# Check specific phase constituents
phase = db.phases['FCC_A1']
print("Sublattices:", phase.constituents)
```

## Units and Conventions

- **Energy**: J/mol or J/mol-atom (check database formulation)
- **Temperature**: Kelvin (K)
- **Pressure**: Pascal (Pa), 101325 Pa = 1 atm
- **Composition**: Mole fractions (0 to 1)
- **Reference states**: Defined in TDB file (typically pure elements at 298.15 K)

## Resources and Citation

**Documentation:**
- Official docs: https://pycalphad.org/docs/latest/
- GitHub: https://github.com/pycalphad/pycalphad
- Examples: https://pycalphad.org/docs/latest/examples/

**Community:**
- Google Group: For installation and usage questions
- GitHub Issues: For bugs and technical problems
- Gitter chat: Real-time discussion

**Citation:**
When publishing work using pycalphad, cite:
> Otis, R. & Liu, Z.-K., (2017). pycalphad: CALPHAD-based Computational Thermodynamics in Python. Journal of Open Research Software. 5(1), p.1. DOI: http://doi.org/10.5334/jors.140

**Databases:**
- Free databases: NIST, GT databases (check licenses)
- Commercial: Thermo-Calc, CompuTherm (require licenses)
- Community databases: Thermochimica, FREED

## Workflow Summary

1. **Load database**: `db = Database('file.tdb')`
2. **Define system**: components, phases
3. **Set conditions**: Temperature, pressure, composition
4. **Calculate**: `equilibrium()` or `calculate()`
5. **Extract results**: Access xarray dataset variables
6. **Visualize**: Use matplotlib or pycalphad plotting tools
7. **Validate**: Check physical constraints and conservation laws
8. **Iterate**: Refine conditions, add/remove phases as needed

## Related Skills

- **python-ase**: For atomistic simulations and DFT calculations
- **materials-databases**: For accessing experimental materials data
- **materials-properties**: For first-principles property calculations
- **python-optimization**: For custom thermodynamic optimization
- **python-plotting**: For advanced visualization of results
