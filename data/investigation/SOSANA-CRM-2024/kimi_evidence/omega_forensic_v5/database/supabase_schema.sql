-- ============================================================================
-- RMI (RugMunch Intelligence) - Complete Supabase Database Schema
-- 
-- Instructions:
-- 1. Go to your Supabase project dashboard
-- 2. Navigate to SQL Editor
-- 3. Click "New Query"
-- 4. Paste this entire file
-- 5. Click "Run"
-- 
-- This creates all tables, indexes, triggers, and RLS policies
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    wallet_address TEXT UNIQUE,
    display_name TEXT,
    avatar_url TEXT,
    is_crm_holder BOOLEAN DEFAULT FALSE,
    crm_balance NUMERIC(20, 9) DEFAULT 0,
    subscription_tier TEXT DEFAULT 'free',
    scans_remaining INTEGER DEFAULT 5,
    total_scans_used INTEGER DEFAULT 0,
    reputation_score INTEGER DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Investigations/Cases table
CREATE TABLE IF NOT EXISTS public.investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    token_address TEXT,
    token_symbol TEXT,
    chain TEXT DEFAULT 'solana',
    status TEXT DEFAULT 'active',
    risk_level TEXT DEFAULT 'unknown',
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Evidence files table
CREATE TABLE IF NOT EXISTS public.evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES public.investigations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    storage_path TEXT NOT NULL,
    content_hash TEXT UNIQUE,
    source TEXT,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE,
    processing_status TEXT DEFAULT 'pending',
    extracted_text TEXT,
    ai_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- FORENSIC TABLES
-- ============================================================================

-- Wallet analysis results
CREATE TABLE IF NOT EXISTS public.wallet_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES public.investigations(id) ON DELETE CASCADE,
    wallet_address TEXT NOT NULL,
    chain TEXT DEFAULT 'solana',
    analysis_type TEXT NOT NULL,
    risk_score INTEGER,
    risk_level TEXT,
    tags TEXT[] DEFAULT '{}',
    connections JSONB DEFAULT '{}',
    transaction_stats JSONB DEFAULT '{}',
    token_holdings JSONB DEFAULT '{}',
    findings JSONB DEFAULT '{}',
    related_scams TEXT[] DEFAULT '{}',
    behavioral_profile JSONB DEFAULT '{}',
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

-- Token/Contract analysis
CREATE TABLE IF NOT EXISTS public.token_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES public.investigations(id) ON DELETE CASCADE,
    token_address TEXT NOT NULL,
    chain TEXT DEFAULT 'solana',
    token_symbol TEXT,
    token_name TEXT,
    analysis_type TEXT NOT NULL,
    risk_score INTEGER,
    risk_level TEXT,
    mint_authority TEXT,
    freeze_authority TEXT,
    supply_info JSONB DEFAULT '{}',
    holder_analysis JSONB DEFAULT '{}',
    liquidity_analysis JSONB DEFAULT '{}',
    contract_flags TEXT[] DEFAULT '{}',
    findings JSONB DEFAULT '{}',
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

-- Cluster detection results
CREATE TABLE IF NOT EXISTS public.cluster_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES public.investigations(id) ON DELETE CASCADE,
    cluster_id TEXT NOT NULL,
    wallets TEXT[] NOT NULL,
    detection_methods TEXT[] DEFAULT '{}',
    confidence_score NUMERIC(5, 2),
    cluster_type TEXT,
    behavior_tags TEXT[] DEFAULT '{}',
    transaction_patterns JSONB DEFAULT '{}',
    funding_sources TEXT[] DEFAULT '{}',
    common_counterparties TEXT[] DEFAULT '{}',
    temporal_analysis JSONB DEFAULT '{}',
    related_clusters TEXT[] DEFAULT '{}',
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

-- Bubble map data
CREATE TABLE IF NOT EXISTS public.bubble_maps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES public.investigations(id) ON DELETE CASCADE,
    center_wallet TEXT NOT NULL,
    depth INTEGER DEFAULT 2,
    map_data JSONB NOT NULL,
    node_count INTEGER,
    edge_count INTEGER,
    cluster_count INTEGER,
    interactive_html TEXT,
    export_paths JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

-- ============================================================================
-- KOL TRACKING TABLES
-- ============================================================================

