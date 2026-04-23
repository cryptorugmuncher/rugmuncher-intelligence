# POST-COLLAPSE FUND FLOWS
## Tracking Where the Money Went

**Investigation Date:** March 28, 2026  
**Purpose:** Trace fund movements after CRM dump

---

## METHODOLOGY

### How We Track Funds

1. **Start with dump wallets** - Wallets that sold CRM
2. **Trace SOL/USDC outflows** - Where did the proceeds go?
3. **Identify CEX deposits** - Exchanges where funds cashed out
4. **Track remaining balances** - What's still in the ecosystem?

### Tools Used
- Solscan (https://solscan.io)
- Helius API
- Bubblemaps (for clustering)

---

## DUMP WALLET ANALYSIS

### 1. HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc

**Status:** PRIMARY DUMPER + FEEDER

**March 26, 2026 Dump:**
- Amount: 140,377 CRM
- Proceeds: Unknown (need transaction signature)

**March 28, 2026 Activity:**
- Selling 79.7M CRM in batches
- Fee collector: GVC9Zvh3mxfUHfMRi9zGzjRdQtfoQ2WkFXHSfy3ySwoT
- SOL collected: 223.88 SOL (~$26,800)

**Where Did the SOL Go?**

| Destination | Amount | Status | Evidence |
|-------------|--------|--------|----------|
| GVC9Zvh3 (fee collector) | 223.88 SOL | HELD | [ON-CHAIN] |
| Unknown CEX deposits | Unknown | NEEDS TRACING | [INVESTIGATION NEEDED] |

**Verification:**
- https://solscan.io/account/HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc

---

### 2. 8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj

**Status:** CONFIRMED DUMPER

**March 2026 Sells:**
- Amount: 762,848 CRM
- Proceeds: 4.19 SOL (~$362)

**Where Did the SOL Go?**

| Destination | Amount | Status | Evidence |
|-------------|--------|--------|----------|
| Unknown | 4.19 SOL | NEEDS TRACING | [INVESTIGATION NEEDED] |

**Current Holdings:**
- CRM: ~19.7M (~$3,755)
- PBTC: 73,574
- Status: Still holding 96% of position

**Verification:**
- https://solscan.io/account/8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj

---

### 3. Dump Cluster (6LXutJvK, 7uCYuvPb, HGS4DyyX)

**Status:** COORDINATED DUMPERS

**March 26, 2026:**
- Combined dump: ~2.7M CRM
- Proceeds: ~$499

**Post-Dump Status:**
- Wallets DELETED (zeroed out)
- Funds moved to unknown destinations

**Where Did the Money Go?**

| Source | Amount | Destination | Status |
|--------|--------|-------------|--------|
| 6LXutJvK | ~900K CRM | Unknown | DELETED |
| 7uCYuvPb | ~900K CRM | Unknown | DELETED |
| HGS4DyyX | ~900K CRM | Unknown | DELETED |

**Investigation Needed:**
- Trace pre-deletion outflows
- Identify where funds consolidated
- Check for CEX deposit patterns

---

## FEE COLLECTOR ANALYSIS

### GVC9Zvh3mxfUHfMRi9zGzjRdQtfoQ2WkFXHSfy3ySwoT

**Role:** CRM-for-SOL swap fee collector

**SOL Collected:** 223.88 SOL (~$26,800 and growing)

**Where Is This Money Going?**

| Hypothesis | Likelihood | Evidence Needed |
|------------|------------|-----------------|
| Held for future operations | HIGH | No outflows yet observed |
| Distributed to operators | MEDIUM | Check for distribution patterns |
| CEX cashout | LOW | No large outflows yet |

**Verification:**
- https://solscan.io/account/GVC9Zvh3mxfUHfMRi9zGzjRdQtfoQ2WkFXHSfy3ySwoT

---

## DORMANT WALLETS (Still Holding)

### DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh

**Status:** DORMANT VOLCANO

**Holdings:**
- CRM: ~104.6M (~$19,943)
- GAS: 237M

**Activity:**
- ZERO sells to date
- No outflows observed
- Largest threat waiting to activate

**Where Will Money Go If They Dump?**

| Scenario | Destination | Impact |
|----------|-------------|--------|
| Raydium swap | SOL/USDC | Price collapse |
| CEX deposit | Gate.io, MEXC | Immediate cashout |
| OTC sale | Private buyer | Minimal market impact |

---

## FUNDS STILL IN CRM ECOSYSTEM

### Network Holdings Summary

| Wallet | CRM Holdings | USD Value | Status |
|--------|--------------|-----------|--------|
| DLHnb1yt | 104.6M | $19,943 | DORMANT |
| 8eVZa7 | 19.7M | $3,755 | ACTIVE |
| HLnpSz9h | 79.7M | $15,199 | DUMPING |
| **TOTAL** | **204M** | **$38,897** | |

**Percentage of Supply:** ~20.4%

**Key Question:** Will they dump or hold?

---

## WHERE THE MONEY WENT (CONFIRMED)

### Extracted Funds

| Source | Amount | Destination | Status |
|--------|--------|-------------|--------|
| 8eVZa7 March dump | 4.19 SOL | Unknown | NEEDS TRACING |
| Dump cluster | ~$499 | Unknown | DELETED |
| HLnpSz9h fees | 223.88 SOL | GVC9Zvh3 | HELD |

### Total Realized
- **Confirmed extracted:** ~$861 + 228.07 SOL (~$27,368)
- **Total realized:** ~$28,229

### Total Still at Risk
- **Unrealized holdings:** ~$38,897 in CRM
- **Potential extraction:** $38,897 if fully dumped

---

## INVESTIGATION GAPS

### What We Don't Know (Yet)

1. **CEX Deposit Addresses**
   - Which exchanges received the dumped funds?
   - Need to trace outflows from dump wallets

2. **Final Cashout Points**
   - Where did the SOL ultimately go?
   - Fiat off-ramps?

3. **Operator Payouts**
   - How are operators compensated?
   - PBTC/EPIK rewards (June 2025 pattern)?

4. **Cross-Chain Movements**
   - Any bridges to ETH, BSC, etc.?
   - Need to check Wormhole/Synapse activity

---

## TRACING METHODOLOGY

### Step-by-Step Fund Tracing

```
1. Identify dump transaction
   ↓
2. Note SOL/USDC received
   ↓
3. Trace subsequent outflows
   ↓
4. Identify CEX deposit addresses
   ↓
5. Cross-reference with known exchange wallets
   ↓
6. Document final destination
```

### Tools for Tracing

| Tool | URL | Purpose |
|------|-----|---------|
| Solscan | https://solscan.io | Transaction history |
| Bubblemaps | https://bubblemaps.io | Wallet clustering |
| Arkham | https://arkhamintelligence.com | Entity labeling |
| Chainalysis | (Enterprise) | Advanced tracing |

---

## VERIFICATION TASKS

### For Each Dump Wallet

- [ ] List all outgoing transactions post-dump
- [ ] Identify largest recipients
- [ ] Check for CEX deposit patterns
- [ ] Track SOL/USDC final destinations
- [ ] Document any cross-chain bridges

### Priority Order

1. **HLnpSz9h** - Currently dumping, active threat
2. **8eVZa7** - Confirmed dumper, needs full trace
3. **Dump cluster** - Deleted, need pre-deletion analysis
4. **GVC9Zvh3** - Fee collector, monitor for distribution

---

## HYPOTHESIS: WHERE THE MONEY REALLY WENT

### Theory 1: Held for Future Operations
**Evidence:** GVC9Zvh3 holding 223+ SOL, no large outflows  
**Likelihood:** HIGH  
**Implication:** Preparing for next campaign

### Theory 2: Distributed to Operators
**Evidence:** PBTC/EPIK rewards pattern from June 2025  
**Likelihood:** MEDIUM  
**Implication:** Payroll for criminal network

### Theory 3: CEX Cashout
**Evidence:** Small amounts suggest testing, not full extraction  
**Likelihood:** LOW  
**Implication:** Most value still in ecosystem

### Theory 4: Multi-Token Strategy
**Evidence:** Holdings in CRM, PBTC, GAS  
**Likelihood:** HIGH  
**Implication:** Diversified extraction across tokens

---

## RECOMMENDED ACTIONS

### Immediate (24 hours)
1. Set up Helius webhooks on GVC9Zvh3
2. Monitor for any large outflows
3. Screenshot current balances

### Short-term (1 week)
1. Trace full outflow history from dump wallets
2. Identify CEX deposit patterns
3. Cross-reference with known exchange wallets

### Long-term (ongoing)
1. Build complete fund flow diagram
2. Identify fiat off-ramps
3. Document for law enforcement

---

## CONCLUSION

### What We Know
- ~$28,229 realized from CRM dumps
- ~$38,897 still held in CRM
- 223.88 SOL held by GVC9Zvh3
- Most dump wallets deleted

### What We Don't Know
- Final cashout destinations
- CEX deposit addresses
- Operator compensation structure
- Next target token

### Key Insight
The network extracted minimal dollars from CRM (~$28K) compared to their holdings (~$67K total). This suggests:
1. CRM was a test run, not primary target
2. They're holding for future campaigns
3. Value extraction happens across multiple tokens (PBTC, GAS, CRM)

**The real money may be in SOSANA/PBTC, not CRM.**

---

**Document Status:** INVESTIGATION ONGOING  
**Last Updated:** March 28, 2026  
**Next Review:** After new transaction activity
