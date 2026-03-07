# Trunk-Based Development Complete Guide

## Philosophy

Trunk-Based Development (TBD) is a source control branching model where developers collaborate on code in a single branch called 'trunk' (or 'main'), resist creating long-lived feature branches, and instead make small, frequent changes.

**Core Principles:**
1. Single main branch that is always deployable
2. Short-lived feature branches (hours to days, not weeks)
3. Frequent integration to main
4. Small, incremental changes
5. Continuous integration mindset
6. Feature flags for incomplete features

## Why Trunk-Based Development?

### Benefits

**Faster integration:**
- Merge conflicts are smaller and easier to resolve
- Less time spent on integration
- Faster feedback from CI/CD

**Better collaboration:**
- Team works on current code, not weeks-old branches
- Easier to coordinate work
- Shared ownership of codebase

**Improved quality:**
- Issues found faster
- Always working from tested, integrated code
- CI runs frequently

**Simpler workflow:**
- No complex branching strategies
- Less mental overhead
- Easier for new team members

**Enables CD:**
- Main branch always deployable
- Can release at any time
- Faster time to market

### Challenges

**Requires discipline:**
- Must commit tested code
- Need good CI/CD pipeline
- Requires code review process

**Incomplete features:**
- Need feature flags
- Hide work-in-progress
- Additional complexity

**Team coordination:**
- More communication needed
- Shared responsibility
- Cultural shift from Git Flow

## Main Branch (Trunk)

### Always Deployable Rule

**Main branch must always:**
- Pass all tests
- Build successfully
- Be ready for production deployment
- Contain no broken features (use feature flags instead)

**This means:**
```bash
# This should always work
git checkout main
npm run build
npm test
./deploy.sh
```

### Branch Protection

**Required GitHub settings:**
- ✅ Require pull request before merging
- ✅ Require approval from code reviewer
- ✅ Require status checks to pass
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Require linear history (squash or rebase)
- ✅ Do not allow bypassing above settings
- ✅ Automatically delete head branches after merge

### Never Break Main

**Before merging to main:**
- ✅ All tests pass
- ✅ Code review approved
- ✅ CI checks green
- ✅ No merge conflicts
- ✅ Branch updated from latest main

**If main is broken:**
- 🚨 Drop everything and fix immediately
- 🚨 Either fix forward or revert
- 🚨 Communicate with team
- 🚨 Post-mortem to prevent recurrence

## Feature Branch Workflow

### Branch Lifetime: Short

**Ideal:** Same day (hours)
**Acceptable:** 1-3 days
**Maximum:** 1 week
**Too long:** 2+ weeks

**If branch is getting old:**
- Break into smaller pieces
- Merge what's complete
- Use feature flags for incomplete work
- Consider pair programming to finish faster

### Creating Feature Branch

```bash
# Always start from updated main
git checkout main
git pull origin main

# Create focused feature branch
git checkout -b feat/user-authentication

# Branch naming: type/short-description
# - feat/feature-name
# - fix/bug-description
# - refactor/what-refactored
```

### Working on Feature

**Make small, logical commits:**
```bash
# Don't wait until feature is "done"
git add src/auth/login.ts
git commit -m "feat(auth): add login component"

git add src/auth/validation.ts
git commit -m "feat(auth): add form validation"

git add tests/auth/login.test.ts
git commit -m "test(auth): add login component tests"
```

**Stay in sync with main:**
```bash
# Update from main frequently (at least daily)
git checkout main
git pull origin main
git checkout feat/user-authentication
git rebase main  # Keep history linear

# Resolve conflicts if any
# Test after rebase!
git push --force-with-lease origin feat/user-authentication
```

### Submitting for Review

```bash
# Ensure branch is updated
git rebase main

# Push to remote
git push -u origin feat/user-authentication

# Create PR immediately
# Don't wait until feature is "perfect"
```

### Review and Merge

**Quick review cycle:**
- Submit PR as soon as tests pass
- Review within hours, not days
- Address feedback quickly
- Merge as soon as approved

