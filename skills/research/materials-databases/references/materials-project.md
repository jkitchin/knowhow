# Materials Project API Reference

Comprehensive guide to the Materials Project API using the `mp-api` Python client.

## API Key Management

### Getting an API Key

1. Visit https://materialsproject.org/api
2. Login using ORCID or email
3. Click "Generate API Key"
4. Copy the generated key (long alphanumeric string)

### Setting Up Authentication

**Environment Variable (Recommended)**
```bash
export MP_API_KEY="your_api_key_here"

# Add to .bashrc or .zshrc for persistence
echo 'export MP_API_KEY="your_api_key_here"' >> ~/.bashrc
```

**Configuration File**
```bash
# Option 1: .mpapi.json
mkdir -p ~/.config
echo '{"MAPI_KEY": "your_api_key_here"}' > ~/.config/.mpapi.json

# Option 2: .pmgrc.yaml (legacy pymatgen format)
echo "PMG_MAPI_KEY: your_api_key_here" > ~/.pmgrc.yaml
```

**Direct in Code**
```python
from mp_api.client import MPRester

with MPRester(api_key="your_api_key_here") as mpr:
    pass
```

## MPRester Client

### Initialization

```python
from mp_api.client import MPRester

# Automatic (uses env var or config file)
with MPRester() as mpr:
    pass

# Manual API key
with MPRester(api_key="YOUR_KEY") as mpr:
    pass

# Custom endpoint (for testing)
with MPRester(endpoint="https://custom-endpoint.org") as mpr:
    pass
```

## Available Endpoints

The MPRester provides access to multiple specialized endpoints:

```python
with MPRester() as mpr:
    # Materials data
    mpr.materials.summary              # General materials properties
    mpr.materials.thermo               # Thermodynamic data
    mpr.materials.electronic_structure # Band structures, DOS
    mpr.materials.phonon               # Phonon data
    mpr.materials.elasticity           # Elastic tensors
    mpr.materials.magnetism            # Magnetic properties
    mpr.materials.surface_properties   # Surface energies
    mpr.materials.grain_boundaries     # Grain boundary data
    mpr.materials.substrates           # Substrate matching
    mpr.materials.xas                  # X-ray absorption spectra

    # Other data types
    mpr.molecules                      # Molecular structures
    mpr.synthesis                      # Synthesis recipes
    mpr.oxidation_states              # Oxidation state data
    mpr.electronic_structure_bandstructure  # Detailed band structures
    mpr.electronic_structure_dos      # Detailed DOS
```

## Materials Summary Endpoint

The most commonly used endpoint for general materials queries.

### Search Methods

```python
with MPRester() as mpr:
    # Search with criteria
    docs = mpr.materials.summary.search(...)

    # Get by material ID
    doc = mpr.materials.summary.get_data_by_id("mp-149")

    # Get multiple by IDs
    docs = mpr.materials.summary.get_data_by_id(["mp-149", "mp-1234"])
```

### Search Parameters

**By Composition**
```python
# Exact formula
docs = mpr.materials.summary.search(formula="Fe2O3")

# By elements
docs = mpr.materials.summary.search(elements=["Fe", "O"])

# Exclude elements
docs = mpr.materials.summary.search(
    elements=["Fe", "O"],
    exclude_elements=["H"]
)

# Number of elements
docs = mpr.materials.summary.search(
    elements=["Fe", "O"],
    num_elements=2  # Exactly 2 elements (binary)
)

# Chemical system
docs = mpr.materials.summary.search(chemsys="Fe-O")
```

**By Properties**
```python
# Band gap range
docs = mpr.materials.summary.search(band_gap=(1.0, 3.0))

# Energy above hull (stability)
docs = mpr.materials.summary.search(energy_above_hull=(0, 0.05))

# Formation energy
docs = mpr.materials.summary.search(formation_energy_per_atom=(-2, 0))

# Density range
docs = mpr.materials.summary.search(density=(5.0, 10.0))

# Volume range
docs = mpr.materials.summary.search(volume=(10, 100))

# Number of sites
docs = mpr.materials.summary.search(nsites=(1, 20))
```

**By Structure**
```python
# Crystal system
docs = mpr.materials.summary.search(crystal_system="cubic")

# Space group
docs = mpr.materials.summary.search(spacegroup_number=225)

# Space group symbol
docs = mpr.materials.summary.search(spacegroup_symbol="Fm-3m")
```

**By Stability and Theoretical Status**
```python
# Only stable materials
docs = mpr.materials.summary.search(is_stable=True)

# Theoretical or experimental
docs = mpr.materials.summary.search(theoretical=False)  # Experimental
```

**Combining Criteria**
```python
# Multiple filters
docs = mpr.materials.summary.search(
    elements=["Li", "Co", "O"],
    energy_above_hull=(0, 0.01),
    band_gap=(0, 0.5),
    theoretical=True
)
```

