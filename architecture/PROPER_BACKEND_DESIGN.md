# RMI Intelligence Operations Center - Backend Architecture

**Status:** Design Document  
**Date:** 2026-04-14  
**Author:** Claude (post-n8n-hell)  
**Budget:** Cloud credits only (lean)  
**Team:** Solo  
**Vibe:** Darkroom command center, flawless graphics, intelligence agency aesthetic

---

## Philosophy

**Before (n8n):** Visual spaghetti, no version control, debugging by clicking
**After:** Code-first, event-driven, testable, observable

**Core principle for solo devs:** Modular monolith > microservices. One deployable unit, clean internal boundaries.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (Caddy/Nginx)                │
│              SSL termination, rate limiting, routing         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    RMI Core Service (FastAPI)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  REST API   │  │  WebSocket  │  │  Webhooks   │         │
│  │  (public)   │  │  (realtime) │  │  (internal) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Event Bus (Redis Streams)                   │
│         ┌─────────┬─────────┬─────────┬─────────┐            │
│         │scan.q   │alert.q  │osint.q  │trade.q  │            │
│         └─────────┴─────────┴─────────┴─────────┘            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐    ┌────────▼────────┐   ┌──────▼──────┐
│   Workers    │    │   AI Workers      │   │   Notifier  │
│  (Celery)    │    │  (GPU/CPU queue)  │   │  (Telegram) │
│              │    │                   │   │             │
│ • Scanner    │    │ • Face recog      │   │ • Channels  │
│ • Indexer    │    │ • Dating search     │   │ • Users     │
│ • OSINT      │    │ • Risk scoring      │   │ • Alerts    │
└──────────────┘    └─────────────────────┘   └─────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ PostgreSQL   │  │   Redis      │  │   S3/MinIO   │       │
│  │ (primary)    │  │  (cache/q)   │  │  (files)     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 0. Intelligence Operations Center (Dashboard UI)

**Purpose:** Real-time command center for monitoring RMI platform, revenue, systems, and intelligence operations.

**Stack:**
- React + TypeScript + Vite
- Recharts / D3.js for visualizations
- WebSocket for real-time updates
- Tailwind CSS (dark theme)
- Grid layout (responsive but desktop-first for ops center)

**Dashboard Layout (Darkroom Aesthetic):**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│  RMI INTELLIGENCE OPERATIONS CENTER                    [Live] [System: OK] │
├──────────────────┬──────────────────┬──────────────────┬───────────────────────┤
│  REVENUE DASH    │  SYSTEM HEALTH   │  ACTIVE SCANS    │   THREAT RADAR     │
│  ┌────────────┐  │  ┌────────────┐  │  ┌────────────┐  │  ┌────────────┐    │
│  │  $24,592   │  │  ● API 99.9%│  │  ████████░░  │  │     ⚡       │    │
│  │  +12% day  │  │  ● DB  OK   │  │  847/min     │  │   ACTIVE     │    │
│  │  ━━━━━━━━  │  │  ● Q  12ms  │  │  ▲ 23%     │  │   THREATS    │    │
│  │  MRR Graph │  │  ● Workers 8│  │  └────────────┘  │     23       │    │
│  └────────────┘  │  └────────────┘  │                   └────────────┘    │
├──────────────────┴──────────────────┴──────────────────┴────────────────────┤
│  INTELLIGENCE FEED (Real-time)                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ [14:32:01] Whale alert: 0x7a...9b2 moved 2.4M USDC → SUSPECT_TOKEN   │    │
│  │ [14:31:45] New scan complete: 0x3d...e1f (RISK: 87/100)            │    │
│  │ [14:31:22] OSINT hit: Face match 94% on dating profile              │    │
│  │ [14:30:58] The Trenches: New trader joined (karma: 1,247)           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│  BLOCKCHAIN PULSE│  BOT FLEET STATUS│  QUEUE DEPTH     │  AI WORKLOAD       │
│  ┌────────────┐  │  ┌────────────┐  │  ┌────────────┐  │  ┌────────────┐    │
│  │ ETH ▓▓▓░░░ │  │  🤖 RugMunch│  │  scan:  12   │  │  GPU:  67%   │    │
│  │ BSC ▓▓▓▓░░ │  │  🤖 Alpha   │  │  alert:  3   │  │  CPU:  34%   │    │
│  │ SOL ▓▓▓▓▓░ │  │  🤖 Intel   │  │  osint:  7   │  │  Queue: 23   │    │
│  │ BASE▓▓░░░░ │  │  🤖 Backend │  │  ─────────── │  │  ▲ 2.3/min   │    │
│  │            │  │  All Online │  │  Total:  22   │  │              │    │
│  └────────────┘  │  └────────────┘  │  └────────────┘  │  └────────────┘    │
├──────────────────┴──────────────────┴──────────────────┴────────────────────┤
│  REVENUE BREAKDOWN                    │  TOP PERFORMING TOKENS (24h)         │
│  ┌────────────────────────────────┐   │  ┌────────────────────────────────┐ │
│  │ FREE:  12,402 users            │   │  1. PEPE ........ $2.4M vol       │ │
│  │ PRO:      847 users ($8,470)   │   │  2. BONK ........ $1.8M vol       │ │
│  │ ELITE:    123 users ($12,300)  │   │  3. MOG ......... $1.2M vol       │ │
│  │ ENTERPRISE: 4 ($3,200)         │   │  4. WIF ......... $980K vol       │ │
│  │ ─────────────────────────      │   │  5. FLOKI ....... $842K vol       │ │
│  │ ARR: $294,840 | MRR: $24,570   │   │                                    │ │
│  └────────────────────────────────┘   │  └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Dashboard Features:**

