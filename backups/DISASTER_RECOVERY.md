# RMI Disaster Recovery Guide

## If You Lost All Data

### Step 1: Access What's Left
```bash
# SSH to server (if still running)
ssh root@167.86.116.51

# Check backup directory
ls -la /root/rmi/backups/
```

### Step 2: Recover Credentials
```bash
# Boundary login
cat /root/rmi/backups/BOUNDARY_CREDENTIALS.txt

# RMI API master key
cat /root/rmi/backups/MASTER_KEY.txt

# Daily admin key
cat /root/rmi/backups/ADMIN_KEY.txt
```

### Step 3: Recover Database
```bash
# List database backups
ls -la /root/rmi/backups/*.sql.gz

# Restore latest backup
gunzip -c /root/rmi/backups/rmi_db_20260414_214639.sql.gz | sudo -u postgres psql rmi_db
```

### Step 4: If Server Is Destroyed

You need to recreate:

1. **PostgreSQL Database**
   - User: rmi_user
   - Password: rmi_pass
   - Database: rmi_db
   - Restore from latest .sql.gz backup

2. **RMI API (.env file)**
   ```
   DATABASE_URL=postgresql://rmi_user:rmi_pass@localhost:5432/rmi_db
   SECRET_KEY=dev-secret-key-change-in-production-immediately!
   ```

3. **Boundary (if used)**
   - Reinstall boundary
   - Reinitialize database
   - Recreate targets manually
   - Or restore from boundary_db backup

4. **API Keys**
   - MASTER_KEY in MASTER_KEY.txt never expires
   - Can be used immediately after API restart

### Step 5: Emergency Key Creation
If all keys are lost:
```bash
cd /root/rmi/v2/api
python3 -c "
import os
import hashlib
secret = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-immediately!')
master = hashlib.sha256(f'master_recovery_{secret}'.encode()).hexdigest()
print(f'New Master Key: rmi_rmi_master_{master}')
"
```

## Critical Info to Save Off-Server

Copy these to your password manager NOW:

1. **Server IP:** 167.86.116.51
2. **SSH Key:** (your private key)
3. **Boundary Password:** JHXhwmrnQZKO5RasfYuI
4. **Master Key:** rmi_rmi_master_41c737fe869d287ac225d971e79866195889fb309a928e4abdf2ccbd4e2cacf7
5. **DB Password:** rmi_pass

## Backup Schedule

- Database: Daily at 2 AM (30 day retention)
- Files: Manual before major changes
- Location: /root/rmi/backups/

## Contact

If totally stuck:
1. Check this file: /root/rmi/backups/DISASTER_RECOVERY.md
2. PostgreSQL data is in /var/lib/postgresql/16/main/
3. Boundary data is in boundary_db PostgreSQL database
