#!/bin/bash
# GitHub Pages Setup for V1.00 Package
# Sets up automated deployment of V1.00 frontend to GitHub Pages

set -e

echo "🚀 Setting up GitHub Pages for V1.00 package..."

# Configuration
V1_FRONTEND_PATH="packages/v1.00/frontend"
PAGES_BRANCH="gh-pages"

# Step 1: Build V1.00 frontend
echo "📦 Building V1.00 frontend..."
cd "$V1_FRONTEND_PATH"

# Install dependencies and build
npm ci --legacy-peer-deps
npm run build

# Step 2: Setup GitHub Pages branch
echo "🌐 Setting up GitHub Pages branch..."
cd ../../..

# Create or update gh-pages branch
git checkout --orphan "$PAGES_BRANCH" 2>/dev/null || git checkout "$PAGES_BRANCH"

# Clear branch and copy V1.00 build
git rm -rf . 2>/dev/null || true
cp -r "$V1_FRONTEND_PATH/dist"/* .

# Create CNAME file if needed (update with your domain)
# echo "your-domain.com" > CNAME

# Create .nojekyll to prevent Jekyll processing
touch .nojekyll

# Commit and push
git add .
git commit -m "Deploy V1.00 frontend to GitHub Pages - $(date)"
git push origin "$PAGES_BRANCH"

# Return to development branch
git checkout v1.00D

echo "✅ GitHub Pages setup complete!"
echo "🌐 Site will be available at: https://HANSKMIEL.github.io/landscape-architecture-tool/"
echo "⚠️ Update repository settings to enable GitHub Pages from $PAGES_BRANCH branch"