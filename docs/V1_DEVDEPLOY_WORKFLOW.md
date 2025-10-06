# V1.00D DevDeploy Workflow Documentation

## Overview

The V1.00D DevDeploy workflow (`.github/workflows/v1-devdeploy.yml`) provides automated deployment to the VPS DevDeploy environment when changes are pushed to the v1.00D branch.

## Workflow Triggers

The workflow is triggered by:

1. **Automatic**: Push events to the `v1.00D` branch (e.g., when PRs are merged)
2. **Manual**: Via GitHub Actions UI (`workflow_dispatch`)

## Workflow Jobs

### 1. Pre-Deployment Validation

**Purpose**: Validates the deployment configuration and optionally runs tests before deployment.

**Steps**:
- Checkout v1.00D branch
- Validate deployment files exist (src/, main.py, requirements.txt)
- Setup Python 3.12
- Run quick validation tests (unless skipped)

**Timeout**: 10 minutes

### 2. Deploy to VPS DevDeploy

**Purpose**: Deploys the application to the VPS DevDeploy environment.

**Environment**: 
- Name: `devdeploy`
- URL: `http://72.60.176.200:8080`

**Steps**:
1. Checkout v1.00D branch
2. Build frontend (React/Vite)
3. Setup SSH authentication
4. Test SSH connection with detailed error messages
5. Prepare VPS directory structure
6. Backup existing data (database and uploads)
7. Deploy backend files via rsync
8. Deploy frontend build via rsync
9. Install/update backend dependencies in venv
10. Run database migrations
11. Restart services (gunicorn)
12. Health check with retry logic
13. Deployment summary

**Timeout**: 30 minutes

## Required GitHub Secrets

The workflow requires the following secrets to be configured in GitHub repository settings:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `VPS_SSH_KEY` | Private SSH key for authentication | Content of private key file |
| `VPS_USER` | SSH username on VPS | `ubuntu` or `root` |
| `VPS_HOST` | VPS IP address or hostname | `72.60.176.200` |

## SSH Key Authentication

The workflow uses SSH key authentication to connect to the VPS. If SSH authentication fails, the workflow provides a detailed troubleshooting guide in the logs.

### Common SSH Issues and Solutions

#### Issue 1: Permission denied (publickey,password)

**Cause**: The public key corresponding to `VPS_SSH_KEY` is not installed on the VPS.

**Solution**:
```bash
# 1. Generate public key from the private key
ssh-keygen -y -f /path/to/private_key > public_key.pub

# 2. Add public key to VPS
ssh $VPS_USER@$VPS_HOST
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo 'YOUR_PUBLIC_KEY_CONTENT' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 3. Restart SSH service
sudo systemctl restart sshd
```

#### Issue 2: Incorrect file permissions

**Cause**: SSH requires specific permissions on `.ssh` directory and `authorized_keys` file.

**Solution**:
```bash
ssh $VPS_USER@$VPS_HOST
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

#### Issue 3: SSH daemon not configured

**Cause**: SSH daemon doesn't have public key authentication enabled.

**Solution**:
```bash
sudo nano /etc/ssh/sshd_config
# Ensure these lines are present and uncommented:
# PubkeyAuthentication yes
# AuthorizedKeysFile .ssh/authorized_keys

sudo systemctl restart sshd
```

## VPS Directory Structure

The workflow creates and uses the following directory structure on the VPS:

```
/var/www/landscape-architecture-tool/
├── backend/              # Backend application files
│   ├── src/             # Source code
│   ├── venv/            # Python virtual environment
│   └── requirements.txt # Python dependencies
├── frontend/            # Frontend static files (built)
└── data/               # Application data
    ├── app.db          # SQLite database
    ├── backups/        # Backup files
    ├── access.log      # Access logs
    └── error.log       # Error logs
```

## Deployment Process

1. **Frontend Build**: The frontend is built locally in the GitHub Actions runner
2. **File Transfer**: Both frontend and backend are transferred via rsync (preserving existing data)
3. **Dependency Installation**: Backend dependencies are installed in a Python virtual environment on the VPS
4. **Database Migration**: Flask migrations are run to update the database schema
5. **Service Restart**: Gunicorn is restarted to load the new code
6. **Health Check**: The workflow waits for the backend to respond to health checks

## Health Check

The workflow performs health checks by:
- Testing the `/health` endpoint on port 8080
- Retrying up to 10 times with 10-second intervals
- Failing the deployment if health checks don't pass

## Manual Deployment

To manually trigger the workflow:

1. Go to GitHub repository → Actions tab
2. Select "V1.00D DevDeploy Deployment" workflow
3. Click "Run workflow"
4. Select branch: `v1.00D`
5. (Optional) Check "Skip pre-deployment tests" to skip testing
6. Click "Run workflow"

## Troubleshooting

### Deployment Failed: SSH Connection

**Solution**: Follow the SSH setup guide in `archive/vps-config/vps_ssh_setup_guide.md`

### Deployment Failed: Services Not Starting

**Solution**: 
1. SSH into the VPS manually
2. Check error logs: `tail -50 /var/www/landscape-architecture-tool/data/error.log`
3. Check if gunicorn is running: `ps aux | grep gunicorn`
4. Try starting manually: `cd /var/www/landscape-architecture-tool/backend && source venv/bin/activate && gunicorn src.main:app`

### Deployment Failed: Health Check Timeout

**Solution**:
1. Verify the application is running on VPS
2. Check if port 8080 is accessible
3. Review application logs for errors
4. Ensure database and dependencies are properly installed

## Related Documentation

- SSH Setup Guide: `archive/vps-config/vps_ssh_setup_guide.md`
- Deployment Guide: `docs/HOSTINGER_DEPLOYMENT_GUIDE.md`
- Manual Deploy Workflow: `.github/workflows/manual-deploy.yml`

## Workflow History

- **Created**: In response to issue about missing V1.00D DevDeploy workflow
- **Purpose**: Automate deployment to VPS when v1.00D branch is updated
- **Status**: Active

## Notes

- The workflow uses `gunicorn` with 4 workers on port 8080
- Database backups are created before each deployment
- Existing user data (database, uploads) is preserved during deployment
- The workflow has a 30-minute timeout for the deployment job
- Pre-deployment tests can be skipped via manual trigger input
