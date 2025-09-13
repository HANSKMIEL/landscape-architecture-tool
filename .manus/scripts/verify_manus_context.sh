#!/bin/bash

# Manus Context Verification Script
# Verifies that Manus has successfully loaded context from .manus folder
# Usage: ./verify_manus_context.sh

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MANUS_DIR="$PROJECT_ROOT/.manus"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        🤖 MANUS CONTEXT VERIFICATION                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo -e "${BLUE}📍 Current Branch:${NC} $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" != "V1.00D" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Not on V1.00D branch. Context may not be current.${NC}"
fi

echo ""

# Verify .manus directory structure
echo -e "${BLUE}📂 Verifying .manus Directory Structure:${NC}"

required_dirs=(
    ".manus"
    ".manus/handoff"
    ".manus/reports"
    ".manus/context"
    ".manus/scripts"
)

required_files=(
    ".manus/CONTINUATION_INSTRUCTIONS.md"
    ".manus/TASK_CONTINUATION.md"
    ".manus/MANUS_CONTEXT_MANAGEMENT.md"
    ".manus/reports/current_session_report.md"
    ".manus/scripts/copilot_handoff.sh"
    ".manus/scripts/monitor_copilot_completion.sh"
)

all_good=true

# Check directories
for dir in "${required_dirs[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        echo -e "   ✅ $dir"
    else
        echo -e "   ❌ $dir ${RED}(missing)${NC}"
        all_good=false
    fi
done

echo ""

# Check files
echo -e "${BLUE}📄 Verifying Required Context Files:${NC}"
for file in "${required_files[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        size=$(du -h "$PROJECT_ROOT/$file" | cut -f1)
        echo -e "   ✅ $file ${GREEN}($size)${NC}"
    else
        echo -e "   ❌ $file ${RED}(missing)${NC}"
        all_good=false
    fi
done

echo ""

# Check recent handoff files
echo -e "${BLUE}🤖 Recent AI-to-AI Handoff Files:${NC}"
if [[ -d "$MANUS_DIR/handoff" ]]; then
    handoff_count=$(ls -1 "$MANUS_DIR/handoff"/*.md 2>/dev/null | wc -l || echo "0")
    if [[ $handoff_count -gt 0 ]]; then
        echo -e "   📊 Found $handoff_count handoff files"
        # Show most recent 3 files
        ls -lt "$MANUS_DIR/handoff"/*.md 2>/dev/null | head -3 | while read -r line; do
            filename=$(echo "$line" | awk '{print $9}' | xargs basename)
            date=$(echo "$line" | awk '{print $6, $7, $8}')
            echo -e "   📝 $filename ${GREEN}($date)${NC}"
        done
    else
        echo -e "   ${YELLOW}⚠️  No handoff files found${NC}"
    fi
else
    echo -e "   ${RED}❌ Handoff directory missing${NC}"
    all_good=false
fi

echo ""

# Check GitHub connectivity
echo -e "${BLUE}🔗 GitHub Connectivity:${NC}"
if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
        username=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
        echo -e "   ✅ GitHub CLI authenticated as: ${GREEN}$username${NC}"
        
        # Check repository access
        if gh repo view >/dev/null 2>&1; then
            repo_name=$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null || echo "unknown")
            echo -e "   ✅ Repository access: ${GREEN}$repo_name${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Repository access limited${NC}"
        fi
    else
        echo -e "   ${RED}❌ GitHub CLI not authenticated${NC}"
        all_good=false
    fi
else
    echo -e "   ${RED}❌ GitHub CLI not installed${NC}"
    all_good=false
fi

echo ""

# Check development environment
echo -e "${BLUE}🚀 Development Environment:${NC}"
if curl -s -f "http://72.60.176.200:8080/health" >/dev/null 2>&1; then
    echo -e "   ✅ DevDeploy environment accessible: ${GREEN}http://72.60.176.200:8080${NC}"
else
    echo -e "   ${YELLOW}⚠️  DevDeploy environment not accessible${NC}"
fi

echo ""

# Context summary
echo -e "${BLUE}📋 Context Summary:${NC}"

# Get last session info
if [[ -f "$MANUS_DIR/reports/current_session_report.md" ]]; then
    last_update=$(stat -c %y "$MANUS_DIR/reports/current_session_report.md" 2>/dev/null | cut -d' ' -f1 || echo "unknown")
    echo -e "   📅 Last session report: ${GREEN}$last_update${NC}"
else
    echo -e "   ${YELLOW}⚠️  No session report found${NC}"
fi

# Get task continuation info
if [[ -f "$MANUS_DIR/TASK_CONTINUATION.md" ]]; then
    task_lines=$(wc -l < "$MANUS_DIR/TASK_CONTINUATION.md" 2>/dev/null || echo "0")
    echo -e "   📋 Task continuation: ${GREEN}$task_lines lines${NC}"
else
    echo -e "   ${YELLOW}⚠️  No task continuation found${NC}"
fi

# Get handoff status
if [[ -f "$MANUS_DIR/handoff/workflow_status.env" ]]; then
    source "$MANUS_DIR/handoff/workflow_status.env" 2>/dev/null || true
    if [[ -n "$WORKFLOW_STATUS" ]]; then
        echo -e "   🔄 Workflow status: ${GREEN}$WORKFLOW_STATUS${NC}"
    fi
fi

echo ""

# Final verification result
if $all_good; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ MANUS CONTEXT VERIFICATION SUCCESSFUL                                   ║${NC}"
    echo -e "${GREEN}║                                                                              ║${NC}"
    echo -e "${GREEN}║  🎯 All required context files are present and accessible                   ║${NC}"
    echo -e "${GREEN}║  🤖 AI-to-AI handoff system is ready                                        ║${NC}"
    echo -e "${GREEN}║  🔗 GitHub connectivity established                                          ║${NC}"
    echo -e "${GREEN}║  📂 Project context successfully loaded                                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    
    echo ""
    echo -e "${BLUE}🚀 Ready to continue development on V1.00D branch${NC}"
    echo -e "${BLUE}💡 Use '.manus/scripts/ai_to_ai_workflow_monitor.sh status' for workflow status${NC}"
    
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ MANUS CONTEXT VERIFICATION FAILED                                       ║${NC}"
    echo -e "${RED}║                                                                              ║${NC}"
    echo -e "${RED}║  Some required context files or connections are missing                     ║${NC}"
    echo -e "${RED}║  Please check the errors above and resolve them                             ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    
    exit 1
fi
