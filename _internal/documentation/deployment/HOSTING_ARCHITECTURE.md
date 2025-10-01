# Hosting Architecture and Deployment Strategy for Landscape Architecture Tool + N8n

## 🌐 Executive Summary

This document outlines the comprehensive hosting architecture for deploying the Landscape Architecture Tool with N8n integration on Hostinger VPS, providing a cost-effective, scalable, and secure solution for workflow automation.

## 🏗️ Architecture Overview

### Current vs. Enhanced Architecture

#### Before N8n Integration
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │  Flask Backend  │    │   PostgreSQL    │
│  Reverse Proxy  │ -> │     Python      │ -> │    Database     │
│   Port 80/443   │    │    Port 5000    │    │    Port 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         v                       v                       v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ React Frontend  │    │      Redis      │    │   File Storage  │
│    Port 5174    │    │ Cache/Sessions  │    │     Docker      │
│    (Vite SPA)   │    │    Port 6379    │    │    Volumes      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### After N8n Integration
```
                    ┌─────────────────┐
                    │     Nginx       │
                    │  Reverse Proxy  │
                    │   Port 80/443   │
                    └─────────┬───────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              v               v               v
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ React Frontend  │ │  Flask Backend  │ │      N8n        │
    │    Port 5174    │ │     Python      │ │   Automation    │
    │   (Vite SPA)    │ │    Port 5000    │ │    Port 5678    │
    └─────────────────┘ └─────────┬───────┘ └─────────┬───────┘
                                  │                   │
                  ┌───────────────┼───────────────────┼─────────┐
                  │               │                   │         │
                  v               v                   v         v
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │   PostgreSQL    │ │      Redis      │ │ External APIs   │ │   Monitoring    │
        │ Main + N8n DBs  │ │ Cache/Sessions  │ │ Email, CRM, etc │ │ Logs + Metrics  │
        │    Port 5432    │ │    Port 6379    │ │   Various       │ │   Port 9090     │
        └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🖥️ Hostinger VPS Specifications

### Recommended VPS Plans

#### Option 1: VPS 1 (Development/Small Production)
- **CPU**: 1 vCPU
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **Bandwidth**: Unlimited
- **Price**: €8-12/month
- **Use Case**: Development, testing, small client base

#### Option 2: VPS 2 (Production Recommended)
- **CPU**: 2 vCPU
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Bandwidth**: Unlimited
- **Price**: €15-25/month
- **Use Case**: Production with moderate automation workload

#### Option 3: VPS 3 (High Performance)
- **CPU**: 4 vCPU
- **RAM**: 16GB
- **Storage**: 200GB SSD
- **Bandwidth**: Unlimited
- **Price**: €30-45/month
- **Use Case**: Heavy automation, multiple workflows, high traffic

### Resource Allocation Planning

#### Memory Distribution (8GB VPS Example)
```
Total: 8GB RAM
├── System OS (Ubuntu): 1GB
├── Docker Engine: 0.5GB
├── Nginx: 0.1GB
├── PostgreSQL: 2GB
├── Redis: 0.5GB
├── Flask Backend: 1.5GB
├── React Frontend (Nginx): 0.1GB
├── N8n: 1.5GB
└── System Buffer: 0.8GB
```

#### Storage Distribution (100GB SSD Example)
```
Total: 100GB SSD
├── OS and System: 20GB
├── Docker Images: 10GB
├── Application Code: 5GB
├── PostgreSQL Data: 30GB
├── N8n Workflows/Logs: 10GB
├── Logs and Monitoring: 10GB
├── Backups (local): 10GB
└── Free Space: 5GB
```

## 🐳 Docker Container Architecture

### Service Dependencies and Startup Order

```yaml
# Startup sequence optimization
networks:
  landscape-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  # Layer 1: Core Infrastructure
  postgres:
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U landscape_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      landscape-network:
        ipv4_address: 172.20.0.10

  redis:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      landscape-network:
        ipv4_address: 172.20.0.11

  # Layer 2: Application Services
  landscape-backend:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      landscape-network:
        ipv4_address: 172.20.0.20

  n8n:
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    networks:
      landscape-network:
        ipv4_address: 172.20.0.21

  # Layer 3: Frontend and Proxy
  landscape-frontend:
    depends_on:
      - landscape-backend
    restart: unless-stopped
    networks:
      landscape-network:
        ipv4_address: 172.20.0.30

  nginx:
    depends_on:
      - landscape-frontend
      - landscape-backend
      - n8n
    restart: unless-stopped
    networks:
      landscape-network:
        ipv4_address: 172.20.0.40
