#!/bin/bash

# Legacy Compatibility Wrapper for deploy-production.sh
# This script has been moved to archive/deployment/deploy-production.sh

echo "⚠️ DEPRECATION NOTICE:"
echo "The script 'deploy-production.sh' has been moved to:"
echo "  archive/deployment/deploy-production.sh"
echo ""
echo "Please update your automation to use the new location."
echo "This wrapper will be removed in a future version."
echo ""

# Check if the archived script exists
if [ -f "archive/deployment/deploy-production.sh" ]; then
    echo "🔄 Forwarding to archived script..."
    exec archive/deployment/deploy-production.sh "$@"
else
    echo "❌ Error: Archived script not found at archive/deployment/deploy-production.sh"
    echo "Please check the repository structure."
    exit 1
fi