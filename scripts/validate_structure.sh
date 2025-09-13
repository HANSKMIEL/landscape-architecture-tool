#!/bin/bash
# Repository Structure Validation Script
# Validates the V1.00+ repository organization and structure

set -e

echo "🔍 Validating V1.00+ repository structure..."

# Configuration
ERRORS=0
WARNINGS=0

# Function to check directory exists
check_directory() {
    local dir="$1"
    local description="$2"
    local required="$3"
    
    if [ -d "$dir" ]; then
        echo "✅ $description: $dir"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo "❌ $description missing: $dir"
            ((ERRORS++))
            return 1
        else
            echo "⚠️ $description not found: $dir"
            ((WARNINGS++))
            return 1
        fi
    fi
}

# Function to check file exists
check_file() {
    local file="$1"
    local description="$2"
    local required="$3"
    
    if [ -f "$file" ]; then
        echo "✅ $description: $file"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo "❌ $description missing: $file"
            ((ERRORS++))
            return 1
        else
            echo "⚠️ $description not found: $file"
            ((WARNINGS++))
            return 1
        fi
    fi
}

# Function to check no legacy files in root
check_no_legacy() {
    local pattern="$1"
    local description="$2"
    
    if ls $pattern 2>/dev/null >/dev/null; then
        echo "⚠️ Legacy $description found in root directory:"
        ls $pattern
        ((WARNINGS++))
        return 1
    else
        echo "✅ No legacy $description in root"
        return 0
    fi
}

echo ""
echo "📋 Checking core repository structure..."

# Main source directories
check_directory "src" "Main backend source" "true"
check_directory "frontend" "Main frontend source" "true"
check_directory "docs" "Main documentation" "true"
check_directory "tests" "Test suite" "true"
check_directory "scripts" "Automation scripts" "true"

echo ""
echo "📦 Checking package structure..."

# Package directories
check_directory "packages" "Packages directory" "true"
check_directory "packages/v1.00" "V1.00 protected package" "true"
check_directory "packages/v1.00D" "V1.00D development package" "true"

# V1.00 package structure
check_directory "packages/v1.00/backend" "V1.00 backend" "true"
check_directory "packages/v1.00/frontend" "V1.00 frontend" "true"
check_directory "packages/v1.00/docs" "V1.00 docs" "true"
check_directory "packages/v1.00/deploy" "V1.00 deploy" "false"

# V1.00D package structure  
check_directory "packages/v1.00D/backend" "V1.00D backend" "true"
check_directory "packages/v1.00D/frontend" "V1.00D frontend" "true"
check_directory "packages/v1.00D/docs" "V1.00D docs" "true"
check_directory "packages/v1.00D/deploy" "V1.00D deploy" "false"

echo ""
echo "📁 Checking archive organization..."

# Archive structure
check_directory "archive" "Archive directory" "true"
check_directory "archive/deployment" "Deployment archives" "false"
check_directory "archive/vps-config" "VPS config archives" "false"
check_directory "archive/legacy-scripts" "Legacy script archives" "false"

echo ""
echo "🔧 Checking DevOps structure..."

# DevOps directories
check_directory "DEV_OPS_STEPS" "DevOps documentation" "true"
check_directory "DEV_OPS_STEPS/DEV_OPS_COPILOT" "DevOps Copilot instructions" "true"

echo ""
echo "📄 Checking essential files..."

# Essential files
check_file "README.md" "Main README" "true"
check_file "requirements.txt" "Python requirements" "true"
check_file "Makefile" "Build automation" "true"
check_file "pyproject.toml" "Python project config" "true"
check_file ".gitignore" "Git ignore rules" "true"

# Package documentation
check_file "packages/README.md" "Package documentation" "true"
check_file "archive/README.md" "Archive documentation" "true"

