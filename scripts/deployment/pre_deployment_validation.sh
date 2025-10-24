#!/bin/bash
# Pre-Deployment Validation Script
# Validates that the repository and VPS are ready for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Pre-Deployment Validation${NC}"
echo -e "${BLUE}============================${NC}"
echo ""

# Configuration
VPS_HOST="${VPS_HOST:-72.60.176.200}"
VPS_USER="${VPS_USER:-root}"
VALIDATION_PASSED=0
VALIDATION_FAILED=0
VALIDATION_WARNINGS=0

# Function to print status
print_status() {
    echo -e "${GREEN}✅${NC} $1"
    VALIDATION_PASSED=$((VALIDATION_PASSED + 1))
}

print_error() {
    echo -e "${RED}❌${NC} $1"
    VALIDATION_FAILED=$((VALIDATION_FAILED + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# 1. Check Git Status
echo -e "${BLUE}1. Git Repository Status${NC}"
if git diff-index --quiet HEAD --; then
    print_status "No uncommitted changes"
else
    print_warning "Uncommitted changes detected - consider committing before deployment"
fi

CURRENT_BRANCH=$(git branch --show-current)
# Note: After branch migration, 'main' is the active development branch (formerly V1.00D)
if [ "$CURRENT_BRANCH" = "V1.00D" ] || [ "$CURRENT_BRANCH" = "main" ]; then
    print_status "On active development branch: $CURRENT_BRANCH"
elif [ "$CURRENT_BRANCH" = "Archive-main" ]; then
    print_warning "On archived production branch - switch to main for development"
else
    print_info "On branch: $CURRENT_BRANCH"
fi

echo ""

# 2. Check Required Files
echo -e "${BLUE}2. Required Files${NC}"
REQUIRED_FILES=(
    ".env.example"
    "requirements.txt"
    "requirements-dev.txt"
    "frontend/package.json"
    "src/main.py"
    "Makefile"
    ".github/workflows/v1d-devdeploy.yml"
    "scripts/deployment/deploy_v1d_to_devdeploy.sh"
    "scripts/deployment/promote_v1d_to_v1.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found: $file"
    else
        print_error "Missing: $file"
    fi
done

echo ""

# 3. Check Active Deployment Scripts
echo -e "${BLUE}3. Deployment Scripts${NC}"
DEPLOYMENT_SCRIPTS=(
    "scripts/deployment/promote_v1d_to_v1.sh"
    "scripts/deployment/deploy_v1d_to_devdeploy.sh"
    "scripts/deployment/github-actions-deploy.sh"
    "scripts/deployment/enhanced-deploy.sh"
    "scripts/deployment/fix_firewall.sh"
    "scripts/deployment/fix_backend_binding.sh"
)

for script in "${DEPLOYMENT_SCRIPTS[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        print_status "Executable: $script"
    elif [ -f "$script" ]; then
        print_warning "Not executable: $script (may need chmod +x)"
    else
        print_error "Missing: $script"
    fi
done

echo ""

# 4. Check for Legacy/Archived Scripts in Wrong Location
echo -e "${BLUE}4. Legacy Scripts Check${NC}"
LEGACY_IN_ROOT=(
    "scripts/deploy_to_vps.sh"
    "scripts/deploy_vps_automated.sh"
    "scripts/vps_deploy_v1d.sh"
    "scripts/vps_deployment_test.sh"
    "scripts/update_v1_from_dev.sh"
)

LEGACY_FOUND=0
for script in "${LEGACY_IN_ROOT[@]}"; do
    if [ -f "$script" ]; then
        print_warning "Legacy script found: $script (should be archived)"
        LEGACY_FOUND=1
    fi
done

if [ $LEGACY_FOUND -eq 0 ]; then
    print_status "No legacy scripts in active directories"
fi

echo ""

# 5. Check Python Environment
echo -e "${BLUE}5. Python Environment${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python available: $PYTHON_VERSION"
else
    print_error "Python3 not found"
fi

if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    print_status "Pip available"
else
    print_error "Pip not found"
fi

echo ""

# 6. Check Node.js Environment
echo -e "${BLUE}6. Node.js Environment${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js available: $NODE_VERSION"
else
    print_error "Node.js not found"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_status "npm available: $NPM_VERSION"
else
    print_error "npm not found"
fi

echo ""

# 7. Check Frontend Dependencies
echo -e "${BLUE}7. Frontend Dependencies${NC}"
if [ -d "frontend/node_modules" ]; then
    print_status "Frontend node_modules exists"
else
    print_warning "Frontend node_modules missing - run 'cd frontend && npm ci --legacy-peer-deps'"
fi

if [ -f "frontend/package-lock.json" ]; then
    print_status "package-lock.json exists"
else
    print_warning "package-lock.json missing"
fi

echo ""

# 8. Check Backend Dependencies
echo -e "${BLUE}8. Backend Dependencies${NC}"
if python3 -c "import flask" 2>/dev/null; then
    print_status "Flask is installed"
else
    print_warning "Flask not installed - run 'pip install -r requirements.txt'"
fi

echo ""

# 9. Check Documentation
echo -e "${BLUE}9. Documentation${NC}"
DOCS=(
    ".github/SECRETS_REQUIRED.md"
    ".github/copilot-instructions.md"
    "docs/deployment/DEPLOYMENT_SCRIPTS_GUIDE.md"
    "README.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        print_status "Found: $doc"
    else
        print_warning "Missing: $doc"
    fi
done

echo ""

# 10. Check Secrets Configuration (if in GitHub Actions)
echo -e "${BLUE}10. Secrets Configuration${NC}"
if [ -n "$GITHUB_ACTIONS" ]; then
    if [ -n "$VPS_SSH_KEY" ]; then
        print_status "VPS_SSH_KEY is configured"
    else
        print_error "VPS_SSH_KEY is NOT configured"
    fi
    
    if [ -n "$VPS_HOST" ]; then
        print_info "VPS_HOST: $VPS_HOST"
    else
        print_info "VPS_HOST using default: 72.60.176.200"
    fi
    
    if [ -n "$VPS_USER" ]; then
        print_info "VPS_USER: $VPS_USER"
    else
        print_info "VPS_USER using default: root"
    fi
else
    print_info "Not running in GitHub Actions - skipping secret checks"
    print_info "To validate secrets, run: .github/workflows/validate-secrets.yml"
fi

echo ""

# 11. Test VPS Connection (if SSH key is available)
echo -e "${BLUE}11. VPS Connection Test${NC}"
if [ -n "$VPS_SSH_KEY" ] && [ -n "$GITHUB_ACTIONS" ]; then
    print_info "Testing SSH connection to $VPS_HOST..."
    
    # Test SSH connection using process substitution for the key
    if timeout 30 ssh -i <(echo "$VPS_SSH_KEY") -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        $VPS_USER@$VPS_HOST "echo 'SSH connection successful'" 2>&1; then
        print_status "VPS connection test passed"
    else
        print_error "VPS connection test failed"
    fi
else
    print_info "Skipping VPS connection test (no SSH key or not in GitHub Actions)"
fi

echo ""

# 12. Summary
echo -e "${BLUE}============================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}============================${NC}"
echo ""
echo -e "${GREEN}✅ Passed:${NC} $VALIDATION_PASSED"
echo -e "${YELLOW}⚠️  Warnings:${NC} $VALIDATION_WARNINGS"
echo -e "${RED}❌ Failed:${NC} $VALIDATION_FAILED"
echo ""

if [ $VALIDATION_FAILED -eq 0 ] && [ $VALIDATION_WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 All validations passed! Ready for deployment.${NC}"
    exit 0
elif [ $VALIDATION_FAILED -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validations passed with warnings. Review warnings before deployment.${NC}"
    exit 0
else
    echo -e "${RED}❌ Validation failed. Please fix errors before deployment.${NC}"
    exit 1
fi
