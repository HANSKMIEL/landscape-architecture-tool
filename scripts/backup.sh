#!/bin/bash
# Database backup script for production environment

set -e

# Configuration
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="landscape_production"
DB_USER="landscape_user"
POSTGRES_PASSWORD=$(cat /run/secrets/postgres_password)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Export password for pg_dump
export PGPASSWORD="$POSTGRES_PASSWORD"

# Create backup
echo "Starting database backup at $(date)"
pg_dump -h postgres -U $DB_USER -d $DB_NAME -f $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Verify backup was created
if [ -f "$BACKUP_DIR/backup_$DATE.sql.gz" ]; then
    echo "Backup completed successfully: backup_$DATE.sql.gz"
    
    # Get backup size
    BACKUP_SIZE=$(du -h $BACKUP_DIR/backup_$DATE.sql.gz | cut -f1)
    echo "Backup size: $BACKUP_SIZE"
else
    echo "ERROR: Backup file not found!"
    exit 1
fi

# Remove backups older than 30 days
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Log backup completion
echo "Database backup completed at $(date)"

# Optional: Send notification (uncomment if you have mail configured)
# echo "Database backup completed successfully on $(hostname) at $(date). Size: $BACKUP_SIZE" | mail -s "Landscape Tool Backup Success" admin@your-domain.com