#!/usr/bin/env python3
"""
RMI Backend API — Main FastAPI Application
==========================================
8-Agent AI Mesh | Crypto Intelligence | Forensic Engine
"""

import os
import logging
import sys
import json
import re
import asyncio
import httpx
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── Add project root ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── CONFIGURATION ──
class Settings:
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Redis (Dragonfly)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # AI Providers
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_DEV_API_KEY: str = os.getenv("NVIDIA_DEV_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    KIMI_API_KEY: str = os.getenv("KIMI_API_KEY", "")
    TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "")

    # Crypto APIs
    HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY", "")
    HELIUS_API_KEY_2: str = os.getenv("HELIUS_API_KEY_2", "")
    BIRDEYE_API_KEY: str = os.getenv("BIRDEYE_API_KEY", "")
    ARKHAM_API_KEY: str = os.getenv("ARKHAM_API_KEY", "")
    MORALIS_API_KEY: str = os.getenv("MORALIS_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    SOLSCAN_API_KEY: str = os.getenv("SOLSCAN_API_KEY", "")
    ETHERSCAN_KEY: str = os.getenv("ETHERSCAN_KEY", "")
    BSCSCAN_KEY: str = os.getenv("BSCSCAN_KEY", "")
    ALCHEMY_KEY: str = os.getenv("ALCHEMY_KEY", "")
    QUICKNODE_KEY: str = os.getenv("QUICKNODE_KEY", "")

    # Security
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "dev-key-change-me")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "rmi-jwt-secret-change-me")

    # n8n
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "")

    # Vault
    VAULT_ADDR: str = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    VAULT_ENABLED: bool = os.getenv("VAULT_ENABLED", "false").lower() == "true"

settings = Settings()

# ── REDIS CLIENT ──
redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    return redis_client

# ── LIFESPAN ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    r = await get_redis()
    await r.set("rmi:status", "online", ex=60)
    await r.set("rmi:started", datetime.utcnow().isoformat())
    print("[RMI] Backend online — 8-Agent Mesh ready")
    yield
    # Shutdown
    if redis_client:
        await redis_client.close()
    print("[RMI] Backend shutting down")

