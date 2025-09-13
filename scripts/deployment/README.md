# 🚀 Deployment Scripts

This directory contains all deployment-related scripts for the Landscape Architecture Tool.

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

- [Deployment Isolation Guide](../../docs/deployment/DEPLOYMENT_ISOLATION_GUIDE.md)
- [Development Guide](../../docs/development/DEVELOPMENT_GUIDE.md)
- [Main Scripts README](../README.md)

---
**Last Updated**: September 13, 2025  
**V1.00D DevDeploy**: ✅ Fully Configured  
**Environment Isolation**: ✅ Complete
