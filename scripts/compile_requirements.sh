#!/bin/bash
# Enhanced pip-compile script with retry logic and network timeout handling
# Usage: ./scripts/compile_requirements.sh [requirements.in] [--dry-run]

set -e

# Default values
REQUIREMENTS_FILE="${1:-requirements.in}"
DRY_RUN_FLAG="${2:-}"
TIMEOUT_SECONDS=300
MAX_ATTEMPTS=3
BASE_DELAY=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Enhanced pip-compile with network timeout handling${NC}"
echo "Requirements file: $REQUIREMENTS_FILE"
echo "Timeout: ${TIMEOUT_SECONDS}s"
echo "Max attempts: $MAX_ATTEMPTS"
echo ""

# Check if requirements file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}❌ Requirements file '$REQUIREMENTS_FILE' not found${NC}"
    exit 1
fi

# Ensure pip-tools is installed
if ! command -v pip-compile >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ pip-tools not found, installing...${NC}"
    pip install pip-tools
fi

# Function to compile requirements with timeout
compile_with_timeout() {
    local attempt=$1
    local delay=$((BASE_DELAY * attempt))
    
    echo -e "${BLUE}🔄 Attempt $attempt/$MAX_ATTEMPTS (timeout: ${TIMEOUT_SECONDS}s)${NC}"
    
    # Build pip-compile command
    local cmd="pip-compile $REQUIREMENTS_FILE --resolver=backtracking --verbose"
    if [ "$DRY_RUN_FLAG" = "--dry-run" ]; then
        cmd="$cmd --dry-run"
    fi
    
    # Execute with timeout
    # Execute pip-compile with timeout, passing arguments safely
    if [ "$DRY_RUN_FLAG" = "--dry-run" ]; then
        timeout $TIMEOUT_SECONDS pip-compile "$REQUIREMENTS_FILE" --resolver=backtracking --verbose --dry-run
    else
        timeout $TIMEOUT_SECONDS pip-compile "$REQUIREMENTS_FILE" --resolver=backtracking --verbose
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ pip-compile successful on attempt $attempt${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Attempt $attempt failed${NC}"
        
        if [ $attempt -lt $MAX_ATTEMPTS ]; then
            echo -e "${YELLOW}🕐 Waiting ${delay}s before retry...${NC}"
            sleep $delay
        fi
        
        return 1
    fi
}

# Main compilation loop with exponential backoff
echo -e "${BLUE}🚀 Starting pip-compile with retry logic...${NC}"
echo ""

for attempt in $(seq 1 $MAX_ATTEMPTS); do
    if compile_with_timeout $attempt; then
        echo ""
        echo -e "${GREEN}🎉 Requirements compilation completed successfully!${NC}"
        
        # Show summary
        if [ "$DRY_RUN_FLAG" != "--dry-run" ]; then
            OUTPUT_FILE="${REQUIREMENTS_FILE%.in}.txt"
            if [ -f "$OUTPUT_FILE" ]; then
                PACKAGE_COUNT=$(grep -c "^[a-zA-Z]" "$OUTPUT_FILE" || echo "0")
                echo -e "${GREEN}📦 Generated $OUTPUT_FILE with $PACKAGE_COUNT packages${NC}"
            fi
        fi
        
        exit 0
    fi
done

# All attempts failed
echo ""
echo -e "${RED}❌ pip-compile failed after $MAX_ATTEMPTS attempts${NC}"
echo ""
echo -e "${YELLOW}🔍 Troubleshooting suggestions:${NC}"
echo "1. Check network connectivity to PyPI"
echo "2. Try again during off-peak hours"
echo "3. Consider using --upgrade-package for specific packages only"
echo "4. Check if any dependencies have networking issues"
echo ""
echo -e "${BLUE}💡 For immediate development, use existing requirements files${NC}"
exit 1