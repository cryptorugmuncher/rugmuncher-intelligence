# RMI Database Structure

Complete database layout for the RugMuncher Investigation platform.

## Overview

This document consolidates:
1. Original RugMuncher bot schema (`/root/database_schema.sql`)
2. RMI Investigation platform schema (`/root/rmi/setup_database.sql`)
3. Evidence collection structure from dumps

---

## Core Schema Comparison

| Feature | Original Bot Schema | RMI Investigation Schema |
|---------|--------------------|-------------------------|
| **Primary Key Type** | SERIAL (integer) | UUID |
| **User Tracking** | telegram_id | case-centric |
| **Evidence Storage** | File hashes + paths | Full entity extraction |
| **Wallet Tracking** | Basic scammer DB | Multi-case wallet graph |
| **Timeline** | Simple created_at | Full event timeline |

---

## Consolidated Schema (Production-Ready)

### 1. CASE MANAGEMENT

```sql
-- Primary investigation container
CREATE TABLE investigation_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT UNIQUE NOT NULL,           -- e.g., "SOSANA-CRM-2024"
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',           -- active, closed, archived
    priority TEXT DEFAULT 'medium',         -- low, medium, high, critical
    summary JSONB DEFAULT '{}',             -- {total_files, wallets_found, etc.}
    tags TEXT[] DEFAULT '{}',
    assigned_to TEXT,                       -- analyst identifier
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    is_public BOOLEAN DEFAULT FALSE
);

-- Legacy compatibility view
CREATE VIEW investigations AS
SELECT 
    id,
    case_id,
    title,
    description,
    target_address,
    chain,
    status,
    priority as severity,
    assigned_to,
    created_at,
    updated_at,
    resolved_at
FROM investigation_cases;
```

### 2. EVIDENCE & FILES

```sql
-- File storage with extraction metadata
CREATE TABLE investigation_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    
    -- File identification
    file_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256
    filename TEXT,                          -- Stored name
    original_name TEXT,                     -- Original upload name
    file_id TEXT,                           -- Short unique ID
    
    -- File properties
    size_bytes BIGINT,
    mime_type TEXT,
    extension TEXT,
    
    -- Categorization
    category TEXT,                          -- logs, financial, communication, 
                                            -- code, config, evidence, mixed
    source TEXT,                            -- Where it came from
    status TEXT DEFAULT 'pending',          -- pending, processing, critical, 
                                            -- useful, suspicious, useless
    
    -- Storage
    path TEXT,                              -- Filesystem path
    storage_backend TEXT DEFAULT 'local',   -- local, s3, ipfs
    
    -- Extraction results
    extracted_wallets JSONB DEFAULT '[]',   -- Wallets found in file
    extracted_entities JSONB DEFAULT '[]',  -- Named entities
    extracted_emails JSONB DEFAULT '[]',
    extracted_ips JSONB DEFAULT '[]',
    extracted_domains JSONB DEFAULT '[]',
    
    -- Processing metadata
    analysis JSONB DEFAULT '{}',            -- AI analysis results
    processing_errors TEXT[],
    
    -- Audit trail
    uploaded_by TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    
    -- Legacy compatibility
    investigation_id INTEGER  -- For migration from old schema
);

-- Evidence items (extracted artifacts)
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    file_id UUID REFERENCES investigation_files(id) ON DELETE SET NULL,
    
    evidence_type TEXT,                     -- transaction, wallet, communication, 
                                            -- contract, document
    severity TEXT DEFAULT 'low',            -- low, medium, high, critical
    
    description TEXT,
    content TEXT,                           -- Extracted text content
    
    -- Relationships
    related_wallets JSONB DEFAULT '[]',
    related_entities JSONB DEFAULT '[]',
    related_files JSONB DEFAULT '[]',
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Verification
    verified_by TEXT,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_notes TEXT
);

-- Evidence collection from dump_server metadata
CREATE TABLE evidence_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id),
    collection_name TEXT,                   -- e.g., "investigation-20260409"
    collection_path TEXT,                   -- Root path
    total_files INTEGER DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    file_categories JSONB DEFAULT '{}',     -- {mixed: 249, logs: 50, ...}
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);
```

