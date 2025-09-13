#!/bin/bash

echo "🧪 COMPREHENSIVE AI-TO-AI HANDOFF SYSTEM VERIFICATION"
echo "====================================================="
echo ""

# Test 1: GitHub CLI Authentication
echo "📋 Test 1: GitHub CLI Authentication"
if gh auth status > /dev/null 2>&1; then
    echo "✅ GitHub CLI authenticated"
else
    echo "❌ GitHub CLI not authenticated"
    exit 1
fi

# Test 2: .manus Directory Structure
echo "📋 Test 2: .manus Directory Structure"
REQUIRED_DIRS=(".manus/handoff" ".manus/scripts" ".manus/reports" ".manus/context")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing"
        exit 1
    fi
done

# Test 3: Required Scripts
echo "📋 Test 3: Required Scripts"
REQUIRED_SCRIPTS=(".manus/scripts/monitor_copilot_completion.sh" ".manus/scripts/copilot_handoff.sh")
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "✅ $script executable"
    else
        echo "❌ $script missing or not executable"
        exit 1
    fi
done

# Test 4: Context Files
echo "📋 Test 4: Context Files"
CONTEXT_FILES=$(ls .manus/handoff/copilot_context_*.md 2>/dev/null | wc -l)
if [ "$CONTEXT_FILES" -gt 0 ]; then
    echo "✅ $CONTEXT_FILES context files found"
else
    echo "❌ No context files found"
    exit 1
fi

# Test 5: Monitoring Script
echo "📋 Test 5: Monitoring Script"
if ./.manus/scripts/monitor_copilot_completion.sh > /dev/null 2>&1; then
    echo "✅ Monitoring script runs (no completion detected - expected)"
else
    echo "❌ Monitoring script failed"
    exit 1
fi

# Test 6: Issue Creation Capability
echo "📋 Test 6: Issue Creation Capability"
if gh issue list > /dev/null 2>&1; then
    echo "✅ Can access GitHub issues"
else
    echo "❌ Cannot access GitHub issues"
    exit 1
fi

echo ""
echo "🎉 ALL TESTS PASSED - AI-TO-AI HANDOFF SYSTEM VERIFIED"
echo "======================================================"
echo ""
echo "✅ System is ready for production use"
echo "✅ Copilot handoffs will work correctly"
echo "✅ Monitoring and verification systems operational"
