# RMI (Rug Munch Intelligence) - Complete Platform Documentation
## Training Document for Bot Integration & System Architecture

**Document Version:** 2.0  
**Date:** 2026-04-13  
**Classification:** Internal Technical Documentation  
**Purpose:** Comprehensive system overview for AI training and developer onboarding

---

## 1. EXECUTIVE OVERVIEW

### 1.1 What is RMI?
RMI (Rug Munch Intelligence) is a comprehensive cryptocurrency scam detection and forensic investigation platform. It combines automated contract analysis, community-driven intelligence, OSINT (Open Source Intelligence) tools, and gamified user engagement to identify, track, and expose crypto scams.

### 1.2 Core Products
1. **Rug Munch Bot** (@rugmunchbot) - Telegram contract analysis bot
2. **Munch Maps** - Geographic visualization of scam networks
3. **The Trenches** - Community intelligence platform (retail interface)
4. **RMI Intel Platform** - Professional investigation dashboard
5. **CRM V2** - Case management system (relaunching after V1 collapse)

### 1.3 Mission Statement
"Illuminate the shadows of crypto through collective intelligence, forensic rigor, and unwavering transparency."

---

## 2. RUG MUNCH BOT - DETAILED SPECIFICATIONS

### 2.1 Bot Identity
- **Username:** @rugmunchbot
- **Token:** 8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU
- **Primary Function:** Automated smart contract analysis and risk scoring
- **Platform:** Telegram (primary), Web integration (secondary)

### 2.2 Core Features

#### Contract Scanning Engine
```
Scan Trigger: User submits contract address (CA)
Supported Chains: Ethereum, BSC, Polygon, Arbitrum, Base, Solana
Scan Time: 3-8 seconds average
Database: 342,847+ contracts analyzed (accurate count as of 2026-04-13)
```

**Analysis Components:**
1. **Honey Pot Detection** - Tests buy/sell simulation
2. **Ownership Analysis** - Checks contract ownership concentration
3. **Liquidity Verification** - Validates LP token locks and liquidity depth
4. **Code Similarity** - Cross-references known scam contracts
5. **Function Analysis** - Identifies malicious functions (mint, blacklist, etc.)
6. **Holder Distribution** - Analyzes whale concentration and distribution
7. **Social Signals** - Cross-references social media mentions and sentiment

#### Risk Scoring Algorithm
```python
Risk Score = (
    (honeypot_risk * 0.30) +
    (ownership_risk * 0.20) +
    (liquidity_risk * 0.20) +
    (code_risk * 0.15) +
    (distribution_risk * 0.10) +
    (social_risk * 0.05)
) * 100

Output: 0-100 Score
0-30: LOW RISK (Green)
31-60: MEDIUM RISK (Yellow) 
61-85: HIGH RISK (Orange)
86-100: CRITICAL RISK (Red)
```

#### Response Format
```
🚨 RUG MUNCH SCAN RESULTS 🚨

Token: $TOKEN_NAME
Contract: 0x... (Verified/Unverified)
Chain: [Network Icon]

📊 RISK SCORE: XX/100 [Color Coded]

🔍 ANALYSIS BREAKDOWN:
├─ Honey Pot Test: [PASS/FAIL]
├─ Ownership: [Concentration %]
├─ Liquidity: [Locked/Unlock Date]
├─ Code Safety: [Similarity Score]
└─ Holder Distribution: [Gini Coefficient]

⚠️ WARNINGS:
• [List of specific findings]

✅ SAFE INDICATORS:
• [List of positive findings]

🔗 Full Report: [Link to web dashboard]

🤖 Powered by RMI Intel
```

### 2.3 Integration Architecture
```
User → Telegram → Bot Handler → FastAPI Backend → Analysis Engine
                                          ↓
                                    PostgreSQL (Cache)
                                          ↓
                                    Web3 Providers (Alchemy/Infura)
                                          ↓
                                    Third-party APIs (Basescan, Etherscan)
```

### 2.4 Rate Limiting & Anti-Spam
- Free Tier: 5 scans/day per user
- PRO Tier: Unlimited scans
- Rate Limit: 1 scan per 10 seconds per user
- Duplicate Prevention: 1-hour cache for identical contracts

