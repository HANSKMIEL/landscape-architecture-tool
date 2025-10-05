#!/bin/bash

# Legacy Compatibility Wrapper for complete_vps_deployment.sh
# This script has been moved to archive/deployment/complete_vps_deployment.sh

echo "⚠️ DEPRECATION NOTICE:"
echo "The script 'complete_vps_deployment.sh' has been moved to:"
echo "  archive/deployment/complete_vps_deployment.sh"
echo ""
echo "Please update your automation to use the new location."
echo "This wrapper will be removed in a future version."
echo ""

# Check if the archived script exists
if [ -f "archive/deployment/complete_vps_deployment.sh" ]; then
    echo "🔄 Forwarding to archived script..."
    exec archive/deployment/complete_vps_deployment.sh "$@"
else
    echo "❌ Error: Archived script not found at archive/deployment/complete_vps_deployment.sh"
    echo "Please check the repository structure."
    exit 1
fi