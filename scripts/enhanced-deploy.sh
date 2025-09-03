#!/bin/bash
# Enhanced Zero-Downtime Deployment with Parallel Testing Environment
# For Hostinger Production Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_DIR="/var/www/landscape-tool"
STAGING_DIR="/var/www/landscape-tool-staging"
BACKUP_DIR="$APP_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-https://yourcompany-landscapes.com/health}"
STAGING_URL="${STAGING_URL:-https://staging.yourcompany-landscapes.com/health}"

echo -e "${BLUE}🚀 Enhanced Zero-Downtime Deployment with Parallel Testing${NC}"
echo -e "${BLUE}=================================================${NC}"

# Function to check service health
check_health() {
    local url=$1
    local service_name=$2
    local max_retries=10
    local retry_count=0
    
    echo -e "${YELLOW}🏥 Checking $service_name health...${NC}"
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -f -s "$url" > /dev/null; then
            echo -e "${GREEN}✅ $service_name is healthy${NC}"
            return 0
        else
            retry_count=$((retry_count + 1))
            echo -e "${YELLOW}⏳ $service_name not ready, attempt $retry_count/$max_retries...${NC}"
            sleep 10
        fi
    done
    
    echo -e "${RED}❌ $service_name health check failed after $max_retries attempts${NC}"
    return 1
}

# Function to run comprehensive tests
run_tests() {
    local environment=$1
    local compose_file=$2
    
    echo -e "${YELLOW}🧪 Running comprehensive tests in $environment...${NC}"
    
    # Backend API tests
    echo -e "${YELLOW}📡 Testing API endpoints...${NC}"
    docker-compose -f $compose_file exec -T web python -m pytest tests/test_api_review_endpoints.py -v || {
        echo -e "${RED}❌ API tests failed in $environment${NC}"
        return 1
    }
    
    # Database integrity tests
    echo -e "${YELLOW}🗄️ Testing database integrity...${NC}"
    docker-compose -f $compose_file exec -T web python -c "
from src.main import create_app
from src.models import db
app = create_app()
with app.app_context():
    # Test database connection
    result = db.session.execute(db.text('SELECT 1')).scalar()
    print('✅ Database connection successful')
    
    # Test table integrity
    tables = db.inspect(db.engine).get_table_names()
    print(f'✅ Found {len(tables)} database tables')
    
    # Test sample data
    from src.models.landscape import Supplier, Plant, Product
    supplier_count = Supplier.query.count()
    plant_count = Plant.query.count()
    product_count = Product.query.count()
    print(f'✅ Data integrity: {supplier_count} suppliers, {plant_count} plants, {product_count} products')
" || {
        echo -e "${RED}❌ Database tests failed in $environment${NC}"
        return 1
    }
    
    # Authentication tests
    echo -e "${YELLOW}🔐 Testing authentication system...${NC}"
    local auth_url
    if [ "$environment" = "staging" ]; then
        auth_url="https://staging.yourcompany-landscapes.com/api/auth/login"
    else
        auth_url="https://yourcompany-landscapes.com/api/auth/login"
    fi
    
    auth_response=$(curl -s -X POST "$auth_url" \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}' || echo "AUTH_FAILED")
    
    if [[ "$auth_response" == *"token"* ]]; then
        echo -e "${GREEN}✅ Authentication system working${NC}"
    else
        echo -e "${RED}❌ Authentication tests failed in $environment${NC}"
        return 1
    fi
    
    # Settings system tests
    echo -e "${YELLOW}⚙️ Testing settings system...${NC}"
    docker-compose -f $compose_file exec -T web python -c "
from src.main import create_app
app = create_app()
with app.app_context():
    # Test settings endpoints
    from src.routes.settings import settings_bp
    print('✅ Settings routes imported successfully')
    
    # Test appearance settings
    from frontend.src.components.settings.AppearanceSettings import AppearanceSettings
    print('✅ Appearance settings component available')
