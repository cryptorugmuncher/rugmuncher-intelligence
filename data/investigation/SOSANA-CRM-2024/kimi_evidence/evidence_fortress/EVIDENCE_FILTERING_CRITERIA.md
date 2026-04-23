# EVIDENCE FILTERING CRITERIA
## Distinguishing Legitimate DeFi from Suspicious Activity

**Purpose:** Establish rigorous standards for what counts as evidence vs. normal DeFi behavior

---

## WHAT TO EXCLUDE (Normal DeFi Activity)

### 1. Raydium Pool Interactions

**EXCLUDE unless:**
- Funds enter pool and never exit (suspicious)
- Pattern of rapid in/out (wash trading)
- Used as intermediate step in multi-hop laundering

**Normal (exclude from evidence):**
- User swaps CRM for SOL via Raydium
- User adds liquidity to CRM-SOL pool
- User removes liquidity

**Suspicious (include):**
- Wallet dumps large CRM into pool, receives SOL, SOL immediately moves to CEX
- Pattern of multiple wallets using same pool in coordinated timeframe

### 2. Meteora Pool Interactions

**EXCLUDE unless:**
- Same criteria as Raydium
- Evidence of DLMM manipulation

### 3. Jupiter Aggregator Swaps

**EXCLUDE unless:**
- Part of multi-hop laundering chain
- Coordinated timing with other suspicious wallets

### 4. Normal Wallet Funding

**EXCLUDE:**
- Wallet receives SOL from exchange (normal on-ramp)
- Wallet receives tokens from airdrop
- Wallet receives tokens from legitimate transfer

---

## WHAT TO INCLUDE (Suspicious Activity)

### 1. Direct Wallet-to-Wallet Transfers

**INCLUDE when:**
- Large amounts transferred between known network wallets
- Timing correlates with dump events
- Pattern suggests coordination

**Example (INCLUDE):**
```
HLnpSz9h → 8eVZa7: 20M CRM (30 transfers, Dec 28-31)
8eVZa7 → 7abBmGf4H: 1M CRM (Dec 31)
```

### 2. CEX Deposit Patterns

**INCLUDE when:**
- Funds move from suspicious wallet to known CEX hot wallet
- Timing correlates with dump events
- Amounts are significant

**Example (INCLUDE):**
```
Dump wallet → MEXC hot wallet: SOL proceeds
```

### 3. Coordinated Timing

**INCLUDE when:**
- Multiple wallets act within minutes of each other
- Pattern suggests automation
- Actions are identical (same amounts, same timing)

**Example (INCLUDE):**
```
March 26, 2026 21:42: 970 wallets seeded in 7 seconds
```

### 4. Wallet Deletion After Dump

**INCLUDE:**
- Wallet dumps tokens
- Wallet is zeroed out
- Pattern suggests single-use wallets

**Example (INCLUDE):**
```
6LXutJvK, 7uCYuvPb, HGS4DyyX: All dumped and deleted March 26
```

### 5. Dust-Fee Transfer Patterns

**INCLUDE when:**
- Multiple small transfers (0.002 SOL fee each)
- Used to load wallets without market impact
- Pattern suggests systematic loading

**Example (INCLUDE):**
```
HLnpSz9h → 8eVZa7: 30+ transfers, Dec 28-31, 0.002 SOL each
```

---

## EVIDENCE CONFIDENCE LEVELS

### Tier 1: Ironclad (99% confidence)

**Criteria:**
- Direct on-chain evidence
- Multiple independent sources confirm
- Transaction signatures provided
- No alternative explanation

**Examples:**
- 970-wallet seeding (138/sec) - automation proven
- 1M CRM to victim whale (tx signature provided)
- Dust-fee loading pattern (30+ transfers documented)

### Tier 2: Strong (90% confidence)

**Criteria:**
- Strong on-chain evidence
- Logical inference from patterns
- Some alternative explanations possible but unlikely

**Examples:**
- Coordinated dump timing (4 wallets, same minute)
- CEX deposit patterns (matches known hot wallets)
- Wallet deletion after single use

### Tier 3: Moderate (75% confidence)

**Criteria:**
- Some on-chain evidence
- Pattern matches but not definitive
- Alternative explanations exist

**Examples:**
- Wallet clustering (same funding source)
- Timing correlation (not exact)
- Suspicious but not proven coordination

### Tier 4: Weak (50% confidence)

**Criteria:**
- Limited evidence
- Mostly circumstantial
- Alternative explanations likely

