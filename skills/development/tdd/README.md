# Test-Driven Development (TDD) Skill

A comprehensive skill for practicing Test-Driven Development with systematic guidance through the red-green-refactor cycle.

## Overview

This skill provides structured guidance for Test-Driven Development (TDD), helping you write tests first, implement minimal code to pass those tests, and then refactor with confidence. It supports multiple programming languages with specific guidance for Python and Emacs Lisp.

## Core Methodology

### The Red-Green-Refactor Cycle

**🔴 RED - Write a Failing Test**
1. Write a test for the next small piece of functionality
2. Run the test and watch it fail
3. Ensure the test fails for the right reason

**🟢 GREEN - Make It Pass**
1. Write the minimal code to make the test pass
2. Don't worry about elegance or optimization
3. Just make it work

**🔵 REFACTOR - Improve the Code**
1. Clean up the code while keeping tests green
2. Remove duplication
3. Improve names and structure
4. Commit your changes

**🔁 REPEAT**
- Start the next cycle with a new test

## When to Use This Skill

- **Starting a new feature** - Build it test-first
- **Fixing a bug** - Write a failing test that reproduces it
- **Learning a new language** - Practice with TDD
- **Refactoring legacy code** - Add tests first, then refactor
- **Building critical logic** - Ensure correctness with tests
- **Working in a team** - Tests document behavior

## Key Capabilities

1. **Red-Green-Refactor Cycle** - Systematic TDD workflow
2. **Test Structure Patterns** - AAA (Arrange-Act-Assert) and Given-When-Then
3. **Test Case Design** - What to test, edge cases, error conditions
4. **Minimal Implementation** - Resist over-engineering
5. **Refactoring with Tests** - Safe code improvement
6. **Test Organization** - Naming, grouping, file structure
7. **Mocking & Stubbing** - Isolate code under test
8. **Test Coverage** - Identify gaps and prioritize
9. **Language-Specific Guidance** - Python (pytest, unittest) and Elisp (ERT, Buttercup)
10. **Integration vs Unit Tests** - Understanding the test pyramid

## Language Support

### Python
- **pytest** - Modern, feature-rich framework
- **unittest** - Standard library testing
- **pytest-cov** - Coverage reporting
- **unittest.mock** - Mocking and stubbing

See `references/python-tdd.md` for comprehensive Python TDD guide.

### Emacs Lisp
- **ERT** - Built-in Emacs Lisp Regression Testing
- **Buttercup** - BDD-style testing framework
- Buffer and interactive function testing
- Mock/stub with `cl-letf`

See `references/elisp-tdd.md` for comprehensive Elisp TDD guide.

### Any Language
- Universal TDD principles
- Finding testing frameworks
- Test naming conventions
- Build tool integration

See `references/general-tdd.md` for language-agnostic guidance.

## Tools & Scripts

### Test Template Generator
Generate test file boilerplate for different languages:

```bash
# Python test template
python scripts/test_template_generator.py --language python --module calculator

# Elisp test template
python scripts/test_template_generator.py --language elisp --module my-package

# JavaScript test template
python scripts/test_template_generator.py --language javascript --module utils

# Save to file
python scripts/test_template_generator.py --language python --module mymod --output test_mymod.py
```

### Coverage Analyzer
Analyze test coverage and identify gaps:

```bash
# Analyze coverage report
python scripts/coverage_analyzer.py analyze coverage.xml

# Get suggestions for next tests
python scripts/coverage_analyzer.py suggest coverage.xml --min-coverage 80

# Different formats
python scripts/coverage_analyzer.py analyze coverage.json --format json
```

## Templates

### Python Test Template
Comprehensive pytest template with:
- Fixtures and parametrized tests
- Happy path, edge cases, and error conditions
- Mocking examples
- Integration tests
- Async test patterns

Location: `assets/templates/python_test_template.py`

### Elisp Test Template
Comprehensive ERT template with:
- Basic assertions (should, should-not, should-error)
- Buffer manipulation tests
- Interactive function tests
- Mock/stub patterns with `cl-letf`
- Fixtures with `unwind-protect`

