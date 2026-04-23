# FREE API Integration Guide - RMI Crypto Router

## Overview
All APIs listed here have **FREE tiers** sufficient for production use. The intelligent router automatically fails over between them.

---

## 1. HELIUS (Free Tier: 100k requests/month)
**Best For:** Rich token metadata, NFTs, enhanced transactions

**Configured In:** `HELIUS_KEY`

**Strengths:**
- Token metadata with off-chain images
- Wallet transaction history (enhanced)
- NFT collection data
- Webhook support

**Rate Limit:** 100 req/sec

**Fallback Chain:**
```
Helius → Solscan → Birdeye
```

---

## 2. QUICKNODE ($10/month or free credits)
**Best For:** Raw RPC access, program bytecode

**Configured In:** `QUICKNODE_KEY`

**Strengths:**
- Program bytecode fetch
- Raw account data
- Fast RPC queries
- Program accounts enumeration

**Rate Limit:** 50 req/sec

**Fallback Chain:**
```
QuickNode → Helius (RPC mode)
```

---

## 3. SOLSCAN (Free Tier: 10k requests/day)
**Best For:** Token holders, distribution analysis

**Configured In:** `SOLSCAN_KEY`

**Strengths:**
- Top 100 holder data
- Holder percentage calculations
- Token price (delayed)
- Transaction history

**Rate Limit:** 30 req/min

**Fallback Chain:**
```
Solscan → Helius → Birdeye
```

---

## 4. ARKHAM (Free Tier: 1k requests/day)
**Best For:** Wallet labels, entity intelligence

**Configured In:** `ARKHAM_KEY`

**Strengths:**
- Exchange wallet identification
- Entity labeling ("Binance", "Jump Trading")
- DeFi position tracking
- Smart money tracking

**Rate Limit:** 20 req/min

**Fallback Chain:**
```
Arkham → Manual labeling database
```

---

## 5. BIRDEYE (Free Tier: 60 req/min)
**Best For:** Real-time token prices

**Configured In:** `BIRDEYE_KEY` = `58c5b02e9e484c73b02691687379673a`

**Strengths:**
- Real-time price updates
- Token metadata
- Volume data
- Market cap calculations

**Rate Limit:** 60 req/min (1/sec)

**Fallback Chain:**
```
Birdeye → Jupiter → Solscan
```

---

## 6. JUPITER (FREE - No limits)
**Best For:** Swap quotes (price proxy), DEX aggregation

**No API Key Required**

**Strengths:**
- Real-time swap quotes
- Best price across all DEXs
- Route optimization
- Free forever

**Rate Limit:** 100 req/sec (generous)

**Fallback Chain:**
```
Jupiter → Birdeye → Solscan
```

---

## 7. GMGN.ai (FREE - No API key)
**Best For:** Smart money tracking, bundle detection, Pump.fun analysis

**No API Key Required**

**Unique Features:**
- **Top Traders:** Track wallets with highest PnL
- **Bundle Detection:** Find coordinated buying (sniper attacks)
- **Insider Wallets:** Identify dev/team wallets
- **Bonding Curve:** Pump.fun graduation tracking
- **Holder Changes:** Live holder flow analysis

**Rate Limit:** ~50 req/min (unofficial)

**Fallback Chain:**
```
GMGN → Manual analysis → Community reports
```

---

## Additional FREE APIs Available

### 8. DexScreener (FREE)
**URL:** `https://api.dexscreener.com`

**Best For:**
- Real-time DEX pair data
- Price charts
- Volume tracking
- Liquidity pools

**No API key required**

---

### 9. CoinGecko (Free Tier)
**URL:** `https://api.coingecko.com`

**Best For:**
- Historical prices
- Market cap rankings
- Exchange volumes
- Trending coins

**Rate Limit:** 10-50 calls/min (free tier)

---

### 10. SolanaFM (Free Tier)
**URL:** `https://api.solana.fm`

**Best For:**
- Alternative RPC
- Account parsing
- Transaction decoding
- Program analysis

---

### 11. Bitquery (Free Tier - GraphQL)
**URL:** `https://graphql.bitquery.io`

