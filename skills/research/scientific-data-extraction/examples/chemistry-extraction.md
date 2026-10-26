# Example: Chemistry-Specific Data Extraction

This example demonstrates specialized extraction of chemical and materials data from scientific literature.

## Scenario

You have a materials science paper containing:
- Material property data (bandgaps, melting points, conductivity)
- Chemical reactions with conditions
- Synthesis procedures
- Chemical structure images

Goal: Extract all chemistry-related data in a structured format.

## Step 1: Document Assessment

```python
import pymupdf4llm
import re

pdf_path = "materials_paper.pdf"

# Extract text for analysis
text = pymupdf4llm.to_markdown(pdf_path)

def detect_chemistry_content(text: str) -> dict:
    """Detect chemistry-specific content in document."""

    patterns = {
        'chemical_formulas': r'\b[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\b',
        'reactions': r'→|⟶|⇌|⟹',
        'temperatures': r'\d+\.?\d*\s*°C|\d+\.?\d*\s*K',
        'percentages': r'\d+\.?\d*\s*%',
        'concentrations': r'\d+\.?\d*\s*(?:mol/L|M|mM|μM|mg/mL)',
        'energies': r'\d+\.?\d*\s*(?:eV|meV|kJ/mol|kcal/mol)',
        'wavelengths': r'\d+\.?\d*\s*(?:nm|μm|Å)',
        'smiles': r'[A-Za-z0-9@+\-\[\]()=#%]+',  # Simple SMILES pattern
        'inchi': r'InChI=[^\s]+',
    }

    results = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text)
        results[name] = {
            'count': len(matches),
            'examples': list(set(matches))[:5]  # First 5 unique
        }

    # Identify likely sections
    section_keywords = {
        'synthesis': ['synthesis', 'preparation', 'fabrication'],
        'characterization': ['characterization', 'analysis', 'measurement'],
        'properties': ['properties', 'bandgap', 'conductivity', 'melting'],
        'reactions': ['reaction', 'mechanism', 'pathway']
    }

    results['sections'] = {}
    for section_type, keywords in section_keywords.items():
        found = any(kw in text.lower() for kw in keywords)
        results['sections'][section_type] = found

    return results

content_analysis = detect_chemistry_content(text)
print("Chemistry content detected:")
for key, value in content_analysis.items():
    print(f"  {key}: {value}")
```

## Step 2: Property Extraction with ChemDataExtractor

```python
from chemdataextractor import Document
from chemdataextractor.model import Compound

# Load document
doc = Document.from_file(pdf_path)

# Extract all records
all_records = []
for record in doc.records:
    data = record.serialize()
    if data:
        all_records.append(data)

print(f"Total records extracted: {len(all_records)}")

# Categorize by property type
property_types = {}
for record in all_records:
    for prop_type in record.keys():
        if prop_type not in property_types:
            property_types[prop_type] = []
        property_types[prop_type].append(record[prop_type])

print("\nProperty types found:")
for prop_type, records in property_types.items():
    print(f"  {prop_type}: {len(records)} records")
```

### Processing Specific Property Types

```python
def extract_melting_points(records: list) -> list:
    """Extract and normalize melting point data."""
    results = []

    for record in records:
        if 'MeltingPoint' in record:
            mp_data = record['MeltingPoint']
            compound_names = mp_data.get('compound', {}).get('names', [])
            compound_labels = mp_data.get('compound', {}).get('labels', [])

            for value_entry in mp_data.get('value', []):
                value = value_entry.get('value')
                units = value_entry.get('units', '°C')

                # Normalize to Kelvin
                if value:
                    numeric_value = float(value)
                    if '°C' in units:
                        kelvin = numeric_value + 273.15
                    elif '°F' in units:
                        kelvin = (numeric_value - 32) * 5/9 + 273.15
                    else:
                        kelvin = numeric_value

                    results.append({
                        'compound': compound_names[0] if compound_names else 'Unknown',
                        'formula': compound_labels[0] if compound_labels else None,
                        'value': numeric_value,
                        'unit': units,
                        'value_kelvin': kelvin
                    })

    return results

def extract_bandgaps(records: list) -> list:
    """Extract bandgap data."""
    results = []

    # ChemDataExtractor may categorize bandgaps differently
    bandgap_keys = ['BandGap', 'Bandgap', 'OpticalBandGap', 'ElectronicBandGap']

    for record in records:
        for key in bandgap_keys:
            if key in record:
                bg_data = record[key]
                compound_names = bg_data.get('compound', {}).get('names', [])
                compound_labels = bg_data.get('compound', {}).get('labels', [])

                for value_entry in bg_data.get('value', []):
                    value = value_entry.get('value')
                    units = value_entry.get('units', 'eV')

                    if value:
                        results.append({
                            'compound': compound_names[0] if compound_names else 'Unknown',
                            'formula': compound_labels[0] if compound_labels else None,
                            'bandgap_value': float(value),
                            'unit': units,
                            'bandgap_type': key
                        })

    return results

melting_points = extract_melting_points(all_records)
bandgaps = extract_bandgaps(all_records)

print(f"\nExtracted {len(melting_points)} melting points")
print(f"Extracted {len(bandgaps)} bandgaps")
```

