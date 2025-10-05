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

## 📚 Full Documentation

See `VPS_DEPLOYMENT_FIX.md` for complete details and troubleshooting.