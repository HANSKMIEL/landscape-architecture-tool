#!/bin/bash
# VPS Deployment Helper Script
# This script helps you deploy to the VPS from your local machine

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VPS_HOST="72.60.176.200"
VPS_USER="root"
VPS_URL="http://72.60.176.200:8080"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 VPS Deployment Helper                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "scripts/vps_deploy_v1d.sh" ]; then
    echo -e "${RED}Error: Must run from repository root${NC}"
    exit 1
fi

echo -e "${YELLOW}Choose deployment method:${NC}"
echo "1. Copy script and show SSH command (recommended)"
echo "2. Execute deployment remotely (requires SSH access)"
echo "3. Just copy the script to VPS"
echo "4. Test VPS connectivity"
echo "5. View deployment documentation"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Copying script to VPS...${NC}"
        scp scripts/vps_deploy_v1d.sh ${VPS_USER}@${VPS_HOST}:/root/
        
        echo ""
        echo -e "${GREEN}✓ Script copied successfully!${NC}"
        echo ""
        echo -e "${YELLOW}Now run these commands:${NC}"
        echo ""
        echo -e "${BLUE}ssh ${VPS_USER}@${VPS_HOST}${NC}"
        echo -e "${BLUE}bash /root/vps_deploy_v1d.sh${NC}"
        echo ""
        ;;
    2)
        echo ""
        echo -e "${BLUE}Executing deployment remotely...${NC}"
        echo -e "${YELLOW}This will run the deployment script on the VPS${NC}"
        echo ""
        read -p "Continue? [y/N]: " confirm
        
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            ssh ${VPS_USER}@${VPS_HOST} 'bash -s' < scripts/vps_deploy_v1d.sh
        else
            echo "Cancelled."
        fi
        ;;
    3)
        echo ""
        echo -e "${BLUE}Copying script to VPS...${NC}"
        scp scripts/vps_deploy_v1d.sh ${VPS_USER}@${VPS_HOST}:/root/
        echo -e "${GREEN}✓ Script copied to /root/vps_deploy_v1d.sh${NC}"
        ;;
    4)
        echo ""
        echo -e "${BLUE}Testing VPS connectivity...${NC}"
        echo ""
        
        echo -e "${YELLOW}Testing SSH access...${NC}"
        if ssh -o ConnectTimeout=5 ${VPS_USER}@${VPS_HOST} 'echo "SSH OK"' > /dev/null 2>&1; then
            echo -e "${GREEN}✓ SSH access working${NC}"
        else
            echo -e "${RED}✗ SSH access failed${NC}"
        fi
        
        echo ""
        echo -e "${YELLOW}Testing HTTP access...${NC}"
        if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 ${VPS_URL}/health | grep -q "200"; then
            echo -e "${GREEN}✓ HTTP access working${NC}"
        else
            echo -e "${RED}✗ HTTP access failed or service not running${NC}"
        fi
        
        echo ""
        echo -e "${YELLOW}Testing frontend...${NC}"
        if curl -s --connect-timeout 5 ${VPS_URL}/ | grep -q "Landscape Architecture Tool"; then
            echo -e "${GREEN}✓ Frontend is responding${NC}"
        else
            echo -e "${RED}✗ Frontend not responding${NC}"
        fi
        ;;
    5)
        echo ""
        echo -e "${BLUE}Opening documentation...${NC}"
        echo ""
        
        if [ -f "docs/QUICK_VPS_DEPLOY.md" ]; then
            cat docs/QUICK_VPS_DEPLOY.md
        else
            echo "Documentation not found!"
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  View logs:     ssh ${VPS_USER}@${VPS_HOST} 'journalctl -u landscape-backend -f'"
echo "  Check status:  ssh ${VPS_USER}@${VPS_HOST} 'systemctl status landscape-backend'"
echo "  Test health:   curl ${VPS_URL}/health"
echo "  Visit site:    ${VPS_URL}/"
echo ""
