#!/bin/bash
# DevDeploy Environment Diagnostic Script
# Checks development deployment configuration on VPS

echo "🔍 DevDeploy Environment Diagnostic"
echo "===================================="
echo ""

# Check deployment directory
echo "📁 Deployment Directory Check:"
if [ -d "/var/www/landscape-architecture-tool-dev" ]; then
    echo "✅ Development directory exists: /var/www/landscape-architecture-tool-dev"
    cd /var/www/landscape-architecture-tool-dev
    echo "   Current branch: $(git branch --show-current 2>/dev/null || echo 'Not a git repo')"
    echo "   Current commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
    echo "   Last commit message: $(git log -1 --oneline 2>/dev/null | cut -d' ' -f2- || echo 'N/A')"
else
    echo "❌ Development directory not found: /var/www/landscape-architecture-tool-dev"
    echo "   This needs to be created for DevDeploy deployments"
fi
echo ""

# Check virtual environment
echo "🐍 Python Virtual Environment Check:"
for venv_path in "/var/www/landscape-architecture-tool-dev/venv-dev" "/var/www/landscape-architecture-tool-dev/venv"; do
    if [ -d "$venv_path" ]; then
        echo "✅ Virtual environment found: $venv_path"
        if [ -f "$venv_path/bin/python" ]; then
            echo "   Python version: $($venv_path/bin/python --version)"
        fi
    fi
done
echo ""

# Check backend service
echo "🔧 Backend Service Check:"
SERVICE_NAME="landscape-backend-dev"
if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    echo "✅ Service exists: $SERVICE_NAME"
    echo "   Status: $(systemctl is-active $SERVICE_NAME 2>/dev/null || echo 'inactive')"
    echo "   Enabled: $(systemctl is-enabled $SERVICE_NAME 2>/dev/null || echo 'disabled')"
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo ""
        echo "📊 Service Details:"
        systemctl status $SERVICE_NAME --no-pager | grep -E "(Active:|Main PID:|Tasks:|Memory:|CGroup:)" || true
    fi
else
    echo "❌ Service not found: $SERVICE_NAME"
    echo "   Expected location: /etc/systemd/system/$SERVICE_NAME.service"
fi
echo ""

# Check port bindings
echo "🔌 Port Binding Check:"
echo "   Backend port 5001:"
if ss -tlnp 2>/dev/null | grep -q ":5001"; then
    echo "   ✅ Port 5001 is listening"
    ss -tlnp 2>/dev/null | grep ":5001" | head -5
else
    echo "   ❌ Port 5001 is NOT listening"
fi

echo "   Frontend port 8080:"
if ss -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "   ✅ Port 8080 is listening"
    ss -tlnp 2>/dev/null | grep ":8080" | head -5
else
    echo "   ❌ Port 8080 is NOT listening"
fi
echo ""

# Check nginx configuration
echo "🌐 Nginx Configuration Check:"
NGINX_CONF="/etc/nginx/sites-enabled/landscape-architecture-tool-dev"
if [ -f "$NGINX_CONF" ]; then
    echo "✅ Nginx config exists: $NGINX_CONF"
    echo "   Proxy pass configuration:"
    grep -E "proxy_pass|listen|server_name" "$NGINX_CONF" 2>/dev/null | sed 's/^/   /' || echo "   Unable to read config"
else
    echo "❌ Nginx config not found: $NGINX_CONF"
    echo "   Checking alternative locations..."
    for conf in /etc/nginx/sites-enabled/*dev* /etc/nginx/conf.d/*dev*; do
        [ -f "$conf" ] && echo "   Found: $conf"
    done
fi
echo ""

# Test connectivity
echo "🧪 Connectivity Test:"
echo "   Testing frontend (port 8080):"
if curl -s -m 5 http://127.0.0.1:8080/ | grep -q "devdeploy"; then
    echo "   ✅ Frontend accessible with devdeploy title"
elif curl -s -m 5 http://127.0.0.1:8080/ >/dev/null 2>&1; then
    echo "   ⚠️ Frontend accessible but title check failed"
else
    echo "   ❌ Frontend not accessible"
fi

echo "   Testing backend (port 5001):"
for endpoint in "/health" "/api/health"; do
    if curl -s -m 5 http://127.0.0.1:5001$endpoint 2>/dev/null | grep -q -E "(healthy|ok|success)"; then
        echo "   ✅ Backend API $endpoint responding"
        break
    fi
done
echo ""

# Check frontend build
echo "📦 Frontend Build Check:"
if [ -f "/var/www/landscape-architecture-tool-dev/frontend/dist/index.html" ]; then
    echo "✅ Frontend build exists"
    if grep -q "devdeploy" /var/www/landscape-architecture-tool-dev/frontend/dist/index.html; then
        echo "   ✅ DevDeploy title present in build"
    else
        echo "   ❌ DevDeploy title missing from build"
    fi
else
    echo "❌ Frontend build not found"
fi
echo ""

# Summary
echo "📋 Summary:"
echo "   Expected configuration:"
echo "   - Directory: /var/www/landscape-architecture-tool-dev"
echo "   - Branch: V1.00D"
echo "   - Service: landscape-backend-dev"
echo "   - Backend port: 5001 (public binding: 0.0.0.0:5001)"
echo "   - Frontend port: 8080 (via nginx)"
echo "   - Title: 'devdeploy - Landscape Architecture Tool (Development)'"
echo ""
echo "🔗 Access URLs:"
echo "   - Development frontend: http://72.60.176.200:8080"
echo "   - Development backend: http://72.60.176.200:5001"
echo ""
