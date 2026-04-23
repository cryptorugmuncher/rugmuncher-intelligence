"""
Trending Scams Monitor - Real-Time Scam Detection
=================================================
Monitors for trending/potential scams across:
- New token launches
- Social media trends
- ChainAbuse reports
- Wallet clustering
- Volume anomalies
"""

import json
import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class ScamStage(Enum):
    """Stage of scam detection."""
    EARLY_WARNING = "early_warning"
    SUSPICIOUS = "suspicious"
    CONFIRMED = "confirmed"
    RUGGED = "rugged"
    POST_RUG = "post_rug"


class ScamType(Enum):
    """Type of scam."""
    RUG_PULL = "rug_pull"
    PUMP_AND_DUMP = "pump_and_dump"
    HONEYPOT = "honeypot"
    FAKE_TOKEN = "fake_token"
    PHISHING = "phishing"
    BOT_MANIPULATION = "bot_manipulation"
    INSIDER_TRADING = "insider_trading"
    UNKNOWN = "unknown"


@dataclass
class ScamIndicator:
    """A single scam indicator."""
    indicator_type: str
    severity: str  # low, medium, high, critical
    description: str
    evidence: Dict
    detected_at: datetime


@dataclass
class TrendingScam:
    """A trending/potential scam."""
    scam_id: str
    token_address: str
    token_symbol: str
    token_name: str
    
    # Detection
    first_detected: datetime
    stage: ScamStage
    scam_type: ScamType
    confidence: float  # 0-1
    
    # Indicators
    indicators: List[ScamIndicator] = field(default_factory=list)
    
    # Metrics
    price_at_detection: float = 0.0
    current_price: float = 0.0
    price_change_24h: float = 0.0
    market_cap: float = 0.0
    liquidity: float = 0.0
    holder_count: int = 0
    
    # Social
    social_mentions_24h: int = 0
    social_sentiment: str = "neutral"
    
    # Wallets
    suspicious_wallets: List[str] = field(default_factory=list)
    connected_clusters: List[str] = field(default_factory=list)
    
    # Reports
    chainabuse_reports: int = 0
    community_reports: int = 0
    
    # Timeline
    timeline: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "scam_id": self.scam_id,
            "token": {
                "address": self.token_address,
                "symbol": self.token_symbol,
                "name": self.token_name
            },
            "detection": {
                "first_detected": self.first_detected.isoformat(),
                "stage": self.stage.value,
                "type": self.scam_type.value,
                "confidence": self.confidence
            },
            "indicators": [
                {
                    "type": i.indicator_type,
                    "severity": i.severity,
                    "description": i.description,
                    "detected_at": i.detected_at.isoformat()
                }
                for i in self.indicators
            ],
            "metrics": {
                "price": {
                    "at_detection": self.price_at_detection,
                    "current": self.current_price,
                    "change_24h": self.price_change_24h
                },
                "market_cap": self.market_cap,
                "liquidity": self.liquidity,
                "holders": self.holder_count
            },
            "social": {
                "mentions_24h": self.social_mentions_24h,
                "sentiment": self.social_sentiment
            },
            "risk": {
                "suspicious_wallets": len(self.suspicious_wallets),
                "connected_clusters": len(self.connected_clusters),
                "chainabuse_reports": self.chainabuse_reports,
                "community_reports": self.community_reports
            }
        }


