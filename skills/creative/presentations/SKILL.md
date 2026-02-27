---
name: presentations
description: |
  Create slide presentations in multiple formats: Marp (Markdown, default), Beamer (LaTeX),
  Jupyter Notebook slides, and PowerPoint (python-pptx). Supports scientific, business, and
  developer content with math, code, charts, and tables. Converts existing documents into slides
  or creates from scratch. Auto-compiles to PDF/HTML/PPTX.

  Use this skill when the user requests:
  - Creating a presentation or slide deck
  - Converting a document, paper, or report into slides
  - Making conference talk, lecture, or meeting slides
  - Generating PowerPoint, PDF slides, or HTML slideshows
  - Beamer, Marp, reveal.js, or notebook slideshow creation
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "AskUserQuestion", "WebFetch"]
---

## Purpose

Generate professional slide presentations from scratch or by converting existing documents. Supports four output formats covering academic, business, and developer use cases. Enforces slide layout best practices to prevent text overflow, cluttered slides, and poor readability.

## When to Use

- User asks to create a presentation, slide deck, or talk
- User wants to convert a paper, report, outline, or notes into slides
- User requests a specific format: Beamer, Marp, Jupyter slides, or PowerPoint
- User asks for conference talk, lecture, or meeting slides

## CRITICAL: Slide Layout Rules

**These rules apply to ALL formats. Follow them by default. The user may override for specific slides (e.g., reference/appendix slides), but warn about readability.**

### Text Density Limits

- **Max 6 bullet points per slide** — if more content is needed, split across multiple slides
- **Max ~40 words per slide body** (excluding title) — slides are visual aids, not documents
- **One core idea per slide** — each slide should have a single takeaway message
- **Bullet text max ~10 words each** — use sentence fragments, not full sentences

### Font Size Minimums

| Element | Beamer | Marp | PPTX | Jupyter |
|---------|--------|------|------|---------|
| Title | `\Large` (24pt+) | 32px+ | Pt(28)+ | H1/H2 |
| Body text | `\normalsize` (11pt+) | 20px+ | Pt(18)+ | normal |
| Code | `\small` (10pt) | 16px+ | Pt(14)+ | cell default |
| Footnotes | `\footnotesize` (8pt) | 14px | Pt(12) | small |

### Content-Specific Limits

- **Code blocks**: Max ~12 lines per slide. For longer code, split across slides or move to appendix
- **Tables**: Max ~5 data rows visible per slide. Paginate or simplify larger tables
- **Images**: Always specify explicit size constraints. Never let images overflow slide boundaries
- **Equations**: Max 2-3 display equations per slide. Use align environments for multi-line math

### Whitespace and Margins

- Maintain at least 10% padding on all sides — do not fill every pixel
- Leave breathing room between elements (bullets, images, code blocks)
- Prefer visual balance over cramming content

### Override Policy

If the user explicitly requests dense content (e.g., "make a reference slide with all parameters"), honor the request but:
1. Reduce font sizes to the minimums above (never below)
2. Add a note that the slide is intentionally dense
3. Suggest splitting if it still overflows

## Format Selection

**Default: Marp** (Markdown-based, exports to HTML/PDF/PPTX)

Use AskUserQuestion only if the user hasn't specified a format and the content strongly suggests a different one.

```
Format Decision:
├── Heavy LaTeX math / academic conference → Beamer
├── Live code demos / data science → Jupyter Notebook slides
├── Enterprise / editable by non-technical users → PowerPoint (python-pptx)
└── Everything else (default) → Marp
```

## Instructions

### Step 1: Gather Requirements

Before generating slides, determine:
1. **Topic and audience** — what is the presentation about and who is it for?
2. **Format** — use Marp unless user specifies otherwise or content suggests a better fit
3. **Slide count** — ask if not specified; default to ~10-15 slides for a talk
4. **Content source** — from scratch, or converting an existing document?
5. **Special needs** — math, code, charts, animations, speaker notes?

If converting a document, read it first with the Read tool, then extract key points and organize into an outline before generating slides.

### Step 2: Create Slide Outline

Before writing any slides, create a brief outline:
```
1. Title slide
2. Outline/Agenda
3-N. Content slides (one idea each)
N+1. Summary/Conclusions
N+2. Questions / Thank you
```

Present the outline to the user for approval before proceeding.

### Step 3: Generate Slides

Use the appropriate format section below. Always apply the layout rules from the CRITICAL section.

### Step 4: Auto-Compile

After writing the source file, compile to final output:

