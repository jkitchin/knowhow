# Example: Complete PDF Data Extraction Workflow

This example demonstrates a complete workflow for extracting structured data from a scientific PDF paper.

## Scenario

You have a materials science paper (PDF) containing:
- Text describing material properties
- Tables with experimental data
- Figures showing graphs and chemical structures

Goal: Extract all numerical data into a structured JSON format with confidence scores.

## Step 1: Initial Assessment

```python
import pymupdf4llm
import pdfplumber
from pathlib import Path

pdf_path = "paper.pdf"

# Quick text extraction for assessment
text = pymupdf4llm.to_markdown(pdf_path)

# Check content type
def assess_document(text: str) -> dict:
    """Assess document to determine extraction strategy."""
    import re

    assessment = {
        "has_chemistry": False,
        "has_tables": False,
        "has_figures": False,
        "estimated_pages": text.count("---") + 1,  # Page breaks in markdown
    }

    # Chemistry indicators
    chemistry_patterns = [
        r'\b[A-Z][a-z]?\d*[A-Z]?[a-z]?\d*\b',  # Formulas like TiO2, NaCl
        r'→|⟶|⇌',  # Reaction arrows
        r'\b\d+\.?\d*\s*°C\b',  # Temperatures
        r'\b\d+\.?\d*\s*(eV|meV|kJ|kcal|nm|Å)\b',  # Units
    ]
    assessment["has_chemistry"] = any(re.search(p, text) for p in chemistry_patterns)

    # Table indicators
    assessment["has_tables"] = bool(re.search(r'Table\s+\d|│|┌|┐|└|┘|\|[-+]+\|', text))

    # Figure indicators
    assessment["has_figures"] = bool(re.search(r'Figure\s+\d|Fig\.\s*\d', text))

    return assessment

assessment = assess_document(text)
print(f"Assessment: {assessment}")
# Example output:
# Assessment: {'has_chemistry': True, 'has_tables': True, 'has_figures': True, 'estimated_pages': 12}
```

## Step 2: Extract Text Content with Structure

```python
import scipdf_parser

# Use GROBID for structured extraction
# Requires GROBID server running: docker run -p 8070:8070 lfoppiano/grobid:0.8.0

try:
    article = scipdf_parser.parse_pdf_to_dict(pdf_path)
    print(f"Title: {article['title']}")
    print(f"Sections: {[s['heading'] for s in article['sections']]}")
except Exception as e:
    # Fallback to simpler extraction
    print(f"GROBID unavailable, using PyMuPDF: {e}")
    article = {"title": "Unknown", "sections": [], "abstract": "", "text": text}

# Identify sections likely containing data
data_sections = []
for section in article.get('sections', []):
    heading = section.get('heading', '').lower()
    if any(kw in heading for kw in ['result', 'data', 'experiment', 'property', 'measurement']):
        data_sections.append(section)

print(f"Data sections found: {len(data_sections)}")
```

## Step 3: Extract Tables

```python
import camelot
import pandas as pd

# Extract tables with Camelot
tables_lattice = camelot.read_pdf(pdf_path, flavor='lattice', pages='all')
tables_stream = camelot.read_pdf(pdf_path, flavor='stream', pages='all')

print(f"Found {len(tables_lattice)} bordered tables, {len(tables_stream)} stream tables")

# Process each table
extracted_tables = []
for i, table in enumerate(tables_lattice):
    if table.accuracy > 80:  # Filter by quality
        df = table.df
        extracted_tables.append({
            "table_id": f"Table_{i+1}",
            "page": table.page,
            "accuracy": table.accuracy,
            "data": df.to_dict(orient='records'),
            "columns": df.columns.tolist()
        })
        print(f"Table {i+1} (page {table.page}): {df.shape}, accuracy: {table.accuracy}%")

# Alternative: pdfplumber for complex tables
with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            if table and len(table) > 1:
                df = pd.DataFrame(table[1:], columns=table[0])
                print(f"pdfplumber - Page {page_num+1}, Table {j+1}: {df.shape}")
```

## Step 4: Chemistry-Specific Extraction

```python
from chemdataextractor import Document

# Load document
cde_doc = Document.from_file(pdf_path)

# Extract chemical records
chemical_records = []
for record in cde_doc.records:
    data = record.serialize()
    if data:  # Non-empty record
        chemical_records.append(data)
        print(f"Extracted: {list(data.keys())}")

print(f"Total chemical records: {len(chemical_records)}")

# Example output processing
for record in chemical_records[:3]:
    for prop_type, prop_data in record.items():
        if isinstance(prop_data, dict):
            compound = prop_data.get('compound', {}).get('names', ['Unknown'])[0]
            value = prop_data.get('value', [{}])[0]
            print(f"  {prop_type}: {compound} = {value.get('value')} {value.get('units', '')}")
```

