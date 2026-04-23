"""
Arkham Intelligence Service
============================
On-chain entity labeling, wallet intelligence, exchange flows
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import urllib.request

from app.services.vault_keys import get_secret

logger = logging.getLogger("arkham")
ARKHAM_API_BASE = "https://api.arkhamintelligence.com"

def _get_key() -> str:
    key = os.getenv("ARKHAM_API_KEY", "")
    if not key:
        key = get_secret("crypto/arkham", "api_key") or ""
    return key

def _request(path: str) -> Dict[str, Any]:
    api_key = _get_key()
    headers = {"Content-Type": "application/json", "API-Key": api_key}
    req = urllib.request.Request(f"{ARKHAM_API_BASE}{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_entity(entity_id: str) -> Dict[str, Any]:
    try: return _request(f"/entity/{entity_id}")
    except Exception as e: logger.error(f"Arkham entity failed: {e}"); return {"error": str(e)}

def get_address_intel(address: str) -> Dict[str, Any]:
    try: return _request(f"/intel/address/{address}")
    except Exception as e: logger.error(f"Arkham intel failed: {e}"); return {"error": str(e)}

def search_entities(query: str) -> Dict[str, Any]:
    try: return _request(f"/search?query={query}")
    except Exception as e: logger.error(f"Arkham search failed: {e}"); return {"error": str(e)}
