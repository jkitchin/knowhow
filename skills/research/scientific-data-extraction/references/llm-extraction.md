# LLM-Based Data Extraction Reference

This document covers using Large Language Models (LLMs) for extracting structured data from scientific literature, including prompt patterns, validation strategies, and confidence scoring.

## Overview

LLM-based extraction uses language models like GPT-4, Claude, and others to:
- Convert unstructured text to structured JSON
- Extract data from tables and figures (with vision capabilities)
- Validate and verify extracted data
- Handle ambiguous or complex content

**Key Advantages**:
- Flexible schema adaptation
- Context-aware extraction
- No domain-specific training required
- Multi-modal capabilities (text + images)

**Limitations**:
- Can hallucinate data
- Precision limited compared to specialized tools
- Requires validation
- Cost and latency considerations

## Prompt Engineering Patterns

### 1. Structured Extraction Prompt

```python
def create_extraction_prompt(text: str, schema: dict) -> str:
    """Create prompt for structured data extraction."""
    return f"""Extract structured data from the following scientific text.

Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Rules:
1. Extract ONLY information explicitly stated in the text
2. Use null for missing or uncertain values
3. Include units with all numerical values
4. Do not infer or calculate values not directly stated

Text to extract from:
\"\"\"
{text}
\"\"\"

JSON output:"""

# Example schema
schema = {
    "properties": [
        {
            "compound": "string - compound name",
            "property": "string - property name",
            "value": "number",
            "unit": "string",
            "conditions": {
                "temperature": "number or null",
                "pressure": "number or null"
            }
        }
    ]
}
```

### 2. Entity-Relationship Extraction

```python
entity_relation_prompt = """Extract entities and relationships from this scientific text.

Entities to identify:
- COMPOUND: Chemical compounds, materials
- PROPERTY: Measured or calculated properties
- VALUE: Numerical values with units
- METHOD: Experimental or computational methods
- CONDITION: Experimental conditions

Relationships:
- HAS_PROPERTY: compound -> property
- MEASURED_AT: property -> condition
- USED_METHOD: property -> method

Format as JSON:
{
  "entities": [
    {"id": "E1", "type": "COMPOUND", "text": "..."}
  ],
  "relationships": [
    {"type": "HAS_PROPERTY", "source": "E1", "target": "E2"}
  ]
}

Text:
\"\"\"
{text}
\"\"\"
"""
```

### 3. ChatExtract Pattern (with Verification)

The ChatExtract approach uses follow-up questions to verify extracted data:

```python
def chatextract_workflow(text: str, llm_client) -> dict:
    """Multi-turn extraction with verification."""

    # Step 1: Identify data-containing sentences
    identification_prompt = f"""Read the following text and identify sentences that contain
quantitative data (numbers with units, measurements, properties).

List each sentence that contains extractable data.

Text:
\"\"\"
{text}
\"\"\"

Data-containing sentences:"""

    sentences = llm_client.complete(identification_prompt)

    # Step 2: Extract from identified sentences
    extraction_prompt = f"""Extract structured data from these sentences.

For each data point, provide:
- Property name
- Value (number only)
- Unit
- Associated entity (compound/material)
- Context (what was measured/calculated)

Sentences:
{sentences}

JSON output:"""

    extracted = llm_client.complete(extraction_prompt)

    # Step 3: Verification questions
    verification_prompt = f"""Review the extracted data and answer these verification questions:

Extracted data:
{extracted}

Original text:
{text}

Questions:
1. Is each value explicitly stated in the text, or was it inferred?
2. Are the units correct for each property?
3. Are there any data points in the text that were missed?
4. Are there any values that seem unusual or potentially misread?

Verification:"""

    verification = llm_client.complete(verification_prompt)

    return {
        "extracted": extracted,
        "verification": verification
    }
```

### 4. Table Extraction Prompt

```python
table_extraction_prompt = """Convert this table to structured JSON.

The table appears in a scientific paper and may contain:
- Chemical compound names or formulas
- Property values with units
- Experimental conditions
- References to other tables or figures

Table content:
\"\"\"
{table_text}
\"\"\"

Table caption (if available):
{caption}

Extract as JSON with this structure:
{
  "table_id": "Table N",
  "caption_summary": "brief description",
  "columns": ["col1", "col2", ...],
  "rows": [
    {"col1": "value1", "col2": "value2", ...}
  ],
  "notes": "any footnotes or special notations"
}

JSON output:"""
```

### 5. Figure/Graph Interpretation Prompt

