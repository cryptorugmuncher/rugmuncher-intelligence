#!/usr/bin/env python3
"""
🚨 RUG MUNCHER WEBHOOK SERVER
Real-time alert system for rug pulls, dev sells, and suspicious activity
FastAPI-based webhook server that monitors blockchain and sends Telegram alerts
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import sqlite3

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# Configuration
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8080'))
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-secret-key')
BOT_TOKEN = os.getenv('RUG_MUNCHER_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_TELEGRAM_ID', '0'))

# API Keys
BSCSCAN_KEY = os.getenv('BSCSCAN_KEY', '')
ETHERSCAN_KEY = os.getenv('ETHERSCAN_KEY', '')

app = FastAPI(title="Rug Muncher Webhook Server", version="1.0.0")
security = HTTPBearer()

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════

class AlertDatabase:
    def __init__(self, db_path: str = '/root/rugmuncher_alerts.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contract TEXT,
                chain TEXT,
                alert_type TEXT,
                threshold REAL,
                triggered BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dev_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                dev_wallet TEXT,
                contract TEXT,
                chain TEXT,
                alert_on_sell BOOLEAN DEFAULT 1,
                alert_on_transfer BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                alert_type TEXT,
                contract TEXT,
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitored_contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract TEXT,
                chain TEXT,
                user_id INTEGER,
                score INTEGER,
                monitored_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_check TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_price_alert(self, user_id: int, contract: str, chain: str, 
                        alert_type: str, threshold: float):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO price_alerts (user_id, contract, chain, alert_type, threshold)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, contract.lower(), chain, alert_type, threshold))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_dev_watch(self, user_id: int, dev_wallet: str, contract: str, chain: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO dev_watchlist 
            (user_id, dev_wallet, contract, chain, alert_on_sell, alert_on_transfer)
            VALUES (?, ?, ?, ?, 1, 1)
        ''', (user_id, dev_wallet.lower(), contract.lower(), chain))
        self.conn.commit()
    
    def get_active_alerts(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM price_alerts WHERE triggered = 0
        ''')
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_dev_watchlist(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT dev_wallet, chain, contract, user_id 
            FROM dev_watchlist
        ''')
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def log_alert_sent(self, user_id: int, alert_type: str, contract: str, message: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alert_history (user_id, alert_type, contract, message)
            VALUES (?, ?, ?, ?)
        ''', (user_id, alert_type, contract, message))
        self.conn.commit()
    
    def mark_alert_triggered(self, alert_id: int):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE price_alerts SET triggered = 1 WHERE id = ?
        ''', (alert_id,))
        self.conn.commit()

db = AlertDatabase()

# ═══════════════════════════════════════════════════════════
# ALERT MANAGER
# ═══════════════════════════════════════════════════════════

class AlertManager:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        if self.session:
            await self.session.close()
    
    async def send_telegram_alert(self, user_id: int, message: str, 
                                   buttons: List[List[Dict]] = None):
        """Send alert to Telegram user"""
        if not self.session:
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': user_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        if buttons:
            payload['reply_markup'] = json.dumps({'inline_keyboard': buttons})
        
        try:
            async with self.session.post(url, json=payload, timeout=10) as r:
                result = await r.json()
                if result.get('ok'):
                    return True
        except Exception as e:
            print(f"[Alert Error] Failed to send to {user_id}: {e}")
        
        return False
    
    async def broadcast_alert(self, user_ids: List[int], message: str, 
                              buttons: List[List[Dict]] = None):
        """Broadcast alert to multiple users"""
        tasks = [self.send_telegram_alert(uid, message, buttons) for uid in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return sum(1 for r in results if r is True)

alert_manager = AlertManager()

# ═══════════════════════════════════════════════════════════
# BLOCKCHAIN MONITOR
# ═══════════════════════════════════════════════════════════

class BlockchainMonitor:
    """Monitor blockchain for suspicious activity"""
    
    def __init__(self):
        self.last_checked = defaultdict(dict)
    
    async def check_dev_activity(self, dev_wallet: str, contract: str, 
                                  chain: str) -> Optional[Dict]:
        """Check if dev has sold or transferred tokens"""
        api_key = BSCSCAN_KEY if chain == 'bsc' else ETHERSCAN_KEY
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        async with aiohttp.ClientSession() as session:
            # Check for sells in last hour
            url = f"https://{base}/api?module=account&action=tokentx&address={dev_wallet}&page=1&offset=10&sort=desc&apikey={api_key}"
            
            try:
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    if data.get('status') != '1':
                        return None
                    
                    txs = data.get('result', [])
                    sells = []
                    
                    for tx in txs:
                        if tx.get('from', '').lower() == dev_wallet.lower() and \
                           tx.get('contractAddress', '').lower() == contract.lower():
                            
                            tx_time = int(tx.get('timeStamp', 0))
                            amount = int(tx.get('value', 0)) / 1e18
                            
                            sells.append({
                                'amount': amount,
                                'token': tx.get('tokenSymbol', 'UNKNOWN'),
                                'tx_hash': tx.get('hash'),
                                'time': datetime.fromtimestamp(tx_time).isoformat()
                            })
                    
                    if sells:
                        return {
                            'type': 'dev_sell',
                            'wallet': dev_wallet,
                            'contract': contract,
                            'chain': chain,
                            'sells': sells,
                            'total_sold': sum(s['amount'] for s in sells)
                        }
            except Exception as e:
                print(f"[Monitor Error] {e}")
        
        return None
    
    async def check_lp_removal(self, contract: str, chain: str) -> Optional[Dict]:
        """Check for LP removal (rug pull indicator)"""
        # This would check for liquidity removal events
        # Simplified implementation - would need pair address lookup in production
        return None
    
    async def check_price_drop(self, contract: str, chain: str, 
                                threshold_pct: float = 50) -> Optional[Dict]:
        """Check if price dropped significantly"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as r:
                    data = await r.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        pair = pairs[0]
                        price_change = pair.get('priceChange', {}).get('h24', 0)
                        
                        if price_change <= -threshold_pct:
                            return {
                                'type': 'price_crash',
                                'contract': contract,
                                'chain': chain,
                                'drop_pct': abs(price_change),
                                'current_price': pair.get('priceUsd', 0)
                            }
        except Exception as e:
            print(f"[Price Check Error] {e}")
        
        return None

