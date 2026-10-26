# Skill Template

This template helps you create a new Claude Code skill that follows the official specifications.

## Quick Reference

**File Location:**
- Personal: `~/.claude/skills/skill-name/SKILL.md`
- Project: `.claude/skills/skill-name/SKILL.md`
- Plugin: `skills/skill-name/SKILL.md`

**Naming Rules:**
- Lowercase letters, numbers, and hyphens only
- Maximum 64 characters
- Example: `python-ase`, `phd-qualifier`, `pdf-processor`

**Description Guidelines:**
- Maximum 1024 characters
- Must explain BOTH "what it does" AND "when to use it"
- Be specific and assertive about trigger conditions (see Pushy Descriptions below)
- Good: "Extract text and tables from PDF files. Use when the user provides a PDF path, asks to read or analyze PDF content, or needs to convert PDF tables to structured data."
- Bad: "Helps with documents"

---

## Pushy Descriptions: The #1 Skill Quality Factor

**The problem:** Claude tends to *undertrigger* skills — it sees the description but decides not to invoke the skill. Vague or passive descriptions make this worse. The fix is to write descriptions that are assertive about when to trigger.

**Why this matters:** The description is the primary signal Claude uses to decide whether to load and apply a skill. A weak description means the skill sits unused even when it would help.

**Weak (passive) vs. Strong (pushy) examples:**

| Weak | Strong |
|------|--------|
| "Helps with Python code" | "Use immediately when the user asks about Python code quality, style, linting, or best practices." |
| "For PDF files" | "Trigger when the user provides a `.pdf` file path, asks to read/analyze/extract PDF content, or mentions a PDF document." |
| "Scientific computing assistance" | "Use this skill when the user is working with ASE atoms objects, running DFT calculations, or asking about atomistic simulations." |

**Structural template for a pushy description:**
```
[What the skill does in 1 sentence.]

Use this skill when: [concrete trigger conditions — list specific verbs,
file types, tool names, user phrasings that should activate it].

[Optional: "Do NOT use when..." for disambiguation from similar skills.]
[Optional: dependencies — "Requires: package-name"]
```

**When to trigger block (include in your description):**
```
Use this skill when the user:
- mentions [specific tool/file/concept names]
- asks to [specific action verbs]
- provides [specific inputs like file paths, data formats]
- says things like "[example phrase 1]" or "[example phrase 2]"
```

---

## Progressive Disclosure Architecture

**Keep SKILL.md under 500 lines.** Claude loads the full SKILL.md body when it invokes the skill, so large files slow down every invocation and waste context.

**Three-level loading model:**
1. **Metadata (always in context):** The `description` field — always visible, used for triggering decisions
2. **SKILL.md body (on trigger):** Loaded when Claude invokes the skill — keep this focused and action-oriented
3. **References (on demand):** Large docs, API references, code examples — Claude reads these only when needed

**Where to put content:**
```
skill-name/
├── SKILL.md          # <500 lines: purpose, instructions, key examples
├── references/
│   ├── api-ref.md    # Full API documentation
│   ├── patterns.md   # Detailed pattern library
│   └── examples.md   # Extended examples
└── scripts/
    ├── helper.py     # Utility scripts Claude can run
    └── template.py   # Code generators
```

**In your SKILL.md, reference these files explicitly:**
```markdown
## Extended Reference
For detailed API documentation, see @references/api-ref.md.
For code patterns, see @references/patterns.md.
```

---

## Explain the Why

Instructions in SKILL.md work better when they explain *why* a guideline exists, not just *what* to do. LLMs respond better to reasoning than bare imperatives.

**Imperative (less effective):**
```
NEVER skip validation. ALWAYS check file exists first.
```

**Reasoning-based (more effective):**
```
Check that the file exists before processing it — this prevents confusing
error messages that obscure the real problem (missing input vs. bad code).
```