# DevOps files
check_file "DEV_OPS_STEPS/UNIFIED_DEVELOPMENT_GUIDE.md" "Unified development guide" "true"
check_file "DEV_OPS_STEPS/DEV_OPS_COPILOT/COPILOT_INSTRUCTIONS_V1_POSTreporeorganisation.md" "Post-reorganization Copilot instructions" "true"

# Automation scripts
check_file "scripts/update_v1_from_dev.sh" "V1.00 promotion script" "true"
check_file "scripts/sync_packages.sh" "Package sync script" "true"
check_file "scripts/setup_github_pages.sh" "GitHub Pages setup" "true"

echo ""
echo "🚫 Checking for legacy files in root..."

# Check no legacy files in root
check_no_legacy "*.conf" "config files"
check_no_legacy "*.service" "service files"
check_no_legacy "*deploy*.sh" "deployment scripts"
check_no_legacy "*vps*.sh" "VPS scripts"
check_no_legacy "*vps*.md" "VPS documentation"
check_no_legacy "cookies.txt" "cookie files"
check_no_legacy "*.tar.gz" "archive files"

echo ""
echo "🔗 Checking workflow files..."

# GitHub workflows
check_file ".github/workflows/v1-development.yml" "V1.00D development workflow" "true"
check_file ".github/workflows/v1-deployment.yml" "V1.00 deployment workflow" "true"

echo ""
echo "📊 Checking file counts..."

# File count validation
if [ -d "src" ] && [ -d "packages/v1.00D/backend" ]; then
    MAIN_FILES=$(find src -name "*.py" | wc -l)
    PACKAGE_FILES=$(find packages/v1.00D/backend -name "*.py" | wc -l)
    echo "🐍 Python files - Main: $MAIN_FILES, V1.00D: $PACKAGE_FILES"
    
    DIFF=$((MAIN_FILES - PACKAGE_FILES))
    if [ $DIFF -lt -10 ] || [ $DIFF -gt 10 ]; then
        echo "⚠️ Large file count discrepancy detected (diff: $DIFF)"
        ((WARNINGS++))
    else
        echo "✅ File counts reasonably aligned"
    fi
fi

if [ -d "frontend" ] && [ -d "packages/v1.00D/frontend" ]; then
    MAIN_JS_FILES=$(find frontend/src -name "*.jsx" -o -name "*.js" | wc -l)
    PACKAGE_JS_FILES=$(find packages/v1.00D/frontend/src -name "*.jsx" -o -name "*.js" 2>/dev/null | wc -l)
    echo "⚛️ JS/JSX files - Main: $MAIN_JS_FILES, V1.00D: $PACKAGE_JS_FILES"
    
    DIFF=$((MAIN_JS_FILES - PACKAGE_JS_FILES))
    if [ $DIFF -lt -10 ] || [ $DIFF -gt 10 ]; then
        echo "⚠️ Large frontend file count discrepancy detected (diff: $DIFF)"
        ((WARNINGS++))
    else
        echo "✅ Frontend file counts reasonably aligned"
    fi
fi

echo ""
echo "🏷️ Checking version tags..."

# Check for V1.00 tag
if git tag --list | grep -q "^v1\.00$"; then
    echo "✅ V1.00 tag exists"
else
    echo "⚠️ V1.00 tag not found"
    ((WARNINGS++))
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "🌿 Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" = "v1.00D" ]; then
    echo "✅ On V1.00D development branch"
elif [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo "ℹ️ On main branch"
else
    echo "ℹ️ On feature branch: $CURRENT_BRANCH"
fi

echo ""
echo "📋 Validation Summary"
echo "=================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 Perfect! Repository structure fully compliant with V1.00+ organization"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "✅ Repository structure valid with $WARNINGS warnings"
    echo "⚠️ Warnings should be addressed but don't block development"
    exit 0
else
    echo "❌ Repository structure has $ERRORS errors and $WARNINGS warnings"
    echo "🛠️ Errors must be fixed for proper V1.00+ operation"
    exit 1
fi