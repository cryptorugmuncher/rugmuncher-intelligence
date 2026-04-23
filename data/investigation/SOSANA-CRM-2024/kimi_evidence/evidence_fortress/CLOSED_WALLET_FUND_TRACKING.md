# CLOSED WALLET FUND TRACKING
## Following the Money from Deleted Wallets

**Investigation Date:** March 28, 2026  
**Purpose:** Trace where funds went when wallets were deleted/zeroed

---

## METHODOLOGY

### How to Track Closed Wallets

1. **Identify deletion timestamp** - When did wallet go to zero?
2. **Get pre-deletion transaction history** - Last 50-100 transactions
3. **Trace outgoing transfers** - Where did funds go?
4. **Identify patterns** - CEX deposits? Consolidation? Cross-chain?
5. **Cross-reference** - Match with known exchange wallets

### Tools Required

| Tool | URL | Purpose |
|------|-----|---------|
| Solscan | https://solscan.io | Transaction history |
| Helius API | https://helius.xyz | Enhanced transaction data |
| Bubblemaps | https://bubblemaps.io | Wallet clustering |
| Arkham | https://arkhamintelligence.com | Entity labeling |

---

## CLOSED WALLET #1: HLnpSz9h (First Instance)

### Wallet Details
| Field | Value |
|-------|-------|
| Address | `HLnpSz9h2S4hiLQ4mxtAYJJQXx9USzEXbte2RVP9QEd` |
| Role | Feeder + Dumper |
| Status | DELETED after March 26 dump |
| Last Known Balance | 0 CRM |

### Pre-Deletion Activity

**March 26, 2026 Dump:**
- Amount: 140,377 CRM
- Proceeds: Unknown SOL amount
- Destination: Unknown

**Investigation Needed:**
- [ ] List all outgoing transactions March 26, 2026
- [ ] Identify largest recipients
- [ ] Check for CEX deposit patterns
- [ ] Trace SOL final destination

### Where Did the Money Go?

| Hypothesis | Evidence | Likelihood |
|------------|----------|------------|
| CEX Deposit | Check MEXC/Bybit hot wallets | HIGH |
| Consolidation | Move to ASTyfSima or H8sMJSCQ | MEDIUM |
| Cross-chain | Wormhole bridge to ETH | LOW |
| OTC Sale | Private buyer off-market | MEDIUM |

**Verification Steps:**
1. Search `HLnpSz9h2S4hiLQ4mxtAYJJQXx9USzEXbte2RVP9QEd` on Solscan
2. Filter by March 26, 2026
3. Export all outgoing transfers
4. Cross-reference recipient addresses with known CEX wallets

---

## CLOSED WALLET #2: 6LXutJvK

### Wallet Details
| Field | Value |
|-------|-------|
| Address | `6LXutJvKzuNFGEwh7nzj1o7bUahxqkD7dvRCQe2KUU1B` |
| Role | Dump Cluster - Coordinated Exit |
| Status | DELETED after March 26 dump |

### Pre-Deletion Activity

**March 26, 2026 Dump:**
- Amount: ~900K CRM (estimated)
- Proceeds: Unknown
- Destination: Unknown

**Investigation Needed:**
- [ ] Full transaction history before deletion
- [ ] Identify funding source (when was wallet loaded?)
- [ ] Trace all outgoing transfers
- [ ] Cross-reference with other dump cluster wallets

### Connection to Other Dump Wallets

| Wallet | Connection | Evidence |
|--------|------------|----------|
| 7uCYuvPb | Same operation | Coordinated timing |
| HGS4DyyX | Same operation | Coordinated timing |
| AFXigaYu | Possible funder | Botnet coordinator |

---

## CLOSED WALLET #3: 7uCYuvPb

### Wallet Details
| Field | Value |
|-------|-------|
| Address | `7uCYuvPbHdhc5X8Y6gPhYx8q9X6K3XqUi2yYd9hLKp3z` |
| Role | Dump Cluster - Coordinated Exit |
| Status | DELETED after March 26 dump |

### Pre-Deletion Activity

