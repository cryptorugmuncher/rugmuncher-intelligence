"""
📱 Telegram Service
===================
Backend business logic for @rugmunchbot integration.
Uses Supabase for persistence, Redis for rate-limiting.
"""

import os
import json
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# ── Supabase Client ─────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

_supabase: Optional[Client] = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None and SUPABASE_URL:
        key = SUPABASE_SERVICE_KEY or SUPABASE_KEY
        if key:
            _supabase = create_client(SUPABASE_URL, key)
    return _supabase


# ── Tier Configuration ──────────────────────────────────────
TIERS = {
    "free":   {"scans_per_month": 3,   "xp_multiplier": 1.0},
    "basic":  {"scans_per_month": 25,  "xp_multiplier": 1.2},
    "pro":    {"scans_per_month": 100, "xp_multiplier": 1.5},
    "elite":  {"scans_per_month": -1,  "xp_multiplier": 2.0},  # unlimited
}

LEVELS = [
    {"level": 1, "name": "Rookie",    "xp_required": 0},
    {"level": 2, "name": "Scout",     "xp_required": 100},
    {"level": 3, "name": "Analyst",   "xp_required": 300},
    {"level": 4, "name": "Detective", "xp_required": 600},
    {"level": 5, "name": "Veteran",   "xp_required": 1000},
    {"level": 6, "name": "Legend",    "xp_required": 2000},
]


def _level_from_xp(xp: int) -> Dict:
    current_level = 1
    current_name = "Rookie"
    for lvl in LEVELS:
        if xp >= lvl["xp_required"]:
            current_level = lvl["level"]
            current_name = lvl["name"]
    return {"level": current_level, "name": current_name}


# ── Core Functions ──────────────────────────────────────────

def get_or_create_telegram_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Dict:
    """Get or create a Telegram user in the database."""
    sb = get_supabase()
    if not sb:
        logger.warning("Supabase not configured; returning stub user")
        return _stub_user(telegram_id)

    try:
        resp = sb.table("telegram_users").select("*").eq("telegram_id", telegram_id).execute()
        if resp.data:
            user = resp.data[0]
            # Check if scans need resetting (monthly cycle)
            now = datetime.utcnow()
            reset_at = user.get("scans_reset_at")
            if reset_at and datetime.fromisoformat(reset_at.replace("Z", "+00:00")) < now:
                tier = user.get("tier", "free")
                new_limit = TIERS.get(tier, TIERS["free"]).get("scans_per_month", 3)
                sb.table("telegram_users").update({
                    "scans_used": 0,
                    "scans_limit": new_limit,
                    "scans_reset_at": (now + timedelta(days=30)).isoformat(),
                    "updated_at": now.isoformat(),
                }).eq("telegram_id", telegram_id).execute()
                user["scans_used"] = 0
                user["scans_limit"] = new_limit

            # Update username/first_name if changed
            update_fields = {"updated_at": datetime.utcnow().isoformat()}
            if username and username != user.get("username"):
                update_fields["username"] = username
            if first_name and first_name != user.get("first_name"):
                update_fields["first_name"] = first_name
            if update_fields:
                sb.table("telegram_users").update(update_fields).eq("telegram_id", telegram_id).execute()

            return user

        # Create new user
        tier = "free"
        new_limit = TIERS[tier]["scans_per_month"]
        new_user = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "tier": tier,
            "scans_used": 0,
            "scans_limit": new_limit,
            "scans_reset_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "xp": 0,
            "level": 1,
            "badges": [],
            "total_scans": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        resp = sb.table("telegram_users").insert(new_user).execute()
        return resp.data[0] if resp.data else new_user
    except Exception as e:
        logger.error(f"Failed to get/create telegram user: {e}")
        return _stub_user(telegram_id)


def _stub_user(telegram_id: int) -> Dict:
    return {
        "telegram_id": telegram_id,
        "tier": "free",
        "scans_used": 0,
        "scans_limit": 3,
        "xp": 0,
        "level": 1,
        "badges": [],
        "total_scans": 0,
    }


