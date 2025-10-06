# GitHub Secrets Configuration for DevDeploy Deployment

This document describes all required GitHub secrets for the V1.00D DevDeploy deployment workflow.

## Required Secrets

Navigate to your repository: **Settings → Secrets and variables → Actions**

### Core VPS Access Secrets

#### `VPS_SSH_KEY` (REQUIRED)
- **Description**: Private SSH key for authenticating with the VPS
- **Format**: Complete private key content including header and footer
- **Example**:
  ```
  -----BEGIN OPENSSH PRIVATE KEY-----
  b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
  ... (your key content) ...
  -----END OPENSSH PRIVATE KEY-----
  ```
- **How to obtain**:
  ```bash
  # Generate new SSH key pair
  ssh-keygen -t rsa -b 4096 -C "github-actions@landscape-tool" -f ~/.ssh/landscape_deploy
  
  # Copy private key content (add to GitHub secret)
  cat ~/.ssh/landscape_deploy
  
  # Copy public key content (add to VPS authorized_keys)
  cat ~/.ssh/landscape_deploy.pub
  ```

#### `VPS_HOST` (OPTIONAL)
- **Description**: VPS hostname or IP address
- **Default**: `72.60.176.200`
- **Format**: IP address or domain name
- **Example**: `72.60.176.200`

#### `VPS_USER` (OPTIONAL)
- **Description**: VPS user for SSH connection
- **Default**: `root`
- **Format**: Username string
- **Example**: `root` or `ubuntu`

## SSH Key Setup Instructions

### Step 1: Generate SSH Key Pair (Local Machine)

```bash
# Generate a new SSH key specifically for deployment
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy@landscape-tool"

# When prompted:
# - Save to: ~/.ssh/landscape_deploy (or your preferred name)
# - Passphrase: Leave empty for automated deployment
```

This creates two files:
- `~/.ssh/landscape_deploy` (private key) → Goes to GitHub Secrets
- `~/.ssh/landscape_deploy.pub` (public key) → Goes to VPS

### Step 2: Add Public Key to VPS

**Important**: Your VPS at 72.60.176.200 has SSH configured with `PermitRootLogin yes`, which allows root user login via SSH keys. This is the expected configuration for the deployment workflow.

Connect to your VPS and add the public key:

```bash
# Connect to VPS (you may need password for first connection)
ssh root@72.60.176.200

# Create SSH directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add your public key to authorized_keys
# Replace with actual public key content from step 1
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ... github-actions-deploy@landscape-tool" >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys

# Verify SSH configuration allows key authentication
sudo nano /etc/ssh/sshd_config
```

The VPS SSH configuration should have these settings (verify with `cat /etc/ssh/sshd_config`):
```
# Public key authentication (default: yes, can be commented)
PubkeyAuthentication yes

# Authorized keys file location (default)
AuthorizedKeysFile .ssh/authorized_keys

# Root login via SSH key (required for deployment)
PermitRootLogin yes

# Password authentication (default: yes, can be commented)
# PasswordAuthentication yes
```

**Note**: The VPS has `PermitRootLogin yes` configured, which allows root login via SSH keys. This is required for the deployment workflow to function properly.

If you need to restart SSH service after changes:
```bash
sudo systemctl restart sshd
# Or on some systems:
sudo systemctl restart ssh
```

### Step 3: Test SSH Key Authentication

From your local machine:

```bash
# Test connection with key
ssh -i ~/.ssh/landscape_deploy root@72.60.176.200

# If successful, you should connect without password prompt
```

### Step 4: Add Private Key to GitHub Secrets

1. Copy the complete private key content:
   ```bash
   cat ~/.ssh/landscape_deploy
   ```

2. Go to your GitHub repository:
   - Navigate to: **Settings → Secrets and variables → Actions**
   - Click: **New repository secret**
   - Name: `VPS_SSH_KEY`
   - Value: Paste the complete private key (including BEGIN and END lines)
   - Click: **Add secret**

### Step 5: Verify Secrets Configuration

Check that these secrets are configured:

| Secret Name | Status | Notes |
|------------|--------|-------|
| `VPS_SSH_KEY` | ✅ Required | Complete private key content |
| `VPS_HOST` | ⚪ Optional | Defaults to `72.60.176.200` |
| `VPS_USER` | ⚪ Optional | Defaults to `root` |

## Firewall Configuration

### Allow GitHub Actions IP Ranges

GitHub Actions runners use dynamic IP addresses. You have two options:

#### Option 1: Allow All IPs (Testing)
```bash
# On VPS - temporarily allow all SSH connections
sudo ufw allow 22/tcp
```

#### Option 2: Restrict to GitHub IP Ranges (Production)
```bash
# On VPS - allow GitHub Actions IP ranges
# GitHub publishes their IP ranges at: https://api.github.com/meta

# Example commands (update with current ranges):
sudo ufw allow from 140.82.112.0/20 to any port 22
sudo ufw allow from 143.55.64.0/20 to any port 22
sudo ufw allow from 185.199.108.0/22 to any port 22
```

#### Verify Firewall Status
```bash
# Check firewall status
sudo ufw status verbose

# Check SSH port is open
sudo netstat -tlnp | grep :22
```

## Troubleshooting

### SSH Connection Fails

**Error**: "Permission denied (publickey)"

**Solutions**:
1. Verify private key is correctly formatted in GitHub secret (check BEGIN/END lines)
2. Verify public key is in VPS `~/.ssh/authorized_keys`
3. Check file permissions on VPS:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```
4. Check SSH daemon allows key authentication

### Firewall Blocking Connection

**Error**: "Connection timed out"

**Solutions**:
1. Verify firewall allows port 22:
   ```bash
   sudo ufw status | grep 22
   ```
2. Temporarily disable firewall for testing:
   ```bash
   sudo ufw disable  # Only for testing!
   ```
3. Check SSH service is running:
   ```bash
   sudo systemctl status sshd
   ```

### VPS Not Responding

**Solutions**:
1. Verify VPS is online and accessible
2. Check VPS resource usage (CPU, memory, disk)
3. Review VPS provider's status page
4. Check network connectivity from another location

## Security Best Practices

1. ✅ **Use SSH keys** instead of passwords
2. ✅ **Keep private keys secure** - never commit to repository
3. ✅ **Rotate keys regularly** - generate new keys every 90 days
4. ✅ **Use separate keys** - different keys for different purposes
5. ✅ **Monitor access logs** - review `/var/log/auth.log` regularly
6. ✅ **Limit SSH access** - use firewall rules to restrict IPs
7. ✅ **Keep software updated** - regularly update VPS packages

## Testing the Workflow

Once secrets are configured:

1. Go to your repository on GitHub
2. Navigate to: **Actions** tab
3. Select: **V1.00D DevDeploy Deployment** workflow
4. Click: **Run workflow** button
5. Select branch: `V1.00D`
6. Optionally check: **Force deployment even if tests fail**
7. Click: **Run workflow**
8. Monitor the workflow execution
9. Verify deployment at: http://72.60.176.200:8080

## Additional Resources

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [GitHub Actions IP ranges](https://api.github.com/meta)
- [SSH key authentication guide](https://www.ssh.com/academy/ssh/public-key-authentication)
- [UFW firewall guide](https://help.ubuntu.com/community/UFW)
