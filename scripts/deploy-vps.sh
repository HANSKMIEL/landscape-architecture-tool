#!/bin/bash
# Deployment script for VPS

# Configuration
VPS_HOST="72.60.176.200"
VPS_USER="root"
FRONTEND_DIST_PATH="frontend/dist"
VPS_FRONTEND_PATH="/var/www/landscape-tool/frontend/dist"
VPS_BACKEND_PATH="/var/www/landscape-tool/backend"

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

# Check if SSH key is provided
if [ -z "$SSH_KEY" ]; then
  print_warning "No SSH key provided, will use password authentication"
  SSH_CMD="sshpass -p \"$SSH_PASSWORD\" ssh -o StrictHostKeyChecking=no"
  SCP_CMD="sshpass -p \"$SSH_PASSWORD\" scp -o StrictHostKeyChecking=no"
else
  print_status "Using SSH key authentication"
  SSH_CMD="ssh -i $SSH_KEY -o StrictHostKeyChecking=no"
  SCP_CMD="scp -i $SSH_KEY -o StrictHostKeyChecking=no"
fi

# Build frontend for production
print_status "Building frontend for production..."
cd frontend
npm ci
npm run build
cd ..

if [ $? -ne 0 ]; then
  print_error "Frontend build failed!"
  exit 1
fi

print_status "Frontend build successful!"

# Deploy frontend to VPS
print_status "Deploying frontend to VPS..."
$SSH_CMD $VPS_USER@$VPS_HOST "mkdir -p $VPS_FRONTEND_PATH"
$SCP_CMD -r $FRONTEND_DIST_PATH/* $VPS_USER@$VPS_HOST:$VPS_FRONTEND_PATH/

if [ $? -ne 0 ]; then
  print_error "Frontend deployment failed!"
  exit 1
fi

print_status "Frontend deployed successfully!"

# Deploy backend to VPS
print_status "Deploying backend to VPS..."
$SSH_CMD $VPS_USER@$VPS_HOST "mkdir -p $VPS_BACKEND_PATH"
$SCP_CMD -r src/* $VPS_USER@$VPS_HOST:$VPS_BACKEND_PATH/

if [ $? -ne 0 ]; then
  print_error "Backend deployment failed!"
  exit 1
fi

print_status "Backend deployed successfully!"

# Restart services on VPS
print_status "Restarting services on VPS..."
$SSH_CMD $VPS_USER@$VPS_HOST "systemctl restart nginx && cd $VPS_BACKEND_PATH && source venv/bin/activate && pkill -f gunicorn || true && gunicorn -b 127.0.0.1:5000 main:app --daemon"

if [ $? -ne 0 ]; then
  print_error "Service restart failed!"
  exit 1
fi

print_status "Services restarted successfully!"

# Test deployment
print_status "Testing deployment..."
$SSH_CMD $VPS_USER@$VPS_HOST "curl -s http://localhost:5000/api/health"

if [ $? -ne 0 ]; then
  print_error "Deployment test failed!"
  exit 1
fi

print_status "Deployment test successful!"
print_status "Deployment completed successfully!"
print_status "Application is now available at http://$VPS_HOST"
