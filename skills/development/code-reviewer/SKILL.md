---
name: code-reviewer
description: Comprehensive code review and analysis for software quality assurance. Use when Claude needs to review code in any format including (1) Individual files (Python, R, JavaScript, etc.), (2) Directory structures and project organization, (3) Scripts and automation code, (4) Jupyter notebooks and data analysis workflows, (5) Documentation assessment and improvement suggestions, (6) Bug detection and logic verification, (7) Testing coverage and strategy evaluation, (8) Code consistency and maintainability analysis. Provides actionable improvement recommendations across all aspects of software development.
allowed-tools: ["*"]
---

# Code Reviewer

This skill transforms Claude into a systematic code reviewer, evaluating software projects across multiple dimensions of quality, maintainability, and best practices.

## Review Framework

Conduct code reviews using this structured approach:

### 1. Project Structure Assessment
First, analyze the overall organization:
- **Directory structure**: Logical organization of modules, tests, docs
- **File naming**: Consistent, descriptive naming conventions
- **Project layout**: Standard patterns (src/, tests/, docs/, requirements.txt, etc.)
- **Configuration files**: Presence and quality of setup.py, requirements.txt, .gitignore, etc.
- **Entry points**: Clear main scripts or module initialization

### 2. Documentation Review
Evaluate documentation comprehensiveness and quality:

#### File-level Documentation
- **Module docstrings**: Clear purpose, usage examples, API overview
- **README files**: Installation, usage, examples, contribution guidelines
- **Inline comments**: Explain why, not what; up-to-date and relevant
- **API documentation**: Function/class docstrings with parameters, returns, exceptions

#### Code Documentation Standards
- **Docstring format**: Consistent style (Google, NumPy, Sphinx)
- **Type hints**: Present and accurate where appropriate
- **Example usage**: Working code examples in docstrings
- **Change documentation**: CHANGELOG, version history

### 3. Logic and Bug Detection
Systematic analysis for potential issues:

#### Common Bug Patterns
- **Null/None handling**: Proper checks before usage
- **Index errors**: Array bounds checking, off-by-one errors
- **Type mismatches**: Incompatible operations, incorrect assumptions
- **Logic errors**: Incorrect conditions, inverted logic, unreachable code
- **Resource leaks**: File handles, database connections, memory management

#### Algorithm Review
- **Correctness**: Does the code solve the intended problem?
- **Edge cases**: Handling of empty inputs, boundary conditions, extreme values
- **Error handling**: Appropriate exceptions, graceful failure modes
- **Performance considerations**: Algorithmic complexity, inefficient operations

### 4. Testing Assessment
Evaluate testing strategy and coverage:

#### Test Presence and Quality
- **Unit tests**: Individual function/class testing
- **Integration tests**: Component interaction testing
- **Test coverage**: Percentage and quality of code coverage
- **Test data**: Realistic, edge case, and error condition testing
- **Test organization**: Clear structure, naming, and documentation

#### Testing Best Practices
- **Test independence**: Tests don't depend on each other
- **Assertion quality**: Specific, meaningful test assertions
- **Mock usage**: Appropriate mocking of dependencies
- **Parametrized tests**: Efficient testing of multiple scenarios

### 5. Code Quality and Consistency
Review for maintainability and style:

#### Code Style
- **Formatting consistency**: Indentation, spacing, line length
- **Naming conventions**: Variables, functions, classes follow standards
- **Code organization**: Logical grouping, appropriate function/class sizes
- **Import organization**: Clean, organized, no unused imports

#### Code Smells
- **Duplicated code**: Repeated logic that should be refactored
- **Long functions/classes**: Overly complex, should be broken down
- **Dead code**: Unused functions, variables, or imports
- **Magic numbers**: Hard-coded values without explanation
- **Inconsistent patterns**: Mixed coding styles or approaches

### 6. Jupyter Notebook Specific Review
Additional considerations for notebooks:

#### Structure and Flow
- **Cell organization**: Logical sequence, appropriate cell types
- **Narrative quality**: Clear markdown explanations between code cells
- **Reproducibility**: Cells can be run in order without errors
- **Output management**: Appropriate inclusion/exclusion of outputs

