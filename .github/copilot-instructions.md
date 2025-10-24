# Landscape Architecture Tool – Copilot Guide

## 📚 Essential Documentation (Read First)
**Start here for comprehensive best practices:**
- **[DEVELOPMENT_GUIDE.md](../docs/DEVELOPMENT_GUIDE.md)** - Complete framework covering all 5 pillars of engineering velocity
- **[BRANCHING_STRATEGY.md](../docs/BRANCHING_STRATEGY.md)** - Git workflow and V1.00D approach explained
- **[API_DOCUMENTATION.md](../docs/API_DOCUMENTATION.md)** - Full REST API reference
- **[DEBUGGING_GUIDE.md](../docs/DEBUGGING_GUIDE.md)** - Systematic 5-step debugging process

## Branch & deployment guardrails
- Work exclusively on `V1.00D`; `main` is production-only and promoted via `scripts/deployment/promote_v1d_to_v1.sh`.
- **Branching Strategy**: Follow [BRANCHING_STRATEGY.md](../docs/BRANCHING_STRATEGY.md) for feature/fix/chore branch patterns
- **Feature branches**: Use `feat/*`, `fix/*`, `chore/*` naming convention
- **Pull Requests**: Required for all merges to V1.00D; see [BRANCHING_STRATEGY.md](../docs/BRANCHING_STRATEGY.md#pull-request-guidelines)
- Dev pushes auto-deploy to http://72.60.176.200:8080; no Docker builds locally (Dockerfile currently broken).

## System architecture
- **Architecture Overview**: See [DEVELOPMENT_GUIDE.md - Section 3](../docs/DEVELOPMENT_GUIDE.md#3-architecture-for-maintainability)
- Backend: Flask app in `src/main.py` with blueprints under `src/routes/`, SQLAlchemy models in `src/models/`, services in `src/services/`, schemas in `src/schemas/`.
- Frontend: React/Vite in `frontend/`, API layer at `frontend/src/services/api.js`, components under `frontend/src/components/`.
- **SOLID Principles**: All code follows SOLID principles - see [DEVELOPMENT_GUIDE.md](../docs/DEVELOPMENT_GUIDE.md#solid-principles-implementation)
- N8n automations live in `n8n-workflows/`; backend triggers them via `requests.post` calls in utility helpers.
- Config files: `config/wsgi.py`, `config/gunicorn.conf.py`, `.env.example` for required variables.

## Coding patterns
- **Service Layer Pattern**: Services wrap DB work; always commit/rollback inside service methods (see `src/services/base_service.py`).
- **RESTful API Design**: Follow conventions in [API_DOCUMENTATION.md](../docs/API_DOCUMENTATION.md) and [DEVELOPMENT_GUIDE.md - RESTful API](../docs/DEVELOPMENT_GUIDE.md#restful-api-design)
- Route handlers validate with schemas, call services, and log failures; mirror `src/routes/suppliers.py` when adding endpoints.
- Tests rely on SAVEPOINT transactions; follow `tests/conftest.py` when writing DB tests (`conn.begin_nested()` if already in txn).
- When seeding data or migrations, use Alembic under `migrations/` and run via `flask --app src.main db ...`.

## Build & validation workflow
- **Environment Setup**: See [DEVELOPMENT_GUIDE.md - Section 1](../docs/DEVELOPMENT_GUIDE.md#1-bulletproof-development-environment)
- Fresh setup: `make install` → `make build` (runs frontend + backend builds).
- Fast checks: `make backend-test` (~50s; expect ~5 known plant route failures) and `make lint`.
- Frontend tests: `cd frontend` then `npm run test:vitest:run` (~8s; two known flaky tests).
- **TDD Workflow**: Write failing test first - see [DEVELOPMENT_GUIDE.md - TDD](../docs/DEVELOPMENT_GUIDE.md#test-driven-development-tdd)
- Never cancel long commands; backend tests timeout at 120s, frontend build at 180s.
- For manual smoke: start backend with `PYTHONPATH=. python src/main.py`, frontend via `npm run dev`, hit `/health` and dashboard.

## Debugging
- **Follow Systematic Process**: Use the 5-step framework in [DEBUGGING_GUIDE.md](../docs/DEBUGGING_GUIDE.md#the-5-step-debugging-process)
  1. Identify the Problem
  2. Reproduce Consistently
  3. Isolate the Root Cause
  4. Fix the Issue
  5. Verify the Fix
- **Common Issues**: Check [DEBUGGING_GUIDE.md - Common Issues](../docs/DEBUGGING_GUIDE.md#common-issues--solutions) first
- **Tools Reference**: See [DEBUGGING_GUIDE.md - Tools](../docs/DEBUGGING_GUIDE.md#debugging-tools-reference)

## Tooling & scripts
- Deployment helpers live in `scripts/deployment/`; use `scripts/deploy_helper.sh` for VPS interactions when needed.
- Quality sweeps: `python scripts/copilot_workflow.py --all` aggregates lint/tests/security; store generated reports under `reports/`.
- **Pre-commit Hooks**: Configured for Black, Ruff, isort, Bandit - see [DEVELOPMENT_GUIDE.md - Pre-commit](../docs/DEVELOPMENT_GUIDE.md#pre-commit-hooks)
- Run `pre-commit run --all-files` before large commits.

## Documentation hotspots
- **Core Guides**: `docs/DEVELOPMENT_GUIDE.md`, `docs/API_DOCUMENTATION.md`, `docs/DEBUGGING_GUIDE.md`, `docs/BRANCHING_STRATEGY.md`
- Architecture overviews in `docs/architecture/` and operational runbooks in `docs/VPS_*.md`.
- Validation reports and diagnostics live under `reports/`; check latest for context on known issues.
- **Best Practices**: See [BEST_PRACTICES_OVERVIEW.md](../docs/BEST_PRACTICES_OVERVIEW.md) for framework adherence

## Expectations for contributions
- **Follow SOLID Principles**: See [DEVELOPMENT_GUIDE.md - SOLID](../docs/DEVELOPMENT_GUIDE.md#solid-principles-implementation)
- **Conventional Commits**: Use `feat:`, `fix:`, `docs:`, etc. - see [BRANCHING_STRATEGY.md - Commits](../docs/BRANCHING_STRATEGY.md#commit-message-convention)
- Respect existing response shapes (`to_dict()` on models) and localized UI strings.
- Update or add minimal tests alongside backend changes; document new commands in `docs/` if non-obvious.
- **API Changes**: Update [API_DOCUMENTATION.md](../docs/API_DOCUMENTATION.md) when adding/modifying endpoints
