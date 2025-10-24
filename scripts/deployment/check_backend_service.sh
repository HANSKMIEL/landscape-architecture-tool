#!/bin/bash
# Script to check and diagnose backend service status on VPS

set -e

echo "🔍 Checking V1.00D Backend Service Status..."
echo "=============================================="

# SSH connection details
VPS_HOST="${VPS_HOST:-72.60.176.200}"
VPS_USER="${VPS_USER:-root}"
DEV_DIR="/var/www/landscape-architecture-tool-dev"

echo ""
echo "📡 Connecting to VPS: $VPS_USER@$VPS_HOST"
echo ""

# Check deployment directory exists
echo "1️⃣ Checking deployment directory..."
ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
if [ -d "/var/www/landscape-architecture-tool-dev" ]; then
    echo "✅ Development directory exists: /var/www/landscape-architecture-tool-dev"
    ls -la /var/www/landscape-architecture-tool-dev/ | head -15
else
    echo "❌ Development directory NOT FOUND"
    exit 1
fi
ENDSSH

echo ""
echo "2️⃣ Checking systemd services..."
ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
echo "📋 Available landscape services:"
systemctl list-unit-files | grep landscape || echo "No landscape services found"

echo ""
echo "🔍 Checking specific services:"
for service in landscape-backend-dev landscape-backend landscape-tool; do
    if systemctl list-unit-files | grep -q "$service"; then
        echo "  - $service: EXISTS"
        systemctl status "$service" --no-pager -l || true
    else
        echo "  - $service: NOT FOUND"
    fi
done
ENDSSH

echo ""
echo "3️⃣ Checking if backend process is running..."
ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
echo "🔍 Looking for Python/gunicorn processes on port 5001:"
ps aux | grep -E "(python|gunicorn|flask).*5001" | grep -v grep || echo "❌ No backend process found on port 5001"

echo ""
echo "🔍 Checking port 5001:"
netstat -tlnp | grep 5001 || echo "❌ Port 5001 is not listening"
ENDSSH

echo ""
echo "4️⃣ Checking virtual environment..."
ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
if [ -d "/var/www/landscape-architecture-tool-dev/venv" ]; then
    echo "✅ Virtual environment exists"
    /var/www/landscape-architecture-tool-dev/venv/bin/python --version
elif [ -d "/var/www/landscape-architecture-tool-dev/venv-dev" ]; then
    echo "✅ Virtual environment exists (venv-dev)"
    /var/www/landscape-architecture-tool-dev/venv-dev/bin/python --version
else
    echo "❌ No virtual environment found"
fi
ENDSSH

echo ""
echo "5️⃣ Testing manual backend startup..."
ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
cd /var/www/landscape-architecture-tool-dev
if [ -d "venv" ]; then
    VENV_PATH="venv"
elif [ -d "venv-dev" ]; then
    VENV_PATH="venv-dev"
else
    echo "❌ Cannot find virtual environment"
    exit 1
fi

echo "🧪 Testing backend startup (10 second test)..."
source "$VENV_PATH/bin/activate"
timeout 10s python src/main.py 2>&1 | head -20 &
sleep 3
if curl -s http://localhost:5001/health | head -5; then
    echo "✅ Backend responds on localhost:5001"
else
    echo "❌ Backend does not respond"
fi
killall python 2>/dev/null || true
ENDSSH

echo ""
echo "✅ Diagnostic complete!"
