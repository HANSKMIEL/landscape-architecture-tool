# Deployment Scripts

This directory contains scripts for deploying and configuring the Landscape Architecture Tool.

## Available Scripts

### `secure_vps_setup.sh`

A script for securely setting up environment variables and security configurations on the VPS.

#### Usage

```bash
# Run on the VPS as root
sudo ./secure_vps_setup.sh
```

#### Features

- Sets up environment variables for the backend
- Generates a secure random JWT secret
- Configures proper file permissions
- Sets up SSH key authentication (optional)
- Creates a backup of sensitive information

#### Requirements

- Root access on the VPS
- OpenSSL installed for generating secure secrets

## Deployment Best Practices

1. **Use SSH key authentication** instead of passwords
2. **Set proper file permissions** for sensitive files
3. **Keep environment variables secure** and separate from code
4. **Regularly rotate secrets** and credentials
5. **Implement proper backup procedures** for configuration files
