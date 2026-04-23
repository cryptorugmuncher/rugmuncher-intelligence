# DEX Manipulation Detection Quickstart
## Identifying Sophisticated Dumping Patterns

**Objective:** Detect iceberg orders, liquidity harvesting, drip feeding, and wash trading  
**Evidence Quality Goal:** TIER 1-2 - Pattern-based forensic proof  
**Last Updated:** April 6, 2026

---

## Overview

This toolkit analyzes DEX transactions to identify **sophisticated market manipulation** used by the criminal network. Unlike simple dumps, these patterns require:

- Cross-wallet coordination analysis
- Temporal pattern recognition
- Counterparty mapping
- Volume correlation analysis

**Key Principle:** Not all DEX users are innocent. We're looking for **coordination, timing synchronization, and volume patterns** that indicate organized dumping.

---

## Manipulation Patterns We Detect

### 1. Iceberg Orders
Large sell orders split into many small pieces to hide total size.

**Detection:** 10+ sells in 1 hour with similar sizes (±30% variance)

### 2. Liquidity Harvesting
Selling slowly into buying demand to avoid crashing the market.

**Detection:** Sells concentrated during high-volume periods

### 3. Drip Feeding / Scaling Out
Consistent small sells over days/weeks.

**Detection:** 7+ consecutive days of similar-sized sells

### 4. Wash Trading
Self-trading between controlled wallets to create fake volume.

**Detection:** Repeated counterparties (3+ trades with same wallet)

### 5. Cross-Wallet Coordination
Multiple wallets dumping simultaneously or sequentially.

**Detection:** 3+ wallets selling in same 1-hour window

---

## Prerequisites

### 1. Helius API Key
```bash
# Get free API key at https://helius.xyz
# 100,000 calls/month on free tier
```

### 2. Python Environment
```bash
pip install requests numpy
```

### 3. CRM Token Mint Address
```python
# Update in scripts with actual CRM mint:
CRM_MINT = "YOUR_CRM_MINT_ADDRESS_HERE"
```

---

## Step-by-Step Workflow

### Phase 1: Export DEX Transaction History

#### Step 1.1: Export All Network Wallets

```bash
cd /mnt/okcomputer/output/scripts

python export_dex_transactions.py \
    --all-network-wallets \
    --api-key YOUR_HELIUS_API_KEY
```

**This exports:**
- All swaps (Raydium, Meteora, Jupiter, Orca)
- Liquidity operations
- Counterparty information
- Direction (buy/sell CRM)

**Output files:**
- `DEX_{WALLET}_{TIMESTAMP}.json` - Full data
- `DEX_{WALLET}_{TIMESTAMP}_swaps.csv` - Swaps only
- `DEX_ALL_WALLETS_{TIMESTAMP}.json` - Combined

#### Step 1.2: Export Individual Wallet (Optional)

```bash
python export_dex_transactions.py \
    --wallet DLHnb1yt \
    --api-key YOUR_HELIUS_API_KEY
```

---

### Phase 2: Detect Manipulation Patterns

#### Step 2.1: Analyze All Exported Wallets

```bash
python detect_manipulation_patterns.py \
    --all \
    --input-dir .
```

**This detects:**
- Iceberg orders (10+ sells in 1 hour)
- Drip feeding (7+ days of consistent sells)
- Liquidity harvesting (timing patterns)
- Wash trading (repeated counterparties)
- Cross-wallet coordination

**Output:** `MANIPULATION_ANALYSIS_{TIMESTAMP}.json`

#### Step 2.2: Review Analysis Results

The report contains:

