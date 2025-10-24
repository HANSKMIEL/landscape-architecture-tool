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