---

## 3. MUNCH MAPS - GEOINTELLIGENCE SYSTEM

### 3.1 Purpose
Munch Maps provides geographic visualization of cryptocurrency scam networks, tracing the physical locations of:
- Scammer operations
- Money laundering hubs
- Exchange concentrations
- Victim clusters
- Infrastructure nodes (servers, mining operations)

### 3.2 Data Sources
1. **IP Geolocation** - Exchange/trading platform access logs
2. **Wallet Clustering** - Blockchain analysis linking addresses to regions
3. **Social Media** - Geotagged posts from scammer accounts
4. **Domain Analysis** - Hosting location of scam websites
5. **User Reports** - Community-submitted location data
6. **OSINT Feeds** - Law enforcement and security research data

### 3.3 Visualization Layers
```
Layer 1: Heat Map (Scam concentration by region)
Layer 2: Node Graph (Connection between wallets and locations)
Layer 3: Timeline Animation (Scam evolution over time)
Layer 4: Threat Corridors (Money flow visualization)
Layer 5: Infrastructure Markers (Exchange, mixing service locations)
```

### 3.4 Technical Implementation
```javascript
// Frontend: Leaflet.js + Mapbox GL JS
// Backend: PostGIS for spatial queries
// Data Processing: Python GeoPandas + NetworkX

Map Features:
- Interactive zoom (Country → City → Street level where available)
- Filter by time range, scam type, token chain
- Cluster analysis (identifying scam syndicates)
- Export to KML/GeoJSON for law enforcement
```

### 3.5 Privacy & Ethics Framework
- Location data anonymized to city-level for non-law enforcement
- No exact residential addresses displayed publicly
- Differential privacy applied to victim location data
- Clear data retention policies (90 days for raw logs)

---

## 4. THE TRENCHES - RETAIL PLATFORM DETAILED BREAKDOWN

### 4.1 Overview
The Trenches is a Reddit-style community platform for crypto intelligence sharing. It gamifies scam detection through a badge system, karma points, and leaderboards.

### 4.2 Navigation Structure

#### Primary Feeds
```
FEED (Left Sidebar)
├── Hot (Trending discussions)
├── Trending (Rising posts)
├── Fresh (Newest submissions)
└── Random (Discovery mode)

ALPHA & GAINS
├── Calls (Price predictions)
├── Warnings (Scam alerts)
├── Analysis (Technical breakdowns)
└── Research (Deep dives)

COMMUNITY
├── General
├── Newcomer Help
├── Memes
└── Off-Topic
```

### 4.3 Post Types & Features

#### Post Creation Modal
```
Create Post Options:
1. 📊 ALPHA CALL - Predict price movements
2. 🚨 SCAM ALERT - Report suspicious contracts
3. 🔍 INVESTIGATION - Detailed analysis
4. 📰 NEWS - Crypto industry updates
5. ❓ QUESTION - Community Q&A
6. 💬 DISCUSSION - General topics
```

#### Gamification System

**Karma System:**
- Post Upvotes: +10 karma
- Comment Upvotes: +5 karma
- Verified Call: +100 karma
- Scam Confirmed: +200 karma
- Incorrect Call: -50 karma
- False Scam Report: -100 karma

**Badge System (50+ Badges):**

| Tier | Count | Examples |
|------|-------|----------|
| Common | 20 | First Post, First Comment, Daily Active |
| Uncommon | 15 | Verified Caller, Alpha Finder, Helper |
| Rare | 10 | Whale Spotter, Scam Hunter, Trend Setter |
| Legendary | 4 | Crypto Sherlock, Diamond Hands, Rug Destroyer |
| Secret | 3 | ??? (Easter egg badges) |

**Badge Unlock Animation:**
- Confetti effect on unlock
- Modal with badge display
- Social sharing integration
- Rarity-based sound effects

### 4.4 User Profile System
```
Profile Components:
├── Avatar (Dicebear generated)
├── Username + Handle (@username)
├── Karma Score (Lifetime + Current)
├── Badge Collection (Grid display)
├── Activity Graph (Posts/Comments over time)
├── Accuracy Rating (Call success rate)
├── Trust Score (Anti-sybil metric)
└── Investigation History (Linked cases)
```