# ── FASTAPI APP ──
app = FastAPI(
    title="Rug Munch Intelligence API",
    description="AI-Native Crypto Intelligence Ecosystem",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REQUEST MODELS ──
class WalletScanRequest(BaseModel):
    address: str = Field(..., min_length=32, max_length=64)
    chain: str = Field(default="solana")
    depth: str = Field(default="standard")  # quick, standard, deep

class ContractAuditRequest(BaseModel):
    address: str = Field(..., min_length=32, max_length=64)
    chain: str = Field(default="solana")
    source_code: Optional[str] = None

class TokenScanRequest(BaseModel):
    address: str = Field(..., min_length=32, max_length=64)
    chain: str = Field(default="solana")

class InvestigationRequest(BaseModel):
    target: str
    type: str = Field(default="wallet")  # wallet, contract, token, syndicate
    evidence: Optional[List[str]] = None

class AlertRequest(BaseModel):
    token_address: str
    alert_types: List[str] = Field(default=["liquidity_remove", "mint", "blacklist"])
    webhook_url: Optional[str] = None

class AgentCommandRequest(BaseModel):
    agent: str = Field(..., description="Agent name: nexus, scout, tracer, cipher, sentinel, chronicler, forge, relay")
    command: str
    context: Optional[Dict] = None
    priority: str = Field(default="normal")  # low, normal, high, critical

class ConsensusRequest(BaseModel):
    topic: str
    evidence: Dict[str, Any]
    min_agents: int = Field(default=3, ge=2, le=8)
    threshold: float = Field(default=0.85, ge=0.5, le=1.0)

class WalletAuthRequest(BaseModel):
    message: str
    signature: str
    wallet_address: str = Field(..., pattern="^0x[a-fA-F0-9]{40}$")

class NonceResponse(BaseModel):
    nonce: str
    timestamp: str

class WalletAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: Dict[str, Any]

# ── API KEY AUTH ──
async def verify_admin_key(request: Request):
    key = request.headers.get("X-Admin-Key", "")
    if key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True

# ── JWT USER AUTH ──
async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Verify JWT from Authorization header (wallet or Supabase)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    return await verify_auth_token(token)

async def require_auth(request: Request) -> Dict[str, Any]:
    """Require valid JWT. Raises 401 if missing/invalid."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# ── WEB3 AUTH IMPORTS ──
from app.auth_wallet import (
    generate_nonce,
    build_sign_message,
    verify_wallet_signature,
    get_or_create_wallet_user,
    verify_auth_token,
)

# ── SUPABASE DB CLIENT ──
from app.db_client import (
    get_db,
    RmiDatabase,
    User,
    InvestigationCase,
    TrenchesPost,
    Alert,
    cache_set,
    cache_get,
    cache_hash_set,
    cache_hash_get_all,
)

# ── CRM CASE LOADER ──
from app.crm_case_loader import (
    get_case_summary,
    get_full_case_data,
    get_timeline,
    get_criminal_structure,
    get_wallets_from_db,
    get_wallet_details,
    get_transactions,
    get_relationship_graph,
    get_evidence_categories,
    get_stats,
    is_published,
    set_published,
    CASE_ID,
)

# ── AI ROUTER IMPORTS ──
from app.ai_router import router as ai_router, MODEL_TIERS, PROVIDERS

# Chain config for GMGN quote routing
CHAIN_CONFIG = {
    "sol": {
        "usdc": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "native": "So11111111111111111111111111111111111111112",
    },
    "bsc": {
        "usdc": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
        "native": "0x0000000000000000000000000000000000000000",
    },
    "base": {
        "usdc": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "native": "0x0000000000000000000000000000000000000000",
    },
}


@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
@app.get("/api/v1/status")
async def status():
    r = await get_redis()
    agents_raw = await r.hgetall("rmi:agents") or {}
    agents = {k: json.loads(v) for k, v in agents_raw.items()}
    return {
        "system": "operational",
        "agents_total": len(agents),
        "agents_online": sum(1 for a in agents.values() if a.get("status") == "online"),
        "agents": agents,
        "version": "2.0.0"
    }

@app.get("/api/v1/stats")
async def stats():
    """Public system stats for dashboards."""
    r = await get_redis()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    api_calls = int(await r.get(f"rmi:metrics:api_calls:{today}") or 0)
    cache_hits = int(await r.get("rmi:metrics:cache_hits") or 0)
    cache_misses = int(await r.get("rmi:metrics:cache_misses") or 1)
    hit_rate = cache_hits / (cache_hits + cache_misses)
    cases_raw = await r.hgetall("rmi:cases") or {}
    wallets_raw = await r.hgetall("rmi:wallets") or {}
    return {
        "total_investigations": len(cases_raw),
        "total_wallets": len(wallets_raw),
        "api_calls_today": api_calls,
        "cache_hit_rate": round(hit_rate, 3),
        "dragonfly_status": "connected",
        "supabase_status": "connected",
    }

# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

@app.get("/auth/nonce", response_model=NonceResponse)
async def auth_nonce():
    """Get a nonce for wallet signature."""
    return {
        "nonce": generate_nonce(),
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.post("/auth/wallet", response_model=WalletAuthResponse)
async def auth_wallet(req: WalletAuthRequest):
    """Authenticate via wallet signature."""
    # Verify signature
    if not verify_wallet_signature(req.message, req.signature, req.wallet_address):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Get or create user (persisted to Supabase via db_client inside auth_wallet)
    user_data = await get_or_create_wallet_user(req.wallet_address)

    # Cache user in Redis for fast lookups
    r = await get_redis()
    await r.hset("rmi:users", user_data["id"], json.dumps(user_data))
    await cache_set(f"user:{user_data['id']}", user_data, ttl=600)
    
    return {
        "access_token": user_data["access_token"],
        "refresh_token": user_data["refresh_token"],
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "wallet_address": user_data["wallet_address"],
            "role": user_data["role"],
            "tier": user_data["tier"],
            "created_at": user_data["created_at"],
        },
    }

# ═══════════════════════════════════════════════════════════════
# AGENT MESH
# ═══════════════════════════════════════════════════════════════
AGENTS = {
    "nexus": {"name": "NEXUS", "role": "Strategic Coordinator", "tier": "T0", "models": ["gemini-2.5-pro", "nvidia/nemotron-4-340b"], "triggers": ["strategize", "plan", "coordinate", "synthesize"]},
    "scout": {"name": "SCOUT", "role": "Alpha Hunter", "tier": "T3", "models": ["groq/llama-3.1-8b-instant", "gemini-2.5-flash"], "triggers": ["find", "scan", "hunt", "alpha"]},
    "tracer": {"name": "TRACER", "role": "Forensic Investigator", "tier": "T1", "models": ["gemini-2.5-pro", "deepseek/deepseek-r1"], "triggers": ["trace", "investigate", "follow", "wallet"]},
    "cipher": {"name": "CIPHER", "role": "Contract Auditor", "tier": "T1", "models": ["qwen/qwen2.5-coder-32b-instruct", "deepseek/deepseek-coder-v2"], "triggers": ["audit", "security", "contract", "code"]},
    "sentinel": {"name": "SENTINEL", "role": "Rug Detector", "tier": "T2", "models": ["deepseek/deepseek-r1", "groq/llama-3.3-70b-versatile"], "triggers": ["monitor", "watch", "alert", "rug"]},
    "chronicler": {"name": "CHRONICLER", "role": "Investigative Reporter", "tier": "T2", "models": ["deepseek/deepseek-r1", "gemini-2.5-flash"], "triggers": ["write", "document", "report", "evidence"]},
    "forge": {"name": "FORGE", "role": "Implementation Architect", "tier": "T1", "models": ["qwen/qwen2.5-coder-32b-instruct", "deepseek/deepseek-coder-v2"], "triggers": ["code", "implement", "build", "script"]},
    "relay": {"name": "RELAY", "role": "Communications Coordinator", "tier": "T3", "models": ["groq/llama-3.1-8b-instant", "gemini-2.5-flash"], "triggers": ["format", "relay", "dispatch", "notify"]},
}

@app.get("/api/v1/agents")
async def list_agents():
    return {"agents": AGENTS, "total": len(AGENTS)}

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    r = await get_redis()
    status_raw = await r.hget("rmi:agents", agent_id)
    status = json.loads(status_raw) if status_raw else {"status": "online", "last_ping": datetime.utcnow().isoformat()}
    return {**AGENTS[agent_id], **status}

@app.post("/api/v1/agents/{agent_id}/command")
async def agent_command(agent_id: str, req: AgentCommandRequest):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    agent = AGENTS[agent_id]
    r = await get_redis()

    # Queue the command
    task_id = f"task:{datetime.utcnow().timestamp():.0f}:{agent_id}"
    task_data = {
        "id": task_id,
        "agent": agent_id,
        "command": req.command,
        "context": req.context or {},
        "priority": req.priority,
        "status": "queued",
        "created": datetime.utcnow().isoformat()
    }
    await r.hset("rmi:tasks", task_id, json.dumps(task_data))
    await r.lpush("rmi:queue:" + req.priority, task_id)

    return {"task_id": task_id, "agent": agent["name"], "status": "queued", "command": req.command}

# ═══════════════════════════════════════════════════════════════
# CRYPTO ENDPOINTS
# ═══════════════════════════════════════════════════════════════
@app.post("/api/v1/wallet/scan")
async def scan_wallet(req: WalletScanRequest, request: Request):
    """Scan a wallet address across chains"""
    results = {"address": req.address, "chain": req.chain, "timestamp": datetime.utcnow().isoformat()}
    
    # Award XP if authenticated
    user = await get_current_user(request)
    if user:
        try:
            from app.gamification_service import record_activity
            await record_activity(user["id"], "wallet_scan")
        except Exception as e:
            print(f"[GAMI] Failed to record scan XP: {e}")

    # Helius for Solana
    if req.chain == "solana" and settings.HELIUS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"https://api.helius.xyz/v0/addresses/?api-key={settings.HELIUS_API_KEY}&address={req.address}"
                )
                if resp.status_code == 200:
                    results["helius"] = resp.json()
        except Exception as e:
            results["helius_error"] = str(e)

    # Arkham for entity labeling
    if settings.ARKHAM_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.arkhamintelligence.com/intelligence/address",
                    headers={"API-Key": settings.ARKHAM_API_KEY},
                    json={"address": req.address, "chain": req.chain}
                )
                if resp.status_code == 200:
                    results["arkham"] = resp.json()
        except Exception as e:
            results["arkham_error"] = str(e)

    return results

@app.post("/api/v1/contract/audit")
async def audit_contract(req: ContractAuditRequest):
    """Audit a smart contract — combines on-chain data, Birdeye security scan, and AI analysis."""
    results = {"address": req.address, "chain": req.chain, "timestamp": datetime.utcnow().isoformat()}

    # Check cache
    cache_key = f"audit:{req.chain}:{req.address}"
    r = await get_redis()
    try:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Redis cache read error: {e}")

    findings: List[str] = []
    on_chain_data: Dict[str, Any] = {}
    risk_score = 0.0
    risk_level = "UNKNOWN"

    # ── Solana on-chain data via FreeSolscanClient ──
    if req.chain == "solana":
        try:
            from app.free_solscan_client import FreeSolscanClient
            token_data = await asyncio.to_thread(FreeSolscanClient.token_data, req.address)
            if token_data:
                on_chain_data["token_data"] = token_data
                findings.append(f"Token: {token_data.get('name', 'Unknown')} ({token_data.get('symbol', '???')})")
            creation_tx = await asyncio.to_thread(FreeSolscanClient.get_token_creation_tx, req.address)
            if creation_tx:
                on_chain_data["creation_tx"] = creation_tx
                signers = creation_tx.get("signer", [])
                if signers:
                    on_chain_data["deployer"] = signers[0]
                    findings.append(f"Deployer: {signers[0]}")
            account_info = await asyncio.to_thread(FreeSolscanClient.account_info, req.address)
            if account_info:
                on_chain_data["account_info"] = account_info
            holders_total = await asyncio.to_thread(FreeSolscanClient.token_holders_total, req.address)
            if holders_total:
                on_chain_data["holders_total"] = holders_total
                findings.append(f"Total holders: {holders_total}")
        except Exception as e:
            results["solscan_error"] = str(e)

    # ── Birdeye security scan (token contracts, all chains) ──
    try:
        from app.birdeye_client import BirdeyeClient
        client = BirdeyeClient()
        try:
            birdeye_result = await client.security_scan(req.address)
            if isinstance(birdeye_result, dict) and "error" not in birdeye_result:
                on_chain_data["birdeye"] = birdeye_result
                risk_score = float(birdeye_result.get("risk_score", 0))
                risk_level = birdeye_result.get("risk_level", "UNKNOWN")
                findings.extend(birdeye_result.get("flags", []))
            else:
                on_chain_data["birdeye_error"] = birdeye_result.get("error", "Unknown error")
        finally:
            await client.close()
    except Exception as e:
        results["birdeye_error"] = str(e)

    # ── AI code audit via CIPHER-style analysis ──
    ai_analysis: Dict[str, Any] = {}
    try:
        audit_prompt = (
            "You are a smart contract security auditor. Analyze this contract for: mint authority, freeze authority, "
            "upgradeability, hidden functions, honeypot patterns, liquidity locking.\n\n"
            f"Chain: {req.chain}\n"
            f"Address: {req.address}\n"
            f"On-chain data: {json.dumps(on_chain_data, default=str)}\n"
        )
        if req.source_code:
            audit_prompt += f"\nSource code:\n{req.source_code}\n"
        audit_prompt += "\nReturn JSON with risk_score (0-100), findings[], and recommendations[]."
        ai_result = await _get_ai_analysis(audit_prompt, tier="T2")
        if "error" not in ai_result:
            ai_analysis = ai_result
            if "risk_score" in ai_result:
                ai_risk = float(ai_result["risk_score"])
                risk_score = round((risk_score * 0.4) + (ai_risk * 0.6), 1)
        else:
            ai_analysis = {"error": ai_result.get("error"), "raw": ai_result.get("raw")}
    except Exception as e:
        ai_analysis = {"error": str(e)}

    # ── Final risk level ──
    if risk_score >= 60:
        risk_level = "HIGH RISK"
    elif risk_score >= 35:
        risk_level = "MEDIUM RISK"
    elif risk_score >= 15:
        risk_level = "LOW-MEDIUM RISK"
    else:
        risk_level = "LOW RISK"

    results.update({
        "risk_score": risk_score,
        "risk_level": risk_level,
        "findings": findings,
        "ai_analysis": ai_analysis,
        "on_chain_data": on_chain_data,
        "status": "completed",
    })

    # Cache for 1 hour
    try:
        await r.set(cache_key, json.dumps(results, default=str), ex=3600)
    except Exception as e:
        logger.warning(f"Redis cache write error: {e}")

    return results

@app.post("/api/v1/token/scan")
async def scan_token(req: TokenScanRequest):
    """Full token scan — liquidity, holders, risk"""
    results = {"address": req.address, "chain": req.chain, "timestamp": datetime.utcnow().isoformat()}

    # DexScreener for pair data (free API)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"https://api.dexscreener.com/latest/dex/search?q={req.address}")
            if resp.status_code == 200:
                results["dexscreener"] = resp.json()
    except Exception as e:
        results["dexscreener_error"] = str(e)

    # Birdeye for Solana token data
    if req.chain == "solana" and settings.BIRDEYE_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"https://public-api.birdeye.so/defi/token_overview?address={req.address}",
                    headers={"X-API-KEY": settings.BIRDEYE_API_KEY}
                )
                if resp.status_code == 200:
                    results["birdeye"] = resp.json()
        except Exception as e:
            results["birdeye_error"] = str(e)

    return results

# ═══════════════════════════════════════════════════════════════
# INVESTIGATION
# ═══════════════════════════════════════════════════════════════
@app.post("/api/v1/investigation/start")
async def start_investigation(req: InvestigationRequest, user: Dict[str, Any] = Depends(require_auth)):
    """Start a new investigation case (write-through: Supabase -> Redis cache)"""
    case_id = "CASE-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    case_data = {
        "id": case_id,
        "target": req.target,
        "type": req.type,
        "evidence": req.evidence or [],
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "agents_assigned": ["nexus", "tracer", "cipher"],
        "risk_score": 0.0,
        "findings": {},
    }

    # 1. Persist to Supabase
    db = get_db()
    try:
        case_model = InvestigationCase(
            id=case_id,
            target=req.target,
            type=req.type,
            status="open",
            evidence=req.evidence or [],
            agents_assigned=["nexus", "tracer", "cipher"],
            created_at=case_data["created_at"],
            updated_at=case_data["updated_at"],
        )
        await db.cases.create(case_model)
    except Exception as exc:
        print(f"[DB] Case create failed (falling back to Redis only): {exc}")

    # 2. Cache in Redis
    r = await get_redis()
    await r.hset("rmi:cases", case_id, json.dumps(case_data))

    # Notify n8n if configured
    if settings.N8N_WEBHOOK_URL:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(settings.N8N_WEBHOOK_URL, json={"event": "investigation_opened", "case": case_data})
        except:
            pass

    return case_data

def _is_admin(request: Request) -> bool:
    """Check if request has valid admin key."""
    key = request.headers.get("X-Admin-Key", "")
    return key == settings.ADMIN_API_KEY

@app.get("/api/v1/investigation/cases")
async def list_cases(request: Request):
    admin = _is_admin(request)
    # Read-through cache: Redis first, Supabase on miss
    r = await get_redis()
    cases_raw = await r.hgetall("rmi:cases") or {}
    cases = []
    if cases_raw:
        cases = [json.loads(v) for v in cases_raw.values()]

    # Inject CRM case if not already present
    crm_case = get_case_summary()
    if not any(c.get("id") == CASE_ID for c in cases):
        cases.insert(0, crm_case)
        await r.hset("rmi:cases", CASE_ID, json.dumps(crm_case))

    # SECURITY: Filter out unpublished CRM case for non-admins
    if not admin:
        cases = [c for c in cases if c.get("id") != CASE_ID or c.get("published") is True]

    if cases:
        return {"cases": cases, "total": len(cases), "source": "cache"}

    # Cache miss — query Supabase
    db = get_db()
    try:
        cases = await db.cases.list(limit=500)
        for case in cases:
            await r.hset("rmi:cases", case["id"], json.dumps(case))
        if not any(c.get("id") == CASE_ID for c in cases):
            cases.insert(0, crm_case)
            await r.hset("rmi:cases", CASE_ID, json.dumps(crm_case))
        if not admin:
            cases = [c for c in cases if c.get("id") != CASE_ID or c.get("published") is True]
        return {"cases": cases, "total": len(cases), "source": "supabase"}
    except Exception as exc:
        print(f"[DB] Cases list failed (returning empty): {exc}")
        if admin:
            return {"cases": [crm_case], "total": 1, "source": "error"}
        return {"cases": [], "total": 0, "source": "error"}

@app.get("/api/v1/investigation/cases/{case_id}")
async def get_case(case_id: str, request: Request):
    admin = _is_admin(request)
    r = await get_redis()
    case_raw = await r.hget("rmi:cases", case_id)
    if not case_raw:
        raise HTTPException(status_code=404, detail="Case not found")
    case = json.loads(case_raw)
    # SECURITY: Block unpublished CRM case for non-admins
    if case.get("id") == CASE_ID and not case.get("published") and not admin:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

# ═══════════════════════════════════════════════════════════════
# CRM INVESTIGATION — FULL INTEGRATION
# ═══════════════════════════════════════════════════════════════

@app.get("/api/v1/investigation/cases/{case_id}/crm/full")
async def get_crm_full_case(case_id: str, request: Request):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return get_full_case_data()

@app.get("/api/v1/investigation/cases/{case_id}/crm/timeline")
async def get_crm_timeline(case_id: str, request: Request):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"timeline": get_timeline()}

@app.get("/api/v1/investigation/cases/{case_id}/crm/structure")
async def get_crm_structure(case_id: str, request: Request):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return get_criminal_structure()

@app.get("/api/v1/investigation/cases/{case_id}/crm/wallets")
async def get_crm_wallets(case_id: str, request: Request, limit: int = 500):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"wallets": get_wallets_from_db(limit), "count": len(get_wallets_from_db(limit))}

@app.get("/api/v1/investigation/cases/{case_id}/crm/wallets/{address}")
async def get_crm_wallet_detail(case_id: str, address: str, request: Request):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    detail = get_wallet_details(address)
    if not detail:
        raise HTTPException(status_code=404, detail="Wallet not found in CRM database")
    return detail

@app.get("/api/v1/investigation/cases/{case_id}/crm/transactions")
async def get_crm_transactions(case_id: str, request: Request, min_suspicion: float = 0.0, limit: int = 100):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"transactions": get_transactions(min_suspicion, limit), "count": len(get_transactions(min_suspicion, limit))}

@app.get("/api/v1/investigation/cases/{case_id}/crm/graph")
async def get_crm_graph(case_id: str, request: Request):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return get_relationship_graph()

@app.get("/api/v1/investigation/cases/{case_id}/crm/evidence")
async def get_crm_evidence(case_id: str, request: Request):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return get_evidence_categories()

@app.get("/api/v1/investigation/cases/{case_id}/crm/stats")
async def get_crm_stats(case_id: str, request: Request):
    if case_id != CASE_ID:
        raise HTTPException(status_code=404, detail="CRM data only available for " + CASE_ID)
    if not is_published() and not _is_admin(request):
        raise HTTPException(status_code=404, detail="Case not found")
    return get_stats()

# Legacy syndicate endpoint — now powered by CRM data
@app.get("/api/v1/syndicate/wallets")
async def list_syndicate_wallets():
    wallets = get_wallets_from_db(limit=50)
    return {
        "case": CASE_ID,
        "wallets": wallets,
        "total": len(wallets),
    }

@app.get("/api/v1/syndicate/wallets/{address}")
async def get_syndicate_wallet(address: str):
    detail = get_wallet_details(address)
    if not detail:
        raise HTTPException(status_code=404, detail="Wallet not in syndicate database")
    return detail

# ═══════════════════════════════════════════════════════════════
# ALERTS
# ═══════════════════════════════════════════════════════════════
@app.post("/api/v1/alerts/subscribe")
async def subscribe_alert(req: AlertRequest, user: Dict[str, Any] = Depends(require_auth)):
    alert_id = f"alert:{datetime.utcnow().timestamp():.0f}"
    alert_data = {
        "id": alert_id,
        "token_address": req.token_address,
        "types": req.alert_types,
        "webhook_url": req.webhook_url,
        "created_at": datetime.utcnow().isoformat(),
        "active": True,
    }

    # 1. Persist to Supabase
    db = get_db()
    try:
        alert_model = Alert(
            id=alert_id,
            token_address=req.token_address,
            types=req.alert_types,
            webhook_url=req.webhook_url,
            active=True,
            created_at=alert_data["created_at"],
        )
        await db.alerts.create(alert_model)
    except Exception as exc:
        print(f"[DB] Alert create failed (falling back to Redis only): {exc}")

    # 2. Cache in Redis
    r = await get_redis()
    await r.hset("rmi:alerts", alert_id, json.dumps(alert_data))
    return alert_data

@app.get("/api/v1/alerts")
async def list_alerts():
    r = await get_redis()
    alerts_raw = await r.hgetall("rmi:alerts") or {}
    alerts = [json.loads(v) for v in alerts_raw.values()]
    return {"alerts": alerts, "total": len(alerts)}

# ═══════════════════════════════════════════════════════════════
# TRENCHES (Community Board)
# ═══════════════════════════════════════════════════════════════

class TrenchesPostRequest(BaseModel):
    title: str
    content: str
    category: str = Field(default="discussion", pattern="^(scam_report|discussion|intel|announcement)$")
    tags: Optional[List[str]] = None

class TrenchesCommentRequest(BaseModel):
    content: str

@app.post("/api/v1/trenches/posts")
async def create_trenches_post(req: TrenchesPostRequest, user: Dict[str, Any] = Depends(require_auth)):
    """Create a new post in The Trenches (write-through: Supabase -> Redis cache)."""
    post_id = f"post:{datetime.utcnow().timestamp():.0f}"
    post_data = {
        "id": post_id,
        "title": req.title,
        "content": req.content,
        "category": req.category,
        "tags": req.tags or [],
        "author_id": user["id"],
        "author_email": user.get("email", ""),
        "author_wallet": user.get("wallet_address", ""),
        "upvotes": 0,
        "comments": 0,
        "created_at": datetime.utcnow().isoformat(),
    }

    # 1. Persist to Supabase
    db = get_db()
    try:
        post_model = TrenchesPost(
            id=post_id,
            title=req.title,
            content=req.content,
            category=req.category,
            author_id=user["id"],
            upvotes=0,
            comments=0,
            tags=req.tags or [],
            created_at=post_data["created_at"],
        )
        await db.trenches_posts.create(post_model)
    except Exception as exc:
        print(f"[DB] Trenches post create failed (falling back to Redis only): {exc}")

    # 2. Cache in Redis
    r = await get_redis()
    await r.hset("rmi:trenches:posts", post_id, json.dumps(post_data))
    
    # Award XP
    try:
        from app.gamification_service import record_activity
        await record_activity(user["id"], "post_created")
    except Exception as e:
        print(f"[GAMI] Failed to record post XP: {e}")
    
    return post_data

@app.get("/api/v1/trenches/posts")
async def list_trenches_posts(category: Optional[str] = None, limit: int = 50):
    """List posts from The Trenches (read-through cache)."""
    r = await get_redis()
    posts_raw = await r.hgetall("rmi:trenches:posts") or {}
    if posts_raw:
        posts = [json.loads(v) for v in posts_raw.values()]
        posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        if category and category != "all":
            posts = [p for p in posts if p.get("category") == category]
        return {"posts": posts[:limit], "total": len(posts), "source": "cache"}

    # Cache miss — query Supabase
    db = get_db()
    try:
        posts = await db.trenches_posts.list(limit=limit, category=category)
        # Populate Redis cache
        for post in posts:
            await r.hset("rmi:trenches:posts", post["id"], json.dumps(post))
        return {"posts": posts, "total": len(posts), "source": "supabase"}
    except Exception as exc:
        print(f"[DB] Trenches posts list failed (returning empty): {exc}")
        return {"posts": [], "total": 0, "source": "error"}

@app.post("/api/v1/trenches/posts/{post_id}/comments")
async def create_trenches_comment(post_id: str, req: TrenchesCommentRequest, user: Dict[str, Any] = Depends(require_auth)):
    """Add a comment to a post."""
    r = await get_redis()
    
    # Check post exists
    post_raw = await r.hget("rmi:trenches:posts", post_id)
    if not post_raw:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment_id = f"comment:{datetime.utcnow().timestamp():.0f}"
    comment_data = {
        "id": comment_id,
        "post_id": post_id,
        "content": req.content,
        "author_id": user["id"],
        "author_email": user.get("email", ""),
        "created_at": datetime.utcnow().isoformat(),
    }
    await r.hset("rmi:trenches:comments", comment_id, json.dumps(comment_data))
    
    # Increment post comment count
    post = json.loads(post_raw)
    post["comments"] = post.get("comments", 0) + 1
    await r.hset("rmi:trenches:posts", post_id, json.dumps(post))
    
    # Award XP
    try:
        from app.gamification_service import record_activity
        await record_activity(user["id"], "comment_created")
    except Exception as e:
        print(f"[GAMI] Failed to record comment XP: {e}")
    
    return comment_data

@app.get("/api/v1/trenches/posts/{post_id}/comments")
async def list_trenches_comments(post_id: str):
    """List comments for a post."""
    r = await get_redis()
    comments_raw = await r.hgetall("rmi:trenches:comments") or {}
    comments = [json.loads(v) for v in comments_raw.values() if json.loads(v).get("post_id") == post_id]
    comments.sort(key=lambda x: x.get("created_at", ""))
    return {"comments": comments}

# ═══════════════════════════════════════════════════════════════
# UNIVERSAL COMMENTS (works on any content type)
# ═══════════════════════════════════════════════════════════════

class CommentRequest(BaseModel):
    content_type: str  # 'trenches_post', 'news', 'bot_intel', 'fear_greed', 'scan_result', etc.
    content_id: str
    body: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[str] = None

@app.post("/api/v1/comments")
async def create_comment(req: CommentRequest, user: Dict[str, Any] = Depends(require_auth)):
    """Create a comment on any content type."""
    comment_id = f"uc:{datetime.utcnow().timestamp():.0f}"
    comment_data = {
        "id": comment_id,
        "content_type": req.content_type,
        "content_id": req.content_id,
        "body": req.body,
        "user_id": user["id"],
        "author_email": user.get("email", ""),
        "author_wallet": user.get("wallet_address", ""),
        "parent_id": req.parent_id,
        "upvotes": 0,
        "created_at": datetime.utcnow().isoformat(),
    }
    r = await get_redis()
    await r.hset("rmi:comments", comment_id, json.dumps(comment_data))

    # Also persist to Supabase if available
    db = get_db()
    try:
        db.db.table("content_comments").insert({
            "content_type": req.content_type,
            "content_id": req.content_id,
            "user_id": user["id"],
            "parent_id": req.parent_id,
            "body": req.body,
        }).execute()
    except Exception as exc:
        print(f"[DB] Comment persist failed: {exc}")

    # Award XP
    try:
        from app.gamification_service import record_activity
        await record_activity(user["id"], "comment_created")
    except Exception as e:
        print(f"[GAMI] Failed to record comment XP: {e}")

    return comment_data

@app.get("/api/v1/comments")
async def list_comments(content_type: str, content_id: str):
    """List comments for any content type + id."""
    r = await get_redis()
    comments_raw = await r.hgetall("rmi:comments") or {}
    comments = [
        json.loads(v) for v in comments_raw.values()
        if json.loads(v).get("content_type") == content_type and json.loads(v).get("content_id") == content_id
    ]
    comments.sort(key=lambda x: x.get("created_at", ""))
    return {"comments": comments, "total": len(comments)}

@app.post("/api/v1/comments/{comment_id}/upvote")
async def upvote_comment(comment_id: str, user: Dict[str, Any] = Depends(require_auth)):
    """Upvote a comment."""
    r = await get_redis()
    comment_raw = await r.hget("rmi:comments", comment_id)
    if not comment_raw:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment = json.loads(comment_raw)
    comment["upvotes"] = comment.get("upvotes", 0) + 1
    await r.hset("rmi:comments", comment_id, json.dumps(comment))
    return comment

@app.delete("/api/v1/comments/{comment_id}")
async def delete_comment(comment_id: str, user: Dict[str, Any] = Depends(require_auth)):
    """Delete own comment."""
    r = await get_redis()
    comment_raw = await r.hget("rmi:comments", comment_id)
    if not comment_raw:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment = json.loads(comment_raw)
    if comment.get("user_id") != user["id"] and user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Not your comment")
    await r.hdel("rmi:comments", comment_id)
    return {"deleted": True}

@app.post("/api/v1/trenches/posts/{post_id}/upvote")
async def upvote_trenches_post(post_id: str, user: Dict[str, Any] = Depends(require_auth)):
    """Upvote a post."""
    r = await get_redis()
    
    post_raw = await r.hget("rmi:trenches:posts", post_id)
    if not post_raw:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = json.loads(post_raw)
    post["upvotes"] = post.get("upvotes", 0) + 1
    await r.hset("rmi:trenches:posts", post_id, json.dumps(post))
    
    # Award XP to voter
    try:
        from app.gamification_service import record_activity
        await record_activity(user["id"], "upvote_given")
        # Award XP to post author
        if post.get("author_id") and post["author_id"] != user["id"]:
            await record_activity(post["author_id"], "upvote_received")
    except Exception as e:
        print(f"[GAMI] Failed to record upvote XP: {e}")
    
    return {"upvotes": post["upvotes"]}

# ═══════════════════════════════════════════════════════════════
# CONSENSUS
# ═══════════════════════════════════════════════════════════════
@app.post("/api/v1/consensus")
async def run_consensus(req: ConsensusRequest):
    """Run Delphi-style multi-agent consensus across specialist agents."""
    agent_profiles = [
        {"name": "TRACER", "role": "forensic", "tier": "T1",
         "system": "You are TRACER, a forensic blockchain investigator. Analyze the evidence for wallet patterns, funding traces, transaction anomalies, and coordination signs. Return JSON with decision (approve/reject/uncertain), confidence (0-1), and reasoning."},
        {"name": "CIPHER", "role": "code", "tier": "T1",
         "system": "You are CIPHER, a smart contract security auditor. Analyze for code vulnerabilities, authority issues, upgrade risks, and hidden functions. Return JSON with decision (approve/reject/uncertain), confidence (0-1), and reasoning."},
        {"name": "SENTINEL", "role": "threat", "tier": "T2",
         "system": "You are SENTINEL, a threat detection specialist. Look for rug pull indicators, honeypot patterns, malicious behavior, and known scam signatures. Return JSON with decision (approve/reject/uncertain), confidence (0-1), and reasoning."},
        {"name": "SCOUT", "role": "market", "tier": "T3",
         "system": "You are SCOUT, a market intelligence analyst. Look for tokenomics red flags, liquidity issues, holder concentration, and price manipulation. Return JSON with decision (approve/reject/uncertain), confidence (0-1), and reasoning."},
    ]

    # Limit agents based on request (max 5)
    active_profiles = agent_profiles[: min(req.min_agents, 5)]
    if len(active_profiles) < 2:
        active_profiles = agent_profiles[:2]

    evidence_json = json.dumps(req.evidence, default=str)

    # ── Phase 1: specialist agents in parallel ──
    async def _agent_vote(profile: Dict[str, str]) -> Dict[str, Any]:
        prompt = (
            f"{profile['system']}\n\n"
            f"Topic: {req.topic}\n"
            f"Evidence: {evidence_json}\n\n"
            f"Return JSON with keys: decision (approve/reject/uncertain), confidence (0-1), reasoning (string)."
        )
        raw = await _get_ai_analysis(prompt, tier=profile["tier"])
        if "error" in raw:
            return {
                "agent": profile["name"],
                "role": profile["role"],
                "decision": "uncertain",
                "confidence": 0.0,
                "reasoning": f"AI error: {raw.get('error')}",
                "error": raw.get("error"),
            }
        return {
            "agent": profile["name"],
            "role": profile["role"],
            "decision": str(raw.get("decision", "uncertain")).lower(),
            "confidence": float(raw.get("confidence", 0)),
            "reasoning": str(raw.get("reasoning", "")),
        }

    agent_votes = await asyncio.gather(*[_agent_vote(p) for p in active_profiles])

    # ── Phase 2: NEXUS synthesis (runs after specialists) ──
    nexus_vote: Dict[str, Any] = {}
    try:
        nexus_prompt = (
            "You are NEXUS, a strategic coordinator. Synthesize the following specialist agent opinions into a final recommendation.\n\n"
            f"Topic: {req.topic}\n"
            f"Evidence: {evidence_json}\n\n"
            "Specialist opinions:\n"
        )
        for v in agent_votes:
            nexus_prompt += f"- {v['agent']} ({v['role']}): {v['decision']} (confidence: {v['confidence']}) — {v['reasoning']}\n"
        nexus_prompt += (
            "\nReturn JSON with decision (approve/reject/uncertain), confidence (0-1), and synthesis (string)."
        )
        nexus_raw = await _get_ai_analysis(nexus_prompt, tier="T0")
        if "error" not in nexus_raw:
            nexus_vote = {
                "agent": "NEXUS",
                "role": "strategic",
                "decision": str(nexus_raw.get("decision", "uncertain")).lower(),
                "confidence": float(nexus_raw.get("confidence", 0)),
                "reasoning": str(nexus_raw.get("synthesis", nexus_raw.get("reasoning", ""))),
            }
        else:
            nexus_vote = {
                "agent": "NEXUS",
                "role": "strategic",
                "decision": "uncertain",
                "confidence": 0.0,
                "reasoning": f"Nexus synthesis error: {nexus_raw.get('error')}",
                "error": nexus_raw.get("error"),
            }
    except Exception as e:
        nexus_vote = {
            "agent": "NEXUS",
            "role": "strategic",
            "decision": "uncertain",
            "confidence": 0.0,
            "reasoning": f"Nexus exception: {e}",
            "error": str(e),
        }

    all_votes = agent_votes + [nexus_vote]

    # ── Phase 3: calculate consensus ──
    total = len(all_votes)
    counts: Dict[str, int] = {}
    for v in all_votes:
        d = v["decision"]
        counts[d] = counts.get(d, 0) + 1

    final_decision = "uncertain"
    confidence = 0.0
    if total > 0 and counts:
        max_decision, max_count = max(counts.items(), key=lambda x: x[1])
        if max_count / total >= req.threshold:
            final_decision = max_decision
            agreeing = [v for v in all_votes if v["decision"] == final_decision]
            confidence = round(sum(v["confidence"] for v in agreeing) / len(agreeing), 2)
        else:
            # No super-majority; fall back to weighted average leaning
            confidence = round(sum(v["confidence"] for v in all_votes) / total, 2)

    dissenting_opinions = [v for v in all_votes if v["decision"] != final_decision]

    return {
        "topic": req.topic,
        "agents_participated": total,
        "threshold": req.threshold,
        "result": final_decision,
        "confidence": confidence,
        "agent_votes": all_votes,
        "dissenting_opinions": dissenting_opinions,
        "synthesis": nexus_vote.get("reasoning", ""),
        "timestamp": datetime.utcnow().isoformat(),
    }

# ═══════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════
@app.get("/api/v1/admin/agents", dependencies=[Depends(verify_admin_key)])
async def admin_agents():
    r = await get_redis()
    agents_raw = await r.hgetall("rmi:agents") or {}
    return {"agents": {k: json.loads(v) for k, v in agents_raw.items()}}

@app.post("/api/v1/admin/agents/{agent_id}/role", dependencies=[Depends(verify_admin_key)])
async def set_agent_role(agent_id: str, role: str, request: Request):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    r = await get_redis()
    await r.hset(f"rmi:agent:{agent_id}:config", "role", role)
    await r.publish("rmi:agent:reload", json.dumps({"agent": agent_id, "role": role}))
    return {"agent": agent_id, "new_role": role, "status": "updated"}

@app.get("/api/v1/admin/tasks", dependencies=[Depends(verify_admin_key)])
async def admin_tasks():
    r = await get_redis()
    tasks_raw = await r.hgetall("rmi:tasks") or {}
    tasks = [json.loads(v) for v in tasks_raw.values()]
    return {"tasks": tasks, "total": len(tasks)}

@app.post("/api/v1/admin/self-heal", dependencies=[Depends(verify_admin_key)])
async def trigger_self_heal():
    r = await get_redis()
    await r.lpush("rmi:queue:system", json.dumps({"type": "self_heal", "timestamp": datetime.utcnow().isoformat()}))
    return {"status": "self_heal_triggered"}

# ═══════════════════════════════════════════════════════════════
# ADMIN CASE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@app.get("/api/v1/admin/cases/{case_id}/publish-status", dependencies=[Depends(verify_admin_key)])
async def admin_get_publish_status(case_id: str):
    """Get publication status for a case."""
    if case_id == CASE_ID:
        return {"case_id": CASE_ID, "published": is_published(), "source": "filesystem"}
    # For regular cases, check Supabase
    db = get_db()
    try:
        case = await db.cases.get(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return {"case_id": case_id, "published": case.get("published", False), "source": "supabase"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/cases/{case_id}/publish", dependencies=[Depends(verify_admin_key)])
async def admin_publish_case(case_id: str):
    """Publish a case so it appears in public API responses."""
    if case_id == CASE_ID:
        new_state = set_published(True)
        # Update Redis cache
        r = await get_redis()
        crm_case = get_case_summary()
        await r.hset("rmi:cases", CASE_ID, json.dumps(crm_case))
        return {"case_id": CASE_ID, "published": new_state, "action": "published"}
    db = get_db()
    try:
        await db.cases.update(case_id, {"published": True})
        return {"case_id": case_id, "published": True, "action": "published"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/cases/{case_id}/unpublish", dependencies=[Depends(verify_admin_key)])
async def admin_unpublish_case(case_id: str):
    """Unpublish a case to hide it from public API responses."""
    if case_id == CASE_ID:
        new_state = set_published(False)
        r = await get_redis()
        crm_case = get_case_summary()
        await r.hset("rmi:cases", CASE_ID, json.dumps(crm_case))
        return {"case_id": CASE_ID, "published": new_state, "action": "unpublished"}
    db = get_db()
    try:
        await db.cases.update(case_id, {"published": False})
        return {"case_id": case_id, "published": False, "action": "unpublished"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── MAIN ──



# ═══════════════════════════════════════════════════════════════
# BIRDEYE CRYPTO SECURITY SUITE
# ═══════════════════════════════════════════════════════════════

@app.post("/api/v1/security/scan")
async def security_scan_token(req: TokenScanRequest):
    """Full security audit: mint authority, freeze authority, holder concentration, risks"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        result = await client.security_scan(req.address)
        return {
            "address": req.address,
            "chain": req.chain,
            "risk_score": result.get("risk_score", 0),
            "risk_level": result.get("risk_level", "UNKNOWN"),
            "token_name": result.get("token_name", ""),
            "symbol": result.get("symbol", ""),
            "price": result.get("price", 0),
            "market_cap": result.get("market_cap", 0),
            "liquidity": result.get("liquidity", 0),
            "holders": result.get("holders", 0),
            "price_change_24h": result.get("price_change_24h", 0),
            "security_flags": result.get("flags", []),
            "positive_signals": result.get("positive_signals", []),
            "metadata": result.get("metadata", {}),
            "analyzed_at": result.get("analyzed_at"),
            "birdeye_powered": True
        }
    finally:
        await client.close()

@app.get("/api/v1/security/scan/{address}")
async def security_scan_get(address: str, chain: str = "solana"):
    """GET version of security scan for easy browser access"""
    return await security_scan_token(TokenScanRequest(address=address, chain=chain))

@app.get("/api/v1/tokens/new")
async def new_token_radar(limit: int = 20, min_liquidity: float = 1000):
    """New token radar with safety scoring — finds gems early"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        tokens = await client.get_new_listings(limit=limit, min_liquidity=min_liquidity)
        return {
            "tokens": tokens,
            "count": len(tokens),
            "filter": {"min_liquidity": min_liquidity},
            "timestamp": datetime.utcnow().isoformat(),
            "birdeye_powered": True
        }
    finally:
        await client.close()

@app.get("/api/v1/tokens/trending")
async def trending_tokens(limit: int = 20, timeframe: str = "30m"):
    """Trending tokens with momentum — meme discovery, breakout detection"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        tokens = await client.get_trending(limit=limit, timeframe=timeframe)
        return {
            "tokens": tokens,
            "count": len(tokens),
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat(),
            "birdeye_powered": True
        }
    finally:
        await client.close()

@app.get("/api/v1/smart-money")
async def smart_money_activity(limit: int = 50):
    """Track smart money (profitable wallets) — copy-trade signals"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        activity = await client.get_smart_money_activity(limit=limit)
        return {
            "activities": activity,
            "count": len(activity),
            "timestamp": datetime.utcnow().isoformat(),
            "birdeye_powered": True
        }
    finally:
        await client.close()

@app.get("/api/v1/wallet/{address}/analysis")
async def wallet_full_analysis(address: str):
    """Complete wallet analysis: networth, PnL, smart money status"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        networth, pnl, smart = await asyncio.gather(
            client.get_wallet_networth(address),
            client.get_wallet_pnl(address),
            client.get_wallet_smart_money_status(address),
            return_exceptions=True
        )

        return {
            "address": address,
            "networth": networth if not isinstance(networth, Exception) else {"error": str(networth)},
            "pnl": pnl if not isinstance(pnl, Exception) else {"error": str(pnl)},
            "smart_money_status": smart if not isinstance(smart, Exception) else {"error": str(smart)},
            "timestamp": datetime.utcnow().isoformat(),
            "birdeye_powered": True
        }
    finally:
        await client.close()

