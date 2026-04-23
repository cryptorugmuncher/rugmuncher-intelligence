"""
Gamification Service
====================
Hybrid architecture: Supabase for badges/user_badges, Redis for stats/progress/streaks.
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any

import redis.asyncio as redis

# Supabase client
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

_supabase = None

def get_supabase():
    global _supabase
    if _supabase is None and SUPABASE_URL and SUPABASE_KEY:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase

# Redis client (shared with main.py)
_redis: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "127.0.0.1"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD") or None,
            db=int(os.getenv("REDIS_DB", "0")),
            decode_responses=True
        )
    return _redis


# ═══════════════════════════════════════════════════════════
# LEVEL SYSTEM
# ═══════════════════════════════════════════════════════════

LEVELS = [
    (0, "Rookie", 1),
    (50, "Analyst", 2),
    (200, "Detective", 3),
    (500, "Special Agent", 4),
    (1000, "Master Investigator", 5),
    (2500, "Legend", 6),
]

def get_level_from_xp(xp: int) -> Dict[str, Any]:
    """Get level info from total XP."""
    current_level = 1
    current_title = "Rookie"
    next_threshold = 50
    
    for threshold, title, level_num in LEVELS:
        if xp >= threshold:
            current_level = level_num
            current_title = title
            next_threshold = threshold
    
    # Find next level threshold
    next_threshold = None
    for threshold, title, level_num in LEVELS:
        if level_num > current_level:
            next_threshold = threshold
            break
    
    if next_threshold is None:
        next_threshold = xp + 1000  # Legend keeps growing
    
    progress = min(100, int((xp / next_threshold) * 100)) if next_threshold else 100
    
    return {
        "level": current_level,
        "title": current_title,
        "xp": xp,
        "next_level_xp": next_threshold,
        "progress_percent": progress,
    }


# ═══════════════════════════════════════════════════════════
# XP AWARDS
# ═══════════════════════════════════════════════════════════

XP_TABLE = {
    "wallet_scan": 10,
    "first_scan": 50,
    "post_created": 25,
    "comment_created": 15,
    "upvote_given": 5,
    "upvote_received": 10,
    "login": 5,
    "streak_bonus": 20,
    "wallet_connected": 50,
    "report_submitted": 30,
    "report_verified": 100,
}


# ═══════════════════════════════════════════════════════════
# BADGE DEFINITIONS (fallback if DB is empty)
# ═══════════════════════════════════════════════════════════

DEFAULT_BADGES = [
    {"badge_id": "first_scan", "name": "First Steps", "emoji": "🔍", "description": "Completed your first wallet scan", "rarity": "common", "condition_type": "scan_count", "condition_config": {"value": 1}, "xp_value": 10},
    {"badge_id": "scan_100", "name": "Centurion", "emoji": "💯", "description": "100 scans completed", "rarity": "uncommon", "condition_type": "scan_count", "condition_config": {"value": 100}, "xp_value": 50},
    {"badge_id": "first_post", "name": "First Blood", "emoji": "🎯", "description": "Made your first post in The Trenches", "rarity": "common", "condition_type": "post_count", "condition_config": {"value": 1}, "xp_value": 10},
    {"badge_id": "top_contributor", "name": "Top Contributor", "emoji": "🏆", "description": "50 posts in The Trenches", "rarity": "rare", "condition_type": "post_count", "condition_config": {"value": 50}, "xp_value": 100},
    {"badge_id": "first_comment", "name": "First Words", "emoji": "💬", "description": "Left your first comment", "rarity": "common", "condition_type": "comment_count", "condition_config": {"value": 1}, "xp_value": 10},
    {"badge_id": "conversationalist", "name": "Conversationalist", "emoji": "🗣️", "description": "100 comments made", "rarity": "uncommon", "condition_type": "comment_count", "condition_config": {"value": 100}, "xp_value": 50},
    {"badge_id": "wallet_verified", "name": "Verified", "emoji": "✅", "description": "Verified wallet ownership", "rarity": "common", "condition_type": "wallet_connect", "condition_config": {"value": 1}, "xp_value": 10},
    {"badge_id": "alpha_caller", "name": "Alpha Caller", "emoji": "💎", "description": "10 verified alpha calls", "rarity": "rare", "condition_type": "verified_alpha", "condition_config": {"value": 10}, "xp_value": 150},
    {"badge_id": "guardian", "name": "Guardian", "emoji": "🛡️", "description": "10 verified scam reports", "rarity": "rare", "condition_type": "verified_scam_reports", "condition_config": {"value": 10}, "xp_value": 150},
    {"badge_id": "night_watch", "name": "Night Watch", "emoji": "🌙", "description": "Active 7 days straight", "rarity": "epic", "condition_type": "login_streak", "condition_config": {"value": 7}, "xp_value": 200},
    {"badge_id": "diamond_hands", "name": "Diamond Hands", "emoji": "💎", "description": "Held through 50%+ dump", "rarity": "legendary", "condition_type": "hold_through_dump", "condition_config": {"value": 50}, "xp_value": 500},
    {"badge_id": "early_adopter", "name": "Early Adopter", "emoji": "🚀", "description": "Joined during V2 beta", "rarity": "special", "condition_type": "manual", "condition_config": {}, "xp_value": 100},
]


# ═══════════════════════════════════════════════════════════
# REDIS KEY HELPERS
# ═══════════════════════════════════════════════════════════

def _user_stats_key(user_id: str) -> str:
    return f"rmi:gami:stats:{user_id}"

def _user_streak_key(user_id: str) -> str:
    return f"rmi:gami:streak:{user_id}"

def _leaderboard_key(category: str) -> str:
    return f"rmi:gami:lb:{category}"

def _badge_progress_key(user_id: str, badge_id: str) -> str:
    return f"rmi:gami:prog:{user_id}:{badge_id}"


# ═══════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════

async def get_user_stats(user_id: str) -> Dict[str, Any]:
    """Get user gamification stats from Redis."""
    r = await get_redis()
    data = await r.hgetall(_user_stats_key(user_id))
    
    defaults = {
        "post_count": 0,
        "comment_count": 0,
        "scan_count": 0,
        "upvote_received": 0,
        "upvote_given": 0,
        "login_streak": 0,
        "longest_streak": 0,
        "total_xp": 0,
        "current_level": 1,
        "wallet_connected": 0,
        "verified_alpha": 0,
        "verified_scam_reports": 0,
    }
    
    result = {**defaults}
    for k, v in data.items():
        try:
            result[k] = int(v)
        except ValueError:
            result[k] = v
    
    return result


async def update_user_stats(user_id: str, updates: Dict[str, int]) -> Dict[str, Any]:
    """Update user stats in Redis."""
    r = await get_redis()
    key = _user_stats_key(user_id)
    
    # Use HINCRBY for numeric fields
    pipe = r.pipeline()
    for field, value in updates.items():
        pipe.hincrby(key, field, value)
    await pipe.execute()
    
    return await get_user_stats(user_id)


async def record_activity(user_id: str, activity_type: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """Record a user activity and award XP."""
    r = await get_redis()
    
    # 1. Determine XP amount
    xp_amount = XP_TABLE.get(activity_type, 5)
    
    # 2. Update stats
    stat_updates: Dict[str, int] = {"total_xp": xp_amount}
    
    if activity_type == "wallet_scan":
        stat_updates["scan_count"] = 1
    elif activity_type == "post_created":
        stat_updates["post_count"] = 1
    elif activity_type == "comment_created":
        stat_updates["comment_count"] = 1
    elif activity_type == "upvote_given":
        stat_updates["upvote_given"] = 1
    elif activity_type == "upvote_received":
        stat_updates["upvote_received"] = 1
    elif activity_type == "wallet_connected":
        stat_updates["wallet_connected"] = 1
    elif activity_type == "report_verified":
        stat_updates["verified_scam_reports"] = 1
    elif activity_type == "alpha_verified":
        stat_updates["verified_alpha"] = 1
    
    # 3. Handle login streak
    if activity_type == "login":
        today = date.today().isoformat()
        streak_key = _user_streak_key(user_id)
        last_login = await r.hget(streak_key, "last_login_date")
        
        if last_login == today:
            pass  # Already logged in today
        elif last_login == (date.today() - timedelta(days=1)).isoformat():
            # Consecutive day
            await r.hincrby(streak_key, "current_streak", 1)
            await r.hset(streak_key, "last_login_date", today)
            current = await r.hget(streak_key, "current_streak")
            stat_updates["login_streak"] = 0  # Don't increment login_streak in stats
            stat_updates["total_xp"] = xp_amount
            if current and int(current) >= 7:
                stat_updates["total_xp"] += XP_TABLE.get("streak_bonus", 20)
        else:
            # Streak broken
            await r.hset(streak_key, "current_streak", 1)
            await r.hset(streak_key, "last_login_date", today)
    
    updated_stats = await update_user_stats(user_id, stat_updates)
    
    # 4. Update leaderboard
    await r.zadd(_leaderboard_key("xp"), {user_id: updated_stats["total_xp"]})
    if "post_count" in stat_updates:
        await r.zadd(_leaderboard_key("posts"), {user_id: updated_stats["post_count"]})
    if "comment_count" in stat_updates:
        await r.zadd(_leaderboard_key("comments"), {user_id: updated_stats["comment_count"]})
    
    # 5. Check for new badges
    new_badges = await check_and_award_badges(user_id, updated_stats)
    
    return {
        "xp_gained": xp_amount,
        "stats": updated_stats,
        "new_badges": new_badges,
        "level": get_level_from_xp(updated_stats["total_xp"]),
    }


async def get_badges_from_db() -> List[Dict[str, Any]]:
    """Load badge definitions from Supabase or fallback to defaults."""
    sb = get_supabase()
    if sb:
        try:
            result = sb.table("badges").select("*").execute()
            if result.data and len(result.data) > 0:
                return result.data
        except Exception as e:
            print(f"[GAMI] Failed to load badges from DB: {e}")
    return DEFAULT_BADGES


async def _get_earned_badge_ids(user_id: str) -> set:
    """Get earned badge IDs from Redis + Supabase."""
    earned = set()
    r = await get_redis()
    redis_badges = await r.smembers(f"rmi:gami:badges:{user_id}")
    earned.update(redis_badges)
    
    sb = get_supabase()
    if sb:
        try:
            result = sb.table("user_badges").select("badge_id").eq("user_id", user_id).execute()
            if result.data:
                earned.update(row["badge_id"] for row in result.data)
        except Exception as e:
            print(f"[GAMI] Failed to load earned badges from DB: {e}")
    
    return earned


async def check_and_award_badges(user_id: str, stats: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Check badge conditions and award any new badges."""
    if stats is None:
        stats = await get_user_stats(user_id)
    
    badges = await get_badges_from_db()
    new_badges = []
    earned_ids = await _get_earned_badge_ids(user_id)
    
    for badge in badges:
        badge_id = badge.get("badge_id") or badge.get("id")
        if not badge_id or badge_id in earned_ids:
            continue
        
        condition_type = badge.get("condition_type", "")
        condition_config = badge.get("condition_config", {})
        target_value = condition_config.get("value", 1)
        
        # Check condition
        earned = False
        if condition_type == "scan_count" and stats.get("scan_count", 0) >= target_value:
            earned = True
        elif condition_type == "post_count" and stats.get("post_count", 0) >= target_value:
            earned = True
        elif condition_type == "comment_count" and stats.get("comment_count", 0) >= target_value:
            earned = True
        elif condition_type == "wallet_connect" and stats.get("wallet_connected", 0) >= target_value:
            earned = True
        elif condition_type == "verified_alpha" and stats.get("verified_alpha", 0) >= target_value:
            earned = True
        elif condition_type == "verified_scam_reports" and stats.get("verified_scam_reports", 0) >= target_value:
            earned = True
        elif condition_type == "login_streak" and stats.get("login_streak", 0) >= target_value:
            earned = True
        elif condition_type == "manual":
            earned = False  # Manual badges are awarded by admins
        
        if earned:
            # Always store in Redis first (resilient)
            r = await get_redis()
            await r.sadd(f"rmi:gami:badges:{user_id}", badge_id)
            earned_ids.add(badge_id)
            new_badges.append(badge)
            
            # Try Supabase as well
            sb = get_supabase()
            if sb:
                try:
                    sb.table("user_badges").insert({
                        "user_id": user_id,
                        "badge_id": badge_id,
                        "earned_via": "automatic",
                        "metadata": {"stats_snapshot": stats},
                    }).execute()
                except Exception as e:
                    print(f"[GAMI] Supabase badge insert failed (badge stored in Redis): {e}")
    
    return new_badges


