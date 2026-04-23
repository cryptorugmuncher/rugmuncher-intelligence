"""
Alchemy API Service
===================
Multi-chain data: ETH, SOL, Base, Polygon, Arbitrum, Optimism
Token balances, transfers, NFTs, transaction history, gas prices
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import urllib.request

from app.services.vault_keys import get_secret

logger = logging.getLogger("alchemy")

ALCHEMY_CHAINS = {
    "ethereum": "eth-mainnet",
    "base": "base-mainnet",
    "polygon": "polygon-mainnet",
    "arbitrum": "arb-mainnet",
    "optimism": "opt-mainnet",
}


def _get_key() -> str:
    key = os.getenv("ALCHEMY_API_KEY", "")
    if not key:
        key = get_secret("crypto/alchemy", "api_key") or ""
    return key


def _request(path: str, payload: Optional[Dict] = None, chain: str = "ethereum") -> Dict[str, Any]:
    api_key = _get_key()
    network = ALCHEMY_CHAINS.get(chain, "eth-mainnet")
    url = f"https://{network}.g.alchemy.com/v2/{api_key}{path}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if payload else "GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


# ═══════════════════════════════════════════════════════════
# TOKEN DATA
# ═══════════════════════════════════════════════════════════

def get_token_balances(address: str, chain: str = "ethereum") -> Dict[str, Any]:
    """Get ERC20 token balances for an address."""
    try:
        return _request("", payload={
            "id": 1, "jsonrpc": "2.0",
            "method": "alchemy_getTokenBalances",
            "params": [address, "erc20"]
        }, chain=chain)
    except Exception as e:
        logger.error(f"Alchemy token balances failed: {e}")
        return {"error": str(e)}


def get_token_metadata(contract: str, chain: str = "ethereum") -> Dict[str, Any]:
    """Get token metadata (name, symbol, decimals, logo)."""
    try:
        return _request("", payload={
            "id": 1, "jsonrpc": "2.0",
            "method": "alchemy_getTokenMetadata",
            "params": [contract]
        }, chain=chain)
    except Exception as e:
        logger.error(f"Alchemy token metadata failed: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# TRANSACTIONS
# ═══════════════════════════════════════════════════════════

def get_asset_transfers(address: str, chain: str = "ethereum", category: List[str] = None) -> Dict[str, Any]:
    """Get asset transfers (ERC20, ERC721, ERC1155, external)."""
    try:
        return _request("", payload={
            "id": 1, "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [{
                "fromBlock": "0x0",
                "toBlock": "latest",
                "fromAddress": address,
                "category": category or ["erc20", "external"],
                "withMetadata": True,
                "excludeZeroValue": True,
                "maxCount": "0x64",
            }]
        }, chain=chain)
    except Exception as e:
        logger.error(f"Alchemy transfers failed: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# NFTs
# ═══════════════════════════════════════════════════════════

def get_nfts_for_owner(address: str, chain: str = "ethereum") -> Dict[str, Any]:
    """Get all NFTs owned by an address."""
    try:
        return _request(f"/getNFTs?owner={address}&withMetadata=true&pageSize=100", chain=chain)
    except Exception as e:
        logger.error(f"Alchemy NFTs failed: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# SOLANA (Alchemy Solana API)
# ═══════════════════════════════════════════════════════════

def get_solana_account(address: str) -> Dict[str, Any]:
    """Get Solana account info via Alchemy."""
    try:
        api_key = _get_key()
        url = f"https://solana-mainnet.g.alchemy.com/v2/{api_key}"
        payload = {"id": 1, "jsonrpc": "2.0", "method": "getAccountInfo", "params": [address, {"encoding": "jsonParsed"}]}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.error(f"Alchemy Solana failed: {e}")
        return {"error": str(e)}
