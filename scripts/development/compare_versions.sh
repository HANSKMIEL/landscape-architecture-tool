#!/bin/bash
# Version Comparison Script
# Compares V1.00 and V1.00D packages to identify differences

set -e

echo "🔍 Comparing V1.00 vs V1.00D packages..."

# Configuration
V1_00_PATH="packages/v1.00"
V1_00D_PATH="packages/v1.00D"
MAIN_SRC="src"
MAIN_FRONTEND="frontend"
REPORT_FILE="version-comparison-$(date +%Y%m%d_%H%M%S).md"

# Function to count files
count_files() {
    local dir="$1"
    local pattern="$2"
    
    if [ -d "$dir" ]; then
        find "$dir" -name "$pattern" 2>/dev/null | wc -l
    else
        echo "0"
    fi
}

# Function to get directory size
get_dir_size() {
    local dir="$1"
    
    if [ -d "$dir" ]; then
        du -sh "$dir" 2>/dev/null | cut -f1
    else
        echo "0"
    fi
}

# Function to compare directories
compare_directories() {
    local dir1="$1"
    local dir2="$2"
    local name="$3"
    
    echo "📁 Comparing $name..."
    
    if [ ! -d "$dir1" ] || [ ! -d "$dir2" ]; then
        echo "  ⚠️ One or both directories missing"
        return 1
    fi
    
    # File counts
    FILES1=$(find "$dir1" -type f | wc -l)
    FILES2=$(find "$dir2" -type f | wc -l)
    SIZE1=$(get_dir_size "$dir1")
    SIZE2=$(get_dir_size "$dir2")
    
    echo "  📊 Files: $FILES1 vs $FILES2"
    echo "  💾 Size: $SIZE1 vs $SIZE2"
    
    # Check for major differences
    DIFF=$((FILES1 - FILES2))
    if [ $DIFF -lt -10 ] || [ $DIFF -gt 10 ]; then
        echo "  ⚠️ Large file count difference: $DIFF"
        return 1
    elif [ $DIFF -eq 0 ]; then
        echo "  ✅ Identical file counts"
        return 0
    else
        echo "  ℹ️ Minor file count difference: $DIFF"
        return 0
    fi
}

# Function to check for new/missing files
check_file_differences() {
    local dir1="$1"
    local dir2="$2"
    local name="$3"
    
    echo "🔍 Checking file differences in $name..."
    
    if [ ! -d "$dir1" ] || [ ! -d "$dir2" ]; then
        echo "  ⚠️ Cannot compare - directory missing"
        return 1
    fi
    
    # Get relative file lists
    cd "$dir1" && find . -type f | sort > /tmp/files1.txt
    cd - >/dev/null
    cd "$dir2" && find . -type f | sort > /tmp/files2.txt
    cd - >/dev/null
    
    # Find differences
    NEW_FILES=$(comm -13 /tmp/files1.txt /tmp/files2.txt | wc -l)
    REMOVED_FILES=$(comm -23 /tmp/files1.txt /tmp/files2.txt | wc -l)
    
    echo "  📝 New files in $dir2: $NEW_FILES"
    echo "  🗑️ Missing files from $dir1: $REMOVED_FILES"
    
    if [ $NEW_FILES -gt 5 ]; then
        echo "  ⚠️ Many new files detected"
        echo "  New files:"
        comm -13 /tmp/files1.txt /tmp/files2.txt | head -10
        [ $NEW_FILES -gt 10 ] && echo "  ... and $((NEW_FILES - 10)) more"
    fi
    
    if [ $REMOVED_FILES -gt 5 ]; then
        echo "  ⚠️ Many removed files detected"
        echo "  Removed files:"
        comm -23 /tmp/files1.txt /tmp/files2.txt | head -10
        [ $REMOVED_FILES -gt 10 ] && echo "  ... and $((REMOVED_FILES - 10)) more"
    fi
    
    # Cleanup
    rm -f /tmp/files1.txt /tmp/files2.txt
}

# Start comparison report
cat > "$REPORT_FILE" << EOF
# V1.00 vs V1.00D Package Comparison Report

**Generated**: $(date)
**Git Branch**: $(git branch --show-current)
**Git Commit**: $(git rev-parse HEAD)

