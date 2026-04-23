# RMI Platform v3.0 - NVIDIA AI + n8n + Supabase Architecture

## Executive Summary

New architecture leveraging NVIDIA's free tier models, n8n for workflow automation, Supabase for database, and Lovable for UX.

---

## AI Model Stack (NVIDIA Free Tier)

### Primary Model: Kimi k1.6 (Lead)
**Role:** Complex analysis, reasoning, decision making

**Use Cases:**
- Token contract analysis & risk scoring
- Wallet cluster detection algorithms
- Investigation report generation
- Complex fraud pattern recognition
- Multi-step reasoning tasks

**Why Kimi k1.6:**
- Best-in-class reasoning capabilities
- 2M token context window
- Excellent at following complex instructions
- Strong at code analysis

---

### Secondary Model: Llama 3.3 70B
**Role:** Code generation, technical analysis, data processing

**Use Cases:**
- SQL query generation for n8n workflows
- API integration code
- Data transformation scripts
- Smart contract code review
- Technical documentation

**Why Llama 3.3 70B:**
- Open source (no vendor lock-in)
- Excellent code capabilities
- Large context window (128k)
- Multilingual support
- Fast inference on NVIDIA hardware

---

### Tertiary Model: Mistral Large 2
**Role:** Fast inference, content generation, summaries

**Use Cases:**
- Social media content generation
- News article summarization
- Quick token summaries
- Chat responses
- Content translation

**Why Mistral Large 2:**
- Very fast inference
- Cost-effective
- Strong multilingual capabilities
- Good at creative tasks
- 128k context window

---

## Alternative Model Options

If the above aren't available on NVIDIA free tier:

| Slot | Option A | Option B | Option C |
|------|----------|----------|----------|
| Lead | **Kimi k1.6** | Claude 3.5 Sonnet | GPT-4o |
| Code | **Llama 3.3 70B** | DeepSeek Coder V2 | CodeLlama 70B |
| Fast | **Mistral Large 2** | Qwen 2.5 72B | Mixtral 8x22B |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                      (Lovable - React/TS)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SUPABASE                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  PostgreSQL │  │   Auth      │  │    Realtime/Webhooks    │  │
│  │  Database   │  │  (JWT)      │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│      n8n        │ │  NVIDIA AI      │ │  External APIs  │
│   Workflows     │ │   Models        │ │                 │
│                 │ │                 │ │  • Birdeye      │
│  ┌───────────┐  │ │  • Kimi k1.6    │ │  • Helius       │
│  │ Triggers  │  │ │  • Llama 3.3    │ │  • Arkham       │
│  │ (DB/Web)  │  │ │  • Mistral L2   │ │  • Twitter      │
│  └───────────┘  │ │                 │ │  • Telegram     │
│                 │ │                 │ │                 │
│  ┌───────────┐  │ │                 │ │                 │
│  │  Nodes    │  │ │                 │ │                 │
│  │ • AI Code │  │ │                 │ │                 │
│  │ • SQL     │  │ │                 │ │                 │
│  │ • HTTP    │  │ │                 │ │                 │
│  │ • Logic   │  │ │                 │ │                 │
│  └───────────┘  │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## n8n Workflow Architecture

### Workflow Categories

#### 1. Data Ingestion Workflows
```
Trigger: Schedule (every 5 min)
  ↓
Node: HTTP Request (Birdeye/Helius)
  ↓
Node: AI (Llama 3.3) - Parse & Transform
  ↓
Node: PostgreSQL - Insert to Supabase
```

#### 2. Analysis Workflows
```
Trigger: New token in database
  ↓
Node: PostgreSQL - Fetch token data
  ↓
Node: AI (Kimi k1.6) - Risk Analysis
  ↓
Node: PostgreSQL - Update risk score
  ↓
Node: Webhook - Notify frontend
```

