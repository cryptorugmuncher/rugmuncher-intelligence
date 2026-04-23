"""
Dev Finder - Developer History & Token Tracking
===============================================
Finds developers behind tokens and tracks:
- All tokens they've deployed
- Rug pull history
- Wallet connections
- Social profiles
- KYC vectors
"""

import json
import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TokenStatus(Enum):
    """Status of a token."""
    ACTIVE = "active"
    RUGGED = "rugged"
    ABANDONED = "abandoned"
    UNKNOWN = "unknown"
    UNDER_INVESTIGATION = "under_investigation"


@dataclass
class Token:
    """Represents a token deployed by a developer."""
    address: str
    name: str
    symbol: str
    deploy_date: datetime
    status: TokenStatus
    current_price: float = 0.0
    ath_price: float = 0.0
    atl_price: float = 0.0
    market_cap: float = 0.0
    liquidity: float = 0.0
    holder_count: int = 0
    
    # Rug metrics
    rugged_date: Optional[datetime] = None
    rugged_percentage: float = 0.0  # How much price dropped
    victim_count: int = 0
    estimated_loss_usd: float = 0.0
    
    # Evidence
    red_flags: List[str] = field(default_factory=list)
    transaction_signatures: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "name": self.name,
            "symbol": self.symbol,
            "deploy_date": self.deploy_date.isoformat() if self.deploy_date else None,
            "status": self.status.value,
            "price_data": {
                "current": self.current_price,
                "ath": self.ath_price,
                "atl": self.atl_price,
                "drop_from_ath": round((1 - self.current_price / self.ath_price) * 100, 2) if self.ath_price > 0 else 0
            },
            "market_cap": self.market_cap,
            "liquidity": self.liquidity,
            "holder_count": self.holder_count,
            "rug_data": {
                "rugged_date": self.rugged_date.isoformat() if self.rugged_date else None,
                "rugged_percentage": self.rugged_percentage,
                "victim_count": self.victim_count,
                "estimated_loss_usd": self.estimated_loss_usd
            },
            "red_flags": self.red_flags
        }


@dataclass
class Developer:
    """Represents a developer/team."""
    primary_wallet: str
    aliases: List[str] = field(default_factory=list)
    wallets: List[str] = field(default_factory=list)
    
    # Identity
    known_name: Optional[str] = None
    social_profiles: Dict[str, str] = field(default_factory=dict)
    kyc_status: str = "unknown"  # verified, partial, none, unknown
    kyc_provider: Optional[str] = None
    
    # History
    first_seen: Optional[datetime] = None
    total_tokens_deployed: int = 0
    tokens: List[Token] = field(default_factory=list)
    
    # Rug stats
    rugged_tokens: int = 0
    abandoned_tokens: int = 0
    active_tokens: int = 0
    total_estimated_victims: int = 0
    total_estimated_losses: float = 0.0
    
    # Risk
    risk_score: float = 0.0  # 0-100
    risk_level: str = "unknown"  # low, medium, high, extreme
    
    # Evidence
    evidence_links: List[str] = field(default_factory=list)
    chainabuse_reports: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "primary_wallet": self.primary_wallet,
            "aliases": self.aliases,
            "wallets": self.wallets,
            "known_name": self.known_name,
            "social_profiles": self.social_profiles,
            "kyc_status": self.kyc_status,
            "kyc_provider": self.kyc_provider,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "token_stats": {
                "total_deployed": self.total_tokens_deployed,
                "rugged": self.rugged_tokens,
                "abandoned": self.abandoned_tokens,
                "active": self.active_tokens
            },
            "impact": {
                "estimated_victims": self.total_estimated_victims,
                "estimated_losses_usd": self.total_estimated_losses
            },
            "risk": {
                "score": self.risk_score,
                "level": self.risk_level
            },
            "tokens": [t.to_dict() for t in self.tokens],
            "evidence_links": self.evidence_links
        }


