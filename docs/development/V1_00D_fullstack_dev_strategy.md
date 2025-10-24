# V1.00D Full-Stack Development Strategy

> **⚠️ Branch Migration Notice (October 2025)**
> 
> As of October 2025, the V1.00D branch has been renamed to `main`. All references to "V1.00D" in this document now refer to the `main` branch. See [Branch Migration Guide](../BRANCH_MIGRATION_GUIDE.md) for details.

> Last updated: 2025-10-09

This guide maps the main development branch (formerly V1.00D) into focused development categories, articulates stability expectations, defines the guardrails needed for "vibe coding" without breakage, and prepares a foundation for future MCP-driven AI agents.

---

## 1. Category map and stability profile

| Category | Scope | Stability | Interfaces & Dependencies |
| --- | --- | --- | --- |
| Backend API & Services | `src/main.py`, `src/routes/**`, `src/services/**`, `src/models/**`, `src/schemas/**` | **Medium** – frequent enhancements, must stay backward compatible | Flask app factory, SQLAlchemy session, Alembic migrations, dependency validator |
| Frontend UI & Client API | `frontend/src/**`, `frontend/package.json`, `frontend/src/services/api.js` | **Medium** – UX iterations ongoing, integrates with backend schema | React + Vite pipeline, shadcn/Tailwind design system, REST API responses |
| Deployment & Infrastructure | `.github/workflows/v1d-devdeploy.yml`, `scripts/deployment/**`, VPS runbooks | **High** – should remain stable to protect devdeploy | GitHub Actions, SSH secrets (`VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`), remote `/var/www/landscape-architecture-tool-dev` |
| Data Ingestion & Tooling | `src/routes/excel_import.py`, related services, Excel/CSV utilities, `scripts/development/` | **Medium/High** – bug-prone, affects data quality | Pandas (if enabled), custom parsers, validation schemas, test fixtures |
| Automation & Integrations | `n8n-workflows/**`, `src/routes/n8n_receivers.py`, `scripts/*.py` | **Medium** – triggered workflows require consistency | HTTP webhooks, requests to n8n, secrets inventory |
| Documentation & Ops Knowledge | `docs/**`, `reports/**`, `_internal/**` | **Low volatility** – but authoritative | Ops runbooks, architecture docs, validation reports |
| Testing & Quality Gates | `tests/**`, `frontend/tests/**`, `Makefile`, `pyproject.toml` configs | **Medium** – regression safety net evolving with features | Pytest + coverage, Vitest, Ruff/Black, Make targets (`make backend-test`, `make lint`) |

---

## 2. Deep dive per category

### 2.1 Backend API & Services

#### Backend Responsibilities

- Expose REST endpoints via Flask blueprints
- Enforce data integrity through schemas and SQLAlchemy models
- Wrap DB operations in service layer (`BaseService`) to own transaction boundaries
- Maintain `/health` diagnostics and dependency validation

#### Backend Hotspots & Risks

- `src/routes/plants.py`, `projects.py`, `excel_import.py` frequently touched and sensitive to schema drift
- `DependencyValidator` usage: new imports must respect tests in `tests/test_dependency_validator_import.py`
- Alembic migrations under `migrations/versions/` must remain synchronized with models

#### Backend Required Tests & Commands

```powershell
python -m pytest tests/routes tests/services  # targeted when API/service logic changes
python -m pytest tests/test_dependency_validator_import.py  # must stay green
flake8/ruff or make lint if formatting changes occur
```

#### Backend Vibe Coding Guardrails

- Start each task by loading schema + service context (MCP fetch): models (`src/models`), service definitions, associated tests.
- Any change to DB schema must produce an Alembic migration via `flask --app src.main db migrate` and update fixtures.
- Maintain `to_dict()` outputs to avoid breaking frontend consumption.

#### Backend MCP Agent Notes

- Provide agent with direct API to fetch route/service pairings and schema definitions.
- Pre-flight checklist: ensure `DependencyValidator` unchanged unless tests updated, run targeted pytest job, ensure transaction boundaries.

---

### 2.2 Frontend UI & Client API

#### Frontend Responsibilities

- Deliver SPA in `frontend/src`, using component library + Tailwind
- Maintain API layer in `frontend/src/services/api.js`
- Ensure state management & route guards align with backend auth/roles

#### Frontend Hotspots & Risks

- `frontend/src/components/dashboard/**` (complex data-driven views)
- Form components bound to backend validation rules
- Build pipeline: `vite.config.js`, environment variables

#### Frontend Required Tests & Commands

```powershell
cd frontend
npm run test:run
npm run build  # verifies Vite pipeline
```

#### Frontend Vibe Coding Guardrails

- Pull backend OpenAPI schema via MCP to auto-validate expected payloads.
- Constrain design experiments to tokens in `tailwind.config.js` and shadcn primitives.
- Update localized strings consistently; avoid hard-coded text.

#### Frontend MCP Agent Notes

