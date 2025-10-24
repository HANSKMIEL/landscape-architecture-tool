# Legacy Deployment Scripts Archive

This directory contains deployment scripts that have been superseded by:
1. GitHub Actions workflow automation (`.github/workflows/v1d-devdeploy.yml`)
2. Newer consolidated scripts in `scripts/deployment/`

## Archived Scripts

### `deploy_to_vps.sh`
- **Original Purpose**: Manual VPS deployment
- **Archived Date**: 2025-10-05
- **Reason**: Superseded by workflow automation and `deploy_v1d_to_devdeploy.sh`
- **Replacement**: Use `.github/workflows/v1d-devdeploy.yml` or `scripts/deployment/deploy_v1d_to_devdeploy.sh`

### `deploy_vps_automated.sh`
- **Original Purpose**: Automated VPS deployment with rollback
- **Archived Date**: 2025-10-05
- **Reason**: Functionality now integrated in workflows
- **Replacement**: GitHub Actions workflows

### `vps_deploy_v1d.sh`
- **Original Purpose**: V1.00D branch VPS deployment
- **Archived Date**: 2025-10-05
- **Reason**: Superseded by `scripts/deployment/deploy_v1d_to_devdeploy.sh`
- **Replacement**: Use `scripts/deployment/deploy_v1d_to_devdeploy.sh`

### `vps_deployment_test.sh`
- **Original Purpose**: Test VPS deployment
- **Archived Date**: 2025-10-05
- **Reason**: Testing now integrated in workflows
- **Replacement**: Workflow verification steps in `v1d-devdeploy.yml`

## Recovery

If you need to recover any of these scripts:
```bash
# Check script history
git log -- archive/deployment/legacy-scripts/deploy_to_vps.sh

# Recover a script (creates a copy, doesn't restore)
git show HEAD:archive/deployment/legacy-scripts/deploy_to_vps.sh > scripts/recovered_deploy.sh
```

## Current Active Scripts

See `docs/deployment/DEPLOYMENT_SCRIPTS_GUIDE.md` for documentation on active deployment scripts.

---

**Archived**: 2025-10-05  
**Maintained by**: HANSKMIEL
