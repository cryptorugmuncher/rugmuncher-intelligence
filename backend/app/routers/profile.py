#!/usr/bin/env python3
"""
Profile Management Router
=========================
Handles user profiles, badges, scan history, and avatar uploads.
"""

import os
import json
import base64
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from pydantic import BaseModel, Field

from app.auth import require_auth, get_current_user

router = APIRouter(prefix="/api/v1", tags=["profile"])

# ── Supabase client (lazy) ──
_supabase = None

def _get_supabase():
    global _supabase
    if _supabase is None:
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL", "")
            key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
            if url and key:
                _supabase = create_client(url, key)
        except Exception as e:
            print(f"[PROFILE] Supabase init failed: {e}")
    return _supabase


# ── PYDANTIC MODELS ──
class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    telegram_handle: Optional[str] = Field(None, max_length=100)
    wallet_address: Optional[str] = Field(None, max_length=64)
    chain_preference: Optional[str] = Field(None, max_length=20)
    tier: Optional[str] = Field(None, pattern="^(free|member|institutional)$")
    website: Optional[str] = Field(None, max_length=200)
    twitter_handle: Optional[str] = Field(None, max_length=100)
    interests: Optional[List[str]] = None
    chains: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    telegram_handle: Optional[str] = None
    wallet_address: Optional[str] = None
    chain_preference: Optional[str] = None
    tier: str = "free"
    role: str = "USER"
    xp: int = 0
    level: int = 1
    scans_remaining: int = 5
    total_scans_used: int = 0
    reputation_score: int = 0
    onboarding_completed: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BadgeResponse(BaseModel):
    id: str
    badge_type: str
    badge_name: str
    awarded_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ScanHistoryItem(BaseModel):
    id: str
    contract_address: str
    chain: str
    risk_score: float
    verdict: Optional[str] = None
    scan_result: Optional[Dict[str, Any]] = None
    scanned_at: Optional[str] = None


# ── HELPERS ──
def _now() -> str:
    return datetime.utcnow().isoformat()


def _get_user_id(user: Dict[str, Any]) -> str:
    """Extract deterministic user ID from auth payload."""
    uid = user.get("id") or user.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid user token")
    return uid


def _generate_username_from_id(user_id: str) -> str:
    """Generate a default username from user id."""
    return f"agent_{user_id[:8].lower()}"


