# Hostinger Deployment Guide
# Complete setup for Landscape Architecture Tool on Hostinger

## 🚀 **Step 1: Hostinger Account Setup**

### **Account Creation Process:**
1. **Go to Hostinger.com** 
   - Click "Get Started" → Choose **Premium** or **Business** plan
   - Business plan recommended for Docker support and higher resources
   
2. **Domain Configuration:**
   - Register new domain or use existing domain
   - Example: `yourcompany-landscapes.com`
   - Configure subdomain for staging: `staging.yourcompany-landscapes.com`

3. **Hosting Plan Selection:**
   - **Recommended: Business Plan** (€3.99/month)
   - Features needed: Docker support, SSH access, 100GB storage, unlimited bandwidth
   - Alternative: Premium plan (€2.99/month) with limited Docker capability

### **Initial Hostinger Panel Setup:**
1. **Login to Hostinger Control Panel**
2. **Navigate to:** Hosting → Manage → Advanced → SSH Access
3. **Enable SSH Access** and note connection details
4. **Set up Domain DNS:**
   - Go to: Domains → Manage → DNS Zone
   - Add A record pointing to your server IP
   - Add CNAME for `staging` subdomain

## 🔧 **Step 2: Server Environment Setup**

### **SSH Connection:**
```bash
# Connect to your Hostinger server
ssh username@your-server-ip

# Or use Hostinger's built-in terminal
# Available at: Hosting → Manage → Advanced → Terminal
```

### **System Updates & Dependencies:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git unzip software-properties-common

# Install Docker (if not pre-installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js (for frontend builds)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx (for reverse proxy)
sudo apt install -y nginx

# Install Certbot (for SSL certificates)
sudo apt install -y certbot python3-certbot-nginx
```

## 📁 **Step 3: Application Deployment**

### **Clone and Setup Application:**
```bash
# Create application directory
sudo mkdir -p /var/www/landscape-tool
sudo chown $USER:$USER /var/www/landscape-tool
cd /var/www/landscape-tool

# Clone repository
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git .

# Create production environment file
cp .env.example .env.production
```

### **Configure Environment Variables:**
```bash
# Edit production environment
nano .env.production
```

**Production Environment Configuration:**
```bash
# Database Configuration
DATABASE_URL=postgresql://landscape_user:SECURE_PASSWORD_HERE@postgres:5432/landscape_production
REDIS_URL=redis://redis:6379/0

# Security (Generate strong keys)
SECRET_KEY=YOUR_VERY_SECURE_SECRET_KEY_HERE
FLASK_ENV=production
DEBUG=false

# Email Configuration (for notifications)
SMTP_SERVER=smtp.hostinger.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourcompany-landscapes.com
SMTP_PASSWORD=your_email_password

# AI Services (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Domain Configuration  
DOMAIN=yourcompany-landscapes.com
CORS_ORIGINS=https://yourcompany-landscapes.com,https://staging.yourcompany-landscapes.com

# Business Configuration
COMPANY_NAME=Your Landscape Architecture Company
COMPANY_ADDRESS=Your Business Address
COMPANY_VAT=NL123456789B01
```

### **Generate Secure Keys:**
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate database password
openssl rand -base64 32
```

## 🐳 **Step 4: Docker Configuration**

### **Create Hostinger-Optimized Docker Compose:**
```bash
# Create Hostinger production compose file
nano docker-compose.hostinger.yml
```

**docker-compose.hostinger.yml:**
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.hostinger.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - /var/log/nginx:/var/log/nginx
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - landscape-network

  web:
    build: 
      context: .
      dockerfile: Dockerfile.production
    environment:
      - FLASK_ENV=production
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    volumes:
      - ./uploads:/app/uploads
      - ./backups:/app/backups
    networks:
      - landscape-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: landscape_production
      POSTGRES_USER: landscape_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - landscape-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U landscape_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - landscape-network

  backup:
    image: postgres:15
    depends_on:
      - postgres
    volumes:
      - ./backups:/backups
    environment:
      PGPASSWORD: ${POSTGRES_PASSWORD}
    command: >
      bash -c "
        while true; do
          sleep 86400  # 24 hours
          pg_dump -h postgres -U landscape_user landscape_production > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql
          find /backups -name 'backup_*.sql' -mtime +30 -delete
        done
      "
    restart: unless-stopped
    networks:
      - landscape-network

volumes:
  postgres_data:
  redis_data:

networks:
  landscape-network:
    driver: bridge
