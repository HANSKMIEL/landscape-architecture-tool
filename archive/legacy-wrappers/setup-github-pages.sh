#!/bin/bash

# Legacy Compatibility Wrapper for setup-github-pages.sh
# This script has been moved to archive/legacy-scripts/setup-github-pages.sh

echo "⚠️ DEPRECATION NOTICE:"
echo "The script 'setup-github-pages.sh' has been moved to:"
echo "  archive/legacy-scripts/setup-github-pages.sh"
echo ""
echo "Please update your automation to use the new location."
echo "This wrapper will be removed in a future version."
echo ""

# Check if the archived script exists
if [ -f "archive/legacy-scripts/setup-github-pages.sh" ]; then
    echo "🔄 Forwarding to archived script..."
    exec archive/legacy-scripts/setup-github-pages.sh "$@"
else
    echo "❌ Error: Archived script not found at archive/legacy-scripts/setup-github-pages.sh"
    echo "Please check the repository structure."
    exit 1
fi