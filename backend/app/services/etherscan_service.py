"""
Etherscan / Blockscan API Service
==================================
EVM chain explorers: ETH, BSC, Polygon, Arbitrum, Base, Optimism
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import urllib.request

from app.services.vault_keys import get_secret

logger = logging.getLogger("etherscan")

CHAIN_ENDPOINTS = {
    "ethereum": "https://api.etherscan.io/api",
    "bsc": "https://api.bscscan.com/api",
    "polygon": "https://api.polygonscan.com/api",
    "arbitrum": "https://api.arbiscan.io/api",
    "base": "https://api.basescan.org/api",
    "optimism": "https://api.optimistic.etherscan.io/api",
}

def _get_key(chain: str) -> str:
    env_map = {"ethereum": "ETHERSCAN_API_KEY", "bsc": "BSCSCAN_API_KEY", "polygon": "POLYGONSCAN_API_KEY",
               "arbitrum": "ARBISCAN_API_KEY", "base": "BASESCAN_API_KEY", "optimism": "OPTIMISM_API_KEY"}
    key = os.getenv(env_map.get(chain, "ETHERSCAN_API_KEY"), "")
    if not key:
        key = get_secret(f"crypto/etherscan", "api_key") or ""
    return key

def _request(params: Dict[str, Any], chain: str = "ethereum") -> Dict[str, Any]:
    api_key = _get_key(chain)
    endpoint = CHAIN_ENDPOINTS.get(chain, CHAIN_ENDPOINTS["ethereum"])
    query = "&".join(f"{k}={v}" for k, v in {**params, "apikey": api_key}.items())
    req = urllib.request.Request(f"{endpoint}?{query}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_account_balance(address: str, chain: str = "ethereum") -> Dict[str, Any]:
    try: return _request({"module": "account", "action": "balance", "address": address, "tag": "latest"}, chain)
    except Exception as e: logger.error(f"Etherscan balance failed: {e}"); return {"error": str(e)}

def get_token_transactions(address: str, contract: str, chain: str = "ethereum") -> Dict[str, Any]:
    try: return _request({"module": "account", "action": "tokentx", "contractaddress": contract, "address": address, "page": 1, "offset": 100, "sort": "desc"}, chain)
    except Exception as e: logger.error(f"Etherscan token txs failed: {e}"); return {"error": str(e)}

def get_contract_source(address: str, chain: str = "ethereum") -> Dict[str, Any]:
    try: return _request({"module": "contract", "action": "getsourcecode", "address": address}, chain)
    except Exception as e: logger.error(f"Etherscan source failed: {e}"); return {"error": str(e)}

def get_abi(address: str, chain: str = "ethereum") -> Dict[str, Any]:
    try: return _request({"module": "contract", "action": "getabi", "address": address}, chain)
    except Exception as e: logger.error(f"Etherscan ABI failed: {e}"); return {"error": str(e)}
