# CEX Hot Wallet Database
## Known Exchange Deposit Addresses for Cross-Reference

**Purpose:** Cross-reference fund flows from deleted wallets to identify KYC endpoints  
**Last Updated:** April 6, 2026  
**Status:** Active compilation - addresses being added as identified

---

## How to Use This Database

1. **When analyzing exported wallet history**, check recipient addresses against this list
2. **If match found**, mark as HIGH confidence CEX deposit
3. **If suspected but not confirmed**, mark as MEDIUM confidence and flag for verification
4. **Update this file** as new CEX wallets are identified through analysis

---

## MEXC Global

**Status:** Primary CEX for CRM trading - HIGH PRIORITY  
**Website:** mexc.com  
**Known Hot Wallets:**

```
# To be populated from:
# 1. Solscan labeled addresses
# 2. Community reports
# 3. Direct analysis of CRM trading pairs

Primary Hot Wallet: [PENDING IDENTIFICATION]
Secondary Wallets: [PENDING IDENTIFICATION]
```

**Identification Method:**
- Search Solscan for "MEXC" labeled addresses
- Look for wallets with high volume of CRM deposits
- Check for consolidation patterns (many small deposits → one large wallet)

**Subpoena Contact:**
- Legal: legal@mexc.com
- Compliance: compliance@mexc.com
- Jurisdiction: Seychelles (challenging)

---

## Bybit

**Status:** Secondary CEX for CRM trading  
**Website:** bybit.com  
**Known Hot Wallets:**

```
# To be populated from:
# 1. Solscan labeled addresses
# 2. Bybit API documentation
# 3. Community verification

Primary Hot Wallet: [PENDING IDENTIFICATION]
Secondary Wallets: [PENDING IDENTIFICATION]
```

**Identification Method:**
- Bybit occasionally publishes hot wallet addresses for transparency
- Look for wallets receiving deposits before large CRM sell orders
- Check transaction patterns (user deposit → internal transfer → hot wallet)

**Subpoena Contact:**
- Legal: legal@bybit.com
- Compliance: compliance@bybit.com
- Jurisdiction: Dubai (better than Seychelles)

---

## Gate.io

**Status:** Early CRM listing  
**Website:** gate.io  
**Known Hot Wallets:**

```
# To be populated from:
# 1. Solscan labeled addresses
# 2. Gate.io API documentation
# 3. Community verification

Primary Hot Wallet: [PENDING IDENTIFICATION]
Secondary Wallets: [PENDING IDENTIFICATION]
```

**Identification Method:**
- Gate.io has labeled wallets on Solscan
- Look for wallets with consistent deposit patterns
- Check for Gate.io-specific transaction memos

**Subpoena Contact:**
- Legal: legal@gate.io
- Compliance: compliance@gate.io
- Jurisdiction: Cayman Islands

---

## Binance

**Status:** Unlikely for CRM but verify  
**Website:** binance.com  
**Known Hot Wallets:**

```
# Well-documented hot wallets (public information)

Primary SOL Hot Wallet: 5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBw9KHKiyc6mU
Secondary Wallets: [Multiple - see Binance documentation]
```

**Note:** Binance is unlikely to list CRM due to compliance standards, but verify for:
- SOL transfers that might be pre-CRM accumulation
- Bridge transactions to BSC
- Large institutional deposits

**Subpoena Contact:**
- Legal: legal@binance.com
- Compliance: compliance@binance.com
- Jurisdiction: Multiple (complex)

---

## Coinbase

**Status:** Unlikely for CRM but verify for SOL  
**Website:** coinbase.com  
**Known Hot Wallets:**

```
# Well-documented institutional wallets

Primary SOL Custody: [Public information]
Retail Hot Wallets: [Public information]
```

**Note:** Coinbase is very unlikely for CRM, but check for:
- SOL transfers that might be pre-CRM accumulation
- Institutional custody relationships

**Subpoena Contact:**
- Legal: legal@coinbase.com
- Jurisdiction: USA (easiest subpoena)

