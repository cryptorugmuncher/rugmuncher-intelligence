# RMI Disaster Recovery Guide

**Last Updated:** 2026-04-14  
**System:** RMI v2 API  
**Location:** `/root/rmi/`

---

## Quick Emergency Access

If you're locked out, you have **4 ways back in**:

### 1. Master Recovery Key (Always Works)
```bash
# The master key is stored at:
cat /root/rmi/backups/MASTER_KEY.txt

# If that file is missing, regenerate it:
cd /root/rmi/v2/api
python3 /root/rmi/scripts/emergency-access.py create-master-key
```

### 2. Database Direct Access
```bash
# Connect directly to PostgreSQL
psql "$(grep DATABASE_URL /root/rmi/v2/api/.env | cut -d= -f2)"

# List API keys
SELECT id, name, key_preview, is_active FROM api_keys WHERE is_active = true;
```

### 3. Create New Admin Key (Emergency Script)
```bash
cd /root/rmi/v2/api
python3 /root/rmi/scripts/emergency-access.py create-admin-key
# This creates a new admin key and prints it
```

### 4. Filesystem Backup Recovery
```bash
# Restore from latest backup
ls -la /root/rmi/backups/

# Restore database
gunzip < /root/rmi/backups/rmi_db_YYYYMMDD_HHMMSS.sql.gz | psql "$(grep DATABASE_URL .env | cut -d= -f2)"

# Restore env
cp /root/rmi/backups/env_YYYYMMDD.backup /root/rmi/v2/api/.env
```

---

## Backup System

### Automated Backups
- **Location:** `/root/rmi/backups/`
- **Database:** Daily at 2 AM via cron
- **Retention:** 30 days
- **Contents:**
  - Database dumps (`rmi_db_*.sql.gz`)
  - Environment files (`env_*.backup`)
  - Redis dumps (`redis_*.rdb`)
  - API key exports (`api_keys_*.json`)

### Manual Backup Now
```bash
/root/rmi/scripts/backup-database.sh
```

### Export Current Keys
```bash
python3 /root/rmi/scripts/export-keys.py
```

---

## Recovery Scenarios

### Scenario 1: Lost All API Keys
```bash
# Create new emergency admin key
python3 /root/rmi/scripts/emergency-access.py create-admin-key

# Save the printed key - it has full admin access
```

### Scenario 2: Database Corrupted
```bash
# 1. Stop the API
pkill -f uvicorn

# 2. Find latest backup
LATEST=$(ls -t /root/rmi/backups/rmi_db_*.sql.gz | head -1)
echo "Restoring from: $LATEST"

# 3. Drop and recreate database (CAREFUL!)
dropdb rmi_dev  # Or your db name
createdb rmi_dev

# 4. Restore
gunzip < "$LATEST" | psql rmi_dev

# 5. Restart API
cd /root/rmi/v2/api && uvicorn rmi.main:app
```

### Scenario 3: Wrong Password/Env Corrupted
```bash
# Restore env from backup
LATEST_ENV=$(ls -t /root/rmi/backups/env_*.backup | head -1)
cp "$LATEST_ENV" /root/rmi/v2/api/.env
```

### Scenario 4: Redis Data Lost
```bash
# Restore Redis from RDB backup
LATEST_REDIS=$(ls -t /root/rmi/backups/redis_*.rdb | head -1)
cp "$LATEST_REDIS" /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb
systemctl restart redis
```

### Scenario 5: Complete Server Failure
```bash
# On new server:

# 1. Install dependencies
apt-get update
apt-get install -y postgresql-client redis-tools python3-pip

# 2. Clone/copy your code
git clone <your-repo> /root/rmi
# OR
rsync -avz user@old-server:/root/rmi/ /root/rmi/

# 3. Restore database from backup
gunzip < /root/rmi/backups/rmi_db_latest.sql.gz | psql <connection-string>

# 4. Restore environment
cp /root/rmi/backups/env_latest.backup /root/rmi/v2/api/.env

# 5. Install Python deps
cd /root/rmi/v2/api && pip install -r requirements.txt

# 6. Start API
uvicorn rmi.main:app --host 0.0.0.0 --port 8000
```

---

## Critical Files to Backup

| File | Purpose | Backup Method |
|------|---------|---------------|
| `/root/rmi/v2/api/.env` | Configuration | Daily to `/root/rmi/backups/` |
| PostgreSQL database | All data | Daily pg_dump |
| `/root/rmi/backups/MASTER_KEY.txt` | Emergency access | Manual (one-time) |
| Redis RDB | Cache/sessions | Daily copy |
| `/root/rmi/v2/api/` | Code | Git or rsync |

---

## Security Notes

1. **Master Key File:** Has 600 permissions (owner read-only)
2. **Backup Files:** Have 600 permissions
3. **Key Exports:** Only contain key previews, not full keys
4. **Emergency Script:** Bypasses all auth - use with caution
5. **Database Connection:** Emergency script reads from `.env` directly

---

## Testing Recovery

**Test your backups monthly:**

```bash
# Test database restore to temp database
createdb rmi_test_restore
gunzip < /root/rmi/backups/rmi_db_latest.sql.gz | psql rmi_test_restore
psql rmi_test_restore -c "SELECT count(*) FROM users;"
dropdb rmi_test_restore

echo "✓ Database backup is valid"
```

---

## Contact & Documentation

- **This file:** `/root/rmi/DISASTER_RECOVERY.md`
- **Scripts:** `/root/rmi/scripts/`
- **Backups:** `/root/rmi/backups/`
- **API Code:** `/root/rmi/v2/api/`

**If all else fails:**
1. SSH into server as root
2. Run `python3 /root/rmi/scripts/emergency-access.py create-admin-key`
3. You now have a working key
