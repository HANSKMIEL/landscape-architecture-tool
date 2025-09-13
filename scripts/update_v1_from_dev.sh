#!/bin/bash
# V1.00 Update Script - Promote validated changes from V1.00D to V1.00
# This script safely updates the protected V1.00 release with tested changes

set -e  # Exit on any error

echo "🚀 Starting V1.00 update process from V1.00D..."

# Configuration
BACKUP_DIR="backups/v1.00_$(date +%Y%m%d_%H%M%S)"
V1_00_PATH="packages/v1.00"
V1_00D_PATH="packages/v1.00D"

# Step 1: Validation
echo "🔍 Step 1: Validating V1.00D package..."

# Check if we're in the right directory
if [ ! -d "$V1_00D_PATH" ]; then
    echo "❌ Error: V1.00D package not found. Are you in the repository root?"
    exit 1
fi

# Run tests on V1.00D
echo "🧪 Running tests on V1.00D..."
cd $V1_00D_PATH
if [ -f "../../Makefile" ]; then
    cd ../..
    make backend-test
    if [ $? -ne 0 ]; then
        echo "⚠️ Warning: Some tests failed. Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "❌ Update cancelled due to test failures"
            exit 1
        fi
    fi
else
    echo "⚠️ Warning: Makefile not found, skipping automated tests"
fi

# Step 2: Backup current V1.00
echo "📦 Step 2: Creating backup of current V1.00..."
mkdir -p "$BACKUP_DIR"
if [ -d "$V1_00_PATH" ]; then
    cp -r "$V1_00_PATH" "$BACKUP_DIR/"
    echo "✅ Backup created at $BACKUP_DIR"
else
    echo "⚠️ Warning: V1.00 package not found, creating new one"
fi

# Step 3: Update V1.00 with V1.00D changes
echo "🔄 Step 3: Updating V1.00 package..."

# Create V1.00 directory if it doesn't exist
mkdir -p "$V1_00_PATH"

# Copy core application files
echo "  📁 Updating backend..."
rm -rf "$V1_00_PATH/backend"
cp -r "$V1_00D_PATH/backend" "$V1_00_PATH/"

echo "  🎨 Updating frontend..."
rm -rf "$V1_00_PATH/frontend"
cp -r "$V1_00D_PATH/frontend" "$V1_00_PATH/"

echo "  📚 Updating documentation..."
rm -rf "$V1_00_PATH/docs"
cp -r "$V1_00D_PATH/docs" "$V1_00_PATH/"

# Step 4: Create deployment package
echo "📦 Step 4: Creating deployment package..."
cat > "$V1_00_PATH/deploy/deploy.sh" << 'EOF'
#!/bin/bash
# V1.00 Deployment Script
# Deploy the protected V1.00 package to production

echo "🚀 Deploying V1.00 to production..."

# Build frontend
cd frontend
npm ci --legacy-peer-deps
npm run build

# Setup backend
cd ../backend
pip install -r ../../requirements.txt

# Start services
echo "✅ V1.00 deployment ready"
EOF

chmod +x "$V1_00_PATH/deploy/deploy.sh"

# Step 5: Create version info
echo "📋 Step 5: Creating version information..."
cat > "$V1_00_PATH/VERSION" << EOF
V1.00 - Landscape Architecture Tool
Updated: $(date)
Source: V1.00D branch
Backup: $BACKUP_DIR
EOF

# Step 6: Git operations
echo "📝 Step 6: Committing changes..."
git add .
git commit -m "Update V1.00 package from V1.00D - $(date)"

# Step 7: Create new tag
NEW_TAG="v1.00.$(date +%Y%m%d%H%M)"
git tag "$NEW_TAG"
echo "🏷️ Created new tag: $NEW_TAG"

# Step 8: Summary
echo ""
echo "✅ V1.00 update completed successfully!"
echo "📦 Backup location: $BACKUP_DIR"
echo "🏷️ New version tag: $NEW_TAG"
echo "📁 Updated package: $V1_00_PATH"
echo ""
echo "🚀 To deploy to production:"
echo "   cd $V1_00_PATH/deploy && ./deploy.sh"
echo ""
echo "⚠️ To rollback if needed:"
echo "   rm -rf $V1_00_PATH && cp -r $BACKUP_DIR/v1.00 packages/"