Bare "MUST/NEVER/ALWAYS" language is useful for hard safety constraints, but for
workflow guidance, reasoning produces more adaptive behavior.

---

## SKILL.md Template

Copy the content below to create your skill:

```markdown
---
name: skill-name
description: |
  [What this skill does in 1-2 sentences]

  Use this skill when [specific trigger conditions or scenarios].

  [Optional: Key capabilities or features]

  [Optional: Dependencies - e.g., "Requires: pandas, numpy"]
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---

# [Skill Name]

## Purpose

[Detailed explanation of what this skill does and why it's useful]

## When to Use

This skill should be invoked when:
- [Specific trigger condition 1]
- [Specific trigger condition 2]
- [Specific trigger condition 3]

## Capabilities

[List the key capabilities or operations this skill provides]

1. **[Capability 1]**: [Description]
2. **[Capability 2]**: [Description]
3. **[Capability 3]**: [Description]

## Instructions

[Detailed step-by-step instructions for Claude to follow when using this skill]

### Step 1: [Task]
[Specific instructions, including which tools to use]

### Step 2: [Task]
[Specific instructions]

### Step 3: [Task]
[Specific instructions]

## Requirements

[List any dependencies, prerequisites, or environment requirements]
- [Requirement 1]
- [Requirement 2]

## Best Practices

[Guidelines for optimal use of this skill]
- [Best practice 1]
- [Best practice 2]

## Examples

[Optional: Show example scenarios or expected outputs]

### Example 1: [Scenario]
**User request:** [Example user request]
**Expected behavior:** [What the skill should do]

### Example 2: [Scenario]
**User request:** [Example user request]
**Expected behavior:** [What the skill should do]

## Limitations

[Optional: Note any known limitations or constraints]
- [Limitation 1]
- [Limitation 2]

## Related Skills

[Optional: Link to related or complementary skills]
- [Related skill 1]
- [Related skill 2]
```

---

## Optional Supporting Files

### reference.md
Create `reference.md` in the same directory for extensive reference documentation:
- API documentation
- Configuration options
- Detailed technical specifications
- Long code examples

### examples.md
Create `examples.md` for multiple examples:
- Common use cases
- Input/output samples
- Edge cases
- Integration examples

### scripts/
Create `scripts/` directory for helper scripts:
- Python utilities
- Shell scripts
- Data processing tools
- Template generators

### templates/
Create `templates/` directory for file templates:
- Configuration file templates
- Code scaffolding
- Document templates

---

## Allowed Tools Reference

Common tool combinations by use case:

**Read-only analysis:**
```yaml
allowed-tools: Read, Grep, Glob
```

**File editing:**
```yaml
allowed-tools: Read, Edit, Write, Glob
```

**Development workflow:**
```yaml
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
```

**Restricted execution:**
```yaml
allowed-tools: Read, Bash
```

**All tools (default if omitted):**
```yaml
# No allowed-tools field = all tools available
```

### Available Tools
- `Read` - Read file contents
- `Write` - Create new files
- `Edit` - Modify existing files
- `Bash` - Execute shell commands
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `Task` - Launch sub-agents
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web
- `AskUserQuestion` - Prompt user for input
- `TodoWrite` - Manage task lists
- `NotebookEdit` - Edit Jupyter notebooks
- `Skill` - Invoke other skills
- `SlashCommand` - Execute slash commands

---

## Validation Checklist

Before deploying your skill, verify:

- [ ] `name` field uses only lowercase, numbers, and hyphens
- [ ] `name` is 64 characters or less
- [ ] `description` clearly explains "what" and "when"
- [ ] `description` is 1024 characters or less
- [ ] `description` is assertive — uses "Use this skill when..." with specific trigger conditions
- [ ] `description` includes concrete trigger phrases (not just capabilities)
- [ ] SKILL.md body is under 500 lines; overflow content is in `references/`
- [ ] YAML frontmatter is valid (three dashes at start and end)
- [ ] File is saved as `SKILL.md` in the skill directory
- [ ] Instructions explain *why*, not just *what* (reasoning over imperatives)
- [ ] Dependencies are listed in description
- [ ] Tool restrictions are appropriate for the task
- [ ] Examples demonstrate expected behavior
- [ ] Run `skillpack optimize <skill-name>` to check and improve triggering

