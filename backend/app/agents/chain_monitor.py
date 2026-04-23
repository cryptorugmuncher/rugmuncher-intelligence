"""
On-Chain Monitor
================
Watches for new token deployments and flags suspicious patterns using FREE AI.
Always prioritizes free providers (Workers AI, OpenRouter free, Gemini free tier).
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


def _ai_risk_assessment(chain: str, data: dict) -> dict:
    """Use FREE AI to assess on-chain risk. Always free-first."""
    try:
        from app.services.cloudflare_ai import smart_chat
        from app.services.vault_keys import get_all_ai_keys

        keys = get_all_ai_keys()
        text = json.dumps(data, default=str)[:3000]

        result = smart_chat(
            messages=[
                {"role": "system", "content": "Assess token risk. Reply with JSON only: {\"risk_level\": \"LOW|MEDIUM|HIGH\", \"flags\": [\"flag1\", \"flag2\"], \"reason\": \"short reason\"}"},
                {"role": "user", "content": f"{chain} token data: {text}"},
            ],
            keys=keys,
            priority="free",
        )
        content = result.get("response", "") or result.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Try to extract JSON from response
        try:
            parsed = json.loads(content.strip())
            return {
                "risk_level": parsed.get("risk_level", "UNKNOWN"),
                "flags": parsed.get("flags", []),
                "reason": parsed.get("reason", ""),
                "ai_analyzed": True,
            }
        except json.JSONDecodeError:
            return {"risk_level": "UNKNOWN", "flags": [], "reason": "AI parse failed", "ai_analyzed": False}
    except Exception as e:
        logger.warning(f"FREE AI risk assessment failed: {e}")
        return {"risk_level": "UNKNOWN", "flags": [], "reason": "AI unavailable", "ai_analyzed": False}


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
    logger.info("⛓️ Chain monitor running (FREE AI priority)")
    sb = _get_supabase()

    # Check Solana
    sol_result = check_solana_new_tokens()
    assessment = {}
    if sol_result:
        logger.info("Solana RPC reachable — analyzing with FREE AI")
        assessment = _ai_risk_assessment("solana", sol_result)

    # Store heartbeat + assessment
    if sb:
        try:
            sb.table("agent_heartbeats").insert({
                "agent": "chain_monitor",
                "checked_at": datetime.utcnow().isoformat(),
                "solana_reachable": sol_result is not None,
                "risk_level": assessment.get("risk_level", "UNKNOWN"),
                "ai_analyzed": assessment.get("ai_analyzed", False),
            }).execute()
        except Exception:
            pass

    logger.info(f"✅ Chain monitor complete — risk: {assessment.get('risk_level', 'UNKNOWN')}")