#### 3. Content Generation Workflows
```
Trigger: Schedule (daily 9am)
  ↓
Node: PostgreSQL - Get trending scams
  ↓
Node: AI (Mistral Large 2) - Write article
  ↓
Node: PostgreSQL - Save to content queue
  ↓
Node: Slack/Discord - Notify editor
```

#### 4. Social Media Workflows
```
Trigger: Approved content in queue
  ↓
Node: AI (Mistral) - Generate X thread
  ↓
Node: HTTP Request - Post to Twitter
  ↓
Node: HTTP Request - Post to Telegram
  ↓
Node: PostgreSQL - Mark as posted
```

#### 5. Alert Workflows
```
Trigger: Risk score > 70
  ↓
Node: PostgreSQL - Get watchlist users
  ↓
Node: SendGrid - Email alerts
  ↓
Node: FCM - Push notifications
  ↓
Node: PostgreSQL - Log alerts
```

---

## Database Schema (Supabase)

### Core Tables

```sql
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    wallet_address TEXT UNIQUE,
    display_name TEXT,
    avatar_url TEXT,
    is_crm_holder BOOLEAN DEFAULT FALSE,
    crm_balance NUMERIC(20, 9) DEFAULT 0,
    subscription_tier TEXT DEFAULT 'free',
    scans_remaining INTEGER DEFAULT 5,
    total_scans_used INTEGER DEFAULT 0,
    notification_settings JSONB DEFAULT '{
        "email": true,
        "push": true,
        "risk_alerts": true,
        "price_alerts": false
    }',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TOKENS & ANALYSIS
-- ============================================
CREATE TABLE tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT NOT NULL,
    chain TEXT DEFAULT 'solana',
    symbol TEXT,
    name TEXT,
    decimals INTEGER,
    
    -- Risk Analysis
    risk_score INTEGER,
    risk_level TEXT,
    risk_factors JSONB DEFAULT '[]',
    
    -- Contract Info
    mint_authority TEXT,
    freeze_authority TEXT,
    supply_info JSONB,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_analyzed_at TIMESTAMPTZ,
    analyze_count INTEGER DEFAULT 0,
    
    UNIQUE(address, chain)
);

-- Token analysis history
CREATE TABLE token_analysis_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_id UUID REFERENCES tokens(id) ON DELETE CASCADE,
    risk_score INTEGER,
    risk_level TEXT,
    analysis_data JSONB,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- WALLETS & CLUSTERING
-- ============================================
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT NOT NULL UNIQUE,
    chain TEXT DEFAULT 'solana',
    
    -- Risk
    risk_score INTEGER,
    risk_level TEXT,
    tags TEXT[] DEFAULT '{}',
    
    -- Behavior
    transaction_count INTEGER DEFAULT 0,
    first_seen_at TIMESTAMPTZ,
    last_active_at TIMESTAMPTZ,
    
    -- Clustering
    cluster_id UUID,
    behavioral_profile JSONB,
    
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wallet clusters
CREATE TABLE wallet_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cluster_name TEXT,
    cluster_type TEXT,
    confidence_score NUMERIC(5, 2),
    wallets TEXT[] DEFAULT '{}',
    detection_methods TEXT[] DEFAULT '{}',
    behavioral_patterns JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INVESTIGATIONS
-- ============================================
CREATE TABLE investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    
    -- Related entities
    token_id UUID REFERENCES tokens(id),
    wallet_ids UUID[] DEFAULT '{}',
    
    -- Risk
    risk_level TEXT DEFAULT 'unknown',
    risk_score INTEGER,
    
    -- Content
    findings JSONB DEFAULT '{}',
    evidence_ids UUID[] DEFAULT '{}',
    
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================
-- EVIDENCE
-- ============================================
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    
    evidence_type TEXT NOT NULL,
    title TEXT,
    description TEXT,
    
    -- Storage
    storage_path TEXT,
    content_hash TEXT,
    
    -- AI Analysis
    extracted_text TEXT,
    ai_summary TEXT,
    ai_metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- CONTENT MANAGEMENT (Scam Library)
-- ============================================
CREATE TABLE content_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    
    -- Categorization
    content_type TEXT NOT NULL,
    category TEXT,
    tags TEXT[] DEFAULT '{}',
    difficulty_level TEXT DEFAULT 'beginner',
    
    -- Status
    status TEXT DEFAULT 'draft',
    author_id TEXT DEFAULT 'ai',
    editor_id UUID REFERENCES profiles(id),
    
    -- Publishing
    published_at TIMESTAMPTZ,
    scheduled_for TIMESTAMPTZ,
    
    -- Stats
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    
    -- SEO
    meta_title TEXT,
    meta_description TEXT,
    keywords TEXT[] DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content revisions
CREATE TABLE content_revisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID REFERENCES content_articles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    revision_notes TEXT,
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- NEWS AGGREGATOR
-- ============================================
CREATE TABLE news_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    title TEXT NOT NULL,
    content TEXT,
    source TEXT NOT NULL,
    source_url TEXT,
    
    -- Categorization
    category TEXT,
    risk_level TEXT,
    
    -- Entities
    affected_tokens TEXT[] DEFAULT '{}',
    affected_chains TEXT[] DEFAULT '{}',
    
    -- Financial
    estimated_loss_usd NUMERIC(20, 2),
    
    -- AI Analysis
    ai_summary TEXT,
    key_takeaways TEXT[] DEFAULT '{}',
    
    -- Status
    is_posted BOOLEAN DEFAULT FALSE,
    posted_to TEXT[] DEFAULT '{}',
    
    published_at TIMESTAMPTZ,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- KOL TRACKING
-- ============================================
CREATE TABLE kol_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    handle TEXT UNIQUE NOT NULL,
    platform TEXT NOT NULL,
    display_name TEXT,
    bio TEXT,
    follower_count INTEGER,
    
    -- Metrics
    reputation_score INTEGER DEFAULT 50,
    accuracy_score NUMERIC(5, 2),
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    
    -- Wallets
    verified_wallets TEXT[] DEFAULT '{}',
    
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- KOL calls
CREATE TABLE kol_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kol_id UUID REFERENCES kol_profiles(id) ON DELETE CASCADE,
    
    token_address TEXT NOT NULL,
    token_symbol TEXT,
    call_type TEXT NOT NULL,
    
    platform TEXT,
    post_url TEXT,
    
    timestamp TIMESTAMPTZ NOT NULL,
    price_at_call NUMERIC(20, 9),
    
    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    wallet_activity_match BOOLEAN,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- USER WATCHLIST
-- ============================================
CREATE TABLE watchlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    token_id UUID REFERENCES tokens(id) ON DELETE CASCADE,
    
    -- Alert settings
    alert_on_risk_change BOOLEAN DEFAULT TRUE,
    alert_on_price_change BOOLEAN DEFAULT FALSE,
    price_change_threshold NUMERIC(5, 2) DEFAULT 10,
    
    added_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, token_id)
);

-- ============================================
-- NOTIFICATIONS
-- ============================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    notification_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    
    data JSONB DEFAULT '{}',
    
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- API CREDITS & PAYMENTS
-- ============================================
CREATE TABLE api_credit_purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    provider TEXT NOT NULL,
    credits_purchased INTEGER NOT NULL,
    credits_remaining INTEGER NOT NULL,
    
    amount_paid NUMERIC(10, 2),
    currency TEXT DEFAULT 'USDC',
    transaction_signature TEXT,
    
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    provider TEXT NOT NULL,
    endpoint TEXT,
    credits_used INTEGER DEFAULT 1,
    
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_tokens_address ON tokens(address);
CREATE INDEX idx_tokens_risk_score ON tokens(risk_score);
CREATE INDEX idx_tokens_last_analyzed ON tokens(last_analyzed_at);

CREATE INDEX idx_wallets_address ON wallets(address);
CREATE INDEX idx_wallets_cluster ON wallets(cluster_id);

CREATE INDEX idx_investigations_user ON investigations(user_id);
CREATE INDEX idx_investigations_status ON investigations(status);

CREATE INDEX idx_content_status ON content_articles(status);
CREATE INDEX idx_content_type ON content_articles(content_type);

CREATE INDEX idx_news_category ON news_items(category);
CREATE INDEX idx_news_posted ON news_items(is_posted);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- ============================================
-- RLS POLICIES
-- ============================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigations ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can view own investigations"
    ON investigations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can CRUD own watchlist"
    ON watchlist_items FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own notifications"
    ON notifications FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================
-- FUNCTIONS
-- ============================================
-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tokens_updated_at
    BEFORE UPDATE ON tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- New user trigger
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (id, wallet_address)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'wallet_address');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

---

## n8n Installation & Setup

### Option 1: Docker (Recommended)

```bash
# Create n8n directory
mkdir -p ~/n8n && cd ~/n8n

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-secure-password
      - N8N_HOST=n8n.yourdomain.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.yourdomain.com/
      - GENERIC_TIMEZONE=UTC
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=db
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n-password
    volumes:
      - ~/.n8n:/home/node/.n8n
    depends_on:
      - db
    networks:
      - n8n-network

  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n-password
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - n8n-network

