---
name: tdd
description: |
  Test-Driven Development facilitation using the red-green-refactor cycle. Guides users through
  writing tests first, implementing minimal code to pass, and refactoring for quality. Use when
  users want to practice TDD, need help writing tests before code, are developing new features
  test-first, or want guidance on test structure and implementation. Triggers include 'use TDD,'
  'test-driven development,' 'write tests first,' 'red-green-refactor,' or requests to develop
  functionality with tests.
allowed-tools: ["*"]
---

# Test-Driven Development (TDD) Skill

Guide users through disciplined test-first development using the red-green-refactor cycle.

## Core TDD Workflow

**RED → GREEN → REFACTOR → REPEAT**

### RED: Write a Failing Test
1. Identify next small behavior to implement
2. Write test that specifies that behavior
3. Run test to verify it **fails for the right reason**
4. If test passes unexpectedly, test is wrong

### GREEN: Make It Pass
1. Write **minimal** code to make test pass
2. Don't worry about perfection yet
3. Simplest solution that works
4. Run test to verify it passes

### REFACTOR: Improve the Code
1. Improve code quality while keeping tests green
2. Remove duplication
3. Improve names and structure
4. Run tests after each change to ensure still passing

### REPEAT
1. Commit when tests are green
2. Identify next behavior
3. Start cycle again with new test

## TDD Discipline

**Critical rules to follow:**

### Test First (RED Phase)
- **Always write test before implementation**
- Resist urge to write code first
- Test defines what "done" means
- See test fail before making it pass

### Minimal Implementation (GREEN Phase)
- **Write simplest code to pass**
- Don't over-engineer
- Don't add features not tested
- One test at a time

### Refactor Only When Green
- **Never refactor with failing tests**
- Keep tests passing during refactoring
- Small, incremental improvements
- Run tests after each refactoring step

### Run Tests Frequently
- After writing test (should fail)
- After writing implementation (should pass)
- After each refactoring step (should stay green)
- Before committing

## When to Use This Skill

Activate for requests involving:
- "Use TDD for..." / "Test-driven development..."
- "Write tests first..." / "Red-green-refactor..."
- Developing new features test-first
- Learning TDD practices
- Setting up test infrastructure
- Test design and organization

## Test Structure Patterns

### Arrange-Act-Assert (AAA)
**Arrange** - Set up test data and environment
**Act** - Execute the code under test
**Assert** - Verify the results

```python
def test_add_two_numbers():
    calculator = Calculator()           # Arrange
    result = calculator.add(2, 3)      # Act
    assert result == 5                  # Assert
```

### Given-When-Then (BDD Style)
**Given** - Initial context/preconditions
**When** - Action/event occurs
**Then** - Expected outcome

## Test Design Principles

### What to Test
- **Public interface** - Test behavior users depend on
- **Edge cases** - Boundaries, empty inputs, max values
- **Error conditions** - Invalid inputs, exceptions
- **Business logic** - Core algorithms and rules
- **Integration points** - Where components interact

### What NOT to Test
- **Private implementation details** - Test behavior, not internals
- **Third-party libraries** - Trust they work, test your usage
- **Simple getters/setters** - Unless they have logic
- **Framework code** - Test your code, not the framework

### One Behavior Per Test
- Each test should verify single behavior
- Makes failures easier to diagnose
- Keeps tests focused and readable
- Prefer multiple small tests over one large test

### Make Tests Readable
- **Descriptive names** - `test_add_returns_sum_of_two_positive_numbers`
- **Clear structure** - AAA or Given-When-Then
- **Self-documenting** - Test shows how code should be used
- **Minimal setup** - Only what's needed for this test

### Keep Tests Independent
- Tests should not depend on each other
- Tests can run in any order
- Each test starts with clean state
- No shared mutable state between tests

See `references/test-design-patterns.md` for comprehensive guidance.

## Language-Specific Guidance

### For Python
See `references/python-tdd.md` for:
- pytest and unittest frameworks
- Fixtures and parametrized tests
- Mocking with unittest.mock
- Testing async code
- Coverage with pytest-cov
- Running and organizing tests

