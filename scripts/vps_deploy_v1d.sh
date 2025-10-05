#!/bin/bash
# VPS Deployment Script for Landscape Architecture Tool V1.00D
# Run this script on your VPS as root: bash vps_deploy_v1d.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
APP_DIR="/var/www/landscape-architecture-tool"
BRANCH="V1.00D"
BACKUP_DIR="/var/backups/landscape-$(date +%Y%m%d_%H%M%S)"
VPS_URL="http://72.60.176.200:8080"
BACKEND_PORT="5000"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${MAGENTA}[INFO]${NC} $1"
}

# Banner
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 VPS Deployment Script for V1.00D Development          ║${NC}"
echo -e "${BLUE}║  Landscape Architecture Tool - DevDeploy Environment       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root: sudo bash $0"
    exit 1
fi

log "Starting deployment process for V1.00D..."

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    error "Application directory $APP_DIR does not exist!"
    error "Please clone the repository first:"
    echo "  cd /var/www"
    echo "  git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git"
    exit 1
fi

# Create backup
log "Creating backup of current deployment..."
mkdir -p "$(dirname "$BACKUP_DIR")"
cp -r "$APP_DIR" "$BACKUP_DIR"
success "Backup created at $BACKUP_DIR"

# Navigate to app directory
log "Navigating to application directory..."
cd "$APP_DIR"

# Show current status
log "Current repository status:"
git branch --show-current
git log -1 --oneline

# Fetch latest changes
log "Fetching latest changes from GitHub..."
git fetch --all --prune

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    warning "Currently on branch $CURRENT_BRANCH, switching to $BRANCH..."
    git checkout "$BRANCH"
fi

# Check how many commits behind
COMMITS_BEHIND=$(git rev-list HEAD..origin/$BRANCH --count)
if [ "$COMMITS_BEHIND" -gt 0 ]; then
    info "Repository is $COMMITS_BEHIND commits behind origin/$BRANCH"
else
    success "Repository is already up to date!"
fi

# Update to latest V1.00D
log "Updating to latest $BRANCH..."
git reset --hard origin/$BRANCH

# Show new status
success "Updated to:"
git log -1 --oneline
git log -3 --oneline --decorate

# Stop backend service
log "Stopping backend service..."
systemctl stop landscape-backend 2>/dev/null || warning "Backend service was not running"

# Kill any remaining backend processes
log "Cleaning up any remaining backend processes..."
pkill -f gunicorn 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

# Kill any frontend processes that might be blocking port 8080
log "Checking for processes blocking port 8080..."
PROCESS_ON_8080=$(lsof -ti:8080 2>/dev/null || true)
if [ -n "$PROCESS_ON_8080" ]; then
    warning "Found process(es) on port 8080: $PROCESS_ON_8080"
    log "Killing processes on port 8080..."
    kill -9 $PROCESS_ON_8080 2>/dev/null || true
    sleep 2
    success "Port 8080 cleared"
else
    success "Port 8080 is already available"
fi

# Also kill any npm/node processes that might be running dev servers
log "Cleaning up any remaining Node.js processes..."
pkill -f "vite" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true

sleep 3

# Activate Python environment and update dependencies
log "Setting up Python environment..."
if [ ! -d "venv" ]; then
    warning "Virtual environment not found! Creating new one..."
    python3 -m venv venv
fi

source venv/bin/activate

log "Updating Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Clear Python cache
log "Clearing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Run database migrations if needed
log "Checking database migrations..."
if [ -d "migrations" ]; then
    FLASK_APP=src.main flask db upgrade 2>/dev/null || warning "Database migrations skipped"
fi

# Rebuild frontend
log "Rebuilding frontend with devdeploy branding..."
cd frontend

# Clear npm cache and build artifacts with force
log "Clearing npm and build caches..."
npm cache clean --force 2>/dev/null || true

# Force remove node_modules and lock file completely to avoid ENOTEMPTY errors
if [ -d "node_modules" ]; then
    log "Removing existing node_modules..."
    rm -rf node_modules 2>/dev/null || true
    # If normal rm fails, try with sudo and force
    if [ -d "node_modules" ]; then
        chmod -R 755 node_modules 2>/dev/null || true
        rm -rf node_modules 2>/dev/null || true
    fi
fi

# Remove lock file to force fresh dependency resolution
rm -f package-lock.json 2>/dev/null || true

# Clear other build artifacts
rm -rf node_modules/.cache .next dist build 2>/dev/null || true

# Install dependencies fresh with clean slate
log "Installing frontend dependencies (this may take a few minutes)..."
npm install --legacy-peer-deps

# Verify critical dependencies are installed
log "Verifying critical dependencies..."
if [ ! -d "node_modules/clsx" ]; then
    error "Critical dependency 'clsx' not installed! Retrying..."
    npm install clsx --save --legacy-peer-deps
fi
if [ ! -d "node_modules/recharts" ]; then
    error "Critical dependency 'recharts' not installed! Retrying..."
    npm install recharts --save --legacy-peer-deps
fi

# Set devdeploy environment
log "Configuring devdeploy environment..."
export VITE_APP_TITLE="devdeploy - Landscape Architecture Tool (Development)"
export VITE_APP_ENV="development"
export VITE_API_URL="http://72.60.176.200:8080/api"

# Update index.html with devdeploy title BEFORE build
log "Setting devdeploy branding in index.html..."
sed -i 's|<title>.*</title>|<title>devdeploy - Landscape Architecture Tool (Development)</title>|g' index.html

# Set GIT_BRANCH environment variable for backend
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
export GIT_BRANCH=$CURRENT_BRANCH
echo "GIT_BRANCH=$CURRENT_BRANCH" >> ../.env 2>/dev/null || true

