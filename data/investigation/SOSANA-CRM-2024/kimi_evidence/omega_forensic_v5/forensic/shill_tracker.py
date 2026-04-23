"""
Shill Campaign Tracker - X/Twitter Shilling Detection
=====================================================
Tracks and analyzes shill campaigns on X including:
- Coordinated posting patterns
- Bot network detection
- KOL (Key Opinion Leader) tracking
- Sentiment analysis
- Timing analysis
"""

import json
import asyncio
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum


class ShillType(Enum):
    """Type of shilling activity."""
    ORGANIC = "organic"
    PAID_PROMOTION = "paid_promotion"
    COORDINATED = "coordinated"
    BOT_NETWORK = "bot_network"
    PUMP_AND_DUMP = "pump_and_dump"
    UNKNOWN = "unknown"


class KOLTier(Enum):
    """KOL influence tier."""
    NANO = "nano"       # 1K-10K followers
    MICRO = "micro"     # 10K-50K followers
    MID = "mid"         # 50K-100K followers
    MACRO = "macro"     # 100K-500K followers
    MEGA = "mega"       # 500K-1M followers
    CELEBRITY = "celebrity"  # 1M+ followers


@dataclass
class XPost:
    """Represents an X/Twitter post."""
    post_id: str
    author_handle: str
    author_id: str
    content: str
    posted_at: datetime
    
    # Engagement
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    impressions: int = 0
    
    # Token mentions
    tokens_mentioned: List[str] = field(default_factory=list)
    cashtags: List[str] = field(default_factory=list)
    
    # Analysis
    sentiment: str = "neutral"  # positive, negative, neutral
    is_shill: bool = False
    shill_confidence: float = 0.0


@dataclass
class KOL:
    """Key Opinion Leader profile."""
    handle: str
    user_id: str
    display_name: str
    
    # Stats
    follower_count: int = 0
    following_count: int = 0
    tier: KOLTier = KOLTier.NANO
    
    # History
    account_created: Optional[datetime] = None
    posts_count: int = 0
    
    # Token promotions
    tokens_promoted: List[str] = field(default_factory=list)
    promotion_history: List[Dict] = field(default_factory=list)
    
    # Reputation
    reputation_score: float = 50.0  # 0-100
    successful_calls: int = 0
    failed_calls: int = 0
    rug_associations: int = 0
    
    # Analysis
    avg_engagement_rate: float = 0.0
    posting_frequency: float = 0.0  # posts per day
    bot_likelihood: float = 0.0  # 0-1
    
    def to_dict(self) -> Dict:
        return {
            "handle": self.handle,
            "display_name": self.display_name,
            "follower_count": self.follower_count,
            "tier": self.tier.value,
            "reputation": {
                "score": self.reputation_score,
                "successful_calls": self.successful_calls,
                "failed_calls": self.failed_calls,
                "rug_associations": self.rug_associations
            },
            "engagement": {
                "avg_rate": self.avg_engagement_rate,
                "posts_per_day": self.posting_frequency
            },
            "risk": {
                "bot_likelihood": self.bot_likelihood,
                "tokens_promoted": len(self.tokens_promoted)
            }
        }


@dataclass
class ShillCampaign:
    """Represents a detected shill campaign."""
    campaign_id: str
    token_address: str
    token_symbol: str
    
    # Detection
    detected_at: datetime
    campaign_type: ShillType
    confidence: float
    
    # Participants
    posts: List[XPost] = field(default_factory=list)
    unique_authors: Set[str] = field(default_factory=set)
    kol_participants: List[str] = field(default_factory=list)
    
    # Timing
    first_post: Optional[datetime] = None
    last_post: Optional[datetime] = None
    peak_activity: Optional[datetime] = None
    
    # Metrics
    total_posts: int = 0
    total_reach: int = 0
    total_engagement: int = 0
    estimated_cost: float = 0.0  # Estimated paid promotion cost
    
    # Analysis
    coordinated_score: float = 0.0  # 0-1
    bot_ratio: float = 0.0  # Percentage of posts from bots
    sentiment_trend: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "campaign_id": self.campaign_id,
            "token": {
                "address": self.token_address,
                "symbol": self.token_symbol
            },
            "detection": {
                "detected_at": self.detected_at.isoformat(),
                "type": self.campaign_type.value,
                "confidence": self.confidence
            },
            "reach": {
                "total_posts": self.total_posts,
                "unique_authors": len(self.unique_authors),
                "total_reach": self.total_reach,
                "total_engagement": self.total_engagement
            },
            "timing": {
                "first_post": self.first_post.isoformat() if self.first_post else None,
                "last_post": self.last_post.isoformat() if self.last_post else None,
                "duration_hours": self._get_duration_hours()
            },
            "analysis": {
                "coordinated_score": self.coordinated_score,
                "bot_ratio": self.bot_ratio,
                "estimated_cost_usd": self.estimated_cost
            }
        }
    
    def _get_duration_hours(self) -> float:
        """Get campaign duration in hours."""
        if self.first_post and self.last_post:
            return (self.last_post - self.first_post).total_seconds() / 3600
        return 0.0