| Format | Command |
|--------|---------|
| Marp → PDF | `npx @marp-team/marp-cli@latest --pdf --allow-local-files slides.md` |
| Marp → HTML | `npx @marp-team/marp-cli@latest --allow-local-files slides.md` |
| Marp → PPTX | `npx @marp-team/marp-cli@latest --pptx --allow-local-files slides.md` |
| Beamer → PDF | `latexmk -pdf presentation.tex` |
| Beamer + minted | `latexmk -pdf -shell-escape presentation.tex` |
| Jupyter → HTML slides | `jupyter nbconvert --to slides presentation.ipynb --post serve` |
| PowerPoint | No compilation needed — python-pptx writes .pptx directly |

If a compilation tool is not installed, inform the user and provide the install command.

---

## Format: Marp (Default)

### Prerequisites

```bash
# Option 1: Use npx (no install, requires Node.js >= 18)
npx @marp-team/marp-cli@latest --version

# Option 2: Global install
npm install -g @marp-team/marp-cli

# Option 3: Homebrew
brew install marp-cli
```

### Template

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-size: 20px;
  }
  h1 {
    font-size: 36px;
  }
  h2 {
    font-size: 30px;
  }
  code {
    font-size: 16px;
  }
  table {
    font-size: 18px;
  }
---

<!-- _paginate: false -->

# Presentation Title

**Author Name**
Date | Event

---

## Outline

1. First topic
2. Second topic
3. Third topic

---

## Slide Title

- Key point one
- Key point two
- Key point three

<!-- Use fragment-style reveals sparingly -->

---
```

### Key Features

**Auto-fit headers** (prevents title overflow):
```markdown
<!-- fit -->
# This Long Title Will Auto-Scale to Fit
```

**Background images**:
```markdown
![bg right:40%](image.png)

# Split Layout

Content on the left, image on the right.
```

**Image sizing** (always constrain):
```markdown
![width:500px](figure.png)
![height:300px](chart.png)
![bg contain](full-slide-image.png)
```

**Math** (KaTeX):
```markdown
Inline: $E = mc^2$

$$
\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}
$$
```

**Code blocks** (syntax highlighted automatically):
````markdown
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```
````

**Two-column layout**:
```markdown
<div style="display: flex; gap: 40px;">
<div style="flex: 1;">

### Left Column
- Point A
- Point B

</div>
<div style="flex: 1;">

### Right Column
- Point C
- Point D

</div>
</div>
```

**Speaker notes** (only when requested):
```markdown
<!--
Speaker notes go here.
These are not visible in the presentation.
-->
```

### Overflow Prevention

- Use `<!-- fit -->` before headings that might be too long
- Set global `font-size` in the style block to control base size
- Use `![width:Npx]` or `![height:Npx]` for all images — never use unsized images
- For dense tables, reduce font size locally: `<div style="font-size: 14px;">...</div>`
- Split content across slides rather than shrinking fonts below minimums

### Compilation

```bash
# PDF output (most common)
npx @marp-team/marp-cli@latest --pdf --allow-local-files slides.md

# HTML output (interactive, good for sharing)
npx @marp-team/marp-cli@latest --allow-local-files slides.md -o slides.html

# PPTX output (note: slides are rasterized images, not editable)
npx @marp-team/marp-cli@latest --pptx --allow-local-files slides.md
```

---

## Format: Beamer (LaTeX)

### Prerequisites

```bash
# macOS
brew install --cask mactex

# Ubuntu/Debian
sudo apt install texlive-latex-extra latexmk

# For code highlighting with minted
pip install Pygments
```

### Template

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{Madrid}
\usecolortheme{default}

% Prevent text overflow
\setbeamertemplate{frametitle}{\vspace{0.2cm}\insertframetitle}

% Code listings
\usepackage{listings}
\usepackage{xcolor}
\lstset{
  basicstyle=\ttfamily\small,
  keywordstyle=\color{blue},
  commentstyle=\color{green!60!black},
  stringstyle=\color{red},
  frame=single,
  breaklines=true,
  breakatwhitespace=true,
  postbreak=\mbox{\textcolor{red}{$\hookrightarrow$}\space},
  numbers=left,
  numberstyle=\tiny\color{gray}
}

% Graphics
\usepackage{graphicx}

% Math
\usepackage{amsmath,amssymb}

\title[Short Title]{Full Presentation Title}
\author{Author Name}
\institute{Institution}
\date{\today}

\begin{document}

\begin{frame}
  \titlepage
\end{frame}

\begin{frame}{Outline}
  \tableofcontents
\end{frame}

\section{Introduction}

\begin{frame}{Slide Title}
  \begin{itemize}
    \item First key point
    \item Second key point
    \item Third key point
  \end{itemize}
