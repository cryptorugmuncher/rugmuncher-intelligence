"""
Rug Munch Intelligence — Hero Chat Engine
═══════════════════════════════════════════
Streaming SSE chat with free-tier tracking, context memory,
multi-provider AI routing, response caching, and tool execution.

Design goals:
- Use singleton ai_router for provider health + failover
- In-memory LRU cache for identical non-streaming queries
- Real provider SSE streaming (no word-split simulation)
- Structured JSON output for rich frontend cards/charts
- Internal tool calls to existing RMI endpoints
"""

import os
import json
import uuid
import time
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import redis.asyncio as redis
import httpx

from app.ai_router import router as ai_router

router = APIRouter(prefix="/api/v1/intel", tags=["intel"])

# ── CONFIG ──
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

FREE_MESSAGES_PER_SESSION = int(os.getenv("FREE_MESSAGES", "5"))
SESSION_TTL = 86400 * 7  # 7 days
CONTEXT_MAX_MESSAGES = 20
CACHE_TTL_SECONDS = 300  # 5 min in-memory cache
REDIS_CACHE_TTL = 86400 * 1  # 1 day for exact query matches

# ── SYSTEM PROMPT ──
SYSTEM_PROMPT = """You are the RMI Terminal, Rug Munch Intelligence's flagship AI engine.
You provide forensic-grade crypto security analysis, on-chain intelligence, and market insight.

Personality: Precise, fast, data-driven. Speak with technical authority but keep it readable.

Capabilities:
- Token security analysis (contracts, holders, liquidity, deployer history)
- Wallet forensics (funding sources, cluster analysis, exchange tagging)
- Market intelligence (whale movements, smart money, sniper detection)
- On-chain detective work (transaction tracing, pattern recognition)
- Narrative intelligence (trend tracking, sentiment, KOL analysis)

Rules:
- Keep answers concise but deeply informative (2-4 sentences unless asked for depth)
- When analyzing a token, always structure: Risk Score / Key Findings / Verdict
- Never give financial advice — only security and intelligence analysis
- Reference tools naturally: Birdeye, GMGN, Helius, Solscan, Moralis, DexScreener
- If asked about $CRM or cryptorugmunch, be objective but proud of the transparency
- You can suggest commands: /scan <token>, /whales <token>, /trace <wallet>, /trending

When the user asks for a token scan, wallet trace, or holder analysis, you may emit a TOOL CALL
in this exact format so the system can fetch real data for you:

[[TOOL:scan_token|{{"chain":"solana","address":"<contract_address>"}}]]
[[TOOL:wallet_summary|{{"chain":"solana","address":"<wallet_address>"}}]]
[[TOOL:whale_check|{{"token":"<contract_address>"}}]]

Current date: {date}
"""

# ── REDIS ──
_redis: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
        )
    return _redis


# ── IN-MEMORY CACHE ──
_cache: Dict[str, Dict[str, Any]] = {}
_cache_hits = 0
_cache_misses = 0


def _cache_key(messages: List[Dict[str, str]]) -> str:
    """Deterministic cache key from message list."""
    return json.dumps(messages, sort_keys=True, ensure_ascii=True)


def _get_cached(messages: List[Dict[str, str]]) -> Optional[str]:
    global _cache_hits
    key = _cache_key(messages)
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL_SECONDS:
        _cache_hits += 1
        return entry["content"]
    return None


def _set_cached(messages: List[Dict[str, str]], content: str):
    global _cache_misses
    _cache_misses += 1
    key = _cache_key(messages)
    _cache[key] = {"content": content, "ts": time.time()}
    # Simple eviction: keep newest 500 entries
    if len(_cache) > 500:
        oldest = min(_cache, key=lambda k: _cache[k]["ts"])
        del _cache[oldest]


