---
name: literature-review
description: |
  Conduct systematic scientific literature reviews by integrating multi-source searches, iterative analysis, and synthesis into well-structured reports with proper citations.

  Use this skill when you need to: synthesize knowledge across multiple research domains, identify research gaps, track the evolution of methodologies, evaluate evidence quality, or write comprehensive literature reviews for academic papers, grant proposals, or research projects.

  Key capabilities: multi-database search strategies, iterative query refinement, content analysis and summarization, thematic synthesis, citation management, quality assessment, bias detection, and structured report generation with multiple output formats.
allowed-tools: ["*"]
---

# Scientific Literature Review Skill

## Overview

This skill guides comprehensive, systematic literature reviews that combine automated search capabilities across multiple academic databases with iterative analysis and synthesis into well-structured reports. It transforms the literature review process from a manual, time-consuming task into an efficient, systematic, and reproducible research methodology.

## When to Use This Skill

Use this skill when you need to:

- **Comprehensive Knowledge Synthesis**: Gather and integrate knowledge across multiple research domains or methodologies
- **Research Gap Identification**: Identify underexplored areas, conflicting findings, or methodological limitations
- **Methodology Tracking**: Understand the evolution and current state of research methodologies and techniques
- **Evidence Evaluation**: Assess the quality, reliability, and significance of research findings
- **Literature-Supported Writing**: Write evidence-based sections for papers, grants, dissertations, or technical reports
- **Research Foundation**: Build a solid foundation for new research by understanding prior work
- **Systematic Assessment**: Conduct systematic reviews, meta-analyses, or structured literature analyses
- **Knowledge Documentation**: Create comprehensive, citable references for complex research domains

## CRITICAL: Citation Verification Requirements

**Every citation included in a literature review MUST be verified before inclusion.** Hallucinated or fabricated citations undermine scientific integrity and are unacceptable.

### Mandatory Verification Protocol

Before including ANY citation in the review, you MUST complete one of these verification steps:

1. **CrossRef API Verification** (Preferred for DOIs)
   - Query `https://api.crossref.org/works/{doi}` via WebFetch
   - Confirm the paper exists and metadata matches (title, authors, year)
   - Extract the verified DOI for inclusion

2. **WebSearch Verification** (For papers without known DOIs)
   - Search for the exact paper title in quotes
   - Verify the paper appears in search results with matching authors/year
   - Obtain the actual URL or DOI from search results

3. **Database Search Verification** (For specific databases)
   - Search PubMed, arXiv, or domain-specific databases
   - Confirm the paper exists with matching metadata
   - Record the database identifier (PMID, arXiv ID, etc.)

4. **User-Provided References** (Still require verification)
   - Even if the user provides a reference, verify it exists
   - Confirm the DOI resolves or URL is accessible
   - Report any discrepancies to the user

### Verification Workflow

For each paper you intend to cite:

```
1. SEARCH: Find the paper via WebSearch or database query
2. VERIFY: Confirm paper exists (check DOI via CrossRef or URL via WebFetch)
3. EXTRACT: Record verified metadata (title, authors, journal, year, DOI/URL)
4. CITE: Only include the citation after verification succeeds
5. FLAG: If verification fails, DO NOT include the citation
```

### What NOT to Do (Forbidden Practices)

**NEVER do any of the following:**

1. **Never fabricate DOIs**
   - Do NOT create DOIs by pattern-matching (e.g., guessing `10.1038/` + random numbers)
   - Do NOT assume a DOI format based on publisher patterns
   - If you don't have a verified DOI, don't include one

2. **Never include unverified citations**
   - Do NOT cite papers you haven't confirmed exist
   - Do NOT assume a paper exists because it "sounds plausible"
   - Do NOT include citations based on memory or training data alone

3. **Never fabricate author names**
   - Do NOT guess author names or initials
   - Do NOT create plausible-sounding author combinations
   - Only use author names from verified sources

4. **Never guess bibliographic details**
   - Do NOT invent page numbers, volume numbers, or issue numbers
   - Do NOT fabricate journal names or conference proceedings
   - Do NOT estimate publication years

5. **Never cite papers you cannot verify**
   - If CrossRef returns 404, the DOI doesn't exist - don't use it
   - If WebSearch finds no matching paper, it may not exist - don't cite it
   - If you cannot access verification, explicitly state "citation unverified"

### Acceptable Citation Sources

Citations may ONLY come from:

| Source | Verification Method | What You Get |
|--------|---------------------|--------------|
| CrossRef API | WebFetch to `api.crossref.org/works/{doi}` | Verified DOI, title, authors, journal, year |
| WebSearch Results | Search with paper title in quotes | URL to actual paper, metadata from results |
| PubMed | Search or direct PMID lookup | PMID, verified metadata |
| arXiv | Search or direct arXiv ID lookup | arXiv ID, verified metadata |
| Google Scholar | WebSearch with `site:scholar.google.com` | Link to paper, citation metadata |
| Publisher websites | WebFetch to paper URL | Confirmed existence, DOI if available |
| User-provided references | Must still verify via above methods | Confirmed accuracy |

