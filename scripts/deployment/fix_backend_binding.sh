#!/bin/bash
# Fix Backend Binding Configuration
# This script ensures the backend binds to 0.0.0.0 instead of 127.0.0.1

set -e

echo "=========================================="
echo "🔧 Fixing Backend Binding Configuration"
echo "=========================================="
echo ""

# Find the systemd service file
SERVICE_FILE=""
for service in "landscape-backend-dev" "landscape-backend"; do
    if [ -f "/etc/systemd/system/$service.service" ]; then
        SERVICE_FILE="/etc/systemd/system/$service.service"
        SERVICE_NAME="$service"
        break
    fi
done

if [ -z "$SERVICE_FILE" ]; then
    echo "❌ No landscape backend service file found in /etc/systemd/system/"
    echo "   Searching in /lib/systemd/system/..."
    for service in "landscape-backend-dev" "landscape-backend"; do
        if [ -f "/lib/systemd/system/$service.service" ]; then
            SERVICE_FILE="/lib/systemd/system/$service.service"
            SERVICE_NAME="$service"
            break
        fi
    done
fi

if [ -z "$SERVICE_FILE" ]; then
    echo "❌ Could not find systemd service file"
    echo "   Available service files:"
    ls -la /etc/systemd/system/landscape* 2>/dev/null || echo "   (none found)"
    exit 1
fi

echo "✅ Found service file: $SERVICE_FILE"
echo "   Service name: $SERVICE_NAME"
echo ""

# Show current configuration
echo "📋 Current service configuration:"
grep -E "(ExecStart|WorkingDirectory)" "$SERVICE_FILE" | sed 's/^/   /'
echo ""

# Check if it's binding to localhost
if grep -q "127.0.0.1" "$SERVICE_FILE"; then
    echo "⚠️  Service is configured to bind to 127.0.0.1 (localhost only)"
    echo "   Fixing binding to 0.0.0.0 (all interfaces)..."
    echo ""
    
    # Create backup
    cp "$SERVICE_FILE" "${SERVICE_FILE}.backup"
    echo "✅ Backup created: ${SERVICE_FILE}.backup"
    
    # Fix the binding (replace 127.0.0.1 with 0.0.0.0)
    sed -i 's/--bind 127\.0\.0\.1:/--bind 0.0.0.0:/g' "$SERVICE_FILE"
    sed -i 's/bind=127\.0\.0\.1:/bind=0.0.0.0:/g' "$SERVICE_FILE"
    sed -i 's/:127\.0\.0\.1:/:0.0.0.0:/g' "$SERVICE_FILE"
    
    echo "✅ Updated binding configuration"
    echo ""
    
    echo "📋 New service configuration:"
    grep -E "(ExecStart|WorkingDirectory)" "$SERVICE_FILE" | sed 's/^/   /'
    echo ""
    
    # Reload systemd daemon
    echo "🔄 Reloading systemd daemon..."
    systemctl daemon-reload
    echo "✅ Systemd daemon reloaded"
    echo ""
    
    # Restart the service
    echo "🔄 Restarting $SERVICE_NAME service..."
    systemctl restart "$SERVICE_NAME"
    sleep 3
    
    # Check service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✅ Service $SERVICE_NAME is running"
        systemctl status "$SERVICE_NAME" --no-pager | head -10 | sed 's/^/   /'
    else
        echo "❌ Service $SERVICE_NAME failed to start"
        echo "   Last 10 log lines:"
        journalctl -u "$SERVICE_NAME" -n 10 --no-pager | sed 's/^/   /'
        exit 1
    fi
    
    echo ""
    
    # Verify new binding
    echo "🔍 Verifying new binding..."
    sleep 2
    NEW_BINDING=$(ss -tlnp 2>/dev/null | grep :5001 || echo "")
    if [ -n "$NEW_BINDING" ]; then
        echo "✅ Backend is now listening:"
        echo "$NEW_BINDING" | sed 's/^/   /'
        
        if echo "$NEW_BINDING" | grep -q "0.0.0.0:5001"; then
            echo ""
            echo "🎉 SUCCESS! Backend is now bound to 0.0.0.0:5001"
            echo "   This allows external access to the backend."
        elif echo "$NEW_BINDING" | grep -q "127.0.0.1:5001"; then
            echo ""
            echo "⚠️  Backend is still bound to 127.0.0.1:5001"
            echo "   The configuration change may not have taken effect."
        fi
    else
        echo "❌ Backend is not listening on port 5001"
    fi
    
else
    echo "✅ Service is already configured to bind to 0.0.0.0 or external interface"
    echo "   No changes needed."
fi

echo ""
echo "=========================================="
echo "🏁 Backend Binding Fix Complete"
echo "=========================================="
