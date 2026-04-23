# Munch Maps V2 - Lean MVP Implementation Plan
## Cost-Optimized Architecture Using Cloud Credits & Free Tiers

**Version:** 1.0  
**Date:** 2026-04-13  
**Budget:** $2,000 GCP + $180 AWS + $300 Oracle + Free Tiers  
**Goal:** MVP with 10,000+ wallet coverage (50x Bubblemaps) for under $500 actual spend

---

## 1. CLOUD CREDIT ARSENAL

### Confirmed Credits
| Provider | Amount | Validity | Best Use |
|----------|--------|----------|----------|
| **Google Cloud** | $2,000 | 90 days from activation | BigQuery, GKE, Cloud SQL |
| **AWS** | $180 | 12 months | EC2 spot, S3, Lambda |
| **Oracle Cloud** | $300 (estimated) | Always Free + credits | Compute instances, Autonomous DB |

### Additional Free Tier Providers to Claim

| Provider | Free Tier | How to Get | Best For |
|----------|-----------|------------|----------|
| **IBM Cloud** | $200 credit + Lite tier | New account signup | Kubernetes, Watson ML |
| **DigitalOcean** | $200 credit (GitHub Student/Referral) | Referral link | Managed databases, simple compute |
| **Linode (Akamai)** | $100 credit | New account promo | Block storage, Kubernetes |
| **Vultr** | $100 credit | New account | Cheap compute instances |
| **Hetzner Cloud** | €20 credit | New account | CHEAPEST compute in EU |
| **Alibaba Cloud** | $450 credit (new users) | Signup promo | International regions |
| **Tencent Cloud** | $200 credit | New account | APAC regions |
| **Paperspace** | $10 credit + free tier | ML platform | GPU instances for ML training |
| **Saturn Cloud** | Free community tier | Signup | Pandas/Dask data processing |
| **GitHub Codespaces** | 120 core-hours/month | GitHub Pro (free for students) | Development environments |
| **GitPod** | 50 hours/month | Free tier | Cloud IDE |
| **MongoDB Atlas** | 512MB-5GB forever free | Signup | Document database (skip TigerGraph initially) |
| **PlanetScale** | 5GB free | Signup | MySQL-compatible serverless DB |
| **Neon** | 3GB free | Signup | Serverless PostgreSQL |
| **Supabase** | 500MB-2GB free | Signup | Firebase alternative |
| **ClickHouse Cloud** | Trial credits | Signup | Analytics database |
| **Aiven** | 5GB free | Signup | Managed Kafka, PostgreSQL |
| **Upstash** | 10k requests/day | Signup | Serverless Redis |
| **Cloudflare Workers** | 100k requests/day | Signup | Edge functions (free tier) |
| **Vercel** | Hobby tier free | Signup | Frontend hosting |
| **Netlify** | Starter tier free | Signup | Frontend hosting |
| **Railway** | $5/month equivalent | Signup | Easy deployments |
| **Render** | Free tier | Signup | Web services, PostgreSQL |
| **Fly.io** | $20-30 credit | Signup | Container hosting |
| **CockroachDB** | 5GB free | Signup | Distributed SQL |
| **YugabyteDB** | Free tier | Signup | Distributed PostgreSQL |
| **TiDB** | $50 credit + free tier | Signup | HTAP database |
| **ScyllaDB Cloud** | Free tier | Signup | Cassandra-compatible |
| **DataStax Astra** | $25/month free | Signup | Cassandra as a service |
| **StreamNative** | Free tier | Signup | Managed Pulsar (Kafka alternative) |
| **Confluent Cloud** | $400 credit | Signup | Managed Kafka |
| **Quix** | Free tier | Signup | Stream processing |
| **Estuary** | Free tier | Signup | Real-time ETL |
| **Airbyte** | Self-hosted free | GitHub | Data integration |
| **Databend** | Free tier | Signup | Cloud data warehouse |
| **SelectDB** | Free tier | Signup | Apache Doris cloud |
| **StarRocks** | Self-hosted free | GitHub | Real-time analytics |
| **DuckDB** | Forever free | GitHub | In-process analytics |
| **QuestDB** | Self-hosted free | GitHub | Time-series database |
| **TimescaleDB** | Free tier | Signup | Time-series PostgreSQL |
| **InfluxDB Cloud** | Free tier | Signup | Time-series database |
| **Grafana Cloud** | Free tier | Signup | Monitoring/visualization |
| **SigNoz** | Self-hosted free | GitHub | APM + monitoring |
| **Uptime Kuma** | Self-hosted free | GitHub | Status monitoring |
| **NocoDB** | Self-hosted free | GitHub | Airtable alternative |
| **Baserow** | Self-hosted free | GitHub | Database builder |
| **Appsmith** | Free tier | Signup | Internal tools builder |
| **ToolJet** | Free tier | Signup | Low-code platform |
| **n8n Cloud** | Free tier | Signup | Workflow automation |
| **Trigger.dev** | Free tier | Signup | Background jobs |
| **Inngest** | Free tier | Signup | Event-driven workflows |
| **Temporal Cloud** | $200 credit | Signup | Durable execution |
| **Deel** | $200+ credit | Referral | Not compute, but useful |
| **Twilio** | $15 credit | Signup | SMS (for alerts) |
| **SendGrid** | 100 emails/day free | Signup | Email (for reports) |
| **Postmark** | 100 emails/month free | Signup | Transactional email |
| **Resend** | 3,000 emails/month free | Signup | Developer email |