monitor = BlockchainMonitor()

# ═══════════════════════════════════════════════════════════
# BACKGROUND MONITORING TASK
# ═══════════════════════════════════════════════════════════

async def monitoring_loop():
    """Continuous monitoring loop"""
    print("[Monitor] Starting blockchain monitoring loop...")
    
    while True:
        try:
            # Check dev watchlist
            watches = db.get_dev_watchlist()
            for watch in watches:
                activity = await monitor.check_dev_activity(
                    watch['dev_wallet'], 
                    watch['contract'], 
                    watch['chain']
                )
                
                if activity:
                    # Send alert to watching user
                    message = f"""
🚨 <b>DEV ACTIVITY DETECTED</b>

<b>Dev Wallet:</b> <code>{activity['wallet'][:12]}...</code>
<b>Contract:</b> <code>{activity['contract'][:12]}...</code>
<b>Chain:</b> {activity['chain'].upper()}

<b>Sell Activity:</b>
"""
                    for sell in activity['sells'][:3]:
                        message += f"• {sell['amount']:.2f} {sell['token']}\n"
                    
                    message += f"""
<b>Total Sold:</b> {activity['total_sold']:.2f}

<i>This could be the beginning of a rug pull. Consider exiting.</i>
"""
                    
                    buttons = [[
                        {'text': '🔴 PANIC SELL', 'url': f"https://dexscreener.com/{activity['chain']}/{activity['contract']}"},
                        {'text': '📊 Full Scan', 'url': f"https://t.me/RugMuncherBot?start=scan_{activity['contract']}"}
                    ]]
                    
                    await alert_manager.send_telegram_alert(
                        watch['user_id'], message, buttons
                    )
                    
                    db.log_alert_sent(
                        watch['user_id'], 'dev_sell', 
                        activity['contract'], message
                    )
            
            # Wait before next check
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            print(f"[Monitor Loop Error] {e}")
            await asyncio.sleep(60)

