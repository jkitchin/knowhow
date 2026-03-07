---
name: scientific-writing
description: |
  Comprehensive scientific writing guidance for research papers, grants, and technical documentation.
  Covers paper structure (IMRAD), methods writing, results presentation, figure/table design, citation
  formatting, abstract writing, and revision responses. Use when users are writing scientific papers,
  formatting manuscripts, responding to reviewers, writing grant proposals, or need help with any aspect
  of scientific communication. Triggers include 'write a paper,' 'scientific writing,' 'format my
  manuscript,' 'methods section,' 'respond to reviewers,' or any research writing task.
allowed-tools: ["*"]
---

# Scientific Writing

Systematic guidance for writing research papers, grants, and scientific communications with
emphasis on clarity, reproducibility, and adherence to field conventions.

## Scientific Writing Workflow

### 1. Identify Document Type and Requirements

Determine what you're writing:
- Research article → Full paper with novel findings
- Review article → Synthesis of existing literature
- Grant proposal → Funding application
- Conference abstract → Brief standalone summary
- Revision response → Reply to peer reviewers
- Technical report → Documentation of work

Gather venue requirements:
- Target journal/conference/funder name
- Word/page limits by section
- Citation style required
- Figure/table format specifications
- Submission guidelines and templates

### 2. Select Structure and Route to Guidance

For research articles:
- Use IMRAD structure (see references/paper-structure.md)
- Introduction: references/introduction-writing.md
- Methods: references/methods-writing.md
- Results: references/results-writing.md
- Discussion: references/discussion-writing.md
- Abstract: references/abstract-writing.md

For review articles:
- See references/review-writing.md for thematic organization
- Focus on synthesis, not chronological listing
- Critical evaluation of literature

For grant proposals:
- See references/grant-writing.md for funder-specific guidance
- Specific Aims structure
- Significance, Innovation, Approach

For revision responses:
- See references/revision-response.md for point-by-point format
- Diplomatic language and tracking changes

### 3. Write Section by Section

Follow section-specific guidance:

Introduction (references/introduction-writing.md)
- Funnel structure: Broad → Narrow → Gap → Objective
- Establish context and importance
- Identify knowledge gap
- State clear objective

Methods (references/methods-writing.md)
- Reproducibility is paramount
- Include all essential details: equipment, reagents, software, statistics
- Organize chronologically or by subsystem
- Past tense, field-appropriate voice

Results (references/results-writing.md)
- Report observations objectively
- No interpretation (save for discussion)
- Integrate figures and tables
- Include statistical details
- Past tense

Discussion (references/discussion-writing.md)
- Interpret findings in context
- Compare with literature
- Acknowledge limitations honestly
- Discuss implications and future work
- Mix of present (facts) and past (your results)

### 4. Create Figures and Tables

Figures (references/figure-design.md)
- Match figure type to data type
- Publication quality: 300+ DPI, readable fonts, vector when possible
- Complete captions with all essential information
- Colorblind-friendly palettes

Tables (references/table-design.md)
- Use when precise values needed
- Clear headers with units
- Consistent decimal places
- Descriptive captions

Tools:
```bash
# Generate publication-quality figures
python scripts/figure_generator.py data.csv config.yaml --output fig1.pdf

# Format tables for journals
python scripts/table_formatter.py data.csv --format latex --journal nature
```

### 5. Manage Citations and References

Citation formatting (references/citation-management.md)
- Match journal's required style:
  - Numbered: [1], [2,3], [1-5]
  - Author-year: (Smith, 2020; Jones, 2021)
  - Author-number: Smith (1)
- Check all in-text citations have references
- Check all references are cited
- Consistent formatting throughout

Tools:
```bash
# Validate citation consistency
python scripts/citation_checker.py manuscript.docx --style apa
```

### 6. Improve Clarity and Conciseness

Language clarity (references/language-clarity.md)
- Active voice preferred (field norms vary)
- Concise: remove filler words and redundancies
- Precise: avoid vague terms ("very," "quite," "many")
- One main idea per sentence
- Logical paragraph flow

Tools:
```bash
# Analyze readability
python scripts/readability_analyzer.py section.txt

# Count words by section
python scripts/word_counter.py manuscript.docx
```

### 7. Review Against Requirements

