#!/usr/bin/env python3
"""
🎯 RMI Unified Bot Orchestrator
================================
FastAPI service that coordinates the 8-bot task force.

Endpoints:
  POST /orchestrator/task          — Dispatch task to a bot
  POST /orchestrator/swarm-task    — Dispatch to swarm with consensus
  GET  /orchestrator/bots          — List all bot identities
  GET  /orchestrator/bots/{id}     — Get specific bot details
  GET  /orchestrator/capabilities  — List all extension capabilities
  GET  /orchestrator/status        — Health + load status
  GET  /orchestrator/extensions    — Extension load status
  POST /orchestrator/alert         — Broadcast alert via Herald

Architecture:
  Client (Telegram/Web) → Orchestrator → Bot Identity → AI Model (Swarm)
                                              ↓
                                       Extension Plugins
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from pathlib import Path

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "swarm"))
sys.path.insert(0, str(PROJECT_ROOT / "bots"))
sys.path.insert(0, str(PROJECT_ROOT / "bots" / "extensions"))
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from orchestrator.bot_identities import (
    RMI_BOT_SWARM, BotRole, get_bot_by_id, get_bot_by_role,
    get_bots_by_specialty, get_all_enabled_bots
)
from orchestrator.extension_plugins import ExtensionPluginManager

# Optional: import swarm orchestrator if available
try:
    from ai_swarm_orchestrator import AISwarmOrchestrator
    SWARM_AVAILABLE = True
except ImportError as e:
    SWARM_AVAILABLE = False
    logging.warning(f"Swarm orchestrator not available: {e}")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("orchestrator")


# ═══════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════

class TaskRequest(BaseModel):
    task_type: str = Field(..., description="Type of task: scan, analyze, predict, audit, alert, etc.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task-specific data")
    target_bot: Optional[str] = Field(None, description="Specific bot ID, or auto-routed if omitted")
    target_role: Optional[str] = Field(None, description="Bot role: investigator, sentry, oracle, etc.")
    require_consensus: bool = Field(False, description="Require swarm consensus for this task")
    priority: str = Field("normal", description="low, normal, high, critical")
    source: str = Field("api", description="Source of request: telegram, web, internal")


class TaskResponse(BaseModel):
    success: bool
    task_id: str
    bot_id: Optional[str] = None
    bot_name: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None
    timestamp: str


class AlertRequest(BaseModel):
    severity: str = Field(..., description="critical, high, medium, low")
    title: str
    description: str
    contract_address: Optional[str] = None
    chain: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    channels: List[str] = Field(default=["telegram"], description="telegram, discord, webhook, twitter")


class BotStatusResponse(BaseModel):
    id: str
    name: str
    role: str
    emoji: str
    enabled: bool
    specialties: List[str]
    preferred_model: str
    fallback_model: str
    extensions: List[str]
    capabilities: List[str]


# ═══════════════════════════════════════════════════════════════════
# ORCHESTRATOR STATE
# ═══════════════════════════════════════════════════════════════════

class OrchestratorState:
    def __init__(self):
        self.plugins = ExtensionPluginManager()
        self.swarm: Optional[Any] = None
        self.task_counter = 0
        self.task_history: List[Dict] = []
        self.started_at = datetime.now(timezone.utc).isoformat()

        if SWARM_AVAILABLE:
            try:
                self.swarm = AISwarmOrchestrator()
                logger.info("🐝 Swarm orchestrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize swarm: {e}")

    def next_task_id(self) -> str:
        self.task_counter += 1
        return f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.task_counter:04d}"


state = OrchestratorState()


# ═══════════════════════════════════════════════════════════════════
# FASTAPI LIFESPAN
# ═══════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 RMI Bot Orchestrator starting...")
    logger.info(f"   Bots: {len(get_all_enabled_bots())}")
    logger.info(f"   Extensions: {len(state.plugins.EXTENSION_REGISTRY)}")
    logger.info(f"   Swarm: {'✅' if state.swarm else '❌'}")
    yield
    logger.info("👋 RMI Bot Orchestrator shutting down...")


app = FastAPI(
    title="RMI Bot Orchestrator",
    description="Unified 8-bot task force coordinator for Rug Munch Intelligence",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "orchestrator": "running",
        "swarm_available": SWARM_AVAILABLE and state.swarm is not None,
        "bots_active": len(get_all_enabled_bots()),
        "extensions_loaded": sum(1 for v in state.plugins.get_load_status().values() if v),
        "extensions_total": len(state.plugins.EXTENSION_REGISTRY),
        "uptime_since": state.started_at,
    }


@app.get("/orchestrator/status")
async def status():
    load_status = state.plugins.get_load_status()
    return {
        "orchestrator": {
            "version": "2.0.0",
            "started_at": state.started_at,
            "tasks_processed": state.task_counter,
        },
        "bots": {
            "total": len(RMI_BOT_SWARM),
            "enabled": len(get_all_enabled_bots()),
            "identities": [{"id": b.id, "name": b.name, "role": b.role.value, "emoji": b.emoji} for b in RMI_BOT_SWARM],
        },
        "extensions": {
            "total": len(state.plugins.EXTENSION_REGISTRY),
            "loaded": sum(1 for v in load_status.values() if v),
            "failed": sum(1 for v in load_status.values() if not v),
            "details": load_status,
        },
        "swarm": {
            "available": SWARM_AVAILABLE and state.swarm is not None,
            "bots": len(state.swarm.bots) if state.swarm else 0,
        } if state.swarm else {"available": False},
    }


# ═══════════════════════════════════════════════════════════════════
# BOT IDENTITIES
# ═══════════════════════════════════════════════════════════════════

@app.get("/orchestrator/bots", response_model=List[BotStatusResponse])
async def list_bots():
    results = []
    for bot in RMI_BOT_SWARM:
        caps = state.plugins.get_capabilities_for_role(bot.role.value)
        results.append(BotStatusResponse(
            id=bot.id,
            name=bot.name,
            role=bot.role.value,
            emoji=bot.emoji,
            enabled=bot.enabled,
            specialties=bot.specialties,
            preferred_model=bot.preferred_model,
            fallback_model=bot.fallback_model,
            extensions=bot.extensions,
            capabilities=caps,
        ))
    return results


@app.get("/orchestrator/bots/{bot_id}")
async def get_bot(bot_id: str):
    bot = get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    return {
        "id": bot.id,
        "name": bot.name,
        "role": bot.role.value,
        "tagline": bot.tagline,
        "emoji": bot.emoji,
        "personality": bot.personality,
        "specialties": bot.specialties,
        "preferred_model": bot.preferred_model,
        "fallback_model": bot.fallback_model,
        "extensions": bot.extensions,
        "capabilities": state.plugins.get_capabilities_for_role(bot.role.value),
        "system_prompt_preview": bot.system_prompt[:200] + "...",
    }


@app.get("/orchestrator/roles/{role}")
async def get_bots_by_role(role: str):
    try:
        bot_role = BotRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    bot = get_bot_by_role(bot_role)
    if not bot:
        raise HTTPException(status_code=404, detail=f"No bot found for role {role}")
    return {
        "role": role,
        "bot": {"id": bot.id, "name": bot.name, "emoji": bot.emoji},
        "capabilities": state.plugins.get_capabilities_for_role(role),
    }


# ═══════════════════════════════════════════════════════════════════
# CAPABILITIES & EXTENSIONS
# ═══════════════════════════════════════════════════════════════════

@app.get("/orchestrator/capabilities")
async def list_capabilities():
    return state.plugins.list_all_capabilities()


@app.get("/orchestrator/extensions")
async def list_extensions():
    return {
        "extensions": state.plugins.get_load_status(),
        "registry": {
            name: {
                "description": meta["description"],
                "capabilities": meta["capabilities"],
                "roles": meta["roles"],
            }
            for name, meta in state.plugins.EXTENSION_REGISTRY.items()
        },
    }


# ═══════════════════════════════════════════════════════════════════
# TASK DISPATCH
# ═══════════════════════════════════════════════════════════════════

@app.post("/orchestrator/task", response_model=TaskResponse)
async def dispatch_task(req: TaskRequest, background_tasks: BackgroundTasks):
    """Dispatch a task to the appropriate bot."""
    import time
    start = time.time()
    task_id = state.next_task_id()

    # Resolve target bot
    bot = None
    if req.target_bot:
        bot = get_bot_by_id(req.target_bot)
    elif req.target_role:
        try:
            role = BotRole(req.target_role)
            bot = get_bot_by_role(role)
        except ValueError:
            pass
    else:
        # Auto-route by task_type
        bot = _auto_route_task(req.task_type)

    if not bot:
        return TaskResponse(
            success=False,
            task_id=task_id,
            error=f"No bot found for task_type={req.task_type}, target={req.target_bot or req.target_role}",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # Build result
    result = {
        "task_id": task_id,
        "task_type": req.task_type,
        "bot_id": bot.id,
        "bot_name": bot.name,
        "bot_emoji": bot.emoji,
        "role": bot.role.value,
        "payload_received": req.payload,
        "priority": req.priority,
        "source": req.source,
        "capabilities_available": state.plugins.get_capabilities_for_role(bot.role.value),
        "extensions": bot.extensions,
    }

    # If swarm is available, attempt AI processing
    if state.swarm and SWARM_AVAILABLE:
        try:
            swarm_result = await state.swarm.assign_task(
                task_type=req.task_type,
                task_data={"prompt": str(req.payload), **req.payload},
                require_consensus=req.require_consensus,
            )
            result["swarm_result"] = {
                "success": swarm_result.get("success", False),
                "bot_used": swarm_result.get("bot"),
                "text": swarm_result.get("result", {}).get("text", "")[:500] if swarm_result.get("result") else None,
            }
        except Exception as e:
            logger.warning(f"Swarm task failed: {e}")
            result["swarm_error"] = str(e)

    elapsed = int((time.time() - start) * 1000)

    # Log task
    state.task_history.append({
        "task_id": task_id,
        "bot_id": bot.id,
        "task_type": req.task_type,
        "timestamp": datetime.utcnow().isoformat(),
        "success": True,
    })

    return TaskResponse(
        success=True,
        task_id=task_id,
        bot_id=bot.id,
        bot_name=bot.name,
        result=result,
        processing_time_ms=elapsed,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/orchestrator/swarm-task")
async def dispatch_swarm_task(req: TaskRequest):
    """Dispatch a task requiring swarm consensus."""
    if not state.swarm or not SWARM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Swarm orchestrator not available")

    task_id = state.next_task_id()
    try:
        result = await state.swarm.assign_task(
            task_type=req.task_type,
            task_data={"prompt": str(req.payload), **req.payload},
            require_consensus=True,
        )
        return {
            "task_id": task_id,
            "success": result.get("success", False),
            "bot": result.get("bot"),
            "result": result.get("result"),
            "code": result.get("code") if req.task_type == "code_generation" else None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Swarm task failed: {e}")


def _auto_route_task(task_type: str) -> Optional[Any]:
    """Auto-select bot based on task type keywords."""
    routing = {
        "scan": BotRole.SENTRY,
        "analyze": BotRole.INVESTIGATOR,
        "trace": BotRole.INVESTIGATOR,
        "predict": BotRole.ORACLE,
        "forecast": BotRole.ORACLE,
        "audit": BotRole.AUDITOR,
        "code": BotRole.AUDITOR,
        "alert": BotRole.HERALD,
        "broadcast": BotRole.HERALD,
        "report": BotRole.ARCHIVIST,
        "social": BotRole.VANGUARD,
        "sentiment": BotRole.VANGUARD,
        "threat": BotRole.WARDEN,
        "bundling": BotRole.WARDEN,
        "vampire": BotRole.WARDEN,
        # Telegram bot task types — route to most capable bot
        "portfolio": BotRole.ORACLE,      # Oracle tracks market positions
        "whale": BotRole.VANGUARD,        # Vanguard monitors smart money
        "holder": BotRole.VANGUARD,       # Vanguard analyzes distribution
        "rug_pull": BotRole.WARDEN,       # Warden detects threats
    }
    task_lower = task_type.lower()
    for keyword, role in routing.items():
        if keyword in task_lower:
            return get_bot_by_role(role)
    # Default to Investigator
    return get_bot_by_role(BotRole.INVESTIGATOR)


# ═══════════════════════════════════════════════════════════════════
# ALERT BROADCAST
# ═══════════════════════════════════════════════════════════════════

@app.post("/orchestrator/alert")
async def broadcast_alert(req: AlertRequest):
    """Broadcast an alert through The Herald."""
    herald = get_bot_by_role(BotRole.HERALD)
    if not herald:
        raise HTTPException(status_code=503, detail="Herald bot not available")

    alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    # In production, this would trigger actual Telegram/webhook/Twitter sends
    result = {
        "alert_id": alert_id,
        "herald": herald.name,
        "severity": req.severity,
        "title": req.title,
        "channels_targeted": req.channels,
        "status": "queued",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # TODO: Integrate with actual alert_router and telegram_bridge extensions
    logger.info(f"🚨 ALERT [{req.severity}] {req.title} → channels: {req.channels}")

    return result


# ═══════════════════════════════════════════════════════════════════
# TASK HISTORY
# ═══════════════════════════════════════════════════════════════════

@app.get("/orchestrator/tasks")
async def list_tasks(limit: int = 50):
    return {
        "tasks": state.task_history[-limit:],
        "total": len(state.task_history),
    }


# ═══════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("ORCHESTRATOR_PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port)