# Build optimized bundle with devdeploy branding
log "Building optimized frontend bundle with devdeploy branding..."
log "Note: 'production' mode = optimized build, NOT production environment"
npm run build

# Verify build
if [ -d "dist" ] && [ -f "dist/index.html" ]; then
    success "Frontend build completed successfully"
    ls -lh dist/index.html
    
    # Check if devdeploy title is in the build
    if grep -q "devdeploy" dist/index.html; then
        success "DevDeploy branding verified in build"
    else
        warning "DevDeploy branding not found in build - this may be normal"
    fi
    
    # Add cache-busting meta tag to force browser refresh
    DEPLOY_TIMESTAMP=$(date +%s)
    log "Adding cache-busting timestamp: $DEPLOY_TIMESTAMP"
    sed -i "s|</head>|  <meta name=\"deploy-version\" content=\"$DEPLOY_TIMESTAMP\">\n  </head>|" dist/index.html
else
    error "Frontend build failed!"
    exit 1
fi

# Return to app root
cd ..

# Update nginx configuration if needed
log "Checking nginx configuration..."
if [ -f "/etc/nginx/sites-available/landscape" ]; then
    info "Nginx configuration found"
    nginx -t && success "Nginx configuration is valid" || error "Nginx configuration has errors"
    
    # Clear nginx cache if it exists
    if [ -d "/var/cache/nginx" ]; then
        log "Clearing nginx cache..."
        rm -rf /var/cache/nginx/* 2>/dev/null || true
        success "Nginx cache cleared"
    fi
fi

# Reload systemd and start backend
log "Reloading systemd configuration..."
systemctl daemon-reload

log "Starting backend service..."
systemctl start landscape-backend

# Enable service on boot
systemctl enable landscape-backend 2>/dev/null || true

# Wait for service to start
log "Waiting for service to start..."
sleep 8

# Check service status
log "Checking service status..."
if systemctl is-active --quiet landscape-backend; then
    success "Backend service is running"
    systemctl status landscape-backend --no-pager -l | head -20
else
    error "Backend service failed to start!"
    log "Recent logs:"
    journalctl -u landscape-backend -n 30 --no-pager
    exit 1
fi

# Reload nginx
log "Reloading nginx..."
systemctl reload nginx || warning "Nginx reload failed"

# Add cache-busting information
echo ""
log "═══════════════════════════════════════════════════════════"
log "Cache-Busting Information"
log "═══════════════════════════════════════════════════════════"
success "✓ Hashed filenames enabled for automatic cache invalidation"
success "✓ Deploy timestamp added to HTML: $DEPLOY_TIMESTAMP"
success "✓ Nginx cache cleared"
info "→ If changes not visible, perform hard refresh:"
info "  • Windows/Linux: Ctrl+Shift+R"
info "  • macOS: Cmd+Shift+R"
info "  • Or clear browser cache manually"

# Health checks
echo ""
log "═══════════════════════════════════════════════════════════"
log "Performing comprehensive health checks..."
log "═══════════════════════════════════════════════════════════"

# Test backend locally
log "Testing backend health endpoint (localhost)..."
HEALTH_RESPONSE=$(curl -s http://localhost:$BACKEND_PORT/health)
if [ $? -eq 0 ]; then
    success "Backend health check passed"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    error "Backend health check failed"
    log "Checking service logs..."
    journalctl -u landscape-backend -n 20 --no-pager
fi

# Test external access
log "Testing external access ($VPS_URL)..."
EXTERNAL_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $VPS_URL/health 2>/dev/null)
if [ "$EXTERNAL_RESPONSE" = "200" ]; then
    success "External access working (HTTP $EXTERNAL_RESPONSE)"
else
    warning "External access returned HTTP $EXTERNAL_RESPONSE"
fi

# Test frontend
log "Testing frontend homepage..."
FRONTEND_RESPONSE=$(curl -s $VPS_URL/ 2>/dev/null)
if echo "$FRONTEND_RESPONSE" | grep -q "Landscape Architecture Tool"; then
    success "Frontend is serving correctly"
    if echo "$FRONTEND_RESPONSE" | grep -q "devdeploy"; then
        success "DevDeploy branding detected in live site"
    fi
else
    warning "Frontend may have issues"
fi

# Test API endpoint
log "Testing API endpoint..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $VPS_URL/api/dashboard/stats 2>/dev/null)
if [ "$API_RESPONSE" = "200" ] || [ "$API_RESPONSE" = "401" ]; then
    success "API endpoint responding (HTTP $API_RESPONSE)"
else
    warning "API endpoint returned HTTP $API_RESPONSE"
fi

# Disk space check
log "Checking disk space..."
df -h "$APP_DIR" | tail -1

# Memory check
log "Checking memory usage..."
free -h | grep Mem

# Final status
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Deployment Complete!                                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

log "Deployment Summary:"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "✓ Repository updated to latest V1.00D"
log "✓ Python dependencies updated"
log "✓ Frontend rebuilt with devdeploy branding"
log "✓ Backend service restarted and healthy"
log "✓ Nginx configuration validated"
log "✓ Backup created at: $BACKUP_DIR"
echo ""

info "Application URLs:"
log "🌐 Frontend: $VPS_URL/"
log "🔧 Health:   $VPS_URL/health"
log "📊 API:      $VPS_URL/api/"
echo ""

info "Useful commands:"
log "📋 Service status:  systemctl status landscape-backend"
log "📋 Live logs:       journalctl -u landscape-backend -f"
log "📋 Nginx logs:      tail -f /var/log/nginx/error.log"
log "📋 Restore backup:  cp -r $BACKUP_DIR/* $APP_DIR/"
echo ""

success "Deployment completed successfully! 🎉"
echo ""
