# ⚡ FIX YOUR VPS NOW - IMMEDIATE ACTION REQUIRED

## 🎯 YOUR SITUATION

Your VPS at **http://72.60.176.200:8080/** is showing old code from **September 25, 2025**.

**Good news:** The VPS is running fine, it just needs to pull the latest code!

---

## 🚀 FASTEST FIX (Copy & Paste This)

**Open your terminal and paste this ONE command:**

```bash
ssh root@72.60.176.200 "cd /var/www/landscape-architecture-tool && git fetch --all && git reset --hard origin/V1.00D && systemctl stop landscape-backend && pkill -f gunicorn && source venv/bin/activate && pip install -r requirements.txt && cd frontend && npm ci --legacy-peer-deps && npm run build && cd .. && systemctl start landscape-backend && sleep 5 && systemctl status landscape-backend"
```

**That's it!** Wait 2-3 minutes for it to complete.

---

## ✅ VERIFY IT WORKED

Check the health endpoint:
```bash
curl http://72.60.176.200:8080/health
```

You should see the latest version and timestamp.

Or open in browser: **http://72.60.176.200:8080/**

---

## 🎨 EASIER WAY (Using Our Helper Script)

From the repository directory:

```bash
./scripts/vps_ssh_helper.sh quick-deploy
```

This does the same thing but with nice formatting!

---

## 📋 WANT TO SEE WHAT'S WRONG FIRST?

Run the diagnostic:

```bash
./scripts/vps_ssh_helper.sh diagnose
```

This will show you:
- Current commit vs latest commit
- Service status
- Build dates
- What needs updating

---

## 🔄 PREVENT THIS IN THE FUTURE

### Option 1: Auto-Deploy Every 4 Hours

```bash
ssh root@72.60.176.200 << 'EOF'
cat > /root/quick_deploy.sh << 'INNER'
#!/bin/bash
cd /var/www/landscape-architecture-tool
git fetch --all && git reset --hard origin/V1.00D
systemctl stop landscape-backend
pkill -f gunicorn || true
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm ci --legacy-peer-deps && npm run build && cd ..
systemctl start landscape-backend
INNER
chmod +x /root/quick_deploy.sh
echo "0 */4 * * * /root/quick_deploy.sh >> /var/log/landscape-deploy.log 2>&1" | crontab -
echo "✅ Auto-deploy configured!"
EOF
```

### Option 2: Use Our Helper to Set Everything Up

```bash
./scripts/vps_ssh_helper.sh copy-scripts
```

This installs all helper scripts on your VPS.

---

## 🆘 IF SOMETHING GOES WRONG

### Quick Health Check
```bash
./scripts/vps_ssh_helper.sh health
```

### View Logs
```bash
./scripts/vps_ssh_helper.sh logs
```

### Restart Service
```bash
./scripts/vps_ssh_helper.sh restart
```

### Full Diagnostic
```bash
./scripts/vps_ssh_helper.sh diagnose
```

---

## 📚 DOCUMENTATION

- **Quick Reference:** `VPS_DEPLOYMENT_SOLUTION.md`
- **Complete Guide:** `VPS_DEPLOYMENT_GUIDE.md`
- **Original Docs:** `README_DEPLOYMENT.md`

---

## 🎯 TL;DR

1. **Run this now:**
   ```bash
   ssh root@72.60.176.200 "cd /var/www/landscape-architecture-tool && git fetch --all && git reset --hard origin/V1.00D && systemctl stop landscape-backend && pkill -f gunicorn && source venv/bin/activate && pip install -r requirements.txt && cd frontend && npm ci --legacy-peer-deps && npm run build && cd .. && systemctl start landscape-backend"
   ```

2. **Verify:**
   ```bash
   curl http://72.60.176.200:8080/health
   ```

3. **Set up auto-deploy** (so this doesn't happen again)

**Done!** Your VPS is now showing the latest code! 🎉

---

**Questions?** Check `VPS_DEPLOYMENT_GUIDE.md` for detailed troubleshooting.
