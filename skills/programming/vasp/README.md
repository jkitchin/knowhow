# VASP Calculation Setup Skill

Expert guidance for setting up VASP (Vienna Ab initio Simulation Package) calculations with optimal parameters.

## Overview

This skill helps you generate VASP input files (INCAR, POSCAR, KPOINTS, POTCAR) and select appropriate parameters for different calculation types. Focuses on **best practices** and **parameter recommendations** from the VASP manual.

## Quick Start

### Basic Relaxation Calculation

**1. Create INCAR:**
```bash
SYSTEM = My Material
PREC = Accurate
ENCUT = 520
IBRION = 2
ISIF = 3
NSW = 100
EDIFFG = -0.02
ISMEAR = 1
SIGMA = 0.2
```

**2. Create POSCAR:**
```bash
Material Name
1.0
  a1x a1y a1z
  a2x a2y a2z
  a3x a3y a3z
Elements
  N1 N2
Direct
  ...coordinates...
```

**3. Create KPOINTS:**
```bash
Automatic mesh
0
Gamma
  8 8 8
  0 0 0
```

**4. Create POTCAR:**
```bash
cat $VASP_PP/potpaw_PBE/Element/POTCAR > POTCAR
```

**5. Run VASP:**
```bash
mpirun -np 16 vasp_std > vasp.out
```

## File Organization

```
vasp/
├── SKILL.md              # Main skill with parameter guide
├── README.md             # This file
├── QUICK_REFERENCE.md    # Quick parameter lookup
├── subskills/
│   ├── relaxation.md
│   ├── electronic-structure.md
│   ├── molecular-dynamics.md
│   ├── advanced-functionals.md
│   ├── phonons.md
│   └── convergence.md
├── examples/
│   ├── basic_relaxation/
│   ├── band_structure/
│   └── convergence_tests/
└── references/
    ├── parameter_guide.md
    └── troubleshooting.md
```

## Common Calculation Types

### Structure Relaxation
```bash
IBRION = 2      # CG optimization
ISIF = 3        # Relax cell + ions
NSW = 100
EDIFFG = -0.02  # Force convergence
```

### Static Calculation
```bash
IBRION = -1     # No ionic movement
NSW = 0
ISMEAR = -5     # Tetrahedron method
```

### Band Structure
```bash
# Step 1: Self-consistent
ICHARG = 2
LCHARG = .TRUE.

# Step 2: Non-SC with band path
ICHARG = 11
LORBIT = 11
```

### Molecular Dynamics
```bash
IBRION = 0      # MD
NSW = 1000      # Number of MD steps
POTIM = 1.0     # Time step (fs)
TEBEG = 300     # Temperature (K)
```

## Parameter Quick Reference

### Energy Cutoff (ENCUT)
- **Standard:** 520 eV (1.3 × ENMAX)
- **High accuracy:** 600 eV
- **Forces/phonons:** 550-600 eV
- **Test:** Converge to < 1 meV/atom

### k-Point Density
- **Testing:** 4×4×4
- **Relaxation:** 6×6×6 to 8×8×8
- **Production:** 8×8×8 to 12×12×12
- **Static/DOS:** 12×12×12+
- **Rule:** 30-50 k-points per Å⁻¹

### Smearing (ISMEAR)
| Value | Method | Use Case |
|-------|--------|----------|
| -5 | Tetrahedron | Static, DOS |
| 0 | Gaussian | General |
| 1 | M-P order 1 | Metals, relaxation |

### Convergence (EDIFF)
- **Standard:** 1E-6 eV
- **Tight (phonons):** 1E-8 eV
- **Loose (testing):** 1E-4 eV

### Force Convergence (EDIFFG)
- **Standard:** -0.02 eV/Å
- **Tight:** -0.01 eV/Å
- **Loose:** -0.05 eV/Å

## Workflow Examples

### Full Relaxation + Properties

1. **Convergence test:** Find optimal ENCUT and k-points
2. **Relaxation:** Optimize structure (ISIF=3)
3. **Static calc:** Accurate energy (ISMEAR=-5)
4. **Band structure:** Self-consistent + non-SC
5. **DOS:** Dense k-mesh
6. **Properties:** Phonons, elastic, etc.

### Quick Testing → Production

1. **Quick test:** ENCUT=400, 4×4×4 k-points, EDIFF=1E-4
2. **Verify:** Structure looks reasonable
3. **Production:** ENCUT=520, 8×8×8 k-points, EDIFF=1E-6

## Common Issues

**SCF not converging:**
- Try ALGO = All
- Increase NELM = 200
- Check structure for overlapping atoms

**Slow calculation:**
- Use LREAL = Auto for large systems
- Optimize NCORE/KPAR parallelization
- Check if PREC too high

**Wrong results:**
- Verify k-point convergence
- Check ENCUT convergence
- Ensure correct POTCAR order

## Learning Path

### Beginner
1. Start with relaxation calculations
2. Learn INCAR parameters (ENCUT, ISMEAR, IBRION)
3. Understand KPOINTS generation
4. Test convergence

### Intermediate
1. Static calculations and DOS
2. Band structure workflows
3. Parameter optimization
4. Error troubleshooting

### Advanced
1. Hybrid functionals (HSE06)
2. GW calculations
3. DFPT (phonons, dielectrics)
4. MD simulations

## Best Practices

1. **Always converge:** Test k-points and ENCUT
2. **Document:** Save all INCAR, KPOINTS, POTCAR
3. **Check outputs:** Verify convergence in OUTCAR
4. **Consistent:** Use same pseudopotentials for related calcs
5. **Backup:** Save vasprun.xml and OUTCAR

## Subskills

Invoke for detailed guidance on specific topics:

- `relaxation` - Structure optimization
- `electronic-structure` - Band structure, DOS
- `molecular-dynamics` - MD simulations
- `advanced-functionals` - HSE, GW, DFT+U
- `phonons` - DFPT calculations
- `convergence` - Systematic testing

## Resources

**Official Documentation:**
- VASP Manual: https://vasp.at/wiki/The_VASP_Manual
- VASP Tutorials: https://vasp.at/tutorials/latest/
- Parameter Reference: https://vasp.at/wiki/index.php/Category:INCAR

**This Skill:**
- Main guide: `SKILL.md`
- Quick reference: `QUICK_REFERENCE.md`
- Examples: `examples/` directory
- Detailed refs: `references/` directory

## Contributing

This skill focuses on best practices and recommended parameters. Contributions welcome for:
- Additional calculation types
- Troubleshooting tips
- Example workflows
- Parameter optimization strategies

## License

Part of the knowhow repository.