---

## Testing Your Skill

1. **Install the skill:**
   ```bash
   # For personal use
   mkdir -p ~/.claude/skills/your-skill-name
   cp SKILL.md ~/.claude/skills/your-skill-name/

   # For project use
   mkdir -p .claude/skills/your-skill-name
   cp SKILL.md .claude/skills/your-skill-name/
   ```

2. **Test discovery:**
   - Start Claude Code
   - Ask a question that should trigger your skill
   - Claude should automatically use the skill (no explicit invocation needed)

3. **Debug if needed:**
   ```bash
   claude --debug
   ```
   Look for skill loading errors in the output

4. **Iterate:**
   - Refine the description if Claude doesn't invoke it when expected
   - Add more specific trigger conditions
   - Adjust tool restrictions if operations fail

---

## Example: Complete Skill

Here's a real example of a properly formatted skill:

```markdown
---
name: pdf-text-extractor
description: |
  Extract text and tables from PDF files. Use when the user asks to read,
  analyze, or extract content from PDF documents. Can handle text extraction,
  table parsing, and basic structure analysis.

  Requires: pdfplumber, PyPDF2
allowed-tools: Read, Bash, Write
---

# PDF Text Extractor

## Purpose

This skill extracts text and tables from PDF files for analysis, processing,
or conversion to other formats.

## When to Use

This skill should be invoked when:
- User provides a PDF file path and asks to read or extract its content
- User wants to analyze text within a PDF
- User needs to convert PDF tables to structured data

## Capabilities

1. **Text Extraction**: Extract all text content from PDF pages
2. **Table Parsing**: Identify and extract tables as structured data
3. **Metadata Reading**: Access PDF metadata (title, author, page count)

## Instructions

### Step 1: Verify PDF exists
Use the Bash tool to check if the PDF file exists and is readable.

### Step 2: Extract content
Use Python with pdfplumber to extract text and tables:
```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
```

### Step 3: Format output
Present the extracted content in a clear, structured format.

## Requirements

- Python package: pdfplumber
- Python package: PyPDF2
- Valid PDF file path

## Best Practices

- Always verify file exists before attempting extraction
- Handle multi-page PDFs page by page
- Report extraction errors clearly to the user
- For large PDFs, show progress indicators

## Limitations

- Cannot extract text from image-based PDFs (requires OCR)
- Complex table structures may need manual review
- Password-protected PDFs require password input
```

---

## Tips for Great Skills

1. **Be Specific**: Vague descriptions lead to skills that are never invoked
2. **One Focus**: Each skill should do one thing well
3. **Clear Triggers**: List explicit conditions that should trigger the skill
4. **Test Thoroughly**: Try multiple phrasings that should invoke your skill
5. **Document Dependencies**: Always list required packages or tools
6. **Restrict Tools**: Use `allowed-tools` for security-sensitive operations
7. **Provide Examples**: Show what good usage looks like
8. **Iterate**: Refine based on how often it's actually invoked

---

## Common Mistakes to Avoid

1. **Too broad**: "Helps with programming" → Should be "Python async/await patterns"
2. **No trigger conditions**: Description doesn't explain when to use it
3. **Missing dependencies**: Skill uses packages but doesn't list them
4. **Wrong tool access**: Needs Bash but `allowed-tools` doesn't include it
5. **Invalid name**: Uses uppercase, spaces, or special characters
6. **Too long**: Description exceeds 1024 characters
7. **Unclear instructions**: Steps are vague or ambiguous

---

## Need Help?

- [Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills.md)
- [Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)
- Run `claude --debug` to see skill loading issues