### For Emacs Lisp
See `references/elisp-tdd.md` for:
- ERT (Emacs Lisp Regression Testing)
- Testing interactive functions
- Buffer manipulation testing
- Mocking with cl-letf
- Buttercup (BDD alternative)
- Running tests in Emacs and batch mode

### For Other Languages
See `references/general-tdd.md` for:
- Finding testing frameworks
- Universal test patterns
- Common testing concepts
- Build tool integration
- Language-agnostic principles

## Test Types and When to Use

### Unit Tests
**What:** Test individual functions/methods in isolation

**When:**
- Testing pure functions
- Testing business logic
- Testing algorithms
- Fast, focused tests

**Example:** `test_calculate_discount(price, percentage)`

### Integration Tests
**What:** Test multiple components working together

**When:**
- Testing database interactions
- Testing API calls
- Testing service integration
- Verifying components connect correctly

**Example:** `test_user_service_saves_to_database()`

### End-to-End Tests
**What:** Test complete user workflows

**When:**
- Testing critical user paths
- Verifying system as a whole
- Smoke tests for deployment

**Example:** `test_user_can_register_and_login()`

**Test Pyramid:**
```
      /\      ← Few E2E tests (slow, brittle)
     /  \
    / IT \    ← Some Integration tests
   /______\
  /  Unit  \  ← Many Unit tests (fast, focused)
 /__________\
```

## TDD Red-Green-Refactor Example

**Goal:** Implement factorial function

**Iteration 1 - Base case:**
- RED: `test_factorial_of_zero_is_one()` → ❌ factorial not defined
- GREEN: `def factorial(n): return 1` → ✅ Passes
- REFACTOR: Nothing yet. Commit.

**Iteration 2 - Positive numbers:**
- RED: `test_factorial_of_five()` expects 120 → ❌ Got 1
- GREEN: Implement loop to calculate factorial → ✅ Passes
- REFACTOR: Use recursion for elegance → ✅ Still passes. Commit.

**Iteration 3 - Error handling:**
- RED: `test_factorial_negative_raises_error()` → ❌ No error raised
- GREEN: Add if n < 0: raise ValueError → ✅ All tests pass
- REFACTOR: Add docstring → ✅ Still passes. Commit.

**Done!** Function is complete, fully tested, documented. Three test-driven iterations.

## Mocking and Test Doubles

### When to Mock
- **External dependencies** - Databases, APIs, file systems
- **Slow operations** - Network calls, large computations
- **Unpredictable behavior** - Random, time-dependent, external state
- **Hard to trigger scenarios** - Error conditions, edge cases

### When NOT to Mock
- **Your own code** - Prefer real objects for your code
- **Simple objects** - Data classes, value objects
- **Logic being tested** - Don't mock what you're testing

### Types of Test Doubles

**Mock** - Programmed with expectations, verifies interactions
**Stub** - Provides canned responses, doesn't verify
**Fake** - Working implementation, simpler than real
**Spy** - Records calls, allows verification after

See `references/test-design-patterns.md` for detailed mocking strategies.

## Common TDD Anti-Patterns

**Don't:**

❌ **Write implementation before test** - Defeats TDD purpose

❌ **Write multiple tests before making them pass** - Stay in rhythm (one test, make it pass, next test)

❌ **Refactor with red tests** - Only refactor when green

❌ **Test implementation details** - Test behavior, not internals

❌ **Skip refactor step** - Technical debt accumulates

❌ **Write tests that are hard to understand** - Tests are documentation

❌ **Create dependencies between tests** - Tests must be independent

❌ **Mock everything** - Use real objects when practical

❌ **Fake it with hardcoded values forever** - "Fake it till you make it" is temporary

❌ **Write slow tests** - Slow test suite won't be run frequently

## Test Naming Conventions

**Good test names are descriptive and specific:**

### Pattern: `test_<function>_<scenario>_<expected_result>`
```python
test_add_two_positive_numbers_returns_sum()
test_add_with_negative_number_returns_correct_result()
test_add_with_zero_returns_other_number()
```

