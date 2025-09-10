# VPS Deployment Guide

This document provides comprehensive instructions for deploying the Landscape Architecture Tool to a VPS (Virtual Private Server).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Setup](#server-setup)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Nginx Configuration](#nginx-configuration)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Automated Deployment](#automated-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Ubuntu 24.04 LTS or similar Linux distribution
- Root access to the VPS
- Domain name (optional)
- SSH access

## Server Setup

1. **Update the system**:
   ```bash
   apt update && apt upgrade -y
   ```

2. **Install required packages**:
   ```bash
   apt install -y nginx python3.12 python3.12-venv python3.12-dev nodejs npm postgresql postgresql-contrib
   ```

3. **Configure firewall**:
   ```bash
   ufw allow 'Nginx Full'
   ufw allow ssh
   ufw enable
   ```

## Backend Deployment

1. **Create application directory**:
   ```bash
   mkdir -p /var/www/landscape-tool/backend
   ```

2. **Copy backend files**:
   ```bash
   # From your local machine
   scp -r src/* root@your-vps-ip:/var/www/landscape-tool/backend/
   ```

3. **Set up virtual environment**:
   ```bash
   cd /var/www/landscape-tool/backend
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Initialize the database**:
   ```bash
   python -c "from src.utils.db_init import init_db, populate_sample_data; init_db(); populate_sample_data()"
   ```

5. **Create a systemd service**:
   ```bash
   cat > /etc/systemd/system/landscape-tool.service << 'EOF'
   [Unit]
   Description=Landscape Architecture Tool Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/landscape-tool/backend
   Environment="PATH=/var/www/landscape-tool/backend/venv/bin"
   ExecStart=/var/www/landscape-tool/backend/venv/bin/gunicorn -b 127.0.0.1:5000 main:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

6. **Set proper permissions**:
   ```bash
   chown -R www-data:www-data /var/www/landscape-tool
   chmod -R 755 /var/www/landscape-tool
   ```

7. **Start and enable the service**:
   ```bash
   systemctl start landscape-tool
   systemctl enable landscape-tool
   ```

## Frontend Deployment

1. **Create frontend directory**:
   ```bash
   mkdir -p /var/www/landscape-tool/frontend/dist
   ```

2. **Build the frontend locally**:
   ```bash
   # On your local machine
   cd frontend
   npm ci
   npm run build
   ```

3. **Copy frontend files**:
   ```bash
   # From your local machine
   scp -r dist/* root@your-vps-ip:/var/www/landscape-tool/frontend/dist/
   ```

## Nginx Configuration

1. **Create Nginx configuration**:
   ```bash
   cat > /etc/nginx/sites-available/landscape-tool << 'EOF'
   server {
       listen 80;
       server_name your-domain.com;  # Replace with your domain or IP

       # Serve frontend
       location / {
           root /var/www/landscape-tool/frontend/dist;
           try_files $uri $uri/ /index.html;
           
           # Add proper MIME types for JavaScript modules
           types {
               application/javascript js mjs;
           }
       }

       # Proxy API requests to backend
       location /api/ {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # CORS headers
           add_header 'Access-Control-Allow-Origin' '$http_origin' always;
           add_header 'Access-Control-Allow-Credentials' 'true' always;
           add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
           add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With' always;
           
           # Handle preflight requests
           if ($request_method = 'OPTIONS') {
               add_header 'Access-Control-Allow-Origin' '$http_origin' always;
               add_header 'Access-Control-Allow-Credentials' 'true' always;
               add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
               add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With' always;
               add_header 'Access-Control-Max-Age' 1728000;
               add_header 'Content-Type' 'text/plain charset=UTF-8';
               add_header 'Content-Length' 0;
               return 204;
           }
       }
   }
   EOF
   ```

2. **Enable the site**:
   ```bash
   ln -s /etc/nginx/sites-available/landscape-tool /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

## Database Setup

1. **Create database and user**:
   ```bash
   sudo -u postgres psql
   ```

   ```sql
   CREATE DATABASE landscape_tool;
   CREATE USER landscape_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE landscape_tool TO landscape_user;
   \q
   ```

2. **Update database configuration**:
   ```bash
   # Edit the configuration file
   nano /var/www/landscape-tool/backend/config.py
   ```

   Update the database URI:
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://landscape_user:your_secure_password@localhost/landscape_tool'
   ```

3. **Restart the backend service**:
   ```bash
   systemctl restart landscape-tool
   ```

## Environment Configuration

1. **Create environment configuration file**:
   ```bash
   cat > /var/www/landscape-tool/backend/.env << 'EOF'
   FLASK_ENV=production
   SECRET_KEY=your_secure_secret_key
   CORS_ORIGINS=http://your-domain.com,http://your-vps-ip
   DATABASE_URL=postgresql://landscape_user:your_secure_password@localhost/landscape_tool
   EOF
   ```

2. **Set proper permissions**:
   ```bash
   chown www-data:www-data /var/www/landscape-tool/backend/.env
   chmod 600 /var/www/landscape-tool/backend/.env
   ```

## Automated Deployment

1. **Create deployment script**:
   ```bash
   mkdir -p /var/www/landscape-tool/scripts
   cat > /var/www/landscape-tool/scripts/deploy.sh << 'EOF'
   #!/bin/bash
   
   # Pull latest changes
   cd /var/www/landscape-tool
   git pull
   
   # Update backend
   cd /var/www/landscape-tool/backend
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Update frontend
   cd /var/www/landscape-tool/frontend
   npm ci
   npm run build
   
   # Restart services
   systemctl restart landscape-tool
   systemctl restart nginx
   
   echo "Deployment completed successfully!"
   EOF
   ```

2. **Make script executable**:
   ```bash
   chmod +x /var/www/landscape-tool/scripts/deploy.sh
   ```

3. **Set up webhook (optional)**:
   ```bash
   apt install -y webhook
   
   cat > /etc/webhook.conf << 'EOF'
   [
     {
       "id": "deploy-landscape-tool",
       "execute-command": "/var/www/landscape-tool/scripts/deploy.sh",
       "command-working-directory": "/var/www/landscape-tool",
       "response-message": "Deployment triggered successfully",
       "trigger-rule": {
         "match": {
           "type": "payload-hash-sha1",
           "secret": "your_webhook_secret",
           "parameter": {
             "source": "header",
             "name": "X-Hub-Signature"
           }
         }
       }
     }
   ]
   EOF
   
   systemctl enable webhook
   systemctl start webhook
   
   # Open webhook port
   ufw allow 9000/tcp
   ```

## Troubleshooting

### Backend Service Not Starting

1. **Check service status**:
   ```bash
   systemctl status landscape-tool
   ```

2. **Check logs**:
   ```bash
   journalctl -u landscape-tool
   ```

3. **Verify permissions**:
   ```bash
   ls -la /var/www/landscape-tool/backend
   ```

### Frontend Shows Blank Page

1. **Check Nginx error logs**:
   ```bash
   tail -f /var/log/nginx/error.log
   ```

2. **Verify file permissions**:
   ```bash
   ls -la /var/www/landscape-tool/frontend/dist
   ```

3. **Check browser console for JavaScript errors**

### Authentication Fails

1. **Check CORS configuration**:
   ```bash
   curl -I -X OPTIONS http://your-vps-ip/api/auth/login
   ```

2. **Test API directly**:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' http://localhost:5000/api/auth/login
   ```

3. **Check backend logs**:
   ```bash
   journalctl -u landscape-tool | grep "auth"
   ```

### Database Connection Issues

1. **Check database status**:
   ```bash
   systemctl status postgresql
   ```

2. **Verify database connection**:
   ```bash
   sudo -u www-data psql -h localhost -U landscape_user -d landscape_tool
   ```

3. **Check database logs**:
   ```bash
   tail -f /var/log/postgresql/postgresql-*.log
   ```
