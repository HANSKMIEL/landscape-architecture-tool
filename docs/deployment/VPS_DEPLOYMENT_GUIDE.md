# VPS Deployment Guide - Complete Step-by-Step Instructions

## 🚨 Issue Identified

**Problem:** The VPS at http://72.60.176.200:8080/ is showing an outdated deployment from September 25, 2025.

**Current Status:**
- ✅ VPS is accessible and responding
- ✅ Backend health endpoint working (version 2.0.0)
- ✅ Nginx is serving content correctly
- ❌ Code is outdated (last deployed: Sept 25, 2025)
- ❌ Latest changes from V1.00D branch not reflected

**Root Cause:**
The VPS repository needs to be updated and the frontend needs to be rebuilt with the latest changes from the V1.00D development branch.

---

## 🎯 Quick Fix (Most Common Solution)

If you just need to deploy the latest changes **immediately**, follow these steps:

### Step 1: Connect to VPS

```bash
ssh root@72.60.176.200
```

### Step 2: Run One-Line Deployment Command

Copy and paste this entire command:

```bash
cd /var/www/landscape-architecture-tool && \
git fetch --all && \
git reset --hard origin/V1.00D && \
systemctl stop landscape-backend && \
pkill -f gunicorn && \
source venv/bin/activate && \
pip install -r requirements.txt && \
cd frontend && npm ci --legacy-peer-deps && npm run build && cd .. && \
systemctl start landscape-backend && \
sleep 5 && \
systemctl status landscape-backend
```

### Step 3: Verify Deployment

```bash
# Check backend health
curl http://localhost:5000/health

# Check external access
curl http://72.60.176.200:8080/health

# Check that frontend is updated
curl http://72.60.176.200:8080/ | head -20
```

**Expected Result:** You should see the latest version and the frontend should show recent changes.

---

## 🔍 Diagnostic Approach (If Quick Fix Doesn't Work)

### Step 1: Run Diagnostic Script

First, let's understand what's happening on the VPS:

```bash
# On your local machine, copy the diagnostic script to VPS
scp scripts/vps_diagnostic.sh root@72.60.176.200:/tmp/

# SSH to VPS and run diagnostic
ssh root@72.60.176.200
bash /tmp/vps_diagnostic.sh
```

The diagnostic script will check:
- ✅ Repository status and current branch
- ✅ Service status (landscape-backend, nginx)
- ✅ Python environment and dependencies
- ✅ Frontend build status and age
- ✅ Network and port accessibility
- ✅ How many commits behind origin/V1.00D
- ✅ Recent error logs

### Step 2: Analyze Diagnostic Output

The diagnostic will tell you exactly what's wrong:

- **If "Repository is X commits behind"**: Need to update code
- **If "Frontend build is older than 7 days"**: Need to rebuild frontend
- **If "Backend service NOT running"**: Need to start service
- **If "Virtual environment missing"**: Need to create venv

---

## 🚀 Automated Deployment (Recommended)

### Option A: Using Enhanced Deployment Script

1. **Copy the automated script to VPS:**
   ```bash
   scp scripts/deploy_vps_automated.sh root@72.60.176.200:/root/
   ```

2. **SSH to VPS and run it:**
   ```bash
   ssh root@72.60.176.200
   bash /root/deploy_vps_automated.sh
   ```

3. **The script will automatically:**
   - ✅ Create a backup before deploying
   - ✅ Fetch latest changes from V1.00D
   - ✅ Stop services gracefully
   - ✅ Update Python dependencies
   - ✅ Rebuild frontend
   - ✅ Start services
   - ✅ Verify deployment
   - ✅ Provide rollback info if something fails

### Option B: Set Up Quick Deploy Script (For Future Use)

Create a simple deployment script on the VPS for quick future updates:

```bash
# SSH to VPS
ssh root@72.60.176.200

# Create quick deploy script
cat > /root/quick_deploy.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting deployment..."
cd /var/www/landscape-architecture-tool
git fetch --all && git reset --hard origin/V1.00D
systemctl stop landscape-backend
pkill -f gunicorn || true
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm ci --legacy-peer-deps && npm run build && cd ..
systemctl start landscape-backend
echo "✅ Deployment complete!"
echo "🏥 Health check:"
sleep 3
curl http://localhost:5000/health
EOF

chmod +x /root/quick_deploy.sh
```

**Then anytime you need to deploy:**
```bash
ssh root@72.60.176.200 '/root/quick_deploy.sh'
```

---

## 🔄 Set Up Automatic Deployments

To ensure the VPS always shows the latest changes, set up automatic deployments:

### Cron Job for Regular Updates

```bash
# SSH to VPS
ssh root@72.60.176.200

# Add to crontab (updates every 4 hours)
crontab -e

# Add this line:
0 */4 * * * /root/quick_deploy.sh >> /var/log/landscape-deploy.log 2>&1
```

This will automatically deploy the latest changes every 4 hours.

### Alternative: Webhook-Based Deployment

For immediate deployments when code is pushed:

1. **Set up webhook on VPS:**
   ```bash
   # Copy webhook script
   scp scripts/webhook_deploy.sh root@72.60.176.200:/root/
   chmod +x /root/webhook_deploy.sh
   ```

2. **Configure GitHub webhook:**
   - Go to repository Settings → Webhooks
   - Add webhook pointing to: `http://72.60.176.200:9000/webhook`
   - Set secret from API key provided
   - Events: Push events

