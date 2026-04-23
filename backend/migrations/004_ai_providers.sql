-- ═══════════════════════════════════════════════════════════
-- Migration: 004_ai_providers
-- Description: Centralized AI provider configuration table.
--              Replaces all hardcoded provider configs in both
--              the backend and the Cloudflare Worker.
-- ═══════════════════════════════════════════════════════════

-- Drop table if re-running (useful for dev resets)
-- DROP TABLE IF EXISTS ai_providers CASCADE;

CREATE TABLE IF NOT EXISTS ai_providers (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    provider_type       TEXT NOT NULL,
    base_url            TEXT,
    header_name         TEXT DEFAULT 'Authorization',
    default_model       TEXT,
    rpm_limit           INTEGER DEFAULT 60,
    models              TEXT[] DEFAULT '{}',
    capabilities        TEXT[] DEFAULT '{}',
    is_free_tier        BOOLEAN DEFAULT false,
    is_enabled          BOOLEAN DEFAULT true,
    weight              FLOAT DEFAULT 1.0,
    cost_per_1k_input   FLOAT DEFAULT 0,
    cost_per_1k_output  FLOAT DEFAULT 0,
    free_quota_type     TEXT,            -- 'daily_requests', 'free_credits', 'unlimited_requests', null
    free_quota_limit    INTEGER,
    free_quota_unit     TEXT DEFAULT 'requests', -- 'requests' or 'usd'
    secret_env_var      TEXT,
    priority            INTEGER DEFAULT 0, -- free chain priority (lower = first)
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups by type / free-tier status / priority
CREATE INDEX IF NOT EXISTS idx_ai_providers_type
    ON ai_providers(provider_type);

CREATE INDEX IF NOT EXISTS idx_ai_providers_free_enabled
    ON ai_providers(is_free_tier, is_enabled, priority);

CREATE INDEX IF NOT EXISTS idx_ai_providers_enabled_weight
    ON ai_providers(is_enabled, weight DESC);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_ai_providers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ai_providers_updated_at ON ai_providers;
CREATE TRIGGER trg_ai_providers_updated_at
    BEFORE UPDATE ON ai_providers
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_providers_updated_at();

-- ═══════════════════════════════════════════════════════════
-- SEED DATA — All current providers
-- ═══════════════════════════════════════════════════════════

-- 1. 🆓 FREE — Cloudflare Workers AI
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'workers-ai', 'Cloudflare Workers AI', 'workers-ai', '', 'Authorization',
    '@cf/meta/llama-3.1-8b-instruct',
    10000,
    ARRAY['@cf/meta/llama-3.1-8b-instruct', '@cf/baai/bge-base-en-v1.5'],
    ARRAY['chat', 'embeddings'],
    true, true, 10.0,
    0, 0,
    'daily_requests', 10000, 'requests',
    '', 1
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 2. 🆓 FREE — OpenRouter free models
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'openrouter-free', 'OpenRouter Free', 'openrouter', 'https://openrouter.ai/api/v1', 'Authorization',
    'openrouter/free',
    200,
    ARRAY['openrouter/free'],
    ARRAY['chat'],
    true, true, 8.0,
    0, 0,
    'unlimited_requests', 999999, 'requests',
    'OPENROUTER_API_KEY', 2
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 3. 🆓 FREE TIER — Google Gemini
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'gemini-free', 'Gemini Free', 'gemini', 'https://generativelanguage.googleapis.com/v1beta/models', 'Authorization',
    'gemini-1.5-flash',
    1500,
    ARRAY['gemini-1.5-flash', 'gemini-1.5-pro'],
    ARRAY['chat', 'vision', 'json_mode'],
    true, true, 7.0,
    0.000125, 0.000375,
    'daily_requests', 1500, 'requests',
    'GEMINI_API_KEY', 3
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 4. 🆓 FREE CREDITS — Groq
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'groq-free', 'Groq Free', 'groq', 'https://api.groq.com/openai/v1', 'Authorization',
    'llama-3.3-70b-versatile',
    30,
    ARRAY['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'gemma2-9b-it'],
    ARRAY['chat', 'json_mode', 'fast'],
    true, true, 6.0,
    0.00005, 0.00008,
    'free_credits', 5, 'usd',
    'GROQ_API_KEY', 4
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 5. 💰 PAID — OpenAI
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'openai-main', 'OpenAI', 'openai', 'https://api.openai.com/v1', 'Authorization',
    'gpt-4o',
    60,
    ARRAY['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
    ARRAY['chat', 'vision', 'json_mode', 'function_calling'],
    false, true, 4.0,
    0.00150, 0.00200,
    NULL, NULL, 'requests',
    'OPENAI_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 6. 💰 PAID — Anthropic
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'anthropic-main', 'Anthropic', 'anthropic', 'https://api.anthropic.com/v1', 'Authorization',
    'claude-sonnet-4-20250514',
    60,
    ARRAY['claude-sonnet-4-20250514', 'claude-haiku-20240307'],
    ARRAY['chat', 'vision', 'long_context'],
    false, true, 3.0,
    0.00300, 0.01500,
    NULL, NULL, 'requests',
    'ANTHROPIC_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 7. 💰 PAID — DeepSeek
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'deepseek-main', 'DeepSeek', 'deepseek', 'https://api.deepseek.com/v1', 'Authorization',
    'deepseek-chat',
    60,
    ARRAY['deepseek-chat', 'deepseek-coder'],
    ARRAY['chat', 'coding'],
    false, true, 5.0,
    0.00014, 0.00028,
    NULL, NULL, 'requests',
    'DEEPSEEK_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 8. 💰 PAID — Fireworks
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'fireworks-main', 'Fireworks', 'fireworks', 'https://api.fireworks.ai/inference/v1', 'Authorization',
    'accounts/fireworks/models/llama-v3p1-8b-instruct',
    60,
    ARRAY['accounts/fireworks/models/llama-v3p1-8b-instruct'],
    ARRAY['chat', 'fast'],
    false, true, 5.0,
    0.00020, 0.00020,
    NULL, NULL, 'requests',
    'FIREWORKS_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 9. 💰 PAID — Mistral
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'mistral-main', 'Mistral', 'mistral', 'https://api.mistral.ai/v1', 'Authorization',
    'mistral-large-latest',
    60,
    ARRAY['mistral-large-latest', 'mistral-medium'],
    ARRAY['chat', 'json_mode'],
    false, true, 4.0,
    0.00020, 0.00060,
    NULL, NULL, 'requests',
    'MISTRAL_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 10. 💰 PAID — Together AI
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'together-main', 'Together AI', 'together', 'https://api.together.xyz/v1', 'Authorization',
    'meta-llama/Llama-3.3-70B-Instruct-Turbo',
    60,
    ARRAY['meta-llama/Llama-3.3-70B-Instruct-Turbo', 'mistralai/Mixtral-8x22B-Instruct-v0.1'],
    ARRAY['chat', 'fast'],
    false, true, 4.0,
    0.00020, 0.00020,
    NULL, NULL, 'requests',
    'TOGETHER_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 11. 💰 PAID — NVIDIA Regular (20 RPM)
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'nvidia-regular', 'NVIDIA Regular', 'nvidia', 'https://integrate.api.nvidia.com/v1', 'Authorization',
    'nvidia/nemotron-4-340b-instruct',
    20,
    ARRAY['nvidia/nemotron-4-340b-instruct', 'meta/llama-3.1-nemotron-70b-instruct'],
    ARRAY['chat', 'long_context'],
    false, true, 3.0,
    0.00050, 0.00050,
    NULL, NULL, 'requests',
    'NVIDIA_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 12. 💰 PAID — NVIDIA Developer (500 RPM, high_rpm)
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'nvidia-dev', 'NVIDIA Developer', 'nvidia', 'https://integrate.api.nvidia.com/v1', 'Authorization',
    'nvidia/nemotron-4-340b-instruct',
    500,
    ARRAY['nvidia/nemotron-4-340b-instruct', 'meta/llama-3.1-nemotron-70b-instruct'],
    ARRAY['chat', 'long_context', 'high_rpm'],
    false, true, 5.0,
    0.00050, 0.00050,
    NULL, NULL, 'requests',
    'NVIDIA_DEV_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;

-- 13. 💰 PAID — Kimi
INSERT INTO ai_providers (
    id, name, provider_type, base_url, header_name, default_model,
    rpm_limit, models, capabilities, is_free_tier, is_enabled, weight,
    cost_per_1k_input, cost_per_1k_output,
    free_quota_type, free_quota_limit, free_quota_unit,
    secret_env_var, priority
) VALUES (
    'kimi-main', 'Kimi', 'kimi', 'https://api.moonshot.cn/v1', 'Authorization',
    'kimi-k2.5',
    3,
    ARRAY['kimi-k2.5'],
    ARRAY['chat', 'long_context'],
    false, true, 2.0,
    0.00100, 0.00200,
    NULL, NULL, 'requests',
    'KIMI_API_KEY', 0
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    header_name = EXCLUDED.header_name,
    default_model = EXCLUDED.default_model,
    rpm_limit = EXCLUDED.rpm_limit,
    models = EXCLUDED.models,
    capabilities = EXCLUDED.capabilities,
    is_free_tier = EXCLUDED.is_free_tier,
    is_enabled = EXCLUDED.is_enabled,
    weight = EXCLUDED.weight,
    cost_per_1k_input = EXCLUDED.cost_per_1k_input,
    cost_per_1k_output = EXCLUDED.cost_per_1k_output,
    free_quota_type = EXCLUDED.free_quota_type,
    free_quota_limit = EXCLUDED.free_quota_limit,
    free_quota_unit = EXCLUDED.free_quota_unit,
    secret_env_var = EXCLUDED.secret_env_var,
    priority = EXCLUDED.priority;
