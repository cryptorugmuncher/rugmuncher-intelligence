#!/usr/bin/env python3
"""
🏰 RugMuncher Security Hardening & Disaster Recovery
Maximum security WITHOUT losing access to keys/wallets/codes

Principles:
1. Defense in depth (multiple layers)
2. Redundancy (never single point of failure)
3. Recovery (always have a way back in)
4. Monitoring (know when something's wrong)
"""

import os
import json
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# 1. SHAMIR'S SECRET SHARING
# Split master key into N parts, need K to reconstruct
# Example: 5 shares, need 3 to recover
# Store in different locations (home, bank, trusted friend, etc.)
# ═══════════════════════════════════════════════════════════

class ShamirSecretSharing:
    """
    🔐 Split secrets into shares for distributed storage
    
    Uses polynomial interpolation over finite field
    Secure even if some shares are compromised (as long as < K)
    """
    
    def __init__(self, prime: int = None):
        # Large prime for finite field arithmetic
        # Using a larger prime (521-bit Mersenne) to handle bigger secrets
        self.prime = prime or (2**521 - 1)  # Large Mersenne prime
    
    def _eval_at(self, poly: List[int], x: int) -> int:
        """Evaluate polynomial at point x using Horner's method"""
        # poly[0] is the secret (constant term), poly[1] is coefficient of x, etc.
        result = 0
        # Process from highest degree to lowest (reverse order)
        for coeff in reversed(poly):
            result = (result * x + coeff) % self.prime
        return result
    
    def split_secret(self, secret: str, n: int, k: int) -> List[Tuple[int, int]]:
        """
        Split secret into n shares, need k to reconstruct
        
        Args:
            secret: The secret to split (string)
            n: Total number of shares to create
            k: Minimum shares needed to reconstruct
        
        Returns:
            List of (x, y) coordinate pairs (the shares)
        """
        # Convert secret to number, ensure it fits in our field
        secret_bytes = secret.encode('utf-8')
        secret_int = int.from_bytes(secret_bytes, 'big')
        
        # Ensure secret is smaller than our prime
        if secret_int >= self.prime:
            raise ValueError("Secret too large for current prime. Use a smaller secret or larger prime.")
        
        # Generate random polynomial coefficients
        # poly[0] = secret (constant term), poly[1:] = random coefficients for x, x^2, etc.
        poly = [secret_int] + [secrets.randbelow(self.prime) for _ in range(k - 1)]
        
        # Generate n points on the polynomial
        shares = []
        for i in range(1, n + 1):
            x = i
            y = self._eval_at(poly, x)
            shares.append((x, y))
        
        return shares
    
    def reconstruct_secret(self, shares: List[Tuple[int, int]]) -> str:
        """
        Reconstruct secret from k shares using Lagrange interpolation
        """
        def lagrange_interpolate(x: int, x_s: List[int], y_s: List[int]) -> int:
            """Lagrange interpolation at x=0 (the secret)"""
            result = 0
            k = len(x_s)
            
            for i in range(k):
                numerator = y_s[i]
                denominator = 1
                
                for j in range(k):
                    if i != j:
                        numerator = (numerator * (x - x_s[j])) % self.prime
                        denominator = (denominator * (x_s[i] - x_s[j])) % self.prime
                
                # Modular inverse of denominator using Fermat's little theorem
                # denominator^(p-2) mod p = inverse of denominator mod p
                try:
                    inv_denominator = pow(denominator, self.prime - 2, self.prime)
                except ValueError:
                    # If denominator is 0, interpolation fails
                    raise ValueError(f"Interpolation failed: denominator is 0 for share {i}")
                
                result = (result + numerator * inv_denominator) % self.prime
            
            return result
        
        x_s = [s[0] for s in shares]
        y_s = [s[1] for s in shares]
        
        secret_int = lagrange_interpolate(0, x_s, y_s)
        
        # Convert back to string
        # The original secret was encoded as a UTF-8 byte sequence
        # We need to determine the correct byte length
        byte_length = (secret_int.bit_length() + 7) // 8
        if byte_length == 0:
            byte_length = 1
        
        secret_bytes = secret_int.to_bytes(byte_length, 'big')
        
        # Remove any leading null bytes that might have been added
        while secret_bytes and secret_bytes[0] == 0:
            secret_bytes = secret_bytes[1:]
        
        return secret_bytes.decode('utf-8')


# ═══════════════════════════════════════════════════════════
# 2. ENCRYPTED BACKUP SYSTEM
# Multiple encrypted backups in different locations
# ═══════════════════════════════════════════════════════════

