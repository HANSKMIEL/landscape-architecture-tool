# GitHub Secrets Required for CI/CD

This document lists all GitHub secrets required for the Landscape Architecture Tool CI/CD pipelines.

## 🔐 Required Secrets

### VPS Deployment Secrets

These secrets are required for automated deployment to the VPS development environment:

#### `VPS_SSH_KEY` (Primary) / `HOSTINGER_SSH_KEY` (Legacy)

- **Type**: SSH Private Key
- **Description**: Private SSH key for authenticating to the VPS server
- **Format**: Multi-line SSH private key (begins with `-----BEGIN OPENSSH PRIVATE KEY-----`)
- **Primary Name**: `VPS_SSH_KEY` (used by most workflows)
- **Legacy Name**: `HOSTINGER_SSH_KEY` (being migrated)
- **Used by**:
  - `.github/workflows/v1d-devdeploy.yml` (primary deployment)
  - `.github/workflows/enhanced-deployment.yml`
  - `.github/workflows/manual-deploy.yml`
  - All VPS diagnostic and management workflows
- **Setup**:

  ```bash
  # Generate key pair (if not exists)
  ssh-keygen -t ed25519 -C "github-actions@landscape-tool" -f vps_deploy_key

  # Add public key to VPS ~/.ssh/authorized_keys
  ssh-copy-id -i vps_deploy_key.pub root@72.60.176.200

  # Add private key to GitHub Secrets as VPS_SSH_KEY
  # Settings → Secrets and variables → Actions → New repository secret
  # Name: VPS_SSH_KEY
  # Value: Contents of vps_deploy_key (entire file including headers)
  ```

#### `VPS_USER` (Primary) / `HOSTINGER_USERNAME` (Legacy)

- **Type**: String
- **Description**: SSH username for VPS server access
- **Example**: `root` (current), or `u123456789`
- **Primary Name**: `VPS_USER` (used by most workflows)
- **Legacy Name**: `HOSTINGER_USERNAME` (being migrated)
- **Used by**: All deployment workflows with fallback to `root`
- **Setup**: VPS username provided by hosting provider
- **Current Value**: `root` (used as default fallback)

#### `VPS_HOST` (Primary) / `HOSTINGER_HOST` (Legacy)

- **Type**: String (IP address or hostname)
- **Description**: VPS server hostname or IP address
- **Example**: `72.60.176.200` (current development server)
- **Primary Name**: `VPS_HOST` (used by most workflows)
- **Legacy Name**: `HOSTINGER_HOST` (being migrated)
- **Used by**: All deployment workflows with fallback to `72.60.176.200`
- **Current Value**: `72.60.176.200` (development server)
- **Setup**: VPS IP address or hostname from hosting provider

### Optional Secrets

#### `STAGING_URL`

- **Type**: String (URL)
- **Description**: Staging environment URL for testing
- **Example**: `http://staging.example.com`
- **Used by**: Testing and validation workflows
- **Required**: No (deployment works without it)

#### `PRODUCTION_URL`

- **Type**: String (URL)
- **Description**: Production environment URL
- **Example**: `https://optura.nl`
- **Used by**: Production deployment workflows (not V1.00D)
- **Required**: No (only for production deployments)

## 🔧 How to Add Secrets

1. Go to GitHub repository: https://github.com/HANSKMIEL/landscape-architecture-tool
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter secret name (exactly as shown above)
5. Paste secret value
6. Click **Add secret**

## ⚠️ Security Best Practices

### Secret Management

- **Never commit secrets** to the repository
- **Rotate SSH keys** every 90 days
- **Use separate keys** for development and production
- **Limit key permissions** on the VPS (use specific user, not root)
- **Monitor secret usage** in workflow logs

### Key Rotation Schedule

```bash
# Recommended rotation schedule
SSH Keys:     Every 90 days
Passwords:    Every 60 days
API Tokens:   Every 30 days
```

### SSH Key Security

```bash
# On VPS: Restrict SSH key to specific IP (GitHub Actions)
# Edit ~/.ssh/authorized_keys
from="140.82.112.0/20,143.55.64.0/20,185.199.108.0/22,192.30.252.0/22" ssh-ed25519 AAAA...
```

## 🔍 Verification

Check if secrets are configured correctly:

```bash
# In GitHub Actions workflow, test SSH connection:
- name: Test SSH Connection
  run: |
    ssh -o StrictHostKeyChecking=no ${{ secrets.HOSTINGER_USERNAME }}@${{ secrets.HOSTINGER_HOST }} "echo 'Connection successful'"
```

## 📋 Secret Audit Log

| Secret Name        | Last Rotated | Expires | Notes                              |
| ------------------ | ------------ | ------- | ---------------------------------- |
| HOSTINGER_SSH_KEY  | -            | -       | Initial setup, needs rotation date |
| HOSTINGER_USERNAME | N/A          | N/A     | Static value                       |
| HOSTINGER_HOST     | N/A          | N/A     | Static value                       |

## 🚨 Troubleshooting

### Deployment fails with "Permission denied (publickey)"

- Verify `HOSTINGER_SSH_KEY` contains the complete private key including headers
- Ensure public key is added to VPS `~/.ssh/authorized_keys`
- Check SSH key format (should be OpenSSH format, not PEM)

### Deployment fails with "Host key verification failed"

- Add `StrictHostKeyChecking=no` to SSH command (already in workflows)
- Or add VPS host key to GitHub Actions known_hosts

### Secret not found error

- Verify secret name spelling (case-sensitive)
- Check secret is set at repository level (not environment level)
- Ensure workflow has access to secrets

## 📚 Related Documentation

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH Key Authentication Best Practices](https://www.ssh.com/academy/ssh/keygen)
- [VPS Deployment Guide](../docs/VPS_DEPLOYMENT_INSTRUCTIONS.md)
- [Security Audit Report](../reports/security/COMPREHENSIVE_SECURITY_AUDIT_V1.00D.md)

## 🔄 Automation

Consider automating secret rotation with GitHub Actions:

```yaml
name: Rotate SSH Keys
on:
  schedule:
    - cron: "0 0 1 */3 *" # Every 3 months
  workflow_dispatch:

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - name: Generate new SSH key
        run: ssh-keygen -t ed25519 -f new_key -N ""

      - name: Update VPS authorized_keys
        run: |
          ssh-copy-id -i new_key.pub ${{ secrets.HOSTINGER_USERNAME }}@${{ secrets.HOSTINGER_HOST }}

      - name: Manual step required
        run: echo "Update HOSTINGER_SSH_KEY secret in GitHub with contents of new_key"
```

---

**Last Updated**: October 1, 2025  
**Maintained by**: HANSKMIEL  
**Version**: 1.0