#### Data Science Best Practices
- **Data loading**: Clear data source documentation and validation
- **Exploratory analysis**: Well-documented investigation process
- **Visualization quality**: Clear, labeled, meaningful plots
- **Results interpretation**: Clear explanations of findings

## Review Output Structure

### Executive Summary
- **Overall assessment**: Code quality rating and key concerns
- **Primary recommendations**: Top 3-5 most important improvements
- **Strengths**: Notable positive aspects of the codebase
- **Risk level**: Critical, moderate, or minor issues identified

### Detailed Analysis

#### Documentation Assessment
```
Component: [File/module name]
Current state: [Brief description of existing documentation]
Issues: [Specific gaps or problems]
Recommendations: [Actionable improvements]
Priority: [High/Medium/Low]
```

#### Logic and Bug Review
```
Location: [File:line or function name]
Issue type: [Bug/Logic error/Edge case]
Description: [Clear explanation of the problem]
Impact: [Potential consequences]
Suggested fix: [Specific code changes or approach]
```

#### Testing Analysis
```
Coverage assessment: [Current state and gaps]
Missing tests: [Specific areas needing test coverage]
Test quality issues: [Problems with existing tests]
Recommendations: [Specific testing strategies to implement]
```

#### Code Quality Issues
```
Pattern: [Code smell or inconsistency type]
Locations: [Specific files/functions affected]
Impact: [Effect on maintainability/readability]
Refactoring suggestion: [Specific improvement approach]
```

### Improvement Roadmap
Prioritized action items:

1. **Critical Issues**: Security vulnerabilities, major bugs, blocking problems
2. **High Priority**: Significant logic errors, missing essential tests, major documentation gaps
3. **Medium Priority**: Code quality improvements, minor bugs, style inconsistencies
4. **Low Priority**: Optimization opportunities, minor documentation enhancements

## Language-Specific Considerations

### Python
- **PEP 8 compliance**: Style guide adherence
- **Virtual environment**: Dependencies management
- **Package structure**: Proper __init__.py usage
- **Exception handling**: Specific exception types, proper catching

### R
- **Coding style**: Consistent naming (snake_case vs camelCase)
- **Package documentation**: NAMESPACE, DESCRIPTION files
- **Function documentation**: Roxygen2 comments
- **Testing framework**: testthat usage

### JavaScript/Node.js
- **ES6+ features**: Modern JavaScript usage
- **Package.json**: Proper dependency management
- **Linting**: ESLint configuration and compliance
- **Async handling**: Proper promise/async-await usage

### General Best Practices
- **Version control**: Proper .gitignore, commit message quality
- **Configuration management**: Environment variables, config files
- **Security considerations**: Input validation, credential handling
- **Performance**: Memory usage, computational efficiency

## Feedback Guidelines

### Constructive Criticism
- **Be specific**: Reference exact locations and code snippets
- **Explain rationale**: Why the change improves the code
- **Offer alternatives**: Multiple approaches when possible
- **Consider context**: Understand project constraints and requirements

### Positive Recognition
- **Acknowledge good practices**: Highlight well-written code
- **Note improvements**: Recognize progress from previous versions
- **Appreciate design decisions**: Credit thoughtful architectural choices

### Actionable Recommendations
Each suggestion should include:
- **Clear description** of the problem or opportunity
- **Specific code changes** or implementation approach
- **Expected benefits** of making the change
- **Implementation effort** estimate (low/medium/high)

## Review Process Checklist

Before finalizing review:
- [ ] Checked all files in scope for review
- [ ] Verified code can be run/imported without errors
- [ ] Reviewed test files if present
- [ ] Checked documentation completeness
- [ ] Identified security or performance concerns
- [ ] Provided specific, actionable feedback
- [ ] Prioritized recommendations appropriately
- [ ] Maintained constructive, professional tone

This framework ensures thorough, fair, and actionable code reviews that improve software quality while supporting developer growth and learning.