### Specifying Fields

Always specify fields to reduce data transfer and improve performance:

```python
docs = mpr.materials.summary.search(
    formula="GaN",
    fields=["material_id", "formula_pretty", "band_gap", "energy_per_atom"]
)

# Access fields
for doc in docs:
    print(f"{doc.material_id}: {doc.formula_pretty}")
    print(f"Band gap: {doc.band_gap} eV")
```

### Common Field Names

**Identifiers and Composition**
- `material_id` - Materials Project ID (e.g., "mp-149")
- `formula_pretty` - Prettified chemical formula
- `formula_anonymous` - Anonymous formula (e.g., "AB2")
- `elements` - List of element symbols
- `nelements` - Number of unique elements
- `composition` - Composition object
- `composition_reduced` - Reduced composition

**Energetics**
- `energy_per_atom` - Total energy per atom (eV/atom)
- `formation_energy_per_atom` - Formation energy (eV/atom)
- `energy_above_hull` - Energy above convex hull (eV/atom)
- `is_stable` - Boolean: on convex hull
- `equilibrium_reaction_energy_per_atom` - Decomposition energy

**Electronic Properties**
- `band_gap` - Band gap (eV)
- `is_gap_direct` - Boolean: direct band gap
- `is_metal` - Boolean: metallic
- `efermi` - Fermi energy (eV)

**Structural Properties**
- `volume` - Unit cell volume (ų)
- `density` - Density (g/cm³)
- `density_atomic` - Atomic packing density
- `nsites` - Number of atoms in unit cell
- `symmetry` - Symmetry information (space group, etc.)
- `crystal_system` - Crystal system (cubic, etc.)
- `spacegroup_number` - International space group number
- `spacegroup_symbol` - Hermann-Mauguin symbol

**Other Properties**
- `theoretical` - Boolean: is it theoretical
- `database_IDs` - External database IDs (ICSD, etc.)
- `has_props` - List of available property calculations
- `deprecated` - Boolean: deprecated entry
- `warnings` - List of warnings about the calculation

### Pagination for Large Results

```python
# Get results in chunks
docs = mpr.materials.summary.search(
    elements=["O"],
    num_chunks=10,
    chunk_size=1000,
    fields=["material_id", "formula_pretty"]
)

# Process as iterator
for doc in docs:
    process(doc)
```

## Structure Retrieval

### Get Structure by Material ID

```python
# Get pymatgen Structure object
structure = mpr.get_structure_by_material_id("mp-149")

# Get multiple structures
structures = mpr.get_structure_by_material_id(["mp-149", "mp-1234"])

# Access structure properties
print(structure.formula)
print(structure.lattice)
print(structure.species)
print(structure.cart_coords)
```

### Structure from Search Results

```python
# Get structure directly in search
docs = mpr.materials.summary.search(
    formula="Si",
    fields=["material_id", "structure"]
)

for doc in docs:
    structure = doc.structure
    # Use structure
```

### Save Structures

```python
structure = mpr.get_structure_by_material_id("mp-149")

# POSCAR format
structure.to(filename="POSCAR")

# CIF format
structure.to(filename="structure.cif")

# JSON format
structure.to(filename="structure.json")

# XYZ format
structure.to(filename="structure.xyz")

# Python object
import pickle
with open("structure.pkl", "wb") as f:
    pickle.dump(structure, f)
```

## Electronic Structure Data

### Band Structures

```python
# Search for materials with band structure data
docs = mpr.materials.electronic_structure.search(
    elements=["Ga", "N"],
    fields=["material_id", "band_gap", "is_gap_direct"]
)

# Get band structure object
bs_doc = mpr.materials.electronic_structure.get_data_by_id("mp-149")
band_structure = bs_doc.band_structure

# Or use dedicated endpoint
bs = mpr.electronic_structure_bandstructure.get_data_by_id("mp-149")
```

### Density of States

```python
# Get DOS
dos_doc = mpr.materials.electronic_structure.get_data_by_id("mp-149")
dos = dos_doc.dos

# Or use dedicated endpoint
dos = mpr.electronic_structure_dos.get_data_by_id("mp-149")

# Access DOS data
energies = dos.energies
densities = dos.densities
```

## Thermodynamic Data

```python
# Get thermo data
thermo_docs = mpr.materials.thermo.search(
    formula="Li2O",
    fields=["material_id", "thermo"]
)

# Access thermodynamic properties
for doc in thermo_docs:
    thermo = doc.thermo
    print(thermo.energy)
    print(thermo.formation_energy_per_atom)
```

## Phase Diagrams

