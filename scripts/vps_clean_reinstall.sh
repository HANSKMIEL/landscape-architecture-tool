#!/bin/bash
# VPS Clean Reinstall Script for Landscape Architecture Tool
# This script performs a clean reinstall from V1.00D branch
# Usage: Run this script on the VPS at 72.60.176.200

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
VPS_HOST="72.60.176.200"
VPS_PORT="8080"
APP_DIR="/var/www/landscape-architecture-tool"
BACKUP_DIR="/var/backups/landscape-architecture-tool"
BRANCH="V1.00D"
LOG_FILE="/var/log/landscape-reinstall.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to log with timestamp
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to display banner
display_banner() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}🚀 VPS Clean Reinstall - Landscape Architecture Tool${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${CYAN}Branch: ${BRANCH}${NC}"
    echo -e "${CYAN}App Directory: ${APP_DIR}${NC}"
    echo -e "${CYAN}Timestamp: ${TIMESTAMP}${NC}"
    echo -e "${BLUE}================================================================${NC}"
    log "Starting VPS clean reinstall process"
}

# Function to create backup
create_backup() {
    log "📦 Step 1: Creating full backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Create backup subdirectory for this timestamp
    BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
    mkdir -p "$BACKUP_PATH"
    
    log "Creating backup at: $BACKUP_PATH"
    
    # Backup application directory if it exists
    if [ -d "$APP_DIR" ]; then
        log "Backing up application directory..."
        tar -czf "$BACKUP_PATH/app_backup.tar.gz" -C "$(dirname $APP_DIR)" "$(basename $APP_DIR)" 2>&1 | tee -a "$LOG_FILE"
        
        # Backup database if it exists
        if [ -f "$APP_DIR/landscape_architecture_prod.db" ]; then
            log "Backing up production database..."
            cp "$APP_DIR/landscape_architecture_prod.db" "$BACKUP_PATH/landscape_architecture_prod_backup.db"
        fi
        
        # Backup .env file if it exists
        if [ -f "$APP_DIR/.env" ]; then
            log "Backing up environment configuration..."
            cp "$APP_DIR/.env" "$BACKUP_PATH/.env.backup"
        fi
        
        log "✅ Backup completed successfully at $BACKUP_PATH"
    else
        log "⚠️ App directory does not exist, skipping backup"
    fi
    
    # Keep only last 5 backups
    log "Cleaning old backups (keeping last 5)..."
    cd "$BACKUP_DIR"
    ls -t | tail -n +6 | xargs -r rm -rf
    log "✅ Old backups cleaned"
}

# Function to stop services
stop_services() {
    log "🛑 Step 2: Stopping all services..."
    
    # Stop systemd service
    if systemctl is-active --quiet landscape-backend; then
        log "Stopping landscape-backend systemd service..."
        systemctl stop landscape-backend 2>&1 | tee -a "$LOG_FILE" || true
    fi
    
    # Kill any remaining gunicorn processes
    if pgrep -f gunicorn > /dev/null; then
        log "Killing remaining gunicorn processes..."
        pkill -f gunicorn 2>&1 | tee -a "$LOG_FILE" || true
        sleep 5
    fi
    
    # Kill any remaining python processes related to the app
    if pgrep -f "landscape" > /dev/null; then
        log "Killing remaining landscape processes..."
        pkill -f "landscape" 2>&1 | tee -a "$LOG_FILE" || true
        sleep 2
    fi
    
    log "✅ All services stopped"
}

# Function to delete old installation
delete_old_installation() {
    log "🗑️ Step 3: Deleting old installation..."
    
    if [ -d "$APP_DIR" ]; then
        log "Removing old application directory: $APP_DIR"
        
        # Preserve .env file if it exists
        if [ -f "$APP_DIR/.env" ]; then
            log "Preserving .env file..."
            cp "$APP_DIR/.env" "/tmp/.env.preserved"
        fi
        
        # Delete the directory
        rm -rf "$APP_DIR"
        log "✅ Old installation removed"
    else
        log "⚠️ App directory does not exist, nothing to delete"
    fi
}

