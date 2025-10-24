#!/bin/bash
# Firewall and Network Diagnostic Script for VPS
# This script checks firewall rules and network configuration

echo "=========================================="
echo "🔥 Firewall & Network Diagnostics"
echo "=========================================="
echo ""

echo "1️⃣ Firewall Status (UFW):"
echo "----------------------------"
if command -v ufw &> /dev/null; then
    echo "UFW Status:"
    ufw status verbose 2>/dev/null || echo "  ⚠️  Unable to check UFW status (may need root)"
    echo ""
    echo "UFW Rules:"
    ufw status numbered 2>/dev/null || echo "  ⚠️  Unable to list UFW rules"
else
    echo "⚠️  UFW not installed"
fi

echo ""
echo "2️⃣ Firewall Status (iptables):"
echo "----------------------------"
if command -v iptables &> /dev/null; then
    echo "iptables INPUT rules:"
    iptables -L INPUT -n -v 2>/dev/null | head -20 || echo "  ⚠️  Unable to check iptables (may need root)"
    echo ""
    echo "iptables OUTPUT rules:"
    iptables -L OUTPUT -n -v 2>/dev/null | head -10 || echo "  ⚠️  Unable to check iptables"
else
    echo "⚠️  iptables not available"
fi

echo ""
echo "3️⃣ Network Interfaces:"
echo "----------------------------"
if command -v ip &> /dev/null; then
    ip addr show | grep -E "(inet |UP|DOWN)" || echo "  ⚠️  Unable to list interfaces"
else
    ifconfig 2>/dev/null | grep -E "(inet |UP|DOWN)" || echo "  ⚠️  Unable to list interfaces"
fi

echo ""
echo "4️⃣ Listening Ports:"
echo "----------------------------"
echo "All listening TCP ports:"
ss -tlnp 2>/dev/null | grep LISTEN || netstat -tlnp 2>/dev/null | grep LISTEN || echo "  ⚠️  Unable to list ports"

echo ""
echo "Target ports (5001, 8080):"
ss -tlnp 2>/dev/null | grep -E ":(5001|8080)" || netstat -tlnp 2>/dev/null | grep -E ":(5001|8080)" || echo "  ⚠️  Ports 5001 and 8080 not listening"

echo ""
echo "5️⃣ Nginx Configuration:"
echo "----------------------------"
if [ -f /etc/nginx/sites-enabled/landscape-architecture-tool-dev ]; then
    echo "Dev site configuration:"
    grep -E "(listen|server_name|location|proxy_pass)" /etc/nginx/sites-enabled/landscape-architecture-tool-dev | head -30
elif [ -f /etc/nginx/sites-enabled/landscape-architecture-tool ]; then
    echo "Main site configuration:"
    grep -E "(listen|server_name|location|proxy_pass)" /etc/nginx/sites-enabled/landscape-architecture-tool | head -30
else
    echo "⚠️  No landscape site configuration found in /etc/nginx/sites-enabled/"
    echo "Available configurations:"
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null | head -10 || echo "  Unable to list"
fi

echo ""
echo "6️⃣ SELinux Status:"
echo "----------------------------"
if command -v getenforce &> /dev/null; then
    getenforce 2>/dev/null || echo "  ⚠️  Unable to check SELinux"
else
    echo "  SELinux not installed (likely not a RHEL/CentOS system)"
fi

echo ""
echo "7️⃣ Cloud Provider Firewall Info:"
echo "----------------------------"
echo "Note: Cloud provider firewalls (AWS Security Groups, Azure NSG, etc.)"
echo "      must be configured separately through the cloud console."
echo "      Required open ports: 8080 (HTTP), 5001 (Backend API)"

echo ""
echo "8️⃣ Localhost Connectivity Test:"
echo "----------------------------"
echo "Testing localhost:8080..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null || echo "failed")
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "  ✅ Frontend accessible on localhost ($FRONTEND_RESPONSE)"
else
    echo "  ❌ Frontend NOT accessible on localhost ($FRONTEND_RESPONSE)"
fi

echo ""
echo "Testing localhost:5001/health..."
BACKEND_RESPONSE=$(curl -s http://localhost:5001/health 2>/dev/null || echo "failed")
if echo "$BACKEND_RESPONSE" | grep -q "healthy"; then
    echo "  ✅ Backend health OK on localhost"
else
    echo "  ❌ Backend NOT accessible on localhost"
    echo "  Response: $BACKEND_RESPONSE"
fi

echo ""
echo "9️⃣ External IP Binding Check:"
echo "----------------------------"
echo "Checking if services bind to 0.0.0.0 (all interfaces) or 127.0.0.1 (localhost only):"
ss -tlnp 2>/dev/null | grep -E ":(5001|8080)" | awk '{print $4}' || netstat -tlnp 2>/dev/null | grep -E ":(5001|8080)" | awk '{print $4}'

echo ""
echo "🔍 Key Findings:"
echo "----------------------------"
echo "If ports show 127.0.0.1:8080 instead of 0.0.0.0:8080 or *:8080,"
echo "the services are only accessible locally and need configuration changes."
echo ""
echo "If UFW is active but ports 5001/8080 are not allowed,"
echo "firewall rules need to be added."
echo ""
echo "=========================================="
echo "🏁 Firewall Diagnostic Complete"
echo "=========================================="
