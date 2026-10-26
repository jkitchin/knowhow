# Materials Properties Calculation Skill

Expert assistant for calculating materials properties from first-principles using ASE (Atomic Simulation Environment) and specialized packages. Comprehensive coverage of structure relaxation, surface energies, adsorption, reaction barriers, phonons, elastic constants, and thermodynamic modeling.

## What This Skill Does

This skill enables Claude to help you:
- Perform structure relaxation and geometry optimization
- Calculate ground state properties (lattice constants, space groups)
- Compute surface energies for different facets
- Determine adsorption energies and preferred binding sites
- Find reaction barriers using nudged elastic band (NEB)
- Calculate vibrational frequencies and zero-point energies
- Compute phonon band structures and thermal properties
- Determine elastic constants and mechanical properties
- Build cluster expansion models for alloys
- Integrate DFT calculations with CALPHAD databases
- Calculate defect formation energies
- Analyze interfaces and grain boundaries
- Study magnetic properties
- Model thermal expansion
- Calculate electronic band structures

## When to Use This Skill

Use this skill when you need to:
- Set up first-principles calculations with proper methodology
- Understand scientific methods for materials property calculations
- Get code examples with scientific citations
- Learn best practices for convergence testing
- Troubleshoot DFT calculations
- Integrate multiple computational tools (ASE, phonopy, elastic, icet, pycalphad)

## Installation

### Core Packages

```bash
# ASE and utilities
pip install ase spglib matplotlib

# Visualization (optional)
pip install ase-gui
```

### Specialized Packages

```bash
# Phonon calculations
pip install phonopy

# Elastic constants
pip install elastic

# Cluster expansions
pip install icet

# CALPHAD integration
pip install pycalphad
```

### DFT Calculators

```bash
# GPAW (requires compilation, conda recommended)
conda install -c conda-forge gpaw

# Or with pip (may require dependencies)
pip install gpaw
```

**VASP**: Requires separate license and installation. Use via `ase.calculators.vasp`.

**Quantum ESPRESSO**: Use via `ase.calculators.espresso` (requires QE installation).

## Quick Start

### 1. Basic Structure Relaxation

```python
from ase.build import bulk
from ase.optimize import BFGS
from ase.calculators.emt import EMT

# Create structure
atoms = bulk('Cu', 'fcc', a=3.6)

# Set calculator (EMT for fast testing)
atoms.calc = EMT()

# Optimize
opt = BFGS(atoms)
opt.run(fmax=0.01)

# Results
print(f"Energy: {atoms.get_potential_energy():.3f} eV")
print(f"Lattice: {atoms.cell.cellpar()[0]:.3f} Å")
```

### 2. Lattice Constant Determination

```python
from ase.build import bulk
from ase.eos import calculate_eos

atoms = bulk('Cu', 'fcc', a=3.6)
atoms.calc = EMT()

eos = calculate_eos(atoms)
v, e, B = eos.fit()
a_opt = v**(1/3)
print(f"Optimal lattice constant: {a_opt:.3f} Å")
print(f"Bulk modulus: {B/1e9:.1f} GPa")
```

### 3. Surface Energy Calculation

```python
from ase.build import bulk, fcc111

# Bulk energy per atom
bulk_atoms = bulk('Cu', 'fcc', a=3.6)
bulk_atoms.calc = EMT()
E_bulk = bulk_atoms.get_potential_energy() / len(bulk_atoms)

# Slab energy
slab = fcc111('Cu', size=(3,3,7), vacuum=10)
slab.calc = EMT()
E_slab = slab.get_potential_energy()

# Surface energy
N = len(slab)
A = slab.get_cell()[0,0] * slab.get_cell()[1,1]
gamma = (E_slab - N * E_bulk) / (2 * A)
print(f"Surface energy: {gamma*1000:.1f} meV/ų")
```

## Skill Coverage

### Core Capabilities

**Structure Relaxation**:
- Geometry optimization (force minimization)
- Unit cell optimization (stress relaxation)
- Constrained optimization
- Multiple optimizers (BFGS, FIRE, LBFGS)

**Ground State Properties**:
- Lattice constants and angles
- Space group determination
- Crystal structure identification
- Atomic positions
- Symmetry operations

### Advanced Property Calculations (15 Subskills)

1. **Surface Energy** - Slab models, convergence testing
2. **Adsorption Energy** - Binding sites, coverage effects
3. **Reaction Barriers (NEB)** - Transition states, minimum energy paths
4. **Vibrational Analysis** - Normal modes, ZPE, IR/Raman
5. **Phonons** - Band structures, DOS, thermal properties (phonopy)
6. **Elastic Constants** - Full tensor, moduli, sound velocities (elastic)
7. **Equation of State** - Birch-Murnaghan, bulk modulus
8. **Formation Energy** - Phase stability, energy above hull
9. **Cluster Expansions** - Alloy ordering, Monte Carlo (icet)
10. **CALPHAD** - Phase diagrams, thermochemical data (pycalphad)
11. **Defect Formation** - Vacancies, interstitials, corrections
12. **Interface Energy** - Grain boundaries, adhesion
13. **Magnetic Properties** - Spin polarization, ordering
14. **Thermal Expansion** - Quasi-harmonic approximation
15. **Electronic Structure** - Band structure, DOS, band gaps

## File Organization

