# Backend Development Guardrails (B1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

1. Review the related route, service, schema, and model files before editing:
   - `src/routes/<area>.py`
   - `src/services/<area>_service.py`
   - `src/schemas/<area>.py`
   - `src/models/`
2. Keep all database access inside service classes. Use `commit_or_rollback()` helpers; do not manage the session directly in route handlers.
3. Maintain response shapes expected by the frontend. Update serialization helpers (e.g., `to_dict()`) and coordinate schema changes with `frontend/src/services/api.js`.
4. Add or update tests under `tests/routes/` and `tests/services/` to cover new logic. Run:

   ```powershell
   python -m pytest tests/routes tests/services
   python -m pytest tests/test_dependency_validator_import.py
   ```

5. Generate Alembic migrations for schema adjustments with `flask --app src.main db migrate` and `flask --app src.main db upgrade --sql`, then update fixtures.
6. Document notable behavior changes in `dev_log.md` and, if applicable, update API docs or `docs/api/` references.
