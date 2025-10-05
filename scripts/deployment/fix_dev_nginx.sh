#!/bin/bash
# Fix nginx configuration for V1.00D development environment

set -e

echo "🔧 Fixing nginx configuration for V1.00D backend API access..."
echo "================================================================"

VPS_HOST="${VPS_HOST:-72.60.176.200}"
VPS_USER="${VPS_USER:-root}"

ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'

echo "1️⃣ Checking current nginx configuration..."
if [ -f "/etc/nginx/sites-available/landscape-dev" ]; then
    echo "📄 Found existing landscape-dev configuration"
    echo ""
    echo "Current API proxy configuration:"
    grep -A 10 "location /api" /etc/nginx/sites-available/landscape-dev || echo "No /api location block found!"
    echo ""
elif [ -f "/etc/nginx/sites-available/default" ]; then
    echo "📄 Using default nginx configuration"
    grep -A 10 "location /api" /etc/nginx/sites-available/default || echo "No /api location block found in default!"
    echo ""
fi

echo ""
echo "2️⃣ Checking what's configured for port 8080..."
grep -r "listen.*8080" /etc/nginx/sites-available/ || echo "No explicit configuration for port 8080"
grep -r "72.60.176.200:8080" /etc/nginx/sites-available/ || true
grep -r "proxy_pass.*5001" /etc/nginx/sites-available/ || echo "No proxy to port 5001 found!"

echo ""
echo "3️⃣ Creating/updating nginx configuration for development..."

cat > /etc/nginx/sites-available/landscape-dev << 'NGINX_CONFIG'
server {
    listen 8080;
    server_name 72.60.176.200;

    root /var/www/landscape-architecture-tool-dev/frontend/dist;
    index index.html;

    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    # Health endpoint
    location /health {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 10s;
        proxy_connect_timeout 10s;
    }

    # Static assets
    location /assets {
        alias /var/www/landscape-architecture-tool-dev/frontend/dist/assets;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Favicon
    location /favicon.ico {
        alias /var/www/landscape-architecture-tool-dev/frontend/dist/favicon.ico;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/landscape-dev-access.log;
    error_log /var/log/nginx/landscape-dev-error.log;
}
NGINX_CONFIG

echo "✅ Nginx configuration created"

echo ""
echo "4️⃣ Enabling site and testing configuration..."
ln -sf /etc/nginx/sites-available/landscape-dev /etc/nginx/sites-enabled/landscape-dev

echo ""
echo "Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors!"
    exit 1
fi

echo ""
echo "5️⃣ Reloading nginx..."
systemctl reload nginx
echo "✅ Nginx reloaded"

echo ""
echo "6️⃣ Verifying backend service is running..."
systemctl status landscape-backend-dev --no-pager -l | grep -E "(Active|Main PID|Listening)"

echo ""
echo "7️⃣ Testing API endpoint..."
sleep 2
if curl -s http://localhost:5001/health | head -5; then
    echo "✅ Backend responds on localhost:5001"
else
    echo "⚠️ Backend does not respond directly"
fi

echo ""
echo "8️⃣ Testing through nginx proxy..."
if curl -s http://72.60.176.200:8080/health | head -5; then
    echo "✅ Backend accessible through nginx on port 8080!"
else
    echo "❌ Backend not accessible through nginx"
fi

ENDSSH

echo ""
echo "✅ Development nginx configuration complete!"
echo ""
echo "🔍 Testing from outside..."
sleep 2
curl -s http://72.60.176.200:8080/health | head -10 || echo "Still testing..."

echo ""
echo "📊 Try accessing:"
echo "  Frontend: http://72.60.176.200:8080/"
echo "  API Health: http://72.60.176.200:8080/health"
echo "  API Example: http://72.60.176.200:8080/api/suppliers"
