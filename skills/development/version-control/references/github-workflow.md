# GitHub Workflow Guide

Complete guide to GitHub-specific features, pull requests, Actions, and collaboration tools.

## GitHub Pull Request Workflow

### Creating a Pull Request

**1. Push your branch:**
```bash
git push -u origin feat/new-feature
```

**2. Create PR on GitHub:**
- Click "Compare & pull request" button, or
- Go to Pull Requests tab → "New pull request"

**3. Fill PR template:**

**Title:** Use Conventional Commit format
```
feat(auth): add OAuth2 authentication support
```

**Description:**
```markdown
## Summary
Add OAuth2 authentication with Google and GitHub providers.
Users can now sign in using their existing accounts.

## Changes
- Implement OAuth2 flow for Google and GitHub
- Add user account linking for existing users
- Create OAuth settings page
- Add tests for authentication flow

## Testing
1. Navigate to /login
2. Click "Sign in with Google" or "Sign in with GitHub"
3. Complete OAuth flow in provider's page
4. Verify user is logged in and profile is synced

## Screenshots
![Login page](screenshots/login.png)

## Checklist
- [x] Tests added and passing
- [x] Documentation updated
- [x] No breaking changes
- [x] Follows Conventional Commits
- [ ] Security review requested
```

**4. Set PR metadata:**
- **Reviewers:** Assign team members
- **Assignees:** Yourself (usually)
- **Labels:** feature, enhancement, bug, etc.
- **Projects:** Link to project board
- **Milestone:** Link to sprint/release
- **Linked issues:** "Closes #123"

### PR Templates

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Summary
<!-- Brief description of changes and motivation -->

## Type of Change
<!-- Mark with [x] -->
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement

## Changes
<!-- List key changes with bullet points -->
-
-
-

## Testing
<!-- How to test these changes -->
1.
2.
3.

**Expected behavior:**

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Documentation
<!-- What documentation needs updating? -->
- [ ] README
- [ ] API docs
- [ ] User guide
- [ ] Inline code comments

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues
<!-- Link related issues -->
Closes #
Refs #
```

### Draft PRs

**Use for work-in-progress:**
```bash
# Push branch
git push -u origin feat/new-feature

# Create as draft PR on GitHub
# Checkbox: "Create as draft"
```

**Benefits:**
- Early feedback on approach
- Show progress to team
- Run CI checks
- Mark ready for review when done

### PR Labels

**Common labels:**
- `bug` - Bug fixes
- `enhancement` - New features
- `documentation` - Docs changes
- `refactoring` - Code restructuring
- `performance` - Performance improvements
- `security` - Security fixes
- `breaking-change` - Breaking changes
- `needs-review` - Ready for review
- `work-in-progress` - Not ready yet
- `blocked` - Waiting on something
- `urgent` - High priority
- `good-first-issue` - For new contributors

### PR Size Guidelines

**Extra Small (XS):** <10 lines
- Typo fixes
- Config changes
- Simple bug fixes

**Small (S):** 10-100 lines
- Single feature addition
- Bug fix with tests
- Small refactoring
- Ideal PR size

**Medium (M):** 100-300 lines
- Feature with multiple components
- Acceptable with good description

**Large (L):** 300-500 lines
- Complex feature
- Should consider splitting
- Requires extra review time

**Extra Large (XL):** 500+ lines
- Too large!
- Split into smaller PRs
- Use feature flags to merge incrementally

## Code Review on GitHub

### As a Reviewer

**1. Review the code:**
- Read PR description first
- Understand the goal
- Check out branch locally to test
- Review files on GitHub

**2. Leave comments:**

**General comment:**
```
Overall looks good! Just a few minor suggestions.
```

**Inline comment:**
```
Consider extracting this into a separate function for
better testability.
```

**Suggestion (GitHub will let author apply directly):**
```suggestion
const result = await fetchUser(userId);
```

**3. Request changes or approve:**
- **Approve:** Code is good to merge
- **Request changes:** Issues must be fixed
- **Comment:** Feedback without blocking

### Review Best Practices

**Do:**
- ✅ Review within 2-4 hours (small PRs)
- ✅ Test code locally
- ✅ Be constructive and specific
- ✅ Explain the "why" behind suggestions
- ✅ Praise good code
- ✅ Distinguish blocking vs non-blocking feedback

**Don't:**
- ❌ Nitpick code style (use linter instead)
- ❌ Leave PRs waiting for days
- ❌ Just say "looks good" without reviewing
- ❌ Be vague ("this doesn't look right")
- ❌ Rewrite in your own style

**Comment prefixes:**
```
nit: Minor style suggestion (non-blocking)
suggestion: Consider this approach
question: Can you explain this?
blocker: Must be fixed before merge
optional: Nice to have
```

### Responding to Review Feedback

**As author:**

**1. Respond to each comment:**
```
Good catch! Fixed in abc123.