## Executive Summary

This report compares the V1.00 (protected) and V1.00D (development) packages to identify synchronization status and differences.

## Directory Comparison

EOF

echo ""
echo "📋 Starting comprehensive comparison..."

# Compare backend
echo "Backend Comparison:" >> "$REPORT_FILE"
compare_directories "$V1_00_PATH/backend" "$V1_00D_PATH/backend" "Backend"
echo "" >> "$REPORT_FILE"

# Compare frontend  
echo "Frontend Comparison:" >> "$REPORT_FILE"
compare_directories "$V1_00_PATH/frontend" "$V1_00D_PATH/frontend" "Frontend"
echo "" >> "$REPORT_FILE"

# Compare docs
echo "Documentation Comparison:" >> "$REPORT_FILE"
compare_directories "$V1_00_PATH/docs" "$V1_00D_PATH/docs" "Documentation"
echo "" >> "$REPORT_FILE"

echo ""
echo "🔍 Detailed file analysis..."

# Detailed file differences
echo "## Detailed File Analysis" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

check_file_differences "$V1_00_PATH/backend" "$V1_00D_PATH/backend" "Backend"
check_file_differences "$V1_00_PATH/frontend" "$V1_00D_PATH/frontend" "Frontend"
check_file_differences "$V1_00_PATH/docs" "$V1_00D_PATH/docs" "Documentation"

echo ""
echo "📊 Synchronization analysis..."

# Synchronization with main source
echo "## Synchronization with Main Source" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

if [ -d "$MAIN_SRC" ] && [ -d "$V1_00D_PATH/backend" ]; then
    echo "### Main Source vs V1.00D Sync" >> "$REPORT_FILE"
    
    MAIN_PY_FILES=$(count_files "$MAIN_SRC" "*.py")
    V1D_PY_FILES=$(count_files "$V1_00D_PATH/backend" "*.py")
    
    echo "- Python files in main source: $MAIN_PY_FILES" >> "$REPORT_FILE"
    echo "- Python files in V1.00D: $V1D_PY_FILES" >> "$REPORT_FILE"
    
    PY_DIFF=$((MAIN_PY_FILES - V1D_PY_FILES))
    if [ $PY_DIFF -eq 0 ]; then
        echo "- ✅ Python files perfectly synchronized" >> "$REPORT_FILE"
        echo "✅ Main source and V1.00D perfectly synchronized (Python)"
    elif [ $PY_DIFF -lt -5 ] || [ $PY_DIFF -gt 5 ]; then
        echo "- ⚠️ Significant Python file difference: $PY_DIFF" >> "$REPORT_FILE"
        echo "⚠️ Main source and V1.00D may need synchronization (diff: $PY_DIFF)"
    else
        echo "- ℹ️ Minor Python file difference: $PY_DIFF" >> "$REPORT_FILE"
        echo "ℹ️ Main source and V1.00D reasonably synchronized (diff: $PY_DIFF)"
    fi
fi

if [ -d "$MAIN_FRONTEND" ] && [ -d "$V1_00D_PATH/frontend" ]; then
    echo "" >> "$REPORT_FILE"
    echo "### Frontend Source vs V1.00D Sync" >> "$REPORT_FILE"
    
    MAIN_JS_FILES=$(count_files "$MAIN_FRONTEND/src" "*.jsx") 
    MAIN_JS_FILES=$((MAIN_JS_FILES + $(count_files "$MAIN_FRONTEND/src" "*.js")))
    V1D_JS_FILES=$(count_files "$V1_00D_PATH/frontend/src" "*.jsx")
    V1D_JS_FILES=$((V1D_JS_FILES + $(count_files "$V1_00D_PATH/frontend/src" "*.js")))
    
    echo "- JS/JSX files in main source: $MAIN_JS_FILES" >> "$REPORT_FILE"
    echo "- JS/JSX files in V1.00D: $V1D_JS_FILES" >> "$REPORT_FILE"
    
    JS_DIFF=$((MAIN_JS_FILES - V1D_JS_FILES))
    if [ $JS_DIFF -eq 0 ]; then
        echo "- ✅ Frontend files perfectly synchronized" >> "$REPORT_FILE"
        echo "✅ Main frontend and V1.00D perfectly synchronized"
    elif [ $JS_DIFF -lt -5 ] || [ $JS_DIFF -gt 5 ]; then
        echo "- ⚠️ Significant frontend file difference: $JS_DIFF" >> "$REPORT_FILE"
        echo "⚠️ Main frontend and V1.00D may need synchronization (diff: $JS_DIFF)"
    else
        echo "- ℹ️ Minor frontend file difference: $JS_DIFF" >> "$REPORT_FILE"
        echo "ℹ️ Main frontend and V1.00D reasonably synchronized (diff: $JS_DIFF)"
    fi
