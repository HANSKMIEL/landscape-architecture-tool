# V1.00D Security & Validation - Action Items
**Quick Reference Guide for Implementation**

## Priority Matrix

### 🔴 CRITICAL (Do Immediately)
**None identified** - System is secure

### 🟠 HIGH PRIORITY (Complete within 24-48 hours)

#### 1. Fix Dockerfile Syntax Error
**File**: `Dockerfile` (Line 37)  
**Issue**: Malformed multi-line Python RUN command  
**Impact**: Cannot build Docker containers  
**Effort**: 30 minutes

**Steps**:
```bash
# 1. Open Dockerfile
nano Dockerfile

# 2. Locate line 37 (multi-line Python RUN command)
# 3. Fix syntax error (proper line continuation)
# 4. Test build
docker build -t landscape-tool:test .

# 5. Verify build succeeds
docker images | grep landscape-tool
```

**Verification**:
```bash
docker build -t landscape-tool:v1d .
# Should complete without errors
```

---

### 🟡 MEDIUM PRIORITY (Complete within 1 week)

#### 2. Configure VPS Firewall
**Target**: VPS at 72.60.176.200  
**Tool**: UFW (Uncomplicated Firewall)  
**Effort**: 30 minutes

**Implementation**:
```bash
# Connect to VPS
ssh root@72.60.176.200

# Install UFW if not present
apt-get update
apt-get install -y ufw

# Configure firewall rules
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 8080/tcp comment 'Application'

# Enable firewall
ufw --force enable

# Verify status
ufw status verbose
```

**Expected Output**:
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
8080/tcp                   ALLOW IN    Anywhere
```

**Verification Script**:
```bash
# Test SSH still works
ssh root@72.60.176.200 'echo "SSH OK"'

# Test application still accessible
curl http://72.60.176.200:8080/health
```

#### 3. Disable SSH Password Authentication
**Target**: VPS SSH configuration  
**Effort**: 15 minutes

**Implementation**:
```bash
# Connect to VPS
ssh root@72.60.176.200

# Edit SSH configuration
nano /etc/ssh/sshd_config

# Make these changes:
# PermitRootLogin prohibit-password
# PasswordAuthentication no
# PubkeyAuthentication yes
# ChallengeResponseAuthentication no

# Test configuration
sshd -t

# Restart SSH service
systemctl restart sshd

# IMPORTANT: Keep current SSH session open and test from NEW terminal
# ssh root@72.60.176.200
```

**⚠️ WARNING**: Keep an existing SSH session open until you verify key-based login works!

**Verification**:
```bash
# From another terminal (should work with key)
ssh root@72.60.176.200 'echo "Key auth OK"'

# Try password auth (should fail)
ssh -o PreferredAuthentications=password root@72.60.176.200
# Expected: Permission denied
```

#### 4. Install Fail2Ban
**Purpose**: Prevent brute force attacks  
**Effort**: 30 minutes

**Implementation**:
```bash
# Connect to VPS
ssh root@72.60.176.200

# Install fail2ban
apt-get install -y fail2ban

# Create custom configuration
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = admin@yourdomain.com
sendername = Fail2Ban

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

# Start and enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Check status
fail2ban-client status
```

**Verification**:
```bash
# Check fail2ban is running
systemctl status fail2ban

# Check jails
fail2ban-client status sshd

# View banned IPs
fail2ban-client status sshd | grep "Banned IP"
```

#### 5. Add Environment-Specific CORS Origins
**File**: Production `.env` file  
**Issue**: CORS currently allows all origins  
**Effort**: 10 minutes

**Implementation**:
```bash
# Edit production .env file
nano /var/www/landscape-architecture-tool/.env

# Add specific CORS origins
CORS_ORIGINS=http://72.60.176.200:8080,https://optura.nl

# Restart application
systemctl restart landscape-backend
```

**Verification**:
```bash
# Test CORS headers
curl -H "Origin: http://72.60.176.200:8080" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     -v \
     http://72.60.176.200:8080/api/suppliers/

# Should see Access-Control-Allow-Origin header
```

---

### 🟢 LOW PRIORITY (Complete within 1 month)

#### 6. Implement Monitoring (Sentry)
**Purpose**: Error tracking and performance monitoring  
**Effort**: 2-4 hours

**Implementation**:
```bash
# 1. Sign up for Sentry (free tier available)
# Visit: https://sentry.io/signup/

# 2. Create new project (Python/Flask)

# 3. Get DSN from Sentry dashboard

# 4. Add to requirements.txt
echo "sentry-sdk[flask]>=1.40.0" >> requirements.txt

