# 🌿 Landscape Architecture Tool

A comprehensive web application for managing landscape architecture projects, suppliers, plants, products, and clients.

**Production**: 🚀 https://optura.nl  
**Development**: 🔧 http://72.60.176.200:8080 (devdeploy)  
**Status**: ✅ V1.00D Clean Structure Complete

## 🚀 Quick Start

### Development
```bash
git clone <repository-url>
cd landscape-architecture-tool
git checkout V1.00D

# Install and run
make install
make build
make backend-test

# Start development servers
PYTHONPATH=. python src/main.py          # Backend (port 5000)
cd frontend && npm run dev                # Frontend (port 5174)
```

### Production Deployment
```bash
# Deploy V1.00D to development environment
./scripts/deployment/deploy_v1d_to_devdeploy.sh

# Promote to production when ready
./scripts/deployment/promote_v1d_to_v1.sh
```

## 📁 Repository Structure

**Ultra-Clean Root Directory** - Only essential project files:

```
landscape-architecture-tool/
├── README.md              # Main project documentation
├── src/                   # Backend Python/Flask source code
├── frontend/              # Frontend React application
├── tests/                 # Test suite
├── scripts/               # Automation and deployment scripts
├── config/                # Configuration files
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── docker-compose.yml     # Development environment
├── Dockerfile            # Container configuration
├── Makefile              # Build automation
├── pyproject.toml        # Python project configuration
├── LICENSE               # Project license
├── migrations/           # Database migrations
├── instance/             # Runtime instance data
├── archive/              # Historical files and legacy code
└── _internal/            # Supporting files (docs, logs, configs)
```

**All documentation, logs, and supporting files** are organized in `_internal/` to maintain a clean root directory.

## 🛡️ Branch Protection

### Main Branch (Protected)
- ❌ **NO direct commits** - Production protected
- ✅ **Only promoted changes** via promotion script
- 🌐 **Production URL**: https://optura.nl

### V1.00D Branch (Development)
- ✅ **All development work** happens here
- 🔄 **Automatic devdeploy** on every push
- 🌐 **Development URL**: http://72.60.176.200:8080
- 🏷️ **Title**: "devdeploy - Landscape Architecture Tool (Development)"

## 🔧 Key Features

### Backend (Python/Flask)
- **RESTful API** for all business operations
- **SQLAlchemy ORM** with SQLite database
- **Authentication & Authorization** system
- **Comprehensive Testing** with pytest
- **Feature Flags** for safe development

### Frontend (React/Vite)
- **Modern React** with hooks and context
- **Responsive Design** with Tailwind CSS
- **Component Library** with shadcn/ui
- **Real-time Updates** and data synchronization
- **Multi-language Support** (Dutch/English)

### DevOps & Automation
- **GitHub Actions** CI/CD pipelines
- **Docker** containerization
- **Automated Testing** and quality gates
- **Environment Isolation** (development/production)
- **Deployment Scripts** for VPS deployment

## 🎯 Development Workflow

### Safe Development Pattern
```bash
# 1. Work on V1.00D branch
git checkout V1.00D
git pull origin V1.00D

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Develop with automatic devdeploy title
./scripts/development/ensure_devdeploy_title.sh

# 4. Test in isolated environment
./scripts/deployment/deploy_v1d_to_devdeploy.sh

# 5. Merge to V1.00D when ready
git checkout V1.00D
git merge feature/your-feature
git push origin V1.00D  # Triggers automatic devdeploy

# 6. Promote to production when stable
./scripts/deployment/promote_v1d_to_v1.sh
```

## 🧪 Testing

### Backend Tests
```bash
make backend-test                    # Run all backend tests
PYTHONPATH=. python -m pytest tests/unit/     # Unit tests only
PYTHONPATH=. python -m pytest tests/integration/  # Integration tests
```

### Frontend Tests
```bash
cd frontend
npm run test:run                     # Run all frontend tests
npm run test:watch                   # Watch mode for development
```

### Full Application Test
```bash
make test                           # Run complete test suite
```

## 🔍 Environment Verification

### Development Environment
```bash
curl -s http://72.60.176.200:8080 | grep "devdeploy"  # Should show devdeploy title
curl -s http://72.60.176.200:8080/health              # Health check
```

### Production Environment
```bash
curl -s https://optura.nl | grep "<title>"            # Should show professional title
curl -s https://optura.nl/api/health                  # Health check
```

## 📚 Documentation

All comprehensive documentation is organized in `_internal/docs/`:

- **Deployment Guides**: `_internal/docs/deployment/`
- **Development Docs**: `_internal/docs/development/`
- **Step-by-step Guides**: `_internal/docs/guides/`
- **Analysis Reports**: `_internal/docs/reports/`

## 🛠️ Scripts

Automation scripts are organized by category in `scripts/`:

- **Deployment**: `scripts/deployment/` - DevDeploy and promotion
- **Development**: `scripts/development/` - Development tools
- **Testing**: `scripts/testing/` - Quality assurance
- **Maintenance**: `scripts/maintenance/` - System maintenance
- **Security**: `scripts/security/` - Security management

## 🐳 Docker

### Development
```bash
docker-compose up --build           # Full development environment
```

### Production
```bash
docker-compose -f _internal/docker/docker-compose.production.yml up
```

### N8n Integration
```bash
docker-compose -f _internal/docker/docker-compose.n8n.yml up
```

## 🔧 Configuration

Configuration files are centralized in `config/`:

- `config/gunicorn.conf.py` - Production server configuration
- `config/wsgi.py` - WSGI application entry point
- `.env.example` - Environment variables template

## 🚨 Emergency Procedures

### Reset Development Environment
```bash
git checkout V1.00D
git reset --hard origin/V1.00D
./scripts/deployment/deploy_v1d_to_devdeploy.sh
```

### Production Issues
```bash
# Check production status
curl -s https://optura.nl/health

# Production is protected - use promotion process only
./scripts/deployment/promote_v1d_to_v1.sh
```

## 📊 Project Status

### ✅ Completed Features
- Complete repository restructure and cleanup
- Environment isolation (development/production)
- Automated devdeploy deployment
- Branch protection and feature flags
- Comprehensive testing suite
- Professional documentation structure

### 🔄 Current Development
- Feature development on V1.00D branch
- Continuous integration improvements
- Performance optimizations
- User experience enhancements

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch from V1.00D
3. **Develop** using the devdeploy environment
4. **Test** thoroughly in isolation
5. **Submit** a pull request to V1.00D branch

See `_internal/docs/development/CONTRIBUTING.md` for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Last Updated**: September 13, 2025  
**Repository Structure**: ✅ Ultra-Clean (17 root items)  
**Environment Isolation**: ✅ Complete  
**Development Workflow**: ✅ Protected and Automated

<- Text input fields now properly accept full text instead of single Deployment trigger: Thu Sep 25 05:49:46 EDT 2025 -->