```python
figure_prompt = """Analyze this scientific figure and extract numerical data.

Instructions:
1. Identify the figure type (scatter plot, line graph, bar chart, etc.)
2. Read axis labels and determine the ranges
3. Extract visible data points or trends
4. Note any error bars or uncertainty indicators
5. Identify different data series by color/marker

Output format:
{
  "figure_type": "string",
  "x_axis": {
    "label": "string",
    "units": "string",
    "range": [min, max],
    "scale": "linear|log"
  },
  "y_axis": {
    "label": "string",
    "units": "string",
    "range": [min, max],
    "scale": "linear|log"
  },
  "data_series": [
    {
      "label": "series name",
      "data_points": [[x1, y1], [x2, y2], ...],
      "trend": "increasing|decreasing|constant|complex",
      "uncertainties": "description of error bars if visible"
    }
  ],
  "observations": "additional notes about the figure"
}

Be conservative - only include data points you can clearly identify.
If uncertain about a value, indicate approximate ranges.
"""
```

## Implementation Examples

### Claude API Integration

```python
import anthropic
import json
from typing import Optional

class LLMExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)

    def extract_structured(self, text: str, schema: dict) -> dict:
        """Extract structured data according to schema."""
        prompt = f"""Extract data from this text as JSON.

Schema:
{json.dumps(schema, indent=2)}

Text:
{text}

Return only valid JSON. Use null for missing values."""

        response = self.client.messages.create(
            model="claude-opus-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON from response
        text_response = response.content[0].text
        try:
            # Find JSON in response
            import re
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        return {"error": "Could not parse JSON", "raw": text_response}

    def extract_with_verification(self, text: str, schema: dict) -> dict:
        """Extract with follow-up verification."""

        # Initial extraction
        extracted = self.extract_structured(text, schema)

        if "error" in extracted:
            return extracted

        # Verification
        verify_prompt = f"""Verify this extracted data against the source text.

Extracted:
{json.dumps(extracted, indent=2)}

Source text:
{text}

Check:
1. Are all values explicitly in the text?
2. Any values seem incorrect or unusual?
3. Any data points missed?

Return corrected JSON if changes needed, otherwise return "VERIFIED"."""

        response = self.client.messages.create(
            model="claude-opus-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": verify_prompt}]
        )

        verification = response.content[0].text

        if "VERIFIED" in verification:
            return {"data": extracted, "verified": True}
        else:
            # Try to parse corrected JSON
            try:
                corrected = json.loads(re.search(r'\{.*\}', verification, re.DOTALL).group())
                return {"data": corrected, "verified": True, "corrections_made": True}
            except:
                return {"data": extracted, "verified": False, "verification_notes": verification}
```

### OpenAI API Integration

```python
import openai
import json

class OpenAIExtractor:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def extract_from_image(self, image_path: str, prompt: str) -> dict:
        """Extract data from image using GPT-4V."""
        import base64

        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        response = self.client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        return self._parse_json_response(response.choices[0].message.content)

    def extract_with_function_calling(self, text: str) -> dict:
        """Use function calling for structured extraction."""

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "extract_material_properties",
                    "description": "Extract material properties from scientific text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "materials": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "formula": {"type": "string"},
                                        "properties": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {"type": "string"},
                                                    "value": {"type": "number"},
                                                    "unit": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["materials"]
                    }
                }
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Extract material properties:\n\n{text}"}],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "extract_material_properties"}}
        )

        tool_call = response.choices[0].message.tool_calls[0]
        return json.loads(tool_call.function.arguments)

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from LLM response."""
        import re
        try:
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError:
            pass
        return {"error": "Could not parse JSON", "raw": text}
```

## Validation Strategies

### 1. Multi-LLM Consensus

```python
def extract_with_consensus(text: str, schema: dict, extractors: list) -> dict:
    """Use multiple LLMs and find consensus."""

    results = []
    for extractor in extractors:
        result = extractor.extract_structured(text, schema)
        if "error" not in result:
            results.append(result)

    if not results:
        return {"error": "No successful extractions"}

    # Find consensus values
    # Simple approach: use values that appear in multiple extractions
    consensus = {}
    for key in results[0].keys():
        values = [r.get(key) for r in results if key in r]
        # Use most common value
        from collections import Counter
        most_common = Counter(str(v) for v in values).most_common(1)
        if most_common:
            consensus[key] = most_common[0][0]

    return {
        "consensus": consensus,
        "individual_results": results,
        "agreement_score": calculate_agreement(results)
    }

def calculate_agreement(results: list) -> float:
    """Calculate agreement score between extractions."""
    if len(results) < 2:
        return 1.0

    total_comparisons = 0
    agreements = 0

    for key in results[0].keys():
        values = [str(r.get(key)) for r in results if key in r]
        if len(values) > 1:
            # Compare all pairs
            for i in range(len(values)):
                for j in range(i + 1, len(values)):
                    total_comparisons += 1
                    if values[i] == values[j]:
                        agreements += 1

    return agreements / total_comparisons if total_comparisons > 0 else 1.0
```

### 2. Self-Consistency Check

