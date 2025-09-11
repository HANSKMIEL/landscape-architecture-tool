#!/bin/bash
set -e

echo "=== Landscape Architecture Tool Backend Deployment (Corrected) ==="

# Find application directory
APP_DIR=""
for dir in "/var/www/landscape-architecture-tool" "/var/www/html/landscape-architecture-tool" "/home/landscape-architecture-tool"; do
    if [ -d "$dir" ]; then
        APP_DIR="$dir"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    echo "Application directory not found. Creating in /var/www..."
    cd /var/www
    git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
    APP_DIR="/var/www/landscape-architecture-tool"
fi

echo "Using application directory: $APP_DIR"
cd "$APP_DIR"

# Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull origin main || (git fetch --all && git reset --hard origin/main)

# Stop existing services
echo "Stopping existing backend services..."
systemctl stop landscape-backend 2>/dev/null || true
systemctl stop landscape-backend-corrected 2>/dev/null || true

# Set up virtual environment
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install requirements
echo "Installing/updating requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Set proper permissions
echo "Setting permissions..."
chown -R www-data:www-data "$APP_DIR"
chmod +x wsgi.py

# Install corrected systemd service
echo "Installing corrected systemd service..."
cp landscape-backend-corrected.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable landscape-backend-corrected

# Start backend service
echo "Starting backend service..."
systemctl start landscape-backend-corrected

# Wait and check service status
sleep 5
echo "Service status:"
systemctl status landscape-backend-corrected --no-pager

# Test backend API (local)
echo "Testing backend API locally..."
curl -f http://127.0.0.1:5000/api/health && echo "✅ Local API working" || echo "❌ Local API failed"

# Check if Nginx is configured for API proxy
echo "Checking Nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
    systemctl reload nginx
else
    echo "❌ Nginx configuration has issues"
fi

# Test external API endpoints
echo "Testing external API endpoints..."
sleep 2
curl -f https://optura.nl/api/health && echo "✅ External API working" || echo "❌ External API failed - check Nginx proxy configuration"

# Test authentication endpoint
echo "Testing authentication endpoint..."
curl -X POST https://optura.nl/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' && echo "✅ Auth endpoint responding" || echo "❌ Auth endpoint failed"

echo "=== Deployment completed ==="
echo "Backend service: $(systemctl is-active landscape-backend-corrected)"
echo "Nginx service: $(systemctl is-active nginx)"

# Show service logs if there are issues
if ! systemctl is-active --quiet landscape-backend-corrected; then
    echo "=== Service logs (last 20 lines) ==="
    journalctl -u landscape-backend-corrected -n 20 --no-pager
fi