1. **Revenue Command Center**
   - Real-time MRR/ARR tracking
   - Tier breakdown visualization (Free/Pro/Elite/Enterprise)
   - Churn rate, LTV, CAC metrics
   - Stripe integration for payment status
   - RUG token economics (if applicable)

2. **System Health Monitor**
   - API response times (p50, p95, p99)
   - Database connection pool status
   - Redis memory usage
   - Worker queue depths (with alerts)
   - Error rates by service
   - Uptime percentage (SLA tracking)

3. **Intelligence Operations**
   - Live scan throughput (contracts/minute)
   - Active investigations counter
   - OSINT provider status (23 providers health)
   - Threat radar (active scams being tracked)
   - Face recognition queue
   - Evidence chain of custody status

4. **Blockchain Pulse**
   - Chain sync status (ETH, BSC, SOL, BASE)
   - Block height per chain
   - Indexer lag detection
   - RPC endpoint health
   - Whale alert frequency

5. **Bot Fleet Status**
   - All 4 Telegram bot health
   - Message delivery rates
   - Webhook latency
   - Command usage stats
   - Channel growth metrics

6. **The Trenches Monitor**
   - Active traders online
   - Karma distribution
   - Badge unlock rate
   - Trade signal performance
   - Community sentiment

**Data Sources:**
```
Dashboard queries:
  - Metrics API (aggregated stats)
  - WebSocket stream (real-time events)
  - Prometheus metrics (system health)
  - Stripe API (revenue data)
  - Database (entity counts)
```

---

### 1. API Layer (FastAPI)

**Why FastAPI:**
- Native async (critical for Web3 I/O)
- Auto-generated OpenAPI docs
- Pydantic validation (catches bugs early)
- Python ecosystem (AI/ML libraries)

**Structure:**
```
rmi/api/
├── main.py                 # App factory, middleware
├── routes/
│   ├── scans.py            # Contract scanning endpoints
│   ├── investigations.py   # OSINT/CRM operations
│   ├── trenches.py         # Retail platform API
│   ├── webhooks.py         # External service callbacks
│   └── admin.py            # Internal ops
├── services/               # Business logic layer
├── models/                 # Pydantic schemas
└── dependencies.py         # Auth, rate limiting, etc.
```

**Key Endpoints:**
```
# Public
POST   /api/v2/scans                 # Submit contract for analysis
GET    /api/v2/scans/{id}            # Get scan results
POST   /api/v2/investigations        # Create OSINT investigation

# Webhook receivers (replacing n8n)
POST   /webhooks/chainscan/{event}   # Blockchain events
POST   /webhooks/dexscreener         # Token listing alerts
POST   /webhooks/openai              # AI completion callbacks

# Internal (service-to-service)
POST   /internal/notify              # Queue notification
POST   /internal/enqueue             # Queue background job
```

### 2. Event Bus (Redis Streams)

**Why Redis Streams:**
- Already using Redis (cache/credits)
- No new infrastructure cost
- Persistent streams (not lost on restart)
- Consumer groups for worker scaling

**Stream Design:**
```
stream:scan:new          → New contract submitted
stream:scan:complete     → Analysis finished
stream:alert:whale         → Whale movement detected
stream:alert:scam          → Scam pattern detected
stream:osint:request       → OSINT investigation queued
stream:osint:result        → OSINT data returned
stream:notify:telegram     → Telegram notification queued
stream:notify:discord      # Future expansion
stream:trade:signal        # The Trenches signals
stream:indexer:block       → New blockchain block
```

