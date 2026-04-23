#!/usr/bin/env python3
"""
Helius Intelligence Client — Deep Solana On-Chain Analysis
Leverages Helius Enhanced API, WebSockets, Webhooks, and Sender
for forensic-grade transaction analysis and real-time monitoring.

Key: 3527e878-8dd6-496c-a388-7540408cc59a
RPC: https://mainnet.helius-rpc.com/?api-key=<key>
WS:  wss://mainnet.helius-rpc.com/?api-key=<key>
Sender: https://sender.helius-rpc.com/fast
"""

import os
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque

logger = logging.getLogger("helius")

# ─── CONFIG ──────────────────────────────────────────────────────────────

API_KEY = os.getenv("HELIUS_API_KEY", "").strip()
RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={API_KEY}"
WS_URL = f"wss://mainnet.helius-rpc.com/?api-key={API_KEY}"
SENDER_URL = "https://sender.helius-rpc.com/fast"
BETA_RPC_URL = f"https://beta.helius-rpc.com/?api-key={API_KEY}"

# Jito tip accounts for Sender
TIP_ACCOUNTS = [
    "4ACfpUFoaSD9bfPdeu6DBt89gB6ENTeHBXCAi87NhDEE",
    "D2L6yPZ2FmmmTKPgzaMKdhu6EWZcTpLy1Vhx8uvZe7NZ",
    "9bnz4RShgq1hAnLnZbP8kbgBg1kEmcJBYQq3gQbmnSta",
    "5VY91ws6B2hMmBFRsXkoAAdsPHBJwRfBht4DXox3xkwn",
    "2nyhqdwKcJZR2vcqCyrYsaPVdAnFoJjiksCXJ7hfEYgD",
    "2q5pghRs6arqVjRvT5gfgWfWcHWmw1ZuCzphgd5KfWGJ",
    "wyvPkWjVZz1M8fHQnMMCDTQDbkManefNNhweYk5WkcF",
    "3KCKozbAaF75qEU33jtzozcJ29yJuaLJTy2jFdzUY8bT",
    "4vieeGHPYPG2MmyPRcYjdiDmmhN3ww7hsFNap8pVN3Ey",
    "4TQLFNWK8AovT1gFvda5jfw2oJeRMKEmw7aH6MGBJ3or",
]

# ─── DATA CLASSES ────────────────────────────────────────────────────────

@dataclass
class TransactionAnalysis:
    signature: str
    timestamp: datetime
    tx_type: str  # transfer, swap, mint, burn, stake, nft_sale, etc.
    from_address: str
    to_address: str
    amount_sol: float
    amount_usd: Optional[float]
    token_address: Optional[str]
    token_amount: Optional[float]
    program_id: str
    is_mev: bool
    mev_type: Optional[str]  # sandwich, frontrun, backrun
    counterparties: List[str]
    risk_flags: List[str]
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WalletProfile:
    address: str
    balance_sol: float
    token_count: int
    nft_count: int
    total_transactions: int
    first_seen: Optional[datetime]
    last_active: Optional[datetime]
    avg_tx_size_sol: float
    top_counterparties: List[Dict[str, Any]]
    risk_score: int
    tags: List[str]  # whale, sniper, bundler, bot, etc.
    pnl_7d: float
    pnl_30d: float

@dataclass
class TokenDeepProfile:
    address: str
    name: str
    symbol: str
    supply: float
    decimals: int
    holder_count: int
    top_holders: List[Dict[str, Any]]
    holder_concentration: float  # % held by top 10
    mint_authority: Optional[str]
    freeze_authority: Optional[str]
    is_mutable: bool
    creation_tx: Optional[str]
    creation_date: Optional[datetime]
    transfer_count_24h: int
    unique_senders_24h: int
    unique_receivers_24h: int
    velocity_score: float  # 0-100
    risk_flags: List[str]

@dataclass
class WhaleAlert:
    tx_signature: str
    timestamp: datetime
    from_wallet: str
    to_wallet: str
    token_address: str
    token_symbol: str
    amount_tokens: float
    amount_usd: float
    alert_type: str  # whale_move, dump, accumulation, distribution
    severity: int  # 1-5

@dataclass
class SniperCluster:
    token_address: str
    launch_tx: str
    launch_time: datetime
    sniper_wallets: List[str]
    total_sniper_count: int
    coordinated_score: float  # 0-100
    avg_buy_time_ms: float
    avg_position_size_sol: float
    total_sniper_volume_sol: float
    risk_verdict: str


# ─── CORE CLIENT ─────────────────────────────────────────────────────────