### 4.5 Technical Stack (Frontend)
```
Framework: Vanilla HTML5 + Tailwind CSS (No React/Vue by design)
Styling: 
  - Tailwind CSS v3.x
  - Custom CSS Variables for theming
  - Dark mode default (--bg-primary: #0a0a0f)
  
Icons: Font Awesome 6.4.0
Fonts: 
  - Inter (primary)
  - JetBrains Mono (monospace/code)
  
Animations:
  - Custom CSS keyframes
  - GSAP for complex animations
  - Canvas confetti for badge unlocks

State Management: 
  - LocalStorage for user preferences
  - SessionStorage for temporary data
  - Backend API for persistent state
  
Real-time:
  - Server-Sent Events for notifications
  - WebSocket for live comments
```

### 4.6 Design Tokens
```css
:root {
  /* Colors */
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-tertiary: #1a1a24;
  --accent-primary: #00ff9d;    /* Crypto green */
  --accent-secondary: #00d4ff;  /* Alert blue */
  --accent-danger: #ff4757;     /* Scam red */
  --accent-warning: #ffa502;    /* Caution yellow */
  --text-primary: #ffffff;
  --text-secondary: #a0a0b0;
  
  /* Spacing */
  --nav-height: 64px;
  --sidebar-width: 280px;
  --content-max-width: 1200px;
  
  /* Effects */
  --glow-green: 0 0 20px rgba(0, 255, 157, 0.3);
  --glow-red: 0 0 20px rgba(255, 71, 87, 0.3);
  --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
```

---

## 5. CRM V1 COLLAPSE ANALYSIS

### 5.1 What Was CRM V1?
CRM V1 was the first iteration of RMI's investigation case management system, designed to track crypto scams through their entire lifecycle.

### 5.2 V1 Architecture Problems

#### Database Issues
```
Problem 1: Schema Fragmentation
- 10+ separate SQL files with conflicting schemas
- No foreign key constraints
- Data integrity failures
- Duplicate entries across tables

Problem 2: SQLite Limitations
- Single-file database for investigation data
- Corruption under concurrent access
- No replication or backup strategy
- 2GB size limit approached

Problem 3: Migration Hell
- No version control on schema changes
- Manual SQL migration scripts
- Data loss during schema updates
```

#### Code Organization Issues
```
Problem 1: Monolithic Structure
- 54 Python files in root directory
- Circular import dependencies
- No clear module boundaries
- "from *" imports everywhere

Problem 2: Service Layer Confusion
- Business logic mixed with API routes
- Direct database access from controllers
- No DTO (Data Transfer Object) pattern
- Raw SQL strings in HTTP handlers

Problem 3: Configuration Chaos
- Secrets hardcoded in files
- Environment variables scattered
- No centralized config management
```

### 5.3 Specific Failure Points

#### Evidence Processing Pipeline
```
Failure: Evidence Processor
- Queue system: In-memory (no persistence)
- Result: 47% of uploaded evidence lost on restart
- Processing: Synchronous (blocked API)
- No retry mechanism

Timeline of Collapse:
Day 1: 3 simultaneous large investigations started
Day 2: Evidence queue exceeded memory limit
Day 3: OOM killer terminated processor
Day 4: Database corruption from partial writes
Day 5: System offline, 18 hours of data lost
```

#### Wallet Analysis Engine
```
Failure: Wallet Tracer
- Recursive query depth: Unlimited (stack overflow)
- No caching strategy
- Rate limiting: None (API keys banned)
- Graph generation: O(n²) complexity

Result: Analysis of whale wallets caused
10-minute API timeouts, cascading failures
```

#### Authentication System
```
Failure: Session Management
- JWT tokens with no expiry
- No refresh token rotation
- Sessions stored in memory
- Cross-origin auth bypass vulnerability discovered

Security Impact: 12 user accounts compromised
Remediation: Emergency session invalidation
```

### 5.4 Lessons Learned

#### Technical Debt
1. **Start with schema design** - Database first, code second
2. **Queue everything** - Never process large jobs synchronously
3. **Circuit breakers** - Fail fast, don't cascade
4. **Observability** - You can't fix what you can't see

