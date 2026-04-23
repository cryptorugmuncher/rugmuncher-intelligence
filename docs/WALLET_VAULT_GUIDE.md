# 🔐 RugMuncher Wallet Vault & Contract Deployment Guide

**Your money, your wallets, your control. Multi-chain, encrypted, human-supervised.**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Supported Chains](#supported-chains)
3. [Wallet Vault System](#wallet-vault-system)
4. [Encrypted Storage](#encrypted-storage)
5. [Human Oversight System](#human-oversight-system)
6. [Wallet Rotation](#wallet-rotation)
7. [Contract Deployment](#contract-deployment)
8. [CRM 2.0 Configuration](#crm-20-configuration)
9. [Best Practices](#best-practices)
10. [Emergency Procedures](#emergency-procedures)

---

## Overview

The Wallet Vault provides:

- **Multi-chain wallet creation**: BTC, ETH, SOL, XMR, TRX, BASE
- **AES-256 encrypted storage** for all credentials
- **Automated wallet rotation** with privacy preservation
- **Human-in-the-loop approval** for all sensitive operations
- **CRM 2.0 contract deployment** on Base and Solana
- **Complete fund control** - withdraw, swap, rotate at will

---

## Supported Chains

| Chain | Symbol | Rotation | Multi-Sig | Notes |
|-------|--------|----------|-----------|-------|
| **Bitcoin** | BTC | 30 days | ✅ | Native SegWit (bech32) |
| **Ethereum** | ETH | 30 days | ✅ | Standard EVM |
| **Solana** | SOL | 14 days | ✅ | Native SPL |
| **Monero** | XMR | 7 days | ✅ | Privacy-focused |
| **Tron** | TRX | 30 days | ❌ | TRC20 support |
| **Base** | ETH | 30 days | ✅ | Ethereum L2 |

---

## Wallet Vault System

### Quick Start

```python
from rugmuncher_wallet_vault import WalletVault, CHAIN_CONFIG

# Initialize vault (prompts for master password)
vault = WalletVault()

# Create wallets across multiple chains
btc_wallet = vault.create_wallet(
    chain='bitcoin',
    name='Primary BTC Vault',
    requires_approval_above=0.5,  # BTC - requires approval above 0.5 BTC
    daily_limit=2.0,
    tags=['primary', 'cold_storage']
)

eth_wallet = vault.create_wallet(
    chain='ethereum',
    name='ETH Operations',
    requires_approval_above=5.0,  # ETH
    daily_limit=20.0,
    tags=['operations', 'hot_wallet']
)

sol_wallet = vault.create_wallet(
    chain='solana',
    name='SOL Trading',
    requires_approval_above=100.0,  # SOL
    daily_limit=500.0,
    tags=['trading', 'high_frequency']
)

xmr_wallet = vault.create_wallet(
    chain='monero',
    name='Privacy Reserve',
    requires_approval_above=10.0,  # XMR
    daily_limit=50.0,
    tags=['privacy', 'reserve']
)

print(f"BTC Address: {btc_wallet.address}")
print(f"ETH Address: {eth_wallet.address}")
print(f"SOL Address: {sol_wallet.address}")
print(f"XMR Address: {xmr_wallet.address}")
```

### Wallet Properties

```python
wallet = vault.get_wallet(wallet_id)

print(f"""
Wallet: {wallet.name}
Chain: {wallet.chain.upper()}
Address: {wallet.address}
Balance: {wallet.balance} {CHAIN_CONFIG[wallet.chain]['symbol']}
Status: {wallet.status.value}
Expires: {wallet.expires_at}
Daily Limit: {wallet.daily_limit}
Approval Threshold: {wallet.requires_approval_above}
Tags: {', '.join(wallet.tags)}
""")
```

---

## Encrypted Storage

### Encryption Details

- **Algorithm**: AES-256-GCM (or Fernet as fallback)
- **Key Derivation**: PBKDF2 (100,000 iterations)
- **Storage**: JSON with encrypted fields
- **Backup**: Automatic encrypted backups on all changes

### Storage Format

```json
{
  "wallets": {
    "a1b2c3d4...": {
      "id": "a1b2c3d4...",
      "chain": "ethereum",
      "name": "ETH Operations",
      "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
      "public_key": "0x...",
      "encrypted_private_key": "gAAAAAB...",
      "encrypted_seed": "gAAAAAB...",
      "created_at": "2024-01-15T10:30:00",
      "expires_at": "2024-02-14T10:30:00",
      "status": "active",
      "tags": ["operations", "hot_wallet"]
    }
  },
  "rotations": [...],
  "pending_approvals": [...]
}
```

### Backup System

```python
# Automatic backups created on:
# - Wallet creation
# - Rotation completion
# - Manual request

# List backups
import glob
backups = glob.glob("wallet_backups/vault_*.enc")

# Restore from backup (if needed)
import shutil
shutil.copy2("wallet_backups/vault_emergency_20240115_143022.enc", "wallet_vault.enc")
```

---

## Human Oversight System

### Approval Required For

1. **Private Key Export** - Decrypting any private key
2. **Wallet Rotation** - Creating replacement wallets
3. **High-Value Transfers** - Above configured threshold
4. **Contract Deployment** - All smart contract deployments
5. **Emergency Withdrawal** - Draining wallets

### Approval Flow

```python
# 1. Request sensitive operation
approval_id = vault.request_rotation(
    wallet_id=wallet_id,
    reason="scheduled_rotation",
    requested_by="auto_scheduler"
)

# 2. Admin reviews pending approvals
pending = vault.get_pending_approvals()
for pa in pending:
    print(f"[{pa['id'][:8]}] {pa['action_type']} - {pa['details']}")

# 3. Admin approves with password
result = vault.approve_rotation(approval_id, admin_password="your_admin_pass")

# New wallet created, old wallet archived
new_wallet = result['new_wallet']
old_private_key = result['old_private_key']  # For fund transfer

# 4. Transfer funds (manual or automated)
# - Use old_private_key to sign transaction
# - Send to new_wallet.address
```

### Rejecting Approvals

```python
vault.reject_approvals(
    approval_id="abc123...",
    reason="Suspicious request - verify identity"
)
```

---

## Wallet Rotation

### Why Rotate?

- **Privacy**: Break transaction chain analysis
- **Security**: Limit exposure of any single key
- **Compliance**: Meet institutional requirements
- **Operational**: Separate concerns per wallet

### Automated Rotation

```python
# Check rotation status
status = vault.get_rotation_status()

print(f"""
Active: {len(status['active'])}
Expiring (7 days): {len(status['expiring_7d'])}
Expiring (30 days): {len(status['expiring_30d'])}
Expired: {len(status['expired'])}
Pending Approval: {len(status['pending_approval'])}
""")

# Auto-request rotation for expired
approval_ids = vault.auto_rotate_expired()
print(f"Rotation requested for {len(approval_ids)} wallets")
```

### Manual Rotation

```python
# Request rotation with custom reason
approval_id = vault.request_rotation(
    wallet_id=btc_wallet.id,
    reason="suspected_exposure",
    requested_by="security_team"
)

# After approval, transfer funds
result = vault.approve_rotation(approval_id, admin_password)

if result['transfer_required']:
    print(f"Transfer {result['old_balance']} from old to new wallet")
    # Implement transfer logic here
```

### Rotation History

```python
# View all rotations
for rotation in vault.rotations:
    print(f"""
    Rotation: {rotation['id'][:8]}
    {rotation['chain'].upper()}: {rotation['old_wallet_id'][:8]} -> {rotation['new_wallet_id'][:8]}
    Reason: {rotation['reason']}
    Funds: {rotation['funds_transferred']}
    Date: {rotation['completed_at']}
    """)
```

---

## Contract Deployment

### Supported Contracts

| Contract | Base | Solana | Description |
|----------|------|--------|-------------|
| **CRM 2.0** | ✅ | ✅ | Customer management for investigations |
| Token | 🚧 | 🚧 | ERC20/SPL tokens |
| Multi-sig | 🚧 | 🚧 | Shared wallet control |
| Vesting | 🚧 | 🚧 | Token vesting schedules |

### Deploy CRM 2.0 to Base

```python
from rugmuncher_contract_deployer import (
    ContractDeployer, 
    CRMConfigBuilder,
    DeploymentConfig
)

# Build configuration
config = (CRMConfigBuilder()
    .on_chain('base')
    .with_admin('0xYourAdminAddress')
    .with_operators([
        '0xOperator1Address',
        '0xOperator2Address'
    ])
    .with_fee_recipient('0xFeeRecipientAddress')
    .with_platform_fee(250)  # 2.5% (basis points)
    .with_multisig(
        threshold=2,
        signers=[
            '0xSigner1',
            '0xSigner2', 
            '0xSigner3'
        ]
    )
    .with_emergency_controls(enabled=True)
    .upgradeable(enabled=True)
    .build())

# Initialize deployer
deployer = ContractDeployer(vault)

# Request deployment (requires approval)
deployment_id = deployer.request_deployment(
    config=config,
    requested_by="dev_team"
)

print(f"Deployment requested: {deployment_id}")

# Approve and deploy (human oversight)
result = deployer.approve_deployment(
    deployment_id=deployment_id,
    approved_by=" CTO",
    wallet_id=eth_wallet.id  # Use this wallet to deploy
)

print(f"Contract deployed!")
print(f"Address: {result['contract_address']}")
print(f"Explorer: {result['explorer_url']}")
```

### Deploy CRM 2.0 to Solana

```python
# Same configuration, different chain
config = (CRMConfigBuilder()
    .on_chain('solana')
    .with_admin('YourSolanaAddress')
    .with_fee_recipient('YourSolanaFeeAddress')
    .with_platform_fee(250)
    .build())

deployment_id = deployer.request_deployment(config)
result = deployer.approve_deployment(deployment_id, "CTO", sol_wallet.id)
```

### Export Contract Source

```python
# Export for manual review/audit
source_file = deployer.export_contract_source(
    contract_type=ContractType.CRM_V2,
    chain='base',
    output_dir='contracts'
)
print(f"Source exported: {source_file}")
```

---

## CRM 2.0 Configuration

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `admin_address` | Address | Required | Contract owner |
| `operator_addresses` | List | [] | Day-to-day operators |
| `fee_recipient` | Address | Required | Where fees go |
| `platform_fee_bps` | int | 250 | Fee in basis points (100 = 1%) |
| `require_multisig` | bool | False | Enable multi-sig |
| `multisig_threshold` | int | 1 | Signatures required |
| `emergency_withdrawal` | bool | True | Emergency escape hatch |
| `upgradeable` | bool | True | Allow upgrades |

### CRM 2.0 Features

1. **Case Management**
   - Create investigation cases
   - Assign investigators
   - Track status (Open → In Progress → Resolved)

2. **Evidence Management**
   - IPFS hash storage
   - Evidence verification
   - Chain of custody

3. **Payment Handling**
   - Client deposits
   - Milestone payments
   - Platform fee collection
   - Investigator payouts

4. **Access Control**
   - Admin role
   - Operator role
   - Investigator role
   - Multi-sig support

5. **Emergency Controls**
   - Pause functionality
   - Emergency withdrawal
   - Upgrade mechanism

---

## Best Practices

### 1. Wallet Segregation

```python
# Separate wallets by purpose
wallets = {
    'btc_cold': vault.create_wallet('bitcoin', 'Cold Storage', 
                                    requires_approval_above=1.0),
    'btc_hot': vault.create_wallet('bitcoin', 'Hot Wallet',
                                   requires_approval_above=0.1),
    'eth_treasury': vault.create_wallet('ethereum', 'Treasury',
                                        requires_approval_above=10.0),
    'eth_operations': vault.create_wallet('ethereum', 'Operations',
                                          requires_approval_above=1.0),
    'sol_trading': vault.create_wallet('solana', 'Trading',
                                       requires_approval_above=50.0),
    'xmr_private': vault.create_wallet('monero', 'Private Reserve',
                                       requires_approval_above=5.0),
}
```

### 2. Regular Rotation Schedule

```python
def weekly_rotation_check():
    """Run weekly to check and rotate expired wallets"""
    status = vault.get_rotation_status()
    
    # Auto-request rotation for expired
    for wallet in status['expired']:
        vault.request_rotation(wallet.id, "scheduled")
    
    # Alert on expiring soon
    if status['expiring_7d']:
        alert_admin(f"{len(status['expiring_7d'])} wallets expiring in 7 days")
```

### 3. Multi-Sig for Critical Operations

```python
# Require multi-sig for high-value wallets
high_value_config = (CRMConfigBuilder()
    .with_multisig(
        threshold=3,  # Need 3 of 5 signatures
        signers=[
            '0xCEOAddress',
            '0xCTOAddress',
            '0xCFOAddress',
            '0xLegalAddress',
            '0xSecurityAddress'
        ]
    )
    .build())
```

### 4. Backup Verification

```python
def verify_backup_integrity():
    """Verify backups are valid monthly"""
    import glob
    
    backups = glob.glob("wallet_backups/vault_*.enc")
    
    for backup in backups[-3:]:  # Check last 3
        # Try to load backup
        test_vault = WalletVault(storage_path=backup)
        print(f"✅ {backup}: {len(test_vault.wallets)} wallets")
```

### 5. Audit Trail

```python
# All operations logged
logger.info(f"Wallet created: {wallet.address} by {requester}")
logger.info(f"Rotation approved: {rotation_id} by {admin}")
logger.info(f"Contract deployed: {address} by {deployer}")
```

---

## Emergency Procedures

### Scenario: Lost Master Password

```python
# 1. Restore from backup with old password
# 2. Create new vault with new password
# 3. Transfer all wallets to new vault
# 4. Rotate all wallets (new keys)

def emergency_vault_recovery():
    """Complete vault recovery procedure"""
    # Restore from most recent backup
    backups = sorted(glob.glob("wallet_backups/vault_*.enc"))
    
    if backups:
        latest_backup = backups[-1]
        print(f"Restoring from: {latest_backup}")
        
        # Restore and create new vault
        import shutil
        shutil.copy2(latest_backup, "wallet_vault_recovered.enc")
        
        # Prompt for new master password
        vault = WalletVault(storage_path="wallet_vault_recovered.enc")
        
        # Rotate ALL wallets immediately
        for wallet in list(vault.wallets.values()):
            approval_id = vault.request_rotation(
                wallet.id, 
                "security_recovery",
                "security_team"
            )
            print(f"Rotation requested: {wallet.chain} - {approval_id[:8]}")
```

### Scenario: Suspected Key Compromise

```python
def breach_response():
    """Immediate response to suspected breach"""
    
    # 1. Identify affected wallets
    affected_chains = ['ethereum', 'solana']  # Based on incident
    
    # 2. Emergency rotate ALL wallets on affected chains
    for chain in affected_chains:
        wallets = vault.get_wallets_by_chain(chain)
        for wallet in wallets:
            # Force rotation
            approval_id = vault.request_rotation(
                wallet.id,
                "security_breach_response",
                "security_team"
            )
            # Emergency approve
            vault.approve_rotation(approval_id, emergency_password)
    
    # 3. Generate new backup codes
    # 4. Audit all recent transactions
    # 5. Notify relevant parties
```

### Scenario: Contract Emergency

```python
# Use CRM 2.0 emergency functions
def emergency_contract_response(contract_address, deployment_id):
    """Pause or emergency withdraw from contract"""
    
    deployer = ContractDeployer(vault)
    deployment = deployer.get_deployment_status(deployment_id)
    
    if deployment and deployment['chain'] == 'base':
        # Call emergencyWithdraw or pause function
        # Requires admin wallet
        admin_wallet = vault.get_wallet(admin_wallet_id)
        
        # Sign and send emergency transaction
        # (Implementation depends on web3.js/ethers.js integration)
        pass
```

---

## CLI Usage

### Interactive Mode

```bash
python rugmuncher_wallet_vault.py
```

Output:
```
======================================================================
🔐 RugMuncher Multi-Chain Wallet Vault
======================================================================

Total wallets: 12
  ✅ Active: 10
  ⏰ Expiring (7d): 1
  ⏰ Expiring (30d): 1
  ❌ Expired: 0
  ⏳ Pending approval: 0
  📦 Archived: 2

⚠️  PENDING APPROVALS:
   [a3f7e2d1] ROTATE - 0x742d35Cc6634C0532925...

Commands:
  1. Create new wallet
  2. List wallets
  3. Request rotation
  4. Approve pending request
  5. Show wallet details
  6. Auto-rotate expired
  7. Export credentials (requires approval)
```

### One-Liners

```bash
# Quick status
python -c "from rugmuncher_wallet_vault import WalletVault; v=WalletVault(); s=v.get_rotation_status(); print(f'Expired: {len(s[\"expired\"])}')"

# Create wallet
python -c "from rugmuncher_wallet_vault import WalletVault; v=WalletVault(); w=v.create_wallet('bitcoin', 'Test'); print(w.address)"
```

---

## Integration Examples

### With Existing Credential System

```python
from credential_rotation_system import RotationManager
from rugmuncher_wallet_vault import WalletVault

# Link credential rotation with wallet vault
cred_manager = RotationManager()
vault = WalletVault()

# When rotating API keys, also rotate wallets
def full_security_rotation():
    # Rotate API credentials
    for cred in cred_manager.check_rotation_status()['expired']:
        cred_manager.rotate_credential(cred.id)
    
    # Rotate wallets
    for wallet_id in vault.wallets:
        vault.request_rotation(wallet_id, "scheduled")
```

### With External APIs

```python
# Get wallet balance from blockchain
def update_wallet_balances(vault):
    for wallet in vault.wallets.values():
        if wallet.chain == 'ethereum':
            # Use Web3 to get balance
            pass
        elif wallet.chain == 'solana':
            # Use Solana API
            pass
```

---

## Installation Requirements

```bash
# Core dependencies
pip install cryptography

# Optional chain-specific libraries
pip install web3          # Ethereum/Base
pip install solders       # Solana
pip install bit           # Bitcoin
pip install monero        # Monero
pip install tronpy        # Tron
```

---

**Remember: Your keys, your coins, your responsibility. Stay secure.**
