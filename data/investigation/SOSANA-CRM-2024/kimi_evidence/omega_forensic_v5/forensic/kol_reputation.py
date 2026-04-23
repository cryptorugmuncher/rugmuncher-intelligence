"""
KOL Reputation System - Key Opinion Leader Tracking
===================================================
Tracks and rates crypto influencers/KOLs based on:
- Call accuracy (successful vs failed calls)
- Rug pull associations
- Transparency (paid promotions disclosed)
- Community trust scores
- Historical performance
"""

import json
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class KOLStatus(Enum):
    """KOL verification status."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    SUSPICIOUS = "suspicious"
    BLACKLISTED = "blacklisted"


class CallType(Enum):
    """Type of call made by KOL."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    AVOID = "avoid"


@dataclass
class TokenCall:
    """A token call made by a KOL."""
    token_address: str
    token_symbol: str
    call_type: CallType
    called_at: datetime
    price_at_call: float
    
    # Result
    result: str = "pending"  # success, failure, pending
    current_price: float = 0.0
    price_change_24h: float = 0.0
    price_change_7d: float = 0.0
    peak_price: float = 0.0
    
    # Metadata
    was_paid: bool = False
    disclosed: bool = False
    evidence_link: str = ""
    
    def calculate_performance(self) -> float:
        """Calculate performance of this call."""
        if self.price_at_call == 0:
            return 0.0
        return ((self.current_price - self.price_at_call) / self.price_at_call) * 100


@dataclass
class KOLReputation:
    """Complete KOL reputation profile."""
    handle: str
    platform: str  # twitter, youtube, tiktok, etc.
    
    # Identity
    display_name: str = ""
    bio: str = ""
    profile_image: str = ""
    follower_count: int = 0
    account_created: Optional[datetime] = None
    
    # Status
    status: KOLStatus = KOLStatus.UNVERIFIED
    verification_date: Optional[datetime] = None
    
    # Performance metrics
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    pending_calls: int = 0
    
    # Accuracy by timeframe
    accuracy_24h: float = 0.0
    accuracy_7d: float = 0.0
    accuracy_30d: float = 0.0
    accuracy_all_time: float = 0.0
    
    # Financial metrics
    avg_return_24h: float = 0.0
    avg_return_7d: float = 0.0
    avg_return_30d: float = 0.0
    
    # Risk metrics
    rug_associations: int = 0
    undisclosed_paid_promos: int = 0
    scam_tokens_promoted: int = 0
    
    # Transparency
    disclosure_rate: float = 0.0  # Percentage of paid promos disclosed
    
    # Community scores
    community_trust_score: float = 50.0  # 0-100
    community_rating: float = 0.0  # 1-5 stars
    total_ratings: int = 0
    
    # Call history
    calls: List[TokenCall] = field(default_factory=list)
    
    # Overall score
    overall_score: float = 50.0  # 0-100
    tier: str = "unranked"  # diamond, platinum, gold, silver, bronze, unranked, blacklisted
    
    def to_dict(self) -> Dict:
        return {
            "handle": self.handle,
            "platform": self.platform,
            "display_name": self.display_name,
            "follower_count": self.follower_count,
            "status": self.status.value,
            "performance": {
                "total_calls": self.total_calls,
                "successful": self.successful_calls,
                "failed": self.failed_calls,
                "accuracy": {
                    "24h": self.accuracy_24h,
                    "7d": self.accuracy_7d,
                    "30d": self.accuracy_30d,
                    "all_time": self.accuracy_all_time
                },
                "avg_return": {
                    "24h": self.avg_return_24h,
                    "7d": self.avg_return_7d,
                    "30d": self.avg_return_30d
                }
            },
            "risk": {
                "rug_associations": self.rug_associations,
                "undisclosed_promos": self.undisclosed_paid_promos,
                "scam_tokens": self.scam_tokens_promoted,
                "disclosure_rate": self.disclosure_rate
            },
            "community": {
                "trust_score": self.community_trust_score,
                "rating": self.community_rating,
                "total_ratings": self.total_ratings
            },
            "overall": {
                "score": self.overall_score,
                "tier": self.tier
            }
        }