### Pattern: `should_<expected_behavior>_when_<condition>`
```python
should_return_empty_list_when_no_items_match()
should_raise_error_when_input_is_null()
should_calculate_discount_when_user_is_premium()
```

### Pattern: `<behavior>_<state>_<expected>`
```elisp
(ert-deftest save-buffer-modified-saves-to-file ())
(ert-deftest load-file-missing-raises-error ())
```

**Test name should:**
- Describe what's being tested
- Describe the scenario/condition
- Describe expected outcome
- Be readable as documentation

## Test Organization

### Directory Structure

**Python:**
```
project/
├── src/
│   └── calculator.py
└── tests/
    ├── __init__.py
    ├── test_calculator.py
    └── conftest.py  # pytest fixtures
```

**Elisp:**
```
package/
├── my-package.el
└── test/
    └── test-my-package.el
```

### Naming Conventions
- Test files: `test_*.py`, `*_test.py`, `test-*.el`
- Test functions: Start with `test_` or `ert-deftest`
- Test classes: `Test*` (if using classes)

### Grouping Tests
- One test file per source file (generally)
- Group related tests in same file
- Separate unit/integration/e2e tests

See language-specific references for detailed organization patterns.

## Refactoring with Tests

### Safe Refactoring Process

1. **Ensure all tests are green** before starting
2. **Make small changes** - One refactoring at a time
3. **Run tests after each change** - Catch breaks immediately
4. **Commit frequently** - When tests pass
5. **Don't add features while refactoring** - Separate concerns

### Common Refactorings
- Extract function (break up large functions)
- Rename for clarity
- Remove duplication (DRY)
- Simplify conditional logic
- Extract variable for readability
- Inline unnecessary abstraction

### When Tests Break During Refactoring

**If test is testing implementation detail:**
- Update test to test behavior instead
- Make test more resilient to changes

**If test is testing behavior:**
- Fix the code, not the test
- Behavior shouldn't change during refactoring

**If too many tests break:**
- Change is too large, revert
- Make smaller incremental changes

See `references/refactoring-with-tests.md` for detailed guidance.

## Test Coverage

**Coverage measures which code is executed by tests, not whether tests are good.**

### Types of Coverage
- **Line coverage** - Which lines executed
- **Branch coverage** - Which paths taken
- **Function coverage** - Which functions called

### Coverage Goals
- Aim for high coverage (80%+) but not 100%
- 100% coverage doesn't mean bug-free
- Focus on critical code paths
- Don't test just to increase coverage

### Using Coverage Tools
- **Python:** pytest-cov, coverage.py
- **JavaScript:** Jest with coverage
- **Java:** JaCoCo
- **Ruby:** SimpleCov

Use `scripts/coverage_analyzer.py` to identify coverage gaps.

## Using Supporting Resources

Additional resources in this skill:

- **references/python-tdd.md**: Comprehensive Python testing guide (pytest, unittest, mocking, async)
- **references/elisp-tdd.md**: Comprehensive Elisp testing guide (ERT, Buttercup, interactive functions)
- **references/general-tdd.md**: Universal TDD principles for any language
- **references/test-design-patterns.md**: What to test, test organization, anti-patterns
- **references/refactoring-with-tests.md**: Safe refactoring process and common refactorings
- **scripts/test_template_generator.py**: Generate test file boilerplate
- **scripts/coverage_analyzer.py**: Analyze coverage reports
- **assets/templates/**: Test file templates for multiple languages

## Quick Reference

**TDD Cycle:**
1. RED - Write failing test
2. GREEN - Make it pass (minimal code)
3. REFACTOR - Improve while keeping green
4. REPEAT

**Test Structure:**
- Arrange (setup)
- Act (execute)
- Assert (verify)

**Test Principles:**
- Test first
- One test at a time
- One behavior per test
- Independent tests
- Fast tests
- Readable tests

**Refactoring Rules:**
- Only refactor when green
- Small changes
- Run tests frequently
- Don't add features

---

**Remember:** TDD is a discipline. The value comes from following the cycle strictly. Test first. See it fail. Make it pass. Refactor. Repeat. The rhythm creates quality code.