fi

echo ""
echo "🏷️ Version information..."

# Version tags and metadata
echo "## Version Information" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "### Git Tags" >> "$REPORT_FILE"
git tag --list | grep -E "^v1\." | tail -5 >> "$REPORT_FILE" 2>/dev/null || echo "No V1.x tags found" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "### Package Metadata" >> "$REPORT_FILE"
if [ -f "$V1_00_PATH/VERSION" ]; then
    echo "**V1.00 Version Info:**" >> "$REPORT_FILE"
    cat "$V1_00_PATH/VERSION" >> "$REPORT_FILE"
else
    echo "V1.00 VERSION file not found" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

if [ -f "$V1_00D_PATH/PACKAGE_INFO" ]; then
    echo "**V1.00D Package Info:**" >> "$REPORT_FILE"
    cat "$V1_00D_PATH/PACKAGE_INFO" >> "$REPORT_FILE"
else
    echo "V1.00D PACKAGE_INFO file not found" >> "$REPORT_FILE"
fi

echo ""
echo "📋 Recommendations..."

# Recommendations
echo "## Recommendations" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check if sync is needed
NEEDS_SYNC=false

if [ -d "$MAIN_SRC" ] && [ -d "$V1_00D_PATH/backend" ]; then
    MAIN_COUNT=$(count_files "$MAIN_SRC" "*.py")
    PACKAGE_COUNT=$(count_files "$V1_00D_PATH/backend" "*.py")
    DIFF=$((MAIN_COUNT - PACKAGE_COUNT))
    
    if [ $DIFF -lt -5 ] || [ $DIFF -gt 5 ]; then
        NEEDS_SYNC=true
    fi
fi

if [ "$NEEDS_SYNC" = "true" ]; then
    echo "### 🔄 Synchronization Recommended" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "V1.00D package appears out of sync with main source. Consider running:" >> "$REPORT_FILE"
    echo "\`\`\`bash" >> "$REPORT_FILE"
    echo "./scripts/sync_packages.sh" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "🔄 Recommendation: Synchronize V1.00D package with main source"
else
    echo "### ✅ Packages Well Synchronized" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "V1.00D package appears reasonably synchronized with main source." >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "✅ Packages appear well synchronized"
fi

# Check if promotion is ready
if [ -f "scripts/update_v1_from_dev.sh" ]; then
    echo "### 🚀 V1.00 Promotion" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "To promote V1.00D changes to V1.00 package:" >> "$REPORT_FILE"
    echo "\`\`\`bash" >> "$REPORT_FILE"
    echo "./scripts/update_v1_from_dev.sh" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Add footer
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "*Report generated by version comparison script*" >> "$REPORT_FILE"
echo "*Repository: $(git remote get-url origin 2>/dev/null || echo 'Local repository')*" >> "$REPORT_FILE"

echo ""
echo "✅ Comparison complete!"
echo "📄 Report saved to: $REPORT_FILE"
echo ""
echo "📋 Quick Summary:"

# Display quick summary
if [ "$NEEDS_SYNC" = "true" ]; then
    echo "  🔄 V1.00D package needs synchronization with main source"
    echo "  📝 Run: ./scripts/sync_packages.sh"
else
    echo "  ✅ V1.00D package is well synchronized"
fi

echo "  📊 V1.00 backend files: $(count_files "$V1_00_PATH/backend" "*.py")"
echo "  📊 V1.00D backend files: $(count_files "$V1_00D_PATH/backend" "*.py")"
echo "  📊 Main source files: $(count_files "$MAIN_SRC" "*.py")"

echo ""
echo "🔗 To view full report: cat $REPORT_FILE"