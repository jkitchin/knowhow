---
name: scientific-data-extraction
description: |
  Extract structured data from scientific literature across multiple formats (PDF, HTML, images, plain text).
  Auto-detects scientific domain to recommend specialized tools for chemistry/materials when appropriate.

  Use this skill when: extracting numerical data from papers, digitizing graphs/plots, parsing tables from PDFs,
  extracting chemical properties or reactions, or converting unstructured scientific text to structured formats.

  Key capabilities: format detection and routing, domain-specific extraction (chemistry/materials), multi-method
  validation, table extraction, graph digitization, LLM-enhanced extraction with verification, confidence scoring.
allowed-tools: ["*"]
---

# Scientific Data Extraction Skill

## Overview

This skill provides comprehensive guidance for extracting structured data from scientific literature across multiple input formats (PDF, HTML, images, plain text). It auto-detects the scientific domain to recommend specialized tools when appropriate (particularly for chemistry and materials science) and employs a hierarchical extraction approach with multi-method validation for high-confidence results.

## When to Use This Skill

Use this skill when you need to:

- **Extract numerical data** from scientific papers, reports, or documents
- **Digitize graphs and plots** to recover underlying data points
- **Parse tables** from PDFs or images into structured formats (CSV, DataFrame, JSON)
- **Extract chemical/materials data** including properties, reactions, compounds, and structures
- **Convert unstructured text** to structured JSON or tabular formats
- **Validate extracted data** through multi-method cross-checking
- **Process document batches** with consistent extraction methodology

## Input Format Detection

The first step is identifying the input format and routing to appropriate tools:

### Plain Text (.txt, .md)
- Domain detection via keyword analysis
- NLP-based entity extraction (spaCy, Stanza)
- Regex patterns for structured data (numbers with units, chemical formulas)
- LLM-based structured extraction

### HTML (.html, web pages)
- HTML parsing with BeautifulSoup + lxml
- Table detection and extraction
- Text content extraction with structure preservation
- Domain-specific processing after text extraction

### PDF (.pdf)
| Priority | Tool | Speed | Use Case |
|----------|------|-------|----------|
| Quick | PyMuPDF4LLM | ~0.12s | Initial exploration, large batches |
| Standard | GROBID | Medium | Research-grade, reference parsing |
| Standard | Docling | Medium | Layout-aware, complex documents |
| Tables | Camelot | Fast | Bordered tables |
| Tables | Tabula | Fast | General tables |
| Tables | pdfplumber | Medium | Complex table structures |
| Deep | Marker-PDF | Slower | Scanned documents with OCR |

### Images (.png, .jpg, .tiff)
| Content Type | Recommended Approach |
|--------------|---------------------|
| Document scan | OCR (Tesseract/Surya) then text pipeline |
| Graph/Plot | WebPlotDigitizer workflow or LLM vision |
| Table image | Table Transformer or LLM vision |
| Chemical structure | OSRA or DECIMER for SMILES conversion |

## Domain Detection

The skill automatically detects scientific domain to apply specialized tools:

### Chemistry/Materials Indicators
- Chemical formulas (H2O, NaCl, TiO2)
- SMILES strings, InChI identifiers
- Reaction arrows (→, ⟶, ⇌)
- Property keywords: melting point, bandgap, conductivity, yield, purity
- Material names and IUPAC nomenclature
- Spectroscopic data patterns (NMR shifts, IR peaks)

### When Chemistry/Materials Detected
Apply specialized tools:
- **ChemDataExtractor v2**: Property extraction, entity recognition, table parsing
- **OpenChemIE**: Reaction extraction from text, tables, and figures
- **Domain-specific NER**: Chemical named entity recognition

### General Scientific Domain
Use general-purpose extraction:
- Standard NLP pipelines
- LLM-based structured extraction
- Template-based parsing

## Extraction Method Hierarchy

Apply methods in order of increasing complexity based on requirements:

### Level 1: Quick Extraction (Speed Priority)
**When to use**: Initial exploration, large document batches, simple structured data

```python
# Quick PDF to text with PyMuPDF4LLM
import pymupdf4llm
text = pymupdf4llm.to_markdown("paper.pdf")

# Quick HTML parsing
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_content, 'lxml')
tables = soup.find_all('table')
```

**Expected confidence**: Lower, suitable for screening

### Level 2: Standard Extraction (Balanced)
**When to use**: Research-grade extraction, structure preservation needed

