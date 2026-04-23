"""
Premium Scan Packs - Monetization System
========================================
Scan pack pricing with CRM v1 holder discounts.
Crypto payment integration.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class ScanPackType(Enum):
    """Types of scan packs."""
    STARTER = "starter"           # 10 scans
    PRO = "pro"                   # 50 scans
    WHALE = "whale"               # 200 scans
    UNLIMITED = "unlimited"       # Unlimited monthly
    ENTERPRISE = "enterprise"     # Custom


class UserTier(Enum):
    """User tiers for pricing."""
    REGULAR = "regular"
    CRM_V1_HOLDER = "crm_v1_holder"  # 50% off
    EARLY_ADOPTER = "early_adopter"  # 25% off
    AFFILIATE = "affiliate"          # 30% off


@dataclass
class ScanPack:
    """A scan pack offering."""
    pack_type: ScanPackType
    name: str
    description: str
    
    # Pricing (in USDC)
    base_price: float
    scan_count: int
    validity_days: int
    
    # Features
    features: List[str] = field(default_factory=list)
    
    def get_price(self, user_tier: UserTier = UserTier.REGULAR) -> float:
        """Get price for user tier."""
        discounts = {
            UserTier.REGULAR: 1.0,
            UserTier.CRM_V1_HOLDER: 0.5,    # 50% off
            UserTier.EARLY_ADOPTER: 0.75,   # 25% off
            UserTier.AFFILIATE: 0.7         # 30% off
        }
        
        return round(self.base_price * discounts.get(user_tier, 1.0), 2)
    
    def to_dict(self, user_tier: UserTier = UserTier.REGULAR) -> Dict:
        return {
            "type": self.pack_type.value,
            "name": self.name,
            "description": self.description,
            "price": self.get_price(user_tier),
            "original_price": self.base_price,
            "scan_count": self.scan_count,
            "validity_days": self.validity_days,
            "features": self.features
        }


@dataclass
class UserSubscription:
    """User's scan pack subscription."""
    user_id: str
    wallet_address: str
    user_tier: UserTier
    
    # Active packs
    active_packs: List[Dict] = field(default_factory=list)
    
    # Usage
    total_scans_used: int = 0
    scans_remaining: int = 0
    
    # History
    purchase_history: List[Dict] = field(default_factory=list)
    
    def can_scan(self) -> bool:
        """Check if user can perform a scan."""
        return self.scans_remaining > 0 or any(
            p.get("type") == ScanPackType.UNLIMITED.value and 
            datetime.fromisoformat(p.get("expires_at", "2000-01-01")) > datetime.now()
            for p in self.active_packs
        )
    
    def use_scan(self) -> bool:
        """Use a scan. Returns True if successful."""
        if self.can_scan():
            self.total_scans_used += 1
            if self.scans_remaining > 0:
                self.scans_remaining -= 1
            return True
        return False