def get_user_status(telegram_id: int) -> Dict:
    """Get user's tier, scan usage, XP, and level."""
    user = get_or_create_telegram_user(telegram_id)
    lvl = _level_from_xp(user.get("xp", 0))
    return {
        "telegram_id": user.get("telegram_id"),
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "tier": user.get("tier", "free"),
        "scans_used": user.get("scans_used", 0),
        "scans_limit": user.get("scans_limit", 3),
        "scans_remaining": _scans_remaining(user),
        "xp": user.get("xp", 0),
        "level": lvl["level"],
        "level_name": lvl["name"],
        "badges": user.get("badges", []),
        "total_scans": user.get("total_scans", 0),
        "wallet_address": user.get("wallet_address"),
    }


def _scans_remaining(user: Dict) -> int:
    limit = user.get("scans_limit", 3)
    if limit == -1:
        return -1  # unlimited
    return max(0, limit - user.get("scans_used", 0))


def can_scan(telegram_id: int) -> bool:
    """Check if user has remaining scans."""
    status = get_user_status(telegram_id)
    remaining = status.get("scans_remaining", 0)
    return remaining == -1 or remaining > 0


def record_scan(telegram_id: int, scan_type: str, token: str,
                result: Dict[str, Any] = None) -> Dict:
    """Record a scan, increment usage, award XP, check badges."""
    sb = get_supabase()
    if not sb:
        return {"success": False, "error": "Supabase not configured"}

    try:
        user = get_or_create_telegram_user(telegram_id)
        new_used = user.get("scans_used", 0) + 1
        new_total = user.get("total_scans", 0) + 1

        # Update user scan counts
        sb.table("telegram_users").update({
            "scans_used": new_used,
            "total_scans": new_total,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("telegram_id", telegram_id).execute()

        # Record scan detail (result as JSONB — Supabase handles JSON)
        scan_record = {
            "telegram_id": telegram_id,
            "scan_type": scan_type,
            "token": token,
            "result": result or {},
            "risk_score": (result or {}).get("risk_score"),
            "ai_consensus": (result or {}).get("consensus"),
        }
        sb.table("telegram_scans").insert(scan_record).execute()

        # Gamification: award XP
        new_xp, new_badges = _award_scan_xp(telegram_id, scan_type, user)

        return {
            "success": True,
            "scans_used": new_used,
            "scans_remaining": _scans_remaining({"scans_used": new_used, "scans_limit": user.get("scans_limit", 3)}),
            "xp_gained": new_xp,
            "badges_unlocked": new_badges,
        }
    except Exception as e:
        logger.error(f"Failed to record scan: {e}")
        return {"success": False, "error": str(e)}


def _award_scan_xp(telegram_id: int, scan_type: str, user: Optional[Dict] = None) -> tuple:
    """Award XP for scans and check for new badges. Returns (xp_gained, badges_unlocked)."""
    sb = get_supabase()
    if not sb:
        return 0, []

    xp_values = {
        "security": 10,
        "scan": 25,
        "full_scan": 25,
        "audit": 20,
        "predict": 15,
        "wallet": 10,
        "whale_analysis": 10,
        "holder_analysis": 10,
        "bundling_detection": 15,
        "portfolio_tracker": 5,
    }
    base_xp = xp_values.get(scan_type, 5)

    # Apply tier multiplier
    if user is None:
        user = get_or_create_telegram_user(telegram_id)
    tier = user.get("tier", "free")
    multiplier = TIERS.get(tier, TIERS["free"]).get("xp_multiplier", 1.0)
    xp = int(base_xp * multiplier)

    new_xp = user.get("xp", 0) + xp
    new_level = _level_from_xp(new_xp)["level"]

    # Check badges
    new_badges = []
    total_scans = user.get("total_scans", 0) + 1
    current_badges = user.get("badges", []) or []

    badge_conditions = [
        ("first_scan", total_scans >= 1),
        ("ten_scans", total_scans >= 10),
        ("fifty_scans", total_scans >= 50),
        ("hundred_scans", total_scans >= 100),
        ("five_hundred_scans", total_scans >= 500),
        ("level_3", new_level >= 3),
        ("level_5", new_level >= 5),
        ("level_6", new_level >= 6),
    ]

    for badge_id, condition in badge_conditions:
        if condition and badge_id not in current_badges:
            new_badges.append(badge_id)

    # Also check tier badges
    tier_badge_map = {"pro": "pro_subscriber", "elite": "elite_subscriber"}
    tier_badge = tier_badge_map.get(tier)
    if tier_badge and tier_badge not in current_badges:
        new_badges.append(tier_badge)

    update_fields = {
        "xp": new_xp,
        "level": new_level,
        "updated_at": datetime.utcnow().isoformat(),
    }
    if new_badges:
        updated_badges = list(current_badges) + new_badges
        update_fields["badges"] = updated_badges

    sb.table("telegram_users").update(update_fields).eq("telegram_id", telegram_id).execute()

    return xp, new_badges


def process_payment(telegram_id: int, payload: str, amount: int,
                    currency: str, provider: str) -> Dict:
    """Process a payment and update user's tier or scan balance."""
    sb = get_supabase()
    if not sb:
        return {"success": False, "error": "Supabase not configured"}

    try:
        user = get_or_create_telegram_user(telegram_id)

        # Record payment
        sb.table("telegram_subscriptions").insert({
            "telegram_id": telegram_id,
            "tier": payload.split(":")[1] if ":" in payload else "unknown",
            "provider": provider,
            "amount": amount,
            "currency": currency,
            "payload": payload,
            "status": "active",
        }).execute()

        if payload.startswith("tier:"):
            tier = payload.split(":")[1]
            tier_config = TIERS.get(tier, TIERS["free"])
            new_limit = tier_config["scans_per_month"]
            sb.table("telegram_users").update({
                "tier": tier,
                "scans_limit": new_limit,
                "scans_used": 0,
                "scans_reset_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("telegram_id", telegram_id).execute()
            return {"success": True, "tier": tier, "scans_limit": new_limit}

        elif payload.startswith("pack:"):
            pack_key = payload.split(":")[1]
            pack_scans = {"5_scans": 5, "15_scans": 15, "50_scans": 50}.get(pack_key, 0)
            current_limit = user.get("scans_limit", 0)
            new_limit = current_limit + pack_scans
            sb.table("telegram_users").update({
                "scans_limit": new_limit,
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("telegram_id", telegram_id).execute()
            return {"success": True, "scans_added": pack_scans, "scans_limit": new_limit}

        return {"success": False, "error": "Unknown payload"}
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        return {"success": False, "error": str(e)}


def get_scan_history(telegram_id: int, limit: int = 50) -> List[Dict]:
    """Get scan history for a user."""
    sb = get_supabase()
    if not sb:
        return []
    try:
        resp = sb.table("telegram_scans").select("*").eq("telegram_id", telegram_id).order("created_at", desc=True).limit(limit).execute()
        return resp.data or []
    except Exception as e:
        logger.error(f"Failed to get scan history: {e}")
        return []


def get_leaderboard(limit: int = 20) -> List[Dict]:
    """Get top scanners leaderboard."""
    sb = get_supabase()
    if not sb:
        return []
    try:
        resp = sb.table("telegram_users").select(
            "telegram_id, username, first_name, total_scans, tier, xp, level"
        ).order("total_scans", desc=True).limit(limit).execute()
        return resp.data or []
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        return []


def record_broadcast(channel_id: str, channel_name: str, message_type: str,
                     content: str, message_id: Optional[int] = None,
                     metadata: Optional[Dict] = None) -> Dict:
    """Log a channel broadcast for analytics."""
    sb = get_supabase()
    if not sb:
        return {"success": False}
    try:
        sb.table("telegram_broadcasts").insert({
            "channel_id": channel_id,
            "channel_name": channel_name,
            "message_type": message_type,
            "content": content[:1000],  # truncate
            "message_id": message_id,
            "metadata": metadata or {},
        }).execute()
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to record broadcast: {e}")
        return {"success": False, "error": str(e)}
