# Deployment & Infrastructure Guardrails (D1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

## Core Best Practices
**Follow the comprehensive framework:**
- **Environment Setup**: [DEVELOPMENT_GUIDE.md - Section 1](../../docs/DEVELOPMENT_GUIDE.md#1-bulletproof-development-environment) - Docker, environment parity
- **Branching & Promotion**: [BRANCHING_STRATEGY.md](../../docs/BRANCHING_STRATEGY.md) - V1.00D → main promotion process
- **Deployment Guide**: See `docs/deployment/` and `docs/VPS_DEPLOYMENT_SOLUTION.md`

## Environment Isolation

1. **DevDeploy Environment (V1.00D)**: Restrict changes to the devdeploy environment: workflows and scripts must target `/var/www/landscape-architecture-tool-dev` and never touch production paths.
   - URL: http://72.60.176.200:8080
   - Automatic deployment on V1.00D push

2. **Production Environment (main)**: Protected, promoted only via script
   - URL: https://optura.nl
   - Promotion: `./scripts/deployment/promote_v1d_to_v1.sh`

## Deployment Workflow

1. **Secrets Management**: Verify secrets usage—only reference `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, and document any new secret requirements in `docs/deployment/GITHUB_SECRETS_CONFIGURATION.md`.

2. **CI Validation**: Keep CI steps running backend smoke tests and frontend builds before deployment. Do not remove validation steps without a replacement plan.

3. **Documentation**: When modifying scripts or workflows, update associated runbooks under `docs/deployment/`.

4. **Pre-deployment Checks**: Run or plan the following checks before merging:

   ```powershell
   python -m pytest tests/test_dependency_validator_import.py
   cd frontend
   npm run build
   ```

5. **Post-deployment Validation**: After deployment-related changes, perform a manual smoke check against `http://72.60.176.200:8080` and `/health`, documenting results in `dev_log.md`.

## Docker & Environment Parity
Follow [DEVELOPMENT_GUIDE.md - Environment Parity](../../docs/DEVELOPMENT_GUIDE.md#goal-environment-parity):
- Use Docker Compose for local development
- Match production environment configuration
- Never commit `.env` files (use `.env.example` as template)
- Test in containers before deploying