Pre-submission checklist:
- [ ] Word limits met for each section
- [ ] All figures/tables referenced in text
- [ ] All citations formatted consistently
- [ ] Statistical details complete
- [ ] Methods reproducible
- [ ] Limitations discussed
- [ ] Abstract within word limit
- [ ] Keywords selected
- [ ] Author contributions stated
- [ ] Conflicts of interest disclosed
- [ ] Data availability statement
- [ ] Ethics approvals included

## Document Type Routing

### Research Article → IMRAD Structure

Structure overview (references/paper-structure.md)

IMRAD sections:
- /I/ntroduction: Background, gap, objective
- /M/ethods: Reproducible experimental details
- /R/esults: Objective observations with data
- /A/nd
- /D/iscussion: Interpretation, implications, limitations

What goes where:
- Introduction: Why this work matters, what's unknown, what you'll do
- Methods: How you did it (enough detail to reproduce)
- Results: What you found (observations, not interpretations)
- Discussion: What it means, how it fits, what's next

Common mistakes to avoid:
- ❌ Interpretation in results section
- ❌ New results in discussion section
- ❌ Methods scattered in results
- ❌ Missing gap identification in introduction
- ❌ Ignoring limitations

### Review Article → Thematic Organization

See references/review-writing.md

Types:
- Narrative review: Broad overview
- Systematic review: Structured search (PRISMA)
- Meta-analysis: Quantitative synthesis

Key principles:
- Synthesize thematically, not chronologically
- Critical evaluation, not just summary
- Identify patterns, gaps, controversies
- Future directions

### Grant Proposal → Funder-Specific Structure

See references/grant-writing.md

Common elements:
- Specific Aims (1 page): Clear, testable objectives
- Significance: Why it matters, current knowledge, impact
- Innovation: What's novel about approach
- Approach: Methods, timeline, pitfalls, alternatives
- Preliminary data: Feasibility demonstration

Review criteria alignment:
- Address all criteria explicitly
- Use headings matching criteria
- Make reviewers' job easy

### Revision Response → Point-by-Point

See references/revision-response.md

Structure:
- Thank reviewers
- Summary of major changes
- Point-by-point responses with line numbers
- Track changes in manuscript

Response strategies:
- Agree and comply: Describe changes made
- Agree but can't comply: Explain why, offer alternative
- Disagree: Provide evidence diplomatically

## Section-Specific Guidance

### Introduction Writing

See references/introduction-writing.md

Funnel structure:
1. Broad context (why general topic matters)
2. Narrow to specific problem area
3. Identify gap in knowledge
4. State objective of this work
5. Brief approach overview (optional)

Length: Typically 1-3 pages

Tense: Present for established facts, past for previous studies

### Methods Writing

See references/methods-writing.md

Reproducibility checklist:
- Equipment: manufacturer, model, specs
- Reagents: source, catalog #, concentration
- Software: name, version, parameters
- Statistical tests with corrections
- Sample size justification
- Ethics approvals

Organization:
- Chronological (when order matters)
- By subsystem (complex systems)
- By measurement type (multiple assays)

Detail level:
- Standard procedures: Brief + citation
- Novel procedures: Full detail
- Modified procedures: Highlight changes

### Results Writing

See references/results-writing.md

Objectivity principles:
- Report observations, not interpretations
- "Data show" not "data prove"
- Present negative results honestly
- Save interpretation for discussion

Statistical reporting:
- Test statistic, df, exact p-value
- Effect sizes and confidence intervals
- Multiple comparison corrections
- Measures of variability (SD, SE, CI)

Figure integration:
- Reference every figure/table in text
- Describe key finding from each
- Don't just say "see Figure X"

### Discussion Writing

See references/discussion-writing.md

Structure:
1. Restate main findings (brief)
2. Interpret in context of literature
3. Compare with previous work
4. Explain unexpected findings
5. Acknowledge limitations
6. Discuss implications
7. Suggest future directions

Limitations:
- Be honest but not self-defeating
- Explain impact of limitations
- Suggest how to address
- Don't introduce obscure limitations

### Abstract Writing

See references/abstract-writing.md

Essential elements:
- Background (1-2 sentences)
- Objective
- Methods (brief approach)
- Results (key findings with data)
- Conclusions (significance)

Word limit strategies:
- Typical: 150-300 words
- Prioritize results and conclusions
- Remove modifiers
- Define abbreviations sparingly
- No citations (usually)

Self-contained requirement:
- Understandable without reading paper
- Include actual data, not just "significant"