#### Organizational
1. **No more root-level files** - Everything has a home
2. **API-first design** - Frontend consumes, doesn't control
3. **Test coverage** - Unit tests for every service
4. **Documentation** - Code changes require doc updates

---

## 6. CRM V2 RELAUNCH STRATEGY

### 6.1 V2 Architecture Principles

#### Unified Directory Structure
```
/root/rmi/
├── backend/
│   ├── api/v1/                    # New unified API
│   │   ├── core/                  # auth, users, billing, api_keys
│   │   ├── crypto/                # contracts, tokens, wallets, alerts
│   │   ├── crm/                   # cases, evidence, timeline, reports
│   │   ├── tools/                 # processors, tracers, analyzers
│   │   ├── osint/                 # face_recognition, dating_search
│   │   └── token/                 # airdrop, discounts, holdings
│   ├── services/                  # Business logic layer
│   ├── models/                    # Pydantic/SQLAlchemy models
│   ├── database/
│   │   ├── unified_schema.sql     # Single source of truth
│   │   ├── migrations/            # Alembic migration scripts
│   │   └── seeds/                 # Initial data
│   └── main.py                    # FastAPI application entry
│
├── frontend/
│   ├── web/                       # Main marketing site
│   ├── retail/                    # The Trenches (community)
│   ├── investigation/             # CRM V2 dashboard
│   ├── education/                 # Learning resources
│   └── shared/                    # Common assets
│
├── data/
│   └── investigation/             # Isolated forensic storage
│
├── scripts/                       # Deployment & maintenance
└── docs/                          # Documentation
```

### 6.2 New API Layer (v1)

#### 24 API Modules
```
Core (5 modules):
├── auth.py           # JWT, OAuth, 2FA
├── users.py          # User CRUD, profiles
├── billing.py        # Stripe integration, invoices
├── api_keys.py       # Key generation, rate limits
└── subscriptions.py  # Tier management

Crypto (4 modules):
├── contracts.py      # Scan requests, results
├── tokens.py         # Token metadata, prices
├── wallets.py        # Analysis, labeling
└── alerts.py         # Webhook subscriptions

CRM (5 modules):
├── cases.py          # Investigation lifecycle
├── evidence.py       # Upload, chain of custody
├── timeline.py       # Event reconstruction
├── reports.py        # PDF generation, exports
└── wallets.py        # Case-linked wallets

Tools (3 modules):
├── evidence_processor.py  # Async processing
├── wallet_tracer.py       # Graph analysis
└── ocr.py                 # Document extraction

OSINT (3 modules):
├── face_recognition.py    # Image matching
├── dating_search.py       # Profile discovery
└── scammer_id.py          # Identity correlation

Token (4 modules):
├── airdrop.py        # Eligibility checks
├── discounts.py      # Promo code system
├── holdings.py       # Portfolio verification
└── staking.py        # Lock-up tracking
```

### 6.3 Database Schema Consolidation

#### PostgreSQL (Primary Database)
```sql
-- Core Tables
users, api_keys, sessions, billing_transactions

-- Crypto Tables  
token_contracts, analyzed_wallets, transactions, 
watchlist, alerts, scan_history

-- CRM Tables (V2)
investigation_cases (
    id, case_number, status, priority,
    assigned_investigator, created_at, updated_at,
    resolved_at, case_type, tags
),

evidence_items (
    id, case_id, evidence_type, hash_sha256,
    storage_path, metadata, chain_of_custody,
    uploaded_by, uploaded_at, processing_status
),

timeline_events (
    id, case_id, event_type, timestamp,
    description, source, evidence_refs,
    blockchain_tx, confidence_score
),

investigation_wallets (
    id, case_id, wallet_address, chain,
    entity_name, risk_score, transaction_count,
    first_seen, last_seen, tags
)

-- Billing Tables
subscriptions, scan_usage, payment_methods
```

