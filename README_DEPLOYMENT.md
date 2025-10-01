# Quick Deployment Guide

## 🚨 VPS Not Showing Latest Changes? 

**Problem**: http://72.60.176.200:8080/ shows old version  
**Solution**: Run the deployment commands below

### 🚀 Immediate Fix (Run on VPS)

```bash
# SSH to VPS
ssh root@72.60.176.200

# Quick deployment command (V1.00D branch)
cd /var/www/landscape-architecture-tool && \
git fetch --all && \
git reset --hard origin/V1.00D && \
systemctl stop landscape-backend && \
pkill -f gunicorn && \
source venv/bin/activate && \
pip install -r requirements.txt && \
cd frontend && npm ci --legacy-peer-deps && npm run build && cd .. && \
systemctl start landscape-backend && \
systemctl status landscape-backend
```

### ✅ Verify Fix

```bash
# Check health
curl http://72.60.176.200:8080/health

# Check frontend
curl -I http://72.60.176.200:8080/
```

### 🔧 Automated Solution

For ongoing deployments, copy this script to VPS and run it:

```bash
# On VPS: Create automated deployment script
cat > /root/quick_deploy.sh << 'EOF'
#!/bin/bash
cd /var/www/landscape-architecture-tool
git fetch --all && git reset --hard origin/V1.00D
systemctl stop landscape-backend
pkill -f gunicorn
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm ci --legacy-peer-deps && npm run build && cd ..
systemctl start landscape-backend
echo "✅ Deployment complete - Check: http://72.60.176.200:8080/health"
EOF

chmod +x /root/quick_deploy.sh

# Run it
/root/quick_deploy.sh
```

### 📋 Add to cron for automatic updates

```bash
# Add to crontab (updates every 4 hours)
echo "0 */4 * * * /root/quick_deploy.sh >> /var/log/deploy.log 2>&1" | crontab -
```

## 🔍 Troubleshooting

### If deployment fails:

1. **Run diagnostic script:**
   ```bash
   scp scripts/vps_diagnostic.sh root@72.60.176.200:/tmp/
   ssh root@72.60.176.200 "bash /tmp/vps_diagnostic.sh"
   ```

2. **Check service logs:**
   ```bash
   ssh root@72.60.176.200 "journalctl -u landscape-backend -n 50"
   ```

3. **Verify services are running:**
   ```bash
   ssh root@72.60.176.200 "systemctl status landscape-backend nginx"
   ```

### Common Issues:

**Issue:** Backend won't start  
**Fix:** Check logs, kill port 5000, restart service

**Issue:** Frontend not updating  
**Fix:** Clear dist/ and rebuild: `rm -rf frontend/dist && cd frontend && npm run build`

**Issue:** Git fetch fails  
**Fix:** Check network, reset repo: `git reset --hard HEAD && git fetch --all`

## 🛠️ Helper Scripts

We've created helper scripts to make deployment easier:

- **`scripts/vps_ssh_helper.sh`** - Interactive menu for common VPS tasks
- **`scripts/vps_diagnostic.sh`** - Full diagnostic report
- **`scripts/deploy_vps_automated.sh`** - Automated deployment with backup

**Quick usage:**
```bash
# Interactive menu
./scripts/vps_ssh_helper.sh

# Or direct commands
./scripts/vps_ssh_helper.sh quick-deploy
./scripts/vps_ssh_helper.sh diagnose
./scripts/vps_ssh_helper.sh status
```

## 📚 Full Documentation

- **Quick Fix:** This file (README_DEPLOYMENT.md)
- **Complete Guide:** `VPS_DEPLOYMENT_GUIDE.md`
- **Quick Reference:** `VPS_DEPLOYMENT_SOLUTION.md`
- **Original Fix:** `VPS_DEPLOYMENT_FIX.md`