- Provide agent with component dependency graph and API contracts; can lint for unused imports and run Vitest automatically.
- Integrate Chromatic-style visual diff later if feasible.

---

### 2.3 Deployment & Infrastructure

#### Deployment Responsibilities

- Build/test bundle (backend + frontend) and deliver to VPS devdeploy target
- Manage secrets setup, service restarts, and health verification

#### Deployment Hotspots & Risks

- `.github/workflows/v1d-devdeploy.yml`: safety checks to prevent production contamination
- `scripts/deployment/validate_deployment_prerequisites.sh` and friends
- Remote directory `/var/www/landscape-architecture-tool-dev`

#### Deployment Required Tests & Commands

- Run `python -m pytest tests/test_dependency_validator_import.py` (already enforced in workflow)
- `npm run build` to ensure front-end artifacts exist before deployment
- Manual validation: `curl` on `/health` and `http://:8080`

#### Deployment Vibe Coding Guardrails

- Treat workflows as high-stability: only change with explicit ticket and full regression plan.
- Any new secret requirement must be documented in `docs/deployment/GITHUB_SECRETS_CONFIGURATION.md`.
- Keep remote path whitelisted (`landscape-architecture-tool-dev`).

#### Deployment MCP Agent Notes

- Agent should fetch workflow YAML, diff safe list, and validate remote commands using static analyzer.
- Automate generation of deployment reports and store under `reports/`.

---

### 2.4 Data Ingestion & Tooling

#### Data Responsibilities

- Import Excel/CSV data into DB with validation & dedupe
- Provide admin-level flows for bulk updates

#### Data Hotspots & Risks

- `src/routes/excel_import.py`: concurrency, file IO, error handling
- Fixtures in `tests/test_excel_import.py`, `tests/fixtures/test_stability.py`
- `scripts/development/update_dev_log.py` / `scripts/update_dev_log.py`

#### Data Required Tests & Commands

```powershell
python -m pytest tests/test_excel_import.py tests/fixtures/test_stability.py
```

#### Data Vibe Coding Guardrails

- Ensure file parsing uses safe temp directories; sanitize inputs
- Log import operations and handle partial failure gracefully
- Keep docstrings + dev log updated with changes in accepted columns/specs

#### Data MCP Agent Notes

- Provide agent access to sample spreadsheets and schema mapping docs
- Use MCP to validate column names and generate test fixture updates automatically

---

### 2.5 Automation & Integrations

#### Automation Responsibilities

- Manage n8n automations and webhook handlers
- Provide CLI utilities in `scripts/`

#### Automation Hotspots & Risks

- `n8n-workflows/` – JSON definitions; changes require careful deployment
- `src/routes/n8n_receivers.py` – verifies signatures/payloads

#### Automation Required Tests & Commands

- Run relevant targeted tests (add as they exist); at minimum `python -m pytest tests/routes/test_n8n_receivers.py` if available
- Smoke test workflow using staging n8n endpoint when possible

#### Automation Vibe Coding Guardrails

- Keep webhook payload schema in sync with n8n versions; document changes
- Avoid blocking operations in receivers; use async tasks when necessary

#### Automation MCP Agent Notes

- Provide agent with workflow diffs and ability to check for unauthorized node additions (security posture)

---

### 2.6 Documentation & Ops Knowledge

#### Documentation Responsibilities

- Maintain accurate deployment & architecture docs
- Update validation reports and logs post-change

#### Documentation Hotspots & Risks

- `docs/VPS_*` guides – canonical operations knowledge
- `dev_log.md` – running log of changes

#### Documentation Required Tests & Commands

- None automated, but run spellcheck/lint if available

#### Documentation Vibe Coding Guardrails

- Document any new process or command; link to tickets where possible
- Keep docs versioned per branch; note when instructions diverge from `main`

#### Documentation MCP Agent Notes

- Provide summarization capabilities to generate changelog entries automatically

---

### 2.7 Testing & Quality Gates

#### Testing Responsibilities

- Provide regression safety nets for backend, frontend, data flows
- Manage fixtures and test utilities

#### Testing Hotspots & Risks

- `tests/conftest.py` – transaction savepoints, fixture lifetime
- Known flaky tests (documented in `Makefile` comments and dev log)

#### Testing Required Tests & Commands

```powershell
make backend-test
make lint
cd frontend
npm run test:run
```

#### Testing Vibe Coding Guardrails

- Run targeted suites after any touching change; no skipping unless ticketed
- Update fixtures when data shape evolves; prefer factory functions to hard-coded ids

#### Testing MCP Agent Notes

- Integrate with MCP-run test execution logs; agent can recommend additional tests based on diff

---

## 3. Triaging workflow blueprint

