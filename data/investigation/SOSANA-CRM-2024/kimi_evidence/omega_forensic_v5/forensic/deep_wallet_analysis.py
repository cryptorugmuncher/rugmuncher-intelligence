"""
Deep Wallet Analysis - Advanced Wallet Investigation
====================================================
Deep analysis of wallets looking for:
- Past scam associations
- KOL connections
- Exchange relationships
- Mixer usage
- Cross-chain activity
- Behavioral patterns
"""

import json
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class WalletTag(Enum):
    """Tags for wallet classification."""
    SCAMMER = "scammer"
    SUSPECTED_SCAMMER = "suspected_scammer"
    KOL = "kol"
    DEV = "dev"
    EXCHANGE = "exchange"
    MARKET_MAKER = "market_maker"
    WHALE = "whale"
    BOT = "bot"
    MIXER_USER = "mixer_user"
    BRIDGE_USER = "bridge_user"
    EARLY_ADOPTER = "early_adopter"
    UNKNOWN = "unknown"


class RiskIndicator(Enum):
    """Risk indicators for wallets."""
    KNOWN_SCAMMER = "known_scammer"
    RUGGED_BEFORE = "rugged_before"
    ASSOCIATED_WITH_SCAM = "associated_with_scam"
    KOL_PROMOTED_SCAMS = "kol_promoted_scams"
    MIXER_USAGE = "mixer_usage"
    SUSPICIOUS_TIMING = "suspicious_timing"
    BOT_BEHAVIOR = "bot_behavior"
    INSIDER_TRADING = "insider_trading"
    WASH_TRADING = "wash_trading"
    NEW_WALLET = "new_wallet"


@dataclass
class WalletAssociation:
    """Association between wallets."""
    wallet_a: str
    wallet_b: str
    association_type: str
    strength: float  # 0-1
    evidence: List[Dict]
    first_seen: datetime
    last_seen: datetime


@dataclass
class ScamConnection:
    """Connection to a known scam."""
    scam_token: str
    scam_name: str
    connection_type: str  # deployer, holder, promoter, beneficiary
    evidence: str
    date: datetime
    loss_amount_usd: float = 0.0


@dataclass
class DeepWalletProfile:
    """Complete deep analysis of a wallet."""
    address: str
    analyzed_at: datetime
    
    # Identity
    tags: List[WalletTag] = field(default_factory=list)
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None
    
    # Activity
    first_transaction: Optional[datetime] = None
    last_transaction: Optional[datetime] = None
    total_transactions: int = 0
    total_volume_usd: float = 0.0
    unique_counterparties: int = 0
    
    # Risk
    risk_score: float = 0.0
    risk_level: str = "unknown"
    risk_indicators: List[RiskIndicator] = field(default_factory=list)
    
    # Scam connections
    scam_connections: List[ScamConnection] = field(default_factory=list)
    
    # KOL connections
    kol_connections: List[Dict] = field(default_factory=list)
    
    # Exchange connections
    exchange_deposits: float = 0.0
    exchange_withdrawals: float = 0.0
    preferred_exchanges: List[str] = field(default_factory=list)
    
    # Mixer/Bridge usage
    mixer_volume: float = 0.0
    bridge_volume: float = 0.0
    mixer_transactions: int = 0
    
    # Behavioral
    avg_transaction_size: float = 0.0
    transaction_frequency: float = 0.0
    preferred_hours: List[int] = field(default_factory=list)
    program_usage: Dict[str, int] = field(default_factory=dict)
    
    # Associations
    associated_wallets: List[WalletAssociation] = field(default_factory=list)
    
    # Cross-chain
    cross_chain_activity: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "analyzed_at": self.analyzed_at.isoformat(),
            "identity": {
                "tags": [t.value for t in self.tags],
                "entity_name": self.entity_name,
                "entity_type": self.entity_type
            },
            "activity": {
                "first_tx": self.first_transaction.isoformat() if self.first_transaction else None,
                "last_tx": self.last_transaction.isoformat() if self.last_transaction else None,
                "total_transactions": self.total_transactions,
                "total_volume_usd": self.total_volume_usd,
                "unique_counterparties": self.unique_counterparties
            },
            "risk": {
                "score": self.risk_score,
                "level": self.risk_level,
                "indicators": [i.value for i in self.risk_indicators]
            },
            "scam_connections": [
                {
                    "token": s.scam_token,
                    "name": s.scam_name,
                    "type": s.connection_type,
                    "date": s.date.isoformat() if s.date else None,
                    "loss_usd": s.loss_amount_usd
                }
                for s in self.scam_connections
            ],
            "kol_connections": self.kol_connections,
            "exchange_activity": {
                "deposits": self.exchange_deposits,
                "withdrawals": self.exchange_withdrawals,
                "preferred": self.preferred_exchanges
            },
            "privacy_tools": {
                "mixer_volume": self.mixer_volume,
                "mixer_txs": self.mixer_transactions,
                "bridge_volume": self.bridge_volume
            },
            "behavioral": {
                "avg_tx_size": self.avg_transaction_size,
                "tx_frequency": self.transaction_frequency,
                "preferred_hours": self.preferred_hours
            },
            "cross_chain": self.cross_chain_activity
        }


