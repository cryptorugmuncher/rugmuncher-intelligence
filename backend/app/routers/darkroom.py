"""
Darkroom Control Center Router
==============================
Web3 + AI-first command center for the entire RMI ecosystem.
Market intelligence, content command, social posting, project control.
"""

import os
import sys
import json
import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/darkroom", tags=["darkroom"])

# ── Auth helper ──
async def _verify_darkroom(request: Request):
    admin_key = os.getenv("ADMIN_API_KEY", "dev-key-change-me")
    key = request.headers.get("X-Admin-Key", "")
    if key != admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True

# ═══════════════════════════════════════════════════════════════
# MARKET INTELLIGENCE
# ═══════════════════════════════════════════════════════════════

@router.get("/market/briefing")
async def market_briefing(request: Request, _=Depends(_verify_darkroom)):
    """AI-curated market intelligence briefing."""
    try:
        from main import get_redis
        r = await get_redis()

        # Gather signals from Redis caches
        trending_raw = await r.zrevrange("rmi:trending:tokens", 0, 9, withscores=True)
        whale_alerts = await r.lrange("rmi:alerts:whale", 0, 4)
        rug_alerts = await r.lrange("rmi:alerts:rug", 0, 4)
        alpha_signals = await r.lrange("rmi:alpha:signals", 0, 9)

        # Parse trending
        trending = []
        for token, score in trending_raw:
            info = await r.hgetall(f"rmi:token:{token}")
            trending.append({
                "symbol": token,
                "name": info.get("name", token),
                "price": float(info.get("price", 0)),
                "change_24h": float(info.get("change_24h", 0)),
                "volume_24h": float(info.get("volume_24h", 0)),
                "risk_score": int(info.get("risk_score", 0)),
                "momentum": round(score, 2),
            })

        # Parse alerts
        def _parse_alerts(raw):
            out = []
            for item in raw:
                try:
                    out.append(json.loads(item))
                except Exception:
                    pass
            return out

        briefing = {
            "generated_at": datetime.utcnow().isoformat(),
            "market_sentiment": await r.get("rmi:sentiment:global") or "neutral",
            "fear_greed_index": int(await r.get("rmi:fear_greed") or 50),
            "trending_tokens": trending,
            "whale_movements": _parse_alerts(whale_alerts),
            "rug_detections": _parse_alerts(rug_alerts),
            "alpha_signals": _parse_alerts(alpha_signals),
            "total_scans_24h": int(await r.get("rmi:metrics:scans:24h") or 0),
            "active_investigations": len(await r.hgetall("rmi:cases") or {}),
        }
        return briefing
    except Exception as e:
        logger.error(f"[Darkroom] Market briefing error: {e}")
        # Graceful fallback with demo data structure
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "market_sentiment": "neutral",
            "fear_greed_index": 50,
            "trending_tokens": [],
            "whale_movements": [],
            "rug_detections": [],
            "alpha_signals": [],
            "total_scans_24h": 0,
            "active_investigations": 0,
            "error": str(e),
        }


