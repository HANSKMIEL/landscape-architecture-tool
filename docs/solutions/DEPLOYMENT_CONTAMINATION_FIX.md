# 🚨 Deployment Contamination Fix - V1.00D → Production

**Status**: CRITICAL - Production contaminated with development code
**Date**: October 1, 2025
**Impact**: https://optura.nl displays "devdeploy" title instead of production title

## 🔴 Problem Summary

The V1.00D development branch was accidentally deployed to the **production environment** (optura.nl) instead of the development environment (72.60.176.200:8080), causing:

1. ❌ Production website shows "devdeploy - Landscape Architecture Tool (Development)" title
2. ❌ Development code running on production server
3. ❌ Branch protection bypassed

## 🔍 Root Cause Analysis

### Issue Found in `.github/workflows/v1d-devdeploy.yml`

**Line 150-162** contained a critical flaw:

```yaml
find_deployment_dir() {
    for dir in "/var/www/landscape-architecture-tool" "/var/www/landscape-architecture-tool-dev" ...
}
```

**Problem**: The workflow checked the **production directory FIRST**, causing it to deploy V1.00D code to `/var/www/landscape-architecture-tool/` (production) instead of `/var/www/landscape-architecture-tool-dev/` (development).

### Why This Happened

1. The `find_deployment_dir()` function prioritized production directory
2. No safety check prevented deployment to production
3. Nginx for optura.nl reads from `/var/www/landscape-architecture-tool/`
4. Result: Production site contaminated with development build

## ✅ Fixes Applied

### 1. Fixed Directory Priority (`.github/workflows/v1d-devdeploy.yml`)

**Changed line 153** from:
```yaml
for dir in "/var/www/landscape-architecture-tool" "/var/www/landscape-architecture-tool-dev" ...
```

**To**:
```yaml
for dir in "/var/www/landscape-architecture-tool-dev" "/var/www/landscape-architecture-tool" ...
```

**Impact**: Development directory is now checked FIRST.

### 2. Added Safety Check (`.github/workflows/v1d-devdeploy.yml`)

**Added after line 172**:
```bash
# CRITICAL SAFETY CHECK: Prevent accidental production deployment
if [[ "$DEPLOY_DIR" == "/var/www/landscape-architecture-tool" ]] && [[ ! "$DEPLOY_DIR" =~ -dev ]]; then
    echo "🚨 CRITICAL ERROR: Attempting to deploy V1.00D to PRODUCTION directory!"
    echo "❌ Deployment directory: $DEPLOY_DIR"
    echo "❌ This V1.00D workflow should ONLY deploy to development environment"
    echo "🛡️ BLOCKING deployment to protect production (optura.nl)"
    exit 1
fi
```

**Impact**: Workflow will now **EXIT IMMEDIATELY** if it detects production directory, preventing contamination.

### 3. Created Emergency Restoration Script

**File**: `scripts/deployment/EMERGENCY_RESTORE_PRODUCTION_TITLE.sh`

This script:
- ✅ Creates backup of current production state
- ✅ Checks out `main` branch (NOT V1.00D)
- ✅ Rebuilds frontend with correct production title
- ✅ Restarts services
- ✅ Verifies title restoration

## 🔧 How to Fix Production NOW

### Option 1: Run Emergency Restoration Script (Recommended)

```bash
# Set your VPS credentials
export VPS_HOST="72.60.176.200"
export VPS_USER="root"
export VPS_SSH_KEY="<your-ssh-key>"  # Optional, will prompt for password if not set

# Run restoration script
bash scripts/deployment/EMERGENCY_RESTORE_PRODUCTION_TITLE.sh
```

### Option 2: Manual VPS Login