async def get_user_gamification_profile(user_id: str) -> Dict[str, Any]:
    """Get full gamification profile for a user."""
    stats = await get_user_stats(user_id)
    level_info = get_level_from_xp(stats["total_xp"])
    
    # Get earned badge IDs from Redis + Supabase
    earned_ids = await _get_earned_badge_ids(user_id)
    
    # Build earned badge list from definitions
    all_badges = await get_badges_from_db()
    earned_badges = [b for b in all_badges if (b.get("badge_id") or b.get("id")) in earned_ids]
    
    # Get streak info
    r = await get_redis()
    streak_data = await r.hgetall(_user_streak_key(user_id))
    
    return {
        "user_id": user_id,
        "stats": stats,
        "level": level_info,
        "badges": earned_badges,
        "streak": {
            "current": int(streak_data.get("current_streak", 0)),
            "longest": int(streak_data.get("longest_streak", 0)),
            "last_login": streak_data.get("last_login_date"),
        },
    }


async def get_leaderboard(category: str = "xp", period: str = "all_time", limit: int = 50) -> List[Dict[str, Any]]:
    """Get leaderboard from Redis sorted set."""
    r = await get_redis()
    key = _leaderboard_key(category)
    
    # Get top N with scores
    results = await r.zrevrange(key, 0, limit - 1, withscores=True)
    
    leaderboard = []
    for user_id, score in results:
        stats = await get_user_stats(user_id)
        level = get_level_from_xp(stats.get("total_xp", 0))
        leaderboard.append({
            "user_id": user_id,
            "score": int(score),
            "level": level,
            "stats": stats,
        })
    
    return leaderboard


