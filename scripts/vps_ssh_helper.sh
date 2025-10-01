#!/bin/bash
# VPS SSH Helper Script
# This script helps you connect to the VPS and run common commands
# Usage: ./vps_ssh_helper.sh [command]

VPS_HOST="72.60.176.200"
VPS_USER="root"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔐 VPS SSH Helper${NC}"
echo -e "${BLUE}==================${NC}"
echo ""

# Function to show menu
show_menu() {
    echo -e "${YELLOW}Available commands:${NC}"
    echo "  1) connect          - Open SSH connection to VPS"
    echo "  2) diagnose         - Run diagnostic script on VPS"
    echo "  3) deploy           - Deploy latest changes to VPS"
    echo "  4) quick-deploy     - Run quick deployment (one-liner)"
    echo "  5) status           - Check services status"
    echo "  6) logs             - View recent logs"
    echo "  7) health           - Check health endpoint"
    echo "  8) restart          - Restart backend service"
    echo "  9) copy-scripts     - Copy deployment scripts to VPS"
    echo "  0) help             - Show this menu"
    echo ""
}

# Check if command provided
if [ $# -eq 0 ]; then
    show_menu
    read -p "Enter command number or name: " CMD
else
    CMD=$1
fi

case $CMD in
    1|connect)
        echo -e "${GREEN}Connecting to VPS...${NC}"
        ssh ${VPS_USER}@${VPS_HOST}
        ;;
    
    2|diagnose)
        echo -e "${GREEN}Running diagnostics on VPS...${NC}"
        echo -e "${YELLOW}First, copying diagnostic script...${NC}"
        scp scripts/vps_diagnostic.sh ${VPS_USER}@${VPS_HOST}:/tmp/
        echo -e "${YELLOW}Running diagnostic...${NC}"
        ssh ${VPS_USER}@${VPS_HOST} 'bash /tmp/vps_diagnostic.sh'
        ;;
    
    3|deploy)
        echo -e "${GREEN}Deploying with automated script...${NC}"
        echo -e "${YELLOW}Copying deployment script...${NC}"
        scp scripts/deploy_vps_automated.sh ${VPS_USER}@${VPS_HOST}:/root/
        echo -e "${YELLOW}Running deployment...${NC}"
        ssh ${VPS_USER}@${VPS_HOST} 'bash /root/deploy_vps_automated.sh'
        ;;
    
    4|quick-deploy)
        echo -e "${GREEN}Running quick deployment...${NC}"
        ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /var/www/landscape-architecture-tool && \
git fetch --all && \
git reset --hard origin/V1.00D && \
systemctl stop landscape-backend && \
pkill -f gunicorn && \
source venv/bin/activate && \
pip install -r requirements.txt && \
cd frontend && npm ci --legacy-peer-deps && npm run build && cd .. && \
systemctl start landscape-backend && \
echo "✅ Deployment complete!" && \
sleep 3 && \
curl -s http://localhost:5000/health | python3 -m json.tool
ENDSSH
        ;;
    
    5|status)
        echo -e "${GREEN}Checking services status...${NC}"
        ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
echo "=== Backend Service ==="
systemctl status landscape-backend --no-pager | head -15
echo ""
echo "=== Nginx Service ==="
systemctl status nginx --no-pager | head -10
echo ""
echo "=== Gunicorn Processes ==="
ps aux | grep gunicorn | grep -v grep
ENDSSH
        ;;
    
    6|logs)
        echo -e "${GREEN}Viewing recent logs...${NC}"
        echo -e "${YELLOW}Backend logs (last 50 lines):${NC}"
        ssh ${VPS_USER}@${VPS_HOST} 'journalctl -u landscape-backend -n 50 --no-pager'
        ;;
    
    7|health)
        echo -e "${GREEN}Checking health endpoint...${NC}"
        echo ""
        echo -e "${YELLOW}Local (from VPS):${NC}"
        ssh ${VPS_USER}@${VPS_HOST} 'curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:5000/health'
        echo ""
        echo -e "${YELLOW}External:${NC}"
        curl -s http://${VPS_HOST}:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://${VPS_HOST}:8080/health
        ;;
    
    8|restart)
        echo -e "${GREEN}Restarting backend service...${NC}"
        ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
systemctl stop landscape-backend
pkill -f gunicorn || true
sleep 2
systemctl start landscape-backend
sleep 3
systemctl status landscape-backend --no-pager
ENDSSH
        ;;
    
    9|copy-scripts)
        echo -e "${GREEN}Copying deployment scripts to VPS...${NC}"
        echo -e "${YELLOW}Copying vps_diagnostic.sh...${NC}"
        scp scripts/vps_diagnostic.sh ${VPS_USER}@${VPS_HOST}:/root/
        echo -e "${YELLOW}Copying deploy_vps_automated.sh...${NC}"
        scp scripts/deploy_vps_automated.sh ${VPS_USER}@${VPS_HOST}:/root/
        echo -e "${YELLOW}Creating quick_deploy.sh...${NC}"
        ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cat > /root/quick_deploy.sh << 'EOF'
#!/bin/bash
cd /var/www/landscape-architecture-tool
git fetch --all && git reset --hard origin/V1.00D
systemctl stop landscape-backend
pkill -f gunicorn || true
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm ci --legacy-peer-deps && npm run build && cd ..
systemctl start landscape-backend
echo "✅ Deployment complete - Check: http://72.60.176.200:8080/health"
EOF
chmod +x /root/quick_deploy.sh
echo "✅ Scripts created in /root/"
ENDSSH
        echo -e "${GREEN}✅ All scripts copied successfully!${NC}"
        echo -e "${YELLOW}You can now run on VPS:${NC}"
        echo "  - /root/quick_deploy.sh"
        echo "  - /root/vps_diagnostic.sh"
        echo "  - /root/deploy_vps_automated.sh"
        ;;
    
    0|help|*)
        show_menu
        ;;
esac

echo ""
echo -e "${BLUE}==================${NC}"
