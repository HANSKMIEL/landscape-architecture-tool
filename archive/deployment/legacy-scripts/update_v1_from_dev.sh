#!/bin/bash
# Script to update V1.00 production from V1.00D development
# Manual trigger script as requested in Issue #553

set -e

echo "🔄 Starting V1.00D → V1.00 promotion process..."

# Validate we're in the right directory
if [ ! -d "packages/v1.00D" ] || [ ! -d "packages/v1.00" ]; then
    echo "❌ Error: V1.00D or V1.00 packages not found"
    exit 1
fi

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: Uncommitted changes detected. Please commit or stash changes first."
    exit 1
fi

# Run tests on V1.00D first
echo "🧪 Running V1.00D tests..."
cd frontend
npm run test:run || {
    echo "❌ Frontend tests failed. Aborting promotion."
    exit 1
}
cd ..

# Backend tests
echo "🧪 Running backend tests..."
make backend-test || {
    echo "❌ Backend tests failed. Aborting promotion."
    exit 1
}

# Backup current V1.00
echo "💾 Creating backup of current V1.00..."
cp -r packages/v1.00 packages/v1.00.backup.$(date +%Y%m%d_%H%M%S)

# Sync V1.00D to V1.00
echo "🔄 Syncing V1.00D → V1.00..."
rsync -av --delete packages/v1.00D/ packages/v1.00/

# Update version tags
echo "🏷️ Updating version information..."
git add packages/v1.00/
git commit -m "🚀 Promote V1.00D to V1.00 production

- Sync all V1.00D development changes to V1.00 production
- All tests passed successfully
- Backup created: packages/v1.00.backup.$(date +%Y%m%d_%H%M%S)"

echo "✅ V1.00D → V1.00 promotion completed successfully!"
echo "📦 V1.00 package updated with latest development changes"
echo "🎯 Ready for production deployment"
