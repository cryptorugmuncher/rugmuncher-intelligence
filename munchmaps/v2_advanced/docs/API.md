# MunchMaps V2 API Documentation

## Base URL
```
Production: https://api.munchmaps.io
Local: http://localhost:8000
```

## Authentication
```bash
# Free tier - API key in header
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.munchmaps.io/api/v1/wallet/lookup?address=0x...&chain=ethereum
```

## Rate Limits
| Tier | Daily Requests | Rate |
|------|----------------|------|
| Free | 5 | 10/min |
| Starter | 50 | 60/min |
| Pro | 1000 | 600/min |
| Enterprise | Unlimited | 6000/min |

## Endpoints

### Wallet Lookup (FREE)
```bash
GET /api/v1/wallet/lookup?address={address}&chain={chain}
```

**Response:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "chain": "ethereum",
  "risk_level": "suspicious",
  "transaction_count": 1523,
  "first_seen": "2023-01-15",
  "balance_usd": 45000,
  "is_contract": false,
  "tier": "free",
  "upgrade_prompt": "Upgrade for full analysis"
}
```

### Network Graph (FREE - Limited)
```bash
GET /api/v1/wallet/network?address={address}&chain={chain}&depth=1
```

### OSINT Aggregation (FREE)
```bash
GET /api/v1/osint/aggregate?query={address}
```

### Sanctions Check (FREE)
```bash
GET /api/v1/osint/sanctions?address={address}
```

### Premium: Full Analysis
```bash
GET /api/v1/premium/full-analysis?address={address}
```

### Premium: Pig Butcherer Specialist
```bash
GET /api/v1/premium/pig-butcherer?address={address}
```

## Webhooks (Pro+)
```bash
POST /api/v1/webhooks/register
{
  "url": "https://your-app.com/webhook",
  "events": ["large_transfer", "cex_interaction"],
  "wallets": ["0x...", "0x..."]
}
```

## SDKs
- Python: `pip install munchmaps`
- JavaScript: `npm install @munchmaps/sdk`
- Go: `go get github.com/munchmaps/go-sdk`