### 3. WALLET & BLOCKCHAIN TRACKING

```sql
-- Wallet discovery and tracking
CREATE TABLE investigation_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    
    -- Wallet identification
    address TEXT NOT NULL,
    chain TEXT DEFAULT 'ethereum',          -- ethereum, solana, bitcoin, 
                                            -- base, bsc, arbitrum, etc.
    address_type TEXT,                      -- eoawallet, contract, exchange, 
                                            -- mixer, bridge
    
    -- Discovery source
    source TEXT,                            -- file extraction, manual, api
    source_file_id UUID REFERENCES investigation_files(id),
    
    -- Risk assessment
    risk_score INTEGER,                     -- 0-100
    risk_level TEXT,                        -- safe, low, medium, high, critical
    is_scammer BOOLEAN DEFAULT FALSE,
    is_exchange BOOLEAN DEFAULT FALSE,
    is_mixer BOOLEAN DEFAULT FALSE,
    
    -- Balance tracking (snapshot)
    balance_eth DECIMAL(30,18),
    balance_usd DECIMAL(20,2),
    last_balance_check TIMESTAMP WITH TIME ZONE,
    
    -- Tags and metadata
    tags TEXT[] DEFAULT '{}',
    aliases TEXT[] DEFAULT '{}',            -- Known names for this wallet
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    first_seen TIMESTAMP WITH TIME ZONE,
    last_active TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(case_id, address)
);

-- Scammer database (consolidated)
CREATE TABLE known_scammers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    primary_address TEXT UNIQUE NOT NULL,
    chain TEXT,
    
    -- Identity
    alias TEXT,
    aliases JSONB DEFAULT '[]',
    
    -- Classification
    scam_type TEXT,                         -- rug_pull, honeypot, phishing, 
                                            -- ponzi, fake_exchange
    tactics TEXT[],                         -- Methods used
    
    -- Impact
    total_stolen_usd DECIMAL(20,2),
    total_stolen_native DECIMAL(30,18),
    victims_count INTEGER,
    
    -- Activity
    first_seen TIMESTAMP WITH TIME ZONE,
    last_active TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Verification
    evidence_count INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    verified_by TEXT,
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    associated_wallets JSONB DEFAULT '[]',
    related_scammers JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Wallet connections (graph relationships)
CREATE TABLE wallet_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    
    wallet_1_id UUID REFERENCES investigation_wallets(id),
    wallet_2_id UUID REFERENCES investigation_wallets(id),
    
    connection_type TEXT,                   -- same_deployer, funded_by, 
                                            -- shared_wallet, interacted, etc.
    evidence TEXT,
    confidence INTEGER,                     -- 0-100
    
    -- Transaction evidence
    supporting_txs JSONB DEFAULT '[]',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(wallet_1_id, wallet_2_id, connection_type)
);

-- Transaction analysis cache
CREATE TABLE transaction_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tx_hash TEXT NOT NULL,
    chain TEXT,
    
    from_address TEXT,
    to_address TEXT,
    value DECIMAL(30,18),
    
    gas_price DECIMAL(30,0),
    gas_used BIGINT,
    gas_fee_eth DECIMAL(30,18),
    
    timestamp TIMESTAMP WITH TIME ZONE,
    block_number BIGINT,
    
    -- Analysis
    is_suspicious BOOLEAN DEFAULT FALSE,
    suspicion_reasons TEXT[],
    analysis JSONB DEFAULT '{}',
    
    -- Relations
    case_id TEXT REFERENCES investigation_cases(case_id),
    related_scammer_id UUID REFERENCES known_scammers(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tx_hash, chain)
);

-- Wallet traces (fund flow)
CREATE TABLE wallet_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    
    source_address TEXT,
    target_address TEXT,
    
    trace_method TEXT,                      -- direct, alternative, mixer, cex, bridge
    path_data JSONB,                        -- Full path with hops
    
    total_value_eth DECIMAL(30,18),
    total_value_usd DECIMAL(20,2),
    
    confidence INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. ENTITIES & IDENTITIES

```sql
-- Named entities (people, organizations, etc.)
CREATE TABLE investigation_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    
    entity_type TEXT NOT NULL,              -- person, organization, exchange, 
                                            -- mixer, project, token
    name TEXT NOT NULL,
    
    aliases TEXT[] DEFAULT '{}',
    
    -- Contact info
    emails TEXT[] DEFAULT '{}',
    phones TEXT[] DEFAULT '{}',
    social_media JSONB DEFAULT '{}',        -- {twitter: "@handle", telegram: "..."}
    websites TEXT[] DEFAULT '{}',
    
    -- Associated wallets
    wallets JSONB DEFAULT '[]',
    
    -- Risk
    risk_level TEXT DEFAULT 'unknown',      -- unknown, low, medium, high, critical
    risk_reasons TEXT[],
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scammer aliases (legacy + new)
CREATE TABLE entity_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES investigation_entities(id) ON DELETE CASCADE,
    scammer_id UUID REFERENCES known_scammers(id) ON DELETE CASCADE,
    
    alias_type TEXT,                        -- telegram, twitter, email, username, 
                                            -- domain, other
    alias_value TEXT,
    source TEXT,
    confidence INTEGER DEFAULT 100,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CHECK (entity_id IS NOT NULL OR scammer_id IS NOT NULL)
);
```

### 5. TIMELINE & EVENTS

```sql
-- Investigation timeline
CREATE TABLE investigation_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    
    event_date TIMESTAMP WITH TIME ZONE,    -- When it happened
    event_type TEXT,                        -- contract_deploy, rug_pull, 
                                            -- fund_movement, communication, etc.
    
    title TEXT,
    description TEXT,
    
    -- Related data
    related_wallets JSONB DEFAULT '[]',
    related_entities JSONB DEFAULT '[]',
    related_txs JSONB DEFAULT '[]',
    evidence_refs JSONB DEFAULT '[]',       -- References to files/evidence
    
    -- Source
    source TEXT,
    source_confidence INTEGER,
    
    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verified_by TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Automated scan results
CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id),
    
    -- Target
    contract_address TEXT,
    chain TEXT,
    
    -- Results
    score INTEGER,                          -- Risk score 0-100
    risk_level TEXT,                        -- safe, low, medium, high, critical
    is_honeypot BOOLEAN,
    
    -- Tax info
    buy_tax DECIMAL(5,2),
    sell_tax DECIMAL(5,2),
    transfer_tax DECIMAL(5,2),
    
    -- Contract properties
    owner_renounced BOOLEAN,
    lp_locked BOOLEAN,
    lp_lock_duration INTEGER,               -- Days
    
    -- Token info
    token_name TEXT,
    token_symbol TEXT,
    token_decimals INTEGER,
    total_supply DECIMAL(40,0),
    
    -- Full data
    scan_data JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 6. USER MANAGEMENT (Legacy Bot)

```sql
-- Bot users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Subscription
    tier VARCHAR(20) DEFAULT 'free',        -- free, basic, pro, enterprise
    scans_remaining INTEGER DEFAULT 3,
    scans_used INTEGER DEFAULT 0,
    
    -- Activity
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_banned BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Subscriptions
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id),
    
    tier VARCHAR(20) NOT NULL,
    payment_method VARCHAR(50),             -- crypto_eth, crypto_bnb, stars, stripe
    
    amounts_usd DECIMAL(10,2),
    amount_crypto DECIMAL(18,8),
    crypto_type VARCHAR(10),
    tx_hash VARCHAR(100),
    wallet_used VARCHAR(100),
    
    status VARCHAR(20) DEFAULT 'pending',   -- pending, active, expired, cancelled
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    activated_at TIMESTAMP
);

-- Pending payments
CREATE TABLE payments_pending (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    payment_id VARCHAR(100) UNIQUE,
    
    tier VARCHAR(20),
    crypto VARCHAR(20),
    amount_usd DECIMAL(10,2),
    amount_crypto DECIMAL(18,8),
    wallet VARCHAR(100),
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    
    tx_detected VARCHAR(100),
    confirmations INTEGER DEFAULT 0
);

-- Transaction history
CREATE TABLE transactions_processed (
    id SERIAL PRIMARY KEY,
    tx_hash VARCHAR(100) UNIQUE NOT NULL,
    user_id BIGINT,
    tier VARCHAR(20),
    crypto VARCHAR(20),
    amount DECIMAL(18,8),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. AUTOMATION (n8n)

```sql
-- n8n workflow definitions
CREATE TABLE n8n_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    
    trigger_type TEXT,                      -- webhook, schedule, manual
    config JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow execution log
