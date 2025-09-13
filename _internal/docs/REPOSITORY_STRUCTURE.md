# 🗂️ Repository Structure - V1.00D

## 📋 Clean Repository Organization

This document outlines the clean, organized structure of the V1.00D branch after comprehensive cleanup and restructuring.

## 🎯 Root Directory (Essential Files Only)

```
landscape-architecture-tool/
├── .coveragerc                 # Test coverage configuration
├── .deepsource.toml           # Code quality analysis
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── Dockerfile                 # Container configuration
├── LICENSE                    # Project license
├── Makefile                   # Build automation
├── README.md                  # Main project documentation
├── docker-compose.yml         # Development environment
├── docker-compose.production.yml  # Production environment
├── docker-compose.n8n.yml     # N8n workflow integration
├── pyproject.toml             # Python project configuration
├── requirements.txt           # Production dependencies
└── requirements-dev.txt       # Development dependencies
```

## 📁 Directory Structure

### 🏗️ Core Application
```
src/                           # Backend source code
├── models/                    # Database models
├── routes/                    # API endpoints
├── services/                  # Business logic
├── utils/                     # Utility functions
│   └── feature_flags.py       # Feature flag system
└── main.py                    # Application entry point

frontend/                      # Frontend React application
├── src/                       # React source code
├── public/                    # Static assets
├── package.json               # Frontend dependencies
└── vite.config.js            # Build configuration
```

### 🔧 Configuration
```
config/                        # Configuration files
├── README.md                  # Configuration documentation
├── gunicorn.conf.py          # Gunicorn server configuration
└── wsgi.py                   # WSGI application entry point
```

### 🛠️ Scripts (Organized by Category)
```
scripts/
├── deployment/               # Deployment automation
│   ├── deploy_v1d_to_devdeploy.sh    # DevDeploy deployment
│   ├── promote_v1d_to_v1.sh          # Production promotion
│   └── README.md                     # Deployment documentation
├── development/              # Development tools
│   ├── ensure_devdeploy_title.sh     # Title enforcement
│   ├── pre_commit_protection.sh      # Branch protection
│   └── manage_titles.sh              # Title management
├── maintenance/              # System maintenance
├── testing/                  # Quality assurance
│   └── quality_gates.py              # Quality validation
└── security/                 # Security management
```

### 📚 Documentation (Structured by Topic)
```
docs/
├── deployment/               # Deployment guides
│   ├── DEPLOYMENT_ISOLATION_GUIDE.md  # Environment isolation
│   └── DEPLOYMENT.md                  # General deployment
├── development/              # Developer documentation
│   ├── DEVELOPMENT_GUIDE.md           # Main development guide
│   └── CONTRIBUTING.md                # Contribution guidelines
├── guides/                   # Step-by-step guides
└── reports/                  # Analysis and status reports
    └── REPOSITORY_RESTRUCTURE_REPORT.md  # Restructure analysis
```

### 🔄 CI/CD & Automation
```
.github/
├── workflows/                # GitHub Actions
│   ├── main-ci.yml          # Main CI pipeline
│   ├── v1-development.yml   # Development workflow
│   ├── v1-deployment.yml    # Deployment workflow
│   └── v1d-devdeploy.yml    # DevDeploy automation
├── copilot-instructions.md   # Main Copilot instructions
├── copilot-instructions-v1d.md  # V1.00D specific instructions
└── BRANCH_PROTECTION_STRATEGY.md  # Protection documentation
```

### 🗄️ Archive & Legacy
```
archive/                      # Historical files
├── legacy-scripts/          # Old automation scripts
├── old-configs/             # Previous configurations
└── deprecated-docs/         # Outdated documentation

packages/                     # Version packages
├── v1.00/                   # Production package
└── v1.00D/                  # Development package
```

### 🧪 Testing
```
tests/                        # Test suite
├── unit/                    # Unit tests
├── integration/             # Integration tests
└── conftest.py              # Test configuration
```

## 🎯 Key Improvements Made

### ✅ Root Directory Cleanup
- **Before**: 14+ loose files cluttering root
- **After**: Only essential configuration and project files
- **Moved**: Documentation, configuration, and utility files to appropriate directories

### ✅ Logical Organization
- **Scripts**: Categorized by purpose (deployment, development, testing, etc.)
- **Documentation**: Structured by audience and topic
- **Configuration**: Centralized in dedicated config/ directory

### ✅ Clear Separation
- **Development**: V1.00D branch with devdeploy automation
- **Production**: V1.00 package with promotion process
- **Archive**: Historical files preserved but organized

## 🔍 File Location Quick Reference

| File Type | Location | Purpose |
|-----------|----------|---------|
| **Core Config** | Root directory | Essential project files |
| **App Config** | `config/` | Runtime configuration |
| **Scripts** | `scripts/{category}/` | Automation by purpose |
| **Documentation** | `docs/{topic}/` | Guides by audience |
| **Workflows** | `.github/workflows/` | CI/CD automation |
| **Legacy Files** | `archive/` | Historical preservation |

## 🚀 Benefits of Clean Structure

### 🎯 Developer Experience
- **Easy Navigation**: Logical file organization
- **Clear Purpose**: Each directory has a specific role
- **Quick Access**: Files grouped by function

### 🛡️ Maintenance
- **Reduced Clutter**: Clean root directory
- **Better Organization**: Related files grouped together
- **Easier Updates**: Clear file locations

### 🔄 Automation
- **Script Categories**: Easy to find automation tools
- **Documentation Structure**: Guides organized by topic
- **Configuration Management**: Centralized settings

## 📋 Usage Guidelines

### 🔍 Finding Files
1. **Configuration**: Check `config/` directory
2. **Scripts**: Look in `scripts/{category}/`
3. **Documentation**: Browse `docs/{topic}/`
4. **Workflows**: Find in `.github/workflows/`

### 📝 Adding New Files
1. **Scripts**: Add to appropriate `scripts/{category}/`
2. **Documentation**: Place in relevant `docs/{topic}/`
3. **Configuration**: Put in `config/` directory
4. **Avoid Root**: Keep root directory clean

### 🧹 Maintenance
1. **Regular Cleanup**: Move loose files to appropriate directories
2. **Archive Old Files**: Use `archive/` for historical files
3. **Update Documentation**: Keep structure docs current

---

**Status**: ✅ **V1.00D Repository Structure Cleaned and Organized**  
**Root Files**: Reduced from 14+ to essential files only  
**Organization**: Logical categorization by purpose and audience  
**Maintenance**: Clear guidelines for ongoing organization