class KOLReputationSystem:
    """
    Tracks and rates KOLs based on their call performance.
    """
    
    # Tier thresholds
    TIER_THRESHOLDS = {
        "diamond": 90,
        "platinum": 80,
        "gold": 70,
        "silver": 60,
        "bronze": 50,
        "unranked": 0,
        "blacklisted": -1
    }
    
    def __init__(self):
        self.kols: Dict[str, KOLReputation] = {}  # handle -> KOL
        self.token_calls: Dict[str, List[TokenCall]] = defaultdict(list)  # token -> calls
        self.blacklist: List[str] = []
        
    async def register_kol(
        self, 
        handle: str, 
        platform: str,
        display_name: str = "",
        follower_count: int = 0
    ) -> KOLReputation:
        """Register a new KOL."""
        if handle in self.kols:
            return self.kols[handle]
        
        kol = KOLReputation(
            handle=handle,
            platform=platform,
            display_name=display_name or handle,
            follower_count=follower_count
        )
        
        self.kols[handle] = kol
        return kol
    
    async def record_call(
        self,
        kol_handle: str,
        token_address: str,
        token_symbol: str,
        call_type: CallType,
        price_at_call: float,
        was_paid: bool = False,
        disclosed: bool = False
    ) -> TokenCall:
        """Record a token call made by a KOL."""
        kol = self.kols.get(kol_handle)
        if not kol:
            raise ValueError(f"KOL {kol_handle} not registered")
        
        call = TokenCall(
            token_address=token_address,
            token_symbol=token_symbol,
            call_type=call_type,
            called_at=datetime.now(),
            price_at_call=price_at_call,
            was_paid=was_paid,
            disclosed=disclosed
        )
        
        kol.calls.append(call)
        self.token_calls[token_address].append(call)
        
        # Update stats
        kol.total_calls += 1
        kol.pending_calls += 1
        
        # Track disclosure
        if was_paid and not disclosed:
            kol.undisclosed_paid_promos += 1
        
        return call
    
    async def update_call_results(self):
        """Update results of all pending calls."""
        for kol in self.kols.values():
            for call in kol.calls:
                if call.result == "pending":
                    # In production, fetch current price from API
                    # For demo, simulate
                    call.current_price = call.price_at_call * 1.2  # Simulate 20% gain
                    call.price_change_24h = 20.0
                    
                    # Determine success
                    if call.call_type == CallType.BUY:
                        if call.current_price > call.price_at_call * 1.1:  # 10%+ gain
                            call.result = "success"
                            kol.successful_calls += 1
                            kol.pending_calls -= 1
                        elif call.current_price < call.price_at_call * 0.9:  # 10%+ loss
                            call.result = "failure"
                            kol.failed_calls += 1
                            kol.pending_calls -= 1
                    
                    elif call.call_type == CallType.AVOID:
                        if call.current_price < call.price_at_call * 0.9:
                            call.result = "success"
                            kol.successful_calls += 1
                            kol.pending_calls -= 1
                        elif call.current_price > call.price_at_call * 1.1:
                            call.result = "failure"
                            kol.failed_calls += 1
                            kol.pending_calls -= 1
        
        # Recalculate all metrics
        for kol in self.kols.values():
            self._calculate_kol_metrics(kol)
    
    def _calculate_kol_metrics(self, kol: KOLReputation):
        """Calculate all metrics for a KOL."""
        # Accuracy calculations
        if kol.total_calls > 0:
            kol.accuracy_all_time = (kol.successful_calls / kol.total_calls) * 100
        
        # Time-based accuracy
        now = datetime.now()
        
        calls_24h = [c for c in kol.calls if (now - c.called_at).days <= 1]
        calls_7d = [c for c in kol.calls if (now - c.called_at).days <= 7]
        calls_30d = [c for c in kol.calls if (now - c.called_at).days <= 30]
        
        kol.accuracy_24h = self._calculate_accuracy(calls_24h)
        kol.accuracy_7d = self._calculate_accuracy(calls_7d)
        kol.accuracy_30d = self._calculate_accuracy(calls_30d)
        
        # Average returns
        kol.avg_return_24h = self._calculate_avg_return(calls_24h)
        kol.avg_return_7d = self._calculate_avg_return(calls_7d)
        kol.avg_return_30d = self._calculate_avg_return(calls_30d)
        
        # Disclosure rate
        paid_calls = [c for c in kol.calls if c.was_paid]
        if paid_calls:
            disclosed = len([c for c in paid_calls if c.disclosed])
            kol.disclosure_rate = (disclosed / len(paid_calls)) * 100
        
        # Overall score
        kol.overall_score = self._calculate_overall_score(kol)
        kol.tier = self._score_to_tier(kol.overall_score, kol.status)
    
    def _calculate_accuracy(self, calls: List[TokenCall]) -> float:
        """Calculate accuracy percentage for a list of calls."""
        completed = [c for c in calls if c.result != "pending"]
        if not completed:
            return 0.0
        successful = len([c for c in completed if c.result == "success"])
        return (successful / len(completed)) * 100
    
    def _calculate_avg_return(self, calls: List[TokenCall]) -> float:
        """Calculate average return percentage."""
        completed = [c for c in calls if c.result != "pending"]
        if not completed:
            return 0.0
        returns = [c.calculate_performance() for c in completed]
        return sum(returns) / len(returns)
    
    def _calculate_overall_score(self, kol: KOLReputation) -> float:
        """Calculate overall reputation score (0-100)."""
        score = 50.0  # Start neutral
        
        # Performance (40% weight)
        if kol.total_calls > 0:
            performance_score = kol.accuracy_all_time * 0.4
            score += performance_score - 20  # Normalize around 50
        
        # Returns (20% weight)
        if kol.avg_return_30d > 0:
            score += min(kol.avg_return_30d * 0.2, 20)
        elif kol.avg_return_30d < 0:
            score += max(kol.avg_return_30d * 0.2, -20)
        
        # Transparency (20% weight)
        if kol.disclosure_rate >= 90:
            score += 20
        elif kol.disclosure_rate >= 50:
            score += 10
        elif kol.disclosure_rate < 50 and kol.undisclosed_paid_promos > 0:
            score -= 15
        
        # Community trust (20% weight)
        score += (kol.community_trust_score - 50) * 0.2
        
        # Penalties
        score -= kol.rug_associations * 10
        score -= kol.scam_tokens_promoted * 5
        score -= kol.undisclosed_paid_promos * 3
        
        return max(0, min(100, score))
    
    def _score_to_tier(self, score: float, status: KOLStatus) -> str:
        """Convert score to tier."""
        if status == KOLStatus.BLACKLISTED:
            return "blacklisted"
        
        for tier, threshold in sorted(self.TIER_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return tier
        
        return "unranked"
    
    async def get_leaderboard(self, timeframe: str = "all_time", limit: int = 100) -> List[Dict]:
        """Get KOL leaderboard."""
        kols_list = list(self.kols.values())
        
        # Sort by appropriate metric
        if timeframe == "24h":
            kols_list.sort(key=lambda k: k.accuracy_24h, reverse=True)
        elif timeframe == "7d":
            kols_list.sort(key=lambda k: k.accuracy_7d, reverse=True)
        elif timeframe == "30d":
            kols_list.sort(key=lambda k: k.accuracy_30d, reverse=True)
        else:
            kols_list.sort(key=lambda k: k.overall_score, reverse=True)
        
        return [kol.to_dict() for kol in kols_list[:limit]]
    
    async def get_kol_report(self, handle: str) -> Optional[Dict]:
        """Get comprehensive KOL report."""
        kol = self.kols.get(handle)
        if not kol:
            return None
        
        # Get recent calls
        recent_calls = sorted(kol.calls, key=lambda c: c.called_at, reverse=True)[:20]
        
        # Get tokens promoted
        tokens_promoted = defaultdict(lambda: {"calls": 0, "success": 0, "failure": 0})
        for call in kol.calls:
            tokens_promoted[call.token_symbol]["calls"] += 1
            if call.result == "success":
                tokens_promoted[call.token_symbol]["success"] += 1
            elif call.result == "failure":
                tokens_promoted[call.token_symbol]["failure"] += 1
        
        return {
            "kol": kol.to_dict(),
            "recent_calls": [
                {
                    "token": c.token_symbol,
                    "type": c.call_type.value,
                    "date": c.called_at.isoformat(),
                    "result": c.result,
                    "performance": c.calculate_performance(),
                    "was_paid": c.was_paid,
                    "disclosed": c.disclosed
                }
                for c in recent_calls
            ],
            "tokens_promoted": dict(tokens_promoted),
            "verdict": self._generate_kol_verdict(kol)
        }
    
    def _generate_kol_verdict(self, kol: KOLReputation) -> str:
        """Generate verdict on KOL."""
        if kol.status == KOLStatus.BLACKLISTED:
            return "🚫 BLACKLISTED - Known scammer or serial pumper"
        
        if kol.overall_score >= 80:
            return f"✅ HIGHLY TRUSTED - {kol.tier.upper()} tier with strong track record"
        elif kol.overall_score >= 60:
            return f"✅ RELIABLE - {kol.tier.upper()} tier, generally good calls"
        elif kol.overall_score >= 40:
            return f"⚡ MIXED - {kol.tier.upper()} tier, verify independently"
        elif kol.overall_score >= 20:
            return f"⚠️ CAUTION - {kol.tier.upper()} tier, many failed calls"
        else:
            return f"🚨 HIGH RISK - {kol.tier.upper()} tier, likely to lose money"
    
    def blacklist_kol(self, handle: str, reason: str):
        """Blacklist a KOL."""
        kol = self.kols.get(handle)
        if kol:
            kol.status = KOLStatus.BLACKLISTED
            self.blacklist.append(handle)
    
    def verify_kol(self, handle: str):
        """Mark a KOL as verified."""
        kol = self.kols.get(handle)
        if kol:
            kol.status = KOLStatus.VERIFIED
            kol.verification_date = datetime.now()
    
    async def search_kols(self, query: str) -> List[KOLReputation]:
        """Search for KOLs."""
        results = []
        query_lower = query.lower()
        
        for kol in self.kols.values():
            if query_lower in kol.handle.lower():
                results.append(kol)
            elif query_lower in kol.display_name.lower():
                results.append(kol)
        
        return results


# Global instance
_system = None

def get_kol_reputation_system() -> KOLReputationSystem:
    """Get global KOL reputation system."""
    global _system
    if _system is None:
        _system = KOLReputationSystem()
    return _system


if __name__ == "__main__":
    print("=" * 70)
    print("KOL REPUTATION SYSTEM")
    print("=" * 70)
    
    system = get_kol_reputation_system()
    
    print("\n📊 Features:")
    print("  • Track KOL call accuracy")
    print("  • Calculate performance metrics")
    print("  • Community trust scoring")
    print("  • Transparency ratings")
    print("  • Leaderboard system")
    
    print("\n🏆 Tiers:")
    print("  💎 Diamond (90+)   - Elite callers")
    print("  🥇 Platinum (80+)  - Highly trusted")
    print("  🥈 Gold (70+)      - Reliable")
    print("  🥉 Silver (60+)    - Decent")
    print("  🏅 Bronze (50+)    - Average")
    print("  ⚪ Unranked        - New/insufficient data")
    print("  🚫 Blacklisted     - Known scammers")
    
    print("\n" + "=" * 70)
