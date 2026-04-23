-- ============================================
-- RMI Gamification & Social Profiles Database Setup
-- Adds tables for user profiles, gamification, and social linking
-- ============================================

-- ============================================
-- USER PROFILE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    banner_url TEXT,
    location TEXT,
    website TEXT,
    
    -- Legacy social handles
    twitter_handle TEXT,
    telegram_handle TEXT,
    discord_handle TEXT,
    
    -- Crypto-native social profiles
    farcaster_fid INTEGER,
    farcaster_handle TEXT,
    lens_handle TEXT,
    lens_profile_id TEXT,
    base_app_username TEXT,
    base_app_address TEXT,
    github_username TEXT,
    
    -- Verification status
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_method TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE
);

-- User social links table (detailed linking)
CREATE TABLE IF NOT EXISTS user_social_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    platform TEXT NOT NULL, -- twitter, farcaster, lens, base_app, github, telegram, discord
    handle TEXT NOT NULL,
    url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_hash TEXT, -- Hash of expected verification message
    verification_proof TEXT, -- Tweet ID, signature, gist URL, etc.
    follower_count INTEGER,
    display_on_profile BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

-- User settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    settings_json JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- User connections/friendships
CREATE TABLE IF NOT EXISTS user_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    recipient_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending', -- pending, accepted, rejected, blocked
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accepted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(requester_id, recipient_id)
);

-- ============================================
-- GAMIFICATION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS user_gamification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    xp_total INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    scans_total INTEGER DEFAULT 0,
    rugs_detected INTEGER DEFAULT 0,
    referrals_total INTEGER DEFAULT 0,
    login_streak INTEGER DEFAULT 0,
    badges JSONB DEFAULT '[]',
    achievements JSONB DEFAULT '[]',
    last_login TIMESTAMP WITH TIME ZONE,
    last_active TIMESTAMP WITH TIME ZONE,
    is_premium BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Leaderboard table
CREATE TABLE IF NOT EXISTS leaderboard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    category TEXT NOT NULL, -- xp, scans, rugs_detected, referrals, streak
    period TEXT NOT NULL, -- daily, weekly, monthly, all_time
    score INTEGER DEFAULT 0,
    rank INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, category, period)
);

-- User activity log
CREATE TABLE IF NOT EXISTS user_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL,
    activity_data JSONB DEFAULT '{}',
    xp_gained INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- MONETIZATION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    tier TEXT DEFAULT 'free', -- free, basic, pro, enterprise
    status TEXT DEFAULT 'active', -- active, cancelled, expired
    billing_cycle TEXT DEFAULT 'monthly', -- monthly, yearly, pay_as_you_go
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    credits_balance INTEGER DEFAULT 0,
    credits_reset_at TIMESTAMP WITH TIME ZONE,
    auto_renew BOOLEAN DEFAULT TRUE,
    payment_method_id TEXT,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    amount INTEGER NOT NULL, -- positive for credit, negative for debit
    transaction_type TEXT NOT NULL, -- purchase, usage, bonus, refund
    description TEXT,
    reference_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    credits_used INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    status_code INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS revenue_share (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    period_start DATE,
    period_end DATE,
    total_revenue DECIMAL(20, 8),
    user_share DECIMAL(20, 8),
    status TEXT DEFAULT 'pending', -- pending, paid, failed
    paid_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, period_start)
);

-- ============================================
-- USER STATS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    total_scans INTEGER DEFAULT 0,
    total_verifications INTEGER DEFAULT 0,
    total_reports INTEGER DEFAULT 0,
    total_alerts_created INTEGER DEFAULT 0,
    total_alerts_triggered INTEGER DEFAULT 0,
    rugs_detected INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5, 2) DEFAULT 0.00,
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    reputation_score DECIMAL(5, 2) DEFAULT 0.00,
    total_scan_time_ms BIGINT DEFAULT 0,
    avg_response_time_ms INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ============================================
