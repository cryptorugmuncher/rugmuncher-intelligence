#!/usr/bin/env python3
"""
🕵️ DEVELOPER PROFILER v1.0
Analyze dev history to determine: pumper, dumper, rugger, or builder?

Categories:
- 🏗️ BUILDER: Long-term projects, steady development, no rugs
- 🎭 PUMP & DUMP: Hype → Peak → Exit, multiple projects same pattern
- ☠️ SERIAL RUGGER: Creates, extracts liquidity, abandons
- 🔄 FLIPPER: Quick launches, sells dev allocation fast
- 🏃 GHOST DEV: Creates project, disappears immediately
- 🎪 MARKETING DEV: Great at hype, terrible at delivery
- 🔒 HODLER DEV: Holds large %, slowly dumps over time
- ⚡ INSTA NUKER: Rugs within hours/days of launch
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class DevType(Enum):
    """Developer archetypes"""
    UNKNOWN = "unknown"
    BUILDER = "builder"              # 🏗️ Legitimate long-term builder
    PUMP_AND_DUMP = "pump_and_dump"  # 🎭 Hype cycle repeater
    SERIAL_RUGGER = "serial_rugger"  # ☠️ Multiple confirmed rugs
    FLIPPER = "flipper"              # 🔄 Quick launch & exit
    GHOST_DEV = "ghost_dev"          # 🏃 Disappears immediately
    MARKETING_DEV = "marketing_dev"  # 🎪 All hype, no substance
    HODLER_DEV = "hodler_dev"        # 🔒 Slow dumper
    INSTA_NUKER = "insta_nuker"      # ⚡ Rugs within 24-72h
    SLOW_RUG = "slow_rug"            # 🐍 Drains over weeks/months
    COPY_PASTER = "copy_paster"      # 📋 Forks others, no originality
    WHALE_DEV = "whale_dev"          # 🐋 Creates to pump their bags


class DevRedFlag(Enum):
    """Individual red flags"""
    PREVIOUS_RUG = "previous_rug"
    RENOUNCED_OWNERSHIP = "renounced_ownership"
    TEAM_ALLOCATION_HIGH = "team_allocation_high"
    INSTANT_LP_REMOVAL = "instant_lp_removal"
    MINT_AUTHORITY = "mint_authority"
    FREEZE_AUTHORITY = "freeze_authority"
    HONEYPOT_CODE = "honeypot_code"
    HIDDEN_OWNER = "hidden_owner"
    PROXY_CONTRACT = "proxy_contract"
    UNAUDITED = "unaudited"
    NO_VERIFIED_SOURCE = "no_verified_source"
    SAME_WALLET_PREVIOUS_RUG = "same_wallet_previous_rug"
    MULTIPLE_PROJECTS_30D = "multiple_projects_30d"
    NO_SOCIAL_PRESENCE = "no_social_presence"
    FAKE_FOLLOWERS = "fake_followers"
    PAID_PROMO_ONLY = "paid_promo_only"
    NO_UTILITY = "no_utility"
    COPY_CONTRACT = "copy_contract"
    LAUNCH_SNIPE = "launch_snipe"
    DEV_WALLET_DUMP = "dev_wallet_dump"


@dataclass
class PreviousProject:
    """Record of a previous project by this dev"""
    token_address: str
    name: str
    launch_date: datetime
    death_date: Optional[datetime] = None
    lifespan_days: float = 0.0
    exit_type: str = ""  # rug, dump, active, abandoned
    max_mcap_usd: float = 0.0
    current_status: str = ""
    liquidity_status: str = ""  # locked, burned, removed, partial
    dev_action: str = ""  # what dev did
    red_flags: List[DevRedFlag] = field(default_factory=list)


@dataclass
class DevProfile:
    """Complete developer profile"""
    # Identity
    dev_wallets: List[str]
    primary_wallet: str
    identified_since: Optional[datetime] = None
    
    # Classification
    dev_type: DevType = DevType.UNKNOWN
    dev_type_confidence: float = 0.0
    secondary_types: List[Tuple[DevType, float]] = field(default_factory=list)
    
    # History
    total_projects: int = 0
    active_projects: int = 0
    rugged_projects: int = 0
    abandoned_projects: int = 0
    successful_projects: int = 0
    previous_projects: List[PreviousProject] = field(default_factory=list)
    
    # Behavior patterns
    avg_project_lifespan_days: float = 0.0
    avg_time_to_rug_days: float = 0.0
    avg_dev_allocation_pct: float = 0.0
    pattern_consistency: float = 0.0  # 0-1, how consistent the pattern
    
    # Current project metrics
    current_project_age_hours: float = 0.0
    current_dev_holding_pct: float = 0.0
    current_liquidity_locked: bool = False
    current_mint_auth: bool = False
    
    # Risk assessment
    overall_risk_score: float = 0.0  # 0-100
    risk_factors: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    
    # Prediction
    estimated_exit_timeline: str = ""
    estimated_exit_probability_7d: float = 0.0
    estimated_exit_probability_30d: float = 0.0
    
    # Summary
    summary: str = ""
    advice: str = ""


class DeveloperProfiler:
    """
    🕵️ Analyze developer history and behavior patterns
    """
    
    def __init__(self):
        self.type_indicators = {
            DevType.SERIAL_RUGGER: {
                'weight': 0,
                'evidence': []
            },
            DevType.PUMP_AND_DUMP: {
                'weight': 0,
                'evidence': []
            },
            DevType.INSTA_NUKER: {
                'weight': 0,
                'evidence': []
            },
            DevType.BUILDER: {
                'weight': 0,
                'evidence': []
            },
            DevType.FLIPPER: {
                'weight': 0,
                'evidence': []
            },
            DevType.HODLER_DEV: {
                'weight': 0,
                'evidence': []
            },
            DevType.GHOST_DEV: {
                'weight': 0,
                'evidence': []
            },
        }
    
    async def profile_developer(
        self,
        dev_wallets: List[str],
        current_token: str,
        project_history: List[Dict],
        on_chain_data: Dict,
        social_data: Dict
    ) -> DevProfile:
        """
        Main profiling function
        """
        if not dev_wallets:
            dev_wallets = ["unknown"]
        
        logger.info(f"Profiling developer: {dev_wallets[0][:10]}...")
        
        profile = DevProfile(
            dev_wallets=dev_wallets,
            primary_wallet=dev_wallets[0] if dev_wallets else "unknown"
        )
        
        # Process project history
        await self._analyze_project_history(profile, project_history)
        
        # Analyze current project
        await self._analyze_current_project(profile, current_token, on_chain_data)
        
        # Check social patterns
        await self._analyze_social_patterns(profile, social_data)
        
        # Determine dev type
        await self._classify_developer(profile)
        
        # Calculate risk
        await self._calculate_risk_score(profile)
        
        # Generate predictions
        await self._generate_predictions(profile)
        
        # Create summary
        profile.summary = self._generate_summary(profile)
        profile.advice = self._generate_advice(profile)
        
        return profile
    
    async def _analyze_project_history(
        self,
        profile: DevProfile,
        project_history: List[Dict]
    ):
        """Analyze all previous projects"""
        projects = []
        
        for proj in project_history:
            prev = PreviousProject(
                token_address=proj.get('address', ''),
                name=proj.get('name', 'Unknown'),
                launch_date=proj.get('launch_date', datetime.now()),
                death_date=proj.get('death_date'),
                lifespan_days=proj.get('lifespan_days', 0),
                exit_type=proj.get('exit_type', 'unknown'),
                max_mcap_usd=proj.get('max_mcap', 0),
                current_status=proj.get('status', 'unknown'),
                liquidity_status=proj.get('liquidity_status', 'unknown'),
                dev_action=proj.get('dev_action', ''),
                red_flags=[DevRedFlag(f) for f in proj.get('red_flags', [])]
            )
            projects.append(prev)
        
        profile.previous_projects = projects
        profile.total_projects = len(projects)
        
        # Calculate statistics
        if projects:
            lifespans = [p.lifespan_days for p in projects if p.lifespan_days > 0]
            profile.avg_project_lifespan_days = sum(lifespans) / len(lifespans) if lifespans else 0
            
            rugged = [p for p in projects if p.exit_type in ['rug', 'soft_rug']]
            profile.rugged_projects = len(rugged)
            
            abandoned = [p for p in projects if p.exit_type == 'abandoned']
            profile.abandoned_projects = len(abandoned)
            
            active = [p for p in projects if p.current_status == 'active']
            profile.active_projects = len(active)
            
            successful = [p for p in projects if p.max_mcap_usd > 1000000 and p.lifespan_days > 30]
            profile.successful_projects = len(successful)
            
            # Time to rug
            rug_times = [p.lifespan_days for p in rugged if p.lifespan_days > 0]
            profile.avg_time_to_rug_days = sum(rug_times) / len(rug_times) if rug_times else 0
    
    async def _analyze_current_project(
        self,
        profile: DevProfile,
        token: str,
        on_chain_data: Dict
    ):
        """Analyze current project metrics"""
        profile.current_project_age_hours = on_chain_data.get('age_hours', 0)
        profile.current_dev_holding_pct = on_chain_data.get('dev_holding_pct', 0)
        profile.current_liquidity_locked = on_chain_data.get('liquidity_locked', False)
        profile.current_mint_auth = on_chain_data.get('mint_authority', False)
        
        # Track dev type indicators
        if profile.current_dev_holding_pct > 20:
            self.type_indicators[DevType.HODLER_DEV]['weight'] += 20
            self.type_indicators[DevType.HODLER_DEV]['evidence'].append(
                f"Dev holds {profile.current_dev_holding_pct:.1f}% supply"
            )
        
        if profile.current_mint_auth:
            self.type_indicators[DevType.SERIAL_RUGGER]['weight'] += 15
            self.type_indicators[DevType.SERIAL_RUGGER]['evidence'].append(
                "Retained mint authority (can infinite mint)"
            )
        
        if not profile.current_liquidity_locked:
            self.type_indicators[DevType.INSTA_NUKER]['weight'] += 10
            self.type_indicators[DevType.SERIAL_RUGGER]['weight'] += 10
    
    async def _analyze_social_patterns(
        self,
        profile: DevProfile,
        social_data: Dict
    ):
        """Analyze social media patterns"""
        
        # Check for ghost dev pattern
        if social_data.get('twitter_posts', 0) < 5 and profile.current_project_age_hours > 48:
            self.type_indicators[DevType.GHOST_DEV]['weight'] += 25
            self.type_indicators[DevType.GHOST_DEV]['evidence'].append(
                f"Only {social_data.get('twitter_posts', 0)} posts in {profile.current_project_age_hours:.0f} hours"
            )
        
        # Check for marketing dev
        if social_data.get('paid_promos', 0) > 10 and social_data.get('utility_announced', False) is False:
            self.type_indicators[DevType.MARKETING_DEV]['weight'] += 20
            self.type_indicators[DevType.MARKETING_DEV]['evidence'].append(
                f"{social_data.get('paid_promos', 0)} paid promos, no utility"
            )
        
        # Fake followers
        if social_data.get('follower_growth_rate', 0) > 1000:  # >1000 per day
            self.type_indicators[DevType.PUMP_AND_DUMP]['weight'] += 15
            self.type_indicators[DevType.PUMP_AND_DUMP]['evidence'].append(
                "Suspicious follower growth (likely bought)"
            )
    
    async def _classify_developer(self, profile: DevProfile):
        """Determine developer type based on all evidence"""
        
        # Score each type based on history
        
        # Serial Rugger indicators
        if profile.rugged_projects >= 2:
            self.type_indicators[DevType.SERIAL_RUGGER]['weight'] += 50 * profile.rugged_projects
            self.type_indicators[DevType.SERIAL_RUGGER]['evidence'].append(
                f"{profile.rugged_projects} confirmed previous rugs"
            )
        
        # Insta Nuker
        if profile.avg_time_to_rug_days < 7 and profile.rugged_projects > 0:
            self.type_indicators[DevType.INSTA_NUKER]['weight'] += 40
            self.type_indicators[DevType.INSTA_NUKER]['evidence'].append(
                f"Averages {profile.avg_time_to_rug_days:.1f} days to rug"
            )
        
        # Flipper
        if profile.avg_project_lifespan_days < 14 and profile.total_projects > 2:
            self.type_indicators[DevType.FLIPPER]['weight'] += 35
            self.type_indicators[DevType.FLIPPER]['evidence'].append(
                f"Projects last avg {profile.avg_project_lifespan_days:.1f} days"
            )
        
        # Pump & Dump
        if profile.successful_projects > 0 and profile.rugged_projects > 0:
            self.type_indicators[DevType.PUMP_AND_DUMP]['weight'] += 30
            self.type_indicators[DevType.PUMP_AND_DUMP]['evidence'].append(
                "Pattern: Pump projects then abandon"
            )
        
        # Builder (positive indicators)
        if profile.successful_projects > 0 and profile.rugged_projects == 0:
            self.type_indicators[DevType.BUILDER]['weight'] += 50
            self.type_indicators[DevType.BUILDER]['evidence'].append(
                f"{profile.successful_projects} successful long-term projects, no rugs"
            )
        
        if profile.active_projects > 0 and profile.avg_project_lifespan_days > 90:
            self.type_indicators[DevType.BUILDER]['weight'] += 25
            self.type_indicators[DevType.BUILDER]['evidence'].append(
                f"Maintains projects for {profile.avg_project_lifespan_days:.0f}+ days"
            )
        
        # Determine primary type
        sorted_types = sorted(
            self.type_indicators.items(),
            key=lambda x: x[1]['weight'],
            reverse=True
        )
        
        if sorted_types:
            primary_type, data = sorted_types[0]
            profile.dev_type = primary_type
            profile.dev_type_confidence = min(1.0, data['weight'] / 100)
            
            # Secondary types
            profile.secondary_types = [
                (t, min(1.0, d['weight'] / 100))
                for t, d in sorted_types[1:3]
                if d['weight'] > 10
            ]
        
        # Collect all red flags
        for data in self.type_indicators.values():
            profile.red_flags.extend(data['evidence'])
    
    async def _calculate_risk_score(self, profile: DevProfile):
        """Calculate overall risk score 0-100"""
        score = 0
        
        # Previous rugs (highest weight)
        score += min(50, profile.rugged_projects * 20)
        
        # Short lifespans
        if profile.avg_project_lifespan_days < 7:
            score += 20
        elif profile.avg_project_lifespan_days < 30:
            score += 10
        
        # Current project red flags
        if profile.current_mint_auth:
            score += 15
        if not profile.current_liquidity_locked:
            score += 10
        if profile.current_dev_holding_pct > 30:
            score += 10
        if profile.current_project_age_hours < 24 and profile.total_projects > 2:
            score += 15  # Experienced dev with new project
        
        # Social red flags
        if profile.dev_type in [DevType.GHOST_DEV, DevType.INSTA_NUKER]:
            score += 15
        
        profile.overall_risk_score = min(100, score)
        
        # Risk factors
        if profile.rugged_projects > 0:
            profile.risk_factors.append(f"Has rugged {profile.rugged_projects} previous project(s)")
        if profile.avg_time_to_rug_days < 7:
            profile.risk_factors.append(f"Fast rugs: avg {profile.avg_time_to_rug_days:.1f} days")
        if profile.current_mint_auth:
            profile.risk_factors.append("Can mint unlimited tokens")
        if profile.total_projects > 5:
            profile.risk_factors.append(f"Prolific launcher ({profile.total_projects} projects)")
    
    async def _generate_predictions(self, profile: DevProfile):
        """Predict likely exit behavior"""
        
        # Exit timeline
        if profile.dev_type == DevType.INSTA_NUKER:
            profile.estimated_exit_timeline = "24-72 hours"
            profile.estimated_exit_probability_7d = 0.9
            profile.estimated_exit_probability_30d = 0.95
        elif profile.dev_type == DevType.PUMP_AND_DUMP:
            profile.estimated_exit_timeline = "1-2 weeks (after peak hype)"
            profile.estimated_exit_probability_7d = 0.4
            profile.estimated_exit_probability_30d = 0.8
        elif profile.dev_type == DevType.HODLER_DEV:
            profile.estimated_exit_timeline = "Gradual over months"
            profile.estimated_exit_probability_7d = 0.1
            profile.estimated_exit_probability_30d = 0.3
        elif profile.dev_type == DevType.SERIAL_RUGGER:
            profile.estimated_exit_timeline = "Any moment"
            profile.estimated_exit_probability_7d = 0.7
            profile.estimated_exit_probability_30d = 0.9
        elif profile.dev_type == DevType.BUILDER:
            profile.estimated_exit_timeline = "No exit expected"
            profile.estimated_exit_probability_7d = 0.05
            profile.estimated_exit_probability_30d = 0.1
        else:
            profile.estimated_exit_timeline = "Unknown - watch closely"
            profile.estimated_exit_probability_7d = 0.3
            profile.estimated_exit_probability_30d = 0.5
    
    def _generate_summary(self, profile: DevProfile) -> str:
        """Generate human-readable summary"""
        
        type_emoji = {
            DevType.BUILDER: "🏗️",
            DevType.PUMP_AND_DUMP: "🎭",
            DevType.SERIAL_RUGGER: "☠️",
            DevType.INSTA_NUKER: "⚡",
            DevType.FLIPPER: "🔄",
            DevType.GHOST_DEV: "🏃",
            DevType.HODLER_DEV: "🔒",
            DevType.MARKETING_DEV: "🎪",
            DevType.UNKNOWN: "❓"
        }
        
        emoji = type_emoji.get(profile.dev_type, "❓")
        confidence_pct = profile.dev_type_confidence * 100
        
        lines = [
            f"{emoji} DEVELOPER TYPE: {profile.dev_type.value.upper()}",
            f"   Confidence: {confidence_pct:.0f}%",
            f"",
            f"📊 HISTORY:",
            f"   Total Projects: {profile.total_projects}",
            f"   Rugged: {profile.rugged_projects} | Active: {profile.active_projects} | Successful: {profile.successful_projects}",
            f"   Avg Lifespan: {profile.avg_project_lifespan_days:.1f} days",
        ]
        
        if profile.rugged_projects > 0:
            lines.append(f"   Avg Time to Rug: {profile.avg_time_to_rug_days:.1f} days")
        
        lines.extend([
            f"",
            f"🎯 CURRENT PROJECT:",
            f"   Age: {profile.current_project_age_hours:.1f} hours",
            f"   Dev Holdings: {profile.current_dev_holding_pct:.1f}%",
            f"   Liquidity Locked: {'✅' if profile.current_liquidity_locked else '❌'}",
            f"",
            f"⚠️  RISK SCORE: {profile.overall_risk_score}/100",
        ])
        
        return "\n".join(lines)
    
    def _generate_advice(self, profile: DevProfile) -> str:
        """Generate trading advice based on profile"""
        
        if profile.dev_type == DevType.SERIAL_RUGGER:
            return "☠️ AVOID COMPLETELY. This dev has a confirmed history of rugs. DO NOT INVEST."
        
        elif profile.dev_type == DevType.INSTA_NUKER:
            return "⚠️ EXTREME RISK. If already in, take profits NOW. If not in, AVOID."
        
        elif profile.dev_type == DevType.PUMP_AND_DUMP:
            return "🎭 SHORT-TERM ONLY. Ride the pump but exit before the inevitable dump. Set tight stops."
        
        elif profile.dev_type == DevType.HODLER_DEV:
            return "🔒 CAUTION - WHALE DEV. Can dump on you anytime. Watch wallet movements closely."
        
        elif profile.dev_type == DevType.BUILDER:
            return "🏗️ RELATIVELY SAFE. Legitimate builder with track record. Still DYOR and manage risk."
        
        elif profile.dev_type == DevType.GHOST_DEV:
            return "🏃 HIGH RISK. Dev already disappeared. Community might pump it, but no support."
        
        elif profile.dev_type == DevType.FLIPPER:
            return "🔄 QUICK FLIP ONLY. Dev moves fast. Get in, get out, don't hold."
        
        else:
            return "❓ UNKNOWN TYPE. Watch for 24-48h before investing. Check for red flags."


def format_dev_report(profile: DevProfile) -> str:
    """Format profile as full report"""
    
    lines = [
        "=" * 70,
        "🕵️  DEVELOPER PROFILER REPORT",
        "=" * 70,
        "",
        profile.summary,
        "",
        "-" * 70,
        "📋 PROJECT HISTORY:",
        "-" * 70,
    ]
    
    for proj in profile.previous_projects[:5]:  # Show last 5
        status_emoji = {
            'rug': '☠️',
            'active': '✅',
            'abandoned': '🏃',
            'exit': '🚪'
        }.get(proj.exit_type, '❓')
        
        lines.append(f"{status_emoji} {proj.name[:30]:30} | {proj.lifespan_days:.0f}d | {proj.exit_type}")
        lines.append(f"   Max MCAP: ${proj.max_mcap_usd:,.0f} | {len(proj.red_flags)} red flags")
    
    if profile.red_flags:
        lines.extend([
            "",
            "-" * 70,
            "🚩 RED FLAGS:",
            "-" * 70,
        ])
        for flag in profile.red_flags[:10]:
            lines.append(f"  • {flag}")
    
    if profile.risk_factors:
        lines.extend([
            "",
            "-" * 70,
            "⚠️  RISK FACTORS:",
            "-" * 70,
        ])
        for factor in profile.risk_factors:
            lines.append(f"  • {factor}")
    
    lines.extend([
        "",
        "-" * 70,
        "🔮 PREDICTIONS:",
        "-" * 70,
        f"Exit Timeline: {profile.estimated_exit_timeline}",
        f"Exit Probability (7d): {profile.estimated_exit_probability_7d:.0%}",
        f"Exit Probability (30d): {profile.estimated_exit_probability_30d:.0%}",
        "",
        "=" * 70,
        "💡 ADVICE:",
        f"{profile.advice}",
        "=" * 70,
    ])
    
    return "\n".join(lines)


# Convenience function
async def profile_dev(
    dev_wallets: List[str],
    current_token: str = "",
    project_history: List[Dict] = None,
    on_chain_data: Dict = None,
    social_data: Dict = None
) -> DevProfile:
    """Quick dev profiling"""
    profiler = DeveloperProfiler()
    
    return await profiler.profile_developer(
        dev_wallets=dev_wallets,
        current_token=current_token,
        project_history=project_history or [],
        on_chain_data=on_chain_data or {},
        social_data=social_data or {}
    )


# Demo
if __name__ == "__main__":
    # Example: Serial rugger dev
    sample_history = [
        {
            'address': 'token1',
            'name': 'MoonShot Inu',
            'launch_date': datetime.now() - timedelta(days=60),
            'lifespan_days': 3,
            'exit_type': 'rug',
            'max_mcap': 500000,
            'red_flags': ['previous_rug', 'mint_authority']
        },
        {
            'address': 'token2',
            'name': 'SafeRocket',
            'launch_date': datetime.now() - timedelta(days=30),
            'lifespan_days': 2,
            'exit_type': 'rug',
            'max_mcap': 300000,
            'red_flags': ['previous_rug', 'instant_lp_removal']
        },
        {
            'address': 'token3',
            'name': 'ElonDoge',
            'launch_date': datetime.now() - timedelta(days=5),
            'lifespan_days': 1,
            'exit_type': 'rug',
            'max_mcap': 800000,
            'red_flags': ['previous_rug', 'honeypot_code']
        }
    ]
    
    async def demo():
        profile = await profile_dev(
            dev_wallets=["DeVaBc123..."],
            current_token="NewToken123",
            project_history=sample_history,
            on_chain_data={
                'age_hours': 6,
                'dev_holding_pct': 25,
                'liquidity_locked': False,
                'mint_authority': True
            },
            social_data={
                'twitter_posts': 2,
                'paid_promos': 5,
                'follower_growth_rate': 2000
            }
        )
        
        print(format_dev_report(profile))
    
    asyncio.run(demo())
