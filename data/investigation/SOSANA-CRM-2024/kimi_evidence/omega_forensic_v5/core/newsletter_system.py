"""
Newsletter System - Crypto Intelligence Briefings
=================================================
Morning crypto intelligence briefings and weekly newsletters.
Crypto payment integration for subscriptions.
"""

import json
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class SubscriptionTier(Enum):
    """Subscription tiers."""
    FREE = "free"
    BASIC = "basic"      # Weekly only
    PREMIUM = "premium"  # Daily + Weekly
    WHALE = "whale"      # Everything + exclusive


class NewsletterType(Enum):
    """Types of newsletters."""
    MORNING_BRIEFING = "morning_briefing"
    WEEKLY_DIGEST = "weekly_digest"
    SCAM_ALERT = "scam_alert"
    TRENDING_TOKENS = "trending_tokens"
    KOL_REPORT = "kol_report"


@dataclass
class Subscriber:
    """Newsletter subscriber."""
    email: str
    wallet_address: Optional[str] = None
    
    # Subscription
    tier: SubscriptionTier = SubscriptionTier.FREE
    subscribed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Preferences
    preferred_time: str = "08:00"  # UTC
    timezone: str = "UTC"
    
    # History
    newsletters_received: int = 0
    last_sent: Optional[datetime] = None
    
    # Payment
    payment_tx: Optional[str] = None
    payment_amount: float = 0.0
    payment_token: str = "USDC"
    
    def is_active(self) -> bool:
        """Check if subscription is active."""
        if self.tier == SubscriptionTier.FREE:
            return True
        if self.expires_at:
            return datetime.now() < self.expires_at
        return True