```json
{
  "wallets_analyzed": 8,
  "summary": {
    "total_patterns_detected": 15,
    "wallets_with_iceberg": 3,
    "wallets_with_drip_feeding": 4,
    "wallets_with_wash_trading": 2,
    "coordination_detected": true
  },
  "individual_reports": [
    {
      "wallet": "DLHnb1yt",
      "patterns_detected": [
        {
          "pattern_type": "ICEBERG_ORDERS",
          "periods": [
            {
              "hour": "2026-03-15 14",
              "sell_count": 25,
              "total_volume": 1250000,
              "evidence_tier": "TIER_1"
            }
          ]
        }
      ],
      "financial_metrics": {
        "total_crm_sold": 50000000,
        "total_sells": 150,
        "estimated_usd_value": 15000
      },
      "legal_significance": {
        "charges_supported": ["Market Manipulation"],
        "evidence_strength": "STRONG"
      }
    }
  ]
}
```

---

### Phase 3: Cross-Project Analysis

#### Step 3.1: Check for Multi-Project Activity

```bash
python cross_project_analysis.py \
    --all-network-wallets \
    --api-key YOUR_HELIUS_API_KEY
```

**This identifies:**
- Tokens held across multiple wallets
- Projects the network is active in
- Shared token holdings (coordination indicator)
- Suspicious token patterns

**Output:** `CROSS_PROJECT_ANALYSIS_{TIMESTAMP}.json`

#### Step 3.2: Review Cross-Project Findings

```json
{
  "summary": {
    "shared_tokens_across_wallets": 12,
    "coordination_detected": true
  },
  "cross_wallet_analysis": {
    "shared_tokens": {
      "TOKEN_MINT_1": ["DLHnb1yt", "6LXutJvK", "7uCYuvPb"],
      "TOKEN_MINT_2": ["HLnpSz9h", "HGS4DyyX"]
    }
  }
}
```

---

### Phase 4: Manual Verification

#### Step 4.1: Verify Iceberg Orders on Solscan

1. Open detected transaction on Solscan
2. Check if multiple sells occurred in same hour
3. Verify similar order sizes
4. Document pattern

**Example:**
```
Wallet: DLHnb1yt
Hour: 2026-03-15 14:00-15:00 UTC
Transactions:
- Tx1: 50,000 CRM at 14:02
- Tx2: 52,000 CRM at 14:05
- Tx3: 48,000 CRM at 14:08
... (25 total transactions)
Pattern: Similar sizes, regular intervals
```

#### Step 4.2: Verify Wash Trading

1. Identify repeated counterparty addresses
2. Check if counterparty is also a network wallet
3. Look for circular patterns (A→B→A)
4. Document coordination

#### Step 4.3: Cross-Reference with Price Action

1. Pull CRM price data for dumping periods
2. Correlate large dumps with price drops
3. Calculate price impact
4. Document market manipulation

---

## Evidence Compilation

### For Each Detected Pattern, Document:

```markdown
## Pattern: Iceberg Orders

**Wallet:** DLHnb1yt
**Time Period:** 2026-03-15 14:00-15:00 UTC
**DEX:** Raydium

**Pattern Details:**
- Number of transactions: 25
- Total volume: 1,250,000 CRM
- Average order size: 50,000 CRM
- Size variance: 8% (indicates automation)
- Average interval: 2.4 minutes

**Evidence (Transaction Signatures):**
1. 5x...abc - 50,000 CRM at 14:02:15
2. 3y...def - 52,000 CRM at 14:05:22
3. 7z...ghi - 48,000 CRM at 14:08:45
... (list all 25)

**Price Impact:**
- Pre-dump: $0.00031
- Post-dump: $0.00028
- Decline: 9.7%

**Legal Significance:**
- Demonstrates intent to hide selling pressure
- Supports market manipulation charges
- Evidence tier: TIER 1
```

---

## Expected Outcomes

### Tier 1 Evidence (High Confidence)

- ✅ 20+ iceberg orders in 1 hour with <10% size variance
- ✅ 14+ consecutive days of drip feeding
- ✅ 5+ wash trades with same counterparty
- ✅ 5+ wallets coordinating in same 30-minute window