```

## 🌐 **Step 5: Nginx Configuration**

### **Create Hostinger Nginx Config:**
```bash
nano nginx.hostinger.conf
```

**nginx.hostinger.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Upstream backend
    upstream app {
        server web:5000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name yourcompany-landscapes.com www.yourcompany-landscapes.com staging.yourcompany-landscapes.com;
        return 301 https://$server_name$request_uri;
    }

    # Production HTTPS
    server {
        listen 443 ssl http2;
        server_name yourcompany-landscapes.com www.yourcompany-landscapes.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        # SSL Security
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        add_header Referrer-Policy "strict-origin-when-cross-origin";

        # Frontend static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 60s;
            proxy_connect_timeout 60s;
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

        # Upload handling
        location /uploads/ {
            alias /var/www/landscape-tool/uploads/;
            expires 1M;
            add_header Cache-Control "public";
        }
    }

    # Staging HTTPS
    server {
        listen 443 ssl http2;
        server_name staging.yourcompany-landscapes.com;

        ssl_certificate /etc/nginx/ssl/staging-fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/staging-privkey.pem;
        
        # Same SSL and security settings as production
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS;
        
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Staging environment indicator
        add_header X-Environment "staging";

        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🔒 **Step 6: SSL Certificate Setup**

### **Generate SSL Certificates:**
```bash
# Create SSL directory
sudo mkdir -p /var/www/landscape-tool/ssl

# Generate certificates for production
sudo certbot certonly --standalone \
  -d yourcompany-landscapes.com \
  -d www.yourcompany-landscapes.com \
  --email admin@yourcompany-landscapes.com \
  --agree-tos --non-interactive

# Generate certificate for staging
sudo certbot certonly --standalone \
  -d staging.yourcompany-landscapes.com \
  --email admin@yourcompany-landscapes.com \
  --agree-tos --non-interactive

# Copy certificates to application directory
sudo cp /etc/letsencrypt/live/yourcompany-landscapes.com/fullchain.pem /var/www/landscape-tool/ssl/
sudo cp /etc/letsencrypt/live/yourcompany-landscapes.com/privkey.pem /var/www/landscape-tool/ssl/
sudo cp /etc/letsencrypt/live/staging.yourcompany-landscapes.com/fullchain.pem /var/www/landscape-tool/ssl/staging-fullchain.pem
sudo cp /etc/letsencrypt/live/staging.yourcompany-landscapes.com/privkey.pem /var/www/landscape-tool/ssl/staging-privkey.pem