Location: `assets/templates/elisp_test_template.el`

### Test Coverage Checklist
Comprehensive checklist covering:
- Happy path tests
- Edge cases
- Error conditions
- Integration points
- State management
- Performance and security
- Regression tests

Location: `assets/templates/test_checklist.md`

### TDD Session Log
Template for documenting TDD sessions with:
- Red-Green-Refactor cycle tracking
- Code changes and commits
- Coverage metrics
- Insights and learnings
- Technical decisions

Location: `assets/templates/tdd_session_log.md`

## Reference Documentation

### `references/python-tdd.md`
Complete Python TDD guide covering pytest, unittest, fixtures, parametrized tests, mocking, async testing, and best practices.

### `references/elisp-tdd.md`
Complete Emacs Lisp TDD guide covering ERT, Buttercup, buffer testing, mocking, and CI/CD integration.

### `references/general-tdd.md`
Universal TDD principles applicable to any language, including finding frameworks, test structure, naming conventions, and common anti-patterns.

### `references/test-design-patterns.md`
Comprehensive guide to what to test, test organization, test smells, mocking strategies, and coverage goals.

### `references/refactoring-with-tests.md`
Safe refactoring process with tests as safety net, including common refactoring patterns and when to refactor.

## Example Usage

### Example 1: Building a Calculator with Python TDD

**Cycle 1: Addition**

```python
# 🔴 RED - test_calculator.py
def test_add_two_positive_numbers():
    calc = Calculator()
    assert calc.add(2, 3) == 5

# Run: ❌ NameError: Calculator not defined
```

```python
# 🟢 GREEN - calculator.py
class Calculator:
    def add(self, a, b):
        return a + b

# Run: ✅ All tests pass
```

```python
# 🔵 REFACTOR - Add docstrings
class Calculator:
    """Simple calculator for basic arithmetic."""

    def add(self, a, b):
        """Add two numbers and return the sum."""
        return a + b

# Run: ✅ All tests still pass
# Commit: "Add Calculator.add() method"
```

**Cycle 2: Edge Case - Negative Numbers**

```python
# 🔴 RED
def test_add_negative_numbers():
    calc = Calculator()
    assert calc.add(-2, -3) == -5

# Run: ✅ Already passes (implementation handles it)
# Good! Test documents behavior.
```

**Cycle 3: Error Handling**

```python
# 🔴 RED
def test_add_non_numeric_raises_error():
    calc = Calculator()
    with pytest.raises(TypeError):
        calc.add("2", 3)

# Run: ❌ Test fails (no type checking)
```

```python
# 🟢 GREEN
def add(self, a, b):
    """Add two numbers and return the sum."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a + b

# Run: ✅ All tests pass
# Commit: "Add type checking to Calculator.add()"
```

### Example 2: Elisp String Utilities

**Cycle 1: Reverse String**

```elisp
;; 🔴 RED - test-string-utils.el
(ert-deftest test-reverse-string ()
  "Test reversing a string."
  (should (string= (reverse-string "hello") "olleh")))

;; Run: ❌ void-function reverse-string
```

```elisp
;; 🟢 GREEN - string-utils.el
(defun reverse-string (s)
  "Reverse string S."
  (concat (reverse (string-to-list s))))

;; Run: ✅ Test passes
```

```elisp
;; 🔵 REFACTOR - Add error handling
(defun reverse-string (s)
  "Reverse string S.

S must be a string. Returns reversed string.
Signals error if S is not a string."
  (unless (stringp s)
    (error "Argument must be a string"))
  (concat (reverse (string-to-list s))))

;; Run: ✅ Test still passes
;; Add test for error case:
(ert-deftest test-reverse-string-error ()
  (should-error (reverse-string 123) :type 'error))
;; Commit: "Add reverse-string with error handling"
```

## Best Practices

