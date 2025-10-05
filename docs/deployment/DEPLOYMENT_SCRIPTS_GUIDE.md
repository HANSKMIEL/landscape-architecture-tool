# Deployment Scripts Guide

## Overview

This guide documents all deployment scripts in the repository, their purpose, and when to use each one.

## 📊 Script Status and Usage

### ✅ Active Scripts (Used by Workflows)

These scripts are actively used by GitHub Actions workflows and should be maintained:

#### 1. `scripts/deployment/github-actions-deploy.sh`
- **Purpose**: Deployment script designed for GitHub Actions
- **Used by**: Production deployment workflows
- **Status**: ✅ Active
- **Location**: `scripts/deployment/github-actions-deploy.sh`

#### 2. `scripts/deployment/enhanced-deploy.sh`
- **Purpose**: Enhanced deployment with zero-downtime features
- **Used by**: `.github/workflows/enhanced-deployment.yml`
- **Status**: ✅ Active
- **Location**: `scripts/deployment/enhanced-deploy.sh`

#### 3. `scripts/deployment/fix_firewall.sh`
- **Purpose**: Fixes VPS firewall configuration for port access
- **Used by**: `.github/workflows/v1d-devdeploy.yml` (embedded)
- **Status**: ✅ Active
- **Location**: `scripts/deployment/fix_firewall.sh`

#### 4. `scripts/deployment/fix_backend_binding.sh`
- **Purpose**: Fixes backend binding to allow external access
- **Used by**: `.github/workflows/v1d-devdeploy.yml` (embedded)
- **Status**: ✅ Active
- **Location**: `scripts/deployment/fix_backend_binding.sh`

#### 5. `scripts/deployment/deploy_v1d_to_devdeploy.sh`
- **Purpose**: Manual V1.00D to devdeploy deployment
- **Used by**: Manual operations, embedded in v1d-devdeploy.yml
- **Status**: ✅ Active
- **Location**: `scripts/deployment/deploy_v1d_to_devdeploy.sh`

#### 6. `scripts/deployment/promote_v1d_to_v1.sh`
- **Purpose**: Promotes V1.00D changes to V1.00 production package
- **Used by**: Manual promotion workflow
- **Status**: ✅ Active
- **Location**: `scripts/deployment/promote_v1d_to_v1.sh`

### ⚠️ Helper Scripts (Not Directly Used by Workflows)

These scripts provide helper functionality but aren't directly called by workflows:

#### 1. `scripts/deploy_helper.sh`
- **Purpose**: Interactive deployment helper for local deployment
- **Usage**: Manual local deployments
- **Status**: ⚠️ Helper - Keep for manual operations
- **Recommendation**: Keep - useful for local testing

#### 2. `scripts/webhook_deploy.sh`
- **Purpose**: VPS-side webhook deployment handler
- **Usage**: Can be set up on VPS for webhook-triggered deployments
- **Status**: ⚠️ Helper - Optional VPS setup
- **Recommendation**: Keep - useful for webhook automation

#### 3. `scripts/deployment/devdeploy_diagnostic.sh`
- **Purpose**: Diagnostic script for devdeploy environment
- **Usage**: Troubleshooting devdeploy issues
- **Status**: ⚠️ Helper - Diagnostic tool
- **Recommendation**: Keep - useful for debugging

### 🔄 Deprecated/Redundant Scripts

These scripts have overlapping functionality or are superseded by workflow automation:

#### 1. `scripts/deploy_to_vps.sh` ❌ **RECOMMEND ARCHIVE**
- **Purpose**: Manual VPS deployment script
- **Issue**: Functionality now in `.github/workflows/v1d-devdeploy.yml`
- **Replacement**: Use GitHub Actions workflow or `deploy_v1d_to_devdeploy.sh`
- **Recommendation**: Move to `archive/deployment/`

#### 2. `scripts/deploy_vps_automated.sh` ❌ **RECOMMEND ARCHIVE**
- **Purpose**: Automated VPS deployment with rollback
- **Issue**: Overlaps with `deploy_v1d_to_devdeploy.sh` and workflow automation
- **Replacement**: GitHub Actions workflows handle this
- **Recommendation**: Move to `archive/deployment/`

#### 3. `scripts/vps_deploy_v1d.sh` ❌ **RECOMMEND ARCHIVE**
- **Purpose**: V1.00D VPS deployment
- **Issue**: Superseded by `scripts/deployment/deploy_v1d_to_devdeploy.sh` and workflows
- **Replacement**: Use workflow or newer deployment script
- **Recommendation**: Move to `archive/deployment/`

