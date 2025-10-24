# Landscape Architecture Tool – Copilot Guide
## Branch & deployment guardrails
- **Primary development branch**: `main` (formerly `V1.00D` before October 2025 migration)
- **Archive branch**: `Archive-main` (historical production state, archived)
- Work on `main` branch for all development; it auto-deploys to http://72.60.176.200:8080
- No Docker builds locally (Dockerfile currently broken)
- The old promotion script (`scripts/deployment/promote_v1d_to_v1.sh`) is deprecated post-migration
## System architecture
- Backend: Flask app in `src/main.py` with blueprints under `src/routes/`, SQLAlchemy models in `src/models/`, services in `src/services/`, schemas in `src/schemas/`.
- Frontend: React/Vite in `frontend/`, API layer at `frontend/src/services/api.js`, components under `frontend/src/components/`.
- N8n automations live in `n8n-workflows/`; backend triggers them via `requests.post` calls in utility helpers.
- Config files: `config/wsgi.py`, `config/gunicorn.conf.py`, `.env.example` for required variables.
## Coding patterns
- Services wrap DB work; always commit/rollback inside service methods (see `src/services/base_service.py`).
- Route handlers validate with schemas, call services, and log failures; mirror `src/routes/suppliers.py` when adding endpoints.
- Tests rely on SAVEPOINT transactions; follow `tests/conftest.py` when writing DB tests (`conn.begin_nested()` if already in txn).
- When seeding data or migrations, use Alembic under `migrations/` and run via `flask --app src.main db ...`.
## Build & validation workflow
- Fresh setup: `make install` → `make build` (runs frontend + backend builds).
- Fast checks: `make backend-test` (~50s; expect ~5 known plant route failures) and `make lint`.
- Frontend tests: `cd frontend` then `npm run test:vitest:run` (~8s; two known flaky tests).
- Never cancel long commands; backend tests timeout at 120s, frontend build at 180s.
- For manual smoke: start backend with `PYTHONPATH=. python src/main.py`, frontend via `npm run dev`, hit `/health` and dashboard.
## Tooling & scripts
- Deployment helpers live in `scripts/deployment/`; use `scripts/deploy_helper.sh` for VPS interactions when needed.
- Quality sweeps: `python scripts/copilot_workflow.py --all` aggregates lint/tests/security; store generated reports under `reports/`.
- Pre-commit hooks (Black, Ruff, isort) are configured; run `pre-commit run --all-files` before large commits.
## Documentation hotspots
- Architecture overviews in `docs/architecture/` and operational runbooks in `docs/VPS_*.md`.
- Validation reports and diagnostics live under `reports/`; check latest for context on known issues.
## Expectations for contributions
- Respect existing response shapes (`to_dict()` on models) and localized UI strings.
- Update or add minimal tests alongside backend changes; document new commands in `docs/` if non-obvious.
