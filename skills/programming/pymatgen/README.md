# Pymatgen Skill

Comprehensive guidance for using [pymatgen](https://pymatgen.org/) (Python Materials Genomics) for computational materials science.

## Overview

This skill provides systematic guidance for:
- Creating and manipulating crystal structures
- Reading/writing materials science file formats (CIF, POSCAR, XYZ)
- Analyzing symmetry and structure properties
- Querying the Materials Project database
- Generating DFT calculation inputs (VASP, Gaussian, etc.)
- Analyzing electronic structure, phase diagrams, and more

## Quick Start

### Installation

```bash
pip install pymatgen
# Or with all optional dependencies
pip install pymatgen[all]
```

### Configure Materials Project API

```bash
# Get API key from materialsproject.org
pmg config --add PMG_MAPI_KEY your_api_key_here
```

### Basic Usage

```python
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# Load structure
structure = Structure.from_file("structure.cif")

# Analyze
print(f"Formula: {structure.composition.reduced_formula}")
print(f"Space group: {SpacegroupAnalyzer(structure).get_space_group_symbol()}")

# Generate VASP inputs
from pymatgen.io.vasp.sets import MPRelaxSet
input_set = MPRelaxSet(structure)
input_set.write_input("vasp_calc")
```

## Skill Structure

### Core Workflow

The `SKILL.md` file routes you to appropriate references based on your task:

- **Structure Creation/Loading** → See what format you have
- **Structure Analysis** → Symmetry, neighbors, properties
- **Structure Transformation** → Supercells, slabs, substitutions
- **Materials Database** → Query Materials Project
- **Electronic Structure** → Band structures, DOS
- **Input Generation** → VASP, Gaussian, Q-Chem

### Reference Files

Detailed guides in `references/`:

| File | Topic | Key Content |
|------|-------|-------------|
| `core-objects.md` | Fundamental classes | Element, Structure, Lattice, Composition |
| `file-io.md` | Reading/writing files | CIF, POSCAR, XYZ, vasprun.xml |
| `structure-analysis.md` | Analyzing structures | Symmetry, comparison, neighbors |
| `transformations.md` | Modifying structures | Supercells, slabs, defects, strain |
| `materials-project.md` | Database queries | API usage, retrieving properties |
| `phase-diagrams.md` | Thermodynamics | Stability, formation energy |
| `electronic-structure.md` | Electronic properties | Band structures, DOS, band gaps |
| `vasp-integration.md` | VASP workflows | Input generation, output parsing |
| `properties.md` | Calculated properties | Mechanical, magnetic, optical |
| `visualization.md` | Viewing structures | VESTA, matplotlib, nglview |

### Examples

Working examples in `examples/`:
- `structure_analysis_workflow.py` - Complete analysis workflow from CIF to VASP

## Common Tasks

### Load and Analyze a Structure

```python
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

structure = Structure.from_file("material.cif")
sga = SpacegroupAnalyzer(structure)

print(f"Formula: {structure.composition.reduced_formula}")
print(f"Space group: {sga.get_space_group_symbol()}")
print(f"Volume: {structure.volume:.2f} Ų")
print(f"Density: {structure.density:.2f} g/cm³")
```

### Query Materials Project

```python
from mp_api.client import MPRester

with MPRester() as mpr:
    # Search for materials
    docs = mpr.materials.summary.search(
        formula="Fe2O3",
        fields=["material_id", "formula_pretty", "band_gap"]
    )

    for doc in docs:
        print(f"{doc.material_id}: {doc.formula_pretty}, Eg = {doc.band_gap:.2f} eV")

    # Get structure
    structure = mpr.get_structure_by_material_id("mp-149")
```

### Create Supercell

```python
# Simple 2×2×1 supercell
supercell = structure * (2, 2, 1)

# Or with matrix
structure.make_supercell([[2, 0, 0], [0, 2, 0], [0, 0, 1]])
```

### Generate VASP Inputs

```python
from pymatgen.io.vasp.sets import MPRelaxSet

# Create all VASP input files
input_set = MPRelaxSet(structure)
input_set.write_input("relax_calc")
# Creates: POSCAR, INCAR, KPOINTS, POTCAR
```

### Parse VASP Outputs

```python
from pymatgen.io.vasp.outputs import Vasprun, Outcar

vasprun = Vasprun("vasprun.xml")
print(f"Final energy: {vasprun.final_energy:.6f} eV")

outcar = Outcar("OUTCAR")
print(f"Max force: {max(outcar.final_fr):.4f} eV/Å")
```

### Analyze Band Structure

```python
from mp_api.client import MPRester
from pymatgen.electronic_structure.plotter import BSPlotter

with MPRester() as mpr:
    bs = mpr.get_bandstructure_by_material_id("mp-149")

    # Get band gap
    gap = bs.get_band_gap()
    print(f"Band gap: {gap['energy']:.3f} eV")
    print(f"Direct: {gap['direct']}")

    # Plot
    plotter = BSPlotter(bs)
    plotter.save_plot("band_structure.png")
```

### Build Phase Diagram

```python
from mp_api.client import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter

with MPRester() as mpr:
    entries = mpr.get_entries_in_chemsys(["Fe", "O"])

pd = PhaseDiagram(entries)
plotter = PDPlotter(pd)
plotter.show()
```

## When to Use This Skill

Use this pymatgen skill when you need to:

- **Load structures** from files (CIF, POSCAR, XYZ, etc.)
- **Analyze structures** (symmetry, coordination, properties)
- **Transform structures** (supercells, slabs, substitutions)
- **Query databases** (Materials Project API)
- **Generate inputs** for DFT codes (VASP, Gaussian, Q-Chem)
- **Parse outputs** from calculations
- **Analyze results** (band structures, DOS, phase diagrams)
- **Visualize structures** and properties

## Integration with Other Skills

This skill works well with:
- **Scientific writing** skill for documenting results
- **TDD** skill for testing pymatgen workflows
- **Python-ASE** skill for complementary materials analysis

## Key Concepts

### Object Hierarchy

```
Lattice       → 3×3 matrix defining unit cell
  ↓
Structure     → Lattice + Sites (periodic)
Molecule      → Sites (non-periodic)
  ↓
Site          → Element + Coordinates
  ↓
Element       → Atomic properties
Species       → Element + oxidation state
```

### Coordinates

- **Fractional coordinates** - Default for Structure (0-1 range)
- **Cartesian coordinates** - Real space (Angstroms)
- Use `coords_are_cartesian=True` when providing Cartesian

### Common Patterns

**Load → Analyze → Transform → Write:**
```python
structure = Structure.from_file("input.cif")
sga = SpacegroupAnalyzer(structure)
primitive = sga.get_primitive_standard_structure()
primitive.to(filename="output.cif")
```

**Query → Analyze → Calculate:**
```python
with MPRester() as mpr:
    structure = mpr.get_structure_by_material_id("mp-149")
    input_set = MPRelaxSet(structure)
    input_set.write_input("calc")
```

## Configuration

### Required Setup

**For Materials Project access:**
```bash
pmg config --add PMG_MAPI_KEY your_key_here
```

**For VASP POTCAR generation:**
```bash
pmg config --add PMG_VASP_PSP_DIR /path/to/vasp/potentials
```

### Configuration File

Location: `~/.pmgrc.yaml`

```yaml
PMG_MAPI_KEY: your_api_key_here
PMG_VASP_PSP_DIR: /path/to/vasp/potentials
PMG_DEFAULT_FUNCTIONAL: PBE
```

## Common Issues

### Issue: Cannot import pymatgen

**Solution:**
```bash
pip install pymatgen
# Or for all dependencies
pip install pymatgen[all]
```

### Issue: Materials Project API errors

**Solution:**
```bash
# Register at materialsproject.org
# Get API key from dashboard
pmg config --add PMG_MAPI_KEY your_key
```

### Issue: POTCAR generation fails

**Solution:**
```bash
# Set pseudopotential directory
pmg config --add PMG_VASP_PSP_DIR /path/to/vasp/potcars
# Ensure you have VASP license and pseudopotentials
```

### Issue: Import errors for plotting

**Solution:**
```bash
pip install matplotlib scipy plotly
# Or install all optional dependencies
pip install pymatgen[all]
```

## Best Practices

### Always Use Context Managers for API

```python
# Good
with MPRester() as mpr:
    structure = mpr.get_structure_by_material_id("mp-149")

# Bad
mpr = MPRester()
structure = mpr.get_structure_by_material_id("mp-149")
```

### Copy Before Modifying

```python
# Good - preserve original
original = Structure.from_file("POSCAR")
modified = original.copy()
modified.perturb(0.1)

# Bad - modifies original
original.perturb(0.1)
```

### Use Transformations for Reproducibility

```python
# Good - reproducible
from pymatgen.transformations.standard_transformations import SupercellTransformation
trans = SupercellTransformation([[2,0,0],[0,2,0],[0,0,1]])
supercell = trans.apply_transformation(structure)

# OK but less reproducible
supercell = structure * (2, 2, 1)
```

### Validate Results

```python
# Check convergence
vasprun = Vasprun("vasprun.xml")
if not vasprun.converged:
    print("WARNING: Calculation not converged")

# Check structure validity
if not structure.is_valid():
    print("WARNING: Structure may have overlapping atoms")
```

## External Resources

- **Official Documentation**: https://pymatgen.org/
- **Materials Project**: https://materialsproject.org/
- **GitHub**: https://github.com/materialsproject/pymatgen
- **Forum**: https://matsci.org/pymatgen
- **Tutorial**: https://pymatgen.org/usage.html

## Contributing

To extend this skill:
- Add more examples for specific use cases
- Create templates for common workflows
- Add journal-specific export formats
- Share tips and best practices

## License

This skill is part of the skillpack project.

## Support

For pymatgen issues:
- Check the [documentation](https://pymatgen.org/)
- Search the [forum](https://matsci.org/pymatgen)
- File issues on [GitHub](https://github.com/materialsproject/pymatgen/issues)

For this skill:
- Refer to `SKILL.md` for workflow routing
- Check reference files for detailed guides
- Run examples for working code