#### 4. `scripts/vps_deployment_test.sh` ❌ **RECOMMEND ARCHIVE**
- **Purpose**: Test VPS deployment
- **Issue**: Workflows now include built-in testing
- **Replacement**: Workflow verification steps
- **Recommendation**: Move to `archive/deployment/`

#### 5. `scripts/update_v1_from_dev.sh` ⚠️ **REVIEW NEEDED**
- **Purpose**: Update V1.00 from development
- **Issue**: Overlaps with `promote_v1d_to_v1.sh`
- **Note**: Check if still used by any workflows
- **Recommendation**: Consolidate with `promote_v1d_to_v1.sh` or archive

## 🎯 Recommended Actions

### Immediate Actions

1. **Archive Redundant Scripts**
   ```bash
   # Move deprecated scripts to archive
   mkdir -p archive/deployment/legacy-scripts
   git mv scripts/deploy_to_vps.sh archive/deployment/legacy-scripts/
   git mv scripts/deploy_vps_automated.sh archive/deployment/legacy-scripts/
   git mv scripts/vps_deploy_v1d.sh archive/deployment/legacy-scripts/
   git mv scripts/vps_deployment_test.sh archive/deployment/legacy-scripts/
   ```

2. **Document Active Scripts**
   - Add header comments to each active script
   - Include usage examples
   - Document required environment variables

3. **Create Script Reference**
   - Update README with deployment workflow
   - Link to this guide from main README

### Script Organization Structure

```
scripts/
├── deployment/           # Active deployment scripts used by workflows
│   ├── github-actions-deploy.sh
│   ├── enhanced-deploy.sh
│   ├── deploy_v1d_to_devdeploy.sh
│   ├── promote_v1d_to_v1.sh
│   ├── fix_firewall.sh
│   ├── fix_backend_binding.sh
│   ├── devdeploy_diagnostic.sh
│   └── README.md
├── deploy_helper.sh      # Manual deployment helper
└── webhook_deploy.sh     # VPS webhook handler

archive/deployment/legacy-scripts/  # Archived scripts
├── deploy_to_vps.sh
├── deploy_vps_automated.sh
├── vps_deploy_v1d.sh
└── vps_deployment_test.sh
```

## 📚 Deployment Workflows

### V1.00D Development Deployment

```bash
# Automatic: Push to V1.00D branch triggers workflow
git push origin V1.00D

# Manual: Use GitHub Actions workflow_dispatch
# Go to Actions → "V1.00D DevDeploy Deployment" → Run workflow

# Local Manual: Use deployment helper
./scripts/deploy_helper.sh
```

### Production Deployment (V1.00)

```bash
# Promote V1.00D to V1.00 (creates backup)
./scripts/deployment/promote_v1d_to_v1.sh

# Deploy to production via workflow
# Go to Actions → "Production Deployment" → Run workflow
```

### Emergency/Manual Deployment

```bash
# Use deployment helper for local manual deployment
./scripts/deploy_helper.sh

# Or use direct deployment script
./scripts/deployment/deploy_v1d_to_devdeploy.sh
```

## 🔍 Script Dependencies

### Required Tools
- `bash` 4.0+
- `git`
- `ssh` client
- `curl`
- `jq` (for some diagnostic scripts)

### Required Secrets/Variables
- `VPS_SSH_KEY` - SSH private key for VPS access
- `VPS_HOST` - VPS hostname/IP (default: 72.60.176.200)
- `VPS_USER` - VPS username (default: root)

## 🧪 Testing Deployment Scripts

### Test Locally
```bash
# Dry-run mode (if supported)
DRY_RUN=true ./scripts/deployment/deploy_v1d_to_devdeploy.sh

# Test with diagnostic script
./scripts/deployment/devdeploy_diagnostic.sh
```

### Test on VPS
```bash
# SSH to VPS and run diagnostic
ssh root@72.60.176.200 "bash <(curl -fsSL https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/deployment/devdeploy_diagnostic.sh)"
```

## 📝 Maintenance Guidelines

### Before Adding New Scripts
1. Check if existing scripts can be enhanced
2. Document purpose and usage in header
3. Add to this guide
4. Include in appropriate workflow if needed

### Before Removing Scripts
1. Check for workflow references
2. Check for documentation references
3. Archive instead of delete
4. Update this guide

### Regular Reviews
- Quarterly review of script usage
- Check for deprecated functionality
- Update documentation
- Consolidate similar scripts

---

**Last Updated**: 2025-10-05  
**Maintained by**: HANSKMIEL  
**Version**: 1.0
