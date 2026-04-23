-- RMI Token Budget & Spending Tracker
-- Tracks API key usage, budgets, and free-tier prioritization

CREATE TABLE IF NOT EXISTS ai_provider_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT UNIQUE NOT NULL,
    display_name TEXT,
    is_free BOOLEAN DEFAULT false,
    is_free_tier BOOLEAN DEFAULT false,
    cost_per_1k_input DECIMAL(12,8) DEFAULT 0,
    cost_per_1k_output DECIMAL(12,8) DEFAULT 0,
    monthly_budget DECIMAL(12,4) DEFAULT 0,
    daily_budget DECIMAL(12,4) DEFAULT 0,
    rpm_limit INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 100,
    active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed provider configs with known pricing
INSERT INTO ai_provider_configs (provider, display_name, is_free, is_free_tier, cost_per_1k_input, cost_per_1k_output, monthly_budget, daily_budget, rpm_limit, priority, metadata)
VALUES
    ('workers-ai', 'Cloudflare Workers AI', true, false, 0, 0, 0, 0, 1000, 1, '{"type": "edge", "notes": "Free tier: 10k requests/day"}'),
    ('openrouter-free', 'OpenRouter Free', true, true, 0, 0, 0, 0, 200, 2, '{"type": "aggregator", "notes": "Free models only"}'),
    ('groq', 'Groq', false, false, 0.00005, 0.00008, 100, 5, 30, 10, '{"type": "fast", "notes": "Very fast, cheap"}'),
    ('openai', 'OpenAI', false, false, 0.0015, 0.002, 500, 20, 60, 20, '{"type": "premium"}'),
    ('anthropic', 'Anthropic', false, false, 0.003, 0.015, 500, 20, 60, 21, '{"type": "premium"}'),
    ('deepseek', 'DeepSeek', false, false, 0.00014, 0.00028, 200, 10, 60, 15, '{"type": "cheap"}'),
    ('fireworks', 'Fireworks', false, false, 0.0002, 0.0002, 200, 10, 60, 16, '{"type": "cheap"}'),
    ('gemini', 'Google Gemini', false, true, 0.000125, 0.000375, 300, 15, 60, 12, '{"type": "cheap", "notes": "Has generous free tier"}'),
    ('mistral', 'Mistral', false, false, 0.0002, 0.0006, 200, 10, 60, 17, '{"type": "cheap"}'),
    ('nvidia', 'NVIDIA', false, false, 0.0005, 0.0005, 200, 10, 20, 18, '{"type": "dev"}'),
    ('nvidia_dev', 'NVIDIA Dev', false, false, 0.0005, 0.0005, 200, 10, 500, 18, '{"type": "dev"}'),
    ('kimi', 'Kimi', false, false, 0.001, 0.002, 200, 10, 3, 25, '{"type": "premium"}'),
    ('together', 'Together AI', false, false, 0.0002, 0.0002, 200, 10, 60, 19, '{"type": "cheap"}')
ON CONFLICT (provider) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    is_free = EXCLUDED.is_free,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    priority = EXCLUDED.priority,
    metadata = EXCLUDED.metadata;

-- ═══════════════════════════════════════════════════════════
-- TOKEN SPENDING LOG
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS token_spending_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL,
    model TEXT,
    endpoint TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(12,8) DEFAULT 0,
    latency_ms INTEGER,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_spending_provider ON token_spending_log(provider);
CREATE INDEX IF NOT EXISTS idx_spending_created ON token_spending_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_spending_status ON token_spending_log(status);

-- ═══════════════════════════════════════════════════════════
-- DAILY/MONTHLY AGGREGATE VIEWS
-- ═══════════════════════════════════════════════════════════
CREATE OR REPLACE VIEW daily_spending AS
SELECT
    provider,
    DATE(created_at) as date,
    COUNT(*) as request_count,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(total_tokens) as total_tokens,
    SUM(estimated_cost) as total_cost,
    AVG(latency_ms) as avg_latency_ms
FROM token_spending_log
WHERE status = 'success'
GROUP BY provider, DATE(created_at);

CREATE OR REPLACE VIEW monthly_spending AS
SELECT
    provider,
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as request_count,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(total_tokens) as total_tokens,
    SUM(estimated_cost) as total_cost,
    AVG(latency_ms) as avg_latency_ms
FROM token_spending_log
WHERE status = 'success'
GROUP BY provider, DATE_TRUNC('month', created_at);
