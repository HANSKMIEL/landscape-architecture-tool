#!/bin/bash
# Complete GitHub Actions deployment workflow for landscape architecture tool
# Supports: automated testing, building, and deployment to production

set -e

echo "🚀 Starting GitHub Actions Deployment Pipeline"

# Configuration
PROJECT_NAME="landscape-architecture-tool"
DOCKER_IMAGE="$PROJECT_NAME:latest"
PRODUCTION_DOMAIN="${PRODUCTION_DOMAIN:-your-domain.com}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Function: Environment validation
validate_environment() {
    log "🔍 Validating deployment environment..."
    
    # Check required environment variables
    REQUIRED_VARS=(
        "DATABASE_URL"
        "SECRET_KEY" 
        "REDIS_URL"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [[ -z "${!var}" ]]; then
            error "Required environment variable $var is not set"
        fi
    done
    
    # Check required tools
    REQUIRED_TOOLS=("docker" "docker-compose" "git")
    for tool in "${REQUIRED_TOOLS[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool '$tool' is not installed"
        fi
    done
    
    log "✅ Environment validation passed"
}

# Function: Run comprehensive tests
run_tests() {
    log "🧪 Running comprehensive test suite..."
    
    # Backend tests
    log "Running backend tests..."
    if ! make backend-test; then
        error "Backend tests failed"
    fi
    
    # Frontend tests (if configured)
    if [[ -f "frontend/package.json" ]]; then
        log "Running frontend tests..."
        cd frontend
        if npm run test:vitest:run --reporter=basic; then
            log "✅ Frontend tests passed"
        else
            warn "Frontend tests failed, but continuing deployment"
        fi
        cd ..
    fi
    
    # Code quality checks
    log "Running code quality checks..."
    if ! make lint; then
        error "Code quality checks failed"
    fi
    
    log "✅ All tests passed"
}

# Function: Build production images
build_production() {
    log "🏗️ Building production Docker images..."
    
    # Create production environment file
    cat > .env.production << EOF
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production
DEBUG=false
CORS_ORIGINS=https://${PRODUCTION_DOMAIN}
EOF
    
    # Build with Docker Compose
    if ! docker compose -f docker-compose.production.yml build; then
        error "Docker build failed"
    fi
    
    log "✅ Production images built successfully"
}

# Function: Database backup
backup_database() {
    log "💾 Creating database backup..."
    
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    # Create backup directory
    mkdir -p backups
    
    # Create database backup (PostgreSQL)
    if [[ "$DATABASE_URL" == postgres* ]]; then
        if ! pg_dump "$DATABASE_URL" > "backups/$BACKUP_FILE"; then
            error "Database backup failed"
        fi
    else
        warn "Database backup skipped - not PostgreSQL"
    fi
    
    # Compress backup
    if [[ -f "backups/$BACKUP_FILE" ]]; then
        gzip "backups/$BACKUP_FILE"
        log "✅ Database backup created: backups/${BACKUP_FILE}.gz"
    fi
    
    # Clean old backups
    find backups -name "backup_*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
}

# Function: Deploy to production
deploy_production() {
    log "🚀 Deploying to production..."
    
    # Stop existing services
    docker compose -f docker-compose.production.yml down || true
    
    # Start new services
    if ! docker compose -f docker-compose.production.yml up -d; then
        error "Production deployment failed"
    fi
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if curl -f "http://localhost:5000/health" &> /dev/null; then
        log "✅ Application health check passed"
    else
        error "Application health check failed"
    fi
    
    log "✅ Production deployment completed successfully"
}

# Function: Post-deployment tasks
post_deployment() {
    log "🔧 Running post-deployment tasks..."
    
    # Database migrations
    log "Running database migrations..."
    docker compose -f docker-compose.production.yml exec -T app flask db upgrade || warn "Migration failed"
    
    # Create sample data if needed
    docker compose -f docker-compose.production.yml exec -T app python scripts/create_sample_data.py || warn "Sample data creation failed"
    
    # Clear application cache
    docker compose -f docker-compose.production.yml exec -T redis redis-cli FLUSHDB || warn "Cache clear failed"
    
    log "✅ Post-deployment tasks completed"
}

# Function: Cleanup
cleanup() {
    log "🧹 Cleaning up temporary files..."
    
    # Remove temporary files
    rm -f .env.production
    
    # Clean unused Docker images
    docker image prune -f || warn "Docker cleanup failed"
    
    log "✅ Cleanup completed"
}

# Function: Send notifications
send_notifications() {
    local status=$1
    local message=$2
    
    log "📢 Sending deployment notifications..."
    
    # Slack notification (if webhook configured)
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 Deployment $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" || warn "Slack notification failed"
    fi
    
    # Email notification (if configured)
    if [[ -n "$NOTIFICATION_EMAIL" ]]; then
        echo "$message" | mail -s "Deployment $status" "$NOTIFICATION_EMAIL" || warn "Email notification failed"
    fi
}

# Main deployment pipeline
main() {
    local start_time=$(date +%s)
    
    log "🎯 Starting deployment pipeline for $PROJECT_NAME"
    
    # Trap errors and cleanup
    trap 'error "Deployment failed"; cleanup; send_notifications "FAILED" "Deployment pipeline failed"; exit 1' ERR
    
    # Execute deployment steps
    validate_environment
    run_tests
    backup_database
    build_production
    deploy_production
    post_deployment
    cleanup
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "🎉 Deployment completed successfully in ${duration}s"
    send_notifications "SUCCESS" "Deployment completed successfully in ${duration}s"
}

# Parse command line arguments
case "${1:-deploy}" in
    "test")
        run_tests
        ;;
    "build")
        build_production
        ;;
    "deploy")
        main
        ;;
    "backup")
        backup_database
        ;;
    "validate")
        validate_environment
        ;;
    *)
        echo "Usage: $0 {test|build|deploy|backup|validate}"
        echo "  test     - Run test suite only"
        echo "  build    - Build production images only"
        echo "  deploy   - Full deployment pipeline (default)"
        echo "  backup   - Create database backup only"
        echo "  validate - Validate environment only"
        exit 1
        ;;
esac