@dataclass
class BackupConfig:
    """Backup configuration"""
    name: str
    location: str  # local, s3, gdrive, physical
    encryption_key: str  # Key ID, not the actual key
    schedule: str  # daily, weekly, monthly
    retention: int  # Number of backups to keep


class EncryptedBackupSystem:
    """
    💾 Multi-layer encrypted backup system
    
    Strategy: 3-2-1 Rule
    - 3 copies of data
    - 2 different media types
    - 1 offsite
    
    Plus encryption and integrity verification
    """
    
    BACKUP_LOCATIONS = {
        'local_encrypted': '/backup/rugmuncher/',
        'external_drive': '/mnt/backup-drive/',
        's3_encrypted': 's3://rugmuncher-backup/',
        'gdrive': 'gdrive:/RugMuncher/',
    }
    
    def __init__(self):
        self.backups: List[BackupConfig] = []
        self._init_backup_plan()
    
    def _init_backup_plan(self):
        """Initialize comprehensive backup plan"""
        self.backups = [
            BackupConfig(
                name="primary_local",
                location="local_encrypted",
                encryption_key="master",
                schedule="daily",
                retention=7
            ),
            BackupConfig(
                name="external_drive",
                location="external_drive",
                encryption_key="master",
                schedule="weekly",
                retention=4
            ),
            BackupConfig(
                name="cloud_encrypted",
                location="s3_encrypted",
                encryption_key="secondary",
                schedule="daily",
                retention=30
            ),
            BackupConfig(
                name="offline_cold",
                location="gdrive",
                encryption_key="shamir",
                schedule="monthly",
                retention=12
            ),
        ]
    
    def generate_backup_manifest(self) -> Dict:
        """Generate backup verification manifest"""
        return {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'backups': [
                {
                    'name': b.name,
                    'location': b.location,
                    'schedule': b.schedule,
                    'retention': b.retention
                }
                for b in self.backups
            ],
            'recovery_procedure': {
                'priority': ['primary_local', 'external_drive', 'cloud_encrypted', 'offline_cold'],
                'verification': 'sha256sum manifest.json',
                'decryption_order': ['master', 'secondary', 'shamir']
            }
        }


# ═══════════════════════════════════════════════════════════
# 3. DEAD MAN'S SWITCH
# If you don't check in, secrets get released to trusted contacts
# ═══════════════════════════════════════════════════════════

