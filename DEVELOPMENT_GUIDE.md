# 🌿 Landscape Architecture Tool - Development Guide

## 📋 Overview

This guide consolidates all development steps and procedures for the Landscape Architecture Tool V1.00 and V1.00D development workflow.

## 🏗️ Repository Structure

### Production vs Development
- **V1.00**: Production-ready package in `packages/v1.00/`
- **V1.00D**: Development package in `packages/v1.00D/`
- **Main Source**: Active development in root `src/` and `frontend/`

### Directory Organization
```
landscape-architecture-tool/
├── packages/
│   ├── v1.00/          # Production package
│   └── v1.00D/         # Development package
├── src/                # Main backend source
├── frontend/           # Main frontend source
├── archive/            # Legacy files and backups
├── DEV_OPS_STEPS/      # DevOps documentation
├── scripts/            # Automation scripts
└── docs/               # Documentation
```

## 🔄 Development Workflow

### 1. Development Process
1. **Work on main source** (`src/`, `frontend/`)
2. **Test thoroughly** using V1.00D branch workflows
3. **Sync to V1.00D package** when ready
4. **Promote to V1.00** using promotion script

### 2. Branch Strategy
- **main**: Stable production branch
- **V1.00D**: Development branch with workflow fixes
- **Feature branches**: For specific features/fixes

### 3. Testing Requirements
- All tests must pass before promotion
- Frontend: `npm run test:run`
- Backend: `make backend-test`
- Security scans: Automated in CI/CD

## 🚀 Deployment Process

### VPS Deployment (Current Production)
- **URL**: https://optura.nl
- **Backend**: Flask + Gunicorn on port 5000
- **Frontend**: React SPA served via Nginx
- **Database**: SQLite production database

### GitHub Pages Deployment
- **V1.00 package** can be deployed to GitHub Pages
- **Workflow**: `.github/workflows/v1-deployment.yml`
- **Manual trigger** with confirmation required

## 🔧 Scripts and Automation

### Key Scripts
- `scripts/update_v1_from_dev.sh`: Promote V1.00D → V1.00
- `quality_gates.py`: Code quality validation
- `wsgi.py`: Production WSGI entry point

### CI/CD Workflows
- **main-ci.yml**: Main branch testing
- **v1-development.yml**: V1.00D development testing
- **v1-deployment.yml**: V1.00 package deployment

## 📦 Package Management

### V1.00D Development Package
- **Purpose**: Development and testing
- **Updates**: Synced from main source
- **Testing**: Full CI/CD pipeline

### V1.00 Production Package
- **Purpose**: Stable production releases
- **Updates**: Only via promotion script
- **Protection**: Isolated from development changes

## 🛡️ Security and Quality

### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **Bandit**: Security scanning

### Testing Strategy
- **Unit Tests**: Vitest for frontend, pytest for backend
- **Integration Tests**: Full application testing
- **Security Tests**: Automated vulnerability scanning

## 🔍 Monitoring and Maintenance

### Health Checks
- **Endpoint**: `/health` (internal), `/api/health` (external)
- **Status**: Monitors database, dependencies, services
- **Alerts**: Automated failure detection

### Performance Monitoring
- **Cache Performance**: Redis-based caching
- **Database**: SQLite with optimization
- **Frontend**: React with lazy loading

## 📚 Documentation Structure

### Core Documentation
- `README.md`: Project overview and quick start
- `DEVELOPMENT_GUIDE.md`: This comprehensive guide
- `DEPLOYMENT.md`: Deployment procedures
- `CONTRIBUTING.md`: Contribution guidelines

### DevOps Documentation
- `DEV_OPS_STEPS/`: Complete DevOps procedures
- `DEV_OPS_STEPS/DEV_OPS_COPILOT/`: Copilot instructions
- `docs/`: Technical documentation

## 🎯 Issue #553 Implementation Status

### ✅ Completed
1. **Repository Protection**: V1.00 package isolated
2. **Repository Cleanup**: Legacy files archived
3. **Version Management**: V1.00/V1.00D structure
4. **DevOps Instructions**: Comprehensive documentation
5. **Promotion Script**: Manual trigger for updates
6. **CI/CD Updates**: All pipelines target V1.00D

### 🔄 Ongoing
- **Issues/PRs Cleanup**: Regular maintenance
- **Documentation Updates**: Continuous improvement
- **Performance Optimization**: Ongoing monitoring

## 🚨 Critical Fixes Applied

### Workflow Compatibility
- **Node.js**: Updated to version 20 for React 19.x
- **Test Scripts**: Fixed naming consistency
- **Security Reports**: Proper directory structure
- **Nginx Configuration**: Health endpoint routing

### Repository Organization
- **Legacy Scripts**: Moved to `archive/legacy-scripts/`
- **Documentation**: Consolidated and organized
- **Package Structure**: Clear V1.00/V1.00D separation

## 🎮 Quick Commands

### Development
```bash
# Start development
npm run dev                    # Frontend development server
python src/main.py            # Backend development server

# Testing
npm run test:run              # Frontend tests
make backend-test             # Backend tests

# Promotion
./scripts/update_v1_from_dev.sh  # Promote V1.00D → V1.00
```

### Deployment
```bash
# VPS deployment (manual)
# See DEPLOYMENT.md for detailed instructions

# GitHub Pages deployment
# Use GitHub Actions workflow with manual trigger
```

## 📞 Support and Maintenance

### Regular Tasks
1. **Weekly**: Review and close obsolete issues/PRs
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Performance review and optimization

### Emergency Procedures
1. **Production Issues**: Check VPS health endpoint
2. **CI/CD Failures**: Review workflow logs
3. **Security Alerts**: Immediate patch and deployment

---

**Last Updated**: September 13, 2025  
**Version**: V1.00D Post-Reorganization  
**Status**: ✅ Complete Implementation of Issue #553
