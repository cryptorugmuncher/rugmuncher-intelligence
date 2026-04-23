#!/usr/bin/env python3
"""
GMGN Full-Feature Integration — All 6 Skill Modules for RMI
═══════════════════════════════════════════════════════════════

Based on GMGN Skills Wiki (github.com/GMGNAI/gmgn-skills):
  1. gmgn-market     — K-line, trending, trenches, signals
  2. gmgn-swap       — Market/limit orders, TP/SL, trailing, multi-wallet
  3. gmgn-token      — Token info, security, top holders/traders
  4. gmgn-portfolio  — Wallet holdings, P&L, tx history
  5. gmgn-track      — Real-time wallet tracking, KOL trades, smart money
  6. gmgn-cooking    — One-command buy + TP/SL strategy orders

Chains: Solana, BSC, Base
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

logger = logging.getLogger("gmgn-full")

# ─── CONFIG ──────────────────────────────────────────────────────────────

API_KEY = os.getenv("GMGN_API_KEY", "").strip()
BASE_URL = "https://gmgn.ai/defi/router/v1"

# Chain configurations
CHAIN_CONFIG = {
    "sol": {
        "name": "Solana",
        "native": "SOL",
        "native_address": "So11111111111111111111111111111111111111112",
        "usdc": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "dex": ["pump.fun", "Raydium", "Jupiter"],
    },
    "bsc": {
        "name": "BSC",
        "native": "BNB",
        "native_address": "0x0000000000000000000000000000000000000000",
        "usdc": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
        "dex": ["fourmeme", "PancakeSwap"],
    },
    "base": {
        "name": "Base",
        "native": "ETH",
        "native_address": "0x0000000000000000000000000000000000000000",
        "usdc": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "dex": ["letsbonk", "Uniswap V3"],
    },
}

# Safety filter defaults per chain
DEFAULT_FILTERS = {
    "sol": "renounced frozen",
    "bsc": "not_honeypot verified renounced",
    "base": "not_honeypot verified renounced",
}

KLINE_RESOLUTIONS = ["1m", "5m", "15m", "1h", "4h", "1d"]
TRENDING_INTERVALS = ["1m", "5m", "1h", "6h", "24h"]


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class KlineData:
    """OHLCV candlestick data."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume_usd: float  # USD value of trades
    amount_tokens: float  # Token units traded

@dataclass
class TrendingToken:
    """Token from trending/trenches lists."""
    address: str
    chain: str
    name: str
    symbol: str
    price_usd: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    rug_ratio: float  # 0-1 rug pull likelihood
    smart_degen_count: int  # Smart money wallets holding
    renowned_count: int  # KOL wallets holding
    hot_level: int  # Trending intensity
    holder_count: int
    top_10_holder_rate: float  # % held by top 10
    dev_team_hold_rate: float  # % held by dev team
    is_honeypot: bool
    is_verified: bool
    renounced_mint: bool
    renounced_freeze: bool
    launchpad: Optional[str]  # pump.fun, fourmeme, etc.
    launch_time: Optional[datetime]
    safety_score: int  # 0-100 (our calc)

@dataclass
class TokenSecurity:
    """Comprehensive token security analysis."""
    address: str
    chain: str
    name: str
    symbol: str
    is_honeypot: bool
    buy_tax: float
    sell_tax: float
    transfer_tax: float
    max_buy: float
    max_sell: float
    renounced_mint: bool
    renounced_freeze: bool
    renounced_transfer: bool
    is_mutable: bool
    holder_count: int
    top_10_holder_rate: float
    dev_team_hold_rate: float
    liquidity_locked: bool
    liquidity_lock_duration: Optional[int]  # days
    contract_verified: bool
    rug_ratio: float
    safety_score: int
    risk_flags: List[str]

@dataclass
class TopHolder:
    """Top holder or trader for a token."""
    address: str
    balance: float
    balance_usd: float
    pct_of_supply: float
    tag: Optional[str]  # smart_degen, renowned, etc.
    is_contract: bool
    bought_at: Optional[float]
    avg_buy_price: Optional[float]
    unrealized_pnl: Optional[float]

