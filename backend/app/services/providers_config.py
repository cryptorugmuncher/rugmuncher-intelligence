"""
AI Providers Config Service
===========================
Reads provider configurations from Supabase `ai_providers` table.
Caches in memory with a 60-second TTL and falls back to sensible defaults.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("providers_config")

# ── In-memory cache ──
_CACHE: Dict[str, Dict[str, Any]] = {}
_LAST_FETCH: float = 0.0
_TTL_SECONDS = 60

# ── Sensible fallback defaults (aligned with legacy hardcoded configs) ──
_FALLBACK_PROVIDERS: List[Dict[str, Any]] = [
    {
        "id": "workers-ai",
        "name": "Cloudflare Workers AI",
        "provider_type": "cloudflare",
        "base_url": "",
        "header_name": "",
        "default_model": "@cf/meta/llama-3.1-8b-instruct",
        "rpm_limit": 10000,
        "models": ["@cf/meta/llama-3.1-8b-instruct", "@cf/baai/bge-base-en-v1.5"],
        "capabilities": ["chat", "embeddings"],
        "is_free_tier": True,
        "is_enabled": True,
        "weight": 10.0,
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "free_quota_type": "daily_requests",
        "free_quota_limit": 10000,
        "free_quota_unit": "requests",
        "secret_env_var": "",
        "priority": 1,
    },
    {
        "id": "openrouter-free",
        "name": "OpenRouter Free Models",
        "provider_type": "openrouter",
        "base_url": "https://openrouter.ai/api/v1",
        "header_name": "",
        "default_model": "openrouter/free",
        "rpm_limit": 200,
        "models": ["openrouter/free"],
        "capabilities": ["chat"],
        "is_free_tier": True,
        "is_enabled": True,
        "weight": 8.0,
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "free_quota_type": "unlimited_requests",
        "free_quota_limit": 999999,
        "free_quota_unit": "requests",
        "secret_env_var": "OPENROUTER_API_KEY",
        "priority": 2,
    },
    {
        "id": "gemini",
        "name": "Google Gemini",
        "provider_type": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "header_name": "",
        "default_model": "gemini-1.5-flash",
        "rpm_limit": 1500,
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "capabilities": ["chat", "vision", "json_mode"],
        "is_free_tier": True,
        "is_enabled": True,
        "weight": 7.0,
        "cost_per_1k_input": 0.000125,
        "cost_per_1k_output": 0.000375,
        "free_quota_type": "daily_requests",
        "free_quota_limit": 1500,
        "free_quota_unit": "requests",
        "secret_env_var": "GEMINI_API_KEY",
        "priority": 3,
    },
    {
        "id": "groq",
        "name": "Groq",
        "provider_type": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "header_name": "",
        "default_model": "llama-3.3-70b-versatile",
        "rpm_limit": 30,
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
        "capabilities": ["chat", "json_mode", "fast"],
        "is_free_tier": True,
        "is_enabled": True,
        "weight": 6.0,
        "cost_per_1k_input": 0.00005,
        "cost_per_1k_output": 0.00008,
        "free_quota_type": "free_credits",
        "free_quota_limit": 5,
        "free_quota_unit": "usd",
        "secret_env_var": "GROQ_API_KEY",
        "priority": 4,
    },
    {
        "id": "nvidia",
        "name": "NVIDIA Regular",
        "provider_type": "nvidia",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "header_name": "",
        "default_model": "nvidia/nemotron-4-340b-instruct",
        "rpm_limit": 20,
        "models": ["nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-nemotron-70b-instruct"],
        "capabilities": ["chat", "long_context"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 3.0,
        "cost_per_1k_input": 0.00050,
        "cost_per_1k_output": 0.00050,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "NVIDIA_API_KEY",
        "priority": 10,
    },
    {
        "id": "nvidia_dev",
        "name": "NVIDIA Developer",
        "provider_type": "nvidia",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "header_name": "",
        "default_model": "meta/llama-3.1-nemotron-70b-instruct",
        "rpm_limit": 500,
        "models": ["nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-nemotron-70b-instruct"],
        "capabilities": ["chat", "long_context", "high_rpm"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 5.0,
        "cost_per_1k_input": 0.00050,
        "cost_per_1k_output": 0.00050,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "NVIDIA_DEV_API_KEY",
        "priority": 10,
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "provider_type": "openai",
        "base_url": "https://api.openai.com/v1",
        "header_name": "",
        "default_model": "gpt-4o-mini",
        "rpm_limit": 60,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "capabilities": ["chat", "vision", "json_mode", "function_calling"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 4.0,
        "cost_per_1k_input": 0.00150,
        "cost_per_1k_output": 0.00200,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "OPENAI_API_KEY",
        "priority": 10,
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "provider_type": "anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "header_name": "",
        "default_model": "claude-sonnet-4-20250514",
        "rpm_limit": 60,
        "models": ["claude-sonnet-4-20250514", "claude-haiku-20240307"],
        "capabilities": ["chat", "vision", "long_context"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 3.0,
        "cost_per_1k_input": 0.00300,
        "cost_per_1k_output": 0.01500,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "ANTHROPIC_API_KEY",
        "priority": 10,
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "provider_type": "deepseek",
        "base_url": "https://api.deepseek.com/v1",
        "header_name": "",
        "default_model": "deepseek-chat",
        "rpm_limit": 60,
        "models": ["deepseek-chat", "deepseek-coder"],
        "capabilities": ["chat", "coding"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 5.0,
        "cost_per_1k_input": 0.00014,
        "cost_per_1k_output": 0.00028,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "DEEPSEEK_API_KEY",
        "priority": 10,
    },
    {
        "id": "fireworks",
        "name": "Fireworks",
        "provider_type": "fireworks",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "header_name": "",
        "default_model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "rpm_limit": 60,
        "models": ["accounts/fireworks/models/llama-v3p1-8b-instruct"],
        "capabilities": ["chat", "fast"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 5.0,
        "cost_per_1k_input": 0.00020,
        "cost_per_1k_output": 0.00020,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "FIREWORKS_API_KEY",
        "priority": 10,
    },
    {
        "id": "mistral",
        "name": "Mistral",
        "provider_type": "mistral",
        "base_url": "https://api.mistral.ai/v1",
        "header_name": "",
        "default_model": "mistral-large-latest",
        "rpm_limit": 60,
        "models": ["mistral-large-latest", "mistral-medium"],
        "capabilities": ["chat", "json_mode"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 4.0,
        "cost_per_1k_input": 0.00020,
        "cost_per_1k_output": 0.00060,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "MISTRAL_API_KEY",
        "priority": 10,
    },
    {
        "id": "together",
        "name": "Together AI",
        "provider_type": "together",
        "base_url": "https://api.together.xyz/v1",
        "header_name": "",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "rpm_limit": 60,
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "mistralai/Mixtral-8x22B-Instruct-v0.1"],
        "capabilities": ["chat", "fast"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 4.0,
        "cost_per_1k_input": 0.00020,
        "cost_per_1k_output": 0.00020,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "TOGETHER_API_KEY",
        "priority": 10,
    },
    {
        "id": "kimi",
        "name": "Kimi",
        "provider_type": "kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "header_name": "",
        "default_model": "kimi-k2.5",
        "rpm_limit": 3,
        "models": ["kimi-k2.5"],
        "capabilities": ["chat", "long_context"],
        "is_free_tier": False,
        "is_enabled": True,
        "weight": 2.0,
        "cost_per_1k_input": 0.00100,
        "cost_per_1k_output": 0.00200,
        "free_quota_type": "",
        "free_quota_limit": 0,
        "free_quota_unit": "",
        "secret_env_var": "KIMI_API_KEY",
        "priority": 10,
    },
]


def _fetch_providers() -> List[Dict[str, Any]]:
    """Fetch provider rows from Supabase or return fallback defaults."""
    try:
        from app.db_client import RMI_DB
        sb = RMI_DB().client
    except Exception:
        sb = None

    if sb is None:
        logger.warning("Supabase unavailable; using fallback provider configs")
        return list(_FALLBACK_PROVIDERS)

    try:
        result = sb.table("ai_providers").select("*").execute()
        data = result.data or []
        if not data:
            logger.warning("ai_providers table empty; using fallback")
            return list(_FALLBACK_PROVIDERS)

        normalized: List[Dict[str, Any]] = []
        for row in data:
            row = dict(row)
            # Normalise array columns that may come back as strings or None
            for arr_key in ("models", "capabilities"):
                val = row.get(arr_key)
                if val is None:
                    row[arr_key] = []
                elif isinstance(val, str):
                    try:
                        row[arr_key] = json.loads(val)
                    except Exception:
                        row[arr_key] = [v.strip() for v in val.split(",") if v.strip()]
                else:
                    row[arr_key] = list(val)
            normalized.append(row)
        return normalized
    except Exception as exc:
        logger.warning(f"Failed to fetch ai_providers: {exc}; using fallback")
        return list(_FALLBACK_PROVIDERS)


def _ensure_cache() -> None:
    """Load cache if stale or missing."""
    global _CACHE, _LAST_FETCH
    now = time.time()
    if not _CACHE or now - _LAST_FETCH > _TTL_SECONDS:
        providers = _fetch_providers()
        _CACHE = {p["id"]: p for p in providers}
        _LAST_FETCH = now


def refresh_providers() -> List[Dict[str, Any]]:
    """Force refresh provider configs from the database."""
    global _CACHE, _LAST_FETCH
    providers = _fetch_providers()
    _CACHE = {p["id"]: p for p in providers}
    _LAST_FETCH = time.time()
    return list(_CACHE.values())


def get_all_providers() -> List[Dict[str, Any]]:
    """Return all provider configs."""
    _ensure_cache()
    return list(_CACHE.values())


def get_free_providers() -> List[Dict[str, Any]]:
    """Return providers marked as free tier."""
    return [p for p in get_all_providers() if p.get("is_free_tier")]


def get_paid_providers() -> List[Dict[str, Any]]:
    """Return providers not marked as free tier."""
    return [p for p in get_all_providers() if not p.get("is_free_tier")]


def get_provider(provider_id: str) -> Optional[Dict[str, Any]]:
    """Return a single provider config by ID."""
    _ensure_cache()
    return _CACHE.get(provider_id)


def get_provider_cost_rates() -> Dict[str, Dict[str, float]]:
    """Map provider ID -> {input, output} cost per 1k tokens."""
    rates: Dict[str, Dict[str, float]] = {}
    for p in get_all_providers():
        inp = p.get("cost_per_1k_input")
        out = p.get("cost_per_1k_output")
        if inp is not None or out is not None:
            rates[p["id"]] = {
                "input": float(inp) if inp is not None else 0.0,
                "output": float(out) if out is not None else 0.0,
            }
    return rates


def get_free_tier_limits() -> Dict[str, Dict[str, Any]]:
    """Map provider ID -> free tier limit info."""
    limits: Dict[str, Dict[str, Any]] = {}
    for p in get_all_providers():
        if not p.get("is_free_tier"):
            continue
        limits[p["id"]] = {
            "type": p.get("free_quota_type", "unlimited_requests"),
            "limit": p.get("free_quota_limit", 0),
            "unit": p.get("free_quota_unit", ""),
            "description": f"{'🆓 FREE' if p.get('is_free_tier') else ''} — {p.get('name', p['id'])}",
        }
    return limits


def get_default_models() -> Dict[str, str]:
    """Map provider ID -> default model name."""
    return {
        p["id"]: p.get("default_model", "")
        for p in get_all_providers()
        if p.get("default_model")
    }