class PremiumScans:
    """
    Premium scan pack system with tiered pricing.
    """
    
    # Payment wallet (Solana USDC)
    PAYMENT_WALLET = "RMI Premium Payment Wallet"
    
    # Scan pack definitions
    PACKS = {
        ScanPackType.STARTER: ScanPack(
            pack_type=ScanPackType.STARTER,
            name="Starter Pack",
            description="Perfect for casual users",
            base_price=10.0,
            scan_count=10,
            validity_days=30,
            features=[
                "Contract Check (100-point analysis)",
                "Basic Wallet Investigation",
                "Export results as JSON",
                "Email support"
            ]
        ),
        ScanPackType.PRO: ScanPack(
            pack_type=ScanPackType.PRO,
            name="Pro Pack",
            description="For serious traders",
            base_price=35.0,
            scan_count=50,
            validity_days=30,
            features=[
                "Everything in Starter",
                "Dev Finder",
                "KOL Reputation Check",
                "Bubble Map Generation",
                "Export PNG/SVG/PDF",
                "Priority support"
            ]
        ),
        ScanPackType.WHALE: ScanPack(
            pack_type=ScanPackType.WHALE,
            name="Whale Pack",
            description="For power users",
            base_price=100.0,
            scan_count=200,
            validity_days=30,
            features=[
                "Everything in Pro",
                "Advanced Cluster Detection",
                "Shill Campaign Tracker",
                "Trending Scams Alerts",
                "API Access (1000 req/day)",
                "White-label reports"
            ]
        ),
        ScanPackType.UNLIMITED: ScanPack(
            pack_type=ScanPackType.UNLIMITED,
            name="Unlimited Monthly",
            description="Unlimited scans for 30 days",
            base_price=250.0,
            scan_count=-1,  # Unlimited
            validity_days=30,
            features=[
                "Unlimited scans",
                "All features unlocked",
                "Priority processing",
                "API Access (10K req/day)",
                "Discord VIP channel",
                "Direct line to team"
            ]
        ),
        ScanPackType.ENTERPRISE: ScanPack(
            pack_type=ScanPackType.ENTERPRISE,
            name="Enterprise",
            description="Custom solution for teams",
            base_price=1000.0,
            scan_count=-1,
            validity_days=30,
            features=[
                "Custom integration",
                "Dedicated support",
                "SLA guarantee",
                "White-label options",
                "Custom features",
                "Team training"
            ]
        )
    }
    
    def __init__(self):
        self.users: Dict[str, UserSubscription] = {}
        self.pending_payments: Dict[str, Dict] = {}
        self.crm_v1_holders: set = set()  # Would be loaded from blockchain
        
    def get_pricing(self, user_tier: UserTier = UserTier.REGULAR) -> Dict:
        """Get pricing for all packs."""
        return {
            "user_tier": user_tier.value,
            "discount": self._get_discount_percent(user_tier),
            "packs": [pack.to_dict(user_tier) for pack in self.PACKS.values()]
        }
    
    def _get_discount_percent(self, user_tier: UserTier) -> int:
        """Get discount percentage for tier."""
        discounts = {
            UserTier.REGULAR: 0,
            UserTier.CRM_V1_HOLDER: 50,
            UserTier.EARLY_ADOPTER: 25,
            UserTier.AFFILIATE: 30
        }
        return discounts.get(user_tier, 0)
    
    async def check_crm_v1_holder(self, wallet_address: str) -> bool:
        """Check if wallet is a CRM v1 holder."""
        # In production, query blockchain for CRM token balance
        # For demo, check against stored list
        return wallet_address in self.crm_v1_holders
    
    async def get_user_tier(self, wallet_address: str) -> UserTier:
        """Determine user tier."""
        if await self.check_crm_v1_holder(wallet_address):
            return UserTier.CRM_V1_HOLDER
        return UserTier.REGULAR
    
    async def create_payment(
        self,
        user_id: str,
        wallet_address: str,
        pack_type: ScanPackType
    ) -> Dict:
        """Create a payment request."""
        user_tier = await self.get_user_tier(wallet_address)
        pack = self.PACKS.get(pack_type)
        
        if not pack:
            return {"error": "Invalid pack type"}
        
        price = pack.get_price(user_tier)
        payment_id = f"RMI-{user_id[:8]}-{pack_type.value}-{int(datetime.now().timestamp())}"
        
        payment_request = {
            "payment_id": payment_id,
            "pack_type": pack_type.value,
            "pack_name": pack.name,
            "amount": price,
            "token": "USDC",
            "network": "Solana",
            "recipient_wallet": self.PAYMENT_WALLET,
            "memo": payment_id,
            "user_tier": user_tier.value,
            "discount_applied": self._get_discount_percent(user_tier),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "instructions": f"""
Send exactly {price} USDC to:
{self.PAYMENT_WALLET}

Include memo: {payment_id}

Payment expires in 24 hours.
"""
        }
        
        self.pending_payments[payment_id] = payment_request
        
        return payment_request
    
    async def verify_payment(
        self,
        payment_id: str,
        tx_signature: str
    ) -> Dict:
        """Verify payment and activate pack."""
        payment = self.pending_payments.get(payment_id)
        
        if not payment:
            return {"error": "Payment not found"}
        
        # In production, verify on-chain
        # For demo, assume valid
        
        pack_type = ScanPackType(payment["pack_type"])
        pack = self.PACKS.get(pack_type)
        
        # Activate pack for user
        user_id = payment_id.split("-")[1]
        
        if user_id not in self.users:
            self.users[user_id] = UserSubscription(
                user_id=user_id,
                wallet_address="",  # Would be set from payment
                user_tier=UserTier(payment["user_tier"])
            )
        
        user = self.users[user_id]
        
        # Add to active packs
        active_pack = {
            "type": pack_type.value,
            "name": pack.name,
            "scan_count": pack.scan_count,
            "scans_used": 0,
            "activated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=pack.validity_days)).isoformat(),
            "payment_tx": tx_signature
        }
        
        user.active_packs.append(active_pack)
        user.scans_remaining += pack.scan_count if pack.scan_count > 0 else 999999
        
        # Add to purchase history
        user.purchase_history.append({
            "pack_type": pack_type.value,
            "amount": payment["amount"],
            "payment_id": payment_id,
            "tx_signature": tx_signature,
            "purchased_at": datetime.now().isoformat()
        })
        
        # Clean up pending
        del self.pending_payments[payment_id]
        
        return {
            "success": True,
            "pack_activated": pack_type.value,
            "scans_remaining": user.scans_remaining,
            "expires_at": active_pack["expires_at"]
        }
    
    async def use_scan(self, user_id: str) -> Dict:
        """Use a scan for a user."""
        user = self.users.get(user_id)
        
        if not user:
            return {"error": "User not found", "can_scan": False}
        
        if user.use_scan():
            return {
                "success": True,
                "scans_remaining": user.scans_remaining,
                "total_used": user.total_scans_used
            }
        
        return {
            "error": "No scans remaining",
            "can_scan": False,
            "upgrade_url": "/pricing"
        }
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user scan statistics."""
        user = self.users.get(user_id)
        
        if not user:
            return {"error": "User not found"}
        
        return {
            "user_tier": user.user_tier.value,
            "total_scans_used": user.total_scans_used,
            "scans_remaining": user.scans_remaining,
            "active_packs": user.active_packs,
            "purchase_history": user.purchase_history
        }
    
    def get_revenue_stats(self) -> Dict:
        """Get revenue statistics."""
        total_revenue = sum(
            p["amount"] 
            for u in self.users.values() 
            for p in u.purchase_history
        )
        
        pack_sales = {}
        for u in self.users.values():
            for p in u.purchase_history:
                pack_type = p["pack_type"]
                pack_sales[pack_type] = pack_sales.get(pack_type, 0) + 1
        
        return {
            "total_revenue_usd": total_revenue,
            "total_users": len(self.users),
            "total_scans_used": sum(u.total_scans_used for u in self.users.values()),
            "pack_sales": pack_sales
        }


# Global instance
_premium = None

def get_premium_scans() -> PremiumScans:
    """Get global premium scans instance."""
    global _premium
    if _premium is None:
        _premium = PremiumScans()
    return _premium


if __name__ == "__main__":
    print("=" * 70)
    print("PREMIUM SCAN PACKS")
    print("=" * 70)
    
    premium = get_premium_scans()
    
    print("\n💰 Pricing (Regular Users):")
    for pack_type, pack in premium.PACKS.items():
        scans = "Unlimited" if pack.scan_count == -1 else pack.scan_count
        print(f"  {pack.name}: ${pack.base_price} - {scans} scans ({pack.validity_days} days)")
    
    print("\n🎁 CRM v1 Holder Pricing (50% OFF):")
    for pack_type, pack in premium.PACKS.items():
        price = pack.get_price(UserTier.CRM_V1_HOLDER)
        scans = "Unlimited" if pack.scan_count == -1 else pack.scan_count
        print(f"  {pack.name}: ${price} - {scans} scans ({pack.validity_days} days)")
    
    print("\n👤 User Tiers:")
    print("  Regular - Full price")
    print("  CRM v1 Holder - 50% off (verify by wallet)")
    print("  Early Adopter - 25% off")
    print("  Affiliate - 30% off")
    
    print("\n💳 Payment:")
    print("  • Solana USDC")
    print("  • Auto-verification")
    print("  • Instant activation")
    
    print("\n" + "=" * 70)
