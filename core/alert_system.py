#!/usr/bin/env python3
"""
🚨 REAL-TIME ALERT SYSTEM
Monitor tokens and alert on suspicious activity
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"           # ℹ️ General information
    WARNING = "warning"     # ⚠️ Something to watch
    DANGER = "danger"       # 🚨 High risk activity
    CRITICAL = "critical"   # ☠️ Immediate action required


class AlertType(Enum):
    BUNDLE_DETECTED = "bundle_detected"
    DEV_DUMPING = "dev_dumping"
    LIQUIDITY_REMOVED = "liquidity_removed"
    LARGE_SELL = "large_sell"
    PRICE_DROP = "price_drop"
    NEW_CONTRACT = "new_contract"
    RUG_PULL = "rug_pull"
    SUSPICIOUS_TRADING = "suspicious_trading"
    MINT_DETECTED = "mint_detected"
    WHALE_MOVEMENT = "whale_movement"


@dataclass
class Alert:
    """Alert notification"""
    id: str
    timestamp: datetime
    alert_type: AlertType
    severity: AlertSeverity
    token_address: str
    token_name: str
    title: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    acknowledged: bool = False


class AlertSystem:
    """
    🚨 Real-time monitoring and alerting
    """
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.monitored_tokens: Dict[str, Dict] = {}
        self.alert_handlers: List[Callable] = []
        self.is_running = False
        
        # Alert thresholds
        self.thresholds = {
            'bundle_probability': 70,  # % to trigger alert
            'dev_dump_pct': 10,  # % dev wallet dumps to trigger
            'price_drop_pct': 30,  # % price drop to trigger
            'large_sell_usd': 10000,  # USD value to trigger
        }
    
    def add_handler(self, handler: Callable):
        """Add alert handler (Discord, Telegram, etc)"""
        self.alert_handlers.append(handler)
    
    async def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        token_address: str,
        token_name: str,
        title: str,
        message: str,
        data: Dict = None
    ) -> Alert:
        """Create and dispatch alert"""
        
        alert = Alert(
            id=f"{token_address[:8]}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            token_address=token_address,
            token_name=token_name,
            title=title,
            message=message,
            data=data or {},
            actions=self._suggest_actions(alert_type, severity)
        )
        
        self.alerts.append(alert)
        
        # Dispatch to handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"ALERT [{severity.value.upper()}]: {title}")
        
        return alert
    
    def _suggest_actions(self, alert_type: AlertType, severity: AlertSeverity) -> List[str]:
        """Suggest actions based on alert"""
        actions = []
        
        if severity in [AlertSeverity.DANGER, AlertSeverity.CRITICAL]:
            actions.append("Consider exiting position immediately")
        
        if alert_type == AlertType.BUNDLE_DETECTED:
            actions.append("Review bundle analysis")
            actions.append("Check wallet clusters")
        
        elif alert_type == AlertType.DEV_DUMPING:
            actions.append("Monitor dev wallet activity")
            actions.append("Set stop loss")
        
        elif alert_type == AlertType.LIQUIDITY_REMOVED:
            actions.append("EMERGENCY EXIT - Liquidity gone")
        
        elif alert_type == AlertType.RUG_PULL:
            actions.append("SELL IMMEDIATELY if possible")
        
        return actions
    
    async def check_bundle_alert(self, token_address: str, token_name: str, bundle_probability: float):
        """Check if bundle alert should fire"""
        if bundle_probability >= self.thresholds['bundle_probability']:
            await self.create_alert(
                alert_type=AlertType.BUNDLE_DETECTED,
                severity=AlertSeverity.DANGER if bundle_probability > 85 else AlertSeverity.WARNING,
                token_address=token_address,
                token_name=token_name,
                title=f"🚨 Bundle Detected: {bundle_probability:.0f}% probability",
                message=f"Token shows strong signs of wallet bundling. Multiple wallets likely controlled by same entity.",
                data={'bundle_probability': bundle_probability}
            )
    
    async def check_dev_dump_alert(self, token_address: str, token_name: str, dump_pct: float, wallet: str):
        """Alert when dev is dumping"""
        if dump_pct >= self.thresholds['dev_dump_pct']:
            await self.create_alert(
                alert_type=AlertType.DEV_DUMPING,
                severity=AlertSeverity.CRITICAL if dump_pct > 50 else AlertSeverity.DANGER,
                token_address=token_address,
                token_name=token_name,
                title=f"☠️ DEV DUMPING: {dump_pct:.1f}% sold",
                message=f"Developer wallet {wallet[:10]}... has dumped {dump_pct:.1f}% of holdings",
                data={'dump_percentage': dump_pct, 'wallet': wallet}
            )
    
    async def check_liquidity_alert(self, token_address: str, token_name: str, removed_pct: float):
        """Alert on liquidity removal"""
        if removed_pct > 50:
            await self.create_alert(
                alert_type=AlertType.LIQUIDITY_REMOVED,
                severity=AlertSeverity.CRITICAL,
                token_address=token_address,
                token_name=token_name,
                title="🚨 LIQUIDITY REMOVED",
                message=f"{removed_pct:.0f}% of liquidity has been removed. Potential rug pull in progress.",
                data={'removed_percentage': removed_pct}
            )
    
    async def check_price_drop_alert(self, token_address: str, token_name: str, drop_pct: float):
        """Alert on significant price drop"""
        if drop_pct >= self.thresholds['price_drop_pct']:
            await self.create_alert(
                alert_type=AlertType.PRICE_DROP,
                severity=AlertSeverity.DANGER if drop_pct > 50 else AlertSeverity.WARNING,
                token_address=token_address,
                token_name=token_name,
                title=f"📉 Price Drop: -{drop_pct:.1f}%",
                message=f"Token price has dropped significantly in short time period.",
                data={'drop_percentage': drop_pct}
            )
    
    def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """Get active (unacknowledged) alerts"""
        alerts = [a for a in self.alerts if not a.acknowledged]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def acknowledge_alert(self, alert_id: str):
        """Mark alert as acknowledged"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def format_alert(self, alert: Alert) -> str:
        """Format alert for display"""
        emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.DANGER: "🚨",
            AlertSeverity.CRITICAL: "☠️"
        }.get(alert.severity, "❓")
        
        lines = [
            f"{emoji} [{alert.severity.value.upper()}] {alert.title}",
            f"   Token: {alert.token_name}",
            f"   Time: {alert.timestamp.strftime('%H:%M:%S')}",
            f"   {alert.message}",
        ]
        
        if alert.actions:
            lines.append(f"   Suggested Actions:")
            for action in alert.actions:
                lines.append(f"      → {action}")
        
        return "\n".join(lines)


# Global alert system
alert_system = AlertSystem()


# Example handlers
async def console_handler(alert: Alert):
    """Print alert to console"""
    print("\n" + "=" * 70)
    print(alert_system.format_alert(alert))
    print("=" * 70)


async def discord_handler(alert: Alert):
    """Send to Discord webhook"""
    # Would integrate with actual Discord webhook
    pass


async def telegram_handler(alert: Alert):
    """Send to Telegram"""
    # Would integrate with Telegram bot
    pass


if __name__ == "__main__":
    # Demo
    async def demo():
        alert_system.add_handler(console_handler)
        
        # Simulate alerts
        await alert_system.check_bundle_alert(
            "Token123...", "TestCoin", 85
        )
        
        await alert_system.check_dev_dump_alert(
            "Token123...", "TestCoin", 25, "DeVaBc123..."
        )
        
        print("\nActive Alerts:")
        for alert in alert_system.get_active_alerts():
            print(f"  - {alert.title}")
    
    asyncio.run(demo())
