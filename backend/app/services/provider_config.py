"""
Dynamic AI Provider Configuration
Reads from Supabase (primary) + Vault (secrets).
Adding a new provider = 1 database row. No code changes.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("provider_config")

_config_cache = None
_config_cache_time = 0
CACHE_TTL_SECONDS = 60


@dataclass
class ProviderConfig:
    name: str
    provider_type: str
    base_url: str
    header_name: str = "Authorization"
    default_model: str = ""
    models: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    is_free_tier: bool = False
    rpm_limit: int = 60
    weight: float = 1.0
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    free_quota_type: str = "none"
    free_quota_limit: float = 0.0
    free_quota_unit: str = "requests"
    auto_register_url: Optional[str] = None
    auto_register_enabled: bool = False
    enabled: bool = True
    secret_vault_path: Optional[str] = None
    secret_env_var: Optional[str] = None


def _get_supabase():
    try:
        from app.db_client import SupabaseClient
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
        if url and key:
            return SupabaseClient(url=url, key=key).client
    except Exception as e:
        logger.warning(f"Supabase unavailable: {e}")
    return None


def _get_vault_key(path: str, key: str = "api_key") -> Optional[str]:
    try:
        from app.services.vault_keys import get_secret
        return get_secret(path, key)
    except Exception as e:
        logger.debug(f"Vault lookup failed for {path}: {e}")
        return None


def _load_hardcoded_defaults() -> List[ProviderConfig]:
    return [
        ProviderConfig(name="workers-ai", provider_type="cloudflare", base_url="", header_name="", default_model="@cf/meta/llama-3.1-8b-instruct", models=["@cf/meta/llama-3.1-8b-instruct", "@cf/baai/bge-base-en-v1.5"], capabilities=["chat", "embeddings"], is_free_tier=True, rpm_limit=10000, weight=10.0, free_quota_type="daily_requests", free_quota_limit=10000),
        ProviderConfig(name="openrouter-free", provider_type="openrouter", base_url="https://openrouter.ai/api/v1", header_name="Authorization", default_model="openrouter/auto", models=["openrouter/auto", "openrouter/free"], capabilities=["chat"], is_free_tier=True, rpm_limit=200, weight=8.0, free_quota_type="unlimited", free_quota_limit=999999, secret_vault_path="ai/openrouter", secret_env_var="OPENROUTER_API_KEY"),
        ProviderConfig(name="gemini-free", provider_type="gemini", base_url="https://generativelanguage.googleapis.com/v1beta/models", header_name="Authorization", default_model="gemini-1.5-flash", models=["gemini-1.5-flash", "gemini-1.5-pro"], capabilities=["chat", "vision", "json_mode"], is_free_tier=True, rpm_limit=1500, weight=7.0, cost_per_1k_input=0.000125, cost_per_1k_output=0.000375, free_quota_type="daily_requests", free_quota_limit=1500, secret_vault_path="ai/gemini", secret_env_var="GEMINI_API_KEY"),
        ProviderConfig(name="groq-free", provider_type="groq", base_url="https://api.groq.com/openai/v1", header_name="Authorization", default_model="llama-3.1-8b-instant", models=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"], capabilities=["chat", "json_mode", "fast"], is_free_tier=True, rpm_limit=30, weight=6.0, cost_per_1k_input=0.00005, cost_per_1k_output=0.00008, free_quota_type="free_credits", free_quota_limit=5.0, free_quota_unit="usd", secret_vault_path="ai/groq", secret_env_var="GROQ_API_KEY"),
        ProviderConfig(name="deepseek", provider_type="deepseek", base_url="https://api.deepseek.com/v1", header_name="Authorization", default_model="deepseek-chat", models=["deepseek-chat", "deepseek-coder"], capabilities=["chat", "coding"], rpm_limit=60, weight=5.0, cost_per_1k_input=0.00014, cost_per_1k_output=0.00028, secret_vault_path="ai/deepseek", secret_env_var="DEEPSEEK_API_KEY"),
        ProviderConfig(name="fireworks", provider_type="fireworks", base_url="https://api.fireworks.ai/inference/v1", header_name="Authorization", default_model="accounts/fireworks/models/llama-v3p1-8b-instruct", models=["accounts/fireworks/models/llama-v3p1-8b-instruct"], capabilities=["chat", "fast"], rpm_limit=60, weight=5.0, cost_per_1k_input=0.0002, cost_per_1k_output=0.0002, secret_vault_path="ai/fireworks", secret_env_var="FIREWORKS_API_KEY"),
        ProviderConfig(name="openai", provider_type="openai", base_url="https://api.openai.com/v1", header_name="Authorization", default_model="gpt-4o-mini", models=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], capabilities=["chat", "vision", "json_mode", "function_calling"], rpm_limit=60, weight=4.0, cost_per_1k_input=0.0015, cost_per_1k_output=0.002, secret_vault_path="ai/openai", secret_env_var="OPENAI_API_KEY"),
        ProviderConfig(name="anthropic", provider_type="anthropic", base_url="https://api.anthropic.com/v1", header_name="x-api-key", default_model="claude-3-haiku-20240307", models=["claude-sonnet-4-20250514", "claude-haiku-20240307"], capabilities=["chat", "vision", "long_context"], rpm_limit=60, weight=3.0, cost_per_1k_input=0.003, cost_per_1k_output=0.015, secret_vault_path="ai/anthropic", secret_env_var="ANTHROPIC_API_KEY"),
        ProviderConfig(name="mistral", provider_type="mistral", base_url="https://api.mistral.ai/v1", header_name="Authorization", default_model="mistral-small-latest", models=["mistral-large-latest", "mistral-medium"], capabilities=["chat", "json_mode"], rpm_limit=60, weight=4.0, cost_per_1k_input=0.0002, cost_per_1k_output=0.0006, secret_vault_path="ai/mistral", secret_env_var="MISTRAL_API_KEY"),
        ProviderConfig(name="nvidia", provider_type="nvidia", base_url="https://integrate.api.nvidia.com/v1", header_name="Authorization", default_model="meta/llama-3.1-nemotron-70b-instruct", models=["nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-nemotron-70b-instruct"], capabilities=["chat", "long_context"], rpm_limit=20, weight=3.0, cost_per_1k_input=0.0005, cost_per_1k_output=0.0005, secret_vault_path="ai/nvidia", secret_env_var="NVIDIA_API_KEY"),
        ProviderConfig(name="nvidia_dev", provider_type="nvidia", base_url="https://integrate.api.nvidia.com/v1", header_name="Authorization", default_model="meta/llama-3.1-nemotron-70b-instruct", models=["nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-nemotron-70b-instruct"], capabilities=["chat", "long_context", "high_rpm"], rpm_limit=500, weight=5.0, cost_per_1k_input=0.0005, cost_per_1k_output=0.0005, secret_vault_path="ai/nvidia_dev", secret_env_var="NVIDIA_DEV_API_KEY"),
        ProviderConfig(name="together", provider_type="together", base_url="https://api.together.xyz/v1", header_name="Authorization", default_model="meta-llama/Llama-3.3-70B-Instruct-Turbo", models=["meta-llama/Llama-3.3-70B-Instruct-Turbo", "mistralai/Mixtral-8x22B-Instruct-v0.1"], capabilities=["chat", "fast"], rpm_limit=60, weight=4.0, cost_per_1k_input=0.0002, cost_per_1k_output=0.0002, secret_vault_path="ai/together", secret_env_var="TOGETHER_API_KEY"),
        ProviderConfig(name="kimi", provider_type="kimi", base_url="https://api.moonshot.cn/v1", header_name="Authorization", default_model="kimi-k2.5", models=["kimi-k2.5"], capabilities=["chat", "long_context"], rpm_limit=3, weight=2.0, cost_per_1k_input=0.001, cost_per_1k_output=0.002, secret_vault_path="ai/kimi", secret_env_var="KIMI_API_KEY"),
    ]


def get_all_providers() -> List[ProviderConfig]:
    global _config_cache, _config_cache_time
    now = time.time()
    if _config_cache and (now - _config_cache_time) < CACHE_TTL_SECONDS:
        return _config_cache["providers"]

    sb = _get_supabase()
    if sb:
        try:
            result = sb.table("ai_providers").select("*").eq("enabled", True).execute()
            if result.data:
                providers = []
                for row in result.data:
                    cfg = ProviderConfig(
                        name=row["name"], provider_type=row["provider_type"], base_url=row.get("base_url", ""),
                        header_name=row.get("header_name", "Authorization"), default_model=row.get("default_model", ""),
                        models=row.get("models", []), capabilities=row.get("capabilities", []),
                        is_free_tier=row.get("is_free_tier", False), rpm_limit=row.get("rpm_limit", 60),
                        weight=row.get("weight", 1.0), cost_per_1k_input=row.get("cost_per_1k_input", 0.0),
                        cost_per_1k_output=row.get("cost_per_1k_output", 0.0),
                        free_quota_type=row.get("free_quota_type", "none"),
                        free_quota_limit=row.get("free_quota_limit", 0.0),
                        free_quota_unit=row.get("free_quota_unit", "requests"),
                        auto_register_url=row.get("auto_register_url"),
                        auto_register_enabled=row.get("auto_register_enabled", False),
                        enabled=row.get("enabled", True),
                        secret_vault_path=row.get("secret_vault_path"),
                        secret_env_var=row.get("secret_env_var"),
                    )
                    providers.append(cfg)
                _config_cache = {"providers": providers, "time": now}
                _config_cache_time = now
                logger.info(f"Loaded {len(providers)} providers from Supabase")
                return providers
        except Exception as e:
            logger.warning(f"Failed to load from Supabase: {e}")

    defaults = _load_hardcoded_defaults()
    _config_cache = {"providers": defaults, "time": now}
    _config_cache_time = now
    return defaults


def get_provider(name: str) -> Optional[ProviderConfig]:
    for p in get_all_providers():
        if p.name == name:
            return p
    return None


def get_free_providers() -> List[ProviderConfig]:
    return [p for p in get_all_providers() if p.is_free_tier and p.enabled]


def get_paid_providers() -> List[ProviderConfig]:
    return [p for p in get_all_providers() if not p.is_free_tier and p.enabled]


def get_provider_secret(cfg: ProviderConfig) -> Optional[str]:
    if cfg.secret_env_var:
        key = os.getenv(cfg.secret_env_var, "")
        if key:
            return key
    if cfg.secret_vault_path:
        key = _get_vault_key(cfg.secret_vault_path, "api_key")
        if key:
            return key
    return None


def get_routing_order(prefer_free: bool = True) -> List[ProviderConfig]:
    free = get_free_providers()
    paid = get_paid_providers()
    free.sort(key=lambda p: p.weight, reverse=True)
    paid.sort(key=lambda p: p.cost_per_1k_input + p.cost_per_1k_output)
    if prefer_free:
        return free + paid
    return paid + free


def get_cheapest_provider(required_caps: Optional[List[str]] = None) -> Optional[ProviderConfig]:
    candidates = get_paid_providers()
    if required_caps:
        candidates = [p for p in candidates if all(c in p.capabilities for c in required_caps)]
    if not candidates:
        candidates = get_free_providers()
        if required_caps:
            candidates = [p for p in candidates if all(c in p.capabilities for c in required_caps)]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.cost_per_1k_input + p.cost_per_1k_output)
    return candidates[0]


def get_bot_detection_provider() -> Optional[ProviderConfig]:
    return get_cheapest_provider(required_caps=["chat"])


def invalidate_cache():
    global _config_cache, _config_cache_time
    _config_cache = None
    _config_cache_time = 0
    logger.info("Provider config cache invalidated")
