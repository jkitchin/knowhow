# Scientific Writing Skill

Comprehensive guidance for writing research papers, grants, and scientific communications.

## Overview

This skill provides systematic guidance through all aspects of scientific writing, from research paper structure to grant proposals to peer review responses. It covers the complete writing process with emphasis on clarity, reproducibility, and adherence to field conventions.

## Core Capabilities

1. **Paper Structure Guidance (IMRAD)** - Complete workflow from introduction through discussion
2. **Section-Specific Writing** - Detailed guidance for each paper section
3. **Citation Management** - Multiple citation styles and reference formatting
4. **Methods Writing** - Reproducibility-focused experimental details
5. **Results Presentation** - Objective, data-driven reporting
6. **Figure and Table Design** - Publication-quality visualizations
7. **Abstract Writing** - Structured abstracts within word limits
8. **Language Clarity** - Concise, precise scientific writing
9. **Grant Proposals** - NIH, NSF, and other funding agencies
10. **Literature Reviews** - Systematic synthesis of research
11. **Peer Review Responses** - Diplomatic point-by-point responses

## When to Use This Skill

- **Writing a research paper** - Use IMRAD structure and section-specific guidance
- **Preparing a grant proposal** - Follow funder-specific templates
- **Responding to reviewers** - Use diplomatic response strategies
- **Creating figures/tables** - Apply publication quality standards
- **Formatting citations** - Match journal citation style
- **Improving clarity** - Apply conciseness and precision principles
- **Writing abstracts** - Fit content in word limits

## Quick Start

### Writing a Research Paper

1. **Identify target journal** - Check requirements (length, format, citation style)
2. **Use IMRAD structure** - See `references/paper-structure.md`
3. **Write section by section:**
   - Introduction: `references/introduction-writing.md`
   - Methods: `references/methods-writing.md`
   - Results: `references/results-writing.md`
   - Discussion: `references/discussion-writing.md`
   - Abstract: `references/abstract-writing.md`
4. **Create figures/tables** - See `references/figure-design.md` and `references/table-design.md`
5. **Format citations** - See `references/citation-management.md`
6. **Check clarity** - See `references/language-clarity.md`

### Writing a Grant Proposal

1. **Identify funding agency** - NIH, NSF, ERC, etc.
2. **Follow structure** - See `references/grant-writing.md`
3. **Use templates** - `assets/templates/grant_aims_template.docx`
4. **Address review criteria** - Explicitly match funder requirements

### Responding to Reviewers

1. **Read all comments carefully**
2. **Use point-by-point format** - See `references/revision-response.md`
3. **Start from template** - `assets/templates/response_letter_template.md`
4. **Be diplomatic** - Thank, explain, specify changes

## File Structure

```
scientific-writing/
├── SKILL.md                          # Main skill coordination and workflow
├── README.md                         # This file
├── references/                       # Detailed writing guidance
│   ├── paper-structure.md           # IMRAD and alternative structures
│   ├── introduction-writing.md      # Funnel structure, gap identification
│   ├── methods-writing.md           # Reproducibility checklist
│   ├── results-writing.md           # Objective reporting with statistics
│   ├── discussion-writing.md        # Interpretation and implications
│   ├── abstract-writing.md          # Structured abstracts, word limits
│   ├── figure-design.md             # Publication-quality figures
│   ├── table-design.md              # Table structure and formatting
│   ├── citation-management.md       # Citation styles and reference formatting
│   ├── language-clarity.md          # Concise, precise writing
│   ├── grant-writing.md             # NIH/NSF proposal structure
│   ├── revision-response.md         # Responding to peer review
│   └── review-writing.md            # Literature review synthesis
├── scripts/                         # Utility scripts
│   ├── word_counter.py              # Count words by section
│   ├── readability_analyzer.py      # Analyze text complexity
│   ├── citation_checker.py          # Validate citations (placeholder)
│   ├── figure_generator.py          # Generate publication figures (placeholder)
│   └── table_formatter.py           # Format tables for journals (placeholder)
├── assets/
│   ├── templates/                   # Document templates
│   │   ├── imrad_template.md
│   │   ├── methods_checklist.md
│   │   └── response_letter_template.md
│   └── style-guides/                # Quick reference guides
│       ├── nature_guide.md
│       └── apa_guide.md
```

## Reference Documentation

### Paper Writing References

**`references/paper-structure.md`**
- Complete IMRAD structure breakdown
- Alternative structures (short communications, case reports, etc.)
- Field-specific variations (biology, chemistry, physics, engineering, CS)
- Section integration and flow
- What belongs where (common mistakes)

**`references/introduction-writing.md`**
- Funnel structure: Broad → Narrow → Gap → Objective
- Literature review synthesis (not chronological listing)
- Gap identification strategies (knowledge, methodological, application, resolution)
- Objective statement formats
- Tense usage (present for facts, past for previous studies)

