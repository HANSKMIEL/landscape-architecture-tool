#!/bin/bash
# GitHub Secrets Verification Helper
# This script helps verify that GitHub secrets are properly configured
# Run this locally to check what secrets you have configured

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  GitHub Secrets Configuration Helper${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) is not installed${NC}"
    echo ""
    echo "To install GitHub CLI:"
    echo "  • macOS: brew install gh"
    echo "  • Ubuntu/Debian: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo "  • Windows: https://github.com/cli/cli#windows"
    echo ""
    echo "After installing, authenticate with: gh auth login"
    echo ""
    echo "Without gh CLI, you can manually check secrets at:"
    echo "  https://github.com/HANSKMIEL/landscape-architecture-tool/settings/secrets/actions"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with GitHub CLI${NC}"
    echo ""
    echo "Please authenticate with: gh auth login"
    exit 1
fi

echo -e "${BLUE}Checking GitHub Secrets for repository...${NC}"
echo ""

# Get repository secrets
echo -e "${BLUE}Repository Secrets:${NC}"
echo "-------------------------------------------"

# List secrets (gh doesn't show values for security)
SECRETS=$(gh secret list 2>&1)

if [ $? -eq 0 ]; then
    echo "$SECRETS"
    echo ""
    
    # Check for required secrets
    echo -e "${BLUE}Required Secrets Status:${NC}"
    echo "-------------------------------------------"
    
    if echo "$SECRETS" | grep -q "VPS_SSH_KEY"; then
        echo -e "${GREEN}✅ VPS_SSH_KEY${NC} - Configured"
    else
        echo -e "${RED}❌ VPS_SSH_KEY${NC} - Not configured (REQUIRED)"
    fi
    
    if echo "$SECRETS" | grep -q "VPS_HOST"; then
        echo -e "${GREEN}✅ VPS_HOST${NC} - Configured"
    else
        echo -e "${YELLOW}⚪ VPS_HOST${NC} - Not configured (optional, defaults to 72.60.176.200)"
    fi
    
    if echo "$SECRETS" | grep -q "VPS_USER"; then
        echo -e "${GREEN}✅ VPS_USER${NC} - Configured"
    else
        echo -e "${YELLOW}⚪ VPS_USER${NC} - Not configured (optional, defaults to root)"
    fi
    
    echo ""
    
    # Check if all required secrets are present
    if echo "$SECRETS" | grep -q "VPS_SSH_KEY"; then
        echo -e "${GREEN}✅ All required secrets are configured!${NC}"
        echo ""
        echo "You can now deploy using:"
        echo "  • Push to V1.00D branch"
        echo "  • Or run workflow manually in GitHub Actions"
    else
        echo -e "${RED}❌ Missing required secrets!${NC}"
        echo ""
        echo "To add VPS_SSH_KEY secret:"
        echo "  1. Generate SSH key: ssh-keygen -t rsa -b 4096 -f ~/.ssh/landscape_deploy"
        echo "  2. Add public key to VPS ~/.ssh/authorized_keys"
        echo "  3. Run: gh secret set VPS_SSH_KEY < ~/.ssh/landscape_deploy"
        echo ""
        echo "Or add manually at:"
        echo "  https://github.com/HANSKMIEL/landscape-architecture-tool/settings/secrets/actions"
    fi
else
    echo -e "${RED}❌ Failed to list secrets${NC}"
    echo "Error: $SECRETS"
    echo ""
    echo "You may need to:"
    echo "  • Check repository permissions"
    echo "  • Re-authenticate: gh auth login"
    echo "  • Manually check at: https://github.com/HANSKMIEL/landscape-architecture-tool/settings/secrets/actions"
fi

echo ""
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  Documentation${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""
echo "For detailed setup instructions, see:"
echo "  📖 docs/deployment/GITHUB_SECRETS_CONFIGURATION.md"
echo ""
echo "For troubleshooting, see:"
echo "  🔧 docs/deployment/DEPLOYMENT_TROUBLESHOOTING.md"
echo ""

# Offer to set up secrets interactively
echo -e "${BLUE}Would you like to set up VPS_SSH_KEY now? [y/N]${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}Setting up VPS_SSH_KEY...${NC}"
    echo ""
    
    # Check if SSH key exists
    if [ -f "$HOME/.ssh/landscape_deploy" ]; then
        echo -e "${GREEN}✅ Found existing SSH key at ~/.ssh/landscape_deploy${NC}"
        echo ""
        echo "Adding to GitHub secrets..."
        
        if gh secret set VPS_SSH_KEY < "$HOME/.ssh/landscape_deploy"; then
            echo -e "${GREEN}✅ VPS_SSH_KEY secret added successfully!${NC}"
        else
            echo -e "${RED}❌ Failed to add secret${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  SSH key not found at ~/.ssh/landscape_deploy${NC}"
        echo ""
        echo "Please generate an SSH key first:"
        echo "  ssh-keygen -t rsa -b 4096 -C 'github-actions@landscape-tool' -f ~/.ssh/landscape_deploy"
        echo ""
        echo "Then add the public key to your VPS:"
        echo "  ssh-copy-id -i ~/.ssh/landscape_deploy.pub root@72.60.176.200"
        echo ""
        echo "After that, run this script again."
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}Done!${NC}"
