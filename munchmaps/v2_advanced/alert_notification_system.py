#!/usr/bin/env python3
"""
Alert & Notification System
Real-time monitoring and alerts for suspicious activity
"""
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json

class AlertSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    NEW_TRANSACTION = "new_transaction"
    LARGE_TRANSFER = "large_transfer"
    CEX_INTERACTION = "cex_interaction"
    MIXER_USAGE = "mixer_usage"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    WALLET_ACTIVATION = "wallet_activation"
    COORDINATED_ACTIVITY = "coordinated_activity"
    SANCTIONS_HIT = "sanctions_hit"
    THREAT_DETECTED = "threat_detected"
    FUND_MOVEMENT = "fund_movement"

class AlertRule:
    """Rule for generating alerts"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        conditions: Dict,
        actions: List[str],
        cooldown_minutes: int = 60
    ):
        self.rule_id = rule_id
        self.name = name
        self.alert_type = alert_type
        self.severity = severity
        self.conditions = conditions
        self.actions = actions
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None
        self.trigger_count = 0
    
    def check_conditions(self, event_data: Dict) -> bool:
        """Check if event matches alert conditions"""
        # Check cooldown
        if self.last_triggered:
            cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return False
        
        # Check each condition
        for key, expected in self.conditions.items():
            actual = event_data.get(key)
            
            if isinstance(expected, dict):
                # Range condition
                if 'min' in expected and actual < expected['min']:
                    return False
                if 'max' in expected and actual > expected['max']:
                    return False
            elif isinstance(expected, list):
                # One of condition
                if actual not in expected:
                    return False
            else:
                # Exact match
                if actual != expected:
                    return False
        
        return True
    
    def trigger(self, event_data: Dict) -> Dict:
        """Trigger the alert"""
        self.last_triggered = datetime.now()
        self.trigger_count += 1
        
        return {
            'rule_id': self.rule_id,
            'rule_name': self.name,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'timestamp': datetime.now().isoformat(),
            'event_data': event_data,
            'actions': self.actions,
            'trigger_count': self.trigger_count
        }


class AlertNotificationSystem:
    """
    Real-time alert and notification system
    """
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alert_history: List[Dict] = []
        self.subscribers: Dict[str, List[Callable]] = {
            'email': [],
            'webhook': [],
            'slack': [],
            'telegram': [],
            'dashboard': []
        }
        self.muted_until = {}
        
    def create_rule(self, rule_config: Dict) -> AlertRule:
        """Create new alert rule"""
        rule = AlertRule(
            rule_id=rule_config['id'],
            name=rule_config['name'],
            alert_type=AlertType(rule_config['type']),
            severity=AlertSeverity(rule_config['severity']),
            conditions=rule_config['conditions'],
            actions=rule_config['actions'],
            cooldown_minutes=rule_config.get('cooldown', 60)
        )
        
        self.rules[rule.rule_id] = rule
        return rule
    
    def setup_default_rules(self):
        """Setup default alert rules"""
        default_rules = [
            {
                'id': 'large_transfer',
                'name': 'Large Transfer Detected',
                'type': 'large_transfer',
                'severity': 'high',
                'conditions': {'value_usd': {'min': 100000}},
                'actions': ['email', 'dashboard', 'webhook'],
                'cooldown': 30
            },
            {
                'id': 'mixer_usage',
                'name': 'Mixer/Tumbler Usage',
                'type': 'mixer_usage',
                'severity': 'critical',
                'conditions': {'to_address': ['tornado_cash', 'samourai']},
                'actions': ['email', 'dashboard', 'webhook'],
                'cooldown': 5
            },
            {
                'id': 'sanctions_hit',
                'name': 'Sanctions List Match',
                'type': 'sanctions_hit',
                'severity': 'critical',
                'conditions': {'sanctions_match': True},
                'actions': ['email', 'dashboard', 'webhook', 'slack'],
                'cooldown': 0  # No cooldown for sanctions
            },
            {
                'id': 'coordinated_movement',
                'name': 'Coordinated Wallet Movement',
                'type': 'coordinated_activity',
                'severity': 'high',
                'conditions': {'cluster_size': {'min': 5}, 'time_window_minutes': {'max': 60}},
                'actions': ['email', 'dashboard'],
                'cooldown': 60
            },
            {
                'id': 'new_wallet_activation',
                'name': 'Monitored Wallet Activated',
                'type': 'wallet_activation',
                'severity': 'medium',
                'conditions': {'previous_activity_hours': {'min': 168}},
                'actions': ['dashboard'],
                'cooldown': 1440  # 24 hours
            },
            {
                'id': 'cex_cashout',
                'name': 'CEX Cashout Detected',
                'type': 'cex_interaction',
                'severity': 'high',
                'conditions': {'interaction_type': 'deposit', 'cex_tier': 'major'},
                'actions': ['email', 'dashboard', 'webhook'],
                'cooldown': 60
            },
            {
                'id': 'threat_detected',
                'name': 'High-Risk Threat Detected',
                'type': 'threat_detected',
                'severity': 'critical',
                'conditions': {'threat_tier': 'CRITICAL', 'confidence': {'min': 0.8}},
                'actions': ['email', 'dashboard', 'webhook', 'slack', 'telegram'],
                'cooldown': 0
            }
        ]
        
        for rule_config in default_rules:
            self.create_rule(rule_config)
        
        return len(default_rules)
    
    def process_event(self, event_data: Dict) -> List[Dict]:
        """Process event and generate alerts"""
        triggered_alerts = []
        
        for rule in self.rules.values():
            if rule.check_conditions(event_data):
                alert = rule.trigger(event_data)
                triggered_alerts.append(alert)
                self.alert_history.append(alert)
                
                # Dispatch to subscribers
                self._dispatch_alert(alert)
        
        return triggered_alerts
    
    def _dispatch_alert(self, alert: Dict):
        """Dispatch alert to all subscribers"""
        for action in alert['actions']:
            if action in self.subscribers:
                for callback in self.subscribers[action]:
                    try:
                        callback(alert)
                    except Exception as e:
                        print(f"Error dispatching alert to {action}: {e}")
    
    def subscribe(self, channel: str, callback: Callable):
        """Subscribe to alerts on a channel"""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)
    
    def unsubscribe(self, channel: str, callback: Callable):
        """Unsubscribe from alerts"""
        if channel in self.subscribers:
            if callback in self.subscribers[channel]:
                self.subscribers[channel].remove(callback)
    
    def get_recent_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None,
        hours: int = 24
    ) -> List[Dict]:
        """Get recent alerts with optional filtering"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        filtered = []
        for alert in reversed(self.alert_history):  # Newest first
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time < cutoff:
                break
            
            if severity and alert['severity'] != severity.value:
                continue
            if alert_type and alert['alert_type'] != alert_type.value:
                continue
            
            filtered.append(alert)
        
        return filtered
    
    def get_alert_statistics(self, hours: int = 24) -> Dict:
        """Get alert statistics"""
        recent = self.get_recent_alerts(hours=hours)
        
        by_severity = {}
        by_type = {}
        
        for alert in recent:
            sev = alert['severity']
            typ = alert['alert_type']
            
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_type[typ] = by_type.get(typ, 0) + 1
        
        return {
            'total_alerts': len(recent),
            'time_period_hours': hours,
            'by_severity': by_severity,
            'by_type': by_type,
            'most_triggered_rules': self._get_top_rules(5)
        }
    
    def _get_top_rules(self, n: int) -> List[Dict]:
        """Get most frequently triggered rules"""
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: r.trigger_count,
            reverse=True
        )
        
        return [
            {
                'rule_id': r.rule_id,
                'name': r.name,
                'trigger_count': r.trigger_count
            }
            for r in sorted_rules[:n]
        ]
    
    def mute_alerts(self, rule_id: str, duration_minutes: int):
        """Temporarily mute alerts for a rule"""
        self.muted_until[rule_id] = datetime.now() + timedelta(minutes=duration_minutes)
    
    def export_alerts(self, filepath: str, hours: int = 24):
        """Export alerts to file"""
        alerts = self.get_recent_alerts(hours=hours)
        
        with open(filepath, 'w') as f:
            json.dump(alerts, f, indent=2, default=str)
        
        return len(alerts)