```python
from mp_api.client import MPRester

with MPRester() as mpr:
    # Get phase diagram data
    phase_diagram = mpr.get_phase_diagram_by_chemsys("Li-Fe-O")

    # Analyze stability
    entry = mpr.get_entry_by_material_id("mp-1234")
    decomp, e_above_hull = phase_diagram.get_decomp_and_e_above_hull(entry)

    print(f"Energy above hull: {e_above_hull} eV/atom")
    print(f"Decomposition: {decomp}")
```

## Phonon Data

```python
# Search for phonon data
phonon_docs = mpr.materials.phonon.search(
    formula="Si",
    fields=["material_id", "has_imaginary_modes"]
)

# Get phonon band structure
phonon_bs = mpr.materials.phonon.get_data_by_id("mp-149")
```

## Elastic Properties

```python
# Get elastic tensor data
elastic_docs = mpr.materials.elasticity.search(
    elements=["Fe"],
    fields=["material_id", "bulk_modulus", "shear_modulus"]
)

for doc in elastic_docs:
    print(f"Bulk modulus: {doc.bulk_modulus} GPa")
    print(f"Shear modulus: {doc.shear_modulus} GPa")
```

## Surface Properties

```python
# Get surface energy data
surface_docs = mpr.materials.surface_properties.search(
    elements=["Pt"],
    fields=["material_id", "weighted_surface_energy"]
)
```

## Molecules

```python
# Search for molecules
mol_docs = mpr.molecules.search(
    elements=["C", "H", "O"],
    nelements=3,
    fields=["molecule_id", "formula_alphabetical", "charge", "spin_multiplicity"]
)
```

## Advanced Query Techniques

### OR Queries

```python
# Multiple formulas
docs = mpr.materials.summary.search(
    formula=["GaN", "GaP", "GaAs"],
    fields=["material_id", "formula_pretty", "band_gap"]
)
```

### Sorting Results

```python
# Sort by property (done client-side)
docs = mpr.materials.summary.search(
    elements=["O"],
    band_gap=(1, 3),
    fields=["material_id", "band_gap"]
)

sorted_docs = sorted(docs, key=lambda x: x.band_gap if x.band_gap else 0)
```

### Filtering Results

```python
# Filter after retrieval
docs = mpr.materials.summary.search(
    elements=["O"],
    fields=["material_id", "formula_pretty", "band_gap", "nsites"]
)

# Filter for small unit cells
small_cell_docs = [doc for doc in docs if doc.nsites < 10]
```

## Error Handling

```python
from mp_api.client import MPRester
from mp_api.client.core import MPRestError

try:
    with MPRester() as mpr:
        docs = mpr.materials.summary.search(formula="InvalidFormula")

except MPRestError as e:
    # API-specific errors (auth, rate limit, etc.)
    print(f"API Error: {e}")

except ValueError as e:
    # Invalid parameter values
    print(f"Invalid input: {e}")

except ConnectionError as e:
    # Network issues
    print(f"Connection error: {e}")

except Exception as e:
    # Unexpected errors
    print(f"Unexpected error: {e}")
```

## Rate Limits and Best Practices

### Rate Limits
- Materials Project is generally generous with rate limits
- For very large queries, use pagination
- Cache results locally when possible

### Best Practices

1. **Request only needed fields**
   ```python
   # Good - specific fields
   docs = mpr.materials.summary.search(
       formula="Si",
       fields=["material_id", "band_gap"]
   )

   # Less efficient - all fields
   docs = mpr.materials.summary.search(formula="Si")
   ```

2. **Use pagination for large results**
   ```python
   docs = mpr.materials.summary.search(
       elements=["O"],
       chunk_size=1000
   )
   ```

3. **Cache results**
   ```python
   import pickle

   # Save
   with open("results.pkl", "wb") as f:
       pickle.dump(docs, f)

   # Load
   with open("results.pkl", "rb") as f:
       docs = pickle.load(f)
   ```

4. **Narrow searches when possible**
   ```python
   # More specific search
   docs = mpr.materials.summary.search(
       formula="TiO2",
       spacegroup_number=136
   )
   ```

## Integration with Pymatgen

Materials Project structures are pymatgen Structure objects:

```python
from pymatgen.core import Structure
from pymatgen.analysis.structure_analyzer import SpacegroupAnalyzer
from pymatgen.io.ase import AseAtomsAdaptor

# Get structure
structure = mpr.get_structure_by_material_id("mp-149")

# Analyze symmetry
sga = SpacegroupAnalyzer(structure)
print(f"Space group: {sga.get_space_group_symbol()}")

# Convert to ASE
atoms = AseAtomsAdaptor.get_atoms(structure)

# Primitive cell
primitive = structure.get_primitive_structure()

# Conventional cell
conventional = sga.get_conventional_standard_structure()
```

## Resources

- **API Documentation**: https://materialsproject.org/api
- **GitHub**: https://github.com/materialsproject/api
- **Pymatgen Docs**: https://pymatgen.org
- **Forum**: https://matsci.org/materials-project
