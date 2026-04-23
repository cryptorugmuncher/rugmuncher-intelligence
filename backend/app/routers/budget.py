"""
Token Budget Admin Router
=========================
Endpoints for viewing spending, free quotas, and provider health.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from app.services.token_budget import (
    get_budget_summary,
    get_remaining_free_quota,
    get_smart_provider_order,
)
from app.services.vault_keys import get_all_ai_keys

router = APIRouter(prefix="/api/v1/admin", tags=["budget"])


@router.get("/budget/summary")
async def budget_summary():
    """Overall budget and spending summary."""
    return get_budget_summary()


@router.get("/budget/free-quota")
async def free_quota_status():
    """Remaining free quota for all providers."""
    providers = ["workers-ai", "openrouter-free", "gemini", "groq"]
    return {
        "quotas": {p: get_remaining_free_quota(p) for p in providers},
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


@router.get("/budget/providers")
async def provider_status():
    """All providers with their keys and priority order."""
    keys = get_all_ai_keys()
    order = get_smart_provider_order(keys)
    return {
        "available_keys": {k: bool(v) for k, v in keys.items()},
        "routing_order": [{"provider": p, "has_key": bool(k)} for p, k in order],
        "free_first": True,
    }
