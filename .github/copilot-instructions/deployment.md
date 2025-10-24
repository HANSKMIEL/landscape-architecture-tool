# Deployment & Infrastructure Guardrails (D1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

1. Restrict changes to the devdeploy environment: workflows and scripts must target `/var/www/landscape-architecture-tool-dev` and never touch production paths.
2. Verify secrets usage—only reference `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, and document any new secret requirements in `docs/deployment/GITHUB_SECRETS_CONFIGURATION.md`.
3. Keep CI steps running backend smoke tests and frontend builds before deployment. Do not remove validation steps without a replacement plan.
4. When modifying scripts or workflows, update associated runbooks under `docs/deployment/`.
5. Run or plan the following checks before merging:

   ```powershell
   python -m pytest tests/test_dependency_validator_import.py
   cd frontend
   npm run build
   ```

6. After deployment-related changes, perform a manual smoke check against `http://72.60.176.200:8080` and `/health`, documenting results in `dev_log.md`.
