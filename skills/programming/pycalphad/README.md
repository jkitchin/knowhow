# pycalphad Skill

This skill provides expert guidance for using **pycalphad**, a Python library for computational thermodynamics based on the CALPHAD (CALculation of PHAse Diagrams) method.

## What is pycalphad?

pycalphad is an open-source Python library that enables researchers to:
- Calculate phase diagrams for multicomponent materials systems
- Determine phase equilibria at specified thermodynamic conditions
- Compute thermodynamic properties from CALPHAD databases
- Model ordered phases, charged species, and complex phase transformations
- Automate thermodynamic calculations for materials design

## When to Use This Skill

This skill is automatically invoked when you:
- Ask about calculating phase diagrams
- Need to perform equilibrium thermodynamic calculations
- Want to compute activities, chemical potentials, or other thermodynamic properties
- Work with thermodynamic databases (TDB files)
- Analyze metastability or driving forces for phase transformations
- Create property maps or phase stability diagrams

## What's Included

- **SKILL.md**: Comprehensive guide covering all aspects of pycalphad
  - Core concepts and API reference
  - Common workflows with complete code examples
  - Binary, ternary, and multicomponent calculations
  - Activity calculations and driving force analysis
  - Best practices and debugging tips

- **QUICK_REFERENCE.md**: Condensed reference for quick lookups
  - Essential functions and imports
  - Common patterns and code snippets
  - Units and conventions
  - Troubleshooting common errors

## Key Features Covered

1. **Phase Diagram Calculations**
   - Binary and ternary diagrams
   - Isobaric and isothermal sections
   - Property overlays on diagrams

2. **Equilibrium Calculations**
   - Single-point equilibrium
   - Property maps (T-X, P-T, etc.)
   - Phase fraction evolution

3. **Thermodynamic Properties**
   - Gibbs energy, enthalpy, entropy
   - Heat capacity
   - Chemical potentials and activities

4. **Advanced Analysis**
   - Driving forces for precipitation
   - T0 temperature calculations
   - Partial ordering in phases
   - Metastability assessment

## Installation

```bash
pip install pycalphad
```

## Requirements

- Python 3.9+
- numpy, scipy, xarray, sympy, matplotlib
- Thermodynamic database file (TDB format)

## Quick Example

```python
from pycalphad import Database, binplot
import matplotlib.pyplot as plt

# Load database and plot binary phase diagram
db = Database('alzn.tdb')
binplot(db, ['AL', 'ZN', 'VA'], ['LIQUID', 'FCC_A1', 'HCP_A3'],
        conditions={'P': 101325, 'T': (300, 1000, 10), 'X(ZN)': (0, 1, 0.01)})
plt.show()
```

## Resources

- **Official Documentation**: https://pycalphad.org/docs/latest/
- **GitHub Repository**: https://github.com/pycalphad/pycalphad
- **Examples**: https://pycalphad.org/docs/latest/examples/
- **Google Group**: pycalphad@googlegroups.com

## Citation

If you publish work using pycalphad, please cite:

> Otis, R. & Liu, Z.-K., (2017). pycalphad: CALPHAD-based Computational Thermodynamics in Python. *Journal of Open Research Software*. 5(1), p.1. DOI: http://doi.org/10.5334/jors.140

## Related Skills

- **python-ase**: Atomistic simulations and DFT calculations
- **materials-databases**: Accessing materials property databases
- **materials-properties**: First-principles property calculations
- **python-optimization**: Advanced optimization techniques
- **python-plotting**: Visualization and plotting

## Contributing

This skill is part of the skillin repository. To suggest improvements or report issues, please open an issue or pull request at the repository.