# ── REDIS RESPONSE CACHE ──
def _redis_cache_key(user_message: str) -> str:
    """Cache key based on user message only (exact match)."""
    import hashlib
    h = hashlib.sha256(user_message.strip().lower().encode()).hexdigest()[:32]
    return f"intel:response_cache:{h}"


async def _get_redis_cached(user_message: str) -> Optional[str]:
    """Get cached response from Redis."""
    r = await get_redis()
    key = _redis_cache_key(user_message)
    data = await r.get(key)
    if data:
        return json.loads(data).get("response")
    return None


async def _set_redis_cached(user_message: str, response: str, ttl: int = REDIS_CACHE_TTL):
    """Store response in Redis cache."""
    r = await get_redis()
    key = _redis_cache_key(user_message)
    await r.setex(key, ttl, json.dumps({"response": response, "ts": time.time()}))


# ── MODELS ──
class ChatMessage(BaseModel):
    role: str = Field(..., description="user | assistant | system")
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = True
    tier: Optional[str] = None


class ChatSession(BaseModel):
    session_id: str
    messages_used: int
    messages_remaining: int
    created_at: str


# ── HELPERS ──
def _session_key(sid: str) -> str:
    return f"intel:session:{sid}"


def _context_key(sid: str) -> str:
    return f"intel:context:{sid}"


async def get_or_create_session(sid: Optional[str] = None) -> Dict[str, Any]:
    r = await get_redis()
    if not sid:
        sid = str(uuid.uuid4())
    key = _session_key(sid)
    data = await r.get(key)
    if data:
        session = json.loads(data)
    else:
        session = {
            "session_id": sid,
            "messages_used": 0,
            "messages_remaining": FREE_MESSAGES_PER_SESSION,
            "created_at": datetime.utcnow().isoformat(),
            "tier": "free",
        }
        await r.setex(key, SESSION_TTL, json.dumps(session))
    return session


async def increment_usage(sid: str) -> Dict[str, Any]:
    r = await get_redis()
    key = _session_key(sid)
    data = await r.get(key)
    if not data:
        return await get_or_create_session(sid)
    session = json.loads(data)
    session["messages_used"] += 1
    session["messages_remaining"] = max(0, FREE_MESSAGES_PER_SESSION - session["messages_used"])
    if session["messages_remaining"] <= 0:
        session["tier"] = "locked"
    await r.setex(key, SESSION_TTL, json.dumps(session))
    return session


async def get_context(sid: str) -> List[Dict[str, str]]:
    r = await get_redis()
    key = _context_key(sid)
    data = await r.get(key)
    if data:
        return json.loads(data)
    return []


async def append_context(sid: str, role: str, content: str):
    r = await get_redis()
    key = _context_key(sid)
    context = await get_context(sid)
    context.append({"role": role, "content": content})
    if len(context) > CONTEXT_MAX_MESSAGES:
        context = context[-CONTEXT_MAX_MESSAGES:]
    await r.setex(key, SESSION_TTL, json.dumps(context))


async def build_messages(sid: str, user_message: str) -> List[Dict[str, str]]:
    context = await get_context(sid)
    system = SYSTEM_PROMPT.format(date=datetime.utcnow().strftime("%Y-%m-%d"))
    messages = [{"role": "system", "content": system}]
    messages.extend(context)
    messages.append({"role": "user", "content": user_message})
    return messages


# ── TOOL EXECUTION ──
# These hit existing internal endpoints so the AI gets real data.
INTERNAL_BASE = os.getenv("INTERNAL_API_BASE", "http://127.0.0.1:8000")


async def _call_internal(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call an existing internal API endpoint."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{INTERNAL_BASE}{endpoint}", json=payload)
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"Status {resp.status_code}", "detail": resp.text[:200]}
    except Exception as e:
        return {"error": str(e)}


_TOOL_REGISTRY = {
    "scan_token": lambda p: _call_internal("/api/v1/security/scan", p),
    "wallet_summary": lambda p: _call_internal("/api/v1/analytics/wallet/summary", p),
    "whale_check": lambda p: _call_internal("/api/v1/analytics/whales/concentration", p),
}