```

### Container Resource Limits

```yaml
services:
  landscape-backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1.5G
        reservations:
          cpus: '0.5'
          memory: 512M

  n8n:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1.5G
        reservations:
          cpus: '0.25'
          memory: 512M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 128M
```

## 🔒 Security Architecture

### Network Security

#### Firewall Configuration (UFW)
```bash
# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (change port if using non-standard)
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Optional: Allow specific IPs for N8n admin access
ufw allow from YOUR_OFFICE_IP to any port 5678

# Optional: Database access for external tools (restrict by IP)
# ufw allow from TRUSTED_IP to any port 5432

# Enable firewall
ufw --force enable
```

#### SSL/TLS Configuration

```nginx
# Enhanced SSL configuration in nginx-n8n.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_stapling on;
ssl_stapling_verify on;

# HSTS (HTTP Strict Transport Security)
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### Application Security

#### Environment Variables Security
```bash
# Use strong passwords and secrets
SECRET_KEY=$(openssl rand -base64 64)
N8N_WEBHOOK_SECRET=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24)
N8N_BASIC_AUTH_PASSWORD=$(openssl rand -base64 16)

# Database connection with security parameters
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require&connect_timeout=30"
```

#### API Security Implementation
```python
# Rate limiting configuration
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

# Secure webhook endpoints
@limiter.limit("30 per minute")
@bp.route('/webhooks/n8n/project-created', methods=['POST'])
def trigger_project_created():
    # Implementation with input validation
    pass

# API key authentication for sensitive endpoints
@limiter.limit("10 per minute")
@bp.route('/api/admin/system-status', methods=['GET'])
@require_api_key
def system_status():
    # Administrative endpoint
    pass
```

## 📊 Monitoring and Logging Architecture

### Logging Strategy

#### Application Logs
```python
# Enhanced logging configuration
import logging
from logging.handlers import RotatingFileHandler
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage(),
            'thread': record.thread,
            'process': record.process
        }
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
            
        return json.dumps(log_data)

# Configure rotating file handler
handler = RotatingFileHandler(
    '/var/log/landscape-tool/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(JSONFormatter())
app.logger.addHandler(handler)
```

#### Docker Logging Configuration
```yaml
services:
  landscape-backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=landscape-backend"

  n8n:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=n8n"
```

### Monitoring Stack

#### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'landscape-backend'
    static_configs:
      - targets: ['landscape-backend:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
```

#### Health Check Implementation
```python
# Enhanced health check endpoint
@app.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Comprehensive health check with component status"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': __version__,
        'environment': os.environ.get('FLASK_ENV', 'unknown'),
        'components': {}
    }
    
    # Database health
    try:
        db.session.execute(text("SELECT 1"))
        health_data['components']['database'] = {
            'status': 'healthy',
            'response_time_ms': 0  # Measure actual response time
        }
    except Exception as e:
        health_data['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_data['status'] = 'degraded'
    
    # Redis health
    try:
        redis_client = redis.Redis.from_url(current_app.config['REDIS_URL'])
        redis_client.ping()
        health_data['components']['redis'] = {'status': 'healthy'}
    except Exception as e:
        health_data['components']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_data['status'] = 'degraded'
    
    # N8n connectivity
    try:
        import requests
        n8n_url = current_app.config.get('N8N_BASE_URL')
        response = requests.get(f"{n8n_url}/healthz", timeout=5)
        health_data['components']['n8n'] = {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time_ms': int(response.elapsed.total_seconds() * 1000)
        }
    except Exception as e:
        health_data['components']['n8n'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_data['status'] = 'degraded'
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code
```

## 🚀 Deployment Automation

### Automated Deployment Script

```bash
#!/bin/bash
# deploy-hostinger.sh - Automated deployment script

set -e

# Configuration
DEPLOY_DIR="/opt/landscape-architecture-tool"
BACKUP_DIR="/opt/backups"
LOG_FILE="/var/log/deployment.log"
DOMAIN="${DOMAIN:-yourdomain.com}"
EMAIL="${SSL_EMAIL:-admin@yourdomain.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date)]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date)] ERROR:${NC} $1" | tee -a $LOG_FILE
    exit 1
}

warn() {
    echo -e "${YELLOW}[$(date)] WARNING:${NC} $1" | tee -a $LOG_FILE
}

# Pre-deployment checks
check_requirements() {
    log "Checking system requirements..."
    
    # Check Docker
    docker --version > /dev/null 2>&1 || error "Docker is not installed"
    docker-compose --version > /dev/null 2>&1 || error "Docker Compose is not installed"
    
    # Check available space
    AVAILABLE=$(df / | tail -1 | awk '{print $4}')
    if [ $AVAILABLE -lt 5242880 ]; then  # 5GB in KB
        error "Insufficient disk space. Need at least 5GB free"
    fi
    
    # Check memory
    MEMORY=$(free -m | awk '/^Mem:/{print $2}')
    if [ $MEMORY -lt 4096 ]; then
        warn "System has less than 4GB RAM. Performance may be affected"
    fi
    
    log "System requirements check passed"
}

# Create backup before deployment
create_backup() {
    if [ -d "$DEPLOY_DIR" ]; then
        log "Creating backup before deployment..."
        BACKUP_FILE="$BACKUP_DIR/pre-deploy-$(date +%Y%m%d_%H%M%S).tar.gz"
        mkdir -p $BACKUP_DIR
        tar -czf $BACKUP_FILE -C $DEPLOY_DIR . --exclude='node_modules' --exclude='.git'
        log "Backup created: $BACKUP_FILE"
    fi
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        apt update
        apt install -y certbot python3-certbot-nginx
    fi
    
    # Create webroot directory
    mkdir -p /var/www/certbot
    
    # Check if certificate already exists
    if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        log "Obtaining SSL certificate for $DOMAIN..."
        certbot certonly --webroot \
            --webroot-path=/var/www/certbot \
            --email $EMAIL \
            --agree-tos \
            --no-eff-email \
            -d $DOMAIN
    else
        log "SSL certificate already exists for $DOMAIN"
    fi
    
    # Copy certificates to nginx directory
    mkdir -p $DEPLOY_DIR/ssl
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $DEPLOY_DIR/ssl/cert.pem
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $DEPLOY_DIR/ssl/key.pem
    
    # Set up auto-renewal
    CRON_CMD="0 2 * * * certbot renew --post-hook 'docker-compose -f $DEPLOY_DIR/docker-compose.yml restart nginx'"
    (crontab -l 2>/dev/null | grep -v "certbot renew"; echo "$CRON_CMD") | crontab -
    
    log "SSL setup completed"
}

# Deploy application
deploy_application() {
    log "Deploying application..."
    
    # Create deployment directory
    mkdir -p $DEPLOY_DIR
    cd $DEPLOY_DIR
    
    # Clone or update repository
    if [ -d ".git" ]; then
        log "Updating existing repository..."
        git pull origin main
    else
        log "Cloning repository..."
        git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git .
    fi
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    # Generate environment file if it doesn't exist
    if [ ! -f ".env.production" ]; then
        log "Generating production environment file..."
        cat > .env.production << EOF
# Generated environment file - UPDATE THESE VALUES
DATABASE_URL=postgresql://landscape_user:$(openssl rand -base64 24)@postgres:5432/landscape_architecture_prod
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$(openssl rand -base64 64)
FLASK_ENV=production
DEBUG=false
N8N_BASE_URL=http://n8n:5678
N8N_WEBHOOK_SECRET=$(openssl rand -base64 32)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=$(openssl rand -base64 16)
DOMAIN_NAME=$DOMAIN
SSL_EMAIL=$EMAIL
POSTGRES_DB=landscape_architecture_prod
POSTGRES_USER=landscape_user
POSTGRES_PASSWORD=$(openssl rand -base64 24)
N8N_DB_USER=n8n_user
N8N_DB_PASSWORD=$(openssl rand -base64 24)
EOF
        warn "Environment file created. Please review and update $DEPLOY_DIR/.env.production"
    fi
    
    # Build and start services
    log "Starting services..."
    docker-compose -f docker-compose.yml --env-file .env.production up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 30
    
    # Check service health
    check_deployment_health
    
    log "Application deployment completed"
}

# Check deployment health
check_deployment_health() {
    log "Checking deployment health..."
    
    # Check container status
    FAILED_SERVICES=$(docker-compose ps --filter "health=unhealthy" --format "table {{.Service}}")
    if [ ! -z "$FAILED_SERVICES" ]; then
        error "Some services are unhealthy: $FAILED_SERVICES"
    fi
    
    # Test HTTP endpoints
    sleep 10  # Give services time to fully start
    
    # Test health endpoint
    if curl -f -s "http://localhost/health" > /dev/null; then
        log "Health endpoint responding"
    else
        error "Health endpoint not responding"
    fi
    
    # Test API endpoint
    if curl -f -s "http://localhost/api/" > /dev/null; then
        log "API endpoint responding"
    else
        error "API endpoint not responding"
    fi
    
    # Test N8n endpoint (if accessible)
    if curl -f -s "http://localhost:5678/healthz" > /dev/null; then
        log "N8n endpoint responding"
    else
        warn "N8n endpoint not accessible (may be protected)"
    fi
    
    log "Health checks passed"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create monitoring directory
    mkdir -p $DEPLOY_DIR/monitoring
    
    # Create log rotation configuration
    cat > /etc/logrotate.d/landscape-tool << EOF
/var/log/landscape-tool/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
    
    # Setup system monitoring script
    cat > /usr/local/bin/landscape-monitor.sh << 'EOF'
#!/bin/bash
DEPLOY_DIR="/opt/landscape-architecture-tool"
LOG_FILE="/var/log/landscape-monitor.log"

check_services() {
    cd $DEPLOY_DIR
    UNHEALTHY=$(docker-compose ps --filter "health=unhealthy" -q)
    if [ ! -z "$UNHEALTHY" ]; then
        echo "[$(date)] Unhealthy services detected, attempting restart..." >> $LOG_FILE
        docker-compose restart
    fi
}

check_disk_space() {
    USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $USAGE -gt 85 ]; then
        echo "[$(date)] Warning: Disk usage is ${USAGE}%" >> $LOG_FILE
    fi
}

check_services
check_disk_space
EOF
    
    chmod +x /usr/local/bin/landscape-monitor.sh
    
    # Add monitoring cron job
    MONITOR_CRON="*/5 * * * * /usr/local/bin/landscape-monitor.sh"
    (crontab -l 2>/dev/null | grep -v "landscape-monitor.sh"; echo "$MONITOR_CRON") | crontab -
    
    log "Monitoring setup completed"
}