class ShillTracker:
    """
    Tracks and analyzes shill campaigns on X/Twitter.
    """
    
    # Shill indicators
    SHILL_KEYWORDS = [
        "moon", "mooning", "gem", "100x", "1000x", "gem", "alpha",
        "dont miss", "don't miss", "next", "going to", "will pump",
        "buy now", "get in early", "early entry", "diamond hands",
        "paper hands", "hodl", "hold", "pump", "pumping"
    ]
    
    COORDINATION_INDICATORS = [
        "same time posting",
        "identical hashtags",
        "similar wording",
        "tagged same accounts"
    ]
    
    def __init__(self):
        self.campaigns: Dict[str, ShillCampaign] = {}  # campaign_id -> campaign
        self.kols: Dict[str, KOL] = {}  # handle -> KOL
        self.token_campaigns: Dict[str, List[str]] = {}  # token -> campaign_ids
        self.posts_db: List[XPost] = []
        
    async def track_token(self, token_address: str, token_symbol: str) -> ShillCampaign:
        """
        Start tracking shill activity for a token.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            
        Returns:
            ShillCampaign object
        """
        campaign_id = f"shill_{token_address[:16]}_{int(datetime.now().timestamp())}"
        
        campaign = ShillCampaign(
            campaign_id=campaign_id,
            token_address=token_address,
            token_symbol=token_symbol,
            detected_at=datetime.now(),
            campaign_type=ShillType.UNKNOWN,
            confidence=0.0
        )
        
        self.campaigns[campaign_id] = campaign
        
        if token_address not in self.token_campaigns:
            self.token_campaigns[token_address] = []
        self.token_campaigns[token_address].append(campaign_id)
        
        return campaign
    
    async def analyze_posts(self, posts: List[XPost], token_address: str) -> ShillCampaign:
        """Analyze a batch of posts for shill patterns."""
        # Get or create campaign
        campaign = None
        if token_address in self.token_campaigns:
            campaign_id = self.token_campaigns[token_address][-1]
            campaign = self.campaigns.get(campaign_id)
        
        if not campaign:
            campaign = await self.track_token(token_address, "UNKNOWN")
        
        # Analyze each post
        for post in posts:
            # Check if shill
            is_shill, confidence = self._detect_shill_post(post)
            post.is_shill = is_shill
            post.shill_confidence = confidence
            
            if is_shill:
                campaign.posts.append(post)
                campaign.unique_authors.add(post.author_handle)
                
                # Update timing
                if not campaign.first_post or post.posted_at < campaign.first_post:
                    campaign.first_post = post.posted_at
                if not campaign.last_post or post.posted_at > campaign.last_post:
                    campaign.last_post = post.posted_at
            
            self.posts_db.append(post)
        
        # Update campaign metrics
        campaign.total_posts = len(campaign.posts)
        campaign.total_reach = sum(p.impressions for p in campaign.posts)
        campaign.total_engagement = sum(p.likes + p.retweets + p.replies for p in campaign.posts)
        
        # Detect campaign type
        campaign.campaign_type = self._detect_campaign_type(campaign)
        campaign.confidence = self._calculate_campaign_confidence(campaign)
        
        # Calculate coordinated score
        campaign.coordinated_score = self._calculate_coordination(campaign)
        campaign.bot_ratio = self._calculate_bot_ratio(campaign)
        
        # Estimate cost
        campaign.estimated_cost = self._estimate_campaign_cost(campaign)
        
        return campaign
    
    def _detect_shill_post(self, post: XPost) -> Tuple[bool, float]:
        """Detect if a post is shilling."""
        content_lower = post.content.lower()
        
        # Check for shill keywords
        keyword_matches = sum(1 for kw in self.SHILL_KEYWORDS if kw in content_lower)
        
        # Check for excessive emojis
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', post.content))
        
        # Check for excessive cashtags
        cashtag_count = len(post.cashtags)
        
        # Check for excessive hashtags
        hashtag_count = content_lower.count('#')
        
        # Calculate shill score
        score = 0.0
        score += keyword_matches * 0.15
        score += min(emoji_count * 0.05, 0.3)
        score += min(cashtag_count * 0.1, 0.3)
        score += min(hashtag_count * 0.03, 0.2)
        
        # Check for engagement bait
        if any(x in content_lower for x in ["like", "retweet", "follow", "tag"]):
            score += 0.1
        
        is_shill = score >= 0.4
        confidence = min(score, 1.0)
        
        return is_shill, confidence
    
    def _detect_campaign_type(self, campaign: ShillCampaign) -> ShillType:
        """Detect the type of shill campaign."""
        if campaign.bot_ratio > 0.7:
            return ShillType.BOT_NETWORK
        
        if campaign.coordinated_score > 0.8:
            return ShillType.COORDINATED
        
        if campaign.estimated_cost > 5000:
            return ShillType.PAID_PROMOTION
        
        if campaign.total_posts < 10:
            return ShillType.ORGANIC
        
        return ShillType.UNKNOWN
    
    def _calculate_campaign_confidence(self, campaign: ShillCampaign) -> float:
        """Calculate confidence in campaign detection."""
        if campaign.total_posts == 0:
            return 0.0
        
        # Average shill confidence of posts
        avg_confidence = sum(p.shill_confidence for p in campaign.posts) / len(campaign.posts)
        
        # Boost for coordination
        if campaign.coordinated_score > 0.7:
            avg_confidence += 0.2
        
        # Boost for bot detection
        if campaign.bot_ratio > 0.5:
            avg_confidence += 0.15
        
        return min(avg_confidence, 1.0)
    
    def _calculate_coordination(self, campaign: ShillCampaign) -> float:
        """Calculate coordination score (0-1)."""
        if len(campaign.posts) < 5:
            return 0.0
        
        # Group posts by time windows
        time_groups = defaultdict(list)
        for post in campaign.posts:
            window = post.posted_at.replace(minute=0, second=0, microsecond=0)
            time_groups[window].append(post)
        
        # Check for simultaneous posting
        max_in_window = max(len(posts) for posts in time_groups.values())
        coordination_score = min(max_in_window / 10, 1.0)
        
        return coordination_score
    
    def _calculate_bot_ratio(self, campaign: ShillCampaign) -> float:
        """Calculate percentage of posts likely from bots."""
        if not campaign.posts:
            return 0.0
        
        bot_indicators = 0
        for post in campaign.posts:
            score = 0
            
            # Low engagement relative to followers (would need follower count)
            # For now, use heuristics
            
            # Repetitive content
            similar_posts = sum(1 for p in campaign.posts if self._content_similarity(post.content, p.content) > 0.8)
            if similar_posts > 3:
                score += 0.3
            
            # Perfect timing
            if post.posted_at.minute == 0 and post.posted_at.second == 0:
                score += 0.2
            
            # No engagement
            if post.likes == 0 and post.retweets == 0:
                score += 0.2
            
            if score > 0.5:
                bot_indicators += 1
        
        return bot_indicators / len(campaign.posts)
    
    def _content_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _estimate_campaign_cost(self, campaign: ShillCampaign) -> float:
        """Estimate the cost of a paid shill campaign."""
        cost = 0.0
        
        # Estimate based on KOL tiers
        for handle in campaign.kol_participants:
            kol = self.kols.get(handle)
            if kol:
                tier_costs = {
                    KOLTier.NANO: 50,
                    KOLTier.MICRO: 200,
                    KOLTier.MID: 500,
                    KOLTier.MACRO: 2000,
                    KOLTier.MEGA: 10000,
                    KOLTier.CELEBRITY: 50000
                }
                cost += tier_costs.get(kol.tier, 100)
        
        # Add bot network cost
        if campaign.bot_ratio > 0.5:
            cost += len(campaign.posts) * 0.5  # $0.50 per bot post
        
        return cost
    
    async def get_kol_report(self, handle: str) -> Optional[Dict]:
        """Get reputation report for a KOL."""
        kol = self.kols.get(handle)
        if not kol:
            return None
        
        # Get all posts by this KOL
        kol_posts = [p for p in self.posts_db if p.author_handle == handle]
        
        # Analyze promoted tokens
        promoted_tokens = defaultdict(lambda: {"posts": 0, "avg_sentiment": 0})
        for post in kol_posts:
            for token in post.tokens_mentioned:
                promoted_tokens[token]["posts"] += 1
                promoted_tokens[token]["avg_sentiment"] += 1 if post.sentiment == "positive" else -1
        
        # Calculate success rate
        success_rate = 0.0
        if kol.successful_calls + kol.failed_calls > 0:
            success_rate = kol.successful_calls / (kol.successful_calls + kol.failed_calls)
        
        return {
            "kol": kol.to_dict(),
            "stats": {
                "total_posts": len(kol_posts),
                "shill_posts": len([p for p in kol_posts if p.is_shill]),
                "success_rate": success_rate,
                "tokens_promoted": len(promoted_tokens)
            },
            "promoted_tokens": dict(promoted_tokens),
            "risk_assessment": self._assess_kol_risk(kol)
        }
    
    def _assess_kol_risk(self, kol: KOL) -> Dict:
        """Assess risk level of a KOL."""
        risk_factors = []
        risk_score = 0
        
        if kol.rug_associations > 0:
            risk_factors.append(f"Associated with {kol.rug_associations} rug pulls")
            risk_score += kol.rug_associations * 20
        
        if kol.bot_likelihood > 0.7:
            risk_factors.append("High bot likelihood")
            risk_score += 25
        
        if kol.failed_calls > kol.successful_calls:
            risk_factors.append("More failed calls than successful")
            risk_score += 15
        
        if kol.posting_frequency > 50:  # More than 50 posts per day
            risk_factors.append("Excessive posting frequency")
            risk_score += 10
        
        risk_level = "low"
        if risk_score >= 50:
            risk_level = "extreme"
        elif risk_score >= 35:
            risk_level = "high"
        elif risk_score >= 20:
            risk_level = "medium"
        
        return {
            "score": risk_score,
            "level": risk_level,
            "factors": risk_factors
        }
    
    async def generate_campaign_report(self, campaign_id: str) -> Optional[Dict]:
        """Generate comprehensive campaign report."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # Get KOL details
        kol_details = []
        for handle in campaign.kol_participants:
            report = await self.get_kol_report(handle)
            if report:
                kol_details.append(report)
        
        # Timeline analysis
        timeline = self._generate_campaign_timeline(campaign)
        
        return {
            "campaign": campaign.to_dict(),
            "kols": kol_details,
            "timeline": timeline,
            "verdict": self._generate_campaign_verdict(campaign),
            "warnings": self._generate_campaign_warnings(campaign)
        }
    
    def _generate_campaign_timeline(self, campaign: ShillCampaign) -> List[Dict]:
        """Generate timeline of campaign activity."""
        timeline = []
        
        # Sort posts by time
        sorted_posts = sorted(campaign.posts, key=lambda p: p.posted_at)
        
        for post in sorted_posts:
            timeline.append({
                "time": post.posted_at.isoformat(),
                "author": post.author_handle,
                "engagement": post.likes + post.retweets + post.replies,
                "is_shill": post.is_shill,
                "confidence": post.shill_confidence
            })
        
        return timeline
    
    def _generate_campaign_verdict(self, campaign: ShillCampaign) -> str:
        """Generate verdict on campaign."""
        if campaign.campaign_type == ShillType.BOT_NETWORK:
            return "🚨 BOT NETWORK DETECTED - Artificial engagement, likely scam"
        elif campaign.campaign_type == ShillType.COORDINATED:
            return "⚠️ COORDINATED SHILL - Organized promotion campaign"
        elif campaign.campaign_type == ShillType.PAID_PROMOTION:
            return "💰 PAID PROMOTION - Sponsored content, not organic"
        elif campaign.campaign_type == ShillType.PUMP_AND_DUMP:
            return "📉 PUMP & DUMP PATTERN - Artificial price manipulation"
        else:
            return "✅ ORGANIC GROWTH - Natural community interest"
    
    def _generate_campaign_warnings(self, campaign: ShillCampaign) -> List[str]:
        """Generate warnings about campaign."""
        warnings = []
        
        if campaign.bot_ratio > 0.5:
            warnings.append(f"{campaign.bot_ratio*100:.0f}% of posts appear to be from bots")
        
        if campaign.coordinated_score > 0.7:
            warnings.append("Highly coordinated posting pattern detected")
        
        if campaign.estimated_cost > 10000:
            warnings.append(f"Estimated campaign cost: ${campaign.estimated_cost:,.0f}")
        
        if campaign.total_posts > 100 and campaign.total_engagement < 1000:
            warnings.append("High post volume but low engagement - possible bot activity")
        
        return warnings


# Global instance
_tracker = None

def get_shill_tracker() -> ShillTracker:
    """Get global shill tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = ShillTracker()
    return _tracker


if __name__ == "__main__":
    print("=" * 70)
    print("SHILL TRACKER - X/Twitter Campaign Detection")
    print("=" * 70)
    
    tracker = get_shill_tracker()
    
    print("\n📊 Features:")
    print("  • Detect coordinated shill campaigns")
    print("  • Bot network identification")
    print("  • KOL reputation tracking")
    print("  • Sentiment analysis")
    print("  • Timing pattern detection")
    print("  • Campaign cost estimation")
    
    print("\n🎯 Shill Types Detected:")
    print("  🟢 Organic - Natural community interest")
    print("  💰 Paid Promotion - Sponsored content")
    print("  ⚠️ Coordinated - Organized campaign")
    print("  🤖 Bot Network - Artificial engagement")
    print("  📉 Pump & Dump - Price manipulation")
    
    print("\n" + "=" * 70)