class RealTimeMonitor:
    """
    Real-time monitoring of wallet addresses
    """
    
    def __init__(self, alert_system: AlertNotificationSystem):
        self.alert_system = alert_system
        self.watched_addresses: Dict[str, Dict] = {}
        self.running = False
    
    def add_watch(self, address: str, config: Dict):
        """Add address to watch list"""
        self.watched_addresses[address] = {
            'added_at': datetime.now().isoformat(),
            'config': config,
            'last_checked': None,
            'alert_rules': config.get('rules', ['all'])
        }
    
    def remove_watch(self, address: str):
        """Remove address from watch list"""
        if address in self.watched_addresses:
            del self.watched_addresses[address]
    
    async def start_monitoring(self, check_interval_seconds: int = 60):
        """Start real-time monitoring"""
        self.running = True
        
        while self.running:
            await self._check_all_watches()
            await asyncio.sleep(check_interval_seconds)
    
    async def _check_all_watches(self):
        """Check all watched addresses"""
        for address, watch_config in self.watched_addresses.items():
            try:
                # This would integrate with blockchain APIs
                new_transactions = await self._fetch_new_transactions(address)
                
                for tx in new_transactions:
                    event_data = self._transaction_to_event(tx, address)
                    self.alert_system.process_event(event_data)
                
                watch_config['last_checked'] = datetime.now().isoformat()
                
            except Exception as e:
                print(f"Error checking {address}: {e}")
    
    async def _fetch_new_transactions(self, address: str) -> List[Dict]:
        """Fetch new transactions for address"""
        # This integrates with the multi-chain manager
        # Placeholder for actual implementation
        return []
    
    def _transaction_to_event(self, tx: Dict, watched_address: str) -> Dict:
        """Convert transaction to event format"""
        return {
            'type': 'transaction',
            'address': watched_address,
            'tx_hash': tx.get('hash'),
            'from': tx.get('from'),
            'to': tx.get('to'),
            'value_usd': tx.get('value_usd', 0),
            'timestamp': tx.get('timestamp'),
            'chain': tx.get('chain', 'unknown')
        }
    
    def stop(self):
        """Stop monitoring"""
        self.running = False


if __name__ == "__main__":
    print("Alert & Notification System initialized")
    
    # Setup
    alert_system = AlertNotificationSystem()
    num_rules = alert_system.setup_default_rules()
    print(f"Created {num_rules} default alert rules")
    
    # Demo alert
    test_event = {
        'type': 'transaction',
        'value_usd': 150000,
        'to_address': '0x123...',
        'from_address': '0x456...',
        'chain': 'ethereum'
    }
    
    alerts = alert_system.process_event(test_event)
    print(f"Generated {len(alerts)} alerts from test event")
    
    for alert in alerts:
        print(f"  - {alert['rule_name']} ({alert['severity']})")
