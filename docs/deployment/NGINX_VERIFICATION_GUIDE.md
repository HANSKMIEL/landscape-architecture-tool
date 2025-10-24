# VPS Nginx Configuration Verification Guide

## Current Setup Analysis

Based on the repository structure and deployment scripts, here's how the frontend is served:

### 🔍 **Current Configuration: Nginx + Static Files**

The V1.00D deployment uses **Nginx** to serve the static frontend files, NOT Node.js/Vite dev server.

#### Deployment Flow:

```bash
1. Frontend built with: npm run build
   → Generates static files in: frontend/dist/

2. Nginx configured to serve from: /var/www/landscape-architecture-tool/frontend/dist/
   → Located at: /etc/nginx/sites-available/landscape

3. Backend served via reverse proxy:
   → Nginx forwards /api/* to localhost:5000 (Gunicorn)
```

### 📋 Expected Nginx Configuration

The Nginx config should look like this (located at `/etc/nginx/sites-available/landscape`):

```nginx
server {
    listen 80;
    server_name 72.60.176.200;

    # Frontend - Static files
    location / {
        root /var/www/landscape-architecture-tool/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API - Reverse proxy
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health endpoint
    location /health {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

### ⚠️ Common Issue: Port 8080 Blocking

**Problem**: Changes not appearing after deployment

**Possible Causes**:

1. Old Node.js dev server still running on port 8080
2. Nginx not reloading properly
3. Browser caching old frontend version
4. Build artifacts not being replaced

**Solution** (now implemented in `vps_deploy_v1d.sh`):

```bash
# Kill any process on port 8080
lsof -ti:8080 | xargs kill -9

# Kill any npm/vite dev servers
pkill -f "vite"
pkill -f "npm.*dev"

# Clear frontend build cache
rm -rf frontend/dist/
rm -rf frontend/node_modules/.cache/

# Rebuild frontend
cd frontend && npm run build

# Reload Nginx
systemctl reload nginx
```

### 🔧 VPS Verification Commands

Run these commands on the VPS to verify the setup:

```bash
# 1. Check if Nginx is running
systemctl status nginx

# 2. Check Nginx configuration
nginx -t

# 3. View current Nginx config
cat /etc/nginx/sites-available/landscape

# 4. Check what's listening on port 8080
lsof -i:8080
# Expected: nginx process, NOT node/npm

# 5. Check what's listening on port 5000
lsof -i:5000
# Expected: gunicorn/python (backend)

# 6. Verify frontend dist directory exists
ls -la /var/www/landscape-architecture-tool/frontend/dist/
# Expected: index.html and assets/ folder

# 7. Check Nginx access logs
tail -f /var/log/nginx/access.log

# 8. Check Nginx error logs
tail -f /var/log/nginx/error.log

# 9. Test frontend locally on VPS
curl -I http://localhost/
# Expected: HTTP 200, content-type: text/html

# 10. Test backend locally on VPS
curl http://localhost:5000/health
# Expected: JSON with status: healthy
```

### 🚀 Deployment Process Checklist

When deploying V1.00D to VPS:

- [ ] 1. **Pull latest code** from V1.00D branch
- [ ] 2. **Kill port 8080 processes** (now automated in script)
- [ ] 3. **Clear frontend caches**
  ```bash
  rm -rf frontend/dist/ frontend/node_modules/.cache/
  ```
- [ ] 4. **Rebuild frontend with devdeploy branding**
  ```bash
  export VITE_APP_TITLE="devdeploy - Landscape Architecture Tool (Development)"
  npm run build
  ```
- [ ] 5. **Verify build output**
  ```bash
  ls -lh frontend/dist/index.html
  grep -i "devdeploy" frontend/dist/index.html
  ```
- [ ] 6. **Restart backend**
  ```bash
  systemctl restart landscape-backend
  ```
- [ ] 7. **Reload Nginx**
  ```bash
  nginx -t && systemctl reload nginx
  ```
- [ ] 8. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)
- [ ] 9. **Test externally**
  ```bash
  curl http://72.60.176.200:8080/
  ```

### 🐛 Troubleshooting

#### Issue: "Changes not appearing after deployment"

**Diagnosis**:

```bash
# Check last modification time of dist files
stat /var/www/landscape-architecture-tool/frontend/dist/index.html

# Check if build actually ran
ls -lat /var/www/landscape-architecture-tool/frontend/dist/ | head

# Check Nginx is serving correct directory
curl -I http://72.60.176.200:8080/
# Look for X-Served-By or similar headers
```

**Solutions**:

1. **Hard browser refresh**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. **Clear browser cache**: Settings → Clear browsing data → Cached files
3. **Force rebuild**:
   ```bash
   cd /var/www/landscape-architecture-tool/frontend
   rm -rf dist/ node_modules/.cache/
   npm cache clean --force
   npm run build
   ```
4. **Verify Nginx serves fresh content**:
   ```bash
   # Disable caching temporarily for testing
   # Edit /etc/nginx/sites-available/landscape
   # Add: add_header Cache-Control "no-cache, no-store, must-revalidate";
   nginx -t && systemctl reload nginx
   ```

#### Issue: "502 Bad Gateway"

**Cause**: Backend not running or Nginx can't reach it

**Solution**:

```bash
# Check backend status
systemctl status landscape-backend

# Check if backend is listening
netstat -tlnp | grep 5000

# Restart backend
systemctl restart landscape-backend

# Check logs
journalctl -u landscape-backend -n 50
```

#### Issue: "404 Not Found for API calls"

**Cause**: Nginx reverse proxy misconfigured

**Solution**:

```bash
# Verify proxy_pass configuration
grep -A 5 "location /api/" /etc/nginx/sites-available/landscape

# Test backend directly
curl http://localhost:5000/api/dashboard/stats

# Reload Nginx
nginx -t && systemctl reload nginx
```

### 📊 Monitoring

**Check deployment status**:

```bash
# Full system check
systemctl status landscape-backend nginx

# Resource usage
df -h  # Disk space
free -h  # Memory
top -bn1 | head -20  # CPU/processes

# Recent logs
journalctl -u landscape-backend --since "10 minutes ago"
tail -50 /var/log/nginx/error.log
```

### 🔐 Security Considerations

**Nginx Security Headers** (should be in config):

```nginx
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

**Rate Limiting** (for API endpoints):

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    # ... rest of proxy config
}
```

### 📚 Related Files

- Deployment script: `scripts/vps_deploy_v1d.sh`
- Nginx template: `archive/legacy-scripts/nginx.conf`
- GitHub Actions: `.github/workflows/devdeploy-v1d.yml`
- VPS Architecture: `docs/VPS_ARCHITECTURE.md`

---

**Last Updated**: October 1, 2025  
**Maintained by**: HANSKMIEL  
**Version**: 1.0
