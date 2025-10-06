#!/bin/bash
# Pre-Deployment Validation Script for V1.00D DevDeploy Workflow
# This script validates all prerequisites before attempting deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VALIDATION_PASSED=true

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  V1.00D DevDeploy Pre-Deployment Validation${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# Function to check status
check_status() {
    local test_name="$1"
    local status="$2"
    local message="$3"
    
    if [ "$status" -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        [ -n "$message" ] && echo -e "   ${BLUE}ℹ${NC}  $message"
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        [ -n "$message" ] && echo -e "   ${RED}⚠${NC}  $message"
        VALIDATION_PASSED=false
    fi
}

# 1. Check GitHub Secrets
echo -e "${BLUE}[1/7] Checking GitHub Secrets${NC}"
echo "---------------------------------------"

if [ -n "$VPS_SSH_KEY" ]; then
    # Check if it looks like a valid SSH key
    if echo "$VPS_SSH_KEY" | grep -q "BEGIN.*PRIVATE KEY"; then
        check_status "VPS_SSH_KEY secret" 0 "Private key format detected"
    else
        check_status "VPS_SSH_KEY secret" 1 "Secret exists but may not be a valid SSH private key"
    fi
else
    check_status "VPS_SSH_KEY secret" 1 "VPS_SSH_KEY is not set - required for deployment"
fi

VPS_HOST="${VPS_HOST:-72.60.176.200}"
VPS_USER="${VPS_USER:-root}"
check_status "VPS_HOST" 0 "Using: $VPS_HOST"
check_status "VPS_USER" 0 "Using: $VPS_USER"

echo ""

# 2. Check Branch
echo -e "${BLUE}[2/7] Validating Git Branch${NC}"
echo "---------------------------------------"

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$CURRENT_BRANCH" = "V1.00D" ]; then
    check_status "Git branch" 0 "On V1.00D branch"
else
    check_status "Git branch" 1 "Not on V1.00D branch (current: $CURRENT_BRANCH)"
fi

echo ""

# 3. Check Node.js and npm
echo -e "${BLUE}[3/7] Checking Node.js Environment${NC}"
echo "---------------------------------------"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_status "Node.js installed" 0 "Version: $NODE_VERSION"
    
    # Check if version is 20.x
    if echo "$NODE_VERSION" | grep -q "^v20\."; then
        check_status "Node.js version" 0 "Version 20.x detected"
    else
        check_status "Node.js version" 1 "Expected version 20.x, got $NODE_VERSION"
    fi
else
    check_status "Node.js installed" 1 "Node.js not found"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    check_status "npm installed" 0 "Version: $NPM_VERSION"
else
    check_status "npm installed" 1 "npm not found"
fi

echo ""

# 4. Check Python
echo -e "${BLUE}[4/7] Checking Python Environment${NC}"
echo "---------------------------------------"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_status "Python installed" 0 "$PYTHON_VERSION"
    
    # Check if version is 3.12
    if python3 --version | grep -q "3\.12"; then
        check_status "Python version" 0 "Version 3.12 detected"
    else
        check_status "Python version" 1 "Expected 3.12, got: $PYTHON_VERSION"
    fi
else
    check_status "Python installed" 1 "Python3 not found"
fi

if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    check_status "pip installed" 0 "pip available"
else
    check_status "pip installed" 1 "pip not found"
fi

echo ""

# 5. Check Dependencies Files
echo -e "${BLUE}[5/7] Checking Dependency Files${NC}"
echo "---------------------------------------"

if [ -f "requirements.txt" ]; then
    REQ_COUNT=$(wc -l < requirements.txt)
    check_status "requirements.txt exists" 0 "$REQ_COUNT lines"
else
    check_status "requirements.txt exists" 1 "File not found"
fi

if [ -f "frontend/package.json" ]; then
    check_status "frontend/package.json exists" 0 "Found"
else
    check_status "frontend/package.json exists" 1 "File not found"
fi

if [ -f "frontend/package-lock.json" ]; then
    check_status "frontend/package-lock.json exists" 0 "Found"
else
    check_status "frontend/package-lock.json exists" 1 "File not found - npm ci requires this"
fi

echo ""

# 6. Check SSH Connectivity (if VPS_SSH_KEY is set)
echo -e "${BLUE}[6/7] Checking VPS Connectivity${NC}"
echo "---------------------------------------"

if [ -n "$VPS_SSH_KEY" ]; then
    # Setup temporary SSH key for testing
    TEMP_KEY=$(mktemp)
    echo "$VPS_SSH_KEY" > "$TEMP_KEY"
    chmod 600 "$TEMP_KEY"
    
    # Test SSH connection
    if ssh -i "$TEMP_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o BatchMode=yes "$VPS_USER@$VPS_HOST" "echo 'Connection successful'" &>/dev/null; then
        check_status "SSH connection to VPS" 0 "Successfully connected to $VPS_USER@$VPS_HOST"
    else
        check_status "SSH connection to VPS" 1 "Cannot connect to $VPS_USER@$VPS_HOST (check firewall, SSH key, and VPS status)"
    fi
    
    # Cleanup
    rm -f "$TEMP_KEY"
else
    check_status "SSH connection to VPS" 1 "Cannot test - VPS_SSH_KEY not set"
fi

# Check basic HTTP connectivity to VPS
if curl -s -m 10 -I "http://$VPS_HOST:8080" &>/dev/null; then
    check_status "HTTP connectivity to VPS" 0 "VPS is responding on port 8080"
else
    check_status "HTTP connectivity to VPS" 1 "VPS not responding on port 8080 (may need deployment)"
fi

echo ""

# 7. Check Deployment Scripts
echo -e "${BLUE}[7/7] Checking Deployment Scripts${NC}"
echo "---------------------------------------"

DEPLOY_SCRIPTS=(
    "scripts/deployment/fix_firewall.sh"
    "scripts/deployment/fix_backend_binding.sh"
)

for script in "${DEPLOY_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_status "$(basename "$script")" 0 "Exists and executable"
        else
            check_status "$(basename "$script")" 1 "Exists but not executable (will chmod +x during deployment)"
        fi
    else
        check_status "$(basename "$script")" 1 "Script not found: $script"
    fi
done

echo ""
echo -e "${BLUE}=====================================================${NC}"

# Final Summary
if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}✅ All validation checks passed!${NC}"
    echo -e "${GREEN}   Deployment can proceed.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some validation checks failed.${NC}"
    echo -e "${YELLOW}   Review the failures above before deploying.${NC}"
    echo ""
    echo -e "${BLUE}Common Solutions:${NC}"
    echo "  • Missing secrets: Add VPS_SSH_KEY in GitHub repo settings"
    echo "  • SSH connection failed: Check VPS firewall and SSH key setup"
    echo "  • Wrong branch: Run 'git checkout V1.00D'"
    echo "  • Missing dependencies: Run 'npm install' and 'pip install -r requirements.txt'"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  • GitHub Secrets: docs/deployment/GITHUB_SECRETS_CONFIGURATION.md"
    echo "  • SSH Setup: archive/vps-config/ssh_key_setup_instructions.md"
    exit 1
fi
