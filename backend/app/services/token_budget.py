"""Token Budget & Quota Tracker — CONFIG-DRIVEN"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from app.services.provider_config import get_all_providers, get_provider, get_free_providers

logger = logging.getLogger("token_budget")


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


def get_today_usage(provider: str) -> int:
    sb = _get_supabase()
    if not sb:
        return 0
    today = datetime.utcnow().strftime("%Y-%m-%d")
    try:
        result = sb.table("token_spending_log").select("id", count="exact").eq("provider", provider).gte("created_at", f"{today}T00:00:00Z").execute()
        return result.count if hasattr(result, "count") and result.count is not None else 0
    except Exception as e:
        logger.warning(f"Failed to get today usage: {e}")
        return 0


def get_monthly_spend(provider: str) -> float:
    sb = _get_supabase()
    if not sb:
        return 0.0
    start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    try:
        result = sb.table("token_spending_log").select("estimated_cost").eq("provider", provider).gte("created_at", start).execute()
        return sum(float(r.get("estimated_cost", 0) or 0) for r in (result.data or []))
    except Exception as e:
        logger.warning(f"Failed to get monthly spend: {e}")
        return 0.0


def get_remaining_free_quota(provider_name: str) -> Dict[str, Any]:
    cfg = get_provider(provider_name)
    if not cfg or not cfg.is_free_tier or cfg.free_quota_type == "none":
        return {"has_free_tier": False, "remaining": 0}
    if cfg.free_quota_type == "daily_requests":
        used = get_today_usage(provider_name)
        remaining = max(int(cfg.free_quota_limit) - used, 0)
        return {"has_free_tier": True, "type": "daily_requests", "limit": int(cfg.free_quota_limit), "used": used, "remaining": remaining, "description": f"FREE — {cfg.name}"}
    if cfg.free_quota_type == "free_credits":
        spent = get_monthly_spend(provider_name)
        remaining = max(cfg.free_quota_limit - spent, 0)
        return {"has_free_tier": True, "type": "free_credits", "limit": cfg.free_quota_limit, "unit": cfg.free_quota_unit, "spent": round(spent, 4), "remaining": round(remaining, 4), "description": f"FREE CREDITS — {cfg.name}"}
    if cfg.free_quota_type == "unlimited":
        return {"has_free_tier": True, "type": "unlimited_requests", "limit": cfg.free_quota_limit, "remaining": cfg.free_quota_limit, "description": f"FREE — {cfg.name} (unlimited)"}
    return {"has_free_tier": False, "remaining": 0}


def is_free_quota_available(provider_name: str) -> bool:
    quota = get_remaining_free_quota(provider_name)
    if not quota["has_free_tier"]:
        return False
    if quota["type"] == "unlimited_requests":
        return True
    return quota["remaining"] > 0


def estimate_cost(provider_name: str, input_tokens: int = 0, output_tokens: int = 0) -> float:
    cfg = get_provider(provider_name)
    if not cfg:
        return 0.0
    return round((input_tokens / 1000) * cfg.cost_per_1k_input + (output_tokens / 1000) * cfg.cost_per_1k_output, 8)


def log_usage(provider: str, model: str, endpoint: str, input_tokens: int = 0, output_tokens: int = 0, latency_ms: Optional[int] = None, status: str = "success", error_message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
    sb = _get_supabase()
    if not sb:
        return
    total = input_tokens + output_tokens
    cost = estimate_cost(provider, input_tokens, output_tokens) if status == "success" else 0
    try:
        sb.table("token_spending_log").insert({"provider": provider, "model": model, "endpoint": endpoint, "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total, "estimated_cost": cost, "latency_ms": latency_ms, "status": status, "error_message": error_message, "metadata": metadata or {}, "created_at": datetime.utcnow().isoformat()}).execute()
    except Exception as e:
        logger.warning(f"Failed to log usage: {e}")


def get_paid_providers_with_costs() -> List[Dict[str, Any]]:
    from app.services.provider_config import get_paid_providers
    result = []
    for cfg in get_paid_providers():
        result.append({"name": cfg.name, "type": cfg.provider_type, "cost_per_1k_input": cfg.cost_per_1k_input, "cost_per_1k_output": cfg.cost_per_1k_output, "total_cost_per_1k": round(cfg.cost_per_1k_input + cfg.cost_per_1k_output, 6), "rpm_limit": cfg.rpm_limit, "capabilities": cfg.capabilities})
    result.sort(key=lambda x: x["total_cost_per_1k"])
    return result


def get_smart_provider_order(keys: Dict[str, Optional[str]]) -> List[Tuple[str, Optional[str]]]:
    from app.services.provider_config import get_routing_order, get_provider_secret
    order = []
    for cfg in get_routing_order(prefer_free=True):
        if cfg.is_free_tier and not is_free_quota_available(cfg.name):
            continue
        key = get_provider_secret(cfg) or keys.get(cfg.provider_type)
        if cfg.provider_type == "cloudflare":
            key = None
        if not key and cfg.provider_type != "cloudflare":
            continue
        order.append((cfg.name, key))
    return order


def get_budget_summary() -> Dict[str, Any]:
    sb = _get_supabase()
    if not sb:
        return {}
    today = datetime.utcnow().strftime("%Y-%m-%d")
    start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    try:
        today_result = sb.table("token_spending_log").select("estimated_cost").gte("created_at", f"{today}T00:00:00Z").execute()
        today_cost = sum(float(r.get("estimated_cost", 0) or 0) for r in (today_result.data or []))
        month_result = sb.table("token_spending_log").select("estimated_cost").gte("created_at", start).execute()
        month_cost = sum(float(r.get("estimated_cost", 0) or 0) for r in (month_result.data or []))
    except Exception as e:
        logger.warning(f"Failed to get budget summary: {e}")
        today_cost = month_cost = 0.0

    free_usage = {}
    for cfg in get_free_providers():
        free_usage[cfg.name] = get_remaining_free_quota(cfg.name)

    paid = get_paid_providers_with_costs()
    return {"today_spend_usd": round(today_cost, 4), "month_spend_usd": round(month_cost, 4), "free_quota_status": free_usage, "paid_provider_costs": paid, "cheapest_provider": paid[0]["name"] if paid else None, "timestamp": datetime.utcnow().isoformat()}


def get_cheapest_provider_name() -> Optional[str]:
    from app.services.provider_config import get_cheapest_provider
    cfg = get_cheapest_provider(required_caps=["chat"])
    return cfg.name if cfg else None