@app.get("/api/v1/wallet/{address}/pnl")
async def wallet_pnl(address: str, timeframe: str = "7d"):
    """Wallet profit/loss analysis"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        result = await client.get_wallet_pnl(address, timeframe)
        return {"address": address, "timeframe": timeframe, "data": result, "birdeye_powered": True}
    finally:
        await client.close()

@app.get("/api/v1/tokens/{address}/holders")
async def token_holders(address: str):
    """Holder concentration analysis — whale risk detection"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        result = await client.get_holder_distribution(address)
        return {"address": address, "holders": result, "birdeye_powered": True}
    finally:
        await client.close()

@app.get("/api/v1/tokens/{address}/large-txs")
async def large_transactions(address: str, min_usd: float = 10000):
    """Large transaction monitoring — whale alerts"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        txs = await client.get_large_transactions(address, min_usd)
        return {
            "address": address,
            "min_usd": min_usd,
            "transactions": txs,
            "count": len(txs),
            "birdeye_powered": True
        }
    finally:
        await client.close()

@app.get("/api/v1/tokens/{address}/overview")
async def token_overview(address: str):
    """Comprehensive token data: price, volume, liquidity, market cap"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        result = await client.get_token_overview(address)
        return {"address": address, "data": result, "birdeye_powered": True}
    finally:
        await client.close()

