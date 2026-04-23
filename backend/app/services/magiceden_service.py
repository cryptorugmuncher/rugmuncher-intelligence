"""
Magic Eden Service
==================
Solana NFT marketplace data, collections, listings
"""
import os
import json
import logging
from typing import Dict, Any
import urllib.request

from app.services.vault_keys import get_secret

logger = logging.getLogger("magiceden")
ME_API_BASE = "https://api-mainnet.magiceden.dev/v2"

def _get_key() -> str:
    key = os.getenv("MAGICEDEN_API_KEY", "")
    if not key:
        key = get_secret("crypto/magiceden", "api_key") or ""
    return key

def _request(path: str) -> Dict[str, Any]:
    api_key = _get_key()
    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "PLACEHOLDER_UPDATE_ME":
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(f"{ME_API_BASE}{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_collection_stats(symbol: str) -> Dict[str, Any]:
    try: return _request(f"/collections/{symbol}/stats")
    except Exception as e: logger.error(f"ME stats failed: {e}"); return {"error": str(e)}

def get_collection_listings(symbol: str, limit: int = 20) -> Dict[str, Any]:
    try: return _request(f"/collections/{symbol}/listings?limit={limit}")
    except Exception as e: logger.error(f"ME listings failed: {e}"); return {"error": str(e)}

def get_wallet_tokens(address: str) -> Dict[str, Any]:
    try: return _request(f"/wallets/{address}/tokens")
    except Exception as e: logger.error(f"ME wallet failed: {e}"); return {"error": str(e)}
