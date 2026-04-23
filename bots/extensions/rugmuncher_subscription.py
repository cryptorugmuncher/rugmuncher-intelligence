#!/usr/bin/env python3
"""
💳 RugMuncher Subscription & Payment Management
Handles Free/Premium/Whale tiers with crypto payments
"""

import os
import sqlite3
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class SubscriptionTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    WHALE = "whale"
    ADMIN = "admin"


@dataclass
class Subscription:
    user_id: int
    tier: SubscriptionTier
    expires_at: Optional[datetime]
    scans_today: int
    total_scans: int
    payment_address: Optional[str]
    payment_tx_hash: Optional[str]
    created_at: datetime


class RugMuncherSubscriptionManager:
    """
    💳 Manages user subscriptions and payment verification
    """
    
    # Tier limits
    TIERS = {
        SubscriptionTier.FREE: {
            'daily_scans': 3,
            'max_wallet_tracks': 1,
            'max_alerts': 1,
            'api_access': False,
            'priority_support': False,
            'price_monthly': 0,
            'price_yearly': 0
        },
        SubscriptionTier.PREMIUM: {
            'daily_scans': 50,
            'max_wallet_tracks': 10,
            'max_alerts': 10,
            'api_access': True,
            'priority_support': True,
            'price_monthly': 29.99,
            'price_yearly': 299.99
        },
        SubscriptionTier.WHALE: {
            'daily_scans': 999999,  # Unlimited
            'max_wallet_tracks': 100,
            'max_alerts': 100,
            'api_access': True,
            'priority_support': True,
            'custom_reports': True,
            'price_monthly': 99.99,
            'price_yearly': 999.99
        },
        SubscriptionTier.ADMIN: {
            'daily_scans': 999999,
            'max_wallet_tracks': 999999,
            'max_alerts': 999999,
            'api_access': True,
            'priority_support': True,
            'custom_reports': True,
            'price_monthly': 0,
            'price_yearly': 0
        }
    }
    
    # Payment addresses (loaded from env)
    PAYMENT_WALLETS = {
        'ETH': os.getenv('PAYMENT_ETH_WALLET', ''),
        'BNB': os.getenv('PAYMENT_BNB_WALLET', ''),
        'SOL': os.getenv('PAYMENT_SOL_WALLET', ''),
        'USDT_ETH': os.getenv('PAYMENT_USDT_ETH_WALLET', ''),
        'USDT_BSC': os.getenv('PAYMENT_USDT_BSC_WALLET', ''),
        'USDC_ETH': os.getenv('PAYMENT_USDC_ETH_WALLET', '')
    }
    
    def __init__(self, db_path: str = "/root/rugmuncher.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize subscription tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Subscriptions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                tier TEXT DEFAULT 'free',
                expires_at TIMESTAMP,
                scans_today INTEGER DEFAULT 0,
                total_scans INTEGER DEFAULT 0,
                payment_address TEXT,
                payment_tx_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Payment transactions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                currency TEXT,
                tier TEXT,
                duration_months INTEGER,
                tx_hash TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                confirmed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Scan usage tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS scan_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scan_date DATE DEFAULT CURRENT_DATE,
                scan_count INTEGER DEFAULT 0,
                UNIQUE(user_id, scan_date)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def get_subscription(self, user_id: int) -> Subscription:
        """Get user's current subscription"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT tier, expires_at, scans_today, total_scans, 
                   payment_address, payment_tx_hash, created_at
            FROM subscriptions WHERE user_id = ?
        ''', (user_id,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            # Create free subscription
            self._create_subscription(user_id)
            return self.get_subscription(user_id)
        
        tier = SubscriptionTier(row[0])
        expires_at = datetime.fromisoformat(row[1]) if row[1] else None
        
        # Check if subscription expired
        if expires_at and datetime.now() > expires_at:
            if tier not in [SubscriptionTier.FREE, SubscriptionTier.ADMIN]:
                self._downgrade_to_free(user_id)
                tier = SubscriptionTier.FREE
                expires_at = None
        
        return Subscription(
            user_id=user_id,
            tier=tier,
            expires_at=expires_at,
            scans_today=row[2] or 0,
            total_scans=row[3] or 0,
            payment_address=row[4],
            payment_tx_hash=row[5],
            created_at=datetime.fromisoformat(row[6])
        )
    
    def _create_subscription(self, user_id: int):
        """Create new free subscription"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO subscriptions (user_id, tier)
            VALUES (?, 'free')
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def _downgrade_to_free(self, user_id: int):
        """Downgrade expired subscription to free"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE subscriptions 
            SET tier = 'free', expires_at = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"User {user_id} downgraded to free tier (expired)")
    
    def can_scan(self, user_id: int) -> tuple[bool, str]:
        """Check if user can perform a scan"""
        sub = self.get_subscription(user_id)
        tier_config = self.TIERS[sub.tier]
        
        # Check daily limit
        daily_used = self._get_daily_scans(user_id)
        if daily_used >= tier_config['daily_scans']:
            if sub.tier == SubscriptionTier.FREE:
                return False, f"⚠️ Daily limit reached! Upgrade to Premium for 50 scans/day."
            else:
                return False, f"⚠️ Daily limit reached for your {sub.tier.value} plan."
        
        return True, f"✅ {tier_config['daily_scans'] - daily_used} scans remaining today"
    
    def _get_daily_scans(self, user_id: int) -> int:
        """Get number of scans used today"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT scan_count FROM scan_usage 
            WHERE user_id = ? AND scan_date = CURRENT_DATE
        ''', (user_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0
    
    def record_scan(self, user_id: int):
        """Record a scan usage"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Update or insert daily usage
        c.execute('''
            INSERT INTO scan_usage (user_id, scan_date, scan_count)
            VALUES (?, CURRENT_DATE, 1)
            ON CONFLICT(user_id, scan_date) DO UPDATE SET
            scan_count = scan_count + 1
        ''', (user_id,))
        
        # Update total scans
        c.execute('''
            UPDATE subscriptions 
            SET scans_today = scans_today + 1, 
                total_scans = total_scans + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_payment_options(self, tier: SubscriptionTier, duration: str = 'monthly') -> Dict[str, Any]:
        """Get payment options for a tier"""
        if tier == SubscriptionTier.FREE:
            return {'error': 'Free tier requires no payment'}
        
        config = self.TIERS[tier]
        price = config['price_monthly'] if duration == 'monthly' else config['price_yearly']
        months = 1 if duration == 'monthly' else 12
        
        options = {}
        for currency, address in self.PAYMENT_WALLETS.items():
            if address:
                options[currency] = {
                    'address': address,
                    'amount': price if currency in ['USDT_ETH', 'USDT_BSC', 'USDC_ETH'] else None,
                    'qr_data': f"{currency}:{address}?amount={price}" if currency.startswith('USDT') or currency.startswith('USDC') else f"{currency}:{address}"
                }
        
        return {
            'tier': tier.value,
            'duration': duration,
            'price_usd': price,
            'months': months,
            'payment_methods': options
        }
    
    def verify_payment(self, tx_hash: str, user_id: int, expected_amount: float, currency: str) -> bool:
        """Verify a crypto payment (placeholder - integrate with blockchain APIs)"""
        # TODO: Integrate with Etherscan/BscScan/Helius APIs
        # For now, manual verification via admin panel
        logger.info(f"Payment verification requested: {tx_hash} for user {user_id}")
        return False  # Require manual verification
    
    def upgrade_subscription(self, user_id: int, tier: SubscriptionTier, 
                            duration_months: int = 1, tx_hash: Optional[str] = None) -> bool:
        """Upgrade user subscription"""
        if tier == SubscriptionTier.FREE:
            return False
        
        expires = datetime.now() + timedelta(days=30 * duration_months)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE subscriptions 
            SET tier = ?, expires_at = ?, payment_tx_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (tier.value, expires.isoformat(), tx_hash, user_id))
        
        # Record payment
        config = self.TIERS[tier]
        price = config['price_monthly'] * duration_months if duration_months < 12 else config['price_yearly']
        
        c.execute('''
            INSERT INTO payments (user_id, amount, currency, tier, duration_months, tx_hash, status)
            VALUES (?, ?, 'USD', ?, ?, ?, 'completed')
        ''', (user_id, price, tier.value, duration_months, tx_hash or 'admin_upgrade'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"User {user_id} upgraded to {tier.value} until {expires}")
        return True
    
    def get_tier_benefits(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get benefits for a tier"""
        config = self.TIERS[tier]
        return {
            'name': tier.value.upper(),
            'daily_scans': config['daily_scans'] if config['daily_scans'] < 999999 else 'Unlimited',
            'wallet_tracks': config['max_wallet_tracks'] if config['max_wallet_tracks'] < 999999 else 'Unlimited',
            'alerts': config['max_alerts'] if config['max_alerts'] < 999999 else 'Unlimited',
            'api_access': config['api_access'],
            'priority_support': config['priority_support'],
            'custom_reports': config.get('custom_reports', False),
            'monthly_price': config['price_monthly'],
            'yearly_price': config['price_yearly']
        }
    
    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user subscription stats"""
        sub = self.get_subscription(user_id)
        tier_config = self.TIERS[sub.tier]
        daily_used = self._get_daily_scans(user_id)
        
        return {
            'tier': sub.tier.value,
            'expires_at': sub.expires_at.isoformat() if sub.expires_at else None,
            'daily_used': daily_used,
            'daily_limit': tier_config['daily_scans'] if tier_config['daily_scans'] < 999999 else 'Unlimited',
            'total_scans': sub.total_scans,
            'days_remaining': (sub.expires_at - datetime.now()).days if sub.expires_at else None
        }


# Singleton instance
_subscription_manager: Optional[RugMuncherSubscriptionManager] = None

def get_subscription_manager() -> RugMuncherSubscriptionManager:
    """Get or create subscription manager singleton"""
    global _subscription_manager
    if _subscription_manager is None:
        _subscription_manager = RugMuncherSubscriptionManager()
    return _subscription_manager


if __name__ == "__main__":
    # Test
    sm = get_subscription_manager()
    print("Subscription Manager initialized")
    print("Tiers:", list(sm.TIERS.keys()))
    print("Premium benefits:", sm.get_tier_benefits(SubscriptionTier.PREMIUM))
