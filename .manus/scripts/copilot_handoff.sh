#!/bin/bash

# 🤖 Manus to GitHub Copilot Handoff Automation Script
# ====================================================
# This script automates the handoff process for "analyze and fix" tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 MANUS TO COPILOT HANDOFF AUTOMATION${NC}"
echo "========================================"
echo ""

# Check if task description is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Task description required${NC}"
    echo "Usage: $0 \"Task description for Copilot\""
    echo "Example: $0 \"Analyze and fix error handling in Login component\""
    exit 1
fi

TASK_DESCRIPTION="$1"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
HANDOFF_DIR=".manus/handoff"
ASSIGNMENT_FILE="$HANDOFF_DIR/copilot_assignment_$TIMESTAMP.md"

echo -e "${YELLOW}📋 Task: $TASK_DESCRIPTION${NC}"
echo ""

# Step 1: Generate Copilot Context
echo -e "${BLUE}📋 Step 1: Generating Copilot Context${NC}"
echo "====================================="
./.manus/handoff_to_copilot.sh

# Get the latest context file
CONTEXT_FILE=$(ls -t $HANDOFF_DIR/copilot_context_*.md | head -1)
echo -e "${GREEN}✅ Context generated: $CONTEXT_FILE${NC}"
echo ""

# Step 2: Create Copilot Assignment
echo -e "${BLUE}📋 Step 2: Creating Copilot Assignment${NC}"
echo "======================================"

cat > "$ASSIGNMENT_FILE" << EOF
# 🤖 GitHub Copilot (GPT-5) Assignment

**Generated**: $(date)  
**Source**: Manus Development Session  
**Task ID**: COPILOT_$TIMESTAMP  

## 📋 **Assignment Details**

### **Task**: $TASK_DESCRIPTION

### **🎯 Objective**
- Analyze the identified issue/component thoroughly
- Implement comprehensive fixes following established patterns
- Create a Pull Request within V1.00D branch
- Follow all development patterns and guidelines from context

### **🔧 Requirements**
- Work exclusively on V1.00D branch (NEVER main)
- Maintain devdeploy environment isolation
- Follow API error handling patterns provided in context
- Test all changes thoroughly before PR creation
- Create descriptive PR with detailed changelog
- Use provided testing commands for verification

### **📋 Deliverables**
1. **Feature Branch**: Create from V1.00D with descriptive name
2. **Implementation**: Comprehensive solution following patterns
3. **Testing**: Verify with provided curl commands and build process
4. **Pull Request**: Ready for Manus review with detailed description
5. **Documentation**: Update relevant docs if needed

### **🚨 Critical Constraints**
- ❌ NEVER touch main branch or production environment
- ✅ Maintain "devdeploy" title branding in development
- ✅ Follow auto-push protocol (push after every commit)
- ✅ Use provided API patterns and testing commands
- ✅ Test in devdeploy environment (http://72.60.176.200:8080)
- ✅ Ensure all changes work with existing authentication

### **📂 Complete Project Context**

EOF

# Append the context file content
echo "$(cat "$CONTEXT_FILE")" >> "$ASSIGNMENT_FILE"

cat >> "$ASSIGNMENT_FILE" << EOF

## 🎯 **Next Steps for Copilot**

1. **Read Context**: Understand the complete project state above
2. **Create Branch**: \`git checkout -b feature/fix-$TIMESTAMP\` from V1.00D
3. **Implement Solution**: Follow the patterns and guidelines provided
4. **Test Thoroughly**: Use the testing commands and verify in devdeploy
5. **Create PR**: Submit for Manus review with detailed description
6. **Notify Manus**: Comment on this assignment when PR is ready

## 🔍 **Testing Verification Required**

Before creating PR, verify:
- [ ] Frontend builds successfully: \`npm run build\`
- [ ] Backend health check: \`curl http://72.60.176.200:8080/health\`
- [ ] DevDeploy title present: \`curl http://72.60.176.200:8080 | grep "devdeploy"\`
- [ ] API endpoints working: Use provided curl commands
- [ ] No console errors in browser developer tools

## 📊 **Success Criteria**

- ✅ Issue/component analyzed and understood
- ✅ Comprehensive fix implemented
- ✅ All tests passing
- ✅ DevDeploy environment working
- ✅ PR created with detailed description
- ✅ Ready for Manus review and deployment

---

**Assignment Status**: 🟡 **Pending Copilot Action**  
**Priority**: 🔥 **High**  
**Expected Completion**: Within 2-4 hours  

**Manus will review and deploy upon PR completion.**
EOF

echo -e "${GREEN}✅ Assignment created: $ASSIGNMENT_FILE${NC}"
echo ""

# Step 3: Display handoff instructions
echo -e "${BLUE}📋 Step 3: Handoff Instructions${NC}"
echo "================================"
echo ""
echo -e "${YELLOW}🤖 FOR GITHUB COPILOT (GPT-5):${NC}"
echo "1. 📁 Open: $ASSIGNMENT_FILE"
echo "2. 📋 Copy the entire assignment content"
echo "3. 🤖 Paste to GitHub Copilot with instruction: 'Use GPT-5 model'"
echo "4. 🚀 Let Copilot complete the task and create PR"
echo ""
echo -e "${YELLOW}📋 FOR MANUS (WHEN NOTIFIED):${NC}"
echo "1. 🔍 Review PR: \`gh pr list --base V1.00D\`"
echo "2. 🧪 Test changes: \`gh pr checkout [PR_NUMBER]\`"
echo "3. 🚀 Deploy if approved: \`./.manus/scripts/deployment/deploy_v1d_to_devdeploy.sh\`"
echo "4. 📊 Update documentation with results"
echo ""

# Step 4: Update session report
echo -e "${BLUE}📋 Step 4: Updating Session Report${NC}"
echo "=================================="
echo ""
echo "✅ Copilot Handoff: $TASK_DESCRIPTION - Assignment created at $TIMESTAMP" >> .manus/reports/current_session_report.md
echo "📂 Assignment File: $ASSIGNMENT_FILE" >> .manus/reports/current_session_report.md
echo "🎯 Status: Pending Copilot completion" >> .manus/reports/current_session_report.md
echo "" >> .manus/reports/current_session_report.md

echo -e "${GREEN}✅ Session report updated${NC}"
echo ""

# Step 5: Commit and push
echo -e "${BLUE}📋 Step 5: Committing Handoff Documentation${NC}"
echo "============================================="
git add .manus/
git commit -m "🤖 Copilot handoff: $TASK_DESCRIPTION

📋 Assignment: $ASSIGNMENT_FILE
🎯 Task: $TASK_DESCRIPTION
⏰ Created: $TIMESTAMP
🔄 Status: Pending Copilot completion

Automated handoff process initiated for analysis and fix task."

git push origin V1.00D

echo -e "${GREEN}✅ Handoff documentation committed and pushed${NC}"
echo ""

echo -e "${GREEN}🎉 COPILOT HANDOFF COMPLETE!${NC}"
echo "=========================="
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "- ✅ Context generated and ready"
echo "- ✅ Assignment created with full details"
echo "- ✅ Instructions provided for both Copilot and Manus"
echo "- ✅ Session documentation updated"
echo "- ✅ All changes committed and pushed"
echo ""
echo -e "${YELLOW}🎯 Next: Hand assignment to GitHub Copilot (GPT-5)${NC}"
echo -e "${YELLOW}📂 Assignment file: $ASSIGNMENT_FILE${NC}"
echo ""
echo -e "${BLUE}🔔 Manus will be notified when Copilot completes the PR${NC}"