## Step 5: LLM-Enhanced Extraction for Complex Content

```python
import anthropic
import json

client = anthropic.Anthropic()

def extract_with_llm(text_chunk: str) -> dict:
    """Use LLM for complex extraction."""
    prompt = f"""Extract all quantitative data from this scientific text.

Return JSON with this structure:
{{
  "properties": [
    {{
      "entity": "compound or material name",
      "property": "property name",
      "value": number,
      "unit": "unit string",
      "conditions": {{"temperature": null, "pressure": null}},
      "context": "brief context"
    }}
  ]
}}

Rules:
- Only extract explicitly stated values
- Use null for unknown conditions
- Include all numerical measurements

Text:
{text_chunk}

JSON:"""

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON from response
    import re
    text_response = response.content[0].text
    json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return {"properties": []}

# Process data sections
llm_extractions = []
for section in data_sections:
    result = extract_with_llm(section['text'][:4000])  # Limit chunk size
    llm_extractions.extend(result.get('properties', []))

print(f"LLM extracted {len(llm_extractions)} property records")
```

## Step 6: Combine and Validate

```python
def combine_extractions(chemical_records: list, table_data: list, llm_data: list) -> list:
    """Combine extractions from multiple sources."""
    combined = []

    # Process ChemDataExtractor records
    for record in chemical_records:
        for prop_type, prop_data in record.items():
            if isinstance(prop_data, dict):
                combined.append({
                    "source": "chemdataextractor",
                    "property_type": prop_type,
                    "data": prop_data
                })

    # Process table data
    for table in table_data:
        combined.append({
            "source": "table_extraction",
            "table_id": table["table_id"],
            "data": table["data"]
        })

    # Process LLM extractions
    for item in llm_data:
        combined.append({
            "source": "llm_extraction",
            "data": item
        })

    return combined

combined = combine_extractions(chemical_records, extracted_tables, llm_extractions)

# Validation: Check for consistency
def validate_extraction(item: dict) -> dict:
    """Validate single extraction."""
    validation = {"valid": True, "issues": []}

    data = item.get("data", {})

    # Check for required fields
    if item["source"] == "llm_extraction":
        if data.get("value") is None:
            validation["issues"].append("Missing value")
            validation["valid"] = False
        if not data.get("unit"):
            validation["issues"].append("Missing unit")

    return validation

for item in combined:
    item["validation"] = validate_extraction(item)
```

## Step 7: Calculate Confidence and Format Output

```python
def calculate_confidence(item: dict, all_items: list) -> dict:
    """Calculate confidence score for extraction."""
    score = 0.5  # Base score

    # Source reliability
    source_scores = {
        "chemdataextractor": 0.3,  # Domain-specific tool
        "table_extraction": 0.25,  # Structured data
        "llm_extraction": 0.2      # General extraction
    }
    score += source_scores.get(item["source"], 0)

    # Validation passed
    if item.get("validation", {}).get("valid"):
        score += 0.1

    # Cross-reference (simplified): check if similar value appears from other source
    if item["source"] == "llm_extraction":
        entity = item["data"].get("entity", "").lower()
        prop = item["data"].get("property", "").lower()

        for other in all_items:
            if other["source"] != "llm_extraction":
                other_text = str(other.get("data", {})).lower()
                if entity in other_text and prop in other_text:
                    score += 0.1
                    break

    # Determine level
    if score >= 0.85:
        level = "HIGH"
    elif score >= 0.7:
        level = "MEDIUM"
    elif score >= 0.5:
        level = "LOW"
    else:
        level = "REVIEW"

    return {"score": round(min(score, 1.0), 2), "level": level}

# Apply confidence scoring
for item in combined:
    item["confidence"] = calculate_confidence(item, combined)

# Format final output
final_output = {
    "extraction_metadata": {
        "source": pdf_path,
        "source_type": "pdf",
        "domain_detected": "chemistry" if assessment["has_chemistry"] else "general",
        "methods_used": ["grobid", "camelot", "chemdataextractor", "llm_extraction"],
        "timestamp": "2025-01-18T12:00:00Z"
    },
    "extracted_data": combined,
    "validation_summary": {
        "total_extracted": len(combined),
        "high_confidence": sum(1 for x in combined if x["confidence"]["level"] == "HIGH"),
        "medium_confidence": sum(1 for x in combined if x["confidence"]["level"] == "MEDIUM"),
        "low_confidence": sum(1 for x in combined if x["confidence"]["level"] == "LOW"),
        "needs_review": sum(1 for x in combined if x["confidence"]["level"] == "REVIEW")
    }
}

# Save to file
with open("extracted_data.json", "w") as f:
    json.dump(final_output, f, indent=2)

print(f"\nExtraction complete:")
print(f"  Total records: {final_output['validation_summary']['total_extracted']}")
print(f"  High confidence: {final_output['validation_summary']['high_confidence']}")
print(f"  Needs review: {final_output['validation_summary']['needs_review']}")
```

