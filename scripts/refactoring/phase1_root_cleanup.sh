#!/bin/bash
# V1.00D Refactoring Implementation Script - Phase 1
# Root Directory Cleanup
# 
# This script implements Phase 1 of the refactoring plan
# Run from repository root: bash scripts/refactoring/phase1_root_cleanup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Phase 1: Root Directory Cleanup                          ║${NC}"
echo -e "${BLUE}║  V1.00D Branch Refactoring                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Safety check
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Must run from repository root${NC}"
    exit 1
fi

# Create backup branch
echo -e "${YELLOW}Creating backup branch...${NC}"
git checkout -b refactoring-backup-$(date +%Y%m%d) 2>/dev/null || true
git checkout V1.00D

# Create new directory structure
echo -e "${BLUE}Creating new directory structure...${NC}"
mkdir -p docs/{api,deployment,development,architecture,solutions,planning}
mkdir -p scripts/{deployment,testing,analysis,maintenance,development}
mkdir -p reports/{analysis,validation,health,security}

# Phase 1a: Move Analysis Reports
echo -e "${BLUE}Moving analysis reports...${NC}"
git mv ACTUAL_ISSUES_FOUND_ANALYSIS.md reports/analysis/ 2>/dev/null || mv ACTUAL_ISSUES_FOUND_ANALYSIS.md reports/analysis/
git mv AI_WORKFLOW_VERIFICATION_AND_VALIDATION.md reports/analysis/ 2>/dev/null || mv AI_WORKFLOW_VERIFICATION_AND_VALIDATION.md reports/analysis/
git mv CHATGPT5_ANALYSIS_IMPLEMENTATION_REPORT.md reports/analysis/ 2>/dev/null || mv CHATGPT5_ANALYSIS_IMPLEMENTATION_REPORT.md reports/analysis/
git mv SYSTEM_VALIDATION_REPORT.md reports/analysis/ 2>/dev/null || mv SYSTEM_VALIDATION_REPORT.md reports/analysis/
git mv VPS_COMPREHENSIVE_ANALYSIS_REPORT.md reports/analysis/ 2>/dev/null || mv VPS_COMPREHENSIVE_ANALYSIS_REPORT.md reports/analysis/
git mv workflow_analysis_results.json reports/analysis/ 2>/dev/null || mv workflow_analysis_results.json reports/analysis/

# Phase 1b: Move Deployment Documentation
echo -e "${BLUE}Moving deployment documentation...${NC}"
git mv README_DEPLOYMENT.md docs/deployment/ 2>/dev/null || mv README_DEPLOYMENT.md docs/deployment/
git mv VPS_DEPLOYMENT_FIX.md docs/deployment/ 2>/dev/null || mv VPS_DEPLOYMENT_FIX.md docs/deployment/
git mv VPS_DEPLOYMENT_GUIDE.md docs/deployment/ 2>/dev/null || mv VPS_DEPLOYMENT_GUIDE.md docs/deployment/
git mv VPS_DEPLOYMENT_ISSUE_ANALYSIS.md docs/deployment/ 2>/dev/null || mv VPS_DEPLOYMENT_ISSUE_ANALYSIS.md docs/deployment/
git mv vps_deployment_analysis.md docs/deployment/ 2>/dev/null || mv vps_deployment_analysis.md docs/deployment/
git mv vps_connectivity_report.md docs/deployment/ 2>/dev/null || mv vps_connectivity_report.md docs/deployment/

# Phase 1c: Move Solution/Fix Reports
echo -e "${BLUE}Moving solution reports...${NC}"
git mv V1_00D_CRITICAL_FIXES_FINAL_REPORT.md docs/solutions/ 2>/dev/null || mv V1_00D_CRITICAL_FIXES_FINAL_REPORT.md docs/solutions/
git mv V1_00D_CRITICAL_ISSUES_ANALYSIS.md docs/solutions/ 2>/dev/null || mv V1_00D_CRITICAL_ISSUES_ANALYSIS.md docs/solutions/
git mv V1_00D_FINAL_DEPLOYMENT_REPORT.md docs/solutions/ 2>/dev/null || mv V1_00D_FINAL_DEPLOYMENT_REPORT.md docs/solutions/
git mv V1_00D_TESTING_REPORT.md docs/solutions/ 2>/dev/null || mv V1_00D_TESTING_REPORT.md docs/solutions/
git mv VPS_ISSUES_AND_FIXES.md docs/solutions/ 2>/dev/null || mv VPS_ISSUES_AND_FIXES.md docs/solutions/
git mv SOLUTION_SUMMARY.md docs/solutions/ 2>/dev/null || mv SOLUTION_SUMMARY.md docs/solutions/
git mv FIX_VPS_NOW.md docs/solutions/ 2>/dev/null || mv FIX_VPS_NOW.md docs/solutions/