async def _get_or_create_profile(user_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch profile from Supabase; create if missing."""
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Try fetch existing
    result = sb.table("profiles").select("*").eq("id", user_id).execute()
    if result.data:
        profile = result.data[0]
        # Ensure wallet_address is synced if present in token
        wallet = user.get("wallet_address")
        if wallet and not profile.get("wallet_address"):
            sb.table("profiles").update({"wallet_address": wallet.lower(), "updated_at": _now()}).eq("id", user_id).execute()
            profile["wallet_address"] = wallet.lower()
        return profile

    # Create new profile
    wallet = user.get("wallet_address", "")
    email = user.get("email", "")
    default_username = _generate_username_from_id(user_id)

    new_profile = {
        "id": user_id,
        "email": email,
        "username": default_username,
        "display_name": default_username.replace("_", " ").title(),
        "bio": "",
        "avatar_url": "",
        "wallet_address": wallet.lower() if wallet else None,
        "chain_preference": "solana",
        "tier": "free",
        "role": user.get("role", "USER"),
        "xp": 0,
        "level": 1,
        "scans_remaining": 5,
        "total_scans_used": 0,
        "reputation_score": 0,
        "onboarding_completed": False,
        "interests": [],
        "chains": [],
        "created_at": _now(),
        "updated_at": _now(),
    }

    insert = sb.table("profiles").insert(new_profile).execute()
    if insert.data:
        return insert.data[0]
    return new_profile


# ── ENDPOINTS ──

@router.get("/me", response_model=ProfileResponse)
async def get_me(request: Request):
    """Get current user profile. Creates one if missing."""
    user = await require_auth(request)
    user_id = _get_user_id(user)
    profile = await _get_or_create_profile(user_id, user)
    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_me(req: ProfileUpdateRequest, request: Request):
    """Update current user profile fields."""
    user = await require_auth(request)
    user_id = _get_user_id(user)
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Ensure profile exists
    await _get_or_create_profile(user_id, user)

    updates: Dict[str, Any] = {}
    for field in [
        "username", "display_name", "bio", "telegram_handle",
        "wallet_address", "chain_preference", "tier",
        "website", "twitter_handle", "interests", "chains"
    ]:
        val = getattr(req, field, None)
        if val is not None:
            if field == "wallet_address" and val:
                val = val.lower()
            updates[field] = val

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updates["updated_at"] = _now()

    # Username uniqueness check (if changing)
    if "username" in updates:
        existing = sb.table("profiles").select("id").eq("username", updates["username"]).neq("id", user_id).execute()
        if existing.data:
            raise HTTPException(status_code=409, detail="Username already taken")

    result = sb.table("profiles").update(updates).eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return result.data[0]


@router.get("/me/badges", response_model=List[BadgeResponse])
async def get_my_badges(request: Request):
    """List badges for the current user."""
    user = await require_auth(request)
    user_id = _get_user_id(user)
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Ensure profile exists to get profile_id
    profile = await _get_or_create_profile(user_id, user)
    profile_id = profile["id"]

    result = sb.table("user_badges").select("*").eq("profile_id", profile_id).order("awarded_at", desc=True).execute()
    return result.data or []


@router.get("/me/scans")
async def get_my_scans(
    request: Request,
    limit: int = 20,
    offset: int = 0
):
    """Paginated scan history for the current user."""
    user = await require_auth(request)
    user_id = _get_user_id(user)
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    profile = await _get_or_create_profile(user_id, user)
    profile_id = profile["id"]

    result = (
        sb.table("scan_history")
        .select("*", count="exact")
        .eq("profile_id", profile_id)
        .order("scanned_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    total = result.count if hasattr(result, "count") and result.count is not None else len(result.data or [])
    return {
        "items": result.data or [],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/me/avatar")
async def upload_avatar(request: Request, file: UploadFile = File(...)):
    """Upload avatar as base64 and store in profile."""
    user = await require_auth(request)
    user_id = _get_user_id(user)
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Validate file type and size
    allowed_types = {"image/png", "image/jpeg", "image/webp", "image/gif"}
    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid image type. Use png, jpeg, webp, or gif.")

    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large. Max 2MB.")

    b64 = base64.b64encode(contents).decode("utf-8")
    data_url = f"data:{content_type};base64,{b64}"

    profile = await _get_or_create_profile(user_id, user)
    result = sb.table("profiles").update({"avatar_url": data_url, "updated_at": _now()}).eq("id", profile["id"]).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update avatar")

    return {"avatar_url": data_url, "success": True}


@router.get("/profiles/{username}")
async def get_public_profile(username: str):
    """Public profile view by username."""
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    result = sb.table("profiles").select("*").eq("username", username).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = result.data[0]
    # Scrub sensitive fields for public view
    public = {
        "id": profile["id"],
        "username": profile.get("username"),
        "display_name": profile.get("display_name"),
        "bio": profile.get("bio"),
        "avatar_url": profile.get("avatar_url"),
        "chain_preference": profile.get("chain_preference"),
        "tier": profile.get("tier", "free"),
        "xp": profile.get("xp", 0),
        "level": profile.get("level", 1),
        "reputation_score": profile.get("reputation_score", 0),
        "created_at": profile.get("created_at"),
    }

    # Include badge count
    badges_result = sb.table("user_badges").select("id", count="exact").eq("profile_id", profile["id"]).execute()
    public["badge_count"] = badges_result.count if hasattr(badges_result, "count") and badges_result.count is not None else 0

    # Include scan count
    scans_result = sb.table("scan_history").select("id", count="exact").eq("profile_id", profile["id"]).execute()
    public["scan_count"] = scans_result.count if hasattr(scans_result, "count") and scans_result.count is not None else 0

    return public