-- KOL (Key Opinion Leader) profiles
CREATE TABLE IF NOT EXISTS public.kol_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    handle TEXT UNIQUE NOT NULL,
    platform TEXT NOT NULL,
    display_name TEXT,
    bio TEXT,
    follower_count INTEGER,
    verified_wallets TEXT[] DEFAULT '{}',
    reputation_score INTEGER DEFAULT 50,
    accuracy_score NUMERIC(5, 2),
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    failed_calls INTEGER DEFAULT 0,
    rug_signals INTEGER DEFAULT 0,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- KOL wallet tracking
CREATE TABLE IF NOT EXISTS public.kol_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kol_id UUID REFERENCES public.kol_profiles(id) ON DELETE CASCADE,
    wallet_address TEXT NOT NULL,
    chain TEXT DEFAULT 'solana',
    verification_status TEXT DEFAULT 'unverified',
    verification_method TEXT,
    first_seen TIMESTAMPTZ,
    last_active TIMESTAMPTZ,
    total_trades INTEGER DEFAULT 0,
    pnl_30d NUMERIC(20, 9) DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    UNIQUE(kol_id, wallet_address)
);

-- KOL token calls
CREATE TABLE IF NOT EXISTS public.kol_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kol_id UUID REFERENCES public.kol_profiles(id) ON DELETE CASCADE,
    token_address TEXT NOT NULL,
    token_symbol TEXT,
    call_type TEXT NOT NULL, -- 'buy', 'sell', 'shill', 'warn'
    platform TEXT,
    post_url TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    price_at_call NUMERIC(20, 9),
    current_price NUMERIC(20, 9),
    performance_24h NUMERIC(10, 4),
    performance_7d NUMERIC(10, 4),
    verified BOOLEAN DEFAULT FALSE,
    wallet_activity_match BOOLEAN,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- KOL positions
CREATE TABLE IF NOT EXISTS public.kol_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kol_id UUID REFERENCES public.kol_profiles(id) ON DELETE CASCADE,
    wallet_address TEXT NOT NULL,
    token_address TEXT NOT NULL,
    token_symbol TEXT,
    amount NUMERIC(20, 9),
    value_usd NUMERIC(20, 2),
    entry_price NUMERIC(20, 9),
    current_price NUMERIC(20, 9),
    unrealized_pnl NUMERIC(20, 2),
    realized_pnl NUMERIC(20, 2),
    first_acquired TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(kol_id, wallet_address, token_address)
);

-- ============================================================================
-- PREMIUM & PAYMENT TABLES
-- ============================================================================

-- Scan packages
CREATE TABLE IF NOT EXISTS public.scan_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    package_type TEXT NOT NULL,
    scan_count INTEGER NOT NULL,
    base_price_usd NUMERIC(10, 2),
    crm_discount_percent INTEGER DEFAULT 0,
    features TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User scan purchases
CREATE TABLE IF NOT EXISTS public.scan_purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    package_id UUID REFERENCES public.scan_packages(id),
    scans_purchased INTEGER NOT NULL,
    scans_remaining INTEGER NOT NULL,
    amount_paid NUMERIC(10, 2),
    currency TEXT DEFAULT 'USDC',
    transaction_signature TEXT,
    payment_status TEXT DEFAULT 'pending',
    is_crm_holder BOOLEAN DEFAULT FALSE,
    discount_applied NUMERIC(10, 2) DEFAULT 0,
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- API marketplace packages
CREATE TABLE IF NOT EXISTS public.api_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    package_key TEXT UNIQUE NOT NULL,
    provider TEXT NOT NULL,
    tier TEXT NOT NULL,
    credits INTEGER NOT NULL,
    bonus_credits INTEGER DEFAULT 0,
    base_price_usd NUMERIC(10, 2),
    discount_percent INTEGER DEFAULT 0,
    features TEXT[] DEFAULT '{}',
    rate_limit_per_min INTEGER DEFAULT 100,
    validity_days INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE
);

-- User API credits
CREATE TABLE IF NOT EXISTS public.user_api_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    package_id UUID REFERENCES public.api_packages(id),
    provider TEXT NOT NULL,
    credits_remaining INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    rate_limit_per_min INTEGER DEFAULT 100,
    activated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

-- API usage tracking
CREATE TABLE IF NOT EXISTS public.api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    endpoint TEXT,
    credits_used INTEGER DEFAULT 1,
    response_time_ms INTEGER,
    status_code INTEGER,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Pending payments
