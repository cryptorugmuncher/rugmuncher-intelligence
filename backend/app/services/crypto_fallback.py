"""
Crypto Data Fallback Chain
==========================
Data ALWAYS loads no matter what. Cascading fallback across multiple sources.

Chain: CoinGecko → GMGN → DexPaprika (MCP) → CoinMarketCap
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import urllib.request

from app.services.gmgn_service import get_token_info as gmgn_token_info, get_token_price as gmgn_token_price
from app.services.mcp_servers import get_token_price_multi_source as mcp_token_price

logger = logging.getLogger("crypto_fallback")

CMC_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "")


def _request(url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


# ═══════════════════════════════════════════════════════════
# PRICE FALLBACK CHAIN
# ═══════════════════════════════════════════════════════════

def get_token_price(token_address: str, chain: str = "solana", symbol: str = "") -> Dict[str, Any]:
    """Get token price — tries multiple sources until one succeeds."""
    result = {"token_address": token_address, "chain": chain, "symbol": symbol, "sources": {}, "errors": []}

    # 1. Try CoinGecko first (most reliable)
    try:
        url = f"https://api.coingecko.com/api/v3/simple/token_price/{chain}?contract_addresses={token_address}&vs_currencies=usd"
        data = _request(url)
        price = data.get(token_address.lower(), {}).get("usd")
        if price:
            result["price_usd"] = price
            result["source"] = "coingecko"
            result["sources"]["coingecko"] = data
            return result
    except Exception as e:
        result["errors"].append({"source": "coingecko", "error": str(e)})

    # 2. Try GMGN
    try:
        data = gmgn_token_price(token_address, chain[:3] if chain == "solana" else chain)
        if "error" not in data:
            price = data.get("price_usd") or data.get("price")
            if price:
                result["price_usd"] = float(price)
                result["source"] = "gmgn"
                result["sources"]["gmgn"] = data
                return result
    except Exception as e:
        result["errors"].append({"source": "gmgn", "error": str(e)})

    # 3. Try MCP (DexPaprika + EVM)
    try:
        data = mcp_token_price(token_address, chain)
        if data.get("price"):
            result["price_usd"] = data["price"]
            result["source"] = data.get("source", "mcp")
            result["sources"]["mcp"] = data
            return result
    except Exception as e:
        result["errors"].append({"source": "mcp", "error": str(e)})

    # 4. Try CoinMarketCap
    if CMC_API_KEY:
        try:
            url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol.upper()}&convert=USD"
            data = _request(url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY, "Accept": "application/json"})
            quote = data.get("data", {}).get(symbol.upper(), {}).get("quote", {}).get("USD", {})
            price = quote.get("price")
            if price:
                result["price_usd"] = price
                result["source"] = "coinmarketcap"
                result["sources"]["coinmarketcap"] = data
                return result
        except Exception as e:
            result["errors"].append({"source": "coinmarketcap", "error": str(e)})

    # All failed
    result["error"] = "All price sources failed"
    return result


# ═══════════════════════════════════════════════════════════
# FULL TOKEN DATA FALLBACK
# ═══════════════════════════════════════════════════════════

def get_token_data(token_address: str, chain: str = "solana") -> Dict[str, Any]:
    """Get comprehensive token data with cascading fallback."""
    result = {"token_address": token_address, "chain": chain, "sources": {}, "errors": []}

    # Try GMGN first (most comprehensive for Solana)
    try:
        data = gmgn_token_info(token_address, chain[:3] if chain == "solana" else chain)
        if "error" not in data:
            result["sources"]["gmgn"] = data
            result["has_data"] = True
            return result
        else:
            result["errors"].append({"source": "gmgn", "error": data["error"]})
    except Exception as e:
        result["errors"].append({"source": "gmgn", "error": str(e)})

    # Fallback to MCP
    try:
        from app.services.mcp_servers import get_wallet_analysis
        data = get_wallet_analysis(token_address, chain)
        if data.get("sources"):
            result["sources"]["mcp"] = data
            result["has_data"] = True
            return result
    except Exception as e:
        result["errors"].append({"source": "mcp", "error": str(e)})

    result["has_data"] = False
    return result


# ═══════════════════════════════════════════════════════════
# TRENDING TOKENS FALLBACK
# ═══════════════════════════════════════════════════════════

def get_trending_tokens(chain: str = "solana") -> Dict[str, Any]:
    """Get trending tokens — tries multiple sources."""
    result = {"chain": chain, "sources": {}, "errors": []}

    # GMGN trending
    try:
        from app.services.gmgn_service import get_trending
        data = get_trending(chain[:3] if chain == "solana" else chain)
        if "error" not in data:
            result["sources"]["gmgn"] = data
            result["tokens"] = data.get("tokens", [])
            result["source"] = "gmgn"
            return result
    except Exception as e:
        result["errors"].append({"source": "gmgn", "error": str(e)})

    # CoinGecko trending
    try:
        data = _request("https://api.coingecko.com/api/v3/search/trending")
        result["sources"]["coingecko"] = data
        result["tokens"] = [c["item"] for c in data.get("coins", [])]
        result["source"] = "coingecko"
        return result
    except Exception as e:
        result["errors"].append({"source": "coingecko", "error": str(e)})

    return result
