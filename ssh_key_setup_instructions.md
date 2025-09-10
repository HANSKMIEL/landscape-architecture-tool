# SSH Key Setup Instructions for VPS Deployment

## Security Notice
For automated deployments, we should use SSH key authentication instead of passwords. This is more secure and allows the GitHub Actions workflow to connect without storing sensitive passwords.

## Step-by-Step SSH Key Setup

### 1. Generate SSH Key Pair (if you don't have one)

On your local machine, generate a new SSH key pair:

```bash
ssh-keygen -t rsa -b 4096 -C "deployment@landscape-tool"
```

When prompted:
- Save it to a specific location (e.g., `~/.ssh/landscape_tool_deploy`)
- You can leave the passphrase empty for automated deployment

This creates two files:
- `~/.ssh/landscape_tool_deploy` (private key)
- `~/.ssh/landscape_tool_deploy.pub` (public key)

### 2. Add Public Key to VPS

Connect to your VPS using the password you provided:

```bash
ssh ubuntu@72.60.176.200
```

Once connected, set up the SSH key:

```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add your public key to authorized_keys
# Replace the content below with your actual public key
echo "ssh-rsa AAAAB3NzaC1yc2E... your-public-key-content-here" >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys
```

### 3. Test SSH Key Authentication

From your local machine, test the SSH key:

```bash
ssh -i ~/.ssh/landscape_tool_deploy ubuntu@72.60.176.200
```

If this works without asking for a password, the SSH key is properly configured.

### 4. Add Private Key to GitHub Secrets

1. Copy the **private key** content:
   ```bash
   cat ~/.ssh/landscape_tool_deploy
   ```

2. Go to your GitHub repository settings:
   - Navigate to Settings → Secrets and variables → Actions
   - Update the `VPS_SSH_KEY` secret with the complete private key content
   - Make sure to include the `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines

### 5. Verify Other GitHub Secrets

Ensure these secrets are properly configured:
- `VPS_HOST`: `72.60.176.200`
- `VPS_USER`: `ubuntu`
- `VPS_BACKEND_PATH`: `/var/www/landscape-tool/backend`
- `VPS_FRONTEND_PATH`: `/var/www/landscape-tool/frontend`
- `DB_PATH`: `data/app.db`
- `BACKEND_SERVICE`: (name of your backend service, if using systemd)

### 6. Prepare VPS Directory Structure

While connected to the VPS, create the required directories:

```bash
sudo mkdir -p /var/www/landscape-tool/{backend,frontend,data/backups}
sudo chown -R ubuntu:ubuntu /var/www/landscape-tool
```

### 7. Install Required Software on VPS

Ensure the VPS has the necessary software:

```bash
# Update system
sudo apt update

# Install Python 3, pip, and venv
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js (for frontend builds if needed)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install and configure Nginx
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 8. Test the Deployment

Once SSH key authentication is working:

1. Go to your GitHub repository
2. Navigate to Actions tab
3. Find "Manual Deploy to VPS" workflow
4. Click "Run workflow"
5. Configure the deployment options:
   - Deploy frontend: ✅
   - Deploy backend: ✅
   - Backup user data: ✅
   - Run tests: ❌ (for first deployment)

## Security Best Practices

1. **Never store passwords in code or GitHub secrets**
2. **Use SSH keys for all automated access**
3. **Regularly rotate SSH keys**
4. **Monitor deployment logs for security issues**
5. **Keep the VPS system updated**

## Troubleshooting

If SSH key authentication still doesn't work:

1. Check SSH configuration on VPS:
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
   Ensure these settings:
   ```
   PubkeyAuthentication yes
   AuthorizedKeysFile .ssh/authorized_keys
   ```

2. Restart SSH service:
   ```bash
   sudo systemctl restart sshd
   ```

3. Check file permissions:
   ```bash
   ls -la ~/.ssh/
   # Should show:
   # drwx------ .ssh/
   # -rw------- authorized_keys
   ```

## Next Steps

After completing this setup:
1. Test SSH key authentication manually
2. Run the deployment workflow
3. Monitor the deployment logs
4. Verify the application is accessible at http://72.60.176.200
