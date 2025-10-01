#!/bin/bash
# VPS Diagnostic Script for Landscape Architecture Tool
# Run this script on the VPS to diagnose deployment issues
# Usage: bash vps_diagnostic.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🔍 VPS Diagnostic Report${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to check status
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# 1. System Information
echo -e "${YELLOW}📊 System Information:${NC}"
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Uptime: $(uptime -p)"
echo ""

# 2. Repository Status
echo -e "${YELLOW}📁 Repository Status:${NC}"
if [ -d "/var/www/landscape-architecture-tool" ]; then
    cd /var/www/landscape-architecture-tool
    echo "Repository Location: $(pwd)"
    echo "Current Branch: $(git branch --show-current 2>/dev/null || echo 'Unknown')"
    echo "Last Commit: $(git log -1 --format='%h - %s (%ar)' 2>/dev/null || echo 'Unknown')"
    echo "Last Update: $(stat -c %y .git/FETCH_HEAD 2>/dev/null || echo 'Unknown')"
    echo ""
    
    # Check for uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        check_status 0 "No uncommitted changes"
    else
        check_status 1 "Uncommitted changes detected"
        echo "  Files modified:"
        git status --short 2>/dev/null | head -10
    fi
else
    check_status 1 "Repository not found at /var/www/landscape-architecture-tool"
fi
echo ""

# 3. Service Status
echo -e "${YELLOW}🔧 Service Status:${NC}"

# Check landscape-backend service
if systemctl is-active --quiet landscape-backend; then
    check_status 0 "landscape-backend service is running"
    echo "  Status: $(systemctl show landscape-backend -p ActiveState --value)"
    echo "  Since: $(systemctl show landscape-backend -p ActiveEnterTimestamp --value)"
else
    check_status 1 "landscape-backend service is NOT running"
fi

# Check for gunicorn processes
GUNICORN_PROCS=$(pgrep -f gunicorn | wc -l)
if [ $GUNICORN_PROCS -gt 0 ]; then
    check_status 0 "Gunicorn processes running ($GUNICORN_PROCS processes)"
else
    check_status 1 "No Gunicorn processes found"
fi

# Check nginx
if systemctl is-active --quiet nginx; then
    check_status 0 "Nginx is running"
else
    check_status 1 "Nginx is NOT running"
fi
echo ""

# 4. Python Environment
echo -e "${YELLOW}🐍 Python Environment:${NC}"
if [ -d "/var/www/landscape-architecture-tool/venv" ]; then
    check_status 0 "Virtual environment exists"
    source /var/www/landscape-architecture-tool/venv/bin/activate
    echo "  Python version: $(python --version 2>&1)"
    echo "  Pip version: $(pip --version 2>&1 | cut -d' ' -f1,2)"
    
    # Check key dependencies
    echo "  Key packages:"
    pip list 2>/dev/null | grep -E "(Flask|gunicorn|SQLAlchemy)" | sed 's/^/    /'
else
    check_status 1 "Virtual environment not found"
fi
echo ""

# 5. Frontend Build
echo -e "${YELLOW}🎨 Frontend Status:${NC}"
if [ -d "/var/www/landscape-architecture-tool/frontend/dist" ]; then
    check_status 0 "Frontend build exists"
    echo "  Build directory: /var/www/landscape-architecture-tool/frontend/dist"
    DIST_DATE=$(stat -c %y /var/www/landscape-architecture-tool/frontend/dist/index.html 2>/dev/null || echo "Unknown")
    echo "  Last build: $DIST_DATE"
    
    # Check if build is old (more than 7 days)
    DIST_AGE=$(find /var/www/landscape-architecture-tool/frontend/dist/index.html -mtime +7 2>/dev/null | wc -l)
    if [ $DIST_AGE -gt 0 ]; then
        check_status 1 "Frontend build is older than 7 days (needs rebuild)"
    else
        check_status 0 "Frontend build is recent"
    fi
else
    check_status 1 "Frontend build not found"
fi

# Check if npm is available
if command -v npm &> /dev/null; then
    check_status 0 "npm is available ($(npm --version))"
else
    check_status 1 "npm is NOT installed"
fi
echo ""

# 6. Network & Port Status
echo -e "${YELLOW}🌐 Network Status:${NC}"

# Check if port 8080 is listening
if ss -ln | grep -q ":8080"; then
    check_status 0 "Port 8080 is listening"
else
    check_status 1 "Port 8080 is NOT listening"
fi

# Check if port 5000 is listening (backend)
if ss -ln | grep -q ":5000"; then
    check_status 0 "Port 5000 (backend) is listening"
else
    check_status 1 "Port 5000 (backend) is NOT listening"
fi