or

I kept it this way because... but open to other approaches.

or

Not sure I understand - can you clarify?
```

**2. Make requested changes:**
```bash
# Make changes
git add .
git commit -m "fix(auth): address PR feedback"
git push origin feat/new-feature
```

**3. Mark conversations as resolved:**
- Click "Resolve conversation" after addressing
- Let reviewer resolve their own comments

**4. Re-request review:**
- Click "Re-request review" icon after pushing changes
- Add comment: "Ready for another look!"

### Review Checklist

**Functionality:**
- [ ] Does the code work as intended?
- [ ] Are edge cases handled?
- [ ] Are errors handled properly?
- [ ] Is the approach sound?

**Code Quality:**
- [ ] Is code readable?
- [ ] Are names descriptive?
- [ ] Is code DRY (no unnecessary duplication)?
- [ ] Are functions reasonably sized?
- [ ] Is complexity reasonable?

**Testing:**
- [ ] Are there tests?
- [ ] Do tests cover main functionality?
- [ ] Do tests cover edge cases?
- [ ] Are tests readable and maintainable?

**Security:**
- [ ] No sensitive data exposed?
- [ ] Input validation present?
- [ ] No SQL injection risk?
- [ ] No XSS vulnerabilities?
- [ ] Authentication/authorization correct?

**Performance:**
- [ ] No obvious performance issues?
- [ ] Database queries optimized?
- [ ] No N+1 query problems?
- [ ] Appropriate caching?

**Documentation:**
- [ ] Public API documented?
- [ ] Complex logic explained?
- [ ] README updated if needed?

## GitHub Actions

### Basic CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Check coverage
        run: npm run coverage

      - name: Build
        run: npm run build
```

### Multi-Job Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
```

### Deployment Workflow

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install
        run: npm ci

      - name: Build
        run: npm run build

      - name: Deploy to production
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: |
          npm run deploy

      - name: Notify team
        if: always()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text":"Deployment ${{ job.status }}"}'
```

### Conventional Commit Validation

```yaml
name: Commit Lint

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: wagoid/commitlint-github-action@v5
        with:
          configFile: .commitlintrc.json
```

### Code Coverage Upload

```yaml
name: Coverage

on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run coverage

      - name: Upload to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
```

## Branch Protection Rules

### Essential Rules

Configure for `main` branch:

**1. Require pull request before merging:**
- ✅ Enable
- Required approvals: 1 (or 2 for larger teams)
- ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ Require review from Code Owners

**2. Require status checks to pass:**
- ✅ Enable
- ✅ Require branches to be up to date before merging
- Required checks:
  - Tests
  - Lint
  - Build
  - Coverage

**3. Require conversation resolution:**
- ✅ Require all conversations to be resolved before merging

**4. Require linear history:**
- ✅ Enable (enforces rebase or squash merge)

**5. Additional settings:**
- ✅ Do not allow bypassing the above settings
- ✅ Restrict who can push to matching branches (admins only)
- ✅ Allow force pushes: Disable
- ✅ Allow deletions: Disable
- ✅ Automatically delete head branches: Enable

### CODEOWNERS File

Create `.github/CODEOWNERS`:

```
# Default owners for everything
* @org/core-team

# Frontend code
/src/components/** @org/frontend-team @user1
/src/styles/** @org/frontend-team

# Backend code
/src/api/** @org/backend-team @user2
/src/database/** @org/backend-team @user3

# DevOps
/.github/workflows/** @org/devops-team
/Dockerfile @org/devops-team
/docker-compose.yml @org/devops-team

# Documentation
/docs/** @user4
README.md @user4

# Critical files require additional review
/package.json @org/senior-devs
/tsconfig.json @org/senior-devs
/.github/workflows/deploy.yml @org/devops-lead
```

**Effects:**
- Auto-assigns reviewers based on files changed
- Can require CODEOWNERS approval in branch protection

## GitHub CLI (gh)

### Installation

```bash
# macOS
brew install gh

# Linux
sudo apt install gh

# Windows
winget install --id GitHub.cli

# Authenticate
gh auth login
```

### PR Management

**Create PR:**
```bash
# Interactive
gh pr create

# With details
gh pr create \
  --title "feat(auth): add OAuth support" \
  --body "Implements OAuth with Google and GitHub" \
  --label "enhancement" \
  --assignee @me

# From template
gh pr create --fill
```