@app.get("/api/v1/tokens/{address}/ohlcv")
async def token_ohlcv(address: str, timeframe: str = "1H", limit: int = 24):
    """OHLCV chart data for visualization"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()
    try:
        result = await client.get_ohlcv(address, timeframe, limit)
        return {"address": address, "timeframe": timeframe, "data": result, "birdeye_powered": True}
    finally:
        await client.close()

@app.post("/api/v1/crypto/full-scan")
async def crypto_full_scan(req: TokenScanRequest):
    """ULTIMATE: Complete crypto intelligence scan combining ALL APIs"""
    from app.birdeye_client import BirdeyeClient
    client = BirdeyeClient()

    try:
        # Run all scans in parallel
        birdeye, helius_data = await asyncio.gather(
            client.security_scan(req.address),
            _get_helius_data(req.address),
            return_exceptions=True
        )

        # Compile comprehensive report
        security = birdeye.get("security", {}) if not isinstance(birdeye, Exception) else {}
        overview = birdeye.get("overview", {}) if not isinstance(birdeye, Exception) else {}

        risk_score = security.get("risk_score", 0)

        verdict = "SAFE"
        if risk_score >= 60:
            verdict = "🚨 HIGH RISK - LIKELY SCAM"
        elif risk_score >= 30:
            verdict = "⚠️ MEDIUM RISK - PROCEED WITH CAUTION"
        elif risk_score >= 10:
            verdict = "🟡 LOW-MEDIUM RISK"
        else:
            verdict = "🟢 LOW RISK"

        return {
            "address": req.address,
            "chain": req.chain,
            "verdict": verdict,
            "risk_score": risk_score,
            "risk_level": security.get("risk_level", "UNKNOWN"),
            "security_flags": security.get("flags", []),
            "birdeye_data": birdeye if not isinstance(birdeye, Exception) else {"error": str(birdeye)},
            "helius_data": helius_data if not isinstance(helius_data, Exception) else {"error": str(helius_data)},
            "scanned_at": datetime.utcnow().isoformat(),
            "sources": ["birdeye", "helius"],
        }
    finally:
        await client.close()

async def _get_helius_data(address: str):
    """Get additional data from Helius"""
    helius_key = os.getenv("HELIUS_API_KEY", "")
    if not helius_key:
        return {"error": "No Helius key"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get(f"https://api.helius.xyz/v0/tokens/?api-key={helius_key}&address={address}")
            return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}


async def _get_ai_analysis(prompt: str, tier: str = "T2") -> Dict[str, Any]:
    """Helper: route an AI analysis prompt through the AI router with JSON parsing and error handling."""
    try:
        from app.ai_router import router as ai_router
        messages = [
            {"role": "system", "content": "You are a crypto security analyst. Respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ]
        result = await ai_router.chat_completion(
            messages=messages, tier=tier, temperature=0.2, max_tokens=2048, timeout=30.0
        )
        if "error" in result:
            return {"error": result["error"], "raw": result.get("content", "")}
        content = result.get("content", "")
        parsed: Optional[Dict[str, Any]] = None
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
        if parsed is None:
            return {"error": "Failed to parse AI response as JSON", "raw": content}
        return parsed
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# GMGN AI AGENT + ORIGINAL INTELLIGENCE FEATURES
# ═══════════════════════════════════════════════════════════════

@app.get("/api/v1/gmgn/token/{address}")
async def gmgn_token(address: str, chain: str = "solana"):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.query_token(address, chain)
    finally: await c.close()

@app.get("/api/v1/gmgn/market/{address}")
async def gmgn_market(address: str, resolution: str = "1h", limit: int = 24):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.query_market(address, resolution, limit)
    finally: await c.close()

@app.get("/api/v1/gmgn/portfolio/{wallet}")
async def gmgn_portfolio(wallet: str, chain: str = "solana"):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.query_portfolio(wallet, chain)
    finally: await c.close()

# ORIGINAL FEATURE #1: Smart Money Narrative
@app.get("/api/v1/intelligence/narrative/{address}")
async def smart_money_narrative(address: str):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.smart_money_narrative(address)
    finally: await c.close()

# ORIGINAL FEATURE #2: Degen Score
@app.get("/api/v1/intelligence/degen/{address}")
async def degen_score(address: str):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.degen_score(address)
    finally: await c.close()

# ORIGINAL FEATURE #3: Sniper Radar
@app.get("/api/v1/intelligence/sniper/{address}")
async def sniper_radar(address: str):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.sniper_radar(address)
    finally: await c.close()

# ORIGINAL FEATURE #4: Trending Deep Dive
@app.get("/api/v1/intelligence/trending")
async def trending_deep_dive(limit: int = 10):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.trending_deep_dive(limit)
    finally: await c.close()

# ORIGINAL FEATURE #5: Cross-Reference Engine
@app.get("/api/v1/intelligence/crossref/{address}")
async def cross_reference(address: str):
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try: return await c.cross_reference(address)
    finally: await c.close()

# ULTIMATE: Full Intelligence Report
@app.get("/api/v1/intelligence/full/{address}")
async def full_intelligence_report(address: str):
    """Complete intelligence report combining ALL features"""
    from app.gmgn_client import GMGNClient
    c = GMGNClient()
    try:
        security, narrative, degen, sniper, crossref = await asyncio.gather(
            c.birdeye.security_scan(address),
            c.smart_money_narrative(address),
            c.degen_score(address),
            c.sniper_radar(address),
            c.cross_reference(address),
            return_exceptions=True
        )
        return {
            "address": address,
            "executive_summary": narrative.get("verdict", "") if not isinstance(narrative, Exception) else "Error",
            "security": security if not isinstance(security, Exception) else {"error": str(security)},
            "narrative": narrative if not isinstance(narrative, Exception) else {"error": str(narrative)},
            "degen_score": degen if not isinstance(degen, Exception) else {"error": str(degen)},
            "sniper_radar": sniper if not isinstance(sniper, Exception) else {"error": str(sniper)},
            "cross_reference": crossref if not isinstance(crossref, Exception) else {"error": str(crossref)},
            "generated_at": datetime.utcnow().isoformat(),
        }
    finally:
        await c.close()

# ═══════════════════════════════════════════════════════════════
# DEXSCREENER SCAM FINDER
# ═══════════════════════════════════════════════════════════════

@app.get("/api/v1/scam-finder/profile-flips")
async def scam_profile_flips():
    from app.dexscreener_scam_finder import DexScreenerScamFinder
    c = DexScreenerScamFinder()
    try: return await c.profile_flip_detector()
    finally: await c.close()

@app.get("/api/v1/scam-finder/boost-traps")
async def scam_boost_traps():
    from app.dexscreener_scam_finder import DexScreenerScamFinder
    c = DexScreenerScamFinder()
    try: return await c.boost_trap_analyzer()
    finally: await c.close()

@app.get("/api/v1/scam-finder/cta-risks")
async def scam_cta_risks():
    from app.dexscreener_scam_finder import DexScreenerScamFinder
    c = DexScreenerScamFinder()
    try: return await c.cta_risk_scorer()
    finally: await c.close()

@app.get("/api/v1/scam-finder/meta-scams")
async def scam_meta_scams():
    from app.dexscreener_scam_finder import DexScreenerScamFinder
    c = DexScreenerScamFinder()
    try: return await c.meta_scam_hunter()
    finally: await c.close()

@app.get("/api/v1/scam-finder/fresh-pairs")
async def scam_fresh_pairs():
    from app.dexscreener_scam_finder import DexScreenerScamFinder
    c = DexScreenerScamFinder()
    try: return await c.fresh_pair_scanner()
    finally: await c.close()

@app.get("/api/v1/scam-finder/clones")
async def scam_clones():
    from app.dexscreener_scam_finder import DexScreenerScamFinder
    c = DexScreenerScamFinder()
    try: return await c.clone_detector()
    finally: await c.close()

@app.get("/api/v1/scam-finder/full-scan")
async def scam_full_scan():
    from app.dexscreener_scam_finder import DexScreenerScamFinder
    c = DexScreenerScamFinder()
    try: return await c.full_scam_scan()
    finally: await c.close()


# ═══════════════════════════════════════════════════════════════════════════
# HELIUS ROUTES — On-chain intelligence
# ═══════════════════════════════════════════════════════════════════════════

class WhaleScanRequest(BaseModel):
    token_address: str

class WalletTrackRequest(BaseModel):
    wallet_address: str

class SniperCheckRequest(BaseModel):
    token_address: str

@app.post("/api/v1/helius/whale-scan")
async def helius_whale_scan(req: WhaleScanRequest):
    """Scan token for whale concentration and activity."""
    from app.helius_tools.helius_whale_watcher import WhaleWatcher
    w = WhaleWatcher()
    try:
        result = await w.scan_token_for_whales(req.token_address)
        return {"status": "ok", "data": result}
    finally:
        await w.close()

@app.post("/api/v1/helius/whale-profile")
async def helius_whale_profile(req: WalletTrackRequest):
    """Build whale profile for a wallet."""
    from app.helius_tools.helius_whale_watcher import WhaleWatcher
    w = WhaleWatcher()
    try:
        result = await w.get_whale_profile(req.wallet_address)
        return {"status": "ok", "data": result}
    finally:
        await w.close()

@app.post("/api/v1/helius/sniper-detect")
async def helius_sniper_detect(req: SniperCheckRequest):
    """Detect coordinated sniping on token launch."""
    from app.helius_tools.helius_sniper_detector import SniperDetector
    d = SniperDetector()
    try:
        result = await d.analyze_token_launch(req.token_address)
        return {"status": "ok", "data": {
            "token_address": result.token_address,
            "launch_tx": result.launch_tx,
            "total_snipers": result.total_sniper_count,
            "coordinated_snipers": result.coordinated_sniper_count,
            "jito_bundles": result.jito_bundle_count,
            "avg_time_to_buy_ms": round(result.avg_time_to_first_buy_ms, 2),
            "total_sniper_volume_sol": round(result.total_sniper_volume_sol, 4),
            "ring_detected": result.ring_detected,
            "ring_size": result.ring_size,
            "insider_probability": result.insider_probability,
            "risk_verdict": result.risk_verdict,
            "evidence": result.evidence,
            "sniper_wallets": [
                {"address": s.address, "time_ms": round(s.first_buy_time_ms, 2),
                 "position_sol": round(s.position_size_sol, 4), "is_jito": s.is_jito_bundle,
                 "funding": s.funding_source}
                for s in result.sniper_wallets[:20]
            ],
            "timestamp": result.detection_time.isoformat(),
        }}
    finally:
        await d.close()

@app.get("/api/v1/helius/syndicate/scan")
async def helius_syndicate_scan():
    """Full scan of CRM V1 contract and syndicate wallets."""
    from app.helius_tools.helius_syndicate_tracker import SyndicateTracker
    t = SyndicateTracker()
    try:
        result = await t.scan_contract()
        return {"status": "ok", "data": result}
    finally:
        await t.close()

@app.post("/api/v1/helius/syndicate/track-wallet")
async def helius_track_wallet(req: WalletTrackRequest):
    """Track a specific syndicate wallet."""
    from app.helius_tools.helius_syndicate_tracker import SyndicateTracker
    t = SyndicateTracker()
    try:
        result = await t.track_wallet(req.wallet_address)
        return {"status": "ok", "data": result}
    finally:
        await t.close()

@app.get("/api/v1/helius/syndicate/wallet-graph")
async def helius_wallet_graph():
    """Build interaction graph between syndicate wallets."""
    from app.helius_tools.helius_syndicate_tracker import SyndicateTracker
    t = SyndicateTracker()
    try:
        result = await t.build_wallet_graph()
        return {"status": "ok", "data": result}
    finally:
        await t.close()



# ═══════════════════════════════════════════════════════════════════════════
# HELIUS WEBHOOK — Real-time on-chain event receiver
# Preserves existing webhook: 7263c8c2-63d0-49b3-9d4e-860b26c5d874
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/webhook/helius")
async def helius_webhook_receiver(request: Request):
    """Receive and process Helius webhook events for CRM V1 + general."""
    from app.helius_tools.helius_syndicate_tracker import SyndicateTracker
    
    try:
        event_data = await request.json()
    except:
        return {"status": "error", "message": "Invalid JSON"}
    
    # Log the event
    logger.info(f"[HELIUS WEBHOOK] Received event: type={event_data.get('type', 'unknown')}, signature={event_data.get('signature', 'N/A')[:20]}...")
    
    # Process through syndicate tracker
    tracker = SyndicateTracker()
    try:
        events = await tracker.handle_webhook_event(event_data)
        
        # If CRM V1 contract involved, alert
        crm_events = [e for e in events if e.token_address == "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"]
        
        result = {
            "status": "processed",
            "events_received": len(events),
            "crm_v1_events": len(crm_events),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if crm_events:
            result["alert"] = f"CRM V1 activity detected: {len(crm_events)} transfer(s)"
            logger.warning(f"[SYNDICATE ALERT] CRM V1 activity: {len(crm_events)} events")
        
        return result
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        await tracker.close()

@app.get("/webhook/helius")
async def helius_webhook_verify():
    """Verification endpoint for Helius webhook setup."""
    return {"status": "ready", "webhook": "helius", "timestamp": datetime.utcnow().isoformat()}

# ═══════════════════════════════════════════════════════════════════════════
# MORALIS ROUTES — Multi-Chain Intelligence
# ═══════════════════════════════════════════════════════════════════════════

class CrossChainProfileRequest(BaseModel):
    wallet_address: str

class TokenDiscoveryRequest(BaseModel):
    query: Optional[str] = None
    chain: Optional[str] = None

@app.post("/api/v1/moralis/cross-chain-profile")
async def moralis_cross_chain_profile(req: CrossChainProfileRequest):
    """Unified cross-chain profile for any wallet (Solana + EVM)."""
    from app.moralis_client import get_moralis_client
    client = get_moralis_client()
    try:
        result = await client.cross_chain_profile(req.wallet_address)
        return {"status": "ok", "data": {
            "wallet": result.wallet_address,
            "chains_found": result.chains_found,
            "total_value_usd": result.total_value_usd,
            "total_tokens": result.total_tokens,
            "total_nfts": result.total_nfts,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "tags": result.tags,
            "chain_portfolios": [
                {
                    "chain": p.chain,
                    "native_balance": p.native_balance,
                    "native_usd": p.native_balance_usd,
                    "token_count": p.token_count,
                    "total_value_usd": p.total_value_usd,
                    "tokens": p.tokens[:10],
                    "risk_flags": p.risk_flags,
                }
                for p in result.chain_portfolios
            ],
            "summary": result.analysis_summary,
            "cu_status": client.get_cu_status(),
        }}
    finally:
        await client.close()

@app.post("/api/v1/moralis/token-discovery")
async def moralis_token_discovery(req: TokenDiscoveryRequest):
    """Discover trending tokens across chains."""
    from app.moralis_client import get_moralis_client
    client = get_moralis_client()
    try:
        results = await client.discover_tokens(req.query, req.chain)
        return {"status": "ok", "data": {
            "tokens": [
                {
                    "address": t.address,
                    "chain": t.chain,
                    "name": t.name,
                    "symbol": t.symbol,
                    "price_usd": t.price_usd,
                    "market_cap": t.market_cap,
                    "volume_24h": t.volume_24h,
                    "price_change_24h": t.price_change_24h,
                    "verified": t.is_verified,
                    "holders": t.holder_count,
                    "liquidity_usd": t.liquidity_usd,
                    "risk_flags": t.risk_flags,
                }
                for t in results[:20]
            ],
            "count": len(results),
            "cu_status": client.get_cu_status(),
        }}
    finally:
        await client.close()

@app.get("/api/v1/moralis/sol-portfolio/{wallet}")
async def moralis_sol_portfolio(wallet: str):
    """Get Solana portfolio via Moralis."""
    from app.moralis_client import get_moralis_client
    client = get_moralis_client()
    try:
        result = await client.sol_portfolio(wallet)
        return {"status": "ok", "data": result, "cu_status": client.get_cu_status()}
    finally:
        await client.close()

@app.get("/api/v1/moralis/cu-status")
async def moralis_cu_status():
    """Get Moralis CU usage status."""
    from app.moralis_client import get_moralis_client
    client = get_moralis_client()
    return {"status": "ok", "data": client.get_cu_status()}


# ═══════════════════════════════════════════════════════════════════════════
# GMGN V2 ROUTES — Full Skill Modules (Market, Token, Portfolio, Track)
# ═══════════════════════════════════════════════════════════════════════════

class GMGNScanRequest(BaseModel):
    chain: str = "sol"
    token_address: str

class GMGNWalletRequest(BaseModel):
    chain: str = "sol"
    wallet_address: str

class GMGNKlineRequest(BaseModel):
    chain: str = "sol"
    token_address: str
    resolution: str = "1h"

@app.post("/api/v1/gmgn-v2/deep-scan")
async def gmgn_deep_scan(req: GMGNScanRequest):
    """Comprehensive token scan combining ALL GMGN modules."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        result = await client.token_deep_scan(req.chain, req.token_address)
        return {"status": "ok", "data": result}
    finally:
        await client.close()