**Event Schema (JSON):**
```json
{
  "event_id": "uuid",
  "timestamp": "2026-04-14T12:00:00Z",
  "type": "scan:complete",
  "payload": { ... },
  "trace_id": "uuid-for-tracing",
  "retry_count": 0
}
```

### 3. Worker Layer (Celery + AsyncIO)

**Why Celery:**
- Mature, well-documented
- Redis broker (reuse existing)
- Task retries, acks_late, dead letter queues
- Flower UI for monitoring

**Worker Categories:**

**CPU Workers (4-8 processes):**
- Contract bytecode analysis
- Risk scoring algorithms
- Data normalization

**I/O Workers (async, 20+ coroutines):**
- Blockchain RPC calls
- Telegram API calls
- External API requests (DEXScreener, etc.)

**GPU Workers (separate queue, optional):**
- Face recognition
- Image analysis
- AI model inference

**Task Definitions:**
```python
# rmi/tasks/scans.py
@app.task(bind=True, max_retries=3)
def analyze_contract(self, contract_address: str, chain: str):
    """Deep contract analysis pipeline"""
    try:
        # 1. Fetch bytecode
        bytecode = fetch_bytecode(contract_address, chain)
        
        # 2. Static analysis
        risks = static_analysis(bytecode)
        
        # 3. Simulated transactions
        simulation = simulate_trades(contract_address, chain)
        
        # 4. Score and store
        result = score_and_save(risks, simulation)
        
        # 5. Emit completion event
        redis.xadd("stream:scan:complete", result.to_dict())
        
        return result.id
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

# rmi/tasks/notifications.py
@app.task
def send_telegram_alert(channel: str, message: dict, priority: str = "normal"):
    """Send alert to appropriate Telegram channel"""
    bot_token = get_bot_for_channel(channel)
    
    if priority == "critical":
        send_immediately(bot_token, message)
    else:
        batch_and_send(bot_token, message)
```

### 4. Data Layer

**PostgreSQL Schema (clean):**

```sql
-- Core entities
contracts (id, address, chain, bytecode_hash, created_at, updated_at)
scans (id, contract_id, status, score, report_json, started_at, completed_at)
investigations (id, type, target, status, results_json, created_by)
evidence (id, investigation_id, source, data_hash, chain_of_custody)
users (id, telegram_id, tier, joined_at, last_active)
alerts (id, user_id, type, payload, sent_at, delivered)

-- Blockchain data
transactions (hash, block_number, from_addr, to_addr, value, token_transfers_json)
token_transfers (tx_hash, token_address, from_addr, to_addr, amount, timestamp)
holders (token_address, wallet_address, balance, snapshot_at)

-- The Trenches
traders (wallet_address, karma_score, badges_json, created_at)
trades (id, trader_id, token_in, token_out, amount, profit_loss, timestamp)
```

**Redis Usage:**
- Streams (event bus)
- Cache (hot contract data, user sessions)
- Rate limiting counters
- Distributed locks (prevent duplicate scans)

**S3/MinIO (object storage):**
- Contract bytecode archives
- OSINT evidence files
- Investigation exports
- ML model weights

### 5. Telegram Bot Layer

**Architecture:**
```
rmi/bots/
├── base.py           # Shared bot framework
├── rugmunch.py       # @rugmunchbot - main interface
├── notifier.py       # Alert posting service
└── commands/
    ├── scan.py       # /scan command handler
    ├── investigate.py # /investigate handler
    └── admin.py      # Admin commands
```

**Bot Framework:**
```python
class RMITelegramBot:
    """Base class for all RMI bots"""
    
    def __init__(self, token: str, name: str):
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.name = name
        
    async def handle_webhook(self, update: dict):
        """Process incoming webhook"""
        telegram_update = Update.model_validate(update)
        await self.dp.feed_update(self.bot, telegram_update)
        
    async def send_alert(self, channel_id: str, message: AlertMessage):
        """Send alert to channel"""
        # Format based on alert type
        formatted = self.formatter.render(message)
        await self.bot.send_message(channel_id, **formatted)
```

---

## Data Flow Examples

### 1. New Contract Scan

