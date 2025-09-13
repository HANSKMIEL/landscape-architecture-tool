# 🛠️ Scripts Directory

This directory contains all automation scripts organized by category for easy maintenance and discovery.

## 📁 Directory Structure

### 🚀 Deployment (`deployment/`)
Scripts for deploying the application to various environments.

- `enhanced-deploy.sh` - Enhanced deployment with validation
- `github-actions-deploy.sh` - GitHub Actions deployment script
- `promote_v1d_to_v1.sh` - **Main promotion script** (V1.00D → V1.00)
- `setup_github_pages.sh` - GitHub Pages deployment setup

### 🔧 Maintenance (`maintenance/`)
Scripts for ongoing maintenance and updates.

- `backup.sh` - Database and file backup utility
- `clean-cache.sh` - Cache cleanup and optimization
- `sync_packages.sh` - Package synchronization between versions
- `update_application.sh` - Application update automation

### 🧪 Testing (`testing/`)
Scripts for automated testing and validation.

- `automated_validation.py` - Comprehensive validation suite
- `test_quality_assurance.py` - Quality assurance testing
- `validate_after_merge.sh` - Post-merge validation
- `validate_structure.sh` - Repository structure validation

### 💻 Development (`development/`)
Scripts for development workflow and tools.

- `copilot_workflow.py` - GitHub Copilot integration
- `manage_titles.sh` - **Title management** (dev/prod)
- `update_dev_log.py` - Development log automation

### 🔒 Security (`security/`)
Scripts for security setup and management.

- `secure_vps_setup.sh` - VPS security hardening
- `setup-secrets.sh` - Secrets management
- `setup-webhooks.sh` - Webhook configuration

## 🎯 Quick Reference

### Most Used Scripts
```bash
# Promote development to production
./scripts/deployment/promote_v1d_to_v1.sh

# Switch between dev/prod titles
./scripts/development/manage_titles.sh dev|prod

# Run comprehensive validation
./scripts/testing/automated_validation.py

# Backup before changes
./scripts/maintenance/backup.sh
```

### Script Execution
All scripts are executable and include help documentation. Run any script with `-h` or `--help` for usage information.

---
**Last Updated**: September 13, 2025  
**Organization**: V1.00D Repository Restructure