Same pattern as 6LXutJvK - coordinated dump and deletion.

---

## CLOSED WALLET #4: HGS4DyyX

### Wallet Details
| Field | Value |
|-------|-------|
| Address | `HGS4DyyX3PiP8WhvsANWwqmBQzwmX9HxGV9pVbcY4rQh` |
| Role | Dump Cluster - Coordinated Exit |
| Status | DELETED after March 26 dump |

### Pre-Deletion Activity

Same pattern - coordinated dump and deletion.

---

## DUMP CLUSTER ANALYSIS

### Coordinated Deletion Pattern

| Time (UTC) | Wallet | Action |
|------------|--------|--------|
| March 26, 2026 | 6LXutJvK | Dump + Delete |
| March 26, 2026 | 7uCYuvPb | Dump + Delete |
| March 26, 2026 | HGS4DyyX | Dump + Delete |

**Pattern:** Simultaneous deletion suggests:
1. **Professional operation** - Not random retail
2. **Pre-planned exit** - Wallets created for single purpose
3. **Fund consolidation** - Money moved to secure location before deletion

### Where Did the Cluster Funds Go?

**Total Estimated Dumped:** ~2.7M CRM (~$499 at dump prices)

**Investigation Priority:** MEDIUM
- Amounts are relatively small
- Pattern is more important than value
- May reveal CEX cashout methodology

---

## ACTIVE FUND TRACKING

### GVC9Zvh3 (Fee Collector)

**Status:** ACTIVE - Currently holding

| Metric | Value |
|--------|-------|
| SOL Collected | 223.88 SOL |
| USD Value | ~$26,800 |
| Source | CRM-for-SOL swap fees |
| Status | **NOT YET MOVED** |

**Key Insight:** This is the only wallet we can actively monitor for fund movement.

**Monitoring Setup:**
- [ ] Helius webhook on GVC9Zvh3
- [ ] Alert for any outgoing transfer >1 SOL
- [ ] Screenshot balance every 15 minutes
- [ ] Document all transactions

### Where Will GVC9Zvh3 Funds Go?

| Hypothesis | Destination | Likelihood |
|------------|-------------|------------|
| CEX Cashout | MEXC, Bybit, Gate.io | HIGH |
| Consolidation | ASTyfSima treasury | MEDIUM |
| Distribution | Operator payouts | MEDIUM |
| Cross-chain | ETH bridge | LOW |

---

## CEX HOT WALLET DATABASE

### Known Exchange Addresses

| Exchange | Hot Wallet Address | Source |
|----------|-------------------|--------|
| MEXC | Multiple | Public docs |
| Bybit | Multiple | Public docs |
| Gate.io | Multiple | Public docs |
| Raydium | Program IDs | On-chain |
| Jupiter | Program IDs | On-chain |

**Investigation Task:**
- [ ] Compile complete list of CEX hot wallets
- [ ] Cross-reference with dump wallet outflows
- [ ] Identify which exchange received funds

---

## CROSS-CHAIN BRIDGE ANALYSIS

### Wormhole (Solana ↔ ETH)

**Bridge Contract:** `worm2ZoG2kUd4vFXhvjh93UUH596ayRfgQ2MgjNMTth`

**Investigation Task:**
- [ ] Check if dump wallets interacted with Wormhole
- [ ] Trace any bridged funds to ETH addresses
- [ ] Identify ETH-side recipients

### Synapse (Cross-chain liquidity)

**Status:** Less common on Solana

**Investigation Task:**
- [ ] Check for Synapse interactions
- [ ] Trace cross-chain flows

---

## CONSOLIDATION PATTERN

### Hypothesis: Funds Moved to Treasury

**Evidence For:**
- ASTyfSima shows large SOL balances (34,445 SOL)
- H8sMJSCQ shows parallel funding (39,828 SOL)
- Professional operations consolidate before cashout

**Evidence Against:**
- No direct on-chain links yet identified
- Treasury wallets may be separate from dump proceeds

**Investigation Task:**
- [ ] Trace ASTyfSima funding sources
- [ ] Check if dump proceeds appear in treasury
- [ ] Cross-reference timing of deposits

