#!/bin/bash
# Secure VPS Environment Setup Script
# This script sets up environment variables and security configurations on the VPS

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  print_error "Please run as root"
  exit 1
fi

# Prompt for configuration values
read -p "Enter backend directory path [/var/www/landscape-tool/backend]: " BACKEND_PATH
BACKEND_PATH=${BACKEND_PATH:-/var/www/landscape-tool/backend}

read -p "Enter database type [sqlite]: " DB_TYPE
DB_TYPE=${DB_TYPE:-sqlite}

read -p "Enter database path [${BACKEND_PATH}/data/app.db]: " DB_PATH
DB_PATH=${DB_PATH:-${BACKEND_PATH}/data/app.db}

# Generate a secure JWT secret
JWT_SECRET=$(openssl rand -base64 32)

read -p "Enter allowed CORS origins (comma-separated): " CORS_ORIGINS

read -p "Enter log level [info]: " LOG_LEVEL
LOG_LEVEL=${LOG_LEVEL:-info}

# Create backend directory if it doesn't exist
mkdir -p ${BACKEND_PATH}
mkdir -p $(dirname ${DB_PATH})

# Create .env file
print_status "Creating .env file..."
cat > ${BACKEND_PATH}/.env << EOF
# Database configuration
DB_TYPE=${DB_TYPE}
DB_PATH=${DB_PATH}

# Security
JWT_SECRET=${JWT_SECRET}
CORS_ORIGINS=${CORS_ORIGINS}

# Application settings
DEBUG=false
LOG_LEVEL=${LOG_LEVEL}
ENVIRONMENT=production
EOF

# Set proper permissions
print_status "Setting proper file permissions..."
chmod 600 ${BACKEND_PATH}/.env
chown www-data:www-data ${BACKEND_PATH}/.env

# Create a backup of the JWT secret
print_status "Creating a backup of your JWT secret..."
mkdir -p /root/.secrets
echo "${JWT_SECRET}" > /root/.secrets/jwt_secret.txt
chmod 600 /root/.secrets/jwt_secret.txt

print_status "Environment setup complete!"
print_status "Your JWT secret has been saved to /root/.secrets/jwt_secret.txt"
print_warning "Keep this secret secure and do not share it!"

# Setup SSH key authentication if needed
read -p "Do you want to set up SSH key authentication? (y/n): " SETUP_SSH
if [[ $SETUP_SSH == "y" || $SETUP_SSH == "Y" ]]; then
  print_status "Setting up SSH key authentication..."
  
  # Create .ssh directory if it doesn't exist
  mkdir -p /root/.ssh
  chmod 700 /root/.ssh
  
  # Create authorized_keys file if it doesn't exist
  touch /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys
  
  # Prompt for public key
  read -p "Enter your public SSH key: " SSH_KEY
  echo "${SSH_KEY}" >> /root/.ssh/authorized_keys
  
  print_status "SSH key added to authorized_keys!"
  
  # Configure SSH to prefer key authentication
  print_status "Configuring SSH to prefer key authentication..."
  sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
  sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
  
  # Restart SSH service
  systemctl restart sshd
  
  print_status "SSH key authentication configured!"
  print_warning "Test your SSH key authentication before disabling password authentication!"
fi

print_status "Security setup complete!"
