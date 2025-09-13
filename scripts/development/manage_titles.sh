#!/bin/bash
# Title Management Script
# Manages different titles for development and production versions

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Title configurations
DEV_TITLE="devdeploy - Landscape Architecture Tool (Development)"
PROD_TITLE="Landscape Architecture Tool - Professional Garden Design Management"

show_usage() {
    echo -e "${BLUE}Title Management Script${NC}"
    echo "Usage: $0 [dev|prod|status]"
    echo ""
    echo "Commands:"
    echo "  dev     - Set development title (devdeploy)"
    echo "  prod    - Set production title"
    echo "  status  - Show current title"
    echo ""
}

set_dev_title() {
    echo -e "${YELLOW}🔧 Setting development title...${NC}"
    sed -i "s|<title>.*</title>|<title>$DEV_TITLE</title>|" frontend/index.html
    echo -e "${GREEN}✅ Development title set${NC}"
    show_current_title
}

set_prod_title() {
    echo -e "${YELLOW}🔧 Setting production title...${NC}"
    sed -i "s|<title>.*</title>|<title>$PROD_TITLE</title>|" frontend/index.html
    echo -e "${GREEN}✅ Production title set${NC}"
    show_current_title
}

show_current_title() {
    echo -e "${BLUE}📋 Current title:${NC}"
    grep '<title>' frontend/index.html | sed 's/^[[:space:]]*//'
}

# Main execution
case "${1:-status}" in
    "dev")
        set_dev_title
        ;;
    "prod")
        set_prod_title
        ;;
    "status")
        show_current_title
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
