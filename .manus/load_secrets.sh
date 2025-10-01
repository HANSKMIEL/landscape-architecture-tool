#!/bin/bash
# 🔐 Manus Secrets Loader
# Loads encrypted authentication data for seamless development continuation

echo "🔐 Loading Manus authentication secrets..."

# Load secrets file
SECRETS_FILE=".manus/secrets.enc"

if [ ! -f "$SECRETS_FILE" ]; then
    echo "❌ Secrets file not found: $SECRETS_FILE"
    exit 1
fi

# Decode and export GitHub token
export GH_TOKEN=$(grep "GITHUB_TOKEN_ENCRYPTED" "$SECRETS_FILE" | cut -d'"' -f2 | base64 -d)
export GITHUB_REPO=$(grep "GITHUB_REPO" "$SECRETS_FILE" | cut -d'"' -f2)

# Decode and export VPS credentials
export VPS_HOST=$(grep "VPS_HOST" "$SECRETS_FILE" | cut -d'"' -f2)
export VPS_USER=$(grep "VPS_USER" "$SECRETS_FILE" | cut -d'"' -f2)
export VPS_PASSWORD=$(grep "VPS_PASSWORD_ENCRYPTED" "$SECRETS_FILE" | cut -d'"' -f2 | base64 -d)

# Export environment URLs
export DEV_URL=$(grep "DEV_URL" "$SECRETS_FILE" | cut -d'"' -f2)
export PROD_URL=$(grep "PROD_URL" "$SECRETS_FILE" | cut -d'"' -f2)

# Export admin credentials for testing
export ADMIN_USERNAME=$(grep "ADMIN_USERNAME" "$SECRETS_FILE" | cut -d'"' -f2)
export ADMIN_PASSWORD=$(grep "ADMIN_PASSWORD" "$SECRETS_FILE" | cut -d'"' -f2)

# Configure git with token
git remote set-url origin "https://$GH_TOKEN@github.com/$GITHUB_REPO.git"

echo "✅ Authentication secrets loaded successfully"
echo "📋 Available environment variables:"
echo "   - GH_TOKEN (GitHub authentication)"
echo "   - VPS_HOST, VPS_USER, VPS_PASSWORD (VPS access)"
echo "   - DEV_URL, PROD_URL (Environment URLs)"
echo "   - ADMIN_USERNAME, ADMIN_PASSWORD (Testing credentials)"

# Verify GitHub access
echo "🔍 Verifying GitHub access..."
if gh auth status >/dev/null 2>&1; then
    echo "✅ GitHub authentication verified"
else
    echo "⚠️  GitHub CLI not authenticated, but token is available in GH_TOKEN"
fi

# Verify VPS access
echo "🔍 Verifying VPS access..."
if sshpass -p "$VPS_PASSWORD" ssh -o ConnectTimeout=5 -o BatchMode=yes "$VPS_USER@$VPS_HOST" "echo 'VPS connection successful'" 2>/dev/null; then
    echo "✅ VPS access verified"
else
    echo "⚠️  VPS access verification failed (may be due to network or SSH settings)"
fi

echo "🚀 Ready for development continuation!"