```python
# GROBID for structured PDF parsing
import scipdf_parser
article = scipdf_parser.parse_pdf_to_dict("paper.pdf")

# Docling for layout-aware extraction
from docling.document_converter import DocumentConverter
converter = DocumentConverter()
result = converter.convert("paper.pdf")

# Camelot for bordered tables
import camelot
tables = camelot.read_pdf("paper.pdf", flavor='lattice')
df = tables[0].df
```

**Expected confidence**: Medium-high

### Level 3: Deep Extraction (Accuracy Priority)
**When to use**: Publication-quality data, domain-specific extraction

```python
# ChemDataExtractor for chemistry documents
from chemdataextractor import Document
doc = Document.from_file("paper.pdf")
records = doc.records

# OpenChemIE for reaction extraction
from openchemie import OpenChemIE
model = OpenChemIE()
reactions = model.extract_reactions_from_text(text)

# Marker-PDF with OCR for scanned documents
from marker.converters.pdf import PdfConverter
converter = PdfConverter()
result = converter("scanned_paper.pdf")
```

**Expected confidence**: High

### Level 4: LLM-Enhanced Extraction
**When to use**: Complex figures, ambiguous data, validation needed

```python
# LLM-based structured extraction
prompt = """
Extract all numerical data from this text as JSON:
- Property name
- Value (number only)
- Unit
- Context (what material/compound)

Text: {text}
"""

# LLM vision for graph interpretation
prompt = """
Analyze this graph image and extract:
1. X-axis label and range
2. Y-axis label and range
3. All data points as (x, y) pairs
4. Any error bars or uncertainty indicators
"""
```

**Expected confidence**: Highest when combined with validation

## Multi-Method Validation Pipeline

For high-confidence results, use multiple extraction methods and validate:

### Step 1: Primary Extraction
Select method based on input type and domain, extract structured data.

### Step 2: Secondary Extraction
Run alternative method on same source, compare results and flag discrepancies.

### Step 3: LLM Verification Queries
Ask targeted questions to verify extracted data:
- "Is this value X consistent with the context Y?"
- "Does unit Z make sense for property P?"
- "Are there any missing data points in the expected range?"

### Step 4: Confidence Scoring

```python
confidence = {
    "score": 0.0,  # 0-1 scale
    "level": "HIGH|MEDIUM|LOW|REVIEW",
    "methods_agreed": [],  # List of methods that produced same result
    "discrepancies": [],   # Any disagreements between methods
    "verification_notes": ""  # LLM verification outcome
}

# Scoring rules:
# - Single method: max 0.7
# - Two methods agree: 0.8
# - Two methods + LLM verification: 0.9
# - Multiple methods + LLM + database cross-reference: 0.95+
```

### Step 5: Database Cross-Reference (Optional)
For chemistry/materials, compare against known databases:
- Materials Project
- AFLOW
- PubChem
- NIST databases

Flag significant deviations from expected ranges.

## Output Format

Structure extracted data consistently:

```json
{
  "extraction_metadata": {
    "source": "path/to/document.pdf",
    "source_type": "pdf",
    "domain_detected": "chemistry",
    "methods_used": ["grobid", "chemdataextractor", "llm_verification"],
    "timestamp": "2025-01-18T..."
  },
  "extracted_data": [
    {
      "data_type": "material_property",
      "entity": "TiO2",
      "property": "bandgap",
      "value": 3.2,
      "unit": "eV",
      "source_location": {
        "page": 4,
        "section": "Results",
        "table_id": "Table 2",
        "row": 3
      },
      "confidence": {
        "score": 0.95,
        "level": "HIGH",
        "methods_agreed": ["chemdataextractor", "llm_extraction"],
        "verification_notes": "Value consistent with literature range 3.0-3.4 eV"
      }
    }
  ],
  "validation_summary": {
    "total_extracted": 47,
    "high_confidence": 38,
    "medium_confidence": 7,
    "needs_review": 2,
    "discrepancies": []
  }
}
```

## Step-by-Step Instructions

### For PDF Data Extraction

1. **Identify document type**: Scanned or text-based PDF
2. **Choose extraction level**: Based on accuracy requirements
3. **Detect domain**: Check for chemistry/materials indicators
4. **Extract text/structure**: Use appropriate tool from hierarchy
5. **Extract tables separately**: Use Camelot, Tabula, or pdfplumber
6. **Apply domain tools**: If chemistry detected, use ChemDataExtractor
7. **Validate**: Run secondary extraction or LLM verification
8. **Format output**: Structure as JSON with confidence scores

### For Graph/Plot Digitization

