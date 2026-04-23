# New Evidence Classification Report
## Auto-Ingest Results

---

## Files Processed

| File | Type | Category | Priority | Case |
|------|------|----------|----------|------|
| `transactions.json` | Helius Export | Transaction Data | **HIGH** | GENERAL_CRYPTO_INVESTIGATION |
| `transactions (2).json` | Helius Export | Transaction Data | **HIGH** | GENERAL_CRYPTO_INVESTIGATION |
| `transactions (3).json` | Helius Export | Transaction Data | **HIGH** | GENERAL_CRYPTO_INVESTIGATION |
| `top_deployers_pump.csv` | Pump.fun Leaderboard | Threat Intelligence | **CRITICAL** | PUMP_FUN_ANALYSIS_2026 |
| `SOSANA_Litepaper_v2.0.pdf` | Project Documentation | Documentation | MEDIUM | SOSANA_RICO_2026 |

---

## 1. Helius Transaction Exports (3 files)

**Classification:** `helius_transactions` | **Priority:** HIGH

### Content Summary
- **Total Transactions:** 100+ per file
- **Format:** Helius Webhook API export
- **Data:** Full transaction details with account changes, transfers, fees

### Key Data Points
```json
{
  "signature": "Transaction signature",
  "type": "TRANSFER | SWAP | MINT | BURN",
  "feePayer": "Wallet paying fees",
  "timestamp": "Unix timestamp",
  "nativeTransfers": ["SOL transfers"],
  "tokenTransfers": ["SPL token transfers"],
  "accountData": ["Account balance changes"]
}
```

### Entities Extracted
- Fee payer wallets
- Transfer senders/recipients
- Token mint addresses
- Program IDs interacted with

### Investigation Value
- **Pattern Detection:** Identify coordinated transactions
- **Flow Tracing:** Follow fund movements
- **Behavioral Analysis:** Wallet interaction patterns

---

## 2. Pump.fun Deployer Leaderboard

**Classification:** `pump_deployers` | **Priority:** CRITICAL

### Content Summary
- **Total Deployers:** 225 addresses
- **Total Tokens Deployed:** 194,446
- **Combined PnL:** $78,889,167.88
- **Average Winrate:** 44.4%

### Top Risk Indicators

| Rank | Address | Tokens | PnL | Winrate | Risk Level |
|------|---------|--------|-----|---------|------------|
| 1 | bwamJzztZ... | 8,902 | $5.5M | 33.2% | 🔴 HIGH |
| 2 | 4dnWLzmdk... | 7,177 | $889K | 29.8% | 🔴 HIGH |
| 3 | AxmFqz3pb... | 6,140 | $151K | 11.6% | 🔴 CRITICAL |
| 4 | 99UtKhdi1... | 3,790 | $773K | 19.3% | 🔴 HIGH |
| 5 | moanTeQ4d... | 3,435 | $836K | 25.4% | 🔴 HIGH |

### Serial Rugger Detection Criteria
- **High Volume:** >1000 tokens deployed
- **Low Winrate:** <30% success rate
- **Pattern:** Repeated deployments, quick exits

### Addresses Flagged for Deep Analysis
```
AxmFqz3pbhj6HDK9dC1u7LsYP3rbsTJyKkeCMSpAxrgU
  └─ 6,140 tokens | 11.6% winrate | $150K PnL
  
4dnWLzmdkLeuDe6hwRBpPqrDbQZ59hpoBu8JLztAescf
  └─ 7,177 tokens | 29.8% winrate | $889K PnL
  
99UtKhdi1RfmMGRpi7kbWz6AQ2y4JkFmxC3swMVMDioZ
  └─ 3,790 tokens | 19.3% winrate | $773K PnL
```

### Cross-Reference with SOSANA Case
- ✅ No direct overlap with known SOSANA entities
- ⚠️ Recommend: Trace if any SOSANA holders also appear in deployer list

---

## 3. SOSANA Litepaper v2.0

