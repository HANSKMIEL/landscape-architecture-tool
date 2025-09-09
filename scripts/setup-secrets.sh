#!/bin/bash

# Landscape Architecture Tool - Secrets Setup Script
# This script helps configure repository secrets for GitHub Actions

set -e

echo "🔐 Landscape Architecture Tool - Secrets Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    print_error "Please authenticate with GitHub CLI first: gh auth login"
    exit 1
fi

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
print_info "Setting up secrets for repository: $REPO"

# Function to set a secret
set_secret() {
    local secret_name=$1
    local secret_description=$2
    local is_required=${3:-false}
    
    echo ""
    echo -e "${BLUE}Setting up: $secret_name${NC}"
    echo "Description: $secret_description"
    
    if [ "$is_required" = true ]; then
        echo -e "${YELLOW}This secret is required for the application to function properly.${NC}"
    fi
    
    read -p "Enter value for $secret_name (or press Enter to skip): " -s secret_value
    echo ""
    
    if [ -n "$secret_value" ]; then
        if gh secret set "$secret_name" --body "$secret_value" --repo "$REPO"; then
            print_status "Successfully set $secret_name"
        else
            print_error "Failed to set $secret_name"
        fi
    else
        print_warning "Skipped $secret_name"
    fi
}

echo ""
print_info "Starting secrets configuration..."

# Required secrets
echo ""
echo "=== REQUIRED SECRETS ==="

set_secret "SECRET_KEY" "Flask application secret key (generate with: python -c 'import secrets; print(secrets.token_hex(32))')" true
set_secret "DATABASE_URL" "Production database connection string" true
set_secret "REDIS_URL" "Redis connection string for caching" true

# API Keys
echo ""
echo "=== API KEYS ==="

set_secret "OPENAI_API_KEY" "OpenAI API key for AI features"
set_secret "VECTORWORKS_API_KEY" "Vectorworks API key for CAD integration"
set_secret "WEATHER_API_KEY" "Weather service API key"
set_secret "PLANT_DATABASE_API_KEY" "Plant database API key"

# Authentication
echo ""
echo "=== AUTHENTICATION ==="

set_secret "JWT_SECRET_KEY" "JWT token secret key"
set_secret "ENCRYPTION_KEY" "32-byte encryption key for sensitive data"

# Email Configuration
echo ""
echo "=== EMAIL CONFIGURATION ==="

set_secret "MAIL_SERVER" "SMTP server hostname"
set_secret "MAIL_PORT" "SMTP server port (usually 587)"
set_secret "MAIL_USERNAME" "SMTP username"
set_secret "MAIL_PASSWORD" "SMTP password or app password"
set_secret "MAIL_USE_TLS" "Use TLS for email (true/false)"

# Cloud Storage
echo ""
echo "=== CLOUD STORAGE ==="

set_secret "AWS_ACCESS_KEY_ID" "AWS access key for S3 storage"
set_secret "AWS_SECRET_ACCESS_KEY" "AWS secret key for S3 storage"
set_secret "AWS_S3_BUCKET" "S3 bucket name for file storage"
set_secret "AWS_REGION" "AWS region (e.g., us-east-1)"

# Deployment
echo ""
echo "=== DEPLOYMENT ==="

set_secret "DOCKER_USERNAME" "Docker Hub username"
set_secret "DOCKER_PASSWORD" "Docker Hub password or token"
set_secret "HEROKU_API_KEY" "Heroku API key for deployment"
set_secret "VERCEL_TOKEN" "Vercel token for frontend deployment"

# Monitoring
echo ""
echo "=== MONITORING & ANALYTICS ==="

set_secret "SENTRY_DSN" "Sentry DSN for error tracking"
set_secret "NEW_RELIC_LICENSE_KEY" "New Relic license key"
set_secret "GOOGLE_ANALYTICS_ID" "Google Analytics tracking ID"
set_secret "MIXPANEL_TOKEN" "Mixpanel analytics token"

echo ""
echo "=============================================="
print_status "Secrets setup completed!"
echo ""
print_info "Next steps:"
echo "1. Review the secrets in your repository settings"
echo "2. Update your workflows to use these secrets"
echo "3. Test your CI/CD pipeline"
echo "4. Configure branch protection rules"
echo ""
print_warning "Remember to:"
echo "- Never commit secrets to your repository"
echo "- Rotate secrets regularly"
echo "- Use least-privilege access principles"
echo "- Monitor secret usage in Actions logs"
echo ""
print_info "For more information, see: .github/security.md"
