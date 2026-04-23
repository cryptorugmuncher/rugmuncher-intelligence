# DEX Manipulation Detection Framework
## Identifying Sophisticated Dumping Patterns in Decentralized Exchanges

**Classification:** TIER 1-2 EVIDENCE - Pattern-Based Forensic Analysis  
**Investigation Status:** Active Pattern Detection  
**Last Updated:** April 6, 2026  
**Purpose:** Detect iceberg orders, liquidity harvesting, drip feeding, and wash trading across DEXes

---

## Executive Summary

This framework analyzes DEX transactions to identify **sophisticated market manipulation** used by the criminal network to extract value without detection. Unlike simple dumps, these patterns require cross-wallet coordination analysis and temporal pattern recognition.

**Key Insight:** The network used DEXes strategically - not all DEX users are innocent. We're looking for **coordination, timing synchronization, and volume patterns** that indicate organized dumping.

---

## Manipulation Patterns to Detect

### 1. Iceberg Orders

**Definition:** Large sell orders divided into smaller limit orders to hide total size from the market.

**Detection Criteria:**
- [ ] Same wallet executes 10+ sell orders within 1-hour window
- [ ] Order sizes follow pattern: similar amounts (e.g., 0.5-2% of position each)
- [ ] Timing: Regular intervals (every 2-5 minutes) or randomized within window
- [ ] Price impact: Each individual order has minimal impact, but cumulative is significant
- [ ] Counterparty diversity: Different buyers for each slice (not wash trading)

**Evidence Quality:**
- TIER 1: 20+ orders in 1 hour with identical size pattern
- TIER 2: 10+ orders in 1 hour with similar timing
- TIER 3: 5+ orders with suspicious intervals

**Example Pattern:**
```
Wallet: DUMP_001
Time: 14:00-15:00 UTC
Orders: 25 sells of 50,000 CRM each
Interval: Every 2.4 minutes (±30 seconds randomization)
Total: 1.25M CRM dumped in 1 hour
Individual impact: 0.1-0.3% each
Cumulative impact: 6-8% price decline
```

---

### 2. Liquidity Harvesting

**Definition:** Selling slowly into buying demand to convert crypto to cash without crashing the market.

**Detection Criteria:**
- [ ] Sells occur during high-volume periods (when buyers are active)
- [ ] Sell size correlates with buy volume (larger sells when more buyers)
- [ ] Price remains relatively stable despite significant selling
- [ ] Pattern repeats across multiple high-volume periods
- [ ] Wallet stops selling when buy volume dries up

**Evidence Quality:**
- TIER 1: Sell volume correlates with buy volume (r > 0.7) over 10+ periods
- TIER 2: Consistent selling during high-volume windows
- TIER 3: Sells only during buyer-active periods

**Example Pattern:**
```
Wallet: DUMP_002
Observation: Only sells during 2-4 PM UTC (high volume period)
Pattern: Sells 100K-200K CRM when buy volume > 500K CRM/hour
Stops: When buy volume drops below 200K CRM/hour
Duration: Sustained over 2 weeks
Total: 3M CRM harvested without major price crash
```

---

### 3. Drip Feeding / Scaling Out

**Definition:** Executing a series of small sell orders over an extended period (days/weeks).

**Detection Criteria:**
- [ ] Consistent daily selling (5+ days)
- [ ] Similar order sizes each day (±20% variance)
- [ ] Total position reduced by 50%+ over time
- [ ] No large individual dumps (>5% of daily volume)
- [ ] Pattern suggests automated or disciplined manual execution

**Evidence Quality:**
- TIER 1: 14+ consecutive days of similar-sized sells
- TIER 2: 7+ days with consistent pattern
- TIER 3: 3+ days with suspicious regularity

**Example Pattern:**
```
Wallet: DUMP_003
Pattern: Sells 25,000 CRM every 6 hours
Duration: 21 consecutive days
Total: 2.1M CRM (70% of initial position)
Variance: Order sizes 23K-27K CRM (±8%)
Automation indicator: Exact 6-hour intervals (±2 minutes)
```

---

### 4. Wash Trading

**Definition:** Self-trading between controlled wallets to create fake volume and manipulate price.

**Detection Criteria:**
- [ ] Wallet A sells to Wallet B, then Wallet B sells back
- [ ] Circular trading patterns (A→B→C→A)
- [ ] Prices don't reflect market (above/below fair value)
- [ ] No net position change for the network
- [ ] Timing: Rapid back-and-forth within minutes

**Evidence Quality:**
- TIER 1: Direct A→B→A circular pattern with same amounts
- TIER 2: Multi-hop circular patterns (A→B→C→A)
- TIER 3: Suspicious timing without clear circular pattern

