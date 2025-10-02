# ⚡ Quick Start: VPS Clean Reinstall from V1.00D Branch

## 🎯 Objective
Complete clean reinstallation of the Landscape Architecture Tool on VPS (72.60.176.200) from the V1.00D branch, with full testing.

## 🚀 Execute Reinstall (Choose One Method)

### Method 1: One-Line Command (Fastest) ⭐ RECOMMENDED

```bash
ssh root@72.60.176.200 "bash <(curl -fsSL https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_clean_reinstall.sh)"
```

### Method 2: Interactive Execution

```bash
# Step 1: SSH into VPS
ssh root@72.60.176.200

# Step 2: Download script
cd /tmp
curl -O https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_clean_reinstall.sh
chmod +x vps_clean_reinstall.sh

# Step 3: Run script (will prompt for confirmation)
sudo ./vps_clean_reinstall.sh
```

### Method 3: Manual Step-by-Step (If script fails)

```bash
ssh root@72.60.176.200

# Backup
cd /var/www
tar -czf /var/backups/landscape-backup-$(date +%Y%m%d_%H%M%S).tar.gz landscape-architecture-tool

# Stop and delete
systemctl stop landscape-backend
pkill -f gunicorn
rm -rf /var/www/landscape-architecture-tool

# Clone fresh from V1.00D
cd /var/www
git clone --branch V1.00D https://github.com/HANSKMIEL/landscape-architecture-tool.git

# Setup
cd landscape-architecture-tool
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend
cd frontend
npm ci --legacy-peer-deps
npm run build
cd ..

# Start service
chown -R www-data:www-data /var/www/landscape-architecture-tool
systemctl daemon-reload
systemctl start landscape-backend
systemctl enable landscape-backend
```

## ✅ Verify Installation

### Quick Verification

```bash
# Check service
systemctl status landscape-backend

# Test health endpoint
curl http://localhost:5000/health

# Test external access
curl http://72.60.176.200:8080/health
```

### Automated Testing

```bash
# Download and run test script
cd /tmp
curl -O https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_deployment_test.sh
chmod +x vps_deployment_test.sh
./vps_deployment_test.sh
```

### Browser Testing

Open in your browser:
- **Main Application**: http://72.60.176.200:8080/
- **Health Check**: http://72.60.176.200:8080/health

## 📊 What the Script Does

1. ✅ Creates backup in `/var/backups/landscape-architecture-tool/`
2. ✅ Stops all services gracefully
3. ✅ Deletes old installation (after backup)
4. ✅ Clones fresh from V1.00D branch
5. ✅ Restores configuration (.env file)
6. ✅ Sets up Python environment and dependencies
7. ✅ Restores database from backup (if exists)
8. ✅ Builds frontend (npm install + build)
9. ✅ Configures systemd service
10. ✅ Sets proper permissions
11. ✅ Starts services
12. ✅ Verifies installation

## 🛡️ Safety Features

- **Automatic Backup**: Full backup created before any changes
- **Configuration Preserved**: .env file saved and restored
- **Database Backup**: Production database backed up
- **Rollback Support**: Can restore from any backup
- **Keeps 5 Backups**: Automatically manages backup retention

## 🔄 Rollback (If Needed)

If something goes wrong:

```bash
# Stop service
systemctl stop landscape-backend

# Find your backup
ls -lt /var/backups/landscape-architecture-tool/

# Restore (replace TIMESTAMP with actual timestamp)
cd /var/www
rm -rf landscape-architecture-tool
tar -xzf /var/backups/landscape-architecture-tool/backup_TIMESTAMP/app_backup.tar.gz

# Start service
systemctl start landscape-backend
```

## 📝 Log Files

Check these if you encounter issues:

- **Installation Log**: `/var/log/landscape-reinstall.log`
- **Service Logs**: `journalctl -u landscape-backend -f`
- **Recent Errors**: `journalctl -u landscape-backend -n 50`

## 🆘 Quick Troubleshooting

### Service Won't Start
```bash
journalctl -u landscape-backend -n 50
systemctl restart landscape-backend
```

### Health Endpoint Not Responding
```bash
netstat -tlnp | grep 5000
systemctl restart landscape-backend
```

### Frontend Not Loading
```bash
cd /var/www/landscape-architecture-tool/frontend
npm ci --legacy-peer-deps && npm run build
systemctl restart landscape-backend
```

## 📚 Full Documentation

For complete details, see:
- **Solution Overview**: `docs/VPS_DEPLOYMENT_SOLUTION.md`
- **Detailed Guide**: `docs/VPS_CLEAN_REINSTALL_GUIDE.md`
- **Quick Reference**: `docs/VPS_QUICK_REFERENCE.md`

## ✨ Expected Results

After successful installation:

✅ Service Status: `active (running)`  
✅ Health Endpoint: Returns JSON with status  
✅ External Access: http://72.60.176.200:8080/ loads application  
✅ API Endpoints: `/api/suppliers`, `/api/plants` respond  
✅ No Errors: Clean logs with no critical errors  

## 🎯 Testing Checklist

- [ ] Service running: `systemctl status landscape-backend`
- [ ] Health local: `curl http://localhost:5000/health`
- [ ] Health external: `curl http://72.60.176.200:8080/health`
- [ ] Browser loads: http://72.60.176.200:8080/
- [ ] API works: Test suppliers, plants, projects pages
- [ ] No errors: `journalctl -u landscape-backend -n 20`
- [ ] Frontend displays: Dashboard shows with data
- [ ] Navigation works: Can switch between pages

## 💡 Tips

1. **Run during low traffic**: Choose a time when users aren't active
2. **Monitor logs**: Watch logs during installation with `journalctl -u landscape-backend -f`
3. **Test thoroughly**: Check all major features after installation
4. **Keep backups**: Don't delete backups until new deployment is verified
5. **Document issues**: Note any problems for troubleshooting

## 📞 Need Help?

1. Check installation log: `/var/log/landscape-reinstall.log`
2. Check service logs: `journalctl -u landscape-backend -n 100`
3. Review full documentation in `docs/` directory
4. Check GitHub issues: https://github.com/HANSKMIEL/landscape-architecture-tool/issues

---

**Ready to proceed?** Just run the one-line command above to start the clean reinstall!
