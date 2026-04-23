# Fund Tracing Quickstart Guide
## Tracking Deleted Wallet Fund Flows for Law Enforcement

**Objective:** Trace where dumped funds went after wallet deletion to identify CEX accounts, bridge destinations, and cash-out vectors  
**Evidence Quality Goal:** TIER 1 - On-chain verified with subpoena-ready documentation  
**Last Updated:** April 6, 2026

---

## Overview

This toolkit provides everything needed to trace fund flows from the four deleted dump wallets:

1. **HLnpSz9h** (first instance) - Deleted after ~50M CRM dump
2. **6LXutJvK** - Deleted dump wallet
3. **7uCYuvPb** - Deleted dump wallet  
4. **HGS4DyyX** - Deleted dump wallet

Plus monitoring of the active **GVC9Zvh3** fee collector (223.88 SOL).

---

## Prerequisites

### 1. Helius API Key

**Get your API key:**
1. Go to https://helius.xyz
2. Sign up for free tier (includes 100,000 API calls/month)
3. Create a new API key
4. Save the key - you'll need it for all scripts

**Why Helius:**
- Free tier sufficient for this analysis
- Enhanced transaction parsing
- Webhook support for real-time monitoring
- Better than Solscan for historical data

### 2. Python Environment

```bash
# Install required packages
pip install requests flask

# Or if using requirements.txt
pip install -r requirements.txt
```

### 3. Directory Structure

```
/mnt/okcomputer/output/
├── scripts/
│   ├── export_deleted_wallet_history.py    # Export transaction history
│   ├── analyze_fund_flows.py               # Analyze exported data
│   └── setup_fee_collector_monitoring.py   # Monitor GVC9Zvh3
├── exports/                                # Exported wallet data (created)
├── analysis/                               # Analysis reports (created)
├── alerts/                                 # Monitoring alerts (created)
├── CLOSED_WALLET_FUND_TRACKING.md          # Full documentation
├── CEX_HOT_WALLET_DATABASE.md              # CEX addresses
└── FUND_TRACING_QUICKSTART.md              # This file
```

---

## Step-by-Step Instructions

### Phase 1: Export Transaction History

**Goal:** Get complete pre-deletion transaction history from all four deleted wallets.

#### Step 1.1: List Known Deleted Wallets

```bash
cd /mnt/okcomputer/output/scripts

python export_deleted_wallet_history.py \
    --list
```

Output shows:
- HLnpSz9h_first: First major dump wallet, deleted after extraction
- 6LXutJvK: Deleted dump wallet
- 7uCYuvPb: Deleted dump wallet
- HGS4DyyX: Deleted dump wallet

#### Step 1.2: Export All Wallets

```bash
python export_deleted_wallet_history.py \
    --all \
    --api-key YOUR_HELIUS_API_KEY \
    --format csv
```

**This will:**
- Export all 4 deleted wallets
- Save as both JSON (full data) and CSV (transfers only)
- Files named: `{WALLET_KEY}_{TIMESTAMP}.json/csv`
- Combined report: `ALL_DELETED_WALLETS_{TIMESTAMP}.json`

**Expected Output:**
```
Exporting: HLnpSz9h_first
Address: HLnpSz9h
Status: CONFIRMED_DUMP_DELETED
Found X transactions
Found Y outgoing transfers
Saved to: HLnpSz9h_first_20250406_120000.json
...
Combined report saved to: ALL_DELETED_WALLETS_20250406_120000.json
```

#### Step 1.3: Export Individual Wallet (Optional)

```bash
python export_deleted_wallet_history.py \
    --wallet HLnpSz9h_first \
    --api-key YOUR_HELIUS_API_KEY \
    --format csv
```

**Files Created:**
- `HLnpSz9h_first_20250406_120000.json` - Full transaction data
- `HLnpSz9h_first_20250406_120000_transfers.csv` - Outgoing transfers only

---

### Phase 2: Analyze Fund Flows

**Goal:** Identify CEX deposits, bridge usage, and fee collector relationships.

#### Step 2.1: Analyze All Exported Wallets

```bash
python analyze_fund_flows.py \
    --all \
    --input-dir . \
    --format json
```

**This will:**
- Find all exported wallet JSON files
- Analyze each for fund flow patterns
- Generate combined report

**Output:** `FUND_FLOW_ANALYSIS_20250406_120000.json`

#### Step 2.2: Review Analysis Results

The analysis report contains:

