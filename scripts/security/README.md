# Security Scripts

This directory contains security-related scripts for the Landscape Architecture Tool.

## Available Scripts

### `check_credentials.sh`

A security scanning script that detects hardcoded credentials, IP addresses, and other sensitive patterns in your codebase.

#### Usage

```bash
# Scan the entire repository
./check_credentials.sh /path/to/repository

# Scan a specific directory
./check_credentials.sh /path/to/directory
```

#### Features

- Detects passwords, tokens, keys, and other sensitive strings
- Identifies hardcoded IP addresses
- Finds URLs with embedded credentials
- Excludes common directories like node_modules and .git
- Generates a report of potential security issues

#### Best Practices

- Run this script before committing code
- Add it to your CI/CD pipeline as a pre-deployment check
- Address all findings by replacing hardcoded values with environment variables

## Security Best Practices

1. **Never hardcode credentials** in source code
2. **Use environment variables** for all sensitive information
3. **Implement proper access controls** for production environments
4. **Regularly audit** your codebase for security issues
5. **Keep dependencies updated** to avoid security vulnerabilities