**TOTAL POTENTIAL:** $5,000+ in credits + unlimited free tiers

---

## 2. LEAN ARCHITECTURE (MVP)

### Core Principle: Build Incrementally
Instead of the full 1M node enterprise architecture, start with:
1. **Phase 1:** 10,000 wallets (50x Bubblemaps) - Free tier only
2. **Phase 2:** 100,000 wallets - Use credits
3. **Phase 3:** 1M+ wallets - Revenue-funded scale

### MVP Tech Stack (Cost-Optimized)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: DATA COLLECTION (Free)                            │
├─────────────────────────────────────────────────────────────┤
│  Provider: Free RPC endpoints + Cheap paid backup          │
│  - Ankr (free tier: 10M calls/day)                         │
│  - Alchemy (free: 300M compute units/month)                │
│  - QuickNode (free tier available)                         │
│  - Chainstack (free tier: 5M requests)                      │
│  - BlastAPI (free tier)                                     │
│  - Infura (free: 100k requests/day) - skip (too low)         │
│  - Cloudflare ETH gateway (free, rate limited)               │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: STORAGE ($0-20/month)                             │
├─────────────────────────────────────────────────────────────┤
│  Primary: MongoDB Atlas (M10 tier with credits)             │
│  - 512MB-5GB free tier for dev                              │
│  - M10: $80/month (use credits)                              │
│  - Schema-flexible for rapid iteration                       │
│                                                              │
│  Alternative: PlanetScale (MySQL) or Neon (PostgreSQL)       │
│  - Both have generous free tiers                             │
│  - Use for relational data (users, cases, etc.)            │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: PROCESSING (Credits)                              │
├─────────────────────────────────────────────────────────────┤
│  GCP Cloud Run (serverless containers)                      │
│  - Pay only when processing                                  │
│  - $0 when idle (perfect for batch jobs)                   │
│  - 2M requests/month free tier                               │
│                                                              │
│  GCP Cloud Functions (lightweight)                         │
│  - 2M invocations/month free                                 │
│  - Perfect for webhooks, triggers                            │
│                                                              │
│  Alternative: AWS Lambda (1M requests free)                  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: GRAPH ANALYSIS (Free/Open Source)                 │
├─────────────────────────────────────────────────────────────┤
│  SKIP: TigerGraph (expensive, ~$2k/month at scale)          │
│                                                              │
│  USE: NetworkX + Pandas (free, runs on cheap compute)       │
│  - Handle 10k-100k nodes easily                             │
│  - Export to visualization-friendly format                   │
│  - Upgrade to graph-tool or igraph for speed               │
│                                                              │
│  Alternative: Memgraph (free tier available)                 │
│  - Cypher-compatible (Neo4j-like)                           │
│  - Can run in Docker on cheap VPS                          │
│  - 10k nodes easily on $5-10/month VPS                     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: VISUALIZATION (Free)                              │
├─────────────────────────────────────────────────────────────┤
│  D3.js + Canvas (not SVG) - Free, proven                   │
│  - Can handle 10k nodes with canvas renderer                │
│  - Use force-graph library (open source)                   │
│                                                              │
│  Upgrade path:                                             │
│  - Pixi.js for 2D GPU acceleration (free)                  │
│  - Deck.gl for large-scale (free, by Uber)                  │
│  - Three.js for 3D force graphs (free)                     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 6: HOSTING (Free)                                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend: Vercel or Netlify (free tier)                    │
│  API: Cloudflare Workers (100k req/day free)                │
│  Or: GCP Cloud Run free tier                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. MVP IMPLEMENTATION ROADMAP

### Week 1-2: Foundation (Free)
**Cost: $0**

