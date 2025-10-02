# VPS Clean Reinstall - Quick Reference

## 🚀 One-Line Reinstall Command

```bash
ssh root@72.60.176.200 "bash <(curl -fsSL https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_clean_reinstall.sh)"
```

## 📋 Manual Reinstall (Step-by-Step)

### 1. Backup & Stop
```bash
ssh root@72.60.176.200
cd /var/www
tar -czf /var/backups/landscape-backup-$(date +%Y%m%d_%H%M%S).tar.gz landscape-architecture-tool
systemctl stop landscape-backend
pkill -f gunicorn
```

### 2. Clean & Clone
```bash
rm -rf /var/www/landscape-architecture-tool
cd /var/www
git clone --branch V1.00D https://github.com/HANSKMIEL/landscape-architecture-tool.git
cd landscape-architecture-tool
```

### 3. Setup Backend
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Setup Frontend
```bash
cd frontend
npm ci --legacy-peer-deps
npm run build
cd ..
```

### 5. Start Service
```bash
chown -R www-data:www-data /var/www/landscape-architecture-tool
systemctl daemon-reload
systemctl start landscape-backend
systemctl enable landscape-backend
```

## ✅ Verification Commands

```bash
# Service status
systemctl status landscape-backend

# Health check (local)
curl http://localhost:5000/health

# Health check (external)
curl http://72.60.176.200:8080/health

# View logs
journalctl -u landscape-backend -f
```

## 🔧 Quick Fixes

### Service Won't Start
```bash
journalctl -u landscape-backend -n 50
source venv/bin/activate && pip install -r requirements.txt
systemctl restart landscape-backend
```

### Health Endpoint Not Responding
```bash
netstat -tlnp | grep 5000
systemctl restart landscape-backend
```

### Frontend Issues
```bash
cd /var/www/landscape-architecture-tool/frontend
npm ci --legacy-peer-deps && npm run build
systemctl restart landscape-backend
```

## 🔄 Rollback to Backup

```bash
systemctl stop landscape-backend
cd /var/www
rm -rf landscape-architecture-tool
tar -xzf /var/backups/landscape-backup-TIMESTAMP.tar.gz
systemctl start landscape-backend
```

## 📊 Testing Checklist

- [ ] Service running: `systemctl status landscape-backend`
- [ ] Health local: `curl http://localhost:5000/health`
- [ ] Health external: `curl http://72.60.176.200:8080/health`
- [ ] Browser: http://72.60.176.200:8080/
- [ ] No errors: `journalctl -u landscape-backend -n 20`

## 🛠️ VPS Info

- **IP**: 72.60.176.200
- **Port**: 8080
- **User**: root
- **App Dir**: /var/www/landscape-architecture-tool
- **Branch**: V1.00D
- **Service**: landscape-backend

## 📞 Need Help?

1. Check logs: `journalctl -u landscape-backend -n 100`
2. Review full guide: `/var/www/landscape-architecture-tool/docs/VPS_CLEAN_REINSTALL_GUIDE.md`
3. GitHub issues: https://github.com/HANSKMIEL/landscape-architecture-tool/issues