@dataclass
class WalletPortfolio:
    """Wallet holdings and performance."""
    address: str
    chain: str
    total_value_usd: float
    total_pnl_usd: float
    total_pnl_pct: float
    token_count: int
    win_count: int
    loss_count: int
    tokens: List[Dict[str, Any]]
    recent_transactions: List[Dict[str, Any]]
    tags: List[str]  # smart_degen, renowned, etc.

@dataclass
class TrackedSignal:
    """Real-time signal from tracked wallet."""
    timestamp: datetime
    wallet_address: str
    wallet_tag: Optional[str]
    token_address: str
    token_symbol: str
    action: str  # buy, sell, add_liquidity, remove_liquidity
    amount_usd: float
    tx_signature: str
    signal_type: str  # kol_trade, smart_money, whale_move
    confidence: int  # 1-10

@dataclass
class CookingStrategy:
    """Pre-built trading strategy (cooking module)."""
    name: str
    chain: str
    token_address: str
    entry_type: str  # market, limit
    entry_price: Optional[float]
    tp_levels: List[Dict[str, Any]]  # [{"price": x, "pct": 25}, ...]
    sl_price: Optional[float]
    trailing_tp: bool
    trailing_sl: bool
    trailing_drawdown_pct: float  # e.g. 0.05 = 5% from peak
    total_tp_levels: int
    anti_mev: bool
    status: str  # pending, active, completed, cancelled


# ═══════════════════════════════════════════════════════════════════════════
# GMGN FULL CLIENT
# ═══════════════════════════════════════════════════════════════════════════

