# Branching Strategy and Workflow

## Overview

This document clarifies the branching strategy for the Landscape Architecture Tool, addressing concerns from the "Framework for Engineering Velocity" document about ad-hoc development processes.

## Current Branch Structure

### Branch Hierarchy

```
main (protected)
  ↑
  │ Promotion via script
  │
V1.00D (active development)
  ↑
  │ Pull requests
  │
Feature branches (temporary)
  feat/*, fix/*, chore/*
```

### Branch Purposes

#### 1. `main` Branch
- **Status**: Protected, production-ready
- **Purpose**: Stable production code deployed to https://optura.nl
- **Protection Rules**:
  - No direct pushes
  - Requires pull request reviews
  - All CI checks must pass
  - Deployed automatically on updates
  
**Access**:
```bash
# View main branch
git checkout main
git pull origin main

# ⚠️ Never commit directly to main!
```

#### 2. `V1.00D` Branch
- **Status**: Active development branch
- **Purpose**: Integration point for all feature development
- **Deployment**: Auto-deploys to http://72.60.176.200:8080 (DevDeploy)
- **Workflow**: Receives features via pull requests

**Development workflow**:
```bash
# Start work from V1.00D
git checkout V1.00D
git pull origin V1.00D

# Create feature branch
git checkout -b feat/new-feature
```

#### 3. Feature Branches
- **Status**: Temporary, short-lived
- **Purpose**: Isolated development of specific features/fixes
- **Lifetime**: Created → Developed → Merged → Deleted
- **Naming Convention**:
  - `feat/feature-name` - New features
  - `fix/bug-name` - Bug fixes
  - `chore/task-name` - Maintenance tasks
  - `docs/topic` - Documentation updates

**Example**:
```bash
# Create feature branch
git checkout -b feat/supplier-search

# Work on feature
git add .
git commit -m "feat(suppliers): add search functionality"

# Push and create PR
git push origin feat/supplier-search
# Create PR on GitHub: feat/supplier-search → V1.00D

# After merge, delete branch
git branch -d feat/supplier-search
```

## Rationale: Why This Structure?

### Addressing the Document's Concerns

The "Framework for Engineering Velocity" document states:

> "The name of the active development branch, V1.00D, is itself a diagnostic indicator, suggesting an ad-hoc, reactive development process"

### Our Justification

While the document recommends simple **GitHub Flow** (main + feature branches), our structure includes an additional development branch (`V1.00D`) for specific business reasons:

