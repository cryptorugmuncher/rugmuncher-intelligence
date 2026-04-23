CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE OR REPLACE FUNCTION exec_sql(query TEXT) 
RETURNS VOID LANGUAGE plpgsql SECURITY DEFINER AS $$ 
BEGIN EXECUTE query; END; 
$$;

GRANT EXECUTE ON FUNCTION exec_sql(TEXT) TO service_role;

CREATE TABLE IF NOT EXISTS investigation_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
    case_id TEXT UNIQUE NOT NULL, 
    title TEXT NOT NULL, 
    status TEXT DEFAULT 'active', 
    summary JSONB DEFAULT '{}'::jsonb, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS investigation_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
    case_id TEXT REFERENCES investigation_cases(case_id), 
    address TEXT NOT NULL, 
    chain TEXT DEFAULT 'ethereum', 
    source TEXT, 
    metadata JSONB DEFAULT '{}'::jsonb, 
    UNIQUE(case_id, address)
);

CREATE TABLE IF NOT EXISTS investigation_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
    case_id TEXT REFERENCES investigation_cases(case_id), 
    file_path TEXT, 
    file_type TEXT, 
    category TEXT, 
    source TEXT, 
    extracted_wallets JSONB DEFAULT '{}'::jsonb, 
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO investigation_cases (case_id, title, status, summary) 
VALUES ('SOSANA-CRM-2024', 'SOSANA Investigation', 'active', '{"files": 237, "wallets": 5883}'::jsonb) 
ON CONFLICT DO NOTHING;