# Setup backup automation
setup_automated_backups() {
    log "Setting up automated backups..."
    
    cat > /usr/local/bin/landscape-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DEPLOY_DIR="/opt/landscape-architecture-tool"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Database backups
cd $DEPLOY_DIR
docker-compose exec -T postgres pg_dump -U landscape_user landscape_architecture_prod > $BACKUP_DIR/landscape_$DATE.sql
docker-compose exec -T postgres pg_dump -U n8n_user n8n_db > $BACKUP_DIR/n8n_$DATE.sql

# N8n workflow data
docker-compose exec -T n8n tar -czf - /home/node/.n8n > $BACKUP_DIR/n8n_data_$DATE.tar.gz

# Application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C $DEPLOY_DIR . --exclude='node_modules' --exclude='.git' --exclude='*.log'

# Cleanup old backups
find $BACKUP_DIR -name "*.sql" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup completed: $DATE" >> /var/log/landscape-backup.log
EOF
    
    chmod +x /usr/local/bin/landscape-backup.sh
    
    # Add backup cron job (daily at 2 AM)
    BACKUP_CRON="0 2 * * * /usr/local/bin/landscape-backup.sh"
    (crontab -l 2>/dev/null | grep -v "landscape-backup.sh"; echo "$BACKUP_CRON") | crontab -
    
    log "Automated backup setup completed"
}

