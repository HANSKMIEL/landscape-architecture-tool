# Unified Development Guide - V1.00 Post-Reorganization

This document consolidates all development steps, procedures, and guidelines for the Landscape Architecture Tool V1.00+ organized repository.

## 🏗️ Repository Structure Overview

The repository has been reorganized for V1.00+ with clear separation between production and development code:

### Key Directories
```
landscape-architecture-tool/
├── src/                 # 🎯 Main backend source (V1.00D development)
├── frontend/            # 🎯 Main frontend source (V1.00D development)  
├── docs/                # 🎯 Main documentation (V1.00D development)
├── packages/            # 📦 Version packages
│   ├── v1.00/          # 🛡️ Protected production release
│   └── v1.00D/         # 🚧 Development package (auto-synced)
├── archive/            # 📁 Legacy files (pre-V1.00)
├── DEV_OPS_STEPS/      # 🔧 DevOps documentation
└── scripts/            # 🛠️ Automation scripts
```

## 🚀 Quick Start Guide

### 1. Initial Setup
```bash
# Clone and setup
git clone <repository>
cd landscape-architecture-tool
git checkout v1.00D  # Development branch

# Install dependencies
make install

# Verify setup
make backend-test
make frontend-test
```

### 2. Daily Development Workflow
```bash
# Work in main source directories
cd src/           # Backend development
cd frontend/      # Frontend development
cd docs/         # Documentation updates

# Test your changes
make backend-test
make lint
make frontend-test

# Commit changes
git add .
git commit -m "Feature: description"
git push origin v1.00D
```

### 3. Promote to Production
```bash
# When ready to update V1.00
./scripts/update_v1_from_dev.sh

# Deploy to production
cd packages/v1.00/deploy
./deploy.sh
```

## 📋 Development Procedures

### Adding New Features

#### Backend Features
1. **Create service layer**:
   ```python
   # File: src/services/new_feature_service.py
   from src.services.base_service import BaseService
   
   class NewFeatureService(BaseService):
       def create_feature(self, data):
           # Implementation
           pass
   ```

2. **Create API route**:
   ```python
   # File: src/routes/new_feature.py
   from flask import Blueprint
   from src.services.new_feature_service import NewFeatureService
   
   new_feature_bp = Blueprint('new_feature', __name__)
   
   @new_feature_bp.route('/api/v1/features', methods=['POST'])
   def create_feature():
       # Implementation
       pass
   ```

3. **Add tests**:
   ```python
   # File: tests/routes/test_new_feature.py
   def test_create_feature(client, db_session):
       # Test implementation
       pass
   ```

#### Frontend Features
1. **Create component**:
   ```javascript
   // File: frontend/src/components/NewFeature.jsx
   import React from 'react';
   
   export const NewFeature = () => {
       return <div>New Feature</div>;
   };
   ```

2. **Add to router**:
   ```javascript
   // File: frontend/src/App.jsx
   import { NewFeature } from './components/NewFeature';
   // Add route configuration
   ```

3. **Add tests**:
   ```javascript
   // File: frontend/src/components/__tests__/NewFeature.test.jsx
   import { render } from '@testing-library/react';
   import { NewFeature } from '../NewFeature';
   // Test implementation
   ```

### Database Changes
1. **Create migration**:
   ```bash
   PYTHONPATH=. flask --app src.main db migrate -m "Add new feature table"
   ```

2. **Update models**:
   ```python
   # File: src/models/landscape.py
   class NewFeatureModel(db.Model):
       # Model definition
       pass
   ```

3. **Test migration**:
   ```bash
   PYTHONPATH=. flask --app src.main db upgrade
   make backend-test
   ```

### Documentation Updates
1. **API documentation**:
   ```markdown
   # File: docs/API/new-feature.md
   ## New Feature API
   
   ### POST /api/v1/features
   Description of endpoint
   ```

2. **User guides**:
   ```markdown
   # File: docs/user-guides/new-feature.md
   ## How to Use New Feature
   Step-by-step guide
   ```

## 🧪 Testing Procedures