### Handling Verification Failures

When verification fails:

1. **Paper not found**: Do NOT include the citation. Instead, note: "Unable to verify reference for [topic]. Further manual verification needed."

2. **Partial match**: If metadata partially matches but differs (different year, slightly different title), report the discrepancy and use ONLY the verified information.

3. **Access restricted**: If you cannot verify due to paywalls or access limits, explicitly mark as "[Verification pending - paywall]" and recommend manual verification.

4. **Conflicting information**: If multiple sources give conflicting metadata, use the DOI-registered metadata from CrossRef as authoritative.

### Citation Format After Verification

Only after verification, format citations as:

```
Author(s). "Title." Journal, Volume(Issue), Pages (Year). DOI or URL

Example (verified):
Smith, J., & Jones, M. "Deep Learning for Medical Imaging." Nature Medicine, 29(3), 456-467 (2023). https://doi.org/10.1038/s41591-023-02345-6
```

If DOI is unavailable but URL is verified:
```
Smith, J., & Jones, M. "Deep Learning for Medical Imaging." Nature Medicine (2023). https://www.nature.com/articles/s41591-023-02345-6
```

### Verification Documentation

For transparency, maintain a verification log:

```
| Citation | Verification Method | Status | Notes |
|----------|---------------------|--------|-------|
| Smith et al. 2023 | CrossRef API | Verified | DOI: 10.1038/xxx |
| Jones 2022 | WebSearch | Verified | URL confirmed |
| Brown et al. 2021 | CrossRef API | FAILED | DOI not found - excluded |
| Lee 2020 | PubMed | Verified | PMID: 12345678 |
```

### Integration with Citation-Verifier Skill

After completing the literature review, use the `citation-verifier` skill to perform a final audit of all citations in the document. This provides an independent verification pass to catch any errors.

## Literature Review Types

### 1. Narrative Literature Reviews
- **Purpose**: Provide comprehensive overview of a research topic
- **Scope**: Broad, subjective assessment of literature
- **Search Strategy**: Exploratory, iterative search across multiple angles
- **Report Structure**: Thematic organization by research concepts
- **Best For**: Introducing new research areas, providing context for research questions
- **Timeline**: 4-12 weeks for comprehensive review

### 2. Systematic Literature Reviews
- **Purpose**: Answer specific research questions using explicit methodology
- **Scope**: Comprehensive, predefined search with inclusion/exclusion criteria
- **Search Strategy**: Exhaustive search of specified databases
- **Report Structure**: PRISMA-compliant with search strategy documentation
- **Best For**: Evidence synthesis, clinical decision-making, policy development
- **Timeline**: 3-12 months for comprehensive review

### 3. Meta-Analyses
- **Purpose**: Quantitative synthesis of comparable study results
- **Scope**: Systematic review with statistical analysis
- **Search Strategy**: Identical to systematic reviews
- **Report Structure**: Statistical analysis with forest plots and funnel plots
- **Best For**: Combining results from multiple studies to determine overall effect
- **Timeline**: 6-18 months

### 4. Scoping Reviews
- **Purpose**: Map research landscape, identify key concepts and gaps
- **Scope**: Broader than systematic reviews, flexible inclusion criteria
- **Search Strategy**: Iterative, including grey literature
- **Report Structure**: Overview of research landscape with gap identification
- **Best For**: Emerging research areas, protocol development
- **Timeline**: 2-6 months

## Systematic Literature Review Workflow

### Phase 1: Planning and Question Formulation

#### Step 1: Define Research Question
Transform broad research interests into specific, answerable questions using PICO/PEO framework:

- **P**opulation/Problem: Who/what is the focus? (e.g., patients, methodologies, organisms)
- **I**ntervention/Indicator: What is being studied? (e.g., treatment, technique, technology)
- **C**omparison: What alternative is compared? (optional, but recommended)
- **O**utcome: What results/impacts matter? (e.g., effectiveness, efficiency, validity)
- **E**xperience (for qualitative): What are participants' perspectives?

**Example PICO Questions:**
- "What is the effectiveness of deep learning methods compared to traditional machine learning for medical image analysis in cancer detection?"
- "What methodologies are used to assess uncertainty in computational chemistry predictions?"
- "How do research groups address reproducibility in high-throughput screening studies?"

#### Step 2: Establish Scope and Criteria

**Define Inclusion/Exclusion Criteria:**
- Document type (peer-reviewed journals, preprints, grey literature)
- Time period (publication date range)
- Language (English-only or other languages)
- Study design (specific methodologies, approaches)
- Population/scope (specific organisms, systems, technologies)
- Quality thresholds (minimum standards for inclusion)

**Example Inclusion Criteria:**
- Peer-reviewed research articles published 2015-2025
- English language publications
- Empirical studies with quantitative or qualitative methodology
- Focus on computational methods in materials science
- Articles with >10 citations or published in high-impact journals (alternative: no citation threshold for very recent work)

