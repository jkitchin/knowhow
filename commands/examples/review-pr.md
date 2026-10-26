---
description: Review code changes with best practices
argument-hint: <files-or-diff>
model: opus
allowed-tools: ["Read", "Grep", "Glob"]
---

# Code Review

Please perform a thorough code review of the changes in: $ARGUMENTS

Review for:

## Code Quality
- [ ] Code is readable and well-structured
- [ ] Naming conventions are clear and consistent
- [ ] Functions are focused and single-purpose
- [ ] No unnecessary complexity

## Best Practices
- [ ] Follows language-specific conventions
- [ ] Error handling is appropriate
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed

## Testing & Documentation
- [ ] Changes are testable
- [ ] Tests are included (if applicable)
- [ ] Documentation is updated
- [ ] Comments explain complex logic

## Suggestions
Provide specific, actionable feedback with examples where helpful.
