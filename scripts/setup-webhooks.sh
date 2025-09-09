#!/bin/bash

# Landscape Architecture Tool - Webhook Setup Script
# This script helps configure webhooks for the repository

set -e

echo "🔗 Landscape Architecture Tool - Webhook Setup"
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
print_info "Setting up webhooks for repository: $REPO"

# Function to create a webhook
create_webhook() {
    local webhook_url=$1
    local webhook_description=$2
    local events=$3
    
    echo ""
    echo -e "${BLUE}Setting up webhook: $webhook_description${NC}"
    echo "URL: $webhook_url"
    echo "Events: $events"
    
    read -p "Do you want to create this webhook? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        read -p "Enter webhook secret (optional): " -s webhook_secret
        echo ""
        
        local webhook_config="{
            \"url\": \"$webhook_url\",
            \"content_type\": \"json\",
            \"events\": [$events]"
        
        if [ -n "$webhook_secret" ]; then
            webhook_config="$webhook_config,
            \"secret\": \"$webhook_secret\""
        fi
        
        webhook_config="$webhook_config
        }"
        
        if gh api repos/"$REPO"/hooks -X POST --input - <<< "$webhook_config" > /dev/null; then
            print_status "Successfully created webhook: $webhook_description"
        else
            print_error "Failed to create webhook: $webhook_description"
        fi
    else
        print_warning "Skipped webhook: $webhook_description"
    fi
}

echo ""
print_info "Starting webhook configuration..."

# Deployment webhooks
echo ""
echo "=== DEPLOYMENT WEBHOOKS ==="

read -p "Enter your production domain (e.g., myapp.com): " prod_domain
if [ -n "$prod_domain" ]; then
    create_webhook "https://$prod_domain/hooks/deploy" "Production Deployment" "\"push\", \"release\""
fi

read -p "Enter your staging domain (e.g., staging.myapp.com): " staging_domain
if [ -n "$staging_domain" ]; then
    create_webhook "https://$staging_domain/hooks/deploy" "Staging Deployment" "\"push\", \"pull_request\""
fi

# Monitoring webhooks
echo ""
echo "=== MONITORING WEBHOOKS ==="

read -p "Enter your Sentry webhook URL (optional): " sentry_url
if [ -n "$sentry_url" ]; then
    create_webhook "$sentry_url" "Sentry Error Tracking" "\"push\", \"issues\""
fi

read -p "Enter your Slack webhook URL (optional): " slack_url
if [ -n "$slack_url" ]; then
    create_webhook "$slack_url" "Slack Notifications" "\"push\", \"pull_request\", \"issues\", \"release\""
fi

read -p "Enter your Discord webhook URL (optional): " discord_url
if [ -n "$discord_url" ]; then
    create_webhook "$discord_url" "Discord Notifications" "\"push\", \"pull_request\", \"issues\""
fi

# Custom application webhooks
echo ""
echo "=== APPLICATION WEBHOOKS ==="

read -p "Enter your application webhook URL for client notifications (optional): " client_webhook_url
if [ -n "$client_webhook_url" ]; then
    create_webhook "$client_webhook_url" "Client Portal Notifications" "\"release\", \"issues\""
fi

read -p "Enter your backup service webhook URL (optional): " backup_webhook_url
if [ -n "$backup_webhook_url" ]; then
    create_webhook "$backup_webhook_url" "Backup Service" "\"push\""
fi

echo ""
echo "=============================================="
print_status "Webhook setup completed!"
echo ""
print_info "Next steps:"
echo "1. Test each webhook endpoint"
echo "2. Configure webhook handlers in your application"
echo "3. Set up monitoring for webhook delivery"
echo "4. Document webhook endpoints for your team"
echo ""
print_warning "Remember to:"
echo "- Use HTTPS for all webhook URLs"
echo "- Validate webhook signatures"
echo "- Implement proper error handling"
echo "- Monitor webhook delivery logs"
echo ""
print_info "View configured webhooks: gh api repos/$REPO/hooks"