```
User submits contract
        ↓
POST /api/v2/scans
        ↓
API validates, creates scan record (PENDING)
        ↓
Push to stream:scan:new
        ↓
Worker picks up task
        ↓
Parallel analysis:
  - Bytecode decompilation
  - Historical tx analysis  
  - Holder distribution
  - Similar contract check
        ↓
Store results, update scan record (COMPLETE)
        ↓
Emit stream:scan:complete
        ↓
Notifier worker → Telegram channels
        ↓
User receives result (push or poll)
```

### 2. Whale Alert

```
Blockchain indexer detects large transfer
        ↓
POST /webhooks/chainscan/transfer
        ↓
API validates, checks thresholds
        ↓
Push to stream:alert:whale
        ↓
Notifier worker:
  - Fetch token metadata
  - Format alert message
  - Route to appropriate channels
        ↓
Telegram bots post to @rmi_alpha_alerts
```

### 3. OSINT Investigation

```
User: /investigate @suspect_wallet
        ↓
Telegram bot receives command
        ↓
POST /api/v2/investigations (async)
        ↓
API creates investigation, returns ID
        ↓
Push to stream:osint:request
        ↓
OSINT worker runs 23 provider checks
        ↓
Each result → stream:osint:result
        ↓
Aggregator worker builds report
        ↓
Update investigation record
        ↓
Notify user via Telegram DM
```

---

## Infrastructure (Cloud Credits)

### Deployment Options

**Option A: Single Hetzner/Vultr instance ($20-40/month)**
- 4-8 vCPU, 16-32GB RAM
- Run everything on one box
- Docker Compose orchestration
- Good for MVP, easy to manage

**Option B: Kubernetes (use cloud credits)**
- GKE/EKS/AKS free tier + credits
- Proper separation of concerns
- Auto-scaling workers
- Overkill for solo dev? Maybe.

**Recommendation:** Start with Option A, migrate to K8s when you have a team.

### Docker Compose (local/dev)

```yaml
version: '3.8'
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://rmi:xxx@postgres/rmi
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  worker-cpu:
    build: ./api
    command: celery -A rmi.tasks worker -Q cpu -c 4
    deploy:
      replicas: 2

  worker-io:
    build: ./api
    command: celery -A rmi.tasks worker -Q io -P eventlet -c 20
    deploy:
      replicas: 2

  notifier:
    build: ./api
    command: celery -A rmi.tasks worker -Q notify -c 2

  scheduler:
    build: ./api
    command: celery -A rmi.tasks beat

  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  caddy:
    image: caddy:2
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
```

### Directory Structure

```
/root/rmi/v2/                    # New clean structure
├── api/                        # FastAPI application
│   ├── rmi/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py           # Pydantic settings
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   ├── tasks/              # Celery tasks
│   │   └── dependencies/
│   ├── Dockerfile
│   └── requirements.txt
├── bots/                       # Telegram bots
│   ├── rmi_bots/
│   ├── Dockerfile
│   └── requirements.txt
├── indexer/                    # Blockchain indexer (separate service)
│   ├── src/
│   └── Dockerfile
├── migrations/                 # Alembic database migrations
├── tests/                      # Test suite
├── scripts/                    # Operational scripts
├── docker-compose.yml
├── k8s/                        # Kubernetes manifests (future)
└── docs/
```

---

## Monitoring & Observability

**Logs:**
- Structured JSON logging (structured-logging library)
- Centralized with Loki or CloudWatch
- Trace IDs propagate through all services

**Metrics:**
- Prometheus + Grafana (free)
- Key metrics:
  - API request rate/latency/errors
  - Queue depths (stream lengths)
  - Worker processing rate
  - Contract scan throughput
  - Telegram delivery rate

**Alerting:**
- Grafana alerts or PagerDuty free tier
- Critical: Queue backing up, workers dead, DB down

**Health Checks:**
```python
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": VERSION,
        "checks": {
            "postgres": await check_postgres(),
            "redis": await check_redis(),
            "workers": await check_celery()
        }
    }
```

---

## Self-Healing Automation Layer