#### Step 3: Plan Search Strategy

**Select Appropriate Databases:**
- **PubMed/MEDLINE**: Biomedical and life sciences literature
- **arXiv**: Preprints in physics, mathematics, computer science, statistics
- **Web of Science**: Multidisciplinary citation index with impact metrics
- **Scopus**: Large multidisciplinary abstract and citation database
- **IEEE Xplore**: Engineering and computer science literature
- **ACM Digital Library**: Computer science and information technology
- **Springer Link**: Multidisciplinary academic publisher
- **ProQuest**: Dissertations, theses, and comprehensive database
- **Google Scholar**: Broad academic search (verify findings in other databases)
- **Domain-Specific Repositories**: ArXiv (physics), bioRxiv (biology), chemRxiv (chemistry), SSRN (social sciences)

**Formulate Search Queries:**
- Use Boolean operators (AND, OR, NOT)
- Include synonyms and related terms
- Use wildcards and truncation (* for variations)
- Apply field-specific search syntax for each database
- Test query effectiveness before scaling

**Example Boolean Queries:**
- "machine learning" AND ("medical imaging" OR "diagnosis") AND ("cancer" OR "oncology")
- ("deep learning" OR "neural network*") NOT "toy dataset*"
- "materials discovery" AND (high-throughput OR computational) AND (screening OR optimization)

#### Step 4: Prepare Documentation System

Create a searchable, organized system for tracking:
- Search strategies and queries used
- Databases searched and date ranges
- Number of results per search
- Selection decisions and reasoning
- Paper characteristics (methodology, quality, relevance)
- Extracted data and findings
- Progress tracking and milestones

Recommended tools and formats:
- Spreadsheet/database: Track all papers with metadata
- Reference manager: Store full citations and PDFs (Zotero, Mendeley, EndNote)
- Note-taking system: Detailed notes on each paper
- Search log: Document all searches performed

### Phase 2: Initial Broad Search

#### Step 5: Execute Broad Searches

**Search across selected databases:**
1. Start with primary query formulation
2. Execute search in each database
3. Limit results (usually by date range, document type)
4. Export results with complete metadata
5. Document search parameters and result counts

**Expected workflow:**
- Initial searches typically return 100-5,000+ results depending on topic breadth
- For broad topics, expect 500-5,000 results
- For narrow topics, expect 50-500 results
- If results exceed 10,000, refine search strategy

**Documentation:**
```
Search #1: "machine learning" AND "medical imaging"
Database: PubMed
Date: 2025-01-15
Results: 2,847 papers
Time period: 2015-2025
Filters: English language, human studies excluded at this stage
Export: PubMed format with abstracts
Notes: High number of results requires refinement
```

#### Step 6: Initial Screening

**Level 1: Title and Abstract Screening**

Review titles and abstracts to identify potentially relevant papers:

Inclusion criteria:
- Research question directly related
- Appropriate study type/design
- Relevant population/scope
- Outcome measures align with review objectives

Exclusion criteria:
- Clearly outside research scope
- Wrong study type (e.g., looking for empirical research but paper is opinion/editorial)
- Duplicate publications
- Conference abstracts without full papers (unless specified in protocol)

**Process:**
- Read title first (quick elimination of obviously irrelevant papers)
- Read abstract to verify relevance
- When uncertain, include rather than exclude (error on side of inclusion)
- Use systematic approach: every paper evaluated by same criteria
- Document decisions: Include, Exclude, or Uncertain

**Expected results:**
- Broad searches: typically 10-30% of papers pass initial screening
- Refined searches: typically 30-60% pass
- If <5% pass, search strategy may be too narrow or inclusion criteria too strict

**Tracking:**
```
Database: PubMed
Initial results: 2,847
Title screening: 1,200 eliminated (obviously off-topic)
Abstract screening: 847 eliminated (wrong study type, unclear relevance)
Potentially relevant: 800 papers
Pass rate: 28%
```

### Phase 3: Iterative Search Refinement

#### Step 7: Concept and Keyword Extraction

From the initially relevant papers (Phase 2), identify:

**New keywords and concepts:**
- Terminology variations used by different research groups
- Specific methodologies mentioned repeatedly
- Technical terms and specialized vocabulary
- Author names appearing frequently
- Key research institutions/groups
- Specific journal names publishing in this area

**Analysis method:**
- Read abstracts and introductions of included papers
- Note any keywords not in original search strategy
- Identify methodological approaches (e.g., specific algorithms, experimental designs)
- Document emerging themes and subtopics

**Example extraction:**
```
Original search: "machine learning" + "medical imaging"
Extracted concepts:
- Specific methodologies: convolutional neural networks, attention mechanisms, transformer models
- Medical applications: radiotherapy planning, pathology analysis, diagnostic support
- Technical terms: semi-supervised learning, transfer learning, domain adaptation
- Related areas: data augmentation, interpretability, fairness in AI
- Key authors: [list of frequently appearing researchers]
- Important journals: IEEE TMI, Medical Image Analysis, Nature Medicine
```