### Backend Testing
```bash
# Full test suite
make backend-test

# Specific test file
PYTHONPATH=. python -m pytest tests/routes/test_new_feature.py -v

# Coverage report
PYTHONPATH=. python -m pytest tests/ --cov=src --cov-report=html
```

### Frontend Testing
```bash
# Frontend tests
cd frontend && npm run test:vitest:run

# Watch mode for development
cd frontend && npm run test:vitest:watch

# E2E tests (if available)
cd frontend && npm run test:e2e
```

### Integration Testing
```bash
# Start backend
PYTHONPATH=. python src/main.py &

# Start frontend
cd frontend && npm run dev &

# Manual testing
curl http://localhost:5000/health
curl http://localhost:5174/
```

### Package Testing
```bash
# Test V1.00 package before deployment
cd packages/v1.00
../../scripts/test_package.sh

# Compare V1.00 vs V1.00D
./scripts/compare_versions.sh
```

## 🔄 CI/CD Procedures

### Branch Management
- **v1.00D**: Main development branch
- **feature/***: Feature development branches
- **hotfix/***: Critical fixes
- **main**: Points to latest V1.00 release

### Pipeline Stages
1. **Development CI** (on v1.00D push):
   ```yaml
   - Install dependencies
   - Run linting
   - Run backend tests
   - Run frontend tests
   - Security scanning
   ```

2. **Package Validation** (before promotion):
   ```bash
   ./scripts/update_v1_from_dev.sh
   # Includes automated testing
   ```

3. **Production Deployment** (V1.00 package):
   ```bash
   cd packages/v1.00/deploy
   ./deploy.sh
   ```

### Automation Scripts
```bash
# Update V1.00 from development
./scripts/update_v1_from_dev.sh

# Sync packages
./scripts/sync_packages.sh

# Validate repository structure
./scripts/validate_structure.sh

# Deploy specific version
./scripts/deploy_v1.sh
```

## 🛠️ Build Procedures

### Frontend Build
```bash
cd frontend
npm ci --legacy-peer-deps
npm run build
```

### Backend Setup
```bash
pip install -r requirements.txt
PYTHONPATH=. flask --app src.main db upgrade
```

### Docker Build (if available)
```bash
docker compose up --build
```

### Production Package Build
```bash
# Automatic via promotion script
./scripts/update_v1_from_dev.sh

# Manual package creation
./scripts/create_package.sh v1.00
```

## 🚀 Deployment Procedures

### Development Deployment
```bash
# Start development servers
PYTHONPATH=. python src/main.py  # Backend on :5000
cd frontend && npm run dev        # Frontend on :5174
```

### Production Deployment
```bash
# Deploy V1.00 package
cd packages/v1.00/deploy
./deploy.sh

# Verify deployment
curl http://your-domain.com/health
```

### GitHub Pages Setup
```bash
# Setup GitHub Pages for V1.00
./scripts/setup_github_pages.sh

# Build static site
cd packages/v1.00/frontend
npm run build

# Deploy to Pages
git subtree push --prefix packages/v1.00/frontend/dist origin gh-pages
```

## 🔧 Configuration Management

### Environment Variables
```bash
# Development (.env.development)
DATABASE_URL=sqlite:///development.db
DEBUG=true
FLASK_ENV=development

# Production (.env.production)
DATABASE_URL=postgresql://user:pass@host:port/db
DEBUG=false
FLASK_ENV=production
```

### Configuration Files
- **Frontend**: `frontend/vite.config.js`
- **Backend**: `src/config.py`
- **Database**: `migrations/`
- **Docker**: `docker-compose.yml`

## 🐛 Debugging Procedures

### Backend Debugging
```bash
# Debug mode
DEBUG=true PYTHONPATH=. python src/main.py

# Database debug
PYTHONPATH=. flask --app src.main shell

# Log analysis
tail -f logs/application.log
```

### Frontend Debugging
```bash
# Development mode with debugging
cd frontend && npm run dev

# Browser console
# Check Network tab for API calls
# Use React Developer Tools
```

### Package Debugging
```bash
# Compare packages
./scripts/compare_versions.sh

# Check package integrity
./scripts/check_package_integrity.sh

# Validate structure
./scripts/validate_structure.sh
```

## 📊 Monitoring Procedures

### Health Checks
```bash
# Application health
curl http://localhost:5000/health

# Database health
PYTHONPATH=. python -c "from src.main import app; app.test_client().get('/health')"

# Package health
./scripts/check_package_integrity.sh
```

### Performance Monitoring
```bash
# Backend performance
PYTHONPATH=. python scripts/performance_monitor.py

# Frontend performance
cd frontend && npm run analyze

# Database performance
PYTHONPATH=. python scripts/db_performance.py
```

## 🔐 Security Procedures

### Security Scanning
```bash
# Python security
bandit -r src/

# Dependency security
safety check

# Frontend security
cd frontend && npm audit
```

### Access Control
- **V1.00 package**: Read-only except via promotion script
- **Development**: Standard development access
- **Production**: Limited deployment access

## 📝 Documentation Procedures

### Documentation Types
1. **API Documentation**: `docs/API/`
2. **User Guides**: `docs/user-guides/`
3. **Development Guides**: `docs/development/`
4. **Architecture**: `docs/architecture/`

### Documentation Updates
```bash
# Update documentation
vim docs/development/new-feature.md

# Generate API docs (if automated)
./scripts/generate_api_docs.sh

# Validate documentation
./scripts/validate_docs.sh
```

## 🤝 Collaboration Procedures

### Code Review Process
1. Create feature branch from v1.00D
2. Develop and test changes
3. Create pull request to v1.00D
4. Code review and approval
5. Merge to v1.00D
6. Promote to V1.00 when ready

### Communication
- **Development updates**: v1.00D progress
- **Production releases**: V1.00 promotions
- **Emergency changes**: Hotfix communications

## 🚨 Emergency Procedures

### Rollback Procedures
```bash
# Rollback V1.00 to previous version
git tag --list | grep v1.00
git checkout v1.00.YYYYMMDDHHMM
cp -r packages/v1.00 backups/emergency/

# Restore from backup
cp -r backups/v1.00_LATEST packages/v1.00
```

### Hotfix Procedures
```bash
# Create hotfix branch
git checkout -b hotfix/critical-fix v1.00D

# Make critical changes
# ... fix implementation ...

# Fast-track to V1.00
./scripts/hotfix_promote.sh

# Emergency deployment
cd packages/v1.00/deploy && ./deploy.sh
```

### Recovery Procedures
```bash
# Recover development environment
git checkout v1.00D
make clean && make install

# Recover packages
./scripts/sync_packages.sh

# Validate everything
./scripts/validate_structure.sh
make backend-test
```

## 📈 Optimization Procedures

### Performance Optimization
1. **Backend**: Database query optimization, caching
2. **Frontend**: Bundle optimization, lazy loading
3. **Package**: Minimize package size

### Build Optimization
```bash
# Optimize frontend build
cd frontend && npm run build -- --analyze

# Optimize backend
./scripts/optimize_backend.sh

# Package optimization
./scripts/optimize_packages.sh
```

---

## 🎯 Quick Reference Commands

### Daily Commands
```bash
git checkout v1.00D                    # Switch to development
make backend-test                      # Test backend
make frontend-test                     # Test frontend
./scripts/update_v1_from_dev.sh       # Promote to V1.00
```

### Emergency Commands
```bash
cp -r backups/v1.00_LATEST packages/v1.00  # Emergency rollback
./scripts/validate_structure.sh             # Validate repository
./scripts/compare_versions.sh               # Compare versions
```

### Deployment Commands
```bash
cd packages/v1.00/deploy && ./deploy.sh    # Deploy V1.00
./scripts/setup_github_pages.sh            # Setup Pages
curl http://localhost:5000/health          # Health check
```

This guide provides comprehensive procedures for all aspects of V1.00+ development. Always refer to this guide for consistent development practices.