**Examples:**
- Wallet holds same token as network (many do)
- Wallet created around same time (coincidence possible)
- Single transaction that looks suspicious

### Tier 5: Unverified (25% confidence)

**Criteria:**
- No direct evidence
- Based on assumptions
- Needs investigation

**Examples:**
- "Peter Ohanyan" identity (name mentioned, no wallet)
- Prebonding contract analysis (not yet done)
- CEX account ownership (not confirmed)

---

## NETWORK MAPPING RULES

### Rule 1: Direct Connection Required

**Only map wallets with DIRECT on-chain connection:**
- Wallet A sent funds to Wallet B
- Wallet A and B received funds from same source
- Wallet A and B have coordinated timing

**DON'T map based on:**
- Both hold same token (thousands do)
- Both created same week (coincidence)
- Both use Raydium (everyone does)

### Rule 2: Multiple Connections Strengthen

**Single connection:** Weak evidence (Tier 3-4)
**Two connections:** Moderate evidence (Tier 2-3)
**Three+ connections:** Strong evidence (Tier 1-2)

### Rule 3: Timing Matters

**Coordinated timing (same minute):** Strong evidence
**Same day timing:** Moderate evidence
**Same week timing:** Weak evidence

### Rule 4: Amount Patterns Matter

**Identical amounts:** Strong evidence of coordination
**Similar amounts:** Moderate evidence
**Random amounts:** Weak evidence

---

## REVISED WALLET CLASSIFICATION

### CONFIRMED NETWORK (Tier 1-2 Evidence)

| Wallet | Evidence | Tier |
|--------|----------|------|
| HLnpSz9h → 8eVZa7 | 30+ dust transfers | Tier 1 |
| 8eVZa7 → 7abBmGf4H | 1M CRM tx signature | Tier 1 |
| AFXigaYu → 970 wallets | 138/sec seeding | Tier 1 |
| 6LXutJvK/7uCYuvPb/HGS4DyyX | Coordinated dump+delete | Tier 2 |

### SUSPECTED NETWORK (Tier 3-4 Evidence)

| Wallet | Evidence | Tier |
|--------|----------|------|
| DLHnb1yt cluster | Large holdings, 0 tx history | Tier 3 |
| ASTyfSima treasury | Large SOL, no direct CRM link | Tier 4 |

### NEEDS INVESTIGATION (Tier 5)

| Wallet | Evidence | Tier |
|--------|----------|------|
| "Peter Ohanyan" wallets | Name mentioned, no addresses | Tier 5 |
| Prebonding contract recipients | Contract not analyzed | Tier 5 |

---

## WHAT TO REMOVE FROM PREVIOUS ANALYSIS

### Overbroad Claims to Correct

| Previous Claim | Correction |
|----------------|------------|
| "60M+ criminal property" | Only count confirmed network wallets |
| "55.2% supply controlled" | Corrected to 20.4% (confirmed holdings) |
| "30+ wallet network" | Only include confirmed connections |
| "All Raydium users" | Exclude normal DEX interactions |

### Wallets to Reclassify

| Wallet | Previous | Revised | Reason |
|--------|----------|---------|--------|
| ASTyfSima | Tier 1 Treasury | Tier 4 Suspected | No direct CRM connection proven |
| H8sMJSCQ | Tier 1 Treasury | Tier 4 Suspected | No direct CRM connection proven |
| CNSob1Lw | Tier 0 Root | Tier 5 Unverified | No direct evidence of role |

---

## EVIDENCE QUALITY CHECKLIST

Before including any wallet in the network map:

- [ ] Direct on-chain connection to known network wallet?
- [ ] Coordinated timing with known network activity?
- [ ] Suspicious pattern (not normal DeFi behavior)?
- [ ] Alternative explanations considered and ruled out?
- [ ] Evidence tier assigned (1-5)?
- [ ] Can provide transaction signature or on-chain proof?

---

## SUMMARY

**Conservative Network Size:**
- Confirmed (Tier 1-2): ~10-15 wallets
- Suspected (Tier 3-4): ~5-10 wallets
- Unverified (Tier 5): Unknown

**Conservative Holdings:**
- Confirmed CRM: ~204M (20.4% of supply)
- Confirmed extracted: ~$28,000

**This is a smaller, more defensible claim with higher evidence quality.**

---

**Document Status:** EVIDENCE STANDARDS  
**Last Updated:** March 28, 2026