# Set permissions
sudo chown -R $USER:$USER /var/www/landscape-tool/ssl
chmod 600 /var/www/landscape-tool/ssl/*.pem

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 🚀 **Step 7: Application Deployment**

### **Deploy Production Application:**
```bash
cd /var/www/landscape-tool

# Build and start services
docker-compose -f docker-compose.hostinger.yml up -d --build

# Initialize database
docker-compose -f docker-compose.hostinger.yml exec web flask db upgrade

# Create admin user
docker-compose -f docker-compose.hostinger.yml exec web python scripts/create_admin_user.py

# Load sample data (optional)
docker-compose -f docker-compose.hostinger.yml exec web python scripts/load_sample_data.py
```

### **Verify Deployment:**
```bash
# Check service status
docker-compose -f docker-compose.hostinger.yml ps

# Check logs
docker-compose -f docker-compose.hostinger.yml logs web

# Test application
curl -f https://yourcompany-landscapes.com/health
curl -f https://yourcompany-landscapes.com/api/dashboard/stats
```

## 🔄 **Step 8: Zero-Downtime Deployment Workflow**

### **Create Deployment Scripts:**
```bash
# Create scripts directory
mkdir -p /var/www/landscape-tool/scripts
```

### **Blue-Green Deployment Script:**
```bash
nano /var/www/landscape-tool/scripts/deploy.sh
```

**scripts/deploy.sh:**
```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Zero-Downtime Deployment${NC}"

# Configuration
APP_DIR="/var/www/landscape-tool"
BACKUP_DIR="$APP_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

cd $APP_DIR

# Step 1: Create backup
echo -e "${YELLOW}📦 Creating pre-deployment backup...${NC}"
mkdir -p $BACKUP_DIR
docker-compose -f docker-compose.hostinger.yml exec -T postgres pg_dump -U landscape_user landscape_production > $BACKUP_DIR/pre_deploy_$TIMESTAMP.sql

# Step 2: Pull latest changes
echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
git pull origin main

# Step 3: Build new images
echo -e "${YELLOW}🔨 Building new application images...${NC}"
docker-compose -f docker-compose.hostinger.yml build web

# Step 4: Run database migrations
echo -e "${YELLOW}🗄️ Running database migrations...${NC}"
docker-compose -f docker-compose.hostinger.yml exec web flask db upgrade

# Step 5: Run tests
echo -e "${YELLOW}🧪 Running application tests...${NC}"
docker-compose -f docker-compose.hostinger.yml exec web python -m pytest tests/test_basic.py -v

# Step 6: Deploy with rolling update
echo -e "${YELLOW}🔄 Performing rolling update...${NC}"
docker-compose -f docker-compose.hostinger.yml up -d web

# Step 7: Health check
echo -e "${YELLOW}🏥 Performing health checks...${NC}"
sleep 30

for i in {1..10}; do
    if curl -f -s https://yourcompany-landscapes.com/health > /dev/null; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        break
    else
        echo -e "${YELLOW}⏳ Waiting for application to be ready... ($i/10)${NC}"
        sleep 10
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ Health check failed - rolling back${NC}"
            # Rollback logic here
            exit 1
        fi
    fi
done

# Step 8: Update frontend
echo -e "${YELLOW}🎨 Updating frontend...${NC}"
docker-compose -f docker-compose.hostinger.yml restart nginx

# Step 9: Cleanup old images
echo -e "${YELLOW}🧹 Cleaning up old Docker images...${NC}"
docker image prune -f

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}📊 Application available at: https://yourcompany-landscapes.com${NC}"
```

### **Make Script Executable:**
```bash
chmod +x /var/www/landscape-tool/scripts/deploy.sh
```

## 📊 **Step 9: Monitoring & Maintenance**

### **Setup Monitoring:**
```bash
# Create monitoring script
nano /var/www/landscape-tool/scripts/monitor.sh
```

**scripts/monitor.sh:**
```bash
#!/bin/bash
# Application monitoring script

# Check service health
echo "=== Service Status ==="
docker-compose -f docker-compose.hostinger.yml ps

# Check disk usage
echo "=== Disk Usage ==="
df -h

# Check memory usage
echo "=== Memory Usage ==="
free -h

# Check application health
echo "=== Application Health ==="
curl -s https://yourcompany-landscapes.com/health | jq .

# Check recent logs
echo "=== Recent Application Logs ==="
docker-compose -f docker-compose.hostinger.yml logs --tail=20 web
```

### **Setup Automated Backups:**
```bash
# Create backup script
nano /var/www/landscape-tool/scripts/backup.sh
```

**scripts/backup.sh:**
```bash
#!/bin/bash
# Automated backup script

BACKUP_DIR="/var/www/landscape-tool/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create database backup
docker-compose -f docker-compose.hostinger.yml exec -T postgres pg_dump -U landscape_user landscape_production > $BACKUP_DIR/backup_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/backup_$TIMESTAMP.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Backup uploads directory
tar -czf $BACKUP_DIR/uploads_$TIMESTAMP.tar.gz uploads/

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

### **Setup Cron Jobs:**
```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily backup at 2 AM
0 2 * * * /var/www/landscape-tool/scripts/backup.sh

# Monitor every 6 hours
0 */6 * * * /var/www/landscape-tool/scripts/monitor.sh > /var/log/landscape-monitor.log

# SSL certificate renewal check
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 **Step 10: GitHub Actions Integration**

### **Setup GitHub Secrets:**
In your GitHub repository, go to Settings → Secrets and variables → Actions, add:

- `HOSTINGER_HOST`: Your server IP
- `HOSTINGER_USERNAME`: Your SSH username  
- `HOSTINGER_SSH_KEY`: Your private SSH key
- `PRODUCTION_DATABASE_URL`: Database connection string
- `PRODUCTION_SECRET_KEY`: Production secret key

### **Automated Deployment Workflow:**
The existing `.github/workflows/production-deployment.yml` will automatically deploy to Hostinger when you push to the `main` branch.

## ✅ **Step 11: Final Verification**

### **Test Complete Workflow:**
```bash
# Test production site
curl -f https://yourcompany-landscapes.com/health
curl -f https://yourcompany-landscapes.com/api/dashboard/stats

# Test staging site
curl -f https://staging.yourcompany-landscapes.com/health

# Test authentication
curl -X POST https://yourcompany-landscapes.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test SSL
openssl s_client -connect yourcompany-landscapes.com:443 -servername yourcompany-landscapes.com
```

## 🎯 **Next Steps After Deployment:**

1. **Update DNS settings** in your domain registrar to point to Hostinger
2. **Test all features** through the web interface
3. **Configure N8N workflows** for automation
4. **Setup email templates** for client communications
5. **Import your business data** using the Excel import feature
6. **Customize appearance** with your company branding
7. **Train your team** on the new system

## 📞 **Support & Troubleshooting:**

- **Application logs:** `docker-compose logs web`
- **Database connection:** `docker-compose exec postgres psql -U landscape_user landscape_production`
- **Nginx logs:** `docker-compose logs nginx`
- **SSL certificate status:** `certbot certificates`
- **System resources:** Run `scripts/monitor.sh`

Your Landscape Architecture Tool is now fully deployed on Hostinger with zero-downtime updates, automated backups, and production-ready monitoring! 🎉