CREATE TABLE n8n_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT REFERENCES n8n_workflows(workflow_id),
    
    status TEXT,                            -- running, completed, failed
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE
);
```

---

## Indexes

```sql
-- Cases
CREATE INDEX idx_cases_status ON investigation_cases(status);
CREATE INDEX idx_cases_priority ON investigation_cases(priority);
CREATE INDEX idx_cases_created ON investigation_cases(created_at);

-- Files
CREATE INDEX idx_files_case ON investigation_files(case_id);
CREATE INDEX idx_files_hash ON investigation_files(file_hash);
CREATE INDEX idx_files_category ON investigation_files(category);
CREATE INDEX idx_files_status ON investigation_files(status);

-- Evidence
CREATE INDEX idx_evidence_case ON evidence_items(case_id);
CREATE INDEX idx_evidence_type ON evidence_items(evidence_type);
CREATE INDEX idx_evidence_severity ON evidence_items(severity);

-- Wallets
CREATE INDEX idx_wallets_case ON investigation_wallets(case_id);
CREATE INDEX idx_wallets_address ON investigation_wallets(address);
CREATE INDEX idx_wallets_chain ON investigation_wallets(chain);
CREATE INDEX idx_wallets_risk ON investigation_wallets(risk_score);

-- Scammers
CREATE INDEX idx_scammers_address ON known_scammers(primary_address);
CREATE INDEX idx_scammers_alias ON known_scammers(alias);
CREATE INDEX idx_scammers_type ON known_scammers(scam_type);
CREATE INDEX idx_scammers_active ON known_scammers(is_active);

-- Transactions
CREATE INDEX idx_tx_hash ON transaction_analysis(tx_hash);
CREATE INDEX idx_tx_from ON transaction_analysis(from_address);
CREATE INDEX idx_tx_to ON transaction_analysis(to_address);
CREATE INDEX idx_tx_case ON transaction_analysis(case_id);

-- Timeline
CREATE INDEX idx_timeline_case ON investigation_timeline(case_id);
CREATE INDEX idx_timeline_date ON investigation_timeline(event_date);
CREATE INDEX idx_timeline_type ON investigation_timeline(event_type);

-- Entities
CREATE INDEX idx_entities_case ON investigation_entities(case_id);
CREATE INDEX idx_entities_type ON investigation_entities(entity_type);
CREATE INDEX idx_entities_name ON investigation_entities(name);

-- Users (legacy)
CREATE INDEX idx_users_telegram ON users(telegram_id);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

---

## Views