#### Redis (Cache & Queue)
```
Purpose:
- Session cache (TTL: 24 hours)
- Rate limiting counters (TTL: 1 hour)
- Evidence processing queue
- Webhook retry queue
- Real-time leaderboards

Key Patterns:
session:{user_id} → JWT payload
rate:{endpoint}:{user_id} → request count
queue:evidence → Redis Streams
queue:webhooks → Redis Streams
cache:contract:{address} → scan results (TTL: 1 hour)
```

#### IPFS/S3 (Evidence Storage)
```
Tier 1 (Hot): S3 Standard - Active cases
Tier 2 (Warm): S3 IA - Closed cases < 1 year
Tier 3 (Cold): Glacier - Archived > 1 year

Hash verification: SHA-256 on upload
Encryption: AES-256 at rest
Access: Signed URLs with 15-minute expiry
```

### 6.4 Investigation Workflow (V2)

#### 5-Tier Criminal Hierarchy Analysis
```
Tier 1: Token/Contract Level
├─ Smart contract analysis
├─ Token distribution analysis
├─ Liquidity examination
└─ Code similarity matching

Tier 2: Wallet Level
├─ Transaction pattern analysis
├─ Cluster identification
├─ Exchange interaction mapping
└─ Temporal behavior analysis

Tier 3: Entity Level
├─ KYC correlation (where available)
├─ Social media attribution
├─ Infrastructure fingerprinting
└─ Device/link analysis

Tier 4: Network Level
├─ Syndicate identification
├─ Money laundering pathways
├─ Cross-chain bridging analysis
└─ Mixer/tumbler detection

Tier 5: Geographic Level (Munch Maps Integration)
├─ IP geolocation
├─ Timezone analysis
├─ Regional scam pattern matching
└─ Jurisdiction mapping
```

### 6.5 Evidence Processing Pipeline (V2)

#### Async Architecture
```
Upload → Validation → Queue → Processing → Storage → Notification

Worker Pool:
- 8 workers for document analysis (OCR)
- 4 workers for image forensics
- 4 workers for video processing
- 2 workers for blockchain tracing

Monitoring:
- Dead letter queue for failures
- Automatic retry (3 attempts)
- Manual review queue for edge cases
```

#### Chain of Custody
```python
class ChainOfCustody:
    """
    Immutable audit trail for all evidence
    """
    entries: List[CustodyEntry]
    
    def transfer(self, from_user, to_user, reason):
        entry = CustodyEntry(
            timestamp=utc_now(),
            from_party=from_user,
            to_party=to_user,
            reason=reason,
            hash=self.compute_hash()
        )
        self.entries.append(entry)
        self.audit_log.write(entry)  # Append-only log
```

---

## 7. N8N AUTOMATION INFRASTRUCTURE

### 7.1 Workflow Architecture
```
Server: 167.86.116.51:5678
Database: /root/.n8n/database.sqlite
Backups: /root/rmi/backups/n8n/ (Daily at 3 AM)
```

### 7.2 Active Workflows (5 Core)

#### 1. Scan Results → Community Channel
```
Trigger: POST /webhook/scan-result
Destination: @munchscans (Telegram)
Format: Markdown with risk visualization
Features:
- Auto-threading for discussion
- Risk score color coding
- Direct link to web report
```

#### 2. Backend Health Monitor
```
Trigger: POST /webhook/backend-alert
Destination: @rmi_backend (Private)
Severity Levels:
├─ INFO: Routine operations
├─ WARNING: Performance degradation
├─ CRITICAL: Service outage
└─ SECURITY: Intrusion detection
```

#### 3. Whale Alert System
```
Trigger: POST /webhook/whale-alert
Destination: @rmi_alpha_alerts (Public)
Criteria:
├─ Transfer > $100K USD equivalent
├─ Exchange inflow/outflow
└─ Unusual pattern detection
```

#### 4. Scam Alert System
```
Trigger: POST /webhook/scam-alert
Destination: @rmi_alpha_alerts (Public)
Criteria:
├─ New honeypot detected
├─ Liquidity drain detected
├─ Contract upgrade to malicious
└─ Social engineering campaign
```

#### 5. Daily Intelligence Report
```
Schedule: Daily at 9:00 AM UTC
Format: PDF + Telegram summary
Contents:
├─ New scams detected (24h)
├─ Active investigation updates
├─ Community highlights
├─ Whale movement summary
└─ AI-generated risk forecast
```