```python
def self_consistency_extraction(text: str, schema: dict, extractor, n_samples: int = 3) -> dict:
    """Extract multiple times and check consistency."""

    results = []
    for _ in range(n_samples):
        result = extractor.extract_structured(text, schema)
        results.append(result)

    # Analyze consistency
    consistent_values = {}
    inconsistent_values = {}

    for key in results[0].keys():
        values = [r.get(key) for r in results]
        unique_values = set(str(v) for v in values)

        if len(unique_values) == 1:
            consistent_values[key] = values[0]
        else:
            inconsistent_values[key] = values

    confidence = len(consistent_values) / (len(consistent_values) + len(inconsistent_values))

    return {
        "consistent": consistent_values,
        "inconsistent": inconsistent_values,
        "confidence": confidence,
        "all_results": results
    }
```

### 3. Range and Unit Validation

```python
def validate_extracted_values(extracted: dict, property_ranges: dict) -> dict:
    """Validate extracted values against known ranges."""

    validation_results = []

    for item in extracted.get("properties", []):
        prop_name = item.get("property", "").lower()
        value = item.get("value")
        unit = item.get("unit")

        validation = {
            "property": prop_name,
            "value": value,
            "unit": unit,
            "valid": True,
            "issues": []
        }

        # Check if property has known range
        if prop_name in property_ranges:
            expected = property_ranges[prop_name]

            # Unit check
            if unit and unit not in expected.get("units", []):
                validation["issues"].append(f"Unexpected unit: {unit}")
                validation["valid"] = False

            # Range check
            if value is not None:
                min_val, max_val = expected.get("range", (None, None))
                if min_val is not None and value < min_val:
                    validation["issues"].append(f"Value below expected range: {value} < {min_val}")
                    validation["valid"] = False
                if max_val is not None and value > max_val:
                    validation["issues"].append(f"Value above expected range: {value} > {max_val}")
                    validation["valid"] = False

        validation_results.append(validation)

    return {
        "validations": validation_results,
        "all_valid": all(v["valid"] for v in validation_results),
        "invalid_count": sum(1 for v in validation_results if not v["valid"])
    }

# Example property ranges for materials
PROPERTY_RANGES = {
    "bandgap": {"units": ["eV", "meV"], "range": (0, 10)},
    "melting point": {"units": ["K", "°C", "°F"], "range": (0, 5000)},
    "density": {"units": ["g/cm3", "kg/m3"], "range": (0, 25)},
    "conductivity": {"units": ["S/cm", "S/m", "mS/cm"], "range": (0, 1e8)},
}
```

## Confidence Scoring

```python
def calculate_extraction_confidence(
    extracted: dict,
    verification_result: dict,
    validation_result: dict,
    consensus_score: float = None
) -> dict:
    """Calculate overall confidence score for extraction."""

    score = 0.5  # Base score

    # Verification passed
    if verification_result.get("verified"):
        score += 0.2

    # Validation passed
    if validation_result.get("all_valid"):
        score += 0.15
    else:
        # Partial credit
        invalid_ratio = validation_result.get("invalid_count", 0) / max(len(validation_result.get("validations", [])), 1)
        score += 0.15 * (1 - invalid_ratio)

    # Consensus (if available)
    if consensus_score is not None:
        score += 0.15 * consensus_score

    # Determine level
    if score >= 0.9:
        level = "HIGH"
    elif score >= 0.7:
        level = "MEDIUM"
    elif score >= 0.5:
        level = "LOW"
    else:
        level = "REVIEW"

    return {
        "score": min(score, 1.0),
        "level": level,
        "components": {
            "base": 0.5,
            "verification": 0.2 if verification_result.get("verified") else 0,
            "validation": 0.15 * (1 - validation_result.get("invalid_count", 0) / max(len(validation_result.get("validations", [])), 1)),
            "consensus": 0.15 * consensus_score if consensus_score else 0
        }
    }
```

## Best Practices

1. **Be explicit about what to extract**: Vague prompts lead to inconsistent results

2. **Require explicit values**: Tell the model to only extract what's explicitly stated

3. **Use structured output formats**: JSON with defined schemas reduces parsing errors

4. **Always validate**: Never trust LLM extraction without verification

5. **Multiple samples improve reliability**: Self-consistency checks catch random errors

6. **Combine with traditional tools**: Use LLMs to enhance, not replace, specialized extractors

7. **Track provenance**: Record which model and prompt produced each extraction

8. **Handle uncertainty explicitly**: Have the model indicate confidence or flag uncertain values

## References

- Polak et al. "Extracting Accurate Materials Data from Research Papers with Conversational Language Models and Prompt Engineering." *Nature Communications* (2024).

- Zheng et al. "ChatExtract: Interactive Extraction and Verification of Data from Research Publications." *arXiv:2308.02214* (2023).

- White et al. "Assessment of chemistry knowledge in large language models that generate code." *Digital Discovery* (2023).

- Jablonka et al. "GPT Models for Chemical Data: Benchmarks and Prompts." *ChemRxiv* (2024).