1. **Assess graph quality**: Resolution, clarity, labeling
2. **Identify graph type**: Line plot, scatter, bar chart, contour
3. **Choose method**:
   - Simple, clear graphs: WebPlotDigitizer (manual calibration)
   - Complex or batch: LLM vision extraction
4. **Calibrate axes**: Define coordinate system
5. **Extract data points**: Manual selection or automatic detection
6. **Validate**: Check extracted points against visual inspection
7. **Export**: CSV or JSON format with uncertainty estimates

### For Table Extraction

1. **Identify table type**: Bordered (lattice) or borderless (stream)
2. **Choose tool**:
   - Bordered: Camelot with `flavor='lattice'`
   - Borderless: Tabula or Camelot with `flavor='stream'`
   - Complex: pdfplumber for fine-grained control
3. **Extract to DataFrame**: Review structure and headers
4. **Clean data**: Fix merged cells, missing values, formatting
5. **Apply domain parsing**: Convert units, parse chemical formulas
6. **Validate**: Compare against source visually
7. **Export**: CSV, JSON, or integrate into dataset

### For Chemistry/Materials Extraction

1. **Confirm domain**: Verify chemistry/materials content
2. **Choose specialized tool**:
   - Properties: ChemDataExtractor v2
   - Reactions: OpenChemIE
   - Structures from images: OSRA or DECIMER
3. **Configure extraction**: Set up parsers for target properties
4. **Run extraction**: Process document with domain tools
5. **Post-process**: Normalize units, standardize identifiers
6. **Cross-reference**: Compare against databases (Materials Project, PubChem)
7. **Validate**: LLM verification of unusual values
8. **Export**: Structured JSON with confidence scores

## Best Practices

1. **Always start with format detection** - Correct tool selection depends on accurate format identification

2. **Use the simplest method that works** - Start at Level 1 and escalate only if needed

3. **Preserve source location** - Track page numbers, sections, table IDs for traceability

4. **Validate unusual values** - Any value outside expected ranges should be flagged and verified

5. **Document extraction methodology** - Record which tools and settings produced each data point

6. **Handle uncertainty explicitly** - Include error bounds when available, note when values are approximate

7. **Cross-reference chemistry data** - Always compare against known databases for sanity checking

8. **Use LLM verification judiciously** - Most valuable for complex figures and ambiguous cases

## Requirements

### Core Python Packages
- `pymupdf4llm`: Quick PDF extraction
- `pdfplumber`: Detailed PDF analysis
- `camelot-py`: Table extraction (requires ghostscript)
- `beautifulsoup4`, `lxml`: HTML parsing
- `spacy`: NLP processing
- `pandas`: Data manipulation

### Domain-Specific (Chemistry)
- `chemdataextractor`: Chemistry NLP (v2 recommended)
- `openchemie`: Reaction extraction

### Optional
- `tabula-py`: Table extraction (requires Java)
- `grobid` (server): Academic PDF parsing
- `docling`: IBM document converter
- `marker-pdf`: OCR-capable PDF conversion
- `tesseract` or `surya`: OCR engines

## Limitations

1. **Scanned documents require OCR** - Quality depends on scan resolution and OCR accuracy

2. **Complex table structures** - Merged cells, nested headers may require manual correction

3. **Graph digitization is approximate** - Precision limited by image resolution and calibration

4. **Domain tools are specialized** - Chemistry tools won't work well on biology or physics texts

5. **LLM extraction can hallucinate** - Always validate with source or alternative method

6. **Some PDFs are protected** - May not be extractable due to DRM or image-only content

## Related Skills

- **literature-review**: For systematic literature searching and synthesis
- **scientific-reviewer**: For evaluating extracted data quality
- **materials-databases**: For cross-referencing extracted chemistry/materials data
- **python-plotting**: For visualizing extracted data

## References

See the `references/` directory for detailed documentation on:
- `pdf-tools.md`: Comprehensive PDF extraction tool comparison
- `table-extraction.md`: Table extraction methods and code examples
- `graph-digitization.md`: Graph data extraction techniques
- `chemistry-tools.md`: ChemDataExtractor and OpenChemIE usage
- `llm-extraction.md`: LLM-based extraction patterns and validation

See the `examples/` directory for complete workflows:
- `extract-from-pdf.md`: End-to-end PDF extraction example
- `extract-table-data.md`: Table extraction comparison
- `digitize-graph.md`: Graph digitization guide
- `chemistry-extraction.md`: Chemistry-specific extraction workflow
