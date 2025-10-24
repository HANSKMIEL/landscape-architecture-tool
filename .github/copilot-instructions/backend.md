# Backend Development Guardrails (B1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

## Core Best Practices
**Follow the comprehensive framework:**
- **Architecture**: [DEVELOPMENT_GUIDE.md - Section 3](../../docs/DEVELOPMENT_GUIDE.md#3-architecture-for-maintainability) - SOLID principles, service layer pattern
- **API Design**: [API_DOCUMENTATION.md](../../docs/API_DOCUMENTATION.md) and [DEVELOPMENT_GUIDE.md - RESTful API](../../docs/DEVELOPMENT_GUIDE.md#restful-api-design)
- **Debugging**: [DEBUGGING_GUIDE.md - Backend](../../docs/DEBUGGING_GUIDE.md#backend-debugging) - Systematic troubleshooting

## Development Workflow

1. **Review existing code** before editing:
   - `src/routes/<area>.py`
   - `src/services/<area>_service.py`
   - `src/schemas/<area>.py`
   - `src/models/`

2. **Follow Service Layer Pattern**: Keep all database access inside service classes. Use `commit_or_rollback()` helpers; do not manage the session directly in route handlers. See [DEVELOPMENT_GUIDE.md - SRP](../../docs/DEVELOPMENT_GUIDE.md#single-responsibility-principle-srp).

3. **Maintain API Contracts**: Maintain response shapes expected by the frontend. Update serialization helpers (e.g., `to_dict()`) and coordinate schema changes with `frontend/src/services/api.js`. Document in [API_DOCUMENTATION.md](../../docs/API_DOCUMENTATION.md).

4. **Test-Driven Development**: Add or update tests under `tests/routes/` and `tests/services/` to cover new logic. Write failing test first - see [DEVELOPMENT_GUIDE.md - TDD](../../docs/DEVELOPMENT_GUIDE.md#test-driven-development-tdd). Run:

   ```powershell
   python -m pytest tests/routes tests/services
   python -m pytest tests/test_dependency_validator_import.py
   ```

5. **Database Migrations**: Generate Alembic migrations for schema adjustments with `flask --app src.main db migrate` and `flask --app src.main db upgrade --sql`, then update fixtures.

6. **Documentation**: 
   - Document new/modified endpoints in `docs/API_DOCUMENTATION.md`
   - Note behavior changes in `dev_log.md`
   - Update `docs/api/` references if applicable

## RESTful API Standards
Follow conventions from [API_DOCUMENTATION.md](../../docs/API_DOCUMENTATION.md):
- **Resource-oriented URIs**: `/suppliers`, `/plants/{id}`
- **HTTP methods**: GET (retrieve), POST (create), PUT (update), DELETE (remove)
- **Status codes**: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 422 Validation Error, 500 Server Error
- **Response format**: Consistent JSON structure with `status`, `data`, `meta`

## Debugging Backend Issues
Use the systematic 5-step process from [DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md#the-5-step-debugging-process):
1. Identify - Define expected vs actual behavior
2. Reproduce - Create minimal test case
3. Isolate - Use logging and breakpoints
4. Fix - Make minimal targeted changes
5. Verify - Test and write regression test
