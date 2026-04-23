"""
RMI API Marketplace - Cheap API Credits for Investigators
Buy discounted API credits for all major blockchain data providers
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
from solders.pubkey import Pubkey
from solders.signature import Signature


class APIProvider(Enum):
    """Supported API providers."""
    BIRDEYE = "birdeye"
    HELIUS = "helius"
    SHYFT = "shyft"
    QUICKNODE = "quicknode"
    ALCHEMY = "alchemy"
    MORALIS = "moralis"
    BITQUERY = "bitquery"
    SOLSCAN = "solscan"
    CRYPTOSLAM = "cryptoslam"
    DEFILLAMA = "defillama"
    COINGECKO = "coingecko"
    COINMARKETCAP = "coinmarketcap"


class PackageTier(Enum):
    """Package tiers."""
    STARTER = "starter"
    PRO = "pro"
    WHALE = "whale"
    ENTERPRISE = "enterprise"


@dataclass
class APIPackage:
    """API credit package definition."""
    provider: APIProvider
    tier: PackageTier
    credits: int
    base_price_usd: float
    discount_percent: float = 0
    bonus_credits: int = 0
    features: List[str] = field(default_factory=list)
    validity_days: int = 30
    rate_limit_per_min: int = 100
    
    @property
    def final_price(self) -> float:
        """Calculate final price after discount."""
        return round(self.base_price_usd * (1 - self.discount_percent / 100), 2)
    
    @property
    def effective_credits(self) -> int:
        """Total credits including bonus."""
        return self.credits + self.bonus_credits
    
    @property
    def price_per_1k_calls(self) -> float:
        """Price per 1000 API calls."""
        return round((self.final_price / self.effective_credits) * 1000, 4)


@dataclass
class UserAPICredits:
    """User's API credit balance."""
    user_id: str
    provider: APIProvider
    credits_remaining: int
    credits_used: int = 0
    package_tier: PackageTier = PackageTier.STARTER
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    @property
    def utilization_percent(self) -> float:
        """Calculate credit utilization percentage."""
        total = self.credits_remaining + self.credits_used
        if total == 0:
            return 0.0
        return round((self.credits_used / total) * 100, 2)
    
    @property
    def days_until_expiry(self) -> int:
        """Days until package expires."""
        if not self.expires_at:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)


@dataclass
class PendingPayment:
    """Pending payment record."""
    payment_id: str
    user_id: str
    package_key: str
    amount_usdc: float
    recipient_wallet: str
    created_at: datetime
    expires_at: datetime
    status: str = "pending"  # pending, paid, expired, failed