volumes:
  postgres_data:

networks:
  n8n-network:
    driver: bridge
EOF

# Start n8n
docker-compose up -d

# Access at http://localhost:5678
```

### Option 2: Railway/Render (Cloud)

1. Fork n8n template on Railway
2. Add PostgreSQL addon
3. Deploy
4. Configure environment variables

---

## n8n → Supabase Integration

### Custom Supabase Node for n8n

Create a custom n8n node for easy Supabase operations:

```javascript
// supabase.node.js
const { NodeOperationError } = require('n8n-workflow');

class SupabaseNode {
    constructor() {
        this.description = {
            displayName: 'Supabase',
            name: 'supabase',
            icon: 'file:supabase.svg',
            group: ['database'],
            version: 1,
            description: 'Interact with Supabase database',
            defaults: {
                name: 'Supabase',
            },
            inputs: ['main'],
            outputs: ['main'],
            credentials: [
                {
                    name: 'supabaseApi',
                    required: true,
                },
            ],
            properties: [
                {
                    displayName: 'Operation',
                    name: 'operation',
                    type: 'options',
                    options: [
                        { name: 'Select', value: 'select' },
                        { name: 'Insert', value: 'insert' },
                        { name: 'Update', value: 'update' },
                        { name: 'Delete', value: 'delete' },
                        { name: 'Upsert', value: 'upsert' },
                    ],
                    default: 'select',
                },
                {
                    displayName: 'Table',
                    name: 'table',
                    type: 'string',
                    default: '',
                    placeholder: 'tokens',
                },
                {
                    displayName: 'Data',
                    name: 'data',
                    type: 'json',
                    default: '{}',
                    displayOptions: {
                        show: {
                            operation: ['insert', 'update', 'upsert'],
                        },
                    },
                },
                {
                    displayName: 'Filters',
                    name: 'filters',
                    type: 'json',
                    default: '{}',
                    placeholder: '{"risk_score": {"gt": 70}}',
                },
            ],
        };
    }