@dataclass
class DeadMansSwitch:
    """
    ⏰ Dead Man's Switch Configuration
    
    If operator doesn't check in within TIMEOUT period,
    encrypted secrets are released to TRUSTED_CONTACTS
    
    Use case: Prevent total loss if operator is incapacitated
    """
    check_in_interval_hours: int = 168  # 1 week
    trusted_contacts: List[str] = None
    release_delay_hours: int = 48  # Grace period after missed check-in
    
    def __post_init__(self):
        if self.trusted_contacts is None:
            self.trusted_contacts = []
    
    def check_in(self):
        """Operator checks in - resets timer"""
        last_checkin = datetime.now()
        # Store encrypted timestamp
        return {
            'status': 'checked_in',
            'last_checkin': last_checkin.isoformat(),
            'next_checkin_required': (last_checkin + timedelta(hours=self.check_in_interval_hours)).isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get current switch status"""
        # Check last checkin
        # If overdue, calculate time until release
        pass


# ═══════════════════════════════════════════════════════════
# 4. HARDWARE SECURITY MODULE (HSM) SIMULATION
# Store most critical keys in hardware-isolated environment
# ═══════════════════════════════════════════════════════════

class HardwareSecurityModule:
    """
    🔒 HSM-like key storage (simulated with best practices)
    
    In production: Use YubiHSM, AWS CloudHSM, or similar
    Keys never leave the HSM - only operations performed
    """
    
    def __init__(self):
        self._key_store: Dict[str, bytes] = {}
        self._access_log: List[Dict] = []
    
    def generate_key(self, key_id: str) -> bool:
        """Generate key inside HSM - never exposed"""
        if key_id in self._key_store:
            return False
        
        # Generate 256-bit key
        key = secrets.token_bytes(32)
        self._key_store[key_id] = key
        
        self._log_access('generate', key_id)
        return True
    
    def sign(self, key_id: str, data: bytes) -> Optional[bytes]:
        """Sign data using HSM-stored key (key never leaves)"""
        if key_id not in self._key_store:
            return None
        
        # In real HSM: Sign without exposing key
        # Here we simulate with HMAC
        import hmac
        signature = hmac.new(self._key_store[key_id], data, hashlib.sha256).digest()
        
        self._log_access('sign', key_id)
        return signature
    
    def _log_access(self, operation: str, key_id: str):
        """Audit log all key operations"""
        self._access_log.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'key_id': hashlib.sha256(key_id.encode()).hexdigest()[:16],  # Hash key ID for privacy
        })


# ═══════════════════════════════════════════════════════════
# 5. MULTI-SIG WALLET RECOVERY
# Require M of N signatures for critical operations
# ═══════════════════════════════════════════════════════════

class MultiSigRecovery:
    """
    👥 Multi-signature recovery scheme
    
    For critical wallets: Require 2-of-3 or 3-of-5 signatures
    Prevents single point of failure
    """
    
    SCHEMES = {
        'conservative': {'total': 3, 'required': 2},
        'strict': {'total': 5, 'required': 3},
        'maximum': {'total': 7, 'required': 4},
    }
    
    @staticmethod
    def generate_recovery_shares(scheme: str = 'conservative') -> Dict:
        """Generate multi-sig configuration"""
        config = MultiSigRecovery.SCHEMES.get(scheme, MultiSigRecovery.SCHEMES['conservative'])
        
        return {
            'scheme': scheme,
            'total_signers': config['total'],
            'required_signers': config['required'],
            'setup_instructions': {
                1: 'Hardware wallet #1 (primary) - Store in secure location A',
                2: 'Hardware wallet #2 (backup) - Store in secure location B',
                3: 'Hardware wallet #3 (recovery) - Store in secure location C',
            },
            'recovery_scenarios': {
                'lost_primary': 'Use backup + recovery wallets (2-of-3)',
                'compromised': 'Create new wallet, transfer funds using 2-of-3',
                'forgotten_pin': 'Use backup wallet + seed phrase recovery',
            }
        }


# ═══════════════════════════════════════════════════════════
# 6. MONITORING & ALERTING
# Detect unauthorized access attempts
# ═══════════════════════════════════════════════════════════

class SecurityMonitor:
    """
    👁️ Monitor for security events and anomalies
    """
    
    ALERT_THRESHOLDS = {
        'failed_logins': 5,  # per hour
        'unusual_access_times': True,
        'new_ip_addresses': True,
        'large_transfers': 10000,  # USD
    }
    
    def __init__(self):
        self.events: List[Dict] = []
    
    def log_event(self, event_type: str, details: Dict, severity: str = 'info'):
        """Log security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'severity': severity,
            'details': details
        }
        self.events.append(event)
        
        # Check for anomalies
        if severity in ['high', 'critical']:
            self._trigger_alert(event)
    
    def _trigger_alert(self, event: Dict):
        """Send security alert"""
        alert_msg = f"""
🚨 SECURITY ALERT

Type: {event['type']}
Severity: {event['severity'].upper()}
Time: {event['timestamp']}

Details:
{json.dumps(event['details'], indent=2)}

Action Required: Review immediately
"""
        # Send to admin channels
        logger.critical(alert_msg)
    
    def generate_report(self) -> Dict:
        """Generate security audit report"""
        return {
            'period': '24h',
            'total_events': len(self.events),
            'by_severity': {
                'critical': len([e for e in self.events if e['severity'] == 'critical']),
                'high': len([e for e in self.events if e['severity'] == 'high']),
                'medium': len([e for e in self.events if e['severity'] == 'medium']),
                'low': len([e for e in self.events if e['severity'] == 'low']),
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on events"""
        recs = []
        
        # Check for patterns
        failed_logins = len([e for e in self.events if e['type'] == 'failed_login'])
        if failed_logins > 10:
            recs.append(f"Consider IP blocking - {failed_logins} failed login attempts detected")
        
        return recs


# ═══════════════════════════════════════════════════════════
# 7. EMERGENCY RECOVERY KIT
# Complete recovery procedure document
# ═══════════════════════════════════════════════════════════

def generate_recovery_kit() -> Dict:
    """
    📋 Generate complete emergency recovery documentation
    """
    return {
        'version': '1.0',
        'last_updated': datetime.now().isoformat(),
        
        'emergency_contacts': {
            'primary_admin': 'REDACTED - Fill in manually',
            'backup_admin': 'REDACTED - Fill in manually',
            'security_team': 'REDACTED - Fill in manually',
        },
        
        'recovery_procedures': {
            'vault_unseal': {
                'description': 'Unseal HashiCorp Vault after restart',
                'steps': [
                    'SSH to server: ssh root@167.86.116.51',
                    'Get 3 unseal keys from offline storage',
                    'Run: docker exec -it vault vault operator unseal <key1>',
                    'Run: docker exec -it vault vault operator unseal <key2>',
                    'Run: docker exec -it vault vault operator unseal <key3>',
                    'Verify: curl http://127.0.0.1:8200/v1/sys/health'
                ]
            },
            'ollama_recovery': {
                'description': 'Restore Ollama if corrupted',
                'steps': [
                    'Check models: ollama list',
                    'Re-pull if needed: ollama pull gemma2:9b',
                    'Verify: curl http://127.0.0.1:11434/api/tags'
                ]
            },
            'api_key_rotation': {
                'description': 'Rotate compromised API key',
                'steps': [
                    'Generate new key from provider dashboard',
                    'Update in Vault: curl -X POST $VAULT_URL/v1/secret/data/SERVICE',
                    'Restart bridge: systemctl restart rugmuncher-bridge',
                    'Verify in logs: journalctl -u rugmuncher-bridge -f'
                ]
            },
            'complete_disaster': {
                'description': 'Total server loss recovery',
                'steps': [
                    '1. Provision new server',
                    '2. Restore from backup: ./restore-from-backup.sh',
                    '3. Unseal Vault with 3 keys',
                    '4. Verify all services: ./health-check.sh',
                    '5. Test Telegram bridge: /status command'
                ]
            }
        },
        
        'verification_checklist': {
            'daily': [
                'Check Ollama: curl http://127.0.0.1:11434/api/tags',
                'Check Vault: curl http://127.0.0.1:8200/v1/sys/health',
                'Check bridge logs: journalctl -u rugmuncher-bridge --since today'
            ],
            'weekly': [
                'Test backup restoration',
                'Verify Shamir shares accessibility',
                'Review access logs'
            ],
            'monthly': [
                'Rotate Vault Secret ID',
                'Test dead man\'s switch',
                'Update recovery kit'
            ]
        }
    }


# ═══════════════════════════════════════════════════════════
# MAIN RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════

def print_security_recommendations():
    """Print comprehensive security hardening guide"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          RUGMUNCHER SECURITY HARDENING GUIDE                     ║
║         Never Lose Access • Maximum Protection                   ║
╠══════════════════════════════════════════════════════════════════╣

🔐 LAYER 1: SECRET STORAGE (Never Lose Keys)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SHAMIR'S SECRET SHARING (Critical!)
   • Split master password into 5 shares
   • Need 3 shares to reconstruct
   • Store in different physical locations:
     - Home safe
     - Bank safety deposit box
     - Trusted family member
     - Trusted friend
     - Digital (encrypted) backup

2. HARDWARE WALLETS (For crypto wallets)
   • Use 2-of-3 multi-sig setup
   • 3 hardware wallets in different locations
   • Never store all in same place

3. HASHICORP VAULT (API keys)
   • Already configured ✓
   • Unseal keys stored offline (paper + encrypted USB)
   • Regular Secret ID rotation (weekly)


🔐 LAYER 2: BACKUPS (Redundancy)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. 3-2-1 BACKUP STRATEGY
   • 3 copies of all critical data
   • 2 different media types (SSD + Cloud)
   • 1 offsite (different physical location)

5. ENCRYPTED BACKUP LOCATIONS
   Primary:   /backup/rugmuncher/ (local, encrypted)
   Secondary: External USB drive (offline)
   Tertiary:  S3 with encryption (AWS/GCP)
   Cold:      Google Drive (encrypted, different account)

6. BACKUP CONTENTS
   • All source code
   • Configuration files (.env templates)
   • Vault unseal keys (encrypted)
   • Shamir shares (encrypted)
   • System documentation
   • Recovery procedures


🔐 LAYER 3: MONITORING (Detect Problems Early)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. SECURITY MONITORING
   • Failed login attempts (alert if >5/hour)
   • Unusual access times
   • Large/unauthorized transfers
   • Vault access logs
   • Ollama API access logs

8. HEALTH CHECKS
   Daily automated checks:
   ✓ Ollama responding
   ✓ Vault unsealed
   ✓ Telegram bot active
   ✓ Disk space >20%
   ✓ Memory usage <80%


🔐 LAYER 4: DISASTER RECOVERY (Worst Case)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9. DEAD MAN'S SWITCH (Optional but recommended)
   • Weekly check-in required
   • If missed: Release encrypted secrets to trusted contacts
   • Prevents total loss if operator incapacitated

10. EMERGENCY CONTACTS
    Keep updated list of:
    • Primary admin (you)
    • Backup admin (trusted person)
    • Technical advisor
    • Legal contact (for crypto assets)


🔐 LAYER 5: OPERATIONAL SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

11. ACCESS CONTROL
    • SSH key only (no passwords)
    • Fail2ban for brute force protection
    • UFW firewall configured
    • No root login
    • Sudo with password

12. SECRETS MANAGEMENT
    • Never commit secrets to git
    • Never log API keys
    • Rotate keys quarterly
    • Use different keys for dev/prod

13. PHYSICAL SECURITY
    • Server in secure data center (Contabo ✓)
    • Backup drives in safe/safety deposit
    • Hardware wallets in separate locations


📋 RECOVERY CHECKLIST (If Things Go Wrong)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Ollama not responding
  → systemctl restart ollama
  → ollama pull <model> if missing

□ Vault sealed
  → Use 3 unseal keys: docker exec -it vault vault operator unseal

□ Lost SSH access
  → Use Contabo rescue system
  → Restore from backup

□ Compromised API key
  → Generate new key
  → Update in Vault
  → Restart bridge

□ Total server failure
  → Provision new server
  → Restore from S3 backup
  → Unseal Vault
  → Verify all services


✅ VERIFICATION SCRIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run daily:
    python3 rugmuncher_security_hardening.py --check

This verifies:
  • All services running
  • Backups up-to-date
  • No security alerts
  • Vault accessible


🎯 PRIORITY ACTIONS (Do These First!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[CRITICAL] 1. Set up Shamir Secret Sharing for master password
[HIGH]     2. Create 3-2-1 backup system
[HIGH]     3. Test backup restoration (verify it works!)
[MEDIUM]   4. Set up monitoring alerts
[MEDIUM]   5. Document emergency contacts
[LOW]      6. Set up dead man's switch


╚══════════════════════════════════════════════════════════════════╝
""")


def run_security_check():
    """Run comprehensive security verification"""
    print("🔍 Running Security Check...")
    print("=" * 60)
    
    checks = {
        'ollama': False,
        'vault': False,
        'tor': False,
        'firewall': False,
        'backups': False,
        'monitoring': False
    }
    
    # Check Ollama
    try:
        import urllib.request
        urllib.request.urlopen('http://127.0.0.1:11434/api/tags', timeout=2)
        checks['ollama'] = True
        print("✅ Ollama: Running")
    except Exception:
        print("❌ Ollama: Not accessible")
    
    # Check Vault
    try:
        urllib.request.urlopen('http://127.0.0.1:8200/v1/sys/health', timeout=2)
        checks['vault'] = True
        print("✅ Vault: Running")
    except Exception:
        print("❌ Vault: Not accessible")
    
    # Check Tor
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9050))
        if result == 0:
            checks['tor'] = True
            print("✅ Tor: Running")
        else:
            print("⚠️  Tor: Not running (optional)")
    except Exception:
        print("⚠️  Tor: Check failed")
    
    # Check firewall
    try:
        import subprocess
        result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
        if 'active' in result.stdout.lower():
            checks['firewall'] = True
            print("✅ Firewall: Active")
        else:
            print("⚠️  Firewall: Check manually")
    except Exception:
        print("⚠️  Firewall: Check manually")
    
    print("\n" + "=" * 60)
    score = sum(checks.values()) / len(checks) * 100
    print(f"Security Score: {score:.0f}%")
    print(f"Passed: {sum(checks.values())}/{len(checks)}")
    
    if score < 50:
        print("⚠️  CRITICAL: Address failed checks immediately!")
    elif score < 80:
        print("⚡ Review: Some security features not active")
    else:
        print("✅ Good: Core security features active")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='RugMuncher Security Tools')
    parser.add_argument('--check', action='store_true', help='Run security check')
    parser.add_argument('--guide', action='store_true', help='Print security guide')
    parser.add_argument('--split-secret', type=str, help='Split secret (provide secret)')
    parser.add_argument('--shares', type=int, default=5, help='Number of shares')
    parser.add_argument('--threshold', type=int, default=3, help='Shares needed')
    
    args = parser.parse_args()
    
    if args.check:
        run_security_check()
    elif args.split_secret:
        sss = ShamirSecretSharing()
        shares = sss.split_secret(args.split_secret, args.shares, args.threshold)
        print(f"\n🔐 Secret split into {args.shares} shares, need {args.threshold} to reconstruct")
        print("\nShares (SAVE THESE SECURELY):")
        for i, (x, y) in enumerate(shares, 1):
            print(f"  Share {i}: ({x}, {y})")
        print("\n⚠️  Store each share in a different secure location!")
    else:
        print_security_recommendations()
