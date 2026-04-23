#!/usr/bin/env python3
"""
Real-Time Wallet Monitoring System
Monitors the 40+ CRM wallets for suspicious activity
"""

import asyncio
import json
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import websockets

class AlertSeverity(Enum):
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"            # Urgent attention
    MEDIUM = "medium"        # Important
    LOW = "low"              # Informational

class AlertType(Enum):
    LARGE_OUTFLOW = "large_outflow"
    EXCHANGE_DEPOSIT = "exchange_deposit"
    TOKEN_SWAP = "token_swap"
    NEW_ASSOCIATION = "new_association"
    RESERVE_MOVEMENT = "reserve_movement"
    WASH_TRADING = "wash_trading"
    RUG_PULL_SIGNATURE = "rug_pull_signature"
    KYC_TRIGGER = "kyc_trigger"

@dataclass
class MonitoringAlert:
    id: str
    wallet_address: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    tx_hash: Optional[str]
    usd_value: float
    timestamp: datetime
    related_wallets: List[str]
    evidence: Dict
    status: str  # "new", "acknowledged", "investigating", "resolved"
    assigned_to: Optional[str] = None
    notes: str = ""

@dataclass
class MonitoredWallet:
    address: str
    tier: str
    role: str
    risk_score: int
    alert_threshold_usd: float
    is_active: bool
    last_activity: Optional[datetime]
    total_monitored_tx: int
    alert_history: List[str]

class HeliusMonitor:
    """Monitor wallets using Helius API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://mainnet.helius-rpc.com"
        self.webhook_url = None
    
    async def get_wallet_transactions(
        self, 
        address: str, 
        limit: int = 100,
        before: Optional[str] = None
    ) -> List[Dict]:
        """Fetch recent transactions for a wallet"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [address, {"limit": limit}]
            }
            
            async with session.post(
                f"{self.base_url}/?api-key={self.api_key}",
                json=payload
            ) as response:
                data = await response.json()
                return data.get("result", [])
    
    async def get_transaction_details(self, signature: str) -> Dict:
        """Get detailed transaction information"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
            }
            
            async with session.post(
                f"{self.base_url}/?api-key={self.api_key}",
                json=payload
            ) as response:
                data = await response.json()
                return data.get("result", {})
    
    async def get_token_accounts(self, address: str) -> List[Dict]:
        """Get all token accounts for a wallet"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    address,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            async with session.post(
                f"{self.base_url}/?api-key={self.api_key}",
                json=payload
            ) as response:
                data = await response.json()
                return data.get("result", {}).get("value", [])
    
    async def get_token_balance(self, address: str, mint: str) -> float:
        """Get specific token balance"""
        accounts = await self.get_token_accounts(address)
        for account in accounts:
            info = account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
            if info.get("mint") == mint:
                return float(info.get("tokenAmount", {}).get("uiAmount", 0))
        return 0.0


