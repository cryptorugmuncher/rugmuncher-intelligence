"""
RMI Backend Control Router
==========================
Admin endpoints for system monitoring, service control, logs,
database management, bot configuration, and alerts.
"""

import os
import sys
import json
import re
import asyncio
import psutil
import socket
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin-control"])

# ── Auth helper ──
from app.db_client import get_db, RmiDatabase

async def _verify_admin(request: Request):
    settings = sys.modules.get("__main__")
    if hasattr(settings, "Settings"):
        admin_key = getattr(settings, "settings", None)
        if admin_key:
            admin_key = getattr(admin_key, "ADMIN_API_KEY", "dev-key-change-me")
        else:
            admin_key = "dev-key-change-me"
    else:
        admin_key = os.getenv("ADMIN_API_KEY", "dev-key-change-me")

    key = request.headers.get("X-Admin-Key", "")
    if key != admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True

# ═══════════════════════════════════════════════════════════════
# SYSTEM MONITORING
# ═══════════════════════════════════════════════════════════════

@router.get("/system")
async def admin_system(request: Request, _=Depends(_verify_admin)):
    """Get real-time system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net_io = psutil.net_io_counters()
        boot_time = psutil.boot_time()
        uptime_seconds = int(datetime.now().timestamp() - boot_time)

        # Process info for the backend itself
        backend_pid = os.getpid()
        backend_proc = psutil.Process(backend_pid)
        backend_memory_mb = backend_proc.memory_info().rss / (1024 * 1024)
        backend_cpu = backend_proc.cpu_percent(interval=0.2)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent,
                "used_gb": round(memory.used / (1024**3), 2),
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": round(disk.used / disk.total * 100, 1),
            },
            "network": {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            },
            "uptime": {
                "seconds": uptime_seconds,
                "formatted": str(timedelta(seconds=uptime_seconds)),
            },
            "backend_process": {
                "pid": backend_pid,
                "memory_mb": round(backend_memory_mb, 2),
                "cpu_percent": backend_cpu,
                "threads": backend_proc.num_threads(),
            },
        }
    except Exception as e:
        logger.error(f"[Admin] System stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# LOGS
# ═══════════════════════════════════════════════════════════════

LOG_PATHS = [
    "/var/log/rmi/backend.log",
    "/root/rmi/logs/backend.log",
    "/root/rmi/backend.log",
    "/root/logs/rmi.log",
]

@router.get("/logs")
async def admin_logs(
    request: Request,
    lines: int = 100,
    level: Optional[str] = None,
    _=Depends(_verify_admin)
):
    """Read recent backend log lines."""
    log_file = None
    for p in LOG_PATHS:
        if os.path.exists(p):
            log_file = p
            break

    if not log_file:
        # Fallback: return empty but include a message
        return {
            "source": None,
            "lines": [],
            "message": "No log file found. Checked: " + ", ".join(LOG_PATHS),
        }

    try:
        with open(log_file, "r", errors="replace") as f:
            all_lines = f.readlines()

        # Filter by level if requested
        if level:
            all_lines = [ln for ln in all_lines if level.upper() in ln.upper()]

        # Return last N lines
        selected = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return {
            "source": log_file,
            "total_lines": len(all_lines),
            "returned_lines": len(selected),
            "lines": [ln.rstrip("\n") for ln in selected],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log read error: {e}")


# ═══════════════════════════════════════════════════════════════
# DATABASE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    sql: str = Field(..., description="Read-only SQL query")
    limit: int = Field(default=100, ge=1, le=1000)

SAFE_SQL_PATTERN = re.compile(
    r"^\s*SELECT\s+",
    re.IGNORECASE
)

@router.get("/database/tables")
async def admin_db_tables(request: Request, _=Depends(_verify_admin)):
    """List Supabase tables with approximate row counts."""
    db: RmiDatabase = get_db()
    tables = [
        "profiles", "contract_audits", "trenches_posts",
        "wallet_scans", "investigation_cases", "alerts",
        "evidence", "comments", "votes"
    ]
    result = []
    for table in tables:
        try:
            resp = await db.db.client.table(table).select("*", count="exact").limit(0).execute()
            count = getattr(resp, "count", 0) or 0
        except Exception:
            count = 0
        result.append({
            "name": table,
            "rows": count,
            "size": "-",
            "last_write": "-",
        })
    return {"tables": result}


@router.post("/database/query")
async def admin_db_query(req: QueryRequest, request: Request, _=Depends(_verify_admin)):
    """Execute a safe read-only SQL query."""
    sql = req.sql.strip()
    if not SAFE_SQL_PATTERN.match(sql):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

    # Extra safety: block dangerous keywords
    dangerous = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|EXEC|EXECUTE)\b", re.IGNORECASE)
    if dangerous.search(sql):
        raise HTTPException(status_code=400, detail="Dangerous keywords detected")

    db: RmiDatabase = get_db()
    try:
        # Use RPC if available, otherwise fallback to PostgREST
        try:
            resp = await db.db.execute_sql(sql)
            data = resp.data if hasattr(resp, "data") else resp
        except Exception:
            # Fallback: try simple table select via PostgREST
            # This won't work for complex queries, but it's safe
            raise HTTPException(status_code=501, detail="Raw SQL execution not available. Ensure exec_sql RPC exists in Supabase.")

        return {
            "query": sql,
            "row_count": len(data) if isinstance(data, list) else 0,
            "data": data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {e}")


# ═══════════════════════════════════════════════════════════════
# SERVICE CONTROL
# ═══════════════════════════════════════════════════════════════

SERVICES = {
    "fastapi": {"port": 8000, "name": "FastAPI Backend"},
    "dragonfly": {"port": 6379, "name": "Dragonfly Cache"},
    "postgres": {"port": 5432, "name": "PostgreSQL"},
    "n8n": {"port": 5678, "name": "N8N Automation"},
    "trenches": {"port": 8888, "name": "The Trenches"},
    "website": {"port": 8889, "name": "Website"},
}

def _check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

@router.get("/services")
async def admin_services(request: Request, _=Depends(_verify_admin)):
    """Check status of ecosystem services by port."""
    results = []
    for key, cfg in SERVICES.items():
        online = _check_port("127.0.0.1", cfg["port"])
        results.append({
            "id": key,
            "name": cfg["name"],
            "port": cfg["port"],
            "status": "running" if online else "stopped",
            "online": online,
        })
    return {"services": results}


class ServiceActionRequest(BaseModel):
    action: str = Field(..., description="restart, stop, start, clear_cache, health_check")

@router.post("/services/{service_id}/action")
async def admin_service_action(
    service_id: str,
    req: ServiceActionRequest,
    request: Request,
    _=Depends(_verify_admin)
):
    """Trigger an action on a service (best-effort via Redis queue or direct signal)."""
    if service_id not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    action = req.action.lower()
    allowed = {"restart", "stop", "start", "clear_cache", "health_check", "backup"}
    if action not in allowed:
        raise HTTPException(status_code=400, detail=f"Action must be one of {allowed}")

    # For now, store action in Redis queue for worker pickup
    try:
        from main import get_redis
        r = await get_redis()
        await r.lpush(
            "rmi:queue:system",
            json.dumps({
                "type": "service_action",
                "service": service_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
            })
        )
        return {
            "service": service_id,
            "action": action,
            "status": "queued",
            "message": f"{action} queued for {service_id}. Worker will process.",
        }
    except Exception as e:
        logger.error(f"[Admin] Service action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# BOT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

@router.get("/bots")
async def admin_bots(request: Request, _=Depends(_verify_admin)):
    """Get bot configurations from Redis."""
    try:
        from main import get_redis
        r = await get_redis()
        bots_raw = await r.hgetall("rmi:bots") or {}
        bots = []
        for k, v in bots_raw.items():
            try:
                data = json.loads(v)
                data["id"] = k
                bots.append(data)
            except Exception:
                pass
        if not bots:
            # Return default bots if none in Redis
            bots = [
                {"id": "rugmunch", "name": "@rugmunchbot", "type": "main", "status": "active", "token": "***"},
                {"id": "backend", "name": "@rmi_backend_bot", "type": "monitoring", "status": "active", "token": "***"},
                {"id": "alerts", "name": "@rmi_alerts_bot", "type": "free_alerts", "status": "active", "token": "***"},
                {"id": "alpha", "name": "@rmi_alpha_bot", "type": "paid_alerts", "status": "active", "token": "***"},
            ]
        return {"bots": bots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BotUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    token: Optional[str] = None

@router.put("/bots/{bot_id}")
async def admin_update_bot(
    bot_id: str,
    req: BotUpdateRequest,
    request: Request,
    _=Depends(_verify_admin)
):
    """Update bot configuration in Redis."""
    try:
        from main import get_redis
        r = await get_redis()
        existing = await r.hget("rmi:bots", bot_id)
        data = json.loads(existing) if existing else {"id": bot_id}
        if req.name is not None:
            data["name"] = req.name
        if req.type is not None:
            data["type"] = req.type
        if req.status is not None:
            data["status"] = req.status
        if req.token is not None:
            data["token"] = req.token
        await r.hset("rmi:bots", bot_id, json.dumps(data))
        # Mask token in response
        resp = {**data}
        if "token" in resp:
            resp["token"] = "***"
        return {"bot": resp, "status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# ALERTS
# ═══════════════════════════════════════════════════════════════

@router.get("/alerts")
async def admin_alerts(
    request: Request,
    limit: int = 50,
    _=Depends(_verify_admin)
):
    """Get recent alert history from Redis."""
    try:
        from main import get_redis
        r = await get_redis()
        alerts_raw = await r.lrange("rmi:alert:history", 0, limit - 1)
        alerts = []
        for raw in alerts_raw:
            try:
                alerts.append(json.loads(raw))
            except Exception:
                pass
        return {
            "alerts": alerts,
            "total": len(alerts),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TestAlertRequest(BaseModel):
    message: str = "Test alert from RMI Control Center"
    channel: str = "@rmi_backend"
    severity: str = "info"

@router.post("/alerts/test")
async def admin_send_test_alert(
    req: TestAlertRequest,
    request: Request,
    _=Depends(_verify_admin)
):
    """Send a test alert and record it in history."""
    try:
        from main import get_redis
        r = await get_redis()
        alert_entry = {
            "id": f"test-{datetime.utcnow().timestamp()}",
            "message": req.message,
            "channel": req.channel,
            "severity": req.severity,
            "type": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "test": True,
        }
        await r.lpush("rmi:alert:history", json.dumps(alert_entry))
        await r.ltrim("rmi:alert:history", 0, 999)  # Keep last 1000
        return {"status": "sent", "alert": alert_entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# STATS (used by frontend getStats)
# ═══════════════════════════════════════════════════════════════

@router.get("/stats")
async def admin_stats(request: Request, _=Depends(_verify_admin)):
    """Aggregate system stats for the admin overview."""
    try:
        from main import get_redis
        r = await get_redis()

        # Count agents
        agents_raw = await r.hgetall("rmi:agents") or {}
        agents_online = sum(1 for a in agents_raw.values() if json.loads(a).get("status") == "online")

        # Count cases from Redis
        cases_raw = await r.hgetall("rmi:cases") or {}

        # Count wallets from Redis
        wallets_raw = await r.hgetall("rmi:wallets") or {}

        # API calls today (approximate from Redis counter)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        api_calls = int(await r.get(f"rmi:metrics:api_calls:{today}") or 0)

        # Cache hit rate
        cache_hits = int(await r.get("rmi:metrics:cache_hits") or 0)
        cache_misses = int(await r.get("rmi:metrics:cache_misses") or 1)
        hit_rate = cache_hits / (cache_hits + cache_misses)

        # Supabase status check
        supabase_ok = False
        try:
            db = get_db()
            # Quick ping
            await db.db.client.table("profiles").select("id", count="exact").limit(1).execute()
            supabase_ok = True
        except Exception:
            pass

        return {
            "total_investigations": len(cases_raw),
            "total_wallets": len(wallets_raw),
            "api_calls_today": api_calls,
            "cache_hit_rate": round(hit_rate, 3),
            "dragonfly_status": "connected",
            "supabase_status": "connected" if supabase_ok else "disconnected",
            "agents_online": agents_online,
            "agents_total": len(agents_raw),
            "version": "2.0.0",
        }
    except Exception as e:
        logger.error(f"[Admin] Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
