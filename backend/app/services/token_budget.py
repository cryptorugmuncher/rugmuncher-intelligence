"""
Token Budget & Quota Tracker
=============================
Tracks free-tier usage, remaining quotas, and spending across all AI providers.
Always prioritizes free providers first.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("token_budget")

# Free tier limits (requests per day, per month, etc.)
FREE_TIER_LIMITS: Dict[str, Dict[str, Any]] = {
    "workers-ai": {
        "type": "daily_requests",
        "limit": 10000,
        "description": "Cloudflare Workers AI free tier",
    },
    "openrouter-free": {
        "type": "unlimited_requests",
        "limit": 999999,
        "description": "OpenRouter free models",
    },
    "gemini": {
        "type": "daily_requests",
        "limit": 1500,
        "description": "Gemini free tier (approx 1500 requests/day)",
    },
    "groq": {
        "type": "free_credits",
        "limit": 500,
        "description": "Groq free credits ($5 initial)",
        "unit": "usd",
    },
}

# Cost estimates per 1K tokens (USD)
COST_RATES: Dict[str, Dict[str, float]] = {
    "openai": {"input": 0.0015, "output": 0.002},
    "anthropic": {"input": 0.003, "output": 0.015},
    "groq": {"input": 0.00005, "output": 0.00008},
    "deepseek": {"input": 0.00014, "output": 0.00028},
    "fireworks": {"input": 0.0002, "output": 0.0002},
    "gemini": {"input": 0.000125, "output": 0.000375},
    "mistral": {"input": 0.0002, "output": 0.0006},
    "nvidia": {"input": 0.0005, "output": 0.0005},
    "nvidia_dev": {"input": 0.0005, "output": 0.0005},
    "kimi": {"input": 0.001, "output": 0.002},
    "together": {"input": 0.0002, "output": 0.0002},
}


def _get_supabase():
    try:
        from app.db_client import RMI_DB
        return RMI_DB().client
    except Exception as e:
        logger.warning(f"Supabase unavailable for budget tracking: {e}")
        return None


def get_today_usage(provider: str) -> int:
    """Get today's request count for a provider."""
    sb = _get_supabase()
    if not sb:
        return 0
    today = datetime.utcnow().strftime("%Y-%m-%d")
    result = sb.table("token_spending_log") \
        .select("id", count="exact") \
        .eq("provider", provider) \
        .gte("created_at", f"{today}T00:00:00Z") \
        .execute()
    return result.count if hasattr(result, "count") and result.count is not None else 0


def get_monthly_spend(provider: str) -> float:
    """Get current month's estimated spend for a provider."""
    sb = _get_supabase()
    if not sb:
        return 0.0
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    result = sb.table("token_spending_log") \
        .select("estimated_cost") \
        .eq("provider", provider) \
        .gte("created_at", start_of_month) \
        .execute()
    return sum(float(r.get("estimated_cost", 0) or 0) for r in (result.data or []))


def get_remaining_free_quota(provider: str) -> Dict[str, Any]:
    """Check remaining free quota for a provider."""
    limits = FREE_TIER_LIMITS.get(provider)
    if not limits:
        return {"has_free_tier": False, "remaining": 0}

    if limits["type"] == "daily_requests":
        used = get_today_usage(provider)
        remaining = max(limits["limit"] - used, 0)
        return {
            "has_free_tier": True,
            "type": "daily_requests",
            "limit": limits["limit"],
            "used": used,
            "remaining": remaining,
            "description": limits["description"],
        }

    if limits["type"] == "free_credits":
        spent = get_monthly_spend(provider)
        remaining = max(limits["limit"] - spent, 0)
        return {
            "has_free_tier": True,
            "type": "free_credits",
            "limit": limits["limit"],
            "unit": limits.get("unit", "usd"),
            "spent": round(spent, 4),
            "remaining": round(remaining, 4),
            "description": limits["description"],
        }

    if limits["type"] == "unlimited_requests":
        return {
            "has_free_tier": True,
            "type": "unlimited_requests",
            "limit": limits["limit"],
            "remaining": limits["limit"],
            "description": limits["description"],
        }

    return {"has_free_tier": False, "remaining": 0}


def is_free_quota_available(provider: str) -> bool:
    """Check if a provider still has free quota remaining."""
    quota = get_remaining_free_quota(provider)
    if not quota["has_free_tier"]:
        return False
    if quota["type"] == "unlimited_requests":
        return True
    return quota["remaining"] > 0


