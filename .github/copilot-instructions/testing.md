# Testing & Quality Guardrails (T1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

## Testing Best Practices
**Follow the comprehensive framework:**
- **TDD Workflow**: [DEVELOPMENT_GUIDE.md - TDD](../../docs/DEVELOPMENT_GUIDE.md#test-driven-development-tdd) - Write failing test first
- **Code Quality**: [DEVELOPMENT_GUIDE.md - Section 4](../../docs/DEVELOPMENT_GUIDE.md#4-proactive-code-quality--automation)
- **Debugging Tests**: [DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md#backend-debugging) - Systematic test debugging

## Test Development Workflow

1. **Database Transaction Handling**: Treat `tests/conftest.py` as canonical for database transaction handling—use savepoints and provided fixtures to avoid leakage.

2. **Test Structure**: Prefer parametrized pytest cases and shared factories when adding coverage to reduce duplication.

3. **Run Quality Gates**: Run the project-wide quality gates after meaningful backend work:

   ```powershell
   make backend-test
   make lint
   ```

4. **Frontend Testing**: For frontend changes, add:

   ```powershell
   cd frontend
   npm run test:run
   ```

5. **Test-Driven Development (TDD)**:
   - Write failing test that reproduces expected behavior or bug
   - Implement minimum code to pass the test
   - Refactor while keeping tests green
   - See [DEVELOPMENT_GUIDE.md - TDD Example](../../docs/DEVELOPMENT_GUIDE.md#test-driven-development-tdd)

6. **Test Coverage**: Target 80%+ coverage for new code. Run with coverage reporting enabled.

7. **Flaky Tests**: Capture flaky test behavior in `dev_log.md` and open follow-up issues when instability persists.

## Pre-commit and CI/CD
- **Pre-commit Hooks**: Run automatically (Black, Ruff, isort, Bandit). See [DEVELOPMENT_GUIDE.md - Pre-commit](../../docs/DEVELOPMENT_GUIDE.md#pre-commit-hooks).
- **CI/CD Pipeline**: All PRs trigger automated testing. See [DEVELOPMENT_GUIDE.md - CI/CD](../../docs/DEVELOPMENT_GUIDE.md#cicd-pipeline).

## Debugging Test Failures
Follow [DEBUGGING_GUIDE.md - 5-Step Process](../../docs/DEBUGGING_GUIDE.md#the-5-step-debugging-process):
- Identify: What test is failing and why?
- Reproduce: Can you run it in isolation?
- Isolate: Check fixtures, database state, test isolation
- Fix: Make minimal changes
- Verify: Run full test suite to ensure no regressions