    async execute() {
        const credentials = await this.getCredentials('supabaseApi');
        const { supabaseUrl, supabaseKey } = credentials;
        
        const operation = this.getNodeParameter('operation', 0);
        const table = this.getNodeParameter('table', 0);
        
        const { createClient } = require('@supabase/supabase-js');
        const supabase = createClient(supabaseUrl, supabaseKey);
        
        let result;
        
        switch (operation) {
            case 'select':
                const filters = this.getNodeParameter('filters', 0);
                let query = supabase.from(table).select('*');
                // Apply filters
                Object.entries(filters).forEach(([key, value]) => {
                    if (typeof value === 'object') {
                        if (value.gt) query = query.gt(key, value.gt);
                        if (value.lt) query = query.lt(key, value.lt);
                        if (value.eq) query = query.eq(key, value.eq);
                    } else {
                        query = query.eq(key, value);
                    }
                });
                result = await query;
                break;
                
            case 'insert':
                const insertData = this.getNodeParameter('data', 0);
                result = await supabase.from(table).insert(insertData);
                break;
                
            case 'update':
                const updateData = this.getNodeParameter('data', 0);
                result = await supabase.from(table).update(updateData);
                break;
                
            case 'upsert':
                const upsertData = this.getNodeParameter('data', 0);
                result = await supabase.from(table).upsert(upsertData);
                break;
                
            case 'delete':
                result = await supabase.from(table).delete();
                break;
        }
        
        if (result.error) {
            throw new NodeOperationError(this.getNode(), result.error.message);
        }
        
        return [this.helpers.returnJsonArray(result.data)];
    }
}

