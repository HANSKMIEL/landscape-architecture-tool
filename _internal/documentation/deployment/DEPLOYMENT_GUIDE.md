# N8n Deployment Guide for Hostinger VPS

This guide provides step-by-step instructions for deploying the Landscape Architecture Tool with N8n integration on Hostinger VPS.

## 🎯 Pre-Deployment Checklist

### VPS Requirements
- ✅ Ubuntu 22.04 LTS or newer
- ✅ Minimum 4GB RAM, 2 vCPU cores
- ✅ 40GB+ SSD storage
- ✅ Root or sudo access
- ✅ Domain name pointed to VPS IP

### Prerequisites Installation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

## 🚀 Quick Deployment

### Step 1: Application Setup
```bash
# Create application directory
sudo mkdir -p /opt/landscape-architecture-tool
cd /opt/landscape-architecture-tool

# Clone repository
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git .

# Make scripts executable
chmod +x scripts/*.sh
```

### Step 2: Environment Configuration
```bash
# Copy environment template
cp .env.example .env.production

# Generate secure passwords
export SECRET_KEY=$(openssl rand -base64 64)
export N8N_WEBHOOK_SECRET=$(openssl rand -base64 32)
export POSTGRES_PASSWORD=$(openssl rand -base64 24)
export N8N_PASSWORD=$(openssl rand -base64 16)

# Update environment file
cat > .env.production << EOF
# Application Configuration
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://landscape_user:${POSTGRES_PASSWORD}@postgres:5432/landscape_architecture_prod
REDIS_URL=redis://redis:6379/0

# N8n Integration
N8N_BASE_URL=http://n8n:5678
N8N_WEBHOOK_SECRET=${N8N_WEBHOOK_SECRET}
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}

# Domain Configuration
DOMAIN_NAME=your-domain.com
SSL_EMAIL=your-email@domain.com

# PostgreSQL
POSTGRES_DB=landscape_architecture_prod
POSTGRES_USER=landscape_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# CORS
CORS_ORIGINS=https://your-domain.com
EOF

echo "Generated passwords:"
echo "Database: ${POSTGRES_PASSWORD}"
echo "N8n Admin: ${N8N_PASSWORD}"
echo "Webhook Secret: ${N8N_WEBHOOK_SECRET}"
```

### Step 3: SSL Certificate Setup
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Create webroot directory
sudo mkdir -p /var/www/certbot

# Generate certificate (replace with your domain)
sudo certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@domain.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com

# Copy certificates
sudo mkdir -p /opt/landscape-architecture-tool/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/
```

### Step 4: Deploy Application Stack
```bash
# Deploy with production configuration
docker-compose -f docker-compose.n8n.yml --env-file .env.production up -d

# Check deployment status
docker-compose -f docker-compose.n8n.yml ps

# View logs
docker-compose -f docker-compose.n8n.yml logs -f
```

### Step 5: Verify Deployment
```bash
# Wait for services to start
sleep 30

# Test health endpoints
curl -f http://localhost/health || echo "Health check failed"
curl -f http://localhost/api/ || echo "API check failed"

# Test N8n interface (should require authentication)
curl -I http://localhost/n8n/ || echo "N8n interface check"
```

## 🔧 N8n Configuration

### Initial Setup
1. **Access N8n Interface:**
   - URL: `https://your-domain.com/n8n/`
   - Username: `admin`
   - Password: Generated in Step 2

2. **Import Workflows:**
   - Go to "Workflows" → "Import from File"
   - Import all JSON files from `n8n-workflows/` directory

3. **Configure Credentials:**
   - Go to "Settings" → "Credentials"
   - Add SMTP credentials for email sending
   - Add Google API credentials (optional)

### SMTP Configuration
```yaml
Host: smtp.gmail.com
Port: 587
Security: STARTTLS
Username: your-email@gmail.com
Password: your-app-password
```

### Test Workflows
```bash
# Test client onboarding
curl -X POST https://your-domain.com/webhook/client-onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "client_name": "Test Client",
    "client_email": "test@example.com"
  }'

# Test project milestone
curl -X POST https://your-domain.com/webhook/project-milestone \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "milestone": "design_completed",
    "completion_percentage": 50
  }'

# Test inventory alert
curl -X POST https://your-domain.com/webhook/inventory-alert \
  -H "Content-Type: application/json" \
  -d '{
    "plant_id": 1,
    "current_stock": 2,
    "minimum_threshold": 10
  }'
```

## 🔒 Security Configuration

### Firewall Setup
```bash
# Configure UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# Optional: Restrict N8n admin access
# sudo ufw allow from YOUR_OFFICE_IP to any port 5678
```

### SSL Auto-Renewal
```bash
# Add auto-renewal cron job
(crontab -l 2>/dev/null; echo "0 2 * * * certbot renew --post-hook 'docker-compose -f /opt/landscape-architecture-tool/docker-compose.n8n.yml restart nginx'") | crontab -
```

### Backup Configuration
```bash
# Create backup script
cat > /usr/local/bin/landscape-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

cd /opt/landscape-architecture-tool

# Database backups
docker-compose -f docker-compose.n8n.yml exec -T postgres pg_dump -U landscape_user landscape_architecture_prod > $BACKUP_DIR/landscape_$DATE.sql
docker-compose -f docker-compose.n8n.yml exec -T postgres pg_dump -U n8n_user n8n_db > $BACKUP_DIR/n8n_$DATE.sql

# N8n workflow data
docker-compose -f docker-compose.n8n.yml exec -T n8n tar -czf - /home/node/.n8n > $BACKUP_DIR/n8n_data_$DATE.tar.gz

# Application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz . --exclude='node_modules' --exclude='.git'

# Cleanup old backups (30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/landscape-backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/landscape-backup.sh") | crontab -
```

