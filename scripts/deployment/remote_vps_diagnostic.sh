#!/bin/bash
# Remote VPS Diagnostic Script
# This script runs diagnostic checks on the VPS to identify why services are not accessible

set -e

echo "=========================================="
echo "🔍 VPS Remote Diagnostic Check"
echo "=========================================="
echo ""

# Check if services are running
echo "1️⃣ Service Status Check:"
echo "----------------------------"

# Check landscape-backend-dev service
if systemctl is-active --quiet landscape-backend-dev 2>/dev/null; then
    echo "✅ landscape-backend-dev: RUNNING"
    systemctl status landscape-backend-dev --no-pager | grep -E "(Active|Main PID|Memory)" || true
else
    echo "❌ landscape-backend-dev: NOT RUNNING"
    if systemctl status landscape-backend-dev --no-pager 2>&1 | grep -q "could not be found"; then
        echo "   ⚠️  Service does not exist"
    else
        echo "   Failed status:"
        systemctl status landscape-backend-dev --no-pager | tail -10 || true
    fi
fi

echo ""

# Check landscape-backend service
if systemctl is-active --quiet landscape-backend 2>/dev/null; then
    echo "✅ landscape-backend: RUNNING"
    systemctl status landscape-backend --no-pager | grep -E "(Active|Main PID|Memory)" || true
else
    echo "❌ landscape-backend: NOT RUNNING"
    if systemctl status landscape-backend --no-pager 2>&1 | grep -q "could not be found"; then
        echo "   ⚠️  Service does not exist"
    else
        echo "   Failed status:"
        systemctl status landscape-backend --no-pager | tail -10 || true
    fi
fi

echo ""

# Check nginx
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "✅ nginx: RUNNING"
    systemctl status nginx --no-pager | grep -E "(Active|Main PID)" || true
else
    echo "❌ nginx: NOT RUNNING"
    systemctl status nginx --no-pager | tail -10 || true
fi

echo ""
echo "2️⃣ Process Check:"
echo "----------------------------"

# Check for gunicorn processes
GUNICORN_COUNT=$(pgrep -f gunicorn | wc -l)
if [ "$GUNICORN_COUNT" -gt 0 ]; then
    echo "✅ Gunicorn processes: $GUNICORN_COUNT"
    ps aux | grep gunicorn | grep -v grep | head -3 || true
else
    echo "❌ No Gunicorn processes running"
fi

echo ""

# Check for nginx processes
NGINX_COUNT=$(pgrep nginx | wc -l)
if [ "$NGINX_COUNT" -gt 0 ]; then
    echo "✅ Nginx processes: $NGINX_COUNT"
else
    echo "❌ No Nginx processes running"
fi

echo ""
echo "3️⃣ Port Availability Check:"
echo "----------------------------"

# Check if ports are listening
if command -v ss &> /dev/null; then
    echo "Port 5001 (Backend):"
    ss -tlnp | grep :5001 || echo "   ❌ Port 5001 not listening"
    echo ""
    echo "Port 8080 (Frontend/Nginx):"
    ss -tlnp | grep :8080 || echo "   ❌ Port 8080 not listening"
elif command -v netstat &> /dev/null; then
    echo "Port 5001 (Backend):"
    netstat -tlnp | grep :5001 || echo "   ❌ Port 5001 not listening"
    echo ""
    echo "Port 8080 (Frontend/Nginx):"
    netstat -tlnp | grep :8080 || echo "   ❌ Port 8080 not listening"
else
    echo "⚠️  Neither ss nor netstat available"
fi

echo ""
echo "4️⃣ Deployment Directory Check:"
echo "----------------------------"

# Check deployment directories
for dir in "/var/www/landscape-architecture-tool-dev" "/var/www/landscape-architecture-tool"; do
    if [ -d "$dir" ]; then
        echo "✅ Found: $dir"
        if [ -f "$dir/.git/HEAD" ]; then
            cd "$dir"
            echo "   Branch: $(git branch --show-current 2>/dev/null || echo 'Unknown')"
            echo "   Last commit: $(git log -1 --format='%h - %s' 2>/dev/null || echo 'Unknown')"
        fi
    else
        echo "❌ Not found: $dir"
    fi
done

echo ""
echo "5️⃣ System Resources:"
echo "----------------------------"

# Memory usage
echo "Memory:"
free -h | grep -E "(Mem|Swap)" || true

echo ""

# Disk usage
echo "Disk usage:"
df -h / | tail -1 || true

echo ""
echo "6️⃣ Recent System Log Errors:"
echo "----------------------------"

# Check for recent service errors
if command -v journalctl &> /dev/null; then
    echo "Recent landscape-backend errors (last 20 lines):"
    journalctl -u landscape-backend -n 20 --no-pager 2>/dev/null || journalctl -u landscape-backend-dev -n 20 --no-pager 2>/dev/null || echo "   No logs available"
else
    echo "⚠️  journalctl not available"
fi

echo ""
echo "7️⃣ Local Connectivity Test:"
echo "----------------------------"

# Test local connectivity
echo "Testing localhost:8080..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200"; then
    echo "✅ Frontend responds on localhost"
else
    echo "❌ Frontend not responding on localhost"
fi

echo ""
echo "Testing localhost:5001/health..."
if curl -s http://localhost:5001/health 2>/dev/null | grep -q "healthy"; then
    echo "✅ Backend health endpoint responds"
else
    echo "❌ Backend health endpoint not responding"
fi

echo ""
echo "=========================================="
echo "🏁 Diagnostic Check Complete"
echo "=========================================="
