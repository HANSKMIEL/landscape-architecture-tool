#!/bin/bash
#
# Production deployment script for Landscape Architecture Tool
# This script sets up the application for production deployment
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Landscape Architecture Tool Production Deployment${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}" 
   exit 1
fi

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}

echo -e "${YELLOW}Environment: $FLASK_ENV${NC}"
echo -e "${YELLOW}Secret key configured${NC}"

# Install system dependencies (requires sudo)
echo -e "${YELLOW}Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Create application directory
APP_DIR="/opt/landscape-architecture-tool"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files
echo -e "${YELLOW}Copying application files...${NC}"
cp -r . $APP_DIR/
cd $APP_DIR

# Create Python virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install PostgreSQL adapter
pip install psycopg2-binary

# Create production database (PostgreSQL)
echo -e "${YELLOW}Setting up production database...${NC}"
sudo -u postgres createdb landscape_architecture_prod || echo "Database may already exist"
sudo -u postgres psql -c "CREATE USER landscape_user WITH PASSWORD 'landscape_password';" || echo "User may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE landscape_architecture_prod TO landscape_user;"

# Update database URL for PostgreSQL
export DATABASE_URL="postgresql://landscape_user:landscape_password@localhost/landscape_architecture_prod"

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python -c "
from wsgi import application
with application.app_context():
    from src.utils.db_init import initialize_database, populate_sample_data
    initialize_database()
    populate_sample_data()
"

# Create systemd service file
echo -e "${YELLOW}Creating systemd service...${NC}"
sudo tee /etc/systemd/system/landscape-architecture.service > /dev/null <<EOF
[Unit]
Description=Landscape Architecture Tool Gunicorn Server
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=$SECRET_KEY"
Environment="DATABASE_URL=$DATABASE_URL"
ExecStart=$APP_DIR/venv/bin/gunicorn -c gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo -e "${YELLOW}Configuring Nginx...${NC}"
sudo cp nginx.conf /etc/nginx/sites-available/landscape-architecture-tool
sudo ln -sf /etc/nginx/sites-available/landscape-architecture-tool /etc/nginx/sites-enabled/
sudo nginx -t

# Start and enable services
echo -e "${YELLOW}Starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable landscape-architecture
sudo systemctl start landscape-architecture
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Check service status
echo -e "${YELLOW}Checking service status...${NC}"
sudo systemctl status landscape-architecture --no-pager
sudo systemctl status nginx --no-pager

# Test the application
echo -e "${YELLOW}Testing the application...${NC}"
sleep 5
curl -f http://localhost/health || echo -e "${RED}Health check failed${NC}"

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure your domain name in the Nginx configuration"
echo "2. Set up SSL certificates (Let's Encrypt recommended)"
echo "3. Configure firewall rules"
echo "4. Set up monitoring and logging"
echo "5. Configure backup strategies"

echo -e "${GREEN}Application should be available at: http://your-domain.com${NC}"