module.exports = { SupabaseNode };
```

---

## Lovable UX Integration

### Design Tokens for Lovable

```css
/* Colors */
--rmi-primary: #00d4ff;
--rmi-primary-dark: #0099cc;
--rmi-bg-dark: #0f172a;
--rmi-bg-card: #1e293b;
--rmi-border: #334155;
--rmi-text: #e2e8f0;
--rmi-text-muted: #94a3b8;

/* Risk Colors */
--rmi-critical: #ef4444;
--rmi-high: #f97316;
--rmi-medium: #eab308;
--rmi-low: #22c55e;
--rmi-safe: #10b981;

/* Typography */
--rmi-font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--rmi-font-mono: 'JetBrains Mono', monospace;
```

### Supabase Connection in Lovable

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)

// Realtime subscriptions
export const subscribeToToken = (tokenId: string, callback: (payload: any) => void) => {
  return supabase
    .channel(`token-${tokenId}`)
    .on('postgres_changes', 
      { event: 'UPDATE', schema: 'public', table: 'tokens', filter: `id=eq.${tokenId}` },
      callback
    )
    .subscribe()
}
```

---

## Deployment Checklist

### 1. Supabase Setup
- [ ] Create Supabase project
- [ ] Run database schema SQL
- [ ] Set up RLS policies
- [ ] Configure auth providers
- [ ] Get API keys

### 2. n8n Setup
- [ ] Deploy n8n (Docker/Cloud)
- [ ] Install Supabase custom node
- [ ] Configure credentials
- [ ] Import workflow templates
- [ ] Test workflows

### 3. NVIDIA AI Setup
- [ ] Sign up for NVIDIA AI free tier
- [ ] Get API keys for:
  - [ ] Kimi k1.6
  - [ ] Llama 3.3 70B
  - [ ] Mistral Large 2
- [ ] Configure in n8n

### 4. Lovable Setup
- [ ] Create Lovable project
- [ ] Connect Supabase
- [ ] Import design tokens
- [ ] Build pages
- [ ] Deploy

### 5. External APIs
- [ ] Birdeye API key
- [ ] Helius API key
- [ ] Twitter/X API key
- [ ] Telegram Bot token

---

## Cost Estimation

| Service | Free Tier | Paid (Est.) |
|---------|-----------|-------------|
| NVIDIA AI | 90+ models free | ~$50-100/mo |
| Supabase | 500MB, 2M requests | ~$25/mo |
| n8n | Self-hosted free | ~$20/mo |
| Lovable | Free tier | ~$20/mo |
| External APIs | Varies | ~$100-200/mo |
| **Total** | **$0** | **~$215-365/mo** |

---

**Architecture v3.0 - Ready to Build**
