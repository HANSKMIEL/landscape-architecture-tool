# VPS DevDeploy Setup & Verification Guide

**Purpose**: Complete guide to configure secrets and verify devdeploy deployment  
**Target Environment**: V1.00D → http://72.60.176.200:8080  
**VPS Provider**: Hostinger VPS (fully compatible)  
**Status**: Ready for execution

---

## 🎯 Overview

This guide walks through configuring and deploying to your **Hostinger VPS** at 72.60.176.200:8080.

### Hostinger VPS Compatibility ✅

This configuration is **fully tested and compatible** with Hostinger VPS hosting:
- ✅ Works with standard Hostinger Ubuntu VPS
- ✅ Compatible with Hostinger firewall settings
- ✅ Supports both `HOSTINGER_*` and `VPS_*` secret naming
- ✅ Uses standard Hostinger `/var/www/` directory structure
- ✅ Documented in `docs/architecture/HOSTINGER_DEPLOYMENT_GUIDE.md`

**Note**: If you're currently using `HOSTINGER_SSH_KEY`, `HOSTINGER_HOST`, or `HOSTINGER_USERNAME` secrets, they will continue to work. The new `VPS_*` naming is recommended for clarity but not required.

### What This Guide Covers
### What This Guide Covers

1. Configuring required VPS_SSH_KEY secret (works with Hostinger VPS)
2. Validating secret configuration
3. Testing deployment to devdeploy on Hostinger VPS
4. Verifying deployment success

**Time Required**: 15-20 minutes

**Hostinger-Specific Notes**:
- If you have existing `HOSTINGER_*` secrets, they work without changes
- Hostinger firewall configuration is handled automatically
- See `docs/architecture/HOSTINGER_DEPLOYMENT_GUIDE.md` for Hostinger account setup

---

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] Admin access to GitHub repository
- [ ] SSH access to Hostinger VPS (72.60.176.200)
- [ ] GitHub account with necessary permissions
- [ ] Terminal/SSH client installed