## 📊 Monitoring Setup

### Health Monitoring
```bash
# Create monitoring script
cat > /usr/local/bin/landscape-monitor.sh << 'EOF'
#!/bin/bash
cd /opt/landscape-architecture-tool

# Check service health
UNHEALTHY=$(docker-compose -f docker-compose.n8n.yml ps --filter "health=unhealthy" -q)
if [ ! -z "$UNHEALTHY" ]; then
    echo "[$(date)] Unhealthy services detected, restarting..." >> /var/log/landscape-monitor.log
    docker-compose -f docker-compose.n8n.yml restart
fi

# Check disk space
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt 85 ]; then
    echo "[$(date)] Warning: Disk usage is ${USAGE}%" >> /var/log/landscape-monitor.log
fi

# Check application endpoints
if ! curl -f -s http://localhost/health > /dev/null; then
    echo "[$(date)] Health endpoint failed" >> /var/log/landscape-monitor.log
fi
EOF

chmod +x /usr/local/bin/landscape-monitor.sh

# Schedule monitoring every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/landscape-monitor.sh") | crontab -
```

### Log Rotation
```bash
# Configure log rotation
sudo cat > /etc/logrotate.d/landscape-tool << EOF
/var/log/landscape-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}

/opt/landscape-architecture-tool/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

## 🔄 Maintenance Procedures

### Regular Updates
```bash
# Weekly update script
cat > /usr/local/bin/landscape-update.sh << 'EOF'
#!/bin/bash
cd /opt/landscape-architecture-tool

# Pull latest changes
git pull origin main

# Update Docker images
docker-compose -f docker-compose.n8n.yml pull

# Restart services with new images
docker-compose -f docker-compose.n8n.yml up -d

# Clean up unused images
docker image prune -f

echo "Update completed: $(date)"
EOF

chmod +x /usr/local/bin/landscape-update.sh
```

### Performance Monitoring
```bash
# Performance report script
cat > /usr/local/bin/landscape-performance.sh << 'EOF'
#!/bin/bash
REPORT_FILE="/var/log/performance-$(date +%Y%m).log"

echo "=== Performance Report $(date) ===" >> $REPORT_FILE
echo "CPU Usage:" >> $REPORT_FILE
top -bn1 | grep "Cpu(s)" >> $REPORT_FILE

echo "Memory Usage:" >> $REPORT_FILE
free -h >> $REPORT_FILE

echo "Disk Usage:" >> $REPORT_FILE
df -h >> $REPORT_FILE

echo "Docker Stats:" >> $REPORT_FILE
docker stats --no-stream >> $REPORT_FILE

echo "========================" >> $REPORT_FILE
EOF

chmod +x /usr/local/bin/landscape-performance.sh

# Run monthly performance reports
(crontab -l 2>/dev/null; echo "0 0 1 * * /usr/local/bin/landscape-performance.sh") | crontab -
```

## 🐛 Troubleshooting

### Common Issues

**Service Won't Start:**
```bash
# Check container logs
docker-compose -f docker-compose.n8n.yml logs service-name

# Check resource usage
docker stats

# Restart specific service
docker-compose -f docker-compose.n8n.yml restart service-name
```

**N8n Workflows Not Triggering:**
```bash
# Check webhook URLs
curl -I https://your-domain.com/webhook/test-webhook

# Check N8n logs
docker-compose -f docker-compose.n8n.yml logs n8n

# Verify credentials in N8n interface
```

**Email Not Sending:**
```bash
# Test SMTP connection from N8n container
docker-compose -f docker-compose.n8n.yml exec n8n \
  curl -v telnet://smtp.gmail.com:587

# Check email credentials in N8n
# Verify app password for Gmail
```

**Database Connection Issues:**
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.n8n.yml logs postgres

# Test database connection
docker-compose -f docker-compose.n8n.yml exec postgres \
  psql -U landscape_user -d landscape_architecture_prod -c "SELECT 1;"
```

### Recovery Procedures

**Restore from Backup:**
```bash
# Stop services
docker-compose -f docker-compose.n8n.yml down

# Restore database
docker-compose -f docker-compose.n8n.yml up -d postgres
docker-compose -f docker-compose.n8n.yml exec -T postgres \
  psql -U landscape_user -d landscape_architecture_prod < backup.sql

# Restore N8n data
docker-compose -f docker-compose.n8n.yml exec -T n8n \
  tar -xzf - -C /home/node/.n8n < n8n_backup.tar.gz

# Restart all services
docker-compose -f docker-compose.n8n.yml up -d
```

## 📈 Scaling Considerations

### Performance Optimization
```yaml
# Update docker-compose.n8n.yml for high traffic
services:
  landscape-backend:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
  
  n8n:
    environment:
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_TIMEOUT=7200
      - N8N_METRICS=true
```

### Database Scaling
```bash
# Enable PostgreSQL connection pooling
# Add to postgres environment:
# - POSTGRES_MAX_CONNECTIONS=200
# - POSTGRES_SHARED_BUFFERS=256MB
```

## 🎉 Deployment Verification

After completing deployment, verify these endpoints:

- ✅ **Main Application**: `https://your-domain.com`
- ✅ **API Documentation**: `https://your-domain.com/api/`
- ✅ **Health Check**: `https://your-domain.com/health`
- ✅ **N8n Interface**: `https://your-domain.com/n8n/`
- ✅ **N8n Status**: `https://your-domain.com/api/n8n/status`

**Success Metrics:**
- All services running in Docker
- SSL certificates valid
- N8n workflows imported and active
- Email notifications working
- Backup automation configured
- Monitoring scripts operational

---

*Your Landscape Architecture Tool with N8n automation is now deployed and ready for production use!*