## Step 3: Reaction Extraction with OpenChemIE

```python
from openchemie import OpenChemIE

# Initialize model
model = OpenChemIE()

# Extract reactions from text
text_sample = """
The synthesis begins with the reaction of titanium isopropoxide with
acetic acid at 80°C for 2 hours to form a titanium acetate complex.
Subsequently, calcination at 450°C in air yields anatase TiO2.
"""

reactions = model.extract_reactions_from_text(text_sample)

for i, rxn in enumerate(reactions):
    print(f"\nReaction {i+1}:")
    print(f"  Reactants: {rxn.get('reactants', [])}")
    print(f"  Products: {rxn.get('products', [])}")
    print(f"  Conditions: {rxn.get('conditions', {})}")
```

### Processing Reaction Images

```python
from PIL import Image

def extract_reaction_from_figure(figure_path: str, model) -> dict:
    """Extract reaction from a figure image."""
    image = Image.open(figure_path)

    try:
        reaction = model.extract_reaction_from_figure(image)
        return {
            'success': True,
            'reactant_smiles': reaction.get('reactant_smiles', []),
            'product_smiles': reaction.get('product_smiles', []),
            'conditions': reaction.get('conditions', {}),
            'source': figure_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'source': figure_path
        }

# Process multiple reaction figures
figure_paths = ['scheme1.png', 'scheme2.png', 'scheme3.png']
reaction_data = []

for path in figure_paths:
    result = extract_reaction_from_figure(path, model)
    reaction_data.append(result)
    if result['success']:
        print(f"{path}: Extracted reaction with {len(result['product_smiles'])} products")
    else:
        print(f"{path}: Failed - {result['error']}")
```

## Step 4: Table Extraction with Chemistry Parsing

```python
import camelot
import pandas as pd
from rdkit import Chem

def parse_chemistry_table(df: pd.DataFrame) -> list:
    """Parse table containing chemistry data."""
    results = []

    # Identify column types
    column_types = {}
    for col in df.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in ['compound', 'material', 'sample']):
            column_types[col] = 'compound'
        elif any(kw in col_lower for kw in ['formula', 'structure']):
            column_types[col] = 'formula'
        elif any(kw in col_lower for kw in ['bandgap', 'band gap']):
            column_types[col] = 'bandgap'
        elif any(kw in col_lower for kw in ['melting', 'mp', 't_m']):
            column_types[col] = 'melting_point'
        elif any(kw in col_lower for kw in ['yield', '%']):
            column_types[col] = 'yield'
        elif any(kw in col_lower for kw in ['smiles']):
            column_types[col] = 'smiles'

    # Process each row
    for idx, row in df.iterrows():
        entry = {'row_index': idx}

        for col, col_type in column_types.items():
            value = row[col]
            if pd.isna(value):
                continue

            if col_type == 'compound':
                entry['compound_name'] = str(value).strip()
            elif col_type == 'formula':
                entry['formula'] = str(value).strip()
            elif col_type == 'smiles':
                # Validate SMILES
                smiles = str(value).strip()
                mol = Chem.MolFromSmiles(smiles)
                entry['smiles'] = smiles
                entry['smiles_valid'] = mol is not None
            elif col_type in ['bandgap', 'melting_point', 'yield']:
                # Extract numeric value
                try:
                    numeric = float(re.search(r'[\d.]+', str(value)).group())
                    entry[col_type] = numeric
                except:
                    entry[col_type + '_raw'] = str(value)

        if len(entry) > 1:  # More than just row_index
            results.append(entry)

    return results

# Extract and parse tables
tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='all')

chemistry_data = []
for i, table in enumerate(tables):
    if table.accuracy > 70:
        parsed = parse_chemistry_table(table.df)
        chemistry_data.extend(parsed)
        print(f"Table {i+1}: Extracted {len(parsed)} chemistry entries")

print(f"\nTotal chemistry entries from tables: {len(chemistry_data)}")
```

## Step 5: Synthesis Procedure Extraction

