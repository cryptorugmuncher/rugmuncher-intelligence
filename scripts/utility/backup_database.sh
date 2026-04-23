#!/bin/bash
# Database backup script
BACKUP_DIR="/root/rmi/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

echo "Creating database backup..."
export PGPASSWORD="rmi_secure_pass_2024"
pg_dump -h localhost -U rmi_user -d rmi_db > "$BACKUP_DIR/rmi_db_$DATE.sql"

# Keep only last 7 backups
ls -t $BACKUP_DIR/*.sql | tail -n +8 | xargs -r rm

echo "Backup complete: $BACKUP_DIR/rmi_db_$DATE.sql"
