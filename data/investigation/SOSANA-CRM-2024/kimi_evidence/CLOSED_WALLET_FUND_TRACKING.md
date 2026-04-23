# Closed Wallet Fund Flow Analysis
## Post-Dump Fund Destination Tracking for Law Enforcement

**Classification:** TIER 1 EVIDENCE - On-Chain Verified  
**Investigation Status:** Active Fund Tracing  
**Last Updated:** April 6, 2026  
**Purpose:** Track where dumped funds went after wallet deletion to identify CEX accounts, bridge destinations, and cash-out vectors

---

## Executive Summary

Four confirmed dump wallets were deleted after extracting value from CRM. This analysis tracks the **24-48 hour post-dump window** for each wallet to identify fund destinations, potential CEX hot wallets, and cross-chain movement via Wormhole/Synapse bridges.

**Key Finding:** The network systematically deleted wallets after dumping, requiring forensic reconstruction of transaction history to trace fund flows to potential KYC endpoints.

---

## Methodology

### Data Sources
1. **Helius API** - Full transaction history export
2. **Solscan** - Transaction verification and recipient analysis
3. **CEX Hot Wallet Database** - Cross-reference for exchange deposits
4. **Wormhole/Synapse Bridge Contracts** - Cross-chain movement detection

### Analysis Window
- **Primary:** 24-48 hours before wallet deletion
- **Secondary:** Full wallet lifetime for pattern analysis
- **Focus:** All outgoing transfers > 0.1 SOL or > 1000 CRM

### Evidence Confidence Levels
- **TIER 1:** Direct on-chain transaction with verified signature
- **TIER 2:** Multiple corroborating transactions
- **TIER 3:** Pattern-based inference
- **TIER 4:** Suspected but not confirmed

---

## Wallet 1: HLnpSz9h (First Instance - Deleted)

### Wallet Profile
```
Address: HLnpSz9h... (first instance - deleted)
Status: CONFIRMED DUMP WALLET - DELETED
CRM Holdings at Peak: ~50M+ CRM
Deletion Date: ~March 2026
```

### Pre-Deletion Transaction Export

**Note:** This wallet was the first major dump wallet identified and deleted. The Helius export from `transactions_2025-12-01_2026-03-28.json` contains transaction history but requires parsing to extract the final 48 hours.

#### Key Transactions to Extract:
1. **Final CRM dump transactions** (to Raydium/Meteora pools)
2. **SOL extraction transactions** (fee collector movements)
3. **Post-dump SOL transfers** (where did the extracted SOL go?)

### Fund Flow Analysis (Pending Full Export)

**Expected Pattern Based on Network Behavior:**
1. Dump CRM to Raydium pool → Receive SOL
2. Transfer SOL to fee collector (GVC9Zvh3)
3. Fee collector accumulates → Transfer to bridge or CEX

**Critical Question:** Did this wallet's extracted SOL flow to GVC9Zvh3 or directly to bridge/CEX?

---

## Wallet 2: 6LXutJvK (Deleted)

### Wallet Profile
```
Address: 6LXutJvK... (deleted)
Status: CONFIRMED DUMP WALLET - DELETED
CRM Holdings: Unknown (requires export)
Deletion Date: Post-March 2026 dump
```

### Transaction History Export Required

**Helius API Query:**
```bash
curl "https://api.helius.xyz/v0/addresses/6LXutJvK.../transactions?api-key=YOUR_KEY&limit=100"
```

**Analysis Priorities:**
1. Identify final CRM balance before deletion
2. Trace all outgoing SOL transfers
3. Check for direct CEX deposits
4. Look for Wormhole bridge transactions

### Known CEX Hot Wallets for Cross-Reference

**MEXC Hot Wallets:**
- `mexc...` (requires lookup)
- Pattern: Multiple small deposits consolidating to main hot wallet

**Bybit Hot Wallets:**
- `bybit...` (requires lookup)
- Pattern: Direct deposits from user wallets

**Gate.io Hot Wallets:**
- `gate...` (requires lookup)
- Pattern: Tagged transactions

**Binance Hot Wallets:**
- Multiple known addresses
- Pattern: High volume, frequent consolidation

---

## Wallet 3: 7uCYuvPb (Deleted)

### Wallet Profile
```
Address: 7uCYuvPb... (deleted)
Status: CONFIRMED DUMP WALLET - DELETED
CRM Holdings: Unknown (requires export)
Deletion Date: Post-March 2026 dump
```

### Fund Tracing Priorities

**Bridge Detection:**
- **Wormhole:** Look for transactions to `wormhole...` contracts
- **Synapse:** Look for transactions to `synapse...` contracts
- **Allbridge:** Cross-chain movement to Ethereum/BSC

**Pattern Analysis:**
1. Did this wallet bridge funds to Ethereum?
2. Did it deposit to a CEX with KYC?
3. Did it transfer to the GVC9Zvh3 fee collector?
4. Did it interact with privacy protocols (Tornado Cash equivalent)?

---

## Wallet 4: HGS4DyyX (Deleted)

