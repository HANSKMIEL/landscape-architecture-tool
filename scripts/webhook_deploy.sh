#!/bin/bash
# Webhook-triggered deployment script for VPS
# This script should be placed on the VPS and called via webhook

set -e

# Configuration
APP_DIR="/var/www/landscape-architecture-tool"
LOG_FILE="/var/log/landscape-deploy.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "🚀 Starting webhook deployment..."

# Navigate to app directory
cd "$APP_DIR" || exit 1

# Pull latest changes from V1.00D branch
log "📥 Pulling latest changes from V1.00D branch..."
git fetch --all
git reset --hard origin/V1.00D

# Stop existing services
log "🛑 Stopping existing services..."
systemctl stop landscape-backend 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
sleep 5

# Activate virtual environment and update dependencies
log "🔧 Updating Python dependencies..."
source venv/bin/activate || (python3 -m venv venv && source venv/bin/activate)
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend if npm is available
log "🎨 Building frontend..."
cd frontend
if command -v npm &> /dev/null; then
    npm ci --legacy-peer-deps
    npm run build
    log "✅ Frontend built successfully"
else
    log "⚠️ npm not found, skipping frontend build"
fi
cd ..

# Update systemd service file if needed
log "🔄 Updating systemd service..."
if [ ! -f "/etc/systemd/system/landscape-backend.service" ]; then
    cat > /etc/systemd/system/landscape-backend.service << 'EOF'
[Unit]
Description=Landscape Architecture Tool Backend API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/landscape-architecture-tool
Environment=PATH=/var/www/landscape-architecture-tool/venv/bin
Environment=FLASK_ENV=production
Environment=DATABASE_URL=sqlite:///landscape_architecture_prod.db
Environment=FLASK_APP=wsgi:application
ExecStart=/var/www/landscape-architecture-tool/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 --timeout 120 wsgi:application
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    log "✅ Systemd service updated"
fi

# Set proper permissions
log "🔐 Setting file permissions..."
chown -R www-data:www-data "$APP_DIR"
chmod +x wsgi.py

# Start services
log "▶️ Starting backend service..."
systemctl daemon-reload
systemctl start landscape-backend
systemctl enable landscape-backend

# Wait for service to start
sleep 10

# Verify deployment
log "🔍 Verifying deployment..."
if systemctl is-active --quiet landscape-backend; then
    log "✅ Backend service is running"
else
    log "❌ Backend service failed to start"
    systemctl status landscape-backend
    exit 1
fi

# Test health endpoint
if curl -f -s http://localhost:5000/health > /dev/null; then
    log "✅ Health endpoint responding"
else
    log "⚠️ Health endpoint not responding"
fi

log "🎉 Deployment completed successfully!"
log "📊 Service status:"
systemctl status landscape-backend --no-pager -l