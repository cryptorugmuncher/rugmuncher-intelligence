"""
Wallet Protection Tools - Protect Users from Scams
==================================================
Tools to protect users when interacting with tokens:
- Transaction warnings
- Blocklist checking
- Simulation before signing
- Risk alerts
"""

import json
import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProtectionAction(Enum):
    """Action to take when risk detected."""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    SIMULATE = "simulate"


class RiskCategory(Enum):
    """Category of risk."""
    KNOWN_SCAM = "known_scam"
    SUSPICIOUS = "suspicious"
    NEW_TOKEN = "new_token"
    HIGH_RISK = "high_risk"
    LOW_LIQUIDITY = "low_liquidity"
    UNVERIFIED = "unverified"


@dataclass
class ProtectionRule:
    """A protection rule."""
    name: str
    category: RiskCategory
    condition: str
    action: ProtectionAction
    message: str
    enabled: bool = True


@dataclass
class TransactionCheck:
    """Result of checking a transaction."""
    token_address: str
    token_symbol: str
    
    # Risk assessment
    risk_level: str  # safe, low, medium, high, critical
    risk_score: int  # 0-100
    risk_categories: List[RiskCategory] = field(default_factory=list)
    
    # Action
    action: ProtectionAction = ProtectionAction.ALLOW
    message: str = ""
    
    # Details
    red_flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Protection
    blocked: bool = False
    bypass_available: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "token": {
                "address": self.token_address,
                "symbol": self.token_symbol
            },
            "risk": {
                "level": self.risk_level,
                "score": self.risk_score,
                "categories": [c.value for c in self.risk_categories]
            },
            "action": self.action.value,
            "message": self.message,
            "red_flags": self.red_flags,
            "warnings": self.warnings,
            "blocked": self.blocked,
            "bypass_available": self.bypass_available
        }


@dataclass
class ProtectedWallet:
    """A wallet under protection."""
    address: str
    owner_email: Optional[str] = None
    
    # Settings
    protection_level: str = "standard"  # minimal, standard, maximum
    auto_block_known_scams: bool = True
    warn_on_suspicious: bool = True
    require_simulation: bool = False
    
    # Stats
    transactions_checked: int = 0
    warnings_shown: int = 0
    transactions_blocked: int = 0
    estimated_savings: float = 0.0
    
    # History
    checked_tokens: List[str] = field(default_factory=list)
    blocked_tokens: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "protection_level": self.protection_level,
            "settings": {
                "auto_block": self.auto_block_known_scams,
                "warn_suspicious": self.warn_on_suspicious,
                "require_simulation": self.require_simulation
            },
            "stats": {
                "checked": self.transactions_checked,
                "warnings": self.warnings_shown,
                "blocked": self.transactions_blocked,
                "estimated_savings": self.estimated_savings
            }
        }