### Tier 2 Evidence (Strong Inference)

- ⚠️ 10-19 iceberg orders with <30% variance
- ⚠️ 7-13 days of drip feeding
- ⚠️ 3-4 wash trades with same counterparty
- ⚠️ 3-4 wallets coordinating in same 1-hour window

### Tier 3 Evidence (Suspected)

- ❓ 5-9 orders with suspicious timing
- ❓ 3-6 days of consistent selling
- ❓ 1-2 repeated counterparties
- ❓ 2 wallets with correlated timing

---

## Common Issues & Solutions

### Issue: No DEX transactions found

**Cause:**
- Wallet may have used different DEX
- Transactions may be older than Helius indexing
- CRM mint address incorrect

**Solution:**
```python
# Verify CRM mint address
# Check Solscan for actual swaps
# Use Solscan API as backup
```

### Issue: Can't identify wash trading

**Cause:**
- Counterparties use different wallets
- Multi-hop washing (A→B→C→A)
- Cross-DEX washing

**Solution:**
- Analyze counterparty wallets separately
- Look for circular patterns
- Check multiple DEXes

### Issue: Timing data incomplete

**Cause:**
- Helius timestamp precision
- Network latency variations

**Solution:**
- Use block time instead of receipt time
- Allow ±5 minute variance in analysis
- Focus on patterns, not exact timing

---

## Integration with Fund Tracing

### Combine DEX Analysis with Fund Flow Tracing

1. **DEX dumps → Fee collector**
   - Track SOL from DEX swaps to GVC9Zvh3
   - Document the full extraction chain

2. **Cross-wallet coordination → CEX deposits**
   - If multiple wallets dump then deposit to same CEX
   - Stronger coordination evidence

3. **Wash trading → Network mapping**
   - Map all controlled wallets
   - Build complete network graph

---

## Legal Documentation

### For Law Enforcement Submission

**Include:**
1. Raw transaction data (JSON exports)
2. Pattern detection analysis
3. Visual charts showing:
   - Sell timing patterns
   - Order size distributions
   - Cross-wallet coordination
4. Expert witness explanation
5. Correlation with price action

**Charges Supported:**
- Market Manipulation (SEC/CFTC)
- Wire Fraud (DOJ)
- Money Laundering (if proceeds traced)
- Conspiracy (if coordination proven)

---

## Next Steps After Analysis

### Immediate (This Week)

1. **Export all network wallet DEX history**
2. **Run manipulation detection**
3. **Verify top patterns on Solscan**
4. **Document findings**

### Short-Term (Next 2 Weeks)

5. **Cross-project analysis**
   - Check if network active in other projects
   - Build multi-project case

6. **Price correlation**
   - Pull historical CRM prices
   - Correlate with dumping periods

7. **Expert witness prep**
   - Document methodology
   - Prepare visualizations

### Medium-Term (Next Month)

8. **Legal submission**
   - Compile evidence package
   - Draft expert testimony
   - Coordinate with prosecutors

---

## Key Metrics to Track

### Manipulation Metrics

| Metric | Target | Evidence Tier |
|--------|--------|---------------|
| Iceberg orders/hour | 20+ | TIER 1 |
| Drip feeding days | 14+ | TIER 1 |
| Wash trade counterparties | 5+ | TIER 1 |
| Coordinated wallets | 5+ | TIER 1 |

### Financial Impact

| Metric | Calculation |
|--------|-------------|
| Total CRM dumped via DEX | Sum of all sells |
| Estimated USD extracted | SOL received × price |
| Price suppression impact | % decline during dumps |
| Market manipulation profit | vs. legitimate selling |

---

## Document History

- **v1.0** (April 6, 2026) - Initial DEX manipulation detection framework

---

**Classification:** INVESTIGATION TOOLKIT  
**Chain of Custody:** Evidence Fortress v4.0  
**Next Review:** Upon completion of DEX export and analysis
