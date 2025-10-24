# Testing & Quality Guardrails (T1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

1. Treat `tests/conftest.py` as canonical for database transaction handling—use savepoints and provided fixtures to avoid leakage.
2. Prefer parametrized pytest cases and shared factories when adding coverage to reduce duplication.
3. Run the project-wide quality gates after meaningful backend work:

   ```powershell
   make backend-test
   make lint
   ```

4. For frontend changes, add:

   ```powershell
   cd frontend
   npm run test:run
   ```

5. Capture flaky test behavior in `dev_log.md` and open follow-up issues when instability persists.
