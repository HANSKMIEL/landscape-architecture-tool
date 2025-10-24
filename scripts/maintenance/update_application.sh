#!/bin/bash
# Update application to latest version safely

set -e

echo "🚀 Updating Landscape Architecture Tool..."
echo "Current time: $(date)"

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
BACKUP_DIR="./backups/pre-update"

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Production compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Create backup directory
mkdir -p $BACKUP_DIR

echo "📦 Creating pre-update backup..."
# Create database backup before update
docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U landscape_user landscape_production > $BACKUP_DIR/pre-update-$(date +%Y%m%d_%H%M%S).sql

echo "📥 Pulling latest changes..."
git fetch origin
git pull origin main

echo "🔧 Building new application images..."
docker-compose -f $COMPOSE_FILE build --no-cache web

echo "📊 Running database migrations..."
# Run migrations before restarting services
docker-compose -f $COMPOSE_FILE run --rm web flask db upgrade

echo "🔄 Restarting services..."
# Restart services with zero-downtime deployment
docker-compose -f $COMPOSE_FILE up -d --no-deps web

# Wait for health check
echo "⏱️  Waiting for application to be healthy..."
for i in {1..30}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Application is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Application health check failed"
        echo "🔄 Rolling back..."
        docker-compose -f $COMPOSE_FILE logs web
        exit 1
    fi
    sleep 2
done

# Restart nginx to pick up any config changes
docker-compose -f $COMPOSE_FILE restart nginx

echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "✅ Application updated successfully!"
echo "🔍 Current status:"
docker-compose -f $COMPOSE_FILE ps

echo "📝 Update completed at: $(date)"