#### Step 8: Citation Mining and Author Tracking

**Follow reference trails:**
1. Review reference lists of included papers
2. Identify papers cited multiple times (signal importance)
3. Retrieve and evaluate highly-cited references
4. Look for foundational/seminal papers in field

**Author tracking:**
1. Identify key researchers with multiple papers in review
2. Search for recent publications by these authors
3. Review their recent works not captured in initial searches
4. Check co-authors for related research

**Citation tracking (forward citation searching):**
1. Use Web of Science, Scopus, or Google Scholar
2. Find papers that cite key included papers
3. Evaluate citing papers for relevance
4. Identify recent developments building on earlier work

**Process:**
```
Key paper: "Deep Learning for Medical Image Analysis" (Smith et al., 2020)
Citation count: 1,247 (as of Jan 2025)
Recent citing papers (2023-2025): 342
Evaluate: Random sample or all, depending on review scope
References cited: 198 papers
New papers identified: 23 additional relevant papers
```

#### Step 9: Targeted Methodology-Based Searches

Based on identified methodologies, conduct focused searches:

**Examples:**
- Original: "machine learning" + "medical imaging"
- Refined searches:
  - "convolutional neural networks" + "radiology"
  - "attention mechanisms" + "medical images"
  - "transfer learning" + "diagnostic imaging"
  - "federated learning" + "clinical data"

**Process:**
1. Take each identified methodology
2. Combine with population/domain from original question
3. Execute new searches in selected databases
4. Screen results using same inclusion/exclusion criteria
5. Integrate new papers into literature base

#### Step 10: Gap Identification and Targeted Search

Identify underexplored areas:

**Questions to investigate:**
- "What specific applications are missing?"
- "Are there contradictory findings in any area?"
- "What methodological approaches haven't been compared?"
- "What populations/domains are underrepresented?"
- "What time periods show publication gaps?"

**Targeted searches:**
- Searches designed to find papers on identified gaps
- May use different search strategies (e.g., seeking negative results, null findings)
- Searches for specific applications or populations
- Temporal searches (recent developments)

**Convergence assessment:**
- Monitor if each new search finds mostly previously identified papers
- Track percentage of truly new papers with each search iteration
- Indicate saturation when <10-15% of results are new

#### Step 11: Temporal Analysis

**Track research evolution:**
1. Group papers by publication year
2. Identify trends in methodology adoption
3. Note shifts in research focus or populations studied
4. Identify recently emerging topics

**Visualization:**
```
2015: 15 papers (foundational period)
2016: 23 papers (growth phase)
2017: 45 papers (expansion)
2018: 89 papers (mainstream adoption)
2019: 156 papers (rapid growth)
2020: 289 papers (explosion due to...)
2021: 312 papers (continued growth)
2022: 298 papers (plateau)
2023: 276 papers (slight decline in pure methodology papers)
2024: 214 papers (applications and variants increasing)
2025: 127 papers (partial year, trend toward...)
```

### Phase 4: Full-Text Review and Data Extraction

#### Step 12: Full-Text Screening

**Level 2: Detailed Full-Text Review**

For all papers passing abstract screening:

1. Obtain full text (use university library, ResearchGate, contact authors)
2. Read complete paper carefully
3. Apply detailed inclusion/exclusion criteria
4. Extract structured data
5. Assess quality

**Detailed screening process:**
- Read introduction for research context and questions
- Review methodology for study design and quality
- Examine results for outcome measures
- Assess conclusions for validity and scope
- Document reasons for exclusion if not included

**Tracking results:**
```
Papers for full-text review: 800
Full text obtained: 775 (97%)
Unable to obtain: 25 (contact authors or wait)
After full-text screening: 312 included
Excluded (with reasons):
  - Wrong study design: 156
  - No relevant outcomes: 189
  - No original data: 78
  - Data quality concerns: 40
  - Duplicate/updated version: 22
```

#### Step 13: Structured Data Extraction

Create standardized extraction form for consistent data collection:

**Bibliographic information:**
- Authors, year, journal, volume/issue, pages, DOI
- Publication type (original research, review, methodological)
- Journal impact factor (if relevant)

**Study characteristics:**
- Study design/methodology
- Population/scope (sample size, characteristics, organisms/systems studied)
- Intervention/methodology tested
- Comparison groups (if applicable)
- Study duration and setting

**Results and findings:**
- Primary outcomes reported
- Quantitative results (effect sizes, p-values, confidence intervals)
- Qualitative findings (themes, patterns)
- Statistical analysis methods used
- Quality metrics and limitations acknowledged

**Quality assessment:**
- Design quality (randomization, blinding, sample size calculation)
- Data quality (missing data, response rates, measurement validity)
- Bias assessment (selection bias, performance bias, reporting bias)
- Generalizability/applicability
- Reproducibility assessment

**Thematic coding:**
- Primary research theme(s)
- Secondary themes
- Methodological approach(es)
- Key contributions
- Relevance to review objectives