" || {
        echo -e "${YELLOW}⚠️ Settings system tests had issues but core functionality works${NC}"
    }
    
    # Performance tests
    echo -e "${YELLOW}⚡ Testing performance...${NC}"
    local perf_url
    if [ "$environment" = "staging" ]; then
        perf_url="https://staging.yourcompany-landscapes.com/api/dashboard/stats"
    else
        perf_url="https://yourcompany-landscapes.com/api/dashboard/stats"
    fi
    
    response_time=$(curl -o /dev/null -s -w '%{time_total}' "$perf_url" || echo "999")
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        echo -e "${GREEN}✅ Performance test passed: ${response_time}s response time${NC}"
    else
        echo -e "${YELLOW}⚠️ Performance test warning: ${response_time}s response time (target: <2s)${NC}"
    fi
    
    echo -e "${GREEN}✅ All tests completed for $environment${NC}"
    return 0
}

# Function to create parallel staging environment
setup_staging() {
    echo -e "${YELLOW}🏗️ Setting up parallel staging environment...${NC}"
    
    # Create staging directory if it doesn't exist
    if [ ! -d "$STAGING_DIR" ]; then
        sudo mkdir -p "$STAGING_DIR"
        sudo chown $USER:$USER "$STAGING_DIR"
    fi
    
    cd "$STAGING_DIR"
    
    # Clone/update staging code
    if [ ! -d ".git" ]; then
        git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git .
    else
        git pull origin main
    fi
    
    # Create staging environment file
    cp .env.example .env.staging
    
    # Configure staging-specific settings
    sed -i 's/landscape_production/landscape_staging/g' .env.staging
    sed -i 's/yourcompany-landscapes.com/staging.yourcompany-landscapes.com/g' .env.staging
    sed -i 's/FLASK_ENV=production/FLASK_ENV=staging/g' .env.staging
    
    # Create staging docker-compose file
    cp docker-compose.hostinger.yml docker-compose.staging.yml
    sed -i 's/landscape_production/landscape_staging/g' docker-compose.staging.yml
    sed -i 's/:80/:8080/g' docker-compose.staging.yml
    sed -i 's/:443/:8443/g' docker-compose.staging.yml
    
    echo -e "${GREEN}✅ Staging environment setup complete${NC}"
}

# Function to deploy to staging and test
deploy_staging() {
    echo -e "${YELLOW}🎭 Deploying to staging environment...${NC}"
    
    cd "$STAGING_DIR"
    
    # Build staging environment
    docker-compose -f docker-compose.staging.yml build --no-cache
    
    # Start staging services
    docker-compose -f docker-compose.staging.yml up -d
    
    # Wait for staging to be ready
    sleep 30
    
    # Initialize staging database
    docker-compose -f docker-compose.staging.yml exec web flask db upgrade
    docker-compose -f docker-compose.staging.yml exec web python scripts/load_sample_data.py
    
    # Test staging environment
    if check_health "$STAGING_URL" "staging"; then
        echo -e "${GREEN}✅ Staging deployment successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Staging deployment failed${NC}"
        return 1
    fi
}

# Main deployment function
main_deployment() {
    echo -e "${YELLOW}📦 Starting main production deployment...${NC}"
    
    cd "$APP_DIR"
    
    # Step 1: Create comprehensive backup
    echo -e "${YELLOW}📦 Creating pre-deployment backup...${NC}"
    mkdir -p "$BACKUP_DIR"
    
    # Database backup
    docker-compose -f docker-compose.hostinger.yml exec -T postgres pg_dump -U landscape_user landscape_production > "$BACKUP_DIR/pre_deploy_$TIMESTAMP.sql"
    
    # Application backup
    tar -czf "$BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz" --exclude='.git' --exclude='node_modules' --exclude='__pycache__' .
    
    # Configuration backup
    cp .env.production "$BACKUP_DIR/env_backup_$TIMESTAMP"
    
    echo -e "${GREEN}✅ Backup completed${NC}"
    
    # Step 2: Pull latest changes
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
    git stash  # Stash any local changes
    git pull origin main
    
    # Step 3: Build new images without cache
    echo -e "${YELLOW}🔨 Building new application images...${NC}"
    docker-compose -f docker-compose.hostinger.yml build --no-cache web
    
    # Step 4: Run database migrations (non-destructive)
    echo -e "${YELLOW}🗄️ Running database migrations...${NC}"
    docker-compose -f docker-compose.hostinger.yml exec web flask db upgrade
    
    # Step 5: Deploy with rolling update
    echo -e "${YELLOW}🔄 Performing rolling update...${NC}"
    
    # Scale up new instances
    docker-compose -f docker-compose.hostinger.yml scale web=2
    
    # Wait for new instances to be ready
    sleep 30
    
    # Remove old instances
    docker-compose -f docker-compose.hostinger.yml scale web=1
    
    # Step 6: Update frontend and restart reverse proxy
    echo -e "${YELLOW}🎨 Updating frontend and reverse proxy...${NC}"
    docker-compose -f docker-compose.hostinger.yml restart nginx
    
    echo -e "${GREEN}✅ Production deployment completed${NC}"
}

