-- ============================================
-- RMI Investigation Platform - Database Setup
-- Run this in Supabase Dashboard > SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create exec_sql function for programmatic access
CREATE OR REPLACE FUNCTION exec_sql(query TEXT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
END;
$$;

GRANT EXECUTE ON FUNCTION exec_sql(TEXT) TO service_role;

-- ============================================
-- CORE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS investigation_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    priority TEXT DEFAULT 'medium',
    summary JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_public BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS investigation_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id),
    address TEXT NOT NULL,
    chain TEXT DEFAULT 'ethereum',
    source TEXT,
    risk_score INTEGER,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(case_id, address)
);

CREATE TABLE IF NOT EXISTS investigation_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id),
    file_path TEXT,
    file_name TEXT,
    file_type TEXT,
    category TEXT,
    source TEXT,
    file_size INTEGER,
    extracted_wallets JSONB DEFAULT '{}',
    extracted_entities JSONB DEFAULT '{}',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS investigation_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id),
    entity_type TEXT NOT NULL,
    name TEXT NOT NULL,
    aliases TEXT[] DEFAULT '{}',
    wallets JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    risk_level TEXT DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS investigation_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id TEXT REFERENCES investigation_cases(case_id),
    event_date TIMESTAMP WITH TIME ZONE,
    event_type TEXT,
    description TEXT,
    related_entities JSONB DEFAULT '{}',
    evidence_refs JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_wallets_address ON investigation_wallets(address);
CREATE INDEX IF NOT EXISTS idx_wallets_case ON investigation_wallets(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_case ON investigation_evidence(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_category ON investigation_evidence(category);
CREATE INDEX IF NOT EXISTS idx_entities_case ON investigation_entities(case_id);
CREATE INDEX IF NOT EXISTS idx_timeline_case ON investigation_timeline(case_id);
CREATE INDEX IF NOT EXISTS idx_timeline_date ON investigation_timeline(event_date);

-- ============================================
-- RLS POLICIES
-- ============================================
ALTER TABLE investigation_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_timeline ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access" ON investigation_cases
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Public view" ON investigation_cases
    FOR SELECT USING (is_public = TRUE);
CREATE POLICY "Service role wallets" ON investigation_wallets
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role evidence" ON investigation_evidence
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role entities" ON investigation_entities
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role timeline" ON investigation_timeline
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- INITIAL DATA
-- ============================================
INSERT INTO investigation_cases (case_id, title, description, status, priority, summary, tags)
VALUES (
    'SOSANA-CRM-2024',
    'SOSANA Enterprise Criminal Investigation',
    'Investigation into SOSANA organization for cryptocurrency fraud, fake voting manipulation, and CRM token extraction.',
    'active',
    'critical',
    '{"total_files": 237, "wallets_found": 5883, "sosana_related": 129, "critical_evidence": 125}',
    '{"sosana", "crm", "fraud", "voting", "extraction"}'
)
ON CONFLICT (case_id) DO UPDATE SET
    updated_at = NOW(),
    summary = EXCLUDED.summary;

-- ============================================
-- N8N WORKFLOW TABLES
-- ============================================
CREATE TABLE IF NOT EXISTS n8n_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    trigger_type TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS n8n_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT REFERENCES n8n_workflows(workflow_id),
    status TEXT,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE
);

-- Sample n8n workflow for investigation alerts
INSERT INTO n8n_workflows (workflow_id, name, description, trigger_type, config)
VALUES (
    'investigation-alerts',
    'Investigation Alert Handler',
    'Processes new evidence and sends alerts',
    'webhook',
    '{"webhook_path": "/investigation-alert", "methods": ["POST"]}'
)
ON CONFLICT DO NOTHING;