# Function to clone repository
clone_repository() {
    log "📥 Step 4: Cloning fresh repository from $BRANCH branch..."
    
    # Create parent directory
    mkdir -p "$(dirname $APP_DIR)"
    cd "$(dirname $APP_DIR)"
    
    # Clone the repository
    log "Cloning from GitHub..."
    git clone --branch "$BRANCH" --single-branch https://github.com/HANSKMIEL/landscape-architecture-tool.git "$(basename $APP_DIR)" 2>&1 | tee -a "$LOG_FILE"
    
    cd "$APP_DIR"
    
    # Show current branch and commit
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    log "✅ Repository cloned successfully"
    log "Current commit: $CURRENT_COMMIT"
    log "Current branch: $(git branch --show-current)"
}

# Function to restore configuration
restore_configuration() {
    log "🔧 Step 5: Restoring configuration..."
    
    # Restore .env file if it was preserved
    if [ -f "/tmp/.env.preserved" ]; then
        log "Restoring preserved .env file..."
        cp "/tmp/.env.preserved" "$APP_DIR/.env"
        rm "/tmp/.env.preserved"
        log "✅ .env file restored"
    else
        log "⚠️ No preserved .env file found"
        
        # Create a minimal .env file if none exists
        if [ ! -f "$APP_DIR/.env" ]; then
            log "Creating minimal .env file from .env.example..."
            if [ -f "$APP_DIR/.env.example" ]; then
                cp "$APP_DIR/.env.example" "$APP_DIR/.env"
                log "✅ Created .env from example"
            fi
        fi
    fi
}

# Function to setup Python environment
setup_python_environment() {
    log "🐍 Step 6: Setting up Python environment..."
    
    cd "$APP_DIR"
    
    # Create virtual environment
    log "Creating Python virtual environment..."
    python3 -m venv venv 2>&1 | tee -a "$LOG_FILE"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"
    
    # Install Python dependencies
    log "Installing Python dependencies (this may take a few minutes)..."
    pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"
    
    log "✅ Python environment setup complete"
}

# Function to initialize database
initialize_database() {
    log "🗄️ Step 7: Initializing database..."
    
    cd "$APP_DIR"
    source venv/bin/activate
    
    # Check if we need to restore database backup
    BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
    if [ -f "$BACKUP_PATH/landscape_architecture_prod_backup.db" ]; then
        log "Restoring database from backup..."
        cp "$BACKUP_PATH/landscape_architecture_prod_backup.db" "$APP_DIR/landscape_architecture_prod.db"
        log "✅ Database restored from backup"
    else
        log "No database backup found, will initialize fresh database"
        # Database will be initialized on first run
    fi
}

# Function to setup frontend
setup_frontend() {
    log "🎨 Step 8: Setting up frontend..."
    
    cd "$APP_DIR/frontend"
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        log "❌ npm not found! Please install Node.js and npm first."
        return 1
    fi
    
    log "Installing frontend dependencies..."
    npm ci --legacy-peer-deps 2>&1 | tee -a "$LOG_FILE"
    
    log "Building frontend..."
    npm run build 2>&1 | tee -a "$LOG_FILE"
    
    cd "$APP_DIR"
    log "✅ Frontend setup complete"
}

# Function to setup systemd service
setup_systemd_service() {
    log "🔄 Step 9: Setting up systemd service..."
    
    # Create systemd service file
    cat > /etc/systemd/system/landscape-backend.service << 'EOF'
[Unit]
Description=Landscape Architecture Tool Backend API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/landscape-architecture-tool
Environment=PATH=/var/www/landscape-architecture-tool/venv/bin
Environment=FLASK_ENV=production
Environment=DATABASE_URL=sqlite:///landscape_architecture_prod.db
Environment=FLASK_APP=wsgi:application
ExecStart=/var/www/landscape-architecture-tool/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 --timeout 120 wsgi:application
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    log "✅ Systemd service file created"
}

# Function to set permissions
set_permissions() {
    log "🔐 Step 10: Setting file permissions..."
    
    cd "$APP_DIR"
    
    # Set ownership
    chown -R www-data:www-data "$APP_DIR"
    
    # Make scripts executable
    chmod +x wsgi.py 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true
    
    log "✅ Permissions set"
}