def estimate_cost(provider: str, input_tokens: int = 0, output_tokens: int = 0) -> float:
    """Estimate cost in USD for a request."""
    rates = COST_RATES.get(provider, {"input": 0, "output": 0})
    input_cost = (input_tokens / 1000) * rates["input"]
    output_cost = (output_tokens / 1000) * rates["output"]
    return round(input_cost + output_cost, 8)


def log_usage(
    provider: str,
    model: str,
    endpoint: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    latency_ms: Optional[int] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Log token usage to the database."""
    sb = _get_supabase()
    if not sb:
        return

    total_tokens = input_tokens + output_tokens
    cost = estimate_cost(provider, input_tokens, output_tokens) if status == "success" else 0

    try:
        sb.table("token_spending_log").insert({
            "provider": provider,
            "model": model,
            "endpoint": endpoint,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": cost,
            "latency_ms": latency_ms,
            "status": status,
            "error_message": error_message,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception as e:
        logger.warning(f"Failed to log usage: {e}")


def get_free_providers(keys: Dict[str, Optional[str]]) -> List[str]:
    """Return list of providers that have free quota AND a valid key."""
    free_providers = []
    for provider in ["workers-ai", "openrouter-free", "gemini", "groq"]:
        if is_free_quota_available(provider):
            if provider == "workers-ai":
                free_providers.append(provider)  # No key needed
            elif keys.get(provider.replace("-free", "")):
                free_providers.append(provider)
    return free_providers


def get_paid_providers(keys: Dict[str, Optional[str]]) -> List[Tuple[str, str]]:
    """Return list of paid providers sorted by cost (cheapest first)."""
    paid = []
    for provider, key in keys.items():
        if not key:
            continue
        if provider in ["workers-ai"]:
            continue
        # Calculate a simple cost score (input + output rate)
        rates = COST_RATES.get(provider, {"input": 999, "output": 999})
        score = rates["input"] + rates["output"]
        paid.append((provider, key, score))
    # Sort by cost score (cheapest first)
    paid.sort(key=lambda x: x[2])
    return [(p, k) for p, k, _ in paid]


def get_smart_provider_order(keys: Dict[str, Optional[str]]) -> List[Tuple[str, Optional[str]]]:
    """Return provider order: free first (with quota), then paid (cheapest first)."""
    order: List[Tuple[str, Optional[str]]] = []

    # 1. Workers AI (always free, no key needed)
    if is_free_quota_available("workers-ai"):
        order.append(("workers-ai", None))

    # 2. OpenRouter free models
    if is_free_quota_available("openrouter-free") and keys.get("openrouter"):
        order.append(("openrouter-free", keys["openrouter"]))

    # 3. Gemini free tier
    if is_free_quota_available("gemini") and keys.get("gemini"):
        order.append(("gemini", keys["gemini"]))

    # 4. Groq free credits
    if is_free_quota_available("groq") and keys.get("groq"):
        order.append(("groq", keys["groq"]))

    # 5. Paid providers sorted by cost
    paid = get_paid_providers(keys)
    for provider, key in paid:
        # Skip if already added as free variant
        if provider not in [p for p, _ in order]:
            order.append((provider, key))

    return order


def get_budget_summary() -> Dict[str, Any]:
    """Get overall budget summary for dashboard."""
    sb = _get_supabase()
    if not sb:
        return {}

    today = datetime.utcnow().strftime("%Y-%m-%d")
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

    # Today's spend
    today_result = sb.table("token_spending_log") \
        .select("estimated_cost") \
        .gte("created_at", f"{today}T00:00:00Z") \
        .execute()
    today_cost = sum(float(r.get("estimated_cost", 0) or 0) for r in (today_result.data or []))

    # Month's spend
    month_result = sb.table("token_spending_log") \
        .select("estimated_cost") \
        .gte("created_at", start_of_month) \
        .execute()
    month_cost = sum(float(r.get("estimated_cost", 0) or 0) for r in (month_result.data or []))

    # Free usage today
    free_providers = ["workers-ai", "openrouter-free", "gemini", "groq"]
    free_usage = {}
    for fp in free_providers:
        free_usage[fp] = get_remaining_free_quota(fp)

    return {
        "today_spend_usd": round(today_cost, 4),
        "month_spend_usd": round(month_cost, 4),
        "free_quota_status": free_usage,
        "timestamp": datetime.utcnow().isoformat(),
    }
