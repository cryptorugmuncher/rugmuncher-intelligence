# 🗺️ MunchMaps V2 - Revolutionary Blockchain Visualization

## Philosophy: "What Bubblemaps Wishes It Was"

### Key Differentiators from Bubblemaps:
1. **Temporal Analysis** - See evolution over time (playback)
2. **Behavioral Clustering** - Similar actions > direct transfers
3. **Fresh Wallet Detection** - Spot newly created wallets
4. **CEX Funding Tracing** - Follow money back to exchanges
5. **Indirect Connections** - Multi-hop relationships
6. **Pattern Recognition** - AI-detected anomalies
7. **Free Data Sources** - No expensive APIs required

---

## 🎯 Core Features

### 1. Temporal Visualization (Time Machine)
```
Current: Static snapshot
MunchMaps: "Play" button shows evolution
          - When wallets first appeared
          - How clusters formed over time
          - Funding flows chronologically
```

### 2. Behavioral Similarity (Not Just Transactions)
```
Bubblemaps: "Wallet A sent to Wallet B"
MunchMaps: "These 50 wallets all:
           - Created within 24 hours
           - Funded from same CEX
           - Bought exactly $500 worth
           - Never sold"
           → HIGH PROBABILITY: Same owner"
```

### 3. Fresh Wallet Detection
```
Detect wallets that:
- Were created < 7 days ago
- Immediately participated in token
- No prior transaction history
→ Sybil attack indicator
```

### 4. CEX Funding Analysis
```
Trace back to:
- Binance hot wallets
- Coinbase deposits
- Kraken withdrawals
→ Real-world identity clues
```

### 5. Indirect Connection Mapping
```
Instead of: A → B → C (direct)
Show: A → X → Y → B → Z → C
     (multi-hop relationships)
```

### 6. Amount Pattern Clustering
```
Wallets holding similar amounts:
- 100 wallets with exactly 1,000,000 tokens
- Created within 1 hour of each other
→ Airdrop farming or coordinated buying
```

---

## 🏗️ Architecture

### Free Data Sources:
1. **SolanaFM API** (Free tier) - Solana data
2. **Helius** (Free 100k/month) - Enhanced Solana
3. **Etherscan** (Free) - Ethereum data
4. **GitHub** (Free) - Known scam patterns
5. **Blockchain RPCs** (Free public nodes)
6. **Twitter API** (Free tier) - Social signals
7. **Telegram** (Free) - Community intel

### Analysis Engine:
1. **Temporal Analyzer** - Time-based patterns
2. **Behavioral Clusterer** - Similarity detection
3. **Funding Tracer** - CEX connections
4. **Anomaly Detector** - Statistical outliers
5. **Graph Builder** - Multi-hop connections

### Visualization:
1. **D3.js Force Graph** - Interactive network
2. **Time Slider** - Temporal playback
3. **Heat Maps** - Risk concentration
4. **Behavioral Charts** - Pattern visualization
