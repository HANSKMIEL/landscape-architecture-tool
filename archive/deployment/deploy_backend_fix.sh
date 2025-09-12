#!/bin/bash
set -e

echo "=== Landscape Architecture Tool Backend Deployment Fix ==="

# Stop any existing backend processes
echo "Stopping existing backend processes..."
sudo systemctl stop landscape-backend || true

# Navigate to application directory
cd /var/www/landscape-architecture-tool || cd /root/landscape-architecture-tool || cd /home/landscape-architecture-tool

echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Activate virtual environment or create it
if [ -d "venv" ]; then
    echo "Activating existing virtual environment..."
    source venv/bin/activate
else
    echo "Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/update requirements
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Set proper permissions
echo "Setting permissions..."
sudo chown -R root:root .
sudo chmod +x wsgi.py

# Install systemd service
echo "Installing systemd service..."
sudo cp landscape-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable landscape-backend
sudo systemctl start landscape-backend

# Check service status
echo "Checking service status..."
sudo systemctl status landscape-backend --no-pager

# Test API endpoints
echo "Testing API endpoints..."
sleep 3
curl -X GET http://127.0.0.1:5000/api/health || echo "Health check failed"

# Restart nginx
echo "Restarting nginx..."
sudo systemctl restart nginx

echo "=== Backend deployment completed ==="
echo "Service status:"
sudo systemctl is-active landscape-backend

