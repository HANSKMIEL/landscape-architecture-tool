#!/bin/bash

# AI-to-AI Workflow Monitor
# Comprehensive monitoring and management for Manus <-> Copilot handoffs
# Usage: ./ai_to_ai_workflow_monitor.sh [COMMAND] [OPTIONS]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HANDOFF_DIR="$PROJECT_ROOT/.manus/handoff"
REPORTS_DIR="$PROJECT_ROOT/.manus/reports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
AI-to-AI Workflow Monitor

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    monitor [PR] [ISSUE]    Monitor for Copilot completion (default: PR=563, ISSUE=564)
    status                  Show current workflow status
    create-handoff          Create a new handoff assignment
    list-handoffs          List all handoff files
    cleanup                Clean up old handoff files
    verify                 Verify workflow system integrity
    help                   Show this help message

EXAMPLES:
    $0 monitor 563 564     # Monitor PR #563 and Issue #564
    $0 status              # Show current status
    $0 create-handoff      # Interactive handoff creation
    $0 verify              # Verify system integrity

EOF
}

# Monitor for Copilot completion
monitor_completion() {
    local pr_number=${1:-563}
    local issue_number=${2:-564}
    
    log "Starting AI-to-AI workflow monitoring..."
    log "PR: #${pr_number}, Issue: #${issue_number}"
    
    # Run the monitoring script
    if "$SCRIPT_DIR/monitor_copilot_completion.sh" "$pr_number" "$issue_number"; then
        success "Copilot completion detected!"
        
        # Update workflow status
        echo "WORKFLOW_STATUS=COMPLETED" > "$HANDOFF_DIR/workflow_status.env"
        echo "LAST_COMPLETION=$(date)" >> "$HANDOFF_DIR/workflow_status.env"
        echo "COMPLETED_PR=${pr_number}" >> "$HANDOFF_DIR/workflow_status.env"
        echo "COMPLETED_ISSUE=${issue_number}" >> "$HANDOFF_DIR/workflow_status.env"
        
        return 0
    else
        warning "Copilot work still in progress"
        
        # Update workflow status
        echo "WORKFLOW_STATUS=IN_PROGRESS" > "$HANDOFF_DIR/workflow_status.env"
        echo "LAST_CHECK=$(date)" >> "$HANDOFF_DIR/workflow_status.env"
        echo "MONITORING_PR=${pr_number}" >> "$HANDOFF_DIR/workflow_status.env"
        echo "MONITORING_ISSUE=${issue_number}" >> "$HANDOFF_DIR/workflow_status.env"
        
        return 1
    fi
}

