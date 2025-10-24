#!/bin/bash
# Pre-commit hook to ensure devdeploy title on V1.00D branch
# This script automatically sets the correct title when working on V1.00D

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Only run on V1.00D branch
if [ "$CURRENT_BRANCH" != "V1.00D" ]; then
    exit 0
fi

echo -e "${BLUE}🔍 Checking devdeploy title configuration on V1.00D branch...${NC}"

# Check if frontend/index.html exists
if [ ! -f "frontend/index.html" ]; then
    echo -e "${YELLOW}⚠️ frontend/index.html not found, skipping title check${NC}"
    exit 0
fi

# Check current title
CURRENT_TITLE=$(grep -o '<title>[^<]*</title>' frontend/index.html | sed 's/<title>\(.*\)<\/title>/\1/')

# Expected devdeploy title
DEVDEPLOY_TITLE="devdeploy - Landscape Architecture Tool (Development)"

if [ "$CURRENT_TITLE" = "$DEVDEPLOY_TITLE" ]; then
    echo -e "${GREEN}✅ DevDeploy title already configured correctly${NC}"
    exit 0
fi

echo -e "${YELLOW}🔧 Setting devdeploy title for V1.00D branch...${NC}"
echo "Current title: $CURRENT_TITLE"
echo "Setting to: $DEVDEPLOY_TITLE"

# Update the title
sed -i "s|<title>.*</title>|<title>$DEVDEPLOY_TITLE</title>|" frontend/index.html

# Verify the change
NEW_TITLE=$(grep -o '<title>[^<]*</title>' frontend/index.html | sed 's/<title>\(.*\)<\/title>/\1/')

if [ "$NEW_TITLE" = "$DEVDEPLOY_TITLE" ]; then
    echo -e "${GREEN}✅ DevDeploy title set successfully${NC}"
    
    # Stage the change if we're in a git repository
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git add frontend/index.html
        echo -e "${GREEN}✅ Title change staged for commit${NC}"
    fi
else
    echo -e "${RED}❌ Failed to set devdeploy title${NC}"
    exit 1
fi
