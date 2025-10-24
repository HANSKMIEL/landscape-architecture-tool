# 🚀 Deployment Scripts

This directory contains all deployment-related scripts for the Landscape Architecture Tool.

## 📚 Essential Documentation

Before using deployment scripts, review these comprehensive guides:

- **[DEVELOPMENT_GUIDE.md](../../docs/DEVELOPMENT_GUIDE.md)** - Environment parity and deployment workflow (Section 1)
- **[BRANCHING_STRATEGY.md](../../docs/BRANCHING_STRATEGY.md)** - Promotion workflow V1.00D → main
- **[DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md)** - Troubleshooting deployment issues
- **[Deployment Guide](../../docs/deployment/DEPLOYMENT_SCRIPTS_GUIDE.md)** - Detailed deployment documentation

## Best Practices

All deployment scripts follow these principles from the engineering velocity framework:

1. **Environment Parity** ([DEVELOPMENT_GUIDE.md - Section 1](../../docs/DEVELOPMENT_GUIDE.md#1-bulletproof-development-environment))
   - Docker ensures consistent environments
   - Configuration via environment variables

2. **Safe Promotion** ([BRANCHING_STRATEGY.md](../../docs/BRANCHING_STRATEGY.md#3-promotion-to-production))
   - V1.00D (development) → DevDeploy testing
   - Validation and approval required
   - Automated promotion to main (production)

3. **Automated Testing** ([DEVELOPMENT_GUIDE.md - Section 4](../../docs/DEVELOPMENT_GUIDE.md#4-proactive-code-quality--automation))
   - Pre-deployment validation
   - Health checks post-deployment
   - Rollback on failure

## 📋 Available Scripts

### 🎯 Main Deployment Scripts

#### `deploy_v1d_to_devdeploy.sh`
**Purpose**: Deploy V1.00D branch to the development environment  
**Target**: DevDeploy environment (http://72.60.176.200:8080)  
**Features**:
- ✅ Automatic devdeploy title configuration
- ✅ Complete V1.00D branch deployment
- ✅ Health checks and verification
- ✅ Isolated from production environment

**Usage**:
```bash
# Set VPS password
export VPS_PASSWORD='your_password'

# Deploy V1.00D to devdeploy
./scripts/deployment/deploy_v1d_to_devdeploy.sh
```

#### `promote_v1d_to_v1.sh`
**Purpose**: Promote V1.00D development changes to V1.00 production package  
**Target**: Repository packages (safe promotion)  
**Features**:
- ✅ Complete isolation from live production
- ✅ Automated backup creation
- ✅ Comprehensive testing before promotion
- ✅ Two-step deployment process

**Usage**:
```bash
# Promote V1.00D to V1.00 package
./scripts/deployment/promote_v1d_to_v1.sh
```

### 🔧 Supporting Scripts

#### `validate_deployment_prerequisites.sh` ⭐ NEW
**Purpose**: Comprehensive pre-deployment validation  
**Features**:
- ✅ Validates GitHub secrets and SSH keys
- ✅ Checks Node.js 20.x and Python 3.12
- ✅ Tests SSH connectivity to VPS
- ✅ Verifies dependency files
- ✅ Provides troubleshooting guidance

**Usage**:
```bash
# Set environment variables
export VPS_SSH_KEY="$(cat ~/.ssh/landscape_deploy)"
export VPS_HOST="72.60.176.200"
export VPS_USER="root"

# Run validation
./scripts/deployment/validate_deployment_prerequisites.sh
```

#### `check_github_secrets.sh` ⭐ NEW
**Purpose**: Interactive GitHub secrets verification  
**Features**:
- ✅ Lists configured secrets via GitHub CLI
- ✅ Checks for required VPS_SSH_KEY
- ✅ Interactive setup wizard
- ✅ Documentation links

**Usage**:
```bash
# Requires GitHub CLI (gh) authenticated
./scripts/deployment/check_github_secrets.sh
```

#### `fix_firewall.sh`
**Purpose**: Configure VPS firewall for deployment  
**Features**: Opens required ports (22, 8080, 5001)

#### `fix_backend_binding.sh`
**Purpose**: Ensure backend binds to 0.0.0.0  
**Features**: External access configuration

#### `devdeploy_diagnostic.sh`
**Purpose**: Comprehensive development environment diagnostics  
**Features**: Service status, logs, configuration

#### `enhanced-deploy.sh`
**Purpose**: Enhanced deployment with comprehensive validation  
**Features**: Multi-environment support, rollback capabilities

#### `github-actions-deploy.sh`
**Purpose**: GitHub Actions integration deployment  
**Features**: CI/CD pipeline integration

#### `setup_github_pages.sh`
**Purpose**: GitHub Pages deployment setup  
**Features**: Static site deployment configuration

## 🎯 Deployment Workflows

### Development Workflow (V1.00D)
```bash
# 1. Work on V1.00D branch
git checkout V1.00D

# 2. Deploy to development environment
./scripts/deployment/deploy_v1d_to_devdeploy.sh

# 3. Test at http://72.60.176.200:8080
# Browser tab shows: "devdeploy - Landscape Architecture Tool (Development)"

# 4. When ready, promote to production package
./scripts/deployment/promote_v1d_to_v1.sh
```

### Production Deployment
```bash
# 1. After promotion, deploy V1.00 package to production
./scripts/deployment/deploy_v1_to_production.sh

# 2. Verify at https://optura.nl
# Browser tab shows: "Landscape Architecture Tool - Professional Garden Design Management"
```

## 🛡️ Environment Isolation

| Environment | Branch | URL | Title | Backend Port |
|-------------|--------|-----|-------|--------------|
| **Development** | V1.00D | http://72.60.176.200:8080 | devdeploy - ... | 5001 |
| **Production** | V1.00 | https://optura.nl | Landscape Architecture Tool - ... | 5000 |

## 🔍 Verification Commands

### DevDeploy Environment
```bash
# Check devdeploy title
curl -s http://72.60.176.200:8080 | grep '<title>'

# Check API health
curl -s http://72.60.176.200:8080/health

# Check backend status
curl -s http://72.60.176.200:8080/api/auth/status
```

### Production Environment
```bash
# Check production title
curl -s https://optura.nl | grep '<title>'

# Check API health
curl -s https://optura.nl/api/health
```

## 🚨 Troubleshooting

### DevDeploy Deployment Issues

**Problem**: DevDeploy title not showing correctly  
**Solution**:
```bash
# Run title enforcement script
./scripts/development/ensure_devdeploy_title.sh

# Redeploy
./scripts/deployment/deploy_v1d_to_devdeploy.sh
```

**Problem**: VPS connection failed  
**Solution**:
```bash
# Check VPS password is set
echo $VPS_PASSWORD

# Test VPS connection
sshpass -p "$VPS_PASSWORD" ssh root@72.60.176.200 "echo 'Connection OK'"
```

**Problem**: Frontend build failed  
**Solution**:
```bash
# Clean and rebuild
cd frontend
rm -rf node_modules dist
npm ci --legacy-peer-deps
npm run build
```

### Production Deployment Issues

**Problem**: Production affected during development  
**Solution**: This should never happen with proper isolation. Check that you're using the correct scripts.

## 📊 Deployment Logs

All deployment scripts create detailed logs:
- **DevDeploy**: `deployment_logs/devdeploy_TIMESTAMP.log`
- **Promotion**: `promotion_logs/promotion_TIMESTAMP.log`

## 🔗 Related Documentation

- **⭐ NEW**: [GitHub Secrets Configuration](../../docs/deployment/GITHUB_SECRETS_CONFIGURATION.md)
- **⭐ NEW**: [Deployment Troubleshooting Guide](../../docs/deployment/DEPLOYMENT_TROUBLESHOOTING.md)
- **⭐ NEW**: [Quick Reference Card](../../docs/deployment/QUICK_REFERENCE.md)
- **⭐ NEW**: [Deployment Documentation Hub](../../docs/deployment/README.md)
- [Deployment Isolation Guide](../../docs/deployment/DEPLOYMENT_ISOLATION_GUIDE.md)
- [Development Guide](../../docs/development/DEVELOPMENT_GUIDE.md)
- [Main Scripts README](../README.md)

## 🆕 What's New

### Recent Enhancements (2024)
- ✅ Added pre-deployment validation script
- ✅ Added GitHub secrets verification helper
- ✅ Created comprehensive secrets setup guide
- ✅ Added troubleshooting documentation
- ✅ Enhanced workflow with SSH connectivity tests
- ✅ Improved error messages and documentation links
- ✅ Added quick reference card for common tasks

---
**Last Updated**: September 13, 2025  
**V1.00D DevDeploy**: ✅ Fully Configured  
**Environment Isolation**: ✅ Complete