**Extraction format:**
```
---
Authors: Smith, J., Jones, M.
Year: 2023
Title: [Full title]
Journal: Nature Medicine
Impact Factor: 73.5
DOI: 10.1038/xxxxx

Study Design: Randomized controlled trial
Population: Adult patients with diagnosis [X], n=2,847
Intervention: Treatment A (n=1,424)
Comparison: Standard treatment (n=1,423)
Primary Outcome: Reduction in symptom severity
Results: 45% reduction (95% CI: 38-52%) vs 18% (95% CI: 12-24%), p<0.001
Effect Size: Cohen's d = 1.2 (large effect)

Quality: High (GRADE rating: A)
Key Limitations: Single-center study, limited demographic diversity
Reproducibility: Good (methods detailed, data availability statement: Yes)

Themes: Treatment efficacy, Clinical outcomes, Comparative effectiveness
Innovation Level: Incremental (application of known methodology to new population)

---
```

### Phase 5: Synthesis and Analysis

#### Step 14: Thematic Organization

Group papers by key themes and organize findings:

**Organizational approaches:**

1. **By Methodology:**
   - Group papers using similar approaches
   - Compare methodological strengths/limitations
   - Track methodology evolution over time

2. **By Research Question/Aspect:**
   - Organize around components of research question (PICO elements)
   - Compare how different studies address each component
   - Integrate findings to answer overall question

3. **By Chronological Development:**
   - Show how ideas evolved
   - Track technological/methodological improvements
   - Highlight paradigm shifts

4. **By Research Group/Tradition:**
   - Organize by major research groups or schools of thought
   - Compare different theoretical frameworks
   - Note collaborations and conflicts

5. **By Population/Application Domain:**
   - Different populations studied
   - Different application contexts
   - Geographic or demographic patterns

**Example thematic map:**
```
Main Theme: Applications of Deep Learning in Medical Imaging

Subtopic 1: Cancer Diagnosis
├─ Breast cancer detection
│  ├─ Mammography analysis (45 papers)
│  ├─ Ultrasound (12 papers)
│  └─ MRI analysis (8 papers)
├─ Lung cancer detection (34 papers)
├─ Colorectal cancer (18 papers)
└─ Other cancers (22 papers)

Subtopic 2: Treatment Planning
├─ Radiotherapy planning (28 papers)
├─ Surgical guidance (15 papers)
└─ Patient monitoring (8 papers)

Subtopic 3: Risk Stratification
├─ Prognostic models (31 papers)
└─ Predictive biomarkers (12 papers)
```

#### Step 15: Quality Assessment and Bias Detection

**Quality assessment methodology:**

For each research domain, use established quality assessment tools:
- **Quantitative studies**: GRADE, Cochrane Risk of Bias, ROBINS-I
- **Qualitative studies**: CASP Qualitative Checklist, STROBE-Q
- **Methodological studies**: STROBE, reporting checklists
- **Model/Algorithm papers**: Methodological rigor assessment

**Bias detection:**

1. **Publication bias**
   - Papers showing positive results more likely to be published
   - Searches for unpublished/negative studies
   - Statistical tests: funnel plots, Egger's test
   - Gray literature search

2. **Selection bias**
   - Populations studied may not be representative
   - Note demographic patterns in papers
   - Identify missing populations/applications
   - Track over/underrepresented areas

3. **Methodological bias**
   - Study design limitations
   - Sample size and power considerations
   - Measurement validity
   - Control for confounders

4. **Reporting bias**
   - Selective outcome reporting
   - Favorable vs. unfavorable results emphasis
   - Statistical significance bias (p-hacking)
   - Effect size reporting consistency

**Quality summary:**
```
Quality Assessment Results (80 papers):
High quality (GRADE: A): 12 papers (15%)
Good quality (GRADE: B): 28 papers (35%)
Fair quality (GRADE: C): 32 papers (40%)
Poor quality (GRADE: D): 8 papers (10%)

Bias Assessment:
- Publication bias: Moderate (positive results overrepresented)
- Selection bias: Low (diverse populations generally well-represented)
- Methodological bias: Moderate (sample size, blinding concerns)
- Reporting bias: Moderate (selective outcome reporting in 40% of papers)

Key limitation: Predominantly English-language journals (may miss non-English research)
```

#### Step 16: Evidence Synthesis

Create integrated summary of evidence:

**Types of synthesis:**

1. **Narrative synthesis**
   - Written summary of findings organized thematically
   - Discussion of agreement/disagreement between studies
   - Integration of quantitative and qualitative findings
   - Assessment of strength of evidence

2. **Meta-analysis (if appropriate)**
   - Statistical combination of comparable results
   - Analysis by subgroup (methodology, population, etc.)
   - Assessment of heterogeneity
   - Sensitivity analysis

3. **Framework synthesis**
   - Organize findings using conceptual framework
   - Map concepts and relationships
   - Show how different findings interconnect
   - Identify patterns and principles

4. **Critical interpretive synthesis**
   - Deep interpretation of findings
   - Identify underlying assumptions and interpretations
   - Reconcile contradictory findings
   - Build new understanding through integration