## Universal Scientific Writing Principles

### 1. Clarity Over Complexity

- Simple words over complex when meaning is same
- Short sentences preferred
- One idea per sentence
- Active voice when possible (field norms vary)
- Define specialized terms

### 2. Precision in Language

- Specific numbers over vague terms
- "Approximately 50%" not "many"
- Distinguish "significant" (statistical) from "important"
- Clear about causation vs correlation
- Avoid hedging excessively ("relatively," "quite," "very")

### 3. Objectivity in Reporting

- Separate observations (results) from interpretations (discussion)
- Present negative results honestly
- Acknowledge contradictory evidence
- Don't overstate conclusions
- Appropriate level of certainty

### 4. Reproducibility in Methods

- Include all information needed to reproduce
- Equipment specifications
- Exact concentrations and conditions
- Statistical methods fully described
- Software versions and parameters
- Code availability when applicable

### 5. Logical Flow of Argument

- Each section builds on previous
- Clear transitions between ideas
- Coherent narrative throughout
- Introduction sets up discussion
- Discussion answers introduction's questions

### 6. Appropriate Detail for Audience

- Assume audience has field background
- Define specialized terms first use
- Balance between too much and too little detail
- Don't explain fundamental concepts
- Do explain novel techniques or applications

## Tense and Voice Usage Guide

### Tense by Section

Introduction:
- Present: Established facts ("DNA is composed of...")
- Past: Previous studies ("Smith et al. showed...")
- Present: Your objective ("This study investigates...")

Methods:
- Past: What you did ("Cells were cultured...")
- Past: ("We cultured cells...")

Results:
- Past: Your findings ("Expression increased...")
- Past: ("We observed increased expression...")

Discussion:
- Past: Your results ("Our data showed...")
- Present: Established facts ("This gene regulates...")
- Present: Interpretations ("These results suggest...")

Conclusions:
- Present: General conclusions ("This approach provides...")

### Voice by Field

Biology/Medicine:
- More passive acceptable in methods
- Either active or passive in other sections

Engineering/Computer Science:
- Active voice preferred throughout
- "We designed..." rather than "A design was created..."

Physics/Chemistry:
- Varies by journal and author preference
- Either acceptable if consistent

## Quick Reference - Common Issues

Results vs Discussion: Keep observations in results, interpretations in discussion

Citation Consistency: Use one style throughout (numbered [1] or author-year)

Figure References: Reference all figures/tables in text with findings, not just "see Figure X"

Statistical Reporting: Include test statistic, df, exact p-value, effect size, variability measure

Methods Detail: Include manufacturer, catalog #, concentrations for reproducibility

Limitations: Be honest but not self-defeating; explain impact, suggest solutions

See individual reference files for detailed examples and guidance.

## Tools and Utilities

### Citation Checker

```bash
python scripts/citation_checker.py manuscript.docx --style apa
```

Validates citation consistency between in-text and reference list.

### Figure Generator

```bash
python scripts/figure_generator.py data.csv config.yaml --output fig1.pdf
```

Creates publication-quality figures from data.

### Word Counter

```bash
python scripts/word_counter.py manuscript.docx
```

Counts words by section for length requirements.

### Readability Analyzer

```bash
python scripts/readability_analyzer.py section.txt
```

Analyzes text complexity and suggests improvements.

### Table Formatter

```bash
python scripts/table_formatter.py data.csv --format latex --journal nature
```

Formats tables for specific journals.

## Templates

Access templates for common document types:
- assets/templates/manuscript_template.docx - Generic manuscript
- assets/templates/imrad_template.md - IMRAD structure
- assets/templates/grant_aims_template.docx - NIH Specific Aims
- assets/templates/response_letter_template.docx - Revision response
- assets/templates/abstract_template.txt - Structured abstract
- assets/templates/methods_checklist.md - Reproducibility checklist

## Style Guides

Journal-specific quick references:
- assets/style-guides/apa_guide.md - APA style
- assets/style-guides/nature_guide.md - Nature requirements
- assets/style-guides/science_guide.md - Science requirements
- assets/style-guides/cell_guide.md - Cell requirements
- assets/style-guides/plos_guide.md - PLOS requirements
- assets/style-guides/nih_guide.md - NIH grant guidelines
- assets/style-guides/nsf_guide.md - NSF grant guidelines