# ═══════════════════════════════════════════════════════════
# API MODELS
# ═══════════════════════════════════════════════════════════

class AlertRequest(BaseModel):
    user_id: int
    contract: str
    chain: str = 'bsc'
    alert_type: str  # price_drop, dev_sell, lp_removal
    threshold: Optional[float] = None

class DevWatchRequest(BaseModel):
    user_id: int
    dev_wallet: str
    contract: str
    chain: str = 'bsc'

class BroadcastRequest(BaseModel):
    message: str
    user_ids: Optional[List[int]] = None  # None = all users

# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

@app.on_event("startup")
async def startup():
    await alert_manager.start()
    asyncio.create_task(monitoring_loop())

@app.on_event("shutdown")
async def shutdown():
    await alert_manager.stop()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "monitored_devs": len(db.get_dev_watchlist()),
        "active_alerts": len(db.get_active_alerts())
    }

@app.post("/alerts/price")
async def create_price_alert(
    request: AlertRequest,
    token: str = Depends(verify_token)
):
    """Create a new price alert"""
    alert_id = db.add_price_alert(
        request.user_id,
        request.contract,
        request.chain,
        request.alert_type,
        request.threshold or 50.0
    )
    
    return {
        "success": True,
        "alert_id": alert_id,
        "message": f"Alert created for {request.contract[:12]}..."
    }

@app.post("/alerts/watch-dev")
async def watch_dev(
    request: DevWatchRequest,
    token: str = Depends(verify_token)
):
    """Add dev to watchlist"""
    db.add_dev_watch(
        request.user_id,
        request.dev_wallet,
        request.contract,
        request.chain
    )
    
    return {
        "success": True,
        "message": f"Now watching dev {request.dev_wallet[:12]}..."
    }

@app.post("/alerts/broadcast")
async def broadcast_alert(
    request: BroadcastRequest,
    token: str = Depends(verify_token)
):
    """Broadcast alert to users"""
    # In production, get user list from main database
    # For now, use provided list or admin only
    user_ids = request.user_ids or [ADMIN_ID]
    
    sent = await alert_manager.broadcast_alert(user_ids, request.message)
    
    return {
        "success": True,
        "sent": sent,
        "total": len(user_ids)
    }

@app.post("/webhooks/rug-detected")
async def rug_detected_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """External webhook for rug detection services"""
    data = await request.json()
    
    contract = data.get('contract')
    chain = data.get('chain', 'bsc')
    rug_type = data.get('rug_type')
    
    # Get users monitoring this contract
    # In production, query main database
    
    message = f"""
🚨 <b>RUG PULL DETECTED</b>

<b>Contract:</b> <code>{contract}</code>
<b>Type:</b> {rug_type}
<b>Time:</b> {datetime.now().isoformat()}

<i>This token has been flagged as a confirmed rug.</i>
"""
    
    # Broadcast to admin for now
    await alert_manager.send_telegram_alert(ADMIN_ID, message)
    
    return {"success": True}

@app.get("/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get alert statistics"""
    return {
        "active_price_alerts": len(db.get_active_alerts()),
        "dev_watches": len(db.get_dev_watchlist()),
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🚨 Starting Rug Muncher Webhook Server...")
    print(f"   Port: {WEBHOOK_PORT}")
    print(f"   Health: http://localhost:{WEBHOOK_PORT}/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=WEBHOOK_PORT,
        log_level="info"
    )
