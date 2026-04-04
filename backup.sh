#!/bin/bash

# Database Backup Script
# Schedule: Run daily via cron job

set -e

# Configuration
BACKUP_DIR="/opt/ecommerce/backups"
DB_CONTAINER="ecommerce_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ecommerce_db_$TIMESTAMP.sql.gz"
LOG_FILE="/var/log/ecommerce_backup.log"
RETENTION_DAYS=30

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting database backup..."

# Check if database container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    log "ERROR: Database container $DB_CONTAINER is not running!"
    exit 1
fi

# Perform backup
if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
    log "✓ Backup completed: $BACKUP_FILE (Size: $BACKUP_SIZE)"
else
    log "ERROR: Backup failed!"
    exit 1
fi

# Clean up old backups (retention policy)
log "Cleaning up backups older than $RETENTION_DAYS days..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "ecommerce_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
log "✓ Deleted $DELETED_COUNT old backup(s)"

# Optional: Upload to S3 (requires AWS CLI)
# aws s3 cp "$BACKUP_FILE" "s3://your-bucket/backups/" --region us-east-1

log "Backup process completed successfully!"
