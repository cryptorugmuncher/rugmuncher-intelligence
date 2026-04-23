#!/usr/bin/env python3
"""
Moralis Multi-Chain Intelligence Client
Covers Solana + EVM chains with cross-chain portfolio, whale detection,
token discovery, and safety analysis.

Free Tier: 3,000 CU/day, 25 CU/sec
Strategic CU budgeting per call to stay within limits.
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger("moralis")

# ─── CONFIG ──────────────────────────────────────────────────────────────

API_KEY = os.getenv("MORALIS_API_KEY", "").strip()
BASE_URL = "https://deep-index.moralis.io/api/v2.2"

# Chain name mapping
SOLANA_CHAINS = ["solana", "devnet"]
EVM_CHAINS = {
    "eth": "0x1",
    "polygon": "0x89",
    "bsc": "0x38",
    "arbitrum": "0xa4b1",
    "base": "0x2105",
    "optimism": "0xa",
    "avalanche": "0xa86a",
    "fantom": "0xfa",
    "linea": "0xe708",
    "blast": "0x13e31",
}

ALL_CHAINS = ["solana"] + list(EVM_CHAINS.keys())

# CU cost estimates (free tier: 3000/day)
CU_COSTS = {
    "sol_balance": 5,
    "sol_portfolio": 15,
    "sol_tokens": 10,
    "sol_nfts": 10,
    "evm_balance": 5,
    "evm_tokens": 10,
    "evm_nfts": 10,
    "evm_txs": 10,
    "token_price": 5,
    "token_metadata": 5,
    "token_security": 10,
    "wallet_history": 15,
    "search_tokens": 10,
}


@dataclass
class ChainPortfolio:
    chain: str
    native_balance: float
    native_balance_usd: float
    token_count: int
    nft_count: int
    total_value_usd: float
    tokens: List[Dict[str, Any]]
    risk_flags: List[str] = field(default_factory=list)


@dataclass
class CrossChainProfile:
    wallet_address: str
    chains_found: List[str]
    chain_portfolios: List[ChainPortfolio]
    total_value_usd: float
    total_tokens: int
    total_nfts: int
    risk_score: int
    risk_level: str
    tags: List[str]
    last_active: Optional[datetime]
    analysis_summary: str


@dataclass
class TokenDiscovery:
    address: str
    chain: str
    name: str
    symbol: str
    price_usd: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    security_score: Optional[int]
    is_verified: bool
    holder_count: int
    liquidity_usd: float
    risk_flags: List[str]


class MoralisClient:
    """Multi-chain intelligence via Moralis with CU-aware rate limiting."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self._cu_used_today = 0
        self._cu_limit = 3000  # Free tier daily limit
        self._rate_limiter = asyncio.Semaphore(5)  # Max 5 concurrent
        self._last_reset = datetime.utcnow()
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = 300  # 5 min cache

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"X-API-Key": self.api_key, "Accept": "application/json"}
            )
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def _check_cu(self, cost: int) -> bool:
        """Check if we have enough CU remaining."""
        if datetime.utcnow().date() != self._last_reset.date():
            self._cu_used_today = 0
            self._last_reset = datetime.utcnow()
        return (self._cu_used_today + cost) <= self._cu_limit

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached response if fresh."""
        if key in self._cache:
            data, ts = self._cache[key]
            if (datetime.utcnow() - ts).total_seconds() < self.cache_ttl:
                return data
        return None

    async def _get(self, path: str, params: dict = None, cu_cost: int = 5) -> Dict[str, Any]:
        """Make a cached, CU-tracked GET request."""
        cache_key = f"{path}:{str(params)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self._check_cu(cu_cost):
            return {"error": "Daily CU limit reached", "cu_used": self._cu_used_today}

        async with self._rate_limiter:
            s = await self._get_session()
            try:
                async with s.get(f"{BASE_URL}{path}", params=params or {}) as resp:
                    self._cu_used_today += cu_cost
                    if resp.status == 200:
                        data = await resp.json()
                        self._cache[cache_key] = (data, datetime.utcnow())
                        return data
                    return {"error": f"HTTP {resp.status}", "detail": await resp.text()}
            except Exception as e:
                return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════════════
    # SOLANA ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════

    async def sol_balance(self, wallet: str, network: str = "mainnet") -> Dict[str, Any]:
        """Get SOL balance + USD value."""
        return await self._get(
            f"/account/{network}/{wallet}/balance",
            cu_cost=CU_COSTS["sol_balance"]
        )

    async def sol_portfolio(self, wallet: str, network: str = "mainnet") -> Dict[str, Any]:
        """Full portfolio with USD valuations."""
        return await self._get(
            f"/account/{network}/{wallet}/portfolio",
            cu_cost=CU_COSTS["sol_portfolio"]
        )

    async def sol_tokens(self, wallet: str, network: str = "mainnet") -> Dict[str, Any]:
        """SPL token balances with metadata."""
        return await self._get(
            f"/account/{network}/{wallet}/tokens",
            cu_cost=CU_COSTS["sol_tokens"]
        )

    async def sol_nfts(self, wallet: str, network: str = "mainnet") -> Dict[str, Any]:
        """NFT holdings on Solana."""
        return await self._get(
            f"/account/{network}/{wallet}/nft",
            cu_cost=CU_COSTS["sol_nfts"]
        )

    # ═══════════════════════════════════════════════════════════════════
    # EVM ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════

    async def evm_balance(self, wallet: str, chain: str = "eth") -> Dict[str, Any]:
        """Get native balance for EVM chain."""
        chain_hex = EVM_CHAINS.get(chain, "0x1")
        return await self._get(
            f"/{wallet}/balance",
            {"chain": chain_hex},
            cu_cost=CU_COSTS["evm_balance"]
        )

    async def evm_tokens(self, wallet: str, chain: str = "eth") -> Dict[str, Any]:
        """ERC20 token balances."""
        chain_hex = EVM_CHAINS.get(chain, "0x1")
        return await self._get(
            f"/{wallet}/erc20",
            {"chain": chain_hex},
            cu_cost=CU_COSTS["evm_tokens"]
        )

    async def evm_nfts(self, wallet: str, chain: str = "eth") -> Dict[str, Any]:
        """NFT holdings on EVM."""
        chain_hex = EVM_CHAINS.get(chain, "0x1")
        return await self._get(
            f"/{wallet}/nft",
            {"chain": chain_hex, "format": "decimal", "limit": 50},
            cu_cost=CU_COSTS["evm_nfts"]
        )

    async def evm_transactions(self, wallet: str, chain: str = "eth", limit: int = 50) -> Dict[str, Any]:
        """Transaction history."""
        chain_hex = EVM_CHAINS.get(chain, "0x1")
        return await self._get(
            f"/{wallet}",
            {"chain": chain_hex, "limit": limit},
            cu_cost=CU_COSTS["evm_txs"]
        )

    # ═══════════════════════════════════════════════════════════════════
    # TOKEN INTELLIGENCE (Universal)
    # ═══════════════════════════════════════════════════════════════════

    async def token_price(self, token_address: str, chain: str = "eth", include_exchanges: bool = False) -> Dict[str, Any]:
        """Get token price + 24h change."""
        chain_hex = EVM_CHAINS.get(chain, "0x1")
        params = {"chain": chain_hex, "include_exchanges": str(include_exchanges).lower()}
        return await self._get(
            f"/erc20/{token_address}/price",
            params,
            cu_cost=CU_COSTS["token_price"]
        )

    async def token_metadata(self, token_address: str, chain: str = "eth") -> Dict[str, Any]:
        """Token metadata."""
        chain_hex = EVM_CHAINS.get(chain, "0x1")
        return await self._get(
            f"/erc20/metadata",
            {"chain": chain_hex, "addresses": token_address},
            cu_cost=CU_COSTS["token_metadata"]
        )

    async def search_tokens(self, query: str) -> List[Dict[str, Any]]:
        """Search tokens across all chains."""
        result = await self._get(
            "/tokens/search",
            {"q": query, "limit": 20},
            cu_cost=CU_COSTS["search_tokens"]
        )
        return result if isinstance(result, list) else []

    # ═══════════════════════════════════════════════════════════════════
    # CROSS-CHAIN INTELLIGENCE (Our Original Features)
    # ═══════════════════════════════════════════════════════════════════

    async def cross_chain_profile(self, wallet: str) -> CrossChainProfile:
        """
        Build a unified cross-chain profile for any wallet.
        Checks Solana + top EVM chains simultaneously.
        """
        logger.info(f"Building cross-chain profile for {wallet}")

        portfolios = []
        total_value = 0
        total_tokens = 0
        total_nfts = 0
        chains_found = []

        # Solana check (if wallet is Solana format)
        if len(wallet) in [43, 44]:
            try:
                portfolio = await self.sol_portfolio(wallet)
                if "result" in portfolio or "nativeBalance" in portfolio:
                    sol_port = self._parse_sol_portfolio(portfolio, wallet)
                    portfolios.append(sol_port)
                    total_value += sol_port.total_value_usd
                    total_tokens += sol_port.token_count
                    total_nfts += sol_port.nft_count
                    chains_found.append("solana")
            except Exception as e:
                logger.debug(f"Solana check failed: {e}")

        # EVM checks (if wallet is EVM format)
        elif wallet.startswith("0x") and len(wallet) == 42:
            evm_tasks = []
            for chain_name in ["eth", "polygon", "bsc", "arbitrum", "base"]:
                evm_tasks.append(self._check_evm_chain(wallet, chain_name))

            evm_results = await asyncio.gather(*evm_tasks, return_exceptions=True)
            for chain_name, result in zip(["eth", "polygon", "bsc", "arbitrum", "base"], evm_results):
                if isinstance(result, ChainPortfolio):
                    portfolios.append(result)
                    total_value += result.total_value_usd
                    total_tokens += result.token_count
                    total_nfts += result.nft_count
                    if result.total_value_usd > 0:
                        chains_found.append(chain_name)

        # Risk analysis
        risk_flags = []
        tags = []
        for p in portfolios:
            risk_flags.extend(p.risk_flags)
        risk_flags = list(set(risk_flags))

        if total_value > 100000:
            tags.append("whale")
        elif total_value > 10000:
            tags.append("heavy_holder")
        if len(chains_found) > 2:
            tags.append("multi_chain")
        if total_tokens > 50:
            tags.append("degen_diverse")

        risk_score = min(100, len(risk_flags) * 20 + (50 if total_value > 100000 else 0))
        risk_level = "CRITICAL" if risk_score >= 80 else "HIGH" if risk_score >= 60 else "ELEVATED" if risk_score >= 40 else "LOW" if risk_score >= 20 else "SAFE"

        return CrossChainProfile(
            wallet_address=wallet,
            chains_found=chains_found,
            chain_portfolios=portfolios,
            total_value_usd=round(total_value, 2),
            total_tokens=total_tokens,
            total_nfts=total_nfts,
            risk_score=risk_score,
            risk_level=risk_level,
            tags=tags,
            last_active=datetime.utcnow(),
            analysis_summary=self._generate_summary(wallet, chains_found, total_value, tags),
        )

    def _parse_sol_portfolio(self, data: Dict, wallet: str) -> ChainPortfolio:
        """Parse Moralis Solana portfolio into our format."""
        result = data if isinstance(data, dict) else {}
        native = result.get("nativeBalance", {})
        sol_amount = float(native.get("solana", 0))
        sol_usd = float(native.get("value", {}).get("usd", 0)) if isinstance(native.get("value"), dict) else 0

        tokens = result.get("tokens", [])
        token_value = sum(
            float(t.get("value", {}).get("usd", 0)) if isinstance(t.get("value"), dict) else 0
            for t in tokens
        )

        risk_flags = []
        if sol_amount < 0.01 and len(tokens) > 0:
            risk_flags.append("Low SOL for gas — may be drained soon")

        return ChainPortfolio(
            chain="solana",
            native_balance=round(sol_amount, 6),
            native_balance_usd=round(sol_usd, 2),
            token_count=len(tokens),
            nft_count=0,
            total_value_usd=round(sol_usd + token_value, 2),
            tokens=[{"symbol": t.get("symbol", "?"), "balance": t.get("amount", 0),
                     "usd_value": t.get("value", {}).get("usd", 0) if isinstance(t.get("value"), dict) else 0}
                    for t in tokens[:20]],
            risk_flags=risk_flags,
        )

    async def _check_evm_chain(self, wallet: str, chain: str) -> ChainPortfolio:
        """Check a single EVM chain for portfolio data."""
        try:
            balance_data = await self.evm_balance(wallet, chain)
            tokens_data = await self.evm_tokens(wallet, chain)

            balance_eth = float(balance_data.get("balance", 0))
            balance_usd = 0  # Moralis free may not include USD

            tokens = tokens_data if isinstance(tokens_data, list) else []
            token_count = len(tokens)

            # Estimate total value (rough)
            total_value = balance_usd

            risk_flags = []
            if balance_eth < 0.001 and token_count > 0:
                risk_flags.append(f"Low native {chain.upper()} for gas")

            return ChainPortfolio(
                chain=chain,
                native_balance=round(balance_eth, 6),
                native_balance_usd=round(balance_usd, 2),
                token_count=token_count,
                nft_count=0,
                total_value_usd=round(total_value, 2),
                tokens=[{"symbol": t.get("symbol", "?"), "balance": t.get("balance", "0")[:20]} for t in tokens[:10]],
                risk_flags=risk_flags,
            )
        except Exception as e:
            logger.debug(f"EVM {chain} check failed: {e}")
            return ChainPortfolio(
                chain=chain, native_balance=0, native_balance_usd=0,
                token_count=0, nft_count=0, total_value_usd=0, tokens=[],
                risk_flags=[],
            )

    def _generate_summary(self, wallet: str, chains: List[str], value: float, tags: List[str]) -> str:
        """Generate human-readable summary."""
        parts = [f"Wallet active on {len(chains)} chain(s): {', '.join(chains)}."]
        if value > 0:
            parts.append(f"Estimated total value: ${value:,.2f}.")
        if tags:
            parts.append(f"Tags: {', '.join(tags)}.")
        return " ".join(parts)

    # ═══════════════════════════════════════════════════════════════════
    # MULTI-CHAIN WHALE DETECTOR
    # ═══════════════════════════════════════════════════════════════════

    async def multi_chain_whale_scan(self, min_value_usd: float = 50000) -> List[Dict[str, Any]]:
        """Scan tracked wallets across chains for whale activity."""
        # This would use a stored watchlist - simplified version
        return [{"note": "Configure wallet watchlist to enable multi-chain whale scanning"}]

    # ═══════════════════════════════════════════════════════════════════
    # TOKEN DISCOVERY (Trending across chains)
    # ═══════════════════════════════════════════════════════════════════

    async def discover_tokens(self, query: str = None, chain: str = None) -> List[TokenDiscovery]:
        """Discover trending tokens across chains."""
        if query:
            results = await self.search_tokens(query)
        else:
            # Default: search for trending terms
            results = []
            for term in ["meme", "AI", "game", "defi"]:
                r = await self.search_tokens(term)
                if isinstance(r, list):
                    results.extend(r)
                await asyncio.sleep(0.2)  # Rate limit

        tokens = []
        for item in results[:20]:
            t = TokenDiscovery(
                address=item.get("tokenAddress", ""),
                chain=item.get("chainName", "unknown"),
                name=item.get("name", "Unknown"),
                symbol=item.get("symbol", "?"),
                price_usd=float(item.get("priceUsd", 0) or 0),
                market_cap=float(item.get("marketCap", 0) or 0),
                volume_24h=float(item.get("volume24h", 0) or 0),
                price_change_24h=float(item.get("priceChange24h", 0) or 0),
                security_score=None,
                is_verified=item.get("verified", False),
                holder_count=int(item.get("holderCount", 0) or 0),
                liquidity_usd=float(item.get("liquidityUsd", 0) or 0),
                risk_flags=[],
            )

            # Add risk flags
            if t.liquidity_usd < 10000:
                t.risk_flags.append("Low liquidity")
            if t.holder_count < 100:
                t.risk_flags.append("Very few holders")
            if not t.is_verified:
                t.risk_flags.append("Unverified contract")

            tokens.append(t)

        # Sort by market cap
        tokens.sort(key=lambda x: x.market_cap, reverse=True)
        return tokens

    # ═══════════════════════════════════════════════════════════════════
    # STATUS
    # ═══════════════════════════════════════════════════════════════════

    def get_cu_status(self) -> Dict[str, Any]:
        """Get current CU usage."""
        remaining = self._cu_limit - self._cu_used_today
        pct_used = (self._cu_used_today / self._cu_limit) * 100
        return {
            "cu_used_today": self._cu_used_today,
            "cu_limit": self._cu_limit,
            "cu_remaining": remaining,
            "pct_used": round(pct_used, 1),
            "status": "healthy" if pct_used < 80 else "warning" if pct_used < 95 else "critical",
        }


# ─── Singleton ───────────────────────────────────────────────────────────

_client: Optional[MoralisClient] = None

def get_moralis_client() -> MoralisClient:
    global _client
    if _client is None:
        _client = MoralisClient()
    return _client
