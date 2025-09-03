# GitHub Labels Setup for Dependabot Integration

## Overview

This guide explains how to set up the GitHub labels required for Dependabot to function properly. Dependabot uses these labels to categorize dependency update pull requests.

## Problem

If you see this error from Dependabot:

```
The following labels could not be found: `dependencies`, `javascript`. 
Please create them before Dependabot can add them to a pull request.
```

This means the required labels don't exist in your GitHub repository and need to be created.

## Quick Fix (Automated)

### Prerequisites

1. **Install GitHub CLI**: https://cli.github.com/
2. **Authenticate**: `gh auth login`
3. **Repository access**: Ensure you have admin/write access to the repository

### Run the Setup Script

```bash
# Check what labels need to be created (dry run)
python scripts/setup_github_labels.py --dry-run

# Create the missing labels
python scripts/setup_github_labels.py --create
```

## Manual Setup (Alternative)

If you prefer to create labels manually or the script doesn't work:

### Required Labels

Create these labels in your GitHub repository (Settings → Labels → New label):

| Label Name | Description | Color |
|------------|-------------|--------|
| `dependencies` | Updates to project dependencies | `#0366d6` (Blue) |
| `javascript` | JavaScript/Node.js related changes | `#f1e05a` (Yellow) |
| `python` | Python related changes | `#3572A5` (Python blue) |
| `security` | Security related updates | `#d73a49` (Red) |
| `frontend` | Frontend/UI related changes | `#7057ff` (Purple) |
| `docker` | Docker/containerization changes | `#0db7ed` (Docker blue) |
| `infrastructure` | Infrastructure and deployment changes | `#5319e7` (Purple) |
| `github-actions` | GitHub Actions workflow changes | `#2088ff` (GitHub blue) |
| `ci-cd` | Continuous integration and deployment | `#28a745` (Green) |

### Manual Creation Steps

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Labels** in the left sidebar
4. Click **New label** button
5. Fill in the name, description, and color for each label above
6. Click **Create label**

## Verification

After creating the labels, Dependabot should be able to create pull requests without errors. You can verify by:

1. Checking that labels appear in your repository's Labels page
2. Waiting for the next Dependabot run (or trigger one manually)
3. Confirming PRs are created with appropriate labels

## Labels Used by Dependabot

The labels are configured in `.github/dependabot.yml` and are used as follows:

- **Python ecosystem**: `dependencies`, `python`, `security`
- **Frontend/npm ecosystem**: `dependencies`, `frontend`, `javascript`
- **Docker ecosystem**: `dependencies`, `docker`, `infrastructure`
- **GitHub Actions**: `dependencies`, `github-actions`, `ci-cd`

## Troubleshooting

### GitHub CLI Issues

```bash
# Check if gh is installed
gh --version

# Check authentication status
gh auth status

# Re-authenticate if needed
gh auth login
```

### Permission Issues

Ensure your GitHub account has:
- Admin or write access to the repository
- Permission to manage labels (usually included with write access)

### Script Issues

```bash
# Run with debug output
python scripts/setup_github_labels.py --dry-run

# Check script permissions
ls -la scripts/setup_github_labels.py

# Make executable if needed
chmod +x scripts/setup_github_labels.py
```

## Related Files

- `.github/dependabot.yml` - Dependabot configuration that references these labels
- `scripts/setup_github_labels.py` - Automated setup script
- Issue #406 - Original issue reporting missing labels

---

**Last Updated**: September 2025  
**Status**: Active - Required for Dependabot functionality