CREATE TABLE IF NOT EXISTS public.pending_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    item_type TEXT NOT NULL, -- 'scan_pack', 'api_credits', 'subscription'
    item_id UUID,
    amount_usdc NUMERIC(10, 2) NOT NULL,
    recipient_wallet TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    transaction_signature TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 minutes'),
    completed_at TIMESTAMPTZ
);

-- ============================================================================
-- TRANSPARENCY TRACKER TABLES
-- ============================================================================

-- Project transparency scores
CREATE TABLE IF NOT EXISTS public.transparency_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_address TEXT NOT NULL,
    chain TEXT DEFAULT 'solana',
    token_symbol TEXT,
    overall_score INTEGER,
    overall_grade TEXT,
    percentile_rank INTEGER,
    category_scores JSONB DEFAULT '{}',
    red_flags TEXT[] DEFAULT '{}',
    green_flags TEXT[] DEFAULT '{}',
    team_info JSONB DEFAULT '{}',
    contract_info JSONB DEFAULT '{}',
    treasury_info JSONB DEFAULT '{}',
    audit_info JSONB DEFAULT '{}',
    roadmap_info JSONB DEFAULT '{}',
    assessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'),
    UNIQUE(token_address, chain)
);

-- Transparency assessments history
CREATE TABLE IF NOT EXISTS public.transparency_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_address TEXT NOT NULL,
    score INTEGER,
    grade TEXT,
    changes JSONB DEFAULT '{}',
    assessed_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- NOTIFICATION & ALERT TABLES
-- ============================================================================

-- User notifications
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert subscriptions
CREATE TABLE IF NOT EXISTS public.alert_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL,
    target_address TEXT,
    target_type TEXT,
    conditions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Profile indexes
CREATE INDEX idx_profiles_wallet ON public.profiles(wallet_address);
CREATE INDEX idx_profiles_crm_holder ON public.profiles(is_crm_holder);

-- Investigation indexes
CREATE INDEX idx_investigations_user ON public.investigations(user_id);
CREATE INDEX idx_investigations_token ON public.investigations(token_address);
CREATE INDEX idx_investigations_status ON public.investigations(status);
CREATE INDEX idx_investigations_created ON public.investigations(created_at DESC);

-- Evidence indexes
CREATE INDEX idx_evidence_investigation ON public.evidence(investigation_id);
CREATE INDEX idx_evidence_hash ON public.evidence(content_hash);
CREATE INDEX idx_evidence_type ON public.evidence(file_type);

-- Wallet analysis indexes
CREATE INDEX idx_wallet_analysis_investigation ON public.wallet_analyses(investigation_id);
CREATE INDEX idx_wallet_analysis_address ON public.wallet_analyses(wallet_address);
CREATE INDEX idx_wallet_analysis_risk ON public.wallet_analyses(risk_score);
CREATE INDEX idx_wallet_analysis_expires ON public.wallet_analyses(expires_at);

-- Token analysis indexes
CREATE INDEX idx_token_analysis_token ON public.token_analyses(token_address);
CREATE INDEX idx_token_analysis_risk ON public.token_analyses(risk_score);

-- Cluster indexes
CREATE INDEX idx_cluster_analysis_investigation ON public.cluster_analyses(investigation_id);
CREATE INDEX idx_cluster_analysis_cluster_id ON public.cluster_analyses(cluster_id);

-- KOL indexes
CREATE INDEX idx_kol_profiles_handle ON public.kol_profiles(handle);
CREATE INDEX idx_kol_profiles_platform ON public.kol_profiles(platform);
CREATE INDEX idx_kol_wallets_address ON public.kol_wallets(wallet_address);
CREATE INDEX idx_kol_calls_kol ON public.kol_calls(kol_id);
CREATE INDEX idx_kol_calls_token ON public.kol_calls(token_address);
CREATE INDEX idx_kol_positions_kol ON public.kol_positions(kol_id);
CREATE INDEX idx_kol_positions_token ON public.kol_positions(token_address);

-- Payment indexes
CREATE INDEX idx_scan_purchases_user ON public.scan_purchases(user_id);
CREATE INDEX idx_pending_payments_payment_id ON public.pending_payments(payment_id);
CREATE INDEX idx_pending_payments_user ON public.pending_payments(user_id);

-- API indexes
CREATE INDEX idx_user_api_credits_user ON public.user_api_credits(user_id);
CREATE INDEX idx_user_api_credits_provider ON public.user_api_credits(provider);
CREATE INDEX idx_api_usage_user ON public.api_usage(user_id);
CREATE INDEX idx_api_usage_timestamp ON public.api_usage(timestamp DESC);

