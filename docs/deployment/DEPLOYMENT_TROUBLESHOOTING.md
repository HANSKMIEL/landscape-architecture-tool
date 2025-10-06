# V1.00D DevDeploy Deployment Troubleshooting Guide

This guide helps diagnose and resolve common issues with the V1.00D DevDeploy deployment workflow.

## Quick Diagnostics Checklist

Before troubleshooting specific issues, verify these basics:

- [ ] GitHub Secrets are configured (see [GITHUB_SECRETS_CONFIGURATION.md](GITHUB_SECRETS_CONFIGURATION.md))
- [ ] VPS is online and accessible
- [ ] SSH key is properly configured on VPS
- [ ] Firewall allows GitHub Actions IPs (port 22)
- [ ] You're deploying from the V1.00D branch

## Common Issues and Solutions

### 1. SSH Connection Failed

#### Error Message
```
❌ ERROR: Cannot establish SSH connection to VPS
Permission denied (publickey)
```

#### Possible Causes
1. **VPS_SSH_KEY secret not configured**
2. **Public key not added to VPS**
3. **Firewall blocking connection**
4. **SSH service not running**

#### Solutions

**Solution A: Verify GitHub Secret**
1. Go to: Repository → Settings → Secrets and variables → Actions
2. Check that `VPS_SSH_KEY` exists
3. Verify it contains the complete private key including:
   ```
   -----BEGIN OPENSSH PRIVATE KEY-----
   ... key content ...
   -----END OPENSSH PRIVATE KEY-----
   ```

**Solution B: Add Public Key to VPS**
```bash
# Connect to VPS
ssh root@72.60.176.200

# Add your public key
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-rsa AAAAB3... your-public-key" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**Solution C: Check Firewall**
```bash
# On VPS - check firewall status
sudo ufw status

# Allow SSH from anywhere (for testing)
sudo ufw allow 22/tcp

# Or allow specific GitHub Actions IP ranges
sudo ufw allow from 140.82.112.0/20 to any port 22
sudo ufw allow from 143.55.64.0/20 to any port 22
```

**Solution D: Verify SSH Service**
```bash
# On VPS - check SSH is running
sudo systemctl status sshd

# Restart if needed
sudo systemctl restart sshd

# Check SSH configuration
sudo nano /etc/ssh/sshd_config
# Ensure: PubkeyAuthentication yes
```

### 2. Deployment Workflow Fails at "Setup SSH Key" Step

#### Error Message
```
❌ ERROR: VPS_SSH_KEY secret is not configured!
```

#### Solution
This means the `VPS_SSH_KEY` secret is missing from GitHub.

1. Generate SSH key pair (if you haven't):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@landscape-tool" -f ~/.ssh/landscape_deploy
   ```

2. Add public key to VPS:
   ```bash
   cat ~/.ssh/landscape_deploy.pub
   # Copy the output and add to VPS ~/.ssh/authorized_keys
   ```

3. Add private key to GitHub:
   ```bash
   cat ~/.ssh/landscape_deploy
   # Copy the entire output (including BEGIN/END lines)
   # Add to GitHub: Settings → Secrets → New secret → VPS_SSH_KEY
   ```

See: [GITHUB_SECRETS_CONFIGURATION.md](GITHUB_SECRETS_CONFIGURATION.md) for detailed instructions.

### 3. VPS Firewall Blocking GitHub Actions

#### Error Message
```
Connection timed out
ssh: connect to host 72.60.176.200 port 22: Connection timed out
```

#### Solution
GitHub Actions uses dynamic IP addresses from these ranges:

```bash
# On VPS - allow GitHub Actions IP ranges
sudo ufw allow from 140.82.112.0/20 to any port 22
sudo ufw allow from 143.55.64.0/20 to any port 22
sudo ufw allow from 185.199.108.0/22 to any port 22
sudo ufw allow from 192.30.252.0/22 to any port 22

# For testing only - allow all IPs temporarily
sudo ufw allow 22/tcp

# Reload firewall
sudo ufw reload
```

