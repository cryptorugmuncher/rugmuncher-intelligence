-- Free API Discoveries Table
-- Tracks discovered free AI APIs and their signup status

CREATE TABLE IF NOT EXISTS free_api_discoveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    name TEXT,
    description TEXT,
    source TEXT,
    source_url TEXT,
    signup_url TEXT,
    key_url TEXT,
    free BOOLEAN DEFAULT true,
    pricing JSONB DEFAULT '{}',
    auto_add_ready BOOLEAN DEFAULT false,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'new',
    metadata JSONB DEFAULT '{}',
    UNIQUE(provider, model)
);

CREATE INDEX IF NOT EXISTS idx_free_api_provider ON free_api_discoveries(provider);
CREATE INDEX IF NOT EXISTS idx_free_api_status ON free_api_discoveries(status);
CREATE INDEX IF NOT EXISTS idx_free_api_discovered ON free_api_discoveries(discovered_at DESC);
