# VPS Clean Reinstall Instructions - V1.00D

**Date**: October 2, 2025  
**Branch**: V1.00D  
**VPS IP**: 72.60.176.200  
**Latest Commit**: 8de88e3

---

## ✅ Pre-Reinstall Verification Complete

### Git Status Verified
- ✅ Working tree clean (no uncommitted changes)
- ✅ No untracked files
- ✅ Local and remote in sync (0 commits ahead/behind)
- ✅ All critical files present and pushed

### Recent Commits (Last 5)
```
8de88e3 - Add test report after Hostinger firewall reset - all ports still blocked
9b1f00d - Add comprehensive VPS root diagnostic workflow
1f5366e - docs: Add comprehensive VPS access test report after restart
72a631d - docs: Add VPS access test report after firewall activation
be045b3 - feat: Add VPS external access test workflow
```

### Critical Files Verified
- ✅ `src/main.py` (50 KB)
- ✅ `requirements.txt` (6.1 KB)
- ✅ `frontend/package.json` (3 KB)
- ✅ `.github/workflows/v1d-devdeploy.yml` (16.8 KB)

---

## 🎯 Reinstall Instructions

### Method 1: Via Hostinger Web Console (RECOMMENDED)

1. **Login to Hostinger Panel**
   - Go to https://hpanel.hostinger.com
   - Select your VPS (72.60.176.200)

2. **Open Web Console**
   - Look for "Terminal" or "Console" button
   - This opens a web-based terminal directly on the VPS

3. **Run the Reinstall Script**
   
   Copy and paste this entire script into the console:

```bash
#!/bin/bash
# V1.00D Clean Reinstall Script
# Date: October 2, 2025
# Verified: All changes committed and pushed

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  V1.00D Clean Reinstall Starting...                        ║"
echo "╚════════════════════════════════════════════════════════════╝"

# 1. Stop services
echo ""
echo "=== STEP 1: Stopping Services ==="
systemctl stop nginx 2>/dev/null || echo "Nginx not running"
systemctl stop landscape-backend-dev 2>/dev/null || echo "Backend not running"
sleep 2
echo "✅ Services stopped"

# 2. Backup database
echo ""
echo "=== STEP 2: Backing Up Database ==="
BACKUP_DIR="/root/vps-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ -d "/var/www/landscape-architecture-tool-dev/instance" ]; then
    cp -r /var/www/landscape-architecture-tool-dev/instance "$BACKUP_DIR/"
    echo "✅ Database backed up to: $BACKUP_DIR"
else
    echo "⚠️  No database found to backup"
fi

# 3. Backup environment
if [ -f "/var/www/landscape-architecture-tool-dev/.env" ]; then
    cp /var/www/landscape-architecture-tool-dev/.env "$BACKUP_DIR/"
    echo "✅ Environment file backed up"
fi

# 4. Remove old installation
echo ""
echo "=== STEP 3: Removing Old Installation ==="
rm -rf /var/www/landscape-architecture-tool-dev
echo "✅ Old installation removed"

# 5. Clone fresh from GitHub
echo ""
echo "=== STEP 4: Cloning Fresh Code from GitHub ==="
cd /var/www
git clone -b V1.00D https://github.com/HANSKMIEL/landscape-architecture-tool.git landscape-architecture-tool-dev
cd landscape-architecture-tool-dev
CLONED_COMMIT=$(git rev-parse --short HEAD)
echo "✅ Cloned commit: $CLONED_COMMIT (should be 8de88e3)"

# 6. Install Python dependencies
echo ""
echo "=== STEP 5: Installing Python Dependencies ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# 7. Build frontend
echo ""
echo "=== STEP 6: Building Frontend ==="
cd frontend
npm ci --legacy-peer-deps
npm run build
cd ..
echo "✅ Frontend built"

# 8. Setup database
echo ""
echo "=== STEP 7: Setting Up Database ==="
mkdir -p instance
source venv/bin/activate

# Initialize database
PYTHONPATH=. flask --app src.main db upgrade

# Seed initial data
PYTHONPATH=. python3 << 'PYEOF'
from src.utils.db_init import init_db
from src.main import app
with app.app_context():
    init_db()
print("✅ Database initialized with sample data")
PYEOF

echo "✅ Database setup complete"

# 9. Verify Nginx config exists
echo ""
echo "=== STEP 8: Verifying Nginx Configuration ==="
if [ ! -f "/etc/nginx/sites-available/landscape-dev" ]; then
    echo "⚠️  Nginx config missing, creating..."
    cat > /etc/nginx/sites-available/landscape-dev << 'NGINXCONF'
server {
    listen 8080;
    server_name _;

    location / {
        root /var/www/landscape-architecture-tool-dev/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://127.0.0.1:5001/health;
        proxy_set_header Host $host;
    }
}
NGINXCONF
    ln -sf /etc/nginx/sites-available/landscape-dev /etc/nginx/sites-enabled/
    echo "✅ Nginx config created"
else
    echo "✅ Nginx config exists"
fi

# 10. Verify backend service exists
echo ""
echo "=== STEP 9: Verifying Backend Service ==="
if [ ! -f "/etc/systemd/system/landscape-backend-dev.service" ]; then
    echo "⚠️  Backend service missing, creating..."
    cat > /etc/systemd/system/landscape-backend-dev.service << 'SERVICECONF'
[Unit]
Description=Landscape Architecture Tool Backend (Development)
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/var/www/landscape-architecture-tool-dev
Environment="PATH=/var/www/landscape-architecture-tool-dev/venv/bin"
Environment="PYTHONPATH=/var/www/landscape-architecture-tool-dev"
Environment="FLASK_ENV=production"
ExecStart=/var/www/landscape-architecture-tool-dev/venv/bin/gunicorn \
    --bind 0.0.0.0:5001 \
    --workers 4 \
    --timeout 120 \
    --log-level info \
    src.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICECONF
    systemctl daemon-reload
    echo "✅ Backend service created"
else
    echo "✅ Backend service exists"
    systemctl daemon-reload
fi

# 11. Start services
echo ""
echo "=== STEP 10: Starting Services ==="
systemctl enable landscape-backend-dev
systemctl start landscape-backend-dev
systemctl restart nginx

sleep 5

# 12. Verify services are running
echo ""
echo "=== STEP 11: Verifying Services ==="
systemctl is-active landscape-backend-dev && echo "✅ Backend is running" || echo "❌ Backend failed to start"
systemctl is-active nginx && echo "✅ Nginx is running" || echo "❌ Nginx failed to start"

# 13. Test endpoints
echo ""
echo "=== STEP 12: Testing Endpoints ==="
echo "Testing frontend (localhost:8080)..."
curl -s -o /dev/null -w "Frontend: HTTP %{http_code}\n" http://localhost:8080/

echo "Testing backend (localhost:5001/health)..."
curl -s http://localhost:5001/health | head -5

echo ""
echo "Listening ports:"
ss -tulpn | grep -E ':(8080|5001)'

# 14. Summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ V1.00D REINSTALL COMPLETE                             ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Backup Location: $BACKUP_DIR"
echo "║  Installed Commit: $CLONED_COMMIT                         ║"
echo "║                                                            ║"
echo "║  INTERNAL ACCESS (from VPS):                              ║"
echo "║  • Frontend: http://localhost:8080 ✅                     ║"
echo "║  • Backend:  http://localhost:5001 ✅                     ║"
echo "║                                                            ║"
echo "║  EXTERNAL ACCESS:                                         ║"
echo "║  • http://72.60.176.200:8080 - ⚠️  FIREWALL BLOCKED      ║"
echo "║                                                            ║"
echo "║  NEXT STEP: Fix Hostinger firewall attachment!           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
```

