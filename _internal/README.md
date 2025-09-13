# 🗂️ Internal Directory Structure

This `_internal/` directory contains all non-essential files that were moved from the root directory to create a clean, professional repository structure.

## 📋 Directory Organization

### 📚 `docs/` - All Documentation
Contains all documentation files that were previously scattered across multiple directories:

```
docs/
├── deployment/          # Deployment guides and instructions
├── development/         # Developer documentation and guides
├── guides/             # Step-by-step guides
├── reports/            # Analysis and status reports
└── REPOSITORY_STRUCTURE.md  # Repository structure documentation
```

### 🔧 `operations/` - Operational Files
Contains operational files and logs that are needed but clutter the root:

```
operations/
├── deployment_logs/    # Deployment logs and history
├── screenshots/        # Application screenshots
├── secrets/           # Secret management files
└── fixes/             # Quick fixes and patches
```

### 🐳 `docker/` - Docker Configurations
Contains specialized Docker configurations:

```
docker/
├── docker-compose.n8n.yml        # N8n workflow integration
└── docker-compose.production.yml  # Production environment
```

### 🏗️ `build/` - Build Configuration
Contains build-related configuration files:

```
build/
├── requirements-dev.in  # Development dependencies input
└── requirements.in      # Production dependencies input
```

### 🔄 `n8n-workflows/` - Workflow Automation
Contains N8n workflow definitions and automation scripts.

### 📄 `documentation/` - Legacy Documentation
Contains any legacy documentation that needs to be preserved.

## 🎯 Purpose of This Structure

### ✅ **Clean Root Directory**
- Only essential project files remain in root
- Professional appearance for new developers
- Easy navigation and onboarding

### ✅ **Organized Internal Files**
- All supporting files logically organized
- Easy to find when needed
- Preserved but not cluttering

### ✅ **Maintainable Structure**
- Clear separation of concerns
- Scalable organization
- Easy to add new files in appropriate locations

## 🔍 Finding Files

### Common File Locations

| File Type | Location | Example |
|-----------|----------|---------|
| **Documentation** | `_internal/docs/` | Deployment guides, dev docs |
| **Logs** | `_internal/operations/deployment_logs/` | Deployment history |
| **Screenshots** | `_internal/operations/screenshots/` | App screenshots |
| **Docker Configs** | `_internal/docker/` | Specialized compose files |
| **Build Files** | `_internal/build/` | Requirements input files |
| **Workflows** | `_internal/n8n-workflows/` | Automation workflows |

### Quick Access Commands

```bash
# View documentation
ls _internal/docs/

# Check deployment logs
ls _internal/operations/deployment_logs/

# Find Docker configurations
ls _internal/docker/

# Access build files
ls _internal/build/
```

## 📋 Root Directory (Clean)

The root directory now contains only essential project files:

```
landscape-architecture-tool/
├── README.md              # Main project documentation
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── docker-compose.yml     # Main development environment
├── Dockerfile            # Container configuration
├── Makefile              # Build automation
├── pyproject.toml        # Python project configuration
├── LICENSE               # Project license
├── src/                  # Backend source code
├── frontend/             # Frontend React application
├── tests/                # Test suite
├── scripts/              # Automation scripts
├── config/               # Configuration files
├── migrations/           # Database migrations
├── instance/             # Runtime instance data
├── archive/              # Historical files
└── _internal/            # All supporting files (this directory)
```

## 🚀 Benefits

### 🎯 **Professional Appearance**
- Clean, uncluttered root directory
- Industry-standard structure
- Easy for new team members to understand

### 🔍 **Easy Navigation**
- Essential files immediately visible
- Supporting files logically organized
- Clear separation of concerns

### 🛠️ **Maintainable**
- Easy to add new files in appropriate locations
- Scalable structure for project growth
- Clear guidelines for file placement

---

**Last Updated**: September 13, 2025  
**Purpose**: Clean repository structure with organized internal files  
**Root Items**: Reduced from 32 to 17 essential items
