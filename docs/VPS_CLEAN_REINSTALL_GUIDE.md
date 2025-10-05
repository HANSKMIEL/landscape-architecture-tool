# VPS Clean Reinstall Guide

## Overview
This guide provides instructions for performing a clean reinstallation of the Landscape Architecture Tool on the VPS from the V1.00D branch. The reinstallation script will backup, delete, and reinstall all necessary files.

## Prerequisites

### VPS Access
- **VPS IP**: 72.60.176.200
- **VPS Port**: 8080
- **SSH User**: root
- **Application Path**: /var/www/landscape-architecture-tool

### Required Software on VPS
- Git
- Python 3.8+
- Node.js 16+ and npm
- systemd (for service management)

## Quick Start

### Option 1: Direct SSH Execution (Recommended)

Connect to your VPS and run the reinstall script:

```bash
# SSH into the VPS
ssh root@72.60.176.200

# Download and run the clean reinstall script
cd /tmp
curl -O https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_clean_reinstall.sh
chmod +x vps_clean_reinstall.sh
sudo ./vps_clean_reinstall.sh
```

### Option 2: Manual Step-by-Step Execution

If you prefer to execute each step manually or the automated script encounters issues:

```bash
# SSH into the VPS
ssh root@72.60.176.200

# 1. Create backup
mkdir -p /var/backups/landscape-architecture-tool/backup_$(date +%Y%m%d_%H%M%S)
cd /var/www
tar -czf /var/backups/landscape-architecture-tool/backup_$(date +%Y%m%d_%H%M%S)/app_backup.tar.gz landscape-architecture-tool

# 2. Stop services
systemctl stop landscape-backend 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
sleep 5

# 3. Delete old installation
rm -rf /var/www/landscape-architecture-tool

# 4. Clone fresh from V1.00D branch
cd /var/www
git clone --branch V1.00D --single-branch https://github.com/HANSKMIEL/landscape-architecture-tool.git

# 5. Setup Python environment
cd /var/www/landscape-architecture-tool
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. Setup environment variables
cp .env.example .env
# Edit .env with your configuration: nano .env

# 7. Build frontend
cd frontend
npm ci
npm run build
cd ..

# 8. Setup systemd service (see service configuration below)

# 9. Set permissions
chown -R www-data:www-data /var/www/landscape-architecture-tool
chmod +x wsgi.py

# 10. Start service
systemctl daemon-reload
systemctl start landscape-backend
systemctl enable landscape-backend
```

## Systemd Service Configuration

Create the systemd service file at `/etc/systemd/system/landscape-backend.service`:

```ini
[Unit]
Description=Landscape Architecture Tool Backend API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/landscape-architecture-tool
Environment=PATH=/var/www/landscape-architecture-tool/venv/bin
Environment=FLASK_ENV=production
Environment=DATABASE_URL=sqlite:///landscape_architecture_prod.db
Environment=FLASK_APP=wsgi:application
ExecStart=/var/www/landscape-architecture-tool/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 --timeout 120 wsgi:application
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## What the Clean Reinstall Script Does

### Step 1: Create Backup
- Creates timestamped backup in `/var/backups/landscape-architecture-tool/`
- Backs up application directory, database, and .env file
- Keeps only the last 5 backups

### Step 2: Stop Services
- Stops systemd service gracefully
- Kills remaining gunicorn processes
- Ensures clean shutdown

### Step 3: Delete Old Installation
- Preserves .env file temporarily
- Removes entire application directory
- Clears all old files

### Step 4: Clone Repository
- Clones fresh copy from V1.00D branch
- Uses single-branch clone for efficiency
- Shows current commit hash

### Step 5: Restore Configuration
- Restores preserved .env file
- Creates .env from example if needed

### Step 6: Setup Python Environment
- Creates fresh virtual environment
- Upgrades pip
- Installs all Python dependencies

### Step 7: Initialize Database
- Restores database from backup if available
- Otherwise, prepares for fresh initialization

### Step 8: Setup Frontend
- Installs Node.js dependencies
- Builds production frontend bundle

### Step 9: Setup Systemd Service
- Creates/updates systemd service file
- Configures service parameters

### Step 10: Set Permissions
- Sets www-data ownership
- Makes scripts executable

### Step 11: Start Services
- Reloads systemd daemon
- Starts and enables service

### Step 12: Verify Installation
- Checks service status
- Tests health endpoint
- Verifies external access
- Shows detailed status

## Verification Steps

After installation completes, verify the deployment:

### 1. Check Service Status
```bash
systemctl status landscape-backend
```

Expected output: Service should be "active (running)"

### 2. Test Health Endpoint (Local)
```bash
curl http://localhost:5000/health
```

Expected output: JSON with status and version information

### 3. Test Health Endpoint (External)
```bash
curl http://72.60.176.200:8080/health
```

Expected output: Same JSON response as local test

### 4. Check Application in Browser
Navigate to: http://72.60.176.200:8080/

Expected: Application loads with working interface

### 5. Monitor Logs
```bash
# Real-time log monitoring
journalctl -u landscape-backend -f