@app.post("/api/v1/gmgn-v2/smart-money-dashboard")
async def gmgn_smart_money_dashboard(req: GMGNScanRequest):
    """What smart money is doing RIGHT NOW."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        result = await client.smart_money_dashboard(req.chain, limit=20)
        return {"status": "ok", "data": result}
    finally:
        await client.close()

@app.post("/api/v1/gmgn-v2/wallet-intelligence")
async def gmgn_wallet_intelligence(req: GMGNWalletRequest):
    """Full GMGN wallet intelligence with tags + P&L."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        result = await client.wallet_intelligence(req.chain, req.wallet_address)
        return {"status": "ok", "data": result}
    finally:
        await client.close()

@app.get("/api/v1/gmgn-v2/trending")
async def gmgn_trending_v2(chain: str = "sol", interval: str = "24h"):
    """Get trending tokens with full safety scores."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        tokens = await client.get_trending(chain, interval=interval, limit=50)
        return {"status": "ok", "data": {
            "tokens": [
                {
                    "address": t.address,
                    "symbol": t.symbol,
                    "name": t.name,
                    "price": t.price_usd,
                    "market_cap": t.market_cap,
                    "volume_24h": t.volume_24h,
                    "change_24h": t.price_change_24h,
                    "rug_ratio": t.rug_ratio,
                    "smart_degen": t.smart_degen_count,
                    "renowned": t.renowned_count,
                    "hot_level": t.hot_level,
                    "holders": t.holder_count,
                    "top_10_rate": t.top_10_holder_rate,
                    "dev_hold": t.dev_team_hold_rate,
                    "safety_score": t.safety_score,
                    "is_honeypot": t.is_honeypot,
                }
                for t in tokens[:50]
            ],
            "count": len(tokens),
        }}
    finally:
        await client.close()

@app.get("/api/v1/gmgn-v2/trenches")
async def gmgn_trenches(chain: str = "sol"):
    """Newly launched tokens from pump.fun, Raydium, etc."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        tokens = await client.get_trenches(chain, limit=50)
        return {"status": "ok", "data": {
            "tokens": [
                {
                    "address": t.address,
                    "symbol": t.symbol,
                    "name": t.name,
                    "price": t.price_usd,
                    "market_cap": t.market_cap,
                    "launchpad": t.launchpad,
                    "launch_time": t.launch_time.isoformat() if t.launch_time else None,
                    "rug_ratio": t.rug_ratio,
                    "smart_degen": t.smart_degen_count,
                    "holders": t.holder_count,
                    "safety_score": t.safety_score,
                }
                for t in tokens[:50]
            ],
            "count": len(tokens),
        }}
    finally:
        await client.close()

