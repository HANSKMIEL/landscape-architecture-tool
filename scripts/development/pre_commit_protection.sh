#!/bin/bash
# Pre-commit Hook for Branch Protection and Feature Isolation
# Prevents dangerous commits and ensures proper development workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

echo -e "${BLUE}🛡️ Branch Protection Pre-commit Hook${NC}"
echo "Current branch: $BRANCH"

# Function to block main branch commits
block_main_commits() {
    echo -e "${RED}❌ CRITICAL: Direct commits to main branch are NOT ALLOWED!${NC}"
    echo ""
    echo -e "${YELLOW}🔒 Main branch is production-protected. Use this workflow instead:${NC}"
    echo ""
    echo "1. Switch to development branch:"
    echo -e "   ${GREEN}git checkout V1.00D${NC}"
    echo ""
    echo "2. Make your changes on V1.00D branch"
    echo ""
    echo "3. Test in devdeploy environment:"
    echo -e "   ${GREEN}./scripts/deployment/deploy_v1d_to_devdeploy.sh${NC}"
    echo ""
    echo "4. When ready, promote to production:"
    echo -e "   ${GREEN}./scripts/deployment/promote_v1d_to_v1.sh${NC}"
    echo ""
    echo -e "${BLUE}💡 This protects production (https://optura.nl) from accidental changes${NC}"
    exit 1
}

# Function to ensure devdeploy title on V1.00D
ensure_devdeploy_title() {
    echo -e "${YELLOW}🏷️ Ensuring devdeploy title for V1.00D branch...${NC}"
    
    if [ -f "frontend/index.html" ]; then
        CURRENT_TITLE=$(grep -o '<title>[^<]*</title>' frontend/index.html | sed 's/<title>\(.*\)<\/title>/\1/')
        DEVDEPLOY_TITLE="devdeploy - Landscape Architecture Tool (Development)"
        
        if [ "$CURRENT_TITLE" != "$DEVDEPLOY_TITLE" ]; then
            echo -e "${YELLOW}⚠️ Fixing title for V1.00D branch...${NC}"
            sed -i "s|<title>.*</title>|<title>$DEVDEPLOY_TITLE</title>|" frontend/index.html
            git add frontend/index.html
            echo -e "${GREEN}✅ DevDeploy title set and staged${NC}"
        else
            echo -e "${GREEN}✅ DevDeploy title already correct${NC}"
        fi
    fi
}

# Function to validate workflow files
validate_workflow_changes() {
    # Check if any workflow files are being modified
    WORKFLOW_FILES=$(git diff --cached --name-only | grep -E "\.github/workflows/.*\.yml$" || true)
    
    if [ -n "$WORKFLOW_FILES" ]; then
        echo -e "${YELLOW}⚠️ Workflow files being modified:${NC}"
        echo "$WORKFLOW_FILES"
        
        # Check for dangerous workflow changes
        if echo "$WORKFLOW_FILES" | grep -E "(main-ci|v1-deployment|production)" > /dev/null; then
            echo -e "${RED}❌ Critical workflow files detected!${NC}"
            echo -e "${YELLOW}🔍 Please review these changes carefully:${NC}"
            echo "$WORKFLOW_FILES"
            
            # In V1.00D, this is allowed but with warning
            if [ "$BRANCH" = "V1.00D" ]; then
                echo -e "${YELLOW}⚠️ Workflow changes on V1.00D will be tested in devdeploy environment${NC}"
                echo -e "${GREEN}✅ Proceeding with workflow changes on development branch${NC}"
            fi
        fi
    fi
}

# Function to check for production-affecting changes
check_production_impact() {
    # Check for changes that might affect production
    SENSITIVE_FILES=$(git diff --cached --name-only | grep -E "(main\.py|requirements\.txt|Dockerfile|docker-compose\.yml)" || true)
    
    if [ -n "$SENSITIVE_FILES" ]; then
        echo -e "${YELLOW}⚠️ Sensitive files being modified:${NC}"
        echo "$SENSITIVE_FILES"
        
        if [ "$BRANCH" = "V1.00D" ]; then
            echo -e "${GREEN}✅ Changes will be tested in devdeploy environment first${NC}"
        else
            echo -e "${YELLOW}⚠️ Please ensure these changes are tested thoroughly${NC}"
        fi
    fi
}

