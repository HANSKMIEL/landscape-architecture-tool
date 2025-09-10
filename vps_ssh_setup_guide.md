# VPS SSH Setup and Troubleshooting Guide

## Current Issue
The deployment workflow is failing because SSH key authentication is not properly configured on the VPS (72.60.176.200). The connection is asking for a password instead of using the SSH key stored in GitHub secrets.

## Required Actions

### 1. SSH Key Setup on VPS
The VPS needs to be configured to accept SSH key authentication. This requires:

1. **Generate SSH Key Pair** (if not already done):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@landscape-tool"
   ```

2. **Add Public Key to VPS**:
   - Copy the public key content
   - SSH into VPS with password: `ssh ubuntu@72.60.176.200`
   - Add key to authorized_keys:
     ```bash
     mkdir -p ~/.ssh
     chmod 700 ~/.ssh
     echo "YOUR_PUBLIC_KEY_CONTENT" >> ~/.ssh/authorized_keys
     chmod 600 ~/.ssh/authorized_keys
     ```

3. **Configure SSH on VPS**:
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
   Ensure these settings:
   ```
   PubkeyAuthentication yes
   AuthorizedKeysFile .ssh/authorized_keys
   PasswordAuthentication yes  # Keep enabled for backup access
   ```

4. **Restart SSH Service**:
   ```bash
   sudo systemctl restart sshd
   ```

### 2. GitHub Secrets Configuration
The private key needs to be stored in GitHub secrets:

1. **VPS_SSH_KEY**: The complete private key content (including headers)
2. **VPS_USER**: ubuntu
3. **VPS_HOST**: 72.60.176.200

### 3. Test SSH Connection
Test the connection locally:
```bash
ssh -i /path/to/private/key ubuntu@72.60.176.200
```

## VPS Directory Structure
Based on the workflow, the expected structure is:
```
/var/www/landscape-tool/
├── backend/          # Backend application files
├── frontend/         # Frontend static files  
└── data/            # Database and user data
    ├── app.db       # SQLite database
    └── backups/     # Backup files
```

## Workflow Requirements
The deployment workflow expects:
- SSH key authentication working
- User `ubuntu` has sudo privileges
- Nginx installed and configured
- Python 3.12 environment available
- Node.js 20 for frontend builds

## Troubleshooting Steps

### If SSH Key Authentication Fails:
1. Check SSH key format in GitHub secrets
2. Verify public key is in VPS authorized_keys
3. Check SSH service configuration
4. Verify file permissions (700 for .ssh, 600 for authorized_keys)

### If Deployment Paths Don't Exist:
1. Create required directories on VPS
2. Set proper ownership (www-data for web files)
3. Configure Nginx to serve from correct paths

### If Services Don't Restart:
1. Check if systemd services exist
2. Verify service configurations
3. Check logs: `journalctl -u nginx` or `journalctl -u your-backend-service`

## Next Steps
1. Fix SSH key authentication on VPS
2. Verify all required directories exist
3. Test the deployment workflow
4. Monitor deployment logs for any remaining issues