### Purpose
The system must operate autonomously: self-heal from failures, auto-update threat intelligence, maintain itself, and protect critical data. This is achieved through a hybrid approach: **n8n for visual automation + Supabase for data-driven triggers + Code for complex logic**.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATION & SELF-HEALING LAYER                       │
├─────────────────────┬─────────────────────┬─────────────────────────────┤
│  SUPABASE TRIGGERS  │   n8n WORKFLOWS     │   CELERY BEAT SCHEDULERS    │
│  (Data-driven)      │   (Visual auto)      │   (Code-complex)            │
├─────────────────────┼─────────────────────┼─────────────────────────────┤
│ • DB change webhooks│ • Alert routing     │ • Database cleanup          │
│ • Real-time subs    │ • Webhook bridging   │ • Threat signature updates  │
│ • Auth events       │ • Simple IF/THEN     │ • AI model retraining       │
│ • Storage events    │ • Notification flow  │ • Evidence integrity checks │
└─────────────────────┴─────────────────────┴─────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   HOOKDECK          │
                    │   (Reliable delivery)│
                    │                     │
                    │ • Queue & retry     │
                    │ • Dead letter       │
                    │ • Delivery tracking │
                    └─────────────────────┘
```

### 1. Supabase Integration

**Database Triggers → Webhooks:**
```sql
-- Example: Trigger on new high-risk scan
CREATE OR REPLACE FUNCTION notify_high_risk_scan()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.overall_score >= 85 THEN
    -- Supabase webhook will fire
    PERFORM pg_notify('high_risk_scan', json_build_object(
      'scan_id', NEW.id,
      'score', NEW.overall_score,
      'contract_id', NEW.contract_id
    )::text);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER high_risk_scan_trigger
AFTER INSERT OR UPDATE ON scans
FOR EACH ROW EXECUTE FUNCTION notify_high_risk_scan();
```

**Supabase Realtime (WebSocket subscriptions):**
- Frontend subscribes to `scans` table changes
- Instant UI updates when new scan completes
- No polling needed

**Edge Functions (if needed):**
- Lightweight serverless functions for simple transforms
- Keeps heavy logic in main API

### 2. n8n Automation (Purposeful Use)

**What n8n DOES here:**
- Visual workflow editing for non-dev changes
- Quick webhook routing without code deploys
- Simple notification logic (IF alert THEN send to channel X)
- Connecting services without native integrations

**n8n Workflows:**
```
1. "Health Check Router"
   Trigger: API health endpoint poll (every 5 min)
   IF unhealthy → Send Telegram alert to @rmi_backend
   IF critical → Trigger auto-restart via SSH

2. "Revenue Alert"
   Trigger: Stripe webhook (via Supabase)
   IF new subscription → Post to @rmi_alpha_alerts
   IF churn → Post to @rmi_backend (internal)

3. "Threat Intel Updater"
   Trigger: Daily at 3 AM
   Fetch new scam patterns from 5 sources
   POST to /api/v2/admin/threat-update

4. "Database Guardian"
   Trigger: Weekly
   Run VACUUM ANALYZE
   Check table sizes
   Alert if > 10GB

5. "Document Protector"
   Trigger: Hourly
   Sync evidence to S3
   Verify checksums
   Report integrity status
```

### 3. Self-Healing Mechanisms

**Auto-Recovery:**
```python
# Celery Beat scheduled task
@app.task
def health_check_and_heal():
    """Every 5 minutes: check health, heal if needed"""
    health = check_system_health()

    if health['redis']['status'] == 'error':
        restart_redis()
        alert_admin("Redis auto-restarted")

    if health['database']['status'] == 'error':
        alert_admin("Database connection failed - manual intervention needed")

    if queue_depth('scan:new') > 100:
        scale_workers('cpu', replicas=8)
        alert_admin("Auto-scaled CPU workers due to queue backlog")
```

**Circuit Breakers:**
```python
class CircuitBreaker:
    """Prevent cascade failures"""

    def __init__(self, threshold=5, timeout=60):
        self.failures = 0
        self.threshold = threshold
        self.timeout = timeout
        self.last_failure = None
        self.state = 'closed'  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure < self.timeout:
                raise Exception("Circuit breaker is OPEN")
            self.state = 'half-open'

        try:
            result = func(*args, **kwargs)
            self.failures = 0
            self.state = 'closed'
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = 'open'
            raise
```

### 4. Auto-Learning Pipeline

**Threat Signature Updates:**
```python
@app.task
def update_threat_signatures():
    """Daily: learn from new scam patterns"""
    # 1. Fetch recent high-risk scans
    recent_scams = get_scans(score_gte=85, since='24h')

    # 2. Extract common patterns
    patterns = ml.extract_patterns(recent_scams)

    # 3. Update signature database
    for pattern in patterns:
        if pattern.confidence > 0.8:
            add_threat_signature(pattern)

    # 4. Emit event for n8n to notify team
    event_bus.publish('system:signatures_updated', {
        'new_signatures': len(patterns),
        'timestamp': now()
    })
