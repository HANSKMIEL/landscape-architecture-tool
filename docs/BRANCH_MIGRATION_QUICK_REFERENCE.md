# 🚀 Branch Migration Quick Reference

## What's Happening?
**V1.00D** → **main** (becomes the primary development branch)
**main** → **Archive-main** (archived historical state)

## For Repository Administrators

### Manual Steps Required (GitHub Web Interface)
1. Go to: **Settings → Branches**
2. **Rename** `main` → `Archive-main`
3. **Rename** `V1.00D` → `main`
4. **Set** `main` as default branch
5. **Update** branch protection rules (if any)

📖 **Detailed Instructions**: [GitHub Branch Rename Instructions](docs/GITHUB_BRANCH_RENAME_INSTRUCTIONS.md)

## For All Team Members (After Rename)

### Update Your Local Repository
```bash
# 1. Fetch all changes
git fetch origin

# 2. Switch to new main branch
git checkout main

# 3. Update tracking
git branch -u origin/main

# 4. Verify
git status
git log --oneline -3
```

### If You Were on V1.00D Branch
```bash
# V1.00D was renamed to main, so just:
git fetch origin
git checkout main
```

### If You Were on Old Main Branch
```bash
# Old main is now Archive-main:
git fetch origin
git checkout Archive-main  # If you need the old state
# Or switch to active development:
git checkout main
```

## For CI/CD & Automation

### No Changes Needed! ✅
All workflows are already configured to work with both branch names during transition.

After rename:
- Workflows that triggered on `V1.00D` will automatically trigger on `main`
- Workflows that triggered on `main` will automatically trigger on both
- No workflow file changes required post-rename

## For VPS/Deployment

### Current Setup
- **URL**: http://72.60.176.200:8080
- **Auto-deploys from**: V1.00D (soon to be `main`)
- **Directory**: `/var/www/landscape-architecture-tool-dev`

### After Rename
- Everything continues working automatically
- Deploys from `main` branch (which is the renamed V1.00D)
- No VPS configuration changes needed

## Key Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| [BRANCH_MIGRATION_REQUIRED.md](BRANCH_MIGRATION_REQUIRED.md) | Action required notice | Everyone |
| [Branch Migration Guide](docs/BRANCH_MIGRATION_GUIDE.md) | Complete migration guide | Everyone |
| [GitHub Rename Instructions](docs/GITHUB_BRANCH_RENAME_INSTRUCTIONS.md) | Step-by-step for admins | Admins only |
| [Implementation Summary](docs/BRANCH_MIGRATION_IMPLEMENTATION_SUMMARY.md) | Technical details | Developers |

## FAQs

### Q: When should this PR be merged?
**A**: Before, during, or after the GitHub rename. The workflows are designed to work with both branch structures.

### Q: Will this break my local development?
**A**: No, but you'll need to update your local branch tracking after the GitHub rename (see commands above).

### Q: What happens to my open PRs?
**A**: PRs targeting the old `main` may need to be retargeted to the new branch structure. Check each PR after rename.

### Q: Can this be rolled back?
**A**: Yes. Rename branches back via GitHub, revert this PR if needed. See the full rollback plan in the Migration Guide.

### Q: Will VPS deployment break?
**A**: No. The deployment continues automatically since it follows the branch rename.

### Q: What about the old promotion script?
**A**: The `promote_v1d_to_v1.sh` script is now deprecated. Development happens directly on `main` with PR reviews.

## Timeline

- ✅ **PR Created & Reviewed**: October 24, 2025
- ⏳ **PR Merge**: Awaiting approval
- ⏳ **GitHub Rename**: To be scheduled
- ⏳ **Team Migration**: After rename complete
- ⏳ **Verification**: Confirm all systems working

## Need Help?

1. Check the relevant documentation above
2. Contact repository maintainers
3. Review open issues for updates

---

**Status**: Ready for administrator action
**Last Updated**: October 24, 2025