# Function to run quick validation
run_quick_validation() {
    echo -e "${YELLOW}🧪 Running quick validation...${NC}"
    
    # Check if Python files have syntax errors
    PYTHON_FILES=$(git diff --cached --name-only | grep "\.py$" || true)
    if [ -n "$PYTHON_FILES" ]; then
        for file in $PYTHON_FILES; do
            if [ -f "$file" ]; then
                if ! python -m py_compile "$file" 2>/dev/null; then
                    echo -e "${RED}❌ Python syntax error in: $file${NC}"
                    exit 1
                fi
            fi
        done
        echo -e "${GREEN}✅ Python syntax validation passed${NC}"
    fi
    
    # Check if frontend files have basic issues
    if git diff --cached --name-only | grep -E "\.(js|jsx|ts|tsx)$" > /dev/null; then
        if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
            cd frontend
            if command -v npm > /dev/null; then
                # Quick lint check if available
                if npm list eslint > /dev/null 2>&1; then
                    echo -e "${YELLOW}🔍 Running frontend lint check...${NC}"
                    if npm run lint:check > /dev/null 2>&1; then
                        echo -e "${GREEN}✅ Frontend lint check passed${NC}"
                    else
                        echo -e "${YELLOW}⚠️ Frontend lint issues detected (not blocking)${NC}"
                    fi
                fi
            fi
            cd ..
        fi
    fi
}

# Function to show environment status
show_environment_status() {
    echo -e "${BLUE}📊 Environment Status:${NC}"
    
    # Check if devdeploy is accessible
    if command -v curl > /dev/null; then
        if curl -s --connect-timeout 3 http://72.60.176.200:8080/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ DevDeploy environment: Online${NC}"
        else
            echo -e "${YELLOW}⚠️ DevDeploy environment: Offline or unreachable${NC}"
        fi
        
        if curl -s --connect-timeout 3 https://optura.nl/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Production environment: Online${NC}"
        else
            echo -e "${YELLOW}⚠️ Production environment: Offline or unreachable${NC}"
        fi
    fi
}

# Main execution
main() {
    echo ""
    
    # Branch-specific protection
    case "$BRANCH" in
        "main")
            block_main_commits
            ;;
        "V1.00D")
            ensure_devdeploy_title
            validate_workflow_changes
            check_production_impact
            run_quick_validation
            show_environment_status
            echo -e "${GREEN}✅ V1.00D pre-commit validation passed${NC}"
            ;;
        "feature/"*)
            echo -e "${BLUE}🔧 Feature branch detected${NC}"
            run_quick_validation
            echo -e "${GREEN}✅ Feature branch pre-commit validation passed${NC}"
            ;;
        *)
            echo -e "${YELLOW}⚠️ Unknown branch: $BRANCH${NC}"
            echo -e "${BLUE}💡 Consider using V1.00D for development${NC}"
            run_quick_validation
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}🎉 Pre-commit hook completed successfully!${NC}"
}

# Show help if requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Branch Protection Pre-commit Hook"
    echo ""
    echo "This hook enforces branch protection rules and ensures safe development:"
    echo ""
    echo "• Blocks direct commits to main branch"
    echo "• Ensures devdeploy title on V1.00D branch"
    echo "• Validates workflow changes"
    echo "• Runs quick syntax validation"
    echo "• Shows environment status"
    echo ""
    echo "To install as git hook:"
    echo "  ln -sf ../../scripts/development/pre_commit_protection.sh .git/hooks/pre-commit"
    echo ""
    echo "To run manually:"
    echo "  ./scripts/development/pre_commit_protection.sh"
    exit 0
fi

# Run main function
main "$@"