```

**OSINT Provider Rotation:**
```python
@app.task
def optimize_osint_providers():
    """Weekly: analyze OSINT provider performance"""
    stats = analyze_provider_performance()

    # Disable slow/unreliable providers
    for provider in stats:
        if provider.success_rate < 0.5:
            disable_provider(provider.name)
            alert_admin(f"Disabled {provider.name} due to low success rate")

    # Update routing priorities
    update_provider_rankings(stats)
```

### 5. Database Maintenance & Cleanup

**Scheduled Maintenance (Celery Beat):**
```python
# tasks/maintenance.py

@app.task
def daily_cleanup():
    """Daily at 3 AM"""
    # Archive old scans (keep 90 days hot)
    archive_old_scans(days=90)

    # Purge soft-deleted records
    purge_deleted_records()

    # Update materialized views
    refresh_analytics_views()

    # Vacuum (if PostgreSQL)
    run_vacuum_analyze()

@app.task
def weekly_maintenance():
    """Weekly on Sunday"""
    # Reindex tables
    reindex_tables()

    # Check table sizes
    sizes = get_table_sizes()
    for table, size in sizes.items():
        if size > 10_000_000_000:  # 10GB
            alert_admin(f"Table {table} is {size/1GB:.1f} GB")

@app.task
def monthly_maintenance():
    """Monthly 1st"""
    # Full backup
    create_full_backup()

    # Data integrity check
    verify_checksums()

    # Generate usage report
    generate_monthly_report()
```

### 6. Document Protection & Chain of Custody

**Evidence Integrity:**
```python
@app.task
def verify_evidence_chain():
    """Hourly: verify evidence integrity"""
    evidence_items = get_all_evidence()

    for item in evidence_items:
        current_hash = calculate_hash(item.data)
        stored_hash = item.integrity_hash

        if current_hash != stored_hash:
            # CRITICAL: Evidence tampered or corrupted
            alert_admin(
                f"INTEGRITY ALERT: Evidence {item.id} hash mismatch!",
                priority='critical'
            )
            lock_investigation(item.investigation_id)

@app.task
def backup_to_s3():
    """Every 6 hours: sync to S3"""
    sync_evidence_to_s3()
    sync_contracts_to_s3()
    sync_database_backup_to_s3()

    # Verify backups
    verify_s3_backups()
```

**Chain of Custody Tracking:**
```python
def log_custody_event(evidence_id: str, action: str, user_id: str):
    """Log every touch of evidence"""
    custody_record = {
        'evidence_id': evidence_id,
        'action': action,  # 'viewed', 'exported', 'analyzed'
        'user_id': user_id,
        'timestamp': utcnow(),
        'ip_address': get_client_ip(),
        'hash_before': get_current_hash(evidence_id),
        'hash_after': calculate_hash(evidence_id)
    }

    db.insert('custody_log', custody_record)
    audit_log.info("custody_event", **custody_record)
```

---

## Migration Plan (from n8n)

### Phase 1: Dual Run (1-2 weeks)
- Build new API alongside n8n
- Write to both systems (n8n reads, new writes)
- Migrate data to PostgreSQL

### Phase 2: Cutover (1 week)
- Switch webhooks to hit new API
- n8n becomes read-only (just Telegram posting)
- New system handles all business logic

### Phase 3: Full Cut (1 week)
- Build Telegram notifier worker
- Move bot logic from n8n to code
- Shut down n8n workflows one by one

### Phase 4: Cleanup
- Remove n8n entirely
- Archive old database

---

## What This Gives You

**Before (n8n):**
- ❌ Business logic in visual nodes
- ❌ No version control for workflows
- ❌ Debugging by clicking through runs
- ❌ Hard to test
- ❌ Scaling means more n8n instances
- ❌ No code review possible

**After (this design):**
- ✅ Code in git, reviewed, tested
- ✅ Unit tests for business logic
- ✅ Structured logs, tracing, metrics
- ✅ Scale workers horizontally
- ✅ Type safety (Pydantic)
- ✅ OpenAPI docs generated
- ✅ Background jobs with retries
- ✅ Event-driven (decoupled)

---

## Next Steps

1. **Approve this design** - Any changes needed?
2. **Start with API skeleton** - FastAPI app with health endpoint
3. **Database migration** - Alembic setup, initial schema
4. **First worker** - Simple notification task
5. **Telegram webhook bridge** - Replace one n8n workflow

**Time estimate:** 2-3 weeks for full migration working solo, assuming 4-6 hours/day.

Want me to start building this? Or need adjustments to the design?