**Merge strategy:**
```bash
# Squash merge (recommended for most cases)
# - Combines commits into one
# - Clean main history
# - Loses detailed commit history

# Or rebase merge (if commits are clean)
# - Preserves individual commits
# - Linear history
# - Requires well-crafted commits
```

**After merge:**
```bash
# Delete feature branch immediately
git checkout main
git pull origin main
git branch -d feat/user-authentication

# Start next feature
git checkout -b feat/next-feature
```

## Small Changes Strategy

### Breaking Down Work

**Instead of:**
```
feat/complete-user-system (2 weeks)
├── Authentication
├── Authorization
├── User profiles
├── Settings
└── Admin panel
```

**Do:**
```
feat/user-auth-backend (1 day) → Merge
feat/user-auth-ui (1 day) → Merge
feat/user-profiles-api (1 day) → Merge
feat/user-profiles-ui (1 day) → Merge
feat/user-settings (1 day) → Merge
feat/admin-panel (2 days) → Merge
```

### Vertical Slicing

Build complete, thin features rather than horizontal layers:

**Bad (horizontal):**
```
PR 1: All database models
PR 2: All API endpoints
PR 3: All UI components
PR 4: Connect everything
```

**Good (vertical):**
```
PR 1: User login (model + API + UI + tests)
PR 2: User logout (model + API + UI + tests)
PR 3: User profile (model + API + UI + tests)
```

### Atomic Changes

Each PR should be:
- **Complete:** Feature works end-to-end
- **Tested:** Tests included and passing
- **Documented:** If needed
- **Reviewable:** Can be understood in 10-15 minutes
- **Revertable:** Can be safely reverted

## Feature Flags

### Why Feature Flags?

**Allow incomplete features in main:**
```javascript
if (featureFlags.isEnabled('new-search')) {
  return <NewSearchComponent />;
} else {
  return <OldSearchComponent />;
}
```

**Benefits:**
- Merge code before feature is complete
- Test in production with subset of users
- Quick rollback if issues found
- Gradual rollout
- A/B testing

### Simple Feature Flag Implementation

```javascript
// featureFlags.js
const flags = {
  'new-search': process.env.ENABLE_NEW_SEARCH === 'true',
  'redesigned-dashboard': false,
  'beta-features': isUserBeta(user),
};

export function isEnabled(flag) {
  return flags[flag] || false;
}
```

### Feature Flag Workflow

**1. Add feature flag:**
```javascript
feat(flags): add new-checkout-flow feature flag
```

**2. Implement behind flag:**
```javascript
feat(checkout): add new checkout flow (behind flag)

New checkout flow is implemented but disabled by default.
Enable with ENABLE_NEW_CHECKOUT=true environment variable.
```

**3. Test and refine:**
```javascript
fix(checkout): handle payment errors in new flow
refactor(checkout): simplify payment processing
```

**4. Enable for subset:**
```javascript
feat(flags): enable new checkout for beta users
```

**5. Enable for everyone:**
```javascript
feat(flags): enable new checkout for all users
```

**6. Remove flag and old code:**
```javascript
refactor(checkout): remove feature flag and old flow

New checkout has been stable for 2 weeks. Removing flag
and old implementation.
```

### Feature Flag Best Practices

**Do:**
- ✅ Remove flags once feature is stable
- ✅ Document what each flag controls
- ✅ Test both enabled and disabled states
- ✅ Use flags for incomplete work
- ✅ Use flags for risky changes

**Don't:**
- ❌ Leave flags indefinitely
- ❌ Create complex flag dependencies
- ❌ Use flags for permanent configuration
- ❌ Forget to remove old code after flag removal

## Continuous Integration

### CI Requirements for TBD

**Must have:**
- Automated tests on every commit
- Fast feedback (<10 minutes ideal)
- Main branch always tested
- Block merge if tests fail
- Test coverage reporting

**Should have:**
- Multiple test environments
- Performance testing
- Security scanning
- Code quality checks

### CI Workflow

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
      - uses: actions/checkout@v4

      - name: Setup
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run unit tests
        run: npm test

      - name: Run integration tests
        run: npm run test:integration

      - name: Check coverage
        run: npm run coverage

      - name: Build
        run: npm run build