### 7.3 Telegram Bot Fleet

| Bot | Username | Purpose | Channel |
|-----|----------|---------|---------|
| Rug Munch | @rugmunchbot | Contract analysis | @munchscans |
| Backend | @rmi_backend_bot | System alerts | @rmi_backend |
| Alerts | @rmi_alerts_bot | FREE tier intel | @rmi_alerts |
| Alpha | @rmi_alpha_bot | PAID tier intel | @rmi_alpha_alerts |

### 7.4 Monitoring Scripts
```bash
# Health Check (Every 5 minutes)
/root/rmi/backend/n8n/monitor-n8n.sh

# Backup (Daily at 3 AM)
/root/rmi/backend/n8n/backup-n8n.sh

# Status Dashboard
/root/rmi/backend/n8n/status.sh

# Emergency Repair
/root/rmi/backend/n8n/emergency-repair.sh
```

---

## 8. AI & OSINT CAPABILITIES

### 8.1 AI Router System
```
Providers: 23 integrated
Free Credits: $3,400+ available
Routing Logic:
├─ Cost optimization
├─ Capability matching
└─ Failover handling

Providers Include:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Local models (Llama, Mistral)
```

### 8.2 AI Applications

#### Contract Analysis
```
Input: Solidity bytecode + metadata
Output: Natural language risk summary
Model: GPT-4 with custom fine-tuning
Use Case: Explaining technical findings to non-technical users
```

#### Social Media Analysis
```
Input: Telegram/Discord/Twitter text
Output: Sentiment + scam probability
Model: Fine-tuned BERT variant
Training Data: 50K+ labeled scam messages
```

#### Investigation Assistant
```
Input: Case context + evidence
Output: Lead suggestions, timeline gaps
Model: Claude with investigation prompt engineering
Features:
- Suggests follow-up evidence
- Identifies timeline inconsistencies
- Recommends similar case patterns
```

### 8.3 OSINT Tools

#### Face Recognition
```
Purpose: Identify scammers across platforms
Sources: Dating sites, social media, KYC leaks
Tech: OpenCV + dlib + custom neural network
Privacy: Hash-based matching, no raw storage
```

#### Dating Site Search
```
Purpose: Find scammer profiles on dating platforms
Method: Username correlation, image reverse search
Platforms: 50+ sites indexed
Alert System: New match → Investigation notification
```

#### Scammer Identification Engine
```
Correlation Methods:
├─ Username similarity (Levenshtein distance)
├─ Writing style analysis (stylometry)
├─ Wallet cluster intersection
├─ Timezone/activity pattern matching
└─ Device fingerprint correlation

Output: Confidence score + evidence links
```

---

## 9. MONETIZATION STRUCTURE

### 9.1 Tier System

| Tier | Price | Features |
|------|-------|----------|
| **FREE** | $0 | 5 scans/day, community access, basic alerts |
| **PRO** | $19.99/mo | Unlimited scans, advanced analytics, priority API |
| **ELITE** | $49.99/mo | Real-time alerts, OSINT tools, investigation dashboard |
| **ENTERPRISE** | Custom | API access, white-label, dedicated support, custom integrations |

### 9.2 Revenue Streams
```
1. Subscription Revenue (Primary)
   - Monthly/Annual plans
   - 20% discount for annual
   
2. API Usage (Secondary)
   - Pay-per-scan for non-subscribers
   - Bulk pricing for researchers
   
3. Data Licensing (Future)
   - Anonymized scam database
   - Academic/law enforcement partnerships
   
4. Investigation Services (Enterprise)
   - Professional investigation team
   - Asset recovery assistance
   - Expert witness services
```

### 9.3 Token Utility (RUG Token - Future)
```
Planned Utilities:
- Staking for tier upgrades
- Payment for premium features
- Governance voting
- Tip system for quality contributors
- Reward for confirmed scam reports
```

---

## 10. SECURITY & FORENSIC STANDARDS

### 10.1 Evidence Handling
```
Chain of Custody Requirements:
1. Immutable audit log
2. Hash verification at each step
3. Access control (RBAC)
4. Encryption at rest and in transit
5. 90-day minimum retention
6. Legal hold capability
```