\end{frame}

\end{document}
```

### Key Features

**Overlay animations**:
```latex
\begin{frame}{Incremental Reveal}
  \begin{itemize}
    \item<1-> Always visible
    \item<2-> Appears second
    \item<3-> Appears third
  \end{itemize}
\end{frame}
```

**Two-column layout**:
```latex
\begin{frame}{Side by Side}
  \begin{columns}
    \column{0.48\textwidth}
      Left content here.
    \column{0.48\textwidth}
      \includegraphics[width=\textwidth]{figure.png}
  \end{columns}
\end{frame}
```

**Code blocks** (use `[fragile]` on the frame):
```latex
\begin{frame}[fragile]{Code Example}
\begin{lstlisting}[language=Python]
def greet(name):
    return f"Hello, {name}!"
\end{lstlisting}
\end{frame}
```

**Math**:
```latex
\begin{frame}{Equations}
  The Schrödinger equation:
  \begin{equation}
    i\hbar\frac{\partial}{\partial t}\Psi = \hat{H}\Psi
  \end{equation}
\end{frame}
```

**Figures with size control**:
```latex
\begin{frame}{Results}
  \begin{figure}
    \centering
    \includegraphics[width=0.7\textwidth,height=0.5\textheight,keepaspectratio]{plot.png}
    \caption{Always constrain both width and height.}
  \end{figure}
\end{frame}
```

**Blocks**:
```latex
\begin{block}{Definition}
  A concise definition here.
\end{block}

\begin{alertblock}{Warning}
  Important caveat.
\end{alertblock}

\begin{exampleblock}{Example}
  Illustrative example.
\end{exampleblock}
```

**Speaker notes** (only when requested):
```latex
\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}

\begin{frame}{Title}
  Content here.
  \note{Talking points for this slide.}
\end{frame}
```

### Popular Themes

| Theme | Style | Best for |
|-------|-------|----------|
| Madrid | Classic with navigation | General academic |
| Metropolis | Clean, modern, minimal | Modern talks |
| Berlin | Header navigation bar | Long talks |
| CambridgeUS | Red/blue accent | Formal conferences |
| default | Minimal, no decoration | When you want plain |

### Overflow Prevention

- Use `[shrink]` frame option as a last resort: `\begin{frame}[shrink]{Title}`
- Constrain images: `\includegraphics[width=0.7\textwidth,height=0.5\textheight,keepaspectratio]{img}`
- Use `breaklines=true` in lstset for code that might wrap
- For dense slides, use `\small` or `\footnotesize` but never below `\scriptsize`
- Use `\resizebox{\textwidth}{!}{...}` to scale a table to fit width

### Compilation

```bash
# Standard
latexmk -pdf presentation.tex

# With minted code highlighting
latexmk -pdf -shell-escape presentation.tex

# Clean auxiliary files
latexmk -c
```

---

## Format: Jupyter Notebook Slides

### Prerequisites

```bash
pip install notebook nbconvert

# For live presentation mode (classic notebook only)
pip install RISE                # notebook <= 6
pip install jupyterlab-rise     # JupyterLab / notebook 7+
```

### Creating Slides Programmatically

Use this approach to generate a notebook with slide metadata from Python:

```python
import nbformat

nb = nbformat.v4.new_notebook()

# Title slide
title_cell = nbformat.v4.new_markdown_cell("# Presentation Title\n\n**Author** | Date")
title_cell.metadata["slideshow"] = {"slide_type": "slide"}
nb.cells.append(title_cell)

# Content slide with markdown
content_cell = nbformat.v4.new_markdown_cell(
    "## Key Findings\n\n"
    "- Finding one\n"
    "- Finding two\n"
    "- Finding three"
)
content_cell.metadata["slideshow"] = {"slide_type": "slide"}
nb.cells.append(content_cell)

# Code slide
code_cell = nbformat.v4.new_code_cell(
    "import matplotlib.pyplot as plt\n"
    "import numpy as np\n\n"
    "x = np.linspace(0, 10, 100)\n"
    "plt.plot(x, np.sin(x))\n"
    "plt.title('Sine Wave')\n"
    "plt.show()"
)
code_cell.metadata["slideshow"] = {"slide_type": "slide"}
nb.cells.append(code_cell)

