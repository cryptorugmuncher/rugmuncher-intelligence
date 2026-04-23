# TECHNICAL APPENDIX

## Blockchain Analysis Methodology

### Tools Used
- Helius API for transaction data
- Custom clustering algorithms
- Temporal analysis
- Behavioral pattern matching

### Clustering Methods
1. **Temporal Clustering**: Wallets funded within same time window
2. **Behavioral Clustering**: Similar transaction patterns
3. **Funding Source**: Common funding wallets
4. **Token Flow**: Token movement patterns
5. **Contract Interaction**: Common smart contract interactions
6. **Gas Pattern**: Similar gas price/timing
7. **Graph Analysis**: Network centrality metrics

## Anomaly Detection

### Ghost Signer Detection
- 17 wallets with identical behavioral signatures
- All funded within 7-second window
- All wiped after 30-115 days
- Parallel transaction signing detected

### Wash Trading Detection
- Self-trading loops identified
- Volume disproportionate to holder count
- Price manipulation patterns
- Coordinated buy/sell walls

## Data Integrity

All blockchain data verified against:
- Solana mainnet RPC nodes
- Multiple independent sources
- Cryptographic signatures
- Timestamp verification

---

*Technical analysis performed by RMI Forensics Platform v5.0*  
*Chain of custody maintained for all evidence*
