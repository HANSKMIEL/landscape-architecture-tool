# VPS SSH, User, and Secrets Verification Guide

## Overview

This guide documents the SSH, user configuration, and secrets management verification that has been integrated into the VPS clean reinstall process. The enhanced scripts now automatically verify and report on the security and configuration status of your VPS deployment.

## What Gets Verified

### 1. SSH Configuration

#### SSH Service Status
- ✅ Checks if SSH daemon (sshd/ssh) is running
- ✅ Verifies service is active and accessible

#### SSH Key Authentication
- ✅ Verifies `/root/.ssh` directory exists
- ✅ Checks for `authorized_keys` file
- ✅ Reports number of SSH keys configured
- ✅ Validates file permissions (700 for .ssh, 600 for authorized_keys)

**Expected Setup:**
```bash
/root/.ssh/                     # drwx------ (700)
/root/.ssh/authorized_keys      # -rw------- (600)
```

### 2. User Configuration

#### System Users
- ✅ Verifies `www-data` user exists (required for web services)
- ✅ Checks if running with root privileges
- ✅ Validates user permissions for application directories

#### Application Ownership
- ✅ Ensures `/var/www/landscape-architecture-tool` owned by `www-data:www-data`
- ✅ Verifies executable permissions on scripts

### 3. Secrets Management

#### Environment Variables (.env)
- ✅ Checks `.env` file exists
- ✅ Verifies file permissions (should be 600 or 400)
- ✅ Validates critical secrets are configured:
  - `SECRET_KEY` (not using default value)
  - `DATABASE_URL` (if using PostgreSQL)
  - `JWT_SECRET_KEY`

#### Secrets Backup
- ✅ Checks `/root/.secrets` directory exists
- ✅ Verifies JWT secret backup at `/root/.secrets/jwt_secret.txt`
- ✅ Ensures backup has secure permissions (600)

**Expected Structure:**
```bash
/var/www/landscape-architecture-tool/.env    # -rw------- (600)
/root/.secrets/                              # drwx------ (700)
/root/.secrets/jwt_secret.txt                # -rw------- (600)
```

## Enhanced Script Features

### VPS Clean Reinstall Script (`vps_clean_reinstall.sh`)

#### New Verification Steps

**Step 5: Configuration Verification**
```bash
# Automatically checks:
- .env file exists and is restored from backup
- SECRET_KEY is configured (not default)
- DATABASE_URL is set
- Critical environment variables are present
```

**Step 12: Enhanced Installation Verification**
```bash
# Now includes:
- SSH service status
- SSH key authentication setup
- www-data user existence
- Secrets backup directory
- .env file security (permissions)
- Root privilege verification
```

### VPS Deployment Test Script (`vps_deployment_test.sh`)

#### New Tests Added

**Test 11: SSH and User Configuration**
- SSH service running
- www-data user exists
- `/root/.ssh` directory configured
- SSH keys in authorized_keys
- SSH key count reporting

**Test 12: Secrets and Configuration Security**
- `.env` file exists
- `.env` file has secure permissions
- `SECRET_KEY` is configured (not default)
- Secrets backup directory exists
- Critical secrets validation

## Usage

### Running the Enhanced Reinstall

```bash
# Standard execution (includes all verifications)
ssh root@72.60.176.200 "bash <(curl -fsSL https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_clean_reinstall.sh)"
```

### Running Comprehensive Tests

```bash
# Run full test suite including SSH/secrets tests
ssh root@72.60.176.200
cd /tmp
curl -O https://raw.githubusercontent.com/HANSKMIEL/landscape-architecture-tool/V1.00D/scripts/vps_deployment_test.sh
chmod +x vps_deployment_test.sh
./vps_deployment_test.sh
```

Expected output will include:
```
=== Test 11: SSH and User Configuration ===
✅ PASS: SSH service is running
✅ PASS: www-data user exists
✅ PASS: /root/.ssh directory exists
✅ PASS: SSH authorized_keys configured (2 keys)

=== Test 12: Secrets and Configuration Security ===
✅ PASS: .env file exists
✅ PASS: .env file has secure permissions (600)
✅ PASS: SECRET_KEY is configured
✅ PASS: Secrets backup directory exists
```