**Synthesis questions to address:**
- What do we know (consensus findings)?
- What do we NOT know (gaps)?
- What conflicts exist (controversial or contradictory findings)?
- What are implications for practice/future research?
- What quality/strength of evidence supports conclusions?
- What remains uncertain or debated?

**Evidence summary table example:**
```
| Topic | Consensus Finding | Evidence Strength | Conflicting Evidence | Notes |
|-------|------------------|-------------------|---------------------|-------|
| Effectiveness | 70-85% success rate | Strong (24 RCTs) | Effectiveness varies by subtype (40-90%) | Context-dependent |
| Mechanism | Works via pathway X | Moderate (12 studies) | Some evidence for pathway Y (3 studies) | Need more mechanistic work |
| Best practice | Method A superior | Moderate (8 trials) | Method B equivalent in 2 trials | Population and context matter |
| Safety | Well-tolerated overall | Strong (1,200+ patients) | 5-10% adverse events in vulnerable populations | More data needed on elderly |
```

#### Step 17: Identify Gaps and Future Directions

**Research gaps identified through review:**

1. **Knowledge gaps**
   - Questions not yet addressed by research
   - Populations/contexts not yet studied
   - Outcomes not yet measured
   - Mechanisms not yet understood

2. **Methodological gaps**
   - Inadequate study designs for certain questions
   - Lack of comparative studies
   - Gaps in measurement approaches
   - Need for larger/longer studies

3. **Application gaps**
   - Research not translated to practice
   - Implementation challenges not addressed
   - Real-world effectiveness not studied
   - Access/equity issues underexplored

4. **Conflict/uncertainty areas**
   - Contradictory findings needing resolution
   - Debated interpretations
   - Emerging evidence not yet synthesized

**Gap identification process:**
- List what questions remain unanswered
- Note populations not well-represented in literature
- Identify methodological approaches not yet compared
- Document inconsistent findings
- Highlight emerging/underexplored topics

**Future research recommendations:**
```
Priority gaps identified:

1. HIGH PRIORITY - Unaddressed populations
   Gap: Limited research on [specific population]
   Current evidence: [brief summary]
   Recommended study: Prospective cohort study in [population]
   Rationale: [explanation]

2. HIGH PRIORITY - Methodological comparison
   Gap: No direct comparison of Method A vs. Method B
   Current evidence: [separate evidence for each]
   Recommended study: Randomized comparison trial
   Rationale: [explanation]

3. MEDIUM PRIORITY - Mechanism clarification
   Gap: Exact mechanism of action unclear
   Current evidence: [partial evidence]
   Recommended study: Mechanistic studies using [approach]
   Rationale: [explanation]

4. EMERGING AREA - Novel applications
   Gap: New applications identified but not yet studied
   Current evidence: [anecdotal/preliminary evidence]
   Recommended study: Feasibility study
   Rationale: [explanation]
```

### Phase 6: Report Writing and Organization

#### Step 18: Report Structure and Organization

**For Narrative Literature Review:**

1. **Executive Summary** (1 page)
   - Research scope and objectives
   - Key findings and consensus
   - Major gaps and recommendations

2. **Introduction** (2-3 pages)
   - Problem statement and significance
   - Research questions/objectives
   - Scope and relevance

3. **Methods** (1-2 pages)
   - Search strategy and databases
   - Inclusion/exclusion criteria
   - Data extraction and analysis approach
   - Study quality assessment method

4. **Results** (variable, typically 5-10 pages)
   - Literature search and selection process (with flow diagram)
   - Characteristics of included studies
   - Study quality and bias assessment
   - Findings organized thematically

5. **Thematic Sections** (variable, typically 8-20 pages)
   - Current state of knowledge on each theme
   - Key methodologies and approaches
   - Major findings and areas of consensus
   - Conflicting results and areas of debate
   - Recent developments and emerging trends

6. **Synthesis and Discussion** (3-5 pages)
   - Integration of findings across themes
   - Identification of patterns, trends, and paradigm shifts
   - Assessment of research quality and reliability
   - Critical analysis of methodological approaches
   - Implications for theory, practice, and future research

7. **Gaps and Future Directions** (1-2 pages)
   - Identified research gaps
   - Methodological limitations
   - Suggested research priorities
   - Barriers to translation/implementation (if applicable)

8. **Conclusions** (1 page)
   - Summary of key insights
   - Implications for research and practice
   - Recommendations
   - Final synthesis statement

9. **References** (formatted bibliography)
   - Complete citation information
   - Organized by theme (optional)
   - Hyperlinks to DOIs (if digital format)

**For Systematic Literature Review:**

Follow PRISMA 2020 guidelines with additional elements:
- Inclusion/exclusion criteria fully documented
- Detailed search strategy for every database
- PRISMA flow diagram
- Meta-analysis (if appropriate)
- Risk of bias assessment for each study
- Certainty of evidence assessment (GRADE)
- Extended appendices with tables of study characteristics

