# Materials Databases Quick Reference

## Installation

```bash
# Materials Project
pip install mp-api pymatgen

# AFLOW (optional)
pip install aflow requests
```

## API Key Setup

```bash
# Materials Project - set environment variable
export MP_API_KEY="your_api_key_here"

# Get key from: https://materialsproject.org/api
```

## Materials Project - Common Queries

### Basic Setup

```python
from mp_api.client import MPRester

# Use environment variable or config file
with MPRester() as mpr:
    # Your queries here
    pass

# Or specify API key directly
with MPRester(api_key="YOUR_KEY") as mpr:
    pass
```

### Search by Formula

```python
# Simple formula search
docs = mpr.materials.summary.search(formula="Si")

# With specific fields
docs = mpr.materials.summary.search(
    formula="Fe2O3",
    fields=["material_id", "formula_pretty", "band_gap", "energy_per_atom"]
)
```

### Search by Material ID

```python
# Get structure
structure = mpr.get_structure_by_material_id("mp-149")

# Get full data
doc = mpr.materials.summary.get_data_by_id("mp-149")
```

### Search by Properties

```python
# Band gap range
docs = mpr.materials.summary.search(
    band_gap=(1.0, 3.0),
    fields=["material_id", "formula_pretty", "band_gap"]
)

# Stability (energy above hull)
docs = mpr.materials.summary.search(
    energy_above_hull=(0, 0.01),  # Nearly stable
    fields=["material_id", "energy_above_hull"]
)

# By elements
docs = mpr.materials.summary.search(
    elements=["Li", "Co", "O"],
    num_elements=3,  # Exactly 3 elements
    fields=["material_id", "formula_pretty"]
)
```

### Common Field Names

```python
fields = [
    "material_id",           # MP ID (e.g., mp-149)
    "formula_pretty",        # Chemical formula
    "band_gap",             # Band gap (eV)
    "is_gap_direct",        # Direct/indirect gap
    "energy_per_atom",      # Energy per atom (eV)
    "energy_above_hull",    # Stability (eV/atom)
    "formation_energy_per_atom",  # Formation energy
    "volume",               # Unit cell volume
    "density",              # Density (g/cm³)
    "nsites",              # Number of atoms in unit cell
    "elements",            # List of elements
    "symmetry",            # Space group info
    "is_stable",           # Boolean stability
    "theoretical",         # Is it theoretical
]
```

### Available Endpoints

```python
# General properties
mpr.materials.summary

# Thermodynamics
mpr.materials.thermo

# Electronic structure (band structure, DOS)
mpr.materials.electronic_structure

# Phonons
mpr.materials.phonon

# Elastic properties
mpr.materials.elasticity

# Surface properties
mpr.materials.surface_properties

# Molecules
mpr.molecules
```

## AFLOW - REST API

### URL Structure

```
http://aflowlib.duke.edu/AFLOWDATA/<catalog>/<system>/<file>?<directives>
http://aflowlib.duke.edu/search/API/?<AFLUX_query>
```

### Basic Queries (Python requests)

```python
import requests

# Get property
url = "http://aflowlib.duke.edu/AFLOWDATA/ICSD_WEB/FCC/Ag1/?enthalpy_formation_atom"
response = requests.get(url)
value = response.text

# Get structure (POSCAR format)
url = "http://aflowlib.duke.edu/AFLOWDATA/ICSD_WEB/FCC/Ag1/?geometry"
poscar = requests.get(url).text

# List available properties
url = "http://aflowlib.duke.edu/AFLOWDATA/ICSD_WEB/FCC/Ag1/?keywords"
keywords = requests.get(url).text
```

### AFLUX Search Syntax

```python
# Search by species and band gap
url = "http://aflowlib.duke.edu/search/API/?species(Au),Egap(5*)"
results = requests.get(url).json()

# Search by composition and formation enthalpy
url = "http://aflowlib.duke.edu/search/API/?species(Ti,O),nspecies(2),enthalpy_formation_atom(-3*,0*)"
results = requests.get(url).json()

# Multiple criteria
url = "http://aflowlib.duke.edu/search/API/?species(Fe,O),Egap(1*,3*),catalog(ICSD)"
results = requests.get(url).json()
```

### Common AFLUX Keywords

