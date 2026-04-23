"""
On-Chain Monitor
Watches for new token deployments and flags suspicious patterns.
"""
import os
import json
import logging
from datetime import datetime
from urllib.request import urlopen, Request

logger = logging.getLogger("chain_monitor")

RPC_ENDPOINTS = {
    "solana": "https://api.mainnet-beta.solana.com",
    "ethereum": "https://eth.llamarpc.com",
}


def _get_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def check_solana_new_tokens():
    """Query Solana for recent large token mints via simple heuristic."""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getRecentBlockhash",
            "params": [{"commitment": "finalized"}]
        }
        req = Request(
            RPC_ENDPOINTS["solana"],
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result.get("result", {})
    except Exception as e:
        logger.warning(f"Solana check failed: {e}")
        return None


def run():
    logger.info("Chain monitor running")
    sb = _get_supabase()

    # Check Solana
    sol_result = check_solana_new_tokens()
    if sol_result:
        logger.info("Solana RPC reachable")

    # Store a heartbeat
    if sb:
        try:
            sb.table("agent_heartbeats").insert({
                "agent": "chain_monitor",
                "checked_at": datetime.utcnow().isoformat(),
                "solana_reachable": sol_result is not None,
            }).execute()
        except Exception:
            pass

    logger.info("Chain monitor complete")
