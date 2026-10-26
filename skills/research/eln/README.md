# Electronic Lab Notebook (ELN) Skill

Professional scientific documentation using org-mode for reproducible research and comprehensive record-keeping.

## What This Skill Does

This skill enhances Claude Code with expertise in maintaining professional electronic lab notebooks, enabling it to help you:

- **Structure notebook entries** - Create well-organized, date-based research documentation
- **Document experiments** - Record hypotheses, methods, results, and conclusions
- **Ensure reproducibility** - Include all details needed to reproduce your work
- **Use org-mode effectively** - Leverage properties, tags, links, and code blocks
- **Maintain research integrity** - Follow best practices for scientific documentation
- **Cross-reference work** - Link related entries and build knowledge networks
- **Archive data** - Organize data files and computational outputs
- **Generate summaries** - Create project overviews and progress reports

## When to Use This Skill

Claude will automatically use this skill when you're working on lab notebook documentation. You can also explicitly request it:

- "Using the eln skill, help me document this experiment"
- "Create a lab notebook entry for today's calculations"
- "How should I document this failed attempt?"
- "Help me write a monthly summary of my research"

## Core Principles

### 1. Chronological Organization
Files organized by date for easy navigation:
```
notebook/
├── 2025/
│   ├── 01-January/
│   │   ├── 2025-01-15.org
│   │   └── 2025-01-20.org
│   └── 02-February/
```

### 2. Complete Documentation
Every entry includes:
- **What** - Detailed description of work performed
- **Why** - Hypothesis, motivation, reasoning
- **How** - Methods, procedures, parameters
- **Results** - Observations, data, outputs
- **Analysis** - Interpretation and meaning
- **Next** - Follow-up work and questions

### 3. Reproducibility
Documentation enables anyone to:
- Understand your reasoning
- Reproduce your work exactly
- Access all data and code
- Follow your logic chain

### 4. Professional Standards
- Clear, professional writing
- Honest reporting (including failures)
- Dated and timestamped entries
- Never delete past entries (make corrections forward)
- Sufficient detail for independent reproduction

## Example Entry Structure

```org
#+TITLE: Lab Notebook - 2025-01-15
#+AUTHOR: Your Name
#+DATE: [2025-01-15 Wed]
#+FILETAGS: :experiment:catalyst:

* Daily Summary
Validated DFT methodology for catalyst screening project.
Compared three functionals against experimental data.
Selected PBE for production runs.

* [09:30] DFT Functional Validation
:PROPERTIES:
:ID: 2025-01-15-001
:PROJECT: Catalyst_Screening
:STATUS: Complete
:END:

** Objective
Determine which DFT functional best reproduces experimental
CO adsorption energies on Pt(111).

** Hypothesis
PBE will provide reasonable agreement (within 0.3 eV) based
on literature precedent.

** Methods
Calculated CO adsorption using three functionals:
- PBE (standard GGA)
- PBE+D3 (with dispersion)
- RPBE (revised PBE)

Parameters: 400 eV cutoff, 6×6×1 k-points, 0.05 eV/Å forces

** Results
| Functional | E_ads (eV) | Experiment | Error |
|------------+------------+------------+-------|
| PBE        |     -1.82  |      -1.60 | -0.22 |
| PBE+D3     |     -2.15  |      -1.60 | -0.55 |
| RPBE       |     -1.45  |      -1.60 |  0.15 |

** Analysis
- PBE shows best agreement (error 0.22 eV)
- PBE+D3 significantly overbinds (0.55 eV error)
- RPBE underestimates binding

** Conclusions
**Decision: Use PBE for production calculations.**
Expected error ~0.2 eV, acceptable for screening purposes.

** Next Steps
- [ ] Begin screening of FCC metals
- [ ] Document PBE choice in methods section
```

## Key Features

### Org-Mode Integration

**Properties Drawer** - Metadata for organization
```org
:PROPERTIES:
:ID: unique-identifier
:PROJECT: Project_Name
:STATUS: Planning|In_Progress|Complete
:RELATED: [[link-to-related-work]]
:END:
```

**Tags** - For filtering and search
```org
#+FILETAGS: :experiment:simulation:catalyst:
* Entry Title                                    :important:urgent:
```

**Links** - Cross-reference related work
```org
[[file:2025-01-10.org::*Previous Results]]
[[file:~/data/experiment_001.csv][Data file]]
```

**Code Blocks** - Reproducible analysis
```org
#+BEGIN_SRC python :results output :exports both
import pandas as pd
data = pd.read_csv('results.csv')
print(f"Mean: {data['energy'].mean():.3f} eV")
#+END_SRC

#+RESULTS:
: Mean: -1.234 eV
```

**Tables** - Organized data
```org
| Parameter | Value | Units |
|-----------+-------+-------|
| Temp      |   300 | K     |
| Pressure  |     1 | atm   |
```

## Example Interactions

### Example 1: Starting New Work
```
You: I'm about to run DFT calculations to find the optimal
lattice constant for copper. Help me create a notebook entry.

Claude: I'll help you create a comprehensive notebook entry for
your lattice optimization study...

[Provides structured org-mode entry with:
- Objective (find equilibrium lattice constant)
- Hypothesis (expected around 3.6 Å based on experiment)
- Methods (EOS fitting approach)
- Results template (table for a vs E data)
- Analysis section (comparison with literature)
- Next steps]
```