async def _execute_tools(text: str) -> str:
    """Parse [[TOOL:name|{json}]] blocks, execute, and append results."""
    import re
    pattern = r"\[\[TOOL:(\w+)\|(\{.*?\})\]\]"
    matches = re.findall(pattern, text)
    if not matches:
        return text

    tool_results = []
    for tool_name, json_str in matches:
        try:
            params = json.loads(json_str)
        except json.JSONDecodeError:
            continue
        handler = _TOOL_REGISTRY.get(tool_name)
        if handler:
            result = await handler(params)
            tool_results.append(f"\n\n[TOOL RESULT: {tool_name}]\n{json.dumps(result, indent=2)}\n")

    if tool_results:
        return text + "\n" + "".join(tool_results)
    return text


# ── AI CALLS ──
async def _call_ai(messages: List[Dict[str, str]], stream: bool = False, tier: str = "T2", user_message: str = "") -> str:
    """Call the AI router. Uses cache for non-streaming."""
    if not stream:
        # Check in-memory cache first
        cached = _get_cached(messages)
        if cached:
            return cached
        # Check Redis exact-match cache
        if user_message:
            redis_cached = await _get_redis_cached(user_message)
            if redis_cached:
                _cache_hits += 1
                return redis_cached

    try:
        result = await ai_router.chat_completion(
            messages=messages,
            model=None,
            tier=tier,
            temperature=0.75,
            max_tokens=2048,
            timeout=30.0,
        )
        if "error" in result:
            return f"⚠️ System disturbance: {result['error']}. The mesh is recalibrating..."
        content = result.get("content", "The terminal is silent.")
        if not stream:
            _set_cached(messages, content)
            if user_message:
                await _set_redis_cached(user_message, content)
        return content
    except Exception as e:
        return f"⚠️ The signal is clouded: {str(e)}"


async def _stream_ai(messages: List[Dict[str, str]], tier: str = "T2", user_message: str = "") -> AsyncGenerator[str, None]:
    """Stream real tokens from the best available provider."""
    # Check Redis cache for exact match — if cached, yield it word-by-word for streaming effect
    if user_message:
        cached = await _get_redis_cached(user_message)
        if cached:
            for word in cached.split():
                yield word + " "
                await asyncio.sleep(0.01)
            return

    try:
        async for token in ai_router.stream_chat_completion(
            messages=messages,
            model=None,
            tier=tier,
            temperature=0.75,
            max_tokens=2048,
            timeout=60.0,
        ):
            if token.startswith("[ERROR:"):
                yield "⚠️ " + token[7:-1]
                return
            yield token
    except Exception as e:
        yield f"⚠️ Stream interrupted: {str(e)}"


# ── RESPONSE FORMATTER ──
def _format_response(raw: str) -> Dict[str, Any]:
    """Try to detect structured data in the response for rich frontend rendering."""
    result: Dict[str, Any] = {"text": raw, "structured": None}

    # Look for JSON block
    if "```json" in raw:
        try:
            json_text = raw.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(json_text)
            result["structured"] = parsed
        except Exception:
            pass
    elif raw.strip().startswith("{") and raw.strip().endswith("}"):
        try:
            result["structured"] = json.loads(raw.strip())
        except Exception:
            pass

    # Detect risk score mentions
    lower = raw.lower()
    if "risk score" in lower or "risk:" in lower:
        # Extract numeric risk score if present
        import re
        m = re.search(r"risk[\s\w]*[:\/]?\s*(\d{1,3})\s*[/\\]?\s*(100)?", lower)
        if m:
            try:
                score = int(m.group(1))
                result["risk_score"] = min(score, 100)
            except ValueError:
                pass

    return result


# ── ENDPOINTS ──