---

## Raydium (DEX but institutional)

**Status:** DEX but has institutional integrations  
**Website:** raydium.io  
**Known Program Addresses:**

```
AMM Program: 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
Liquidity Pool Program: [Multiple pools]
```

**Note:** Raydium is a DEX, not a CEX, but:
- Institutional market makers may have KYC relationships
- Large liquidity providers can sometimes be identified
- Pool creation transactions may reveal operator wallets

**Subpoena Strategy:**
- Raydium is decentralized - no central entity to subpoena
- Focus on identifying market makers and liquidity providers
- Check for institutional API key usage

---

## Jupiter (Aggregator)

**Status:** DEX aggregator  
**Website:** jup.ag  
**Known Program Addresses:**

```
Jupiter Aggregator: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4
```

**Note:** Jupiter is an aggregator, not a CEX, but:
- Institutional users may be identifiable
- API usage may reveal operators

**Subpoena Strategy:**
- Jupiter is decentralized - no central entity
- Focus on transaction patterns and MEV extraction

---

## Cross-Chain Bridges

### Wormhole

**Status:** Primary Solana bridge  
**Contracts:**
```
Token Bridge: wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb
NFT Bridge: WnFt12ZrnzZrFZkt2xsNsaNWoQribnu6Q5hX1RY8VM
```

**Subpoena Strategy:**
- Wormhole Foundation may have records
- Destination chain address is visible on-chain
- Follow to Ethereum/BSC for further tracing

### Synapse

**Status:** Cross-chain liquidity protocol  
**Contracts:** [Update with actual addresses]

**Subpoena Strategy:**
- Synapse Protocol team may have records
- Check for bridge transaction logs

### Allbridge

**Status:** Solana bridge  
**Contracts:**
```
Classic: BrdgN2RPzEMjSngpWPRr6zRvobgsADWXZLg7R9LLMQe
```

**Subpoena Strategy:**
- Allbridge team may have records
- Destination chain visible in transaction data

---

## Identification Checklist

When analyzing exported wallet history, look for:

- [ ] **Recurring deposit addresses** - Same recipient across multiple deleted wallets
- [ ] **Round number transfers** - 1.0 SOL, 5.0 SOL, 10.0 SOL (CEX deposit pattern)
- [ ] **Transaction memos/tags** - Some CEXes require destination tags
- [ ] **Consolidation patterns** - Many small deposits → one large wallet
- [ ] **High volume wallets** - Check Solscan for wallets with >1000 transactions
- [ ] **Labeled addresses** - Solscan labels major CEX hot wallets
- [ ] **Timing patterns** - Deposits followed by exchange trading activity

---

## Adding New CEX Wallets

When you identify a new CEX hot wallet:

1. **Verify the identification** (multiple sources)
2. **Add to this database** with evidence
3. **Update CEX_HOT_WALLETS in scripts**
4. **Re-run fund flow analysis** with updated database

**Template for new entry:**
```markdown
## [Exchange Name]

**Status:** [Primary/Secondary/Unlikely]  
**Website:** [URL]  
**Known Hot Wallets:**

```
Primary: [ADDRESS]
Evidence: [How identified]
Confidence: [HIGH/MEDIUM/LOW]
```

**Subpoena Contact:**
- [Contact info]
```

---

## Priority Order for Subpoenas

1. **MEXC** - Most likely for CRM, but jurisdiction challenge
2. **Bybit** - Good jurisdiction (Dubai), likely for CRM
3. **Gate.io** - Early listing, possible for CRM
4. **Wormhole** - If bridge usage confirmed
5. **Binance/Coinbase** - Unlikely but verify for SOL

---

**Next Steps:**
1. Populate MEXC hot wallets from Solscan
2. Populate Bybit hot wallets from community verification
3. Populate Gate.io hot wallets from API docs
4. Re-run fund flow analysis with complete database

---

**Document Classification:** REFERENCE DATA  
**Last Verified:** April 6, 2026  
**Update Frequency:** As new wallets identified
