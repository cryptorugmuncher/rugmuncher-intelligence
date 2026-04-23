# RMI Platform - Complete Features Guide

## 🎯 Overview

The RMI (RugMunch Intelligence) platform is now a comprehensive crypto fraud investigation and protection ecosystem.

---

## 🔍 Core Investigation Features

### 1. Contract Check (100-Point Analysis)
**File:** `forensic/contract_checker.py`

Comprehensive token contract analysis scoring 0-100 points across 8 categories:

| Category | Points | Checks |
|----------|--------|--------|
| **Ownership** | 15 | Renounced, mint authority, freeze authority, upgrade authority |
| **Supply** | 15 | Concentration, max supply, burn mechanism |
| **Liquidity** | 15 | Locked status, concentration, LP token burn |
| **Code** | 10 | Verified source, known vulnerabilities |
| **Holders** | 15 | Distribution, whale concentration, new wallet % |
| **History** | 15 | Deployer history, similar contracts, previous rugs |
| **Trading** | 10 | Volume patterns, price manipulation |
| **Social** | 5 | Presence, legitimacy |

**API:** `GET /api/contract-check/<token_address>`

**Risk Levels:**
- 🟢 Safe (85-100)
- 🟢 Low (70-84)
- 🟡 Medium (50-69)
- 🔴 High (30-49)
- 🚨 Critical (0-29)

---

### 2. Dev Finder
**File:** `forensic/dev_finder.py`

Track developers across all their deployed tokens:

**Features:**
- Find developer behind any token
- List all tokens they've deployed
- Track rug pull history
- Find connected wallets
- Social profile mapping
- Risk scoring (0-100)

**Risk Levels:**
- 🟢 Minimal (0-10) - Clean history
- 🟢 Low (10-30) - Generally safe
- 🟡 Medium (30-50) - Some concerns
- 🔴 High (50-70) - Multiple red flags
- 🚨 Extreme (70-100) - Known scammer

**API:**
- `GET /api/dev-finder/<token_address>`
- `GET /api/dev-finder/wallet/<wallet_address>`
- `GET /api/dev-finder/search?q=<query>`

---

### 3. Shill Campaign Tracker
**File:** `forensic/shill_tracker.py`

Detect and analyze X/Twitter shill campaigns:

**Detection Types:**
- 🟢 Organic - Natural community interest
- 💰 Paid Promotion - Sponsored content
- ⚠️ Coordinated - Organized campaign
- 🤖 Bot Network - Artificial engagement
- 📉 Pump & Dump - Price manipulation

**Features:**
- Coordinated posting detection
- Bot network identification
- KOL participation tracking
- Campaign cost estimation
- Sentiment analysis
- Timeline visualization

**API:**
- `GET /api/shill-tracker/track/<token_address>`
- `GET /api/shill-tracker/campaign/<campaign_id>`
- `GET /api/shill-tracker/kol/<handle>`

---

### 4. KOL Reputation System
**File:** `forensic/kol_reputation.py`

Track and rate crypto influencers:

**Performance Metrics:**
- Call accuracy (24h, 7d, 30d, all-time)
- Average returns
- Successful vs failed calls
- Disclosure rate (paid promos)

**Tiers:**
| Tier | Score | Description |
|------|-------|-------------|
| 💎 Diamond | 90+ | Elite callers |
| 🥇 Platinum | 80+ | Highly trusted |
| 🥈 Gold | 70+ | Reliable |
| 🥉 Silver | 60+ | Decent |
| 🏅 Bronze | 50+ | Average |
| ⚪ Unranked | <50 | New/insufficient data |
| 🚫 Blacklisted | - | Known scammers |

**API:**
- `GET /api/kol/leaderboard?timeframe=all_time&limit=100`
- `GET /api/kol/<handle>`
- `GET /api/kol/search?q=<query>`

---

### 5. Trending Scams Monitor
**File:** `forensic/trending_scams.py`

Real-time scam detection and monitoring:

**Scam Stages:**
- ⚡ Early Warning - Initial indicators
- ⚠️ Suspicious - Multiple red flags
- 🚨 Confirmed - High confidence scam
- 💀 Rugged - Liquidity removed
- 📊 Post-Rug - Aftermath analysis

**Features:**
- New token monitoring
- Social signal analysis
- Volume anomaly detection
- ChainAbuse integration
- Real-time alerts

**API:**
- `GET /api/trending-scams?limit=20`
- `GET /api/trending-scams/<token_address>`
- `GET /api/trending-scams/stats`

---

## 🛡️ Protection Features

### 6. Wallet Protection Tools
**File:** `core/wallet_protection.py`

Protect users from scam tokens:

**Protection Levels:**
- 🟢 Minimal - Block only known scams
- 🟡 Standard - Block + warnings
- 🔴 Maximum - Block + warnings + simulation

**Protection Rules:**
- ✅ Block Known Scams
- ⚠️ Warn Suspicious (risk > 70)
- ⚡ New Token Warning (< 24h)
- ⚠️ Low Liquidity Warning (< $10k)
- 💰 Simulate High Value (>$1k + risk > 50)

**Features:**
- Transaction pre-checking
- Blocklist management
- Risk assessment
- Transaction simulation
- Protection statistics

**API:**
- `POST /api/wallet-protection/check`
- `POST /api/wallet-protection/protect`
- `GET /api/wallet-protection/stats?wallet=<address>`
- `POST /api/wallet-protection/simulate`

---

### 7. Browser Extension
**Files:** `extension/`

Chrome/Firefox extension for real-time protection:

**Supported Sites:**
- solscan.io
- dexscreener.com
- birdeye.so
- raydium.io
- jup.ag
- meteora.ag

**Features:**
- RMI score overlay on token pages
- Risk level indicator
- Red flag warnings
- Quick check from popup
- Wallet protection toggle
- Statistics tracking

**Widget Shows:**
- Security score (0-100)
- Risk level
- Red flags
- Category scores
- Link to full analysis

---

## 📧 Newsletter System

### 8. Morning Intelligence Briefing
**File:** `core/newsletter_system.py`

Daily crypto intelligence newsletter:

**Content:**
- Market overview
- Scam alerts (overnight)
- Investigation updates
- Trending tokens
- KOL highlights

**Schedule:** Daily at 8:00 AM UTC

---

### 9. Weekly Digest

Comprehensive weekly summary:

**Content:**
- Week's scam activity
- New investigations
- KOL performance
- Market analysis
- Featured reports

---

### 10. Subscription Tiers

| Tier | Price | Features |
|------|-------|----------|
| 🆓 Free | $0 | Basic alerts |
| 📰 Basic | $5/mo | Weekly newsletter |
| ⭐ Premium | $15/mo | Daily + Weekly |
| 🐋 Whale | $50/mo | Everything + exclusive |

**Payment:** Solana USDC

**API:**
- `POST /api/newsletter/subscribe`
- `POST /api/newsletter/payment/verify`
- `GET /api/newsletter/latest?type=morning`
- `GET /api/newsletter/stats`

---

## 🔬 Forensic Features

### 11. Wallet Clustering
**File:** `forensic/wallet_clustering.py`

Detect coordinated wallet groups:

**Methods:**
- Temporal proximity (5-min windows)
- Common counterparties
- Behavioral patterns
- Common funding sources

**API:** `GET /api/cluster/<wallet_address>`

---

### 12. Bubble Maps
**File:** `web/bubble_map_visualizer.py`

Interactive wallet relationship visualization:

**Features:**
- Size = transaction volume
- Color = wallet type
- Line thickness = connection strength
- Interactive depth control
- Export PNG/SVG

**API:** `GET /api/bubble/<wallet_address>?depth=2`

---

### 13. Final Report Generator
**File:** `forensic/final_report_generator.py`

Legal-ready forensic reports:

**Includes:**
- Named wallets and entities
- KYC vectors
- Evidence tiers
- Transaction signatures
- Methodology
- Corrections log
- Legal disclaimers

**Formats:** Markdown, JSON, PDF

---

## 🤖 AI Features

### 14. LLM Rotation System
**File:** `core/llm_rotation.py`

Intelligent free tier optimization:

**Providers:**
- Groq ($200 credit)
- Amazon Bedrock ($200 credit)
- Google AI (free tier)
- Anthropic (limited free)
- OpenRouter (free tier)
- DeepSeek (very cheap)

**Auto-selects best model for task while respecting rate limits**

---

### 15. RMI Bot
**File:** `bots/rmi_bot.py`

Polite crypto investigator for Telegram:

**Commands:**
- `/investigate <wallet>` - Deep analysis
- `/cluster <wallet>` - Find clusters
- `/bubble <wallet>` - Generate bubble map
- `/token <address>` - Analyze token
- `/report` - Generate report
- `/status` - System status
- `/methodology` - View methodology

---

## 📊 API Endpoints Summary

### Contract Analysis
- `GET /api/contract-check/<token>`
- `POST /api/contract-check/batch`

### Developer Tracking
- `GET /api/dev-finder/<token>`
- `GET /api/dev-finder/wallet/<wallet>`
- `GET /api/dev-finder/search`

### Shill Tracking
- `GET /api/shill-tracker/track/<token>`
- `GET /api/shill-tracker/campaign/<id>`
- `GET /api/shill-tracker/kol/<handle>`

### KOL Reputation
- `GET /api/kol/leaderboard`
- `GET /api/kol/<handle>`
- `GET /api/kol/search`

### Trending Scams
- `GET /api/trending-scams`
- `GET /api/trending-scams/<token>`
- `GET /api/trending-scams/stats`

### Wallet Protection
- `POST /api/wallet-protection/check`
- `POST /api/wallet-protection/protect`
- `GET /api/wallet-protection/stats`
- `POST /api/wallet-protection/simulate`

### Newsletter
- `POST /api/newsletter/subscribe`
- `POST /api/newsletter/payment/verify`
- `GET /api/newsletter/latest`
- `GET /api/newsletter/stats`

### Investigation
- `GET /api/investigate/<wallet>`
- `GET /api/cluster/<wallet>`
- `GET /api/bubble/<wallet>`
- `POST /api/report/generate`

### System
- `GET /api/status`
- `GET /api/methodology`
- `GET /api/llm/usage`

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start web server
python main.py web

# Start Telegram bot
python main.py telegram

# Generate report
python main.py report

# View LLM recommendations
python main.py llm
```

---

## 💰 Monetization

### Current Revenue Streams:
1. **Newsletter Subscriptions** - Crypto payments
2. **Premium API Access** - Rate limits
3. **Custom Reports** - Investigation services

### Future Opportunities:
1. **Browser Extension Premium** - Advanced features
2. **KOL Verification Service** - Paid verification
3. **White-label Solutions** - B2B partnerships
4. **Alert Subscriptions** - Real-time notifications
5. **Consulting Services** - Investigation expertise

---

## 🔒 Security

- Firewall (ufw) configured
- Fail2ban protection
- SSL via Let's Encrypt
- Services under supervisor
- SSH key authentication

---

Built with ❤️ using Kimi AI