# Main deployment function
main() {
    log "Starting Hostinger VPS deployment for Landscape Architecture Tool + N8n"
    
    check_requirements
    create_backup
    setup_ssl
    deploy_application
    setup_monitoring
    setup_automated_backups
    
    log "Deployment completed successfully!"
    log "Application URL: https://$DOMAIN"
    log "N8n Interface: https://$DOMAIN/n8n/"
    log "API Documentation: https://$DOMAIN/api/"
    
    echo ""
    echo -e "${GREEN}🎉 Deployment Summary:${NC}"
    echo -e "${GREEN}✅ Application:${NC} https://$DOMAIN"
    echo -e "${GREEN}✅ N8n Interface:${NC} https://$DOMAIN/n8n/"
    echo -e "${GREEN}✅ API Docs:${NC} https://$DOMAIN/api/"
    echo -e "${GREEN}✅ SSL:${NC} Enabled with Let's Encrypt"
    echo -e "${GREEN}✅ Monitoring:${NC} Health checks every 5 minutes"
    echo -e "${GREEN}✅ Backups:${NC} Daily at 2 AM, 30-day retention"
    echo ""
    echo -e "${YELLOW}⚠️  Important:${NC}"
    echo -e "1. Review and update ${DEPLOY_DIR}/.env.production"
    echo -e "2. Update N8n password at https://$DOMAIN/n8n/"
    echo -e "3. Configure your first N8n workflows"
    echo -e "4. Test the webhook endpoints"
    echo ""
}

# Run main function
main "$@"
```

## 💰 Cost Analysis and ROI

### Monthly Hosting Costs (Hostinger VPS)

| Resource | Cost (EUR/month) | Notes |
|----------|------------------|-------|
| VPS 2 (8GB RAM, 2 vCPU) | €20-25 | Recommended for production |
| Domain Name | €1-2 | Annual cost divided by 12 |
| SSL Certificate | €0 | Let's Encrypt (free) |
| Backup Storage | €5-10 | Optional cloud backup |
| **Total** | **€26-37** | Monthly operational cost |

### Comparison with Alternatives

| Platform | Monthly Cost | Pros | Cons |
|----------|--------------|------|------|
| **Hostinger VPS** | €26-37 | Full control, cost-effective | Self-managed |
| Heroku | €50-100 | Easy deployment | Expensive, limited control |
| DigitalOcean | €30-60 | Good performance | More complex pricing |
| AWS/GCP | €40-80 | Scalable | Complex, variable pricing |
| Azure | €45-85 | Enterprise features | Higher cost |

### Return on Investment (ROI)

#### Time Savings with N8n Automation
- **Manual client onboarding**: 2 hours → 15 minutes (85% reduction)
- **Project status updates**: 1 hour/week → 10 minutes (83% reduction)
- **Invoice processing**: 30 minutes → 5 minutes (83% reduction)
- **Inventory management**: 1 hour/week → 15 minutes (75% reduction)

#### Estimated Monthly Savings
- **Time saved**: 15-20 hours/month
- **Hourly rate**: €50-100/hour (landscape architect)
- **Monthly value**: €750-2000
- **ROI**: 2000%+ (savings vs. hosting cost)

## 📈 Scaling Strategy

### Horizontal Scaling Options

#### Multi-Container Setup (Future)
```yaml
# docker-compose.scale.yml
services:
  landscape-backend:
    deploy:
      replicas: 2
    environment:
      - INSTANCE_ID={{.Task.Slot}}

  n8n:
    deploy:
      replicas: 2
    environment:
      - N8N_INSTANCE_ID={{.Task.Slot}}

  nginx:
    # Load balancer configuration
    depends_on:
      - landscape-backend