# Function to start services
start_services() {
    log "▶️ Step 11: Starting services..."
    
    # Reload systemd
    systemctl daemon-reload
    
    # Start and enable service
    log "Starting landscape-backend service..."
    systemctl start landscape-backend 2>&1 | tee -a "$LOG_FILE"
    systemctl enable landscape-backend 2>&1 | tee -a "$LOG_FILE"
    
    # Wait for service to start
    sleep 10
    
    log "✅ Services started"
}

# Function to verify installation
verify_installation() {
    log "🔍 Step 12: Verifying installation..."
    
    # Check if service is running
    if systemctl is-active --quiet landscape-backend; then
        log "✅ Backend service is running"
    else
        log "❌ Backend service is not running!"
        systemctl status landscape-backend --no-pager -l 2>&1 | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Test health endpoint
    log "Testing health endpoint..."
    sleep 5
    if curl -f -s http://localhost:5000/health > /tmp/health_check.json; then
        log "✅ Health endpoint responding"
        cat /tmp/health_check.json | tee -a "$LOG_FILE"
    else
        log "⚠️ Health endpoint not responding yet"
    fi
    
    # Test external access
    log "Testing external access on port $VPS_PORT..."
    if curl -f -s "http://$VPS_HOST:$VPS_PORT/health" > /tmp/external_health_check.json 2>&1; then
        log "✅ External access working"
        cat /tmp/external_health_check.json | tee -a "$LOG_FILE"
    else
        log "⚠️ External access may require firewall/nginx configuration"
    fi
    
    # Check frontend files
    if [ -d "$APP_DIR/frontend/dist" ] || [ -d "$APP_DIR/frontend/build" ]; then
        log "✅ Frontend build files exist"
    else
        log "⚠️ Frontend build files not found"
    fi
    
    # Display service status
    log "Service status:"
    systemctl status landscape-backend --no-pager -l 2>&1 | tee -a "$LOG_FILE"
}

# Function to display final summary
display_summary() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${GREEN}🎉 VPS Clean Reinstall Completed!${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${CYAN}Application Directory: ${APP_DIR}${NC}"
    echo -e "${CYAN}Backup Location: ${BACKUP_DIR}/backup_${TIMESTAMP}${NC}"
    echo -e "${CYAN}Branch: ${BRANCH}${NC}"
    echo -e "${CYAN}Log File: ${LOG_FILE}${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "1. Verify application at: ${GREEN}http://${VPS_HOST}:${VPS_PORT}/${NC}"
    echo -e "2. Check health endpoint: ${GREEN}http://${VPS_HOST}:${VPS_PORT}/health${NC}"
    echo -e "3. Monitor logs: ${GREEN}journalctl -u landscape-backend -f${NC}"
    echo -e "4. Check service status: ${GREEN}systemctl status landscape-backend${NC}"
    echo -e "${BLUE}================================================================${NC}"
    log "Installation summary displayed"
}

# Main execution function
main() {
    display_banner
    
    # Confirm before proceeding
    if [ -t 0 ]; then
        echo -e "${YELLOW}⚠️ This will DELETE and REINSTALL the application from scratch!${NC}"
        echo -e "${YELLOW}A backup will be created at: $BACKUP_DIR/backup_$TIMESTAMP${NC}"
        read -p "Do you want to continue? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log "Installation cancelled by user"
            exit 0
        fi
    fi
    
    # Execute installation steps
    create_backup || { log "❌ Backup failed"; exit 1; }
    stop_services || { log "❌ Failed to stop services"; exit 1; }
    delete_old_installation || { log "❌ Failed to delete old installation"; exit 1; }
    clone_repository || { log "❌ Failed to clone repository"; exit 1; }
    restore_configuration || { log "❌ Failed to restore configuration"; exit 1; }
    setup_python_environment || { log "❌ Failed to setup Python environment"; exit 1; }
    initialize_database || { log "❌ Failed to initialize database"; exit 1; }
    setup_frontend || { log "❌ Failed to setup frontend"; exit 1; }
    setup_systemd_service || { log "❌ Failed to setup systemd service"; exit 1; }
    set_permissions || { log "❌ Failed to set permissions"; exit 1; }
    start_services || { log "❌ Failed to start services"; exit 1; }
    verify_installation || { log "⚠️ Verification warnings detected"; }
    
    display_summary
    
    log "✅ VPS clean reinstall process completed successfully!"
}

# Run main function
main "$@"
