# Requirements Files Guide

This guide explains the purpose and usage of all requirements files in the landscape architecture tool repository.

## 📋 Overview

The project uses a **pip-tools workflow** with `.in` source files and compiled `.txt` lock files for reproducible builds and dependency management.

## 🎯 Which File Should I Use?

### For Developers
```bash
pip install -r requirements-dev.txt
```
**Use Case**: Local development, testing, linting, code quality checks
**Contains**: All production dependencies + development tools (pytest, black, flake8, etc.)

### For Production Deployment  
```bash
pip install -r requirements.txt
```
**Use Case**: Production deployments, Docker containers, minimal installations
**Contains**: Only production dependencies (Flask, database drivers, etc.)

### For CI/CD Pipelines
```bash
pip install -r requirements-dev.txt
```
**Use Case**: GitHub Actions, automated testing, code quality checks
**Contains**: Everything needed for comprehensive testing and validation

### For Users
Users should use the provided Docker setup or GitHub Codespaces - dependencies are handled automatically.

## 📁 File Structure & Purpose

### Core Requirements Files

| File | Purpose | Generated From | Lines | Usage |
|------|---------|----------------|--------|--------|
| `requirements.txt` | Production dependencies | `requirements.in` | 282 | Production, Docker |
| `requirements-dev.txt` | Development dependencies | `requirements-dev.in` | 499 | Development, CI/CD |
| `requirements.in` | Production source | Manual edit | 49 | Source for requirements.txt |
| `requirements-dev.in` | Development source | Manual edit | 40 | Source for requirements-dev.txt |

### Management Tools

| File | Purpose |
|------|---------|
| `scripts/compile_requirements.sh` | Compiles .in files to .txt with retry logic |

## 🔄 Dependency Management Workflow

### Adding New Dependencies

1. **For production dependencies**: Edit `requirements.in`
2. **For development dependencies**: Edit `requirements-dev.in`  
3. **Compile the changes**:
   ```bash
   # Compile production dependencies
   ./scripts/compile_requirements.sh requirements.in
   
   # Compile development dependencies  
   ./scripts/compile_requirements.sh requirements-dev.in
   ```
4. **Commit both .in and .txt files**

### Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
./scripts/compile_requirements.sh requirements.in --upgrade
./scripts/compile_requirements.sh requirements-dev.in --upgrade
```

## 📊 Dependency Analysis

### Production Dependencies (requirements.txt)
- **Core Flask application**: Flask, Flask-Migrate, Flask-SQLAlchemy, Flask-CORS, Flask-WTF, Flask-Limiter
- **Database drivers**: psycopg2-binary, redis, SQLAlchemy  
- **Production server**: gunicorn, waitress
- **HTTP and API**: httpx, requests
- **Data validation**: pydantic, email-validator
- **AI/ML integration**: openai
- **OneDrive integration**: msal, msgraph-core, azure-identity, azure-storage-file-datalake
- **PDF generation**: reportlab
- **Utilities**: python-dotenv, click, tqdm, distro

### Development Dependencies (requirements-dev.txt)
Includes all production dependencies plus:
- **Testing framework**: pytest, pytest-cov, pytest-flask, pytest-mock, pytest-xdist, pytest-timeout, pytest-html
- **Test data generation**: Faker, factory-boy
- **Code quality tools**: black, flake8, isort, bandit
- **Security scanning**: safety  
- **Database migrations**: alembic
- **Documentation**: sphinx, sphinx-rtd-theme
- **Development utilities**: ipython, debugpy
- **Dependency management**: pip-tools

## 🧪 Testing Requirements Files

### Verify Production Requirements
```bash
pip install -r requirements.txt --dry-run
python -c "import flask; print('Flask import successful')"
```

### Verify Development Requirements  
```bash
pip install -r requirements-dev.txt --dry-run
python -c "import pytest; print('Pytest import successful')"
```

### Run the Application
```bash
# With production requirements
pip install -r requirements.txt
python src/main.py

# With development requirements  
pip install -r requirements-dev.txt
python src/main.py
```

## 🔧 CI/CD Integration

The requirements files are integrated into GitHub Actions workflows:

### Backend Testing
```yaml
- name: Install dependencies
  run: pip install -r requirements-dev.txt
```

### Code Quality Checks
```yaml
- name: Install linting tools
  run: pip install -r requirements-dev.txt
```

### Docker Builds
```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
```

## 🎯 Best Practices

### Do ✅
- Use `requirements-dev.txt` for all development work
- Use `requirements.txt` only for production deployments
- Always compile .in files after editing them
- Commit both .in and .txt files together
- Test changes in multiple environments

### Don't ❌
- Don't edit .txt files directly (they're auto-generated)
- Don't install production requirements for development
- Don't commit .txt files without corresponding .in changes
- Don't skip the compilation step

## 🚨 Troubleshooting

### pip-compile Fails
```bash
# Try with enhanced timeout handling
./scripts/compile_requirements.sh requirements.in --dry-run

# Check for dependency conflicts
pip-check
```

### Import Errors
```bash
# Verify current environment
pip list | grep flask

# Reinstall requirements
pip install -r requirements-dev.txt --force-reinstall
```

### CI/CD Failures
1. Check if requirements files are properly compiled
2. Verify no merge conflicts in .txt files
3. Ensure both .in and .txt files are committed
4. Test locally first: `pip install -r requirements-dev.txt`

---

## 📚 Related Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup and workflow
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Environment setup guide
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Copilot development guidelines

---

*Last updated: Based on analysis of 50+ recent PRs and current CI/CD pipeline requirements*