```

### Pre-Merge Requirements

**All must be green before merge:**
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Linter passes
- ✅ Build succeeds
- ✅ Coverage meets threshold
- ✅ No security vulnerabilities

## Code Review in TBD

### Fast Review Cycle

**Goal:** Review within 2-4 hours, not days

**Why:**
- Reduces context switching
- Prevents branches from getting stale
- Maintains momentum
- Enables faster iteration

### Small PRs → Fast Reviews

**Good PR size:**
- 50-200 lines changed
- Single concern or feature
- Reviewable in 10-15 minutes
- Clear scope and purpose

**Too large:**
- 500+ lines changed
- Multiple unrelated changes
- Takes >30 minutes to review
- Hard to give quality feedback

### PR Review Checklist

**Functionality:**
- [ ] Does it work as intended?
- [ ] Are edge cases handled?
- [ ] Are errors handled properly?

**Code Quality:**
- [ ] Is code readable and maintainable?
- [ ] Are names clear and descriptive?
- [ ] Is there duplication that should be extracted?
- [ ] Are there commented-out code or TODOs?

**Testing:**
- [ ] Are there adequate tests?
- [ ] Do tests actually test the behavior?
- [ ] Are edge cases tested?

**Integration:**
- [ ] Is it consistent with existing code?
- [ ] Does it follow project conventions?
- [ ] Are breaking changes documented?

**Documentation:**
- [ ] Is public API documented?
- [ ] Are complex algorithms explained?
- [ ] Is README updated if needed?

### Review Response Time

**For reviewer:**
- Check for PRs at least 2-3 times per day
- Review small PRs immediately
- If can't review now, let author know when you will
- Block time for reviews

**For author:**
- Respond to feedback within hours
- Ask questions if feedback unclear
- Push updates promptly
- Re-request review after changes

## Team Size Considerations

### Small Team (2-5 developers)

**Simple workflow:**
```bash
# Create branch
git checkout -b feat/feature

# Make changes, commit frequently
git add .
git commit -m "feat: add feature"

# Update from main
git rebase main

# Push and create PR
git push -u origin feat/feature

