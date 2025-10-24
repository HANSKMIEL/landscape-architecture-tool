# GitHub Branch Rename Instructions

## ⚠️ IMPORTANT: Repository Owner Action Required

This file contains instructions for **manual operations** that must be performed by a repository administrator through the GitHub web interface. These operations **cannot** be automated due to GitHub API limitations.

## Prerequisites

- Admin access to the HANSKMIEL/landscape-architecture-tool repository
- All open PRs should be noted (they may need retargeting after the rename)
- Team members should be notified in advance

## Step-by-Step Instructions

### Step 1: Rename "main" to "Archive-main"

1. Navigate to: https://github.com/HANSKMIEL/landscape-architecture-tool/settings/branches
2. Locate the "main" branch in the branch list
3. Click the pencil icon (✏️) or "Rename branch" button next to "main"
4. Enter new name: `Archive-main`
5. Read the warning about impacts
6. Click "Rename branch" to confirm

**Expected Result:** The main branch is now called "Archive-main"

### Step 2: Rename "V1.00D" to "main"

1. Still in Settings → Branches
2. Locate the "V1.00D" branch in the branch list
3. Click the pencil icon (✏️) or "Rename branch" button next to "V1.00D"
4. Enter new name: `main`
5. Read the warning about impacts
6. Click "Rename branch" to confirm

**Expected Result:** The V1.00D branch is now called "main"

### Step 3: Update Default Branch

1. Still in Settings → Branches
2. Look for the "Default branch" section at the top
3. Click the switch icon (⇄) or "Switch to another branch" button
4. Select `main` from the dropdown (this is the newly renamed branch, formerly V1.00D)
5. Click "Update" or "I understand, update the default branch"

**Expected Result:** The default branch is now "main" (which contains the former V1.00D content)

### Step 4: Update Branch Protection Rules (If Applicable)

If you have branch protection rules:

1. Check existing rules under Settings → Branches → Branch protection rules
2. If there are rules for "Archive-main" (formerly main), decide if you want to keep them
3. Set up appropriate protection rules for the new "main" branch:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date before merging
   - Include administrators (or not, based on your preference)

### Step 5: Verify the Changes

1. Go to the main repository page: https://github.com/HANSKMIEL/landscape-architecture-tool
2. Verify the default branch shown is "main"
3. Check that the branch dropdown shows:
   - main (default)
   - Archive-main
   - Other branches...
4. Open a test file on main branch and verify it contains V1.00D content (not old main content)

## Post-Rename Actions

### Immediate Actions

1. **Notify Team Members**
   - Send notification that branch rename is complete
   - Share the migration guide: `docs/BRANCH_MIGRATION_GUIDE.md`
   - Ensure everyone updates their local repositories

2. **Update Open PRs**
   - Review all open pull requests
   - Update PR base branches if they were targeting the old main
   - Leave comments on PRs explaining the branch rename

3. **Merge This PR**
   - Once the GitHub operations are complete, merge the PR that updates all code references
   - This ensures CI/CD workflows and documentation are synchronized

### Verify Deployments

After the changes:

1. Check that CI/CD workflows trigger correctly on the new main branch
2. Verify VPS deployment (http://72.60.176.200:8080) continues to work
3. Monitor for any unexpected issues

## Troubleshooting

### Issue: "Cannot rename default branch"
**Solution:** First change the default branch to a different branch (e.g., Archive-main or a temporary branch), then rename main, then rename V1.00D to main, then set main as default.

### Issue: "Branch protection rules prevent rename"
**Solution:** Temporarily disable branch protection rules, perform the rename, then re-enable them for the new branch name.

### Issue: "Open PRs are now targeting the wrong branch"
**Solution:** Each PR needs to be manually updated to target the correct base branch. Use GitHub's "Edit" button on the PR to change the base branch.

## Verification Checklist

After completing all steps, verify:

- [ ] "main" branch exists and contains former V1.00D content
- [ ] "Archive-main" branch exists and contains former main content
- [ ] Default branch is set to "main"
- [ ] Branch protection rules are correctly configured
- [ ] Team members have been notified
- [ ] Open PRs have been reviewed and updated if needed
- [ ] CI/CD workflows trigger on the new main branch
- [ ] Deployment continues to work

## Need Help?

If you encounter issues:
1. Check GitHub's documentation on renaming branches
2. Contact GitHub Support if technical issues arise
3. Review the full migration guide: `docs/BRANCH_MIGRATION_GUIDE.md`

## After Completion

Once these manual steps are complete:
1. Update this file to mark completion date
2. Merge the PR that updates code references
3. Archive this instruction file or move to a "completed-migrations" folder

---

**Completion Status:** ⏳ Pending

**Completed By:** _________________

**Completion Date:** _________________

**Notes:**