async def get_all_badges_with_progress(user_id: str) -> List[Dict[str, Any]]:
    """Get all badges with user's progress toward each."""
    stats = await get_user_stats(user_id)
    badges = await get_badges_from_db()
    earned_ids = await _get_earned_badge_ids(user_id)
    
    result = []
    for badge in badges:
        badge_id = badge.get("badge_id") or badge.get("id")
        condition_type = badge.get("condition_type", "")
        condition_config = badge.get("condition_config", {})
        target = condition_config.get("value", 1)
        
        # Calculate current progress
        current = 0
        if condition_type == "scan_count":
            current = stats.get("scan_count", 0)
        elif condition_type == "post_count":
            current = stats.get("post_count", 0)
        elif condition_type == "comment_count":
            current = stats.get("comment_count", 0)
        elif condition_type == "wallet_connect":
            current = stats.get("wallet_connected", 0)
        elif condition_type == "verified_alpha":
            current = stats.get("verified_alpha", 0)
        elif condition_type == "verified_scam_reports":
            current = stats.get("verified_scam_reports", 0)
        elif condition_type == "login_streak":
            current = stats.get("login_streak", 0)
        
        progress_pct = min(100, int((current / target) * 100)) if target > 0 else 0
        
        result.append({
            **badge,
            "earned": badge_id in earned_ids,
            "progress": {
                "current": current,
                "target": target,
                "percentage": progress_pct,
            },
        })
    
    return result
