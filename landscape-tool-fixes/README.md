# Landscape Architecture Tool - Critical Fixes

This folder contains the critical files that need to be updated to fix the authentication issue and improve security in the Landscape Architecture Tool.

## Files Included

### 1. `frontend/src/services/authService.js`
**Problem**: Hardcoded localhost URL causing authentication failure in production
**Fix**: Updated to use dynamic API base URL from environment configuration

### 2. `frontend/src/utils/mockApi.js`
**Problem**: Mock API detection not respecting production domains
**Fix**: Added environment variable support for production domains

### 3. `frontend/vite.config.js`
**Problem**: Incorrect build configuration for production
**Fix**: Added environment-specific build options and disabled source maps in production

## Implementation Instructions

1. Replace the existing files in your repository with these fixed versions
2. Create the following environment files in the `frontend` directory:

### `.env.production`
```
VITE_API_BASE_URL=/api
VITE_PRODUCTION_DOMAINS=your-domain.com,your-vps-ip
VITE_ENABLE_MOCK_API=false
VITE_ENABLE_DEBUG_TOOLS=false
VITE_APP_TITLE=Landscape Architecture Tool
VITE_DEFAULT_LANGUAGE=nl
```

### `.env.development`
```
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENABLE_MOCK_API=false
VITE_ENABLE_DEBUG_TOOLS=true
VITE_APP_TITLE=Landscape Architecture Tool (Development)
VITE_DEFAULT_LANGUAGE=nl
```

### `.env.demo`
```
VITE_API_BASE_URL=MOCK_API
VITE_ENABLE_MOCK_API=true
VITE_ENABLE_DEBUG_TOOLS=false
VITE_APP_TITLE=Landscape Architecture Tool (Demo)
VITE_DEFAULT_LANGUAGE=nl
```

## Security Notes

1. **NEVER commit actual credentials** to the repository
2. **USE ENVIRONMENT VARIABLES** for all sensitive information
3. **PREFER SSH KEY AUTHENTICATION** over password authentication
4. **DISABLE SOURCE MAPS** in production to prevent source code exposure
