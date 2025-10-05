#!/bin/bash
# VPS Deployment Script for Landscape Architecture Tool
# This script automates the deployment of latest changes to the VPS at 72.60.176.200:8080
# Updated for V1.00D branch workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 VPS Deployment Script for Landscape Architecture Tool${NC}"
echo -e "${BLUE}================================================================${NC}"

# Configuration
VPS_HOST="72.60.176.200"
VPS_USER="root"
VPS_APP_DIR="/var/www/landscape-architecture-tool"

# Function to check if we have SSH access
check_ssh_access() {
    echo -e "${YELLOW}🔐 Checking SSH access to VPS...${NC}"
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $VPS_USER@$VPS_HOST "echo 'SSH connection successful'" 2>/dev/null; then
        echo -e "${RED}❌ Cannot connect to VPS via SSH${NC}"
        echo -e "${YELLOW}Please ensure:${NC}"
        echo -e "1. SSH key is configured for $VPS_USER@$VPS_HOST"
        echo -e "2. VPS is accessible on port 22"
        echo -e "3. You have proper permissions"
        return 1
    fi
    echo -e "${GREEN}✅ SSH access confirmed${NC}"
    return 0
}

# Function to deploy to VPS
deploy_to_vps() {
    echo -e "${YELLOW}🌐 Deploying to VPS at $VPS_HOST:8080...${NC}"
    
    # Create deployment commands
    ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
        set -e
        
        echo "🔄 Updating repository on VPS..."
        cd /var/www/landscape-architecture-tool || exit 1
        
        # Pull latest changes from V1.00D branch
        git fetch --all
        git reset --hard origin/V1.00D
        
        echo "🛑 Stopping existing services..."
        systemctl stop landscape-backend 2>/dev/null || true
        pkill -f gunicorn 2>/dev/null || true
        
        echo "🔧 Updating Python dependencies..."
        source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        echo "🎨 Building frontend..."
        cd frontend
        if command -v npm &> /dev/null; then
            npm ci --legacy-peer-deps
            npm run build
        else
            echo "⚠️ npm not found, skipping frontend build"
        fi
        cd ..
        
        echo "🔄 Starting backend service..."
        systemctl daemon-reload
        systemctl start landscape-backend
        systemctl enable landscape-backend
        
        echo "✅ VPS deployment completed"
ENDSSH
    
    echo -e "${GREEN}✅ VPS deployment completed successfully${NC}"
}

# Function to verify deployment
verify_deployment() {
    echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
    
    sleep 10  # Wait for services to start
    
    # Check health endpoint
    if curl -f -s "http://$VPS_HOST:8080/health" > /tmp/health_check.json; then
        echo -e "${GREEN}✅ Health endpoint responding${NC}"
        cat /tmp/health_check.json | jq '.' 2>/dev/null || cat /tmp/health_check.json
    else
        echo -e "${RED}❌ Health endpoint not responding${NC}"
        return 1
    fi
    
    # Check frontend
    if curl -f -s "http://$VPS_HOST:8080/" | grep -q "Landscape Architecture Tool"; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
    else
        echo -e "${YELLOW}⚠️ Frontend may not be properly configured${NC}"
    fi
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting VPS deployment process from V1.00D branch...${NC}"
    
    # Step 1: Check SSH access (optional for now)
    if ! check_ssh_access; then
        echo -e "${YELLOW}⚠️ SSH access check failed, providing manual deployment commands...${NC}"
    fi
    
    # Step 2: Show deployment commands for manual execution
    echo -e "${BLUE}📋 Manual VPS Deployment Commands (V1.00D branch):${NC}"
    cat << 'EOF'

Connect to your VPS and run these commands:

ssh root@72.60.176.200

cd /var/www/landscape-architecture-tool
git fetch --all
git reset --hard origin/V1.00D

# Stop services
systemctl stop landscape-backend 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true

# Update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Build frontend
cd frontend && npm ci --legacy-peer-deps && npm run build && cd ..

# Start services
systemctl daemon-reload
systemctl start landscape-backend
systemctl enable landscape-backend

# Check status
systemctl status landscape-backend
curl http://localhost:5000/health

EOF
    
    # Step 3: Verify deployment if we can connect
    if check_ssh_access 2>/dev/null; then
        deploy_to_vps
        verify_deployment
    else
        echo -e "${YELLOW}⚠️ Cannot verify deployment automatically due to SSH access${NC}"
        echo -e "${YELLOW}Please run the manual commands above on your VPS${NC}"
    fi
    
    echo -e "${GREEN}🎉 Deployment process completed!${NC}"
    echo -e "${GREEN}🌐 Check: http://$VPS_HOST:8080/${NC}"
}

# Run main function
main "$@"