# Quick VPS Deployment Guide

## 🚀 Deploy V1.00D to VPS in 3 Steps

### Step 1: Copy Script to VPS
```bash
scp scripts/vps_deploy_v1d.sh root@72.60.176.200:/root/
```

### Step 2: SSH to VPS
```bash
ssh root@72.60.176.200
```

### Step 3: Run Deployment
```bash
bash /root/vps_deploy_v1d.sh
```

## ✅ What It Does

- ✓ Backs up current deployment
- ✓ Pulls latest V1.00D changes
- ✓ Updates dependencies
- ✓ Rebuilds frontend with devdeploy branding
- ✓ Restarts backend service
- ✓ Runs health checks

## 🔍 Verify Deployment

```bash
curl http://72.60.176.200:8080/health
curl http://72.60.176.200:8080/
```

## 🔄 Automatic Updates (Optional)

Set up cron job on VPS:
```bash
crontab -e
# Add this line:
0 */6 * * * /root/vps_deploy_v1d.sh >> /var/log/landscape-deploy.log 2>&1
```

## 📖 Full Documentation

See [VPS_DEPLOYMENT_INSTRUCTIONS.md](./VPS_DEPLOYMENT_INSTRUCTIONS.md) for complete details.

## 🛠️ Troubleshooting

**Service not starting?**
```bash
journalctl -u landscape-backend -n 50
```

**Restore from backup:**
```bash
cp -r /var/backups/landscape-YYYYMMDD_HHMMSS/* /var/www/landscape-architecture-tool/
systemctl restart landscape-backend
```
