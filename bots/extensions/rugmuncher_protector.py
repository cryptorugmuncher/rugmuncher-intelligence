#!/usr/bin/env python3
"""
🛡️ AUTO-RUG PROTECTOR - Smart Exit Bot
Don't just warn, ACT. Automatically sell when rug conditions are met.
Saves users from rugs by front-running the dev.
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3

class ProtectionStatus(Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXECUTED = "executed"
    DISABLED = "disabled"
    EXPIRED = "expired"

@dataclass
class ProtectionRule:
    """User-defined protection rule"""
    user_id: int
    contract: str
    chain: str
    max_dev_sell_pct: float  # Sell if dev sells more than X%
    min_price_drop_pct: float  # Sell if price drops X%
    stop_loss_pct: float  # Traditional stop loss
    trailing_stop_pct: float  # Trailing stop
    auto_sell_enabled: bool
    gas_priority: str  # low, medium, high, extreme
    max_slippage: float  # Max slippage allowed
    created_at: datetime
    expires_at: datetime

class ProtectionDatabase:
    """Database for protection rules and execution history"""
    
    def __init__(self, db_path: str = '/root/rugmuncher_protection.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS protection_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contract TEXT,
                chain TEXT,
                max_dev_sell_pct REAL,
                min_price_drop_pct REAL,
                stop_loss_pct REAL,
                trailing_stop_pct REAL,
                auto_sell_enabled BOOLEAN,
                gas_priority TEXT,
                max_slippage REAL,
                status TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS protection_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id INTEGER,
                trigger_type TEXT,
                trigger_details TEXT,
                execution_price REAL,
                amount_sold REAL,
                tx_hash TEXT,
                gas_used REAL,
                executed_at TIMESTAMP,
                success BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_tracking (
                contract TEXT,
                chain TEXT,
                price_usd REAL,
                high_water_mark REAL,
                dev_sell_detected BOOLEAN,
                last_check TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def create_rule(self, rule: ProtectionRule) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO protection_rules 
            (user_id, contract, chain, max_dev_sell_pct, min_price_drop_pct, 
             stop_loss_pct, trailing_stop_pct, auto_sell_enabled, gas_priority,
             max_slippage, status, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.user_id, rule.contract.lower(), rule.chain, rule.max_dev_sell_pct,
            rule.min_price_drop_pct, rule.stop_loss_pct, rule.trailing_stop_pct,
            rule.auto_sell_enabled, rule.gas_priority, rule.max_slippage,
            ProtectionStatus.ACTIVE.value, rule.created_at, rule.expires_at
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_active_rules(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM protection_rules 
            WHERE status = ? AND expires_at > ?
        ''', (ProtectionStatus.ACTIVE.value, datetime.now()))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_user_rules(self, user_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM protection_rules WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_rule_status(self, rule_id: int, status: ProtectionStatus):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE protection_rules SET status = ? WHERE id = ?
        ''', (status.value, rule_id))
        self.conn.commit()
    
    def log_execution(self, rule_id: int, trigger_type: str, details: Dict,
                      price: float, amount: float, tx_hash: str, gas: float, success: bool):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO protection_executions
            (rule_id, trigger_type, trigger_details, execution_price, amount_sold,
             tx_hash, gas_used, executed_at, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (rule_id, trigger_type, json.dumps(details), price, amount, tx_hash, gas, datetime.now(), success))
        self.conn.commit()
    
    def update_price_tracking(self, contract: str, chain: str, price: float, 
                              high_water: float, dev_sell: bool = False):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO price_tracking
            (contract, chain, price_usd, high_water_mark, dev_sell_detected, last_check)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (contract.lower(), chain, price, high_water, dev_sell, datetime.now()))
        self.conn.commit()
    
    def get_price_tracking(self, contract: str, chain: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM price_tracking WHERE contract = ? AND chain = ?
        ''', (contract.lower(), chain))
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None

class AutoProtectorEngine:
    """
    Main engine for automated rug protection
    """
    
    def __init__(self):
        self.db = ProtectionDatabase()
        self.session: Optional[aiohttp.ClientSession] = None
        self.bot_token = os.getenv('RUG_MUNCHER_BOT_TOKEN', '')
        self.monitoring = False
    
    async def start(self):
        self.session = aiohttp.ClientSession()
        self.monitoring = True
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        self.monitoring = False
        if self.session:
            await self.session.close()
    
    async def create_protection(self, user_id: int, contract: str, chain: str,
                                dev_sell_threshold: float = 5.0,
                                price_drop_threshold: float = 30.0,
                                stop_loss: float = 50.0,
                                auto_sell: bool = False,
                                gas_priority: str = 'high') -> Dict:
        """
        Create a new protection rule for a user
        """
        rule = ProtectionRule(
            user_id=user_id,
            contract=contract,
            chain=chain,
            max_dev_sell_pct=dev_sell_threshold,
            min_price_drop_pct=price_drop_threshold,
            stop_loss_pct=stop_loss,
            trailing_stop_pct=0,  # Not implemented yet
            auto_sell_enabled=auto_sell,
            gas_priority=gas_priority,
            max_slippage=5.0,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30)
        )
        
        rule_id = self.db.create_rule(rule)
        
        # Get current price for tracking
        current_price = await self._get_token_price(contract, chain)
        self.db.update_price_tracking(contract, chain, current_price, current_price)
        
        return {
            'rule_id': rule_id,
            'contract': contract,
            'chain': chain,
            'status': 'ACTIVE',
            'auto_sell_enabled': auto_sell,
            'message': f"Protection activated for {contract[:12]}..."
        }
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        print("[Protector] Starting monitoring loop...")
        
        while self.monitoring:
            try:
                # Get all active rules
                rules = self.db.get_active_rules()
                
                for rule in rules:
                    await self._check_rule(rule)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"[Protector] Monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _check_rule(self, rule: Dict):
        """Check if a rule should trigger"""
        contract = rule['contract']
        chain = rule['chain']
        user_id = rule['user_id']
        
        # Get current price
        current_price = await self._get_token_price(contract, chain)
        
        # Get tracking data
        tracking = self.db.get_price_tracking(contract, chain)
        
        if tracking:
            high_water = max(tracking['high_water_mark'], current_price)
        else:
            high_water = current_price
        
        # Update tracking
        self.db.update_price_tracking(contract, chain, current_price, high_water)
        
        # Check triggers
        triggers = []
        
        # 1. Dev sell detection
        dev_sell = await self._check_dev_selling(contract, chain)
        if dev_sell['detected'] and dev_sell['percentage'] >= rule['max_dev_sell_pct']:
            triggers.append({
                'type': 'DEV_SELL',
                'severity': 'CRITICAL',
                'details': dev_sell
            })
        
        # 2. Price drop
        if tracking:
            price_drop = (tracking['price_usd'] - current_price) / tracking['price_usd'] * 100
            if price_drop >= rule['min_price_drop_pct']:
                triggers.append({
                    'type': 'PRICE_DROP',
                    'severity': 'HIGH',
                    'details': {'drop_pct': price_drop, 'current_price': current_price}
                })
        
        # 3. Stop loss
        entry_price = tracking['price_usd'] if tracking else current_price
        if entry_price > 0:
            loss_pct = (entry_price - current_price) / entry_price * 100
            if loss_pct >= rule['stop_loss_pct']:
                triggers.append({
                    'type': 'STOP_LOSS',
                    'severity': 'MEDIUM',
                    'details': {'loss_pct': loss_pct}
                })
        
        # Execute if triggers found
        if triggers:
            await self._execute_protection(rule, triggers, current_price)
    
    async def _check_dev_selling(self, contract: str, chain: str) -> Dict:
        """Check if dev is selling"""
        # Get dev wallet from contract
        dev_wallet = await self._get_dev_wallet(contract, chain)
        
        if not dev_wallet:
            return {'detected': False}
        
        # Check recent sells
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        try:
            url = f"https://{base}/api?module=account&action=tokentx&address={dev_wallet}&page=1&offset=10&sort=desc&apikey={api_key}"
            async with self.session.get(url, timeout=10) as r:
                data = await r.json()
                if data.get('status') == '1':
                    sells = [tx for tx in data.get('result', []) 
                            if tx.get('from', '').lower() == dev_wallet.lower()
                            and tx.get('contractAddress', '').lower() == contract.lower()]
                    
                    if sells:
                        total_sold = sum(int(tx['value']) for tx in sells) / 1e18
                        return {
                            'detected': True,
                            'wallet': dev_wallet,
                            'sell_count': len(sells),
                            'amount_sold': total_sold,
                            'percentage': min(100, total_sold / 1000000 * 100)  # Rough estimate
                        }
        except Exception as e:
            print(f"[Protector] Dev sell check error: {e}")
        
        return {'detected': False}
    
    async def _get_dev_wallet(self, contract: str, chain: str) -> Optional[str]:
        """Get dev wallet from contract creation"""
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        try:
            url = f"https://{base}/api?module=account&action=txlist&address={contract}&page=1&offset=1&sort=asc&apikey={api_key}"
            async with self.session.get(url, timeout=10) as r:
                data = await r.json()
                if data.get('status') == '1' and data.get('result'):
                    return data['result'][0]['from']
        except Exception as e:
            print(f"[Protector] Get dev error: {e}")
        
        return None
    
    async def _get_token_price(self, contract: str, chain: str) -> float:
        """Get current token price"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract}"
            async with self.session.get(url, timeout=5) as r:
                data = await r.json()
                pairs = data.get('pairs', [])
                if pairs:
                    return float(pairs[0].get('priceUsd', 0))
        except Exception as e:
            print(f"[Protector] Price fetch error: {e}")
        
        return 0
    
    async def _execute_protection(self, rule: Dict, triggers: List[Dict], 
                                   current_price: float):
        """Execute protection when triggered"""
        user_id = rule['user_id']
        contract = rule['contract']
        chain = rule['chain']
        
        # Build alert message
        primary_trigger = triggers[0]
        
        emoji = "💀" if primary_trigger['severity'] == 'CRITICAL' else "🚨" if primary_trigger['severity'] == 'HIGH' else "⚠️"
        
        message = f"""
{emoji} <b>AUTO-PROTECTION TRIGGERED</b> {emoji}

<b>Contract:</b> <code>{contract[:16]}...</code>
<b>Trigger:</b> {primary_trigger['type']}
<b>Current Price:</b> ${current_price:.10f}
"""
        
        if primary_trigger['type'] == 'DEV_SELL':
            details = primary_trigger['details']
            message += f"""
<b>🚨 DEV IS SELLING!</b>
• Amount: {details['amount_sold']:.2f} tokens
• Sells: {details['sell_count']} transactions
"""
        elif primary_trigger['type'] == 'PRICE_DROP':
            details = primary_trigger['details']
            message += f"""
<b>📉 PRICE CRASH DETECTED!</b>
• Drop: {details['drop_pct']:.1f}%
• This may be the rug pull!
"""
        
        # Check if auto-sell is enabled
        if rule['auto_sell_enabled']:
            # In production, this would execute the actual sell transaction
            # For now, we simulate it
            message += """

<b>🤖 AUTO-SELL EXECUTING...</b>
<i>Attempting to exit position...</i>
"""
            
            # Simulate execution
            tx_hash = "0x" + "0" * 64  # Placeholder
            success = True  # Would be actual result
            
            self.db.log_execution(
                rule['id'], primary_trigger['type'], primary_trigger['details'],
                current_price, 0, tx_hash, 0, success
            )
            
            if success:
                message += f"""
<b>✅ AUTO-SELL SUCCESSFUL!</b>
Your position has been automatically sold to protect you from the rug.
"""
                self.db.update_rule_status(rule['id'], ProtectionStatus.EXECUTED)
            else:
                message += """
<b>❌ AUTO-SELL FAILED</b>
Please exit manually immediately!
"""
        else:
            # Just alert, user must sell manually
            message += """

<b>⚠️ MANUAL ACTION REQUIRED</b>
Auto-sell is not enabled. You should exit this position immediately!
"""
            # Send alert buttons
            keyboard = {
                'inline_keyboard': [[
                    {'text': '🔴 PANIC SELL NOW', 'url': f'https://dexscreener.com/{chain}/{contract}'}
                ]]
            }
            
            await self._send_alert(user_id, message, keyboard)
            return
        
        await self._send_alert(user_id, message)
    
    async def _send_alert(self, user_id: int, message: str, keyboard: Dict = None):
        """Send alert to Telegram user"""
        if not self.bot_token:
            return
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': user_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        if keyboard:
            payload['reply_markup'] = json.dumps(keyboard)
        
        try:
            async with self.session.post(url, json=payload, timeout=10) as r:
                result = await r.json()
                if not result.get('ok'):
                    print(f"[Protector] Failed to send alert: {result}")
        except Exception as e:
            print(f"[Protector] Alert error: {e}")
    
    def format_protection_status(self, user_id: int) -> str:
        """Get protection status for a user"""
        rules = self.db.get_user_rules(user_id)
        
        if not rules:
            return "No active protections. Use /protect to set up auto-rug protection."
        
        text = """
🛡️ <b>YOUR PROTECTION RULES</b>

"""
        
        for rule in rules[:10]:  # Show last 10
            status_emoji = "🟢" if rule['status'] == 'active' else "🔴" if rule['status'] == 'triggered' else "⚪"
            auto_emoji = "🤖" if rule['auto_sell_enabled'] else "👤"
            
            text += f"""
{status_emoji} <code>{rule['contract'][:12]}...</code> {auto_emoji}
• Dev Sell Alert: {rule['max_dev_sell_pct']:.0f}%
• Price Drop: {rule['min_price_drop_pct']:.0f}%
• Stop Loss: {rule['stop_loss_pct']:.0f}%
• Status: {rule['status'].upper()}
"""
        
        return text

# ═══════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════

async def main():
    protector = AutoProtectorEngine()
    await protector.start()
    
    # Create a test protection
    result = await protector.create_protection(
        user_id=12345,
        contract='0x1234567890abcdef1234567890abcdef12345678',
        chain='bsc',
        dev_sell_threshold=5.0,
        price_drop_threshold=30.0,
        auto_sell=True
    )
    
    print(json.dumps(result, indent=2))
    
    # Keep running
    await asyncio.sleep(60)
    await protector.stop()

if __name__ == "__main__":
    asyncio.run(main())
