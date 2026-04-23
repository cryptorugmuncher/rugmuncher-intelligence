-- ============================================================================
-- EVIDENCE FORTRESS DATABASE SCHEMA v4.0
-- Privacy-First Forensic Evidence Processing System
-- For: SOSANA/CRM RICO Investigation
-- ============================================================================
-- CRITICAL SECURITY PRINCIPLE: Raw wallet addresses NEVER leave Contabo server.
-- All external API calls use pseudonymized tags like [ENTITY_001].
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TIER 1: IMMUTABLE EVIDENCE VAULT (Chain of Custody)
-- ============================================================================

CREATE TABLE evidence_vault (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Evidence identification
    evidence_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256 of raw content
    evidence_type VARCHAR(50) NOT NULL,          -- 'transfer_csv', 'chat_log', 'json_export'
    source_file VARCHAR(255) NOT NULL,           -- Original filename
    
    -- Case linkage
    case_id VARCHAR(50) NOT NULL DEFAULT 'SOSANA_RICO_2026',
    
    -- Content (encrypted at rest)
    encrypted_content BYTEA NOT NULL,            -- AES-256 encrypted raw data
    content_hash VARCHAR(64) NOT NULL,           -- SHA256 for integrity verification
    
    -- Chain of custody
    collected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    collected_by VARCHAR(100) NOT NULL DEFAULT 'system',
    custody_chain JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    -- Tamper detection
    previous_hash VARCHAR(64),                   -- For blockchain-like integrity chain
    integrity_signature VARCHAR(128),            -- HMAC of this record
    
    -- Metadata
    file_size_bytes INTEGER,
    row_count INTEGER,
    parsed_successfully BOOLEAN DEFAULT FALSE,
    
    -- Legal flags
    is_exhibit BOOLEAN DEFAULT FALSE,
    exhibit_number VARCHAR(20),
    legal_hold BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Chain of custody index
CREATE INDEX idx_evidence_case ON evidence_vault(case_id);
CREATE INDEX idx_evidence_type ON evidence_vault(evidence_type);
CREATE INDEX idx_evidence_collected ON evidence_vault(collected_at);

-- ============================================================================
-- TIER 2: CRYPTO ENTITY REGISTRY (Pseudonymization Layer)
-- ============================================================================

CREATE TABLE crypto_entities (
    id SERIAL PRIMARY KEY,
    
    -- Pseudonymization (EXTERNAL USE ONLY)
    address_hash VARCHAR(64) UNIQUE NOT NULL,    -- SHA256(real_address) - lookup key
    pseudonym VARCHAR(30) UNIQUE NOT NULL,       -- [ENTITY_001], [TREASURY_SOSANA]
    
    -- Entity classification (RICO hierarchy)
    entity_tier VARCHAR(20),                     -- 'tier_0_root', 'tier_1_treasury', 
                                                 -- 'tier_2_botnet', 'tier_3_mule',
                                                 -- 'tier_4_cashout', 'tier_5_victim'
    entity_role VARCHAR(50),                     -- 'deployer', 'distributor', 'seeder',
                                                 -- 'liquidity_provider', 'kyc_mule'
    
    -- Case context
    case_id VARCHAR(50) NOT NULL DEFAULT 'SOSANA_RICO_2026',
    cluster_id VARCHAR(50),                      -- Links entities to the same operation
    
    -- Behavioral fingerprints (sanitized)
    behavior_profile JSONB DEFAULT '{}'::jsonb,  -- Patterns without raw addresses
    risk_score DECIMAL(3,2),                     -- 0.00 to 1.00
    confidence_score DECIMAL(3,2),               -- Classification confidence
    
    -- Status
    is_watchlisted BOOLEAN DEFAULT FALSE,
    is_frozen BOOLEAN DEFAULT FALSE,
    analysis_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'analyzing', 'complete'
    
    -- Tracking
    first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    transaction_count INTEGER DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for entity lookups
CREATE INDEX idx_entity_hash ON crypto_entities(address_hash);
CREATE INDEX idx_entity_pseudonym ON crypto_entities(pseudonym);
CREATE INDEX idx_entity_tier ON crypto_entities(entity_tier);
CREATE INDEX idx_entity_cluster ON crypto_entities(cluster_id);
CREATE INDEX idx_entity_case ON crypto_entities(case_id);

-- ============================================================================
-- TIER 3: ADDRESS SECRETS (LOCAL-ONLY ENCRYPTION)
-- ============================================================================
-- WARNING: This table contains sensitive data. Never replicate to cloud.
-- Access only through sanitization gateway.

CREATE TABLE address_secrets (
    address_hash VARCHAR(64) PRIMARY KEY,
    
    -- Encrypted real address (AES-256-GCM)
    encrypted_address BYTEA NOT NULL,
    encryption_nonce BYTEA NOT NULL,             -- GCM nonce
    encryption_tag BYTEA NOT NULL,               -- GCM auth tag
    
    -- Key derivation info
    kdf_salt BYTEA NOT NULL,
    kdf_iterations INTEGER NOT NULL DEFAULT 100000,
    
    -- Access control
    access_level VARCHAR(20) DEFAULT 'investigator', -- 'lead', 'investigator', 'analyst'
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    
    -- Foreign key
    FOREIGN KEY (address_hash) REFERENCES crypto_entities(address_hash)
        ON DELETE CASCADE
);

-- ============================================================================
-- TIER 4: TRANSACTION GRAPH (Sanitized Relationships)
-- ============================================================================

CREATE TABLE transaction_graph (
    id BIGSERIAL PRIMARY KEY,
    
    -- Transaction identifiers
    signature VARCHAR(100) UNIQUE NOT NULL,      -- Solana signature
    block_time TIMESTAMP NOT NULL,
    block_number BIGINT,
    
    -- Sanitized parties (pseudonyms only)
    from_pseudonym VARCHAR(30) NOT NULL,         -- [ENTITY_001]
    to_pseudonym VARCHAR(30) NOT NULL,           -- [ENTITY_002]
    
    -- Token info (public data is safe)
    token_address VARCHAR(50),                   -- Token mint (public)
    token_symbol VARCHAR(20),
    amount_raw NUMERIC(40,0),                    -- Raw token amount
    amount_decimal NUMERIC(30,10),               -- Human-readable
    
    -- Flow classification
    flow_type VARCHAR(20),                       -- 'in', 'out', 'internal'
    
    -- Link to evidence source
    evidence_id UUID REFERENCES evidence_vault(id),
    
    -- Analysis
    pattern_detected VARCHAR(50),                -- 'layering', 'structuring', 'rapid_fire'
    is_suspicious BOOLEAN DEFAULT FALSE,
    suspicion_reasons JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    processed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT fk_from_entity FOREIGN KEY (from_pseudonym) 
        REFERENCES crypto_entities(pseudonym),
    CONSTRAINT fk_to_entity FOREIGN KEY (to_pseudonym) 
        REFERENCES crypto_entities(pseudonym)
);

CREATE INDEX idx_tx_from ON transaction_graph(from_pseudonym);
CREATE INDEX idx_tx_to ON transaction_graph(to_pseudonym);
CREATE INDEX idx_tx_block_time ON transaction_graph(block_time);
CREATE INDEX idx_tx_token ON transaction_graph(token_address);
CREATE INDEX idx_tx_pattern ON transaction_graph(pattern_detected);

-- ============================================================================
-- TIER 5: HUMAN OPERATORS (Off-Chain Intelligence)
-- ============================================================================

CREATE TABLE human_operators (
    id SERIAL PRIMARY KEY,
    
    -- Pseudonymized identity
    operator_pseudonym VARCHAR(30) UNIQUE NOT NULL, -- [OPERATOR_001]
    
    -- Aliases and handles (from chat logs, OSINT)
    known_aliases JSONB DEFAULT '[]'::jsonb,     -- ["CryptoRugMunch", "Marcus"]
    telegram_handles JSONB DEFAULT '[]'::jsonb,
    twitter_handles JSONB DEFAULT '[]'::jsonb,
    discord_handles JSONB DEFAULT '[]'::jsonb,
    
    -- Linked entities (pseudonyms only)
    linked_wallet_pseudonyms JSONB DEFAULT '[]'::jsonb,
    
    -- RICO role
    rico_role VARCHAR(50),                       -- 'organizer', 'manager', 'foot_soldier'
    hierarchy_level INTEGER,                     -- 1-5
    reports_to VARCHAR(30),                      -- Parent operator pseudonym
    
    -- Evidence linkage
    source_evidence_ids JSONB DEFAULT '[]'::jsonb,
    
    -- Status
    is_identified BOOLEAN DEFAULT FALSE,
    identification_confidence DECIMAL(3,2),
    
    -- Notes (sanitized)
    intelligence_notes TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TIER 6: ANALYSIS JOBS (Cost Tracking & Queue Management)
-- ============================================================================

CREATE TABLE analysis_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Job identification
    job_type VARCHAR(50) NOT NULL,               -- 'pattern_detection', 'llm_analysis',
                                                 -- 'graph_analysis', 'entity_clustering'
    
    -- Input (sanitized references only)
    input_evidence_ids JSONB,                    -- Array of evidence UUIDs
    input_entity_pseudonyms JSONB,               -- Array of entity pseudonyms
    
    -- LLM routing
    llm_provider VARCHAR(30),                    -- 'ollama', 'groq', 'aws_bedrock'
    llm_model VARCHAR(50),                       -- 'llama3.1:70b', 'mixtral-8x7b'
    
    -- Cost tracking (microdollar precision)
    estimated_cost_microdollars BIGINT,          -- Pre-job estimate
    actual_cost_microdollars BIGINT,             -- Post-job actual
    tokens_input INTEGER,
    tokens_output INTEGER,
    
    -- Status
    status VARCHAR(20) DEFAULT 'queued',         -- 'queued', 'running', 'complete', 'failed'
    priority INTEGER DEFAULT 5,                  -- 1-10
    
    -- Timing
    queued_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Results
    result_summary JSONB,
    output_location VARCHAR(255),
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Audit
    requested_by VARCHAR(100) NOT NULL DEFAULT 'system',
    ip_address INET
);

CREATE INDEX idx_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_jobs_priority ON analysis_jobs(priority) WHERE status = 'queued';
CREATE INDEX idx_jobs_cost ON analysis_jobs(llm_provider, actual_cost_microdollars);

-- ============================================================================
-- TIER 7: AUDIT LOGS (Legal Chain of Custody)
-- ============================================================================

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL,             -- 'evidence_ingested', 'entity_created',
                                                 -- 'address_accessed', 'analysis_run',
                                                 -- 'export_generated'
    
    -- Actor
    actor_type VARCHAR(20) NOT NULL,             -- 'system', 'user', 'api'
    actor_id VARCHAR(100),
    
    -- Target (what was affected)
    target_table VARCHAR(50),
    target_id VARCHAR(100),
    
    -- Change details
    old_values JSONB,
    new_values JSONB,
    change_description TEXT,
    
    -- Context
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp (immutable)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Integrity
    log_hash VARCHAR(64),                        -- SHA256 of this record
    previous_log_hash VARCHAR(64)                -- Chain for tamper detection
);

CREATE INDEX idx_audit_event ON audit_logs(event_type);
CREATE INDEX idx_audit_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_target ON audit_logs(target_table, target_id);
CREATE INDEX idx_audit_time ON audit_logs(created_at);

-- ============================================================================
-- VIEWS (For Safe Querying)
-- ============================================================================

-- Safe entity view (no sensitive data)
CREATE VIEW v_entities_safe AS
SELECT 
    pseudonym,
    entity_tier,
    entity_role,
    cluster_id,
    risk_score,
    confidence_score,
    first_seen,
    last_seen,
    transaction_count
FROM crypto_entities
WHERE is_frozen = FALSE;

-- Transaction summary view
CREATE VIEW v_transaction_summary AS
SELECT 
    DATE(block_time) as tx_date,
    from_pseudonym,
    to_pseudonym,
    token_symbol,
    COUNT(*) as tx_count,
    SUM(amount_decimal) as total_amount
FROM transaction_graph
GROUP BY DATE(block_time), from_pseudonym, to_pseudonym, token_symbol;

-- Cost analysis view
CREATE VIEW v_cost_analysis AS
SELECT 
    llm_provider,
    llm_model,
    job_type,
    COUNT(*) as job_count,
    SUM(actual_cost_microdollars) / 1000000.0 as total_cost_dollars,
    AVG(tokens_input) as avg_input_tokens,
    AVG(tokens_output) as avg_output_tokens
FROM analysis_jobs
WHERE status = 'complete'
GROUP BY llm_provider, llm_model, job_type;

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_crypto_entities_updated
    BEFORE UPDATE ON crypto_entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_human_operators_updated
    BEFORE UPDATE ON human_operators
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Audit log trigger
CREATE OR REPLACE FUNCTION log_address_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        event_type, actor_type, actor_id, target_table, target_id,
        change_description, created_at
    ) VALUES (
        'address_accessed', 'system', current_user, 
        'address_secrets', NEW.address_hash,
        'Address secret accessed', NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_address_access_audit
    AFTER SELECT ON address_secrets
    FOR EACH ROW EXECUTE FUNCTION log_address_access();

-- ============================================================================
-- INITIAL DATA: SOSANA Case Entities
-- ============================================================================

-- Insert known SOSANA entities (with placeholder encrypted addresses)
-- Real addresses will be populated by ingestion script

INSERT INTO crypto_entities (address_hash, pseudonym, entity_tier, entity_role, cluster_id, risk_score) VALUES
('SOSANA_TREASURY_HASH_PLACEHOLDER', '[TREASURY_SOSANA]', 'tier_1_treasury', 'token_treasury', 'sosana_core', 0.95),
('SOSANA_LP_HASH_PLACEHOLDER', '[LIQUIDITY_SOSANA]', 'tier_1_treasury', 'liquidity_provider', 'sosana_core', 0.90),
('AFXIGAYU_HASH_PLACEHOLDER', '[BOTNET_SEEDER_001]', 'tier_2_botnet', 'wallet_seeder', 'botnet_alpha', 0.98),
('8EVZA7B_HASH_PLACEHOLDER', '[DISTRIBUTOR_009]', 'tier_2_botnet', 'crm_distributor', 'crm_network', 0.92),

-- CRIMINAL ENTERPRISE WALLETS (March 30, 2026 Cross-Reference)
-- Tier 1: Master Feeders
('HLNP_SZ9H_FEEDER_001_HASH', '[MASTER_FEEDER_001]', 'tier_1_treasury', 'dust_fee_source', 'crm_criminal_enterprise', 0.99),
('HLNP_SZ9H_FEEDER_002_HASH', '[MASTER_FEEDER_002]', 'tier_1_treasury', 'dust_fee_source', 'crm_criminal_enterprise', 0.98),

-- Tier 2: Core Botnet
('DLHNB1YT_DORMANT_HASH', '[DORMANT_VOLCANO]', 'tier_2_botnet', 'cluster_leader', 'crm_criminal_enterprise', 0.99),
('8PYIQMCT_CONSOL_HASH', '[CONSOLIDATION_001]', 'tier_2_botnet', 'consolidation_wallet', 'crm_criminal_enterprise', 0.97),
('E9BG6VCA_SOSANA_HASH', '[SOSANA_CORE_001]', 'tier_2_botnet', 'sosana_cluster', 'crm_criminal_enterprise', 0.96),

-- Tier 3: Satellite Mules
('D9ZGRMHM_SAT001_HASH', '[SATELLITE_001]', 'tier_3_mule', 'execution_wallet', 'crm_criminal_enterprise', 0.90),
('HPVUJGJW_RELOAD_HASH', '[RELOAD_001]', 'tier_3_mule', 'reload_wallet', 'crm_criminal_enterprise', 0.88),
('J3V68JVJ_SAT002_HASH', '[SATELLITE_002]', 'tier_3_mule', 'dust_accumulator', 'crm_criminal_enterprise', 0.87),
('CYHJT3O8_IMMINENT_HASH', '[IMMINENT_THREAT]', 'tier_3_mule', 'dormant_threat', 'crm_criminal_enterprise', 0.95),

-- Tier 4: Cashout
('HHXYZI7Z_EXIT_HASH', '[EXIT_SELLER_001]', 'tier_4_cashout', 'systematic_seller', 'crm_criminal_enterprise', 0.92),

-- Tier 5: Victim
('7ABBMGF4_VICTIM_HASH', '[VICTIM_WHALE_001]', 'tier_5_victim', 'downstream_victim', 'crm_criminal_enterprise', 0.60);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE evidence_vault IS 'Immutable evidence storage with chain of custody';
COMMENT ON TABLE crypto_entities IS 'Pseudonymized entity registry - NO RAW ADDRESSES';
COMMENT ON TABLE address_secrets IS 'LOCAL-ONLY: Encrypted real addresses. NEVER leave Contabo.';
COMMENT ON TABLE transaction_graph IS 'Sanitized transaction relationships using pseudonyms only';
COMMENT ON TABLE human_operators IS 'Off-chain human intelligence (Telegram, Twitter, etc.)';
COMMENT ON TABLE analysis_jobs IS 'LLM job queue with microdollar cost tracking';
COMMENT ON TABLE audit_logs IS 'Legal-grade audit trail, append-only';