**For Hostinger Users**:
- [ ] Access to Hostinger control panel (https://hpanel.hostinger.com)
- [ ] Hostinger VPS activated and running
- [ ] SSH access enabled in Hostinger panel

---

## 🔐 Part 1: Configure VPS_SSH_KEY Secret

### Option A: Use Existing SSH Key (If Available)

If you already have SSH access to the VPS:

1. **Locate your existing SSH key**:
   ```bash
   # Check for existing keys
   ls -la ~/.ssh/
   
   # Look for files like:
   # - id_rsa (private) / id_rsa.pub (public)
   # - id_ed25519 (private) / id_ed25519.pub (public)
   ```

2. **Test current access**:
   ```bash
   ssh root@72.60.176.200 "echo 'SSH works'"
   ```

3. **Copy private key content**:
   ```bash
   # For RSA key
   cat ~/.ssh/id_rsa
   
   # For Ed25519 key (recommended)
   cat ~/.ssh/id_ed25519
   
   # Copy the ENTIRE output including headers:
   # -----BEGIN OPENSSH PRIVATE KEY-----
   # [key content]
   # -----END OPENSSH PRIVATE KEY-----
   ```

4. **Skip to "Add Secret to GitHub" section below**

### Option B: Generate New SSH Key (Recommended)

Generate a dedicated key for GitHub Actions:

1. **Generate Ed25519 key** (modern, secure):
   ```bash
   ssh-keygen -t ed25519 -C "github-actions@landscape-tool" -f ~/.ssh/vps_deploy_key -N ""
   ```
   
   Or **Generate RSA key** (if Ed25519 not supported):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@landscape-tool" -f ~/.ssh/vps_deploy_key -N ""
   ```

2. **Add public key to VPS**:
   ```bash
   # Copy public key to VPS
   ssh-copy-id -i ~/.ssh/vps_deploy_key.pub root@72.60.176.200
   
   # OR manually add to VPS:
   cat ~/.ssh/vps_deploy_key.pub | ssh root@72.60.176.200 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
   ```

3. **Test new key**:
   ```bash
   ssh -i ~/.ssh/vps_deploy_key root@72.60.176.200 "echo 'New key works'"
   ```

4. **Get private key content**:
   ```bash
   cat ~/.ssh/vps_deploy_key
   
   # Copy the ENTIRE output including headers
   ```

### Add Secret to GitHub

1. **Navigate to repository secrets**:
   - Go to: https://github.com/HANSKMIEL/landscape-architecture-tool
   - Click: **Settings** → **Secrets and variables** → **Actions**

2. **Create new secret**:
   - Click: **New repository secret**
   - Name: `VPS_SSH_KEY`
   - Value: Paste the entire private key (including headers)
   - Click: **Add secret**

3. **Verify secret added**:
   - Should see `VPS_SSH_KEY` in the secrets list
   - Shows "Updated X minutes ago"

### Optional: Configure VPS_HOST and VPS_USER

Only needed if using different VPS or user:

1. **VPS_HOST** (default: 72.60.176.200):
   - Create secret with your VPS IP/hostname

2. **VPS_USER** (default: root):
   - Create secret with your SSH username

---

## ✅ Part 2: Validate Configuration

### Automated Validation (Recommended)

1. **Run validation workflow**:
   - Go to: **Actions** → **Validate Required Secrets**
   - Click: **Run workflow**
   - Select branch: `copilot/fix-6f3ce97a-a5a3-4f91-ac39-e00571ff27a9` (or current branch)
   - Click: **Run workflow**

2. **Check results**:
   - Wait ~1-2 minutes for completion
   - Should see:
     - ✅ VPS_SSH_KEY: Configured (Valid format)
     - ✅ SSH Connection: Connected successfully
   - Download artifact for detailed report

3. **If validation fails**:
   - Check private key format (should include headers)
   - Verify public key is in VPS authorized_keys
   - Test SSH manually: `ssh -i ~/.ssh/key root@72.60.176.200`

### Manual Validation (Alternative)

Run validation script locally:

```bash
# Clone repository if needed
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
cd landscape-architecture-tool

# Run validation
./scripts/deployment/pre_deployment_validation.sh

# Should show:
# ✅ Passed: 20+ checks
# ⚠️  Warnings: A few (non-critical)
# ❌ Failed: 0 (or 1 for VPS_SSH_KEY if running locally)
```

---

## 🚀 Part 3: Test Deployment

### Option A: Automatic Deployment (Recommended)

Push to V1.00D branch triggers automatic deployment:

```bash
# Ensure you're on correct branch
git checkout V1.00D  # or copilot/fix-* branch
git pull origin V1.00D

# Make a small change (optional)
echo "# Deployment test" >> README.md
git add README.md
git commit -m "test: trigger devdeploy deployment"

# Push to trigger workflow
git push origin V1.00D
```

**Monitor deployment**:
- Go to: **Actions** → **V1.00D DevDeploy Deployment**
- Watch real-time logs
- Deployment takes ~5-10 minutes

### Option B: Manual Workflow Trigger

Trigger deployment without code changes:

1. **Go to Actions**:
   - Navigate to: **Actions** → **V1.00D DevDeploy Deployment**

2. **Run workflow**:
   - Click: **Run workflow**
   - Select branch: `V1.00D`
   - Force deploy: `false` (or `true` to skip tests)
   - Click: **Run workflow**

3. **Monitor progress**:
   - Watch deployment steps in real-time
   - Check for any errors

---

## 🔍 Part 4: Verify Deployment

### Check Workflow Output

1. **Workflow should show**:
   ```
   ✅ V1.00D branch validation complete
   ✅ Dependencies installed
   ✅ Frontend build complete with devdeploy branding
   ✅ V1.00D devdeploy deployment complete
   ✅ DevDeploy title verification passed
   🎉 V1.00D successfully deployed to devdeploy environment!
   ```

2. **Check deployment report**:
   - Download artifact: "v1d-devdeploy-deployment"
   - Review `deployment-report.md`

### Test Frontend Access

1. **Open browser**:
   - Navigate to: http://72.60.176.200:8080

2. **Verify devdeploy branding**:
   - Browser tab title should show: "devdeploy - Landscape Architecture Tool (Development)"
   - Page should load successfully

3. **Check console** (F12):
   - No critical errors (some warnings OK)

### Test Backend API

1. **Health endpoint**:
   ```bash
   curl http://72.60.176.200:8080/health
   
   # Should return:
   # {"status":"healthy","database":"connected"}
   ```

2. **API endpoints**:
   ```bash
   # Test suppliers endpoint
   curl http://72.60.176.200:8080/api/suppliers
   
   # Should return JSON with suppliers list
   ```

### SSH Verification (Advanced)

Connect to VPS and verify:

```bash
ssh root@72.60.176.200

# Check deployment directory
cd /var/www/landscape-architecture-tool-dev
git branch  # Should show V1.00D
git log -1 --oneline  # Should show latest commit

# Check service status
systemctl status landscape-backend-dev

# Check logs
journalctl -u landscape-backend-dev -n 50

# Verify devdeploy title in built frontend
grep "devdeploy" frontend/dist/index.html

# Exit VPS
exit
```

---

## 🎉 Success Criteria

Deployment is successful when:
- [x] Workflow completes without errors
- [x] http://72.60.176.200:8080 accessible
- [x] Browser title shows "devdeploy - Landscape Architecture Tool (Development)"
- [x] Health endpoint returns healthy status
- [x] API endpoints respond correctly
- [x] No critical errors in browser console
- [x] Backend service running on VPS

---

## ⚠️ Troubleshooting

### Workflow Fails: "Permission denied (publickey)"

**Cause**: VPS_SSH_KEY not configured or invalid

**Solution**:
1. Verify secret exists in GitHub Settings
2. Check private key includes full content with headers
3. Test SSH manually: `ssh -i ~/.ssh/key root@72.60.176.200`
4. Ensure public key in VPS `~/.ssh/authorized_keys`

### Workflow Fails: "DevDeploy title verification failed"

**Cause**: Title not set correctly in build

**Solution**:
1. Check `frontend/index.html` has correct title
2. Clear frontend build cache
3. Re-run deployment with force_deploy: true

### Frontend Not Accessible

**Cause**: Nginx not configured or firewall blocking

**Solution**:
```bash
ssh root@72.60.176.200

# Check nginx status
systemctl status nginx

# Check firewall
ufw status

# Allow port 8080
ufw allow 8080/tcp

# Restart nginx
systemctl restart nginx
```

### Backend Not Responding

**Cause**: Service not running or binding issue

**Solution**:
```bash
ssh root@72.60.176.200

# Check service
systemctl status landscape-backend-dev

# Check logs
journalctl -u landscape-backend-dev -n 50

# Restart service
systemctl restart landscape-backend-dev

# Check if port is listening
netstat -tlnp | grep 5001
```

### Legacy Secret Warning

**Cause**: Using old HOSTINGER_* secret names

**Solution**:
1. Workflow will still work (backward compatible with Hostinger secrets)
2. Migrate to VPS_* naming when convenient for clarity
3. See `.github/SECRETS_REQUIRED.md` for migration guide

**Hostinger Note**: If you're using `HOSTINGER_SSH_KEY`, `HOSTINGER_HOST`, or `HOSTINGER_USERNAME`, these continue to work perfectly. No migration required unless you want cleaner naming.

### Hostinger Firewall Issues

**Cause**: Hostinger panel firewall not attached to VPS

**Solution**:
1. Login to Hostinger panel: https://hpanel.hostinger.com
2. Go to: VPS → Manage → Firewall
3. Ensure firewall is "Attached" to your VPS
4. Allow ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8080 (devdeploy)

**Check firewall status**:
```bash
ssh root@72.60.176.200

# Check UFW (local firewall)
ufw status

# Check if Hostinger firewall agent is running
systemctl status firewall-agent 2>/dev/null || echo "Hostinger firewall agent not found"
```

**More details**: See `docs/solutions/HOSTINGER_FIREWALL_TROUBLESHOOTING.md`

### Hostinger SSH Connection Issues

**Cause**: SSH key not in Hostinger VPS authorized_keys

**Solution**:
1. Login to Hostinger panel: https://hpanel.hostinger.com
2. Go to: VPS → Manage → SSH Access
3. Verify SSH is enabled
4. Add your public key via panel or manually:
   ```bash
   # Via Hostinger web terminal
   mkdir -p ~/.ssh
   echo "your-public-key-here" >> ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

---

## 📚 Additional Resources

### Documentation
- **Secrets Guide**: `.github/SECRETS_REQUIRED.md`
- **Deployment Scripts**: `docs/deployment/DEPLOYMENT_SCRIPTS_GUIDE.md`
- **Optimization Summary**: `docs/solutions/V1_00D_OPTIMIZATION_SUMMARY.md`
- **Copilot Instructions**: `.github/copilot-instructions.md`

### Workflows
- **DevDeploy**: `.github/workflows/v1d-devdeploy.yml`
- **Secret Validation**: `.github/workflows/validate-secrets.yml`

### Scripts
- **Pre-deployment Validation**: `scripts/deployment/pre_deployment_validation.sh`
- **Deployment Helper**: `scripts/deploy_helper.sh`

---

## 🔄 Ongoing Maintenance

### Weekly Tasks
- Run secret validation workflow
- Check deployment logs
- Monitor error rates

### Monthly Tasks
- Review and rotate SSH keys
- Update dependencies
- Audit security configurations

### Quarterly Tasks
- Full security audit
- Performance optimization
- Documentation updates

---

## 📞 Support

If issues persist after troubleshooting:
1. Check GitHub Actions logs for detailed error messages
2. Review documentation in `.github/` and `docs/deployment/`
3. Run validation scripts for automated diagnosis
4. Check VPS logs: `journalctl -u landscape-backend-dev -n 100`

---

**Last Updated**: 2025-10-05  
**Version**: 1.0  
**Maintained by**: HANSKMIEL