```sql
-- Active cases summary
CREATE VIEW v_case_summary AS
SELECT 
    c.case_id,
    c.title,
    c.status,
    c.priority,
    COUNT(DISTINCT f.id) as file_count,
    COUNT(DISTINCT w.id) as wallet_count,
    COUNT(DISTINCT e.id) as evidence_count,
    c.created_at,
    c.updated_at
FROM investigation_cases c
LEFT JOIN investigation_files f ON c.case_id = f.case_id
LEFT JOIN investigation_wallets w ON c.case_id = w.case_id
LEFT JOIN evidence_items e ON c.case_id = e.case_id
GROUP BY c.case_id, c.title, c.status, c.priority, c.created_at, c.updated_at;

-- Scammer network
CREATE VIEW v_scammer_network AS
SELECT 
    ks1.primary_address as scammer_1,
    ks1.alias as alias_1,
    ks2.primary_address as scammer_2,
    ks2.alias as alias_2,
    wc.connection_type,
    wc.confidence
FROM wallet_connections wc
JOIN investigation_wallets w1 ON wc.wallet_1_id = w1.id
JOIN investigation_wallets w2 ON wc.wallet_2_id = w2.id
JOIN known_scammers ks1 ON w1.address = ks1.primary_address
JOIN known_scammers ks2 ON w2.address = ks2.primary_address
WHERE wc.confidence >= 70;

-- High-risk wallets
CREATE VIEW v_high_risk_wallets AS
SELECT 
    w.*,
    c.case_id,
    c.title as case_title
FROM investigation_wallets w
JOIN investigation_cases c ON w.case_id = c.case_id
WHERE w.risk_score >= 70 OR w.is_scammer = TRUE;

-- Unprocessed evidence
CREATE VIEW v_unprocessed_evidence AS
SELECT 
    f.*,
    c.title as case_title
FROM investigation_files f
JOIN investigation_cases c ON f.case_id = c.case_id
WHERE f.status = 'pending' OR f.processed_at IS NULL;
```

---

## Evidence Collection Structure

From dump_server analysis:

```
dumps/
└── {investigation-name}/
    ├── mixed/              # Uncategorized files
    │   ├── {timestamp}_{file_id}_{filename}
    │   └── {timestamp}_{file_id}_{filename}.json  # Metadata
    ├── logs/               # Log files
    ├── financial/          # Financial records
    ├── communication/      # Emails, chats
    ├── code/               # Source code
    └── config/             # Configuration files
```

### Metadata Schema (per file)

```json
{
  "original_name": "filename.ext",
  "saved_name": "{timestamp}_{file_id}_{filename}",
  "file_id": "8-char-hex",
  "case_id": "investigation-name",
  "category": "mixed|logs|financial|communication|code|config",
  "source": "",
  "notes": "",
  "sha256": "hash",
  "size": 12345,
  "uploaded_by": "user-id",
  "uploaded_at": "ISO-timestamp",
  "path": "/full/path"
}
```

---

## Migration Strategy

1. **Phase 1**: Create new UUID-based tables alongside existing SERIAL tables
2. **Phase 2**: Migrate data with ID mapping
3. **Phase 3**: Update application code
4. **Phase 4**: Deprecate old tables (keep for reference)

---

## Row Level Security (RLS)

```sql
-- Enable RLS on all tables
ALTER TABLE investigation_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_timeline ENABLE ROW LEVEL SECURITY;

-- Service role full access
CREATE POLICY "Service role full access" ON investigation_cases
    FOR ALL USING (auth.role() = 'service_role');
    
-- Public read for public cases
CREATE POLICY "Public view" ON investigation_cases
    FOR SELECT USING (is_public = TRUE);

-- Similar policies for other tables...
```

---

## FRONTEND FEATURE TABLES (RMI Platform)