class DeepWalletAnalysis:
    """
    Deep analysis system for wallet investigation.
    """
    
    # Known scammer database (would be loaded from ChainAbuse, etc.)
    KNOWN_SCAMMERS: Set[str] = set()
    KNOWN_KOLS: Dict[str, Dict] = {}
    KNOWN_EXCHANGES: Dict[str, str] = {}
    KNOWN_MIXERS: Set[str] = set()
    
    # Risk scoring weights
    RISK_WEIGHTS = {
        RiskIndicator.KNOWN_SCAMMER: 100,
        RiskIndicator.RUGGED_BEFORE: 80,
        RiskIndicator.ASSOCIATED_WITH_SCAM: 60,
        RiskIndicator.KOL_PROMOTED_SCAMS: 50,
        RiskIndicator.MIXER_USAGE: 40,
        RiskIndicator.SUSPICIOUS_TIMING: 30,
        RiskIndicator.BOT_BEHAVIOR: 30,
        RiskIndicator.INSIDER_TRADING: 70,
        RiskIndicator.WASH_TRADING: 50,
        RiskIndicator.NEW_WALLET: 10
    }
    
    def __init__(self):
        self.profiles: Dict[str, DeepWalletProfile] = {}
        self.transaction_cache: Dict[str, List[Dict]] = {}
        
    async def analyze_wallet(
        self,
        wallet_address: str,
        depth: int = 2,
        include_history: bool = True
    ) -> DeepWalletProfile:
        """
        Perform deep analysis of a wallet.
        
        Args:
            wallet_address: Wallet to analyze
            depth: How many hops to analyze
            include_history: Whether to include full history
            
        Returns:
            DeepWalletProfile with complete analysis
        """
        # Check cache
        if wallet_address in self.profiles:
            cached = self.profiles[wallet_address]
            if (datetime.now() - cached.analyzed_at).hours < 1:
                return cached
        
        profile = DeepWalletProfile(
            address=wallet_address,
            analyzed_at=datetime.now()
        )
        
        # Fetch all transactions
        transactions = await self._fetch_all_transactions(wallet_address)
        profile.total_transactions = len(transactions)
        
        if transactions:
            profile.first_transaction = min(t.get("timestamp", datetime.max) for t in transactions)
            profile.last_transaction = max(t.get("timestamp", datetime.min) for t in transactions)
        
        # Check for known scammer
        await self._check_known_scammer(profile)
        
        # Check for KOL
        await self._check_kol_connection(profile)
        
        # Check exchange activity
        await self._analyze_exchange_activity(profile, transactions)
        
        # Check mixer/bridge usage
        await self._analyze_privacy_tools(profile, transactions)
        
        # Analyze behavior
        await self._analyze_behavior(profile, transactions)
        
        # Find scam connections
        await self._find_scam_connections(profile)
        
        # Find associated wallets
        if depth > 0:
            await self._find_associations(profile, depth)
        
        # Calculate risk score
        profile.risk_score = self._calculate_risk_score(profile)
        profile.risk_level = self._score_to_level(profile.risk_score)
        
        # Cache profile
        self.profiles[wallet_address] = profile
        
        return profile
    
    async def _fetch_all_transactions(self, wallet: str) -> List[Dict]:
        """Fetch all transactions for a wallet."""
        if wallet in self.transaction_cache:
            return self.transaction_cache[wallet]
        
        # In production, query Helius with pagination
        transactions = []
        
        self.transaction_cache[wallet] = transactions
        return transactions
    
    async def _check_known_scammer(self, profile: DeepWalletProfile):
        """Check if wallet is a known scammer."""
        if profile.address in self.KNOWN_SCAMMERS:
            profile.tags.append(WalletTag.SCAMMER)
            profile.risk_indicators.append(RiskIndicator.KNOWN_SCAMMER)
            profile.entity_name = "Known Scammer"
    
    async def _check_kol_connection(self, profile: DeepWalletProfile):
        """Check if wallet belongs to a KOL."""
        for kol_handle, kol_data in self.KNOWN_KOLS.items():
            if profile.address in kol_data.get("wallets", []):
                profile.tags.append(WalletTag.KOL)
                profile.entity_name = kol_data.get("name")
                profile.kol_connections.append({
                    "handle": kol_handle,
                    "name": kol_data.get("name"),
                    "reputation": kol_data.get("reputation_score", 50)
                })
    
    async def _analyze_exchange_activity(
        self,
        profile: DeepWalletProfile,
        transactions: List[Dict]
    ):
        """Analyze exchange deposit/withdrawal activity."""
        exchange_txs = []
        
        for tx in transactions:
            counterparty = tx.get("to") if tx.get("from") == profile.address else tx.get("from")
            
            if counterparty in self.KNOWN_EXCHANGES:
                exchange_name = self.KNOWN_EXCHANGES[counterparty]
                amount = tx.get("amount", 0)
                
                if tx.get("from") == profile.address:
                    profile.exchange_deposits += amount
                else:
                    profile.exchange_withdrawals += amount
                
                if exchange_name not in profile.preferred_exchanges:
                    profile.preferred_exchanges.append(exchange_name)
                
                exchange_txs.append(tx)
        
        if exchange_txs:
            profile.tags.append(WalletTag.WHALE if profile.exchange_deposits > 1000000 else WalletTag.UNKNOWN)
    
    async def _analyze_privacy_tools(
        self,
        profile: DeepWalletProfile,
        transactions: List[Dict]
    ):
        """Analyze mixer and bridge usage."""
        for tx in transactions:
            counterparty = tx.get("to") if tx.get("from") == profile.address else tx.get("from")
            
            if counterparty in self.KNOWN_MIXERS:
                profile.mixer_volume += tx.get("amount", 0)
                profile.mixer_transactions += 1
                
                if RiskIndicator.MIXER_USAGE not in profile.risk_indicators:
                    profile.risk_indicators.append(RiskIndicator.MIXER_USAGE)
            
            # Check for bridge usage (would need bridge contract list)
            if "bridge" in tx.get("program", "").lower():
                profile.bridge_volume += tx.get("amount", 0)
    
    async def _analyze_behavior(
        self,
        profile: DeepWalletProfile,
        transactions: List[Dict]
    ):
        """Analyze wallet behavior patterns."""
        if not transactions:
            return
        
        # Transaction sizes
        amounts = [tx.get("amount", 0) for tx in transactions]
        profile.avg_transaction_size = sum(amounts) / len(amounts)
        profile.total_volume_usd = sum(amounts)
        
        # Timing patterns
        timestamps = [tx.get("timestamp") for tx in transactions if tx.get("timestamp")]
        if timestamps and len(timestamps) > 1:
            timestamps.sort()
            time_span = (timestamps[-1] - timestamps[0]).days + 1
            profile.transaction_frequency = len(timestamps) / time_span
            
            # Preferred hours
            hours = [t.hour for t in timestamps]
            hour_counts = defaultdict(int)
            for h in hours:
                hour_counts[h] += 1
            profile.preferred_hours = sorted(hour_counts.keys(), key=lambda x: hour_counts[x], reverse=True)[:3]
        
        # Program usage
        for tx in transactions:
            program = tx.get("program", "unknown")
            profile.program_usage[program] = profile.program_usage.get(program, 0) + 1
        
        # Check for bot behavior
        if profile.transaction_frequency > 100:  # More than 100 tx/day
            profile.risk_indicators.append(RiskIndicator.BOT_BEHAVIOR)
            profile.tags.append(WalletTag.BOT)
        
        # Check for new wallet
        if profile.first_transaction:
            wallet_age = (datetime.now() - profile.first_transaction).days
            if wallet_age < 7:
                profile.risk_indicators.append(RiskIndicator.NEW_WALLET)
    
    async def _find_scam_connections(self, profile: DeepWalletProfile):
        """Find connections to known scams."""
        # In production, query scam database
        # Check if wallet:
        # - Deployed scam tokens
        # - Held scam tokens
        # - Promoted scams
        # - Received funds from scams
        
        # Demo: Check against known scammer list
        for scammer in self.KNOWN_SCAMMERS:
            if scammer == profile.address:
                continue
            
            # Check for transactions with scammer
            # This would query the blockchain
            pass
    
    async def _find_associations(
        self,
        profile: DeepWalletProfile,
        depth: int
    ):
        """Find associated wallets."""
        # Find wallets with strong connections
        # This would use the clustering engine
        pass
    
    def _calculate_risk_score(self, profile: DeepWalletProfile) -> float:
        """Calculate overall risk score."""
        score = 0.0
        
        for indicator in profile.risk_indicators:
            score += self.RISK_WEIGHTS.get(indicator, 10)
        
        # Boost for multiple scam connections
        score += len(profile.scam_connections) * 20
        
        # Boost for high mixer usage
        if profile.mixer_volume > 100000:
            score += 20
        
        return min(100, score)
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level."""
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
    
    async def generate_report(self, wallet_address: str) -> Dict:
        """Generate comprehensive wallet report."""
        profile = await self.analyze_wallet(wallet_address)
        
        return {
            "profile": profile.to_dict(),
            "verdict": self._generate_verdict(profile),
            "warnings": self._generate_warnings(profile),
            "recommendations": self._generate_recommendations(profile)
        }
    
    def _generate_verdict(self, profile: DeepWalletProfile) -> str:
        """Generate human-readable verdict."""
        if WalletTag.SCAMMER in profile.tags:
            return "🚨 CONFIRMED SCAMMER - Avoid all interactions"
        
        if profile.risk_score >= 80:
            return "⚠️ HIGH RISK - Multiple red flags detected"
        
        if profile.risk_score >= 60:
            return "⚡ ELEVATED RISK - Exercise caution"
        
        if profile.risk_score >= 40:
            return "📊 MODERATE RISK - Some concerns present"
        
        return "✅ LOW RISK - No significant red flags"
    
    def _generate_warnings(self, profile: DeepWalletProfile) -> List[str]:
        """Generate warnings."""
        warnings = []
        
        for indicator in profile.risk_indicators:
            if indicator == RiskIndicator.KNOWN_SCAMMER:
                warnings.append("This is a KNOWN scammer wallet")
            elif indicator == RiskIndicator.MIXER_USAGE:
                warnings.append(f"Has used mixers (${profile.mixer_volume:,.0f} volume)")
            elif indicator == RiskIndicator.BOT_BEHAVIOR:
                warnings.append("Exhibits bot-like transaction patterns")
            elif indicator == RiskIndicator.NEW_WALLET:
                warnings.append("Wallet is less than 7 days old")
        
        for scam in profile.scam_connections:
            warnings.append(f"Connected to {scam.scam_name} ({scam.connection_type})")
        
        return warnings
    
    def _generate_recommendations(self, profile: DeepWalletProfile) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        if profile.risk_score >= 80:
            recommendations.append("🚨 DO NOT INTERACT with this wallet")
        
        if profile.mixer_volume > 0:
            recommendations.append("⚠️ Privacy tool usage detected - exercise caution")
        
        if profile.risk_score >= 40:
            recommendations.append("🔍 Research thoroughly before any interaction")
        
        if not recommendations:
            recommendations.append("✅ No specific concerns - always DYOR")
        
        return recommendations


# Global instance
_deep_analysis = None

def get_deep_wallet_analysis() -> DeepWalletAnalysis:
    """Get global deep wallet analysis instance."""
    global _deep_analysis
    if _deep_analysis is None:
        _deep_analysis = DeepWalletAnalysis()
    return _deep_analysis


if __name__ == "__main__":
    print("=" * 70)
    print("DEEP WALLET ANALYSIS")
    print("=" * 70)
    
    print("\n🔍 Analysis Dimensions:")
    print("  • Past scam associations")
    print("  • KOL connections")
    print("  • Exchange relationships")
    print("  • Mixer/bridge usage")
    print("  • Cross-chain activity")
    print("  • Behavioral patterns")
    print("  • Associated wallets")
    
    print("\n🏷️ Wallet Tags:")
    for tag in WalletTag:
        print(f"  • {tag.value}")
    
    print("\n⚠️ Risk Indicators:")
    for indicator in RiskIndicator:
        print(f"  • {indicator.value}")
    
    print("\n" + "=" * 70)
