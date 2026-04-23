#!/usr/bin/env python3
"""
📢 RugMuncher Alert Router
Dual-channel notification system with automatic sanitization

PRIVATE CHANNEL: Full analysis with wallet addresses, PII, detailed data
PUBLIC CHANNEL: Sanitized summaries, no sensitive info

This protects user privacy while keeping community informed
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Telegram Channel IDs (get from @userinfobot or @RawDataBot)
PRIVATE_CHANNEL_ID = os.getenv('PRIVATE_CHANNEL_ID', '-1001111111111')  # Admin bunker
PUBLIC_CHANNEL_ID = os.getenv('PUBLIC_CHANNEL_ID', '-1002222222222')    # Community alerts

# Risk thresholds
RISK_CRITICAL = 80   # Immediate alert to both channels
RISK_HIGH = 60       # Alert to private, summary to public
RISK_MEDIUM = 40     # Log only, no alerts


class AlertLevel(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"            # Warning, review needed
    MEDIUM = "medium"        # Caution
    LOW = "low"              # Informational


@dataclass
class ScanResult:
    """Token scan result with routing info"""
    contract_address: str
    chain: str
    risk_score: int
    threat_level: str
    findings: List[Dict[str, Any]]
    wallet_data: Optional[Dict] = None
    holder_data: Optional[List] = None
    raw_analysis: Optional[str] = None


class AlertRouter:
    """
    📢 Routes alerts between private (full) and public (sanitized) channels
    
    Security:
    - Private channel: Full wallet addresses, PII, detailed analysis
    - Public channel: Truncated addresses, sanitized summaries
    - Never exposes sensitive user data publicly
    """
    
    def __init__(self, bot=None):
        self.bot = bot
        self.private_channel = PRIVATE_CHANNEL_ID
        self.public_channel = PUBLIC_CHANNEL_ID
        
    def _truncate_wallet(self, address: str, visible: int = 6) -> str:
        """Truncate wallet address for public display"""
        if not address or len(address) < visible * 2 + 4:
            return address
        return f"{address[:visible]}...{address[-visible:]}"
    
    def _get_risk_emoji(self, score: int) -> str:
        """Get emoji indicator for risk level"""
        if score >= 80:
            return "🚨"
        elif score >= 60:
            return "⚠️"
        elif score >= 40:
            return "⚡"
        else:
            return "✅"
    
    def _sanitize_for_public(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII and sensitive data for public channel"""
        sanitized = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Truncate wallet addresses
            if any(k in key_lower for k in ['wallet', 'address', 'holder', 'from', 'to']):
                if isinstance(value, str) and value.startswith('0x'):
                    sanitized[key] = self._truncate_wallet(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        self._truncate_wallet(item) if isinstance(item, str) and item.startswith('0x')
                        else item for item in value
                    ]
                else:
                    sanitized[key] = value
                    
            # Remove PII
            elif any(k in key_lower for k in ['ip', 'telegram', 'user_id', 'email', 'phone']):
                sanitized[key] = '[REDACTED]'
                
            # Aggregate large amounts (don't expose exact whale amounts)
            elif any(k in key_lower for k in ['amount', 'balance', 'value']) and isinstance(value, (int, float)):
                if value > 100000:
                    sanitized[key] = f">$100K"
                elif value > 10000:
                    sanitized[key] = f">$10K"
                else:
                    sanitized[key] = value
                    
            # Recurse into nested dicts
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_for_public(value)
                
            # Process lists of dicts
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                sanitized[key] = [self._sanitize_for_public(item) for item in value]
                
            else:
                sanitized[key] = value
                
        return sanitized
    
    def format_private_alert(self, scan: ScanResult) -> str:
        """
        🔒 Format FULL alert for private admin channel
        Includes: Full addresses, detailed analysis, PII
        """
        emoji = self._get_risk_emoji(scan.risk_score)
        
        message = f"""
{emoji} <b>RUGMUNCHBOT ALERT - {scan.threat_level.upper()}</b>

<b>Contract:</b> <code>{scan.contract_address}</code>
<b>Chain:</b> {scan.chain.upper()}
<b>Risk Score:</b> <code>{scan.risk_score}/100</b>

<b>🔍 FINDINGS:</b>
"""
        
        # Add findings with full details
        for finding in scan.findings[:10]:  # Top 10
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🔵'
            }.get(finding.get('severity', ''), '⚪')
            
            message += f"\n{severity_emoji} <b>{finding.get('title', 'Issue')}</b>"
            message += f"\n   {finding.get('description', 'No details')}"
            
            # Include wallet addresses in private channel
            if 'wallet' in finding:
                message += f"\n   Wallet: <code>{finding['wallet']}</code>"
            if 'tx_hash' in finding:
                message += f"\n   TX: <code>{finding['tx_hash']}</code>"
        
        # Include holder data if available (private only)
        if scan.holder_data:
            message += f"\n\n<b>👥 TOP HOLDERS:</b>"
            for holder in scan.holder_data[:5]:
                addr = holder.get('address', 'Unknown')
                pct = holder.get('percentage', 0)
                message += f"\n  <code>{addr}</code>: {pct}%"
        
        # Include wallet analysis if available (private only)
        if scan.wallet_data:
            message += f"\n\n<b>💼 WALLET ANALYSIS:</b>"
            message += f"\n  {scan.wallet_data}"
        
        message += f"\n\n<i>Full analysis via /scan {scan.contract_address}</i>"
        
        return message
    
    def format_public_alert(self, scan: ScanResult) -> str:
        """
        📢 Format SANITIZED alert for public community channel
        No wallet addresses, no PII, no exact amounts
        """
        emoji = self._get_risk_emoji(scan.risk_score)
        truncated_addr = self._truncate_wallet(scan.contract_address)
        
        message = f"""
{emoji} <b>RUGMUNCHBOT ALERT</b>

<b>Token:</b> <code>{truncated_addr}</code>
<b>Chain:</b> {scan.chain.upper()}
<b>Risk Score:</b> <code>{scan.risk_score}/100</b> - {scan.threat_level.upper()}
"""
        
        # Sanitized findings summary
        if scan.findings:
            critical_count = sum(1 for f in scan.findings if f.get('severity') == 'critical')
            high_count = sum(1 for f in scan.findings if f.get('severity') == 'high')
            
            if critical_count > 0:
                message += f"\n⚠️ <b>{critical_count} Critical</b> issues detected"
            if high_count > 0:
                message += f"\n⚡ <b>{high_count} High Risk</b> issues detected"
            
            # General warning categories (no specifics)
            categories = set(f.get('category', 'Unknown') for f in scan.findings[:3])
            if categories:
                message += f"\n\n<b>Issues:</b> {', '.join(categories)}"
        
        # Generic recommendation based on score
        if scan.risk_score >= 80:
            message += "\n\n🛑 <b>Recommendation:</b> Avoid - High probability of scam"
        elif scan.risk_score >= 60:
            message += "\n\n⚠️ <b>Recommendation:</b> Exercise extreme caution"
        elif scan.risk_score >= 40:
            message += "\n\n⚡ <b>Recommendation:</b> Research thoroughly before investing"
        else:
            message += "\n\n✅ <b>Recommendation:</b> Lower risk detected, still DYOR"
        
        message += f"\n\n<i>Detailed scan: @RugMuncherBot</i>"
        
        return message
    
    async def send_alert(self, scan: ScanResult) -> Dict[str, Any]:
        """
        📤 Route alert to appropriate channels based on risk
        
        CRITICAL (>80): Both channels immediately
        HIGH (60-80): Private full, public summary
        MEDIUM (40-60): Private only
        LOW (<40): Log only
        """
        results = {
            'private_sent': False,
            'public_sent': False,
            'risk_level': 'unknown'
        }
        
        if scan.risk_score >= RISK_CRITICAL:
            results['risk_level'] = 'critical'
            
            # Send to private channel (full details)
            private_msg = self.format_private_alert(scan)
            if self.bot:
                try:
                    await self.bot.send_message(
                        chat_id=self.private_channel,
                        text=private_msg,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                    results['private_sent'] = True
                    logger.info(f"Critical alert sent to private channel: {scan.contract_address[:16]}")
                except Exception as e:
                    logger.error(f"Failed to send private alert: {e}")
            
            # Send sanitized to public channel
            public_msg = self.format_public_alert(scan)
            if self.bot:
                try:
                    await self.bot.send_message(
                        chat_id=self.public_channel,
                        text=public_msg,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                    results['public_sent'] = True
                    logger.info(f"Critical alert sent to public channel: {scan.contract_address[:16]}")
                except Exception as e:
                    logger.error(f"Failed to send public alert: {e}")
                    
        elif scan.risk_score >= RISK_HIGH:
            results['risk_level'] = 'high'
            
            # Private channel only for high risk
            private_msg = self.format_private_alert(scan)
            if self.bot:
                try:
                    await self.bot.send_message(
                        chat_id=self.private_channel,
                        text=private_msg,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                    results['private_sent'] = True
                    logger.info(f"High risk alert sent to private channel: {scan.contract_address[:16]}")
                except Exception as e:
                    logger.error(f"Failed to send private alert: {e}")
            
            # Optional: Send brief public warning
            brief_msg = f"⚠️ <b>High Risk Token Detected</b>\n\nContract: <code>{self._truncate_wallet(scan.contract_address)}</code>\nRisk Score: <code>{scan.risk_score}/100</code>\n\n<i>Use @RugMuncherBot for full analysis</i>"
            
            if self.bot:
                try:
                    await self.bot.send_message(
                        chat_id=self.public_channel,
                        text=brief_msg,
                        parse_mode='HTML'
                    )
                    results['public_sent'] = True
                except Exception as e:
                    logger.error(f"Failed to send public brief: {e}")
                    
        elif scan.risk_score >= RISK_MEDIUM:
            results['risk_level'] = 'medium'
            
            # Log only, no alerts
            logger.info(f"Medium risk token logged: {scan.contract_address} ({scan.risk_score})")
            
        else:
            results['risk_level'] = 'low'
            logger.debug(f"Low risk token: {scan.contract_address} ({scan.risk_score})")
        
        return results
    
    def generate_shareable_card(self, scan: ScanResult) -> str:
        """
        🎴 Generate a sanitized shareable card for social media
        No sensitive data, just the essentials
        """
        emoji = self._get_risk_emoji(scan.risk_score)
        addr = self._truncate_wallet(scan.contract_address)
        
        card = f"""
╔═══════════════════════════════════════╗
║     {emoji} RUGMUNCHBOT SCAN {emoji}        ║
╠═══════════════════════════════════════╣
║ Contract: {addr:<26} ║
║ Chain:    {scan.chain.upper():<26} ║
║ Risk:     {scan.risk_score}/100{' ' * (25 - len(str(scan.risk_score)))} ║
║ Level:    {scan.threat_level.upper():<26} ║
╚═══════════════════════════════════════╝

Scanned by @RugMuncherBot
Stay safe. Stay informed."""
        
        return card


# ═══════════════════════════════════════════════════════════
# TELEGRAM BOT INTEGRATION
# ═══════════════════════════════════════════════════════════

async def send_risk_alert(bot, scan_result: Dict[str, Any]) -> Dict[str, bool]:
    """
    🚀 Convenience function for bot integration
    
    Usage in your bot:
        from rugmuncher_alert_router import send_risk_alert
        
        result = await send_risk_alert(bot, {
            'contract_address': '0x742d...',
            'chain': 'bsc',
            'risk_score': 85,
            'threat_level': 'critical',
            'findings': [...],
            'holder_data': [...]
        })
    """
    router = AlertRouter(bot)
    
    scan = ScanResult(
        contract_address=scan_result.get('contract_address', ''),
        chain=scan_result.get('chain', 'eth'),
        risk_score=scan_result.get('risk_score', 50),
        threat_level=scan_result.get('threat_level', 'unknown'),
        findings=scan_result.get('findings', []),
        wallet_data=scan_result.get('wallet_data'),
        holder_data=scan_result.get('holder_data')
    )
    
    return await router.send_alert(scan)


# ═══════════════════════════════════════════════════════════
# EXAMPLE/DEMO
# ═══════════════════════════════════════════════════════════

def demo():
    """Demo the alert routing"""
    print("📢 RugMuncher Alert Router Demo")
    print("=" * 60)
    
    # Example scan result
    scan = ScanResult(
        contract_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        chain="bsc",
        risk_score=85,
        threat_level="critical",
        findings=[
            {"severity": "critical", "title": "Honeypot Detected", "description": "Cannot sell tokens", "wallet": "0x742d...bEb"},
            {"severity": "high", "title": "Ownership Not Renounced", "description": "Owner can mint", "wallet": "0x8ba1...0000"},
            {"severity": "medium", "title": "High Tax", "description": "25% buy tax detected"}
        ],
        holder_data=[
            {"address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", "percentage": 45.5},
            {"address": "0x8ba1f109551bD432803012645Hac136c98C0000", "percentage": 12.3}
        ]
    )
    
    router = AlertRouter()
    
    print("\n🔒 PRIVATE CHANNEL (Full Analysis):")
    print("-" * 60)
    print(router.format_private_alert(scan))
    
    print("\n\n📢 PUBLIC CHANNEL (Sanitized):")
    print("-" * 60)
    print(router.format_public_alert(scan))
    
    print("\n\n🎴 SHAREABLE CARD:")
    print("-" * 60)
    print(router.generate_shareable_card(scan))
    
    print("\n\n📊 Routing Decision:")
    print(f"  Risk Score: {scan.risk_score}")
    print(f"  → Private Channel: FULL DATA")
    print(f"  → Public Channel: SANITIZED")
    print(f"  → Wallet addresses truncated")
    print(f"  → PII removed")


if __name__ == "__main__":
    demo()