class GMGNFullClient:
    """
    Complete GMGN integration covering all 6 skill modules.
    Multi-chain: Solana, BSC, Base
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_bucket = 10  # GMGN leaky bucket
        self._rate_limit_reset = 0
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = 60  # 1 min cache for volatile data

        # Tracking state
        self._tracked_wallets: Dict[str, Dict] = {}
        self._signal_log: deque = deque(maxlen=10000)
        self._price_alerts: List[Dict] = []

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
            )
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def _get(self, path: str, params: dict = None) -> Dict[str, Any]:
        """Cached, rate-limited GET."""
        cache_key = f"GET:{path}:{str(params)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        s = await self._get_session()
        try:
            async with s.get(f"{BASE_URL}{path}", params=params) as resp:
                if resp.status == 429:
                    reset = resp.headers.get("X-RateLimit-Reset", 0)
                    logger.warning(f"GMGN rate limited, reset at {reset}")
                    return {"error": "RATE_LIMIT", "reset_at": reset}

                data = await resp.json() if resp.status == 200 else {"error": f"HTTP {resp.status}"}
                if resp.status == 200:
                    self._cache[cache_key] = (data, datetime.utcnow())
                return data
        except Exception as e:
            return {"error": str(e)}

    async def _post(self, path: str, json_body: dict = None) -> Dict[str, Any]:
        """Rate-limited POST."""
        s = await self._get_session()
        try:
            async with s.post(f"{BASE_URL}{path}", json=json_body) as resp:
                if resp.status == 429:
                    reset = resp.headers.get("X-RateLimit-Reset", 0)
                    return {"error": "RATE_LIMIT", "reset_at": reset}
                return await resp.json() if resp.status in (200, 201) else {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_cached(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, ts = self._cache[key]
            if (datetime.utcnow() - ts).total_seconds() < self.cache_ttl:
                return data
        return None

    # ═══════════════════════════════════════════════════════════════════
    # MODULE 1: MARKET — K-line, Trending, Trenches, Signals
    # ═══════════════════════════════════════════════════════════════════

    async def get_kline(self, chain: str, token_address: str,
                        resolution: str = "1h",
                        from_ts: Optional[int] = None,
                        to_ts: Optional[int] = None) -> List[KlineData]:
        """
        Get OHLCV candlestick data for a token.
        Resolutions: 1m, 5m, 15m, 1h, 4h, 1d
        """
        params = {
            "chain": chain,
            "address": token_address,
            "resolution": resolution,
        }
        if from_ts:
            params["from"] = from_ts
        if to_ts:
            params["to"] = to_ts

        result = await self._get("/sol/kline", params)
        if "error" in result:
            return []

        klines = []
        for item in result.get("data", []):
            klines.append(KlineData(
                timestamp=item.get("t", 0),
                open=float(item.get("o", 0)),
                high=float(item.get("h", 0)),
                low=float(item.get("l", 0)),
                close=float(item.get("c", 0)),
                volume_usd=float(item.get("v", 0)),
                amount_tokens=float(item.get("a", 0)),
            ))
        return klines

    async def get_trending(self, chain: str = "sol",
                          interval: str = "24h",
                          limit: int = 50) -> List[TrendingToken]:
        """
        Get trending tokens by volume.
        Intervals: 1m, 5m, 1h, 6h, 24h
        """
        params = {
            "chain": chain,
            "interval": interval,
            "limit": limit,
        }

        result = await self._get("/trending", params)
        if "error" in result:
            return []

        tokens = []
        for item in result.get("data", []):
            t = self._parse_token_data(item, chain)
            tokens.append(t)

        # Sort by hot_level descending
        tokens.sort(key=lambda x: x.hot_level, reverse=True)
        return tokens

    async def get_trenches(self, chain: str = "sol",
                           limit: int = 50,
                           filter_tags: Optional[str] = None) -> List[TrendingToken]:
        """
        Get newly launched tokens (trenches).
        Default filters applied per chain unless overridden.
        """
        params = {
            "chain": chain,
            "limit": limit,
        }
        if filter_tags:
            params["filter"] = filter_tags

        result = await self._get("/trenches", params)
        if "error" in result:
            return []

        tokens = []
        for item in result.get("data", []):
            t = self._parse_token_data(item, chain)
            t.launchpad = item.get("launchpad")
            tokens.append(t)

        return tokens

    async def get_signal(self, chain: str = "sol") -> List[Dict[str, Any]]:
        """Get token trading signals."""
        result = await self._get("/signal", {"chain": chain})
        return result.get("data", []) if "error" not in result else []

    def _parse_token_data(self, item: Dict, chain: str) -> TrendingToken:
        """Parse common token data fields."""
        # Calculate safety score (0-100)
        safety = 100
        risk_flags = []

        rug = float(item.get("rug_ratio", 0))
        if rug > 0.3:
            safety -= 40
            risk_flags.append(f"High rug ratio: {rug:.2f}")
        elif rug > 0.1:
            safety -= 15

        top10 = float(item.get("top_10_holder_rate", 0))
        if top10 > 0.5:
            safety -= 25
            risk_flags.append(f"Extreme concentration: {top10:.1%}")

        dev_hold = float(item.get("dev_team_hold_rate", 0))
        if dev_hold > 0.2:
            safety -= 20
            risk_flags.append(f"High dev hold: {dev_hold:.1%}")

        is_honeypot = item.get("is_honeypot", False)
        if is_honeypot:
            safety = 0
            risk_flags.append("HONEYPOT DETECTED")

        if not item.get("renounced_mint", True):
            safety -= 15
            risk_flags.append("Mint authority not renounced")

        if not item.get("renounced_freeze_account", True):
            safety -= 10
            risk_flags.append("Freeze authority not renounced")

        return TrendingToken(
            address=item.get("address", ""),
            chain=chain,
            name=item.get("name", "Unknown"),
            symbol=item.get("symbol", "?"),
            price_usd=float(item.get("price", 0) or 0),
            market_cap=float(item.get("market_cap", 0) or 0),
            volume_24h=float(item.get("volume_24h", 0) or 0),
            price_change_24h=float(item.get("price_change_24h", 0) or 0),
            rug_ratio=rug,
            smart_degen_count=int(item.get("smart_degen_count", 0)),
            renowned_count=int(item.get("renowned_count", 0)),
            hot_level=int(item.get("hot_level", 0)),
            holder_count=int(item.get("holder_count", 0)),
            top_10_holder_rate=top10,
            dev_team_hold_rate=dev_hold,
            is_honeypot=is_honeypot,
            is_verified=item.get("is_verified", False),
            renounced_mint=item.get("renounced_mint", True),
            renounced_freeze=item.get("renounced_freeze_account", True),
            launchpad=None,
            launch_time=datetime.fromtimestamp(item.get("launch_time", 0)) if item.get("launch_time") else None,
            safety_score=max(0, safety),
        )

    # ═══════════════════════════════════════════════════════════════════
    # MODULE 2: SWAP — Trading (if enabled for account)
    # ═══════════════════════════════════════════════════════════════════

    async def get_quote(self, chain: str, from_wallet: str,
                        input_token: str, output_token: str,
                        amount: int, slippage: float = 0.01) -> Dict[str, Any]:
        """Get swap quote (doesn't execute)."""
        return await self._post("/trade/quote", {
            "chain": chain,
            "from": from_wallet,
            "input_token": input_token,
            "output_token": output_token,
            "amount": str(amount),
            "slippage": str(slippage),
        })

    # ═══════════════════════════════════════════════════════════════════
    # MODULE 3: TOKEN — Security, Top Holders/Traders
    # ═══════════════════════════════════════════════════════════════════

    async def get_token_security(self, chain: str, token_address: str) -> Optional[TokenSecurity]:
        """Comprehensive token security analysis."""
        result = await self._get("/token/security", {
            "chain": chain,
            "address": token_address,
        })
        if "error" in result:
            return None

        data = result.get("data", {})

        risk_flags = []
        if data.get("is_honeypot"):
            risk_flags.append("HONEYPOT — Cannot sell")
        if float(data.get("buy_tax", 0)) > 10:
            risk_flags.append(f"High buy tax: {data['buy_tax']}%")
        if float(data.get("sell_tax", 0)) > 10:
            risk_flags.append(f"High sell tax: {data['sell_tax']}%")
        if not data.get("renounced_mint"):
            risk_flags.append("Dev can still mint tokens")
        if not data.get("liquidity_locked"):
            risk_flags.append("Liquidity not locked")

        # Calculate safety score
        safety = 100
        if data.get("is_honeypot"):
            safety = 0
        else:
            safety -= min(30, float(data.get("buy_tax", 0)) * 3)
            safety -= min(30, float(data.get("sell_tax", 0)) * 3)
            if not data.get("renounced_mint"):
                safety -= 20
            if not data.get("renounced_freeze"):
                safety -= 10
            if not data.get("liquidity_locked"):
                safety -= 15

        return TokenSecurity(
            address=token_address,
            chain=chain,
            name=data.get("name", "Unknown"),
            symbol=data.get("symbol", "?"),
            is_honeypot=data.get("is_honeypot", False),
            buy_tax=float(data.get("buy_tax", 0)),
            sell_tax=float(data.get("sell_tax", 0)),
            transfer_tax=float(data.get("transfer_tax", 0)),
            max_buy=float(data.get("max_buy_amount", 0)),
            max_sell=float(data.get("max_sell_amount", 0)),
            renounced_mint=data.get("renounced_mint", False),
            renounced_freeze=data.get("renounced_freeze", False),
            renounced_transfer=data.get("renounced_transfer", False),
            is_mutable=data.get("is_mutable", True),
            holder_count=int(data.get("holder_count", 0)),
            top_10_holder_rate=float(data.get("top_10_holder_rate", 0)),
            dev_team_hold_rate=float(data.get("dev_team_hold_rate", 0)),
            liquidity_locked=data.get("liquidity_locked", False),
            liquidity_lock_duration=data.get("liquidity_lock_duration"),
            contract_verified=data.get("contract_verified", False),
            rug_ratio=float(data.get("rug_ratio", 0)),
            safety_score=max(0, int(safety)),
            risk_flags=risk_flags,
        )

    async def get_top_holders(self, chain: str, token_address: str,
                              limit: int = 20) -> List[TopHolder]:
        """Get top holders with smart money tags."""
        result = await self._get("/token/top_holders", {
            "chain": chain,
            "address": token_address,
            "limit": limit,
        })
        if "error" in result:
            return []

        holders = []
        for item in result.get("data", []):
            holders.append(TopHolder(
                address=item.get("address", ""),
                balance=float(item.get("balance", 0)),
                balance_usd=float(item.get("balance_usd", 0)),
                pct_of_supply=float(item.get("pct_of_supply", 0)),
                tag=item.get("tag"),
                is_contract=item.get("is_contract", False),
                bought_at=item.get("bought_at"),
                avg_buy_price=item.get("avg_buy_price"),
                unrealized_pnl=item.get("unrealized_pnl"),
            ))
        return holders

    async def get_top_traders(self, chain: str, token_address: str,
                              limit: int = 20) -> List[Dict[str, Any]]:
        """Get top traders for a token."""
        result = await self._get("/token/top_traders", {
            "chain": chain,
            "address": token_address,
            "limit": limit,
        })
        return result.get("data", []) if "error" not in result else []

    # ═══════════════════════════════════════════════════════════════════
    # MODULE 4: PORTFOLIO — Wallet Analysis
    # ═══════════════════════════════════════════════════════════════════

    async def get_portfolio(self, chain: str, wallet: str) -> Optional[WalletPortfolio]:
        """Full wallet portfolio with P&L."""
        result = await self._get("/portfolio", {
            "chain": chain,
            "address": wallet,
        })
        if "error" in result:
            return None

        data = result.get("data", {})
        return WalletPortfolio(
            address=wallet,
            chain=chain,
            total_value_usd=float(data.get("total_value_usd", 0)),
            total_pnl_usd=float(data.get("total_pnl_usd", 0)),
            total_pnl_pct=float(data.get("total_pnl_pct", 0)),
            token_count=int(data.get("token_count", 0)),
            win_count=int(data.get("win_count", 0)),
            loss_count=int(data.get("loss_count", 0)),
            tokens=data.get("tokens", []),
            recent_transactions=data.get("recent_transactions", []),
            tags=data.get("tags", []),
        )

    # ═══════════════════════════════════════════════════════════════════
    # MODULE 5: TRACK — Real-time Wallet Tracking
    # ═══════════════════════════════════════════════════════════════════

    async def track_wallet(self, chain: str, wallet: str,
                           tag: Optional[str] = None) -> Dict[str, Any]:
        """Start tracking a wallet for real-time signals."""
        self._tracked_wallets[wallet] = {
            "chain": chain,
            "tag": tag,
            "added_at": datetime.utcnow(),
        }
        # In production, this would register a webhook
        return {
            "wallet": wallet,
            "chain": chain,
            "tag": tag,
            "status": "tracking",
            "message": f"Tracking {wallet} on {chain}",
        }

    async def get_tracked_signals(self, chain: str = "sol",
                                  signal_type: Optional[str] = None,
                                  limit: int = 50) -> List[TrackedSignal]:
        """Get recent signals from tracked wallets/KOLs."""
        params = {"chain": chain, "limit": limit}
        if signal_type:
            params["type"] = signal_type

        result = await self._get("/track/signals", params)
        if "error" in result:
            return []

        signals = []
        for item in result.get("data", []):
            signals.append(TrackedSignal(
                timestamp=datetime.fromtimestamp(item.get("timestamp", 0)),
                wallet_address=item.get("wallet", ""),
                wallet_tag=item.get("wallet_tag"),
                token_address=item.get("token", ""),
                token_symbol=item.get("token_symbol", "?"),
                action=item.get("action", "unknown"),
                amount_usd=float(item.get("amount_usd", 0)),
                tx_signature=item.get("tx", ""),
                signal_type=item.get("signal_type", "unknown"),
                confidence=int(item.get("confidence", 5)),
            ))

        # Add to log
        for s in signals:
            self._signal_log.append(s)

        return signals

    async def get_kol_trades(self, chain: str = "sol", limit: int = 30) -> List[TrackedSignal]:
        """Get trades from KOL/renowned wallets."""
        return await self.get_tracked_signals(chain, signal_type="kol_trade", limit=limit)

    async def get_smart_money_moves(self, chain: str = "sol", limit: int = 30) -> List[TrackedSignal]:
        """Get smart money wallet trades."""
        return await self.get_tracked_signals(chain, signal_type="smart_money", limit=limit)

    # ═══════════════════════════════════════════════════════════════════
    # MODULE 6: COOKING — Strategy Orders
    # ═══════════════════════════════════════════════════════════════════

    async def create_strategy(self, strategy: CookingStrategy) -> Dict[str, Any]:
        """
        Create a cooking strategy: market buy + TP/SL attached.
        """
        return await self._post("/cooking/create", {
            "name": strategy.name,
            "chain": strategy.chain,
            "token": strategy.token_address,
            "entry_type": strategy.entry_type,
            "entry_price": strategy.entry_price,
            "tp_levels": strategy.tp_levels,
            "sl_price": strategy.sl_price,
            "trailing_tp": strategy.trailing_tp,
            "trailing_sl": strategy.trailing_sl,
            "trailing_drawdown_pct": strategy.trailing_drawdown_pct,
            "anti_mev": strategy.anti_mev,
        })

    # ═══════════════════════════════════════════════════════════════════
    # COMPOSITE INTELLIGENCE FEATURES (RMI Original)
    # ═══════════════════════════════════════════════════════════════════

    async def token_deep_scan(self, chain: str, token_address: str) -> Dict[str, Any]:
        """
        RMI Original: Comprehensive token scan combining ALL modules.
        Returns: security, trending context, holder analysis, smart money signals
        """
        logger.info(f"Deep scan: {token_address} on {chain}")

        # Run all analysis in parallel
        sec_task = self.get_token_security(chain, token_address)
        holders_task = self.get_top_holders(chain, token_address, limit=20)
        traders_task = self.get_top_traders(chain, token_address, limit=10)
        kline_task = self.get_kline(chain, token_address, resolution="1h", limit=48)

        security, holders, traders, klines = await asyncio.gather(
            sec_task, holders_task, traders_task, kline_task
        )

        # Build composite analysis
        analysis = {
            "token_address": token_address,
            "chain": chain,
            "scanned_at": datetime.utcnow().isoformat(),
            "security": self._security_to_dict(security) if security else None,
            "top_holders": [self._holder_to_dict(h) for h in holders[:10]],
            "top_traders": traders[:10],
            "holder_count": security.holder_count if security else 0,
            "price_chart": self._klines_to_chart(klines),
            "smart_money_presence": {
                "smart_degen_holders": sum(1 for h in holders if h.tag == "smart_degen"),
                "renowned_holders": sum(1 for h in holders if h.tag == "renowned"),
                "whale_holders": sum(1 for h in holders if h.balance_usd > 10000),
            },
            "concentration_risk": self._analyze_concentration(holders),
            "composite_risk_score": self._composite_risk(security, holders, klines),
            "narrative": self._generate_narrative(security, holders, traders, klines),
        }

        return analysis

    async def smart_money_dashboard(self, chain: str = "sol", limit: int = 20) -> Dict[str, Any]:
        """
        RMI Original: Dashboard of what smart money is doing RIGHT NOW.
        """
        # Get trending with smart money counts
        trending = await self.get_trending(chain, interval="24h", limit=50)

        # Get recent KOL trades
        kol_trades = await self.get_kol_trades(chain, limit=30)

        # Get smart money moves
        smart_moves = await self.get_smart_money_moves(chain, limit=30)

        # Aggregate by token
        token_activity = defaultdict(lambda: {
            "kol_buys": 0, "kol_sells": 0,
            "smart_buys": 0, "smart_sells": 0,
            "total_volume_usd": 0,
            "unique_wallets": set(),
        })

        for t in kol_trades:
            ta = token_activity[t.token_address]
            ta["kol_buys" if t.action == "buy" else "kol_sells"] += 1
            ta["total_volume_usd"] += t.amount_usd
            ta["unique_wallets"].add(t.wallet_address)

        for t in smart_moves:
            ta = token_activity[t.token_address]
            ta["smart_buys" if t.action == "buy" else "smart_sells"] += 1
            ta["total_volume_usd"] += t.amount_usd
            ta["unique_wallets"].add(t.wallet_address)

        # Merge with trending data
        hot_tokens = []
        for token in trending[:limit]:
            activity = token_activity.get(token.address, {})
            hot_tokens.append({
                "address": token.address,
                "symbol": token.symbol,
                "name": token.name,
                "price": token.price_usd,
                "change_24h": token.price_change_24h,
                "volume": token.volume_24h,
                "smart_degen_count": token.smart_degen_count,
                "renowned_count": token.renowned_count,
                "kol_buys": activity.get("kol_buys", 0),
                "kol_sells": activity.get("kol_sells", 0),
                "smart_buys": activity.get("smart_buys", 0),
                "smart_sells": activity.get("smart_sells", 0),
                "smart_net": activity.get("smart_buys", 0) - activity.get("smart_sells", 0),
                "safety_score": token.safety_score,
            })

        # Sort by smart net (smart money accumulation)
        hot_tokens.sort(key=lambda x: (x["smart_net"], x["smart_degen_count"]), reverse=True)

        return {
            "chain": chain,
            "timestamp": datetime.utcnow().isoformat(),
            "hot_tokens": hot_tokens,
            "recent_kol_trades": len(kol_trades),
            "recent_smart_moves": len(smart_moves),
            "top_accumulating": [t for t in hot_tokens if t["smart_net"] > 0][:5],
            "top_distributing": [t for t in hot_tokens if t["smart_net"] < 0][:5],
        }

    async def wallet_intelligence(self, chain: str, wallet: str) -> Dict[str, Any]:
        """
        RMI Original: Full wallet intelligence combining portfolio + GMGN tags.
        """
        portfolio = await self.get_portfolio(chain, wallet)

        # Get wallet tag from tracking
        tag = self._tracked_wallets.get(wallet, {}).get("tag")

        return {
            "wallet": wallet,
            "chain": chain,
            "tag": tag,
            "portfolio": {
                "total_value": portfolio.total_value_usd if portfolio else 0,
                "total_pnl": portfolio.total_pnl_usd if portfolio else 0,
                "total_pnl_pct": portfolio.total_pnl_pct if portfolio else 0,
                "token_count": portfolio.token_count if portfolio else 0,
                "win_count": portfolio.win_count if portfolio else 0,
                "loss_count": portfolio.loss_count if portfolio else 0,
            } if portfolio else None,
            "classification": self._classify_wallet(portfolio, tag),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ═══════════════════════════════════════════════════════════════════
    # INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _security_to_dict(self, s: TokenSecurity) -> Dict:
        return {
            "name": s.name, "symbol": s.symbol,
            "is_honeypot": s.is_honeypot, "buy_tax": s.buy_tax, "sell_tax": s.sell_tax,
            "renounced_mint": s.renounced_mint, "renounced_freeze": s.renounced_freeze,
            "holder_count": s.holder_count, "top_10_rate": s.top_10_holder_rate,
            "dev_hold_rate": s.dev_team_hold_rate, "liquidity_locked": s.liquidity_locked,
            "rug_ratio": s.rug_ratio, "safety_score": s.safety_score,
            "risk_flags": s.risk_flags,
        }

    def _holder_to_dict(self, h: TopHolder) -> Dict:
        return {
            "address": h.address[:8] + "..." + h.address[-8:] if len(h.address) > 20 else h.address,
            "balance_usd": round(h.balance_usd, 2),
            "pct": round(h.pct_of_supply * 100, 2),
            "tag": h.tag,
            "is_contract": h.is_contract,
        }

    def _klines_to_chart(self, klines: List[KlineData]) -> List[Dict]:
        return [{"t": k.timestamp, "o": k.open, "h": k.high, "l": k.low, "c": k.close, "v": k.volume_usd}
                for k in klines[-50:]]  # Last 50 candles

    def _analyze_concentration(self, holders: List[TopHolder]) -> Dict[str, Any]:
        if not holders:
            return {"risk": "unknown", "top_10_pct": 0}

        top10_pct = sum(h.pct_of_supply for h in holders[:10])
        smart_pct = sum(h.pct_of_supply for h in holders if h.tag in ("smart_degen", "renowned"))
        whale_wallets = [h for h in holders if h.balance_usd > 50000]

        risk = "LOW"
        if top10_pct > 0.8:
            risk = "CRITICAL"
        elif top10_pct > 0.6:
            risk = "HIGH"
        elif top10_pct > 0.4:
            risk = "ELEVATED"

        return {
            "top_10_pct": round(top10_pct * 100, 2),
            "smart_money_pct": round(smart_pct * 100, 2),
            "whale_wallet_count": len(whale_wallets),
            "concentration_risk": risk,
        }

    def _composite_risk(self, security: Optional[TokenSecurity],
                        holders: List[TopHolder],
                        klines: List[KlineData]) -> int:
        """Calculate composite risk score 0-100."""
        if not security:
            return 50

        score = security.safety_score

        # Concentration penalty
        conc = self._analyze_concentration(holders)
        if conc["concentration_risk"] == "CRITICAL":
            score -= 20
        elif conc["concentration_risk"] == "HIGH":
            score -= 10

        # Price volatility (from klines)
        if len(klines) >= 2:
            prices = [k.close for k in klines]
            max_p = max(prices)
            min_p = min(prices)
            if max_p > 0 and min_p > 0:
                volatility = (max_p - min_p) / min_p
                if volatility > 10:  # 1000% swing
                    score -= 15

        return max(0, min(100, score))

    def _generate_narrative(self, security: Optional[TokenSecurity],
                           holders: List[TopHolder],
                           traders: List[Dict],
                           klines: List[KlineData]) -> str:
        """Generate human-readable analysis narrative."""
        if not security:
            return "No security data available."

        parts = []

        if security.is_honeypot:
            parts.append("🚨 HONEYPOT DETECTED — You cannot sell this token.")
            return " ".join(parts)

        # Holder concentration
        conc = self._analyze_concentration(holders)
        if conc["top_10_pct"] > 80:
            parts.append(f"Extreme whale concentration: top 10 hold {conc['top_10_pct']:.1f}%.")
        elif conc["smart_money_pct"] > 20:
            parts.append(f"Strong smart money presence: {conc['smart_money_pct']:.1f}% held by tagged wallets.")

        # Taxes
        if security.buy_tax > 5 or security.sell_tax > 5:
            parts.append(f"High taxes: {security.buy_tax:.1f}% buy / {security.sell_tax:.1f}% sell.")

        # Authorities
        if not security.renounced_mint:
            parts.append("Dev can still mint more tokens.")
        if not security.renounced_freeze:
            parts.append("Freeze authority active — wallets can be frozen.")

        # Liquidity
        if not security.liquidity_locked:
            parts.append("Liquidity is NOT locked — rug pull risk.")

        # Price action
        if len(klines) >= 2:
            first = klines[0].close
            last = klines[-1].close
            if first > 0:
                change = ((last - first) / first) * 100
                parts.append(f"Price action: {change:+.1f}% over last {len(klines)} candles.")

        return " ".join(parts) if parts else "No significant risk factors detected."

    def _classify_wallet(self, portfolio: Optional[WalletPortfolio], tag: Optional[str]) -> Dict[str, Any]:
        """Classify wallet type based on activity and tags."""
        tags = []
        if tag:
            tags.append(tag)
        if portfolio:
            if portfolio.total_value_usd > 100000:
                tags.append("whale")
            if portfolio.total_pnl_pct > 100:
                tags.append("high_performer")
            if portfolio.win_count > portfolio.loss_count * 2:
                tags.append("consistent_winner")
            if portfolio.token_count > 20:
                tags.append("diverse_trader")

        return {
            "tags": tags,
            "profile_type": tag or "unknown",
            "performance_tier": "high" if portfolio and portfolio.total_pnl_pct > 50 else
                               "medium" if portfolio and portfolio.total_pnl_pct > 0 else "low" if portfolio else "unknown",
        }

    def get_tracked_wallet_count(self) -> int:
        return len(self._tracked_wallets)

    def get_signal_log_size(self) -> int:
        return len(self._signal_log)


# ─── Singleton ───────────────────────────────────────────────────────────

_client: Optional[GMGNFullClient] = None

def get_gmgn_client() -> GMGNFullClient:
    global _client
    if _client is None:
        _client = GMGNFullClient()
    return _client
