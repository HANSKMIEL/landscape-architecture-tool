# Production Deployment Guide
# Landscape Architecture Tool - Professional Business System

This guide provides step-by-step instructions for deploying the Landscape Architecture Tool to production environments for real business use.

## 🚀 Quick Production Setup

### Prerequisites
- Ubuntu 20.04+ or similar Linux server
- Docker and Docker Compose installed
- Domain name pointing to your server
- SSL certificate (Let's Encrypt recommended)
- 2GB+ RAM, 20GB+ storage

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application user
sudo useradd -m -s /bin/bash landscape
sudo usermod -aG docker landscape
```

### 2. Application Deployment

```bash
# Switch to application user
sudo su - landscape

# Clone repository
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
cd landscape-architecture-tool

# Create production environment file
cp .env.example .env.production
```

### 3. Environment Configuration

Edit `.env.production` with your production values:

```bash
# Database Configuration
DATABASE_URL=postgresql://landscape_user:secure_password_here@postgres:5432/landscape_production
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-very-secure-secret-key-generate-with-python-secrets
FLASK_ENV=production
DEBUG=false

# Email Configuration (for notifications)
SMTP_SERVER=smtp.your-domain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@your-domain.com
SMTP_PASSWORD=your-email-password

# AI Services (Optional - for intelligent data mapping)
OPENAI_API_KEY=your-openai-api-key-for-ai-assistance

# Domain Configuration
DOMAIN=your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# SSL Configuration
SSL_EMAIL=admin@your-domain.com

# Business Configuration
COMPANY_NAME=Your Landscape Architecture Company
COMPANY_ADDRESS=Your Business Address
COMPANY_VAT=NL123456789B01
```

### 4. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Generate SSL certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com --email admin@your-domain.com --agree-tos --non-interactive

# Copy certificates to application directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
sudo chown landscape:landscape ssl/*
```

### 5. Production Deployment

```bash
# Build and start production services
docker-compose -f docker-compose.production.yml up -d

# Initialize database
docker-compose -f docker-compose.production.yml exec web flask db upgrade

# Create admin user
docker-compose -f docker-compose.production.yml exec web python scripts/create_admin_user.py

# Load sample business data (optional)
docker-compose -f docker-compose.production.yml exec web python scripts/load_sample_data.py
```

## 📋 Production Configuration Files

### docker-compose.production.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.production.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

  web:
    build: .
    environment:
      - FLASK_ENV=production
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: landscape_production
      POSTGRES_USER: landscape_user
      POSTGRES_PASSWORD: secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### nginx.production.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:5000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Frontend static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Auth endpoints (stricter rate limiting)
        location /auth/ {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://app;
            access_log off;
        }
    }
}
```

## 🔧 Management Scripts

### scripts/create_admin_user.py

```python
#!/usr/bin/env python3
"""Create production admin user"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import create_app
from src.models.user import User
from src.utils.db_init import db
from werkzeug.security import generate_password_hash

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists")
            return
        
        # Get admin credentials from environment or prompt
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD')
        email = os.getenv('ADMIN_EMAIL', 'admin@your-domain.com')
        
        if not password:
            password = input("Enter admin password: ")
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            first_name='Administrator',
            last_name='User'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully")

if __name__ == '__main__':
    create_admin_user()
```

### scripts/backup_database.sh

```bash
#!/bin/bash
# Daily database backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
CONTAINER_NAME="landscape-architecture-tool_postgres_1"

# Create backup
docker exec $CONTAINER_NAME pg_dump -U landscape_user landscape_production > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: backup_$DATE.sql.gz"
```

### scripts/update_application.sh

```bash
#!/bin/bash
# Update application to latest version

echo "Updating Landscape Architecture Tool..."

# Pull latest changes
git pull origin main

# Build new images
docker-compose -f docker-compose.production.yml build

# Update database schema
docker-compose -f docker-compose.production.yml exec web flask db upgrade

# Restart services
docker-compose -f docker-compose.production.yml up -d

echo "Application updated successfully"
```

## 🔒 Security Configuration

### Firewall Setup

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### Monitoring Setup

```bash
# Install monitoring tools
sudo apt install htop iotop fail2ban -y

# Configure fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📈 Maintenance Tasks

### Daily Tasks (Automated)

1. **Database Backups**: Automated via cron job
2. **Log Rotation**: Configured via Docker logging
3. **Health Checks**: Built into Docker Compose
4. **SSL Certificate Renewal**: Automated via Certbot

### Weekly Tasks

1. **System Updates**: `sudo apt update && sudo apt upgrade`
2. **Backup Verification**: Test restore process
3. **Performance Review**: Check resource usage
4. **Security Scan**: Review logs for suspicious activity

### Monthly Tasks

1. **Application Updates**: Run update script
2. **Database Optimization**: VACUUM and ANALYZE
3. **SSL Certificate Check**: Verify renewal
4. **Capacity Planning**: Review growth metrics

## 🆘 Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs web

# Check system resources
df -h
free -h
```

**Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.production.yml exec postgres pg_isready

# Connect to database
docker-compose -f docker-compose.production.yml exec postgres psql -U landscape_user -d landscape_production
```

**SSL Certificate Issues**
```bash
# Check certificate validity
openssl x509 -in ssl/fullchain.pem -text -noout

# Renew certificate
sudo certbot renew
```

## 📞 Support

For production support:
- Check application logs: `docker-compose logs`
- Monitor system resources: `htop`, `df -h`
- Review nginx logs: `docker-compose logs nginx`
- Database maintenance: Use provided backup scripts

## 🎯 Production Checklist

- [ ] Server configured with adequate resources
- [ ] Domain name configured and pointing to server
- [ ] SSL certificates installed and configured
- [ ] Environment variables set securely
- [ ] Database backups automated
- [ ] Monitoring and alerting configured
- [ ] Firewall rules applied
- [ ] Admin user created
- [ ] Application health checks passing
- [ ] Documentation accessible to team

Your Landscape Architecture Tool is now ready for professional business use!