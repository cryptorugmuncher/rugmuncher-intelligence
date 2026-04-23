-- RMI Profile Management Schema Extensions
-- Run this in Supabase SQL Editor to ensure tables support the profile system

-- ═══════════════════════════════════════════════════════════
-- PROFILES TABLE (extends existing auth.users / wallet-auth)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    username TEXT UNIQUE,
    display_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    website TEXT,
    twitter_handle TEXT,
    telegram_handle TEXT,
    wallet_address TEXT UNIQUE,
    chain_preference TEXT DEFAULT 'solana',
    role TEXT DEFAULT 'USER',
    tier TEXT DEFAULT 'free',
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    scans_remaining INTEGER DEFAULT 5,
    total_scans_used INTEGER DEFAULT 0,
    reputation_score INTEGER DEFAULT 0,
    onboarding_completed BOOLEAN DEFAULT false,
    interests JSONB DEFAULT '[]',
    chains JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add columns if table already exists (idempotent)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'profiles') THEN
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS username TEXT UNIQUE;
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS telegram_handle TEXT;
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS wallet_address TEXT;
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS chain_preference TEXT DEFAULT 'solana';
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS tier TEXT DEFAULT 'free';
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS scans_remaining INTEGER DEFAULT 5;
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS total_scans_used INTEGER DEFAULT 0;
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS reputation_score INTEGER DEFAULT 0;
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT false;
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS interests JSONB DEFAULT '[]';
        ALTER TABLE profiles ADD COLUMN IF NOT EXISTS chains JSONB DEFAULT '[]';
    END IF;
END
$$;

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Profiles public read" ON profiles FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Profiles owner write" ON profiles FOR ALL USING (
    auth.uid()::text = id OR auth.uid()::text = user_id::text OR
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_wallet ON profiles(wallet_address);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);

-- ═══════════════════════════════════════════════════════════
-- USER BADGES TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    badge_type TEXT NOT NULL,
    badge_name TEXT NOT NULL,
    awarded_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(profile_id, badge_type)
);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_badges') THEN
        ALTER TABLE user_badges ADD COLUMN IF NOT EXISTS profile_id TEXT;
        ALTER TABLE user_badges ADD COLUMN IF NOT EXISTS badge_name TEXT;
    END IF;
END
$$;

ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Badges public read" ON user_badges FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Badges owner write" ON user_badges FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE profiles.id = user_badges.profile_id AND (profiles.user_id = auth.uid() OR profiles.id = auth.uid()::text))
    OR EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE INDEX IF NOT EXISTS idx_user_badges_profile ON user_badges(profile_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_type ON user_badges(badge_type);

-- ═══════════════════════════════════════════════════════════
-- SCAN HISTORY TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS scan_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    contract_address TEXT NOT NULL,
    chain TEXT DEFAULT 'solana',
    risk_score NUMERIC DEFAULT 0,
    verdict TEXT,
    scan_result JSONB DEFAULT '{}',
    scanned_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE scan_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Scans own read" ON scan_history FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE profiles.id = scan_history.profile_id AND (profiles.user_id = auth.uid() OR profiles.id = auth.uid()::text))
);
CREATE POLICY IF NOT EXISTS "Scans owner write" ON scan_history FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE profiles.id = scan_history.profile_id AND (profiles.user_id = auth.uid() OR profiles.id = auth.uid()::text))
);

CREATE INDEX IF NOT EXISTS idx_scan_history_profile ON scan_history(profile_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_scanned_at ON scan_history(scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_history_contract ON scan_history(contract_address);

-- ═══════════════════════════════════════════════════════════
-- TRIGGER: auto-update updated_at on profiles
-- ═══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS profiles_updated_at_trigger ON profiles;
CREATE TRIGGER profiles_updated_at_trigger
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_updated_at();
