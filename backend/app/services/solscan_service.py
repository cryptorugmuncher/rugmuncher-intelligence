"""
Solscan API Service
===================
Solana token data, transactions, account info, NFTs
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import urllib.request

from app.services.vault_keys import get_secret

logger = logging.getLogger("solscan")
SOLSCAN_API_BASE = "https://api.solscan.io"

def _get_key() -> str:
    key = os.getenv("SOLSCAN_API_KEY", "")
    if not key:
        key = get_secret("crypto/solscan", "api_key") or ""
    return key

def _request(path: str) -> Dict[str, Any]:
    api_key = _get_key()
    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "PLACEHOLDER_UPDATE_ME":
        headers["token"] = api_key
    req = urllib.request.Request(f"{SOLSCAN_API_BASE}{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_account(address: str) -> Dict[str, Any]:
    try: return _request(f"/account/{address}")
    except Exception as e: logger.error(f"Solscan account failed: {e}"); return {"error": str(e)}

def get_account_transactions(address: str, limit: int = 50) -> Dict[str, Any]:
    try: return _request(f"/account/transactions?address={address}&limit={limit}")
    except Exception as e: logger.error(f"Solscan txs failed: {e}"); return {"error": str(e)}

def get_token_meta(address: str) -> Dict[str, Any]:
    try: return _request(f"/token/meta?address={address}")
    except Exception as e: logger.error(f"Solscan token meta failed: {e}"); return {"error": str(e)}

def get_token_holders(address: str, limit: int = 20) -> Dict[str, Any]:
    try: return _request(f"/token/holders?tokenAddress={address}&limit={limit}")
    except Exception as e: logger.error(f"Solscan holders failed: {e}"); return {"error": str(e)}

def get_token_market(address: str) -> Dict[str, Any]:
    try: return _request(f"/token/market?address={address}")
    except Exception as e: logger.error(f"Solscan market failed: {e}"); return {"error": str(e)}

def get_defi_activities(address: str) -> Dict[str, Any]:
    try: return _request(f"/account/defi/activities?address={address}")
    except Exception as e: logger.error(f"Solscan defi failed: {e}"); return {"error": str(e)}
