"""
Nansen Service
==============
Smart money tracking, wallet labeling, token god mode
"""
import os
import json
import logging
from typing import Dict, Any
import urllib.request

from app.services.vault_keys import get_secret

logger = logging.getLogger("nansen")
NANSEN_API_BASE = "https://api.nansen.ai"

def _get_key() -> str:
    key = os.getenv("NANSEN_API_KEY", "")
    if not key:
        key = get_secret("crypto/nansen", "api_key") or ""
    return key

def _request(path: str) -> Dict[str, Any]:
    api_key = _get_key()
    headers = {"Content-Type": "application/json", "X-API-Key": api_key}
    req = urllib.request.Request(f"{NANSEN_API_BASE}{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_wallet_labels(address: str) -> Dict[str, Any]:
    try: return _request(f"/wallet/{address}/labels")
    except Exception as e: logger.error(f"Nansen labels failed: {e}"); return {"error": str(e)}

def get_token_god_mode(token: str) -> Dict[str, Any]:
    try: return _request(f"/token/{token}/god-mode")
    except Exception as e: logger.error(f"Nansen god mode failed: {e}"); return {"error": str(e)}

def get_smart_money_signals(token: str) -> Dict[str, Any]:
    try: return _request(f"/token/{token}/smart-money")
    except Exception as e: logger.error(f"Nansen smart money failed: {e}"); return {"error": str(e)}