### ✅ Do This
- **Write tests first** - Red-Green-Refactor discipline
- **Keep tests fast** - Fast feedback loop is essential
- **Test behavior, not implementation** - Tests survive refactoring
- **Use descriptive names** - Tests are documentation
- **One assertion focus** - Clear test purpose
- **Independent tests** - Run in any order
- **Commit frequently** - After each green+refactor cycle

### ❌ Avoid This
- **Implementation before tests** - Defeats TDD purpose
- **Testing private methods** - Couples tests to implementation
- **Slow tests** - Won't be run frequently
- **Complex test setup** - Hard to understand
- **Testing framework code** - Trust the framework
- **Skipping refactor step** - Accumulates technical debt
- **Large test changes** - Make incremental test improvements

## TDD Anti-Patterns

### Writing Too Much Code
**Problem:** Implementing more than needed to pass test
**Fix:** Write minimal code to make test pass

### Testing Implementation Details
**Problem:** Tests break when refactoring
**Fix:** Test through public interface

### Skipping Tests
**Problem:** Not enough coverage, bugs slip through
**Fix:** Write test for every behavior

### Not Running Tests Frequently
**Problem:** Long feedback loop, hard to locate bugs
**Fix:** Run tests after every change

### Ignoring Failing Tests
**Problem:** Test suite becomes meaningless
**Fix:** Keep all tests green or fix immediately

## Tips for Success

1. **Start Small** - Begin with the simplest test case
2. **Baby Steps** - Take tiny incremental steps
3. **Run Tests Constantly** - After every change
4. **Trust the Process** - Red-Green-Refactor cycle works
5. **Refactor Fearlessly** - Tests give you confidence
6. **Document with Tests** - Tests show how to use code
7. **Learn from Failures** - Failed tests teach you about your code

## Integration with CI/CD

### Python with GitHub Actions
```yaml
- name: Run tests
  run: pytest --cov=mymodule --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### Elisp with GitHub Actions
```yaml
- name: Run tests
  run: |
    emacs -batch -l ert -l my-package.el -l test/test-my-package.el \
    -f ert-run-tests-batch-and-exit
```

## Learning Path

### Beginner
1. Start with `references/general-tdd.md` to understand principles
2. Follow red-green-refactor cycle strictly
3. Use templates to generate test files
4. Practice with simple functions (calculator, string utilities)

### Intermediate
1. Study language-specific patterns (Python or Elisp references)
2. Learn mocking and stubbing
3. Understand test organization
4. Use coverage analyzer to find gaps

### Advanced
1. Master refactoring with tests
2. Design testable architectures
3. Balance unit, integration, and E2E tests
4. Optimize test suite performance
5. Mentor others in TDD practice

## Common Questions

**Q: Do I need 100% coverage?**
A: No. Aim for 80-90% of critical code. Focus on business logic, not simple getters.

**Q: Should I test private methods?**
A: No. Test through public interface. If private method needs testing, it might need to be public or extracted.

**Q: How do I test legacy code?**
A: Add characterization tests first, then refactor. See "Working Effectively with Legacy Code" by Michael Feathers.

**Q: TDD feels slow at first?**
A: Yes, but speeds up as you master it. Prevents debugging time later.

**Q: What if I don't know how to design it yet?**
A: TDD helps you discover the design. Let tests guide your API.

## Resources

- **Books:**
  - "Test Driven Development: By Example" - Kent Beck
  - "Growing Object-Oriented Software, Guided by Tests" - Freeman & Pryce
  - "The Art of Unit Testing" - Roy Osherove

- **Online:**
  - pytest documentation: https://docs.pytest.org/
  - ERT manual: https://www.gnu.org/software/emacs/manual/html_node/ert/
  - Test Pyramid: https://martinfowler.com/bliki/TestPyramid.html

## Contributing

To improve this skill:
1. Add examples for other languages
2. Extend templates with more patterns
3. Add real-world case studies
4. Share TDD tips and tricks

## License

This skill is part of the skillpack project and follows the same license.
