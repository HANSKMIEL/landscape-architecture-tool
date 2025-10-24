# VPS Clean Reinstall Process Flow

## 🔄 Complete Process Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    START: VPS Clean Reinstall                   │
│                   From V1.00D Branch on GitHub                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: BACKUP                                                  │
│ ───────────────────────────────────────────────────────────     │
│ • Create timestamped backup directory                           │
│ • Backup application directory → tar.gz                         │
│ • Backup database file                                          │
│ • Backup .env configuration                                     │
│ • Keep only last 5 backups                                      │
│ Location: /var/backups/landscape-architecture-tool/             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: STOP SERVICES                                           │
│ ───────────────────────────────────────────────────────────     │
│ • Stop landscape-backend systemd service                        │
│ • Kill remaining gunicorn processes                             │
│ • Kill remaining landscape processes                            │
│ • Wait for clean shutdown (5 seconds)                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: DELETE OLD INSTALLATION                                 │
│ ───────────────────────────────────────────────────────────     │
│ • Preserve .env file temporarily                                │
│ • Remove /var/www/landscape-architecture-tool                   │
│ • Clean directory completely                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: CLONE REPOSITORY                                        │
│ ───────────────────────────────────────────────────────────     │
│ • Clone from GitHub (V1.00D branch)                             │
│ • Single-branch clone for efficiency                            │
│ • Verify commit hash and branch                                 │
│ Source: https://github.com/HANSKMIEL/...                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: RESTORE CONFIGURATION                                   │
│ ───────────────────────────────────────────────────────────     │
│ • Restore preserved .env file                                   │
│ • If no .env, create from .env.example                          │
│ • Verify configuration exists                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: SETUP PYTHON ENVIRONMENT                                │
│ ───────────────────────────────────────────────────────────     │
│ • Create fresh virtual environment (venv)                       │
│ • Upgrade pip to latest version                                 │
│ • Install all dependencies from requirements.txt                │
│ • Verify installations                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: INITIALIZE DATABASE                                     │
│ ───────────────────────────────────────────────────────────     │
│ • Check for database backup                                     │
│ • If backup exists: Restore database                            │
│ • If no backup: Prepare for fresh initialization               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: SETUP FRONTEND                                          │
│ ───────────────────────────────────────────────────────────     │
│ • Install Node.js dependencies (npm ci)                         │
│ • Build production frontend bundle (npm run build)              │
│ • Verify build artifacts created                                │
│ Output: frontend/dist/ or frontend/build/                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 9: SETUP SYSTEMD SERVICE                                   │
│ ───────────────────────────────────────────────────────────     │
│ • Create/update service file                                    │
│ • Configure gunicorn with 3 workers                             │
│ • Set environment variables                                     │
│ • Enable auto-restart on failure                                │
│ File: /etc/systemd/system/landscape-backend.service             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 10: SET PERMISSIONS                                        │
│ ───────────────────────────────────────────────────────────     │
│ • Set ownership to www-data:www-data                            │
│ • Make scripts executable                                       │
│ • Verify file permissions                                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 11: START SERVICES                                         │
│ ───────────────────────────────────────────────────────────     │
│ • Reload systemd daemon                                         │
│ • Start landscape-backend service                               │
│ • Enable service for auto-start                                 │
│ • Wait for service to initialize (10 seconds)                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 12: VERIFY INSTALLATION                                    │
│ ───────────────────────────────────────────────────────────     │
│ • Check service status (systemctl)                              │
│ • Test health endpoint (internal: :5000)                        │
│ • Test health endpoint (external: :8080)                        │
│ • Verify frontend files exist                                   │
│ • Check logs for errors                                         │
│ • Display service status                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────┴────────┐
                    │   SUCCESS?     │
                    └───────┬────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
             YES                         NO
              │                           │
              ▼                           ▼
    ┌──────────────────┐      ┌──────────────────┐
    │ DEPLOYMENT       │      │ CHECK LOGS &     │
    │ COMPLETE! ✅     │      │ ROLLBACK ⚠️     │
    │                  │      │                  │
    │ • Service Active │      │ • View logs      │
    │ • App Running    │      │ • Restore backup │
    │ • Tests Pass     │      │ • Investigate    │
    └──────────────────┘      └──────────────────┘