## Setup Requirements

### Initial SSH Configuration

Before running the reinstall script, ensure SSH key authentication is properly configured:

#### 1. Generate SSH Key (if not already done)
```bash
ssh-keygen -t ed25519 -C "deployment@landscape-tool"
```

#### 2. Add Public Key to VPS
```bash
# SSH into VPS
ssh root@72.60.176.200

# Add your public key
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAA... your-key-here" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### 3. Test SSH Key Authentication
```bash
ssh -i ~/.ssh/id_ed25519 root@72.60.176.200
```

### Initial Secrets Setup

The reinstall script will preserve existing secrets, but for initial setup:

#### 1. Create .env File
```bash
cd /var/www/landscape-architecture-tool
cp .env.example .env
chmod 600 .env
```

#### 2. Generate Secure Secrets
```bash
# Generate SECRET_KEY
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Generate JWT_SECRET_KEY
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

#### 3. Update .env with Generated Secrets
```bash
nano /var/www/landscape-architecture-tool/.env

# Set:
SECRET_KEY=<generated-secret-key>
JWT_SECRET_KEY=<generated-jwt-secret-key>
DATABASE_URL=sqlite:///landscape_architecture_prod.db
```

#### 4. Create Secrets Backup
```bash
mkdir -p /root/.secrets
chmod 700 /root/.secrets

# Backup JWT secret
grep "^JWT_SECRET_KEY=" /var/www/landscape-architecture-tool/.env | cut -d'=' -f2 > /root/.secrets/jwt_secret.txt
chmod 600 /root/.secrets/jwt_secret.txt
```

## Verification Checklist

After running the reinstall script, verify:

- [ ] SSH service is active: `systemctl status sshd`
- [ ] SSH keys configured: `ls -la /root/.ssh/`
- [ ] Can SSH with key: `ssh -i ~/.ssh/key root@72.60.176.200`
- [ ] www-data user exists: `id www-data`
- [ ] .env file exists: `ls -la /var/www/landscape-architecture-tool/.env`
- [ ] .env permissions are 600: `stat -c "%a" /var/www/landscape-architecture-tool/.env`
- [ ] SECRET_KEY is set: `grep SECRET_KEY /var/www/landscape-architecture-tool/.env`
- [ ] Secrets backup exists: `ls -la /root/.secrets/`
- [ ] Application runs: `curl http://localhost:5000/health`

## Troubleshooting

### SSH Key Authentication Not Working

**Problem**: SSH still asks for password

**Solution**:
```bash
# 1. Check SSH config on VPS
sudo nano /etc/ssh/sshd_config

# Ensure these are set:
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# 2. Restart SSH
sudo systemctl restart sshd

# 3. Check file permissions
ls -la ~/.ssh/
# Should show: drwx------ for .ssh
# Should show: -rw------- for authorized_keys

# 4. Fix permissions if needed
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### .env File Permissions Warning

**Problem**: Test reports incorrect .env permissions

**Solution**:
```bash
chmod 600 /var/www/landscape-architecture-tool/.env
chown www-data:www-data /var/www/landscape-architecture-tool/.env
```

### SECRET_KEY Using Default Value

**Problem**: Test reports SECRET_KEY is default value

**Solution**:
```bash
# Generate new secret
NEW_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Update .env
sed -i "s/^SECRET_KEY=.*/SECRET_KEY=${NEW_SECRET}/" /var/www/landscape-architecture-tool/.env

# Restart application
systemctl restart landscape-backend
```

### www-data User Not Found

**Problem**: Test reports www-data user doesn't exist

**Solution**:
```bash
# Create www-data user (usually created by Apache/Nginx)
sudo useradd -r -s /usr/sbin/nologin www-data

