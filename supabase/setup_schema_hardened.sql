-- RMI Supabase Schema — Hardened Security Fix
-- =============================================================
-- Fixes exposed tables, weak RLS, and adds proper auth policies

-- Drop old permissive policies (if they exist)
DROP POLICY IF EXISTS "Service full access telegram_users" ON telegram_users;
DROP POLICY IF EXISTS "Service full access telegram_scans" ON telegram_scans;
DROP POLICY IF EXISTS "Service full access telegram_subscriptions" ON telegram_subscriptions;

-- ═══════════════════════════════════════════════════════════
-- CORE TABLES
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS agents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'agent',
    config JSONB DEFAULT '{}',
    status TEXT DEFAULT 'offline',
    last_ping TIMESTAMPTZ,
    tier TEXT DEFAULT 'T2',
    models TEXT[] DEFAULT '{}',
    triggers TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Agents read own" ON agents FOR SELECT USING (auth.uid() IS NOT NULL);
CREATE POLICY "Agents admin write" ON agents FOR ALL USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    target TEXT NOT NULL,
    type TEXT DEFAULT 'wallet',
    evidence JSONB DEFAULT '[]',
    status TEXT DEFAULT 'open',
    risk_score NUMERIC DEFAULT 0,
    agents_assigned TEXT[] DEFAULT '{}',
    findings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Cases owner read" ON cases FOR SELECT USING (
    auth.uid()::text = ANY(agents_assigned) OR
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE TABLE IF NOT EXISTS evidence (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    case_id TEXT REFERENCES cases(id),
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    evidence_type TEXT DEFAULT 'on-chain',
    confidence_score NUMERIC DEFAULT 0,
    ipfs_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Evidence case read" ON evidence FOR SELECT USING (
    EXISTS (SELECT 1 FROM cases WHERE cases.id = evidence.case_id AND (
        auth.uid()::text = ANY(cases.agents_assigned) OR
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
    ))
);

CREATE TABLE IF NOT EXISTS wallet_intel (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    address TEXT NOT NULL UNIQUE,
    chain TEXT DEFAULT 'solana',
    tags TEXT[] DEFAULT '{}',
    risk_score NUMERIC DEFAULT 0,
    balance JSONB DEFAULT '{}',
    transactions JSONB DEFAULT '[]',
    related_addresses TEXT[] DEFAULT '{}',
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE wallet_intel ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Wallet intel public read" ON wallet_intel FOR SELECT USING (true);
CREATE POLICY "Wallet intel admin write" ON wallet_intel FOR ALL USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE TABLE IF NOT EXISTS syndicate_wallets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    address TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL,
    role TEXT NOT NULL,
    balance TEXT,
    status TEXT DEFAULT 'active',
    contract TEXT,
    notes TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE syndicate_wallets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Syndicate admin read" ON syndicate_wallets FOR SELECT USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE TABLE IF NOT EXISTS api_quota_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    provider TEXT NOT NULL,
    model TEXT,
    requests_used INTEGER DEFAULT 0,
    requests_limit INTEGER DEFAULT 0,
    latency_ms INTEGER,
    status TEXT DEFAULT 'ok',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE api_quota_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Quota admin read" ON api_quota_logs FOR SELECT USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    token_address TEXT NOT NULL,
    alert_types TEXT[] DEFAULT '{}',
    webhook_url TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Alerts owner read" ON alerts FOR SELECT USING (
    auth.uid()::text = id OR
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE TABLE IF NOT EXISTS scam_signatures (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pattern_name TEXT NOT NULL,
    indicators JSONB DEFAULT '{}',
    severity TEXT DEFAULT 'medium',
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    count INTEGER DEFAULT 1
);
ALTER TABLE scam_signatures ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Signatures public read" ON scam_signatures FOR SELECT USING (true);
CREATE POLICY "Signatures admin write" ON scam_signatures FOR ALL USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

-- ═══════════════════════════════════════════════════════════
-- TELEGRAM BOT TABLES (HARDENED)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    tier TEXT DEFAULT 'free',
    scans_used INTEGER DEFAULT 0,
    scans_limit INTEGER DEFAULT 3,
    scans_reset_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '30 days',
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    badges TEXT[] DEFAULT '{}',
    total_scans INTEGER DEFAULT 0,
    wallet_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE telegram_users ENABLE ROW LEVEL SECURITY;
-- Users can only read/write their own record via service role or verified telegram_id
CREATE POLICY "Telegram users self" ON telegram_users FOR ALL USING (false) WITH CHECK (false);
-- All access through service_role key only (backend functions)

CREATE TABLE IF NOT EXISTS telegram_scans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    scan_type TEXT NOT NULL,
    token TEXT NOT NULL,
    chain TEXT DEFAULT 'solana',
    result JSONB DEFAULT '{}',
    risk_score INTEGER,
    ai_consensus TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (telegram_id) REFERENCES telegram_users(telegram_id) ON DELETE CASCADE
);
ALTER TABLE telegram_scans ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Telegram scans self" ON telegram_scans FOR ALL USING (false) WITH CHECK (false);

