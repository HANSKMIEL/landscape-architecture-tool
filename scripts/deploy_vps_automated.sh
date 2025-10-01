#!/bin/bash
# Enhanced VPS Deployment Script for Landscape Architecture Tool
# This script provides automated deployment with rollback capability
# Run on VPS: bash deploy_vps_automated.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_DIR="/var/www/landscape-architecture-tool"
BACKUP_DIR="/var/backups/landscape-architecture-tool"
LOG_FILE="/var/log/landscape-deploy.log"
BRANCH="V1.00D"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Banner
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🚀 VPS Deployment Script${NC}"
echo -e "${BLUE}================================================${NC}"
log "Starting deployment process..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root (sudo bash $0)"
    exit 1
fi

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    error "Application directory not found: $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Step 1: Create backup
log "Creating backup..."
BACKUP_TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
BACKUP_PATH="${BACKUP_DIR}/backup_${BACKUP_TIMESTAMP}"

# Backup current git state
CURRENT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
echo "$CURRENT_COMMIT" > "${BACKUP_PATH}_commit.txt"

# Backup frontend dist if exists
if [ -d "frontend/dist" ]; then
    tar -czf "${BACKUP_PATH}_frontend.tar.gz" frontend/dist
    success "Frontend backup created: ${BACKUP_PATH}_frontend.tar.gz"
fi

# Keep only last 5 backups
ls -t ${BACKUP_DIR}/backup_* 2>/dev/null | tail -n +11 | xargs -r rm -f
log "Old backups cleaned up (keeping last 5)"

# Step 2: Check repository status
log "Checking repository status..."

# Fetch latest changes
log "Fetching latest changes from remote..."
if git fetch --all; then
    success "Successfully fetched latest changes"
else
    error "Failed to fetch latest changes"
    exit 1
fi

# Check how many commits behind
COMMITS_BEHIND=$(git rev-list HEAD..origin/${BRANCH} --count 2>/dev/null || echo "0")
log "Repository is $COMMITS_BEHIND commits behind origin/${BRANCH}"

if [ "$COMMITS_BEHIND" = "0" ]; then
    warning "Repository is already up to date. Continuing with rebuild anyway..."
fi

# Step 3: Stop services
log "Stopping backend service..."

if systemctl is-active --quiet landscape-backend; then
    systemctl stop landscape-backend
    success "Backend service stopped"
else
    warning "Backend service was not running"
fi

# Kill any remaining gunicorn processes
if pgrep -f gunicorn > /dev/null; then
    log "Killing remaining gunicorn processes..."
    pkill -f gunicorn
    sleep 2
    success "Gunicorn processes terminated"
fi

# Step 4: Update repository
log "Updating repository to latest ${BRANCH}..."

# Save any local changes (should not be any in production)
if ! git diff-index --quiet HEAD --; then
    warning "Local changes detected, stashing them..."
    git stash
fi

# Reset to latest origin
if git reset --hard origin/${BRANCH}; then
    NEW_COMMIT=$(git rev-parse HEAD)
    success "Repository updated to commit: ${NEW_COMMIT}"
    log "Changes: $(git log --oneline ${CURRENT_COMMIT}..${NEW_COMMIT} 2>/dev/null | wc -l) commits"
else
    error "Failed to update repository"
    # Attempt rollback
    log "Attempting rollback to previous commit..."
    git reset --hard "$CURRENT_COMMIT"
    systemctl start landscape-backend
    exit 1
fi

# Step 5: Update Python dependencies
log "Updating Python dependencies..."

if [ ! -d "venv" ]; then
    warning "Virtual environment not found, creating one..."
    python3 -m venv venv
fi

source venv/bin/activate

if pip install --upgrade pip && pip install -r requirements.txt; then
    success "Python dependencies updated"
else
    error "Failed to update Python dependencies"
    exit 1
fi

# Step 6: Build frontend
log "Building frontend..."

if [ ! -d "frontend" ]; then
    error "Frontend directory not found"
    exit 1
fi

cd frontend

# Check if npm is available
if ! command -v npm &> /dev/null; then
    error "npm is not installed"
    exit 1
fi

# Clean and install dependencies
log "Installing frontend dependencies..."
if npm ci --legacy-peer-deps; then
    success "Frontend dependencies installed"
else
    error "Failed to install frontend dependencies"
    exit 1
fi

# Build frontend
log "Building frontend assets..."
if npm run build; then
    success "Frontend built successfully"
else
    error "Frontend build failed"
    exit 1
fi

cd ..

# Step 7: Verify build
log "Verifying build..."

if [ ! -f "frontend/dist/index.html" ]; then
    error "Frontend build verification failed: index.html not found"
    exit 1
fi

success "Build verification passed"

# Step 8: Start services
log "Starting backend service..."

systemctl daemon-reload

if systemctl start landscape-backend; then
    success "Backend service started"
else
    error "Failed to start backend service"
    exit 1
fi

systemctl enable landscape-backend 2>/dev/null

# Wait for service to be fully ready
log "Waiting for service to be ready..."
sleep 5

# Step 9: Verify deployment
log "Verifying deployment..."

# Check if service is running
if systemctl is-active --quiet landscape-backend; then
    success "Backend service is running"
else
    error "Backend service failed to start"
    journalctl -u landscape-backend -n 50 --no-pager
    exit 1
fi

# Check if backend responds
RETRY_COUNT=0
MAX_RETRIES=10
BACKEND_READY=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
        BACKEND_READY=1
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    log "Waiting for backend to respond... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $BACKEND_READY -eq 1 ]; then
    success "Backend health endpoint responding"
    
    # Get version info
    VERSION=$(curl -s http://localhost:5000/health 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    log "Deployed version: ${VERSION:-Unknown}"
else
    error "Backend health endpoint not responding after $MAX_RETRIES attempts"
    journalctl -u landscape-backend -n 50 --no-pager
    exit 1
fi

# Check external access
if curl -f -s http://72.60.176.200:8080/health > /dev/null 2>&1; then
    success "External access verified (http://72.60.176.200:8080)"
else
    warning "External access check failed - nginx might need restart"
    log "Attempting nginx restart..."
    systemctl restart nginx
    sleep 2
    
    if curl -f -s http://72.60.176.200:8080/health > /dev/null 2>&1; then
        success "External access now working after nginx restart"
    else
        error "External access still failing after nginx restart"
    fi
fi

# Check frontend
if curl -f -s http://72.60.176.200:8080/ | grep -q "devdeploy"; then
    success "Frontend is accessible and showing correct content"
else
    warning "Frontend verification inconclusive"
fi

# Step 10: Summary
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}📊 Deployment Summary${NC}"
echo -e "${BLUE}================================================${NC}"
success "Deployment completed successfully!"
log "Previous commit: ${CURRENT_COMMIT}"
log "New commit: ${NEW_COMMIT}"
log "Commits deployed: ${COMMITS_BEHIND}"
log "Backup location: ${BACKUP_PATH}_*"
echo ""
echo -e "${GREEN}✅ Application is now running the latest code from ${BRANCH}${NC}"
echo -e "${GREEN}🌐 Access: http://72.60.176.200:8080/${NC}"
echo -e "${GREEN}🏥 Health: http://72.60.176.200:8080/health${NC}"
echo ""

# Display service status
echo -e "${BLUE}Service Status:${NC}"
systemctl status landscape-backend --no-pager -l | head -15
echo ""

echo -e "${BLUE}================================================${NC}"
log "Deployment completed successfully at $(date)"

# Exit
exit 0
