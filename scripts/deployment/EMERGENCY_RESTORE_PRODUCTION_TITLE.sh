#!/bin/bash
# EMERGENCY: Restore Production Title on optura.nl
# This script fixes the production deployment that was contaminated with devdeploy title

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}🚨 EMERGENCY PRODUCTION TITLE RESTORATION${NC}"
echo -e "${RED}=========================================${NC}"
echo ""
echo -e "${YELLOW}This script will restore the correct production title on optura.nl${NC}"
echo -e "${YELLOW}NOTE: After branch migration, 'main' branch is the active development branch.${NC}"
echo -e "${YELLOW}The old production state is archived in 'Archive-main' branch.${NC}"
echo ""

# Safety check
read -p "Are you sure you want to proceed? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Configuration
VPS_HOST="${VPS_HOST:-72.60.176.200}"
VPS_USER="${VPS_USER:-root}"
PRODUCTION_DIR="/var/www/landscape-architecture-tool"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/landscape-emergency-backup-$TIMESTAMP"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  VPS Host: $VPS_HOST"
echo "  VPS User: $VPS_USER"
echo "  Production Dir: $PRODUCTION_DIR"
echo "  Backup Dir: $BACKUP_DIR"
echo ""

# Create restore script to run on VPS
cat > /tmp/restore_production_title.sh << 'EOF'
#!/bin/bash
set -e

PRODUCTION_DIR="/var/www/landscape-architecture-tool"
BACKUP_DIR="/var/backups/landscape-emergency-backup-$(date +%Y%m%d_%H%M%S)"

echo "🚨 EMERGENCY PRODUCTION RESTORATION"
echo "===================================="

# Create backup
echo "💾 Creating backup of current state..."
mkdir -p "$(dirname "$BACKUP_DIR")"
cp -r "$PRODUCTION_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

# Navigate to production directory
cd "$PRODUCTION_DIR"

# Show current state
echo "📍 Current branch: $(git branch --show-current)"
echo "📍 Current commit: $(git log -1 --oneline)"

# Checkout main branch (production archive)
# NOTE: After branch migration, use 'Archive-main' for old production state
echo "🔄 Switching to main branch..."
git fetch --all
git checkout main
git reset --hard origin/main

echo "✅ Now on main branch:"
git log -1 --oneline

# Verify the title in source
if grep -q "Professional Garden Design Management" frontend/index.html; then
    echo "✅ Source has correct production title"
else
    echo "⚠️ Fixing source title..."
    sed -i 's/<title>.*<\/title>/<title>Landscape Architecture Tool - Professional Garden Design Management<\/title>/' frontend/index.html
fi

# Rebuild frontend with correct title
echo "🏗️ Rebuilding frontend..."
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --legacy-peer-deps

# Build with production title
echo "🔨 Building..."
npm run build

# Verify build output has correct title
if grep -q "Professional Garden Design Management" dist/index.html; then
    echo "✅ Build has correct production title"
else
    echo "🔧 Fixing build title..."
    sed -i 's/<title>.*<\/title>/<title>Landscape Architecture Tool - Professional Garden Design Management<\/title>/' dist/index.html
fi

cd ..

# Set correct permissions
echo "🔒 Setting permissions..."
chown -R www-data:www-data . || echo "⚠️ Could not set www-data ownership"

# Restart backend service
echo "🔄 Restarting backend service..."
systemctl restart landscape-backend || echo "⚠️ Could not restart backend"

# Reload nginx
echo "🔄 Reloading nginx..."
systemctl reload nginx || echo "⚠️ Could not reload nginx"

# Verification
echo ""
echo "✅ RESTORATION COMPLETE"
echo "======================="
echo "Branch: $(git branch --show-current)"
echo "Commit: $(git log -1 --oneline)"
echo ""
echo "🔍 Verifying title..."
if curl -s http://127.0.0.1/ | grep -q "Professional Garden Design Management"; then
    echo "✅ Production title verified!"
else
    echo "❌ Title verification failed - manual check required"
fi

echo ""
echo "📊 Next steps:"
echo "1. Visit https://optura.nl in your browser"
echo "2. Verify the title shows: 'Landscape Architecture Tool - Professional Garden Design Management'"
echo "3. If needed, clear browser cache (Ctrl+Shift+R)"

EOF

# Copy script to VPS and execute
echo -e "${BLUE}📤 Deploying restoration script to VPS...${NC}"

if [ -n "$VPS_SSH_KEY" ]; then
    # Use SSH key if available
    echo "🔑 Using SSH key authentication..."
    echo "$VPS_SSH_KEY" > ~/.ssh/vps_key
    chmod 600 ~/.ssh/vps_key
    
    scp -i ~/.ssh/vps_key -o StrictHostKeyChecking=no /tmp/restore_production_title.sh $VPS_USER@$VPS_HOST:/tmp/
    ssh -i ~/.ssh/vps_key -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "bash /tmp/restore_production_title.sh"
else
    echo "🔐 Using password authentication..."
    scp -o StrictHostKeyChecking=no /tmp/restore_production_title.sh $VPS_USER@$VPS_HOST:/tmp/
    ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "bash /tmp/restore_production_title.sh"
fi

echo ""
echo -e "${GREEN}✅ EMERGENCY RESTORATION COMPLETED${NC}"
echo ""
echo -e "${YELLOW}Please verify:${NC}"
echo "1. Visit https://optura.nl"
echo "2. Check browser tab title (clear cache if needed: Ctrl+Shift+R)"
echo "3. Verify title: 'Landscape Architecture Tool - Professional Garden Design Management'"
echo ""
echo -e "${BLUE}If issues persist, check the backup at: $BACKUP_DIR${NC}"