CREATE TABLE IF NOT EXISTS telegram_subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    tier TEXT NOT NULL,
    provider TEXT NOT NULL,
    amount NUMERIC,
    currency TEXT,
    payload TEXT,
    status TEXT DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (telegram_id) REFERENCES telegram_users(telegram_id) ON DELETE CASCADE
);
ALTER TABLE telegram_subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Telegram subs self" ON telegram_subscriptions FOR ALL USING (false) WITH CHECK (false);

CREATE TABLE IF NOT EXISTS telegram_broadcasts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    channel_id TEXT NOT NULL,
    channel_name TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    message_id BIGINT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE telegram_broadcasts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Broadcasts admin read" ON telegram_broadcasts FOR SELECT USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_wallet_intel_address ON wallet_intel(address);
CREATE INDEX IF NOT EXISTS idx_wallet_intel_chain ON wallet_intel(chain);
CREATE INDEX IF NOT EXISTS idx_wallet_intel_risk ON wallet_intel(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_telegram_users_tier ON telegram_users(tier);
CREATE INDEX IF NOT EXISTS idx_telegram_scans_telegram_id ON telegram_scans(telegram_id);
CREATE INDEX IF NOT EXISTS idx_telegram_scans_created_at ON telegram_scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_telegram_subscriptions_telegram_id ON telegram_subscriptions(telegram_id);
CREATE INDEX IF NOT EXISTS idx_telegram_broadcasts_channel ON telegram_broadcasts(channel_id);

-- Level & badge config (public read-only reference tables)
CREATE TABLE IF NOT EXISTS telegram_level_config (
    level INTEGER PRIMARY KEY,
    xp_required INTEGER NOT NULL,
    name TEXT NOT NULL,
    perks JSONB DEFAULT '{}'
);
ALTER TABLE telegram_level_config ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Level config public" ON telegram_level_config FOR SELECT USING (true);

INSERT INTO telegram_level_config (level, xp_required, name, perks) VALUES
    (1, 0, 'Rookie', '{"scans_bonus": 0}'),
    (2, 100, 'Scout', '{"scans_bonus": 2}'),
    (3, 300, 'Analyst', '{"scans_bonus": 5}'),
    (4, 600, 'Detective', '{"scans_bonus": 10}'),
    (5, 1000, 'Veteran', '{"scans_bonus": 15}'),
    (6, 2000, 'Legend', '{"scans_bonus": -1, "unlimited": true}')
ON CONFLICT (level) DO NOTHING;

CREATE TABLE IF NOT EXISTS telegram_badge_config (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    rarity TEXT DEFAULT 'common',
    icon TEXT,
    condition_type TEXT NOT NULL,
    condition_value INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 50
);
ALTER TABLE telegram_badge_config ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Badge config public" ON telegram_badge_config FOR SELECT USING (true);

INSERT INTO telegram_badge_config (id, name, description, rarity, icon, condition_type, condition_value, xp_reward) VALUES
    ('first_scan', 'First Blood', 'Performed your first scan', 'common', '🎯', 'scan_count', 1, 10),
    ('ten_scans', 'Scan Surgeon', 'Completed 10 scans', 'common', '🔬', 'scan_count', 10, 25),
    ('fifty_scans', 'Deep Diver', 'Completed 50 scans', 'uncommon', '🌊', 'scan_count', 50, 50),
    ('hundred_scans', 'Centurion', 'Completed 100 scans', 'rare', '⚔️', 'scan_count', 100, 100),
    ('five_hundred_scans', 'Oracle', 'Completed 500 scans', 'epic', '🔮', 'scan_count', 500, 250),
    ('seven_day_streak', 'Consistent', 'Scanned 7 days in a row', 'uncommon', '🔥', 'streak', 7, 50),
    ('thirty_day_streak', 'Obsessed', 'Scanned 30 days in a row', 'rare', '📅', 'streak', 30, 100),
    ('level_3', 'Rising Star', 'Reached Analyst level', 'uncommon', '⭐', 'level', 3, 50),
    ('level_5', 'Elite Hunter', 'Reached Veteran level', 'rare', '🏆', 'level', 5, 100),
    ('level_6', 'Legend', 'Reached Legend level', 'legendary', '👑', 'level', 6, 500),
    ('pro_subscriber', 'Pro Supporter', 'Subscribed to Pro tier', 'rare', '💎', 'tier', 1, 75),
    ('elite_subscriber', 'Elite Supporter', 'Subscribed to Elite tier', 'epic', '👑', 'tier', 2, 200)
ON CONFLICT (id) DO NOTHING;

-- Insert syndicate data (admin-only)
INSERT INTO syndicate_wallets (address, tier, role, balance, status, contract, notes)
VALUES
    ('H8sMJSCQjG3', 'Tier 0', 'Senior Origin', '39,815 SOL', 'active', 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS', 'SOSANA syndicate top level'),
    ('ASTyfSima', 'Tier 1', 'PBTC Treasury', '34,494 SOL', 'active', 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS', 'Parallel BTC treasury'),
    ('8eVZa7b', 'Tier 3', 'Multi-Token Hub', '48M CRM', 'staged', 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS', 'Multi-token staging'),
    ('JATcFT2j', 'Tier 4', 'Wave 2 Coordinator', '0.79 SOL', 'active', 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS', 'Secondary coordinator'),
    ('3TyLzagk', 'Tier 5', 'Field Operative', '12.40 SOL', 'armed', 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS', 'Field operative'),
    ('9Xx7usVB', 'Tier 5', 'Field Operative', '16.22 SOL', 'armed', 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS', 'Field operative')
ON CONFLICT (address) DO NOTHING;

-- Insert agent configs
INSERT INTO agents (name, role, tier, models, triggers, status)
VALUES
    ('nexus', 'Strategic Coordinator', 'T0', ARRAY['gemini-2.5-pro', 'nvidia/nemotron-4-340b'], ARRAY['strategize', 'plan', 'coordinate'], 'online'),
    ('scout', 'Alpha Hunter', 'T3', ARRAY['groq/llama-3.1-8b-instant', 'gemini-2.5-flash'], ARRAY['find', 'scan', 'hunt'], 'online'),
    ('tracer', 'Forensic Investigator', 'T1', ARRAY['gemini-2.5-pro', 'deepseek/deepseek-r1'], ARRAY['trace', 'investigate', 'wallet'], 'online'),
    ('cipher', 'Contract Auditor', 'T1', ARRAY['qwen/qwen2.5-coder-32b', 'deepseek/deepseek-coder-v2'], ARRAY['audit', 'security', 'contract'], 'online'),
    ('sentinel', 'Rug Detector', 'T2', ARRAY['deepseek/deepseek-r1', 'groq/llama-3.3-70b'], ARRAY['monitor', 'alert', 'rug'], 'online'),
    ('chronicler', 'Investigative Reporter', 'T2', ARRAY['deepseek/deepseek-r1', 'gemini-2.5-flash'], ARRAY['write', 'document', 'report'], 'online'),
    ('forge', 'Implementation Architect', 'T1', ARRAY['qwen/qwen2.5-coder-32b', 'deepseek/deepseek-coder-v2'], ARRAY['code', 'build', 'script'], 'online'),
    ('relay', 'Communications Coordinator', 'T3', ARRAY['groq/llama-3.1-8b-instant'], ARRAY['format', 'relay', 'notify'], 'online')
ON CONFLICT (name) DO NOTHING;