```python
import anthropic
import json

def extract_synthesis_procedure(text: str) -> dict:
    """Use LLM to extract structured synthesis procedure."""

    client = anthropic.Anthropic()

    prompt = f"""Extract the synthesis procedure from this scientific text.

Return a structured JSON with:
{{
  "target_compound": "name of compound being synthesized",
  "target_formula": "chemical formula if given",
  "steps": [
    {{
      "step_number": 1,
      "description": "what is done",
      "reagents": [
        {{"name": "reagent name", "amount": "quantity", "role": "e.g., precursor, solvent, catalyst"}}
      ],
      "conditions": {{
        "temperature": "value with units",
        "time": "duration",
        "atmosphere": "air, N2, Ar, etc.",
        "pressure": "if specified"
      }},
      "outcome": "intermediate or product formed"
    }}
  ],
  "final_product": {{
    "name": "product name",
    "formula": "formula",
    "yield": "if reported",
    "characterization": ["methods used to confirm product"]
  }}
}}

Text:
{text}

JSON:"""

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON
    import re
    text_response = response.content[0].text
    json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return {"error": "Could not parse", "raw": text_response}

# Extract synthesis from experimental section
experimental_text = """
Synthesis of TiO2 nanoparticles: Titanium(IV) isopropoxide (5 mL) was
added dropwise to 50 mL of deionized water under vigorous stirring at
room temperature. The white precipitate was aged for 24 h, then collected
by centrifugation and washed three times with ethanol. The powder was
dried at 80°C overnight and calcined at 450°C for 4 h in air to obtain
anatase TiO2. Yield: 1.2 g (85%). The product was characterized by XRD,
TEM, and UV-Vis spectroscopy.
"""

synthesis_data = extract_synthesis_procedure(experimental_text)
print(json.dumps(synthesis_data, indent=2))
```

## Step 6: Validation Against Databases

```python
import requests

def validate_compound_pubchem(compound_name: str) -> dict:
    """Cross-reference compound with PubChem."""
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    try:
        # Search by name
        url = f"{base_url}/compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES/JSON"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            props = data['PropertyTable']['Properties'][0]
            return {
                'found': True,
                'cid': props.get('CID'),
                'molecular_formula': props.get('MolecularFormula'),
                'molecular_weight': props.get('MolecularWeight'),
                'canonical_smiles': props.get('CanonicalSMILES'),
                'source': 'PubChem'
            }
        return {'found': False, 'source': 'PubChem'}

    except Exception as e:
        return {'found': False, 'error': str(e), 'source': 'PubChem'}

def validate_material_properties(formula: str, property_name: str, extracted_value: float) -> dict:
    """Validate extracted property against known ranges."""

    # Known property ranges for common materials
    known_ranges = {
        'TiO2': {
            'bandgap': (3.0, 3.4),  # eV, anatase
            'melting_point': (1800, 1900),  # K
            'density': (3.8, 4.3),  # g/cm3
        },
        'ZnO': {
            'bandgap': (3.2, 3.4),  # eV
            'melting_point': (2200, 2300),  # K
        },
        'SiO2': {
            'bandgap': (8.0, 9.0),  # eV
            'melting_point': (1900, 2000),  # K
        }
    }

    result = {
        'formula': formula,
        'property': property_name,
        'extracted_value': extracted_value,
        'validation': 'unknown'
    }

    if formula in known_ranges and property_name in known_ranges[formula]:
        range_min, range_max = known_ranges[formula][property_name]
        result['expected_range'] = (range_min, range_max)

        if range_min <= extracted_value <= range_max:
            result['validation'] = 'within_range'
        elif extracted_value < range_min * 0.8 or extracted_value > range_max * 1.2:
            result['validation'] = 'outlier'
        else:
            result['validation'] = 'borderline'

    return result

# Validate extracted data
for entry in chemistry_data:
    if 'compound_name' in entry:
        pubchem_result = validate_compound_pubchem(entry['compound_name'])
        entry['pubchem_validation'] = pubchem_result

    if 'formula' in entry and 'bandgap' in entry:
        prop_validation = validate_material_properties(
            entry['formula'],
            'bandgap',
            entry['bandgap']
        )
        entry['property_validation'] = prop_validation
```

## Step 7: Combine and Format Output

