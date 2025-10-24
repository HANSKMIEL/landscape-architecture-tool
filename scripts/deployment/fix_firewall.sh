#!/bin/bash
# Fix VPS Firewall Configuration
# This script opens necessary ports for the landscape architecture tool

set -e

echo "=========================================="
echo "🔧 VPS Firewall Configuration Fix"
echo "=========================================="
echo ""

echo "📋 Opening required ports: 8080 (HTTP), 5001 (Backend API)"
echo ""

# Check if UFW is installed and active
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(ufw status | head -1 || echo "inactive")
    echo "UFW Status: $UFW_STATUS"
    
    if echo "$UFW_STATUS" | grep -q "Status: active"; then
        echo ""
        echo "🔓 Configuring UFW rules..."
        
        # Allow port 8080 (Frontend/HTTP)
        if ! ufw status | grep -q "8080.*ALLOW"; then
            echo "  Adding rule: allow 8080/tcp"
            ufw allow 8080/tcp 2>&1 | head -5 || echo "  ⚠️  Failed to add rule (may need root)"
        else
            echo "  ✅ Port 8080 already allowed"
        fi
        
        # Allow port 5001 (Backend API)
        if ! ufw status | grep -q "5001.*ALLOW"; then
            echo "  Adding rule: allow 5001/tcp"
            ufw allow 5001/tcp 2>&1 | head -5 || echo "  ⚠️  Failed to add rule (may need root)"
        else
            echo "  ✅ Port 5001 already allowed"
        fi
        
        # Allow SSH (just to be safe)
        if ! ufw status | grep -q "22.*ALLOW\|OpenSSH.*ALLOW"; then
            echo "  Adding rule: allow OpenSSH (safety measure)"
            ufw allow OpenSSH 2>&1 | head -5 || echo "  ⚠️  Failed to add SSH rule"
        else
            echo "  ✅ SSH already allowed"
        fi
        
        echo ""
        echo "📊 Current UFW Status:"
        ufw status verbose 2>/dev/null | head -20
    else
        echo "⚠️  UFW is installed but inactive"
        echo "   You may want to activate it with: ufw --force enable"
    fi
else
    echo "⚠️  UFW not installed on this system"
fi

echo ""
echo "🔍 Checking nginx binding configuration..."

# Check nginx configuration for proper binding
NGINX_CONFIG="/etc/nginx/sites-enabled/landscape-architecture-tool-dev"
if [ ! -f "$NGINX_CONFIG" ]; then
    NGINX_CONFIG="/etc/nginx/sites-enabled/landscape-architecture-tool"
fi

if [ -f "$NGINX_CONFIG" ]; then
    echo "Found nginx config: $NGINX_CONFIG"
    
    # Check if nginx is listening on 0.0.0.0 or specific IP
    if grep -q "listen.*8080" "$NGINX_CONFIG"; then
        LISTEN_LINE=$(grep "listen.*8080" "$NGINX_CONFIG" | head -1)
        echo "  Current listen directive: $LISTEN_LINE"
        
        # Ensure it's listening on all interfaces (0.0.0.0 or no IP specified)
        if echo "$LISTEN_LINE" | grep -q "127.0.0.1"; then
            echo "  ⚠️  WARNING: Nginx is binding to localhost only (127.0.0.1)"
            echo "  This prevents external access. Needs configuration change."
            echo ""
            echo "  Suggested fix in nginx config:"
            echo "    Change: listen 127.0.0.1:8080;"
            echo "    To:     listen 8080;"
        else
            echo "  ✅ Nginx appears to be listening on all interfaces"
        fi
    else
        echo "  ⚠️  Port 8080 not found in nginx configuration"
    fi
else
    echo "  ⚠️  Nginx configuration not found"
fi

echo ""
echo "🔍 Checking backend binding..."

# Check if gunicorn/backend is binding properly
BACKEND_PROCS=$(ps aux | grep gunicorn | grep -v grep || echo "")
if [ -n "$BACKEND_PROCS" ]; then
    echo "Backend processes found:"
    echo "$BACKEND_PROCS" | head -3 | sed 's/^/  /'
    
    # Check what the backend is listening on
    BACKEND_BIND=$(ss -tlnp 2>/dev/null | grep :5001 || netstat -tlnp 2>/dev/null | grep :5001 || echo "")
    if [ -n "$BACKEND_BIND" ]; then
        echo ""
        echo "Backend binding:"
        echo "$BACKEND_BIND" | sed 's/^/  /'
        
        if echo "$BACKEND_BIND" | grep -q "127.0.0.1:5001"; then
            echo "  ⚠️  Backend is binding to localhost only (127.0.0.1)"
            echo "  This prevents external access. Needs configuration change."
        else
            echo "  ✅ Backend appears to be binding properly"
        fi
    else
        echo "  ⚠️  Backend not listening on port 5001"
    fi
else
    echo "  ⚠️  No backend processes found"
fi

echo ""
echo "🌐 Testing local connectivity..."

# Test localhost connectivity
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null | grep -q "200"; then
    echo "✅ Frontend accessible on localhost"
else
    echo "❌ Frontend NOT accessible on localhost"
fi

if curl -s http://localhost:5001/health 2>/dev/null | grep -q "healthy"; then
    echo "✅ Backend accessible on localhost"
else
    echo "❌ Backend NOT accessible on localhost"
fi

echo ""
echo "=========================================="
echo "📊 Summary & Recommendations"
echo "=========================================="
echo ""
echo "If services work on localhost but not externally, check:"
echo "  1. UFW firewall rules (ports 5001, 8080 must be allowed)"
echo "  2. Cloud provider firewall/security groups"
echo "  3. Nginx binding (should listen on 0.0.0.0:8080 or just 8080)"
echo "  4. Backend binding (should bind to 0.0.0.0:5001, not 127.0.0.1:5001)"
echo ""
echo "Current status:"
ps aux | grep -E "(nginx|gunicorn)" | grep -v grep | wc -l | xargs -I {} echo "  {} service processes running"
ss -tlnp 2>/dev/null | grep -E ":(5001|8080)" | wc -l | xargs -I {} echo "  {} ports listening"
echo ""
echo "=========================================="
