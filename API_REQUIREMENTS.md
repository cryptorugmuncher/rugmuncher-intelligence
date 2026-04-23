# 🔑 RMI Platform - Complete API Requirements

## Overview
**PRIMARY FOCUS: Solana Scam Detection & Investigation**

While we found some Ethereum wallets in the evidence (likely victims or cross-chain), **SOSANA/CRM was a Solana-based project**. Solana APIs are the priority.

---

## 🗄️ CATEGORY 1: Database & Infrastructure (CRITICAL)

### 1. Supabase (Already Have ✓)
**Purpose:** Primary database
**Status:** ✅ ACTIVE - Database connected

---

## 🔗 CATEGORY 2: Solana Blockchain APIs (CRITICAL - SOLANA PRIORITY)

### 2. Helius API (NEED - PRIMARY for Solana)
**Purpose:** Query Solana blockchain, token accounts, transactions
**Why Critical:** SOSANA/CRM was Solana-based, most wallets are SOL addresses
**Get Key:** https://helius.xyz
**Free Tier:** 100k requests/month
**What I Need:** API Key (format: UUID)
**Storage:** `.secrets/solana_apis.sh`

### 3. Solana RPC Backup (Optional)
**Purpose:** Fallback Solana endpoint
**Options:**
- QuickNode: https://quicknode.com
- Public: https://api.mainnet-beta.solana.com (rate limited)
**Storage:** `.secrets/solana_apis.sh`

---

## 🔗 CATEGORY 3: Ethereum Blockchain APIs (SECONDARY)

### 4. Ethereum RPC (Optional - Secondary)
**Purpose:** Query Ethereum blockchain for cross-chain analysis
**Why:** Some ETH wallets found in evidence (victims, exchanges)
**Options:**
- Alchemy: https://dashboard.alchemy.com (Free: 300M compute/month)
- Infura: https://infura.io (Free: 100k/day)
- Public: https://eth.llamarpc.com
**Storage:** `.secrets/blockchain_apis.sh`

### 5. BSC/Polygon RPC (Optional)
**Purpose:** Multi-chain scam detection
**Status:** ⚪ Optional for now
**Storage:** `.secrets/blockchain_apis.sh`

---

## 🤖 CATEGORY 4: AI & LLM APIs (HIGH PRIORITY)

### 6. Groq API (NEED - $200 free credits)
**Purpose:** Fast LLM for evidence analysis, transaction pattern detection
**Get Key:** https://console.groq.com/keys
**Free Tier:** $200 credits for 30 days
**Models:** Llama 3, Mixtral (ultra-fast for real-time analysis)
**Storage:** `.secrets/ai_apis.sh`

### 7. OpenAI/Claude (Optional)
**Purpose:** Complex analysis, embeddings
**Status:** ⚪ Optional - Groq primary
**Storage:** `.secrets/ai_apis.sh`

---

## 📊 CATEGORY 5: Data Scraping APIs (HIGH PRIORITY)

### 8. Apify API (NEED)
**Purpose:** X/Twitter scraping for scammer social analysis
**Get Key:** https://console.apify.com/account#/integrations
**Note:** You mentioned $5 credit already
**Storage:** `.secrets/scraping_apis.sh`

### 9. Firecrawl API (NEED - 500/month free)
**Purpose:** Scam website analysis, litepaper extraction
**Get Key:** https://firecrawl.dev
**Storage:** `.secrets/scraping_apis.sh`

### 10. Brave Search API (NEED - 2000/month free)
**Purpose:** Research scam projects, dev identities
**Get Key:** https://api.search.brave.com/app/dashboard
**Storage:** `.secrets/scraping_apis.sh`

---

## 📱 CATEGORY 6: Telegram Bot API (HIGH PRIORITY)

### 11. Telegram Bot Token (NEED)
**Purpose:** RMI investigation bot for Telegram-native scams
**Get:** Message @BotFather on Telegram, type `/newbot`
**Format:** `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
**Storage:** `.secrets/telegram_bot.sh`

---

## 🔄 CATEGORY 7: Workflow Automation

### 12. n8n Configuration
**Purpose:** Automate investigation workflows
**Status:** Already configured?
**Storage:** `.secrets/n8n_config.sh`

---

## 📋 UPDATED PRIORITY ORDER

### 🔴 CRITICAL (Solana Focus)
1. ⬜ **Helius API** (Primary Solana RPC)
2. ⬜ **Groq API** (AI analysis)

### 🟡 HIGH PRIORITY
3. ⬜ **Telegram Bot Token** (Bot integration)
4. ⬜ **Apify API** (X scraping)
5. ⬜ **Firecrawl API** (Web scraping)

### 🟢 MEDIUM PRIORITY
6. ⬜ **Ethereum RPC** (Cross-chain analysis)
7. ⬜ **Brave Search API** (Research)
8. ⬜ **n8n Webhook URL** (Workflows)

### ⚪ OPTIONAL
9. ⬜ OpenAI/Claude APIs
10. ⬜ Solana RPC Backup
11. ⬜ BSC/Polygon RPCs

---

## 🎯 SOLANA INVESTIGATION CONTEXT

**Current Data Shows:**
- **158 Ethereum wallets** - Likely victims who bought in, or cross-chain bridges
- **678 Telegram handles** - Primary scam communication
- **89 CRM token mentions** - Solana-based scam token

**Focus Areas:**
1. **Solana wallet tracing** - Track token movements on SOL
2. **Telegram analysis** - Bot communications, group structures  
3. **Social scraping** - X/Twitter for scam promotion
4. **Website analysis** - Scam litepapers, landing pages

---

## 🔐 SECURE STORAGE

Same structure as before, with Solana-specific file:

```
/root/rmi/.secrets/
├── solana_apis.sh        # NEW: Helius, Solana RPC
├── blockchain_apis.sh    # ETH, BSC, other chains
├── ai_apis.sh
├── scraping_apis.sh
├── telegram_bot.sh
├── n8n_config.sh
└── master_env.sh         # Loads all
```

---

## 🚀 PROVIDE APIS - SOLANA FIRST

**Recommended order:**
1. **Helius API** (for Solana blockchain queries)
2. **Groq API** (for AI analysis)
3. **Telegram Bot Token** (for bot)
4. **Apify** (for X scraping)

Tell me: "**Add Helius API: [your-key]**" to get started!