class WalletMonitoringSystem:
    """
    Main monitoring system for CRM evidence wallets
    """
    
    # Exchange addresses for detection
    EXCHANGE_WALLETS = {
        "gate_io": ["gate_io_wallet_1", "gate_io_wallet_2"],
        "coinbase": ["coinbase_wallet_1", "coinbase_wallet_2"],
        "binance": ["binance_wallet_1", "binance_wallet_2"],
        "kraken": ["kraken_wallet_1"],
    }
    
    # Known DEX programs
    DEX_PROGRAMS = [
        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",   # Orca Whirlpools
    ]
    
    # CRM token mint
    CRM_MINT = "CRM_TOKEN_MINT_ADDRESS"
    
    def __init__(
        self, 
        helius_api_key: str,
        supabase_url: str,
        supabase_key: str,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        self.helius = HeliusMonitor(helius_api_key)
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        
        self.monitored_wallets: Dict[str, MonitoredWallet] = {}
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        self.alert_handlers: List[Callable] = []
        self.monitoring_task = None
        self.is_running = False
        
        # Monitoring configuration
        self.check_interval = 30  # seconds
        self.large_outflow_threshold = 1000  # USD
        self.reserve_movement_threshold = 10000  # USD
    
    def load_wallets_from_supabase(self) -> List[MonitoredWallet]:
        """Load monitored wallets from Supabase"""
        import requests
        
        response = requests.get(
            f"{self.supabase_url}/rest/v1/wallets?case_id=eq.crm-token-fraud-2024",
            headers={
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}"
            }
        )
        
        wallets = []
        for data in response.json():
            wallet = MonitoredWallet(
                address=data["address"],
                tier=data["tier"],
                role=data["role"],
                risk_score=data["risk_score"],
                alert_threshold_usd=1000 if data["risk_score"] < 90 else 100,
                is_active=data["is_active"],
                last_activity=None,
                total_monitored_tx=0,
                alert_history=[]
            )
            wallets.append(wallet)
            self.monitored_wallets[wallet.address] = wallet
        
        return wallets
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.is_running = True
        print(f"[Monitor] Started monitoring {len(self.monitored_wallets)} wallets")
        
        while self.is_running:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"[Monitor] Error in monitoring cycle: {e}")
                await asyncio.sleep(5)
    
    async def _monitoring_cycle(self):
        """One monitoring cycle - check all wallets"""
        for address, wallet in self.monitored_wallets.items():
            if not wallet.is_active:
                continue
            
            try:
                await self._check_wallet(address)
            except Exception as e:
                print(f"[Monitor] Error checking {address}: {e}")
    
    async def _check_wallet(self, address: str):
        """Check a single wallet for suspicious activity"""
        wallet = self.monitored_wallets[address]
        
        # Get recent transactions
        transactions = await self.helius.get_wallet_transactions(address, limit=10)
        
        for tx in transactions:
            tx_signature = tx.get("signature")
            tx_time = datetime.fromtimestamp(tx.get("blockTime", 0))
            
            # Skip if already processed
            if wallet.last_activity and tx_time <= wallet.last_activity:
                continue
            
            # Get transaction details
            details = await self.helius.get_transaction_details(tx_signature)
            
            # Analyze for alerts
            await self._analyze_transaction(address, tx_signature, details, wallet)
        
        # Update last activity
        if transactions:
            latest_time = max(
                datetime.fromtimestamp(tx.get("blockTime", 0)) 
                for tx in transactions
            )
            wallet.last_activity = latest_time
    
    async def _analyze_transaction(
        self, 
        wallet_address: str, 
        tx_signature: str,
        details: Dict,
        wallet: MonitoredWallet
    ):
        """Analyze a transaction for suspicious patterns"""
        
        # Parse transaction for token transfers
        token_transfers = self._extract_token_transfers(details)
        
        for transfer in token_transfers:
            usd_value = transfer.get("usd_value", 0)
            
            # Check for large outflows
            if usd_value >= self.large_outflow_threshold:
                await self._create_alert(
                    wallet_address=wallet_address,
                    alert_type=AlertType.LARGE_OUTFLOW,
                    severity=AlertSeverity.CRITICAL if usd_value >= 10000 else AlertSeverity.HIGH,
                    title=f"Large Outflow Detected: ${usd_value:,.0f}",
                    description=f"Wallet sent {transfer.get('amount', 0)} tokens worth ${usd_value:,.0f}",
                    tx_hash=tx_signature,
                    usd_value=usd_value,
                    related_wallets=[transfer.get("to_address", "")],
                    evidence={
                        "token": transfer.get("mint", ""),
                        "amount": transfer.get("amount", 0),
                        "to": transfer.get("to_address", "")
                    }
                )
            
            # Check for exchange deposits
            if transfer.get("to_address") in self._get_all_exchange_wallets():
                await self._create_alert(
                    wallet_address=wallet_address,
                    alert_type=AlertType.EXCHANGE_DEPOSIT,
                    severity=AlertSeverity.CRITICAL,
                    title="Exchange Deposit Detected",
                    description=f"${usd_value:,.0f} deposited to known exchange",
                    tx_hash=tx_signature,
                    usd_value=usd_value,
                    related_wallets=[transfer.get("to_address", "")],
                    evidence={
                        "exchange": self._identify_exchange(transfer.get("to_address", "")),
                        "token": transfer.get("mint", ""),
                        "amount": transfer.get("amount", 0)
                    }
                )
            
            # Check for CRM token swaps
            if transfer.get("mint") == self.CRM_MINT:
                await self._create_alert(
                    wallet_address=wallet_address,
                    alert_type=AlertType.TOKEN_SWAP,
                    severity=AlertSeverity.HIGH,
                    title="CRM Token Movement",
                    description=f"{transfer.get('amount', 0)} CRM tokens moved",
                    tx_hash=tx_signature,
                    usd_value=usd_value,
                    related_wallets=[transfer.get("to_address", "")],
                    evidence={"token_amount": transfer.get("amount", 0)}
                )
        
        # Check for reserve wallet movements
        if wallet.role == "reserve_holder" and token_transfers:
            total_usd = sum(t.get("usd_value", 0) for t in token_transfers)
            if total_usd >= self.reserve_movement_threshold:
                await self._create_alert(
                    wallet_address=wallet_address,
                    alert_type=AlertType.RESERVE_MOVEMENT,
                    severity=AlertSeverity.CRITICAL,
                    title="🚨 RESERVE WALLET MOVEMENT 🚨",
                    description=f"Reserve wallet moved ${total_usd:,.0f} - Potential rug pull imminent!",
                    tx_hash=tx_signature,
                    usd_value=total_usd,
                    related_wallets=[t.get("to_address", "") for t in token_transfers],
                    evidence={"transfers": token_transfers}
                )
    
    def _extract_token_transfers(self, tx_details: Dict) -> List[Dict]:
        """Extract token transfers from transaction details"""
        transfers = []
        
        meta = tx_details.get("meta", {})
        pre_balances = {b.get("mint"): b for b in meta.get("preTokenBalances", [])}
        post_balances = {b.get("mint"): b for b in meta.get("postTokenBalances", [])}
        
        for mint in set(list(pre_balances.keys()) + list(post_balances.keys())):
            pre = pre_balances.get(mint, {})
            post = post_balances.get(mint, {})
            
            pre_amount = float(pre.get("uiTokenAmount", {}).get("uiAmount", 0))
            post_amount = float(post.get("uiTokenAmount", {}).get("uiAmount", 0))
            
            if pre_amount != post_amount:
                transfers.append({
                    "mint": mint,
                    "amount": abs(post_amount - pre_amount),
                    "to_address": post.get("owner", ""),
                    "usd_value": 0  # Would need price oracle
                })
        
        return transfers
    
    def _get_all_exchange_wallets(self) -> List[str]:
        """Get all known exchange wallet addresses"""
        all_wallets = []
        for exchange_wallets in self.EXCHANGE_WALLETS.values():
            all_wallets.extend(exchange_wallets)
        return all_wallets
    
    def _identify_exchange(self, address: str) -> str:
        """Identify which exchange an address belongs to"""
        for exchange, wallets in self.EXCHANGE_WALLETS.items():
            if address in wallets:
                return exchange
        return "unknown"
    
    async def _create_alert(
        self,
        wallet_address: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        tx_hash: Optional[str],
        usd_value: float,
        related_wallets: List[str],
        evidence: Dict
    ):
        """Create and dispatch a monitoring alert"""
        
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{wallet_address[:8]}"
        
        alert = MonitoringAlert(
            id=alert_id,
            wallet_address=wallet_address,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            tx_hash=tx_hash,
            usd_value=usd_value,
            timestamp=datetime.now(),
            related_wallets=related_wallets,
            evidence=evidence,
            status="new"
        )
        
        self.active_alerts[alert_id] = alert
        
        # Save to Supabase
        await self._save_alert_to_supabase(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        # Call registered handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                print(f"[Monitor] Alert handler error: {e}")
        
        print(f"[Alert] {severity.value.upper()}: {title}")
    
    async def _save_alert_to_supabase(self, alert: MonitoringAlert):
        """Save alert to Supabase"""
        import requests
        
        data = {
            "id": alert.id,
            "case_id": "crm-token-fraud-2024",
            "wallet_address": alert.wallet_address,
            "alert_type": alert.alert_type.value,
            "severity": alert.severity.value,
            "title": alert.title,
            "description": alert.description,
            "tx_hash": alert.tx_hash,
            "usd_value": alert.usd_value,
            "timestamp": alert.timestamp.isoformat(),
            "related_wallets": alert.related_wallets,
            "evidence": alert.evidence,
            "status": alert.status,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            requests.post(
                f"{self.supabase_url}/rest/v1/monitoring_alerts",
                json=data,
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                }
            )
        except Exception as e:
            print(f"[Monitor] Failed to save alert: {e}")
    
    async def _send_notifications(self, alert: MonitoringAlert):
        """Send alert notifications via all channels"""
        
        # Telegram notification
        if self.telegram_bot_token and self.telegram_chat_id:
            await self._send_telegram_alert(alert)
    
    async def _send_telegram_alert(self, alert: MonitoringAlert):
        """Send Telegram notification"""
        emoji_map = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "📢",
            AlertSeverity.LOW: "ℹ️"
        }
        
        message = f"""
{emoji_map.get(alert.severity, "📢")} <b>RMI Alert: {alert.severity.value.upper()}</b>

<b>{alert.title}</b>

{alert.description}

💰 Value: ${alert.usd_value:,.2f}
👛 Wallet: <code>{alert.wallet_address}</code>
🔗 Tx: <code>{alert.tx_hash or 'N/A'}</code>
⏰ Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Type: {alert.alert_type.value}
Case: CRM Token Fraud Investigation
"""
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage",
                json={
                    "chat_id": self.telegram_chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            )
    
    def register_alert_handler(self, handler: Callable):
        """Register a custom alert handler"""
        self.alert_handlers.append(handler)
    
    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        print("[Monitor] Monitoring stopped")
    
    def get_alert_statistics(self) -> Dict:
        """Get statistics about monitored alerts"""
        alerts = list(self.active_alerts.values())
        
        return {
            "total_alerts": len(alerts),
            "by_severity": {
                severity.value: len([a for a in alerts if a.severity == severity])
                for severity in AlertSeverity
            },
            "by_type": {
                alert_type.value: len([a for a in alerts if a.alert_type == alert_type])
                for alert_type in AlertType
            },
            "by_status": {
                status: len([a for a in alerts if a.status == status])
                for status in ["new", "acknowledged", "investigating", "resolved"]
            },
            "total_usd_flagged": sum(a.usd_value for a in alerts),
            "monitored_wallets": len(self.monitored_wallets),
            "active_wallets": len([w for w in self.monitored_wallets.values() if w.is_active])
        }


