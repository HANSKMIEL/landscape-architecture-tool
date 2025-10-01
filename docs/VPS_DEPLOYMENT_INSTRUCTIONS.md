# VPS Deployment Instructions for V1.00D Development

## 🎯 Quick Start

This comprehensive deployment script handles the complete V1.00D development deployment to your VPS at http://72.60.176.200:8080.

## 📋 Prerequisites

### On VPS (72.60.176.200)
- Root access via SSH
- Git installed
- Python 3.x with venv
- Node.js and npm
- Nginx configured
- Systemd service configured (`landscape-backend.service`)

### Repository Setup
The repository should be cloned at `/var/www/landscape-architecture-tool` on the VPS.

## 🚀 Deployment Process

### Option 1: Direct Deployment on VPS (Recommended)

1. **Copy the script to your VPS:**
```bash
scp scripts/vps_deploy_v1d.sh root@72.60.176.200:/root/
```

2. **SSH to your VPS:**
```bash
ssh root@72.60.176.200
```

3. **Run the deployment script:**
```bash
cd /root
bash vps_deploy_v1d.sh
```

The script will automatically:
- ✅ Create backup of current deployment
- ✅ Pull latest V1.00D changes from GitHub
- ✅ Update Python dependencies
- ✅ Rebuild frontend with devdeploy branding
- ✅ Restart backend service
- ✅ Validate deployment with health checks
- ✅ Display comprehensive status report

### Option 2: Remote Execution

Execute the deployment remotely using SSH:

```bash
# From your local machine or CI/CD pipeline
ssh root@72.60.176.200 'bash -s' < scripts/vps_deploy_v1d.sh
```

### Option 3: Automated Cron Job

Set up automatic deployments:

```bash
# On VPS, add to crontab (crontab -e)
0 */6 * * * /root/vps_deploy_v1d.sh >> /var/log/landscape-deploy.log 2>&1
```

This will automatically deploy the latest V1.00D changes every 6 hours.

## 🔍 What the Script Does

### 1. Pre-deployment Checks
- ✓ Verifies root access
- ✓ Checks application directory exists
- ✓ Creates timestamped backup
- ✓ Shows current git status

### 2. Repository Update
- ✓ Fetches latest changes from GitHub
- ✓ Switches to V1.00D branch if needed
- ✓ Displays commits behind origin
- ✓ Resets to latest origin/V1.00D

### 3. Backend Updates
- ✓ Stops running services gracefully
- ✓ Kills any remaining processes
- ✓ Activates Python virtual environment
- ✓ Updates pip and dependencies
- ✓ Clears Python cache files
- ✓ Runs database migrations

### 4. Frontend Rebuild
- ✓ Clears npm and build caches
- ✓ Installs dependencies with `--legacy-peer-deps`
- ✓ Sets devdeploy environment variables
- ✓ Builds production version
- ✓ Verifies build artifacts

### 5. Service Management
- ✓ Reloads systemd configuration
- ✓ Starts backend service
- ✓ Enables service on boot
- ✓ Validates nginx configuration
- ✓ Reloads nginx

### 6. Health Checks
- ✓ Backend health endpoint (localhost)
- ✓ External access validation
- ✓ Frontend homepage check
- ✓ DevDeploy branding verification
- ✓ API endpoint testing
- ✓ Disk space check
- ✓ Memory usage check

## 📊 Expected Output

The script provides detailed, color-coded output:

```
╔════════════════════════════════════════════════════════════╗
║  🚀 VPS Deployment Script for V1.00D Development          ║
║  Landscape Architecture Tool - DevDeploy Environment       ║
╚════════════════════════════════════════════════════════════╝

[2025-10-01 12:00:00] Starting deployment process for V1.00D...
[SUCCESS] Backup created at /var/backups/landscape-20251001_120000
[INFO] Repository is 3 commits behind origin/V1.00D
[SUCCESS] Updated to: abc1234 Latest frontend improvements
[SUCCESS] Frontend build completed successfully
[SUCCESS] Backend service is running
[SUCCESS] Backend health check passed
[SUCCESS] External access working (HTTP 200)
[SUCCESS] Frontend is serving correctly
[SUCCESS] DevDeploy branding detected in live site

╔════════════════════════════════════════════════════════════╗
║  ✅ Deployment Complete!                                   ║
╚════════════════════════════════════════════════════════════╝

Deployment Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Repository updated to latest V1.00D
✓ Python dependencies updated
✓ Frontend rebuilt with devdeploy branding
✓ Backend service restarted and healthy
✓ Nginx configuration validated
✓ Backup created at: /var/backups/landscape-20251001_120000

Application URLs:
🌐 Frontend: http://72.60.176.200:8080/
🔧 Health:   http://72.60.176.200:8080/health
📊 API:      http://72.60.176.200:8080/api/

Deployment completed successfully! 🎉
```

