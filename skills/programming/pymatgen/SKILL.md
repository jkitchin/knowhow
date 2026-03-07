---
name: pymatgen
description: |
  Comprehensive guidance for using pymatgen (Python Materials Genomics) for computational
  materials science. Covers structure creation and manipulation, file I/O (CIF, POSCAR, XYZ),
  symmetry analysis, Materials Project API integration, phase diagrams, electronic structure
  analysis, and DFT input generation. Use when working with crystal structures, materials
  properties, computational chemistry calculations, or materials databases. Triggers include
  'pymatgen', 'crystal structure', 'Materials Project', 'CIF file', 'POSCAR', 'band structure',
  'phase diagram', or materials analysis tasks.
allowed-tools: ["*"]
---

# Pymatgen Materials Analysis

Systematic guidance for using pymatgen to analyze crystal structures, access materials databases,
and interface with computational chemistry codes.

## Pymatgen Workflow

### 1. Identify Task Type

**What do you want to do?**

**Structure Creation/Loading:**
- Create structure from scratch → `references/core-objects.md`
- Read from file (CIF, POSCAR, XYZ) → `references/file-io.md`
- Get from Materials Project → `references/materials-project.md`
- Generate from symmetry → `references/structure-analysis.md`

**Structure Analysis:**
- Analyze symmetry/space groups → `references/structure-analysis.md`
- Compare structures → `references/structure-analysis.md`
- Calculate properties → `references/properties.md`
- Visualize structures → `references/visualization.md`

**Structure Manipulation:**
- Create supercells/slabs → `references/transformations.md`
- Substitute atoms → `references/transformations.md`
- Apply symmetry operations → `references/transformations.md`
- Interpolate for NEB → `references/transformations.md`

**Materials Database:**
- Query Materials Project → `references/materials-project.md`
- Retrieve structures/properties → `references/materials-project.md`
- Build phase diagrams → `references/phase-diagrams.md`

**Electronic Structure:**
- Parse band structures → `references/electronic-structure.md`
- Plot DOS → `references/electronic-structure.md`
- Analyze VASP outputs → `references/vasp-integration.md`

**Input Generation:**
- Create VASP inputs → `references/vasp-integration.md`
- Generate Gaussian inputs → `references/file-io.md`
- Set up calculations → `references/vasp-integration.md`

### 2. Core Pymatgen Workflow

**Basic pattern:**
```python
# 1. Import modules
from pymatgen.core import Structure, Lattice, Element

# 2. Load or create structure
structure = Structure.from_file("POSCAR")

# 3. Analyze or manipulate
print(f"Formula: {structure.composition.reduced_formula}")
print(f"Space group: {structure.get_space_group_info()}")

# 4. Transform if needed
supercell = structure * (2, 2, 1)  # 2x2x1 supercell

# 5. Write output
supercell.to(filename="POSCAR_supercell")
```

## Quick Reference - Common Tasks

**Load structure:** `Structure.from_file("file.cif")` - Auto-detects format
**Create structure:** See `references/core-objects.md` for Element, Lattice, Structure creation
**Analyze symmetry:** `SpacegroupAnalyzer(struct).get_space_group_symbol()`
**Make supercell:** `structure * (2, 2, 1)` or use transformations
**Query MP:** `MPRester(key).get_structure_by_material_id("mp-149")`
**Generate VASP:** `MPRelaxSet(struct).write_input("dir")`
**Plot bands/DOS:** See `references/electronic-structure.md`

Detailed examples for all tasks in reference files.

## Task Routing

### Core Objects and Creation

**Route to:** `references/core-objects.md`

**When:**
- Creating structures from scratch
- Understanding Element, Site, Structure classes
- Working with Lattice objects
- Creating molecules
- Composition analysis

**Key classes:**
- Element, Species
- Lattice
- Site, PeriodicSite
- Structure, Molecule
- Composition

### File Input/Output

**Route to:** `references/file-io.md`

**When:**
- Reading CIF, POSCAR, XYZ files
- Writing structures to files
- Format conversion
- Parsing calculation outputs
- Working with multiple formats

**Supported formats:**
- CIF (Crystallographic Information File)
- POSCAR/CONTCAR (VASP)
- XYZ (molecular coordinates)
- JSON (serialization)
- Many computational chemistry codes

### Structure Analysis

**Route to:** `references/structure-analysis.md`

**When:**
- Finding space groups
- Symmetry operations
- Comparing structures
- Getting primitive/conventional cells
- Neighbor analysis

**Key tools:**
- SpacegroupAnalyzer
- StructureMatcher
- VoronoiAnalysis
- Distance calculations

### Structure Transformations

**Route to:** `references/transformations.md`

**When:**
- Creating supercells
- Making slabs/surfaces
- Substituting elements
- Perturbing structures
- High-throughput workflows

**Key modules:**
- pymatgen.transformations.standard_transformations
- pymatgen.transformations.advanced_transformations
- pymatgen.alchemy

### Materials Project API

**Route to:** `references/materials-project.md`

**When:**
- Querying materials database
- Getting structures by formula
- Retrieving calculated properties
- Accessing experimental data
- Building chemical systems

**Key class:**
- MPRester for API access
- Requires API key from materialsproject.org

### Phase Diagrams

**Route to:** `references/phase-diagrams.md`