class WebhookServer:
    """WebSocket server for real-time alert streaming"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: set = set()
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        self.clients.add(websocket)
        print(f"[WebSocket] Client connected. Total: {len(self.clients)}")
        
        try:
            async for message in websocket:
                # Handle client messages if needed
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"[WebSocket] Client disconnected. Total: {len(self.clients)}")
    
    async def broadcast_alert(self, alert: MonitoringAlert):
        """Broadcast alert to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps({
            "type": "alert",
            "data": asdict(alert)
        }, default=str)
        
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        self.clients -= disconnected
    
    async def start(self):
        """Start the WebSocket server"""
        print(f"[WebSocket] Server starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever


# n8n Workflow Integration
class N8NWorkflowTrigger:
    """Trigger n8n workflows on alert events"""
    
    def __init__(self, n8n_webhook_url: str):
        self.webhook_url = n8n_webhook_url
    
    async def trigger_workflow(self, alert: MonitoringAlert):
        """Send alert to n8n webhook"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "event": "monitoring_alert",
                "alert": asdict(alert),
                "timestamp": datetime.now().isoformat()
            }
            
            async with session.post(
                self.webhook_url,
                json=payload
            ) as response:
                return response.status == 200


if __name__ == "__main__":
    import os
    
    # Configuration from environment
    config = {
        "helius_api_key": os.getenv("HELIUS_API_KEY", ""),
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "supabase_key": os.getenv("SUPABASE_KEY", ""),
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    }
    
    # Initialize monitoring system
    monitor = WalletMonitoringSystem(**config)
    
    # Load wallets
    wallets = monitor.load_wallets_from_supabase()
    print(f"Loaded {len(wallets)} wallets from Supabase")
    
    # Start monitoring
    try:
        asyncio.run(monitor.start_monitoring())
    except KeyboardInterrupt:
        print("\nShutting down...")
        asyncio.run(monitor.stop_monitoring())
