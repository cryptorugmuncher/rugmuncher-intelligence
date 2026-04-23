"""
Crypto Data Fallback Chain
==========================
Data ALWAYS loads no matter what. Cascading fallback across 15+ sources.

Chain: CoinGecko → GMGN → Alchemy → Birdeye → Solscan → DexPaprika (MCP) → Moralis → Arkham → Nansen → CoinMarketCap
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import urllib.request

from app.services.vault_keys import get_crypto_key

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
    """Get token price — tries 10+ sources until one succeeds."""
    result = {"token_address": token_address, "chain": chain, "symbol": symbol, "sources": {}, "errors": []}

    # 1. CoinGecko
    try:
        url = f"https://api.coingecko.com/api/v3/simple/token_price/{chain}?contract_addresses={token_address}&vs_currencies=usd"
        data = _request(url)
        price = data.get(token_address.lower(), {}).get("usd")
        if price:
            result["price_usd"] = price; result["source"] = "coingecko"; result["sources"]["coingecko"] = data; return result
    except Exception as e: result["errors"].append({"source": "coingecko", "error": str(e)})

    # 2. GMGN
    try:
        from app.services.gmgn_service import get_token_price
        data = get_token_price(token_address, chain[:3] if chain == "solana" else chain)
        if "error" not in data:
            price = data.get("price_usd") or data.get("price")
            if price: result["price_usd"] = float(price); result["source"] = "gmgn"; result["sources"]["gmgn"] = data; return result
    except Exception as e: result["errors"].append({"source": "gmgn", "error": str(e)})

    # 3. Alchemy
    try:
        from app.services.alchemy_service import get_token_metadata
        data = get_token_metadata(token_address, chain)
        if "error" not in data and data.get("result", {}).get("logo"):
            result["sources"]["alchemy"] = data; result["source"] = "alchemy"; return result
    except Exception as e: result["errors"].append({"source": "alchemy", "error": str(e)})

    # 4. Birdeye
    try:
        key = get_crypto_key("birdeye")
        if key and key != "PLACEHOLDER_UPDATE_ME":
            url = f"https://public-api.birdeye.so/public/price?address={token_address}"
            data = _request(url, headers={"X-API-KEY": key})
            price = data.get("data", {}).get("value")
            if price: result["price_usd"] = float(price); result["source"] = "birdeye"; result["sources"]["birdeye"] = data; return result
    except Exception as e: result["errors"].append({"source": "birdeye", "error": str(e)})

    # 5. Solscan
    try:
        from app.services.solscan_service import get_token_market
        data = get_token_market(token_address)
        if "error" not in data:
            price = data.get("priceUsdt")
            if price: result["price_usd"] = float(price); result["source"] = "solscan"; result["sources"]["solscan"] = data; return result
    except Exception as e: result["errors"].append({"source": "solscan", "error": str(e)})

    # 6. MCP (DexPaprika + EVM)
    try:
        from app.services.mcp_servers import get_token_price_multi_source
        data = get_token_price_multi_source(token_address, chain)
        if data.get("price"): result["price_usd"] = data["price"]; result["source"] = data.get("source", "mcp"); result["sources"]["mcp"] = data; return result
    except Exception as e: result["errors"].append({"source": "mcp", "error": str(e)})

    # 7. Moralis
    try:
        key = get_crypto_key("moralis")
        if key and key != "PLACEHOLDER_UPDATE_ME":
            url = f"https://deep-index.moralis.io/api/v2/erc20/{token_address}/price?chain={chain}"
            data = _request(url, headers={"X-API-Key": key})
            price = data.get("usdPrice")
            if price: result["price_usd"] = float(price); result["source"] = "moralis"; result["sources"]["moralis"] = data; return result
    except Exception as e: result["errors"].append({"source": "moralis", "error": str(e)})

    # 8. Arkham
    try:
        from app.services.arkham_service import get_address_intel
        data = get_address_intel(token_address)
        if "error" not in data:
            result["sources"]["arkham"] = data; result["source"] = "arkham"; return result
    except Exception as e: result["errors"].append({"source": "arkham", "error": str(e)})

    # 9. Nansen
    try:
        from app.services.nansen_service import get_token_god_mode
        data = get_token_god_mode(token_address)
        if "error" not in data:
            result["sources"]["nansen"] = data; result["source"] = "nansen"; return result
    except Exception as e: result["errors"].append({"source": "nansen", "error": str(e)})

    # 10. CoinMarketCap
    if CMC_API_KEY:
        try:
            url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol.upper()}&convert=USD"
            data = _request(url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY, "Accept": "application/json"})
            quote = data.get("data", {}).get(symbol.upper(), {}).get("quote", {}).get("USD", {})
            price = quote.get("price")
            if price: result["price_usd"] = price; result["source"] = "coinmarketcap"; result["sources"]["coinmarketcap"] = data; return result
        except Exception as e: result["errors"].append({"source": "coinmarketcap", "error": str(e)})

    result["error"] = "All 10+ price sources failed"
    return result


# ═══════════════════════════════════════════════════════════
# FULL TOKEN DATA FALLBACK
# ═══════════════════════════════════════════════════════════

def get_token_data(token_address: str, chain: str = "solana") -> Dict[str, Any]:
    """Get comprehensive token data with cascading fallback across ALL sources."""
    result = {"token_address": token_address, "chain": chain, "sources": {}, "errors": []}

    # GMGN (most comprehensive for Solana)
    try:
        from app.services.gmgn_service import get_token_info
        data = get_token_info(token_address, chain[:3] if chain == "solana" else chain)
        if "error" not in data: result["sources"]["gmgn"] = data
        else: result["errors"].append({"source": "gmgn", "error": data["error"]})
    except Exception as e: result["errors"].append({"source": "gmgn", "error": str(e)})

    # Alchemy
    try:
        from app.services.alchemy_service import get_token_metadata
        data = get_token_metadata(token_address, chain)
        if "error" not in data: result["sources"]["alchemy"] = data
    except Exception as e: result["errors"].append({"source": "alchemy", "error": str(e)})

    # Solscan
    try:
        from app.services.solscan_service import get_token_meta
        data = get_token_meta(token_address)
        if "error" not in data: result["sources"]["solscan"] = data
    except Exception as e: result["errors"].append({"source": "solscan", "error": str(e)})

    # MCP
    try:
        from app.services.mcp_servers import get_wallet_analysis
        data = get_wallet_analysis(token_address, chain)
        if data.get("sources"): result["sources"]["mcp"] = data
    except Exception as e: result["errors"].append({"source": "mcp", "error": str(e)})

    # Arkham entity intel
    try:
        from app.services.arkham_service import get_address_intel
        data = get_address_intel(token_address)
        if "error" not in data: result["sources"]["arkham"] = data
    except Exception as e: result["errors"].append({"source": "arkham", "error": str(e)})

    # Nansen smart money
    try:
        from app.services.nansen_service import get_smart_money_signals
        data = get_smart_money_signals(token_address)
        if "error" not in data: result["sources"]["nansen"] = data
    except Exception as e: result["errors"].append({"source": "nansen", "error": str(e)})

    # Birdeye
    try:
        key = get_crypto_key("birdeye")
        if key and key != "PLACEHOLDER_UPDATE_ME":
            url = f"https://public-api.birdeye.so/public/price?address={token_address}"
            data = _request(url, headers={"X-API-KEY": key})
            result["sources"]["birdeye"] = data
    except Exception as e: result["errors"].append({"source": "birdeye", "error": str(e)})

    result["has_data"] = len(result["sources"]) > 0
    return result


# ═══════════════════════════════════════════════════════════
# TRENDING TOKENS FALLBACK
# ═══════════════════════════════════════════════════════════

def get_trending_tokens(chain: str = "solana") -> Dict[str, Any]:
    """Get trending tokens — tries multiple sources."""
    result = {"chain": chain, "sources": {}, "errors": []}

    try:
        from app.services.gmgn_service import get_trending
        data = get_trending(chain[:3] if chain == "solana" else chain)
        if "error" not in data:
            result["sources"]["gmgn"] = data; result["tokens"] = data.get("tokens", []); result["source"] = "gmgn"; return result
    except Exception as e: result["errors"].append({"source": "gmgn", "error": str(e)})

    try:
        data = _request("https://api.coingecko.com/api/v3/search/trending")
        result["sources"]["coingecko"] = data; result["tokens"] = [c["item"] for c in data.get("coins", [])]; result["source"] = "coingecko"; return result
    except Exception as e: result["errors"].append({"source": "coingecko", "error": str(e)})

    return result


# ═══════════════════════════════════════════════════════════
# WALLET ANALYSIS — ALL SOURCES
# ═══════════════════════════════════════════════════════════

def get_wallet_full_analysis(address: str, chain: str = "solana") -> Dict[str, Any]:
    """Comprehensive wallet analysis using ALL available sources."""
    result = {"address": address, "chain": chain, "sources": {}, "errors": []}

    # Solana-specific
    if chain == "solana":
        try:
            from app.services.solscan_service import get_account, get_account_transactions
            result["sources"]["solscan_account"] = get_account(address)
            result["sources"]["solscan_txs"] = get_account_transactions(address)
        except Exception as e: result["errors"].append({"source": "solscan", "error": str(e)})

    # Alchemy (multi-chain)
    try:
        from app.services.alchemy_service import get_token_balances, get_nfts_for_owner, get_asset_transfers
        result["sources"]["alchemy_balances"] = get_token_balances(address, chain)
        result["sources"]["alchemy_nfts"] = get_nfts_for_owner(address, chain)
        result["sources"]["alchemy_transfers"] = get_asset_transfers(address, chain)
    except Exception as e: result["errors"].append({"source": "alchemy", "error": str(e)})

    # Arkham intel
    try:
        from app.services.arkham_service import get_address_intel
        result["sources"]["arkham"] = get_address_intel(address)
    except Exception as e: result["errors"].append({"source": "arkham", "error": str(e)})

    # Nansen labels
    try:
        from app.services.nansen_service import get_wallet_labels
        result["sources"]["nansen"] = get_wallet_labels(address)
    except Exception as e: result["errors"].append({"source": "nansen", "error": str(e)})

    # Etherscan / blockscan
    try:
        from app.services.etherscan_service import get_account_balance
        result["sources"]["etherscan_balance"] = get_account_balance(address, chain)
    except Exception as e: result["errors"].append({"source": "etherscan", "error": str(e)})

    # Moralis
    try:
        key = get_crypto_key("moralis")
        if key and key != "PLACEHOLDER_UPDATE_ME":
            url = f"https://deep-index.moralis.io/api/v2/{address}/nft?chain={chain}"
            result["sources"]["moralis_nfts"] = _request(url, headers={"X-API-Key": key})
    except Exception as e: result["errors"].append({"source": "moralis", "error": str(e)})

    # MCP servers
    try:
        from app.services.mcp_servers import get_wallet_analysis
        result["sources"]["mcp"] = get_wallet_analysis(address, chain)
    except Exception as e: result["errors"].append({"source": "mcp", "error": str(e)})

    result["has_data"] = len(result["sources"]) > 0
    return result