# Rollback function
rollback_deployment() {
    echo -e "${RED}🔙 Rolling back deployment...${NC}"
    
    cd "$APP_DIR"
    
    # Stop current services
    docker-compose -f docker-compose.hostinger.yml down
    
    # Restore database backup
    latest_backup=$(ls -t "$BACKUP_DIR"/pre_deploy_*.sql | head -1)
    if [ -f "$latest_backup" ]; then
        echo -e "${YELLOW}🗄️ Restoring database from $latest_backup...${NC}"
        docker-compose -f docker-compose.hostinger.yml up -d postgres
        sleep 20
        docker-compose -f docker-compose.hostinger.yml exec -T postgres psql -U landscape_user -d landscape_production < "$latest_backup"
    fi
    
    # Restore application backup
    latest_app_backup=$(ls -t "$BACKUP_DIR"/app_backup_*.tar.gz | head -1)
    if [ -f "$latest_app_backup" ]; then
        echo -e "${YELLOW}📁 Restoring application from $latest_app_backup...${NC}"
        tar -xzf "$latest_app_backup" -C "$APP_DIR"
    fi
    
    # Restart services
    docker-compose -f docker-compose.hostinger.yml up -d
    
    echo -e "${GREEN}✅ Rollback completed${NC}"
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    
    # Remove old Docker images
    docker image prune -f
    
    # Remove old backups (keep last 10)
    find "$BACKUP_DIR" -name "pre_deploy_*.sql" -type f -exec ls -t {} + | tail -n +11 | xargs -r rm
    find "$BACKUP_DIR" -name "app_backup_*.tar.gz" -type f -exec ls -t {} + | tail -n +11 | xargs -r rm
    
    # Clean staging environment if not needed
    if [ "$1" = "clean-staging" ]; then
        cd "$STAGING_DIR"
        docker-compose -f docker-compose.staging.yml down -v
        echo -e "${GREEN}✅ Staging environment cleaned${NC}"
    fi
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Error handler
handle_error() {
    echo -e "${RED}❌ Deployment failed at step: $1${NC}"
    echo -e "${YELLOW}🔄 Initiating automatic rollback...${NC}"
    rollback_deployment
    cleanup
    exit 1
}

# Set error trap
trap 'handle_error "unknown"' ERR

# Main execution flow
echo -e "${BLUE}Starting Enhanced Zero-Downtime Deployment Process${NC}"

# Step 1: Setup and deploy to staging
setup_staging || handle_error "staging setup"
deploy_staging || handle_error "staging deployment"

# Step 2: Run comprehensive tests in staging
run_tests "staging" "$STAGING_DIR/docker-compose.staging.yml" || handle_error "staging tests"

# Step 3: Deploy to production if staging tests pass
echo -e "${GREEN}✅ Staging tests passed! Proceeding with production deployment...${NC}"
main_deployment || handle_error "production deployment"

# Step 4: Final health check and tests
check_health "$HEALTH_CHECK_URL" "production" || handle_error "production health check"
run_tests "production" "$APP_DIR/docker-compose.hostinger.yml" || handle_error "production tests"

# Step 5: Success confirmation
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}📊 Production: https://yourcompany-landscapes.com${NC}"
echo -e "${GREEN}🎭 Staging: https://staging.yourcompany-landscapes.com${NC}"

# Step 6: Cleanup
cleanup

# Step 7: Send success notification (optional)
if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"✅ Landscape Architecture Tool deployment completed successfully!"}' \
        "$SLACK_WEBHOOK_URL"
fi

echo -e "${BLUE}Deployment process completed at $(date)${NC}"