```
species(El1,El2,...)         # Chemical species
nspecies(N)                  # Number of species
Egap(min*,max*)             # Band gap range (eV)
enthalpy_formation_atom(min*,max*)  # Formation enthalpy (eV/atom)
catalog(ICSD)               # Database catalog
volume_cell(min*,max*)      # Cell volume range
spacegroup_relax            # Space group number
```

### Common Directives (Properties)

```
?keywords                   # List all available properties
?geometry                   # Structure (POSCAR)
?enthalpy_formation_atom    # Formation enthalpy (eV/atom)
?Egap                      # Band gap (eV)
?volume_cell               # Cell volume (Å³)
?density                   # Density (g/cm³)
?spacegroup_relax          # Space group number
?Bravais_lattice_relax     # Bravais lattice type
?files                     # List of all available files
```

### Using aflow Python Package

```python
import aflow

# Search
results = aflow.search(filter='species(Au),Egap(5*)')

# Access properties
for entry in results:
    print(entry.enthalpy_formation_atom)
    print(entry.Egap)
    structure = entry.atoms  # ASE Atoms object

# Get specific entry
K = aflow.K(catalog='ICSD', file='POSCAR')
print(K.enthalpy_formation_atom)
atoms = K.atoms
```

## Structure Manipulation

### Save Structures

```python
# Materials Project (pymatgen Structure)
structure = mpr.get_structure_by_material_id("mp-149")

# Save as POSCAR
structure.to(filename="POSCAR")

# Save as CIF
structure.to(filename="structure.cif")

# Save as JSON
structure.to(filename="structure.json")

# Convert to ASE
from pymatgen.io.ase import AseAtomsAdaptor
atoms = AseAtomsAdaptor.get_atoms(structure)
```

### AFLOW Structures

```python
# Get POSCAR text
url = "http://aflowlib.duke.edu/AFLOWDATA/ICSD_WEB/FCC/Ag1/?geometry"
poscar_text = requests.get(url).text

# Save to file
with open("POSCAR", "w") as f:
    f.write(poscar_text)

# Parse with pymatgen
from pymatgen.core import Structure
structure = Structure.from_str(poscar_text, fmt="poscar")
```

## Common Workflows

### Find and Download Structure

```python
# Materials Project
with MPRester() as mpr:
    docs = mpr.materials.summary.search(
        formula="GaN",
        fields=["material_id", "band_gap"]
    )

    # Get the one with smallest band gap
    best = min(docs, key=lambda x: x.band_gap if x.band_gap else float('inf'))

    # Download structure
    structure = mpr.get_structure_by_material_id(best.material_id)
    structure.to(filename="GaN.cif")
```

### Screen for Candidates

```python
# Find stable semiconducting oxides
with MPRester() as mpr:
    candidates = mpr.materials.summary.search(
        elements=["O"],
        energy_above_hull=(0, 0.05),
        band_gap=(1.5, 3.5),
        num_elements=(2, 3),
        fields=["material_id", "formula_pretty", "band_gap", "energy_above_hull"]
    )

    for doc in candidates:
        print(f"{doc.formula_pretty}: Egap={doc.band_gap:.2f} eV, "
              f"Ehull={doc.energy_above_hull:.3f} eV/atom")
```

### Compare Databases

```python
# Get data from both databases
formula = "TiO2"

# Materials Project
with MPRester() as mpr:
    mp_docs = mpr.materials.summary.search(
        formula=formula,
        fields=["material_id", "band_gap", "energy_per_atom"]
    )

# AFLOW
aflow_url = f"http://aflowlib.duke.edu/search/API/?species(Ti,O),nspecies(2)"
aflow_data = requests.get(aflow_url).json()
```

## Error Handling

```python
from mp_api.client import MPRester
from mp_api.client.core import MPRestError

try:
    with MPRester() as mpr:
        docs = mpr.materials.summary.search(formula="XYZ")
except MPRestError as e:
    print(f"API Error: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Tips

- Use `fields` parameter to request only needed data
- Cache results to avoid repeated API calls
- Materials Project has rate limits (but they're generous)
- AFLOW queries can be slow for very broad searches
- Always check `energy_above_hull` for thermodynamic stability
- Use `is_gap_direct` to distinguish direct/indirect semiconductors