**Classification:** `litepaper` | **Priority:** MEDIUM

### Key Intelligence Extracted

#### Token Contract
```
Address: 49jdQxUkKtuvorvnwWqDzUoYKEjfgroTzHkQqXG9YFMj
Total Supply: 88,888,888 SOSANA
```

#### Tokenomics Structure
| Allocation | Percentage | Amount | Vesting |
|------------|------------|--------|---------|
| Reserve Treasury | 41.6% | 36,977,588 | 5-year, 6-month cliff |
| Vesting (Team/Pre-sale) | 37.4% | 33,222,412 | 18-month |
| Initial Liquidity | ~11% | ~9,800,000 | Locked at launch |
| Airdrop/Marketing | 10% | 8,888,888 | Available |

#### Transaction Tax (3%)
- **Stability Wallet:** 1.00% (liquidity/market-making)
- **Degen Wallet:** 1.00% (Live Token rewards)
- **Marketing Treasury:** 0.50% (partnerships/growth)
- **Pre-Launch Degen:** 0.50% (Pre-Launch rewards)

#### Vesting Schedule - Team/Investors
| Period | Release Rate |
|--------|--------------|
| Month 1 | 10% |
| Months 2-6 | 8% per month |
| Months 7-11 | 6% per month |
| Month 12 | 4% |
| Months 13-16 | 3% per month |
| Months 17-18 | 2% per month |

#### Investigation Notes
- **High Treasury Control:** 41.6% in reserve treasury
- **Long Vesting:** 5-year vesting with cliff
- **Tax Revenue:** 3% on every transaction creates substantial treasury
- **Centralization Risk:** Team + Treasury = 79% of supply

---

## Auto-Ingest Usage

### Quick Start
```bash
# Process single file
python scripts/auto_ingest.py --input ./evidence/inbox/transactions.json

# Process entire directory
python scripts/auto_ingest.py --input ./evidence/inbox/
```

### Classification Output
Each file gets:
- **File Type:** Auto-detected (helius, pump_deployers, etc.)
- **Category:** Transaction data, threat intel, documentation
- **Priority:** Critical, High, Medium, Low
- **Case Assignment:** SOSANA_RICO_2026, PUMP_FUN_ANALYSIS_2026, etc.
- **Entity Extraction:** Addresses automatically extracted
- **Tags:** Contextual tags for filtering

### Database Storage
All files are:
1. **SHA256 hashed** for integrity
2. **AES-256 encrypted** for storage
3. **Classified** with metadata
4. **Indexed** for quick retrieval

---

## Recommended Next Steps

### For Pump.fun Deployers
```bash
# Ingest the deployer list
python scripts/auto_ingest.py --input ./evidence/raw/top_deployers_pump.csv

# Run pattern detection on high-risk deployers
python -m backend.services.analysis --entity [DEPLOYER_ADDRESS]
```

### For Helius Transactions
```bash
# Ingest all transaction files
python scripts/auto_ingest.py --input ./evidence/raw/transactions*.json

# Extract and register all addresses
python scripts/seed_from_files.py --input ./evidence/raw/transactions*.json
```

### For SOSANA Litepaper
```bash
# Already classified as documentation
# Use for reference when analyzing SOSANA token flows
```

---

## Evidence Vault Status

| Category | Files | Priority Breakdown |
|----------|-------|-------------------|
| Transaction Data | 3 | 3 HIGH |
| Threat Intelligence | 1 | 1 CRITICAL |
| Documentation | 1 | 1 MEDIUM |
| **TOTAL** | **5** | **1 CRITICAL, 3 HIGH, 1 MEDIUM** |

---

## Tags Applied

- `pump_fun` - Pump.fun related
- `deployer_analysis` - Token deployer data
- `serial_rugger_risk` - High-risk deployer pattern
- `helius` - Helius API export
- `on_chain` - On-chain transaction data
- `sosana_related` - SOSANA token related

---

*Auto-generated by Evidence Fortress v4.0*
