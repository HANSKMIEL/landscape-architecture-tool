# MCP Agent Triage Map for V1.00D

Use this directory as the entry point for routing work to the right guardrail before starting a “vibe coding” session or dispatching an MCP automation agent. Each category below pairs with a guardrail file (ID in parentheses) that details expectations, validation commands, and documentation touchpoints. When a task spans multiple domains, follow the cross-category workflow to make sure hand-offs stay traceable.

## Quick Links

- [D1 – Deployment & Infrastructure](deployment.md)
- [A1 – Automation & Integrations](automation.md)
- [B1 – Backend Development](backend.md)
- [F1 – Frontend Development](frontend.md)
- [DT1 – Data Ingestion & Tooling](data_tooling.md)
- [DOC1 – Documentation & Ops](documentation.md)
- [T1 – Testing & Quality](testing.md)
- [Sub-Workflow Matrix](subworkflows.md)

| Category ID | Scope & Responsibilities | Primary Entry Points | Fast Validation | When to Escalate |
|-------------|-------------------------|----------------------|-----------------|------------------|
| D1 – Deployment & Infrastructure | VPS automation, GitHub Actions workflows, shell scripts under `scripts/deployment/`, server smoke checks | `docs/deployment/`, `scripts/deployment/`, `.github/workflows/` | `python -m pytest tests/test_dependency_validator_import.py`; `cd frontend` then `npm run build` | Backend tests fail, missing secrets, or manual smoke test reports regressions |
| A1 – Automation & Integrations | n8n workflows, webhook receivers, cross-service payload contracts | `n8n-workflows/`, `src/routes/n8n_receivers.py`, `_internal/n8n-workflows/` | `python -m pytest tests/routes/test_n8n_receivers.py` | Payload schemas change or long-running tasks block request threads |
| B1 – Backend Development | Flask routes, SQLAlchemy services/models, schema evolution | `src/routes/`, `src/services/`, `src/schemas/`, `migrations/` | `python -m pytest tests/routes tests/services`; `python -m pytest tests/test_dependency_validator_import.py` | Response shape changes, migration conflicts, or session handling anomalies |
| F1 – Frontend Development | React components, Tailwind styling, API client coordination | `frontend/src/components/`, `frontend/src/services/api.js`, `frontend/src/pages/` | `cd frontend` then `npm run test:run`; `npm run build` | Contract drift with backend, localization gaps, or routing/auth guard updates |
| DT1 – Data Ingestion & Tooling | Excel import pipeline, fixtures, bulk data validation utilities | `src/routes/excel_import.py`, `src/services/`, `tests/test_excel_import.py` | `python -m pytest tests/test_excel_import.py tests/fixtures/test_stability.py` | Column format shifts, performance issues on large files, or sanitization regressions |
| DOC1 – Documentation & Ops | Deployment guides, architecture notes, operational runbooks | `docs/deployment/`, `docs/architecture/`, `_internal/` | Markdown lint or spellcheck routines | Documentation diverges between branches or instructions conflict with automation scripts |
| T1 – Testing & Quality | Test harness upkeep, linting, quality gates, flake triage | `tests/`, `Makefile`, `pyproject.toml` | `make backend-test`; `make lint`; `cd frontend` then `npm run test:run` | Repeated flakes, fixture misuse, or missing coverage for new features |

## How to Use This Map

1. **Triage the task**: Tag issues or dev-log entries with the category ID so MCP agents know which guardrail to open first.
2. **Prime the agent**: Include the relevant guardrail file contents plus any quick context (linked routes, components, workflows) when launching a Vibe Coding session.
3. **Close the loop**: After changes land, append a short note to `dev_log.md` referencing the category ID and the validation you ran. This keeps the optimization log searchable.

For multi-scope work, start with the dominant category and explicitly list secondary guardrails in the task notes. This prevents agents from missing required validation steps.

## Cross-Category Workflow

1. **Tag the scope**: In the issue body or MCP prompt, list the primary guardrail ID plus any secondary IDs (e.g., `Primary: B1`, `Secondary: T1`). Use matching GitHub labels where available.
2. **Link guardrails**: Copy the relevant sections from each guardrail file into the agent briefing or pull request description so validation commands and documentation expectations stay visible.
3. **Record ownership**: Note the acting agent (e.g., “MCP backend agent”) in the issue comment or MCP session log when handing off to a different specialty.
4. **Run all validations**: Execute the command set from every guardrail touched. Capture outputs in the issue or PR thread, or attach logs in `reports/` if lengthy.
5. **Close the loop**: Update `dev_log.md` with the guardrail IDs and validations performed. Cross-reference issue numbers or PRs to give future agents historical breadcrumbs.

For a step-by-step handoff template, see `docs/development/mcp_agent_handoff.md`.

## Template Shortcuts

Each guardrail has matching GitHub templates for issues and pull requests:

- Issue templates live under `.github/ISSUE_TEMPLATE/` (for example, `d1_deployment_task.md`).
- Pull request templates live under `.github/PULL_REQUEST_TEMPLATE/` (for example, `d1_deployment_pr.md`).

When opening an issue, pick the matching category template from the chooser. For pull requests, append `?template=<file-name>.md` to the PR URL (for example, `?template=b1_backend_pr.md`).
