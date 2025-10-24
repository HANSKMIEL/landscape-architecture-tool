# VPS Deployment Architecture

## Current State Analysis

```
┌─────────────────────────────────────────────────────────┐
│                    CURRENT VPS STATE                     │
├─────────────────────────────────────────────────────────┤
│ URL: http://72.60.176.200:8080/                         │
│ Status: ✅ Running                                       │
│ Version: 2.0.0                                           │
│ Last Deploy: Sept 25, 2025                              │
│ Branch: V1.00D (outdated)                               │
│ Issue: Not pulling latest code                          │
└─────────────────────────────────────────────────────────┘
```

## Deployment Flow

```
┌────────────────┐
│   Local Dev    │
│   Repository   │
└───────┬────────┘
        │ git push to V1.00D
        ▼
┌────────────────┐
│     GitHub     │
│ V1.00D Branch  │
└───────┬────────┘
        │
        │ Manual: git fetch/pull
        │ or Auto: cron job
        ▼
┌────────────────────────────────────────┐
│              VPS Server                │
│  /var/www/landscape-architecture-tool  │
├────────────────────────────────────────┤
│  1. git fetch --all                    │
│  2. git reset --hard origin/V1.00D     │
│  3. systemctl stop landscape-backend   │
│  4. pip install -r requirements.txt    │
│  5. npm ci && npm run build            │
│  6. systemctl start landscape-backend  │
└───────┬────────────────────────────────┘
        │
        ▼
┌────────────────┐
│   Deployment   │
│   Complete     │
│ http://72.60.  │
│ 176.200:8080/  │
└────────────────┘
```

## File Structure on VPS

```
/var/www/landscape-architecture-tool/
├── .git/                           # Git repository
├── frontend/
│   ├── dist/                      # Built frontend (served by nginx)
│   │   └── index.html             # Last modified: Sept 25
│   ├── src/                       # React source
│   └── package.json
├── src/                           # Python backend
├── venv/                          # Python virtual environment
├── requirements.txt
└── systemd service: landscape-backend
```

## Service Architecture

```
┌───────────────────────────────────────────────────┐
│                   Port 8080                        │
│                     Nginx                          │
│  (Reverse Proxy & Static File Server)             │
└─────────────┬─────────────────────────────────────┘
              │
              ├─► /health, /api/* ─► Port 5000
              │                       ┌─────────────┐
              │                       │   Gunicorn  │
              │                       │   (Flask)   │
              │                       └─────────────┘
              │
              └─► /, /assets/* ─► Static Files
                                  (frontend/dist/)
```

## Deployment Scripts Overview

### 1. vps_diagnostic.sh
```
Input: None
Output: Comprehensive diagnostic report
Purpose: Identify what's wrong

Checks:
✓ Repository status & commits behind
✓ Service status (backend, nginx)
✓ Python environment
✓ Frontend build age
✓ Network connectivity
✓ Logs analysis
```

### 2. deploy_vps_automated.sh
```
Input: None (runs on VPS)
Output: Deployed application
Purpose: Safe deployment with backup

Steps:
1. Create backup
2. Fetch latest code
3. Stop services
4. Update dependencies
5. Rebuild frontend
6. Start services
7. Verify deployment
8. Rollback on failure
```

### 3. vps_ssh_helper.sh
```
Input: Command (connect/diagnose/deploy/etc.)
Output: Command execution
Purpose: Easy VPS management

Features:
- Interactive menu
- Pre-configured commands
- No SSH syntax needed
- Handles scp/ssh automatically
```

## Deployment Decision Tree

```
Start
  │
  ├─ Is VPS accessible? ──NO──► Check network/firewall
  │     │
  │    YES
  │     │
  ├─ Is backend running? ──NO──► systemctl start landscape-backend
  │     │
  │    YES
  │     │
  ├─ Is code up to date? ──NO──► Run deployment
  │     │                         │
  │    YES                        │
  │     │                         │
  ├─ Is frontend recent? ──NO────┘
  │     │
  │    YES
  │     │
  └──► All Good! ✅
```

## Problem Resolution Paths

### Scenario 1: Outdated Code (CURRENT ISSUE)
```
Problem: VPS shows old version
Solution: git fetch && git reset --hard origin/V1.00D
Command: ./scripts/vps_ssh_helper.sh quick-deploy
Time: ~2-3 minutes
```

### Scenario 2: Service Not Running
```
Problem: Backend service stopped
Solution: Restart service
Command: systemctl restart landscape-backend
Time: ~5 seconds
```

### Scenario 3: Frontend Not Updated
```
Problem: Frontend shows old UI
Solution: Rebuild frontend
Command: cd frontend && npm run build
Time: ~30 seconds
```

### Scenario 4: Dependencies Outdated
```
Problem: Missing packages or version conflicts
Solution: Reinstall dependencies
Command: pip install -r requirements.txt && npm ci
Time: ~1-2 minutes
```

## Auto-Deploy Architecture

### Option 1: Cron Job
```
┌───────────────┐
│  Cron Daemon  │
│  (every 4h)   │
└───────┬───────┘
        │
        ▼
┌────────────────────┐
│  quick_deploy.sh   │
│  1. git fetch      │
│  2. git reset      │
│  3. rebuild        │
│  4. restart        │
└────────────────────┘
```

### Option 2: Webhook
```
┌──────────────┐
│   GitHub     │
│   Webhook    │
└──────┬───────┘
       │ HTTP POST
       ▼
┌────────────────────┐
│  webhook_deploy.sh │
│  (listening)       │
└────────────────────┘
```

## Backup Strategy

```
Before Deploy:
┌────────────────────────────────────┐
│  /var/backups/landscape-...tool/   │
│  ├── backup_20251001_083000_       │
│  │   ├── commit.txt               │
│  │   └── frontend.tar.gz          │
│  └── (keeps last 5 backups)       │
└────────────────────────────────────┘

Rollback Command:
git reset --hard $(cat backup_*_commit.txt)
tar -xzf backup_*_frontend.tar.gz
systemctl restart landscape-backend
```

## Monitoring & Verification

### Health Check Flow
```
External Request
  │
  ▼
http://72.60.176.200:8080/health
  │
  ├─► Nginx (port 8080)
  │     │
  │     └─► Gunicorn (port 5000)
  │           │
  │           └─► Flask /health endpoint
  │                 │
  │                 └─► Returns JSON:
  │                     {
  │                       "status": "healthy",
  │                       "version": "2.0.0",
  │                       "database": "connected"
  │                     }
  └─► Response
```

### Verification Steps
```
1. Service Status
   systemctl status landscape-backend
   Expected: active (running)

2. Port Listening
   ss -ln | grep 5000
   Expected: LISTEN on port 5000

3. Health Endpoint
   curl http://localhost:5000/health
   Expected: JSON with status "healthy"

4. External Access
   curl http://72.60.176.200:8080/health
   Expected: Same JSON response

5. Frontend
   curl http://72.60.176.200:8080/
   Expected: HTML with recent build assets
```

## Summary

**Problem:** VPS showing old deployment  
**Cause:** Code not updated from V1.00D branch  
**Solution:** Run deployment script to update code  
**Prevention:** Set up auto-deploy (cron or webhook)  
**Tools:** 3 new scripts + comprehensive documentation  
**Time:** 2-3 minutes to fix, 5 minutes to set up auto-deploy  

**Next Action:** Run `./scripts/vps_ssh_helper.sh quick-deploy`