@dataclass
class NewsletterContent:
    """Content for a newsletter."""
    title: str
    type: NewsletterType
    created_at: datetime
    
    # Sections
    executive_summary: str = ""
    key_stories: List[Dict] = field(default_factory=list)
    trending_tokens: List[Dict] = field(default_factory=list)
    scam_alerts: List[Dict] = field(default_factory=list)
    kol_calls: List[Dict] = field(default_factory=list)
    market_data: Dict = field(default_factory=dict)
    
    # RMI specific
    investigation_updates: List[Dict] = field(default_factory=list)
    wallet_alerts: List[Dict] = field(default_factory=list)
    
    def to_html(self) -> str:
        """Convert to HTML email format."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #0a0a0f; color: #fff; }}
                .header {{ background: linear-gradient(90deg, #1a1a2e, #16213e); padding: 20px; text-align: center; }}
                .header h1 {{ color: #00d4ff; margin: 0; }}
                .section {{ padding: 20px; border-bottom: 1px solid #333; }}
                .section h2 {{ color: #00d4ff; }}
                .alert {{ background: #2d1810; border-left: 4px solid #ff6b6b; padding: 15px; margin: 10px 0; }}
                .token {{ background: #1a1a2e; padding: 15px; margin: 10px 0; border-radius: 8px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .cta {{ background: #00d4ff; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 RMI Intelligence</h1>
                <p>{self.title}</p>
                <p>{self.created_at.strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="section">
                <h2>📋 Executive Summary</h2>
                <p>{self.executive_summary}</p>
            </div>
        """
        
        # Scam alerts
        if self.scam_alerts:
            html += """
            <div class="section">
                <h2>🚨 Scam Alerts</h2>
            """
            for alert in self.scam_alerts[:3]:
                html += f"""
                <div class="alert">
                    <strong>{alert.get('token', 'Unknown')}</strong><br>
                    {alert.get('description', '')}<br>
                    <small>Risk: {alert.get('risk_level', 'Unknown')}</small>
                </div>
                """
            html += "</div>"
        
        # Trending tokens
        if self.trending_tokens:
            html += """
            <div class="section">
                <h2>📈 Trending Tokens</h2>
            """
            for token in self.trending_tokens[:5]:
                html += f"""
                <div class="token">
                    <strong>{token.get('symbol', 'UNKNOWN')}</strong> - {token.get('name', '')}<br>
                    Price: ${token.get('price', 0):.6f} | 
                    24h: {token.get('change_24h', 0):+.2f}%<br>
                    <small>Market Cap: ${token.get('market_cap', 0):,.0f}</small>
                </div>
                """
            html += "</div>"
        
        # Investigation updates
        if self.investigation_updates:
            html += """
            <div class="section">
                <h2>🔍 Investigation Updates</h2>
            """
            for update in self.investigation_updates[:3]:
                html += f"""
                <p><strong>{update.get('title', '')}</strong><br>
                {update.get('summary', '')}</p>
                """
            html += "</div>"
        
        # Footer
        html += f"""
            <div class="footer">
                <p>Built with Kimi AI | intel.cryptorugmunch.com</p>
                <p><a href="https://intel.cryptorugmunch.com/unsubscribe" style="color: #666;">Unsubscribe</a></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        md = f"# {self.title}\n\n"
        md += f"*{self.created_at.strftime('%B %d, %Y')}*\n\n"
        md += "---\n\n"
        
        md += f"## 📋 Executive Summary\n\n{self.executive_summary}\n\n"
        
        if self.scam_alerts:
            md += "## 🚨 Scam Alerts\n\n"
            for alert in self.scam_alerts[:3]:
                md += f"**{alert.get('token', 'Unknown')}** - {alert.get('description', '')}\n"
                md += f"Risk: {alert.get('risk_level', 'Unknown')}\n\n"
        
        if self.trending_tokens:
            md += "## 📈 Trending Tokens\n\n"
            for token in self.trending_tokens[:5]:
                md += f"**{token.get('symbol', 'UNKNOWN')}** - ${token.get('price', 0):.6f} ({token.get('change_24h', 0):+.2f}%)\n"
                md += f"Market Cap: ${token.get('market_cap', 0):,.0f}\n\n"
        
        if self.investigation_updates:
            md += "## 🔍 Investigation Updates\n\n"
            for update in self.investigation_updates[:3]:
                md += f"**{update.get('title', '')}**\n{update.get('summary', '')}\n\n"
        
        md += "---\n\n"
        md += "*Built with Kimi AI | intel.cryptorugmunch.com*\n"
        
        return md


class NewsletterSystem:
    """
    Manages newsletter subscriptions and content generation.
    """
    
    # Pricing in USDC
    PRICING = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.BASIC: 5,      # $5/month - Weekly only
        SubscriptionTier.PREMIUM: 15,   # $15/month - Daily + Weekly
        SubscriptionTier.WHALE: 50      # $50/month - Everything + exclusive
    }
    
    # Payment wallet
    PAYMENT_WALLET = "RMINewsletterPaymentWalletAddress"
    
    def __init__(self):
        self.subscribers: Dict[str, Subscriber] = {}  # email -> subscriber
        self.newsletter_history: List[NewsletterContent] = []
        self.pending_payments: Dict[str, Dict] = {}  # email -> payment info
        
    async def subscribe(
        self, 
        email: str, 
        tier: SubscriptionTier = SubscriptionTier.FREE,
        wallet_address: Optional[str] = None
    ) -> Subscriber:
        """Subscribe to newsletter."""
        if email in self.subscribers:
            subscriber = self.subscribers[email]
            subscriber.tier = tier
            if wallet_address:
                subscriber.wallet_address = wallet_address
            return subscriber
        
        subscriber = Subscriber(
            email=email,
            wallet_address=wallet_address,
            tier=tier
        )
        
        self.subscribers[email] = subscriber
        return subscriber
    
    async def generate_payment_request(
        self, 
        email: str, 
        tier: SubscriptionTier
    ) -> Dict:
        """Generate crypto payment request."""
        amount = self.PRICING.get(tier, 0)
        
        if amount == 0:
            return {"error": "Free tier doesn't require payment"}
        
        # Generate unique payment ID
        payment_id = f"RMI-{email[:8]}-{int(datetime.now().timestamp())}"
        
        payment_request = {
            "payment_id": payment_id,
            "amount": amount,
            "token": "USDC",
            "network": "Solana",
            "recipient_wallet": self.PAYMENT_WALLET,
            "memo": payment_id,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "instructions": f"""