**`references/methods-writing.md`**
- Reproducibility checklist (equipment, reagents, software, statistics)
- Organization strategies (chronological, by subsystem, by measurement type)
- Detail level guidelines (standard vs. novel vs. modified procedures)
- Field-specific patterns (wet lab, chemistry, computational, clinical, field studies)
- Statistical method reporting requirements

**`references/results-writing.md`**
- Objectivity principles (observations not interpretations)
- Organization strategies (chronological, by importance, by theme, by hypothesis)
- Figure/table integration (all must be referenced with findings)
- Complete statistical reporting (test statistic, df, exact p-value, effect size, variability)
- Common problems (interpretation in results, missing statistics, methods in results)

**`references/discussion-writing.md`**
- Discussion structure (restate findings, interpret, compare literature, limitations, implications, future)
- Interpretation strategies (support with evidence, consider alternatives)
- Literature integration (synthesize, compare/contrast, explain discrepancies)
- Limitations discussion (honest but not self-defeating)
- Tense usage (present for interpretations, past for results)

**`references/abstract-writing.md`**
- Abstract types (structured vs. unstructured)
- Essential elements (context, objective, methods, results with data, conclusions)
- Word limit strategies (150-300 words typical)
- Self-contained requirement (understandable without paper)
- Keywords selection (3-6, not repeating title)

### Formatting References

**`references/figure-design.md`**
- Figure types by data type (line, bar, scatter, box, heatmap, schematics, microscopy)
- Publication quality (300+ DPI, vector formats, proper sizing, readable fonts)
- Essential elements (axis labels, legends, error bars, statistical annotations, scale bars, panel labels)
- Caption writing (self-contained, describe all panels, define symbols)
- Colorblind-friendly palettes and accessibility

**`references/table-design.md`**
- When to use tables vs. figures (precise values vs. trends)
- Table structure (headers with units, consistent decimal places, footnotes)
- Formatting (horizontal lines only, decimal alignment)
- Caption writing
- Common problems (too much information, inconsistent sig figs, unclear abbreviations)

**`references/citation-management.md`**
- Citation styles (numbered Vancouver, author-year Harvard, author-number ACS, footnote Chicago)
- In-text citation rules (placement, multiple citations, et al. usage)
- Reference list formatting (journals, books, chapters, websites, preprints)
- Journal abbreviations (PubMed/ISO standards)
- Reference managers (Zotero, Mendeley, EndNote, BibTeX)

**`references/language-clarity.md`**
- Passive vs. active voice (field-dependent preferences)
- Conciseness strategies (remove redundancies, avoid nominalizations, eliminate fillers)
- Precision (avoid vague terms, distinguish correlation/causation, match certainty to evidence)
- Sentence structure (15-25 words average, main idea first, parallel structure)
- Common problems (jargon overuse, ambiguous pronouns, dangling modifiers, inconsistent terminology)

### Special Document Types