# Quick review, merge
# Delete branch
```

**Characteristics:**
- Informal coordination
- Quick verbal sync
- Trust-based reviews
- Can move very fast

### Medium Team (6-20 developers)

**More structure needed:**
- Code ownership areas
- Designated reviewers per area
- More formal PR process
- Regular sync meetings
- Better branch protection

**Workflow additions:**
- Required CODEOWNERS file
- Two approvers for critical areas
- More comprehensive CI
- Deployment coordination

### Large Team (20+ developers)

**Rigorous process:**
- Strict code ownership
- Multiple review stages
- Extensive automated testing
- Release coordination
- Feature flag management

**May need:**
- Release branches (short-lived)
- Release train schedule
- More staging environments
- Advanced monitoring

## Common Pitfalls

### Long-Lived Branches

**Problem:**
```
feat/large-feature (3 weeks old, 200 commits behind main)
```

**Solution:**
- Break into smaller pieces
- Merge what's complete
- Use feature flags
- Rebase frequently

### Waiting for "Perfect"

**Problem:**
```
"I'll create PR when feature is 100% done"
(Week later: still not "done")
```

**Solution:**
- Create PR early
- Mark as draft if WIP
- Get early feedback
- Iterate in small steps

### Avoiding Main

**Problem:**
```
Multiple long-lived branches, rare merges to main
```

**Solution:**
- Merge to main daily
- If can't merge, use feature flag
- Keep main as active branch
- Resist creating staging branches

### Fear of Breaking Main

**Problem:**
```
"What if my code breaks production?"
```

**Solution:**
- Comprehensive CI/CD
- Feature flags for risk
- Good monitoring
- Quick revert process
- Blameless post-mortems

### Perfectionism in Reviews

**Problem:**
```
PR sits for days with nitpicky feedback
```

**Solution:**
- Distinguish blocking vs non-blocking feedback
- Accept "good enough" for minor issues
- Follow-up PRs for improvements
- Focus on functionality and major issues

## TBD vs Git Flow

### Git Flow

**Branches:**
```
main (production)
develop (integration)
feature/* (new features)
release/* (release preparation)
hotfix/* (emergency fixes)
```

**Characteristics:**
- Multiple long-lived branches
- Complex merging strategy
- Scheduled releases
- More overhead
- Better for: Fixed release schedules, less frequent releases

### Trunk-Based Development

**Branches:**
```
main (always deployable)
feat/* (short-lived features)
fix/* (short-lived fixes)
```

**Characteristics:**
- Single long-lived branch (main)
- Simple merging
- Continuous delivery
- Less overhead
- Better for: Frequent releases, continuous deployment

### Migration from Git Flow

**Step 1: Simplify branches**
```bash
# Merge develop into main
git checkout main
git merge develop
git push origin main

# Delete develop branch
git branch -d develop
git push origin --delete develop
```

**Step 2: Update workflow**
- Create feature branches from main (not develop)
- Merge feature branches to main (not develop)
- Delete feature branches immediately after merge

**Step 3: Add protections**
- Enable branch protection on main
- Require PRs and reviews
- Require CI to pass

**Step 4: Cultural shift**
- Small, frequent merges
- Feature flags for incomplete work
- Always keep main deployable

## Deployment Strategies

### Continuous Deployment

**Every merge to main deploys automatically:**
```yaml
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

**Requirements:**
- Excellent test coverage
- Monitoring and alerting
- Quick rollback capability
- Feature flags for WIP

### Continuous Delivery

**Main is always deployable, manual deploy:**
```bash
# Deploy latest main to production
git checkout main
git pull origin main
./deploy.sh production
```

**Benefits:**
- More control over timing
- Can batch multiple changes
- Time for final verification
- Still very frequent releases

### Scheduled Releases

**Deploy from main on schedule:**
```
Monday, Wednesday, Friday at 10 AM
```

**Process:**
```bash
# Tag release
git tag v1.2.3
git push origin v1.2.3

# Deploy tagged version
./deploy.sh v1.2.3
```

## Monitoring and Rollback

### Deploy with Monitoring

**Always monitor after deploy:**
- Error rates
- Response times
- User complaints
- Business metrics

**Automated checks:**
```bash
# Deploy
./deploy.sh

# Health check
curl https://api.example.com/health

# Wait and verify metrics
sleep 300
./check-error-rates.sh

# Rollback if issues
if [ $? -ne 0 ]; then
  ./rollback.sh
fi
```

### Quick Rollback

**Revert commit:**
```bash
# Identify problematic commit
git log --oneline -10

# Revert it
git revert abc123
git push origin main

# Auto-deploys revert
```

**Rollback to previous version:**
```bash
# Deploy previous tagged version
./deploy.sh v1.2.2
```

**Feature flag disable:**
```javascript
// Instant disable without code change
featureFlags.override('new-feature', false);
```

## Best Practices Summary

**Branch Management:**
- ✅ Keep feature branches short-lived (days, not weeks)
- ✅ Merge to main frequently
- ✅ Delete branches immediately after merge
- ✅ Rebase from main daily
- ✅ Always keep main deployable

**Change Management:**
- ✅ Make small, incremental changes
- ✅ Break large features into vertical slices
- ✅ Use feature flags for incomplete work
- ✅ Commit frequently
- ✅ Test before pushing

**Team Collaboration:**
- ✅ Review PRs within hours
- ✅ Communicate about conflicts
- ✅ Fix broken main immediately
- ✅ Share ownership of codebase
- ✅ Celebrate frequent integration

**Process:**
- ✅ Enforce branch protection
- ✅ Require PR reviews
- ✅ Require passing CI
- ✅ Deploy frequently
- ✅ Monitor after deploy

---

**Remember:** Trunk-Based Development is about confidence. Confidence to merge frequently comes from good tests, good reviews, feature flags, and team discipline. Start small, build confidence, and accelerate.
