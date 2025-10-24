# Testing Scripts

This directory contains automated testing and validation scripts for the Landscape Architecture Tool.

## 📚 Essential Documentation

Before using testing scripts, review these comprehensive guides:

- **[DEVELOPMENT_GUIDE.md](../../docs/DEVELOPMENT_GUIDE.md)** - Test-Driven Development (TDD) workflow (Section 4)
- **[DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md)** - Systematic debugging and test troubleshooting
- **[.github/copilot-instructions/testing.md](../../.github/copilot-instructions/testing.md)** - Testing guardrails

## Best Practices

All testing scripts follow these principles from the engineering velocity framework:

### 1. Test-Driven Development (TDD)

From [DEVELOPMENT_GUIDE.md - TDD](../../docs/DEVELOPMENT_GUIDE.md#test-driven-development-tdd):

1. **Write failing test** that defines expected behavior
2. **Run test** to confirm it fails
3. **Write minimal code** to make test pass
4. **Refactor** while keeping tests green
5. **Commit** test and code together

### 2. Automated Quality Gates

From [DEVELOPMENT_GUIDE.md - Code Quality](../../docs/DEVELOPMENT_GUIDE.md#4-proactive-code-quality--automation):

- Pre-commit hooks (Black, Ruff, isort, Bandit)
- CI/CD pipeline validation
- Code coverage tracking (target: 80%+)

### 3. Systematic Test Debugging

From [DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md#debugging-test-failures):

When tests fail, follow the 5-step process:
1. **Identify**: What test failed and why?
2. **Reproduce**: Can you run it in isolation?
3. **Isolate**: Check fixtures, database state, test isolation
4. **Fix**: Make minimal changes
5. **Verify**: Run full test suite to ensure no regressions

## Available Scripts

### `automated_validation.py`
Comprehensive validation after code changes.

**Usage**:
```bash
python scripts/testing/automated_validation.py [--quick] [--full]
```

**Features**:
- Linting (Black, Ruff, isort)
- Backend tests (pytest)
- Frontend tests (vitest)
- Security scanning (Bandit, Safety)
- Code coverage reporting

### `quality_gates.py`
Enforces quality standards before merging.

**Usage**:
```bash
python scripts/testing/quality_gates.py
```

**Checks**:
- Code formatting compliance
- Test coverage thresholds
- Linting errors
- Security vulnerabilities

### `comprehensive_api_test.py`
Tests all API endpoints.

**Usage**:
```bash
python scripts/testing/comprehensive_api_test.py
```

**Features**:
- Tests all REST endpoints
- Validates request/response formats
- Checks status codes
- Verifies data validation

### `validate_after_merge.sh`
Post-merge validation to ensure stability.

**Usage**:
```bash
./scripts/testing/validate_after_merge.sh
```

**Checks**:
- All tests pass
- No merge conflicts
- Build succeeds
- Services start correctly

## Testing Workflow

### For New Features

Follow [DEVELOPMENT_GUIDE.md - TDD](../../docs/DEVELOPMENT_GUIDE.md#test-driven-development-tdd):

```bash
# 1. Write failing test
# Add test in tests/ directory

# 2. Run test to confirm it fails
make backend-test

# 3. Implement feature
# Write minimal code to pass test

# 4. Run tests again
make backend-test

# 5. Commit test and code together
git add tests/ src/
git commit -m "feat(area): add feature with tests"
```

### For Bug Fixes

From [DEBUGGING_GUIDE.md - Fix and Verify](../../docs/DEBUGGING_GUIDE.md#step-4-fix-the-issue):

```bash
# 1. Write test that reproduces bug (should fail)
# Add regression test in tests/

# 2. Run test to confirm it fails
pytest tests/test_bug_reproduction.py

# 3. Fix the bug
# Make minimal changes to fix

# 4. Verify test passes
pytest tests/test_bug_reproduction.py

# 5. Run full suite
make test

# 6. Commit together
git add tests/ src/
git commit -m "fix(area): fix bug description

Fixes #123. Added regression test."
```

## Debugging Test Failures

When tests fail, use the systematic approach from [DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md):

### Backend Test Failures

```bash
# Run specific test with verbose output
pytest tests/test_file.py::test_function -v

# Check for test isolation issues
pytest tests/test_file.py::test_function --lf

# Run in Docker to match CI
docker-compose run backend pytest tests/
```

### Frontend Test Failures

```bash
# Run specific test
cd frontend && npm run test -- --run test_file.spec.js

# Run with coverage
npm run test:coverage

# Check browser console for errors
npm run dev
# Open browser DevTools
```

### Common Issues

See [DEBUGGING_GUIDE.md - Common Issues](../../docs/DEBUGGING_GUIDE.md#common-issues--solutions):

| Issue | Solution |
|-------|----------|
| Tests pass locally, fail in CI | Run in Docker: `docker-compose run backend pytest` |
| Database locked | Check for uncommitted transactions |
| Flaky tests | Review test isolation, add retries for external dependencies |
| Import errors | Check PYTHONPATH: `export PYTHONPATH=.` |

## Pre-commit Validation

From [DEVELOPMENT_GUIDE.md - Pre-commit](../../docs/DEVELOPMENT_GUIDE.md#pre-commit-hooks):

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks automatically run:
- Black (formatting)
- Ruff (linting)
- isort (import sorting)
- Bandit (security scanning)

## CI/CD Integration

All testing scripts are integrated with CI/CD. See [DEVELOPMENT_GUIDE.md - CI/CD](../../docs/DEVELOPMENT_GUIDE.md#cicd-pipeline).

Every PR triggers:
- Code quality checks
- Backend tests
- Frontend tests
- Security scanning
- Build verification

## Additional Resources

- **Backend Testing**: [.github/copilot-instructions/backend.md](../../.github/copilot-instructions/backend.md)
- **Frontend Testing**: [.github/copilot-instructions/frontend.md](../../.github/copilot-instructions/frontend.md)
- **Test Coverage**: Run `make test` and check `htmlcov/index.html`
- **Debugging Guide**: [DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md)