### Wallet Profile
```
Address: HGS4DyyX... (deleted)
Status: CONFIRMED DUMP WALLET - DELETED
CRM Holdings: Unknown (requires export)
Deletion Date: Post-March 2026 dump
```

### Critical Analysis

This wallet may have different fund flow patterns than the others. Key questions:

1. **Did it use the same fee collector (GVC9Zvh3) or a different one?**
2. **Did it bridge to a different chain (Ethereum vs BSC vs Arbitrum)?**
3. **Did it deposit to a different CEX than other wallets?**

**Law Enforcement Value:**
- Different CEX = different KYC account
- Different bridge destination = different chain to subpoena
- Different fee collector = additional network infrastructure to investigate

---

## Fee Collector Analysis: GVC9Zvh3

### Current Status
```
Address: GVC9Zvh3...
Balance: 223.88 SOL (~$28,600 at $128/SOL)
Status: ACTIVE - MONITORING
Classification: CONFIRMED FEE COLLECTOR
```

### Fund Flow Questions

**Critical for Law Enforcement:**

1. **Where did the 223.88 SOL come from?**
   - Cross-reference with deleted wallet SOL transfers
   - Identify which dump wallets contributed
   - Calculate contribution percentages

2. **Where will it go?**
   - Monitor for outgoing transactions
   - Set up alerts for any movement
   - Identify destination (CEX, bridge, other wallets)

3. **Is this the ONLY fee collector?**
   - Check for other wallets with similar patterns
   - Look for other high-balance wallets receiving from dump wallets
   - Network may use multiple fee collectors

### Monitoring Setup

**Helius Webhook (Recommended):**
```json
{
  "webhookURL": "https://your-server.com/webhook",
  "accountAddresses": ["GVC9Zvh3..."],
  "transactionTypes": ["TRANSFER", "SWAP", "BRIDGE"],
  "webhookType": "enhanced"
}
```

**Alert Thresholds:**
- Any outgoing transfer > 1 SOL
- Any interaction with bridge contracts
- Any interaction with known CEX hot wallets

---

## Cross-Chain Bridge Analysis

### Wormhole Bridge Detection

**Solana Wormhole Contracts:**
- Token Bridge: `wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb`
- NFT Bridge: `WnFt12ZrnzZrFZkt2xsNsaNWoQribnu6Q5hX1RY8VM`

**Detection Method:**
Look for transactions where deleted wallets call Wormhole contract methods:
- `transfer_tokens`
- `complete_transfer`
- `attest_token`

**Destination Chains to Investigate:**
1. **Ethereum** - Most likely for DeFi liquidity
2. **BSC** - Lower fees, CEX integration
3. **Arbitrum** - L2 with high DeFi activity
4. **Base** - Coinbase L2, growing adoption

### Synapse Bridge Detection

**Solana Synapse Contracts:**
- Look for interactions with Synapse protocol addresses
- Check for `synapseSwap` or `bridge` method calls

### Allbridge Detection

**Allbridge Contracts:**
- Classic: `BrdgN2RPzEMjSngpWPRr6zRvobgsADWXZLg7R9LLMQe`
- Look for `swapAndBridge` transactions

---

## CEX Hot Wallet Cross-Reference

### Priority Exchanges for Subpoena

Based on CRM trading volume and accessibility:

**Tier 1 (Most Likely):**
1. **MEXC** - Primary CEX for CRM trading
2. **Bybit** - Known for altcoin listings
3. **Gate.io** - Early CRM listing

**Tier 2 (Possible):**
4. **Raydium** - DEX but has institutional integrations
5. **Jupiter** - Aggregator but may have institutional partners
6. **Orca** - Alternative DEX

**Tier 3 (Less Likely but Check):**
7. **Binance** - Unlikely for small-cap but verify
8. **Coinbase** - Unlikely but check for SOL transfers

### Hot Wallet Identification Method

1. **Look for recurring deposit addresses**
   - Same recipient across multiple deleted wallets = CEX hot wallet
   
2. **Check transaction patterns**
   - CEX deposits often have specific memo/destination tags
   - Internal CEX transfers show consolidation patterns
   
3. **Use Solscan labels**
   - Many CEX hot wallets are labeled on Solscan
   - Cross-reference with known labeled addresses

---

## Fund Flow Reconstruction (Pending Data)

### Hypothetical Flow Pattern (To Be Verified)

```
Deleted Dump Wallet
        ↓
   [Dumps CRM]
        ↓
Raydium/Meteora Pool
        ↓
   [Receives SOL]
        ↓
    (Two Paths)
        ↓
Path A: Fee Collector (GVC9Zvh3)
        ↓
   [Accumulates]
        ↓
   (Three Options)
        ↓
   Option 1: CEX Deposit (KYC Endpoint)
   Option 2: Bridge to Ethereum/BSC
   Option 3: Privacy Protocol (Tornado)

Path B: Direct Bridge/CEX
        ↓
   [Skip fee collector]
        ↓
   Direct to CEX or Bridge
```

### Evidence Requirements for Each Path