@app.post("/api/v1/gmgn-v2/token-security")
async def gmgn_token_security(req: GMGNScanRequest):
    """Full token security scan: honeypot, taxes, authorities, holders."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        sec = await client.get_token_security(req.chain, req.token_address)
        if not sec:
            return {"status": "error", "message": "Token not found or API error"}
        return {"status": "ok", "data": {
            "name": sec.name,
            "symbol": sec.symbol,
            "is_honeypot": sec.is_honeypot,
            "buy_tax": sec.buy_tax,
            "sell_tax": sec.sell_tax,
            "transfer_tax": sec.transfer_tax,
            "renounced_mint": sec.renounced_mint,
            "renounced_freeze": sec.renounced_freeze,
            "renounced_transfer": sec.renounced_transfer,
            "holder_count": sec.holder_count,
            "top_10_rate": sec.top_10_holder_rate,
            "dev_hold_rate": sec.dev_team_hold_rate,
            "liquidity_locked": sec.liquidity_locked,
            "contract_verified": sec.contract_verified,
            "rug_ratio": sec.rug_ratio,
            "safety_score": sec.safety_score,
            "risk_flags": sec.risk_flags,
        }}
    finally:
        await client.close()

@app.post("/api/v1/gmgn-v2/top-holders")
async def gmgn_top_holders(req: GMGNScanRequest):
    """Top holders with smart money tags."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        holders = await client.get_top_holders(req.chain, req.token_address, limit=20)
        return {"status": "ok", "data": [
            {
                "address": h.address,
                "balance_usd": h.balance_usd,
                "pct": h.pct_of_supply,
                "tag": h.tag,
                "is_contract": h.is_contract,
            }
            for h in holders
        ]}
    finally:
        await client.close()


# ═══════════════════════════════════════════════════════════════════════════
# GMGN QUOTE PREVIEW — Trade cost calculator (intelligence only)
# ═══════════════════════════════════════════════════════════════════════════

class GMGNQuoteRequest(BaseModel):
    chain: str = "sol"
    token_address: str
    amount_usd: float = 1000.0

@app.post("/api/v1/gmgn-v2/quote")
async def gmgn_quote_preview(req: GMGNQuoteRequest):
    """Get trade quote preview without executing. Intelligence only."""
    from app.gmgn_full_integration import get_gmgn_client
    client = get_gmgn_client()
    try:
        # Try to get price data from GMGN
        quote = await client.get_quote(
            chain=req.chain,
            from_wallet="preview",  # No real wallet — preview mode
            input_token=CHAIN_CONFIG.get(req.chain, {}).get("usdc", ""),
            output_token=req.token_address,
            amount=int(req.amount_usd * 1e6),  # USDC has 6 decimals
        )
        
        # If GMGN quote fails, return estimated preview
        if "error" in quote:
            # Fallback: use trending data for price estimation
            tokens = await client.get_trending(req.chain, limit=100)
            token_data = next((t for t in tokens if t.address == req.token_address), None)
            
            if token_data:
                price = token_data.price_usd
                if price > 0:
                    tokens_out = req.amount_usd / price
                    return {"status": "ok", "data": {
                        "token_out_amount": tokens_out,
                        "price": price,
                        "slippage": 0.5,  # Estimated
                        "route": "estimated",
                        "price_impact": min(5.0, req.amount_usd / max(token_data.volume_24h * 0.1, 1)),
                        "note": "Estimated from trending data. Use Jupiter for exact quote.",
                    }}
            
            return {"status": "ok", "data": {
                "token_out_amount": 0,
                "price": 0,
                "slippage": 0,
                "route": "unknown",
                "price_impact": 0,
                "note": f"Token not found on GMGN. Check {req.token_address} on Jupiter.",
            }}
        
        return {"status": "ok", "data": {
            "token_out_amount": quote.get("output_amount", 0),
            "price": quote.get("price", 0),
            "slippage": quote.get("slippage", 0),
            "route": quote.get("route", "unknown"),
            "price_impact": quote.get("price_impact", 0),
            "note": "Preview only. RMI does not execute trades.",
        }}
    finally:
        await client.close()