#### Step 19: Citation Management

**Citation format selection:**

Choose appropriate format for your discipline:
- **APA**: Social sciences, psychology, education
- **Chicago/Notes-Bibliography**: History, humanities
- **IEEE**: Engineering, computer science
- **Nature**: Natural sciences, biology
- **Science**: Scientific research
- **MLA**: Literature, humanities
- **OSCOLA**: Law

**In-text citation approaches:**
- Numbered system: (1), (2), (3)...
- Author-date system: (Smith, 2023)
- Footnote system: Superscript numbers with notes

**Reference list organization:**
- Alphabetical (typical)
- By thematic section
- By methodological approach
- By publication date

**Citation accuracy checklist:**
- All cited papers listed in references
- Reference information complete and accurate
- Formatting consistent throughout
- URLs and DOIs functional
- Access dates included (for websites, if required)

#### Step 20: Report Quality Assurance

**Logical flow and coherence:**
- Each section connects to research question
- Transitions between sections smooth
- Overall narrative logical and clear
- Conclusions follow from evidence

**Balanced perspective:**
- All major viewpoints represented
- Contradictory findings acknowledged
- Limitations transparently discussed
- No over-emphasis of favored interpretations

**Appropriate detail level:**
- Key studies discussed in detail
- Minor studies appropriately summarized
- Methods described at level appropriate for audience
- Results clearly explained without unnecessary statistics

**Clear distinctions:**
- Established facts vs. interpretations clearly marked
- Author's analysis vs. findings from reviewed literature clear
- Consensus vs. minority views distinguished
- Evidence strength indicated

### Phase 7: Output and Dissemination

#### Step 21: Multiple Output Formats

**Markdown format** (for collaborative editing, version control)
```markdown
# Literature Review: [Title]

## Executive Summary
...

## Introduction
...

## Methods
...

## Results
...
```

**LaTeX format** (for academic submission, journal publication)
```latex
\documentclass{article}
\usepackage{natbib}

\title{Literature Review: ...}
\author{...}

\begin{document}

\section{Executive Summary}
...

\end{document}
```

**Word document** (for institutional requirements, collaborative editing)
- Export from markdown/LaTeX
- Format with institutional templates
- Track changes for feedback

**HTML for web publication**
- Interactive tables of contents
- Hyperlinked references
- Searchable content
- Figure galleries

#### Step 22: Citation Data Management

**Export formats:**

- **BibTeX** (.bib): For LaTeX documents
- **RIS** (.ris): For reference managers
- **CSL JSON**: For citation processing
- **CSV**: For data analysis and spreadsheets

**Citation database integration:**
- Zotero: Open-source, browser integration
- Mendeley: Commercial, cloud-based
- EndNote: Enterprise solution
- RefWorks: Cloud-based institutional solution

**Search history documentation:**
- All databases searched
- Queries used
- Date ranges
- Number of results
- Refinements made
- Rationale for changes

## Best Practices for Literature Reviews

### Search Strategy Best Practices

1. **Start broad, then refine**
   - Initial searches cast wide net
   - Analyze results to identify concepts
   - Refine searches based on learning
   - Converge toward saturation

2. **Document everything**
   - Record every search executed
   - Note parameters and dates
   - Keep search logs
   - Enable reproducibility and auditing

3. **Use multiple strategies**
   - Boolean combinations
   - Citation mining
   - Author searching
   - Keyword and phrase variations

4. **Cross-database verification**
   - Important papers should appear in multiple databases
   - Compare top papers across databases
   - Use cross-database differences to identify missed areas

5. **Combine automated and manual searching**
   - Automated searches for breadth
   - Manual browsing of key journals
   - Citation tracking for depth
   - Expert consultation for validation

### Content Analysis Best Practices

1. **Structured extraction**
   - Use standardized forms
   - Consistency checks
   - Double-checking of key papers
   - Inter-rater reliability assessment (if team effort)

2. **Quality assessment**
   - Use published, validated tools
   - Assess all papers using same criteria
   - Document quality concerns
   - Weight evidence by quality

3. **Bias awareness**
   - Acknowledge reviewer biases
   - Explicit inclusion/exclusion criteria
   - Sensitivity analyses
   - Transparent decision-making

4. **Contextual understanding**
   - Understand publication context
   - Note journal prestige and impact
   - Recognize field-specific practices
   - Account for disciplinary differences

5. **Accuracy and verification**
   - Double-check data extraction
   - Verify direct quotes
   - Confirm effect sizes and statistical values
   - Cross-reference key claims

### Synthesis Best Practices

1. **Systematic organization**
   - Use consistent frameworks
   - Organize thematically for narrative clarity
   - Show relationships between studies
   - Map evidence gaps visually

2. **Avoid cherry-picking**
   - Include all relevant papers, not just supporting ones
   - Acknowledge contradictions
   - Give weight to quality of evidence
   - Report effect size ranges

3. **Integrate multiple types of evidence**
   - Combine quantitative and qualitative findings
   - Synthesize across methodological approaches
   - Build comprehensive understanding
   - Identify convergent and divergent findings

