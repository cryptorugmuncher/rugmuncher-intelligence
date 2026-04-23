#!/bin/bash
# RMI Database Backup Script
# Run this daily via cron: 0 2 * * * /root/rmi/scripts/backup-database.sh

set -e

BACKUP_DIR="/root/rmi/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="rmi_db_${DATE}.sql"
RETENTION_DAYS=30

# Load env
source /root/rmi/v2/api/.env

# Extract DB connection details from DATABASE_URL
# Format: postgresql://user:pass@host:port/dbname
DB_URL="${DATABASE_URL}"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup..."

# PostgreSQL backup
if command -v pg_dump &> /dev/null; then
    pg_dump "$DB_URL" > "$BACKUP_DIR/$BACKUP_FILE"
    echo "[$(date)] Database backup created: $BACKUP_FILE"
else
    echo "ERROR: pg_dump not installed. Install postgresql-client."
    exit 1
fi

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"
echo "[$(date)] Compressed: ${BACKUP_FILE}.gz"

# Backup .env file
cp /root/rmi/v2/api/.env "$BACKUP_DIR/env_${DATE}.backup"

# Redis backup (if available)
if command -v redis-cli &> /dev/null; then
    REDIS_HOST=$(echo "$REDIS_URL" | sed 's|redis://||' | cut -d'/' -f1)
    redis-cli -h "$REDIS_HOST" SAVE 2>/dev/null || true
    if [ -f /var/lib/redis/dump.rdb ]; then
        cp /var/lib/redis/dump.rdb "$BACKUP_DIR/redis_${DATE}.rdb"
        echo "[$(date)] Redis backup created"
    fi
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "rmi_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "env_*.backup" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "redis_*.rdb" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup complete. Files in: $BACKUP_DIR"
echo ""
ls -lh "$BACKUP_DIR"/*.gz "$BACKUP_DIR"/*.backup 2>/dev/null | tail -5