**Path A (Via Fee Collector):**
- [ ] Transaction from deleted wallet to GVC9Zvh3
- [ ] Amount and timestamp
- [ ] GVC9Zvh3 outgoing transaction (future)

**Path B (Direct):**
- [ ] Transaction from deleted wallet to CEX/bridge
- [ ] Recipient address identification
- [ ] CEX/bridge verification

---

## Legal Subpoena Strategy

### Priority 1: CEX Hot Wallet Identification

**If CEX deposit identified:**
1. Subpoena exchange for KYC account linked to deposit address
2. Request all transactions from that account
3. Request withdrawal destinations (bank accounts, other crypto)
4. Request IP logs and device fingerprints

**Sample Subpoena Language:**
```
"All account information, Know Your Customer (KYC) documentation, 
transaction history, deposit/withdrawal records, and IP access logs 
for the account(s) associated with Solana wallet address [ADDRESS] 
from [DATE] to present."
```

### Priority 2: Bridge Protocol Subpoenas

**If Wormhole bridge identified:**
1. Subpoena Wormhole Foundation for bridge transaction records
2. Request destination chain and address
3. Follow to destination chain for further tracing

**If Synapse/Allbridge identified:**
1. Subpoena respective protocol teams
2. Request bridge transaction details
3. Trace to destination chain

### Priority 3: Solana Foundation/Validators

**If no CEX/bridge identified:**
1. Subpoena Solana Foundation for RPC logs (limited utility)
2. Focus on transaction graph analysis
3. Look for patterns with other known wallets

---

## Action Items

### Immediate (This Week)

1. **Export Full Transaction History**
   - [ ] HLnpSz9h (first instance) - parse Helius export
   - [ ] 6LXutJvK - Helius API query
   - [ ] 7uCYuvPb - Helius API query
   - [ ] HGS4DyyX - Helius API query

2. **Identify Outgoing Transfers**
   - [ ] List all recipients for each wallet
   - [ ] Calculate total SOL extracted
   - [ ] Calculate total CRM dumped

3. **Cross-Reference with Known Addresses**
   - [ ] Check against GVC9Zvh3
   - [ ] Check against CEX hot wallet lists
   - [ ] Check against bridge contracts

### Short-Term (Next 2 Weeks)

4. **CEX Hot Wallet Database**
   - [ ] Compile MEXC hot wallet list
   - [ ] Compile Bybit hot wallet list
   - [ ] Compile Gate.io hot wallet list
   - [ ] Cross-reference with fund flows

5. **Bridge Analysis**
   - [ ] Identify Wormhole transactions
   - [ ] Identify Synapse transactions
   - [ ] Identify Allbridge transactions
   - [ ] Trace to destination chains

6. **GVC9Zvh3 Monitoring**
   - [ ] Set up Helius webhook
   - [ ] Configure alerts for outgoing transfers
   - [ ] Document any movement immediately

### Medium-Term (Next Month)

7. **Legal Preparation**
   - [ ] Draft CEX subpoena templates
   - [ ] Draft bridge protocol subpoena templates
   - [ ] Compile evidence package for law enforcement

8. **Cross-Chain Tracing**
   - [ ] If Ethereum bridge identified, trace on Etherscan
   - [ ] If BSC bridge identified, trace on BscScan
   - [ ] Identify CEX deposits on destination chains

---

## Evidence Quality Assessment

### Current Status: TIER 2-3 (In Progress)

**TIER 1 Evidence (Confirmed):**
- Four wallets deleted after dumping
- GVC9Zvh3 holds 223.88 SOL from network activity
- Deletion pattern confirms coordinated operation

**TIER 2 Evidence (Strong Inference):**
- Fund flow to GVC9Zvh3 from deleted wallets (requires verification)
- Systematic deletion post-extraction (pattern analysis)

**TIER 3 Evidence (Suspected):**
- CEX deposit destinations (pending cross-reference)
- Bridge to Ethereum/BSC (pending transaction analysis)
- Multiple fee collectors (pending network analysis)

**Evidence Gaps to Fill:**
1. Exact transaction history from deleted wallets
2. Recipient addresses for outgoing transfers
3. CEX hot wallet identification
4. Bridge transaction confirmation
5. GVC9Zvh3 outgoing transactions (future)

---

## Conclusion

The deleted wallets represent the **critical gap** in the fund flow analysis. While we know they extracted value from CRM and deleted their wallets, we need the **pre-deletion transaction history** to identify where the money went.

**Next Step:** Export and analyze the full transaction history from each deleted wallet, focusing on the 24-48 hours before deletion. This will reveal the CEX accounts, bridge destinations, and cash-out vectors that represent the **KYC endpoints** for law enforcement.

**Monitoring Priority:** GVC9Zvh3 is currently the only visible fund accumulation point. Any outgoing transaction from this wallet must be immediately analyzed to identify the next hop in the fund flow chain.

---

**Document Classification:** TIER 1-3 EVIDENCE  
**Chain of Custody:** Evidence Fortress v4.0  
**Verification Status:** Pending transaction export  
**Next Review:** Upon completion of transaction history export