# ═══════════════════════════════════════════════════════════════════════════
# LOCAL AI CHAT — Lightweight instant assistant
# ═══════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """Local AI chatbot for instant crypto security answers."""
    from app.rmi_chat_service import get_chat_service
    service = get_chat_service()
    try:
        result = await service.ask(req.message, req.user_id)
        return {"status": "ok", **result}
    finally:
        await service.close()

@app.get("/chat/stats")
async def chat_stats():
    """Chat service statistics."""
    from app.rmi_chat_service import get_chat_service
    service = get_chat_service()
    return {"status": "ok", "data": service.get_stats()}


# ═══ Degen Security Scanner ═══
from app.degen_scan_endpoint import router as degen_scan_router
app.include_router(degen_scan_router)

# ═══ Content Syndication ═══
from app.content_syndicate import router as content_router
app.include_router(content_router)

# ═══ Airdrop Checker ═══
# from app.airdrop import router as airdrop_router
# app.include_router(airdrop_router)

# ═══ Rug Munch Intelligence Chat ═══
from app.rmi_intel_chat import router as intel_router
app.include_router(intel_router)

# ═══ Profile Management ═══
from app.routers.profile import router as profile_router
from app.routers.email import router as email_router
from app.routers.admin_control import router as admin_control_router
from app.routers.darkroom import router as darkroom_router
from app.routers.rag import router as rag_router
from app.routers.budget import router as budget_router
app.include_router(profile_router)
app.include_router(email_router)
app.include_router(admin_control_router)
app.include_router(darkroom_router)
app.include_router(rag_router)
app.include_router(budget_router)

# ═══════════════════════════════════════════════════════════════
# GAMIFICATION
# ═══════════════════════════════════════════════════════════════
from app.payments import payment_service, get_product_catalog
from app.mirror_publisher import mirror_publisher
from app.news_service import news_service
from app.gamification_service import (
    record_activity,
    get_user_gamification_profile,
    get_leaderboard,
    get_all_badges_with_progress,
)

class GamificationEventRequest(BaseModel):
    activity_type: str = Field(..., description="Type of activity: wallet_scan, post_created, comment_created, upvote_given, upvote_received, wallet_connected, report_verified, alpha_verified, login")
    metadata: Optional[Dict[str, Any]] = Field(default=None)

@app.get("/api/v1/gamification/profile")
async def gamification_profile(user: Dict[str, Any] = Depends(require_auth)):
    """Get current user's gamification profile."""
    user_id = user.get("id")
    return await get_user_gamification_profile(user_id)

