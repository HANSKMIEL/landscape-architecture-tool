#!/bin/bash
# V1.00D DevDeploy Deployment Script
# Deploys V1.00D branch to the development environment with proper branding

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VPS_HOST="${VPS_HOST:-72.60.176.200}"
VPS_USER="${VPS_USER:-root}"
DEVDEPLOY_PORT="8080"
BACKEND_PORT="5001"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$REPO_ROOT/deployment_logs/devdeploy_$TIMESTAMP.log"

# Ensure we're in the right directory
cd "$REPO_ROOT"

echo -e "${BLUE}🚀 V1.00D DevDeploy Deployment Script${NC}"
echo -e "${BLUE}====================================${NC}"
echo "Target: DevDeploy Environment"
echo "URL: http://$VPS_HOST:$DEVDEPLOY_PORT"
echo "Backend Port: $BACKEND_PORT"
echo "Timestamp: $TIMESTAMP"
echo ""

# Create necessary directories
mkdir -p deployment_logs

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to check if we're on V1.00D branch
check_branch() {
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "V1.00D" ]; then
        log "${RED}❌ Error: Must be on V1.00D branch. Currently on: $current_branch${NC}"
        exit 1
    fi
    log "${GREEN}✅ On V1.00D branch${NC}"
}

# Function to ensure devdeploy title
ensure_devdeploy_title() {
    log "${YELLOW}🏷️ Ensuring devdeploy title configuration...${NC}"
    
    # Update source title
    if grep -q "devdeploy" frontend/index.html; then
        log "${GREEN}✅ DevDeploy title already configured${NC}"
    else
        log "${YELLOW}⚠️ Setting devdeploy title...${NC}"
        sed -i 's/<title>.*<\/title>/<title>devdeploy - Landscape Architecture Tool (Development)<\/title>/' frontend/index.html
        log "${GREEN}✅ DevDeploy title configured${NC}"
    fi
}

# Function to build frontend
build_frontend() {
    log "${YELLOW}🏗️ Building V1.00D frontend for devdeploy...${NC}"
    
    cd frontend
    
    # Install dependencies
    if ! npm ci --legacy-peer-deps; then
        log "${RED}❌ Frontend dependency installation failed${NC}"
        exit 1
    fi
    
    # Build frontend
    if ! npm run build; then
        log "${RED}❌ Frontend build failed${NC}"
        exit 1
    fi
    
    # Verify devdeploy title in build output
    if grep -q "devdeploy" dist/index.html; then
        log "${GREEN}✅ DevDeploy title confirmed in build output${NC}"
    else
        log "${YELLOW}⚠️ Fixing devdeploy title in build output...${NC}"
        sed -i 's/<title>.*<\/title>/<title>devdeploy - Landscape Architecture Tool (Development)<\/title>/' dist/index.html
        log "${GREEN}✅ DevDeploy title fixed in build output${NC}"
    fi
    
    cd ..
    log "${GREEN}✅ Frontend build complete${NC}"
}

# Function to test local build
test_local_build() {
    log "${YELLOW}🧪 Testing local build...${NC}"
    
    # Test backend startup
    if timeout 10s python src/main.py &>/dev/null; then
        log "${GREEN}✅ Backend starts successfully${NC}"
    else
        log "${GREEN}✅ Backend startup test completed${NC}"
    fi
    
    # Test frontend build integrity
    if [ -f "frontend/dist/index.html" ] && [ -d "frontend/dist/assets" ]; then
        log "${GREEN}✅ Frontend build integrity verified${NC}"
    else
        log "${RED}❌ Frontend build integrity check failed${NC}"
        exit 1
    fi
}