**Example Pattern:**
```
14:00:00 - Wallet A sells 100K CRM to Wallet B @ $0.00014
14:02:30 - Wallet B sells 100K CRM to Wallet C @ $0.000141
14:05:00 - Wallet C sells 100K CRM to Wallet A @ $0.000142
Result: No net position change, fake volume created, price artificially pumped
```

---

### 5. Coordinated Multi-Wallet Dumping

**Definition:** Multiple wallets dumping simultaneously or in sequence to maximize extraction.

**Detection Criteria:**
- [ ] 3+ wallets selling within same 1-hour window
- [ ] Similar order sizes across wallets
- [ ] Sequential pattern (Wallet 1 → Wallet 2 → Wallet 3)
- [ ] Shared funding source or fee collector
- [ ] Same DEX pools used

**Evidence Quality:**
- TIER 1: 5+ wallets, same 30-minute window, shared fee collector
- TIER 2: 3+ wallets, same 1-hour window, similar patterns
- TIER 3: 2+ wallets with suspicious timing correlation

**Example Pattern:**
```
14:00:00 - Wallet A dumps 500K CRM on Raydium
14:05:00 - Wallet B dumps 500K CRM on Raydium
14:10:00 - Wallet C dumps 500K CRM on Raydium
14:15:00 - All three transfer SOL to GVC9Zvh3
Shared: Same fee collector, same pool, sequential timing
```

---

## Cross-Project Coordination Detection

### The Network May Be Active in Multiple Projects

**Analysis Framework:**

1. **Identify Network Wallets in CRM**
   - Confirmed: HLnpSz9h, 6LXutJvK, 7uCYuvPb, HGS4DyyX, DLHnb1yt
   - Suspected: ASTyfSima, H8sMJSCQ

2. **Track Their Activity in Other Projects**
   - Check if same wallets hold other tokens
   - Analyze trading patterns in other projects
   - Look for similar manipulation patterns

3. **Cross-Reference with Other Investigations**
   - Search for these wallets in other case files
   - Check blockchain analytics platforms (Nansen, Arkham)
   - Look for shared counterparty wallets

**Evidence Quality:**
- TIER 1: Same wallet confirmed in multiple project dumps
- TIER 2: Shared counterparty wallets across projects
- TIER 3: Similar timing patterns across projects

---

## DEX-Specific Analysis

### Raydium Analysis

**What to Look For:**
- Concentrated Liquidity (CLMM) pool interactions
- AMM v4 pool dumps
- Order book patterns on Raydium Pro

**Detection Script:**
```python
# Analyze Raydium transactions for:
# 1. CLMM position removals followed by dumps
# 2. AMM swaps with high slippage (indicating large orders)
# 3. Repeated swaps in same direction (sell pressure)
```

### Meteora Analysis

**What to Look For:**
- DLMM (Dynamic Liquidity Market Maker) interactions
- Concentrated liquidity withdrawals
- Multi-position strategies

### Jupiter Analysis

**What to Look For:**
- Route optimization patterns (splitting large orders)
- DCA (Dollar Cost Average) settings
- Limit order usage

### Orca Analysis

**What to Look For:**
- Whirlpool interactions
- Concentrated liquidity positions
- Similar patterns to Raydium

---

## Temporal Pattern Analysis

### Burst Detection

**Definition:** Many transactions in short time window

**Detection:**
```python
# Group transactions by 1-hour windows
# Flag windows with >10 transactions from same wallet
# Analyze for manipulation patterns
```

### Interval Analysis

**Definition:** Regular timing between transactions

**Detection:**
```python
# Calculate time deltas between transactions
# Check for regular intervals (automation indicator)
# Flag: std_dev < 10% of mean interval
```

### Synchronization Detection

**Definition:** Multiple wallets acting at same time

**Detection:**
```python
# Cross-correlate transaction timestamps across wallets
# Flag: 3+ wallets with transactions within 5 minutes
# Analyze for coordination
```

---

## Volume & Price Impact Analysis

### Individual Order Impact

**Small Impact Per Order:**
- <0.5% of pool liquidity = Iceberg indicator
- <1% of 1-hour volume = Drip feeding indicator

### Cumulative Impact

**Large Cumulative Impact:**
- >10% of wallet position dumped in 1 hour = Coordinated dumping
- >20% price decline over dumping period = Significant manipulation

### Price Recovery

**Post-Dump Analysis:**
- Does price recover after dumping stops?
- Recovery indicates artificial suppression
- No recovery indicates legitimate selling pressure

---

## Counterparty Analysis

### Who's Buying?

**Legitimate Buyers:**
- Diverse wallet addresses
- No pattern in timing
- Various order sizes

