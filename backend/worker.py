#!/usr/bin/env python3
"""
RMI Background Worker
=====================
Processes tasks from Redis queues: critical, high, normal, low priority.
Handles agent commands, crypto scans, and investigation tasks.
"""

import os
import sys
import json
import asyncio
import logging
import httpx
import dataclasses
import redis.asyncio as redis
from datetime import datetime

sys.path.insert(0, "/root/rmi/backend")
sys.path.insert(0, "/root/rmi/backend/app")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "") or None
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

MAX_RETRIES = 3


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

async def with_retries(coro_factory, task_name: str, max_retries: int = MAX_RETRIES):
    """Execute an async callable with retries and exponential backoff."""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return await coro_factory()
        except Exception as e:
            last_error = e
            logger.warning(f"[{task_name}] Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
    logger.error(f"[{task_name}] All {max_retries} attempts failed: {last_error}")
    raise last_error


async def store_task_result(redis_client, task_id: str, result: dict):
    """Store task result in Redis with a TTL."""
    key = f"rmi:task_results:{task_id}"
    payload = {
        **result,
        "stored_at": datetime.utcnow().isoformat(),
    }
    await redis_client.set(key, json.dumps(payload, default=str), ex=86400)


def _serialize_dataclass(obj):
    """Serialize dataclasses and other objects to JSON-friendly dicts."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, (list, tuple)):
        return [_serialize_dataclass(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize_dataclass(v) for k, v in obj.items()}
    return obj


# ═══════════════════════════════════════════════════════════════════════════════
# TASK HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_wallet_scan(task_data: dict, redis_client) -> dict:
    """Scan a wallet using Birdeye and optional Helius APIs."""
    from app.birdeye_client import BirdeyeClient

    address = task_data.get("address", "")
    chain = task_data.get("chain", "solana")
    depth = task_data.get("depth", "standard")

    logger.info(f"[wallet_scan] Scanning wallet: {address} (chain={chain}, depth={depth})")

    client = BirdeyeClient()
    try:
        networth, pnl, smart = await asyncio.gather(
            with_retries(lambda: client.get_wallet_networth(address), "wallet_networth"),
            with_retries(lambda: client.get_wallet_pnl(address), "wallet_pnl"),
            with_retries(lambda: client.get_wallet_smart_money_status(address), "wallet_smart_money"),
            return_exceptions=True,
        )

        result = {
            "address": address,
            "chain": chain,
            "depth": depth,
            "networth": networth if not isinstance(networth, Exception) else {"error": str(networth)},
            "pnl": pnl if not isinstance(pnl, Exception) else {"error": str(pnl)},
            "smart_money_status": smart if not isinstance(smart, Exception) else {"error": str(smart)},
            "birdeye_powered": True,
        }

        # Helius for Solana
        if chain == "solana" and HELIUS_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as hc:
                    resp = await hc.get(
                        f"https://api.helius.xyz/v0/addresses/?api-key={HELIUS_API_KEY}&address={address}"
                    )
                    if resp.status_code == 200:
                        result["helius"] = resp.json()
            except Exception as e:
                result["helius_error"] = str(e)
                logger.warning(f"[wallet_scan] Helius error: {e}")

        await store_task_result(redis_client, task_data.get("id", "unknown"), result)
        return {"status": "completed", "type": "wallet_scan", "result": result}
    finally:
        await client.close()


async def handle_contract_audit(task_data: dict, redis_client) -> dict:
    """Audit a contract using degen scanner, Solscan, and AI analysis."""
    address = task_data.get("address", "")
    chain = task_data.get("chain", "solana")
    source_code = task_data.get("source_code", "")

    logger.info(f"[contract_audit] Auditing contract: {address} (chain={chain})")

    audit_data = {
        "address": address,
        "chain": chain,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Degen security scanner for Solana tokens
    if chain == "solana":
        try:
            from app.degen_security_scanner import scan_token

            def _run_degen_sync():
                # Degen scanner does blocking I/O inside async methods;
                # run it in its own thread+event loop to avoid blocking the worker loop.
                return asyncio.run(scan_token(address, quick=True))

            report = await asyncio.to_thread(_run_degen_sync)
            audit_data["degen_scan"] = _serialize_dataclass(report)
        except Exception as e:
            logger.error(f"[contract_audit] Degen scan failed: {e}")
            audit_data["degen_scan_error"] = str(e)

    # Supplement with free Solscan data
    try:
        from app.free_solscan_client import FreeSolscanClient

        token_data = await asyncio.to_thread(FreeSolscanClient.token_data, address)
        if token_data:
            audit_data["solscan_token_data"] = token_data

        holders = await asyncio.to_thread(FreeSolscanClient.token_holders_total, address)
        if holders is not None:
            audit_data["total_holders"] = holders
    except Exception as e:
        logger.warning(f"[contract_audit] Solscan fallback error: {e}")
        audit_data["solscan_error"] = str(e)

    # AI analysis via ai_router for code review
    try:
        from app.ai_router import router as ai_router

        context = json.dumps(audit_data.get("solscan_token_data", {}), default=str)[:2000]
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert smart contract security auditor. "
                    "Analyze the following contract and provide a concise risk assessment."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Contract Address: {address}\n"
                    f"Chain: {chain}\n"
                    f"Source Code: {source_code or 'Not provided'}\n"
                    f"On-chain Data: {context}"
                ),
            },
        ]
        ai_result = await with_retries(
            lambda: ai_router.chat_completion(messages, tier="T1", max_tokens=2048),
            "ai_contract_audit",
        )
        audit_data["ai_analysis"] = ai_result
    except Exception as e:
        logger.error(f"[contract_audit] AI analysis failed: {e}")
        audit_data["ai_analysis_error"] = str(e)

    await store_task_result(redis_client, task_data.get("id", "unknown"), audit_data)
    return {"status": "completed", "type": "contract_audit", "result": audit_data}


async def handle_self_heal(task_data: dict, redis_client) -> dict:
    """Check Redis connectivity, Dragonfly health, and attempt reconnection if needed."""
    logger.info("[self_heal] Running self-heal check")

    health_report = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "repairs": [],
    }

    # Check Redis / Dragonfly connectivity
    try:
        await redis_client.ping()
        health_report["checks"]["redis_ping"] = True
        info = await redis_client.info("replication")
        health_report["checks"]["dragonfly_replication"] = info
    except Exception as e:
        health_report["checks"]["redis_ping"] = False
        health_report["checks"]["redis_error"] = str(e)
        logger.error(f"[self_heal] Redis ping failed: {e}")

        # Attempt reconnection
        try:
            new_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,
            )
            await new_client.ping()
            health_report["repairs"].append("redis_reconnected")
            logger.info("[self_heal] Redis reconnected successfully")
            await new_client.close()
        except Exception as recon_e:
            health_report["repairs"].append(f"redis_reconnect_failed: {recon_e}")
            logger.critical(f"[self_heal] Redis reconnection failed: {recon_e}")

    # Check backend health endpoint
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://127.0.0.1:8000/health")
            health_report["checks"]["backend_health"] = resp.status_code == 200
    except Exception as e:
        health_report["checks"]["backend_health"] = False
        health_report["checks"]["backend_error"] = str(e)

    # Check n8n health endpoint
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://127.0.0.1:5678/healthz")
            health_report["checks"]["n8n_health"] = resp.status_code == 200
    except Exception as e:
        health_report["checks"]["n8n_health"] = False
        health_report["checks"]["n8n_error"] = str(e)

    await store_task_result(redis_client, task_data.get("id", "unknown"), health_report)
    return {"status": "completed", "type": "self_heal", "result": health_report}


async def handle_token_scan(task_data: dict, redis_client) -> dict:
    """Scan a token using Birdeye security_scan."""
    from app.birdeye_client import BirdeyeClient

    address = task_data.get("address", "")
    chain = task_data.get("chain", "solana")

    logger.info(f"[token_scan] Scanning token: {address} (chain={chain})")

    client = BirdeyeClient()
    try:
        result = await with_retries(
            lambda: client.security_scan(address),
            "token_security_scan",
        )
        result["chain"] = chain
        result["task_type"] = "token_scan"

        await store_task_result(redis_client, task_data.get("id", "unknown"), result)
        return {"status": "completed", "type": "token_scan", "result": result}
    finally:
        await client.close()


async def handle_alert_broadcast(task_data: dict, redis_client) -> dict:
    """Send Telegram alerts if BOT_TOKEN is configured."""
    message = task_data.get("message", "")
    parse_mode = task_data.get("parse_mode", "HTML")
    channel = task_data.get("channel", "alerts")

    logger.info(f"[alert_broadcast] Broadcasting alert to channel: {channel}")

    if not BOT_TOKEN:
        logger.warning("[alert_broadcast] BOT_TOKEN not set, skipping")
        result = {"status": "skipped", "reason": "BOT_TOKEN not configured"}
        await store_task_result(redis_client, task_data.get("id", "unknown"), result)
        return {"status": "completed", "type": "alert_broadcast", "result": result}

    channel_env_map = {
        "news": os.getenv("CHANNEL_NEWS", ""),
        "alerts": os.getenv("CHANNEL_ALERTS", ""),
        "premium": os.getenv("CHANNEL_PREMIUM", ""),
        "alpha": os.getenv("CHANNEL_ALPHA", ""),
    }
    chat_id = channel_env_map.get(channel, channel)

    if not chat_id:
        result = {
            "status": "skipped",
            "reason": f"No chat_id configured for channel '{channel}'",
        }
        await store_task_result(redis_client, task_data.get("id", "unknown"), result)
        return {"status": "completed", "type": "alert_broadcast", "result": result}

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()
            result = {
                "status": "ok" if data.get("ok") else "failed",
                "telegram_response": data,
                "channel": channel,
            }
            if not data.get("ok"):
                logger.error(f"[alert_broadcast] Telegram API error: {data}")
    except Exception as e:
        logger.error(f"[alert_broadcast] Failed to send Telegram alert: {e}")
        result = {"status": "failed", "error": str(e)}

    await store_task_result(redis_client, task_data.get("id", "unknown"), result)
    return {
        "status": "completed" if result.get("status") != "failed" else "failed",
        "type": "alert_broadcast",
        "result": result,
    }


async def handle_news_fetch(task_data: dict, redis_client) -> dict:
    """Fetch crypto news via news_service."""
    limit = task_data.get("limit", 50)
    logger.info(f"[news_fetch] Fetching news (limit={limit})")

    try:
        from app.news_service import news_service

        headlines = await with_retries(
            lambda: news_service.get_all_news(limit=limit),
            "news_fetch",
        )
        result = {
            "status": "ok",
            "headlines": headlines,
            "count": len(headlines),
        }
    except Exception as e:
        logger.error(f"[news_fetch] Failed: {e}")
        result = {"status": "failed", "error": str(e)}

    await store_task_result(redis_client, task_data.get("id", "unknown"), result)
    return {
        "status": "completed" if result.get("status") != "failed" else "failed",
        "type": "news_fetch",
        "result": result,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

async def process_task(task_data: dict, redis_client) -> dict:
    """Route a task to its handler with centralized error handling."""
    task_type = task_data.get("type", "unknown")
    task_id = task_data.get("id", "unknown")

    logger.info(f"[WORKER] Processing task {task_id}: {task_type}")

    handlers = {
        "wallet_scan": handle_wallet_scan,
        "contract_audit": handle_contract_audit,
        "self_heal": handle_self_heal,
        "token_scan": handle_token_scan,
        "alert_broadcast": handle_alert_broadcast,
        "news_fetch": handle_news_fetch,
    }

    handler = handlers.get(task_type)
    if not handler:
        logger.warning(f"[WORKER] Unknown task type: {task_type}")
        result = {"status": "unknown_type", "type": task_type}
        await store_task_result(redis_client, task_id, result)
        return result

    try:
        return await handler(task_data, redis_client)
    except Exception as e:
        logger.exception(f"[WORKER] Task {task_id} ({task_type}) failed: {e}")
        error_result = {
            "status": "failed",
            "type": task_type,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat(),
        }
        await store_task_result(redis_client, task_id, error_result)
        return error_result


async def main():
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True,
    )

    logger.info("[WORKER] Started — waiting for tasks")

    while True:
        try:
            # Check queues in priority order: critical, high, normal, low
            for queue in [
                "rmi:queue:critical",
                "rmi:queue:high",
                "rmi:queue:normal",
                "rmi:queue:low",
            ]:
                result = await r.brpop(queue, timeout=1)
                if result:
                    _, task_id = result
                    task_raw = await r.hget("rmi:tasks", task_id)
                    if task_raw:
                        task = json.loads(task_raw)
                        task["status"] = "processing"
                        task["started"] = datetime.utcnow().isoformat()
                        await r.hset("rmi:tasks", task_id, json.dumps(task))

                        # Process
                        task_result = await process_task(task, r)

                        task["status"] = task_result.get("status", "completed")
                        task["result"] = task_result
                        task["completed"] = datetime.utcnow().isoformat()
                        await r.hset("rmi:tasks", task_id, json.dumps(task))
                        logger.info(
                            f"[WORKER] Completed task: {task_id} -> {task['status']}"
                        )
                    break
        except Exception as e:
            logger.exception(f"[WORKER] Main loop error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
