# 🍔 MunchMaps V2

**The Ultimate Blockchain Investigation Platform**

Track scammers. Recover funds. Stay safe. Zero cost to operate.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API](https://img.shields.io/badge/API-Open-blue.svg)](docs/API.md)
[![Deployment](https://img.shields.io/badge/Deploy-Ready-green.svg)](deploy.sh)

## 🚀 Quick Start

```bash
# Clone and deploy
git clone https://github.com/yourorg/munchmaps-v2.git
cd munchmaps-v2
./deploy.sh
```

## ✨ Features

- **33 Wallet Types** - From pig butcherers to nation-state actors
- **5 Blockchains** - Ethereum, Solana, Tron, BSC, Polygon
- **48 Free Data Sources** - Zero API costs
- **Interactive Visualization** - BubbleMaps-style graphs (free)
- **AI Copilot** - ChatGPT-powered analysis
- **Scam Recovery** - Help victims recover funds
- **Real-time Monitoring** - Alerts when funds move
- **Court-Ready Reports** - Professional PDF exports

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 5 lookups/day, basic risk score |
| **Starter** | $49/mo | 50 lookups/day, 3 chains |
| **Pro** | $199/mo | Unlimited, all features |
| **Enterprise** | $999/mo | White-label, API access |
| **Law Enforcement** | FREE | Full access, priority support |

## 📊 Zero-Cost Operation

- **48 free data sources**
- **Free visualization** (Cytoscape.js)
- **Aggressive caching** (70% fewer API calls)
- **API key rotation** (15-25x free capacity)
- **Monthly cost**: $0-50
- **Revenue potential**: $10K-100K+/mo

## 🛠️ Architecture

```
Frontend (React/Vue) → API (FastAPI) → Cache (Redis)
                                      ↓
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
              Explorers         OSINT Sources      Premium APIs
              (19 free)         (48 free)          (Paid tier)
```

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Zero Cost Guide](ZERO_COST_GUIDE.md)
- [Deployment Guide](deploy/README.md)
- [Admin Dashboard](admin/dashboard.html)

## 🌍 Live Demo

**Website**: https://munchmaps.io

**Free Tier**: 
- 5 wallet lookups per day
- No signup required
- Instant results

## 🏆 Use Cases

- **Crypto Investors** - Check if token is a scam
- **Scam Victims** - Track and recover stolen funds
- **Journalists** - Investigate crypto crimes
- **Law Enforcement** - Free professional tools
- **Exchanges** - Compliance and monitoring

## 🤝 Contributing

Open source and community-driven!

```bash
# Development setup
pip install -r requirements.txt
python api/main.py
```

## ⚖️ License

MIT License - Free for commercial use

## 📞 Support

- **Discord**: [discord.gg/munchmaps](https://discord.gg/munchmaps)
- **Twitter**: [@MunchMaps](https://twitter.com/MunchMaps)
- **Email**: support@munchmaps.io
- **Law Enforcement**: le@munchmaps.io

---

**Made with ❤️ for the crypto community**

*Zero cost. Maximum value. Catch the bad guys.*