-- INDEXES
-- ============================================

-- User profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);
CREATE INDEX IF NOT EXISTS idx_user_profiles_verified ON user_profiles(is_verified);
CREATE INDEX IF NOT EXISTS idx_user_profiles_twitter ON user_profiles(twitter_handle) WHERE twitter_handle IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_profiles_farcaster ON user_profiles(farcaster_handle) WHERE farcaster_handle IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_profiles_lens ON user_profiles(lens_handle) WHERE lens_handle IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_profiles_base ON user_profiles(base_app_username) WHERE base_app_username IS NOT NULL;

-- Social links
CREATE INDEX IF NOT EXISTS idx_social_links_user ON user_social_links(user_id);
CREATE INDEX IF NOT EXISTS idx_social_links_platform ON user_social_links(platform);
CREATE INDEX IF NOT EXISTS idx_social_links_verified ON user_social_links(user_id, platform) WHERE is_verified = TRUE;

-- Gamification
CREATE INDEX IF NOT EXISTS idx_gamification_user ON user_gamification(user_id);
CREATE INDEX IF NOT EXISTS idx_gamification_xp ON user_gamification(xp_total DESC);
CREATE INDEX IF NOT EXISTS idx_gamification_scans ON user_gamification(scans_total DESC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_category ON leaderboard(category, period, score DESC);
CREATE INDEX IF NOT EXISTS idx_activity_user ON user_activity(user_id, timestamp DESC);

-- Monetization
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON credit_transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_user ON api_usage(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_revenue_share_user ON revenue_share(user_id, period_start);

-- ============================================
-- RLS POLICIES
-- ============================================

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_social_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_gamification ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- Users can view their own data
CREATE POLICY "Users view own profile" ON user_profiles
    FOR SELECT USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Users update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Public view profiles" ON user_profiles
    FOR SELECT USING (true);

-- Social links policies
CREATE POLICY "Users manage own social links" ON user_social_links
    FOR ALL USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Public view social links" ON user_social_links
    FOR SELECT USING (display_on_profile = true);

-- Service role full access policies
CREATE POLICY "Service role user profiles" ON user_profiles FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role social links" ON user_social_links FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role settings" ON user_settings FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role connections" ON user_connections FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role gamification" ON user_gamification FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role activity" ON user_activity FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role subscriptions" ON user_subscriptions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role credit transactions" ON credit_transactions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role api usage" ON api_usage FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- TRIGGERS
-- ============================================

-- Update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_social_links_updated_at BEFORE UPDATE ON user_social_links
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_connections_updated_at BEFORE UPDATE ON user_connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_gamification_updated_at BEFORE UPDATE ON user_gamification
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS
-- ============================================

-- User profile summary view with social counts
CREATE OR REPLACE VIEW user_profile_summary AS
SELECT 
    p.*,
    g.xp_total,
    g.level,
    g.scans_total,
    g.badges,
    s.credits_balance,
    s.tier as subscription_tier,
    COUNT(DISTINCT sl.id) FILTER (WHERE sl.is_verified = true) as verified_social_count,
    COUNT(DISTINCT sl.id) as total_social_links
FROM user_profiles p
LEFT JOIN user_gamification g ON p.user_id = g.user_id
LEFT JOIN user_subscriptions s ON p.user_id = s.user_id
LEFT JOIN user_social_links sl ON p.user_id = sl.user_id
GROUP BY p.id, g.id, s.id;

-- Leaderboard view
CREATE OR REPLACE VIEW leaderboard_all_time AS
SELECT 
    p.user_id,
    p.username,
    p.display_name,
    p.avatar_url,
    g.xp_total as score,
    RANK() OVER (ORDER BY g.xp_total DESC) as rank
FROM user_profiles p
JOIN user_gamification g ON p.user_id = g.user_id
WHERE g.xp_total > 0
ORDER BY g.xp_total DESC;