# Or install nginx which creates it
sudo apt install nginx
```

## Security Best Practices

### SSH Security
1. ✅ Use SSH key authentication (disable password auth after testing)
2. ✅ Use ed25519 or RSA 4096-bit keys
3. ✅ Regularly rotate SSH keys
4. ✅ Limit SSH access to specific IPs if possible
5. ✅ Monitor SSH login attempts: `grep "Failed password" /var/log/auth.log`

### Secrets Management
1. ✅ Never commit .env files to git
2. ✅ Use secure random values for all secrets
3. ✅ Rotate secrets regularly (at least every 90 days)
4. ✅ Keep backup of secrets in secure location
5. ✅ Use environment-specific secrets (dev/staging/prod)

### File Permissions
1. ✅ .env files should be 600 (rw-------)
2. ✅ .ssh directory should be 700 (rwx------)
3. ✅ authorized_keys should be 600 (rw-------)
4. ✅ Application files owned by www-data
5. ✅ Log files should be 640 (rw-r-----)

## Integration with V1.00D Branch

### How It Works

The enhanced verification is built into the V1.00D branch deployment workflow:

1. **Backup Phase**: Preserves existing .env and secrets
2. **Clone Phase**: Fetches fresh code from V1.00D branch
3. **Restore Phase**: Restores secrets and validates configuration
4. **Verification Phase**: Runs comprehensive SSH/user/secrets tests
5. **Reporting Phase**: Logs all verification results

### Accessing Verification Logs

```bash
# View reinstall log with verification results
tail -f /var/log/landscape-reinstall.log

# Check for verification warnings
grep "⚠️" /var/log/landscape-reinstall.log

# Check for verification errors
grep "❌" /var/log/landscape-reinstall.log
```

## Expected Test Results

### All Tests Passing
```
📊 Test Summary
═══════════════════════════════════════
✅ SSH service is running
✅ www-data user exists
✅ /root/.ssh directory exists
✅ SSH authorized_keys configured (2 keys)
✅ .env file exists
✅ .env file has secure permissions (600)
✅ SECRET_KEY is configured
✅ Secrets backup directory exists

Total Tests: 12
Passed: 12
Failed: 0

🎉 All tests passed!
```

### Some Warnings (Acceptable)
```
📊 Test Summary
═══════════════════════════════════════
✅ SSH service is running
✅ www-data user exists
⚠️ SSH key authentication not configured
✅ .env file exists
✅ .env file has secure permissions (600)
✅ SECRET_KEY is configured
⚠️ Secrets backup not configured

Total Tests: 12
Passed: 10
Failed: 0
Warnings: 2

⚠️ Some tests had warnings. Review the output above.
```

## Automated Verification

The verification runs automatically during:

1. **VPS Clean Reinstall**: Step 12 includes all verifications
2. **Deployment Testing**: Tests 11 and 12 verify SSH/secrets
3. **Health Monitoring**: Can be scheduled via cron

### Scheduled Verification (Optional)

Add to crontab to run daily checks:
```bash
crontab -e

# Add this line for daily 2 AM verification
0 2 * * * /var/www/landscape-architecture-tool/scripts/vps_deployment_test.sh >> /var/log/deployment-verification.log 2>&1
```

## Summary

The enhanced VPS deployment scripts now provide comprehensive verification of:

✅ **SSH Configuration** - Service status, key authentication, file permissions
✅ **User Setup** - www-data user, root privileges, file ownership  
✅ **Secrets Management** - .env security, secret configuration, backup status

This ensures that every deployment to the V1.00D branch includes proper security configuration and helps catch configuration issues early.

For more information, see:
- `docs/VPS_CLEAN_REINSTALL_GUIDE.md` - Detailed deployment guide
- `docs/VPS_QUICK_REFERENCE.md` - Quick command reference
- `archive/vps-config/ssh_key_setup_instructions.md` - SSH setup details

---

**Last Updated**: October 2024  
**Version**: 1.1.0 (Enhanced with SSH/User/Secrets verification)