**Best For:**
- Complex queries
- Historical analysis
- Cross-chain data
- Custom aggregations

**Rate Limit:** 1000 points/day (free tier)

---

## Complete Routing Matrix

### Token Metadata Request
```
1. Helius (0.95 score) → Rich metadata + images
2. Solscan (0.80 score) → Basic metadata
3. Birdeye (0.75 score) → Minimal metadata
4. Error
```

### Price Data Request
```
1. Birdeye (0.95 score) → Real-time price
2. Jupiter (0.90 score) → Swap quote price
3. Solscan (0.85 score) → Delayed price
4. Error
```

### Wallet Analysis Request
```
1. Arkham (0.95 score) → Labels + entities
2. Helius (0.85 score) → Transaction history
3. QuickNode (0.90 score) → Raw balance
4. Error
```

### Smart Money Detection
```
1. GMGN (0.98 score) → Top traders + PnL
2. Arkham (0.70 score) → Entity tracking
3. Manual analysis
```

### Bundle Detection
```
1. GMGN (0.95 score) → Coordinated buys
2. Helius (0.60 score) → Transaction timing
3. Manual pattern analysis
```

---

## Cache Strategy

| Data Type | TTL | Provider | Volatility |
|-----------|-----|----------|------------|
| Token Metadata | 1 hour | Helius/Solscan | Low |
| Wallet Balance | 30 seconds | Helius/QuickNode | High |
| Price | 1 minute | Birdeye/Jupiter | Very High |
| Holders | 5 minutes | Solscan | Medium |
| Bytecode | 24 hours | QuickNode | Immutable |
| Top Traders (GMGN) | 5 minutes | GMGN | High |
| Bundles | 10 minutes | GMGN | Medium |
| Bonding Curve | 1 minute | GMGN | Very High |

---

## Cost Analysis (Monthly)

| API | Free Tier | Our Usage | Cost |
|-----|-----------|-----------|------|
| Helius | 100k req | ~30k | $0 |
| QuickNode | Credits | ~20k | ~$0-10 |
| Solscan | 10k/day | ~5k | $0 |
| Arkham | 1k/day | ~500 | $0 |
| Birdeye | 60/min | ~30/min | $0 |
| Jupiter | Unlimited | ~50k | $0 |
| GMGN | ~50/min | ~20/min | $0 |
| **TOTAL** | | | **$0-10/month** |

---

## Environment Variables Required

```bash
# Core APIs
HELIUS_KEY=your_helius_key
QUICKNODE_KEY=your_quicknode_key
SOLSCAN_KEY=your_solscan_key
ARKHAM_KEY=your_arkham_key
BIRDEYE_KEY=58c5b02e9e484c73b02691687379673a

# GMGN - No key required (FREE)
# Jupiter - No key required (FREE)

# Database & Webhooks
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

---

## Testing Commands

```bash
# Test Helius
curl -X POST http://localhost:8002/api/v1/router/query \
  -d '{"data_type": "token_metadata", "target": "TOKEN_MINT"}'

# Test Birdeye price
curl -X POST http://localhost:8002/api/v1/router/query \
  -d '{"data_type": "price_data", "target": "TOKEN_MINT"}'

# Test GMGN top traders (FREE)
curl -X POST http://localhost:8002/api/v1/router/query \
  -d '{"data_type": "top_traders", "target": "TOKEN_MINT"}'

# Test Jupiter (FREE - no key)
curl https://quote-api.jup.ag/v6/price?id=So11111111111111111111111111111111111111112
```

---

## Fallback Behavior

When a provider fails:
1. **Retry** (1 attempt with 1s delay)
2. **Mark unhealthy** (skips for 60s)
3. **Try next provider** in chain
4. **Return best available** data
5. **Log failure** for monitoring

All failures are logged and tracked in health endpoint.

---

## Next Steps

1. **Add API keys** to `.env` file
2. **Restart backend** to load new config
3. **Test each provider** via health endpoint
4. **Monitor fallback** behavior in logs
5. **Scale up** to paid tiers if free limits exceeded