# Save
nbformat.write(nb, "presentation.ipynb")
```

### Cell Slide Types

| Type | Behavior | Use for |
|------|----------|---------|
| `slide` | New horizontal slide | Main content slides |
| `subslide` | Vertical sub-slide | Detail under a main slide |
| `fragment` | Appears incrementally | Reveals within a slide |
| `skip` | Hidden from presentation | Setup code, scratch work |
| `notes` | Speaker notes | Talking points (only when requested) |
| `-` | Continues previous slide | Output cells below code |

### Key Features

- Live code execution during presentation (RISE only)
- Interactive widgets and plots remain functional
- Mix markdown, code, and output on the same slide
- Native syntax highlighting for code cells

### Overflow Prevention

- Keep code cells to max ~10 lines — move setup code to `skip` cells
- Use `plt.figure(figsize=(8, 4))` to control plot sizes explicitly
- For markdown cells, follow the same bullet/word count limits
- Hide verbose output with `;` at end of cell or `skip` type for output-heavy cells
- Use `--no-input` flag with nbconvert to hide code cells if showing only results

### Compilation

```bash
# Static HTML slides
jupyter nbconvert --to slides presentation.ipynb

# Serve in browser immediately
jupyter nbconvert --to slides presentation.ipynb --post serve

# Hide code cells (output only)
jupyter nbconvert --to slides presentation.ipynb --no-input
```

---

## Format: PowerPoint (python-pptx)

### Prerequisites

```bash
pip install python-pptx
```

### Template

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Load custom template if provided, otherwise use default
# prs = Presentation("template.pptx")  # with template
prs = Presentation()  # default

# --- Inspect available layouts (do this first with custom templates) ---
for i, layout in enumerate(prs.slide_layouts):
    print(f"{i}: {layout.name}")

# --- Title Slide ---
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Presentation Title"
slide.placeholders[1].text = "Author | Date"

# --- Content Slide with Bullets ---
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Key Points"
tf = slide.placeholders[1].text_frame
tf.word_wrap = True

tf.text = "First bullet point"
for text, level in [("Second point", 0), ("Sub-point", 1), ("Third point", 0)]:
    p = tf.add_paragraph()
    p.text = text
    p.level = level
    p.font.size = Pt(18) if level == 0 else Pt(16)

prs.save("presentation.pptx")
```

### Adding Images

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only
slide.shapes.title.text = "Results"

# Always specify position and size to prevent overflow
slide_width = prs.slide_width
slide_height = prs.slide_height

img_width = Inches(6)
img_height = Inches(4)
left = (slide_width - img_width) // 2  # center horizontally
top = Inches(1.5)

slide.shapes.add_picture("figure.png", left, top, img_width, img_height)
```

### Adding Tables

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Data Summary"

rows, cols = 4, 3  # max ~5 data rows per slide
table_shape = slide.shapes.add_table(
    rows, cols,
    left=Inches(1), top=Inches(1.8),
    width=Inches(8), height=Inches(3)
)
table = table_shape.table

# Header row
for col_idx, text in enumerate(["Metric", "Value", "Change"]):
    cell = table.cell(0, col_idx)
    cell.text = text
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.bold = True
        paragraph.font.size = Pt(16)

# Data rows
data = [("Revenue", "$1.2M", "+15%"), ("Users", "50K", "+22%"), ("NPS", "72", "+5")]
for row_idx, row_data in enumerate(data, start=1):
    for col_idx, text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(14)
```

### Adding Charts

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Performance"

chart_data = CategoryChartData()
chart_data.categories = ["Q1", "Q2", "Q3", "Q4"]
chart_data.add_series("Revenue", (120, 150, 130, 175))

chart_frame = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(1), Inches(1.8), Inches(8), Inches(4.5),
    chart_data
)
chart = chart_frame.chart
chart.has_legend = True
chart.has_title = True
chart.chart_title.text_frame.text = "Quarterly Revenue"
```

### Custom Template Support

```python
# Load a branded template
prs = Presentation("company_template.pptx")

# Inspect layouts to find the right ones
for i, layout in enumerate(prs.slide_layouts):
    print(f"{i}: {layout.name}")
    for ph in layout.placeholders:
        print(f"   Placeholder {ph.placeholder_format.idx}: {ph.name}")

# Use template layouts by index (indices depend on the template)
slide = prs.slides.add_slide(prs.slide_layouts[1])
```

### Speaker Notes (only when requested)

```python
from pptx.util import Pt

slide = prs.slides.add_slide(prs.slide_layouts[1])
notes_slide = slide.notes_slide
notes_tf = notes_slide.notes_text_frame
notes_tf.text = "Key talking points for this slide."
```

### Overflow Prevention

- Always use `Inches()` or `Pt()` for positioning — never raw integers
- Center images: `left = (prs.slide_width - img_width) // 2`
- Set `text_frame.word_wrap = True` on all text boxes
- Cap font sizes: title `Pt(28)`, body `Pt(18)`, minimum `Pt(12)`
- For tables with many rows, paginate across slides automatically
- Validate positions: ensure `left + width <= prs.slide_width` and `top + height <= prs.slide_height`