# View recent logs
journalctl -u landscape-backend -n 100 --no-pager
```

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
journalctl -u landscape-backend -n 50 --no-pager
```

**Common issues:**
- Missing Python dependencies: `source venv/bin/activate && pip install -r requirements.txt`
- Permission issues: `chown -R www-data:www-data /var/www/landscape-architecture-tool`
- Port conflict: Check if port 5000 is already in use: `netstat -tlnp | grep 5000`

### Health Endpoint Not Responding

**Check if service is running:**
```bash
systemctl status landscape-backend
```

**Check if port is listening:**
```bash
netstat -tlnp | grep 5000
```

**Test with verbose curl:**
```bash
curl -v http://localhost:5000/health
```

### External Access Not Working

**Check firewall:**
```bash
# UFW
sudo ufw status
sudo ufw allow 8080/tcp

# iptables
sudo iptables -L -n | grep 8080
```

**Check nginx/reverse proxy configuration:**
```bash
nginx -t
systemctl status nginx
```

### Frontend Not Loading

**Check frontend build:**
```bash
ls -la /var/www/landscape-architecture-tool/frontend/dist/
# or
ls -la /var/www/landscape-architecture-tool/frontend/build/
```

**Rebuild frontend if needed:**
```bash
cd /var/www/landscape-architecture-tool/frontend
npm ci
npm run build
```

## Rollback Procedure

If the new installation has issues, you can rollback to the backup:

```bash
# Stop current service
systemctl stop landscape-backend

# Find latest backup
ls -lt /var/backups/landscape-architecture-tool/

# Restore from backup (replace TIMESTAMP with actual timestamp)
cd /var/www
rm -rf landscape-architecture-tool
tar -xzf /var/backups/landscape-architecture-tool/backup_TIMESTAMP/app_backup.tar.gz

# Restore database
cp /var/backups/landscape-architecture-tool/backup_TIMESTAMP/landscape_architecture_prod_backup.db \
   /var/www/landscape-architecture-tool/landscape_architecture_prod.db

# Restore .env
cp /var/backups/landscape-architecture-tool/backup_TIMESTAMP/.env.backup \
   /var/www/landscape-architecture-tool/.env

# Restart service
systemctl start landscape-backend
```

## Testing Checklist

After reinstallation, verify these features:

- [ ] **Service Running**: `systemctl status landscape-backend` shows active
- [ ] **Health Endpoint**: `curl http://localhost:5000/health` returns JSON
- [ ] **External Access**: `curl http://72.60.176.200:8080/health` returns JSON
- [ ] **Frontend Loads**: Browser shows application at http://72.60.176.200:8080/
- [ ] **API Endpoints**: Test key API endpoints (suppliers, plants, projects)
- [ ] **Database Access**: Application can read/write to database
- [ ] **No Error Logs**: `journalctl -u landscape-backend -n 50` shows no errors
- [ ] **Navigation Works**: Can navigate between different pages
- [ ] **CRUD Operations**: Can create/read/update/delete records

## Maintenance Commands

### Update from V1.00D Branch
```bash
cd /var/www/landscape-architecture-tool
git fetch --all
git reset --hard origin/V1.00D
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm ci && npm run build && cd ..
systemctl restart landscape-backend
```

### View Service Logs
```bash
# Follow logs in real-time
journalctl -u landscape-backend -f

# View last 100 lines
journalctl -u landscape-backend -n 100

# View logs for specific time range
journalctl -u landscape-backend --since "2024-10-01" --until "2024-10-02"
```

### Restart Service
```bash
systemctl restart landscape-backend
```

### Stop Service
```bash
systemctl stop landscape-backend
```

### Check Service Status
```bash
systemctl status landscape-backend
```

## Security Considerations

1. **Environment Variables**: Ensure `.env` file contains secure secrets
2. **File Permissions**: All files owned by www-data with appropriate permissions
3. **Firewall**: Only necessary ports should be open (22, 8080)
4. **HTTPS**: Consider setting up SSL/TLS for production use
5. **Database**: Ensure database backups are regular and secure

## Support and Documentation

- **Main Documentation**: See `/var/www/landscape-architecture-tool/README.md`
- **API Documentation**: Check `/var/www/landscape-architecture-tool/docs/`
- **Deployment Guide**: `/var/www/landscape-architecture-tool/DEPLOYMENT.md`
- **VPS Deployment Fix**: `/var/www/landscape-architecture-tool/VPS_DEPLOYMENT_FIX.md`

## Automated Updates (Optional)

To set up automated updates from V1.00D branch:

```bash
# Create cron job
crontab -e

# Add this line to update every 6 hours
0 */6 * * * /var/www/landscape-architecture-tool/scripts/webhook_deploy.sh >> /var/log/landscape-deploy.log 2>&1
```

## Contact Information

If you encounter issues not covered in this guide:

1. Check the repository issues: https://github.com/HANSKMIEL/landscape-architecture-tool/issues
2. Review deployment documentation in the repository
3. Check service logs for specific error messages
4. Verify all prerequisites are installed correctly

---

**Last Updated**: October 2024  
**Script Version**: 1.0.0  
**Compatible Branch**: V1.00D
