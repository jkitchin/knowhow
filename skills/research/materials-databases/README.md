# Materials Databases Skill

Expert assistant for accessing materials science databases (AFLOW and Materials Project) to query crystal structures, materials properties, thermodynamic data, and computational results.

## What This Skill Does

This skill enables Claude to help you:
- Access two major computational materials databases (Materials Project and AFLOW)
- Query crystal structures and download them in various formats
- Search for materials by composition, properties, or stability
- Retrieve electronic structure data (band gaps, DOS, band structures)
- Get thermodynamic properties (formation energies, phase stability)
- Access elastic, phonon, and surface properties
- Perform large-scale materials screening

## When to Use This Skill

Use this skill when you need to:
- Find existing computational data for a material
- Screen materials databases for candidates with specific properties
- Compare experimental and computational structures
- Get band gaps, formation energies, or other calculated properties
- Build datasets for machine learning from databases
- Cross-reference data between different databases
- Download crystal structures for further calculations

## Databases Covered

### Materials Project (MP)
- **Size**: 150,000+ inorganic compounds
- **Data**: Electronic structure, phonons, elasticity, surfaces, batteries, molecules
- **Access**: Python API (mp-api) with rich query capabilities
- **Requires**: Free API key
- **Best for**: Detailed electronic/phonon data, phase diagrams, pymatgen integration

### AFLOW (Automatic Flow)
- **Size**: 3.5+ million calculated materials
- **Data**: Structures, thermodynamics, elastic properties, ICSD references
- **Access**: REST API (no package required)
- **Requires**: No API key
- **Best for**: Large-scale screening, elastic properties, simple queries

## Quick Start

### 1. Install Required Packages

```bash
# Materials Project API client
pip install mp-api

# Structure manipulation (recommended)
pip install pymatgen ase

# AFLOW (optional - can use requests instead)
pip install aflow requests
```

### 2. Get Materials Project API Key

1. Visit: https://materialsproject.org/api
2. Click "Generate API Key" (login with ORCID or email)
3. Copy your API key

### 3. Set Up Authentication

**Option A: Environment variable (recommended)**
```bash
export MP_API_KEY="your_api_key_here"
```

**Option B: Configuration file**
```bash
echo '{"MAPI_KEY": "your_api_key_here"}' > ~/.config/.mpapi.json
```

### 4. Test Your Setup

```python
from mp_api.client import MPRester

# This should work without errors
with MPRester() as mpr:
    structure = mpr.get_structure_by_material_id("mp-149")
    print(f"Got structure: {structure.formula}")
```

## Example Usage

### Find Band Gap of Silicon

```python
from mp_api.client import MPRester

with MPRester() as mpr:
    docs = mpr.materials.summary.search(
        formula="Si",
        fields=["material_id", "formula_pretty", "band_gap"]
    )
    for doc in docs:
        print(f"{doc.material_id}: {doc.formula_pretty}, Egap = {doc.band_gap} eV")
```

### Screen for Stable Semiconductors

```python
with MPRester() as mpr:
    docs = mpr.materials.summary.search(
        elements=["Ga", "N"],
        energy_above_hull=(0, 0.05),  # Thermodynamically stable
        band_gap=(1.0, 4.0),  # Semiconducting range
        fields=["material_id", "formula_pretty", "band_gap", "energy_above_hull"]
    )
```

### Get Structure from AFLOW

```python
import requests

# Get POSCAR file for FCC Silver
url = "http://aflowlib.duke.edu/AFLOWDATA/ICSD_WEB/FCC/Ag1/?geometry"
poscar = requests.get(url).text
print(poscar)
```

## Files in This Skill

- `SKILL.md` - Complete skill instructions for Claude
- `README.md` - This file (overview and setup)
- `QUICK_REFERENCE.md` - Quick syntax reference
- `references/materials-project.md` - Detailed Materials Project API documentation
- `references/aflow.md` - AFLOW REST API and AFLUX query syntax
- `examples/mp_search_examples.py` - Materials Project query examples
- `examples/aflow_search_examples.py` - AFLOW query examples
- `examples/structure_download.py` - Download and save structures
- `examples/property_screening.py` - Multi-property screening workflow

## Common Use Cases

1. **Literature Support**: "Find the band gap of GaN from Materials Project"
2. **Structure Retrieval**: "Download the crystal structure of rutile TiO2"
3. **Materials Screening**: "Find all stable ternary oxides with band gaps between 2-3 eV"
4. **Data Collection**: "Get formation energies for all binary transition metal oxides"
5. **Cross-Database**: "Compare elastic constants between AFLOW and Materials Project"
6. **Phase Stability**: "Check if Li2MnO3 is thermodynamically stable"

## Tips

- Always specify `fields` in Materials Project queries to get only what you need
- Use AFLOW for quick lookups without API authentication
- Materials Project has better Python integration and documentation
- AFLOW has more entries but Materials Project has richer property data
- Combine both databases for comprehensive literature reviews
- Cache results locally to avoid repeated API calls

## Resources

- **Materials Project**: https://materialsproject.org
  - API Docs: https://materialsproject.org/api
  - Python Client: https://github.com/materialsproject/api

- **AFLOW**: https://aflow.org
  - Documentation: https://aflow.org/documentation/
  - REST API: http://aflowlib.duke.edu

- **Pymatgen**: https://pymatgen.org (structure analysis toolkit)

## Troubleshooting

**"MPRestError: Unauthorized"**
- Check that your API key is set correctly
- Verify the key at https://materialsproject.org/api

**AFLOW queries timing out**
- Try more specific search criteria
- AFLOW database is very large - narrow your search

**No results found**
- Check formula spelling (case-sensitive in some APIs)
- Try broader search criteria
- Some properties may not be available for all materials

**Import errors**
- Ensure mp-api is installed: `pip install mp-api`
- Update to latest version: `pip install --upgrade mp-api`

## Version Information

- Skill created for mp-api v0.41+ (2024)
- Compatible with Materials Project next-gen API
- AFLOW REST API (current as of 2024)
- Pymatgen 2023.x and later recommended
