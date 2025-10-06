# Deployment Documentation

This directory contains comprehensive documentation for deploying the Landscape Architecture Tool to the VPS environment.

## 📚 Documentation Files

### [GITHUB_SECRETS_CONFIGURATION.md](GITHUB_SECRETS_CONFIGURATION.md)
**Complete guide for setting up GitHub Secrets for deployment**

- Required secrets configuration
- SSH key generation and setup
- Step-by-step instructions
- Firewall configuration
- Security best practices
- Testing procedures

**Start here if:** You're setting up deployment for the first time or GitHub Actions can't connect to VPS.

### [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)
**Comprehensive troubleshooting guide for deployment issues**

- Common error messages and solutions
- SSH connection problems
- Build failures
- VPS connectivity issues
- Advanced diagnostics
- Quick reference guides

**Start here if:** Your deployment is failing and you need to diagnose the problem.

## 🚀 Quick Start

### First-Time Setup

1. **Generate SSH Key Pair**
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@landscape-tool" -f ~/.ssh/landscape_deploy
   ```

2. **Add Public Key to VPS**
   ```bash
   ssh root@72.60.176.200
   mkdir -p ~/.ssh && chmod 700 ~/.ssh
   echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```
   
   **Note**: The VPS has `PermitRootLogin yes` configured, which allows root user SSH key authentication.

3. **Add Private Key to GitHub**
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Create new secret: `VPS_SSH_KEY`
   - Paste entire private key content

4. **Run Deployment**
   - Go to: Actions → V1.00D DevDeploy Deployment
   - Click: Run workflow
   - Select: V1.00D branch

**Full instructions:** [GITHUB_SECRETS_CONFIGURATION.md](GITHUB_SECRETS_CONFIGURATION.md)

### Validating Prerequisites

Before deploying, validate your setup:

```bash
# From repository root
export VPS_SSH_KEY="$(cat ~/.ssh/landscape_deploy)"
export VPS_HOST="72.60.176.200"
export VPS_USER="root"

./scripts/deployment/validate_deployment_prerequisites.sh
```

## 🔍 Common Issues

| Issue | Quick Solution | Full Guide |
|-------|----------------|------------|
| SSH connection failed | Check firewall, add SSH key to VPS | [Troubleshooting #1](DEPLOYMENT_TROUBLESHOOTING.md#1-ssh-connection-failed) |
| VPS_SSH_KEY not configured | Add secret in GitHub settings | [Secrets Configuration](GITHUB_SECRETS_CONFIGURATION.md#required-secrets) |
| Build timeout | Check VPS resources, increase timeout | [Troubleshooting #8](DEPLOYMENT_TROUBLESHOOTING.md#8-workflow-times-out) |
| Can't access :8080 | Check nginx, firewall port 8080 | [Troubleshooting #6](DEPLOYMENT_TROUBLESHOOTING.md#6-verification-failed---cant-access-http7260176200-8080) |

## 📋 Deployment Workflow Overview

The V1.00D DevDeploy deployment workflow (`v1d-devdeploy.yml`) performs these steps:

1. ✅ **Checkout V1.00D Branch** - Ensures correct code version
2. ✅ **Setup Node.js 20** - Prepares JavaScript environment
3. ✅ **Setup Python 3.12** - Prepares Python environment
4. 🔑 **Setup SSH Key** - Configures VPS authentication
5. ✅ **Validate Branch** - Verifies deployment readiness
6. 🔍 **Pre-Deployment Validation** - Comprehensive checks
7. 📦 **Install Backend Dependencies** - pip install
8. 📦 **Install Frontend Dependencies** - npm ci
9. 🏗️ **Build Frontend** - Creates production build
10. 🧪 **Run Quick Tests** - Basic validation
11. 🚀 **Deploy to VPS** - Transfers code and restarts services
12. ✅ **Verify Deployment** - Health checks
13. 📊 **Generate Report** - Deployment summary

## 🛠️ Available Scripts

### Validation Scripts

**`scripts/deployment/validate_deployment_prerequisites.sh`**
- Validates all prerequisites before deployment
- Checks GitHub secrets, branch, dependencies, SSH access
- Safe to run - doesn't modify anything

**Usage:**
```bash
./scripts/deployment/validate_deployment_prerequisites.sh
```

### Deployment Scripts

**`scripts/deployment/fix_firewall.sh`**
- Configures VPS firewall for deployment
- Opens required ports (22, 8080, 5001)

**`scripts/deployment/fix_backend_binding.sh`**
- Ensures backend binds to 0.0.0.0 for external access

**`scripts/deployment/devdeploy_diagnostic.sh`**
- Comprehensive diagnostic information
- Useful for troubleshooting

## 🔐 Security Best Practices

1. ✅ **Use SSH keys** - Never use passwords in automation
2. ✅ **Protect private keys** - Never commit to repository
3. ✅ **Rotate keys regularly** - Update every 90 days
4. ✅ **Limit firewall access** - Restrict to GitHub IP ranges when possible
5. ✅ **Monitor logs** - Review deployment logs regularly
6. ✅ **Use separate environments** - DevDeploy ≠ Production

## 🎯 Deployment Environments

### DevDeploy (Development)
- **Branch:** V1.00D
- **URL:** http://72.60.176.200:8080
- **Title:** "devdeploy - Landscape Architecture Tool (Development)"
- **Backend Port:** 5001
- **Purpose:** Testing and development
- **Auto-deploys:** On push to V1.00D

### Production
- **Branch:** main
- **URL:** https://optura.nl
- **Protected:** Manual promotion only via `promote_v1d_to_v1.sh`
- **Purpose:** Live customer-facing application

**⚠️ IMPORTANT:** Never deploy V1.00D directly to production!

## 📊 Monitoring Deployment

### Via GitHub Actions
1. Go to: Repository → Actions
2. Click: V1.00D DevDeploy Deployment
3. View: Latest run status and logs

### Via VPS
```bash
# SSH to VPS
ssh root@72.60.176.200

# Check backend service
sudo systemctl status landscape-backend-dev

# View recent logs
sudo journalctl -u landscape-backend-dev -n 50

# Check nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

### Via Browser
- Frontend: http://72.60.176.200:8080
- Backend API: http://72.60.176.200:5001/health
- Check page title: Should show "devdeploy"

## 🆘 Getting Help

1. **Check troubleshooting guide** - [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)
2. **Review GitHub Actions logs** - Actions tab → Failed workflow → Expand steps
3. **Check VPS logs** - SSH to VPS and check `journalctl`
4. **Validate prerequisites** - Run validation script
5. **Review documentation** - [GITHUB_SECRETS_CONFIGURATION.md](GITHUB_SECRETS_CONFIGURATION.md)

## 🔄 Related Documentation

- [VPS Configuration](../../archive/vps-config/)
- [Deployment Scripts](../../scripts/deployment/)
- [Hosting Architecture](HOSTING_ARCHITECTURE.md)
- [General Documentation](../)

## 📝 Version History

- **2024-01-XX** - Added comprehensive secrets configuration guide
- **2024-01-XX** - Added troubleshooting guide and validation scripts
- **2024-01-XX** - Enhanced workflow with pre-deployment validation
- **2024-01-XX** - Added deployment documentation README

## 📞 Support

For issues or questions:
1. Check the documentation in this directory
2. Review GitHub Actions logs
3. Test with validation script
4. Verify all secrets are configured correctly
