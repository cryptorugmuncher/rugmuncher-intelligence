"""AI Provider Management API — CRUD for provider configs"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.services.provider_config import get_all_providers, get_provider, invalidate_cache
from app.services.token_budget import get_budget_summary
from app.services.multi_key_router import get_router

router = APIRouter(prefix="/api/v1/admin", tags=["providers"])

class ProviderCreate(BaseModel):
    name: str; provider_type: str; base_url: str; header_name: str = "Authorization"
    default_model: str = ""; models: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list); is_free_tier: bool = False
    rpm_limit: int = 60; weight: float = 1.0; cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0; free_quota_type: str = "none"
    free_quota_limit: float = 0.0; free_quota_unit: str = "requests"
    auto_register_url: Optional[str] = None; auto_register_enabled: bool = False
    enabled: bool = True; secret_vault_path: Optional[str] = None
    secret_env_var: Optional[str] = None

class ProviderUpdate(BaseModel):
    base_url: Optional[str] = None; header_name: Optional[str] = None
    default_model: Optional[str] = None; models: Optional[List[str]] = None
    capabilities: Optional[List[str]] = None; is_free_tier: Optional[bool] = None
    rpm_limit: Optional[int] = None; weight: Optional[float] = None
    cost_per_1k_input: Optional[float] = None; cost_per_1k_output: Optional[float] = None
    free_quota_type: Optional[str] = None; free_quota_limit: Optional[float] = None
    enabled: Optional[bool] = None; secret_vault_path: Optional[str] = None
    secret_env_var: Optional[str] = None

@router.get("/providers")
async def list_providers(free_only: bool = False, enabled_only: bool = True):
    providers = get_all_providers()
    if free_only: providers = [p for p in providers if p.is_free_tier]
    if enabled_only: providers = [p for p in providers if p.enabled]
    return {"providers": [{"name": p.name, "type": p.provider_type, "base_url": p.base_url, "default_model": p.default_model, "models": p.models, "capabilities": p.capabilities, "is_free_tier": p.is_free_tier, "rpm_limit": p.rpm_limit, "weight": p.weight, "cost_per_1k_input": p.cost_per_1k_input, "cost_per_1k_output": p.cost_per_1k_output, "free_quota": {"type": p.free_quota_type, "limit": p.free_quota_limit, "unit": p.free_quota_unit}, "enabled": p.enabled, "has_secret_config": bool(p.secret_vault_path or p.secret_env_var)} for p in providers], "count": len(providers)}

@router.get("/providers/{name}")
async def get_provider_detail(name: str):
    p = get_provider(name)
    if not p: raise HTTPException(status_code=404, detail=f"Provider {name} not found")
    return {"name": p.name, "type": p.provider_type, "base_url": p.base_url, "header_name": p.header_name, "default_model": p.default_model, "models": p.models, "capabilities": p.capabilities, "is_free_tier": p.is_free_tier, "rpm_limit": p.rpm_limit, "weight": p.weight, "cost_per_1k_input": p.cost_per_1k_input, "cost_per_1k_output": p.cost_per_1k_output, "free_quota": {"type": p.free_quota_type, "limit": p.free_quota_limit, "unit": p.free_quota_unit}, "auto_register_url": p.auto_register_url, "auto_register_enabled": p.auto_register_enabled, "enabled": p.enabled, "secret_vault_path": p.secret_vault_path, "secret_env_var": p.secret_env_var}

@router.post("/providers")
async def create_provider(provider: ProviderCreate, background_tasks: BackgroundTasks):
    try:
        from app.db_client import SupabaseClient
        import os
        sb = SupabaseClient(url=os.getenv("SUPABASE_URL", ""), key=os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")).client
        data = {"name": provider.name, "provider_type": provider.provider_type, "base_url": provider.base_url, "header_name": provider.header_name, "default_model": provider.default_model, "models": provider.models, "capabilities": provider.capabilities, "is_free_tier": provider.is_free_tier, "rpm_limit": provider.rpm_limit, "weight": provider.weight, "cost_per_1k_input": provider.cost_per_1k_input, "cost_per_1k_output": provider.cost_per_1k_output, "free_quota_type": provider.free_quota_type, "free_quota_limit": provider.free_quota_limit, "free_quota_unit": provider.free_quota_unit, "auto_register_url": provider.auto_register_url, "auto_register_enabled": provider.auto_register_enabled, "enabled": provider.enabled, "secret_vault_path": provider.secret_vault_path, "secret_env_var": provider.secret_env_var}
        sb.table("ai_providers").insert(data).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save provider: {e}")
    invalidate_cache()
    try: get_router().reload_keys()
    except Exception: pass
    return {"status": "created", "provider": provider.name, "message": f"Provider {provider.name} added. Router and budget auto-updated."}

@router.put("/providers/{name}")
async def update_provider(name: str, update: ProviderUpdate):
    try:
        from app.db_client import SupabaseClient
        import os
        sb = SupabaseClient(url=os.getenv("SUPABASE_URL", ""), key=os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")).client
        data = {k: v for k, v in update.model_dump().items() if v is not None}
        if not data: raise HTTPException(status_code=400, detail="No fields to update")
        sb.table("ai_providers").update(data).eq("name", name).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update provider: {e}")
    invalidate_cache()
    try: get_router().reload_keys()
    except Exception: pass
    return {"status": "updated", "provider": name}

@router.delete("/providers/{name}")
async def delete_provider(name: str):
    if name in ["workers-ai", "openrouter-free", "gemini-free", "groq-free"]:
        raise HTTPException(status_code=403, detail="Cannot delete core free providers")
    try:
        from app.db_client import SupabaseClient
        import os
        sb = SupabaseClient(url=os.getenv("SUPABASE_URL", ""), key=os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")).client
        sb.table("ai_providers").delete().eq("name", name).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete provider: {e}")
    invalidate_cache()
    try: get_router().reload_keys()
    except Exception: pass
    return {"status": "deleted", "provider": name}

@router.post("/providers/{name}/reload")
async def reload_provider_keys(name: str):
    invalidate_cache()
    try:
        router = get_router()
        router.reload_keys()
        key = router.keys.get(name)
        return {"status": "reloaded", "provider": name, "key_loaded": key is not None, "key_healthy": key.healthy if key else False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers/system/summary")
async def system_summary():
    from app.services.provider_config import get_free_providers, get_paid_providers, get_routing_order
    from app.services.token_budget import get_cheapest_provider_name
    return {"free_providers": [{"name": p.name, "type": p.provider_type, "quota_type": p.free_quota_type} for p in get_free_providers()], "paid_providers": [{"name": p.name, "type": p.provider_type, "cost_per_1k": p.cost_per_1k_input + p.cost_per_1k_output} for p in get_paid_providers()], "routing_order": [p.name for p in get_routing_order(prefer_free=True)], "cheapest_provider": get_cheapest_provider_name(), "budget": get_budget_summary()}
