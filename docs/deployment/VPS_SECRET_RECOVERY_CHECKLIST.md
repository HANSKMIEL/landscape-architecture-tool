# VPS Secret Recovery Checklist

When GitHub Actions loses access to the VPS (for example after a credential rotation or if secrets were cleared), run through this checklist to restore deployments quickly and safely.

## 1. Regenerate and register the SSH key

1. **Generate an Ed25519 key pair** on a secure workstation:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions@landscape-tool" -f vps_dev_deploy
   ```
2. **Add the public key** (`vps_dev_deploy.pub`) to the VPS `~/.ssh/authorized_keys` for the deployment user (`root` by default).
   - Via Hostinger panel: VPS → Manage → SSH Access → *Add key*
   - Via CLI:
     ```bash
     ssh-copy-id -i vps_dev_deploy.pub root@72.60.176.200
     ```
3. **Store the private key** (`vps_dev_deploy`) in GitHub repository secrets:
   - Settings → Secrets and variables → Actions
   - Secret name: `VPS_SSH_KEY`
   - Secret value: full contents of the private key file (including BEGIN/END lines)

## 2. Verify companion secrets

| Secret            | Expected value                | Notes                                   |
|-------------------|-------------------------------|-----------------------------------------|
| `VPS_USER`        | `root` (or custom username)   | Falls back to `root` in workflows       |
| `VPS_HOST`        | `72.60.176.200`               | Adjust if the VPS IP changed            |
| `STAGING_URL`     | Optional                      | Used in status notifications            |
| `PRODUCTION_URL`  | Optional                      | Required only for production workflows  |

## 3. Test connectivity from GitHub Actions

After updating secrets, trigger either the **“Manual Deploy to VPS (Improved)”** workflow with only the connectivity step enabled, or the dedicated **“VPS Diagnostic Check”** workflow:

1. Navigate to **Actions → VPS Diagnostic Check**.
2. Dispatch the workflow and confirm the steps `Setup SSH Key` and `Run Remote Diagnostic` complete successfully. The diagnostic script prints detailed SSH output; look for lines starting with `✅` and the final "Frontend accessible externally"/"Backend accessible externally" checks.
3. Alternatively, run **Actions → Manual Deploy to VPS (Improved)** with both `deploy_frontend` and `deploy_backend` set to **false** so only the connectivity verification executes, and confirm the `Test VPS connectivity` step logs `SSH connection successful`.

If you prefer to verify locally:
```bash
ssh -i vps_dev_deploy root@72.60.176.200 "echo 'Connection successful'"
```

## 4. Validate local environment access (optional)

If you deploy manually from your workstation, ensure your personal SSH key still exists and is registered on the VPS. Re-run `ssh-add` if needed:
```bash
ssh-add ~/.ssh/id_ed25519
ssh root@72.60.176.200
```

## 5. Re-run the automated validator

After secrets are restored, run the quick validator locally to ensure dynamic PR analysis and deployment checks succeed:
```powershell
Set-Location "c:\Users\jaapp\OneDrive\Desktop\02 SOFTWARE_DEV\20250610 GITHUB CLONE\landscape-architecture-tool"
$env:GITHUB_TOKEN = "<personal token with repo scope>"
python scripts/testing/automated_validation.py --quick
```

If you prefer to disable dynamic PR analysis locally, export `VALIDATOR_SKIP_PR_ANALYSIS=1` before running the validator.

## 6. Update secret rotation log

Document the new key in `.github/SECRETS_REQUIRED.md` or your internal runbook, including the generation date and responsible engineer. Set a reminder to rotate the key within 90 days.

---

**Tip:** Add a lightweight scheduled job (for example, `.github/workflows/validate-secrets.yml`) to check for missing secrets and alert the team before a deployment fails.
