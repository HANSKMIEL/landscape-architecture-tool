#!/bin/bash
# VPS Backend Fix - One-liner command
# Run this directly on your VPS as root

echo "=== Landscape Architecture Tool Backend Fix ==="

# Find application directory
APP_DIR=""
for dir in "/var/www/landscape-architecture-tool" "/root/landscape-architecture-tool" "/home/landscape-architecture-tool"; do
    if [ -d "$dir" ]; then
        APP_DIR="$dir"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    echo "Application directory not found. Cloning from GitHub..."
    cd /var/www
    git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
    APP_DIR="/var/www/landscape-architecture-tool"
fi

echo "Using application directory: $APP_DIR"
cd "$APP_DIR"

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Stop any existing processes
echo "Stopping existing processes..."
systemctl stop landscape-backend 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true

# Set up virtual environment
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/landscape-backend.service << 'EOF'
[Unit]
Description=Landscape Architecture Tool Backend
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/var/www/landscape-architecture-tool
Environment=PATH=/var/www/landscape-architecture-tool/venv/bin
Environment=FLASK_ENV=production
Environment=DATABASE_URL=sqlite:///landscape_architecture_prod.db
ExecStart=/var/www/landscape-architecture-tool/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload and start service
echo "Starting backend service..."
systemctl daemon-reload
systemctl enable landscape-backend
systemctl start landscape-backend

# Wait and check status
sleep 3
echo "Service status:"
systemctl status landscape-backend --no-pager

# Test API
echo "Testing API..."
curl -f http://127.0.0.1:5000/api/health && echo "✅ Backend API working" || echo "❌ Backend API failed"

# Restart nginx
echo "Restarting nginx..."
systemctl restart nginx

# Final test
echo "Final external API test..."
curl -f https://optura.nl/api/health && echo "✅ External API working" || echo "❌ External API failed"

echo "=== Fix completed ==="
echo "Backend service: $(systemctl is-active landscape-backend)"
echo "Nginx service: $(systemctl is-active nginx)"