**When:**
- Constructing phase diagrams
- Analyzing stability
- Finding decomposition products
- Pourbaix diagrams
- Grand potential diagrams

**Key classes:**
- PhaseDiagram
- PhaseDiagramError (for stability analysis)
- PourbaixDiagram

### Electronic Structure

**Route to:** `references/electronic-structure.md`

**When:**
- Analyzing band structures
- Plotting DOS
- Finding band gaps
- Analyzing orbital contributions
- Electronic property calculations

**Key modules:**
- pymatgen.electronic_structure.bandstructure
- pymatgen.electronic_structure.dos
- pymatgen.electronic_structure.plotter

### VASP Integration

**Route to:** `references/vasp-integration.md`

**When:**
- Generating VASP inputs
- Parsing VASP outputs
- Creating input sets
- High-throughput VASP
- Custom INCAR settings

**Key classes:**
- MPRelaxSet, MPStaticSet, etc.
- Vasprun, Outcar parsers
- Poscar, Incar classes

## Common Patterns

**Pattern 1: Structure Analysis**
- Load → Analyze composition/symmetry → Get primitive/conventional
- See `examples/structure_analysis.py` for complete workflow

**Pattern 2: Materials Project to Calculation**
- Query MP → Get structure → Generate VASP inputs → Customize settings
- See `examples/mp_to_vasp.py`

**Pattern 3: High-Throughput Substitution**
- Load base structure → Apply transformations → Write outputs
- See `examples/substitution_study.py`

**Pattern 4: Electronic Structure Analysis**
- Parse vasprun.xml → Extract band structure/DOS → Plot and analyze
- See `examples/band_structure.py`

All patterns detailed in `examples/` directory with complete code.

## Installation and Setup

### Install Pymatgen

```bash
pip install pymatgen
# Or with optional dependencies
pip install pymatgen[all]
```

### Configure Materials Project API

```bash
# Register at materialsproject.org to get API key
pmg config --add PMG_MAPI_KEY your_api_key_here
```

### Set VASP Pseudopotential Path

```bash
pmg config --add PMG_VASP_PSP_DIR /path/to/vasp/potentials
```

### Configuration File

Located at `~/.pmgrc.yaml`:
```yaml
PMG_MAPI_KEY: your_api_key_here
PMG_VASP_PSP_DIR: /path/to/vasp/potentials
PMG_DEFAULT_FUNCTIONAL: PBE
```

## Common Issues and Solutions

### Issue: Structure not defined

**Problem:** `NameError: name 'Structure' is not defined`

**Solution:**
```python
from pymatgen.core import Structure
```

### Issue: API key not working

**Problem:** MPRester returns authentication error

**Solution:**
1. Get API key from materialsproject.org (free account)
2. Configure: `pmg config --add PMG_MAPI_KEY your_key`
3. Or pass directly: `MPRester("your_key")`

### Issue: POTCAR generation fails

**Problem:** Cannot write POTCAR files

**Solution:**
1. Set PSP directory: `pmg config --add PMG_VASP_PSP_DIR /path`
2. Ensure VASP pseudopotentials are properly installed
3. Check directory structure matches expected format

### Issue: Import errors for optional dependencies

**Problem:** `ImportError` for plotting or specialized modules

**Solution:**
```bash
pip install pymatgen[all]  # Install all optional dependencies
# Or specific ones:
pip install matplotlib  # For plotting
pip install scipy      # For analysis tools
```

## Best Practices

### Object-Oriented Approach

- Use Structure/Molecule objects, not raw coordinates
- Leverage built-in methods (composition, symmetry, etc.)
- Chain operations for clarity

### Serialization

- Use `as_dict()` / `from_dict()` for persistence
- Prefer JSON over pickle for code evolution
- Use MontyEncoder/MontyDecoder for complex objects

### Transformations

- Use Transformation classes for reproducibility
- TransformedStructure tracks history
- Alchemy framework for high-throughput

### Input Sets

- Use MPRelaxSet, MPStaticSet for standard calculations
- Customize by modifying Incar after creation
- Use InputGenerator for custom workflows

### Materials Project

- Use context manager: `with MPRester(...) as mpr:`
- Batch queries when possible
- Cache results to avoid repeated API calls

## Examples Directory

See `examples/` for complete workflows:
- `structure_analysis.py` - Comprehensive structure analysis
- `mp_query.py` - Materials Project queries
- `phase_diagram.py` - Phase diagram construction
- `band_structure.py` - Electronic structure analysis
- `vasp_workflow.py` - VASP calculation setup
- `substitution_study.py` - High-throughput substitutions

## Reference Documentation

- `references/core-objects.md` - Element, Structure, Lattice, Composition
- `references/file-io.md` - Reading/writing all file formats
- `references/structure-analysis.md` - Symmetry, comparison, neighbors
- `references/transformations.md` - Supercells, substitutions, perturbations
- `references/materials-project.md` - API usage and queries
- `references/phase-diagrams.md` - Phase diagram construction
- `references/electronic-structure.md` - Band structures and DOS
- `references/vasp-integration.md` - VASP input/output handling
- `references/properties.md` - Calculated properties
- `references/visualization.md` - Structure visualization

## External Resources

- **Official docs:** https://pymatgen.org/
- **Materials Project:** https://materialsproject.org/
- **GitHub:** https://github.com/materialsproject/pymatgen
- **Forum:** https://matsci.org/pymatgen