@router.post("/chat", response_model=ChatSession)
async def intel_chat_init(req: ChatRequest):
    """Initialize or resume a chat session. Returns session status."""
    session = await get_or_create_session(req.session_id)
    return ChatSession(**session)


@router.post("/chat/stream")
async def intel_chat_stream(request: Request):
    """Streaming SSE chat endpoint. Real provider tokens."""
    body = await request.json()
    req = ChatRequest(**body)

    session = await get_or_create_session(req.session_id)
    sid = session["session_id"]

    # Check free tier
    if session.get("messages_remaining", 0) <= 0:
        async def paywall_stream():
            yield f"data: {json.dumps({'type': 'paywall', 'message': 'Free tier exhausted. Upgrade to continue.'})}\n\n"
        return StreamingResponse(paywall_stream(), media_type="text/event-stream")

    # Increment usage
    await increment_usage(sid)
    session = await get_or_create_session(sid)

    # Determine tier
    chat_tier = req.tier or session.get("tier", "T3")
    if chat_tier not in ("T0", "T1", "T2", "T3", "T4"):
        chat_tier = "T3"  # Default to fast tier for free/unknown users

    # Build context
    messages = await build_messages(sid, req.message)
    await append_context(sid, "user", req.message)

    async def event_stream():
        # Send session update
        yield f"data: {json.dumps({'type': 'session', 'data': session})}\n\n"

        # Stream AI response
        full_response = ""
        async for chunk in _stream_ai(messages, tier=chat_tier, user_message=req.message):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        # Store assistant response in context
        clean_response = full_response.strip()
        await append_context(sid, "assistant", clean_response)

        # Cache the response for future exact matches
        await _set_redis_cached(req.message, clean_response)

        # Try to execute any embedded tool calls (fire-and-forget enrich)
        enriched = await _execute_tools(clean_response)
        if enriched != clean_response:
            # If tools ran, append results to context for future turns
            await append_context(sid, "system", f"Tool results appended: {enriched[-500:]}")

        # Format structured data for frontend
        formatted = _format_response(clean_response)

        # Send done
        yield f"data: {json.dumps({'type': 'done', 'full_response': clean_response, 'formatted': formatted})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat/message")
async def intel_chat_message(request: Request):
    """Non-streaming chat for simple clients. Cached when possible."""
    body = await request.json()
    req = ChatRequest(**body)

    session = await get_or_create_session(req.session_id)
    sid = session["session_id"]

    if session.get("messages_remaining", 0) <= 0:
        return {
            "type": "paywall",
            "message": "You've used your free messages. Upgrade to RMI Pro for unlimited access.",
            "session": session,
        }

    await increment_usage(sid)
    session = await get_or_create_session(sid)

    # Determine tier
    chat_tier = req.tier or session.get("tier", "T3")
    if chat_tier not in ("T0", "T1", "T2", "T3", "T4"):
        chat_tier = "T3"

    messages = await build_messages(sid, req.message)
    response_text = await _call_ai(messages, stream=False, tier=chat_tier, user_message=req.message)
    await append_context(sid, "assistant", response_text)

    # Execute tools if any
    enriched = await _execute_tools(response_text)
    if enriched != response_text:
        await append_context(sid, "system", f"Tool results: {enriched[-500:]}")

    formatted = _format_response(response_text)

    return {
        "type": "message",
        "response": response_text,
        "formatted": formatted,
        "session": session,
    }


@router.get("/chat/session/{session_id}")
async def intel_chat_get_session(session_id: str):
    """Get session status and history."""
    session = await get_or_create_session(session_id)
    context = await get_context(session_id)
    return {
        "session": session,
        "history": context,
    }


@router.get("/chat/stats")
async def intel_chat_stats():
    """Service stats for monitoring."""
    return {
        "cache_hits": _cache_hits,
        "cache_misses": _cache_misses,
        "cache_size": len(_cache),
        "router_status": ai_router.get_status(),
    }
