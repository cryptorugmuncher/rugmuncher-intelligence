# 🔐 RugMuncher OPSEC (Operational Security) Guide

**Never get locked out. Never let scammers in.**

This guide covers credential rotation, secure storage, and operational security practices for the RugMuncher ecosystem.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Security Levels](#security-levels)
3. [Credential Rotation System](#credential-rotation-system)
4. [Backup & Recovery](#backup--recovery)
5. [Password Generation](#password-generation)
6. [Recovery Procedures](#recovery-procedures)
7. [Automated Scheduling](#automated-scheduling)
8. [Best Practices](#best-practices)
9. [Emergency Response](#emergency-response)

---

## Overview

The OPSEC system provides:

- **Automated credential rotation** on configurable schedules
- **Encrypted backup storage** with integrity verification
- **Secure password generation** (memorable & random)
- **Recovery procedure generation** for every credential
- **Multi-scenario disaster recovery** planning

### Core Components

```python
from credential_rotation_system import (
    RotationManager,      # Main credential management
    BackupManager,        # Backup & restore operations
    RotationScheduler,    # Automated scheduling
    SecurePasswordGenerator  # Password generation
)
```

---

## Security Levels

Credentials are classified by criticality:

| Level | Rotation | Services | Backups |
|-------|----------|----------|---------|
| **Critical** | 30 days | Email, GitHub, Vault, Domain | 5 |
| **High** | 60 days | API keys, Database, SSH | 3 |
| **Medium** | 90 days | Third-party APIs, Monitoring | 2 |
| **Low** | 180 days | Newsletters, Forums | 1 |

```python
ROTATION_SCHEDULE = {
    'critical': {
        'interval_days': 30,
        'services': ['primary_email', 'github', 'vault', 'domain_registrar'],
        'backup_count': 5,
    },
    'high': {
        'interval_days': 60,
        'services': ['api_keys', 'database', 'server_ssh'],
        'backup_count': 3,
    },
    # ... etc
}
```

---

## Credential Rotation System

### Adding a New Credential

```python
from credential_rotation_system import RotationManager

manager = RotationManager()

# Add a new credential
cred = manager.add_credential(
    service="github",
    username="rugmuncher_bot",
    password="CurrentPassword123!",
    email="bot@rugmuncher.io",
    security_level="critical",  # Determines rotation schedule
    api_key="ghp_xxxxxxxxxxxx",
    recovery_email="recovery@backup.com"
)

print(f"Credential ID: {cred.id}")
print(f"Backup codes: {cred.backup_codes}")
print(f"Expires: {cred.expires_at}")
```

### Checking Rotation Status

```python
# Get status of all credentials
status = manager.check_rotation_status()

print(f"Current: {len(status['current'])}")
print(f"Expiring (7 days): {len(status['expiring'])}")
print(f"Expired: {len(status['expired'])}")

# Handle expired credentials
for cred in status['expired']:
    print(f"⚠️  MUST ROTATE: {cred.service}")
```

### Rotating a Credential

```python
# Rotate by credential ID
new_cred, new_password = manager.rotate_credential(cred_id)

print(f"New password: {new_password}")
print(f"New expiration: {new_cred.expires_at}")
print(f"New backup codes: {new_cred.backup_codes}")

# Old password is archived (last 3 kept in history)
print(f"Previous passwords in history: {len(new_cred.history)}")
```

---

## Backup & Recovery

### Creating Backups

```python
from credential_rotation_system import BackupManager

backup = BackupManager(manager)

# Create snapshot
filename = backup.create_snapshot(label="manual_backup")
print(f"Backup created: {filename}")

# Verify integrity
is_valid = backup.verify_snapshot(filename)
print(f"Backup valid: {is_valid}")
```

### Restoring from Backup

```python
# Restore credentials
success = backup.restore_from_snapshot("credential_backups/snapshot_manual_20240115_143022.json")

if success:
    print("✅ Credentials restored successfully")
else:
    print("❌ Restore failed - backup may be corrupted")
```

### Backup Storage

Backups are stored in `credential_backups/` with:
- Timestamped filenames
- SHA-256 checksums for integrity
- JSON format (encrypt in production)
- Automatic cleanup (keeps last 10 by default)

---

## Password Generation

### Memorable Passwords

```python
from credential_rotation_system import SecurePasswordGenerator

# Generate memorable password (default)
password = SecurePasswordGenerator.generate(memorable=True)
# Examples: "AlphaCrypto7391!", "LedgerShield2847#"
```

Pattern: `Word1` + `Word2` + `Number` + `Symbol`
- Easy to type
- Cryptographically secure
- 40+ bits of entropy

### Random Passwords

```python
# Generate random password (for API keys)
password = SecurePasswordGenerator.generate(length=32, memorable=False)
# Example: "k9#mP2$vL7@nQ4*wR8&jF5"
```

### Backup Codes

```python
# Generate recovery codes
codes = SecurePasswordGenerator.generate_backup_codes(count=10)
# Example: ["XK92-MNP4-7WQ3", "RJ48-LK9M-3VC7", ...]

# Easy to write down
# Format: XXXX-XXXX-XXXX (no ambiguous characters)
```

---

## Recovery Procedures

### Generate Recovery Plan

```python
# Generate step-by-step recovery procedures
procedures = backup.generate_recovery_procedures(cred_id)

print(json.dumps(procedures, indent=2))
```

### Recovery Scenarios Covered

1. **Forgot Password**
   - Navigate to service login
   - Use "Forgot password" flow
   - Check recovery email
   - Set new password from vault

2. **Lost 2FA Device**
   - Use backup codes
   - Disable old 2FA
   - Set up new 2FA
   - Generate new backup codes

3. **Account Locked/Suspended**
   - Contact service support
   - Provide account details
   - Use recovery email
   - Verify with backup codes

---

## Automated Scheduling

### Starting the Scheduler

```python
from credential_rotation_system import RotationScheduler

scheduler = RotationScheduler(manager, backup)

# Start automated rotation (runs daily at 3 AM)
scheduler.start_scheduler()
```

### What the Scheduler Does

1. **3:00 AM Daily** - Check all credentials
2. **Pre-rotation backup** - Create snapshot before any changes
3. **Auto-rotate expired** - Rotate any expired credentials
4. **Notify expiring** - Log credentials expiring within 7 days
5. **Cleanup** - Remove old backup files

```python
# Daily check output:
# INFO: Running daily rotation check
# INFO: Created backup snapshot: credential_backups/snapshot_pre_rotation_20240115_030001.json
# WARNING: Rotating EXPIRED credential: github
# INFO: Credential expiring soon: api_service (bot@rugmuncher.io)
# INFO: Daily check complete: 1 rotated, 2 expiring soon
```

### Stopping the Scheduler

```python
scheduler.stop_scheduler()
```

---

## Best Practices

### 1. Always Have Recovery Email

```python
# Bad - no recovery
cred = manager.add_credential(
    service="twitter",
    email="bot@rugmuncher.io",
    recovery_email=None  # ❌ Risky
)

# Good - separate recovery
cred = manager.add_credential(
    service="twitter",
    email="bot@rugmuncher.io",
    recovery_email="recovery@backup-provider.com"  # ✅ Safe
)
```

### 2. Use Appropriate Security Levels

```python
# Don't under-classify
cred = manager.add_credential(
    service="github_primary",
    security_level="low"  # ❌ Should be 'critical'
)

# Proper classification
cred = manager.add_credential(
    service="github_primary",
    security_level="critical"  # ✅ Correct
)
```

### 3. Verify Backups Regularly

```python
def weekly_backup_check():
    """Run this weekly to ensure backups work"""
    backups = glob.glob("credential_backups/snapshot_*.json")
    
    for backup_file in backups[-3:]:  # Check last 3
        if not backup.verify_snapshot(backup_file):
            alert_admin(f"Backup verification failed: {backup_file}")
```

### 4. Store Backup Codes Offline

```python
cred = manager.add_credential(
    service="critical_service",
    security_level="critical"
)

# Print and store physically
print("BACKUP CODES - WRITE DOWN AND STORE SAFELY:")
for code in cred.backup_codes:
    print(f"  {code}")
```

### 5. Test Recovery Procedures

```python
# Monthly: Test one recovery procedure
def test_recovery_procedure(cred_id):
    procedures = backup.generate_recovery_procedures(cred_id)
    
    # Review steps
    for scenario in procedures['scenarios']:
        print(f"\nScenario: {scenario['name']}")
        for i, step in enumerate(scenario['steps'], 1):
            print(f"  {i}. {step}")
```

---

## Emergency Response

### Scenario: Complete Lockout

```python
def emergency_recovery():
    """When all else fails"""
    
    # 1. Find latest valid backup
    backups = sorted(glob.glob("credential_backups/snapshot_*.json"))
    
    for backup_file in reversed(backups):
        if backup.verify_snapshot(backup_file):
            print(f"Found valid backup: {backup_file}")
            
            # 2. Restore from backup
            if backup.restore_from_snapshot(backup_file):
                print("✅ Credentials restored")
                break
    
    # 3. Rotate ALL credentials (compromise response)
    status = manager.check_rotation_status()
    for cred in manager.credentials.values():
        manager.rotate_credential(cred.id)
        print(f"Rotated: {cred.service}")
```

### Scenario: Suspected Breach

```python
def breach_response():
    """Immediate response to suspected credential breach"""
    
    # 1. Create forensic backup
    backup.create_snapshot(label="breach_forensic")
    
    # 2. Rotate ALL credentials immediately
    for cred_id in manager.credentials:
        manager.rotate_credential(cred_id)
    
    # 3. Generate new backup codes for all
    # 4. Audit access logs
    # 5. Notify affected services
```

### Emergency Contacts Template

```markdown
## Emergency Recovery Contacts

### Domain Registrar
- Service: Namecheap/Cloudflare
- Support: support@provider.com
- Account: [see vault]
- Recovery: Use backup codes + recovery email

### Email Provider
- Service: ProtonMail/ForwardEmail
- Support: See provider docs
- Recovery: Domain-based recovery

### Code Repository
- Service: GitHub
- Support: support@github.com
- Recovery: Recovery codes + backup email
```

---

## CLI Usage

### Interactive Mode

```bash
python credential_rotation_system.py
```

Output:
```
============================================================
🔄 RugMuncher Credential Rotation System
============================================================

Total credentials: 12
  ✅ Current: 10
  ⚠️  Expiring (7 days): 1
  ❌ Expired: 1

Commands:
  1. Add new credential
  2. Rotate credential
  3. Create backup
  4. Show rotation status
  5. Start auto-rotation
  6. Generate recovery procedures
```

### Command Line Operations

```bash
# Quick status check
python -c "from credential_rotation_system import *; m=RotationManager(); s=m.check_rotation_status(); print(f'Expired: {len(s[\"expired\"])}')"

# Create emergency backup
python -c "from credential_rotation_system import *; m=RotationManager(); b=BackupManager(m); b.create_snapshot('emergency')"
```

---

## Security Checklist

- [ ] All critical services have recovery email configured
- [ ] Backup codes printed and stored in secure physical location
- [ ] Weekly backup verification automated
- [ ] Monthly recovery procedure review scheduled
- [ ] Emergency contacts documented
- [ ] Scheduler running for automated rotation
- [ ] All credentials classified with appropriate security level
- [ ] Domain registrar has 2FA enabled
- [ ] Email provider has 2FA enabled
- [ ] GitHub has 2FA enabled

---

## Storage Format

### Credential Storage (`credentials_vault.json`)

```json
{
  "credentials": {
    "a1b2c3d4...": {
      "id": "a1b2c3d4...",
      "service": "github",
      "username": "rugmuncher_bot",
      "password": "AlphaCrypto7391!",
      "email": "bot@rugmuncher.io",
      "api_key": "ghp_xxxxxxxxxxxx",
      "created_at": "2024-01-01T00:00:00",
      "expires_at": "2024-01-31T00:00:00",
      "backup_codes": ["XK92-MNP4-7WQ3", ...],
      "recovery_email": "recovery@backup.com",
      "security_level": "critical",
      "status": "current",
      "history": [...]
    }
  },
  "history": [...],
  "last_saved": "2024-01-15T10:30:00"
}
```

**Note:** In production, encrypt this file with AES-256 or use a proper secrets manager.

---

## Integration with Other Systems

### With RugMuncher Bot

```python
# Auto-rotate API keys when expiring
from credential_rotation_system import RotationManager
from rug_muncher_bot import update_api_key

manager = RotationManager()
status = manager.check_rotation_status()

for cred in status['expiring']:
    if cred.service == 'quicknode':
        new_cred, new_key = manager.rotate_credential(cred.id)
        update_api_key('quicknode', new_key)
```

### With Vault

```python
# Sync with HashiCorp Vault
from credential_rotation_system import RotationManager
import hvac

manager = RotationManager()
client = hvac.Client(url='https://vault.rugmuncher.io')

for cred in manager.credentials.values():
    client.secrets.kv.v2.create_or_update_secret(
        path=f'credentials/{cred.service}',
        secret={
            'username': cred.username,
            'password': cred.password,
            'api_key': cred.api_key,
        }
    )
```

---

**Remember: Security is a process, not a product. Stay vigilant.**