### Example 2: Documenting Failure
```
You: My VASP calculation failed to converge. How should I
document this?

Claude: It's important to document failed attempts - they're
valuable learning. Let me help you create an entry...

[Provides template including:
- What was attempted
- Error messages/symptoms
- Troubleshooting steps taken
- Root cause analysis
- Solution or next approach
- Lessons learned]
```

### Example 3: Literature Review
```
You: I just read an important paper on CO oxidation catalysis.
Help me document the key points.

Claude: I'll help you create a literature review entry...

[Provides structure for:
- Paper citation
- Key findings
- Relevance to your work
- Questions raised
- Follow-up references]
```

### Example 4: Monthly Summary
```
You: Help me write a summary of this month's research

Claude: I'll help you create a comprehensive monthly summary...

[Provides template for:
- Overview of accomplishments
- Key results and breakthroughs
- Problems encountered and solved
- Data generated/archived
- Publications/presentations
- Next month's goals]
```

## Entry Types

The skill helps with multiple entry types:

1. **Experimental/Computational Work** - Detailed documentation of calculations or experiments
2. **Literature Review** - Summaries of important papers
3. **Data Analysis** - Processing and interpreting results
4. **Meeting Notes** - Record of discussions and decisions
5. **Problem Solving** - Debugging and troubleshooting
6. **Project Planning** - Organizing future work
7. **Progress Reports** - Summaries for advisors/collaborators

## Best Practices

### Document Everything
- Successful experiments AND failures
- Expected results AND surprises
- Clean data AND anomalies
- Final conclusions AND open questions

### Write for Reproducibility
- Include all parameters and settings
- Link to code, data, and input files
- Document software versions
- Provide enough detail for others to reproduce

### Be Honest and Complete
- Report negative results
- Acknowledge limitations
- Document mistakes and how you fixed them
- Note uncertainties and assumptions

### Cross-Reference Liberally
- Link to related entries
- Reference previous work
- Connect to literature
- Build knowledge network

## Skill Contents

- **SKILL.md** - Complete ELN reference (~450 lines)
  - Organization principles
  - Entry templates for all types
  - Org-mode features guide
  - Best practices
  - Reproducibility standards

- **QUICK_REFERENCE.md** - Quick lookup guide
  - Common templates
  - Org-mode syntax
  - Tag conventions
  - Search commands

- **templates/** - Ready-to-use templates
  - Daily entry template
  - Experiment template
  - Analysis template
  - Meeting notes template
  - Literature review template

## Directory Structure

Recommended organization:
```
research-notebook/
├── 2025/
│   ├── 01-January/
│   │   ├── 2025-01-15.org     # Daily entries
│   │   └── data/               # Associated data
│   │       └── 2025-01-15/
│   │           ├── results.csv
│   │           └── plot.png
│   └── 02-February/
├── templates/                   # Entry templates
├── index.org                    # Master index
└── README.org                   # Project overview
```

## Tips for Effective Use

1. **Start simple** - Begin with basic structure, add complexity as needed
2. **Write daily** - Document while fresh, not weeks later
3. **Use templates** - Saves time and ensures consistency
4. **Tag consistently** - Makes searching easier
5. **Link freely** - Build connections between related work
6. **Include code** - Embed analysis scripts for reproducibility
7. **Archive data** - Keep data organized with entries
8. **Review regularly** - Monthly summaries help track progress

## Integration with Research Workflow

### Version Control
```org
** Code Version
Git commit: a3f5e2b
Repository: ~/projects/catalyst-screening
```

### Data Management
```org
** Data Files
- Raw: [[file:./data/2025-01-15/OUTCAR]]
- Processed: [[file:./data/2025-01-15/results.csv]]
- Archive: ~/archives/2025/january/calc_001.tar.gz
```

### Computational Details
```org
** Environment
- VASP: 6.4.2
- Python: 3.11.4
- ASE: 3.23.0
- Submitted to: cluster.university.edu
- Job ID: 123456
```

## Why Org-Mode?

- **Plain text** - Future-proof, version control friendly
- **Structured** - Hierarchical organization
- **Programmable** - Execute code inline
- **Linkable** - Connect related information
- **Exportable** - Convert to PDF, HTML, LaTeX
- **Searchable** - Powerful search and filtering
- **Extendable** - Rich ecosystem of tools

## Related Skills

- `python-ase` - For computational chemistry workflows
- `fairchem` - For machine learning potentials
- `python-pymatgen` - For materials analysis

## Resources

- [Org-mode Manual](https://orgmode.org/manual/)
- [Org-mode for Research](https://orgmode.org/worg/org-contrib/babel/)
- [Reproducible Research with Org-mode](https://orgmode.org/worg/org-contrib/babel/intro.html)

## Contributing

If you have suggestions for improving this skill:
1. Share effective documentation patterns
2. Suggest additional entry types
3. Contribute template improvements
4. Share org-mode tips and tricks

## License

This skill documentation is part of the knowhow project (MIT License).