---

### Method 2: Via GitHub Actions (Alternative)

If the web console doesn't work, we can trigger a GitHub Actions workflow that does the reinstall. However, this requires fixing the firewall first since GitHub Actions needs SSH access.

---

## ⚠️ Important Notes

### Before Reinstall
- ✅ All code is committed and pushed to GitHub
- ✅ Database will be backed up to `/root/vps-backup-YYYYMMDD_HHMMSS/`
- ✅ Environment file will be backed up

### After Reinstall
- Services will be running internally on VPS
- **Firewall still needs to be fixed** for external access
- The application will work on `localhost:8080` and `localhost:5001` from within the VPS

### Known Issue
The **Hostinger firewall is not attached/active** on the VPS. Even after reinstall:
- ✅ Internal access will work (from VPS itself)
- ❌ External access will be blocked (from internet)

**You MUST fix the firewall attachment in Hostinger panel** before external access works.

---

## 🔍 Verification After Reinstall

From within the VPS (web console), run:

```bash
# Check services
systemctl status landscape-backend-dev
systemctl status nginx

# Test endpoints
curl http://localhost:8080/
curl http://localhost:5001/health

# Check listening ports
ss -tulpn | grep -E ':(8080|5001)'

# View logs
tail -50 /var/log/landscape-backend-dev-error.log
journalctl -u landscape-backend-dev -n 50
```

---

## 🆘 Troubleshooting

### If Backend Fails to Start
```bash
# Check logs
journalctl -u landscape-backend-dev -n 100

# Check if Python dependencies installed
/var/www/landscape-architecture-tool-dev/venv/bin/pip list

# Manually test
cd /var/www/landscape-architecture-tool-dev
source venv/bin/activate
PYTHONPATH=. python src/main.py
```

### If Frontend Build Fails
```bash
# Check Node/npm versions
node --version
npm --version

# Rebuild manually
cd /var/www/landscape-architecture-tool-dev/frontend
rm -rf node_modules dist
npm ci --legacy-peer-deps
npm run build
```

### If Database Fails
```bash
cd /var/www/landscape-architecture-tool-dev
source venv/bin/activate
PYTHONPATH=. flask --app src.main db current
PYTHONPATH=. flask --app src.main db upgrade
```

---

## 📝 Related Documentation

- **VPS Access Diagnostic**: `reports/VPS_ACCESS_TEST_AFTER_FIREWALL_RESET.md`
- **Firewall Troubleshooting**: `docs/solutions/HOSTINGER_FIREWALL_TROUBLESHOOTING.md`
- **Deployment Workflow**: `.github/workflows/v1d-devdeploy.yml`

---

**Status**: Ready for reinstall - all changes backed up in GitHub
