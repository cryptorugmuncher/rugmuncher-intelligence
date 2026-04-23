# RMI Core Platform - Free API Arsenal
## Master Intelligence System: Crypto, News, Data, AI APIs for RMI Ecosystem

**Version:** 2.0  
**Date:** 2026-04-13  
**Goal:** $0/month RMI Core infrastructure feeding all modules including 7+ Telegram bots, Munch Maps, Intel Tool, CRM, Trenches  

---

## RMI ARCHITECTURE: CORE PLATFORM DESIGN

**RMI (Rug Munch Intelligence)** is the definitive master platform. All other products are modules that consume RMI Core data.

```
┌─────────────────────────────────────────────────────────────┐
│                    RMI CORE PLATFORM                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Data In    │  │  AI Engine   │  │   OSINT      │      │
│  │  (APIs)      │  │  (LLM/ML)    │  │  (Intel)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           ▼                                │
│              ┌────────────────────────┐                    │
│              │    RMI CORE DATABASE   │                    │
│              │  (Single Source Truth) │                    │
│              └───────────┬────────────┘                    │
│                          │                                 │
│    ┌─────────────────────┼─────────────────────┐            │
│    │                     │                     │            │
│    ▼                     ▼                     ▼            │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│ │ Munch    │  │  Intel   │  │   CRM    │  │  Trenches│ │
│ │ Maps     │  │  Tool    │  │  System  │  │  Module  │ │
│ │ Module   │  │  Module  │  │  Module  │  │          │ │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │              TELEGRAM BOT MODULES                    ││
│ │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  ││
│ │  │@rugmunch │ │@rmi_alpha│ │@rmi_alerts│ │@rmi_     │  ││
│ │  │   bot    │ │  _alerts │ │    bot    │ │ backend │  ││
│ │  │ (Contract│ │  (PAID   │ │  (FREE    │ │  (System│  ││
│ │  │ Analysis)│ │  Alerts) │ │  Alerts) │ │  Alerts)│  ││
│ │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  ││
│ │  ┌──────────┐ ┌──────────┐ ┌──────────┐              ││
│ │  │@munchscans│ │@alpha_   │ │@rugmunch_ │              ││
│ │  │   _bot   │ │  scanner │ │intel_bot │              ││
│ │  │ (Tx      │ │  (Deep   │ │(OSINT    │              ││
│ │  │ Monitor) │ │  Scan)   │ │  Intel)  │              ││
│ │  └──────────┘ └──────────┘ └──────────┘              ││
│ └──────────────────────────────────────────────────────┘│
│                                                          │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│ │  Public  │  │   API    │  │   Web    │               │
│ │   SDK    │  │ External │  │   App    │               │
│ │  Module  │  │  Access  │  │  Portal  │               │
│ └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:** Free APIs → RMI Core → All Modules → Users

**Why this matters:**
- One data pipeline maintains all APIs
- Single AI layer serves all products
- Unified OSINT database
- No duplicate API costs
- Consistent evidence chain
- Telegram bots are the PRIMARY user interface for RMI

### TELEGRAM-EXCLUSIVE: Bot Fleet - @rugmunchbot Controls Everything

**⚠️ TELEGRAM ONLY:** This control structure is exclusive to Telegram platform. Website and API have separate direct access.

**@rugmunchbot = THE OPERATOR** - Controls all Telegram operations ("It all bb")

```
                         ┌─────────────────────────┐
                         │     @rugmunchbot       │
                         │                        │
                         │  THE OPERATOR          │
                         │  Controls Everything   │
                         │  "It all bb"          │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌────────▼────────┐
    │   RMI CORE DB     │  │   Worker Bots     │  │   Web/API      │
    │  (Data Layer)     │  │  (Execution)      │  │  (Interface)   │
    └─────────┬─────────┘  └─────────┬─────────┘  └────────┬────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ @rmi_alpha_     │  │ @munchscans_    │  │   Website       │
    │    alerts       │  │     bot         │  │  (cryptorug...  │
    │ (PAID alerts)   │  │ (Whale monitor) │  │                 │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ @rmi_alerts_bot │  │ @alpha_scanner  │  │   Intel Tool    │
    │ (FREE tier)     │  │    bot          │  │  (intel.crypt..)│
    └─────────────────┘  └─────────────────┘  └─────────────────┘
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ @rmi_backend_   │  │ @rugmunch_      │  │   Munch Maps    │
    │     bot         │  │   intel_bot     │  │  (visualizer)   │
    │ (System ops)    │  │ (OSINT intel)   │  │                 │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
```

| Component | Controlled By | Function |
|-----------|---------------|----------|
| **@rugmunchbot** | **Central Brain** | Main interface, commands all workers, manages RMI Core, "It all bb" |
| RMI Core Database | @rugmunchbot | Single source of truth for all data |
| Worker Bots | @rugmunchbot | Specialized execution arms (alerts, scans, intel) |
| Website/Tools | @rugmunchbot | Visual interfaces fed by bot-controlled data |

**TELEGRAM Control Flow (Exclusive):**
1. User → @rugmunchbot (Telegram entry point ONLY)
2. @rugmunchbot → queries RMI Core
3. @rugmunchbot → commands worker bots
4. Worker bots → report back to @rugmunchbot
5. @rugmunchbot → responds to Telegram user

**@rugmunchbot controls (Telegram only):**
- All Telegram bot operations
- All Telegram user interactions
- All Telegram alerts/notifications
- "It all bb" = everything in Telegram

**SEPARATE ENTRY POINTS:**
- **Telegram:** @rugmunchbot "It all bb" (exclusive control)
- **Website:** Direct tool access via browser
- **API:** Direct programmatic access
- **Each entry point feeds into RMI Core independently**

**Bot API Costs:** $0 (Telegram Bot API is free for unlimited bots)

---

## SECTION 1: BLOCKCHAIN DATA APIS (FREE TIERS)

### Primary RPC Providers (MUST SIGN UP - ALL FREE)

| Provider | Free Tier | Signup URL | Best For | Rate Limits |
|----------|-----------|------------|----------|-------------|
| **Ankr** | 10M requests/day | [ankr.com/rpc](https://www.ankr.com/rpc/) | Primary ETH/BSC/Polygon | No credit card |
| **Alchemy** | 300M CU/month | [alchemy.com](https://www.alchemy.com/) | NFT data, traces | 5 apps free |
| **QuickNode** | 25M credits/month | [quicknode.com](https://www.quicknode.com/) | Fast global RPC | 10 endpoints |
| **Infura** | 100k requests/day | [infura.io](https://www.infura.io/) | ETH mainnet | Requires CC, won't charge |
| **Chainstack** | 5M requests/month | [chainstack.com](https://chainstack.com/) | Multi-chain | 10+ chains free |
| **BlastAPI** | 25M API calls/month | [blastapi.io](https://blastapi.io/) | DeFi protocols | No CC required |
| **GetBlock** | 40k requests/day | [getblock.io](https://getblock.io/) | 50+ chains | IP-based limits |
| **Nodies** | 50M credits/month | [nodies.app](https://www.nodies.app/) | BSC/Solana | No limits seen |
| **Pocket Network** | 1M relays/day | [pokt.network](https://www.pokt.network/) | Decentralized | Stake POKT for more |
| **AllThatNode** | 10k requests/day | [allthatnode.com](https://www.allthatnode.com/) | Aptos/Sui | Asia-focused |

### Etherscan Family (Block Explorers)

| Explorer | Free Tier | Signup URL | Best For | API Limits |
|----------|-----------|------------|----------|------------|
| **Etherscan** | 5 calls/sec | [etherscan.io/apis](https://etherscan.io/apis) | Contract source, logs | 100k calls/day |
| **BSCScan** | 5 calls/sec | [bscscan.com/apis](https://bscscan.com/apis) | BSC tokens, pancakeswap | Same as Etherscan |
| **PolygonScan** | 5 calls/sec | [polygonscan.com/apis](https://polygonscan.com/apis) | Polygon PoS | Same limits |
| **Arbiscan** | 5 calls/sec | [arbiscan.io/apis](https://arbiscan.io/apis) | Arbitrum L2 | Same limits |
| **Optimistic Etherscan** | 5 calls/sec | [optimistic.etherscan.io/apis](https://optimistic.etherscan.io/apis) | Optimism L2 | Same limits |
| **BaseScan** | 5 calls/sec | [basescan.org/apis](https://basescan.org/apis) | Coinbase Base | Same limits |
| **Celoscan** | 5 calls/sec | [celoscan.io/apis](https://celoscan.io/apis) | Celo chain | Same limits |
| **GnosisScan** | 5 calls/sec | [gnosisscan.io/apis](https://gnosisscan.io/apis) | Gnosis/xDAI | Same limits |
| **FraxtalScan** | 5 calls/sec | [fraxtal.io/apis](https://fraxtal.io/apis) | Frax chain | Same limits |
| **BlastScan** | 5 calls/sec | [blastscan.io/apis](https://blastscan.io/apis) | Blast L2 | Same limits |

### Advanced Blockchain Data (Free Tiers)

| Provider | Free Tier | Signup URL | Best For | Limits |
|----------|-----------|------------|----------|--------|
| **The Graph** | 100k queries/month | [thegraph.com/studio](https://thegraph.com/studio/) | Subgraph queries | 10 deployments |
| **Covalent** | 10M credits/month | [covalenthq.com](https://www.covalenthq.com/) | Historical balances | Class A/B free |
| **Moralis** | 10M credits/month | [moralis.io](https://moralis.io/) | Real-time Web3 | Streams API |
| **DeFiLlama** | Unlimited | [defillama.com/docs/api](https://defillama.com/docs/api) | TVL, yields | No key needed |
| **CoinGecko** | 10-30 calls/min | [coingecko.com/api](https://www.coingecko.com/en/api) | Prices, market data | Public API free |
| **CoinMarketCap** | 10k calls/month | [coinmarketcap.com/api](https://coinmarketcap.com/api/) | Market cap, metadata | Professional plan |
| **CryptoCompare** | 250k calls/month | [cryptocompare.com/api](https://min-api.cryptocompare.com/) | OHLCV, social | Historical free |
| **BitQuery** | 10k points/day | [bitquery.io](https://graphql.bitquery.io/) | GraphQL blockchain | IDE available |
| **Arkham Intel** | Free tier | [platform.arkhamintelligence.com](https://platform.arkhamintelligence.com/) | Entity labeling | Points system |
| **Breadcrumbs** | Free searches | [breadcrumbs.app](https://breadcrumbs.app/) | Investigation | Limited volume |
| **TRM Labs** | Sandbox | [trmlabs.com](https://www.trmlabs.com/) | Risk scoring | API key required |
| **Chainalysis** | Demo | [chainalysis.com](https://www.chainalysis.com/) | Compliance data | Enterprise focus |
| **Nansen** | Limited free | [nansen.ai](https://www.nansen.ai/) | Smart money labels | Query limited |
| **Dune Analytics** | Free queries | [dune.com](https://dune.com/) | SQL on-chain | Community queries |
| **Flipside Crypto** | Free tier | [flipsidecrypto.com](https://flipsidecrypto.com/) | SQL analytics | Community plan |
| **Footprint Analytics** | Free tier | [footprint.network](https://www.footprint.network/) | Gaming/NFT data | Limited queries |

### Solana-Specific (Free)

| Provider | Free Tier | Signup URL | Best For |
|----------|-----------|------------|----------|
| **Helius** | 10M credits/month | [helius.xyz](https://www.helius.xyz/) | Solana RPC + APIs |
| **QuickNode Solana** | 25M credits | [quicknode.com](https://www.quicknode.com/) | Dedicated Solana |
| **SolanaFM** | Free tier | [solana.fm](https://solana.fm/) | Solana explorer API |
| **Phantom API** | Free | [phantom.app](https://phantom.app/) | Wallet integration |

---

## SECTION 2: NEWS & SENTIMENT APIs (FREE TIERS)

### Crypto News Aggregators

| Provider | Free Tier | Signup URL | Best For | Limits |
|----------|-----------|------------|----------|--------|
| **CryptoPanic** | 1 API call/min | [cryptopanic.com/developers/api](https://cryptopanic.com/developers/api/) | News sentiment | Public plan |
| **NewsAPI** | 100 requests/day | [newsapi.org](https://newsapi.org/) | General news | 12hr delay |
| **GNews** | 100 requests/day | [gnews.io](https://gnews.io/) | Google News alt | Limited countries |
| **Currents API** | 600 requests/day | [currentsapi.services](https://currentsapi.services/) | Global news | Good for crypto |
| **Newscatcher** | 10k requests/month | [newscatcherapi.com](https://www.newscatcherapi.com/) | Real-time news | 50 articles/request |
| **Aylien** | 1k calls/day | [aylien.com](https://aylien.com/) | NLP news analysis | 14-day trial |
| **Event Registry** | 1k queries/day | [eventregistry.org](https://eventregistry.org/) | Event detection | Good for rugs |
| **MediaStack** | 500 requests/month | [mediastack.com](https://mediastack.com/) | Live news | HTTP only free |

### Social Media APIs (Free/Scrappy)

| Platform | Method | Free Tier | Signup/Access | Rate Limits |
|----------|--------|-----------|---------------|-------------|
| **Twitter/X** | API v2 | 500k tweets/month | [developer.twitter.com](https://developer.twitter.com/) | Essential free |
| **Twitter** | Nitter (alt) | Unlimited | nitter.net instances | No auth needed |
| **Reddit** | PRAW | 100 requests/min | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps/) | OAuth required |
| **Reddit** | Pushshift | Free | [pushshift.io](https://pushshift.io/) | API archived |
| **Telegram** | MTProto | Free | [my.telegram.org](https://my.telegram.org/) | Self-hosted |
| **Discord** | Webhooks | Free | Server settings | No limits webhooks |
| **4chan** | API | Free | [4chan.org](https://github.com/4chan/4chan-API) | Read-only |

### Sentiment Analysis (Free AI)

| Provider | Free Tier | Signup URL | Best For |
|----------|-----------|------------|----------|
| **HuggingFace** | Unlimited (rate limited) | [huggingface.co/inference-api](https://huggingface.co/inference-api) | Pre-trained models |
| **Vader Sentiment** | Open source | [github.com/cjhutto/vaderSentiment](https://github.com/cjhutto/vaderSentiment) | Financial sentiment |
| **TextBlob** | Open source | [textblob.readthedocs.io](https://textblob.readthedocs.io/) | Simple polarity |
| **FinBERT** | Open source | [github.com/ProsusAI/finBERT](https://github.com/ProsusAI/finBERT) | Financial NLP |
| **Cardiff NLP** | HuggingFace | [huggingface.co/cardiffnlp](https://huggingface.co/cardiffnlp/) | Tweet sentiment |

---

## SECTION 3: OSINT & DATA APIs (FREE TIERS)

### IP/Geolocation (Free)

| Provider | Free Tier | Signup URL | Best For | Limits |
|----------|-----------|------------|----------|--------|
| **IP-API** | 45 requests/min | [ip-api.com](https://ip-api.com/) | No key needed | Non-commercial |
| **ipapi.co** | 30k requests/month | [ipapi.co](https://ipapi.co/) | JSON IP lookup | No auth |
| **ipgeolocation** | 1k requests/day | [ipgeolocation.io](https://ipgeolocation.io/) | Accurate data | API key |
| **MaxMind GeoLite2** | Free DB | [dev.maxmind.com](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) | Self-hosted | Download |
| **IPinfo** | 50k requests/month | [ipinfo.io](https://ipinfo.io/) | ASN data | No CC |
| **IP-API.com (pro)** | 10k/day free | [ip-api.com/docs/pro](https://ip-api.com/docs/pro) | SSL support | Requires key |

### Domain/DNS Intelligence (Free)

| Provider | Free Tier | Signup URL | Best For |
|----------|-----------|------------|----------|
| **WHOIS XML API** | 500 requests/month | [whoisxmlapi.com](https://whoisxmlapi.com/) | Domain registration |
| **ViewDNS.info** | Free | [viewdns.info](https://viewdns.info/) | DNS records |
| **DNSDumpster** | Free | [dnsdumpster.com](https://dnsdumpster.com/) | Subdomain finder |
| **SecurityTrails** | Free tier | [securitytrails.com](https://securitytrails.com/) | DNS history |
| **URLScan.io** | Free | [urlscan.io](https://urlscan.io/) | URL analysis |
| **VirusTotal** | 4 lookups/min | [virustotal.com](https://www.virustotal.com/) | Malware check |

### Wallet/Transaction OSINT (Free)

| Provider | Free Tier | URL | Best For |
|----------|-----------|-----|----------|
| **Etherscan** | 5 req/sec | etherscan.io | ETH address lookup |
| **BSCScan** | 5 req/sec | bscscan.com | BNB Chain lookup |
| **DeBank** | Free | debank.com | Portfolio tracking |
| **Zapper** | Free | zapper.fi | DeFi positions |
| **Zerion** | Free | zerion.io | NFT + DeFi |
| **Portfolio Tracker** | Free | [portfolio.nansen.ai](https://portfolio.nansen.ai/) | Nansen free |

---

## SECTION 4: AI/ML APIs (FREE TIERS)

### LLM APIs (Free Tiers)

| Provider | Free Tier | Signup URL | Model | Limits |
|----------|-----------|------------|-------|--------|
| **OpenAI** | $5-18 credit | [platform.openai.com](https://platform.openai.com/) | GPT-3.5/4 | 3-month expiry |
| **Anthropic** | $5 credit | [console.anthropic.com](https://console.anthropic.com/) | Claude 3 | Trial credits |
| **Google AI** | Free tier | [ai.google.dev](https://ai.google.dev/) | Gemini Pro | 60 req/min |
| **Cohere** | 100 API calls/month | [cohere.com](https://cohere.com/) | Command/Rerank | Trial |
| **AI21 Labs** | Free tier | [studio.ai21.com](https://studio.ai21.com/) | Jurassic | Limited tokens |
| **Mistral AI** | Free tier | [console.mistral.ai](https://console.mistral.ai/) | Mistral Small | Rate limited |
| **Groq** | Free tier | [console.groq.com](https://console.groq.com/) | Llama 3/Mixtral | 20 req/min |
| **Perplexity** | $5 credit | [perplexity.ai](https://www.perplexity.ai/) | Sonar models | API beta |
| **Together AI** | $5 credit | [together.ai](https://www.together.ai/) | Open models | GPU credits |
| **Fireworks AI** | 1M tokens/day | [fireworks.ai](https://fireworks.ai/) | Mixtral/Llama | Fast inference |
| **Replicate** | Free tier | [replicate.com](https://replicate.com/) | Open source LLMs | Pay per run |
| **HuggingFace** | Free inference | [huggingface.co/inference-api](https://huggingface.co/inference-api) | 150k+ models | Rate limited |
| **Ollama** | Self-hosted | [ollama.ai](https://ollama.ai/) | Local LLMs | Free forever |

### Embeddings & Vector DBs (Free)

| Provider | Free Tier | Signup URL | Best For |
|----------|-----------|------------|----------|
| **Pinecone** | 1 pod (5M vectors) | [pinecone.io](https://www.pinecone.io/) | Vector search |
| **Weaviate** | 14 days trial | [weaviate.io](https://weaviate.io/) | Semantic search |
| **Chroma** | Open source | [trychroma.com](https://www.trychroma.com/) | Local vector DB |
| **Qdrant** | 1GB free | [qdrant.tech](https://qdrant.tech/) | Rust-based |
| **Milvus** | Open source | [milvus.io](https://milvus.io/) | Distributed |
| **pgvector** | Open source | [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) | Postgres extension |
| **Cohere Embed** | 100 calls/month | [cohere.com](https://cohere.com/) | Text embeddings |
| **OpenAI Embed** | $5 credit | [openai.com](https://openai.com/) | Ada-002 |
| **HuggingFace** | Free | [huggingface.co](https://huggingface.co/sentence-transformers) | SBERT models |

### ML Platforms (Free GPU/Compute)

| Platform | Free Tier | Signup URL | GPU | Hours |
|----------|-----------|------------|-----|-------|
| **Google Colab** | Free | [colab.research.google.com](https://colab.research.google.com/) | T4/V100 | 12 hrs/day |
| **Kaggle** | Free | [kaggle.com](https://www.kaggle.com/) | T4/P100 | 30 hrs/week |
| **Paperspace** | $10 credit | [paperspace.com](https://www.paperspace.com/) | A4000 | Free tier |
| **Lambda Cloud** | $10 trial | [lambdalabs.com](https://lambdalabs.com/) | A10 | Trial |
| **RunPod** | $5 trial | [runpod.io](https://www.runpod.io/) | RTX A5000 | Serverless |
| **Vast.ai** | Spot instances | [vast.ai](https://vast.ai/) | Various | Cheap GPU |
| **Jarvislabs** | $10 credit | [jarvislabs.ai](https://jarvislabs.ai/) | A5000 | Trial |
| **Saturn Cloud** | Free tier | [saturncloud.io](https://saturncloud.io/) | Community | Shared |
| **Deepnote** | Free tier | [deepnote.com](https://deepnote.com/) | CPU | Unlimited |
| **Gradient** | Free tier | [gradient.paperspace.com](https://gradient.paperspace.com/) | Free GPU | 6 hrs/session |

---

## SECTION 5: DATA STORAGE & HOSTING (FREE TIERS)

### Databases (Free Forever/Extended)

| Provider | Free Tier | Signup URL | Limits | Best For |
|----------|-----------|------------|--------|----------|
| **MongoDB Atlas** | 512MB-5GB | [mongodb.com/atlas](https://www.mongodb.com/atlas) | M0 cluster | Document store |
| **PlanetScale** | 5GB | [planetscale.com](https://planetscale.com/) | MySQL-compatible | Relational |
| **Neon** | 3GB | [neon.tech](https://neon.tech/) | Serverless PG | Postgres |
| **Supabase** | 500MB | [supabase.com](https://supabase.com/) | 2GB bandwidth | Firebase alt |
| **CockroachDB** | 5GB | [cockroachlabs.cloud](https://cockroachlabs.cloud/) | Distributed SQL | Global |
| **YugabyteDB** | Free tier | [cloud.yugabyte.com](https://cloud.yugabyte.com/) | Distributed PG | Multi-region |
| **TiDB** | $50 credit | [tidbcloud.com](https://tidbcloud.com/) | HTAP | Real-time |
| **Upstash** | 10k req/day | [upstash.com](https://upstash.com/) | Serverless Redis | Caching |
| **Redis Cloud** | 30MB | [redis.com/try-free](https://redis.com/try-free/) | 1 database | Caching |
| **ScyllaDB** | Free tier | [cloud.scylladb.com](https://cloud.scylladb.com/) | Cassandra | NoSQL |
| **Astra DB** | $25/month free | [astra.datastax.com](https://astra.datastax.com/) | Cassandra | 80GB transfer |
| **ClickHouse** | Trial credits | [clickhouse.cloud](https://clickhouse.cloud/) | Analytics | Fast queries |
| **DuckDB** | Open source | [duckdb.org](https://duckdb.org/) | In-process | Local analytics |
| **SQLite** | Free | [sqlite.org](https://sqlite.org/) | File-based | Embedded |

### Hosting/CDN (Free)

| Provider | Free Tier | Signup URL | Best For |
|----------|-----------|------------|----------|
| **Vercel** | Hobby tier | [vercel.com](https://vercel.com/) | Next.js frontend |
| **Netlify** | Starter | [netlify.com](https://www.netlify.com/) | JAMstack |
| **Cloudflare Pages** | Free | [pages.cloudflare.com](https://pages.cloudflare.com/) | Edge hosting |
| **GitHub Pages** | Free | [pages.github.com](https://pages.github.com/) | Static sites |
| **Surge.sh** | Free | [surge.sh](https://surge.sh/) | Simple static |
| **Render** | Free tier | [render.com](https://render.com/) | Web services |
| **Railway** | $5/month | [railway.app](https://railway.app/) | Easy deploy |
| **Fly.io** | $20 credit | [fly.io](https://fly.io/) | Container hosting |
| **Heroku** | Eco dynos $5/mo | [heroku.com](https://www.heroku.com/) | Classic PaaS |
| **Oracle Cloud** | Always Free | [oracle.com/cloud/free](https://www.oracle.com/cloud/free/) | 2 VMs forever |
| **Google Cloud** | $300 credit | [cloud.google.com/free](https://cloud.google.com/free/) | 90 days |
| **AWS** | 12 months free | [aws.amazon.com/free](https://aws.amazon.com/free/) | 750 hrs EC2 |
| **Azure** | $200 credit | [azure.microsoft.com/free](https://azure.microsoft.com/en-us/free/) | 30 days |
| **IBM Cloud** | $200 credit | [ibm.com/cloud/free](https://www.ibm.com/cloud/free/) | Lite tier |
| **DigitalOcean** | $200 credit | [digitalocean.com](https://www.digitalocean.com/) | GitHub Student |
| **Linode** | $100 credit | [linode.com](https://www.linode.com/) | Promo codes |
| **Vultr** | $100 credit | [vultr.com](https://www.vultr.com/) | New users |

---

## SECTION 6: MESSAGE QUEUES & STREAMING (FREE)

| Provider | Free Tier | Signup URL | Best For |
|----------|-----------|------------|----------|
| **Confluent Cloud** | $400 credit | [confluent.io](https://www.confluent.io/) | Managed Kafka |
| **Upstash Kafka** | 10k req/day | [upstash.com](https://upstash.com/) | Serverless Kafka |
| **StreamNative** | Free tier | [streamnative.io](https://streamnative.io/) | Pulsar |
| **Aiven** | 5GB free | [aiven.io](https://aiven.io/) | Kafka/PG/Redis |
| **Quix** | Free tier | [quix.io](https://quix.io/) | Stream processing |
| **Estuary** | Free tier | [estuary.dev](https://estuary.dev/) | Real-time ETL |
| **Airbyte** | Self-hosted | [airbyte.com](https://airbyte.com/) | Data integration |
| **n8n** | Self-hosted | [n8n.io](https://n8n.io/) | Workflow automation |
| **Trigger.dev** | Free tier | [trigger.dev](https://trigger.dev/) | Background jobs |
| **Inngest** | Free tier | [inngest.com](https://www.inngest.com/) | Event workflows |
| **Temporal Cloud** | $200 credit | [temporal.io](https://temporal.io/) | Durable execution |

---

## SECTION 7: MONITORING & ANALYTICS (FREE)

| Provider | Free Tier | Signup URL | Best For |
|----------|-----------|------------|----------|
| **Grafana Cloud** | 10k metrics | [grafana.com](https://grafana.com/) | Dashboards |
| **SigNoz** | Self-hosted | [signoz.io](https://signoz.io/) | OpenTelemetry |
| **Uptime Kuma** | Self-hosted | [github.com/louislam/uptime-kuma](https://github.com/louislam/uptime-kuma) | Status monitoring |
| **Sentry** | 5k errors/month | [sentry.io](https://sentry.io/) | Error tracking |
| **LogRocket** | 1k sessions/mo | [logrocket.com](https://logrocket.com/) | Session replay |
| **Plausible** | Self-hosted | [plausible.io](https://plausible.io/) | Privacy analytics |
| **PostHog** | 1M events/month | [posthog.com](https://posthog.com/) | Product analytics |
| **Mixpanel** | 20M events/mo | [mixpanel.com](https://mixpanel.com/) | Product analytics |
| **Amplitude** | 10M events/mo | [amplitude.com](https://amplitude.com/) | Analytics |

---

## IMMEDIATE SIGNUP PRIORITY LIST

### Week 1 - Critical Path (Do Today)

**Blockchain Data:**
1. [ ] Ankr - [signup](https://www.ankr.com/rpc/) - 10M/day free
2. [ ] Alchemy - [signup](https://www.alchemy.com/) - 300M CU/month
3. [ ] QuickNode - [signup](https://www.quicknode.com/) - 25M credits/month
4. [ ] Etherscan API - [signup](https://etherscan.io/apis) - 5 req/sec
5. [ ] BSCScan API - [signup](https://bscscan.com/apis) - BSC data

**AI/LLM:**
6. [ ] OpenAI - [signup](https://platform.openai.com/) - $18 credit
7. [ ] Groq - [signup](https://console.groq.com/) - Fast Llama 3
8. [ ] HuggingFace - [signup](https://huggingface.co/) - Free inference
9. [ ] Google AI (Gemini) - [signup](https://ai.google.dev/) - 60 req/min

**Database:**
10. [ ] MongoDB Atlas - [signup](https://www.mongodb.com/atlas) - 512MB free
11. [ ] Upstash Redis - [signup](https://upstash.com/) - 10k req/day

**Hosting:**
12. [ ] Vercel - [signup](https://vercel.com/) - Hobby tier
13. [ ] Cloudflare - [signup](https://dash.cloudflare.com/) - Pages + Workers

### Week 2 - Extended Data Sources

**News & Sentiment:**
- [ ] CryptoPanic API - [signup](https://cryptopanic.com/developers/api/)
- [ ] Twitter API v2 - [signup](https://developer.twitter.com/)
- [ ] Reddit API - [signup](https://www.reddit.com/prefs/apps/)
- [ ] HuggingFace FinBERT - [use](https://huggingface.co/ProsusAI/finBERT)

**OSINT:**
- [ ] IPinfo - [signup](https://ipinfo.io/) - 50k/month
- [ ] MaxMind GeoLite2 - [signup](https://dev.maxmind.com/)
- [ ] VirusTotal - [signup](https://www.virustotal.com/)

**Analytics:**
- [ ] Dune Analytics - [signup](https://dune.com/)
- [ ] Flipside Crypto - [signup](https://flipsidecrypto.com/)
- [ ] DeFiLlama API - [docs](https://defillama.com/docs/api) - no signup

### Week 3 - Backup & Scaling

**Additional RPCs (for rotation):**
- [ ] GetBlock - [signup](https://getblock.io/)
- [ ] Nodies - [signup](https://www.nodies.app/)
- [ ] Chainstack - [signup](https://chainstack.com/)
- [ ] BlastAPI - [signup](https://blastapi.io/)

**Additional AI:**
- [ ] Cohere - [signup](https://cohere.com/)
- [ ] Together AI - [signup](https://www.together.ai/)
- [ ] Fireworks AI - [signup](https://fireworks.ai/)

**GPU Compute (for ML training):**
- [ ] Google Colab - [use](https://colab.research.google.com/)
- [ ] Kaggle - [signup](https://www.kaggle.com/)
- [ ] Paperspace - [signup](https://www.paperspace.com/)

---

## COST SUMMARY

### Running Monthly Cost with Free Tiers Only

| Component | Provider | Monthly Cost |
|-----------|----------|--------------|
| **RPC/Data** | Ankr + Alchemy + QuickNode | **$0** |
| **News** | CryptoPanic + NewsAPI | **$0** |
| **AI** | Groq + HF + Gemini | **$0** |
| **Database** | MongoDB Atlas + Upstash | **$0** |
| **Hosting** | Vercel + Cloudflare | **$0** |
| **Analytics** | Dune + DeFiLlama | **$0** |
| **Monitoring** | Grafana + Sentry | **$0** |
| **Storage** | S3 (minimal) | **$0-5** |
| **TOTAL** | | **$0-5/month** |

With $4,000+ in cloud credits claimed, you have 12-18 months of runway at scale.

---

## API ROTATION STRATEGY (For Rate Limit Avoidance)

When hitting limits, rotate through the free tier stack:

**Primary → Backup → Tertiary**

**ETH RPC:** Ankr (primary) → Alchemy (backup) → QuickNode (tertiary) → GetBlock (emergency)

**News:** CryptoPanic → NewsAPI → GNews → Currents (all free, rotate every 15 min)

**AI:** Groq → HuggingFace → Gemini → Ollama (local backup)

This gives you theoretical infinite throughput by distributing across 30+ free providers.

---

*Next: Start with Week 1 signup list. Ankr + Alchemy + Etherscan will get you 90% of MVP needs day one.*