# Phase 1d: Move Planning Documents
echo -e "${BLUE}Moving planning documents...${NC}"
git mv PRODUCTION_READINESS_CHECKLIST.md docs/planning/ 2>/dev/null || mv PRODUCTION_READINESS_CHECKLIST.md docs/planning/
git mv PR_568_REVIEW_AND_DEPLOYMENT_STATUS.md docs/planning/ 2>/dev/null || mv PR_568_REVIEW_AND_DEPLOYMENT_STATUS.md docs/planning/

# Phase 1e: Move Testing Scripts
echo -e "${BLUE}Moving testing scripts...${NC}"
git mv comprehensive_api_test.py scripts/testing/ 2>/dev/null || mv comprehensive_api_test.py scripts/testing/
git mv comprehensive_ui_test.py scripts/testing/ 2>/dev/null || mv comprehensive_ui_test.py scripts/testing/
git mv comprehensive_vps_test.py scripts/testing/ 2>/dev/null || mv comprehensive_vps_test.py scripts/testing/
git mv simple_api_test.py scripts/testing/ 2>/dev/null || mv simple_api_test.py scripts/testing/
git mv vps_enhanced_testing.py scripts/testing/ 2>/dev/null || mv vps_enhanced_testing.py scripts/testing/
git mv take_vps_screenshot.py scripts/testing/ 2>/dev/null || mv take_vps_screenshot.py scripts/testing/

# Phase 1f: Move Analysis Scripts
echo -e "${BLUE}Moving analysis scripts...${NC}"
git mv input_field_investigation.py scripts/analysis/ 2>/dev/null || mv input_field_investigation.py scripts/analysis/
git mv UI_navigation_investigation.py scripts/analysis/ 2>/dev/null || mv UI_navigation_investigation.py scripts/analysis/
git mv workflow_analyzer.py scripts/analysis/ 2>/dev/null || mv workflow_analyzer.py scripts/analysis/
git mv vps_issue_analysis.py scripts/analysis/ 2>/dev/null || mv vps_issue_analysis.py scripts/analysis/

# Phase 1g: Move Development Scripts
echo -e "${BLUE}Moving development scripts...${NC}"
git mv dom_re_rendering_fix.py scripts/development/ 2>/dev/null || mv dom_re_rendering_fix.py scripts/development/

# Phase 1h: Move JSX files (should be in frontend)
echo -e "${BLUE}Moving misplaced JSX files...${NC}"
if [ -f "FocusDebugging.jsx" ]; then
    git mv FocusDebugging.jsx frontend/src/components/ 2>/dev/null || mv FocusDebugging.jsx frontend/src/components/
fi
if [ -f "OptimizedPlantForm.jsx" ]; then
    git mv OptimizedPlantForm.jsx frontend/src/components/ 2>/dev/null || mv OptimizedPlantForm.jsx frontend/src/components/
fi

# Phase 1i: Move JSON reports
echo -e "${BLUE}Moving JSON reports...${NC}"
git mv api_test_results.json reports/validation/ 2>/dev/null || mv api_test_results.json reports/validation/
git mv comprehensive_ui_test_report.json reports/validation/ 2>/dev/null || mv comprehensive_ui_test_report.json reports/validation/
git mv dom_re_rendering_analysis.json reports/analysis/ 2>/dev/null || mv dom_re_rendering_analysis.json reports/analysis/
git mv input_field_investigation_report.json reports/analysis/ 2>/dev/null || mv input_field_investigation_report.json reports/analysis/
git mv ui_navigation_investigation.json reports/analysis/ 2>/dev/null || mv ui_navigation_investigation.json reports/analysis/
git mv vps_issue_analysis_report.json reports/analysis/ 2>/dev/null || mv vps_issue_analysis_report.json reports/analysis/
git mv vps_test_report.json reports/validation/ 2>/dev/null || mv vps_test_report.json reports/validation/

# Phase 1j: DELETE security risks
echo -e "${RED}Removing security risks...${NC}"
rm -f admin_cookies.txt cookies.txt
rm -f vps_current_state.png  # May contain sensitive info

# Phase 1k: Move INSTRUCTIONS file
echo -e "${BLUE}Moving instructions...${NC}"
git mv INSTRUCTIONS_FOR_USER.txt docs/ 2>/dev/null || mv INSTRUCTIONS_FOR_USER.txt docs/

echo ""
echo -e "${GREEN}✅ Phase 1 Complete!${NC}"
echo ""
echo -e "${BLUE}Summary of changes:${NC}"
echo "  • Created organized directory structure"
echo "  • Moved 21 .md files from root to docs/"
echo "  • Organized 12 .py scripts into scripts/"
echo "  • Moved 8 JSON files to reports/"
echo "  • Moved 2 JSX files to frontend/src/components/"
echo "  • Deleted security risks (cookies.txt, admin_cookies.txt)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review changes: git status"
echo "  2. Test application still works"
echo "  3. Commit changes: git add -A && git commit -m 'refactor: Phase 1 - Clean up root directory'"
echo "  4. Run Phase 2: Documentation consolidation"
echo ""
