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

from app.services import providers_config

logger = logging.getLogger("token_budget")


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
    limits = providers_config.get_free_tier_limits().get(provider)
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
            "description": limits.get("description", ""),
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
            "description": limits.get("description", ""),
        }

    if limits["type"] == "unlimited_requests":
        return {
            "has_free_tier": True,
            "type": "unlimited_requests",
            "limit": limits["limit"],
            "remaining": limits["limit"],
            "description": limits.get("description", ""),
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
    rates = providers_config.get_provider_cost_rates().get(provider, {"input": 0, "output": 0})
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
    for p in providers_config.get_free_providers():
        pid = p["id"]
        if not is_free_quota_available(pid):
            continue
        if not p.get("secret_env_var"):
            free_providers.append(pid)
            continue
        key = keys.get(p.get("provider_type", pid))
        if key:
            free_providers.append(pid)
    return free_providers


def get_paid_providers(keys: Dict[str, Optional[str]]) -> List[Tuple[str, str]]:
    """Return list of paid providers sorted by cost (cheapest first)."""
    paid = []
    cost_rates = providers_config.get_provider_cost_rates()
    for p in providers_config.get_paid_providers():
        pid = p["id"]
        key = keys.get(p.get("provider_type", pid))
        if not key:
            continue
        rates = cost_rates.get(pid, {"input": 999, "output": 999})
        score = rates.get("input", 999) + rates.get("output", 999)
        paid.append((pid, key, score))
    paid.sort(key=lambda x: x[2])
    return [(p, k) for p, k, _ in paid]


def get_smart_provider_order(keys: Dict[str, Optional[str]]) -> List[Tuple[str, Optional[str]]]:
    """Return provider order: free first (with quota), then paid (cheapest first)."""
    order: List[Tuple[str, Optional[str]]] = []

    # Free providers sorted by priority asc, then weight desc
    free_rows = providers_config.get_free_providers()
    free_rows.sort(key=lambda p: (p.get("priority", 999), -p.get("weight", 1)))
    for p in free_rows:
        pid = p["id"]
        if not is_free_quota_available(pid):
            continue
        if not p.get("secret_env_var"):
            order.append((pid, None))
            continue
        key = keys.get(p.get("provider_type", pid))
        if key:
            order.append((pid, key))

    # Paid providers sorted by cost
    paid = get_paid_providers(keys)
    for pid, key in paid:
        if pid not in [p for p, _ in order]:
            order.append((pid, key))

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

    # Free usage for all free-tier providers
    free_usage = {}
    for p in providers_config.get_free_providers():
        pid = p["id"]
        free_usage[pid] = get_remaining_free_quota(pid)

    return {
        "today_spend_usd": round(today_cost, 4),
        "month_spend_usd": round(month_cost, 4),
        "free_quota_status": free_usage,
        "timestamp": datetime.utcnow().isoformat(),
    }