```

#### Database Scaling
```yaml
# PostgreSQL read replicas
postgres-primary:
  image: postgres:15-alpine
  environment:
    - POSTGRES_REPLICATION_MODE=master

postgres-replica:
  image: postgres:15-alpine
  environment:
    - POSTGRES_REPLICATION_MODE=slave
    - POSTGRES_MASTER_SERVICE=postgres-primary
```

### Vertical Scaling Path

1. **Current**: VPS 2 (8GB RAM, 2 vCPU) - €20-25/month
2. **Growth**: VPS 3 (16GB RAM, 4 vCPU) - €35-45/month
3. **Enterprise**: VPS 4 (32GB RAM, 8 vCPU) - €60-80/month

### Migration Strategy to Dedicated Servers

When workload exceeds VPS capacity:

1. **Dedicated Server**: €100-200/month
2. **Multi-server Setup**: Load balancer + App servers
3. **Cloud Hybrid**: Critical components in cloud, static in VPS

## 🔧 Maintenance and Operations

### Automated Maintenance Tasks

#### Weekly Tasks (Automated)
```bash
#!/bin/bash
# weekly-maintenance.sh

# Update system packages
apt update && apt upgrade -y

# Update Docker images
cd /opt/landscape-architecture-tool
docker-compose pull
docker-compose up -d

# Cleanup unused Docker resources
docker system prune -f

# Rotate logs
logrotate -f /etc/logrotate.conf

# Check SSL certificate expiry
certbot renew --dry-run
```

#### Monthly Tasks (Semi-automated)
```bash
#!/bin/bash
# monthly-maintenance.sh

# Database maintenance
docker-compose exec postgres vacuumdb -U landscape_user -d landscape_architecture_prod -z
docker-compose exec postgres vacuumdb -U n8n_user -d n8n_db -z

# Check backup integrity
cd /opt/backups
LATEST_BACKUP=$(ls -t landscape_*.sql | head -1)
docker-compose exec postgres psql -U postgres -c "\l" > /dev/null

# Generate performance report
docker stats --no-stream > /var/log/performance-$(date +%Y%m).log

# Security updates check
unattended-upgrade -d
```

### Performance Monitoring

#### Key Metrics to Track
1. **Response Time**: API endpoint response times
2. **CPU Usage**: Container and system CPU utilization
3. **Memory Usage**: RAM consumption per service
4. **Disk I/O**: Database and file system performance
5. **Network**: Bandwidth usage and latency
6. **Error Rates**: Application and N8n workflow errors

#### Alerting Thresholds
- CPU usage > 80% for 5 minutes
- Memory usage > 90% for 2 minutes
- Disk space > 85%
- Response time > 2 seconds for API endpoints
- Error rate > 5% for 10 minutes

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] VPS provisioned and accessible
- [ ] Domain name configured with DNS
- [ ] SSH access configured
- [ ] Docker and Docker Compose installed
- [ ] Firewall rules configured
- [ ] SSL certificate obtained

### Deployment
- [ ] Repository cloned and configured
- [ ] Environment variables set
- [ ] Docker containers deployed
- [ ] Services health checked
- [ ] SSL certificates configured
- [ ] Nginx routing tested

### Post-Deployment
- [ ] Application accessible via HTTPS
- [ ] N8n interface accessible and secured
- [ ] API endpoints responding correctly
- [ ] Database connectivity verified
- [ ] Monitoring and logging active
- [ ] Backup automation configured
- [ ] Performance baseline established

### Go-Live
- [ ] Documentation updated
- [ ] Team training completed
- [ ] N8n workflows configured
- [ ] Client communication sent
- [ ] Support procedures documented
- [ ] Rollback plan prepared

---

*This hosting architecture provides a robust, scalable, and cost-effective foundation for deploying the Landscape Architecture Tool with N8n workflow automation on Hostinger VPS infrastructure.*