# Show workflow status
show_status() {
    log "AI-to-AI Workflow Status"
    echo "========================"
    
    # Check if status file exists
    if [[ -f "$HANDOFF_DIR/workflow_status.env" ]]; then
        source "$HANDOFF_DIR/workflow_status.env"
        
        echo "Status: $WORKFLOW_STATUS"
        
        if [[ "$WORKFLOW_STATUS" == "COMPLETED" ]]; then
            echo "Last Completion: $LAST_COMPLETION"
            echo "Completed PR: #$COMPLETED_PR"
            echo "Completed Issue: #$COMPLETED_ISSUE"
        elif [[ "$WORKFLOW_STATUS" == "IN_PROGRESS" ]]; then
            echo "Last Check: $LAST_CHECK"
            echo "Monitoring PR: #$MONITORING_PR"
            echo "Monitoring Issue: #$MONITORING_ISSUE"
        fi
    else
        echo "Status: UNKNOWN (no status file found)"
    fi
    
    echo ""
    echo "Recent Handoff Files:"
    echo "--------------------"
    if [[ -d "$HANDOFF_DIR" ]]; then
        ls -lt "$HANDOFF_DIR"/*.md 2>/dev/null | head -5 || echo "No handoff files found"
    else
        echo "Handoff directory not found"
    fi
    
    echo ""
    echo "System Health:"
    echo "-------------"
    
    # Check GitHub CLI authentication
    if gh auth status >/dev/null 2>&1; then
        success "GitHub CLI authenticated"
    else
        error "GitHub CLI not authenticated"
    fi
    
    # Check development environment
    if curl -s -f "http://72.60.176.200:8080/health" >/dev/null 2>&1; then
        success "Development environment accessible"
    else
        warning "Development environment not accessible"
    fi
}

# Create new handoff
create_handoff() {
    log "Creating new AI-to-AI handoff..."
    
    # Interactive input
    read -p "Issue title: " issue_title
    read -p "Branch name: " branch_name
    read -p "PR number: " pr_number
    
    if [[ -z "$issue_title" || -z "$branch_name" || -z "$pr_number" ]]; then
        error "All fields are required"
        exit 1
    fi
    
    # Run the handoff script
    if "$SCRIPT_DIR/copilot_handoff.sh" "$issue_title" "$branch_name" "$pr_number"; then
        success "Handoff created successfully"
        
        # Update status
        echo "WORKFLOW_STATUS=HANDOFF_CREATED" > "$HANDOFF_DIR/workflow_status.env"
        echo "HANDOFF_CREATED=$(date)" >> "$HANDOFF_DIR/workflow_status.env"
        echo "HANDOFF_TITLE=$issue_title" >> "$HANDOFF_DIR/workflow_status.env"
        echo "HANDOFF_BRANCH=$branch_name" >> "$HANDOFF_DIR/workflow_status.env"
        echo "HANDOFF_PR=$pr_number" >> "$HANDOFF_DIR/workflow_status.env"
        
        log "Next steps:"
        echo "1. Create GitHub issue with the generated content"
        echo "2. Assign the issue to Copilot"
        echo "3. Monitor for completion using: $0 monitor $pr_number"
    else
        error "Failed to create handoff"
        exit 1
    fi
}

# List handoff files
list_handoffs() {
    log "Handoff Files"
    echo "============="
    
    if [[ -d "$HANDOFF_DIR" ]]; then
        for file in "$HANDOFF_DIR"/*.md; do
            if [[ -f "$file" ]]; then
                local filename=$(basename "$file")
                local size=$(du -h "$file" | cut -f1)
                local date=$(stat -c %y "$file" | cut -d' ' -f1)
                printf "%-50s %8s %12s\n" "$filename" "$size" "$date"
            fi
        done
    else
        warning "Handoff directory not found"
    fi
}

# Cleanup old handoff files
cleanup_handoffs() {
    log "Cleaning up old handoff files..."
    
    if [[ -d "$HANDOFF_DIR" ]]; then
        # Keep only the 10 most recent files of each type
        for pattern in "copilot_context_*.md" "copilot_assignment_*.md"; do
            local files_to_remove=$(ls -t "$HANDOFF_DIR"/$pattern 2>/dev/null | tail -n +11)
            if [[ -n "$files_to_remove" ]]; then
                echo "$files_to_remove" | xargs rm -f
                success "Cleaned up old $pattern files"
            fi
        done
    fi
}

# Verify system integrity
verify_system() {
    log "Verifying AI-to-AI workflow system integrity..."
    
    local errors=0
    
    # Check required directories
    for dir in "$HANDOFF_DIR" "$REPORTS_DIR"; do
        if [[ ! -d "$dir" ]]; then
            error "Required directory missing: $dir"
            ((errors++))
        else
            success "Directory exists: $dir"
        fi
    done
    
    # Check required scripts
    for script in "copilot_handoff.sh" "monitor_copilot_completion.sh"; do
        if [[ ! -f "$SCRIPT_DIR/$script" ]]; then
            error "Required script missing: $script"
            ((errors++))
        elif [[ ! -x "$SCRIPT_DIR/$script" ]]; then
            error "Script not executable: $script"
            ((errors++))
        else
            success "Script available: $script"
        fi
    done
    
    # Check GitHub CLI
    if ! command -v gh >/dev/null 2>&1; then
        error "GitHub CLI not installed"
        ((errors++))
    elif ! gh auth status >/dev/null 2>&1; then
        error "GitHub CLI not authenticated"
        ((errors++))
    else
        success "GitHub CLI ready"
    fi
    
    # Check development environment
    if curl -s -f "http://72.60.176.200:8080/health" >/dev/null 2>&1; then
        success "Development environment accessible"
    else
        warning "Development environment not accessible (may be normal if not deployed)"
    fi
    
    if [[ $errors -eq 0 ]]; then
        success "System verification passed"
        return 0
    else
        error "System verification failed with $errors errors"
        return 1
    fi
}

# Main command dispatcher
main() {
    case "${1:-help}" in
        monitor)
            monitor_completion "$2" "$3"
            ;;
        status)
            show_status
            ;;
        create-handoff)
            create_handoff
            ;;
        list-handoffs)
            list_handoffs
            ;;
        cleanup)
            cleanup_handoffs
            ;;
        verify)
            verify_system
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