#### 1. Production Stability Requirements
- **main** must be production-ready at all times
- Direct deployments to production (https://optura.nl) require extra safety
- `V1.00D` provides an integration/testing layer before production

#### 2. Dual Environment Strategy
- **DevDeploy** (V1.00D): Rapid testing environment
- **Production** (main): Stable, customer-facing environment
- This separation allows aggressive development without production risk

#### 3. Version Management
- `V1.00` represents a stable release line
- `V1.00D` ("Development") indicates active work on this version
- Future: `V2.00D` could be developed in parallel

### Comparison to Standard Models

| Model | Branches | Our Structure |
|-------|----------|---------------|
| **GitHub Flow** | main + features | ✓ We follow this for features |
| **GitFlow** | main + develop + release + hotfix | Partially - we simplified it |
| **Trunk-Based** | Single main | ✗ Too risky for our deployment needs |

**Our model**: **GitHub Flow with Integration Branch**

## Detailed Workflows

### 1. Feature Development Workflow

```bash
# Day 1: Start feature
git checkout V1.00D
git pull origin V1.00D
git checkout -b feat/supplier-filtering

# Day 1-3: Develop
git add src/routes/suppliers.py
git commit -m "feat(suppliers): add filtering endpoint"

git add frontend/src/components/SupplierFilter.jsx
git commit -m "feat(suppliers): add filter UI component"

git add tests/test_supplier_filtering.py
git commit -m "test(suppliers): add filtering tests"

# Day 3: Push and create PR
git push origin feat/supplier-filtering

# On GitHub:
# 1. Create Pull Request: feat/supplier-filtering → V1.00D
# 2. Add description, link issues
# 3. Wait for CI checks
# 4. Request review (if team member available)

# Day 4: After approval and merge
git checkout V1.00D
git pull origin V1.00D
git branch -d feat/supplier-filtering

# Feature is now on DevDeploy (http://72.60.176.200:8080)
```

### 2. Bug Fix Workflow

```bash
# User reports bug in production
git checkout V1.00D
git pull origin V1.00D

# Create fix branch
git checkout -b fix/supplier-email-validation

# Write failing test first (TDD)
# tests/test_suppliers.py
def test_invalid_email_returns_422():
    response = client.post('/api/suppliers', json={
        'email': 'not-an-email'
    })
    assert response.status_code == 422

# Run test - it fails
pytest tests/test_suppliers.py::test_invalid_email_returns_422

# Fix the code
# src/schemas/supplier.py
email = fields.Email(required=True)  # Add validation

# Run test - it passes
pytest tests/test_suppliers.py::test_invalid_email_returns_422

# Commit and push
git add .
git commit -m "fix(suppliers): validate email format

Fixes #123. Email field now validates format before database insert."
git push origin fix/supplier-email-validation

# Create PR → V1.00D
# After merge, delete branch
```

### 3. Promotion to Production

When V1.00D is stable and tested:

```bash
# Run promotion script
./scripts/deployment/promote_v1d_to_v1.sh

# This script:
# 1. Creates backup of current main
# 2. Runs full test suite
# 3. Merges V1.00D into main
# 4. Tags the release
# 5. Pushes to main (triggers production deployment)
```

**Promotion Checklist**:
- [ ] All features tested on DevDeploy
- [ ] All CI checks passing
- [ ] No known critical bugs
- [ ] Stakeholder approval
- [ ] Database migrations tested
- [ ] Backup verified

## Best Practices

### 1. Keep Feature Branches Short-Lived

**Good** (2-3 days):
```bash
feat/add-supplier-search
- Day 1: Backend endpoint
- Day 2: Frontend UI
- Day 3: Tests and merge
```

**Bad** (weeks):
```bash
feat/complete-supplier-redesign
- Weeks of changes
- Massive divergence from V1.00D
- High merge conflict risk
```

**Principle**: *"The lifetime of a branch is inversely proportional to the health of a project"*

### 2. Commit Frequently

```bash
# ✅ Good: Frequent, focused commits
git commit -m "feat(suppliers): add search endpoint"
git commit -m "feat(suppliers): add search validation"
git commit -m "feat(suppliers): add search tests"
git commit -m "feat(suppliers): add search UI"

# ❌ Bad: Infrequent, large commits
git commit -m "Add supplier search (backend, frontend, tests, docs)"
```

### 3. Write Descriptive Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style (formatting, no logic change)
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance tasks
- `perf` - Performance improvements
- `ci` - CI/CD changes

**Examples**:
```bash
feat(api): add supplier search endpoint

Implements full-text search across supplier name, specialty, and location.
Supports pagination and sorting.

Closes #145

---

fix(suppliers): prevent duplicate email addresses

Database constraint was not catching duplicates. Added unique constraint
and proper error handling to return 409 Conflict.

Fixes #234

---

docs(readme): update installation instructions

Added Docker setup steps and troubleshooting section.
```

### 4. Create Meaningful Pull Requests

**PR Title**:
```
feat(suppliers): Add advanced search and filtering
```

**PR Description Template**:
```markdown
## Description
Implements advanced search and filtering for suppliers page.

## Changes
- Added search endpoint with full-text support
- Implemented filter by specialty, location, country
- Added pagination support (20 items per page)
- Created frontend search UI component
- Added comprehensive tests

## Testing
- [ ] Backend tests pass (pytest)
- [ ] Frontend tests pass (vitest)
- [ ] Manual testing on DevDeploy
- [ ] Edge cases tested (empty results, special characters)

## Screenshots
[Attach UI screenshots if applicable]

## Related Issues
Closes #145
Related to #132

## Deployment Notes
No database migrations required. No breaking changes.
```

### 5. Review Your Own PRs

Even as a solo developer, use PRs as a final review checkpoint:

1. **Create PR** on GitHub
2. **Review the diff** in GitHub's UI
   - Look for debugging code left in
   - Check for TODO comments
   - Verify no secrets committed
   - Review test coverage
3. **Run final checks**
   ```bash
   make lint
   make test
   ```
4. **Merge** after approval

## Handling Special Cases

### Emergency Hotfixes

For critical production bugs:

```bash
# Option 1: Fast-track through V1.00D (preferred)
git checkout V1.00D
git checkout -b fix/critical-security-issue
# Fix, test, PR, merge
./scripts/deployment/promote_v1d_to_v1.sh

# Option 2: Direct to main (rare, emergency only)
# Requires manual override of branch protection
git checkout main
git checkout -b hotfix/critical-security-issue
# Fix, test, PR with override approval
# After merge to main, backport to V1.00D
```

### Long-Running Features

For features taking more than a week:

```bash
# Create feature branch
git checkout -b feat/complex-reporting-system

# Break into smaller PRs
git checkout -b feat/reporting-data-model
# Implement data model
# PR → V1.00D → Merge

git checkout feat/complex-reporting-system
git merge V1.00D

git checkout -b feat/reporting-api
# Implement API
# PR → V1.00D → Merge

git checkout feat/complex-reporting-system
git merge V1.00D

# Continue incrementally
```

**Alternative**: Use feature flags to merge frequently while keeping feature hidden:

```python
# Backend
if current_app.config.get('FEATURE_REPORTING'):
    # Reporting code
    
# Frontend
{import.meta.env.VITE_FEATURE_REPORTING && (
  <ReportingDashboard />
)}
```

### Parallel Development

Multiple developers or multiple features in parallel:

```bash
# Developer A
git checkout -b feat/supplier-import

# Developer B
git checkout -b feat/supplier-export

# Both work independently
# Both create PRs to V1.00D
# Merge conflicts resolved during PR review
```

## Migration from Current State

If starting fresh or cleaning up existing branches:

```bash
# 1. Ensure main is protected
# (Configure in GitHub repository settings)

# 2. Ensure V1.00D is the development branch
git checkout V1.00D
git pull origin V1.00D

# 3. Delete stale feature branches
git branch -d old-feature-branch
git push origin --delete old-feature-branch

# 4. Document workflow for team
# (This document serves that purpose)

# 5. Configure CI/CD
# - V1.00D pushes → Deploy to DevDeploy
# - main pushes → Deploy to Production
# - All PRs → Run full test suite
```

## Comparison to GitHub Flow

Our workflow is **GitHub Flow with an integration branch**:

| Aspect | GitHub Flow | Our Workflow |
|--------|-------------|---------------|
| Main branch | Always deployable | Always deployable |
| Feature branches | Yes | Yes |
| Long-lived dev branch | No | Yes (V1.00D) |
| Deployment | Every merge to main | V1.00D → DevDeploy, main → Production |
| Complexity | Low | Low-Medium |
| Safety | Medium | High (extra testing layer) |

**Trade-offs**:
- **Pro**: Extra testing environment before production
- **Pro**: Ability to batch multiple features before production release
- **Con**: Extra step (V1.00D → main promotion)
- **Con**: Slightly more complex than pure GitHub Flow

**Justification**: For a solo developer or small team managing a production system with customers, the extra safety of V1.00D is worth the slight complexity increase.

## Tools and Automation

### Branch Protection Rules

Configure in GitHub repository settings:

**For `main`**:
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require linear history
- ✅ No direct pushes
- ✅ No force pushes
- ✅ Require signed commits (optional)

**For `V1.00D`**:
- ✅ Require status checks to pass
- ✅ Allow direct pushes (for quick fixes)
- ✅ No force pushes

### CI/CD Integration

```.github/workflows/ci-enhanced.yml
# V1.00D push → Run tests + Deploy to DevDeploy
on:
  push:
    branches: [V1.00D]

# main push → Run tests + Deploy to Production
on:
  push:
    branches: [main]

# All PRs → Run full test suite
on:
  pull_request:
    branches: [V1.00D, main]
```

### Git Aliases

Add helpful aliases to `.gitconfig`:

```bash
git config --global alias.feature '!f() { git checkout V1.00D && git pull && git checkout -b feat/$1; }; f'
git config --global alias.fix '!f() { git checkout V1.00D && git pull && git checkout -b fix/$1; }; f'
git config --global alias.cleanup '!git branch --merged | grep -v "\\*\\|main\\|V1.00D" | xargs -r git branch -d'

# Usage:
git feature supplier-search  # Creates feat/supplier-search from V1.00D
git fix email-validation     # Creates fix/email-validation from V1.00D
git cleanup                  # Deletes merged feature branches
```

## Troubleshooting

### Problem: Merge Conflicts

```bash
# When PR has conflicts with V1.00D
git checkout feat/my-feature
git fetch origin
git merge origin/V1.00D

# Resolve conflicts
# Edit files, remove conflict markers

git add .
git commit -m "Merge V1.00D into feat/my-feature"
git push origin feat/my-feature
```

### Problem: Accidentally Committed to Wrong Branch

```bash
# Committed to V1.00D instead of feature branch
git log -1  # Note the commit SHA

git reset --hard HEAD~1  # Undo commit on V1.00D
git checkout -b feat/my-feature  # Create correct branch
git cherry-pick <commit-sha>  # Apply commit to feature branch
```

### Problem: Need to Update Feature Branch with Latest V1.00D

```bash
git checkout feat/my-feature
git merge origin/V1.00D
# or
git rebase origin/V1.00D  # Cleaner history, but more complex
```

## References

- [GitHub Flow Documentation](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Git Branching Strategies](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Project contribution guidelines

## Summary

**Key Principles**:
1. **main is sacred** - Always production-ready
2. **V1.00D is integration** - Where features come together
3. **Feature branches are temporary** - Create, develop, merge, delete
4. **Commits are frequent** - Small, focused changes
5. **PRs are mandatory** - Even for solo development

**Daily Workflow**:
```bash
git checkout V1.00D
git pull
git checkout -b feat/task-name
# Work
git commit -m "feat: description"
git push
# Create PR
# Merge
git checkout V1.00D
git pull
git branch -d feat/task-name
```

This branching strategy balances the simplicity advocated by the "Framework for Engineering Velocity" document with the practical needs of managing a production system with separate development and production environments.