# 5. Update main.py
```

Add to `src/main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
    environment=os.getenv('FLASK_ENV', 'production')
)
```

**Configuration**:
```bash
# Add to .env
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Restart application
systemctl restart landscape-backend
```

**Verification**:
```python
# Test error reporting
@app.route('/test-sentry')
def test_sentry():
    1/0  # Intentional error
```

#### 7. Implement API Versioning
**Purpose**: Future-proof API changes  
**Effort**: 2-3 hours

**Implementation Steps**:

1. **Create versioned blueprint structure**:
```python
# src/routes/v1/__init__.py
from flask import Blueprint

v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import all route modules
from src.routes.v1 import suppliers, plants, products
```

2. **Update route registrations**:
```python
# src/main.py
from src.routes.v1 import v1_bp
app.register_blueprint(v1_bp)
```

3. **Create migration guide**:
```markdown
# API_MIGRATION_GUIDE.md
## V1 → V2 Migration

Old: /api/suppliers/
New: /api/v1/suppliers/

Deprecation timeline:
- v1: Current (no changes)
- v2: Planned for Q2 2026
- v1 EOL: Q4 2026
```

**Verification**:
```bash
# Test both endpoints work
curl http://72.60.176.200:8080/api/suppliers/
curl http://72.60.176.200:8080/api/v1/suppliers/
```

#### 8. SSL/TLS for Development Environment
**Purpose**: Match production environment  
**Effort**: 1-2 hours

**Options**:

**Option A: Self-Signed Certificate (Quick)**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=72.60.176.200"

# Update nginx config
# Listen on 443 with SSL
```

**Option B: Let's Encrypt (Recommended for production)**
```bash
# Install certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate (requires domain)
certbot --nginx -d optura.nl -d www.optura.nl

# Auto-renewal
systemctl enable certbot.timer
```

**Verification**:
```bash
# Test HTTPS
curl https://72.60.176.200:8080/health
# or
curl https://optura.nl/health
```

#### 9. Database Backup Automation
**Purpose**: Automated daily backups  
**Effort**: 1 hour

**Implementation**:
```bash
# Create backup script
cat > /root/backup-database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U landscape_user landscape_production | \
  gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Remove old backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Log backup
echo "[$TIMESTAMP] Database backup completed" >> /var/log/backup.log
EOF

chmod +x /root/backup-database.sh

# Add to crontab (daily at 2 AM)
crontab -l | { cat; echo "0 2 * * * /root/backup-database.sh"; } | crontab -
```

**Verification**:
```bash
# Test backup script
/root/backup-database.sh

# Check backup created
ls -lh /var/backups/database/

# View cron jobs
crontab -l
```

#### 10. Uptime Monitoring
**Purpose**: External monitoring for availability  
**Effort**: 30 minutes