class APIMarketplace:
    """
    API Marketplace - Buy cheap API credits for investigations.
    
    Features:
    - Bulk pricing (up to 70% off retail)
    - Multi-provider packages
    - CRM holder discounts (additional 20%)
    - Credit pooling across providers
    - Usage analytics
    - Auto-renewal options
    """
    
    # Retail prices per 1000 calls (for comparison)
    RETAIL_PRICES = {
        APIProvider.BIRDEYE: 0.50,
        APIProvider.HELIUS: 0.30,
        APIProvider.SHYFT: 0.40,
        APIProvider.QUICKNODE: 0.25,
        APIProvider.ALCHEMY: 0.20,
        APIProvider.MORALIS: 0.35,
        APIProvider.BITQUERY: 1.00,
        APIProvider.SOLSCAN: 0.15,
        APIProvider.CRYPTOSLAM: 0.80,
        APIProvider.DEFILLAMA: 0.00,  # Free
        APIProvider.COINGECKO: 0.10,
        APIProvider.COINMARKETCAP: 0.25,
    }
    
    # Package definitions with bulk discounts
    PACKAGES: Dict[str, APIPackage] = {
        # === BIRDEYE PACKAGES ===
        "birdeye_starter": APIPackage(
            provider=APIProvider.BIRDEYE,
            tier=PackageTier.STARTER,
            credits=10000,
            base_price_usd=25.00,
            discount_percent=50,
            features=["Token Prices", "OHLCV Data", "Token List", "Search"],
            rate_limit_per_min=300
        ),
        "birdeye_pro": APIPackage(
            provider=APIProvider.BIRDEYE,
            tier=PackageTier.PRO,
            credits=50000,
            base_price_usd=100.00,
            discount_percent=60,
            bonus_credits=5000,
            features=["All Starter Features", "Wallet Portfolio", "Transaction History", "Gainers/Losers"],
            rate_limit_per_min=600
        ),
        "birdeye_whale": APIPackage(
            provider=APIProvider.BIRDEYE,
            tier=PackageTier.WHALE,
            credits=200000,
            base_price_usd=300.00,
            discount_percent=70,
            bonus_credits=30000,
            features=["All Pro Features", "New Pairs", "Trending Tokens", "Premium Support"],
            rate_limit_per_min=1200
        ),
        
        # === HELIUS PACKAGES ===
        "helius_starter": APIPackage(
            provider=APIProvider.HELIUS,
            tier=PackageTier.STARTER,
            credits=50000,
            base_price_usd=35.00,
            discount_percent=53,
            features=["RPC Calls", "NFT APIs", "Parsed Transactions", "Webhooks"],
            rate_limit_per_min=500
        ),
        "helius_pro": APIPackage(
            provider=APIProvider.HELIUS,
            tier=PackageTier.PRO,
            credits=250000,
            base_price_usd=140.00,
            discount_percent=60,
            bonus_credits=25000,
            features=["All Starter Features", "Enhanced APIs", "Priority Support"],
            rate_limit_per_min=1000
        ),
        "helius_whale": APIPackage(
            provider=APIProvider.HELIUS,
            tier=PackageTier.WHALE,
            credits=1000000,
            base_price_usd=450.00,
            discount_percent=68,
            bonus_credits=150000,
            features=["All Pro Features", "Dedicated Resources", "Custom SLA"],
            rate_limit_per_min=2000
        ),
        
        # === SHYFT PACKAGES ===
        "shyft_starter": APIPackage(
            provider=APIProvider.SHYFT,
            tier=PackageTier.STARTER,
            credits=20000,
            base_price_usd=20.00,
            discount_percent=50,
            features=["Wallet APIs", "NFT APIs", "Token APIs", "Transaction Parsing"],
            rate_limit_per_min=300
        ),
        "shyft_pro": APIPackage(
            provider=APIProvider.SHYFT,
            tier=PackageTier.PRO,
            credits=100000,
            base_price_usd=80.00,
            discount_percent=60,
            bonus_credits=10000,
            features=["All Starter Features", "Bulk Operations", "Historical Data"],
            rate_limit_per_min=600
        ),
        
        # === QUICKNODE PACKAGES ===
        "quicknode_starter": APIPackage(
            provider=APIProvider.QUICKNODE,
            tier=PackageTier.STARTER,
            credits=100000,
            base_price_usd=50.00,
            discount_percent=50,
            features=["Core RPC", "Token API", "NFT API", "Streams"],
            rate_limit_per_min=600
        ),
        "quicknode_pro": APIPackage(
            provider=APIProvider.QUICKNODE,
            tier=PackageTier.PRO,
            credits=500000,
            base_price_usd=200.00,
            discount_percent=60,
            bonus_credits=50000,
            features=["All Starter Features", "Add-ons", "Priority Support"],
            rate_limit_per_min=1200
        ),
        
        # === MULTI-PROVIDER BUNDLES ===
        "bundle_investigator": APIPackage(
            provider=APIProvider.BIRDEYE,  # Primary
            tier=PackageTier.PRO,
            credits=75000,  # Split across providers
            base_price_usd=99.00,
            discount_percent=55,
            features=[
                "Birdeye: 25K credits",
                "Helius: 25K credits", 
                "Shyft: 25K credits",
                "Perfect for investigations"
            ],
            rate_limit_per_min=400
        ),
        "bundle_forensic": APIPackage(
            provider=APIProvider.BIRDEYE,
            tier=PackageTier.WHALE,
            credits=400000,
            base_price_usd=299.00,
            discount_percent=62,
            bonus_credits=50000,
            features=[
                "Birdeye: 100K credits",
                "Helius: 100K credits",
                "Shyft: 100K credits",
                "Bitquery: 50K credits",
                "Full forensic toolkit"
            ],
            rate_limit_per_min=800
        ),
        "bundle_unlimited": APIPackage(
            provider=APIProvider.BIRDEYE,
            tier=PackageTier.ENTERPRISE,
            credits=2000000,
            base_price_usd=999.00,
            discount_percent=70,
            bonus_credits=500000,
            features=[
                "All providers included",
                "2M+ total credits",
                "Enterprise SLA",
                "Dedicated support",
                "Custom integrations"
            ],
            rate_limit_per_min=5000,
            validity_days=90
        ),
    }
    
    def __init__(self, solana_rpc: str = "https://api.mainnet-beta.solana.com"):
        """Initialize API marketplace."""
        self.solana_rpc = solana_rpc
        self.user_credits: Dict[str, List[UserAPICredits]] = {}
        self.pending_payments: Dict[str, PendingPayment] = {}
        self.usage_history: List[Dict] = []
        
        # Payment wallet (replace with actual)
        self.payment_wallet = "RugMunchTreasury111111111111111111111111111"
        
        # CRM holder verification
        self.crm_token_mint = "Eyi4JcxVkS9fWzubSu5yS7dHy4kAiFHJN6Rwu6y7r8U"
    
    async def get_all_packages(self, include_retail: bool = True) -> Dict:
        """
        Get all available packages with savings comparison.
        
        Args:
            include_retail: Include retail price comparison
            
        Returns:
            Package catalog with savings
        """
        catalog = {
            "single_provider": {},
            "bundles": {},
            "savings_examples": []
        }
        
        for key, package in self.PACKAGES.items():
            pkg_info = {
                "key": key,
                "provider": package.provider.value,
                "tier": package.tier.value,
                "credits": package.credits,
                "bonus_credits": package.bonus_credits,
                "effective_credits": package.effective_credits,
                "base_price": package.base_price_usd,
                "discount_percent": package.discount_percent,
                "final_price": package.final_price,
                "price_per_1k": package.price_per_1k_calls,
                "features": package.features,
                "rate_limit": package.rate_limit_per_min,
                "validity_days": package.validity_days
            }
            
            # Add retail comparison
            if include_retail:
                retail_price = self.RETAIL_PRICES.get(package.provider, 0)
                retail_cost = (package.effective_credits / 1000) * retail_price
                savings = retail_cost - package.final_price
                savings_percent = (savings / retail_cost * 100) if retail_cost > 0 else 0
                
                pkg_info["retail_comparison"] = {
                    "retail_price_per_1k": retail_price,
                    "retail_total_cost": round(retail_cost, 2),
                    "your_savings_usd": round(savings, 2),
                    "savings_percent": round(savings_percent, 1)
                }
            
            # Categorize
            if "bundle" in key:
                catalog["bundles"][key] = pkg_info
            else:
                provider = package.provider.value
                if provider not in catalog["single_provider"]:
                    catalog["single_provider"][provider] = []
                catalog["single_provider"][provider].append(pkg_info)
        
        # Add savings examples
        catalog["savings_examples"] = [
            {
                "scenario": "10K Birdeye calls",
                "retail_cost": "$5.00",
                "our_cost": "$2.50",
                "savings": "$2.50 (50%)"
            },
            {
                "scenario": "100K Helius calls",
                "retail_cost": "$30.00",
                "our_cost": "$12.60",
                "savings": "$17.40 (58%)"
            },
            {
                "scenario": "Full forensic bundle",
                "retail_cost": "$790.00",
                "our_cost": "$299.00",
                "savings": "$491.00 (62%)"
            }
        ]
        
        return catalog
    
    async def check_crm_holder_discount(self, wallet_address: str) -> Dict:
        """
        Check if wallet is CRM holder for additional discount.
        
        Args:
            wallet_address: User's Solana wallet
            
        Returns:
            Discount eligibility info
        """
        try:
            # Query token account for CRM
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [
                        wallet_address,
                        {"mint": self.crm_token_mint},
                        {"encoding": "jsonParsed"}
                    ]
                }
                
                async with session.post(
                    self.solana_rpc,
                    headers=headers,
                    json=payload
                ) as resp:
                    data = await resp.json()
                    
                    accounts = data.get("result", {}).get("value", [])
                    total_balance = 0
                    
                    for account in accounts:
                        parsed = account.get("account", {}).get("data", {}).get("parsed", {})
                        info = parsed.get("info", {})
                        balance = int(info.get("tokenAmount", {}).get("amount", 0))
                        decimals = info.get("tokenAmount", {}).get("decimals", 9)
                        total_balance += balance / (10 ** decimals)
                    
                    is_holder = total_balance > 0
                    
                    return {
                        "wallet": wallet_address,
                        "is_crm_holder": is_holder,
                        "crm_balance": total_balance,
                        "additional_discount": 20 if is_holder else 0,
                        "discount_tier": "VIP" if total_balance >= 1000000 else (
                            "Gold" if total_balance >= 100000 else (
                                "Silver" if total_balance >= 10000 else "Bronze"
                            )
                        ) if is_holder else "None"
                    }
                    
        except Exception as e:
            return {
                "wallet": wallet_address,
                "is_crm_holder": False,
                "error": str(e),
                "additional_discount": 0
            }
    
    async def calculate_price(
        self,
        package_key: str,
        wallet_address: str
    ) -> Dict:
        """
        Calculate final price including all discounts.
        
        Args:
            package_key: Package identifier
            wallet_address: User's wallet for CRM check
            
        Returns:
            Pricing breakdown
        """
        package = self.PACKAGES.get(package_key)
        if not package:
            return {"error": f"Package {package_key} not found"}
        
        # Get CRM discount
        crm_info = await self.check_crm_holder_discount(wallet_address)
        crm_discount = crm_info.get("additional_discount", 0)
        
        # Calculate stacked discounts
        base_discount = package.discount_percent
        final_discount = min(base_discount + crm_discount, 80)  # Cap at 80%
        
        base_price = package.base_price_usd
        discounted_price = base_price * (1 - final_discount / 100)
        
        # Round to 2 decimals
        final_price = round(discounted_price, 2)
        
        return {
            "package": package_key,
            "provider": package.provider.value,
            "base_price": base_price,
            "base_discount": base_discount,
            "crm_discount": crm_discount,
            "total_discount": final_discount,
            "final_price": final_price,
            "savings_vs_retail": self._calculate_retail_savings(package, final_price),
            "crm_holder_info": crm_info,
            "payment_wallet": self.payment_wallet,
            "currency": "USDC"
        }
    
    def _calculate_retail_savings(
        self,
        package: APIPackage,
        final_price: float
    ) -> Dict:
        """Calculate savings compared to retail pricing."""
        retail_price = self.RETAIL_PRICES.get(package.provider, 0)
        retail_cost = (package.effective_credits / 1000) * retail_price
        savings = retail_cost - final_price
        
        return {
            "retail_cost": round(retail_cost, 2),
            "your_price": final_price,
            "total_savings": round(savings, 2),
            "savings_percent": round((savings / retail_cost * 100), 1) if retail_cost > 0 else 0
        }
    
    async def create_payment(
        self,
        user_id: str,
        package_key: str,
        wallet_address: str
    ) -> Dict:
        """
        Create payment request for package purchase.
        
        Args:
            user_id: User identifier
            package_key: Package to purchase
            wallet_address: Payment wallet
            
        Returns:
            Payment instructions
        """
        package = self.PACKAGES.get(package_key)
        if not package:
            return {"error": "Package not found"}
        
        # Calculate price
        pricing = await self.calculate_price(package_key, wallet_address)
        if "error" in pricing:
            return pricing
        
        # Generate payment ID
        payment_id = hashlib.sha256(
            f"{user_id}:{package_key}:{time.time()}".encode()
        ).hexdigest()[:32]
        
        # Create pending payment
        payment = PendingPayment(
            payment_id=payment_id,
            user_id=user_id,
            package_key=package_key,
            amount_usdc=pricing["final_price"],
            recipient_wallet=self.payment_wallet,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        
        self.pending_payments[payment_id] = payment
        
        return {
            "payment_id": payment_id,
            "amount": pricing["final_price"],
            "currency": "USDC",
            "recipient": self.payment_wallet,
            "network": "Solana",
            "expires_at": payment.expires_at.isoformat(),
            "instructions": {
                "step1": "Send exact amount in USDC to the recipient address",
                "step2": "Copy the transaction signature",
                "step3": "Call /verify-payment with payment_id and tx_signature",
                "warning": "Send exact amount. Payments expire in 30 minutes."
            },
            "pricing": pricing
        }
    
    async def verify_payment(
        self,
        payment_id: str,
        tx_signature: str
    ) -> Dict:
        """
        Verify payment and activate package.
        
        Args:
            payment_id: Payment identifier
            tx_signature: Solana transaction signature
            
        Returns:
            Verification result
        """
        payment = self.pending_payments.get(payment_id)
        
        if not payment:
            return {"error": "Payment not found or expired"}
        
        if payment.status != "pending":
            return {"error": f"Payment already {payment.status}"}
        
        if datetime.utcnow() > payment.expires_at:
            payment.status = "expired"
            return {"error": "Payment expired. Please create a new payment."}
        
        try:
            # Verify transaction on-chain
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [tx_signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
                }
                
                async with session.post(
                    self.solana_rpc,
                    headers=headers,
                    json=payload
                ) as resp:
                    data = await resp.json()
                    
                    if "error" in data:
                        return {"error": f"Transaction verification failed: {data['error']}"}
                    
                    tx_data = data.get("result", {})
                    if not tx_data:
                        return {"error": "Transaction not found. Wait a moment and retry."}
                    
                    # Verify transaction details
                    meta = tx_data.get("meta", {})
                    err = meta.get("err")
                    
                    if err:
                        payment.status = "failed"
                        return {"error": f"Transaction failed: {err}"}
                    
                    # Parse transaction for USDC transfer
                    transaction = tx_data.get("transaction", {})
                    message = transaction.get("message", {})
                    
                    # Check for USDC transfer to our wallet
                    pre_balances = meta.get("preTokenBalances", [])
                    post_balances = meta.get("postTokenBalances", [])
                    
                    usdc_transfer_found = False
                    transfer_amount = 0
                    
                    # Look for USDC mint in token balances
                    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
                    
                    for pre in pre_balances:
                        post = next(
                            (p for p in post_balances if p.get("accountIndex") == pre.get("accountIndex")),
                            None
                        )
                        if post:
                            pre_mint = pre.get("mint")
                            post_mint = post.get("mint")
                            
                            if pre_mint == usdc_mint or post_mint == usdc_mint:
                                pre_amt = float(pre.get("uiTokenAmount", {}).get("uiAmount", 0))
                                post_amt = float(post.get("uiTokenAmount", {}).get("uiAmount", 0))
                                diff = abs(post_amt - pre_amt)
                                
                                if diff >= payment.amount_usdc * 0.99:  # Allow 1% tolerance
                                    usdc_transfer_found = True
                                    transfer_amount = diff
                    
                    if not usdc_transfer_found:
                        return {
                            "error": "USDC transfer not found in transaction",
                            "expected": payment.amount_usdc,
                            "details": "Ensure you sent USDC on Solana mainnet"
                        }
                    
                    # Payment verified - activate credits
                    payment.status = "paid"
                    
                    activation = await self._activate_credits(
                        user_id=payment.user_id,
                        package_key=payment.package_key
                    )
                    
                    return {
                        "status": "success",
                        "payment_id": payment_id,
                        "transaction": tx_signature,
                        "amount_paid": round(transfer_amount, 2),
                        "activation": activation
                    }
                    
        except Exception as e:
            return {"error": f"Verification error: {str(e)}"}
    
    async def _activate_credits(
        self,
        user_id: str,
        package_key: str
    ) -> Dict:
        """Activate API credits for user."""
        package = self.PACKAGES.get(package_key)
        if not package:
            return {"error": "Package not found"}
        
        # Create credit record
        credits = UserAPICredits(
            user_id=user_id,
            provider=package.provider,
            credits_remaining=package.effective_credits,
            credits_used=0,
            package_tier=package.tier,
            activated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=package.validity_days),
            is_active=True
        )
        
        # Store in user's credits
        if user_id not in self.user_credits:
            self.user_credits[user_id] = []
        self.user_credits[user_id].append(credits)
        
        return {
            "status": "activated",
            "provider": package.provider.value,
            "credits_added": package.effective_credits,
            "expires_at": credits.expires_at.isoformat(),
            "rate_limit": package.rate_limit_per_min
        }
    
    async def get_user_credits(self, user_id: str) -> Dict:
        """
        Get user's API credit balances.
        
        Args:
            user_id: User identifier
            
        Returns:
            Credit summary
        """
        user_packages = self.user_credits.get(user_id, [])
        
        if not user_packages:
            return {
                "user_id": user_id,
                "has_credits": False,
                "message": "No active API packages. Visit /marketplace to purchase."
            }
        
        # Group by provider
        by_provider = {}
        total_remaining = 0
        total_used = 0
        
        for pkg in user_packages:
            if not pkg.is_active:
                continue
                
            provider = pkg.provider.value
            if provider not in by_provider:
                by_provider[provider] = []
            
            by_provider[provider].append({
                "credits_remaining": pkg.credits_remaining,
                "credits_used": pkg.credits_used,
                "utilization": f"{pkg.utilization_percent}%",
                "tier": pkg.package_tier.value,
                "expires_in_days": pkg.days_until_expiry,
                "activated_at": pkg.activated_at.isoformat() if pkg.activated_at else None
            })
            
            total_remaining += pkg.credits_remaining
            total_used += pkg.credits_used
        
        return {
            "user_id": user_id,
            "has_credits": True,
            "total_credits_remaining": total_remaining,
            "total_credits_used": total_used,
            "overall_utilization": f"{(total_used / (total_remaining + total_used) * 100):.1f}%" if (total_remaining + total_used) > 0 else "0%",
            "by_provider": by_provider,
            "active_packages": len([p for p in user_packages if p.is_active])
        }
    
    async def use_credits(
        self,
        user_id: str,
        provider: APIProvider,
        amount: int
    ) -> Dict:
        """
        Deduct credits from user's balance.
        
        Args:
            user_id: User identifier
            provider: API provider
            amount: Credits to deduct
            
        Returns:
            Deduction result
        """
        user_packages = self.user_credits.get(user_id, [])
        
        # Find active package for provider
        for pkg in user_packages:
            if pkg.provider == provider and pkg.is_active and pkg.credits_remaining >= amount:
                pkg.credits_remaining -= amount
                pkg.credits_used += amount
                
                # Log usage
                self.usage_history.append({
                    "user_id": user_id,
                    "provider": provider.value,
                    "amount": amount,
                    "timestamp": datetime.utcnow().isoformat(),
                    "remaining": pkg.credits_remaining
                })
                
                return {
                    "success": True,
                    "provider": provider.value,
                    "deducted": amount,
                    "remaining": pkg.credits_remaining,
                    "package_tier": pkg.package_tier.value
                }
        
        # Check if any package has credits
        total_available = sum(
            p.credits_remaining for p in user_packages
            if p.provider == provider and p.is_active
        )
        
        return {
            "success": False,
            "error": "Insufficient credits",
            "provider": provider.value,
            "requested": amount,
            "available": total_available,
            "message": f"Purchase more {provider.value} credits at /marketplace"
        }
    
    async def get_usage_analytics(self, user_id: str, days: int = 30) -> Dict:
        """
        Get user's API usage analytics.
        
        Args:
            user_id: User identifier
            days: Lookback period
            
        Returns:
            Usage analytics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        user_usage = [
            u for u in self.usage_history
            if u.get("user_id") == user_id
            and datetime.fromisoformat(u.get("timestamp", "")) >= cutoff
        ]
        
        if not user_usage:
            return {
                "user_id": user_id,
                "period_days": days,
                "total_calls": 0,
                "message": "No usage data yet"
            }
        
        # Aggregate by provider
        by_provider = {}
        daily_usage = {}
        
        for usage in user_usage:
            provider = usage.get("provider")
            amount = usage.get("amount", 0)
            date = usage.get("timestamp", "")[:10]  # YYYY-MM-DD
            
            by_provider[provider] = by_provider.get(provider, 0) + amount
            daily_usage[date] = daily_usage.get(date, 0) + amount
        
        total_calls = sum(by_provider.values())
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_calls": total_calls,
            "avg_daily": round(total_calls / days, 1),
            "by_provider": by_provider,
            "daily_usage": daily_usage,
            "most_used": max(by_provider.items(), key=lambda x: x[1]) if by_provider else None
        }
    
    async def get_marketplace_stats(self) -> Dict:
        """Get marketplace statistics."""
        total_packages = len(self.PACKAGES)
        
        # Calculate average savings
        savings = []
        for pkg in self.PACKAGES.values():
            retail = self.RETAIL_PRICES.get(pkg.provider, 0)
            retail_cost = (pkg.effective_credits / 1000) * retail
            savings.append(retail_cost - pkg.final_price)
        
        avg_savings = sum(savings) / len(savings) if savings else 0
        
        return {
            "total_packages": total_packages,
            "providers": len(set(p.provider for p in self.PACKAGES.values())),
            "avg_discount": f"{sum(p.discount_percent for p in self.PACKAGES.values()) / total_packages:.0f}%",
            "avg_savings_per_package": f"${avg_savings:.2f}",
            "most_popular": [
                "bundle_forensic",
                "birdeye_pro",
                "helius_starter"
            ],
            "new_arrivals": [
                "quicknode_pro",
                "bundle_unlimited"
            ]
        }


# === FASTAPI ENDPOINTS ===

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/marketplace", tags=["API Marketplace"])

# Global marketplace instance
marketplace = APIMarketplace()


class PaymentRequest(BaseModel):
    user_id: str
    package_key: str
    wallet_address: str


class PaymentVerification(BaseModel):
    payment_id: str
    tx_signature: str


class CreditUsage(BaseModel):
    user_id: str
    provider: str
    amount: int


@router.get("/packages")
async def get_packages(include_retail: bool = True):
    """Get all available API packages."""
    return await marketplace.get_all_packages(include_retail)


@router.get("/packages/{package_key}/price")
async def get_package_price(package_key: str, wallet_address: str):
    """Get price for a package including discounts."""
    result = await marketplace.calculate_price(package_key, wallet_address)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/payment/create")
async def create_payment(request: PaymentRequest):
    """Create a payment for package purchase."""
    result = await marketplace.create_payment(
        request.user_id,
        request.package_key,
        request.wallet_address
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/payment/verify")
async def verify_payment(verification: PaymentVerification):
    """Verify payment and activate credits."""
    result = await marketplace.verify_payment(
        verification.payment_id,
        verification.tx_signature
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/credits/{user_id}")
async def get_user_credits(user_id: str):
    """Get user's API credit balance."""
    return await marketplace.get_user_credits(user_id)


@router.post("/credits/use")
async def use_credits(usage: CreditUsage):
    """Deduct credits from user balance."""
    try:
        provider = APIProvider(usage.provider)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    result = await marketplace.use_credits(usage.user_id, provider, usage.amount)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/usage/{user_id}")
async def get_usage_analytics(user_id: str, days: int = 30):
    """Get user's API usage analytics."""
    return await marketplace.get_usage_analytics(user_id, days)


@router.get("/stats")
async def get_marketplace_stats():
    """Get marketplace statistics."""
    return await marketplace.get_marketplace_stats()


@router.get("/crm-check/{wallet_address}")
async def check_crm_holder(wallet_address: str):
    """Check CRM holder status for discounts."""
    return await marketplace.check_crm_holder_discount(wallet_address)