class WalletProtection:
    """
    Protects users from scam tokens and suspicious transactions.
    """
    
    # Default protection rules
    DEFAULT_RULES = [
        ProtectionRule(
            name="Block Known Scams",
            category=RiskCategory.KNOWN_SCAM,
            condition="token_in_blocklist",
            action=ProtectionAction.BLOCK,
            message="🚫 This token is a KNOWN SCAM. Transaction blocked for your protection.",
            enabled=True
        ),
        ProtectionRule(
            name="Warn Suspicious",
            category=RiskCategory.SUSPICIOUS,
            condition="risk_score > 70",
            action=ProtectionAction.WARN,
            message="⚠️ Suspicious token detected. Review before proceeding.",
            enabled=True
        ),
        ProtectionRule(
            name="New Token Warning",
            category=RiskCategory.NEW_TOKEN,
            condition="token_age < 24h",
            action=ProtectionAction.WARN,
            message="⚡ This token is less than 24 hours old. High risk.",
            enabled=True
        ),
        ProtectionRule(
            name="Low Liquidity Warning",
            category=RiskCategory.LOW_LIQUIDITY,
            condition="liquidity < $10000",
            action=ProtectionAction.WARN,
            message="⚠️ Very low liquidity. You may not be able to sell.",
            enabled=True
        ),
        ProtectionRule(
            name="Simulate High Value",
            category=RiskCategory.HIGH_RISK,
            condition="transaction_value > $1000 AND risk_score > 50",
            action=ProtectionAction.SIMULATE,
            message="💰 High value transaction. Simulating before signing...",
            enabled=True
        )
    ]
    
    def __init__(self):
        self.blocklist: Set[str] = set()  # Known scam tokens
        self.suspicious_list: Set[str] = set()  # Suspicious tokens
        self.protected_wallets: Dict[str, ProtectedWallet] = {}  # wallet -> protection
        self.rules: List[ProtectionRule] = self.DEFAULT_RULES.copy()
        self.check_history: List[Dict] = []
        
    async def protect_wallet(self, wallet_address: str, settings: Dict = None) -> ProtectedWallet:
        """Enable protection for a wallet."""
        if wallet_address in self.protected_wallets:
            wallet = self.protected_wallets[wallet_address]
            if settings:
                wallet.protection_level = settings.get("level", wallet.protection_level)
                wallet.auto_block_known_scams = settings.get("auto_block", wallet.auto_block_known_scams)
                wallet.warn_on_suspicious = settings.get("warn_suspicious", wallet.warn_on_suspicious)
            return wallet
        
        wallet = ProtectedWallet(
            address=wallet_address,
            protection_level=settings.get("level", "standard") if settings else "standard",
            auto_block_known_scams=settings.get("auto_block", True) if settings else True,
            warn_on_suspicious=settings.get("warn_suspicious", True) if settings else True
        )
        
        self.protected_wallets[wallet_address] = wallet
        return wallet
    
    async def check_transaction(
        self,
        wallet_address: str,
        token_address: str,
        transaction_value: float = 0,
        transaction_type: str = "buy"
    ) -> TransactionCheck:
        """
        Check a transaction before it's signed.
        
        Args:
            wallet_address: User's wallet
            token_address: Token being transacted
            transaction_value: Value in USD
            transaction_type: buy, sell, approve, etc.
            
        Returns:
            TransactionCheck with risk assessment and action
        """
        # Get wallet protection settings
        wallet = self.protected_wallets.get(wallet_address)
        if not wallet:
            # No protection enabled, allow with basic check
            wallet = await self.protect_wallet(wallet_address)
        
        # Increment stats
        wallet.transactions_checked += 1
        
        # Create check result
        check = TransactionCheck(
            token_address=token_address,
            token_symbol="UNKNOWN"
        )
        
        # Check blocklist
        if token_address in self.blocklist:
            check.risk_level = "critical"
            check.risk_score = 100
            check.risk_categories.append(RiskCategory.KNOWN_SCAM)
            check.action = ProtectionAction.BLOCK
            check.message = "🚫 This token is a KNOWN SCAM. Transaction blocked."
            check.red_flags.append("Token is on the known scam blocklist")
            check.blocked = True
            
            wallet.transactions_blocked += 1
            wallet.blocked_tokens.append(token_address)
            
            return check
        
        # Get token analysis
        token_analysis = await self._analyze_token(token_address)
        check.token_symbol = token_analysis.get("symbol", "UNKNOWN")
        check.risk_score = token_analysis.get("risk_score", 50)
        check.risk_level = self._score_to_level(check.risk_score)
        
        # Apply rules
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_rule(rule, token_analysis, transaction_value):
                check.risk_categories.append(rule.category)
                
                if rule.action == ProtectionAction.BLOCK and wallet.auto_block_known_scams:
                    check.action = ProtectionAction.BLOCK
                    check.message = rule.message
                    check.blocked = True
                    wallet.transactions_blocked += 1
                    
                elif rule.action == ProtectionAction.WARN and wallet.warn_on_suspicious:
                    check.action = ProtectionAction.WARN
                    check.message = rule.message
                    wallet.warnings_shown += 1
                    
                elif rule.action == ProtectionAction.SIMULATE and wallet.require_simulation:
                    check.action = ProtectionAction.SIMULATE
                    check.message = rule.message
        
        # Collect red flags and warnings
        check.red_flags = token_analysis.get("red_flags", [])
        check.warnings = token_analysis.get("warnings", [])
        
        # Allow bypass for warnings (not blocks)
        if check.action == ProtectionAction.WARN:
            check.bypass_available = True
        
        # Log check
        self.check_history.append({
            "timestamp": datetime.now().isoformat(),
            "wallet": wallet_address,
            "token": token_address,
            "action": check.action.value,
            "risk_score": check.risk_score
        })
        
        return check
    
    async def _analyze_token(self, token_address: str) -> Dict:
        """Analyze a token for risks."""
        # In production, this would call the contract checker
        # For now, return sample data
        
        return {
            "symbol": "SAMPLE",
            "risk_score": 65,
            "liquidity": 5000,
            "token_age_hours": 12,
            "red_flags": [
                "Liquidity not locked",
                "Deployer wallet is new"
            ],
            "warnings": [
                "Low trading volume",
                "Few holders"
            ]
        }
    
    def _evaluate_rule(self, rule: ProtectionRule, token_data: Dict, transaction_value: float) -> bool:
        """Evaluate if a rule applies."""
        condition = rule.condition
        
        if condition == "token_in_blocklist":
            return False  # Already checked
        
        if condition.startswith("risk_score"):
            threshold = int(condition.split(">")[1].strip())
            return token_data.get("risk_score", 0) > threshold
        
        if condition.startswith("token_age"):
            hours = int(condition.split("<")[1].strip().replace("h", ""))
            age_hours = token_data.get("token_age_hours", 999)
            return age_hours < hours
        
        if condition.startswith("liquidity"):
            threshold = int(condition.split("<")[1].strip().replace("$", ""))
            return token_data.get("liquidity", 0) < threshold
        
        if "AND" in condition:
            parts = condition.split("AND")
            return all(self._evaluate_simple_condition(p.strip(), token_data, transaction_value) for p in parts)
        
        return False
    
    def _evaluate_simple_condition(self, condition: str, token_data: Dict, transaction_value: float) -> bool:
        """Evaluate a simple condition."""
        if condition.startswith("transaction_value"):
            threshold = float(condition.split(">")[1].strip().replace("$", "").replace(",", ""))
            return transaction_value > threshold
        
        if condition.startswith("risk_score"):
            threshold = int(condition.split(">")[1].strip())
            return token_data.get("risk_score", 0) > threshold
        
        return False
    
    def _score_to_level(self, score: int) -> str:
        """Convert risk score to level."""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        elif score >= 20:
            return "low"
        else:
            return "safe"
    
    async def add_to_blocklist(self, token_address: str, reason: str):
        """Add a token to the blocklist."""
        self.blocklist.add(token_address)
        
        # Also update all protected wallets
        for wallet in self.protected_wallets.values():
            if token_address in wallet.checked_tokens:
                wallet.blocked_tokens.append(token_address)
    
    async def remove_from_blocklist(self, token_address: str):
        """Remove a token from the blocklist."""
        self.blocklist.discard(token_address)
    
    def is_blocked(self, token_address: str) -> bool:
        """Check if a token is blocked."""
        return token_address in self.blocklist
    
    async def simulate_transaction(
        self,
        wallet_address: str,
        token_address: str,
        amount: float
    ) -> Dict:
        """
        Simulate a transaction to show expected outcomes.
        
        Returns:
            Dict with simulation results
        """
        # In production, this would use a simulation API
        # For now, return estimated data
        
        token_analysis = await self._analyze_token(token_address)
        
        return {
            "simulation_id": f"sim_{int(datetime.now().timestamp())}",
            "token": token_address,
            "amount": amount,
            "estimated_output": amount * 0.95,  # 5% slippage
            "price_impact": "5%",
            "fees": amount * 0.01,
            "warnings": [
                "High slippage due to low liquidity",
                "Price may change before confirmation"
            ],
            "risk_factors": token_analysis.get("red_flags", [])
        }
    
    def get_protection_stats(self, wallet_address: str = None) -> Dict:
        """Get protection statistics."""
        if wallet_address:
            wallet = self.protected_wallets.get(wallet_address)
            if wallet:
                return wallet.to_dict()
            return {"error": "Wallet not found"}
        
        # Global stats
        total_checked = sum(w.transactions_checked for w in self.protected_wallets.values())
        total_blocked = sum(w.transactions_blocked for w in self.protected_wallets.values())
        total_warnings = sum(w.warnings_shown for w in self.protected_wallets.values())
        
        return {
            "protected_wallets": len(self.protected_wallets),
            "blocklist_size": len(self.blocklist),
            "suspicious_list_size": len(self.suspicious_list),
            "total_checked": total_checked,
            "total_blocked": total_blocked,
            "total_warnings": total_warnings,
            "block_rate": (total_blocked / total_checked * 100) if total_checked > 0 else 0
        }
    
    def get_recent_blocks(self, limit: int = 10) -> List[Dict]:
        """Get recent blocked transactions."""
        blocks = [h for h in self.check_history if h["action"] == "block"]
        return sorted(blocks, key=lambda x: x["timestamp"], reverse=True)[:limit]


# Global instance
_protection = None

def get_wallet_protection() -> WalletProtection:
    """Get global wallet protection instance."""
    global _protection
    if _protection is None:
        _protection = WalletProtection()
    return _protection


if __name__ == "__main__":
    print("=" * 70)
    print("WALLET PROTECTION TOOLS")
    print("=" * 70)
    
    protection = get_wallet_protection()
    
    print("\n🛡️ Protection Features:")
    print("  • Block known scam tokens")
    print("  • Warn on suspicious transactions")
    print("  • Transaction simulation")
    print("  • Customizable protection levels")
    print("  • Real-time risk assessment")
    
    print("\n📊 Protection Levels:")
    print("  🟢 Minimal - Block only known scams")
    print("  🟡 Standard - Block + warnings")
    print("  🔴 Maximum - Block + warnings + simulation")
    
    print("\n⚡ Protection Rules:")
    for rule in protection.rules:
        status = "✅" if rule.enabled else "❌"
        print(f"  {status} {rule.name} ({rule.action.value})")
    
    print("\n" + "=" * 70)