```json
{
  "wallets_analyzed": 4,
  "cross_wallet_analysis": {
    "total_sol_transferred": 1234.56,
    "total_crm_transferred": 98765432.00,
    "total_cex_deposits": 5,
    "total_bridge_transactions": 2,
    "total_fee_collector_flows": 8
  },
  "individual_reports": [
    {
      "wallet": "HLnpSz9h_first",
      "fund_flow_analysis": {
        "cex_deposits": { "count": 2, "deposits": [...] },
        "bridge_transactions": { "count": 1, "transactions": [...] },
        "fee_collector_flows": { "count": 3, "flows": [...] },
        "evidence_assessment": {
          "overall_tier": "TIER_2",
          "recommendations": ["Subpoena MEXC", "Monitor fee collector"]
        }
      }
    }
  ]
}
```

#### Step 2.3: Identify CEX Hot Wallets

As you analyze, populate the CEX database:

**Edit:** `CEX_HOT_WALLET_DATABASE.md`

Add identified addresses:
```markdown
## MEXC Global
**Known Hot Wallets:**
```
Primary: 7X...xyz  # Add when identified
Evidence: Received 5 transfers from deleted wallets
Confidence: HIGH
```
```

**Then update the scripts:**
```python
# In analyze_fund_flows.py, update CEX_HOT_WALLETS
CEX_HOT_WALLETS = {
    "MEXC": {
        "wallets": ["7X...xyz"],  # Add identified addresses
        "patterns": ["multiple_small_deposits"]
    }
}
```

---

### Phase 3: Monitor Fee Collector

**Goal:** Set up real-time alerts for GVC9Zvh3 (223.88 SOL).

#### Step 3.1: Check Current Balance

```bash
python setup_fee_collector_monitoring.py \
    --api-key YOUR_HELIUS_API_KEY \
    --balance
```

**Output:**
```json
{
  "sol_balance": 223.88,
  "sol_value_usd": 28656.64,
  "crm_balance": 0,
  "timestamp": "2026-04-06T12:00:00"
}
```

#### Step 3.2: Analyze Recent Activity

```bash
python setup_fee_collector_monitoring.py \
    --api-key YOUR_HELIUS_API_KEY \
    --analyze \
    --hours 48
```

**This shows:**
- Recent incoming transfers (from deleted wallets?)
- Any outgoing transfers (CRITICAL)
- Bridge interactions
- CEX deposits

#### Step 3.3: Set Up Real-Time Monitoring

**Option A: Simple Webhook (Recommended)**

1. **Generate webhook handler:**
```bash
python setup_fee_collector_monitoring.py \
    --generate-handler
```

This creates `webhook_handler.py`.

2. **Start the handler:**
```bash
# In a new terminal
python webhook_handler.py
```

Server starts on `http://localhost:5000/webhook`

3. **Expose to internet (ngrok):**
```bash
# Install ngrok
# Run:
ngrok http 5000

# Copy the https URL (e.g., https://abc123.ngrok.io)
```

4. **Create Helius webhook:**
```bash
python setup_fee_collector_monitoring.py \
    --api-key YOUR_HELIUS_API_KEY \
    --create \
    --webhook-url https://abc123.ngrok.io/webhook
```

5. **Test the webhook:**
- Any transaction involving GVC9Zvh3 will trigger an alert
- Check terminal running webhook_handler.py
- Alerts saved to `ALERT_{TIMESTAMP}.json`

**Option B: Manual Monitoring (No webhook)**

Run analysis periodically:
```bash
# Every hour
while true; do
    python setup_fee_collector_monitoring.py \
        --api-key YOUR_KEY \
        --analyze \
        --hours 1
    sleep 3600
done
```

---

### Phase 4: Legal Documentation

**Goal:** Compile evidence for law enforcement subpoenas.

#### Step 4.1: Document CEX Deposits

For each identified CEX deposit:

```markdown
## CEX Deposit Evidence: [Exchange Name]

**Wallet:** [Deleted wallet address]
**CEX:** [Exchange name]
**Deposit Address:** [CEX hot wallet]
**Amount:** [X SOL / Y CRM]
**Transaction:** [Signature]
**Date:** [Timestamp]
**Evidence Tier:** TIER 1 / TIER 2

**Subpoena Priority:** HIGH / MEDIUM / LOW
**Recommended Action:** Request KYC for deposit address
```

#### Step 4.2: Document Bridge Usage

For each bridge transaction:

```markdown
## Bridge Transaction: [Bridge Name]

**Source Wallet:** [Deleted wallet]
**Bridge:** [Wormhole/Synapse/Allbridge]
**Amount:** [X SOL]
**Transaction:** [Signature]
**Destination Chain:** [Ethereum/BSC/Arbitrum]
**Destination Address:** [If visible]

**Subpoena Priority:** HIGH
**Recommended Action:** Subpoena bridge protocol for destination details
```

#### Step 4.3: Compile Evidence Package

Create final package:

```
EVIDENCE_PACKAGE/
├── 01_Executive_Summary.md
├── 02_Deleted_Wallet_Analysis/
│   ├── HLnpSz9h_analysis.json
│   ├── 6LXutJvK_analysis.json
│   └── ...
├── 03_CEX_Deposits/
│   ├── MEXC_deposits.md
│   ├── Bybit_deposits.md
│   └── ...
├── 04_Bridge_Transactions/
│   ├── Wormhole_transactions.md
│   └── ...
├── 05_Fee_Collector_Monitoring/
│   ├── GVC9Zvh3_balance_history.json
│   └── alert_logs/
└── 06_Subpoena_Templates/
    ├── CEX_subpoena_template.txt
    └── Bridge_subpoena_template.txt
```

---

## Expected Outcomes

### Tier 1 Evidence (High Confidence)

- ✅ Direct CEX deposits with verified hot wallet addresses
- ✅ Bridge transactions with destination chain identified
- ✅ Fee collector flows with exact amounts and timestamps
- ✅ Cross-wallet patterns showing coordinated operation

### Tier 2 Evidence (Strong Inference)

- ⚠️ Suspected CEX deposits (round numbers, patterns)
- ⚠️ Bridge interactions (contract interaction confirmed)
- ⚠️ Network connections between deleted wallets

### Tier 3 Evidence (Suspected)

- ❓ Unidentified recipient addresses requiring further analysis
- ❓ Temporal patterns suggesting coordination
- ❓ Amount patterns consistent with CEX deposits

---

## Common Issues & Solutions

### Issue: Helius API rate limit

**Solution:**
- Free tier: 100,000 calls/month
- If exceeded: Upgrade or wait for reset
- Use caching: Save exports and re-analyze locally

### Issue: Wallet has 0 transactions in Helius

**Cause:**
- Wallet may be too old (pre-Helius indexing)
- May need Solscan fallback

**Solution:**
```python
# Use Solscan API as backup
import requests

def get_solscan_transactions(address):
    url = f"https://api.solscan.io/account/transactions"
    params = {"address": address, "limit": 50}
    response = requests.get(url, params=params)
    return response.json()
```

### Issue: Can't identify CEX hot wallet

**Solution:**
1. Check Solscan labels: https://solscan.io/account/{ADDRESS}
2. Look for recurring addresses across multiple deleted wallets
3. Check community forums for known addresses
4. Contact exchange support (without revealing investigation)

### Issue: No outgoing transfers found

**Possible causes:**
- Wallet was emptied before deletion
- Funds moved through program interactions (not direct transfers)
- Need to analyze swaps, not just transfers

**Solution:**
- Check "SWAP" transactions in export
- Look for Raydium/Jupiter interactions
- Analyze token account closures

---

## Next Steps After Analysis

### Immediate (This Week)

1. **Export all 4 deleted wallets** - Run Phase 1
2. **Identify CEX hot wallets** - Populate database
3. **Set up GVC9Zvh3 monitoring** - Run Phase 3
4. **Document findings** - Create evidence package

### Short-Term (Next 2 Weeks)

5. **Subpoena identified CEXes** - MEXC, Bybit, Gate.io
6. **Subpoena bridge protocols** - Wormhole, Allbridge
7. **Cross-chain tracing** - If Ethereum/BSC destinations found
8. **Monitor for new activity** - Watch GVC9Zvh3

### Medium-Term (Next Month)

9. **Analyze subpoena responses** - Map KYC accounts
10. **Trace further fund flows** - From CEX withdrawals
11. **Compile final report** - For law enforcement
12. **Prepare testimony** - Document chain of custody

---

## Key Metrics to Track

### Financial Impact

- **Total SOL extracted:** Sum of all outgoing SOL transfers
- **Total CRM dumped:** Sum of all CRM transfers
- **USD value at time of dump:** Historical price lookup
- **Current USD value:** If still held

### Network Infrastructure

- **Fee collector accumulation:** 223.88 SOL (current)
- **Number of CEX accounts:** Identified from deposits
- **Bridge destinations:** Chains used for cross-chain movement
- **Coordination evidence:** Temporal patterns, shared recipients

### Evidence Quality

- **Tier 1 evidence count:** Direct on-chain proof
- **Tier 2 evidence count:** Strong inference
- **Subpoena-ready items:** CEX deposits, bridge transactions
- **Gaps requiring further analysis:** Unknown recipients

---

## Contact & Support

### Technical Issues

- Helius API docs: https://docs.helius.xyz
- Solscan API docs: https://docs.solscan.io
- Solana docs: https://docs.solana.com

### Legal Questions

- Consult with law enforcement liaison
- Review chain of custody requirements
- Verify subpoena procedures

---

## Document History

- **v1.0** (April 6, 2026) - Initial quickstart guide
- **v1.1** (Pending) - Updates based on analysis results

---

**Classification:** INVESTIGATION TOOLKIT  
**Chain of Custody:** Evidence Fortress v4.0  
**Next Review:** Upon completion of Phase 1 exports