1. **Set up data pipeline**
   - Sign up for Ankr + Alchemy free tiers
   - Write Python script to fetch top 10,000 token holders
   - Store in MongoDB Atlas (free tier)

2. **Basic clustering**
   - Implement gas-funding heuristic in Python
   - NetworkX for graph operations
   - Run on GitHub Actions (2,000 minutes/month free)

3. **Simple visualization**
   - D3.js force-directed graph
   - Canvas renderer (not SVG)
   - Color by risk score
   - Deploy to Vercel

**Deliverable:** Static site showing 10k wallets with basic clustering

### Week 3-4: Inference Layer (Free/Credits)
**Cost: $0-50**

1. **Smart contract scoring**
   - Use Alchemy API to fetch contract bytecode
   - Simple heuristics (not full ML yet):
     - Check for `selfdestruct` opcode
     - Check for `blacklist` functions
     - Verify ownership concentration
   - Score 0-100

2. **Basic cross-chain**
   - Focus on ETH + BSC only (2 chains)
   - Use Bridge contracts event logs
   - Simple timestamp matching

3. **Entity clustering v1**
   - Gas-funding tree detection
   - Co-spending (for UTXO chains if added)
   - Store cluster assignments in MongoDB

**Deliverable:** Interactive graph with risk scores and clustering

### Week 5-6: OSINT Integration (Credits)
**Cost: $100-200 from GCP credits**

1. **Social media scraping**
   - Twitter API v2 (free tier: 500k tweets/month)
   - Telegram MTProto proxy (free)
   - Match addresses in bio/posts

2. **IP geolocation**
   - Use free MaxMind GeoLite2
   - Or: IP-API (free tier: 45 requests/minute)

3. **Wallet labeling**
   - Etherscan labels API
   - Open-source labels (blockchair, etc.)

**Deliverable:** Wallets show associated social handles + geolocation

### Week 7-8: Performance Optimization (Credits)
**Cost: $200-400 from credits**

1. **Pre-computed clusters**
   - Run clustering nightly on GCP Cloud Run
   - Store results in MongoDB
   - Users query pre-computed data

2. **CDN caching**
   - Cloudflare free tier
   - Cache graph data at edge

3. **Incremental updates**
   - Only fetch new transactions
   - WebSocket for real-time (Socket.io on Render free tier)

**Deliverable:** <2 second load time for 10k wallet graph

---

## 4. COST PROJECTION

### Monthly Run Rate (MVP Scale: 10k-50k wallets)

| Component | Free Tier | Paid (Use Credits) | Actual Cost |
|-----------|-----------|-------------------|-------------|
| **RPC Calls** | Ankr 10M/day | Alchemy backup | $0 |
| **Database** | MongoDB 512MB | M10 for scale | $0 (credits) |
| **Compute** | GitHub Actions | GCP Cloud Run | $0 (credits) |
| **Hosting** | Vercel/Netlify | - | $0 |
| **Storage** | - | S3/GCS minimal | $5-10 |
| **Total** | | | **$5-10/month** |

### Credit Consumption Plan

| Provider | Amount | Use For | Duration |
|----------|--------|---------|----------|
| **GCP** | $2,000 | BigQuery analytics, Cloud Run, Cloud SQL | 6-12 months |
| **AWS** | $180 | S3 storage, EC2 spot for batch jobs | 3-6 months |
| **Oracle** | $300 | Always Free compute + Autonomous DB | 6-12 months |
| **MongoDB** | $200 | M10/M30 tier scaling | 2-3 months |
| **DigitalOcean** | $200 | Managed DB + Kubernetes | 4-6 months |
| **Confluent** | $400 | Managed Kafka (if needed) | 3-4 months |
| **IBM** | $200 | Watson NLU for text analysis | 3-4 months |
| **Others** | $500+ | Various | 6-12 months |
| **TOTAL** | **$4,000+** | | **12-18 months runway** |

---

## 5. SCALING PATH (Revenue-Funded)

### Phase 1: 10k wallets (Now)
- Free tier + minimal credits
- NetworkX + MongoDB
- D3.js canvas
- **Cost: $0-10/month**

### Phase 2: 100k wallets (Month 3-4)
- Use remaining credits
- Memgraph or Neo4j Aura (free tier)
- Pixi.js for rendering
- **Cost: $50-100/month (credits cover)**

### Phase 3: 1M wallets (Month 6+)
- Revenue-funded
- TigerGraph or self-hosted
- Deck.gl + Cosmos.gl
- **Cost: $500-1,000/month (from subscriptions)**

---

## 6. COMPETITIVE MOAT (With Lean Stack)

Even with minimal spend, you can beat Bubblemaps by:

