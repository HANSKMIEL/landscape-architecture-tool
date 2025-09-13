#!/bin/bash
set -e

echo "=== Complete VPS Deployment for Landscape Architecture Tool ==="

# Find application directory
APP_DIR=""
for dir in "/var/www/landscape-architecture-tool" "/var/www/html/landscape-architecture-tool" "/home/landscape-architecture-tool" "/root/landscape-architecture-tool"; do
    if [ -d "$dir" ]; then
        APP_DIR="$dir"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    echo "Application directory not found. Cloning from GitHub..."
    mkdir -p /var/www
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
echo "Stopping existing services..."
systemctl stop landscape-backend 2>/dev/null || true
systemctl stop landscape-backend-corrected 2>/dev/null || true

# Kill any running gunicorn processes
echo "Stopping any running backend processes..."
pkill -f gunicorn 2>/dev/null || true
pkill -f "python.*wsgi" 2>/dev/null || true

# Set up virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install/update requirements
echo "Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend if needed
echo "Checking frontend build..."
if [ ! -d "frontend/build" ] || [ ! -f "frontend/build/index.html" ]; then
    echo "Building frontend..."
    cd frontend
    if command -v npm &> /dev/null; then
        npm install
        npm run build
    elif command -v yarn &> /dev/null; then
        yarn install
        yarn build
    else
        echo "Warning: No npm or yarn found, using existing build"
    fi
    cd ..
fi

# Set proper permissions
echo "Setting file permissions..."
chown -R www-data:www-data "$APP_DIR"
chmod +x wsgi.py
chmod +x complete_vps_deployment.sh

# Install systemd service
echo "Installing backend systemd service..."
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

# Reload systemd and start service
systemctl daemon-reload
systemctl enable landscape-backend
systemctl start landscape-backend

# Configure Nginx
echo "Configuring Nginx..."
cp nginx-optura.conf /etc/nginx/sites-available/optura.nl

# Enable site if not already enabled
if [ ! -L /etc/nginx/sites-enabled/optura.nl ]; then
    ln -s /etc/nginx/sites-available/optura.nl /etc/nginx/sites-enabled/
fi

# Remove default site if it exists
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "Testing Nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
    systemctl reload nginx
else
    echo "❌ Nginx configuration error"
    exit 1
fi

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Check service status
echo "Checking service status..."
echo "Backend service: $(systemctl is-active landscape-backend)"
echo "Nginx service: $(systemctl is-active nginx)"

# Test backend API locally
echo "Testing backend API locally..."
if curl -f http://127.0.0.1:5000/api/health; then
    echo "✅ Local backend API is working"
else
    echo "❌ Local backend API failed"
    echo "Backend service logs:"
    journalctl -u landscape-backend -n 10 --no-pager
fi

# Test external API endpoints
echo "Testing external API endpoints..."
sleep 2
if curl -f https://optura.nl/api/health; then
    echo "✅ External API is working"
else
    echo "❌ External API failed"
fi

# Test authentication endpoint
echo "Testing authentication endpoint..."
AUTH_RESPONSE=$(curl -s -X POST https://optura.nl/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')

if echo "$AUTH_RESPONSE" | grep -q "token\|success\|authenticated"; then
    echo "✅ Authentication endpoint is responding"
else
    echo "❌ Authentication endpoint failed"
    echo "Response: $AUTH_RESPONSE"
fi

echo "=== Deployment completed ==="
echo "🌐 Website: https://optura.nl"
echo "🔧 Backend service: $(systemctl is-active landscape-backend)"
echo "🌍 Nginx service: $(systemctl is-active nginx)"

# Show final status
echo ""
echo "=== Final Status Check ==="
systemctl status landscape-backend --no-pager -l
echo ""
echo "If there are any issues, check logs with:"
echo "journalctl -u landscape-backend -f"
