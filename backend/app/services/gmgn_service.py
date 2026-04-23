"""
GMGN Agent API Integration
==========================
On-chain data, token analysis, portfolio tracking, and swaps.
https://docs.gmgn.ai/index/gmgn-agent-api
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import urllib.request

logger = logging.getLogger("gmgn")

GMGN_API_BASE = "https://gmgn.ai/api/v1"
GMGN_API_KEY = os.getenv("GMGN_API_KEY", "")


def _request(path: str, method: str = "GET", payload: Optional[Dict] = None) -> Dict[str, Any]:
    """Make authenticated request to GMGN API."""
    url = f"{GMGN_API_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": GMGN_API_KEY,
    }
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


# ═══════════════════════════════════════════════════════════
# TOKEN DATA
# ═══════════════════════════════════════════════════════════

def get_token_info(token_address: str, chain: str = "sol") -> Dict[str, Any]:
    """Get token basic info, price, contract security, top holders."""
    try:
        return _request(f"/token/{chain}/{token_address}")
    except Exception as e:
        logger.error(f"GMGN token info failed: {e}")
        return {"error": str(e)}


def get_token_price(token_address: str, chain: str = "sol") -> Dict[str, Any]:
    """Get real-time token price."""
    try:
        return _request(f"/token/{chain}/{token_address}/price")
    except Exception as e:
        logger.error(f"GMGN price failed: {e}")
        return {"error": str(e)}


def get_token_security(token_address: str, chain: str = "sol") -> Dict[str, Any]:
    """Get contract security analysis."""
    try:
        return _request(f"/token/{chain}/{token_address}/security")
    except Exception as e:
        logger.error(f"GMGN security failed: {e}")
        return {"error": str(e)}


def get_token_holders(token_address: str, chain: str = "sol", limit: int = 20) -> Dict[str, Any]:
    """Get top holders and traders."""
    try:
        return _request(f"/token/{chain}/{token_address}/holders?limit={limit}")
    except Exception as e:
        logger.error(f"GMGN holders failed: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# MARKET DATA
# ═══════════════════════════════════════════════════════════

def get_candlesticks(token_address: str, chain: str = "sol", resolution: str = "1h", limit: int = 100) -> Dict[str, Any]:
    """Get candlestick data (1m to 1d resolutions)."""
    try:
        return _request(f"/market/{chain}/{token_address}/candlesticks?resolution={resolution}&limit={limit}")
    except Exception as e:
        logger.error(f"GMGN candlesticks failed: {e}")
        return {"error": str(e)}


def get_trending(chain: str = "sol") -> Dict[str, Any]:
    """Get current trending tokens."""
    try:
        return _request(f"/market/{chain}/trending")
    except Exception as e:
        logger.error(f"GMGN trending failed: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# WALLET / PORTFOLIO
# ═══════════════════════════════════════════════════════════

def get_wallet_portfolio(wallet_address: str, chain: str = "sol") -> Dict[str, Any]:
    """Get wallet holdings and token balances."""
    try:
        return _request(f"/portfolio/{chain}/{wallet_address}")
    except Exception as e:
        logger.error(f"GMGN portfolio failed: {e}")
        return {"error": str(e)}


def get_wallet_transactions(wallet_address: str, chain: str = "sol", limit: int = 50) -> Dict[str, Any]:
    """Get wallet transaction history and PnL."""
    try:
        return _request(f"/portfolio/{chain}/{wallet_address}/transactions?limit={limit}")
    except Exception as e:
        logger.error(f"GMGN transactions failed: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# SMART AGGREGATION — Data always loads no matter what
# ═══════════════════════════════════════════════════════════

def get_full_token_analysis(token_address: str, chain: str = "sol") -> Dict[str, Any]:
    """Aggregate ALL available data for a token. Tries multiple sources."""
    result = {
        "token_address": token_address,
        "chain": chain,
        "sources": {},
        "errors": [],
    }

    # 1. GMGN primary
    info = get_token_info(token_address, chain)
    if "error" not in info:
        result["sources"]["gmgn"] = info
    else:
        result["errors"].append({"source": "gmgn", "error": info["error"]})

    # 2. Price
    price = get_token_price(token_address, chain)
    if "error" not in price:
        result["price"] = price
    else:
        result["errors"].append({"source": "gmgn_price", "error": price["error"]})

    # 3. Security
    security = get_token_security(token_address, chain)
    if "error" not in security:
        result["security"] = security
    else:
        result["errors"].append({"source": "gmgn_security", "error": security["error"]})

    # 4. Holders
    holders = get_token_holders(token_address, chain)
    if "error" not in holders:
        result["holders"] = holders
    else:
        result["errors"].append({"source": "gmgn_holders", "error": holders["error"]})

    # 5. Fallback to CoinGecko if GMGN fails
    if not result["sources"]:
        try:
            from app.services.crypto.coingecko import get_token_data
            cg_data = get_token_data(token_address)
            if cg_data:
                result["sources"]["coingecko"] = cg_data
        except Exception as e:
            result["errors"].append({"source": "coingecko_fallback", "error": str(e)})

    result["has_data"] = len(result["sources"]) > 0
    return result
