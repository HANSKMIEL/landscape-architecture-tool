# Scripts Directory

This directory contains scripts for deploying, testing, and maintaining the Landscape Architecture Tool.

## 📚 Essential Documentation (Read First)

Before using these scripts, familiarize yourself with our comprehensive best practices:

- **[DEVELOPMENT_GUIDE.md](../docs/DEVELOPMENT_GUIDE.md)** - Complete framework covering all 5 pillars
- **[BRANCHING_STRATEGY.md](../docs/BRANCHING_STRATEGY.md)** - Git workflow and V1.00D approach
- **[DEBUGGING_GUIDE.md](../docs/DEBUGGING_GUIDE.md)** - Systematic 5-step debugging process
- **[API_DOCUMENTATION.md](../docs/API_DOCUMENTATION.md)** - REST API reference
- **[Deployment Guide](../docs/deployment/DEPLOYMENT_SCRIPTS_GUIDE.md)** - Detailed deployment documentation

## Best Practices for Using Scripts

All scripts follow the engineering velocity framework principles:

1. **Environment Parity**: Scripts use Docker and standardized commands (see [DEVELOPMENT_GUIDE.md - Section 1](../docs/DEVELOPMENT_GUIDE.md#1-bulletproof-development-environment))
2. **Systematic Workflow**: Follow branching strategy (see [BRANCHING_STRATEGY.md](../docs/BRANCHING_STRATEGY.md))
3. **Automated Testing**: Scripts validate changes before deployment (see [DEVELOPMENT_GUIDE.md - Section 4](../docs/DEVELOPMENT_GUIDE.md#4-proactive-code-quality--automation))
4. **Systematic Debugging**: When scripts fail, use the 5-step process (see [DEBUGGING_GUIDE.md](../docs/DEBUGGING_GUIDE.md#the-5-step-debugging-process))

## Script Organization

```
scripts/
├── deployment/           # Active deployment scripts (used by workflows)
│   ├── promote_v1d_to_v1.sh         # V1.00D → V1.00 promotion
│   ├── deploy_v1d_to_devdeploy.sh   # Deploy to devdeploy environment
│   ├── github-actions-deploy.sh      # GitHub Actions deployment
│   ├── enhanced-deploy.sh            # Zero-downtime deployment
│   ├── fix_firewall.sh               # VPS firewall configuration
│   ├── fix_backend_binding.sh        # Backend binding configuration
│   └── devdeploy_diagnostic.sh       # Diagnostic tools
├── deploy_helper.sh      # Manual deployment helper
├── webhook_deploy.sh     # VPS webhook handler
└── vps_clean_reinstall.sh # Complete VPS reinstallation

archive/deployment/legacy-scripts/  # Archived scripts (superseded)
├── deploy_to_vps.sh
├── deploy_vps_automated.sh
├── vps_deploy_v1d.sh
├── vps_deployment_test.sh
└── update_v1_from_dev.sh
```

## Quick Reference

### Active Deployment Scripts

### `vps_clean_reinstall.sh` ⭐ NEW

A comprehensive script for performing a clean reinstallation of the application on the VPS from the V1.00D branch.

#### Usage

```bash
# SSH into VPS and run directly
ssh root@72.60.176.200
cd /tmp
curl -O https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_clean_reinstall.sh
chmod +x vps_clean_reinstall.sh
sudo ./vps_clean_reinstall.sh
```

#### Features

- **Automatic backup** before deletion (keeps last 5 backups)
- **Complete cleanup** of old installation
- **Fresh clone** from V1.00D branch
- **Configuration preservation** (.env file restored)
- **Full setup** of Python environment, dependencies, and frontend
- **Service configuration** with systemd
- **Comprehensive verification** of installation
- **Detailed logging** to `/var/log/landscape-reinstall.log`
- **Rollback support** if issues occur

#### Documentation

- Full guide: `docs/VPS_CLEAN_REINSTALL_GUIDE.md`
- Quick reference: `docs/VPS_QUICK_REFERENCE.md`

---

### `deploy_to_vps.sh`

Automates deployment of latest changes to the VPS at 72.60.176.200:8080.

#### Usage

```bash
./scripts/deploy_to_vps.sh
```

#### Features

- SSH access verification
- Manual deployment commands display
- Automated deployment if SSH access available
- Deployment verification

---

### `webhook_deploy.sh`

Webhook-triggered deployment script designed to run on the VPS server.

#### Usage

```bash
# On VPS
/root/webhook_deploy.sh

# Or set up cron job for automatic updates
0 */4 * * * /root/webhook_deploy.sh >> /var/log/landscape-deploy.log 2>&1
```

#### Features

- Pulls latest changes from V1.00D branch
- Updates Python and Node.js dependencies
- Rebuilds frontend
- Restarts services
- Logs all operations

---

### `update_v1_from_dev.sh`

Promotes validated changes from V1.00D development to V1.00 production package.

#### Usage

```bash
./scripts/update_v1_from_dev.sh
```

#### Features

- Runs tests before promotion
- Creates backups
- Copies validated changes
- Creates version tags

---

### `secure_vps_setup.sh`

A script for securely setting up environment variables and security configurations on the VPS.

#### Usage

```bash
# Run on the VPS as root
sudo ./secure_vps_setup.sh
```

#### Features

- Sets up environment variables for the backend
- Generates a secure random JWT secret
- Configures proper file permissions
- Sets up SSH key authentication (optional)
- Creates a backup of sensitive information

#### Requirements

- Root access on the VPS
- OpenSSL installed for generating secure secrets

## Deployment Best Practices

1. **Use SSH key authentication** instead of passwords
2. **Set proper file permissions** for sensitive files
3. **Keep environment variables secure** and separate from code
4. **Regularly rotate secrets** and credentials
5. **Implement proper backup procedures** for configuration files