-- Transparency indexes
CREATE INDEX idx_transparency_token ON public.transparency_scores(token_address);
CREATE INDEX idx_transparency_score ON public.transparency_scores(overall_score);

-- Notification indexes
CREATE INDEX idx_notifications_user ON public.notifications(user_id);
CREATE INDEX idx_notifications_unread ON public.notifications(user_id, is_read) WHERE is_read = FALSE;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investigations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallet_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.token_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cluster_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bubble_maps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kol_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kol_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kol_calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kol_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_api_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pending_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_subscriptions ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can read/update their own profile
CREATE POLICY "Users can view own profile" 
    ON public.profiles FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
    ON public.profiles FOR UPDATE 
    USING (auth.uid() = id);

-- Investigations: Users can CRUD their own investigations
CREATE POLICY "Users can view own investigations" 
    ON public.investigations FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create investigations" 
    ON public.investigations FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own investigations" 
    ON public.investigations FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own investigations" 
    ON public.investigations FOR DELETE 
    USING (auth.uid() = user_id);

-- Evidence: Users can CRUD evidence in their investigations
CREATE POLICY "Users can view own evidence" 
    ON public.evidence FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create evidence" 
    ON public.evidence FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own evidence" 
    ON public.evidence FOR DELETE 
    USING (auth.uid() = user_id);

-- Analyses: Users can view analyses for their investigations
CREATE POLICY "Users can view own wallet analyses" 
    ON public.wallet_analyses FOR SELECT 
    USING (EXISTS (
        SELECT 1 FROM public.investigations 
        WHERE id = wallet_analyses.investigation_id 
        AND user_id = auth.uid()
    ));

CREATE POLICY "Users can view own token analyses" 
    ON public.token_analyses FOR SELECT 
    USING (EXISTS (
        SELECT 1 FROM public.investigations 
        WHERE id = token_analyses.investigation_id 
        AND user_id = auth.uid()
    ));

CREATE POLICY "Users can view own cluster analyses" 
    ON public.cluster_analyses FOR SELECT 
    USING (EXISTS (
        SELECT 1 FROM public.investigations 
        WHERE id = cluster_analyses.investigation_id 
        AND user_id = auth.uid()
    ));

CREATE POLICY "Users can view own bubble maps" 
    ON public.bubble_maps FOR SELECT 
    USING (EXISTS (
        SELECT 1 FROM public.investigations 
        WHERE id = bubble_maps.investigation_id 
        AND user_id = auth.uid()
    ));

-- KOL data: Public read access
CREATE POLICY "KOL profiles are public" 
    ON public.kol_profiles FOR SELECT 
    TO PUBLIC USING (true);

CREATE POLICY "KOL wallets are public" 
    ON public.kol_wallets FOR SELECT 
    TO PUBLIC USING (true);

CREATE POLICY "KOL calls are public" 
    ON public.kol_calls FOR SELECT 
    TO PUBLIC USING (true);

CREATE POLICY "KOL positions are public" 
    ON public.kol_positions FOR SELECT 
    TO PUBLIC USING (true);

-- Payments: Users can view their own
CREATE POLICY "Users can view own scan purchases" 
    ON public.scan_purchases FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own API credits" 
    ON public.user_api_credits FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own API usage" 
    ON public.api_usage FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own pending payments" 
    ON public.pending_payments FOR SELECT 
    USING (auth.uid() = user_id);

-- Notifications: Users can CRUD their own
CREATE POLICY "Users can view own notifications" 
    ON public.notifications FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" 
    ON public.notifications FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own notifications" 
    ON public.notifications FOR DELETE 
    USING (auth.uid() = user_id);

-- Alert subscriptions: Users can CRUD their own
CREATE POLICY "Users can view own alert subscriptions" 
    ON public.alert_subscriptions FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create alert subscriptions" 
    ON public.alert_subscriptions FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own alert subscriptions" 
    ON public.alert_subscriptions FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own alert subscriptions" 
    ON public.alert_subscriptions FOR DELETE 
    USING (auth.uid() = user_id);