@app.get("/api/v1/gamification/leaderboard")
async def gamification_leaderboard(
    category: str = "xp",
    limit: int = 50,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get global leaderboard by category."""
    return {
        "category": category,
        "leaderboard": await get_leaderboard(category, limit=limit),
    }

@app.post("/api/v1/gamification/event")
async def gamification_event(req: GamificationEventRequest, user: Dict[str, Any] = Depends(require_auth)):
    """Record a gamification activity event."""
    user_id = user.get("id")
    result = await record_activity(user_id, req.activity_type, req.metadata)
    return result

@app.get("/api/v1/gamification/badges")
async def gamification_badges(user: Dict[str, Any] = Depends(require_auth)):
    """Get all badges with user's progress."""
    user_id = user.get("id")
    return {
        "badges": await get_all_badges_with_progress(user_id),
    }

# ═══════════════════════════════════════════════════════════
# TELEGRAM BOT API
# ═══════════════════════════════════════════════════════════

class TelegramUserRegister(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TelegramScanRecord(BaseModel):
    telegram_id: int
    scan_type: str
    token: str
    result: Dict[str, Any] = {}

class TelegramPaymentConfirm(BaseModel):
    telegram_id: int
    payload: str
    amount: int
    currency: str
    provider: str

@app.post("/api/v1/telegram/user/register")
async def telegram_user_register(req: TelegramUserRegister):
    """Register or update a Telegram user."""
    from app.telegram_service import get_or_create_telegram_user
    user = get_or_create_telegram_user(
        telegram_id=req.telegram_id,
        username=req.username,
        first_name=req.first_name,
        last_name=req.last_name,
    )
    return {"success": True, "user": user}

@app.get("/api/v1/telegram/user/{telegram_id}")
async def telegram_user_status(telegram_id: int):
    """Get user's tier and scan usage."""
    from app.telegram_service import get_user_status
    return get_user_status(telegram_id)

@app.post("/api/v1/telegram/scan/record")
async def telegram_scan_record(req: TelegramScanRecord):
    """Record a scan and award XP."""
    from app.telegram_service import record_scan
    return record_scan(req.telegram_id, req.scan_type, req.token, req.result)

@app.post("/api/v1/telegram/payment/confirm")
async def telegram_payment_confirm(req: TelegramPaymentConfirm):
    """Confirm payment and update tier/scans."""
    from app.telegram_service import process_payment
    return process_payment(
        req.telegram_id, req.payload, req.amount, req.currency, req.provider
    )

@app.get("/api/v1/telegram/scans/{telegram_id}")
async def telegram_scan_history(telegram_id: int, limit: int = 50):
    """Get scan history for a Telegram user."""
    from app.telegram_service import get_scan_history
    return {"scans": get_scan_history(telegram_id, limit)}

@app.get("/api/v1/telegram/leaderboard")
async def telegram_leaderboard(limit: int = 20):
    """Get top scanners leaderboard."""
    from app.telegram_service import get_leaderboard
    return {"leaderboard": get_leaderboard(limit)}

# ═══════════════════════════════════════════════════════════
# SCAN CARD GENERATOR
# ═══════════════════════════════════════════════════════════

class ScanCardRequest(BaseModel):
    token: str
    chain: str = "SOL"
    scan_type: str = "SECURITY SCAN"
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    verdict: Optional[str] = None
    red_flags: Optional[List[str]] = None
    ai_consensus: Optional[str] = None


@app.post("/api/v1/scan-card")
async def generate_scan_card_endpoint(req: ScanCardRequest):
    """Generate a shareable scan card PNG image."""
    try:
        from app.scan_card_service import generate_scan_card_base64
        b64 = generate_scan_card_base64(
            token=req.token,
            chain=req.chain,
            scan_type=req.scan_type,
            risk_score=req.risk_score,
            risk_level=req.risk_level,
            verdict=req.verdict,
            red_flags=req.red_flags or [],
            ai_consensus=req.ai_consensus,
        )
        return {"success": True, "image": b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Card generation failed: {e}")


# ═══════════════════════════════════════════════════════════
# TELEGRAM MINI APP — STARS PAYMENT
# ═════════════════════════════════════════════════════════==

class StarsInvoiceRequest(BaseModel):
    telegram_id: int
    title: str
    description: str
    payload: str
    amount: int  # amount in smallest units (1 Star = 1)


@app.post("/api/v1/telegram/stars-invoice")
async def create_stars_invoice(req: StarsInvoiceRequest):
    """Generate a Telegram Stars invoice link via Bot API."""
    import os, aiohttp
    bot_token = os.getenv("BOT_TOKEN", "")
    if not bot_token:
        raise HTTPException(status_code=503, detail="Bot token not configured")

    api_url = f"https://api.telegram.org/bot{bot_token}/createInvoiceLink"
    body = {
        "title": req.title,
        "description": req.description,
        "payload": req.payload,
        "provider_token": "",  # Empty for Stars
        "currency": "XTR",
        "prices": [{"label": req.title, "amount": req.amount}],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=body, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                data = await resp.json()
                if data.get("ok"):
                    return {"success": True, "invoice_url": data["result"]["invoice_link"]}
                return {"success": False, "error": data.get("description", "Unknown error")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invoice creation failed: {e}")


# ═══════════════════════════════════════════════════════════
# PAYMENTS & SUBSCRIPTIONS
# ═══════════════════════════════════════════════════════════

class PaymentChargeRequest(BaseModel):
    product_id: str
    metadata: dict = {}
    redirect_url: Optional[str] = None
    cancel_url: Optional[str] = None

class MirrorPublishRequest(BaseModel):
    title: str
    body: str
    tags: Optional[list] = None
    cover_image_url: Optional[str] = None

@app.get("/api/v1/payments/products")
async def list_products():
    """Get all available products for purchase."""
    return {"products": get_product_catalog(), "demo_mode": payment_service.demo_mode}

@app.post("/api/v1/payments/charge")
async def create_payment_charge(req: PaymentChargeRequest):
    """Create a Coinbase Commerce charge (or demo charge)."""
    result = await payment_service.create_charge(
        product_id=req.product_id,
        metadata=req.metadata,
        redirect_url=req.redirect_url,
        cancel_url=req.cancel_url,
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 500), detail=result["error"])
    return result["data"]

@app.get("/api/v1/payments/charge/{charge_id}")
async def get_payment_charge(charge_id: str):
    """Get charge status."""
    result = await payment_service.get_charge(charge_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 500), detail=result["error"])
    return result["data"]

@app.post("/api/v1/payments/webhook")
async def payment_webhook(request: Request):
    """Coinbase Commerce webhook handler."""
    payload = await request.body()
    signature = request.headers.get("X-CC-Webhook-Signature", "")
    
    if not payment_service.verify_webhook(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    event = json.loads(payload)
    action = payment_service.handle_webhook(event)
    
    # TODO: Fulfill orders, upgrade tiers, send confirmations
    # This would connect to Supabase to update user records
    return {"received": True, "action": action}

# ═══════════════════════════════════════════════════════════
# NEWS AGGREGATION
# ═══════════════════════════════════════════════════════════

@app.get("/api/v1/news")
async def get_news(limit: int = 50):
    """Get aggregated crypto news from all sources."""
    news = await news_service.get_all_news(limit=limit)
    return {"news": news, "count": len(news), "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1/news/headlines")
async def get_headlines(count: int = 5):
    """Get top headlines for front page."""
    headlines = await news_service.get_top_headlines(count=count)
    return {"headlines": headlines, "count": len(headlines)}

# ═══════════════════════════════════════════════════════════
# MIRROR.XYZ PUBLISHING
# ═════════════════════════════════════════════════════════==

@app.post("/api/v1/newsletter/mirror/publish")
async def publish_to_mirror(req: MirrorPublishRequest):
    """Publish a newsletter article to Mirror.xyz."""
    result = await mirror_publisher.publish_article(
        title=req.title,
        body=req.body,
        tags=req.tags,
        cover_image_url=req.cover_image_url,
    )
    return result

# ═══ Static Frontend (SPA) ═══
app.mount("/", StaticFiles(directory="static"), name="static")

@app.exception_handler(StarletteHTTPException)
async def spa_exception_handler(request: Request, exc: StarletteHTTPException):
    """Serve index.html for SPA routes; preserve API 404s as JSON."""
    if exc.status_code == 404 and not request.url.path.startswith(("/api/", "/docs", "/openapi.json", "/redoc", "/health")):
        return FileResponse("static/index.html")
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

# ═══════════════════════════════════════════════════════════════
# AI ROUTER ENDPOINTS
# ═══════════════════════════════════════════════════════════════

class AICompleteRequest(BaseModel):
    prompt: str
    tier: str = Field(default="T2", pattern="^(T0|T1|T2|T3|T4)$")
    model: Optional[str] = None
    max_tokens: int = Field(default=1024, ge=1, le=8192)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class AICompleteResponse(BaseModel):
    success: bool
    response: str
    model_used: str
    provider: str
    cost_estimate: float
    latency_ms: int

class AIScamDetectRequest(BaseModel):
    text: str
    contract_address: Optional[str] = None
    chain: str = Field(default="solana")

class AISummarizeRequest(BaseModel):
    text: str
    max_length: int = Field(default=200, ge=50, le=2000)

class AIAnalyzeWalletRequest(BaseModel):
    address: str
    chain: str = Field(default="solana")
    context: Optional[str] = None

class AIAnalyzeWalletResponse(BaseModel):
    success: bool
    analysis: str
    wallet_data: Dict[str, Any]
    model_used: str
    provider: str
    latency_ms: int

class AIProviderStatus(BaseModel):
    name: str
    healthy: bool
    rpm_used: int
    rpm_limit: int
    avg_latency_ms: float
    consecutive_errors: int
    has_key: bool
    score: float
    models: List[str]

@app.post("/api/v1/ai/complete", response_model=AICompleteResponse)
async def ai_complete(req: AICompleteRequest):
    """General AI completion routed through the AI Router."""
    try:
        messages = [{"role": "user", "content": req.prompt}]
        result = await ai_router.chat_completion(
            messages=messages,
            model=req.model,
            tier=req.tier,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            timeout=45.0,
        )
        if "error" in result:
            raise HTTPException(status_code=503, detail=f"AI provider error: {result['error']}")

        content = result.get("content", "")
        model_used = result.get("model", req.model or "")
        provider = result.get("_provider", "unknown")
        latency_ms = int(result.get("_latency_ms", 0))

        # Rough cost estimate based on tier
        tier_config = MODEL_TIERS.get(req.tier, MODEL_TIERS["T2"])
        cost_per_1k = tier_config.get("max_cost_per_1k", 0.005)
        # Estimate ~1.5x prompt tokens for output
        cost_estimate = (req.max_tokens / 1000) * cost_per_1k * 0.7

        return AICompleteResponse(
            success=True,
            response=content,
            model_used=model_used,
            provider=provider,
            cost_estimate=round(cost_estimate, 6),
            latency_ms=latency_ms,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI complete error: {e}")
        raise HTTPException(status_code=500, detail=f"AI completion failed: {str(e)}")

@app.post("/api/v1/ai/scam-detect")
async def ai_scam_detect(req: AIScamDetectRequest):
    """AI-powered scam detection analysis."""
    try:
        system_prompt = (
            "You are an expert blockchain security analyst. Analyze the following content for scam indicators. "
            "Return a structured JSON-like assessment with these keys: risk_score (0-100), risk_level (LOW/MEDIUM/HIGH/CRITICAL), "
            "indicators (list of suspicious signals), explanation (concise reasoning), and recommendations (list of actions). "
            "Be precise and evidence-based."
        )
        user_content = f"Text to analyze: {req.text}\nChain: {req.chain}"
        if req.contract_address:
            user_content += f"\nContract Address: {req.contract_address}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        result = await ai_router.chat_completion(
            messages=messages,
            tier="T1",
            temperature=0.3,
            max_tokens=2048,
            timeout=45.0,
        )
        if "error" in result:
            raise HTTPException(status_code=503, detail=f"AI provider error: {result['error']}")

        return {
            "success": True,
            "assessment": result.get("content", ""),
            "model_used": result.get("model", ""),
            "provider": result.get("_provider", "unknown"),
            "latency_ms": int(result.get("_latency_ms", 0)),
            "chain": req.chain,
            "contract_address": req.contract_address,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scam detect error: {e}")
        raise HTTPException(status_code=500, detail=f"Scam detection failed: {str(e)}")

@app.post("/api/v1/ai/summarize")
async def ai_summarize(req: AISummarizeRequest):
    """AI-powered text summarization."""
    try:
        system_prompt = (
            f"You are a concise summarization assistant. Summarize the following text in at most {req.max_length} words. "
            "Preserve key facts, names, numbers, and conclusions. Output only the summary, no preamble."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.text},
        ]

        result = await ai_router.chat_completion(
            messages=messages,
            tier="T2",
            temperature=0.5,
            max_tokens=min(req.max_length * 3, 2048),
            timeout=30.0,
        )
        if "error" in result:
            raise HTTPException(status_code=503, detail=f"AI provider error: {result['error']}")

        return {
            "success": True,
            "summary": result.get("content", "").strip(),
            "model_used": result.get("model", ""),
            "provider": result.get("_provider", "unknown"),
            "latency_ms": int(result.get("_latency_ms", 0)),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/api/v1/ai/analyze-wallet", response_model=AIAnalyzeWalletResponse)
async def ai_analyze_wallet(req: AIAnalyzeWalletRequest):
    """Fetch wallet data and run AI narrative analysis."""
    wallet_data: Dict[str, Any] = {"address": req.address, "chain": req.chain}

    # Fetch on-chain data via existing patterns
    if req.chain == "solana" and settings.HELIUS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"https://api.helius.xyz/v0/addresses/?api-key={settings.HELIUS_API_KEY}&address={req.address}"
                )
                if resp.status_code == 200:
                    wallet_data["helius"] = resp.json()
        except Exception as e:
            wallet_data["helius_error"] = str(e)

    if settings.ARKHAM_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.arkhamintelligence.com/intelligence/address",
                    headers={"API-Key": settings.ARKHAM_API_KEY},
                    json={"address": req.address, "chain": req.chain}
                )
                if resp.status_code == 200:
                    wallet_data["arkham"] = resp.json()
        except Exception as e:
            wallet_data["arkham_error"] = str(e)

    # If address looks like a token, run a Birdeye security scan
    if len(req.address) >= 32:
        try:
            from app.birdeye_client import BirdeyeClient
            client = BirdeyeClient()
            try:
                scan = await client.security_scan(req.address)
                if "error" not in scan:
                    wallet_data["birdeye"] = scan
            finally:
                await client.close()
        except Exception as e:
            wallet_data["birdeye_error"] = str(e)

    try:
        system_prompt = (
            "You are a blockchain intelligence analyst. Given wallet/token data, produce a narrative analysis. "
            "Cover: overall risk level, notable behaviors, associations, and actionable insights. "
            "Be concise but thorough. If data is limited, state what is missing."
        )
        user_prompt = f"Address: {req.address}\nChain: {req.chain}\nData:\n{json.dumps(wallet_data, indent=2, default=str)}"
        if req.context:
            user_prompt += f"\n\nAdditional Context: {req.context}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result = await ai_router.chat_completion(
            messages=messages,
            tier="T1",
            temperature=0.6,
            max_tokens=2048,
            timeout=45.0,
        )
        if "error" in result:
            raise HTTPException(status_code=503, detail=f"AI provider error: {result['error']}")

        return AIAnalyzeWalletResponse(
            success=True,
            analysis=result.get("content", ""),
            wallet_data=wallet_data,
            model_used=result.get("model", ""),
            provider=result.get("_provider", "unknown"),
            latency_ms=int(result.get("_latency_ms", 0)),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze wallet error: {e}")
        raise HTTPException(status_code=500, detail=f"Wallet analysis failed: {str(e)}")

@app.get("/api/v1/ai/providers")
async def ai_providers():
    """List all AI providers and their status."""
    status = ai_router.get_status()
    providers = []
    for name, config in PROVIDERS.items():
        state = status["providers"].get(name, {})
        providers.append({
            "name": name,
            "url": config.get("url", ""),
            "models": config.get("models", []),
            "rpm_limit": config.get("rpm", 0),
            "healthy": state.get("healthy", False),
            "rpm_used": state.get("rpm_used", 0),
            "avg_latency_ms": round(state.get("avg_latency_ms", 0), 2),
            "consecutive_errors": state.get("consecutive_errors", 0),
            "has_key": state.get("has_key", False),
            "score": round(state.get("score", 0), 2),
            "available": state.get("has_key", False) and state.get("healthy", False),
        })
    return {
        "providers": providers,
        "tiers": MODEL_TIERS,
        "total": len(providers),
        "available": sum(1 for p in providers if p["available"]),
    }

@app.get("/api/v1/ai/usage")
async def ai_usage():
    """Return mock usage stats for AI providers."""
    status = ai_router.get_status()
    provider_stats = []
    total_requests = 0
    total_cost = 0.0
    for name, state in status["providers"].items():
        reqs = state.get("request_count", 0)
        total_requests += reqs
        # Rough mock cost: $0.005 per request average
        cost = reqs * 0.005
        total_cost += cost
        provider_stats.append({
            "provider": name,
            "requests": reqs,
            "estimated_cost_usd": round(cost, 4),
            "avg_latency_ms": round(state.get("avg_latency_ms", 0), 2),
        })
    return {
        "total_requests": total_requests,
        "total_estimated_cost_usd": round(total_cost, 4),
        "by_provider": provider_stats,
        "period": "all_time",
        "timestamp": datetime.utcnow().isoformat(),
    }

# ═══════════════════════════════════════════════════════════════
# SPECTER — OSINT & Social Forensics Agent
# Powered by Together AI (different company, free tier)
# ═══════════════════════════════════════════════════════════════

class OSINTInvestigationRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200)
    website: Optional[str] = Field(None, description="Project website URL")
    twitter: Optional[str] = Field(None, description="Twitter/X handle (with or without @)")

class OSINTWebsiteRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze")

@app.post("/api/v1/osint/investigate")
async def osint_investigate(req: OSINTInvestigationRequest):
    """👻 SPECTER: Full OSINT investigation of a crypto project"""
    try:
        from app.osint_service import get_specter
        specter = await get_specter()
        result = await specter.investigate_project(
            project_name=req.project_name,
            website=req.website,
            twitter=req.twitter
        )
        await specter.close()
        return {
            "success": True,
            "agent": "SPECTER",
            "model": "together-llama-3.3-70b",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SPECTER investigation failed: {str(e)}")

@app.post("/api/v1/osint/website")
async def osint_website(req: OSINTWebsiteRequest):
    """👻 SPECTER: Forensic website analysis"""
    try:
        from app.osint_service import get_specter
        specter = await get_specter()
        result = await specter.analyze_website_risk(req.url)
        await specter.close()
        return {
            "success": True,
            "agent": "SPECTER",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SPECTER website analysis failed: {str(e)}")

@app.get("/api/v1/osint/search")
async def osint_search(q: str, count: int = 10):
    """👻 SPECTER: Brave Search web intelligence"""
    try:
        from app.osint_service import get_specter
        specter = await get_specter()
        results = await specter.brave_search(q, count=min(count, 20))
        await specter.close()
        return {
            "success": True,
            "agent": "SPECTER",
            "query": q,
            "results": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SPECTER search failed: {str(e)}")

@app.get("/api/v1/agents/specter")
async def specter_status():
    """SPECTER agent status and capabilities"""
    return {
        "agent": "SPECTER",
        "emoji": "👻",
        "role": "OSINT & Social Forensics",
        "provider": "Together AI",
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "mistralai/Mixtral-8x22B-Instruct-v0.1"],
        "free_credits": "$5",
        "capabilities": [
            "brave_web_search",
            "website_forensics",
            "firecrawl_scraping",
            "dev_identity_hunting",
            "social_media_analysis",
            "litepaper_plagiarism_detection",
            "sockpuppet_detection"
        ],
        "integrations": {
            "brave_search": bool(os.getenv("BRAVE_API_KEY")),
            "firecrawl": bool(os.getenv("FIRECRAWL_API_KEY")),
            "apify": bool(os.getenv("APIFY_API_KEY")),
            "together_ai": bool(os.getenv("TOGETHER_API_KEY")),
        },
        "status": "online"
    }


# ── Agent Management Endpoints ──
@app.get("/api/v1/admin/agents/status")
async def agent_status(request: Request):
    try:
        from app.agents.orchestrator import get_agent_status
        return {"agents": get_agent_status()}
    except Exception as e:
        return {"agents": {}, "error": str(e)}

@app.post("/api/v1/admin/agents/{name}/restart")
async def restart_agent(name: str, request: Request):
    try:
        from app.agents.orchestrator import run_agent
        run_agent(name)
        return {"success": True, "agent": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

