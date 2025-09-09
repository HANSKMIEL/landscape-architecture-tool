#!/bin/bash

echo "🚀 Setting up GitHub Pages for Landscape Architecture Tool"
echo "========================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the repository root"
    exit 1
fi

# Create workflows directory
mkdir -p .github/workflows

# Copy workflow file
echo "📝 Creating GitHub Pages workflow..."
cat > .github/workflows/deploy-demo.yml << 'WORKFLOW'
name: Deploy Demo to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Build frontend
        run: |
          cd frontend
          npm run build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: frontend/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
WORKFLOW

echo "✅ Workflow file created at .github/workflows/deploy-demo.yml"

# Add and commit
git add .github/workflows/deploy-demo.yml GITHUB_PAGES_SETUP.md
git commit -m "feat: Add GitHub Pages deployment setup

- Automated workflow for GitHub Pages deployment
- Complete setup guide with instructions
- Enables live demo at hanskmiel.github.io/landscape-architecture-tool"

echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Go to https://github.com/HANSKMIEL/landscape-architecture-tool/settings/pages"
echo "2. Under 'Source', select 'GitHub Actions'"
echo "3. Your demo will be live at: https://hanskmiel.github.io/landscape-architecture-tool/"
echo ""
echo "📖 See GITHUB_PAGES_SETUP.md for detailed instructions"