```python
def create_chemistry_extraction_report(
    property_records: list,
    table_data: list,
    reactions: list,
    synthesis_data: dict
) -> dict:
    """Create comprehensive chemistry extraction report."""

    report = {
        "metadata": {
            "extraction_date": "2025-01-18",
            "tools_used": ["ChemDataExtractor", "OpenChemIE", "Camelot", "LLM"],
            "document_type": "materials_science_paper"
        },
        "compounds": [],
        "properties": [],
        "reactions": [],
        "synthesis_procedures": []
    }

    # Process property records
    compound_set = set()
    for record in property_records:
        for prop_type, prop_data in record.items():
            if isinstance(prop_data, dict):
                compound = prop_data.get('compound', {})
                names = compound.get('names', [])
                formulas = compound.get('labels', [])

                if names:
                    compound_set.add(names[0])

                for value_entry in prop_data.get('value', []):
                    report['properties'].append({
                        'compound': names[0] if names else 'Unknown',
                        'formula': formulas[0] if formulas else None,
                        'property_type': prop_type,
                        'value': value_entry.get('value'),
                        'unit': value_entry.get('units'),
                        'source': 'ChemDataExtractor'
                    })

    # Process table data
    for entry in table_data:
        if 'compound_name' in entry:
            compound_set.add(entry['compound_name'])

        for key in ['bandgap', 'melting_point', 'yield']:
            if key in entry:
                report['properties'].append({
                    'compound': entry.get('compound_name', 'Unknown'),
                    'formula': entry.get('formula'),
                    'property_type': key,
                    'value': entry[key],
                    'source': 'table_extraction'
                })

    # Add compounds list
    report['compounds'] = list(compound_set)

    # Add reactions
    for rxn in reactions:
        report['reactions'].append({
            'reactants': rxn.get('reactants', []),
            'products': rxn.get('products', []),
            'conditions': rxn.get('conditions', {}),
            'source': 'OpenChemIE'
        })

    # Add synthesis procedures
    if synthesis_data and 'error' not in synthesis_data:
        report['synthesis_procedures'].append(synthesis_data)

    # Summary statistics
    report['summary'] = {
        'total_compounds': len(report['compounds']),
        'total_properties': len(report['properties']),
        'total_reactions': len(report['reactions']),
        'total_syntheses': len(report['synthesis_procedures'])
    }

    return report

# Create final report
final_report = create_chemistry_extraction_report(
    all_records,
    chemistry_data,
    reaction_data if 'reaction_data' in dir() else [],
    synthesis_data if 'synthesis_data' in dir() else {}
)

# Save report
with open('chemistry_extraction_report.json', 'w') as f:
    json.dump(final_report, f, indent=2, default=str)

print(f"\nExtraction complete:")
print(f"  Compounds: {final_report['summary']['total_compounds']}")
print(f"  Properties: {final_report['summary']['total_properties']}")
print(f"  Reactions: {final_report['summary']['total_reactions']}")
print(f"  Syntheses: {final_report['summary']['total_syntheses']}")
```

## Output Schema

```json
{
  "metadata": {
    "extraction_date": "2025-01-18",
    "tools_used": ["ChemDataExtractor", "OpenChemIE", "Camelot", "LLM"],
    "document_type": "materials_science_paper",
    "source_file": "paper.pdf"
  },
  "compounds": ["titanium dioxide", "zinc oxide", "silicon dioxide"],
  "properties": [
    {
      "compound": "titanium dioxide",
      "formula": "TiO2",
      "property_type": "bandgap",
      "value": "3.2",
      "unit": "eV",
      "source": "ChemDataExtractor",
      "confidence": {"score": 0.92, "level": "HIGH"}
    }
  ],
  "reactions": [
    {
      "reactants": [
        {"name": "titanium isopropoxide", "smiles": "..."}
      ],
      "products": [
        {"name": "titanium dioxide", "formula": "TiO2"}
      ],
      "conditions": {
        "temperature": "450°C",
        "atmosphere": "air",
        "time": "4 h"
      },
      "source": "LLM_extraction"
    }
  ],
  "synthesis_procedures": [
    {
      "target_compound": "TiO2 nanoparticles",
      "steps": [...],
      "yield": "85%"
    }
  ],
  "summary": {
    "total_compounds": 3,
    "total_properties": 12,
    "total_reactions": 2,
    "total_syntheses": 1
  }
}
```

## Tips for Chemistry Extraction

1. **Always run ChemDataExtractor first** - It's optimized for chemistry and catches many patterns

2. **Validate SMILES with RDKit** - LLM-generated SMILES may be invalid

3. **Cross-reference with databases** - PubChem, Materials Project for sanity checking

4. **Handle units carefully** - Different papers use different conventions

5. **Extract reaction conditions** - Often more valuable than just reactants/products

6. **Note synthesis details** - Temperature, time, atmosphere are critical for reproducibility
