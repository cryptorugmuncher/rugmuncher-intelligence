"""Crypto MCP Server Integrations — https://github.com/badkk/awesome-crypto-mcp-servers"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import urllib.request

logger = logging.getLogger("mcp_servers")

MCP_SERVERS = {
    "dexpaprika": {"name": "DexPaprika", "description": "Real-time DEX data for 5M+ tokens", "base_url": "https://api.dexpaprika.com", "endpoints": {"token_price": "/tokens/{chain}/{address}", "pools": "/pools/{chain}", "search": "/search"}, "capabilities": ["prices", "liquidity", "pools"], "enabled": True},
    "bankless_onchain": {"name": "Bankless Onchain", "description": "ERC20, tx history, contract state", "base_url": "https://onchain.bankless.com/api", "endpoints": {"token_balances": "/balances/{address}", "transactions": "/transactions/{address}", "contract_state": "/contract/{address}/state"}, "capabilities": ["balances", "transactions", "contract_state"], "enabled": True},
    "crypto_fear_greed": {"name": "Crypto Fear & Greed", "description": "Real-time Fear & Greed Index", "base_url": "https://api.alternative.me", "endpoints": {"current": "/fng/", "historical": "/fng/?limit={limit}"}, "capabilities": ["sentiment", "market_mood"], "enabled": True},
    "cryptopanic": {"name": "CryptoPanic", "description": "Latest crypto news", "base_url": "https://cryptopanic.com/api/v1", "endpoints": {"posts": "/posts/", "trending": "/posts/?filter=trending"}, "capabilities": ["news", "sentiment"], "api_key_env": "CRYPTOPANIC_API_KEY", "enabled": True},
    "whale_tracker": {"name": "Whale Tracker", "description": "Track whale transactions", "base_url": "https://api.whale-alert.io", "endpoints": {"transactions": "/v1/transactions", "status": "/v1/status"}, "capabilities": ["whales", "transactions"], "api_key_env": "WHALE_ALERT_API_KEY", "enabled": True},
    "evm_chains": {"name": "EVM MCP Server", "description": "30+ EVM networks", "base_url": "https://evm-mcp-server.vercel.app/api", "endpoints": {"balance": "/balance/{chain}/{address}", "token_info": "/token/{chain}/{address}", "nft_holdings": "/nfts/{chain}/{address}"}, "capabilities": ["balances", "tokens", "nfts", "contracts"], "enabled": True},
    "solana_agent_kit": {"name": "Solana Agent Kit", "description": "Solana blockchain: 40+ protocol actions", "base_url": "https://solana-agent-kit.sendai.ai/api", "endpoints": {"account": "/account/{address}", "token_accounts": "/token-accounts/{address}", "transactions": "/transactions/{address}"}, "capabilities": ["solana", "transactions", "tokens"], "enabled": True},
    "heurist_mesh": {"name": "Heurist Mesh Agent", "description": "Web3 AI agents for analysis and security", "base_url": "https://mesh.heurist.ai/api", "endpoints": {"analyze_contract": "/analyze/contract", "token_metrics": "/metrics/token", "security_score": "/security/score"}, "capabilities": ["ai_analysis", "security", "token_metrics"], "api_key_env": "HEURIST_API_KEY", "enabled": True},
}

def _mcp_request(server: str, endpoint: str, method: str = "GET", payload: Optional[Dict] = None, path_params: Optional[Dict] = None) -> Dict[str, Any]:
    cfg = MCP_SERVERS.get(server)
    if not cfg or not cfg.get("enabled"):
        return {"error": f"MCP server {server} not found or disabled"}
    url_template = cfg["base_url"] + cfg["endpoints"].get(endpoint, endpoint)
    url = url_template.format(**path_params) if path_params else url_template
    headers = {"Content-Type": "application/json"}
    api_key_env = cfg.get("api_key_env")
    if api_key_env:
        api_key = os.getenv(api_key_env, "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_token_price_multi_source(token_address: str, chain: str = "solana") -> Dict[str, Any]:
    result = {"sources": {}, "errors": [], "token_address": token_address, "chain": chain}
    try:
        price = _mcp_request("dexpaprika", "token_price", path_params={"chain": chain, "address": token_address})
        result["sources"]["dexpaprika"] = price; result["price"] = price.get("price_usd"); result["source"] = "dexpaprika"; return result
    except Exception as e: result["errors"].append({"source": "dexpaprika", "error": str(e)})
    try:
        price = _mcp_request("evm_chains", "token_info", path_params={"chain": chain, "address": token_address})
        result["sources"]["evm_chains"] = price; result["price"] = price.get("price"); result["source"] = "evm_chains"; return result
    except Exception as e: result["errors"].append({"source": "evm_chains", "error": str(e)})
    try:
        from app.services.crypto.coingecko import get_token_data
        cg = get_token_data(token_address)
        if cg: result["sources"]["coingecko"] = cg; result["price"] = cg.get("market_data", {}).get("current_price", {}).get("usd"); result["source"] = "coingecko"; return result
    except Exception as e: result["errors"].append({"source": "coingecko", "error": str(e)})
    return result

def get_market_sentiment() -> Dict[str, Any]:
    result = {"sources": {}, "errors": []}
    try:
        fng = _mcp_request("crypto_fear_greed", "current")
        result["sources"]["fear_greed"] = fng
        result["fear_greed_index"] = fng.get("data", [{}])[0].get("value")
        result["sentiment"] = fng.get("data", [{}])[0].get("value_classification")
    except Exception as e: result["errors"].append({"source": "fear_greed", "error": str(e)})
    try:
        news = _mcp_request("cryptopanic", "trending")
        result["sources"]["cryptopanic"] = news
        result["trending_news"] = news.get("results", [])[:5]
    except Exception as e: result["errors"].append({"source": "cryptopanic", "error": str(e)})
    return result

def get_whale_activity() -> Dict[str, Any]:
    try: return _mcp_request("whale_tracker", "transactions")
    except Exception as e: logger.error(f"Whale tracker failed: {e}"); return {"error": str(e)}

def get_wallet_analysis(address: str, chain: str = "solana") -> Dict[str, Any]:
    result = {"address": address, "chain": chain, "sources": {}, "errors": []}
    if chain == "solana":
        try: result["sources"]["solana_agent_kit"] = _mcp_request("solana_agent_kit", "account", path_params={"address": address})
        except Exception as e: result["errors"].append({"source": "solana_agent_kit", "error": str(e)})
    try: result["sources"]["evm_chains"] = _mcp_request("evm_chains", "balance", path_params={"chain": chain, "address": address})
    except Exception as e: result["errors"].append({"source": "evm_chains", "error": str(e)})
    try: result["sources"]["bankless"] = _mcp_request("bankless_onchain", "token_balances", path_params={"address": address})
    except Exception as e: result["errors"].append({"source": "bankless", "error": str(e)})
    try: result["sources"]["heurist"] = _mcp_request("heurist_mesh", "analyze_contract", payload={"address": address, "chain": chain})
    except Exception as e: result["errors"].append({"source": "heurist", "error": str(e)})
    return result

def get_all_mcp_servers() -> List[Dict[str, Any]]:
    return [{"id": k, "name": v["name"], "description": v["description"], "capabilities": v["capabilities"], "enabled": v["enabled"]} for k, v in MCP_SERVERS.items()]