class TrendingScamsMonitor:
    """
    Monitors for trending and potential scams in real-time.
    """
    
    def __init__(self):
        self.active_scams: Dict[str, TrendingScam] = {}  # token_address -> scam
        self.scam_history: List[TrendingScam] = []
        self.known_scammer_wallets: Set[str] = set()
        self.suspicious_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Alert thresholds
        self.alert_thresholds = {
            "price_drop": 0.50,  # 50% drop
            "liquidity_removal": 0.70,  # 70% removed
            "holder_growth_anomaly": 5.0,  # 5x normal rate
            "social_spike": 10.0,  # 10x mentions
        }
    
    async def monitor_token(self, token_address: str) -> Optional[TrendingScam]:
        """Start monitoring a token for scam indicators."""
        if token_address in self.active_scams:
            return self.active_scams[token_address]
        
        scam = TrendingScam(
            scam_id=f"scam_{token_address[:16]}_{int(datetime.now().timestamp())}",
            token_address=token_address,
            token_symbol="UNKNOWN",
            token_name="Unknown Token",
            first_detected=datetime.now(),
            stage=ScamStage.EARLY_WARNING,
            scam_type=ScamType.UNKNOWN,
            confidence=0.0
        )
        
        self.active_scams[token_address] = scam
        return scam
    
    async def check_new_token(self, token_data: Dict) -> Optional[TrendingScam]:
        """Check a newly launched token for red flags."""
        token_address = token_data.get("address")
        
        scam = await self.monitor_token(token_address)
        scam.token_symbol = token_data.get("symbol", "UNKNOWN")
        scam.token_name = token_data.get("name", "Unknown Token")
        
        # Run initial checks
        await self._check_deployer_history(scam, token_data)
        await self._check_liquidity_status(scam, token_data)
        await self._check_holder_distribution(scam, token_data)
        await self._check_social_signals(scam, token_data)
        await self._check_volume_anomalies(scam, token_data)
        
        # Update confidence
        scam.confidence = self._calculate_confidence(scam)
        
        # Update stage
        scam.stage = self._determine_stage(scam)
        
        # Determine scam type
        scam.scam_type = self._determine_scam_type(scam)
        
        return scam
    
    async def _check_deployer_history(self, scam: TrendingScam, token_data: Dict):
        """Check deployer's history for red flags."""
        deployer = token_data.get("deployer")
        
        if not deployer:
            return
        
        # Check if known scammer
        if deployer in self.known_scammer_wallets:
            scam.indicators.append(ScamIndicator(
                indicator_type="known_scammer_deployer",
                severity="critical",
                description=f"Deployer {deployer[:16]}... is a known scammer",
                evidence={"wallet": deployer},
                detected_at=datetime.now()
            ))
        
        # Check deployer wallet age
        wallet_age_days = token_data.get("deployer_wallet_age_days", 0)
        if wallet_age_days < 7:
            scam.indicators.append(ScamIndicator(
                indicator_type="new_deployer_wallet",
                severity="high",
                description=f"Deployer wallet is only {wallet_age_days} days old",
                evidence={"wallet_age_days": wallet_age_days},
                detected_at=datetime.now()
            ))
    
    async def _check_liquidity_status(self, scam: TrendingScam, token_data: Dict):
        """Check liquidity for red flags."""
        liquidity_locked = token_data.get("liquidity_locked", False)
        liquidity_amount = token_data.get("liquidity_amount", 0)
        
        if not liquidity_locked:
            scam.indicators.append(ScamIndicator(
                indicator_type="unlocked_liquidity",
                severity="critical",
                description="Liquidity is NOT locked - rug pull risk",
                evidence={"liquidity_amount": liquidity_amount},
                detected_at=datetime.now()
            ))
        
        if liquidity_amount < 10000:  # Less than $10k
            scam.indicators.append(ScamIndicator(
                indicator_type="low_liquidity",
                severity="high",
                description=f"Very low liquidity: ${liquidity_amount:,.0f}",
                evidence={"liquidity_amount": liquidity_amount},
                detected_at=datetime.now()
            ))
        
        scam.liquidity = liquidity_amount
    
    async def _check_holder_distribution(self, scam: TrendingScam, token_data: Dict):
        """Check holder distribution for red flags."""
        holder_count = token_data.get("holder_count", 0)
        top_holder_percentage = token_data.get("top_holder_percentage", 0)
        
        scam.holder_count = holder_count
        
        if top_holder_percentage > 50:
            scam.indicators.append(ScamIndicator(
                indicator_type="extreme_supply_concentration",
                severity="critical",
                description=f"Top holder owns {top_holder_percentage}% of supply",
                evidence={"top_holder_percentage": top_holder_percentage},
                detected_at=datetime.now()
            ))
        elif top_holder_percentage > 30:
            scam.indicators.append(ScamIndicator(
                indicator_type="high_supply_concentration",
                severity="high",
                description=f"Top holder owns {top_holder_percentage}% of supply",
                evidence={"top_holder_percentage": top_holder_percentage},
                detected_at=datetime.now()
            ))
    
    async def _check_social_signals(self, scam: TrendingScam, token_data: Dict):
        """Check social media for red flags."""
        social_mentions = token_data.get("social_mentions_24h", 0)
        bot_ratio = token_data.get("social_bot_ratio", 0)
        
        scam.social_mentions_24h = social_mentions
        
        if bot_ratio > 0.7:
            scam.indicators.append(ScamIndicator(
                indicator_type="high_bot_activity",
                severity="high",
                description=f"{bot_ratio*100:.0f}% of social activity appears to be bots",
                evidence={"bot_ratio": bot_ratio},
                detected_at=datetime.now()
            ))
        
        if social_mentions > 10000 and token_data.get("holder_count", 0) < 100:
            scam.indicators.append(ScamIndicator(
                indicator_type="social_holder_mismatch",
                severity="medium",
                description="High social mentions but low holder count - artificial hype",
                evidence={
                    "social_mentions": social_mentions,
                    "holder_count": token_data.get("holder_count", 0)
                },
                detected_at=datetime.now()
            ))
    
    async def _check_volume_anomalies(self, scam: TrendingScam, token_data: Dict):
        """Check for volume/trading anomalies."""
        volume_24h = token_data.get("volume_24h", 0)
        market_cap = token_data.get("market_cap", 0)
        
        scam.market_cap = market_cap
        
        # Check for wash trading
        if volume_24h > market_cap * 5:  # Volume > 5x market cap
            scam.indicators.append(ScamIndicator(
                indicator_type="suspicious_volume",
                severity="high",
                description=f"Volume {volume_24h/market_cap:.1f}x market cap - possible wash trading",
                evidence={
                    "volume_24h": volume_24h,
                    "market_cap": market_cap
                },
                detected_at=datetime.now()
            ))
    
    def _calculate_confidence(self, scam: TrendingScam) -> float:
        """Calculate confidence score based on indicators."""
        if not scam.indicators:
            return 0.0
        
        severity_scores = {
            "critical": 1.0,
            "high": 0.7,
            "medium": 0.4,
            "low": 0.2
        }
        
        total_score = sum(severity_scores.get(i.severity, 0) for i in scam.indicators)
        confidence = min(total_score / 2, 1.0)  # Cap at 1.0
        
        return confidence
    
    def _determine_stage(self, scam: TrendingScam) -> ScamStage:
        """Determine scam stage based on indicators."""
        critical_count = sum(1 for i in scam.indicators if i.severity == "critical")
        high_count = sum(1 for i in scam.indicators if i.severity == "high")
        
        if critical_count >= 2:
            return ScamStage.CONFIRMED
        elif critical_count >= 1 or high_count >= 2:
            return ScamStage.SUSPICIOUS
        else:
            return ScamStage.EARLY_WARNING
    
    def _determine_scam_type(self, scam: TrendingScam) -> ScamType:
        """Determine likely scam type."""
        indicator_types = [i.indicator_type for i in scam.indicators]
        
        if "unlocked_liquidity" in indicator_types and "extreme_supply_concentration" in indicator_types:
            return ScamType.RUG_PULL
        
        if "suspicious_volume" in indicator_types and "high_bot_activity" in indicator_types:
            return ScamType.PUMP_AND_DUMP
        
        if "known_scammer_deployer" in indicator_types:
            return ScamType.RUG_PULL
        
        return ScamType.UNKNOWN
    
    async def update_scam(self, token_address: str, new_data: Dict):
        """Update scam data with new information."""
        scam = self.active_scams.get(token_address)
        if not scam:
            return
        
        # Update metrics
        scam.current_price = new_data.get("current_price", scam.current_price)
        scam.price_change_24h = new_data.get("price_change_24h", scam.price_change_24h)
        scam.liquidity = new_data.get("liquidity", scam.liquidity)
        scam.holder_count = new_data.get("holder_count", scam.holder_count)
        scam.social_mentions_24h = new_data.get("social_mentions_24h", scam.social_mentions_24h)
        
        # Check for new indicators
        if new_data.get("liquidity_removed", 0) > 0.7:
            scam.indicators.append(ScamIndicator(
                indicator_type="liquidity_removed",
                severity="critical",
                description=f"{new_data['liquidity_removed']*100:.0f}% of liquidity removed",
                evidence={"amount_removed": new_data["liquidity_removed"]},
                detected_at=datetime.now()
            ))
            scam.stage = ScamStage.RUGGED
        
        # Update confidence
        scam.confidence = self._calculate_confidence(scam)
        
        # Add to timeline
        scam.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "price": scam.current_price,
            "liquidity": scam.liquidity,
            "holders": scam.holder_count
        })
    
    async def get_trending_list(self, limit: int = 20) -> List[Dict]:
        """Get list of trending scams."""
        # Sort by confidence and recency
        sorted_scams = sorted(
            self.active_scams.values(),
            key=lambda s: (s.confidence, s.first_detected),
            reverse=True
        )
        
        return [scam.to_dict() for scam in sorted_scams[:limit]]
    
    async def get_scam_report(self, token_address: str) -> Optional[Dict]:
        """Get detailed scam report."""
        scam = self.active_scams.get(token_address)
        if not scam:
            return None
        
        return {
            "scam": scam.to_dict(),
            "verdict": self._generate_verdict(scam),
            "warnings": self._generate_warnings(scam),
            "recommendations": self._generate_recommendations(scam)
        }
    
    def _generate_verdict(self, scam: TrendingScam) -> str:
        """Generate verdict on scam."""
        if scam.stage == ScamStage.RUGGED:
            return f"🚨 CONFIRMED RUG PULL - {scam.token_symbol} has been rugged"
        elif scam.stage == ScamStage.CONFIRMED:
            return f"🚨 HIGH CONFIDENCE SCAM - Multiple critical indicators detected"
        elif scam.stage == ScamStage.SUSPICIOUS:
            return f"⚠️ SUSPICIOUS - Several red flags present, exercise caution"
        else:
            return f"⚡ MONITORING - Early warning indicators detected"
    
    def _generate_warnings(self, scam: TrendingScam) -> List[str]:
        """Generate warnings about scam."""
        warnings = []
        
        for indicator in scam.indicators:
            if indicator.severity in ["critical", "high"]:
                warnings.append(indicator.description)
        
        if scam.confidence > 0.7:
            warnings.append(f"High confidence scam detection: {scam.confidence*100:.0f}%")
        
        return warnings
    
    def _generate_recommendations(self, scam: TrendingScam) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        if scam.stage in [ScamStage.CONFIRMED, ScamStage.RUGGED]:
            recommendations.append("🚨 DO NOT INVEST - High scam probability")
            recommendations.append("Report to ChainAbuse and community channels")
        elif scam.stage == ScamStage.SUSPICIOUS:
            recommendations.append("⚠️ Exercise extreme caution")
            recommendations.append("Wait for more information before investing")
            recommendations.append("Check contract on RugCheck.xyz")
        else:
            recommendations.append("⚡ Monitor for additional indicators")
            recommendations.append("DYOR before investing")
        
        return recommendations
    
    async def add_chainabuse_report(self, token_address: str, report_data: Dict):
        """Add a ChainAbuse report to a scam."""
        scam = self.active_scams.get(token_address)
        if scam:
            scam.chainabuse_reports += 1
            scam.indicators.append(ScamIndicator(
                indicator_type="chainabuse_report",
                severity="high",
                description="Reported on ChainAbuse",
                evidence=report_data,
                detected_at=datetime.now()
            ))
    
    def get_stats(self) -> Dict:
        """Get monitor statistics."""
        stages = defaultdict(int)
        types = defaultdict(int)
        
        for scam in self.active_scams.values():
            stages[scam.stage.value] += 1
            types[scam.scam_type.value] += 1
        
        return {
            "total_monitored": len(self.active_scams),
            "by_stage": dict(stages),
            "by_type": dict(types),
            "high_confidence": len([s for s in self.active_scams.values() if s.confidence > 0.7])
        }


# Global instance
_monitor = None

def get_trending_scams_monitor() -> TrendingScamsMonitor:
    """Get global trending scams monitor."""
    global _monitor
    if _monitor is None:
        _monitor = TrendingScamsMonitor()
    return _monitor


if __name__ == "__main__":
    print("=" * 70)
    print("TRENDING SCAMS MONITOR")
    print("=" * 70)
    
    monitor = get_trending_scams_monitor()
    
    print("\n📊 Features:")
    print("  • Real-time scam detection")
    print("  • New token monitoring")
    print("  • Social signal analysis")
    print("  • Volume anomaly detection")
    print("  • ChainAbuse integration")
    
    print("\n🚨 Scam Stages:")
    print("  ⚡ Early Warning - Initial indicators")
    print("  ⚠️ Suspicious - Multiple red flags")
    print("  🚨 Confirmed - High confidence scam")
    print("  💀 Rugged - Liquidity removed")
    print("  📊 Post-Rug - Aftermath analysis")
    
    print("\n" + "=" * 70)
