#!/usr/bin/env python3
"""
🎯 RUG MUNCHER THREAT INTEL GROUP
Premium early warning feed for imminent rugs
$10/month for real-time alerts on predicted rugs before they happen
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from collections import defaultdict

class ThreatLevel(Enum):
    CRITICAL = "critical"      # >90% probability, <24h
    HIGH = "high"              # >75% probability, <48h
    ELEVATED = "elevated"      # >60% probability, <72h
    WATCH = "watch"            # Suspicious patterns detected

@dataclass
class ThreatAlert:
    id: str
    timestamp: datetime
    contract: str
    chain: str
    token_name: str
    token_symbol: str
    threat_level: ThreatLevel
    rug_probability: float
    estimated_rug_window: str
    confidence: str
    trigger_signals: List[Dict]
    dev_identity: Optional[Dict]
    liquidity_risk: Optional[Dict]
    holder_psychology: Optional[Dict]
    social_sentiment: Optional[Dict]
    recommended_action: str
    status: str  # active, confirmed_rug, false_positive, expired
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'contract': self.contract,
            'chain': self.chain,
            'token_name': self.token_name,
            'token_symbol': self.token_symbol,
            'threat_level': self.threat_level.value,
            'rug_probability': self.rug_probability,
            'estimated_rug_window': self.estimated_rug_window,
            'confidence': self.confidence,
            'trigger_signals': self.trigger_signals,
            'dev_identity': self.dev_identity,
            'liquidity_risk': self.liquidity_risk,
            'holder_psychology': self.holder_psychology,
            'social_sentiment': self.social_sentiment,
            'recommended_action': self.recommended_action,
            'status': self.status
        }

class ThreatIntelDatabase:
    """Database for threat intelligence alerts and subscribers"""
    
    def __init__(self, db_path: str = '/root/rugmuncher_threat_intel.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        # Threat alerts feed
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_alerts (
                id TEXT PRIMARY KEY,
                timestamp TIMESTAMP,
                contract TEXT,
                chain TEXT,
                token_name TEXT,
                token_symbol TEXT,
                threat_level TEXT,
                rug_probability REAL,
                estimated_rug_window TEXT,
                confidence TEXT,
                data TEXT,
                status TEXT DEFAULT 'active',
                confirmed_rug BOOLEAN DEFAULT 0,
                confirmed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Subscribers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                tier TEXT DEFAULT 'intel',  -- intel, intel_pro
                subscribed_at TIMESTAMP,
                expires_at TIMESTAMP,
                payment_status TEXT,
                alerts_received INTEGER DEFAULT 0,
                false_positives_reported INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Subscriber alert delivery tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT,
                user_id INTEGER,
                delivered_at TIMESTAMP,
                read BOOLEAN DEFAULT 0,
                acted_upon BOOLEAN DEFAULT 0
            )
        ''')
        
        # Accuracy tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_accuracy (
                alert_id TEXT PRIMARY KEY,
                predicted_probability REAL,
                predicted_window TEXT,
                actual_result TEXT,
                actual_rug_time TIMESTAMP,
                accuracy_score REAL
            )
        ''')
        
        self.conn.commit()
    
    def add_alert(self, alert: ThreatAlert):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO threat_alerts 
            (id, timestamp, contract, chain, token_name, token_symbol, threat_level,
             rug_probability, estimated_rug_window, confidence, data, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.id, alert.timestamp, alert.contract, alert.chain,
            alert.token_name, alert.token_symbol, alert.threat_level.value,
            alert.rug_probability, alert.estimated_rug_window, alert.confidence,
            json.dumps(alert.to_dict()), alert.status
        ))
        self.conn.commit()
    
    def get_active_alerts(self, min_level: str = 'watch') -> List[ThreatAlert]:
        """Get all active alerts above minimum threat level"""
        level_order = {'critical': 4, 'high': 3, 'elevated': 2, 'watch': 1}
        min_val = level_order.get(min_level, 1)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT data FROM threat_alerts 
            WHERE status = 'active' 
            AND datetime(timestamp) > datetime('now', '-7 days')
            ORDER BY rug_probability DESC, timestamp DESC
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            data = json.loads(row[0])
            if level_order.get(data['threat_level'], 0) >= min_val:
                alerts.append(self._dict_to_alert(data))
        
        return alerts
    
    def get_recent_confirmed_rugs(self, hours: int = 168) -> List[Dict]:
        """Get recently confirmed rugs for accuracy tracking"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM threat_alerts 
            WHERE confirmed_rug = 1 
            AND confirmed_at > datetime('now', '-{} hours')
            ORDER BY confirmed_at DESC
        '''.format(hours))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def mark_confirmed_rug(self, alert_id: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE threat_alerts 
            SET confirmed_rug = 1, confirmed_at = ?, status = 'confirmed_rug'
            WHERE id = ?
        ''', (datetime.now(), alert_id))
        self.conn.commit()
    
    def add_subscriber(self, user_id: int, username: str, tier: str = 'intel'):
        cursor = self.conn.cursor()
        expires = datetime.now() + timedelta(days=30)
        cursor.execute('''
            INSERT OR REPLACE INTO threat_subscribers 
            (user_id, username, tier, subscribed_at, expires_at, payment_status, active)
            VALUES (?, ?, ?, ?, ?, 'pending', 1)
        ''', (user_id, username, tier, datetime.now(), expires))
        self.conn.commit()
    
    def get_active_subscribers(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM threat_subscribers 
            WHERE active = 1 AND expires_at > datetime('now')
        ''')
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def is_subscriber(self, user_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 1 FROM threat_subscribers 
            WHERE user_id = ? AND active = 1 AND expires_at > datetime('now')
        ''', (user_id,))
        return cursor.fetchone() is not None
    
    def log_delivery(self, alert_id: str, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alert_deliveries (alert_id, user_id, delivered_at)
            VALUES (?, ?, ?)
        ''', (alert_id, user_id, datetime.now()))
        
        cursor.execute('''
            UPDATE threat_subscribers 
            SET alerts_received = alerts_received + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        """Get feed statistics"""
        cursor = self.conn.cursor()
        
        # Total alerts
        cursor.execute('SELECT COUNT(*) FROM threat_alerts')
        total_alerts = cursor.fetchone()[0]
        
        # Confirmed rugs
        cursor.execute('SELECT COUNT(*) FROM threat_alerts WHERE confirmed_rug = 1')
        confirmed = cursor.fetchone()[0]
        
        # Active subscribers
        cursor.execute('SELECT COUNT(*) FROM threat_subscribers WHERE active = 1')
        subscribers = cursor.fetchone()[0]
        
        # Recent alerts by level
        cursor.execute('''
            SELECT threat_level, COUNT(*) FROM threat_alerts 
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY threat_level
        ''')
        by_level = dict(cursor.fetchall())
        
        # Calculate accuracy
        cursor.execute('''
            SELECT AVG(CASE WHEN confirmed_rug = 1 THEN 1.0 ELSE 0.0 END)
            FROM threat_alerts WHERE threat_level IN ('critical', 'high')
        ''')
        accuracy = cursor.fetchone()[0] or 0
        
        return {
            'total_alerts': total_alerts,
            'confirmed_rugs': confirmed,
            'accuracy_rate': accuracy * 100,
            'active_subscribers': subscribers,
            'alerts_by_level': by_level,
            'last_updated': datetime.now().isoformat()
        }
    
    def _dict_to_alert(self, data: Dict) -> ThreatAlert:
        return ThreatAlert(
            id=data['id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            contract=data['contract'],
            chain=data['chain'],
            token_name=data['token_name'],
            token_symbol=data['token_symbol'],
            threat_level=ThreatLevel(data['threat_level']),
            rug_probability=data['rug_probability'],
            estimated_rug_window=data['estimated_rug_window'],
            confidence=data['confidence'],
            trigger_signals=data['trigger_signals'],
            dev_identity=data.get('dev_identity'),
            liquidity_risk=data.get('liquidity_risk'),
            holder_psychology=data.get('holder_psychology'),
            social_sentiment=data.get('social_sentiment'),
            recommended_action=data['recommended_action'],
            status=data['status']
        )

class ThreatIntelFeed:
    """
    Premium threat intelligence feed generator
    """
    
    PRICING = {
        'intel': {
            'name': 'Threat Intel Feed',
            'price': 10,
            'currency': 'USD',
            'features': [
                'Real-time rug predictions',
                'Critical & High alerts only',
                '12-48h advance warning',
                'Basic dev profiling',
                'Mobile notifications'
            ]
        },
        'intel_pro': {
            'name': 'Threat Intel Pro',
            'price': 25,
            'currency': 'USD',
            'features': [
                'All intel features',
                'Elevated & Watch alerts',
                '72h+ advance warning',
                'Full dev voiceprint',
                'Auto-protection integration',
                'API access',
                'Discord/Telegram webhook'
            ]
        }
    }
    
    def __init__(self):
        self.db = ThreatIntelDatabase()
        self.session: Optional[aiohttp.ClientSession] = None
        self.bot_token = os.getenv('RUG_MUNCHER_BOT_TOKEN', '')
        self.intel_channel_id = os.getenv('THREAT_INTEL_CHANNEL_ID', '')
    
    async def start(self):
        self.session = aiohttp.ClientSession()
        asyncio.create_task(self._feed_generator_loop())
    
    async def stop(self):
        if self.session:
            await self.session.close()
    
    async def _feed_generator_loop(self):
        """Continuously generate threat intelligence alerts"""
        print("[ThreatIntel] Feed generator started...")
        
        while True:
            try:
                # Scan for new threats
                await self._scan_for_threats()
                
                # Update existing alerts
                await self._update_alert_statuses()
                
                # Wait before next scan
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                print(f"[ThreatIntel] Feed error: {e}")
                await asyncio.sleep(300)
    
    async def _scan_for_threats(self):
        """Scan for new rug threats"""
        # This would integrate with the RugPredictor and other modules
        # For now, placeholder for the scanning logic
        pass
    
    async def _update_alert_statuses(self):
        """Update status of existing alerts"""
        # Check if predicted rugs actually happened
        # Mark false positives
        pass
    
    def create_alert(self, prediction_data: Dict, dev_data: Dict = None, 
                     vampire_data: Dict = None) -> ThreatAlert:
        """Create new threat alert from analysis data"""
        
        # Determine threat level
        prob = prediction_data.get('rug_probability', 0)
        hours = prediction_data.get('estimated_hours', [24, 72])
        
        if prob >= 90 and hours[1] <= 24:
            level = ThreatLevel.CRITICAL
        elif prob >= 75 and hours[1] <= 48:
            level = ThreatLevel.HIGH
        elif prob >= 60:
            level = ThreatLevel.ELEVATED
        else:
            level = ThreatLevel.WATCH
        
        # Build recommended action
        if level == ThreatLevel.CRITICAL:
            action = "🚨 EXIT IMMEDIATELY - Rug imminent within 24 hours"
        elif level == ThreatLevel.HIGH:
            action = "⚠️ STRONG SELL SIGNAL - Consider exiting position"
        elif level == ThreatLevel.ELEVATED:
            action = "👁️ MONITOR CLOSELY - Set tight stop loss"
        else:
            action = "📊 WATCH LIST - Unusual patterns detected"
        
        alert = ThreatAlert(
            id=f"TI-{datetime.now().strftime('%Y%m%d%H%M%S')}-{prediction_data['contract'][:8]}",
            timestamp=datetime.now(),
            contract=prediction_data['contract'],
            chain=prediction_data.get('chain', 'bsc'),
            token_name=prediction_data.get('token_name', 'Unknown'),
            token_symbol=prediction_data.get('token_symbol', '???'),
            threat_level=level,
            rug_probability=prob,
            estimated_rug_window=f"{hours[0]}-{hours[1]} hours",
            confidence=prediction_data.get('confidence', 'MEDIUM'),
            trigger_signals=prediction_data.get('trigger_signals', []),
            dev_identity=dev_data,
            liquidity_risk=vampire_data,
            holder_psychology=None,
            social_sentiment=None,
            recommended_action=action,
            status='active'
        )
        
        # Save to database
        self.db.add_alert(alert)
        
        # Broadcast to subscribers
        asyncio.create_task(self._broadcast_alert(alert))
        
        return alert
    
    async def _broadcast_alert(self, alert: ThreatAlert):
        """Broadcast alert to all subscribers"""
        subscribers = self.db.get_active_subscribers()
        
        message = self.format_alert_message(alert)
        
        # Send to each subscriber
        for sub in subscribers:
            try:
                await self._send_telegram_message(
                    sub['user_id'],
                    message,
                    alert.threat_level
                )
                self.db.log_delivery(alert.id, sub['user_id'])
            except Exception as e:
                print(f"[ThreatIntel] Failed to send to {sub['user_id']}: {e}")
        
        # Also post to intel channel if configured
        if self.intel_channel_id:
            try:
                await self._send_telegram_message(
                    self.intel_channel_id,
                    message,
                    alert.threat_level
                )
            except Exception as e:
                print(f"[ThreatIntel] Failed to post to channel: {e}")
    
    async def _send_telegram_message(self, chat_id: int, message: str, 
                                     level: ThreatLevel):
        """Send message via Telegram"""
        if not self.bot_token:
            return
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        # Add buttons based on level
        keyboard = None
        if level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
            keyboard = {
                'inline_keyboard': [[
                    {'text': '🔴 PANIC SELL', 'url': 'https://t.me/RugMuncherBot'},
                    {'text': '📊 Full Analysis', 'url': 'https://t.me/RugMuncherBot'}
                ]]
            }
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        if keyboard:
            payload['reply_markup'] = json.dumps(keyboard)
        
        async with self.session.post(url, json=payload, timeout=10) as r:
            result = await r.json()
            if not result.get('ok'):
                raise Exception(f"Telegram API error: {result}")
    
    def format_alert_message(self, alert: ThreatAlert) -> str:
        """Format alert for Telegram"""
        level_emojis = {
            ThreatLevel.CRITICAL: '💀',
            ThreatLevel.HIGH: '🚨',
            ThreatLevel.ELEVATED: '⚠️',
            ThreatLevel.WATCH: '👁️'
        }
        
        emoji = level_emojis.get(alert.threat_level, '⚡')
        
        text = f"""
{emoji} <b>THREAT INTEL ALERT</b> {emoji}

<b>🎯 Target:</b> {alert.token_name} (${alert.token_symbol})
<b>Contract:</b> <code>{alert.contract}</code>
<b>Chain:</b> {alert.chain.upper()}

<b>📊 THREAT ASSESSMENT:</b>
• Level: <b>{alert.threat_level.value.upper()}</b>
• Rug Probability: <b>{alert.rug_probability:.1f}%</b>
• Time Window: <b>{alert.estimated_rug_window}</b>
• Confidence: {alert.confidence}

<b>🚨 TRIGGER SIGNALS:</b>
"""
        
        for i, signal in enumerate(alert.trigger_signals[:5], 1):
            text += f"{i}. {signal.get('description', 'Unknown signal')}\n"
        
        # Dev identity section
        if alert.dev_identity and alert.dev_identity.get('identity_matched'):
            dev = alert.dev_identity
            text += f"""
<b>👤 DEV IDENTITY:</b>
• Serial Scammer: {dev.get('total_rugs', 0)} previous rugs
• Cross-Chain: {', '.join(dev.get('cross_chains', []))}
• Match Confidence: {dev.get('match_confidence', 0):.0f}%
"""
        
        # Liquidity section
        if alert.liquidity_risk and alert.liquidity_risk.get('threats'):
            text += f"""
<b>🧛 LIQUIDITY RISKS:</b>
• Threats: {len(alert.liquidity_risk['threats'])}
• Real Liquidity: ${alert.liquidity_risk.get('real_liquidity', 0):,.0f}
"""
        
        text += f"""
<b>✅ RECOMMENDED ACTION:</b>
{alert.recommended_action}

<i>Alert ID: {alert.id}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M UTC')}</i>

🔒 <b>Premium Threat Intel Feed</b>
Stay ahead of the rugs. @CryptoRugMunchIntel
"""
        
        return text
    
    def get_feed_summary(self, hours: int = 24) -> str:
        """Get summary of recent intel for subscribers"""
        alerts = self.db.get_active_alerts()
        recent = [a for a in alerts if (datetime.now() - a.timestamp).total_seconds() < hours * 3600]
        
        critical = len([a for a in recent if a.threat_level == ThreatLevel.CRITICAL])
        high = len([a for a in recent if a.threat_level == ThreatLevel.HIGH])
        elevated = len([a for a in recent if a.threat_level == ThreatLevel.ELEVATED])
        
        text = f"""
📊 <b>THREAT INTEL SUMMARY (Last {hours}h)</b>

💀 Critical: {critical}
🚨 High: {high}
⚠️ Elevated: {elevated}

<b>Confirmed Rugs:</b> {len(self.db.get_recent_confirmed_rugs(hours))}

<i>Your early warning system is active.</i>
"""
        return text
    
    def format_subscription_info(self) -> str:
        """Format subscription information"""
        text = """
🎯 <b>RUG MUNCHER THREAT INTEL GROUP</b>

<b>What you get:</b>
"""
        
        for tier_key, tier_info in self.PRICING.items():
            text += f"""
<b>{tier_info['name']} - ${tier_info['price']}/month</b>
"""
            for feature in tier_info['features']:
                text += f"• {feature}\n"
        
        stats = self.db.get_stats()
        text += f"""
<b>📊 FEED PERFORMANCE:</b>
• Total Alerts: {stats['total_alerts']}
• Confirmed Rugs: {stats['confirmed_rugs']}
• Accuracy Rate: {stats['accuracy_rate']:.1f}%
• Active Subscribers: {stats['active_subscribers']}

<b>Recent Successes:</b>
"""
        
        confirmed = self.db.get_recent_confirmed_rugs(168)  # Last 7 days
        for rug in confirmed[:3]:
            text += f"• {rug['token_symbol']} - Predicted {rug['rug_probability']:.0f}% ✓\n"
        
        text += """
<i>Be the first to know. Be the first to exit.</i>

Subscribe: /subscribe_intel
"""
        return text

# Global instance
_intel_instance = None

async def get_threat_intel() -> ThreatIntelFeed:
    """Get or create threat intel instance"""
    global _intel_instance
    if _intel_instance is None:
        _intel_instance = ThreatIntelFeed()
        await _intel_instance.start()
    return _intel_instance

# ═══════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════

async def main():
    intel = await get_threat_intel()
    
    # Sample alert
    sample_prediction = {
        'contract': '0x1234567890abcdef1234567890abcdef12345678',
        'chain': 'bsc',
        'token_name': 'SafeMoon 2.0',
        'token_symbol': 'SAFEMOON2',
        'rug_probability': 87.5,
        'estimated_hours': [12, 24],
        'confidence': 'HIGH',
        'trigger_signals': [
            {'description': 'Dev wallet selling test amounts'},
            {'description': 'LP unlock scheduled in 12 hours'},
            {'description': 'Bot network activated'}
        ]
    }
    
    alert = intel.create_alert(sample_prediction)
    print(intel.format_alert_message(alert))
    
    await intel.stop()

if __name__ == "__main__":
    asyncio.run(main())
