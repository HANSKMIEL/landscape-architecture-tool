# GitHub Pages Setup Guide

## 🚀 Quick Setup for Live Demo

Follow these steps to get your landscape architecture tool running as a live demo on GitHub Pages:

### Step 1: Enable GitHub Pages

1. Go to your repository: `https://github.com/HANSKMIEL/landscape-architecture-tool`
2. Click on **Settings** tab
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

### Step 2: Add the Deployment Workflow

Create a new file at `.github/workflows/deploy-demo.yml` with this content:

```yaml
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
```

### Step 3: Commit and Push

```bash
git add .github/workflows/deploy-demo.yml
git commit -m "Add GitHub Pages deployment workflow"
git push origin main
```

### Step 4: Wait for Deployment

1. Go to **Actions** tab in your repository
2. Watch the "Deploy Demo to GitHub Pages" workflow run
3. Once complete, your demo will be live at:
   `https://hanskmiel.github.io/landscape-architecture-tool/`

## 🎯 What You'll Get

### Live Demo Features:
- ✅ **Complete Frontend UI** - All components and pages working
- ✅ **Mock Data Integration** - Sample projects, plants, clients, and suppliers
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Professional Presentation** - Perfect for showcasing to clients

### Demo Data Includes:
- **3 Sample Projects** - Villa Botanica, Corporate Headquarters, Historic Park
- **Plant Database** - Japanese Maple, English Lavender, Common Boxwood
- **Client Management** - Van der Berg Family, TechCorp Netherlands
- **Supplier Network** - Dutch Garden Center, Herb Specialists BV

## 🔧 Alternative: Manual GitHub Pages Setup

If the workflow approach doesn't work:

1. **Build locally:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Create gh-pages branch:**
   ```bash
   git checkout --orphan gh-pages
   git rm -rf .
   cp -r frontend/dist/* .
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin gh-pages
   ```

3. **Configure Pages:**
   - Go to Settings → Pages
   - Select **Deploy from a branch**
   - Choose **gh-pages** branch
   - Select **/ (root)** folder

## 🌐 Sharing Your Demo

Once deployed, you can share your live demo:

- **Direct Link**: `https://hanskmiel.github.io/landscape-architecture-tool/`
- **QR Code**: Generate one for easy mobile access
- **Embed**: Use in presentations or documentation

## 🔄 Automatic Updates

Every time you push to the main branch:
1. GitHub Actions automatically builds the frontend
2. Deploys the latest version to GitHub Pages
3. Your demo stays up-to-date with your latest changes

## 🎨 Customization

The demo uses mock data defined in `frontend/src/utils/mockApi.js`. You can:
- Add more sample projects
- Include additional plant varieties
- Customize client information
- Modify supplier details

## 📱 Mobile-Friendly

The demo is fully responsive and works great on:
- Desktop computers
- Tablets
- Mobile phones
- Touch devices

Perfect for showing clients during site visits or meetings!