-- Transparency scores: Public read
CREATE POLICY "Transparency scores are public" 
    ON public.transparency_scores FOR SELECT 
    TO PUBLIC USING (true);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables with updated_at
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON public.profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_investigations_updated_at 
    BEFORE UPDATE ON public.investigations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_kol_profiles_updated_at 
    BEFORE UPDATE ON public.kol_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, wallet_address, scans_remaining)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data->>'wallet_address',
        5  -- Free starter scans
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to deduct scan on usage
CREATE OR REPLACE FUNCTION deduct_scan(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    remaining INTEGER;
BEGIN
    SELECT scans_remaining INTO remaining 
    FROM public.profiles 
    WHERE id = p_user_id;
    
    IF remaining > 0 THEN
        UPDATE public.profiles 
        SET scans_remaining = scans_remaining - 1,
            total_scans_used = total_scans_used + 1
        WHERE id = p_user_id;
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean expired data
CREATE OR REPLACE FUNCTION clean_expired_data()
RETURNS void AS $$
BEGIN
    DELETE FROM public.wallet_analyses WHERE expires_at < NOW();
    DELETE FROM public.token_analyses WHERE expires_at < NOW();
    DELETE FROM public.cluster_analyses WHERE expires_at < NOW();
    DELETE FROM public.bubble_maps WHERE expires_at < NOW();
    DELETE FROM public.transparency_scores WHERE expires_at < NOW();
    DELETE FROM public.pending_payments WHERE expires_at < NOW() AND status = 'pending';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Insert default scan packages
INSERT INTO public.scan_packages (name, package_type, scan_count, base_price_usd, crm_discount_percent, features) VALUES
('Starter Pack', 'starter', 10, 10.00, 50, ARRAY['Contract Check', 'Basic Wallet Investigation']),
('Pro Pack', 'pro', 50, 35.00, 50, ARRAY['Contract Check', 'Deep Wallet Analysis', 'Cluster Detection', 'Bubble Map']),
('Whale Pack', 'whale', 200, 100.00, 50, ARRAY['All Pro Features', 'KOL Tracking', 'Priority Processing']),
('Unlimited Monthly', 'unlimited', 999999, 250.00, 50, ARRAY['Unlimited Scans', 'All Features', 'API Access', 'Priority Support'])
ON CONFLICT DO NOTHING;

-- Insert API packages
INSERT INTO public.api_packages (package_key, provider, tier, credits, bonus_credits, base_price_usd, discount_percent, features, rate_limit_per_min, validity_days) VALUES
('birdeye_starter', 'birdeye', 'starter', 10000, 0, 25.00, 50, ARRAY['Token Prices', 'OHLCV Data', 'Token List'], 300, 30),
('birdeye_pro', 'birdeye', 'pro', 50000, 5000, 100.00, 60, ARRAY['All Starter', 'Wallet Portfolio', 'Transaction History'], 600, 30),
('birdeye_whale', 'birdeye', 'whale', 200000, 30000, 300.00, 70, ARRAY['All Pro', 'New Pairs', 'Trending Tokens'], 1200, 30),
('helius_starter', 'helius', 'starter', 50000, 0, 35.00, 53, ARRAY['RPC Calls', 'NFT APIs', 'Parsed Transactions'], 500, 30),
('helius_pro', 'helius', 'pro', 250000, 25000, 140.00, 60, ARRAY['All Starter', 'Enhanced APIs'], 1000, 30),
('helius_whale', 'helius', 'whale', 1000000, 150000, 450.00, 68, ARRAY['All Pro', 'Dedicated Resources'], 2000, 30),
('shyft_starter', 'shyft', 'starter', 20000, 0, 20.00, 50, ARRAY['Wallet APIs', 'NFT APIs', 'Token APIs'], 300, 30),
('shyft_pro', 'shyft', 'pro', 100000, 10000, 80.00, 60, ARRAY['All Starter', 'Bulk Operations'], 600, 30),
('quicknode_starter', 'quicknode', 'starter', 100000, 0, 50.00, 50, ARRAY['Core RPC', 'Token API', 'NFT API'], 600, 30),
('quicknode_pro', 'quicknode', 'pro', 500000, 50000, 200.00, 60, ARRAY['All Starter', 'Add-ons'], 1200, 30),
('bundle_forensic', 'bundle', 'whale', 400000, 50000, 299.00, 62, ARRAY['Birdeye 100K', 'Helius 100K', 'Shyft 100K', 'Bitquery 50K'], 800, 30),
('bundle_unlimited', 'bundle', 'enterprise', 2000000, 500000, 999.00, 70, ARRAY['All Providers', 'Enterprise SLA', 'Dedicated Support'], 5000, 90)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

SELECT 'RMI Database Schema Created Successfully!' as status;
SELECT concat(
    'Tables created: ', 
    (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public')
) as tables_count;
