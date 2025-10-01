# V1.00D Development Guide

**Status**: ✅ Active Development Branch
**Environment**: http://72.60.176.200:8080
**Auto-Deploy**: Enabled on push

## 🎯 Quick Start

V1.00D is the active development branch. All pushes automatically deploy to the development environment.

### Development URL

```
http://72.60.176.200:8080
```

### Current Setup

- **Branch**: V1.00D
- **Deployment**: Automatic via GitHub Actions
- **Directory**: `/var/www/landscape-architecture-tool-dev` (on VPS)
- **Title**: "devdeploy - Landscape Architecture Tool (Development)"
- **Backend Port**: 5001
- **Frontend Port**: 8080

## 🚀 Development Workflow

### 1. Make Changes

Work on features, fixes, or improvements in your local environment or Codespace.

### 2. Commit & Push

```bash
git add -A
git commit -m "feat: your feature description"
git push origin V1.00D
```

### 3. Automatic Deployment

The push triggers `.github/workflows/v1d-devdeploy.yml`:

- Builds frontend with development title
- Deploys to `/var/www/landscape-architecture-tool-dev/`
- Restarts services
- Verifies deployment

### 4. Test on Development

Visit http://72.60.176.200:8080 to test your changes.

### 5. Iterate

Repeat steps 1-4 until your feature is ready.

## 🔧 Monitoring Deployments

### View Recent Deployments

```bash
gh run list --workflow="V1.00D DevDeploy Deployment" --limit 5
```

### Watch Live Deployment

```bash
gh run watch <run-id>
```

### Check Deployment Status

```bash
# Check if development is running
curl -I http://72.60.176.200:8080

# Verify title
curl -s http://72.60.176.200:8080 | grep "<title>"
```

## 🛡️ Safety Features

### Production Protection

The V1.00D workflow includes safety checks to prevent accidental production deployment:

1. **Directory Priority**: Development directory checked FIRST
2. **Safety Check**: Exits immediately if production directory detected
3. **Explicit Verification**: Each deployment verifies target directory

### Isolation Guarantee

```
✅ V1.00D → /var/www/landscape-architecture-tool-dev → http://72.60.176.200:8080
❌ V1.00D → /var/www/landscape-architecture-tool → ⛔ BLOCKED!
```

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                  V1.00D Branch                      │
│                                                     │
│  Local Development / Codespace                      │
└───────────────────┬─────────────────────────────────┘
                    │ git push origin V1.00D
                    ▼
┌─────────────────────────────────────────────────────┐
│              GitHub Actions Workflow                │
│                                                     │
│  • Build Frontend (devdeploy title)                 │
│  • Run Tests                                        │
│  • Check Target Directory                           │
│  • Safety Verification                              │
└───────────────────┬─────────────────────────────────┘
                    │ SSH Deploy
                    ▼
┌─────────────────────────────────────────────────────┐
│              VPS Development Environment            │
│                                                     │
│  Directory: /var/www/landscape-architecture-tool-dev│
│  URL: http://72.60.176.200:8080                     │
│  Title: "devdeploy - Landscape..."                  │
└─────────────────────────────────────────────────────┘
```

## 🧪 Testing Your Changes

### Frontend Testing

```bash
# In Codespace/local
cd frontend
npm run test:vitest:run
```

### Backend Testing

```bash
# In Codespace/local
make backend-test
```

### Live Testing

After deployment, test on http://72.60.176.200:8080:

- ✅ Check page loads correctly
- ✅ Verify new features work
- ✅ Test user interactions
- ✅ Check console for errors
- ✅ Verify API calls work

## 📝 Commit Message Convention

Use semantic commit messages:

```bash
feat: Add new feature
fix: Fix bug or issue
docs: Documentation changes
style: Code style/formatting
refactor: Code refactoring
test: Add or update tests
chore: Maintenance tasks
```

### Examples

```bash
git commit -m "feat: Add plant recommendation algorithm"
git commit -m "fix: Resolve supplier list filtering issue"
git commit -m "docs: Update API documentation"
```

## 🔄 Promoting to Production

When V1.00D is ready for production:

### Step 1: Verify Everything Works

- ✅ All features tested on development
- ✅ No critical bugs
- ✅ Tests passing
- ✅ Documentation updated

### Step 2: Use Promotion Script

```bash
./scripts/deployment/promote_v1d_to_v1.sh
```

This script:

1. Creates backup of current production
2. Merges V1.00D changes to main
3. Updates version numbers
4. Prepares for production deployment

### Step 3: Deploy to Production

Production deployment happens separately from development and requires:

- Manual approval
- Explicit main branch deployment
- Production environment variables

## 🚨 Troubleshooting

### Deployment Failed

```bash
# Check workflow logs
gh run list --workflow="V1.00D DevDeploy Deployment" --limit 1
gh run view <run-id> --log
```

### Development Site Not Updating

```bash
# Verify deployment succeeded
curl -I http://72.60.176.200:8080

# Check if new commit was deployed
curl -s http://72.60.176.200:8080 | grep "index-"
```

### Wrong Directory Error

If you see:

```
🚨 CRITICAL ERROR: Attempting to deploy V1.00D to PRODUCTION directory!
```

This is the safety check working! The workflow detected an attempt to deploy to production and blocked it.

**Action**: No action needed - this is expected behavior.

## 📚 Related Documentation

- **Deployment Fix**: `docs/solutions/DEPLOYMENT_CONTAMINATION_FIX.md`
- **Isolation Guide**: `_internal/docs/deployment/DEPLOYMENT_ISOLATION_GUIDE.md`
- **Copilot Instructions**: `.github/copilot-instructions.md`
- **Promotion Script**: `scripts/deployment/promote_v1d_to_v1.sh`

## 🎓 Best Practices

### 1. Frequent Commits

Commit often with clear messages. Each commit triggers a deployment, so you can test iteratively.

### 2. Test Before Push

Run local tests before pushing to catch issues early:

```bash
make lint          # Check code quality
make backend-test  # Run backend tests
```

### 3. Monitor Deployments

Watch your deployment to catch issues immediately:

```bash
gh run list --branch V1.00D --limit 1
```

### 4. Clear Browser Cache

After deployment, clear cache to see changes:

- Chrome/Edge: `Ctrl + Shift + R`
- Firefox: `Ctrl + F5`

### 5. Keep Development Clean

- Don't commit sensitive data
- Keep .gitignore updated
- Remove debug code before pushing

## ✅ Verification Checklist

Before considering V1.00D ready for promotion:

- [ ] All planned features implemented
- [ ] All bugs fixed
- [ ] Frontend tests passing
- [ ] Backend tests passing
- [ ] Linting clean
- [ ] Documentation updated
- [ ] API endpoints tested
- [ ] User workflows verified
- [ ] Performance acceptable
- [ ] Security reviewed
- [ ] Tested on multiple browsers
- [ ] Mobile responsiveness checked

## 🔗 Quick Links

- **Development URL**: http://72.60.176.200:8080
- **GitHub Actions**: https://github.com/HANSKMIEL/landscape-architecture-tool/actions
- **Workflows**: `.github/workflows/v1d-devdeploy.yml`
- **Repository**: https://github.com/HANSKMIEL/landscape-architecture-tool

---

**Remember**: V1.00D is your safe development playground. Break things, experiment, and iterate. Production (optura.nl) remains untouched until you explicitly promote your changes.

Happy coding! 🚀
