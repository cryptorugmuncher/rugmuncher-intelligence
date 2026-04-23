"""
Content Syndication Engine
==========================
Central hub for publishing content to Website, X/Twitter, and Telegram.

Storage: Redis (simple list of posts)
Workflow:
  1. Content is created via POST /api/v1/content
  2. Syndication triggers based on target_platforms field
  3. Each platform handler formats and delivers the content

Env vars needed:
  BOT_TOKEN          — Telegram bot token
  TWITTER_BEARER     — X API v2 Bearer token (for reading)
  TWITTER_API_KEY    — X API v2 Consumer Key (for posting)
  TWITTER_API_SECRET — X API v2 Consumer Secret
  TWITTER_ACCESS_TOKEN       — X OAuth Access Token
  TWITTER_ACCESS_TOKEN_SECRET— X OAuth Access Token Secret
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Header

import httpx
import redis.asyncio as redis

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/content", tags=["content"])

# ── Redis ──
REDIS_HOST = os.getenv("REDIS_HOST", "rmi_dragonfly")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "") or None
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

_redis: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT,
            password=REDIS_PASSWORD, db=REDIS_DB,
            decode_responses=True
        )
    return _redis

CONTENT_KEY = "rmi:content:posts"
CONTENT_SEQ = "rmi:content:seq"

# ── Models ──

class ContentPost(BaseModel):
    id: str = Field(default_factory=lambda: f"post-{uuid.uuid4().hex[:8]}")
    title: str
    excerpt: str
    content: str
    author: str = "CryptoRugMunch"
    author_handle: str = "@CryptoRugMunch"
    category: str = "Investigation"
    tags: List[str] = Field(default_factory=list)
    color: str = "#D1A340"
    tweet_url: Optional[str] = None
    platforms: List[str] = Field(default_factory=list)  # ["site", "telegram", "x"]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    syndicated: dict = Field(default_factory=dict)  # {"telegram": true, "x": false}

class CreatePostRequest(BaseModel):
    title: str
    excerpt: str
    content: str
    author: str = "CryptoRugMunch"
    category: str = "Investigation"
    tags: List[str] = Field(default_factory=list)
    color: str = "#D1A340"
    platforms: List[str] = ["site"]  # default: site only
    tweet_url: Optional[str] = None

class SyndicateRequest(BaseModel):
    platforms: List[str]  # ["telegram", "x"]

# ── Helpers ──

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_NEWS = os.getenv("CHANNEL_NEWS", "")
CHANNEL_ALERTS = os.getenv("CHANNEL_ALERTS", "")
CHANNEL_PREMIUM = os.getenv("CHANNEL_PREMIUM", "")
CHANNEL_ALPHA = os.getenv("CHANNEL_ALPHA", "")

async def telegram_broadcast(text: str, parse_mode: str = "HTML") -> dict:
    """Broadcast to all configured Telegram channels."""
    if not BOT_TOKEN:
        return {"status": "skipped", "reason": "BOT_TOKEN not configured"}

    channels = {
        "news": CHANNEL_NEWS,
        "alerts": CHANNEL_ALERTS,
        "premium": CHANNEL_PREMIUM,
        "alpha": CHANNEL_ALPHA,
    }

    results = {}
    async with httpx.AsyncClient() as client:
        for name, chat_id in channels.items():
            if not chat_id:
                continue
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False,
            }
            try:
                resp = await client.post(url, json=payload, timeout=30)
                data = resp.json()
                results[name] = "ok" if data.get("ok") else data.get("description", "failed")
            except Exception as e:
                results[name] = str(e)
                logger.error(f"Telegram broadcast to {name} failed: {e}")

    return {"status": "ok", "platform": "telegram", "channels": results}


async def x_post_tweet(text: str, reply_to: Optional[str] = None) -> dict:
    """Post to X/Twitter using API v2. Requires OAuth 1.0a or Bearer + App auth."""
    # NOTE: X API v2 posting requires OAuth 1.0a user context or OAuth 2.0 write scopes.
    # This is a skeleton — fill in credentials to activate.
    api_key = os.getenv("TWITTER_API_KEY", "")
    api_secret = os.getenv("TWITTER_API_SECRET", "")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
    access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    if not all([api_key, api_secret, access_token, access_secret]):
        return {"status": "skipped", "reason": "X API credentials not configured (TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)"}

    # Using OAuth 1.0a would require `requests-oauthlib` or manual signing.
    # For now we return a clear message about what's needed.
    return {
        "status": "pending",
        "platform": "x",
        "reason": "X posting requires OAuth 1.0a signing. Install `requests-oauthlib` or implement HMAC-SHA1 signing. Credentials detected — ready to activate."
    }


async def syndicate_post(post: ContentPost, platforms: List[str]) -> dict:
    """Route content to requested platforms."""
    results = {}

    for platform in platforms:
        if platform == "telegram":
            # Format for Telegram
            tg_text = (
                f"<b>{post.title}</b>\n\n"
                f"{post.excerpt}\n\n"
                f"#{post.category.replace(' ', '')} "
                + " ".join(f"#{t.replace(' ', '')}" for t in post.tags)
            )
            if post.tweet_url:
                tg_text += f"\n\n<a href='{post.tweet_url}'>Read on X →</a>"
            results["telegram"] = await telegram_broadcast(tg_text)

        elif platform == "x":
            x_text = f"{post.title}\n\n{post.excerpt}"
            if len(x_text) > 280:
                x_text = post.excerpt[:250] + "…"
            results["x"] = await x_post_tweet(x_text)

        elif platform == "site":
            results["site"] = {"status": "ok", "message": "Post stored in Redis. Rebuild frontend to include."}

        else:
            results[platform] = {"status": "error", "reason": f"Unknown platform: {platform}"}

    # Update syndicated flags
    for p in platforms:
        if p in results and results[p].get("status") in ("ok", "pending"):
            post.syndicated[p] = True

    return {"status": "ok", "syndicated": results}


# ── API Endpoints ──

@router.post("", response_model=ContentPost)
async def create_post(
    req: CreatePostRequest,
    background_tasks: BackgroundTasks,
    r: redis.Redis = Depends(get_redis)
):
    """Create a new content post and optionally syndicate immediately."""
    post = ContentPost(
        title=req.title,
        excerpt=req.excerpt,
        content=req.content,
        author=req.author,
        category=req.category,
        tags=req.tags,
        color=req.color,
        platforms=req.platforms,
        tweet_url=req.tweet_url,
    )

    # Save to Redis
    await r.lpush(CONTENT_KEY, json.dumps(post.model_dump()))

    # Auto-syndicate if platforms requested
    if req.platforms:
        background_tasks.add_task(syndicate_post, post, req.platforms)

    return post


@router.get("")
async def list_posts(
    limit: int = 20,
    offset: int = 0,
    r: redis.Redis = Depends(get_redis)
):
    """List all content posts (newest first)."""
    raw = await r.lrange(CONTENT_KEY, offset, offset + limit - 1)
    posts = [json.loads(x) for x in raw]
    return {"status": "ok", "count": len(posts), "posts": posts}


@router.get("/{post_id}")
async def get_post(post_id: str, r: redis.Redis = Depends(get_redis)):
    """Get a single post by ID."""
    raw = await r.lrange(CONTENT_KEY, 0, -1)
    for x in raw:
        post = json.loads(x)
        if post.get("id") == post_id:
            return {"status": "ok", "post": post}
    raise HTTPException(status_code=404, detail="Post not found")


@router.post("/{post_id}/syndicate")
async def trigger_syndicate(
    post_id: str,
    req: SyndicateRequest,
    background_tasks: BackgroundTasks,
    r: redis.Redis = Depends(get_redis)
):
    """Manually trigger syndication for an existing post."""
    raw = await r.lrange(CONTENT_KEY, 0, -1)
    found = None
    for x in raw:
        data = json.loads(x)
        if data.get("id") == post_id:
            found = ContentPost(**data)
            break

    if not found:
        raise HTTPException(status_code=404, detail="Post not found")

    background_tasks.add_task(syndicate_post, found, req.platforms)
    return {"status": "ok", "message": f"Syndication triggered for {post_id}", "platforms": req.platforms}


@router.delete("/{post_id}")
async def delete_post(post_id: str, r: redis.Redis = Depends(get_redis)):
    """Delete a post by ID."""
    raw = await r.lrange(CONTENT_KEY, 0, -1)
    removed = 0
    for x in raw:
        data = json.loads(x)
        if data.get("id") == post_id:
            await r.lrem(CONTENT_KEY, 0, x)
            removed += 1
    return {"status": "ok", "removed": removed}

# ── Ghost Webhook Receiver ──

class GhostWebhookPayload(BaseModel):
    post: Optional[dict] = None

@router.post("/webhook/ghost")
async def ghost_webhook(
    payload: dict,
    background_tasks: BackgroundTasks
):
    """Receive Ghost webhooks and syndicate to Telegram."""
    post = payload.get("post", {})
    if not post:
        return {"status": "ignored", "reason": "No post data"}

    # Only syndify on publish
    if post.get("status") != "published":
        return {"status": "ignored", "reason": "Not published"}

    # Check tags for syndication targets
    tags = [t.get("name", "").lower() for t in post.get("tags", [])]
    platforms = []
    if "telegram" in tags or "sync" in tags:
        platforms.append("telegram")

    if not platforms:
        return {"status": "ignored", "reason": "No syndication tags"}

    # Build content post
    content = ContentPost(
        title=post.get("title", "Untitled"),
        excerpt=post.get("excerpt", ""),
        content=post.get("html", ""),
        author=post.get("primary_author", {}).get("name", "CryptoRugMunch"),
        category=post.get("primary_tag", {}).get("name", "Investigation"),
        tags=[t.get("name") for t in post.get("tags", []) if not t.get("name", "").startswith("#")],
        tweet_url=post.get("canonical_url") or post.get("url"),
        platforms=platforms,
    )

    background_tasks.add_task(syndicate_post, content, platforms)
    return {"status": "ok", "syndicating": platforms}

# ═══════════════════════════════════════════════════════════════════════════
# X404 Content Pipeline — Backend-generated drafts → Ghost CMS
# ═══════════════════════════════════════════════════════════════════════════

import httpx

GHOST_ADMIN_KEY = os.getenv("GHOST_ADMIN_KEY", "")
GHOST_URL = os.getenv("GHOST_URL", "http://rmi-ghost:2368")

class X404DraftRequest(BaseModel):
    title: str
    content: str
    excerpt: str = ""
    tags: List[str] = Field(default_factory=list)
    author: str = "RMI Bot"
    featured_image: Optional[str] = None

async def create_ghost_draft(draft: X404DraftRequest) -> dict:
    """Push a draft post to Ghost CMS for editorial review."""
    if not GHOST_ADMIN_KEY:
        return {"status": "skipped", "reason": "GHOST_ADMIN_KEY not configured"}

    # Ghost Admin API v5 uses JWT or Admin Key
    # Admin key format: {id}:{secret}
    url = f"{GHOST_URL}/ghost/api/admin/posts/"
    headers = {
        "Authorization": f"Ghost {GHOST_ADMIN_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "posts": [{
            "title": draft.title,
            "html": draft.content,
            "custom_excerpt": draft.excerpt or draft.content[:200],
            "status": "draft",
            "tags": [{"name": t} for t in draft.tags],
            "authors": [{"name": draft.author}],
            "featured": False,
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=30)
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("posts"):
                post = data["posts"][0]
                return {
                    "status": "ok",
                    "ghost_post_id": post["id"],
                    "edit_url": f"{GHOST_URL}/ghost/#/editor/post/{post['id']}",
                    "title": post["title"],
                }
            return {"status": "error", "code": resp.status_code, "detail": data}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

@router.post("/x404-draft")
async def receive_x404_draft(
    req: X404DraftRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(default="", alias="X-API-Key")
):
    """Receive x404-generated content and push to Ghost as a draft.

    Auth: Pass X-API-Key header matching ADMIN_API_KEY env var.
    """
    # Simple auth check
    expected = os.getenv("ADMIN_API_KEY", "dev-key-change-me")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")

    result = await create_ghost_draft(req)
    return result