---

## Document Conversion Workflow

When converting an existing document into slides:

### Step 1: Read the Source

Use the Read tool to read the document. Supported inputs:
- Markdown (.md)
- LaTeX (.tex)
- Org-mode (.org)
- Plain text (.txt)
- PDF (extract key sections)

### Step 2: Extract Key Points

Identify:
- Main thesis/argument
- Section headings → slide titles
- Key findings/results → bullet points (max 6 per slide)
- Figures/tables → dedicated slides
- Equations → math slides (max 2-3 per slide)

### Step 3: Create Outline

Map document sections to slides. Apply the density rules — a paper section with 5 paragraphs may need 3-4 slides, not one.

### Step 4: Generate and Compile

Follow the format-specific instructions above.

---

## Figure Generation

For slides that need charts or figures:

**Basic inline generation** (matplotlib):
```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(8, 4))  # explicit size for slides
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), linewidth=2)
ax.set_xlabel("x", fontsize=14)
ax.set_ylabel("sin(x)", fontsize=14)
ax.tick_params(labelsize=12)
fig.savefig("sine_plot.png", dpi=150, bbox_inches="tight")
plt.close()
```

For complex visualizations, use the **python-plotting** skill. For AI-generated images or diagrams, use the **image-generation** skill.

---

## Requirements

### Marp
- Node.js >= 18 (for npx/npm)
- Chrome, Edge, or Firefox (for PDF/PPTX export — used headlessly)

### Beamer
- TeX Live, MiKTeX, or MacTeX (full LaTeX distribution)
- `latexmk` (included with TeX Live)
- Pygments (`pip install Pygments`) for minted code highlighting

### Jupyter Notebook Slides
- `notebook` and `nbconvert` (`pip install notebook nbconvert`)
- Optional: `RISE` or `jupyterlab-rise` for live presentations

### PowerPoint
- `python-pptx` (`pip install python-pptx`)
- No system dependencies

---

## Examples

### Example 1: Conference Talk (Marp)

**User request:** "Make a 10-slide presentation about machine learning in materials science"

**Expected behavior:**
1. Use AskUserQuestion to confirm audience and any specific topics to cover
2. Create outline with 10 slides: title, outline, 6 content, summary, questions
3. Write Marp markdown with `theme: default`, `size: 16:9`, proper font sizes
4. Include math for key equations, code for example workflows
5. Apply layout rules: max 6 bullets, ~40 words per slide
6. Compile to PDF: `npx @marp-team/marp-cli@latest --pdf --allow-local-files slides.md`

### Example 2: Paper Conversion (Beamer)

**User request:** "Convert my paper draft.tex into a 20-minute conference talk"

**Expected behavior:**
1. Read draft.tex with Read tool
2. Extract key contributions, figures, and equations
3. Create outline: ~15 slides for 20 minutes (1-1.5 min per slide)
4. Generate Beamer .tex file reusing figures from the paper directory
5. Apply layout rules: one idea per slide, max 2-3 equations per slide
6. Compile: `latexmk -pdf presentation.tex`

### Example 3: Business Report (PowerPoint)

**User request:** "Create a PowerPoint for my quarterly review with sales data"

**Expected behavior:**
1. Ask about data source and key metrics
2. Generate python-pptx script with title slide, data slides, chart slides, summary
3. Create charts using CategoryChartData for sales figures
4. Use proper font sizes (Pt(28) titles, Pt(18) body)
5. Save directly as .pptx — no compilation needed

### Example 4: Interactive Demo (Jupyter)

**User request:** "Make a notebook slideshow demonstrating pandas data analysis"

**Expected behavior:**
1. Create notebook with nbformat, setting slide_type metadata
2. Include code cells with live-executable pandas examples
3. Add markdown cells for explanations (following density limits)
4. Mark setup/import cells as `skip` type
5. Export: `jupyter nbconvert --to slides presentation.ipynb`

---

## Limitations

- Marp PPTX export produces rasterized slides — text is not editable in PowerPoint
- python-pptx cannot render slides — visual verification requires opening in PowerPoint or LibreOffice
- Beamer compilation requires a full LaTeX distribution (several GB)
- Jupyter RISE only works with classic notebook (<= v6); JupyterLab needs jupyterlab-rise
- Speaker notes are only generated when explicitly requested

## Related Skills

- **python-plotting** — for complex chart and visualization generation
- **image-generation** — for AI-generated images and diagrams
- **scientific-writing** — for academic content structuring and LaTeX guidance