**Suspicious Counterparties:**
- Same wallets buying repeatedly
- Wash trading patterns
- Known network-controlled wallets

### Network Mapping

**Build Counterparty Graph:**
```
Dump Wallet → Buyer Wallet → Next Buyer
```

**Look for:**
- Circular patterns (wash trading)
- Hub-and-spoke (coordinated network)
- Chain patterns (money laundering)

---

## Evidence Compilation Template

### For Each Detected Pattern:

```markdown
## Pattern: [Iceberg/Liquidity Harvesting/Drip Feeding/Wash Trading/Coordination]

**Wallets Involved:**
- [Wallet 1]
- [Wallet 2]
- ...

**Time Period:**
- Start: [Timestamp]
- End: [Timestamp]
- Duration: [X hours/days]

**DEX:**
- [Raydium/Meteora/Jupiter/Orca]

**Pattern Details:**
- Number of transactions: [X]
- Total volume: [Y CRM]
- Average order size: [Z CRM]
- Timing pattern: [Every X minutes/hours]

**Evidence:**
- Transaction 1: [Signature] - [Amount] at [Time]
- Transaction 2: [Signature] - [Amount] at [Time]
- ...

**Price Impact:**
- Pre-dump price: $X.XXXX
- Post-dump price: $Y.YYYY
- Decline: Z%

**Counterparty Analysis:**
- Unique buyers: [X]
- Repeated counterparties: [List]
- Suspicious patterns: [Description]

**Cross-Wallet Coordination:**
- Shared fee collector: [Yes/No - Address]
- Sequential timing: [Yes/No - Pattern]
- Similar order sizes: [Yes/No - Variance %]

**Evidence Tier:**
- [TIER 1/2/3]

**Legal Significance:**
- Demonstrates: [Sophisticated manipulation/Coordination/Intent]
- Supports charge: [Market manipulation/Wire fraud/Money laundering]
```

---

## Action Items

### Immediate (This Week)

1. **Export DEX Transaction History**
   - [ ] All Raydium interactions from network wallets
   - [ ] All Meteora interactions from network wallets
   - [ ] All Jupiter swaps from network wallets
   - [ ] All Orca interactions from network wallets

2. **Run Pattern Detection Scripts**
   - [ ] Iceberg order detection
   - [ ] Liquidity harvesting analysis
   - [ ] Drip feeding identification
   - [ ] Wash trading detection
   - [ ] Cross-wallet coordination analysis

3. **Build Counterparty Database**
   - [ ] List all unique counterparties
   - [ ] Identify repeated buyers
   - [ ] Cross-reference with known network wallets
   - [ ] Flag suspicious patterns

### Short-Term (Next 2 Weeks)

4. **Cross-Project Analysis**
   - [ ] Check network wallets in other token projects
   - [ ] Analyze similar manipulation patterns
   - [ ] Build multi-project case

5. **Timeline Reconstruction**
   - [ ] Map all DEX dumps chronologically
   - [ ] Correlate with price action
   - [ ] Identify peak manipulation periods

6. **Financial Impact Calculation**
   - [ ] Calculate total extracted via DEX manipulation
   - [ ] Estimate price suppression impact
   - [ ] Compare to legitimate trading volume

### Medium-Term (Next Month)

7. **Expert Witness Preparation**
   - [ ] Document pattern detection methodology
   - [ ] Prepare visualizations
   - [ ] Draft technical explanation

8. **Legal Documentation**
   - [ ] Compile pattern evidence for each wallet
   - [ ] Prepare expert testimony
   - [ ] Cross-reference with other charges

---

## Tools & Scripts

### 1. DEX Transaction Exporter

Exports all DEX interactions for specified wallets.

### 2. Pattern Detection Engine

Analyzes exported data for manipulation patterns.

### 3. Counterparty Mapper

Builds graph of trading relationships.

### 4. Cross-Wallet Coordination Analyzer

Detects synchronized activity across multiple wallets.

---

## Conclusion

DEX transactions are **not innocent by default**. The network likely used sophisticated manipulation techniques to extract maximum value while avoiding detection. This framework provides the tools to identify:

- **Iceberg orders** hiding large positions
- **Liquidity harvesting** during high-volume periods
- **Drip feeding** over extended periods
- **Wash trading** to create fake volume
- **Cross-wallet coordination** for maximum impact

**Next Step:** Export DEX transaction history and run pattern detection to build the manipulation case.

---

**Document Classification:** TIER 1-2 EVIDENCE FRAMEWORK  
**Chain of Custody:** Evidence Fortress v4.0  
**Verification Status:** Pattern-based inference  
**Next Review:** Upon completion of DEX transaction export
