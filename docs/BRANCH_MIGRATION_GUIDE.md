# Branch Migration Guide: Making V1.00D the Main Branch

## Overview

This guide documents the process of making the V1.00D branch the new main branch and archiving the current main branch as "Archive-main". This change reflects the reality that V1.00D has become the primary development and deployment branch.

## Background

Historically:
- **main** was the production branch
- **V1.00D** was the development branch
- Changes were promoted from V1.00D to main using `scripts/deployment/promote_v1d_to_v1.sh`

Current reality:
- V1.00D is actively deployed to the VPS (http://72.60.176.200:8080)
- V1.00D contains all current development work
- main branch is no longer the active production branch

## Migration Steps

### Phase 1: Manual GitHub Operations (Repository Owner Only)

These steps **MUST** be performed through the GitHub web interface by someone with admin access:

1. **Rename the main branch to Archive-main**
   - Go to: Settings → Branches
   - Find "main" branch → Click rename
   - New name: `Archive-main`
   - Confirm rename

2. **Rename V1.00D to main**
   - Go to: Settings → Branches
   - Find "V1.00D" branch → Click rename
   - New name: `main`
   - Confirm rename

3. **Update default branch**
   - Go to: Settings → Branches
   - In "Default branch" section, change to `main` (formerly V1.00D)
   - Confirm change

4. **Update branch protection rules** (if applicable)
   - Update any branch protection rules that referenced "main" to now reference "Archive-main" if you want to keep those archives protected
   - Set up appropriate protection rules for the new "main" branch

### Phase 2: Update Local Repositories (All Team Members)

After the GitHub operations are complete, all team members need to update their local repositories:

```bash
# Fetch the latest changes
git fetch origin

# If you were on the old main branch, switch to the new one
git checkout main

# Update your local branch tracking
git branch -u origin/main

# Optional: Delete old branch references
git remote prune origin

# Verify you're on the right branch
git status
git log --oneline -5
```

### Phase 3: Update CI/CD and Scripts (Automated via this PR)

The following changes have been made automatically:

1. **Workflow files updated**
   - All references to `main` branch in workflow triggers now point to the new structure
   - Production deployments now reference the correct branch

2. **Deployment scripts updated**
   - Scripts that referenced main branch have been updated
   - Documentation in scripts reflects the new branch structure

3. **Documentation updated**
   - README and other docs reflect that main (formerly V1.00D) is the primary branch
   - Historical references preserved in Archive-main

## What Changed

### Repository Structure

**Before:**
```
main (production, rarely updated)
├── V1.00D (active development, deployed to VPS)
└── other branches
```

**After:**
```
main (formerly V1.00D - active development, deployed to VPS)
├── Archive-main (formerly main - archived production state)
└── other branches
```

### Branch Purpose

| Branch Name | Before | After |
|------------|--------|-------|
| main | Production branch, protected | Active development, deployed to VPS |
| V1.00D | Development branch | *Renamed to "main"* |
| Archive-main | *Did not exist* | Historical production branch (formerly "main") |

### Deployment Workflow

**Before:**
- Develop on V1.00D
- Promote to main via `promote_v1d_to_v1.sh`
- Deploy main to production

**After:**
- Develop on main (formerly V1.00D)
- Push directly to main (with appropriate PR reviews)
- Auto-deploy to VPS from main

## Verification Checklist

After the migration, verify:

- [ ] GitHub default branch is set to "main" (formerly V1.00D)
- [ ] Local repository correctly tracks new main branch
- [ ] CI/CD workflows trigger correctly on pushes to main
- [ ] VPS deployment continues to work from main branch
- [ ] Archive-main branch is accessible for historical reference
- [ ] All team members have updated their local repositories
- [ ] Branch protection rules are correctly configured
- [ ] Documentation reflects new branch structure

## Rollback Plan

If issues arise, the migration can be reversed:

1. Rename branches back to original names through GitHub web interface
2. Update default branch back to original configuration
3. Revert the code changes from this PR
4. Notify all team members to update their local repositories

## FAQ

**Q: What happens to the promotion script?**
A: The `promote_v1d_to_v1.sh` script is deprecated since we no longer have separate production and development branches. Development happens directly on main with appropriate review processes.

**Q: Can we still access old main branch code?**
A: Yes, it's preserved in the `Archive-main` branch.

**Q: Do I need to update my local branches?**
A: Yes, follow the steps in Phase 2 above.

**Q: Will this break existing PRs?**
A: Open PRs targeting the old main branch may need to be retargeted to point to the correct branch after migration.

**Q: What about the packages/v1.00 directory?**
A: This directory structure can remain as-is for now as a reference, though it may be deprecated in future cleanup.

## Related Documentation

- `.github/copilot-instructions.md` - Updated to reflect new branch structure
- `README.md` - Updated branch references
- `docs/development/V1_00D_DEVELOPMENT_GUIDE.md` - Updated for new workflow

## Timeline

- **Created**: October 24, 2025
- **GitHub Operations**: To be performed by repository owner
- **Code Updates**: Automated via this PR
- **Team Migration**: After GitHub operations complete

## Contact

For questions or issues with the migration, please contact the repository maintainers.