Send exactly {amount} USDC to:
{self.PAYMENT_WALLET}

Include memo: {payment_id}

Payment expires in 24 hours.
"""
        }
        
        self.pending_payments[email] = payment_request
        
        return payment_request
    
    async def verify_payment(self, email: str, tx_signature: str) -> bool:
        """Verify crypto payment."""
        # In production:
        # 1. Query Solana for transaction
        # 2. Verify amount and recipient
        # 3. Confirm memo matches
        # 4. Update subscriber status
        
        subscriber = self.subscribers.get(email)
        if not subscriber:
            return False
        
        # Simulate verification
        payment_info = self.pending_payments.get(email)
        if not payment_info:
            return False
        
        # Update subscriber
        subscriber.payment_tx = tx_signature
        subscriber.payment_amount = payment_info["amount"]
        subscriber.expires_at = datetime.now() + timedelta(days=30)
        
        # Clean up pending
        del self.pending_payments[email]
        
        return True
    
    async def generate_morning_briefing(self) -> NewsletterContent:
        """Generate morning crypto intelligence briefing."""
        briefing = NewsletterContent(
            title="☀️ Morning Crypto Intelligence Briefing",
            type=NewsletterType.MORNING_BRIEFING,
            created_at=datetime.now()
        )
        
        # In production, fetch from various sources
        briefing.executive_summary = """
Good morning! Here's your daily crypto intelligence briefing.

Market Overview: Bitcoin holding above $65K, altcoins showing mixed signals.
Scam Activity: 3 new potential scams detected overnight.
Investigation Update: CRM case progressing with new wallet clusters identified.
"""
        
        # Add sample scam alerts
        briefing.scam_alerts = [
            {
                "token": "SCAM1",
                "description": "Unlocked liquidity, new deployer wallet",
                "risk_level": "HIGH"
            },
            {
                "token": "SCAM2",
                "description": "Bot activity detected, 90% supply concentrated",
                "risk_level": "CRITICAL"
            }
        ]
        
        # Add trending tokens
        briefing.trending_tokens = [
            {"symbol": "BONK", "name": "Bonk", "price": 0.000012, "change_24h": 15.5, "market_cap": 750000000},
            {"symbol": "WIF", "name": "Dogwifhat", "price": 1.85, "change_24h": -5.2, "market_cap": 1800000000},
            {"symbol": "POPCAT", "name": "Popcat", "price": 0.45, "change_24h": 8.3, "market_cap": 450000000}
        ]
        
        # Add investigation updates
        briefing.investigation_updates = [
            {
                "title": "CRM Case: New Wallet Cluster Identified",
                "summary": "Found 15 connected wallets with coordinated transaction patterns."
            }
        ]
        
        self.newsletter_history.append(briefing)
        return briefing
    
    async def generate_weekly_digest(self) -> NewsletterContent:
        """Generate weekly newsletter."""
        digest = NewsletterContent(
            title="📊 Weekly Crypto Intelligence Digest",
            type=NewsletterType.WEEKLY_DIGEST,
            created_at=datetime.now()
        )
        
        digest.executive_summary = """
This week's crypto intelligence summary:

- 12 new scams detected and reported
- CRM investigation: 3 new suspect wallets identified
- KOL leaderboard: Top performers this week
- Market analysis: Key trends and patterns
"""
        
        # More comprehensive content than daily
        digest.scam_alerts = [
            {"token": "SCAM1", "description": "Rug pulled on Tuesday, $500K lost", "risk_level": "CONFIRMED"},
            {"token": "SCAM2", "description": "Honeypot contract identified", "risk_level": "CONFIRMED"},
            {"token": "SCAM3", "description": "Pump and dump pattern", "risk_level": "SUSPICIOUS"}
        ]
        
        digest.trending_tokens = [
            {"symbol": "BONK", "name": "Bonk", "price": 0.000012, "change_24h": 45.2, "market_cap": 750000000},
            {"symbol": "WIF", "name": "Dogwifhat", "price": 1.85, "change_24h": 22.1, "market_cap": 1800000000},
            {"symbol": "POPCAT", "name": "Popcat", "price": 0.45, "change_24h": 18.5, "market_cap": 450000000},
            {"symbol": "MEW", "name": "Cat in a Dogs World", "price": 0.003, "change_24h": 35.0, "market_cap": 280000000}
        ]
        
        digest.investigation_updates = [
            {
                "title": "CRM Case Weekly Progress",
                "summary": "Identified 15 connected wallets, 3 with direct scammer links. Preparing evidence package."
            },
            {
                "title": "New KOL Analysis",
                "summary": "Analyzed 50 KOLs this week. 12 flagged for suspicious activity."
            }
        ]
        
        self.newsletter_history.append(digest)
        return digest
    
    async def send_newsletter(self, newsletter: NewsletterContent, subscriber: Subscriber):
        """Send newsletter to subscriber."""
        if not subscriber.is_active():
            return False
        
        # Check tier access
        if newsletter.type == NewsletterType.MORNING_BRIEFING:
            if subscriber.tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.WHALE]:
                return False
        
        # In production, send via email service (SendGrid, AWS SES, etc.)
        # For now, just log
        
        subscriber.newsletters_received += 1
        subscriber.last_sent = datetime.now()
        
        return True
    
    async def send_to_all(self, newsletter: NewsletterContent):
        """Send newsletter to all eligible subscribers."""
        sent_count = 0
        
        for subscriber in self.subscribers.values():
            if await self.send_newsletter(newsletter, subscriber):
                sent_count += 1
        
        return sent_count
    
    def get_subscriber_stats(self) -> Dict:
        """Get subscriber statistics."""
        tiers = {}
        active = 0
        total = len(self.subscribers)
        
        for sub in self.subscribers.values():
            tier = sub.tier.value
            tiers[tier] = tiers.get(tier, 0) + 1
            if sub.is_active():
                active += 1
        
        return {
            "total_subscribers": total,
            "active_subscribers": active,
            "by_tier": tiers,
            "revenue_monthly": sum(
                self.PRICING.get(s.tier, 0) 
                for s in self.subscribers.values() 
                if s.is_active()
            )
        }
    
    async def unsubscribe(self, email: str) -> bool:
        """Unsubscribe a user."""
        if email in self.subscribers:
            del self.subscribers[email]
            return True
        return False


# Global instance
_system = None

def get_newsletter_system() -> NewsletterSystem:
    """Get global newsletter system."""
    global _system
    if _system is None:
        _system = NewsletterSystem()
    return _system


if __name__ == "__main__":
    print("=" * 70)
    print("NEWSLETTER SYSTEM - Crypto Intelligence Briefings")
    print("=" * 70)
    
    system = get_newsletter_system()
    
    print("\n📧 Newsletter Types:")
    print("  ☀️ Morning Briefing - Daily intelligence (Premium+)")
    print("  📊 Weekly Digest - Weekly summary (Basic+)")
    print("  🚨 Scam Alerts - Real-time scam notifications")
    print("  📈 Trending Tokens - Hot tokens analysis")
    print("  🎯 KOL Report - Influencer performance")
    
    print("\n💰 Pricing (USDC/month):")
    print("  🆓 Free - $0 - Basic alerts")
    print("  📰 Basic - $5 - Weekly newsletter")
    print("  ⭐ Premium - $15 - Daily + Weekly")
    print("  🐋 Whale - $50 - Everything + exclusive content")
    
    print("\n🔌 Payment:")
    print("  • Solana USDC")
    print("  • Auto-verification")
    print("  • 30-day subscription")
    
    print("\n" + "=" * 70)