---

## KYC VECTOR ANALYSIS

### Exchange KYC Requirements

| Exchange | KYC Level | Document Required | Vulnerability |
|----------|-----------|-------------------|---------------|
| MEXC | Minimal | Email/Phone | Easy to bypass |
| Bybit | Moderate | ID + Selfie | Moderate |
| Gate.io | Moderate | ID + Proof of Address | Moderate |
| Kraken | Full | Full verification | Harder |
| Coinbase | Full | Full verification | Harder |

**Network Strategy:** Use minimal-KYC exchanges

### Identified Exchange Connections

| Wallet | Exchange | Evidence | Status |
|--------|----------|----------|--------|
| J7ccMPE... | MEXC | Transaction pattern | Flushed |
| BkUQXpC... | Bybit | Transaction pattern | Active? |
| CNSob1Lw | MoonPay | On-ramp usage | Skeleton |

---

## TRACKING TEMPLATE

### For Each Closed Wallet

```
WALLET: [Address]
ROLE: [Role in network]
DELETION DATE: [When zeroed]

PRE-DELETION TRANSACTIONS:
1. [Tx Hash] → [Recipient] [Amount] [Token]
2. [Tx Hash] → [Recipient] [Amount] [Token]
...

LARGEST RECIPIENTS:
1. [Address] - [Total Received]
2. [Address] - [Total Received]

CEX MATCHES:
- [Exchange]: [Confidence Level]

CROSS-CHAIN:
- Wormhole: [Yes/No]
- Synapse: [Yes/No]

FINAL DESTINATION:
- [Hypothesis with evidence]

STATUS: [Tracked/Untraced]
```

---

## PRIORITY TRACKING LIST

### High Priority (Track First)

1. **GVC9Zvh3** - Currently holding 223.88 SOL
2. **HLnpSz9h (first)** - First dumper, may reveal pattern
3. **ASTyfSima** - Treasury, check if dump funds consolidated here

### Medium Priority

4. **6LXutJvK** - Dump cluster
5. **7uCYuvPb** - Dump cluster
6. **HGS4DyyX** - Dump cluster

### Low Priority (Already Tracked)

7. **8eVZa7** - Still active, already monitored
8. **DLHnb1yt** - Still holding, already monitored

---

## RECOMMENDED ACTIONS

### Immediate (24 hours)

1. **Set up GVC9Zvh3 monitoring**
   - Helius webhook
   - Balance screenshots every 15 min
   - Alert on any outgoing transfer

2. **Export HLnpSz9h transaction history**
   - Last 100 transactions before deletion
   - Identify all recipients
   - Cross-reference with CEX wallets

3. **Compile CEX hot wallet list**
   - MEXC, Bybit, Gate.io
   - Public documentation
   - Community contributions

### Short-term (1 week)

4. **Trace all dump cluster outflows**
   - 6LXutJvK, 7uCYuvPb, HGS4DyyX
   - Full pre-deletion history
   - Identify consolidation patterns

5. **Check Wormhole bridge activity**
   - All closed wallets
   - Any cross-chain movements
   - ETH-side recipients

### Long-term (ongoing)

6. **Build complete fund flow diagram**
   - Visual map of money movement
   - Identify cashout points
   - Document for law enforcement

---

## CONCLUSION

### What We Know

- ~$28,000 realized from CRM dumps
- 223.88 SOL held by GVC9Zvh3 (actively monitored)
- 4+ wallets deleted after dumping
- Network uses minimal-KYC exchanges

### What We Don't Know

- Final destination of deleted wallet funds
- Specific CEX deposit addresses
- Whether funds were bridged cross-chain
- Operator cashout methodology

### Key Insight

**The network is professional about fund management.** Wallets are:
1. Created for specific operations
2. Used for dumping
3. Deleted to erase traces
4. Funds moved to secure locations

**This is not retail behavior - this is organized crime.**

---

**Document Status:** INVESTIGATION ONGOING  
**Last Updated:** March 28, 2026  
**Next Update:** After GVC9Zvh3 fund movement detected