class HeliusClient:
    """Full-featured Helius API client with intelligence layer."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={self.api_key}"
        self.ws_url = f"wss://mainnet.helius-rpc.com/?api-key={self.api_key}"
        self.sender_url = SENDER_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self._tx_cache: Dict[str, TransactionAnalysis] = {}
        self._wallet_cache: Dict[str, WalletProfile] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def _rpc_call(self, method: str, params: list = None) -> Dict[str, Any]:
        """Make a Solana JSON-RPC call through Helius."""
        s = await self._get_session()
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }
        try:
            async with s.post(self.rpc_url, json=payload) as resp:
                data = await resp.json()
                return data.get("result", {})
        except Exception as e:
            logger.error(f"RPC call failed ({method}): {e}")
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════════════
    # TOKEN INTELLIGENCE
    # ═══════════════════════════════════════════════════════════════════

    async def get_token_metadata(self, mint_address: str) -> Dict[str, Any]:
        """Get comprehensive token metadata via Helius."""
        result = await self._rpc_call("getAsset", {"id": mint_address})
        if "error" in result:
            return result

        ownership = result.get("ownership", {})
        token_info = result.get("token_info", {})

        return {
            "address": mint_address,
            "name": result.get("content", {}).get("metadata", {}).get("name", "Unknown"),
            "symbol": result.get("content", {}).get("metadata", {}).get("symbol", "?"),
            "supply": token_info.get("supply", 0),
            "decimals": token_info.get("decimals", 0),
            "holder_count": ownership.get("delegated", 0),  # approximate
            "mint_authority": ownership.get("owner", None),
            "is_mutable": result.get("mutable", True),
            "raw": result,
        }

    async def get_token_deep_profile(self, mint_address: str) -> TokenDeepProfile:
        """Build comprehensive token profile from multiple Helius calls."""
        logger.info(f"Building deep profile for {mint_address}")

        # Get metadata
        metadata = await self.get_token_metadata(mint_address)

        # Get largest accounts (holders)
        holder_result = await self._rpc_call("getTokenLargestAccounts", [mint_address])
        holders = holder_result.get("value", []) if isinstance(holder_result, dict) else []

        # Get supply info
        supply_result = await self._rpc_call("getTokenSupply", [mint_address])
        supply_info = supply_result.get("value", {}) if isinstance(supply_result, dict) else {}
        total_supply = float(supply_info.get("amount", 0)) / (10 ** supply_info.get("decimals", 0))

        # Calculate holder concentration
        top_10_balance = sum(float(h.get("amount", 0)) for h in holders[:10])
        concentration = (top_10_balance / total_supply * 100) if total_supply > 0 else 0

        # Get recent signatures for activity metrics
        sigs_result = await self._rpc_call("getSignaturesForAddress", [mint_address, {"limit": 1000}])
        signatures = sigs_result if isinstance(sigs_result, list) else []

        recent_sigs = [s for s in signatures
                      if datetime.utcnow().timestamp() - s.get("blockTime", 0) < 86400]

        # Parse signatures for unique senders/receivers (simplified)
        unique_wallets = set()
        for sig_info in recent_sigs[:100]:
            tx_detail = await self._get_enhanced_tx(sig_info.get("signature", ""))
            if tx_detail and "nativeTransfers" in tx_detail:
                for transfer in tx_detail["nativeTransfers"]:
                    unique_wallets.add(transfer.get("fromUserAccount", ""))
                    unique_wallets.add(transfer.get("toUserAccount", ""))

        # Risk flags
        risk_flags = []
        if concentration > 50:
            risk_flags.append(f"Extreme concentration: {concentration:.1f}% held by top 10")
        if metadata.get("is_mutable", True):
            risk_flags.append("Token metadata is mutable")
        if len(signatures) < 10:
            risk_flags.append("Very low transaction count")

        return TokenDeepProfile(
            address=mint_address,
            name=metadata.get("name", "Unknown"),
            symbol=metadata.get("symbol", "?"),
            supply=total_supply,
            decimals=supply_info.get("decimals", 0),
            holder_count=len(holders),
            top_holders=[{"address": h.get("address", ""), "balance": float(h.get("amount", 0))} for h in holders[:20]],
            holder_concentration=concentration,
            mint_authority=metadata.get("mint_authority"),
            freeze_authority=None,  # Would need getAccountInfo
            is_mutable=metadata.get("is_mutable", True),
            creation_tx=signatures[-1].get("signature") if signatures else None,
            creation_date=datetime.fromtimestamp(signatures[-1].get("blockTime", 0)) if signatures else None,
            transfer_count_24h=len(recent_sigs),
            unique_senders_24h=len(unique_wallets) // 2,
            unique_receivers_24h=len(unique_wallets) // 2,
            velocity_score=min(len(recent_sigs) / 10, 100),
            risk_flags=risk_flags,
        )

    # ═══════════════════════════════════════════════════════════════════
    # ENHANCED TRANSACTION PARSING
    # ═══════════════════════════════════════════════════════════════════

    async def _get_enhanced_tx(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get parsed transaction via Helius enhanced API."""
        result = await self._rpc_call("getTransaction", [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
        return result if result and not isinstance(result, str) else None

    async def parse_transaction(self, signature: str) -> Optional[TransactionAnalysis]:
        """Parse a transaction into structured intelligence."""
        if signature in self._tx_cache:
            return self._tx_cache[signature]

        tx = await self._get_enhanced_tx(signature)
        if not tx:
            return None

        meta = tx.get("meta", {})
        block_time = tx.get("blockTime", 0)

        # Extract native transfers
        native_transfers = []
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        account_keys = tx.get("transaction", {}).get("message", {}).get("accountKeys", [])

        sol_change = 0
        for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
            change = (post - pre) / 1e9
            if abs(change) > 0.000001 and i < len(account_keys):
                native_transfers.append({
                    "address": account_keys[i].get("pubkey", "") if isinstance(account_keys[i], dict) else account_keys[i],
                    "change": change,
                })
                if change < 0:
                    sol_change += abs(change)

        # Detect MEV patterns
        is_mev = False
        mev_type = None
        if len(native_transfers) >= 3:
            # Simple sandwich detection: A->B->A pattern with similar amounts
            addresses = [t["address"] for t in native_transfers]
            if len(set(addresses)) <= 4 and sol_change > 0.01:
                is_mev = True
                mev_type = "suspected_sandwich"

        # Determine tx type
        tx_type = "transfer"
        if meta.get("logMessages"):
            logs = " ".join(meta.get("logMessages", []))
            if "swap" in logs.lower():
                tx_type = "swap"
            elif "mint" in logs.lower():
                tx_type = "mint"
            elif "burn" in logs.lower():
                tx_type = "burn"
            elif "stake" in logs.lower():
                tx_type = "stake"
            elif "nft" in logs.lower() or "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA" in str(tx):
                tx_type = "nft"

        analysis = TransactionAnalysis(
            signature=signature,
            timestamp=datetime.fromtimestamp(block_time),
            tx_type=tx_type,
            from_address=native_transfers[0]["address"] if native_transfers else "",
            to_address=native_transfers[1]["address"] if len(native_transfers) > 1 else "",
            amount_sol=abs(native_transfers[0]["change"]) if native_transfers else 0,
            amount_usd=None,
            token_address=None,
            token_amount=None,
            program_id="",
            is_mev=is_mev,
            mev_type=mev_type,
            counterparties=list(set(t["address"] for t in native_transfers)),
            risk_flags=[mev_type] if is_mev else [],
            raw_data=tx,
        )

        self._tx_cache[signature] = analysis
        return analysis

    # ═══════════════════════════════════════════════════════════════════
    # WALLET FORENSICS
    # ═══════════════════════════════════════════════════════════════════

    async def get_wallet_profile(self, address: str) -> WalletProfile:
        """Build comprehensive wallet profile."""
        if address in self._wallet_cache:
            return self._wallet_cache[address]

        # Get balance
        balance_result = await self._rpc_call("getBalance", [address])
        balance_sol = balance_result.get("value", 0) / 1e9 if isinstance(balance_result, dict) else 0

        # Get recent transactions
        sigs_result = await self._rpc_call("getSignaturesForAddress", [address, {"limit": 100}])
        signatures = sigs_result if isinstance(sigs_result, list) else []

        total_tx = len(signatures)

        # Parse recent transactions for analysis
        tx_sizes = []
        counterparties = defaultdict(lambda: {"count": 0, "total_sol": 0})
        tags = []

        for sig_info in signatures[:50]:
            sig = sig_info.get("signature", "")
            analysis = await self.parse_transaction(sig)
            if analysis:
                tx_sizes.append(analysis.amount_sol)
                for cp in analysis.counterparties:
                    if cp != address:
                        counterparties[cp]["count"] += 1

        # Classify wallet
        avg_tx = sum(tx_sizes) / len(tx_sizes) if tx_sizes else 0
        if balance_sol > 1000:
            tags.append("whale")
        if total_tx > 10000:
            tags.append("bot")
        if avg_tx > 10:
            tags.append("heavy_trader")
        if total_tx > 0 and len(signatures) > 0:
            first_block = signatures[-1].get("blockTime", 0)
            last_block = signatures[0].get("blockTime", 0)
            wallet_age_days = (last_block - first_block) / 86400 if last_block > first_block else 0
            if wallet_age_days < 7 and total_tx > 100:
                tags.append("sniper")
            if wallet_age_days < 30 and total_tx > 500:
                tags.append("bundler")

        # Top counterparties
        top_cp = sorted(counterparties.items(), key=lambda x: x[1]["count"], reverse=True)[:10]

        profile = WalletProfile(
            address=address,
            balance_sol=balance_sol,
            token_count=0,  # Would need token accounts
            nft_count=0,
            total_transactions=total_tx,
            first_seen=datetime.fromtimestamp(signatures[-1].get("blockTime", 0)) if signatures else None,
            last_active=datetime.fromtimestamp(signatures[0].get("blockTime", 0)) if signatures else None,
            avg_tx_size_sol=avg_tx,
            top_counterparties=[{"address": k, **v} for k, v in top_cp],
            risk_score=min(100, len(tags) * 15 + (1000 if balance_sol > 10000 else 0)),
            tags=tags,
            pnl_7d=0,  # Would need historical price data
            pnl_30d=0,
        )

        self._wallet_cache[address] = profile
        return profile

    # ═══════════════════════════════════════════════════════════════════
    # WEBHOOK MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════

    async def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all configured webhooks."""
        s = await self._get_session()
        url = f"https://api.helius.xyz/v0/webhooks?api-key={self.api_key}"
        try:
            async with s.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return [{"error": f"HTTP {resp.status}"}]
        except Exception as e:
            return [{"error": str(e)}]

    async def create_webhook(self, webhook_url: str, account_addresses: List[str],
                             transaction_types: Optional[List[str]] = None,
                             webhook_type: str = "enhanced") -> Dict[str, Any]:
        """Create a new webhook for on-chain event monitoring."""
        s = await self._get_session()
        url = f"https://api.helius.xyz/v0/webhooks?api-key={self.api_key}"
        payload = {
            "webhookURL": webhook_url,
            "accountAddresses": account_addresses,
            "webhookType": webhook_type,
            "transactionTypes": transaction_types or ["ANY"],
            "authHeader": None,
        }
        try:
            async with s.post(url, json=payload) as resp:
                return await resp.json()
        except Exception as e:
            return {"error": str(e)}

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook by ID."""
        s = await self._get_session()
        url = f"https://api.helius.xyz/v0/webhooks/{webhook_id}?api-key={self.api_key}"
        try:
            async with s.delete(url) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Delete webhook failed: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════
    # SENDER — Ultra-Fast Transaction Submission
    # ═══════════════════════════════════════════════════════════════════

    async def send_transaction_fast(self, serialized_tx: str, tip_account_index: int = 0) -> Dict[str, Any]:
        """Submit transaction via Helius Sender (Jito + staked connections)."""
        s = await self._get_session()
        tip_account = TIP_ACCOUNTS[tip_account_index % len(TIP_ACCOUNTS)]

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [serialized_tx, {"skipPreflight": False, "preflightCommitment": "confirmed"}]
        }
        try:
            async with s.post(self.sender_url, json=payload, headers={"Content-Type": "application/json"}) as resp:
                return await resp.json()
        except Exception as e:
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════════════
    # WEBSOCKET — REAL-TIME MONITORING
    # ═══════════════════════════════════════════════════════════════════

    async def subscribe_account(self, account: str, callback: Callable[[Dict], None]):
        """Subscribe to real-time account updates via WebSocket."""
        import websockets
        try:
            async with websockets.connect(self.ws_url) as ws:
                # Subscribe to account
                await ws.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "accountSubscribe",
                    "params": [account, {"encoding": "jsonParsed", "commitment": "confirmed"}]
                }))

                logger.info(f"Subscribed to account: {account}")

                async for message in ws:
                    data = json.loads(message)
                    if "params" in data:
                        await callback(data["params"]["result"])

        except Exception as e:
            logger.error(f"WebSocket error for {account}: {e}")

    async def subscribe_logs(self, mentions: List[str], callback: Callable[[Dict], None]):
        """Subscribe to transaction logs mentioning specific addresses."""
        import websockets
        try:
            async with websockets.connect(self.ws_url) as ws:
                await ws.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [{"mentions": mentions}, {"commitment": "confirmed"}]
                }))

                logger.info(f"Subscribed to logs for: {mentions}")

                async for message in ws:
                    data = json.loads(message)
                    if "params" in data:
                        await callback(data["params"]["result"])

        except Exception as e:
            logger.error(f"Logs WebSocket error: {e}")


# ─── Singleton ───────────────────────────────────────────────────────────

_client: Optional[HeliusClient] = None

def get_helius_client() -> HeliusClient:
    global _client
    if _client is None:
        _client = HeliusClient()
    return _client