**`references/grant-writing.md`**
- Major funding agencies (NIH, NSF, ERC, Wellcome, national funders)
- NIH R01 structure (Specific Aims 1 page, Research Strategy 12 pages)
- Specific Aims page (problem, gap, objective, 3 aims, impact)
- Significance, Innovation, Approach sections
- Preliminary data requirements
- Review criteria alignment (make reviewers' job easy)

**`references/revision-response.md`**
- Response letter structure (thank reviewers, summary, point-by-point, changes list)
- Response strategies (agree/comply, agree/can't comply, disagree diplomatically, clarify)
- Diplomatic language ("We thank... We respectfully disagree... We appreciate...")
- Tracking changes (highlight all, reference line numbers)
- Major vs. minor revisions

**`references/review-writing.md`**
- Review types (narrative, systematic, meta-analysis, scoping)
- Thematic organization (not chronological listing)
- Synthesis strategies (identify patterns, compare/contrast, highlight controversies)
- Critical evaluation (assess quality, note limitations, identify biases)
- Figure/table types (summary tables, conceptual figures, meta-analysis plots)

## Utility Scripts

### Word Counter
```bash
python scripts/word_counter.py manuscript.md
python scripts/word_counter.py manuscript.docx --exclude-refs
```
Counts words by section (Abstract, Introduction, Methods, Results, Discussion, Conclusions) for checking length requirements.

### Readability Analyzer
```bash
python scripts/readability_analyzer.py text_file.txt
python scripts/readability_analyzer.py --text "Your text here"
```
Analyzes readability metrics:
- Flesch Reading Ease score
- Average sentence length
- Complex word percentage
- Problem phrases
- Suggestions for improvement

### Other Tools (Placeholders)

**Citation Checker:** Validate citation consistency
**Figure Generator:** Create publication-quality matplotlib figures
**Table Formatter:** Format tables for specific journals

## Templates

**IMRAD Template** (`assets/templates/imrad_template.md`)
- Complete manuscript structure with section prompts
- Use as starting point for research papers

**Methods Checklist** (`assets/templates/methods_checklist.md`)
- Comprehensive checklist for reproducible methods
- Ensures all essential details included

**Response Letter Template** (`assets/templates/response_letter_template.md`)
- Point-by-point response format
- Professional, grateful tone
- Track changes systematically

## Style Guides

**Nature Guide** (`assets/style-guides/nature_guide.md`)
- Quick reference for Nature journal requirements
- Citation format, figure specs, formatting

**APA Guide** (`assets/style-guides/apa_guide.md`)
- APA 7th edition quick reference
- In-text citations, reference list, formatting

*(Additional journal guides can be added as needed)*

## Workflow Examples

### Example 1: Writing Your First Research Paper

1. Review IMRAD structure (`references/paper-structure.md`)
2. Write Introduction using funnel approach (`references/introduction-writing.md`)
3. Document Methods with reproducibility checklist (`references/methods-writing.md`)
4. Report Results objectively with statistics (`references/results-writing.md`)
5. Interpret in Discussion (`references/discussion-writing.md`)
6. Create publication-quality figures (`references/figure-design.md`)
7. Format citations for target journal (`references/citation-management.md`)
8. Write concise Abstract (`references/abstract-writing.md`)
9. Check clarity and conciseness (`references/language-clarity.md`)
10. Review against journal requirements

### Example 2: Responding to Peer Review

1. Read decision letter and all comments carefully
2. Categorize comments (easy/hard, agree/disagree)
3. Address major experiments/revisions first
4. Use response template (`assets/templates/response_letter_template.md`)
5. Follow diplomatic language guidelines (`references/revision-response.md`)
6. Track all changes with line numbers
7. Proofread response letter
8. Submit before deadline

### Example 3: Writing an NIH Grant Proposal

1. Study NIH grant structure (`references/grant-writing.md`)
2. Draft Specific Aims page (1 page, no citations/figures)
3. Write Significance section (why important, impact)
4. Write Innovation section (what's novel)
5. Write Approach section by Aim (design, expected results, problems/alternatives)
6. Include preliminary data supporting feasibility
7. Align with review criteria
8. Get feedback from mock review panel
9. Revise based on feedback
10. Submit complete application

## Best Practices

### Writing Process

1. **Start with structure** - Use IMRAD or appropriate template
2. **Write sections in order** - Methods → Results → Discussion → Introduction → Abstract
3. **One section at a time** - Focus on completing each section
4. **Create figures early** - Visualizations help organize results
5. **Cite as you write** - Use reference manager to stay organized
6. **Get feedback** - Colleagues, advisors, writing groups
7. **Revise multiple times** - First draft is never final
8. **Check against requirements** - Word limits, formatting, style

### Common Mistakes to Avoid

❌ **Results in Discussion** - Keep observations in Results, interpretations in Discussion
❌ **Interpretation in Results** - "Data suggest..." belongs in Discussion
❌ **New Results in Discussion** - All results must be in Results section first
❌ **Methods in Results** - Detailed methods belong in Methods section
❌ **Missing Statistical Details** - Always include test, df, exact p-value
❌ **Figures Not Referenced** - All figures/tables must be mentioned in text
❌ **Inconsistent Citations** - Use one style throughout
❌ **Vague Language** - "Many samples" → "50 samples"
❌ **Overstating Conclusions** - Match certainty level to evidence
❌ **Ignoring Limitations** - Every study has limitations, acknowledge honestly

## Tips for Success

**Clarity:**
- Use simple words when possible
- Short to medium sentences (15-25 words average)
- One main idea per sentence
- Active voice preferred (field-dependent)

**Precision:**
- Specific numbers over vague terms
- Distinguish statistical significance from importance
- Clear about causation vs. correlation
- Avoid hedging excessively

**Organization:**
- Logical flow from broad to specific
- Clear transitions between sections
- Each paragraph has topic sentence
- Consistent terminology throughout

**Completeness:**
- All essential details for reproducibility
- All figures/tables referenced and described
- All citations complete and consistent
- All review criteria addressed (grants)

## Additional Resources

**For more information on scientific writing:**
- APA Publication Manual (7th edition)
- "The Elements of Style" by Strunk and White
- "Writing Science" by Joshua Schimel
- "How to Write a Lot" by Paul Silvia
- Journal-specific author guidelines

**For grant writing:**
- NIH grant writing tips: https://grants.nih.gov/grants/how-to-apply-application-guide.html
- NSF proposal guide: https://www.nsf.gov/pubs/policydocs/pappg22_1/pappg_2.jsp

**For citations:**
- Zotero: https://www.zotero.org/
- Mendeley: https://www.mendeley.com/
- EndNote: https://endnote.com/

## Contributing

To extend this skill:
- Add journal-specific style guides to `assets/style-guides/`
- Create additional templates for specific document types
- Implement full functionality for placeholder scripts
- Add examples from your field
- Share tips and best practices

## License

This skill is part of the skillpack project.
