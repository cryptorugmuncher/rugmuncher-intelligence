# 🎨 RugMuncher Custom Contract Factory Guide

**Fully customizable smart contracts for Base and Solana with taxes, blacklists, and all the features you need.**

---

## Overview

The Custom Contract Factory lets you deploy fully customizable tokens with:

- **Adjustable Taxes**: Buy/sell/transfer taxes with custom distribution
- **Blacklist**: Block suspicious addresses from trading
- **Whitelist**: Fee exemptions for team, liquidity, partners
- **Anti-Whale**: Max wallet and transaction limits
- **Auto-Liquidity**: Automatic LP generation from taxes
- **Mint/Burn**: Token supply controls
- **Reflection**: Holder rewards (redistribution)

### Supported Chains

| Chain | Standard | Features |
|-------|----------|----------|
| **Base** | ERC-20 | Full feature set |
| **Solana** | SPL Token | Full feature set |

---

## Quick Start

```python
from rugmuncher_custom_contracts import CustomTokenBuilder

# Build your custom token
config = (CustomTokenBuilder()
    .on_chain('base')
    .with_name('RugMuncher Token', 'RUG')
    .with_supply(1_000_000_000, 18)
    .with_taxes(buy=2.5, sell=5.0, transfer=0)
    .with_tax_distribution(
        liquidity=50,
        marketing=30,
        development=10,
        burn=10
    )
    .with_fee_recipients(
        marketing='0xYourMarketingWallet',
        development='0xYourDevWallet'
    )
    .with_blacklist(enabled=True)
    .with_anti_whale(max_wallet=2.0, max_tx=1.0)
    .mintable(True)
    .burnable(True)
    .with_admin('0xYourAdminAddress')
    .build())

# Generate contract
builder = CustomTokenBuilder()
builder.config = config
contract_code = builder.generate_contract()

with open('RugMuncherToken.sol', 'w') as f:
    f.write(contract_code)
```

---

## Tax Configuration

```python
# Configure taxes
.with_taxes(buy=2.5, sell=5.0, transfer=0)

# Distribute tax revenue
.with_tax_distribution(
    liquidity=50,
    marketing=30,
    development=10,
    burn=10
)
```

---

## Blacklist & Whitelist

```python
# Blacklist configuration
.with_blacklist(enabled=True, can_unblacklist=True)
.with_initial_blacklist(['0xBot1...', '0xBot2...'])

# Whitelist for exemptions
.with_whitelist(enabled=True)
```

---

## Anti-Whale Protection

```python
.with_anti_whale(
    max_wallet_percent=2.0,
    max_tx_percent=1.0,
    cooldown_seconds=60
)
```

---

## Contract Deployment

```python
from rugmuncher_contract_deployer import ContractDeployer

deployer = ContractDeployer(vault)
deployment_id = deployer.request_deployment(config)
result = deployer.approve_deployment(deployment_id, "admin", wallet_id)
```

---

**Create your perfect token. Control every aspect. Deploy with confidence.**
