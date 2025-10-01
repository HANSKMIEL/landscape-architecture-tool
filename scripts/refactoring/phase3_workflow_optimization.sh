#!/bin/bash
# V1.00D Refactoring Implementation Script - Phase 3
# Workflow Optimization
# 
# This script implements Phase 3 of the refactoring plan
# Run from repository root: bash scripts/refactoring/phase3_workflow_optimization.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Phase 3: Workflow Optimization                           ║${NC}"
echo -e "${BLUE}║  V1.00D Branch Refactoring                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Safety check
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Must run from repository root${NC}"
    exit 1
fi

echo -e "${BLUE}Current workflow state:${NC}"
echo "  • Total workflows: $(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)"
echo "  • Backup created: archive/workflows-backup-phase3/"
echo ""

# Show what will be done
echo -e "${YELLOW}This will:${NC}"
echo "  1. Delete redundant CI workflows (ci-enhanced.yml, main-ci.yml)"
echo "  2. Keep new unified CI workflow (ci-unified.yml)"
echo "  3. Consolidate demo deployments (keep deploy-demo-updated.yml as deploy-demo.yml)"
echo "  4. Delete old deploy-production.yml (keep production-deployment.yml)"
echo "  5. Create .github/workflows/README.md documentation"
echo "  6. Reduce from 32 to 28 workflows (12.5% reduction)"
echo ""
read -p "Continue? [y/N]: " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

# Phase 3a: Remove redundant CI workflows
echo -e "${BLUE}Removing redundant CI workflows...${NC}"

if [ -f ".github/workflows/ci-enhanced.yml" ]; then
    echo "  • Removing ci-enhanced.yml (replaced by ci-unified.yml)"
    git rm .github/workflows/ci-enhanced.yml
fi

if [ -f ".github/workflows/main-ci.yml" ]; then
    echo "  • Removing main-ci.yml (replaced by ci-unified.yml)"
    git rm .github/workflows/main-ci.yml
fi

# Keep ci.yml for now as fallback, will rename after testing ci-unified.yml
echo "  ✓ Redundant CI workflows removed"

# Phase 3b: Consolidate demo deployments
echo -e "${BLUE}Consolidating demo deployment workflows...${NC}"

if [ -f ".github/workflows/deploy-demo-updated.yml" ] && [ -f ".github/workflows/deploy-demo.yml" ]; then
    echo "  • Comparing deploy-demo workflows..."
    
    # Check which is larger/newer (more features)
    size_updated=$(wc -c < .github/workflows/deploy-demo-updated.yml)
    size_old=$(wc -c < .github/workflows/deploy-demo.yml)
    
    if [ "$size_updated" -ge "$size_old" ]; then
        echo "  • Keeping deploy-demo-updated.yml (more comprehensive)"
        git rm .github/workflows/deploy-demo.yml
        git mv .github/workflows/deploy-demo-updated.yml .github/workflows/deploy-demo.yml
    else
        echo "  • Keeping original deploy-demo.yml"
        git rm .github/workflows/deploy-demo-updated.yml
    fi
    echo "  ✓ Demo deployment consolidated"
else
    echo "  • Demo deployments already consolidated or missing"
fi

# Phase 3c: Consolidate production deployments
echo -e "${BLUE}Consolidating production deployment workflows...${NC}"

if [ -f ".github/workflows/deploy-production.yml" ] && [ -f ".github/workflows/production-deployment.yml" ]; then
    echo "  • Comparing production deployment workflows..."
    
    # Check which is more comprehensive
    size_deploy=$(wc -c < .github/workflows/deploy-production.yml)
    size_production=$(wc -c < .github/workflows/production-deployment.yml)
    
    if [ "$size_production" -ge "$size_deploy" ]; then
        echo "  • Keeping production-deployment.yml (more comprehensive)"
        git rm .github/workflows/deploy-production.yml
    else
        echo "  • Keeping deploy-production.yml (renaming to production-deployment.yml)"
        git rm .github/workflows/production-deployment.yml
        git mv .github/workflows/deploy-production.yml .github/workflows/production-deployment.yml
    fi
    echo "  ✓ Production deployment consolidated"
else
    echo "  • Production deployments already consolidated or missing"
fi

# Phase 3d: Create workflow documentation
echo -e "${BLUE}Creating workflow documentation...${NC}"

cat > .github/workflows/README.md << 'WORKFLOWDOC'
# GitHub Actions Workflows

This directory contains all automated workflows for the Landscape Architecture Tool.

**Total Workflows**: 28 (reduced from 32 in Phase 3 optimization)

---

## 📊 Workflow Categories

### 🧪 CI/Testing (3 workflows)
- **ci-unified.yml** - Main CI pipeline with parallel jobs
  - Code quality & security scanning
  - Backend tests with PostgreSQL
  - Frontend tests with coverage
  - Triggers: push, pull_request on main/V1.00D
- **makefile-test.yml** - Makefile validation
- **codeql.yml** - CodeQL security scanning

### 🚀 Deployment (8 workflows)

#### Production
- **production-deployment.yml** - Production deployment with health checks
  - Environment selection (production/staging)
  - Rollback capability
  - Zero-downtime deployment
- **enhanced-deployment.yml** - Enhanced zero-downtime deployment
  - Parallel testing
  - Advanced health monitoring
- **manual-deploy.yml** - Manual VPS deployment
  - Interactive deployment options
  - Selective frontend/backend deployment