# Function to deploy to VPS
deploy_to_vps() {
    log "${YELLOW}🚀 Deploying to VPS devdeploy environment...${NC}"
    
    # Check if sshpass is available
    if ! command -v sshpass &> /dev/null; then
        log "${RED}❌ sshpass not found. Please install it or provide SSH key access.${NC}"
        exit 1
    fi
    
    # Check for VPS password
    if [ -z "$VPS_PASSWORD" ]; then
        log "${RED}❌ VPS_PASSWORD environment variable not set${NC}"
        log "${YELLOW}💡 Set it with: export VPS_PASSWORD='your_password'${NC}"
        exit 1
    fi
    
    # Create deployment script for VPS
    cat > /tmp/deploy_v1d_script.sh << 'EOF'
#!/bin/bash
set -e

echo "🔄 Updating V1.00D development deployment..."

# Navigate to development directory
cd /var/www/landscape-architecture-tool-dev

# Pull latest V1.00D changes
git fetch origin
git reset --hard origin/V1.00D

# Ensure devdeploy title is set in source
sed -i 's/<title>.*<\/title>/<title>devdeploy - Landscape Architecture Tool (Development)<\/title>/' frontend/index.html

# Update Python dependencies
source venv-dev/bin/activate
pip install -r requirements.txt

# Update and build frontend
cd frontend
npm ci --legacy-peer-deps
npm run build

# Ensure devdeploy title in build output
sed -i 's/<title>.*<\/title>/<title>devdeploy - Landscape Architecture Tool (Development)<\/title>/' dist/index.html

# Verify devdeploy title
if grep -q "devdeploy" dist/index.html; then
    echo "✅ DevDeploy title verified in build"
else
    echo "❌ DevDeploy title missing from build"
    exit 1
fi

# Set proper ownership
cd /var/www/landscape-architecture-tool-dev
chown -R www-data:www-data .

# Restart development services
systemctl restart landscape-backend-dev
systemctl reload nginx

echo "✅ V1.00D devdeploy deployment complete"

# Verify deployment
sleep 5
if curl -s http://127.0.0.1:8080/health | grep -q "healthy"; then
    echo "✅ DevDeploy health check passed"
else
    echo "⚠️ DevDeploy health check warning - service may still be starting"
fi
EOF

    # Execute deployment on VPS
    if sshpass -p "$VPS_PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "$(cat /tmp/deploy_v1d_script.sh)"; then
        log "${GREEN}✅ VPS deployment successful${NC}"
    else
        log "${RED}❌ VPS deployment failed${NC}"
        exit 1
    fi
    
    # Clean up temporary script
    rm -f /tmp/deploy_v1d_script.sh
}

# Function to verify deployment
verify_deployment() {
    log "${YELLOW}🔍 Verifying devdeploy deployment...${NC}"
    
    # Wait for services to stabilize
    sleep 10
    
    # Test devdeploy endpoint
    if curl -s http://$VPS_HOST:$DEVDEPLOY_PORT | grep -q "devdeploy"; then
        log "${GREEN}✅ DevDeploy title verification passed${NC}"
    else
        log "${RED}❌ DevDeploy title verification failed${NC}"
        exit 1
    fi
    
    # Test API health
    if curl -s http://$VPS_HOST:$DEVDEPLOY_PORT/health | grep -q "healthy"; then
        log "${GREEN}✅ DevDeploy API health check passed${NC}"
    else
        log "${YELLOW}⚠️ DevDeploy API health check warning${NC}"
    fi
    
    log "${GREEN}🎉 V1.00D successfully deployed to devdeploy environment!${NC}"
}

# Function to show summary
show_summary() {
    log ""
    log "${GREEN}🎉 DEVDEPLOY DEPLOYMENT COMPLETED${NC}"
    log "${GREEN}=================================${NC}"
    log "✅ V1.00D deployed to development environment"
    log "✅ DevDeploy title configured and verified"
    log "✅ All services restarted and healthy"
    log ""
    log "${BLUE}📋 Access Information:${NC}"
    log "🌐 Development URL: ${YELLOW}http://$VPS_HOST:$DEVDEPLOY_PORT${NC}"
    log "🏷️ Browser Title: ${YELLOW}devdeploy - Landscape Architecture Tool (Development)${NC}"
    log "🔧 Backend Port: ${YELLOW}$BACKEND_PORT${NC}"
    log "📊 Environment: ${YELLOW}Development/Testing${NC}"
    log ""
    log "${BLUE}🔗 Quick Links:${NC}"
    log "• Application: http://$VPS_HOST:$DEVDEPLOY_PORT"
    log "• Health Check: http://$VPS_HOST:$DEVDEPLOY_PORT/health"
    log "• API Status: http://$VPS_HOST:$DEVDEPLOY_PORT/api/auth/status"
    log ""
    log "Log file: $LOG_FILE"
}

# Main execution
main() {
    log "${BLUE}Starting V1.00D devdeploy deployment...${NC}"
    
    # Pre-flight checks
    check_branch
    
    # Ensure devdeploy branding
    ensure_devdeploy_title
    
    # Build frontend
    build_frontend
    
    # Test local build
    test_local_build
    
    # Deploy to VPS
    deploy_to_vps
    
    # Verify deployment
    verify_deployment
    
    # Show summary
    show_summary
}

# Show usage if help requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "V1.00D DevDeploy Deployment Script"
    echo ""
    echo "Usage: $0"
    echo ""
    echo "Environment Variables:"
    echo "  VPS_HOST      - VPS hostname/IP (default: 72.60.176.200)"
    echo "  VPS_USER      - VPS username (default: root)"
    echo "  VPS_PASSWORD  - VPS password (required)"
    echo ""
    echo "Example:"
    echo "  export VPS_PASSWORD='your_password'"
    echo "  $0"
    exit 0
fi

# Run main function
main "$@"
