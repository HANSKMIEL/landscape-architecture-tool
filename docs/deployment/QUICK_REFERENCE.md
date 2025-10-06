# DevDeploy Workflow - Quick Reference Card

## 🚀 Quick Start

### First-Time Setup (5 minutes)

```bash
# 1. Generate SSH key
ssh-keygen -t rsa -b 4096 -C "github-actions@landscape-tool" -f ~/.ssh/landscape_deploy

# 2. Add public key to VPS (root login is enabled on this VPS)
ssh root@72.60.176.200
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit

# 3. Add private key to GitHub
# Go to: Settings → Secrets → Actions → New secret
# Name: VPS_SSH_KEY
# Value: [paste entire private key from: cat ~/.ssh/landscape_deploy]
```

### Deploy

```bash
# Option 1: Push to V1.00D (auto-deploys)
git checkout V1.00D
git push

# Option 2: Manual trigger
# Go to: Actions → V1.00D DevDeploy Deployment → Run workflow
```

## 🔍 Pre-Flight Check

```bash
# Run before deploying
export VPS_SSH_KEY="$(cat ~/.ssh/landscape_deploy)"
./scripts/deployment/validate_deployment_prerequisites.sh
```

## 🆘 Common Issues

| Issue | Quick Fix |
|-------|-----------|
| SSH connection failed | `sudo ufw allow 22/tcp` on VPS |
| VPS_SSH_KEY not set | Add secret in GitHub Settings |
| Wrong branch | `git checkout V1.00D` |
| Build fails | Check `npm ci` and `pip install` logs |
| Can't access :8080 | Check nginx: `sudo systemctl status nginx` |

## 📖 Full Documentation

- **Setup Guide**: [docs/deployment/GITHUB_SECRETS_CONFIGURATION.md](GITHUB_SECRETS_CONFIGURATION.md)
- **Troubleshooting**: [docs/deployment/DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)
- **Overview**: [docs/deployment/README.md](README.md)

## 🔐 Required Secrets

| Name | Required | Default |
|------|----------|---------|
| `VPS_SSH_KEY` | ✅ Yes | None |
| `VPS_HOST` | No | 72.60.176.200 |
| `VPS_USER` | No | root |

## 🧪 Verification

After deployment:
- Frontend: http://72.60.176.200:8080
- Title should show: "devdeploy"
- Backend: http://72.60.176.200:5001/health

## 🔧 On VPS

```bash
# Check services
sudo systemctl status landscape-backend-dev nginx

# View logs
sudo journalctl -u landscape-backend-dev -n 50

# Restart services
sudo systemctl restart landscape-backend-dev
sudo systemctl reload nginx
```

## 🎯 Workflow Steps

1. ✅ Checkout V1.00D
2. ✅ Setup Node.js 20 & Python 3.12
3. 🔑 Setup SSH Key
4. ✅ Validate Branch
5. 🔍 Pre-Deployment Validation
6. 📦 Install Dependencies (Backend → Frontend)
7. 🏗️ Build Frontend
8. 🧪 Run Tests
9. 🚀 Deploy to VPS
10. ✅ Verify Deployment

## 📞 Need Help?

1. Check GitHub Actions logs
2. Run validation script
3. Read troubleshooting guide
4. Verify secrets are configured