1. **Intake**: classify ticket/PR by category (primary + secondary).
2. **Auto-context via MCP**: fetch relevant files, dependencies, and doc references.
3. **Instruction packet**: attach category-specific AI instructions (see section 4) and required command list.
4. **Execution**: implement changes following guardrails; run commands; update docs/tests/dev log.
5. **Verification**: reviewer ensures guardrails satisfied; cross-check with MCP-generated diff summary.
6. **Release**: confirm `v1d-devdeploy` workflow unaffected unless intended; update deployment notes if necessary.
7. **Post-merge**: log in `dev_log.md`, generate or link to validation report if tests were extensive.

---

## 4. Instruction templates (for AI agents & contributors)

Each template can be stored under `.github/copilot-instructions/` for future automation.

### Backend Template (B1)

- Read `src/routes/<area>.py`, `src/services/<area>_service.py`, `src/schemas/<area>.py` before editing.
- Preserve transaction handling through service layer; do not manage sessions in routes.
- Update `tests/routes` and `tests/services` with new behaviors; run `python -m pytest tests/routes/<area>`.
- If response schema changes, notify frontend by updating API docs / OpenAPI generator.

### Frontend Template (F1)

- Update TypeScript interfaces/constants in `frontend/src/services/api.js` or related hooks.
- Respect Tailwind token usage; avoid inline styles unless logged in dev log.
- Run `npm run test:run` and `npm run build` after code changes.
- Sync UI copy changes with translation or constants files.

### Deployment Template (D1)

- Confirm target directory remains `/var/www/landscape-architecture-tool-dev`.
- Do not reference production secrets or hosts.
- Ensure workflows run backend smoke tests + frontend build before deployment.
- Update docs for any new secret or script requirement.

### Data Tooling Template (DT1)

- Adjust fixtures in `tests/test_excel_import.py` when accepted columns change.
- Log new columns or validations in `dev_log.md` and `docs/development/data_ingestion.md` (create if missing).
- Validate large file handling; ensure temp directories cleaned up.

### Automation Template (A1)

- Mirror n8n workflow edits in repository if using CLI export.
- Document new endpoints triggered and update verification scripts.
- Provide sample payloads for tests, storing them under `tests/fixtures`.

### Documentation Template (DOC1)

- Link changes to corresponding ticket/PR for traceability.
- Highlight differences from `main` if instructions diverge.
- Keep timestamps and authors when updating reports.

### Testing Template (T1)

- Update fixtures/factories rather than duplicating data.
- Note flaky test context in dev log and open follow-up issues if unresolved.
- Prefer parametrized pytest cases to reduce duplication.

---

## 5. MCP integration roadmap

| Category | Required MCP capabilities | Artifacts to expose |
| --- | --- | --- |
| Backend | File fetch, dependency graph, test runner | route/service pairs, schema definitions, Alembic revision history |
| Frontend | Component dependency map, API schema fetch, Vitest runner | `frontend/src/services/api.js`, component trees |
| Deployment | Workflow parser, secret validation checklist | `.github/workflows/v1d-devdeploy.yml`, scripts/deployment configs |
| Data Tooling | Sample file ingestion, column mapping summary | repository fixtures, docs for import format |
| Automation | Workflow state diff, webhook payload validator | `n8n-workflows/` exports, webhook docs |
| Documentation | Summarizer, change log generator | `docs/**`, `reports/**`, `dev_log.md` |
| Testing | Test impact analysis, targeted command runner | pytest/Vitest results, fixture directories |

Action items before agent rollout:

1. Tag files with metadata (YAML/JSON) describing category ownership for MCP queries.
2. Expose Make targets + typical commands per category in machine-readable form (e.g., `config/category_commands.yml`).
3. Build `scripts/devops/triage_helper.py` to auto-classify diffs and emit guardrail checklist.

---

## 6. Additional safeguards & suggestions

1. **Instruction Catalog**: create `.github/copilot-instructions/` folder mirroring templates above for direct integration.
2. **PR Checklist Update**: ensure PR template enforces category identification, tests run, doc updates.
3. **Validation Dashboard**: extend reports with last-known successful command runs (Backend tests, Frontend builds, Deploy smoke).
4. **Security Review Cadence**: monthly audit of deployment scripts/workflows to catch drift.
5. **Knowledge Sync**: require summary notes in `dev_log.md` for significant category work, referencing instructions used.
6. **Automated Guardian Scripts**: introduce pre-commit or CI job verifying `v1d-devdeploy` workflow doesn’t reference production resources.
7. **Future “Vibe Coding” Sessions**: schedule creative coding slots but enforce pre/post checklists (pull latest instructions, run target tests, update log).

---

## 7. Next steps checklist

- [x] Generate machine-readable category metadata (e.g., `config/category_map.yml`).
- [x] Create instruction files under `.github/copilot-instructions/` from templates.
- [x] Implement `triage_helper.py` to map diffs -> categories -> required commands.
- [ ] Automate MCP integration to fetch context + guardrails per category.
- [x] Update PR template with category + test confirmation checklist.
- [ ] Schedule review of existing docs to align with this strategy.

This document will guide both human contributors and MCP-backed AI agents in evolving V1.00D without compromising stability, while leaving room for creative “vibe coding” inside clear safety rails.
