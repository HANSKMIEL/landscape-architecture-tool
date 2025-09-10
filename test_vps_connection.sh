#!/bin/bash
# VPS Connection and Setup Test Script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored status messages
print_status() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# VPS connection details
VPS_HOST="72.60.176.200"
VPS_USER="ubuntu"

print_status "Testing VPS connection and setup..."

# Test 1: Basic connectivity
print_status "Testing basic connectivity to VPS..."
if ping -c 3 $VPS_HOST > /dev/null 2>&1; then
    print_status "✅ VPS is reachable"
else
    print_error "❌ VPS is not reachable"
    exit 1
fi

# Test 2: SSH connectivity (will prompt for password if key auth fails)
print_status "Testing SSH connectivity..."
echo "Note: If prompted for password, SSH key authentication is not configured"

# Test SSH connection with timeout
timeout 10 ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "echo 'SSH connection successful'" 2>/dev/null
SSH_RESULT=$?

if [ $SSH_RESULT -eq 0 ]; then
    print_status "✅ SSH connection successful"
    
    # Test 3: Check required directories
    print_status "Checking required directories on VPS..."
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
        echo 'Checking directory structure...'
        
        # Check if directories exist
        if [ -d '/var/www/landscape-tool' ]; then
            echo '✅ /var/www/landscape-tool exists'
        else
            echo '❌ /var/www/landscape-tool does not exist'
            echo 'Creating directory...'
            sudo mkdir -p /var/www/landscape-tool/{backend,frontend,data/backups}
            sudo chown -R ubuntu:ubuntu /var/www/landscape-tool
            echo '✅ Created directory structure'
        fi
        
        # Check services
        echo 'Checking services...'
        if systemctl is-active --quiet nginx; then
            echo '✅ Nginx is running'
        else
            echo '❌ Nginx is not running'
        fi
        
        # Check Python
        if command -v python3 > /dev/null; then
            echo '✅ Python3 is available'
            python3 --version
        else
            echo '❌ Python3 is not available'
        fi
        
        # Check Node.js
        if command -v node > /dev/null; then
            echo '✅ Node.js is available'
            node --version
        else
            echo '❌ Node.js is not available'
        fi
        
        echo 'VPS setup check complete!'
    " 2>/dev/null
    
elif [ $SSH_RESULT -eq 124 ]; then
    print_error "❌ SSH connection timed out"
    print_warning "This usually means SSH key authentication is not configured"
else
    print_error "❌ SSH connection failed"
    print_warning "SSH key authentication may not be configured properly"
fi

print_status "VPS connection test complete!"
print_warning "If SSH key authentication failed, please refer to vps_ssh_setup_guide.md"