To get current GitHub IP ranges:
```bash
curl https://api.github.com/meta | jq .actions
```

### 4. Frontend Build Failed

#### Error Message
```
❌ Frontend build failed - no dist/index.html
```

#### Possible Causes
1. **npm install failed**
2. **Build script error**
3. **Missing dependencies**
4. **Out of memory**

#### Solutions

**Solution A: Check npm Dependencies**
Ensure `package-lock.json` exists in the `frontend/` directory. If it's missing:
```bash
cd frontend
npm install --legacy-peer-deps
git add package-lock.json
git commit -m "Add package-lock.json"
git push
```

**Solution B: Check Build Script**
Verify `frontend/package.json` has a build script:
```json
{
  "scripts": {
    "build": "vite build"
  }
}
```

**Solution C: Test Build Locally**
```bash
cd frontend
npm ci --legacy-peer-deps
npm run build
ls -la dist/  # Verify dist/index.html exists
```

### 5. Backend Python Dependencies Failed

#### Error Message
```
ERROR: Could not find a version that satisfies the requirement...
```

#### Solutions

**Solution A: Pin Dependencies**
Update `requirements.txt` with specific versions:
```txt
Flask==2.3.0
gunicorn==21.2.0
# etc.
```

**Solution B: Update pip**
The workflow already does this, but locally:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Solution C: Check Python Version**
Ensure you're using Python 3.12 (as specified in workflow):
```bash
python3 --version  # Should be 3.12.x
```

### 6. Verification Failed - Can't Access http://72.60.176.200:8080

#### Error Message
```
❌ HTTP connectivity failed
curl: (7) Failed to connect to 72.60.176.200 port 8080: Connection refused
```

#### Possible Causes
1. **Nginx not running**
2. **Backend service not started**
3. **Firewall blocking port 8080**
4. **Wrong port configuration**

#### Solutions

**Solution A: Check Nginx**
```bash
# On VPS
sudo systemctl status nginx
sudo systemctl restart nginx

# Check nginx configuration
sudo nginx -t
sudo nano /etc/nginx/sites-available/landscape-tool-dev
```

**Solution B: Check Backend Service**
```bash
# On VPS
sudo systemctl status landscape-backend-dev
sudo systemctl restart landscape-backend-dev

# Check logs
sudo journalctl -u landscape-backend-dev -n 50
```

**Solution C: Check Firewall**
```bash
# On VPS - allow port 8080
sudo ufw allow 8080/tcp
sudo ufw status
```

**Solution D: Manual Test**
```bash
# On VPS - test backend directly
curl http://localhost:5001/health

# Test frontend
curl http://localhost:8080/
```

### 7. DevDeploy Title Not Appearing

#### Error Message
```
❌ DevDeploy title verification failed on port 8080
```

#### Solution
This is usually a caching issue:

**On GitHub Actions Side:**
The workflow automatically sets the title. If it fails:
1. Check `frontend/index.html` has the title tag
2. Verify build step completed successfully
3. Check that sed command worked in "Build Frontend" step

**On VPS Side:**
```bash
# On VPS - verify title in built files
cd /var/www/landscape-architecture-tool-dev/frontend/dist
grep "devdeploy" index.html

# If not found, manually fix:
sed -i 's/<title>.*<\/title>/<title>devdeploy - Landscape Architecture Tool (Development)<\/title>/' index.html

# Restart nginx
sudo systemctl reload nginx
```

**Browser Side:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Try in incognito/private mode

### 8. Workflow Times Out

#### Error Message
```
Error: The operation was canceled.
```

#### Possible Causes
1. **Network issues**
2. **VPS is slow/overloaded**
3. **Step taking too long**

#### Solutions

**Solution A: Check Timeout Settings**
The workflow has `timeout-minutes: 15`. Individual steps that might timeout:
- Frontend build: Usually 2-5 minutes
- Backend deployment: Usually 1-2 minutes
- SSH connection: 30 seconds