### 10.2 Data Protection
```
PII Handling:
- Encryption: AES-256
- Key Management: HashiCorp Vault
- Access: Need-to-know basis
- Retention: GDPR-compliant deletion

Blockchain Privacy:
- Wallet clustering internally only
- No public attribution without evidence
- Differential privacy for analytics
```

### 10.3 Vulnerability Disclosure
```
Program: HackerOne integration
Scope: All public-facing assets
Rewards: Up to $10,000 for critical findings
Response SLA: 24 hours acknowledgment
Resolution: 30 days for critical
```

---

## 11. DEVELOPMENT ROADMAP

### Phase 1: Foundation (Completed 2026-04)
```
✅ N8N automation infrastructure
✅ Telegram bot fleet (4 bots)
✅ Backend API structure (24 modules)
✅ Database consolidation
✅ The Trenches community platform
✅ Monitoring and backup systems
```

### Phase 2: V2 CRM Relaunch (Q2 2026)
```
🔲 Evidence processing pipeline
🔲 Investigation workflow (5-tier)
🔲 Case management dashboard
🔲 Timeline reconstruction
🔲 Report generation system
🔲 Munch Maps integration
```

### Phase 3: Mobile & Extension (Q3 2026)
```
🔲 iOS/Android apps
🔲 Chrome extension (contract warnings)
🔲 Telegram mini-app
🔲 Discord bot integration
```

### Phase 4: Scale & Enterprise (Q4 2026)
```
🔲 Enterprise API v2
🔲 Law enforcement portal
🔲 Academic research access
🔲 White-label solutions
```

---

## 12. INTEGRATION POINTS

### 12.1 API Authentication
```
Methods:
1. API Key (X-API-Key header)
2. JWT Bearer (Authorization header)
3. OAuth 2.0 (Third-party integrations)

Rate Limits:
- Free: 100 req/hour
- PRO: 1000 req/hour
- ELITE: 10000 req/hour
- Enterprise: Custom
```

### 12.2 Webhook Events
```
Available Events:
- scan.completed
- alert.triggered
- case.updated
- evidence.processed
- report.generated

Payload Format: JSON
Retry Policy: 3 attempts with exponential backoff
Signature: HMAC-SHA256 verification
```

### 12.3 Third-Party Integrations
```
Blockchain:
- Etherscan API
- Basescan API
- SolanaFM
- Alchemy (Web3 provider)

Social:
- Twitter API v2
- Telegram Bot API
- Discord Webhooks

OSINT:
- Shodan
- Have I Been Pwned
- MaxMind GeoIP
```

---

## 13. GLOSSARY

| Term | Definition |
|------|------------|
| **Rug Pull** | Crypto scam where developers abandon project and steal funds |
| **Honey Pot** | Contract that allows buys but blocks sells |
| **OSINT** | Open Source Intelligence - publicly available information gathering |
| **5-Tier Analysis** | Investigation framework covering contract→wallet→entity→network→geo |
| **The Trenches** | Community platform for crypto intelligence |
| **Munch Maps** | Geographic visualization of scam networks |
| **CRM V2** | Relaunched case management system |
| **N8N** | Workflow automation platform |
| **Chain of Custody** | Audit trail for evidence handling |

---

## 14. SUPPORT & CONTACT

**Technical Issues:**
- Status Page: http://167.86.116.51:5678 (N8N dashboard)
- Emergency: Run /root/rmi/backend/n8n/emergency-repair.sh
- Logs: /var/log/n8n*.log

**Documentation:**
- Quick Reference: /root/rmi/backend/n8n/QUICKREF.md
- Full Docs: /root/rmi/backend/n8n/README.md
- This Document: /root/rmi/docs/RMI_COMPLETE_PLATFORM_DOCUMENTATION.md

**API Key:**
- N8N API: n8n_api_76c463961b1964ca86d633436d0b2caf13580ec8faeff4b3ff7a39d879b07ec3
- Storage: /root/rmi/backend/n8n/.env.n8n

---

*End of Document*
*For updates, modify this file and commit to memory system*