4. **Make evidence strength explicit**
   - Use GRADE or similar system
   - Distinguish high-quality from preliminary evidence
   - Acknowledge uncertainty
   - Indicate confidence in conclusions

5. **Address conflicting evidence**
   - Describe conflicting findings fairly
   - Investigate sources of disagreement
   - Propose explanations for conflicts
   - Note when evidence is inconclusive

## Common Mistakes to Avoid

1. **Inadequate search strategy**
   - Too narrow, missing relevant papers
   - Too broad, overwhelming results
   - Missing important databases or grey literature
   - Insufficient iterative refinement

2. **Insufficient documentation**
   - Unclear how papers were selected
   - Search strategy not reproducible
   - Selection decisions not justified
   - Preventing others from assessing quality

3. **Quality assessment omission**
   - Treating all papers as equally valid
   - Over-reliance on poor-quality studies
   - Missing bias assessment
   - Unweighted evidence synthesis

4. **Shallow analysis**
   - Mere summarization instead of synthesis
   - Isolated findings not integrated
   - Contradictions not addressed
   - Limited critical evaluation

5. **Inadequate citation**
   - Incomplete bibliographic information
   - Inconsistent formatting
   - Incorrect attributions
   - Missing DOIs or URLs (for web sources)

6. **Bias toward recent literature**
   - Seminal foundational papers missed
   - Publication bias not addressed
   - Overweight to recent trends
   - Missing historical context

7. **Ignoring methodological variation**
   - Papers using different methodologies treated as directly comparable
   - Methodology-specific findings not noted
   - Invalid meta-analyses (combining incompatible studies)
   - Missed insights from methodological diversity

## Tools and Resources

### Search and Management Tools

**Reference Management:**
- Zotero (zotero.org) - Free, open-source
- Mendeley (mendeley.com) - Free basic version
- RefWorks - Institutional access
- Papers (papersapp.com) - PDF-focused

**Search Tools:**
- PubMed Central: pubmed.ncbi.nlm.nih.gov
- arXiv: arxiv.org
- Web of Science: webofscience.com
- Scopus: scopus.com
- Google Scholar: scholar.google.com

**Citation Tools:**
- CrossRef (crossref.org) - DOI lookup and verification
- Unpaywall (unpaywall.org) - Open access article locator

### Data Extraction and Organization

**Spreadsheets and Databases:**
- Excel: Simple, widely available
- Google Sheets: Collaborative, cloud-based
- Airtable: Database functionality, templates
- Covidence: Systematic review platform
- DistillerSR: Systematic review software

### Synthesis and Visualization

**Concept Mapping:**
- CmapTools: Free concept mapping
- MindMeister: Collaborative mind mapping
- VosViewer: Citation network visualization
- Gephi: Network analysis and visualization

**Statistical Analysis:**
- R: Advanced analysis and visualization
- Python: Data analysis and synthesis
- STATA: Statistical analysis
- RevMan: Systematic review meta-analysis

## Integration with Other Skills

This skill integrates well with:

- **scientific-writing**: For writing the literature review sections of papers
- **eln**: For documenting literature review process in electronic lab notebook
- **planning**: For project planning and tracking literature review progress
- **troubleshooting**: For debugging searches and refining strategy when facing challenges
- **phd-qualifier**: For comprehensive literature reviews needed for exams

## Response Patterns

When conducting literature reviews, I will:

1. **Clarify scope and research questions** - Ensure clear, specific research questions using PICO/PEO framework
2. **Propose search strategy** - Recommend appropriate databases and search queries
3. **Guide iterative refinement** - Suggest ways to refine searches based on initial results
4. **Suggest organizational frameworks** - Propose thematic organization structures
5. **Help with synthesis** - Guide integration of findings and identification of gaps
6. **Provide quality assessment** - Apply relevant quality assessment tools
7. **Support report writing** - Help structure and write literature review sections
8. **Document comprehensively** - Ensure all decisions and searches are documented

I will ask clarifying questions about:
- Research domain and field
- Intended scope (comprehensive vs. focused)
- Time constraints and available resources
- Target audience for the review
- Specific research question(s)
- Preferred output format
- Publication requirements (PRISMA compliance, specific journal guidelines, etc.)

## Limitations and Considerations

1. **Time and resources**: Comprehensive literature reviews require significant time investment (weeks to months)
2. **Database access**: Some databases require institutional access or subscriptions
3. **Full-text availability**: Not all papers are freely available online
4. **Language barriers**: This skill focuses on English-language resources
5. **Currency**: Review methodology follows published guidelines; emerging trends in literature review methodology may not be fully captured
6. **Subjective elements**: Some aspects of literature review (theme identification, synthesis) involve interpretive judgment
7. **Tool limitations**: External tools (databases, search engines) have inherent limitations and biases

---

This comprehensive literature review skill provides a systematic, reproducible approach to synthesizing knowledge across research domains while maintaining rigor, transparency, and critical evaluation of evidence.
