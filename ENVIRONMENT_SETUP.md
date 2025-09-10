# Environment Variables and Secrets Setup

This document provides a comprehensive guide for setting up all required environment variables, API tokens, and secrets for the Landscape Architecture Tool in different environments.

## Table of Contents

- [Local Development Environment](#local-development-environment)
- [Production Environment (VPS)](#production-environment-vps)
- [GitHub Actions Secrets](#github-actions-secrets)
- [Demo Environment (GitHub Pages)](#demo-environment-github-pages)
- [Security Best Practices](#security-best-practices)

## Local Development Environment

### Frontend Environment Variables

Create a `.env.local` file in the `frontend` directory with the following variables:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api

# Feature Flags
VITE_ENABLE_MOCK_API=false
VITE_ENABLE_DEBUG_TOOLS=true

# Application Settings
VITE_APP_TITLE=Landscape Architecture Tool (Development)
VITE_DEFAULT_LANGUAGE=nl
```

### Backend Environment Variables

Create a `.env` file in the project root directory with the following variables:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your_local_development_secret_key_change_this

# Database Configuration
DATABASE_URL=sqlite:///landscape_tool.db

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174

# Authentication
JWT_SECRET_KEY=your_local_jwt_secret_key_change_this
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours in seconds

# Logging
LOG_LEVEL=DEBUG
```

## Production Environment (VPS)

### Frontend Environment Variables

The frontend production environment variables are built into the application during the build process. Use the `.env.production` file in the `frontend` directory:

```bash
# API Configuration
VITE_API_BASE_URL=/api

# Production Domains (comma-separated list)
VITE_PRODUCTION_DOMAINS=72.60.176.200,landscape-tool.example.com

# Feature Flags
VITE_ENABLE_MOCK_API=false
VITE_ENABLE_DEBUG_TOOLS=false

# Application Settings
VITE_APP_TITLE=Landscape Architecture Tool
VITE_DEFAULT_LANGUAGE=nl
```

### Backend Environment Variables

On your VPS, create a `.env` file in the backend directory with the following variables:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your_strong_production_secret_key_change_this

# Database Configuration
DATABASE_URL=sqlite:///landscape_tool.db
# For PostgreSQL: DATABASE_URL=postgresql://landscape_user:your_secure_password@localhost/landscape_tool

# CORS Configuration
CORS_ORIGINS=http://72.60.176.200,https://landscape-tool.example.com

# Authentication
JWT_SECRET_KEY=your_strong_production_jwt_secret_key_change_this
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours in seconds

# Logging
LOG_LEVEL=INFO
```

### Deployment Script Environment Variables

When running the deployment script, set the following environment variables:

```bash
# VPS Connection
export VPS_HOST=72.60.176.200
export VPS_USER=root
export SSH_PASSWORD=your_ssh_password
# Or use SSH key:
# export SSH_KEY=/path/to/your/private_key

# Paths
export FRONTEND_DIST_PATH=frontend/dist
export VPS_FRONTEND_PATH=/var/www/landscape-tool/frontend/dist
export VPS_BACKEND_PATH=/var/www/landscape-tool/backend
export BACKEND_SERVICE=landscape-tool
```

## GitHub Actions Secrets

Add the following secrets to your GitHub repository for CI/CD workflows:

```
# VPS Deployment
VPS_HOST=72.60.176.200
VPS_USER=root
VPS_SSH_PASSWORD=your_ssh_password
# Or use SSH key:
# VPS_SSH_PRIVATE_KEY=your_base64_encoded_private_key

# Environment Configuration
PRODUCTION_SECRET_KEY=your_strong_production_secret_key
PRODUCTION_JWT_SECRET_KEY=your_strong_production_jwt_secret_key
PRODUCTION_DATABASE_URL=sqlite:///landscape_tool.db
```

## Demo Environment (GitHub Pages)

For the GitHub Pages demo environment, create a `.env.demo` file in the `frontend` directory:

```bash
# API Configuration
VITE_API_BASE_URL=MOCK_API

# Feature Flags
VITE_ENABLE_MOCK_API=true
VITE_ENABLE_DEBUG_TOOLS=false

# Application Settings
VITE_APP_TITLE=Landscape Architecture Tool (Demo)
VITE_DEFAULT_LANGUAGE=nl
```

## Security Best Practices

1. **Never commit secrets to version control**:
   - Use `.gitignore` to exclude `.env` files
   - Use GitHub Secrets for CI/CD workflows

2. **Rotate secrets regularly**:
   - Change all production secrets at least every 90 days
   - Immediately rotate secrets if they are accidentally exposed

3. **Use strong, unique secrets**:
   - Generate random strings of at least 32 characters
   - Use a mix of letters, numbers, and special characters

4. **Limit access to secrets**:
   - Only share secrets with team members who need them
   - Use role-based access control for production secrets

5. **Environment-specific secrets**:
   - Use different secrets for development, staging, and production
   - Never use production secrets in development environments

6. **Secret management tools**:
   - Consider using a secret management tool like HashiCorp Vault or AWS Secrets Manager
   - Integrate with your CI/CD pipeline for automated secret rotation

7. **Monitor for secret exposure**:
   - Use tools like GitGuardian to monitor for accidental secret commits
   - Set up alerts for potential secret exposure

## Example Secret Generation

You can generate secure random secrets using the following commands:

```bash
# Generate a random SECRET_KEY
openssl rand -base64 32

# Generate a random JWT_SECRET_KEY
openssl rand -base64 32
```

## Current Production Values

For the current VPS deployment at 72.60.176.200, the following values are being used:

- **VPS_HOST**: 72.60.176.200
- **VPS_USER**: root
- **SSH_PASSWORD**: Volisvol1988.
- **BACKEND_SERVICE**: landscape-tool
- **VPS_FRONTEND_PATH**: /var/www/landscape-tool/frontend/dist
- **VPS_BACKEND_PATH**: /var/www/landscape-tool/backend

> **IMPORTANT**: These values should be changed in a production environment and should never be committed to version control. They are provided here for reference only and should be stored securely.