### rmi_suspects
Human suspect profiles for investigations
```sql
CREATE TABLE rmi_suspects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suspect_id TEXT UNIQUE NOT NULL,
    display_name TEXT,
    aliases TEXT[] DEFAULT '{}',
    estimated_timezone TEXT,
    timezone_confidence INTEGER,
    behavioral_fingerprint JSONB,
    linguistic_patterns TEXT[],
    associated_wallets JSONB,
    status TEXT DEFAULT 'UNDER_INVESTIGATION',
    confidence_score INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### rmi_sessions
Active investigation sessions per user
```sql
CREATE TABLE rmi_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    case_id TEXT REFERENCES investigation_cases(case_id),
    session_data JSONB DEFAULT '{}',
    vault_data JSONB DEFAULT '{}',
    chat_history JSONB DEFAULT '[]',
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### rmi_vault_items
Evidence items discovered during sessions
```sql
CREATE TABLE rmi_vault_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES rmi_sessions(id) ON DELETE CASCADE,
    wallet_address TEXT,
    chain TEXT DEFAULT 'solana',
    source_file TEXT,
    source_evidence_id UUID REFERENCES investigation_evidence(id),
    verified BOOLEAN DEFAULT FALSE,
    api_verification JSONB,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### rmi_analysis_runs
Record of analysis tool executions
```sql
CREATE TABLE rmi_analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES rmi_sessions(id),
    user_id BIGINT,
    analysis_type TEXT, -- ghost_scan, fee_audit, manipulation, prebond, etc.
    target_address TEXT,
    target_type TEXT, -- wallet, contract, pool
    results JSONB,
    confidence INTEGER,
    verified_by_ai TEXT,
    run_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_time_ms INTEGER
);
```

### rmi_syndicate_wallets
Known criminal syndicate wallet mappings
```sql
CREATE TABLE rmi_syndicate_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    syndicate_name TEXT,
    role TEXT, -- BOSS_HOLDING, PAYROLL_HUB, etc.
    wallet_address TEXT,
    chain TEXT DEFAULT 'solana',
    verified BOOLEAN DEFAULT FALSE,
    linked_cases TEXT[],
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### rmi_document_hashes
Document deduplication via content hashing
```sql
CREATE TABLE rmi_document_hashes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sha256_hash TEXT UNIQUE NOT NULL,
    ai_title TEXT,
    ai_summary TEXT,
    original_name TEXT,
    content_type TEXT,
    extracted_entities JSONB,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### rmi_telegram_buttons
Track button interactions for analytics
```sql
CREATE TABLE rmi_telegram_buttons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    session_id UUID REFERENCES rmi_sessions(id),
    button_type TEXT,
    button_data TEXT,
    context JSONB,
    clicked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### rmi_indictments
Generated legal reports
```sql
CREATE TABLE rmi_indictments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id),
    session_id UUID REFERENCES rmi_sessions(id),
    title TEXT,
    content TEXT,
    evidence_refs JSONB,
    confidence_score INTEGER,
    reviewed_by TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Indexes for Frontend Tables

```sql
CREATE INDEX idx_rmi_suspects_id ON rmi_suspects(suspect_id);
CREATE INDEX idx_rmi_suspects_status ON rmi_suspects(status);
CREATE INDEX idx_rmi_sessions_user ON rmi_sessions(user_id);
CREATE INDEX idx_rmi_sessions_case ON rmi_sessions(case_id);
CREATE INDEX idx_rmi_sessions_active ON rmi_sessions(is_active);
CREATE INDEX idx_rmi_vault_session ON rmi_vault_items(session_id);
CREATE INDEX idx_rmi_vault_wallet ON rmi_vault_items(wallet_address);
CREATE INDEX idx_rmi_analysis_session ON rmi_analysis_runs(session_id);
CREATE INDEX idx_rmi_analysis_type ON rmi_analysis_runs(analysis_type);
CREATE INDEX idx_rmi_syndicate_name ON rmi_syndicate_wallets(syndicate_name);
CREATE INDEX idx_rmi_syndicate_wallet ON rmi_syndicate_wallets(wallet_address);
CREATE INDEX idx_rmi_doc_hashes ON rmi_document_hashes(sha256_hash);
CREATE INDEX idx_rmi_indictments_case ON rmi_indictments(case_id);
```
