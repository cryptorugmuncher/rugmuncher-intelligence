#!/usr/bin/env python3
"""
User Profile & Onboarding Router
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from app.auth import require_auth, get_current_user
from app.db_client import get_db, Profile, UserBadge

router = APIRouter(prefix="/api/v1/user", tags=["user"])


# Request/Response Models
class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    twitter_handle: Optional[str] = None
    telegram_username: Optional[str] = None
    role: Optional[str] = None
    interests: Optional[List[str]] = None
    chains: Optional[List[str]] = None


class OnboardingRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=64)
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    twitter_handle: Optional[str] = None
    telegram_username: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    chains: List[str] = Field(default_factory=list)


class TelegramLinkRequest(BaseModel):
    telegram_username: str = Field(..., min_length=1, max_length=64)


class ScanHistoryResponse(BaseModel):
    scans: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int


class BadgeResponse(BaseModel):
    badges: List[Dict[str, Any]]
    total: int


# Helper to get or create profile
async def _get_or_create_profile(user_id: str) -> Dict[str, Any]:
    db = get_db()
    profile = await db.profiles.get_by_user(user_id)
    if not profile:
        new_profile = Profile(user_id=user_id)
        profile = await db.profiles.create(new_profile)
    return profile


@router.get("/profile")
async def get_profile(request: Request, user: Dict[str, Any] = Depends(require_auth)):
    """Get full user profile with scan count and badges."""
    db = get_db()
    user_id = user.get("id") or user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    profile = await _get_or_create_profile(user_id)
    scan_count = await db.user_scans.count_by_user(user_id)
    badges = await db.user_badges.list_by_user(user_id)

    return {
        "profile": profile,
        "scan_count": scan_count,
        "badges": badges,
        "badges_count": len(badges),
    }


@router.put("/profile")
async def update_profile(
    req: ProfileUpdateRequest,
    request: Request,
    user: Dict[str, Any] = Depends(require_auth),
):
    """Update user profile fields."""
    db = get_db()
    user_id = user.get("id") or user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    updates = req.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Prevent non-admins from changing role
    if "role" in updates:
        current_role = user.get("role", "user")
        if current_role not in ("admin", "analyst"):
            del updates["role"]

    updated = await db.profiles.update(user_id, updates)
    return {"profile": updated}


@router.post("/onboarding")
async def complete_onboarding(
    req: OnboardingRequest,
    request: Request,
    user: Dict[str, Any] = Depends(require_auth),
):
    """Mark onboarding complete and set initial profile data."""
    db = get_db()
    user_id = user.get("id") or user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    # Check if profile exists
    existing = await db.profiles.get_by_user(user_id)

    profile_data = {
        "display_name": req.display_name,
        "avatar_url": req.avatar_url,
        "website": req.website,
        "twitter_handle": req.twitter_handle,
        "telegram_username": req.telegram_username,
        "interests": req.interests,
        "chains": req.chains,
        "onboarding_completed": True,
    }

    if existing:
        updated = await db.profiles.update(user_id, profile_data)
    else:
        new_profile = Profile(user_id=user_id, **profile_data)
        updated = await db.profiles.create(new_profile)

    # Award welcome badge
    try:
        welcome_badge = UserBadge(
            user_id=user_id,
            badge_type="welcome",
            metadata={"awarded_at": datetime.utcnow().isoformat(), "reason": "Completed onboarding"},
        )
        await db.user_badges.create(welcome_badge)
    except Exception:
        pass  # Badge may already exist

    return {
        "profile": updated,
        "onboarding_completed": True,
        "message": "Welcome to RugMuncher!",
    }


@router.get("/scans")
async def get_scan_history(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    user: Dict[str, Any] = Depends(require_auth),
):
    """Get paginated scan history for the user."""
    db = get_db()
    user_id = user.get("id") or user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    offset = (page - 1) * page_size
    scans = await db.user_scans.list_by_user(user_id, limit=page_size, offset=offset)
    total = await db.user_scans.count_by_user(user_id)

    return {
        "scans": scans,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/badges")
async def get_badges(request: Request, user: Dict[str, Any] = Depends(require_auth)):
    """List user badges."""
    db = get_db()
    user_id = user.get("id") or user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    badges = await db.user_badges.list_by_user(user_id)
    return {"badges": badges, "total": len(badges)}


@router.post("/telegram-link")
async def link_telegram(
    req: TelegramLinkRequest,
    request: Request,
    user: Dict[str, Any] = Depends(require_auth),
):
    """Link Telegram username to profile."""
    db = get_db()
    user_id = user.get("id") or user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    updated = await db.profiles.update(user_id, {"telegram_username": req.telegram_username})
    return {
        "telegram_username": req.telegram_username,
        "profile": updated,
        "linked": True,
    }