## 🛠️ Troubleshooting

### Deployment Fails

**Check service logs:**
```bash
journalctl -u landscape-backend -n 50 --no-pager
```

**Check nginx logs:**
```bash
tail -f /var/log/nginx/error.log
```

**Manual service restart:**
```bash
systemctl restart landscape-backend
systemctl restart nginx
```

### Frontend Not Updating

**Clear browser cache or test with:**
```bash
curl -I http://72.60.176.200:8080/
```

**Verify dist directory:**
```bash
ls -lh /var/www/landscape-architecture-tool/frontend/dist/
```

### Backend Not Starting

**Check Python environment:**
```bash
cd /var/www/landscape-architecture-tool
source venv/bin/activate
python -c "import src.main; print('OK')"
```

**Test manually:**
```bash
cd /var/www/landscape-architecture-tool
source venv/bin/activate
FLASK_APP=src.main python -m flask run --host=0.0.0.0 --port=5000
```

### Restore from Backup

If deployment fails, restore from the automatic backup:

```bash
# List available backups
ls -lh /var/backups/landscape-*

# Restore latest backup
LATEST_BACKUP=$(ls -t /var/backups/landscape-* | head -1)
cp -r "$LATEST_BACKUP"/* /var/www/landscape-architecture-tool/

# Restart services
systemctl restart landscape-backend
systemctl restart nginx
```

## 🔐 Security Considerations

### Script Safety
- ✅ Runs with `set -e` (exits on error)
- ✅ Creates backup before changes
- ✅ Validates all critical steps
- ✅ Provides rollback capability

### Service Security
- Ensure systemd service runs with appropriate user
- Configure firewall rules for port 8080
- Use SSL/TLS for production deployments
- Rotate logs regularly

## 📈 Monitoring

### Real-time Logs
```bash
# Backend logs
journalctl -u landscape-backend -f

# Nginx access logs
tail -f /var/log/nginx/access.log

# Deployment logs (if using cron)
tail -f /var/log/landscape-deploy.log
```

### Health Checks
```bash
# Quick health check
curl http://72.60.176.200:8080/health

# API test
curl http://72.60.176.200:8080/api/dashboard/stats

# Frontend test
curl -I http://72.60.176.200:8080/
```

## 🔄 Rollback Procedure

If you need to rollback to a previous version:

```bash
# 1. Stop services
systemctl stop landscape-backend

# 2. Restore from backup
cp -r /var/backups/landscape-YYYYMMDD_HHMMSS/* /var/www/landscape-architecture-tool/

# 3. Restart services
systemctl start landscape-backend
systemctl restart nginx

# 4. Verify
curl http://72.60.176.200:8080/health
```

## 🎯 DevDeploy Branding

The V1.00D deployment includes special devdeploy branding to distinguish it from production:

- **Title**: "devdeploy - Landscape Architecture Tool (Development)"
- **Environment**: Development mode
- **URL**: http://72.60.176.200:8080

This is configured via environment variables:
```bash
VITE_APP_TITLE="devdeploy - Landscape Architecture Tool (Development)"
VITE_APP_ENV="development"
VITE_API_URL="http://72.60.176.200:8080/api"
```

## 📞 Support

### Useful Commands

**Check deployment status:**
```bash
systemctl status landscape-backend
nginx -t
df -h
free -h
```

**View recent deployments:**
```bash
ls -lht /var/backups/landscape-* | head -10
```

**Git status:**
```bash
cd /var/www/landscape-architecture-tool
git branch --show-current
git log -5 --oneline
```

## 🚀 Next Steps

After successful deployment:

1. **Verify the deployment:**
   - Visit http://72.60.176.200:8080/
   - Check that "devdeploy" branding is visible
   - Test key functionality

2. **Set up monitoring:**
   - Configure uptime monitoring
   - Set up log aggregation
   - Enable email/Slack notifications

3. **Automate deployments:**
   - Add cron job for automatic updates
   - Integrate with GitHub webhooks
   - Set up CI/CD pipeline

4. **Document changes:**
   - Update deployment log
   - Note any custom configurations
   - Track version numbers

---

**Script Location**: `scripts/vps_deploy_v1d.sh`  
**Last Updated**: October 1, 2025  
**Version**: 1.0.0  
**Branch**: V1.00D (Development)