```bash
# 1. SSH into VPS
ssh root@72.60.176.200

# 2. Navigate to production directory
cd /var/www/landscape-architecture-tool

# 3. Create backup
sudo cp -r /var/www/landscape-architecture-tool /var/backups/landscape-backup-$(date +%Y%m%d_%H%M%S)

# 4. Switch to main branch
git fetch --all
git checkout main
git reset --hard origin/main

# 5. Fix title in source
sed -i 's/<title>.*<\/title>/<title>Landscape Architecture Tool - Professional Garden Design Management<\/title>/' frontend/index.html

# 6. Rebuild frontend
cd frontend
npm ci --legacy-peer-deps
npm run build

# 7. Verify title in build
grep "<title>" dist/index.html
# Should show: <title>Landscape Architecture Tool - Professional Garden Design Management</title>

# 8. Fix if needed
sed -i 's/<title>.*<\/title>/<title>Landscape Architecture Tool - Professional Garden Design Management</title>/' dist/index.html

# 9. Set permissions
cd ..
sudo chown -R www-data:www-data .

# 10. Restart services
sudo systemctl restart landscape-backend
sudo systemctl reload nginx

# 11. Verify
curl -s http://127.0.0.1/ | grep "<title>"
```

### Option 3: Deploy via GitHub Actions

1. Create a new workflow run targeting `main` branch for production deployment
2. Ensure it deploys to `/var/www/landscape-architecture-tool/` explicitly
3. Verify title after deployment

## 📊 Verification Steps

After applying the fix, verify:

1. **Title Check**:
   ```bash
   curl -s https://optura.nl | grep "<title>"
   ```
   Should return: `<title>Landscape Architecture Tool - Professional Garden Design Management</title>`

2. **Branch Check** (on VPS):
   ```bash
   cd /var/www/landscape-architecture-tool && git branch --show-current
   ```
   Should return: `main`

3. **Browser Check**:
   - Visit https://optura.nl
   - Check browser tab title
   - Should show: "Landscape Architecture Tool - Professional Garden Design Management"
   - Clear cache if needed: Ctrl+Shift+R

4. **Development Check**:
   ```bash
   curl -s http://72.60.176.200:8080 | grep "<title>"
   ```
   Should return: `<title>devdeploy - Landscape Architecture Tool (Development)</title>`

## 🛡️ Prevention Measures Now Active

1. ✅ **Directory Priority**: Development directory checked first
2. ✅ **Safety Check**: Workflow exits if production directory detected
3. ✅ **Explicit Validation**: Each deployment verifies target directory
4. ✅ **Title Verification**: Post-deployment checks verify correct title

## 📝 Deployment Isolation Checklist

To maintain proper isolation going forward:

- [ ] **Production** (`/var/www/landscape-architecture-tool/`)
  - [ ] Always deployed from `main` branch
  - [ ] Title: "Landscape Architecture Tool - Professional Garden Design Management"
  - [ ] URL: https://optura.nl
  - [ ] Port 443 (HTTPS) + 5000 (backend)

- [ ] **Development** (`/var/www/landscape-architecture-tool-dev/`)
  - [ ] Always deployed from `V1.00D` branch
  - [ ] Title: "devdeploy - Landscape Architecture Tool (Development)"
  - [ ] URL: http://72.60.176.200:8080
  - [ ] Port 8080 (frontend) + 5001 (backend)

## 🚀 Next Steps

1. **Immediate**: Run emergency restoration script to fix production
2. **Commit**: Push the workflow fixes to V1.00D branch
3. **Test**: Verify next V1.00D deployment goes to development only
4. **Monitor**: Watch for any further contamination
5. **Document**: Update deployment procedures to prevent recurrence

## 📚 Related Documentation

- `_internal/docs/deployment/DEPLOYMENT_ISOLATION_GUIDE.md` - Complete isolation guide
- `scripts/deployment/promote_v1d_to_v1.sh` - Safe promotion process
- `.github/workflows/v1d-devdeploy.yml` - V1.00D deployment workflow (FIXED)
- `.github/workflows/enhanced-deployment.yml` - Production deployment workflow

## 🔗 References

- Issue discovered: October 1, 2025
- Production URL: https://optura.nl
- Development URL: http://72.60.176.200:8080
- Repository: HANSKMIEL/landscape-architecture-tool
- Branch structure: `main` (production) / `V1.00D` (development)