class DevFinder:
    """
    Finds and tracks developers behind crypto tokens.
    """
    
    def __init__(self):
        self.developer_db: Dict[str, Developer] = {}  # wallet -> Developer
        self.token_to_dev: Dict[str, str] = {}  # token -> primary_wallet
        self.known_scammers: Set[str] = set()
        
    async def find_developer(self, token_address: str) -> Optional[Developer]:
        """
        Find the developer behind a token.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Developer profile or None
        """
        # Check if we already know this token
        if token_address in self.token_to_dev:
            dev_wallet = self.token_to_dev[token_address]
            return self.developer_db.get(dev_wallet)
        
        # Otherwise, trace from token
        deployer = await self._trace_token_deployer(token_address)
        
        if not deployer:
            return None
        
        # Check if we know this deployer
        if deployer in self.developer_db:
            dev = self.developer_db[deployer]
        else:
            # Create new developer profile
            dev = Developer(
                primary_wallet=deployer,
                first_seen=datetime.now()
            )
            self.developer_db[deployer] = dev
        
        # Add token to developer
        token = await self._analyze_token(token_address)
        if token:
            dev.tokens.append(token)
            dev.total_tokens_deployed = len(dev.tokens)
            self.token_to_dev[token_address] = deployer
        
        # Update stats
        self._update_developer_stats(dev)
        
        return dev
    
    async def _trace_token_deployer(self, token_address: str) -> Optional[str]:
        """Trace the deployer wallet of a token."""
        # In production, this would query Helius/chain data
        # For demo, return placeholder
        
        # Simulate finding deployer
        # Real implementation would:
        # 1. Query token creation transaction
        # 2. Find the wallet that paid for deployment
        # 3. Verify through multiple sources
        
        return f"DeployerOf{token_address[:8]}"
    
    async def _analyze_token(self, token_address: str) -> Optional[Token]:
        """Analyze a token's history and status."""
        # In production, query BirdEye, Helius, etc.
        
        token = Token(
            address=token_address,
            name="Sample Token",
            symbol="SAMPLE",
            deploy_date=datetime.now() - timedelta(days=30),
            status=TokenStatus.ACTIVE,
            current_price=0.0001,
            ath_price=0.001,
            atl_price=0.00005,
            market_cap=50000,
            liquidity=10000,
            holder_count=500
        )
        
        return token
    
    async def get_all_tokens_by_dev(self, wallet: str) -> List[Token]:
        """Get all tokens deployed by a developer."""
        dev = self.developer_db.get(wallet)
        if dev:
            return dev.tokens
        return []
    
    async def get_rug_history(self, wallet: str) -> List[Token]:
        """Get rug pull history for a developer."""
        tokens = await self.get_all_tokens_by_dev(wallet)
        return [t for t in tokens if t.status == TokenStatus.RUGGED]
    
    async def find_connected_wallets(self, wallet: str) -> List[str]:
        """Find all wallets connected to a developer."""
        # In production:
        # 1. Analyze transaction patterns
        # 2. Find common funding sources
        # 3. Identify coordinated activity
        
        dev = self.developer_db.get(wallet)
        if dev:
            return dev.wallets
        return []
    
    async def find_by_social(self, platform: str, username: str) -> List[Developer]:
        """Find developers by social media profile."""
        results = []
        for dev in self.developer_db.values():
            if dev.social_profiles.get(platform) == username:
                results.append(dev)
        return results
    
    def _update_developer_stats(self, dev: Developer):
        """Update developer statistics."""
        # Count token statuses
        dev.rugged_tokens = len([t for t in dev.tokens if t.status == TokenStatus.RUGGED])
        dev.abandoned_tokens = len([t for t in dev.tokens if t.status == TokenStatus.ABANDONED])
        dev.active_tokens = len([t for t in dev.tokens if t.status == TokenStatus.ACTIVE])
        
        # Calculate impact
        dev.total_estimated_victims = sum(t.victim_count for t in dev.tokens)
        dev.total_estimated_losses = sum(t.estimated_loss_usd for t in dev.tokens)
        
        # Calculate risk score
        dev.risk_score = self._calculate_risk_score(dev)
        dev.risk_level = self._risk_score_to_level(dev.risk_score)
    
    def _calculate_risk_score(self, dev: Developer) -> float:
        """Calculate developer risk score (0-100)."""
        score = 0.0
        
        if dev.total_tokens_deployed == 0:
            return 50.0  # Unknown
        
        # Rug ratio
        rug_ratio = dev.rugged_tokens / dev.total_tokens_deployed
        score += rug_ratio * 40
        
        # Abandoned ratio
        abandoned_ratio = dev.abandoned_tokens / dev.total_tokens_deployed
        score += abandoned_ratio * 20
        
        # Victim impact
        if dev.total_estimated_victims > 1000:
            score += 20
        elif dev.total_estimated_victims > 100:
            score += 10
        
        # Loss impact
        if dev.total_estimated_losses > 1000000:
            score += 20
        elif dev.total_estimated_losses > 100000:
            score += 10
        
        # KYC bonus (negative = good)
        if dev.kyc_status == "verified":
            score -= 15
        elif dev.kyc_status == "none":
            score += 5
        
        return min(100, max(0, score))
    
    def _risk_score_to_level(self, score: float) -> str:
        """Convert risk score to level."""
        if score >= 70:
            return "extreme"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        elif score >= 10:
            return "low"
        else:
            return "minimal"
    
    async def generate_dev_report(self, wallet: str) -> Dict:
        """Generate comprehensive developer report."""
        dev = self.developer_db.get(wallet)
        if not dev:
            return {"error": "Developer not found"}
        
        # Get rug history
        rug_history = await self.get_rug_history(wallet)
        
        # Get connected wallets
        connected = await self.find_connected_wallets(wallet)
        
        # Timeline
        timeline = self._generate_timeline(dev)
        
        return {
            "developer": dev.to_dict(),
            "rug_history": [t.to_dict() for t in rug_history],
            "connected_wallets": connected,
            "timeline": timeline,
            "verdict": self._generate_dev_verdict(dev),
            "warnings": self._generate_dev_warnings(dev)
        }
    
    def _generate_timeline(self, dev: Developer) -> List[Dict]:
        """Generate timeline of developer activity."""
        events = []
        
        for token in dev.tokens:
            events.append({
                "date": token.deploy_date.isoformat() if token.deploy_date else None,
                "type": "token_deploy",
                "token": token.symbol,
                "address": token.address
            })
            
            if token.rugged_date:
                events.append({
                    "date": token.rugged_date.isoformat(),
                    "type": "rug_pull",
                    "token": token.symbol,
                    "loss_usd": token.estimated_loss_usd
                })
        
        events.sort(key=lambda x: x["date"] or "")
        return events
    
    def _generate_dev_verdict(self, dev: Developer) -> str:
        """Generate verdict on developer."""
        if dev.risk_level == "extreme":
            return f"🚨 EXTREME RISK - Known scammer with {dev.rugged_tokens} confirmed rug pulls. AVOID ALL TOKENS."
        elif dev.risk_level == "high":
            return f"⚠️ HIGH RISK - Developer has {dev.rugged_tokens} rugged tokens. Exercise extreme caution."
        elif dev.risk_level == "medium":
            return f"⚡ MODERATE RISK - Some concerning history. DYOR before investing."
        elif dev.risk_level == "low":
            return f"✅ LOW RISK - Generally clean history but always verify."
        else:
            return f"✅ MINIMAL RISK - No significant red flags detected."
    
    def _generate_dev_warnings(self, dev: Developer) -> List[str]:
        """Generate warnings about developer."""
        warnings = []
        
        if dev.rugged_tokens > 0:
            warnings.append(f"Has rugged {dev.rugged_tokens} token(s)")
        
        if dev.total_estimated_losses > 100000:
            warnings.append(f"Estimated ${dev.total_estimated_losses:,.0f} in victim losses")
        
        if dev.total_estimated_victims > 100:
            warnings.append(f"Approximately {dev.total_estimated_victims} victims")
        
        if dev.kyc_status == "none":
            warnings.append("Anonymous team - no KYC")
        
        if len(dev.tokens) > 5:
            warnings.append(f"Serial token launcher ({len(dev.tokens)} tokens)")
        
        return warnings
    
    def add_to_scammer_list(self, wallet: str, evidence: str):
        """Add a wallet to the known scammer list."""
        self.known_scammers.add(wallet)
        
        dev = self.developer_db.get(wallet)
        if dev:
            dev.evidence_links.append(evidence)
    
    def is_known_scammer(self, wallet: str) -> bool:
        """Check if wallet is a known scammer."""
        return wallet in self.known_scammers
    
    def search_database(self, query: str) -> List[Developer]:
        """Search developer database."""
        results = []
        query_lower = query.lower()
        
        for dev in self.developer_db.values():
            # Search by name
            if dev.known_name and query_lower in dev.known_name.lower():
                results.append(dev)
                continue
            
            # Search by wallet
            if query_lower in dev.primary_wallet.lower():
                results.append(dev)
                continue
            
            # Search by token
            for token in dev.tokens:
                if query_lower in token.name.lower() or query_lower in token.symbol.lower():
                    results.append(dev)
                    break
        
        return results


# Global instance
_finder = None

def get_dev_finder() -> DevFinder:
    """Get global dev finder instance."""
    global _finder
    if _finder is None:
        _finder = DevFinder()
    return _finder


if __name__ == "__main__":
    print("=" * 70)
    print("DEV FINDER - Developer History Tracker")
    print("=" * 70)
    
    finder = get_dev_finder()
    
    print("\n🔍 Features:")
    print("  • Find developer behind any token")
    print("  • Track all tokens they've deployed")
    print("  • Identify rug pull history")
    print("  • Find connected wallets")
    print("  • Social profile mapping")
    print("  • Risk scoring (0-100)")
    print("  • Comprehensive reports")
    
    print("\n📊 Risk Levels:")
    print("  🟢 Minimal (0-10)   - Clean history")
    print("  🟢 Low (10-30)      - Generally safe")
    print("  🟡 Medium (30-50)   - Some concerns")
    print("  🔴 High (50-70)     - Multiple red flags")
    print("  🚨 Extreme (70-100) - Known scammer")
    
    print("\n" + "=" * 70)