---

## 🛠️ Manual Deployment Steps (Detailed)

If you prefer step-by-step manual control:

### 1. Connect to VPS
```bash
ssh root@72.60.176.200
```

### 2. Navigate to Application Directory
```bash
cd /var/www/landscape-architecture-tool
```

### 3. Check Current Status
```bash
# See current branch and commit
git branch --show-current
git log -1 --oneline

# Check service status
systemctl status landscape-backend
```

### 4. Update Repository
```bash
# Fetch latest changes
git fetch --all

# Check how many commits behind
git rev-list HEAD..origin/V1.00D --count

# Update to latest V1.00D
git reset --hard origin/V1.00D

# Verify update
git log -1 --oneline
```

### 5. Stop Services
```bash
# Stop backend service
systemctl stop landscape-backend

# Kill any remaining gunicorn processes
pkill -f gunicorn

# Verify stopped
ps aux | grep gunicorn
```

### 6. Update Python Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Rebuild Frontend
```bash
# Navigate to frontend
cd frontend

# Clean install dependencies
npm ci --legacy-peer-deps

# Build production assets
npm run build

# Verify build
ls -lh dist/

# Return to app root
cd ..
```

### 8. Start Services
```bash
# Reload systemd
systemctl daemon-reload

# Start backend
systemctl start landscape-backend

# Enable on boot
systemctl enable landscape-backend

# Check status
systemctl status landscape-backend
```

### 9. Verify Deployment
```bash
# Test backend locally
curl http://localhost:5000/health

# Test external access
curl http://72.60.176.200:8080/health

# Check frontend
curl -I http://72.60.176.200:8080/

# View service logs if issues
journalctl -u landscape-backend -n 50
```

---

## 🔍 Troubleshooting Common Issues

### Issue 1: "Backend service fails to start"

**Check logs:**
```bash
journalctl -u landscape-backend -n 100 --no-pager
```

**Common causes:**
- Port 5000 already in use
- Database connection issues
- Missing environment variables
- Python dependency errors

**Solutions:**
```bash
# Kill processes on port 5000
lsof -ti:5000 | xargs kill -9

# Check environment
cat /etc/systemd/system/landscape-backend.service

# Reinstall dependencies
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
```

### Issue 2: "Frontend not updating"

**Check build:**
```bash
cd /var/www/landscape-architecture-tool/frontend
ls -lh dist/index.html

# Check modification time
stat dist/index.html
```

**Solutions:**
```bash
# Clear old build
rm -rf dist/

# Rebuild
npm ci --legacy-peer-deps
npm run build

# Verify new build
stat dist/index.html
```

### Issue 3: "External access fails but local works"

**Check nginx:**
```bash
# Check nginx status
systemctl status nginx

# Test nginx config
nginx -t

# View nginx error logs
tail -50 /var/log/nginx/error.log
```

**Solutions:**
```bash
# Restart nginx
systemctl restart nginx

# Check if port 8080 is open
ss -tuln | grep 8080

# Test from localhost
curl http://localhost:8080/health
```

### Issue 4: "Git pull/fetch fails"

**Check git status:**
```bash
cd /var/www/landscape-architecture-tool
git status
git remote -v
```

**Solutions:**
```bash
# Reset any local changes
git reset --hard HEAD
git clean -fd

# Fetch again
git fetch --all

# If still fails, check network
ping github.com
```

### Issue 5: "npm build fails"

**Check errors:**
```bash
cd frontend
npm ci --legacy-peer-deps 2>&1 | tee /tmp/npm-error.log
```

**Solutions:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# If memory issues, increase Node memory
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

---

## 📊 Verification Checklist

After deployment, verify everything is working:

- [ ] Backend service running: `systemctl status landscape-backend`
- [ ] Health endpoint responding: `curl http://localhost:5000/health`
- [ ] External health working: `curl http://72.60.176.200:8080/health`
- [ ] Frontend accessible: `curl http://72.60.176.200:8080/`
- [ ] Recent commit deployed: `git log -1 --oneline`
- [ ] Frontend build is recent: `stat frontend/dist/index.html`
- [ ] No errors in logs: `journalctl -u landscape-backend -n 20`
- [ ] Nginx serving correctly: `systemctl status nginx`

---

## 📞 Getting Help

If you encounter issues not covered here:

1. **Run the diagnostic script** and share the output
2. **Check the logs**: `journalctl -u landscape-backend -n 100`
3. **Test health endpoint**: `curl -v http://localhost:5000/health`
4. **Check service status**: `systemctl status landscape-backend nginx`

---

## 🔒 Security Notes

- Always test deployments in development first
- Keep backups before deploying (automated script does this)
- Monitor logs after deployment
- Set up alerts for service failures
- Use environment variables for secrets (never in code)

---

## 📝 Summary

**To fix your current issue:**

```bash
# Quick fix (run on VPS)
ssh root@72.60.176.200
cd /var/www/landscape-architecture-tool && \
git fetch --all && git reset --hard origin/V1.00D && \
systemctl stop landscape-backend && pkill -f gunicorn && \
source venv/bin/activate && pip install -r requirements.txt && \
cd frontend && npm ci --legacy-peer-deps && npm run build && cd .. && \
systemctl start landscape-backend
```

**For future deployments:**
- Use `/root/quick_deploy.sh` for manual updates
- Set up cron job for automatic updates
- Use webhook for instant deployments on push

Your deployment should now show the latest changes! 🎉