**Solution B: Check VPS Resources**
```bash
# On VPS - check resources
top
df -h  # Check disk space
free -h  # Check memory

# If low, consider cleanup:
sudo apt-get autoremove
sudo apt-get clean
```

**Solution C: Increase Timeout**
Edit `.github/workflows/v1d-devdeploy.yml`:
```yaml
jobs:
  deploy-to-devdeploy:
    timeout-minutes: 30  # Increase from 15
```

## Advanced Diagnostics

### Run Validation Script Locally

Test the pre-deployment checks before pushing:

```bash
# Set environment variables (use actual values)
export VPS_SSH_KEY="$(cat ~/.ssh/landscape_deploy)"
export VPS_HOST="72.60.176.200"
export VPS_USER="root"

# Run validation
./scripts/deployment/validate_deployment_prerequisites.sh
```

### Check GitHub Actions Logs

1. Go to: Repository → Actions
2. Click on failed workflow run
3. Expand failed step to see detailed logs
4. Look for specific error messages

### Manual Deployment

If GitHub Actions continues to fail, deploy manually:

```bash
# On VPS
ssh root@72.60.176.200
cd /var/www/landscape-architecture-tool-dev
git fetch --all
git reset --hard origin/V1.00D
source venv-dev/bin/activate
pip install -r requirements.txt
cd frontend && npm ci --legacy-peer-deps && npm run build && cd ..
sudo systemctl restart landscape-backend-dev
sudo systemctl reload nginx
```

### Test VPS Access from Local Machine

Before running the workflow, verify you can access VPS:

```bash
# Test SSH with same key used in GitHub
ssh -i ~/.ssh/landscape_deploy root@72.60.176.200 "echo 'Connection successful'"

# If this fails, GitHub Actions will also fail
```

## Getting Help

### Documentation Resources
- [GitHub Secrets Configuration](GITHUB_SECRETS_CONFIGURATION.md)
- [SSH Key Setup](../../archive/vps-config/ssh_key_setup_instructions.md)
- [VPS Diagnostic Tools](../../scripts/deployment/)

### Useful Commands

**Check Workflow Status:**
```bash
# Using GitHub CLI
gh workflow list
gh run list --workflow=v1d-devdeploy.yml
gh run view <run-id> --log-failed
```

**VPS Diagnostic:**
```bash
# On VPS - comprehensive check
sudo systemctl status nginx landscape-backend-dev
sudo journalctl -xe
sudo netstat -tlnp | grep -E ':(22|8080|5001)'
```

**Network Testing:**
```bash
# From anywhere - test VPS accessibility
ping 72.60.176.200
nc -zv 72.60.176.200 22    # Test SSH port
nc -zv 72.60.176.200 8080  # Test HTTP port
curl -I http://72.60.176.200:8080
```

## Prevention Tips

1. **Always test SSH access** before deploying
2. **Keep dependencies updated** but test locally first
3. **Monitor VPS resources** regularly
4. **Use force_deploy option** sparingly
5. **Check logs** after each deployment
6. **Document any VPS changes** that might affect deployment

## Quick Reference: Required Secrets

| Secret | Required | Default | Purpose |
|--------|----------|---------|---------|
| `VPS_SSH_KEY` | ✅ Yes | None | SSH private key for VPS access |
| `VPS_HOST` | ⚪ No | `72.60.176.200` | VPS IP address or hostname |
| `VPS_USER` | ⚪ No | `root` | SSH username |

## Need More Help?

If you've tried these solutions and deployment still fails:

1. Review the complete workflow logs in GitHub Actions
2. Check VPS logs: `/var/log/nginx/error.log` and `journalctl`
3. Verify all GitHub secrets are correctly configured
4. Test SSH access manually from a machine with similar network setup
5. Consider reaching out to VPS provider if connectivity issues persist