# Test local health endpoint
if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    check_status 0 "Backend health endpoint responding"
    VERSION=$(curl -s http://localhost:5000/health 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo "  Version: ${VERSION:-Unknown}"
else
    check_status 1 "Backend health endpoint NOT responding"
fi

# Test external access
if curl -f -s http://72.60.176.200:8080/health > /dev/null 2>&1; then
    check_status 0 "External access working (http://72.60.176.200:8080)"
else
    check_status 1 "External access FAILING"
fi
echo ""

# 7. Recent Logs
echo -e "${YELLOW}📋 Recent Service Logs (last 20 lines):${NC}"
if systemctl is-active --quiet landscape-backend; then
    echo "--- landscape-backend logs ---"
    journalctl -u landscape-backend -n 20 --no-pager 2>/dev/null | tail -20
else
    echo "Service not running, no logs available"
fi
echo ""

# 8. Disk Space
echo -e "${YELLOW}💾 Disk Space:${NC}"
df -h / | tail -1
echo ""

# 9. Git Remote Status
echo -e "${YELLOW}🔄 Git Remote Status:${NC}"
if [ -d "/var/www/landscape-architecture-tool/.git" ]; then
    cd /var/www/landscape-architecture-tool
    echo "Remote URL: $(git remote get-url origin 2>/dev/null || echo 'Unknown')"
    
    # Fetch latest info
    echo "Fetching latest remote info..."
    git fetch --dry-run 2>&1 | head -5
    
    # Check commits behind
    COMMITS_BEHIND=$(git rev-list HEAD..origin/V1.00D --count 2>/dev/null || echo "Unknown")
    if [ "$COMMITS_BEHIND" != "Unknown" ] && [ $COMMITS_BEHIND -gt 0 ]; then
        check_status 1 "Repository is $COMMITS_BEHIND commits behind origin/V1.00D"
    else
        check_status 0 "Repository is up to date with origin/V1.00D"
    fi
fi
echo ""

# 10. Summary & Recommendations
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}📝 Summary & Recommendations:${NC}"
echo -e "${BLUE}================================================${NC}"

ISSUES=0

# Check critical issues
if ! systemctl is-active --quiet landscape-backend; then
    echo -e "${RED}❌ CRITICAL: Backend service is not running${NC}"
    echo "   Fix: systemctl start landscape-backend"
    ISSUES=$((ISSUES+1))
fi

if ! systemctl is-active --quiet nginx; then
    echo -e "${RED}❌ CRITICAL: Nginx is not running${NC}"
    echo "   Fix: systemctl start nginx"
    ISSUES=$((ISSUES+1))
fi

if [ ! -d "/var/www/landscape-architecture-tool/venv" ]; then
    echo -e "${RED}❌ CRITICAL: Virtual environment missing${NC}"
    echo "   Fix: python3 -m venv /var/www/landscape-architecture-tool/venv"
    ISSUES=$((ISSUES+1))
fi

if [ ! -d "/var/www/landscape-architecture-tool/frontend/dist" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Frontend build missing${NC}"
    echo "   Fix: cd /var/www/landscape-architecture-tool/frontend && npm ci --legacy-peer-deps && npm run build"
    ISSUES=$((ISSUES+1))
fi

# Check if repo needs update
if [ -d "/var/www/landscape-architecture-tool/.git" ]; then
    cd /var/www/landscape-architecture-tool
    COMMITS_BEHIND=$(git rev-list HEAD..origin/V1.00D --count 2>/dev/null || echo "0")
    if [ "$COMMITS_BEHIND" != "0" ] && [ $COMMITS_BEHIND -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Repository needs update (${COMMITS_BEHIND} commits behind)${NC}"
        echo "   Fix: Run the deployment script"
        ISSUES=$((ISSUES+1))
    fi
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! System appears healthy.${NC}"
    echo ""
    echo "If deployments are not showing up, the issue might be:"
    echo "1. Repository needs to be updated (run: git fetch && git reset --hard origin/V1.00D)"
    echo "2. Frontend needs to be rebuilt (run deployment script)"
    echo "3. Services need to be restarted"
else
    echo -e "${YELLOW}Found $ISSUES issue(s) that need attention.${NC}"
fi

echo ""
echo -e "${BLUE}🚀 To deploy latest changes, run:${NC}"
echo "   bash /root/quick_deploy.sh"
echo ""
echo -e "${BLUE}Or manually run:${NC}"
echo "   cd /var/www/landscape-architecture-tool && \\"
echo "   git fetch --all && git reset --hard origin/V1.00D && \\"
echo "   systemctl stop landscape-backend && pkill -f gunicorn && \\"
echo "   source venv/bin/activate && pip install -r requirements.txt && \\"
echo "   cd frontend && npm ci --legacy-peer-deps && npm run build && cd .. && \\"
echo "   systemctl start landscape-backend"
echo ""
echo -e "${BLUE}================================================${NC}"