```
materials-properties/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
├── QUICK_REFERENCE.md                # Quick syntax guide
├── PLAN.md                          # Development plan with references
├── examples/
│   ├── basic_relaxation.py          # Simple optimization
│   ├── lattice_constant.py          # EOS calculation
│   ├── surface_energy.py            # Surface calculation
│   ├── adsorption_energy.py         # Adsorption workflow
│   ├── neb_barrier.py               # Reaction barrier
│   ├── phonon_calculation.py        # Phonon band structure
│   ├── elastic_constants.py         # Mechanical properties
│   ├── cluster_expansion.py         # Alloy modeling
│   └── complete_workflow.py         # Comprehensive example
├── references/
│   ├── surface_energy.md            # Detailed methodology
│   ├── adsorption_energy.md
│   ├── reaction_barriers.md
│   ├── vibrational_analysis.md
│   ├── phonons.md
│   ├── elastic_constants.md
│   ├── equation_of_state.md
│   ├── formation_energy.md
│   ├── cluster_expansion.md
│   ├── calphad.md
│   ├── defect_energy.md
│   ├── interface_energy.md
│   ├── magnetic_properties.md
│   ├── thermal_expansion.md
│   └── electronic_structure.md
└── workflows/
    ├── convergence_testing.md
    ├── best_practices.md
    └── calculator_comparison.md
```

## Calculators Supported

### EMT (Effective Medium Theory)
- **Pros**: Very fast, no setup required
- **Cons**: Limited elements (Cu, Ag, Au, Ni, Pd, Pt, Al, Pb, Fe)
- **Use for**: Workflow development, testing, teaching

### GPAW
- **Pros**: Real DFT, well-documented, Python integration
- **Cons**: Requires compilation, slower than VASP
- **Use for**: Production calculations, method development

### VASP
- **Pros**: Industry standard, very fast, well-validated
- **Cons**: Commercial license, less Python integration
- **Use for**: Large-scale production calculations

### Quantum ESPRESSO
- **Pros**: Open source, well-established
- **Cons**: Input file based, less ASE integration
- **Use for**: Specific functionalities (DFPT, transport)

## Scientific Methodology

All methods in this skill include:
- **Proper formulas** with clear definitions
- **Scientific citations** to original papers
- **Convergence criteria** and testing procedures
- **Validation approaches** against experiments/benchmarks
- **Best practices** from the literature
- **Common pitfalls** and how to avoid them

### Key References

**ASE**:
- Larsen et al., *J. Phys.: Condens. Matter* **29**, 273002 (2017)

**DFT Foundations**:
- Hohenberg & Kohn, *Phys. Rev.* **136**, B864 (1964)
- Kohn & Sham, *Phys. Rev.* **140**, A1133 (1965)

**Textbook**:
- Sholl & Steckel, *Density Functional Theory: A Practical Introduction* (Wiley, 2009)

See `PLAN.md` and individual reference files for complete citations.

## Learning Path

### Beginner
1. Basic structure relaxation
2. Lattice constant calculation
3. Equation of state
4. Space group identification

### Intermediate
5. Surface energy calculations
6. Adsorption energy on surfaces
7. Vibrational analysis
8. Formation energies

### Advanced
9. Nudged elastic band (reaction barriers)
10. Phonon band structures
11. Elastic constants
12. Cluster expansions
13. CALPHAD integration
14. Defect calculations

## Common Use Cases

1. **Optimize crystal structure**: "Help me relax this CIF file and get the lattice constant"
2. **Calculate surface properties**: "Find the surface energy of the (111) facet of copper"
3. **Adsorption study**: "Determine where CO prefers to bind on a Pt surface"
4. **Reaction mechanism**: "Use NEB to find the barrier for H diffusion in Pd"
5. **Thermal properties**: "Calculate the phonon band structure and heat capacity"
6. **Mechanical properties**: "Compute the elastic constants and bulk modulus"
7. **Phase stability**: "Is this compound stable relative to its elements?"
8. **Alloy modeling**: "Build a cluster expansion for the Cu-Au system"

## Best Practices

### Convergence Testing
- Always test k-point convergence (typically < 1 meV/atom)
- Test plane-wave cutoff (if applicable)
- Test slab thickness for surfaces (5-9 layers typical)
- Test vacuum thickness (10-15 Å typical)
- Test supercell size for defects

### Force Convergence
- Standard: fmax = 0.01-0.05 eV/Å
- Vibrations: fmax = 0.001 eV/Å
- Always check final forces

### Documentation
- Record all calculation parameters
- Save trajectories for analysis
- Version control your scripts
- Document any unusual choices

### Validation
- Compare to experimental values when available
- Check against benchmark calculations
- Verify convergence
- Use multiple functionals if uncertain

## Troubleshooting

**SCF not converging**:
- Check for overlapping atoms
- Adjust mixing parameters
- Try different smearing
- Increase electronic temperature

**Forces not converging**:
- Check constraints
- Try different optimizer
- Verify calculator settings
- Increase max steps

**Unexpected results**:
- Verify structure is correct
- Check for symmetry breaking
- Test convergence parameters
- Compare to literature

**Memory issues**:
- Reduce k-points or cutoff
- Use smaller supercells
- Parallelize calculation
- Use more memory-efficient settings

## Integration with Other Skills

- **python-ase**: Core ASE functionality
- **materials-databases**: Get structures from MP/AFLOW
- **pymatgen**: Structure manipulation
- **fairchem**: ML potentials for screening

## Resources

- **ASE Documentation**: https://wiki.fysik.dtu.dk/ase/
- **ASE Tutorials**: https://wiki.fysik.dtu.dk/ase/tutorials/tutorials.html
- **Phonopy**: https://phonopy.github.io/phonopy/
- **Elastic**: https://elastic.readthedocs.io/
- **ICET**: https://icet.materialsmodeling.org/
- **pycalphad**: https://pycalphad.org/

## Contributing

This skill is part of the skillin repository. See examples and references for detailed implementations of each method.

## License

MIT License - Part of skillin project

## Version Information

- Skill created for ASE 3.22+
- Python 3.8+
- Compatible with GPAW 24.x, phonopy 2.x
