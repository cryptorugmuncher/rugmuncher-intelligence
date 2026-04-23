# Comprehensive Wallet Database - Quick Guide

## 🎯 Purpose

Build a complete database of **every wallet** from your snapshot with **direct scammer connections** mapped.

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `comprehensive_wallet_db.py` | Core database with connection mapping |
| `snapshot_processor.py` | Process wallet snapshot data |
| `transaction_analyzer.py` | Analyze transactions for connections |
| `build_comprehensive_db.py` | Master build script |
| `wallet_snapshot_template.csv` | Template for your snapshot data |

---

## 🚀 Quick Start

### Step 1: Prepare Your Snapshot Data

Create a CSV file with your wallet snapshot:

```csv
address,balance_sol,balance_crm,created_at,notes
8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj,45.0,19700000,2025-08-25,Bridge wallet
HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc,0.0,79700000,2025-08-20,Dump wallet
... (add all wallets from snapshot)
```

### Step 2: Prepare Transaction Data (Optional)

If you have transaction data, create:

```csv
signature,timestamp,from,to,amount,token
sig1,2026-03-28T09:19:00Z,WalletA,8eVZa7b...,1000000,CRM
sig2,2026-03-28T09:20:00Z,WalletA,8eVZa7b...,500000,CRM
...
```

### Step 3: Build the Database

```bash
cd /root/crm_audit/data

python build_comprehensive_db.py \
  --snapshot my_wallets.csv \
  --transactions my_transactions.csv \
  --output ./results
```

---

## 📊 Output Files

| File | Contents |
|------|----------|
| `comprehensive_wallet_db.json` | Full database (all wallets) |
| `comprehensive_wallet_db.csv` | CSV version for spreadsheets |
| `connection_report.json` | Summary of connections found |
| `connected_wallets.json` | Wallets with scammer connections |
| `high_risk_wallets.csv` | Wallets with score >= 0.5 |
| `transaction_report.json` | Transaction analysis (if provided) |

---

## 🔗 Connection Scoring

| Score | Status | Risk Level |
|-------|--------|------------|
| 1.0 | Confirmed Scammer | Critical |
| 0.8-0.99 | Suspected Scammer | Critical |
| 0.5-0.79 | Connected | High |
| 0.2-0.49 | Associated | Medium |
| 0.0-0.19 | Clean | Low |

---

## 🏗️ Known Scammer Tiers

| Tier | Wallets | Role |
|------|---------|------|
| 0 | 2 | Root Funding |
| 1 | 4 | Senior Treasuries ($29M+) |
| 2 | 2 | Secondary Routers |
| 3 | 3 | Bridge Wallets (SMOKING GUN) |
| 4 | 5 | Coordinators/Botnet |
| 5 | 7 | Field Operatives (103M CRM) |
| 6 | 2 | Active Dump |

---

## 💡 Usage Examples

### Find All Connected Wallets
```python
from data.comprehensive_wallet_db import get_comprehensive_db

db = get_comprehensive_db()
connected = db.find_connected_wallets(min_score=0.3)

for wallet in connected:
    print(f"{wallet.address}: score={wallet.connection_score:.2f}")
```

### Check Single Wallet
```python
wallet = db.wallets.get("SOME_WALLET_ADDRESS")
if wallet:
    print(f"Status: {wallet.status.value}")
    print(f"Score: {wallet.connection_score}")
    print(f"Connections: {wallet.get_connection_summary()}")
```

### Export Specific Tier
```python
tier_5 = db.get_wallets_by_tier(5)  # Field operatives
for w in tier_5:
    print(f"{w.address}: {w.balance_crm:,.0f} CRM")
```

---

## 🔍 What Gets Flagged

### Automatic Flags
- ✅ Known scammer wallets (pre-loaded)
- ✅ Direct transactions with scammers
- ✅ Rapid-fire transaction patterns
- ✅ Round-number coordination
- ✅ Dusting (witness intimidation)

### Connection Types
- `direct_transaction` - Direct tx between wallets
- `funding` - Funded by scammer
- `received_from` - Received from scammer
- `sent_to` - Sent to scammer
- `common_counterparty` - Shared connections
- `botnet_link` - Same botnet deployment
- `temporal_proximity` - Similar timing

---

## 📈 Database Schema

```python
{
  "address": "wallet_address",
  "status": "confirmed_scammer|suspected|connected|clean|unknown",
  "tier": 0-6,  # For known scammers
  "connection_score": 0.0-1.0,
  "balance_sol": 100.5,
  "balance_crm": 1000000.0,
  "scammer_connections": [
    {
      "target_address": "scammer_wallet",
      "connection_type": "received_from",
      "strength": 0.8,
      "evidence": ["tx_sig1", "tx_sig2"],
      "transaction_count": 5,
      "total_value_transferred": 5000000.0
    }
  ],
  "risk_level": "critical|high|medium|low",
  "flags": ["HIGH_SCAMMER_CONNECTION", "RAPID_FIRE"]
}
```

---

## 🎯 Next Steps

1. **Prepare your snapshot** → Fill `wallet_snapshot_template.csv`
2. **Add transaction data** (if available)
3. **Run build script** → `python build_comprehensive_db.py`
4. **Review high_risk_wallets.csv** → Prioritize investigation
5. **Export to main system** → Use with Omega Forensic V5

---

## 🆘 Troubleshooting

### "No wallets loaded"
- Check CSV has header row
- Verify column names match template

### "No connections found"
- Need transaction data for connection analysis
- Or manually flag connections

### "Wrong format"
- Use `.csv` for CSV files
- Use `.json` for JSON files

---

**Ready to map every wallet connection!**