**Recommended Services** (Free tiers available):
- UptimeRobot (https://uptimerobot.com/)
- Pingdom (https://www.pingdom.com/)
- StatusCake (https://www.statuscake.com/)

**Setup Steps**:
1. Sign up for monitoring service
2. Add monitor for: `http://72.60.176.200:8080/health`
3. Configure alert notifications (email/SMS)
4. Set check interval (5 minutes recommended)

**Health Endpoint Requirements**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "connected",
  "timestamp": "2025-10-01T12:00:00Z"
}
```

---

## Testing and Validation Checklist

### Pre-Deployment Testing

- [ ] **Backend Tests**
  ```bash
  cd /path/to/landscape-architecture-tool
  make backend-test
  # Expected: All tests pass
  ```

- [ ] **Frontend Build**
  ```bash
  cd frontend
  npm run build
  # Expected: Build succeeds without errors
  ```

- [ ] **Linting**
  ```bash
  make lint
  # Expected: No critical issues
  ```

- [ ] **Health Endpoint**
  ```bash
  curl http://72.60.176.200:8080/health
  # Expected: {"status": "healthy", ...}
  ```

- [ ] **Swagger UI**
  ```bash
  # Visit in browser
  http://72.60.176.200:8080/api/docs
  # Expected: Interactive API documentation
  ```

### Post-Implementation Testing

- [ ] **SSH Access**
  ```bash
  ssh root@72.60.176.200 'echo "SSH OK"'
  # Expected: Key-based auth works, password fails
  ```

- [ ] **Firewall Status**
  ```bash
  ssh root@72.60.176.200 'ufw status'
  # Expected: Active with rules for 22, 8080
  ```

- [ ] **Fail2Ban Status**
  ```bash
  ssh root@72.60.176.200 'systemctl status fail2ban'
  # Expected: Active and running
  ```

- [ ] **Application Health**
  ```bash
  curl http://72.60.176.200:8080/health
  # Expected: Healthy status
  ```

- [ ] **API Endpoints**
  ```bash
  curl http://72.60.176.200:8080/api/suppliers/
  # Expected: Valid JSON response
  ```

- [ ] **Rate Limiting**
  ```bash
  # Make 60 requests in quick succession
  for i in {1..60}; do 
    curl http://72.60.176.200:8080/api/suppliers/
  done
  # Expected: 429 Too Many Requests after limit
  ```

- [ ] **Docker Build** (after Dockerfile fix)
  ```bash
  docker build -t landscape-tool:v1d .
  # Expected: Successful build
  ```

---

## Emergency Rollback Procedures

### If Deployment Fails

**Scenario 1: Application Won't Start**
```bash
# Connect to VPS
ssh root@72.60.176.200

# Check service status
systemctl status landscape-backend

# View logs
journalctl -u landscape-backend -n 50

# Rollback to backup
LATEST_BACKUP=$(ls -t /var/backups/landscape-* | head -1)
rm -rf /var/www/landscape-architecture-tool
cp -r $LATEST_BACKUP /var/www/landscape-architecture-tool
systemctl restart landscape-backend
```

**Scenario 2: SSH Locked Out**
```bash
# If you still have one session open:
# 1. Revert SSH config changes
sudo nano /etc/ssh/sshd_config
# Change back: PasswordAuthentication yes
sudo systemctl restart sshd

# If completely locked out:
# Contact VPS provider for console access
# Revert changes through provider's web console
```

**Scenario 3: Firewall Blocks Access**
```bash
# If you have console access:
ufw disable
# Fix rules, then re-enable

# If via SSH (before disconnect):
ufw allow 22/tcp
ufw reload
```

---

## Monitoring Dashboard Setup

### Recommended Dashboard Layout

**1. System Health**
- CPU usage
- Memory usage
- Disk space
- Network traffic

**2. Application Metrics**
- Request rate
- Response time
- Error rate
- Active users

**3. Security Metrics**
- Failed login attempts
- Rate limit violations
- Firewall blocks
- Fail2Ban bans

**4. Database Metrics**
- Connection count
- Query performance
- Database size
- Backup status

### Tools for Dashboard

**Free Options**:
1. **Grafana + Prometheus**
   - Self-hosted
   - Highly customizable
   - Steep learning curve

2. **Netdata**
   - Easy to install
   - Real-time monitoring
   - Beautiful UI

3. **UptimeRobot Dashboard**
   - External monitoring
   - Simple setup
   - Email alerts

**Installation Example (Netdata)**:
```bash
# Install Netdata
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Access dashboard
http://72.60.176.200:19999/

# Secure with nginx proxy
```

---

## Security Audit Schedule

### Daily
- [ ] Check fail2ban status
- [ ] Review error logs
- [ ] Monitor uptime

### Weekly
- [ ] Review access logs
- [ ] Check for security updates
- [ ] Verify backups completed

### Monthly
- [ ] Full security scan
- [ ] Update all dependencies
- [ ] Review and rotate secrets
- [ ] Test disaster recovery

### Quarterly
- [ ] Penetration testing
- [ ] Security training
- [ ] Policy review
- [ ] Infrastructure audit

---

## Quick Reference Commands

### Application Management
```bash
# Check status
systemctl status landscape-backend

# View logs
journalctl -u landscape-backend -f

# Restart
systemctl restart landscape-backend

# Check health
curl http://72.60.176.200:8080/health
```

### Firewall Management
```bash
# Check status
ufw status verbose

# Add rule
ufw allow 443/tcp

# Delete rule
ufw delete allow 443/tcp

# Reset (careful!)
ufw --force reset
```

### Fail2Ban Management
```bash
# Check status
fail2ban-client status

# Check specific jail
fail2ban-client status sshd

# Unban IP
fail2ban-client set sshd unbanip 1.2.3.4
```

### Database Management
```bash
# Connect to database
psql -U landscape_user landscape_production

# Backup database
pg_dump -U landscape_user landscape_production > backup.sql

# Restore database
psql -U landscape_user landscape_production < backup.sql
```

---

## Contact Information

**Repository**: HANSKMIEL/landscape-architecture-tool  
**Branch**: V1.00D  
**Development URL**: http://72.60.176.200:8080  
**Production URL**: optura.nl (when promoted)

**Documentation**:
- Main Analysis: `reports/validation/comprehensive_v1d_security_analysis.md`
- Technical Details: `reports/validation/technical_validation_details.md`
- This Document: `reports/validation/action_items.md`

---

**Last Updated**: October 1, 2025  
**Priority Status**:
- 🔴 Critical: 0 items
- 🟠 High: 1 item (Dockerfile fix)
- 🟡 Medium: 4 items
- 🟢 Low: 5 items

**Overall Status**: ✅ READY FOR IMPLEMENTATION