```

## 📊 Testing Flow After Installation

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTOMATED TESTING                           │
│                Run: vps_deployment_test.sh                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Test 1:      │  │ Test 2-3:    │  │ Test 4-5:    │
│ Service      │  │ Health       │  │ Frontend &   │
│ Status       │  │ Endpoints    │  │ API          │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Test 6-7:    │  │ Test 8-9:    │  │ Test 10:     │
│ Database &   │  │ Git Repo &   │  │ Network      │
│ App Files    │  │ Logs         │  │ Ports        │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       └─────────────────┼──────────────────┘
                         │
                         ▼
               ┌──────────────────┐
               │  TEST SUMMARY    │
               │  Passed: X/Y     │
               │  Failed: Z       │
               └──────────────────┘
```

## 🔄 Rollback Flow (If Needed)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROLLBACK PROCEDURE                           │
│               (If deployment fails or issues found)             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Stop Current Service                                         │
│    systemctl stop landscape-backend                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. List Available Backups                                       │
│    ls -lt /var/backups/landscape-architecture-tool/             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Remove Failed Installation                                   │
│    rm -rf /var/www/landscape-architecture-tool                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Restore from Backup                                          │
│    tar -xzf backup_TIMESTAMP/app_backup.tar.gz                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Restore Database & Config                                    │
│    cp backup_TIMESTAMP/*.db → app_dir/                          │
│    cp backup_TIMESTAMP/.env.backup → app_dir/.env               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Start Service                                                │
│    systemctl start landscape-backend                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               ROLLBACK COMPLETE - SYSTEM RESTORED               │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure After Install

```
/var/www/landscape-architecture-tool/
├── src/                          # Backend source code
│   ├── models/                   # Database models
│   ├── routes/                   # API routes
│   ├── services/                 # Business logic
│   └── main.py                   # Flask application
├── frontend/
│   ├── src/                      # Frontend source
│   └── dist/                     # Built frontend (after build)
├── venv/                         # Python virtual environment
├── migrations/                   # Database migrations
├── .env                          # Configuration (restored)
├── wsgi.py                       # WSGI entry point
├── requirements.txt              # Python dependencies
└── landscape_architecture_prod.db # SQLite database (restored)

/var/backups/landscape-architecture-tool/
├── backup_20241002_120000/
│   ├── app_backup.tar.gz
│   ├── landscape_architecture_prod_backup.db
│   └── .env.backup
├── backup_20241001_180000/       (keeps 5 most recent)
└── ...

/etc/systemd/system/
└── landscape-backend.service     # Systemd service file

/var/log/
└── landscape-reinstall.log       # Installation log
```

## ⏱️ Estimated Timing

| Step | Description | Estimated Time |
|------|-------------|----------------|
| 1 | Backup | 30-60 seconds |
| 2 | Stop Services | 5-10 seconds |
| 3 | Delete Old | 5-10 seconds |
| 4 | Clone Repo | 10-20 seconds |
| 5 | Restore Config | 1-2 seconds |
| 6 | Python Setup | 60-120 seconds |
| 7 | Database Init | 5-10 seconds |
| 8 | Frontend Build | 30-60 seconds |
| 9 | Systemd Setup | 2-5 seconds |
| 10 | Permissions | 2-5 seconds |
| 11 | Start Services | 10-15 seconds |
| 12 | Verify | 10-20 seconds |
| **TOTAL** | | **3-5 minutes** |

## 🎯 Key Decision Points

```
During Installation:
├── Backup exists? → Keep or create new
├── .env exists? → Restore or create from example
├── Database backup? → Restore or initialize fresh
├── npm available? → Build frontend or skip
└── Service file exists? → Update or create new

After Installation:
├── Service running? → Continue or troubleshoot
├── Health responding? → Success or investigate
├── Frontend built? → Complete or rebuild
└── Tests passing? → Done or rollback
```

## 📞 Support Flow

```
Issue Encountered
       │
       ▼
Check Installation Log
(/var/log/landscape-reinstall.log)
       │
       ▼
Check Service Logs
(journalctl -u landscape-backend)
       │
       ├─→ Service Issues → Restart service
       ├─→ Frontend Issues → Rebuild frontend
       ├─→ Database Issues → Check permissions
       └─→ Network Issues → Check firewall/nginx
       │
       ▼
Still Issues?
       │
       ├─→ Review Documentation
       ├─→ Check GitHub Issues
       └─→ Rollback to backup
```

---

**Quick Reference Commands:**

```bash
# Run installation
bash <(curl -fsSL https://raw.githubusercontent.com/HANSKMIEL/.../vps_clean_reinstall.sh)

# Run tests
bash <(curl -fsSL https://raw.githubusercontent.com/HANSKMIEL/.../vps_deployment_test.sh)

# Check status
systemctl status landscape-backend

# View logs
journalctl -u landscape-backend -f

# List backups
ls -lt /var/backups/landscape-architecture-tool/
```
