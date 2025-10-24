# Guardrail Sub-Workflows & Handoff Matrix

Use this reference after selecting a primary guardrail to determine whether niche workflows apply and which secondary agents must be looped in before work begins.

## D1 – Deployment & Infrastructure

| Sub-ID | Workflow Focus | Triggers | Required Secondary Guardrails | Notes |
|--------|----------------|----------|-------------------------------|-------|
| D1-S1 | GitHub Actions / CI updates | Modifying `.github/workflows/` | T1 | Ensure quality gates still fire and report to MCP QA agent before merge. |
| D1-S2 | VPS script changes | Editing `scripts/deployment/` or cron tooling | DOC1, T1 | Documentation refresh and smoke test evidence required. |
| D1-S3 | Secret management | Adding or rotating secrets | DOC1 | Update `docs/deployment/GITHUB_SECRETS_CONFIGURATION.md` and notify ops channel. |

## A1 – Automation & Integrations

| Sub-ID | Workflow Focus | Triggers | Required Secondary Guardrails | Notes |
|--------|----------------|----------|-------------------------------|-------|
| A1-S1 | n8n workflow authoring | Updating JSON exports | DOC1 | Document webhook payload contracts and ops steps. |
| A1-S2 | Webhook receiver logic | Editing `src/routes/n8n_receivers.py` | B1, T1 | Backend agent validates service interactions; QA reviews payload permutations. |
| A1-S3 | Background job orchestration | Introducing async workers | D1 | Coordinate deployment changes and monitoring updates. |

## B1 – Backend Development

| Sub-ID | Workflow Focus | Triggers | Required Secondary Guardrails | Notes |
|--------|----------------|----------|-------------------------------|-------|
| B1-S1 | API route changes | Editing `src/routes/` | F1, T1 | Confirm client contracts and add regression tests. |
| B1-S2 | Service/migration updates | Touching `src/services/` or `migrations/` | DT1, D1 | Data tooling reviews seeding impacts; deployment agent plans rollout. |
| B1-S3 | Security/hardening | Modifying auth, permissions, or secrets usage | DOC1, T1 | Update security docs and run extended tests/linting. |

## F1 – Frontend Development

| Sub-ID | Workflow Focus | Triggers | Required Secondary Guardrails | Notes |
|--------|----------------|----------|-------------------------------|-------|
| F1-S1 | Component & UI changes | Editing `frontend/src/components/` | DOC1 | Update UX notes and screenshots. |
| F1-S2 | API consumption | Changing `frontend/src/services/api.js` or queries | B1 | Coordinate backend contract updates before merge. |
| F1-S3 | Localization & content | Updating locale files or copy | DOC1 | Ensure translations and style guides are synced. |

## DT1 – Data Ingestion & Tooling

| Sub-ID | Workflow Focus | Triggers | Required Secondary Guardrails | Notes |
|--------|----------------|----------|-------------------------------|-------|
| DT1-S1 | Schema/column adjustments | Modifying accepted import formats | B1, DOC1 | Align database models and operator instructions. |
| DT1-S2 | Performance tuning | Optimizing import speed/memory | T1 | Benchmark results shared with QA for verification. |
| DT1-S3 | Data quality validation | Enhancing dedupe/validation rules | DOC1 | Document new checks for operators. |

## DOC1 – Documentation & Ops

| Sub-ID | Workflow Focus | Triggers | Required Secondary Guardrails | Notes |
|--------|----------------|----------|-------------------------------|-------|
| DOC1-S1 | Deployment/runbooks | Updating `docs/deployment/` | D1 | Verify technical accuracy with deployment agent. |
| DOC1-S2 | Architecture updates | Editing `docs/architecture/` | B1, F1 | Ensure diagrams and data flows stay current. |
| DOC1-S3 | Ops communications | Drafting announcements or SOPs | All relevant | Coordinate with owners for sign-off and distribution. |

## T1 – Testing & Quality

| Sub-ID | Workflow Focus | Triggers | Required Secondary Guardrails | Notes |
|--------|----------------|----------|-------------------------------|-------|
| T1-S1 | Regression coverage | Adding/updating test suites | Primary feature guardrail | Collaborate with feature owner to confirm acceptance criteria. |
| T1-S2 | Linting/toolchain updates | Modifying `pyproject.toml`, `Makefile`, or lint configs | D1, DOC1 | Update CI and document new requirements. |
| T1-S3 | Stability triage | Investigating flaky tests or failures | Original owning guardrail | Coordinate fixes and track in `reports/`. |

## Pre-Flight Checklist for Agents

1. Identify applicable sub-ID(s) before starting work.
2. Contact or tag secondary guardrail owners; align on responsibilities.
3. Record coordination in the issue template under “MCP Agent Coordination.”
4. Share artifacts/logs via the PR template to confirm joint validation.
5. If new sub-workflows emerge, extend this file and link updates in `dev_log.md`.
