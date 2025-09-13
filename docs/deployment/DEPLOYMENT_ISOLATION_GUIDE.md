# 🛡️ Deployment Isolation Guide

## 📋 Overview

This guide ensures complete isolation between the V1.00D development version and the V1.00 production version, preventing any cross-contamination during development and deployment processes.

## 🏗️ Isolation Architecture

### Production Environment (V1.00)
- **Location**: `/var/www/landscape-architecture-tool/`
- **URL**: https://optura.nl
- **Backend Port**: 5000
- **Database**: `/var/www/landscape-architecture-tool/instance/production.db`
- **Service**: `landscape-backend.service`
- **Title**: "Landscape Architecture Tool - Professional Garden Design Management"

### Development Environment (V1.00D)
- **Location**: `/var/www/landscape-architecture-tool-dev/`
- **URL**: http://72.60.176.200:8080
- **Backend Port**: 5001
- **Database**: `/var/www/landscape-architecture-tool-dev/instance/development.db`
- **Service**: `landscape-backend-dev.service`
- **Title**: "devdeploy - Landscape Architecture Tool (Development)"

## 🔧 Promotion Process

### Safe Promotion Script: `promote_v1d_to_v1.sh`

The promotion script ensures complete isolation by:

1. **Backup Creation**: Creates timestamped backups before any changes
2. **Package Isolation**: Updates only the `packages/v1.00/` directory
3. **Production Protection**: Never directly touches the live production deployment
4. **Separate Deployment**: Requires explicit deployment step to update production

### Usage

```bash
# Promote V1.00D to V1.00 package (safe)
./scripts/promote_v1d_to_v1.sh

# Deploy V1.00 package to production (separate step)
./scripts/deploy_v1_to_production.sh
```

## 🎯 Title Management

### Development Title
- **Browser Tab**: "devdeploy - Landscape Architecture Tool (Development)"
- **Purpose**: Clearly identifies development environment
- **Management**: Use `./scripts/manage_titles.sh dev`

### Production Title
- **Browser Tab**: "Landscape Architecture Tool - Professional Garden Design Management"
- **Purpose**: Professional production appearance
- **Management**: Use `./scripts/manage_titles.sh prod`

## 🔒 Isolation Safeguards

### 1. Separate Directories
```
/var/www/landscape-architecture-tool/     # Production
/var/www/landscape-architecture-tool-dev/ # Development
```

### 2. Separate Services
```bash
# Production service
systemctl status landscape-backend

# Development service  
systemctl status landscape-backend-dev
```

### 3. Separate Databases
```
production.db    # Production data
development.db   # Development data (isolated)
```

### 4. Separate Ports
```
Port 5000: Production backend
Port 5001: Development backend
```

### 5. Separate URLs
```
https://optura.nl           # Production
http://72.60.176.200:8080   # Development
```

## 📊 Deployment Workflow

### Development Phase
1. Work on V1.00D branch
2. Test on development environment (port 8080)
3. Verify all features work correctly
4. Run promotion script when ready

### Promotion Phase
1. Run `./scripts/promote_v1d_to_v1.sh`
2. Review changes in `packages/v1.00/`
3. Push changes to repository
4. **Production remains untouched**

### Production Deployment Phase
1. Run `./scripts/deploy_v1_to_production.sh`
2. Production gets updated from V1.00 package
3. Services restart automatically
4. Verify production functionality

## 🧪 Testing Isolation

### Before Promotion
```bash
# Test development
curl http://72.60.176.200:8080/health

# Verify production unchanged
curl https://optura.nl/api/health
```

### After Promotion (Before Deployment)
```bash
# Development still works
curl http://72.60.176.200:8080/health

# Production still unchanged
curl https://optura.nl/api/health

# V1.00 package updated but not deployed
ls -la packages/v1.00/
```

### After Production Deployment
```bash
# Both environments working
curl http://72.60.176.200:8080/health  # Development
curl https://optura.nl/api/health       # Production (updated)
```

## 🚨 Emergency Procedures

### Rollback Production
```bash
# Restore from backup
sudo systemctl stop landscape-backend
sudo mv /var/www/landscape-architecture-tool /var/www/landscape-architecture-tool-failed
sudo mv /var/www/landscape-architecture-tool-backup-TIMESTAMP /var/www/landscape-architecture-tool
sudo systemctl start landscape-backend
```

### Reset Development
```bash
# Pull fresh V1.00D
cd /var/www/landscape-architecture-tool-dev
sudo git reset --hard origin/V1.00D
sudo systemctl restart landscape-backend-dev
```

## 📋 Verification Checklist

### Pre-Promotion
- [ ] All tests pass on V1.00D
- [ ] Development environment stable
- [ ] No uncommitted changes
- [ ] Production environment verified working

### Post-Promotion
- [ ] V1.00 package updated
- [ ] Changes committed to repository
- [ ] Development environment still working
- [ ] Production environment unchanged

### Post-Deployment
- [ ] Production updated successfully
- [ ] All services running
- [ ] Health checks passing
- [ ] User functionality verified

## 🎯 Key Benefits

1. **Zero Downtime**: Production never affected during development
2. **Safe Testing**: Complete isolation prevents accidents
3. **Easy Rollback**: Automated backups for quick recovery
4. **Clear Identification**: Different titles prevent confusion
5. **Controlled Deployment**: Explicit steps prevent mistakes

---

**Last Updated**: September 13, 2025  
**Version**: V1.00D Isolation Complete  
**Status**: ✅ Production Protected