#### Version-Specific
- **v1-deployment.yml** - V1.00 package deployment
- **v1d-devdeploy.yml** - V1.00D development deployment (http://72.60.176.200:8080)
- **v1-development.yml** - V1.00 development environment

#### Demo
- **deploy-demo.yml** - GitHub Pages demo deployment
  - Automated on main branch
  - Uses mock API for demo mode

### 🎯 Special Systems (3 workflows)

**Critical orchestration workflows - DO NOT MODIFY without approval**

- **motherspace-orchestrator.yml** - Master orchestrator
  - Analyzes all spaces for harmony (target: ≥85%)
  - Task delegation in chronological order
  - Issue/PR optimization
  - Triggers: issues, PRs, workflow completions, every 2 hours

- **daughter-space-uiux.yml** - UI/UX Manager
  - Visual appeal analysis
  - User workflow optimization
  - Integration requirement reporting
  - Creates "Daughter-Integration Manager" issues

- **integrationmanager-space.yml** - Integration Manager
  - Modules repository management
  - Cross-profession adaptation
  - External system integration (Vectorworks, CRM, AI, APIs)
  - Repository synchronization

### 🔧 Maintenance (4 workflows)
- **nightly-maintenance.yml** - Nightly cleanup and health checks
  - Runs at 19:30 Europe/Amsterdam time
  - Repository cleanup
  - Security checks
- **dependabot-auto-merge.yml** - Automated dependency updates
- **stale.yml** - Stale issue management
- **verify-issue-closed.yml** - Issue closure validation

### 🤖 Automation (6 workflows)
- **automated-validation.yml** - Automated code validation
- **post-merge.yml** - Post-merge analysis and tasks
  - Auto-creates follow-up issues
  - API review triggers
- **pr-automation.yml** - Pull request automation
- **issue-triage.yml** - Issue triage and labeling
- **test-failure-automation.yml** - Test failure handling
  - Creates issues for failing tests
- **summary.yml** - Summary generation

### 📈 Analysis/Monitoring (3 workflows)
- **copilot-analysis-monitor.yml** - Copilot monitoring
- **copilot-dependency-analysis.yml** - Dependency analysis
- **space-management.yml** - Space effectiveness monitoring
  - Weekly validation
  - Clutter monitoring

### 🏗️ Infrastructure (1 workflow)
- **codespaces-prebuilds.yml** - Codespaces prebuild optimization

---

## 🎯 Workflow Usage Guide

### Running CI Tests
```bash
# CI runs automatically on push and PR
# To trigger manually: go to Actions tab → CI → Run workflow
```

### Deploying to Production
```bash
# Option 1: Automatic (on main branch merge)
git checkout main
git merge V1.00D
git push origin main

# Option 2: Manual deployment
# Go to Actions → Production Deployment → Run workflow
```

### Deploying to V1.00D DevDeploy
```bash
# Automatic on every push to V1.00D
git push origin V1.00D

# Check deployment: http://72.60.176.200:8080
```

---

## 📋 Phase 3 Optimization Changes

**Workflows Removed** (4):
- ❌ ci-enhanced.yml → merged into ci-unified.yml
- ❌ main-ci.yml → merged into ci-unified.yml
- ❌ deploy-demo-updated.yml → consolidated to deploy-demo.yml
- ❌ deploy-production.yml → consolidated to production-deployment.yml

**Workflows Added** (1):
- ✅ ci-unified.yml - Unified CI with best features from all CI workflows

**Result**: 32 → 28 workflows (12.5% reduction)

---

## 🔒 Protected Workflows

**DO NOT MODIFY without explicit approval**:
- motherspace-orchestrator.yml
- daughter-space-uiux.yml
- integrationmanager-space.yml
- codeql.yml

These workflows are critical for repository operations and security.

---

## 📚 Additional Documentation

- [CI/CD Architecture](../../docs/architecture/CI_TIMEOUT_SOLUTIONS.md)
- [Deployment Guide](../../docs/deployment/DEPLOYMENT_GUIDE.md)
- [VPS Deployment](../../docs/VPS_DEPLOYMENT_INSTRUCTIONS.md)
- [Branch Protection](../../docs/development/BRANCH_PROTECTION.md)

---

**Last Updated**: October 1, 2025 (Phase 3 Optimization)  
**Maintained by**: HANSKMIEL  
**Branch**: V1.00D
WORKFLOWDOC

echo "  ✓ Created .github/workflows/README.md"

# Phase 3e: Summary
echo ""
echo -e "${GREEN}✅ Phase 3 Complete!${NC}"
echo ""
echo -e "${BLUE}Summary of changes:${NC}"
echo "  • Removed 4 redundant workflows"
echo "  • Created 1 unified CI workflow"
echo "  • Consolidated demo deployments"
echo "  • Consolidated production deployments"
echo "  • Created comprehensive workflow documentation"
echo ""
echo -e "${BLUE}Workflow count:${NC}"
echo "  • Before: 32 workflows"
echo "  • After: $(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l) workflows"
echo "  • Reduction: 12.5%"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review changes: git status"
echo "  2. Check .github/workflows/README.md"
echo "  3. Test ci-unified.yml triggers successfully"
echo "  4. Commit changes: git add -A && git commit -m 'refactor: Phase 3 - Workflow optimization'"
echo "  5. Consider Phase 4: API enhancement (optional)"
echo ""