1. **More Coverage**
   - They show: 150 wallets
   - You show: 10,000 wallets (66x more)
   - Technology: Simple canvas rendering + data aggregation

2. **Basic Inference**
   - Gas-funding detection (catches Sybil networks)
   - Contract risk scoring (catches honeypots)
   - Cross-chain matching (ETH ↔ BSC)

3. **Speed**
   - Pre-computed clusters
   - Edge-cached data
   - Static site generation for popular tokens

4. **Data Freshness**
   - Update every 4 hours vs their daily
   - Real-time webhook integration

---

## 7. ADDITIONAL FREE RESOURCES TO CLAIM

### GPU for ML Training (Contract Classification)
1. **Kaggle** - Free Tesla T4/P100 GPUs (30 hours/week)
2. **Google Colab** - Free Tesla T4 (12 hours/day limit)
3. **Paperspace** - $10 credit + free tier
4. **Lambda Cloud** - $10 trial credit
5. **Jarvislabs** - $10 trial credit
6. **RunPod** - $5 trial credit
7. **Vast.ai** - Cheap spot GPU instances

### Data Sources (Free)
1. **Etherscan API** - Free tier (5 calls/second)
2. **Basescan API** - Free tier
3. **BSCScan API** - Free tier
4. **DeFiLlama API** - Completely free
5. **CoinGecko API** - Free tier (15 calls/minute)
6. **CryptoCompare API** - Free tier
7. **The Graph** - Query subgraphs (free tier)
8. **Covalent API** - Free tier
9. **BitQuery** - Free tier (limited)
10. **Arkham Intel Exchange** - Free tier

### Open Source Alternatives to Paid Tools
| Paid Tool | Open Source Alternative |
|-----------|------------------------|
| TigerGraph | Memgraph, Neo4j Community |
| D3.js Premium | vis.js, sigma.js, Cytoscape.js |
| Alchemy | Self-hosted Erigon (on cheap VPS) |
| Kafka | Redpanda, Pulsar |
| DataDog | SigNoz, Uptime Kuma |
| Figma Penpot | Open source design tool |
| Notion AppFlowy | Open source |
| Airtable NocoDB | Self-hosted |
| Zapier n8n | Self-hosted |
| Twilio | Self-hosted SMS gateway |

---

## 8. IMMEDIATE ACTION ITEMS

### Today (Free)
1. [ ] Sign up for Ankr (free RPC)
2. [ ] Sign up for Alchemy (backup RPC)
3. [ ] Create MongoDB Atlas cluster (free tier)
4. [ ] Deploy Vercel project (hello world)
5. [ ] Write Python script to fetch 10k holders for test token

### This Week (Free)
1. [ ] Implement gas-funding heuristic
2. [ ] Build D3.js canvas visualization
3. [ ] Deploy to Vercel
4. [ ] Claim additional cloud credits (Oracle, IBM, DO)

### This Month (Credits)
1. [ ] Add contract risk scoring
2. [ ] Implement basic cross-chain
3. [ ] Add Twitter scraping
4. [ ] Optimize performance

---

## 9. RISK MITIGATION

### If Credits Run Out
- **Fallback to Hetzner:** €3-5/month VPS handles 10k nodes
- **Oracle Always Free:** 2 VMs forever free
- **AWS Free Tier:** 750 hours/month EC2 (12 months)
- **GCP Free Tier:** 1 f1-micro instance forever

### If MongoDB Free Tier Full
- Migrate to self-hosted PostgreSQL on cheap VPS
- Use TimescaleDB for time-series data
- Or: PlanetScale (MySQL) has larger free tier

### If RPC Rate Limited
- Rotate between 5+ free providers
- Implement request caching
- Self-host Erigon on Oracle free tier

---

## 10. SUCCESS METRICS

### MVP Success = 3 Things
1. **Coverage:** Show 10,000+ wallets (vs their 150)
2. **Inference:** Detect 5+ Sybil clusters per token
3. **Speed:** <3 second initial load

### Revenue Threshold for Scale
- **50 PRO subscribers @ $20/month = $1,000/month**
- This funds 1M node infrastructure
- Target: 6 months from MVP launch

---

## SUMMARY

**You don't need $10k/month infrastructure to beat Bubblemaps.**

You need:
1. **More data** (10k wallets vs 150) - **FREE**
2. **Basic inference** (gas clustering) - **FREE**
3. **Better UX** (canvas rendering, fast load) - **FREE**
4. **Smart credit usage** ($4k+ credits = 12-18 months runway)

**Total MVP cost: $0-10/month for 12-18 months**

Then scale with revenue.

---

*Next step: Claim your credits and build the 10k wallet MVP this week.*