**List PRs:**
```bash
# Your PRs
gh pr list --author @me

# All open PRs
gh pr list

# By label
gh pr list --label "bug"
```

**View PR:**
```bash
# View in terminal
gh pr view 123

# View in browser
gh pr view 123 --web

# View diff
gh pr diff 123
```

**Checkout PR:**
```bash
# Checkout PR locally
gh pr checkout 123

# Create branch and checkout
gh pr checkout 123 --force
```

**Review PR:**
```bash
# Approve
gh pr review 123 --approve

# Request changes
gh pr review 123 --request-changes --body "Please address comments"

# Comment
gh pr review 123 --comment --body "Looks good overall"
```

**Merge PR:**
```bash
# Merge
gh pr merge 123

# Squash merge
gh pr merge 123 --squash

# Rebase merge
gh pr merge 123 --rebase

# Auto-merge when checks pass
gh pr merge 123 --auto --squash
```

**PR checks:**
```bash
# View check status
gh pr checks 123

# Watch checks
gh pr checks 123 --watch
```

### Issue Management

**Create issue:**
```bash
gh issue create \
  --title "User login fails with OAuth" \
  --body "Description..." \
  --label "bug" \
  --assignee @me
```

**List issues:**
```bash
# All open
gh issue list

# Your issues
gh issue list --assignee @me

# By label
gh issue list --label "bug"
```

**View issue:**
```bash
gh issue view 123
gh issue view 123 --web
```

**Close issue:**
```bash
gh issue close 123 --comment "Fixed in #124"
```

### Repository Operations

**Clone:**
```bash
gh repo clone owner/repo
```

**Fork:**
```bash
gh repo fork owner/repo --clone
```

**View repo:**
```bash
gh repo view
gh repo view --web
```

**Create repo:**
```bash
gh repo create my-project --public --source=. --remote=origin
```

## GitHub Features

### Discussions

Enable for:
- Q&A
- Ideas and feature requests
- General discussions
- Community building

### Projects

**Project boards:**
- Kanban-style boards
- Automated workflows
- Link issues and PRs
- Track progress

### Releases

**Create release:**
```bash
# Tag version
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create release on GitHub
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes "Release notes here"
```

### GitHub Pages

**Deploy documentation:**

```yaml
# .github/workflows/docs.yml
name: Deploy Docs

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build docs
        run: npm run docs:build
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs-dist
```

## Collaboration Best Practices

### PR Etiquette

**As author:**
- Write clear PR descriptions
- Keep PRs small and focused
- Respond to feedback promptly
- Don't merge your own PRs without review
- Thank reviewers

**As reviewer:**
- Review promptly (within 2-4 hours)
- Be constructive and specific
- Explain reasoning for changes
- Approve when ready, don't hold up
- Use appropriate tone

### Communication

**In PR comments:**
```markdown
Great work! Just a few suggestions:

1. Consider extracting the validation logic into a separate
   function. This would make it easier to test and reuse.

2. The error handling looks good, but we should also log
   errors to our monitoring service.

Otherwise this looks ready to go! 🚀
```

**In issue comments:**
```markdown
I've investigated this issue and found that...

To reproduce:
1. ...
2. ...

Proposed fix: ...

I can take this on if no one else is working on it.
```

### Mention Protocol

**@mentions:**
- `@username` - Notify specific person
- `@org/team` - Notify team
- Use sparingly - don't spam

**When to mention:**
- Need specific person's input
- Question for code owner
- Blocked on something
- FYI for stakeholder

**When not to mention:**
- Already auto-assigned as reviewer
- General question (ask in discussion instead)
- Just to get attention faster

## Advanced GitHub Features

### Saved Replies

Create common responses:

```markdown
Thanks for the contribution! Before we can merge, please:
- [ ] Add tests
- [ ] Update documentation
- [ ] Ensure CI passes
```

### Issue Templates

`.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS]
- Browser: [e.g. chrome, safari]
- Version: [e.g. 22]

**Additional context**
Any other context about the problem.
```

### Repository Settings

**Security:**
- Enable vulnerability alerts
- Enable automated security fixes (Dependabot)
- Require two-factor authentication

**Branches:**
- Set default branch to `main`
- Configure branch protection
- Auto-delete head branches after merge

**Actions:**
- Set workflow permissions
- Configure required approvals
- Set timeout limits

### Webhooks

Trigger external services:
- Slack notifications on PR events
- Deploy on push to main
- Update project management tools
- Custom automation

---

**Remember:** GitHub is more than just git hosting - it's a collaboration platform. Use PRs for code review, Actions for automation, Issues for tracking, and Discussions for community. Leverage these tools to build better software together.
