# V1.00D – Next Development Steps & Tracking Blueprint

_Last updated: 2025-10-08_

This plan translates the current needs of the V1.00D branch into actionable, testable work items. Each numbered section is intended to ship in its own pull request with a matching GitHub issue (or Jira/Linear ticket) for traceability. Use the checklist template below in every PR description to prove verification steps were completed.

## 🔁 shared workflow for every PR

1. **Create an issue** titled `V1.00D – <scope>` and label it (`devdeploy`, `backend`, `frontend`, `infra`, etc.).
2. **Branch naming**: `feature/v1d-<short-scope>` (e.g., `feature/v1d-devdeploy-hardening`).
3. **PR template checklist** (copy into the PR body):
   - [ ] Scope summary & acceptance criteria
   - [ ] Tests/commands executed (paste output or link to workflow run)
   - [ ] Manual verification / screenshots (if UI)
   - [ ] Rollback plan documented
   - [ ] Linked issue and relevant docs updated
4. **Automation**: attach the latest GitHub Action run, `make`/`npm` logs, and any MCP-generated reports.

---

## 1. DevDeploy pipeline hardening (PR: `feature/v1d-devdeploy-hardening`)

**Objective:** make `.github/workflows/v1d-devdeploy.yml` resilient so the job finishes without manual SSH fixes.

**Action items:**
- Re-run the workflow and capture logs; note where SSH/npm/pip steps fail.
- Extend `deploy_v1d_to_devdeploy.sh` to surface explicit exit codes and nopass scenarios.
- Add post-deploy smoke tests: `curl` frontend root, `/health` proxy, and backend port 5001.
- Ensure `npm` install step reloads the shell so the new PATH is respected (e.g., `hash -r`).
- Document the workflow in `docs/deployment/DEVDEPLOY_AUTOMATION.md`.

**Validation:**
- `make backend-test`
- `npm run build`
- Workflow re-run linked in PR (should end with verification summary)

**MCP assists:** gather live logs (`actions/runs/<id>/logs`), check service status via SSH command integration.

---

## 2. Cloud augmentation review (replace former local-setup step)

**Objective:** decide whether to pair the VPS with Google Cloud or Gemini Studio tooling to accelerate delivery.

**Action items:**
- Evaluate Google Cloud Build or Cloud Deploy to mirror the GitHub Action, giving a controlled environment with longer runtimes.
- Assess Cloud Logging/Monitoring for aggregated VPS telemetry (forward nginx/systemd logs).
- Consider a Cloud SQL replica for safer DB experimentation; verify compliance requirements first.
- If adopting Gemini / Google AI Studio, script a small proof-of-concept calling the same OpenAI-compatible APIs to ensure model parity and rate-limit awareness.
- Summarize findings in `docs/architecture/CLOUD_AUGMENTATION_OPTIONS.md` with pros/cons, cost, and integration steps.

**Validation:**
- Include diagrams or configuration snippets (e.g., build trigger YAML).
- Capture security review notes (service accounts, secret storage).

**Potential blockers:** outbound firewall rules from VPS, data residency constraints, cost approvals.

---

## 3. Backend quality sweep (PR: `feature/v1d-backend-quality`)

**Objective:** eliminate failing/flaky backend tests and tighten lint/type checks.

**Action items:**
- Run `make backend-test`; fix or xfail failures with documented rationale.
- Execute `make lint` (ruff/black/pyright). Resolve warnings; add missing type hints where practical.
- Improve error handling around deployment helpers (e.g., better logging when installing system packages fails).
- Add unit tests for new functions in `src/services` or utility installers.

**Validation:**
- Attach outputs of `make backend-test`, `make lint`.
- Update `tests/README.md` (if missing) with known flaky scenarios.

**Potential pitfalls:** DB migrations interfering with existing data; ensure tests use the nested transaction pattern from `tests/conftest.py`.

---

## 4. Frontend build & test reliability (PR: `feature/v1d-frontend-reliability`)

**Objective:** ensure the Vite build and Vitest suites pass without manual cache busting.

**Action items:**
- Run `npm run build` and `npm run test:vitest:run`; fix failing specs.
- Standardize on `npm ci` everywhere; update docs to warn against `npm install` when `package-lock.json` is present.
- Add a smoke test script (e.g., `scripts/frontend/smoke.sh`) that builds and greps for `devdeploy` in output.
- Consider integrating Vitest run into the GitHub workflow to catch issues before deployment.

**Validation:**
- Attach build + test logs.
- For UI tweaks, capture screenshots or Percy-style diffs if available.

**Potential pitfalls:** cross-platform path issues (Windows vs Linux), outdated lockfile.

---

## 5. Secrets & configuration hardening (PR: `feature/v1d-secrets-hardening`)

**Objective:** tighten secret management and recovery processes.

**Action items:**
- Audit `.env.example` against actual environment variables used in code; add missing entries.
- Update `docs/deployment/VPS_SECRET_RECOVERY_CHECKLIST.md` with the latest SSH/key rotation steps.
- Add a CI script (e.g., `scripts/check_env.py`) that fails when critical env vars are unset during deploy.
- Evaluate GitHub Secret Scanning & Dependabot alerts; document how to respond to hits.

**Validation:**
- Run new env-check script locally and in CI (show output in PR).
- Provide proof of updated documentation.

**Potential pitfalls:** accidentally committing secrets; set `pre-commit` hook to catch `.env` leaks.

---

## 6. Observability & alerting uplift (PR: `feature/v1d-observability`)

**Objective:** gain early warning when devdeploy services degrade.

**Action items:**
- Add a lightweight monitoring script that pings port 8080/5001 and writes to `/var/log/devdeploy-health.log`.
- Integrate with a notification channel (Slack/email) or schedule a GitHub Action on cron that runs the smoke tests and alerts on failure.
- Evaluate forwarding nginx/systemd logs to a hosted solution (e.g., Google Cloud Logging per step 2 assessment).
- Document runbooks in `docs/operations/DEVDEPLOY_RUNBOOK.md`.

**Validation:**
- Demo a simulated failure (stop service) and show alert/log output.
- Include diagrams of the alert flow if using external providers.

**Potential pitfalls:** VPN/firewall restrictions, log volume costs, alert fatigue.

---

## GPT & MCP usage guidelines

- **Consistent model:** configure automation scripts (or MCP server) to invoke the same GPT model used here. If future migrations to GPT‑5 Codex occur, update the model name and re-run compatibility tests (lint, formatters).
- **Prompt hygiene:** store prompts/responses that directly influence code changes in the related issue or PR for auditability.
- **MCP routing:** use MCP to pull structured data (logs, configs) instead of pasting large blocks, keeping context under control.
- **Human verification:** every AI-assisted change must include manual review and tests before merge.

---

## Additional risks & watch-outs

- **VPS capacity:** ensure `/var/www` has enough disk for Node/npm installs; monitor inode usage.
- **Firewall rules:** GitHub Action IPs can change; document how to update VPS firewalls quickly.
- **System package drift:** Debian/Ubuntu repos may lag (e.g., Node 20). Pin versions or host local mirrors if stability becomes an issue.
- **SQLite vs production DB:** devdeploy relies on SQLite; future features needing Postgres-specific functionality must include migration strategies.
- **Backups:** verify automated backups for `instance/landscape_architecture.db` exist before running destructive scripts.
- **Time zones:** scheduled jobs (alerts/tests) should use UTC to avoid DST surprises.

---

Use this document as the master playbook. Update it after each PR to reflect reality (e.g., mark steps complete, add lessons learned). When all sections are shipped, plan the next iteration or roll the improvements into a consolidated `V1.00E` roadmap.