@router.get("/market/trending")
async def market_trending(request: Request, limit: int = 20, _=Depends(_verify_darkroom)):
    """Trending tokens with risk analysis."""
    try:
        from main import get_redis
        r = await get_redis()
        trending_raw = await r.zrevrange("rmi:trending:tokens", 0, limit - 1, withscores=True)
        results = []
        for token, score in trending_raw:
            info = await r.hgetall(f"rmi:token:{token}")
            results.append({
                "symbol": token,
                "name": info.get("name", token),
                "price": float(info.get("price", 0)),
                "change_1h": float(info.get("change_1h", 0)),
                "change_24h": float(info.get("change_24h", 0)),
                "volume_24h": float(info.get("volume_24h", 0)),
                "market_cap": float(info.get("market_cap", 0)),
                "liquidity": float(info.get("liquidity", 0)),
                "holders": int(info.get("holders", 0)),
                "risk_score": int(info.get("risk_score", 0)),
                "risk_level": info.get("risk_level", "UNKNOWN"),
                "momentum": round(score, 2),
                "last_updated": info.get("last_updated"),
            })
        return {"tokens": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# CONTENT COMMAND CENTER
# ═══════════════════════════════════════════════════════════════

class ContentDraftRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    tags: List[str] = Field(default=[])
    category: str = Field(default="intel")
    scheduled_for: Optional[str] = None
    platforms: List[str] = Field(default=["telegram"])
    tone: str = Field(default="analytical")

@router.post("/content/draft")
async def create_content_draft(req: ContentDraftRequest, request: Request, _=Depends(_verify_darkroom)):
    """Save a content draft to Redis."""
    try:
        from main import get_redis
        r = await get_redis()
        draft_id = f"draft-{datetime.utcnow().timestamp()}-{os.urandom(4).hex()}"
        draft = {
            "id": draft_id,
            "title": req.title,
            "body": req.body,
            "tags": req.tags,
            "category": req.category,
            "scheduled_for": req.scheduled_for,
            "platforms": req.platforms,
            "tone": req.tone,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        await r.hset("rmi:content:drafts", draft_id, json.dumps(draft))
        return {"draft": draft, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/drafts")
async def list_content_drafts(request: Request, status: Optional[str] = None, _=Depends(_verify_darkroom)):
    """List content drafts."""
    try:
        from main import get_redis
        r = await get_redis()
        drafts_raw = await r.hgetall("rmi:content:drafts") or {}
        drafts = []
        for k, v in drafts_raw.items():
            try:
                d = json.loads(v)
                if status is None or d.get("status") == status:
                    drafts.append(d)
            except Exception:
                pass
        drafts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return {"drafts": drafts, "total": len(drafts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/publish")
async def publish_content(draft_id: str, request: Request, _=Depends(_verify_darkroom)):
    """Publish a draft and syndicate to platforms."""
    try:
        from main import get_redis
        r = await get_redis()
        draft_raw = await r.hget("rmi:content:drafts", draft_id)
        if not draft_raw:
            raise HTTPException(status_code=404, detail="Draft not found")
        draft = json.loads(draft_raw)
        draft["status"] = "published"
        draft["published_at"] = datetime.utcnow().isoformat()
        await r.hset("rmi:content:drafts", draft_id, json.dumps(draft))
        await r.lpush("rmi:content:published", json.dumps(draft))

        # Queue for syndication
        for platform in draft.get("platforms", []):
            await r.lpush(f"rmi:syndicate:{platform}", json.dumps(draft))

        return {"draft": draft, "status": "published", "syndicated_to": draft.get("platforms", [])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/stats")
async def content_stats(request: Request, _=Depends(_verify_darkroom)):
    """Content performance stats."""
    try:
        from main import get_redis
        r = await get_redis()
        drafts = await r.hlen("rmi:content:drafts")
        published = await r.llen("rmi:content:published")
        scheduled = await r.llen("rmi:content:scheduled")
        return {
            "drafts": drafts,
            "published": published,
            "scheduled": scheduled,
            "total_words": int(await r.get("rmi:content:total_words") or 0),
            "top_category": await r.get("rmi:content:top_category") or "intel",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# SOCIAL POSTING ENGINE
# ═══════════════════════════════════════════════════════════════

class TelegramPostRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    channel: str = Field(default="@rmi_alpha_alerts")
    parse_mode: str = Field(default="HTML")
    pin: bool = Field(default=False)
    draft_id: Optional[str] = None

@router.post("/social/telegram/post")
async def telegram_post(req: TelegramPostRequest, request: Request, _=Depends(_verify_darkroom)):
    """Post directly to Telegram channel via bot API."""
    try:
        # Use the first available bot token
        from main import get_redis
        r = await get_redis()
        bots_raw = await r.hgetall("rmi:bots") or {}
        token = None
        for k, v in bots_raw.items():
            bot_data = json.loads(v)
            if "alpha" in k or "alerts" in k:
                token = bot_data.get("token")
                break
        if not token:
            token = os.getenv("TELEGRAM_BOT_TOKEN", "")

        if not token:
            raise HTTPException(status_code=503, detail="No Telegram bot token configured")

        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "chat_id": req.channel,
                "text": req.message,
                "parse_mode": req.parse_mode,
                "disable_web_page_preview": False,
            }
            resp = await client.post(telegram_url, json=payload)
            result = resp.json()

        if result.get("ok"):
            # Log the post
            post_entry = {
                "id": f"tg-{datetime.utcnow().timestamp()}",
                "platform": "telegram",
                "channel": req.channel,
                "message_preview": req.message[:100],
                "sent_at": datetime.utcnow().isoformat(),
                "message_id": result["result"].get("message_id"),
            }
            await r.lpush("rmi:social:history", json.dumps(post_entry))
            return {"status": "sent", "telegram": result, "post": post_entry}
        else:
            raise HTTPException(status_code=502, detail=result.get("description", "Telegram API error"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram post failed: {e}")


@router.get("/social/telegram/stats")
async def telegram_stats(request: Request, _=Depends(_verify_darkroom)):
    """Telegram bot channel stats."""
    try:
        from main import get_redis
        r = await get_redis()
        history = await r.lrange("rmi:social:history", 0, 99)
        posts = []
        for item in history:
            try:
                posts.append(json.loads(item))
            except Exception:
                pass
        telegram_posts = [p for p in posts if p.get("platform") == "telegram"]
        return {
            "posts_today": len([p for p in telegram_posts if p.get("sent_at", "").startswith(datetime.utcnow().strftime("%Y-%m-%d"))]),
            "posts_total": len(telegram_posts),
            "recent_posts": telegram_posts[:10],
            "channels": list(set(p.get("channel", "") for p in telegram_posts)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/social/ghost/stats")
async def ghost_stats(request: Request, _=Depends(_verify_darkroom)):
    """Ghost/Mirror publishing stats."""
    try:
        from main import get_redis
        r = await get_redis()
        mirror_posts = await r.llen("rmi:mirror:published")
        newsletter_subs = int(await r.get("rmi:newsletter:subscribers") or 0)
        return {
            "mirror_posts": mirror_posts,
            "newsletter_subscribers": newsletter_subs,
            "last_publish": await r.get("rmi:mirror:last_publish") or None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# PROJECT COMMAND & CONTROL
# ═══════════════════════════════════════════════════════════════

@router.get("/project/status")
async def project_status(request: Request, _=Depends(_verify_darkroom)):
    """Complete project health dashboard."""
    try:
        from main import get_redis
        r = await get_redis()

        # System health
        agents_raw = await r.hgetall("rmi:agents") or {}
        agents_online = sum(1 for a in agents_raw.values() if json.loads(a).get("status") == "online")
        cases = await r.hgetall("rmi:cases") or {}
        wallets = await r.hgetall("rmi:wallets") or {}

        # Content health
        drafts = await r.hlen("rmi:content:drafts")
        published = await r.llen("rmi:content:published")

        # Social health
        social_history = await r.llen("rmi:social:history")

        # Queue health
        queue_depth = await r.llen("rmi:queue:system")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health_score": min(100, int(agents_online / max(len(agents_raw), 1) * 100)),
            "agents": {"total": len(agents_raw), "online": agents_online},
            "investigations": {"active": len(cases), "wallets_tracked": len(wallets)},
            "content": {"drafts": drafts, "published": published, "ready_to_publish": drafts},
            "social": {"posts_sent": social_history},
            "queues": {"system": queue_depth},
            "uptime_hours": int(await r.get("rmi:uptime_hours") or 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/mesh")
async def agents_mesh(request: Request, _=Depends(_verify_darkroom)):
    """AI Agent Mesh visualization data."""
    try:
        from main import get_redis
        r = await get_redis()
        agents_raw = await r.hgetall("rmi:agents") or {}
        nodes = []
        edges = []
        for agent_id, agent_json in agents_raw.items():
            agent = json.loads(agent_json)
            nodes.append({
                "id": agent_id,
                "name": agent.get("name", agent_id.upper()),
                "role": agent.get("role", "Agent"),
                "tier": agent.get("tier", "T3"),
                "status": agent.get("status", "offline"),
                "load": float(agent.get("load", 0)),
                "tasks_completed": int(agent.get("tasks_completed", 0)),
                "last_active": agent.get("last_active"),
            })
            # Connect to coordinator
            edges.append({"source": agent_id, "target": "nexus", "type": "reports_to"})

        # Always include nexus
        if not any(n["id"] == "nexus" for n in nodes):
            nodes.append({"id": "nexus", "name": "NEXUS", "role": "Coordinator", "tier": "T0", "status": "online", "load": 0.3, "tasks_completed": 9999})

        return {"nodes": nodes, "edges": edges, "mesh_health": sum(1 for n in nodes if n["status"] == "online") / max(len(nodes), 1)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/active")
async def active_tasks(request: Request, limit: int = 50, _=Depends(_verify_darkroom)):
    """Active task queue with priorities."""
    try:
        from main import get_redis
        r = await get_redis()
        tasks_raw = await r.lrange("rmi:queue:system", 0, limit - 1)
        tasks = []
        for item in tasks_raw:
            try:
                tasks.append(json.loads(item))
            except Exception:
                pass
        return {"tasks": tasks, "total": len(tasks), "queue_depth": await r.llen("rmi:queue:system")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# ADVISOR AGENT
# ═══════════════════════════════════════════════════════════════

class AdvisorChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default={})
    session_id: Optional[str] = None

class AdvisorActionRequest(BaseModel):
    action: str = Field(..., description="scan_wallet, post_telegram, publish_content, trigger_alert, run_investigation, clear_cache")
    params: Dict[str, Any] = Field(default={})
    confirm: bool = Field(default=False)

@router.post("/advisor/chat")
async def advisor_chat(req: AdvisorChatRequest, request: Request, _=Depends(_verify_darkroom)):
    """Chat with the Advisor Agent. It has full context of the project."""
    try:
        from main import get_redis
        r = await get_redis()

        # Build project context
        agents_raw = await r.hgetall("rmi:agents") or {}
        agents_online = sum(1 for a in agents_raw.values() if json.loads(a).get("status") == "online")
        cases = len(await r.hgetall("rmi:cases") or {})
        scans_24h = int(await r.get("rmi:metrics:scans:24h") or 0)
        queue_depth = await r.llen("rmi:queue:system")
        drafts = await r.hlen("rmi:content:drafts")

        # Simple rule-based advisor (can be upgraded to LLM)
        msg = req.message.lower()
        response = {"type": "text", "content": "", "suggestions": [], "actions": []}

        if any(w in msg for w in ["status", "health", "how are we"]):
            response["content"] = (
                f"Project Status: {agents_online}/{len(agents_raw)} agents online. "
                f"{cases} active investigations. {scans_24h} scans in 24h. "
                f"{queue_depth} tasks queued. {drafts} content drafts waiting."
            )
            response["suggestions"] = ["View system panel", "Check agent mesh", "Review queue"]
            response["actions"] = [{"label": "Open System", "action": "navigate", "target": "system"}]

        elif any(w in msg for w in ["scan", "check wallet", "analyze"]):
            response["content"] = "I can help you scan a wallet or contract. Provide the address and chain (solana/ethereum)."
            response["suggestions"] = ["Scan recent flagged wallet", "Run deep investigation", "Check trending tokens"]
            response["actions"] = [{"label": "Open Scanner", "action": "navigate", "target": "wallet-scan"}]

        elif any(w in msg for w in ["post", "telegram", "social"]):
            response["content"] = "I can draft and post to Telegram. What message do you want to send, and to which channel?"
            response["suggestions"] = ["Post market briefing", "Alert subscribers", "Share alpha signal"]
            response["actions"] = [{"label": "Open Social", "action": "navigate", "target": "social"}]

        elif any(w in msg for w in ["content", "draft", "write", "article"]):
            response["content"] = f"You have {drafts} drafts pending. I can help draft new content or publish existing drafts."
            response["suggestions"] = ["Create market briefing", "Draft investigation report", "Publish ready drafts"]
            response["actions"] = [{"label": "Open Content", "action": "navigate", "target": "content"}]

        elif any(w in msg for w in ["alert", "rug", "scam", "whale"]):
            response["content"] = "I monitor alerts in real-time. Would you like to see recent detections or configure alert thresholds?"
            response["suggestions"] = ["Show recent rugs", "Configure whale alerts", "View alert history"]
            response["actions"] = [{"label": "View Alerts", "action": "navigate", "target": "alerts"}]

        elif any(w in msg for w in ["agent", "mesh", "nexus", "scout"]):
            response["content"] = f"The agent mesh has {agents_online} agents online. NEXUS is coordinating operations."
            response["suggestions"] = ["View agent mesh", "Assign task to agent", "Check agent logs"]
            response["actions"] = [{"label": "View Mesh", "action": "navigate", "target": "agents"}]

        else:
            response["content"] = (
                "I'm your Advisor Agent. I can help you: scan wallets, manage content, "
                "post to socials, monitor alerts, check system health, or coordinate the AI agent mesh. "
                "What would you like to do?"
            )
            response["suggestions"] = [
                "Show project status",
                "Scan a wallet",
                "Draft content",
                "Post to Telegram",
                "View market intel",
            ]

        # Store conversation
        session = req.session_id or "default"
        await r.lpush(f"rmi:advisor:{session}", json.dumps({
            "role": "assistant",
            "content": response["content"],
            "timestamp": datetime.utcnow().isoformat(),
        }))
        await r.ltrim(f"rmi:advisor:{session}", 0, 99)

        return {
            "response": response,
            "session_id": session,
            "project_context": {
                "agents_online": agents_online,
                "agents_total": len(agents_raw),
                "investigations": cases,
                "scans_24h": scans_24h,
                "queue_depth": queue_depth,
                "drafts": drafts,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advisor/suggest")
async def advisor_suggest(request: Request, _=Depends(_verify_darkroom)):
    """Get proactive suggestions from the Advisor based on current project state."""
    try:
        from main import get_redis
        r = await get_redis()

        suggestions = []
        agents_raw = await r.hgetall("rmi:agents") or {}
        agents_online = sum(1 for a in agents_raw.values() if json.loads(a).get("status") == "online")
        queue_depth = await r.llen("rmi:queue:system")
        drafts = await r.hlen("rmi:content:drafts")
        alerts = await r.llen("rmi:alert:history")

        if agents_online < len(agents_raw):
            suggestions.append({
                "priority": "high",
                "icon": "alert",
                "title": f"{len(agents_raw) - agents_online} agents offline",
                "description": "Some AI agents are not responding. Check the agent mesh.",
                "action": {"label": "Check Agents", "target": "agents"}
            })

        if queue_depth > 20:
            suggestions.append({
                "priority": "medium",
                "icon": "queue",
                "title": f"{queue_depth} tasks queued",
                "description": "Task queue is backing up. Consider scaling workers.",
                "action": {"label": "View Queue", "target": "system"}
            })

        if drafts > 0:
            suggestions.append({
                "priority": "low",
                "icon": "content",
                "title": f"{drafts} content drafts ready",
                "description": "You have unpublished content waiting.",
                "action": {"label": "View Drafts", "target": "content"}
            })

        if alerts > 0:
            suggestions.append({
                "priority": "info",
                "icon": "bell",
                "title": f"{alerts} recent alerts",
                "description": "New alerts require attention.",
                "action": {"label": "View Alerts", "target": "alerts"}
            })

        if not suggestions:
            suggestions.append({
                "priority": "info",
                "icon": "check",
                "title": "All systems nominal",
                "description": "Everything is running smoothly. Consider reviewing market intelligence.",
                "action": {"label": "Market Intel", "target": "market"}
            })

        return {"suggestions": suggestions, "generated_at": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advisor/act")
async def advisor_act(req: AdvisorActionRequest, request: Request, _=Depends(_verify_darkroom)):
    """Execute an action through the Advisor Agent."""
    try:
        from main import get_redis
        r = await get_redis()

        result = {"status": "queued", "action": req.action, "message": ""}

        if req.action == "scan_wallet":
            addr = req.params.get("address", "")
            chain = req.params.get("chain", "solana")
            if not addr:
                raise HTTPException(status_code=400, detail="Address required")
            await r.lpush("rmi:queue:system", json.dumps({
                "type": "wallet_scan",
                "address": addr,
                "chain": chain,
                "timestamp": datetime.utcnow().isoformat(),
            }))
            result["message"] = f"Wallet scan queued for {addr[:8]}... on {chain}"

        elif req.action == "post_telegram":
            msg = req.params.get("message", "")
            channel = req.params.get("channel", "@rmi_alpha_alerts")
            if not msg:
                raise HTTPException(status_code=400, detail="Message required")
            await r.lpush("rmi:syndicate:telegram", json.dumps({
                "message": msg,
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat(),
            }))
            result["message"] = f"Telegram post queued for {channel}"

        elif req.action == "publish_content":
            draft_id = req.params.get("draft_id", "")
            if draft_id:
                await r.lpush("rmi:queue:system", json.dumps({
                    "type": "publish_content",
                    "draft_id": draft_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }))
                result["message"] = f"Content publish queued for draft {draft_id[:8]}..."
            else:
                raise HTTPException(status_code=400, detail="Draft ID required")

        elif req.action == "trigger_alert":
            alert_msg = req.params.get("message", "Advisor-triggered alert")
            await r.lpush("rmi:alert:history", json.dumps({
                "id": f"adv-{datetime.utcnow().timestamp()}",
                "message": alert_msg,
                "severity": req.params.get("severity", "info"),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "advisor",
            }))
            result["message"] = "Alert triggered and logged"

        elif req.action == "clear_cache":
            await r.flushdb()
            result["message"] = "Cache cleared"

        elif req.action == "run_investigation":
            target = req.params.get("target", "")
            inv_type = req.params.get("type", "wallet")
            if not target:
                raise HTTPException(status_code=400, detail="Investigation target required")
            await r.lpush("rmi:queue:system", json.dumps({
                "type": "investigation",
                "target": target,
                "inv_type": inv_type,
                "timestamp": datetime.utcnow().isoformat(),
            }))
            result["message"] = f"Investigation queued: {inv_type} → {target[:12]}..."

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {req.action}")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# AUTO-CONTENT PIPELINE — Prepares content while you sleep
# ═══════════════════════════════════════════════════════════════

class AutoDraftRequest(BaseModel):
    source: str = Field(default="market_intel", description="market_intel, whale_alert, rug_alert, trending, daily_briefing")
    count: int = Field(default=3, ge=1, le=10)
    tone: str = Field(default="analytical")

@router.post("/content/auto-generate")
async def auto_generate_content(req: AutoDraftRequest, request: Request, _=Depends(_verify_darkroom)):
    """Generate content drafts from live market signals automatically."""
    try:
        from main import get_redis
        r = await get_redis()
        generated = []

        if req.source == "market_intel":
            # Pull trending tokens and craft analysis drafts
            trending_raw = await r.zrevrange("rmi:trending:tokens", 0, req.count - 1, withscores=True)
            for token, score in trending_raw:
                info = await r.hgetall(f"rmi:token:{token}")
                if not info:
                    continue
                change = float(info.get("change_24h", 0))
                risk = int(info.get("risk_score", 0))
                draft_id = f"auto-market-{datetime.utcnow().timestamp()}-{token}"
                title = f"{'🚨' if risk > 70 else '🔥' if change > 20 else '📊'} {info.get('name', token)} Analysis: {change:+.1f}% in 24h"
                body = (
                    f"<b>{info.get('name', token)} (${token.upper()})</b>\n\n"
                    f"Price: ${float(info.get('price', 0)):.6f}\n"
                    f"24h Change: {change:+.2f}%\n"
                    f"Volume: ${float(info.get('volume_24h', 0))/1e6:.1f}M\n"
                    f"Liquidity: ${float(info.get('liquidity', 0))/1e6:.1f}M\n"
                    f"Holders: {int(info.get('holders', 0)):,}\n"
                    f"Risk Score: {risk}/100\n\n"
                    f"{'⚠️ High risk detected — exercise caution.' if risk > 70 else '✅ Moderate risk profile.' if risk > 40 else '🟢 Low risk observation.'}"
                )
                draft = {
                    "id": draft_id,
                    "title": title,
                    "body": body,
                    "tags": [token, "market-intel", "auto-generated"],
                    "category": "intel",
                    "scheduled_for": None,
                    "platforms": ["telegram"],
                    "tone": req.tone,
                    "status": "prepared",
                    "source": req.source,
                    "auto_generated": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "requires_approval": True,
                }
                await r.hset("rmi:content:drafts", draft_id, json.dumps(draft))
                generated.append(draft)

        elif req.source == "daily_briefing":
            # Generate a daily market briefing draft
            scans_24h = int(await r.get("rmi:metrics:scans:24h") or 0)
            cases = len(await r.hgetall("rmi:cases") or {})
            sentiment = await r.get("rmi:sentiment:global") or "neutral"
            fear_greed = int(await r.get("rmi:fear_greed") or 50)

            draft_id = f"auto-briefing-{datetime.utcnow().strftime('%Y%m%d')}"
            title = f"📰 RMI Daily Briefing — {datetime.utcnow().strftime('%B %d, %Y')}"
            body = (
                f"<b>Good morning. Here's your daily intelligence briefing.</b>\n\n"
                f"🌍 Market Sentiment: {sentiment.upper()}\n"
                f"😰 Fear & Greed: {fear_greed}/100 ({'Extreme Fear' if fear_greed < 20 else 'Fear' if fear_greed < 40 else 'Neutral' if fear_greed < 60 else 'Greed' if fear_greed < 80 else 'Extreme Greed'})\n"
                f"🔍 Scans Run (24h): {scans_24h:,}\n"
                f"🕵️ Active Investigations: {cases}\n\n"
                f"<i>Detailed token analysis and whale alerts available in the Darkroom.</i>"
            )
            draft = {
                "id": draft_id,
                "title": title,
                "body": body,
                "tags": ["daily-briefing", "auto-generated"],
                "category": "announcement",
                "scheduled_for": None,
                "platforms": ["telegram", "newsletter"],
                "tone": req.tone,
                "status": "prepared",
                "source": req.source,
                "auto_generated": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "requires_approval": True,
            }
            await r.hset("rmi:content:drafts", draft_id, json.dumps(draft))
            generated.append(draft)

        elif req.source == "whale_alert":
            whale_raw = await r.lrange("rmi:alerts:whale", 0, req.count - 1)
            for i, item in enumerate(whale_raw):
                try:
                    alert = json.loads(item)
                    draft_id = f"auto-whale-{datetime.utcnow().timestamp()}-{i}"
                    title = f"🐋 Whale Alert: {alert.get('description', 'Large movement detected')}"
                    body = (
                        f"<b>Whale Movement Detected</b>\n\n"
                        f"{alert.get('description', 'Significant wallet activity observed.')}\n\n"
                        f"Confidence: {alert.get('confidence', 'medium')}\n"
                        f"Chain: {alert.get('chain', 'unknown')}\n"
                    )
                    draft = {
                        "id": draft_id,
                        "title": title,
                        "body": body,
                        "tags": ["whale-alert", "auto-generated"],
                        "category": "intel",
                        "platforms": ["telegram"],
                        "tone": req.tone,
                        "status": "prepared",
                        "source": req.source,
                        "auto_generated": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "requires_approval": True,
                    }
                    await r.hset("rmi:content:drafts", draft_id, json.dumps(draft))
                    generated.append(draft)
                except Exception:
                    pass

        elif req.source == "rug_alert":
            rug_raw = await r.lrange("rmi:alerts:rug", 0, req.count - 1)
            for i, item in enumerate(rug_raw):
                try:
                    alert = json.loads(item)
                    draft_id = f"auto-rug-{datetime.utcnow().timestamp()}-{i}"
                    title = f"🚨 Rug Pull Warning: {alert.get('token', 'Unknown Token')}"
                    body = (
                        f"<b>🚨 CRITICAL: Potential Rug Pull Detected</b>\n\n"
                        f"Token: {alert.get('token', 'Unknown')}\n"
                        f"Risk Score: {alert.get('risk_score', 'N/A')}/100\n"
                        f"Flags: {', '.join(alert.get('flags', []))}\n\n"
                        f"<b>Do not interact with this contract.</b>"
                    )
                    draft = {
                        "id": draft_id,
                        "title": title,
                        "body": body,
                        "tags": ["rug-alert", "critical", "auto-generated"],
                        "category": "announcement",
                        "platforms": ["telegram"],
                        "tone": "urgent",
                        "status": "prepared",
                        "source": req.source,
                        "auto_generated": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "requires_approval": True,
                    }
                    await r.hset("rmi:content:drafts", draft_id, json.dumps(draft))
                    generated.append(draft)
                except Exception:
                    pass

        return {
            "generated": generated,
            "count": len(generated),
            "source": req.source,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/prepared")
async def list_prepared_content(request: Request, _=Depends(_verify_darkroom)):
    """Get all content waiting for approval (prepared while you slept)."""
    try:
        from main import get_redis
        r = await get_redis()
        drafts_raw = await r.hgetall("rmi:content:drafts") or {}
        prepared = []
        for k, v in drafts_raw.items():
            try:
                d = json.loads(v)
                if d.get("status") == "prepared" and d.get("requires_approval"):
                    prepared.append(d)
            except Exception:
                pass
        prepared.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return {
            "prepared": prepared,
            "count": len(prepared),
            "by_source": {
                "market_intel": len([p for p in prepared if p.get("source") == "market_intel"]),
                "daily_briefing": len([p for p in prepared if p.get("source") == "daily_briefing"]),
                "whale_alert": len([p for p in prepared if p.get("source") == "whale_alert"]),
                "rug_alert": len([p for p in prepared if p.get("source") == "rug_alert"]),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ApproveContentRequest(BaseModel):
    draft_id: str
    decision: str = Field(..., description="approve, reject, schedule")
    scheduled_for: Optional[str] = None

@router.post("/content/approve")
async def approve_content(req: ApproveContentRequest, request: Request, _=Depends(_verify_darkroom)):
    """Approve, reject, or schedule prepared content."""
    try:
        from main import get_redis
        r = await get_redis()
        draft_raw = await r.hget("rmi:content:drafts", req.draft_id)
        if not draft_raw:
            raise HTTPException(status_code=404, detail="Draft not found")
        draft = json.loads(draft_raw)

        if req.decision == "approve":
            draft["status"] = "approved"
            draft["approved_at"] = datetime.utcnow().isoformat()
            draft["requires_approval"] = False
            # Auto-publish or queue for immediate publish
            await r.hset("rmi:content:drafts", req.draft_id, json.dumps(draft))
            await r.lpush("rmi:content:approved", json.dumps(draft))
            # Trigger syndication
            for platform in draft.get("platforms", []):
                await r.lpush(f"rmi:syndicate:{platform}", json.dumps(draft))
            return {"draft": draft, "decision": "approved", "status": "queued_for_publish"}

        elif req.decision == "reject":
            draft["status"] = "rejected"
            draft["rejected_at"] = datetime.utcnow().isoformat()
            draft["requires_approval"] = False
            await r.hset("rmi:content:drafts", req.draft_id, json.dumps(draft))
            return {"draft": draft, "decision": "rejected"}

        elif req.decision == "schedule":
            draft["status"] = "scheduled"
            draft["scheduled_for"] = req.scheduled_for
            draft["requires_approval"] = False
            await r.hset("rmi:content:drafts", req.draft_id, json.dumps(draft))
            await r.lpush("rmi:content:scheduled", json.dumps(draft))
            return {"draft": draft, "decision": "scheduled", "publish_at": req.scheduled_for}

        else:
            raise HTTPException(status_code=400, detail="Decision must be approve, reject, or schedule")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
