# V1.00D DevDeploy Workflow Solution

## Issue Summary

**Problem**: The repository had no automatic deployment workflow for the V1.00D branch, causing confusion when trying to deploy to the VPS DevDeploy environment. The issue reported SSH authentication failures for a workflow that didn't exist.

**Root Cause**: The V1.00D branch only had CI/CD testing (`v1-development.yml`) but no deployment workflow to actually deploy changes to the VPS.

## Solution Implemented

### 1. Created V1.00D DevDeploy Workflow

**File**: `.github/workflows/v1-devdeploy.yml`

A complete automated deployment workflow that:
- Triggers automatically when code is pushed to V1.00D branch
- Can be manually triggered via GitHub Actions UI
- Validates deployment configuration before deploying
- Builds the frontend (React/Vite)
- Deploys to VPS at 72.60.176.200:8080
- Creates backups before deployment
- Runs health checks to verify deployment success

**Key Features**:
- ✅ SSH key authentication with comprehensive error handling
- ✅ Automatic data backup (database and uploads)
- ✅ Incremental deployment using rsync (preserves user data)
- ✅ Health checks with retry logic
- ✅ Detailed troubleshooting guides in error messages
- ✅ Support for manual trigger with skip_tests option

### 2. Created Comprehensive Documentation

**File**: `docs/V1_DEVDEPLOY_WORKFLOW.md`

Complete documentation covering:
- Workflow overview and architecture
- Required GitHub secrets configuration
- SSH authentication setup and troubleshooting
- VPS directory structure
- Manual deployment instructions
- Common issues and solutions

## What You Need to Do

### Step 1: Configure SSH Key on VPS

The workflow uses SSH key authentication. You need to add the public key to your VPS:

```bash
# 1. Generate public key from your VPS_SSH_KEY secret
ssh-keygen -y -f /path/to/your/private_key > public_key.pub

# 2. Add public key to VPS
ssh ubuntu@72.60.176.200  # or root@72.60.176.200
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo 'YOUR_PUBLIC_KEY_CONTENT_HERE' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 3. Verify SSH configuration
sudo nano /etc/ssh/sshd_config
# Ensure these lines:
#   PubkeyAuthentication yes
#   AuthorizedKeysFile .ssh/authorized_keys

# 4. Restart SSH service
sudo systemctl restart sshd
```

### Step 2: Verify GitHub Secrets

Ensure these secrets are configured in your repository settings:

- `VPS_SSH_KEY` - Your private SSH key (complete content including headers)
- `VPS_USER` - SSH username (`ubuntu` or `root`)
- `VPS_HOST` - VPS IP address (`72.60.176.200`)

### Step 3: Test the Workflow

**Option A: Automatic Deployment**
- Push any change to the V1.00D branch
- The workflow will trigger automatically

**Option B: Manual Deployment**
1. Go to GitHub repository → Actions tab
2. Select "V1.00D DevDeploy Deployment"
3. Click "Run workflow"
4. Select branch: V1.00D
5. Click "Run workflow"

### Step 4: Monitor Deployment

1. Watch the workflow run in GitHub Actions
2. If SSH fails, the workflow will display a detailed troubleshooting guide
3. Once successful, verify at: http://72.60.176.200:8080/health

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ V1.00D DevDeploy Deployment Workflow                        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │ Pre-Deployment Validation      │
         │ - Validate files exist         │
         │ - Run quick tests (optional)   │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │ Deploy to VPS DevDeploy        │
         │ 1. Build frontend              │
         │ 2. Setup SSH                   │
         │ 3. Test connection             │
         │ 4. Backup data                 │
         │ 5. Deploy backend              │
         │ 6. Deploy frontend             │
         │ 7. Install dependencies        │
         │ 8. Run migrations              │
         │ 9. Restart services            │
         │ 10. Health check               │
         └────────────────────────────────┘
                          │
                          ▼
                    ┌─────────┐
                    │ Success │
                    └─────────┘
```

## Troubleshooting

### SSH Connection Fails

**Error**: `Permission denied (publickey,password)`

**Solution**: Follow Step 1 above to configure SSH keys on VPS

**Helpful Command**: Test SSH manually:
```bash
ssh -i /path/to/private_key ubuntu@72.60.176.200
```

### Health Check Fails

**Error**: Health check timeout after deployment

**Solutions**:
1. SSH into VPS and check logs:
   ```bash
   tail -50 /var/www/landscape-architecture-tool/data/error.log
   ```

2. Verify gunicorn is running:
   ```bash
   ps aux | grep gunicorn
   ```

3. Check if port 8080 is accessible:
   ```bash
   curl http://localhost:8080/health
   ```

### Services Don't Start

**Solutions**:
1. Check if dependencies are installed:
   ```bash
   cd /var/www/landscape-architecture-tool/backend
   source venv/bin/activate
   pip list
   ```

2. Try starting manually:
   ```bash
   cd /var/www/landscape-architecture-tool/backend
   source venv/bin/activate
   gunicorn -b 0.0.0.0:8080 src.main:app
   ```

## Files Created

1. `.github/workflows/v1-devdeploy.yml` - The deployment workflow
2. `docs/V1_DEVDEPLOY_WORKFLOW.md` - Comprehensive documentation
3. `docs/V1_DEVDEPLOY_SOLUTION.md` - This solution guide

## Related Resources

- **SSH Setup Guide**: `archive/vps-config/vps_ssh_setup_guide.md`
- **Deployment Guide**: `docs/HOSTINGER_DEPLOYMENT_GUIDE.md`
- **Manual Deploy Workflow**: `.github/workflows/manual-deploy.yml`
- **V1 Development CI**: `.github/workflows/v1-development.yml`

## Next Steps

1. ✅ Configure SSH key on VPS (Step 1 above)
2. ✅ Verify GitHub secrets (Step 2 above)
3. ✅ Test deployment (Step 3 above)
4. ✅ Monitor and verify (Step 4 above)

Once SSH authentication is working, the workflow will handle everything else automatically!

## Support

If you encounter issues:
1. Check the workflow logs in GitHub Actions for detailed error messages
2. Review the SSH troubleshooting section in the workflow output
3. Consult `docs/V1_DEVDEPLOY_WORKFLOW.md` for detailed information
4. Check VPS logs at `/var/www/landscape-architecture-tool/data/error.log`

---

**Status**: ✅ Workflow created and validated
**Tested**: YAML syntax validated, structure verified
**Ready**: For SSH key configuration and deployment
