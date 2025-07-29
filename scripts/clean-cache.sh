#!/bin/bash

# Clean script for landscape architecture tool
# Removes Python cache files and compiled bytecode

echo "🧹 Cleaning Python cache files..."

# Remove __pycache__ directories
echo "Removing __pycache__ directories..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove .pyc files
echo "Removing .pyc files..."
find . -name "*.pyc" -delete 2>/dev/null || true

# Remove .pyo files
echo "Removing .pyo files..."
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove other Python cache files
echo "Removing other Python cache files..."
find . -name "*.pyd" -delete 2>/dev/null || true

# Clean pytest cache
echo "Removing pytest cache..."
rm -rf .pytest_cache/ 2>/dev/null || true

# Clean coverage files
echo "Removing coverage files..."
rm -rf htmlcov/ 2>/dev/null || true
rm -f .coverage 2>/dev/null || true

echo "✅ Python cache cleanup completed!"
echo ""
echo "This cleanup is especially important after:"
echo "  • Changes to performance/cache modules"
echo "  • Import structure modifications"
echo "  • Module refactoring"
echo ""
echo "For Docker builds after cache changes, use:"
echo "  docker build --no-cache -t landscape-architecture-tool ."