## Full Workflow Script

```python
#!/usr/bin/env python3
"""Complete PDF data extraction workflow."""

import json
from pathlib import Path
from datetime import datetime

def extract_from_pdf(pdf_path: str, output_path: str = None) -> dict:
    """
    Extract structured data from a scientific PDF.

    Args:
        pdf_path: Path to PDF file
        output_path: Optional path for JSON output

    Returns:
        Dictionary with extracted data and metadata
    """
    import pymupdf4llm
    import camelot
    from chemdataextractor import Document

    if output_path is None:
        output_path = Path(pdf_path).stem + "_extracted.json"

    # Step 1: Quick assessment
    text = pymupdf4llm.to_markdown(pdf_path)
    has_chemistry = any(kw in text.lower() for kw in ['bandgap', 'melting', 'synthesis', 'reaction'])

    # Step 2: Table extraction
    tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='all')
    table_data = [{"id": i, "data": t.df.to_dict('records'), "accuracy": t.accuracy}
                  for i, t in enumerate(tables) if t.accuracy > 70]

    # Step 3: Chemistry extraction (if applicable)
    chem_data = []
    if has_chemistry:
        try:
            doc = Document.from_file(pdf_path)
            chem_data = [r.serialize() for r in doc.records if r.serialize()]
        except Exception as e:
            print(f"ChemDataExtractor warning: {e}")

    # Step 4: Combine results
    result = {
        "metadata": {
            "source": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
            "domain": "chemistry" if has_chemistry else "general"
        },
        "text_content": text[:5000],  # First 5000 chars
        "tables": table_data,
        "chemical_records": chem_data,
        "summary": {
            "tables_found": len(table_data),
            "chemical_records": len(chem_data)
        }
    }

    # Save
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)

    print(f"Extraction saved to {output_path}")
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extract_from_pdf(sys.argv[1])
    else:
        print("Usage: python extract_pdf.py <pdf_path>")
```

## Expected Output Structure

```json
{
  "extraction_metadata": {
    "source": "paper.pdf",
    "source_type": "pdf",
    "domain_detected": "chemistry",
    "methods_used": ["grobid", "camelot", "chemdataextractor", "llm_extraction"],
    "timestamp": "2025-01-18T12:00:00Z"
  },
  "extracted_data": [
    {
      "source": "chemdataextractor",
      "property_type": "MeltingPoint",
      "data": {
        "compound": {"names": ["sodium chloride"]},
        "value": [{"value": "801", "units": "°C"}]
      },
      "validation": {"valid": true, "issues": []},
      "confidence": {"score": 0.85, "level": "HIGH"}
    },
    {
      "source": "table_extraction",
      "table_id": "Table_1",
      "data": [
        {"Material": "TiO2", "Bandgap (eV)": "3.2", "Phase": "anatase"},
        {"Material": "ZnO", "Bandgap (eV)": "3.37", "Phase": "wurtzite"}
      ],
      "validation": {"valid": true, "issues": []},
      "confidence": {"score": 0.75, "level": "MEDIUM"}
    }
  ],
  "validation_summary": {
    "total_extracted": 47,
    "high_confidence": 38,
    "medium_confidence": 7,
    "low_confidence": 2,
    "needs_review": 0
  }
}
```

## Tips for Best Results

1. **Check PDF quality first**: Scanned PDFs need OCR preprocessing
2. **Try multiple table extractors**: Different tools work better for different table styles
3. **Use domain tools when applicable**: ChemDataExtractor significantly outperforms generic extraction for chemistry
4. **Validate critical values**: Always verify high-stakes data manually
5. **Document your extraction**: Record methods and settings for reproducibility
