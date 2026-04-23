#!/usr/bin/env python3
"""
🔬 COMPREHENSIVE TOKEN ANALYZER
Brings together all detection modules for complete token assessment
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from bundle_detector_advanced import AdvancedBundleDetector, BundleAnalysis
from dev_profiler import DeveloperProfiler, DevProfile

logger = logging.getLogger(__name__)


class TokenVerdict(Enum):
    SAFE = "safe"                    # ✅ Low risk, likely legitimate
    CAUTION = "caution"              # ⚠️ Some concerns, manageable risk
    DANGER = "danger"                # 🚨 High risk, multiple red flags
    SCAM = "scam"                    # ☠️ Confirmed scam, avoid completely


@dataclass
class TokenAnalysis:
    """Complete token analysis combining all modules"""
    
    # Token info
    token_address: str
    token_name: str = ""
    chain: str = "solana"
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    # Component analyses
    bundle_analysis: Optional[BundleAnalysis] = None
    dev_profile: Optional[DevProfile] = None
    
    # Scores
    overall_score: float = 0.0  # 0-100 (100 = perfect)
    safety_rating: str = "UNKNOWN"
    verdict: TokenVerdict = TokenVerdict.CAUTION
    
    # Metrics
    bundle_risk: float = 0.0  # 0-100
    dev_risk: float = 0.0  # 0-100
    contract_risk: float = 0.0  # 0-100
    liquidity_risk: float = 0.0  # 0-100
    
    # Composite factors
    risk_factors: List[str] = field(default_factory=list)
    positive_factors: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    
    # Trading recommendations
    entry_recommendation: str = ""
    exit_strategy: str = ""
    position_size: str = ""  # small, medium, large, none
    hold_time: str = ""  # scalp, swing, long-term, avoid
    
    # Summary
    executive_summary: str = ""
    detailed_report: str = ""


class ComprehensiveTokenAnalyzer:
    """
    🔬 Master analyzer combining all detection modules
    """
    
    def __init__(self):
        self.bundle_detector = AdvancedBundleDetector()
        self.dev_profiler = DeveloperProfiler()
    
    async def analyze_token(
        self,
        token_address: str,
        token_data: Dict,
        transactions: List[Dict],
        wallets: List[Dict],
        dev_wallets: List[str],
        project_history: List[Dict],
        on_chain_data: Dict,
        social_data: Dict
    ) -> TokenAnalysis:
        """
        Run complete token analysis using all modules
        """
        logger.info(f"Starting comprehensive analysis of {token_address}")
        
        analysis = TokenAnalysis(
            token_address=token_address,
            token_name=token_data.get('name', 'Unknown')
        )
        
        # Run all analyses concurrently
        bundle_task = self.bundle_detector.analyze_token(
            token_address, transactions, wallets, on_chain_data
        )
        
        dev_task = self.dev_profiler.profile_developer(
            dev_wallets, token_address, project_history, on_chain_data, social_data
        )
        
        analysis.bundle_analysis, analysis.dev_profile = await asyncio.gather(
            bundle_task, dev_task
        )
        
        # Calculate composite scores
        await self._calculate_scores(analysis)
        
        # Determine verdict
        await self._determine_verdict(analysis)
        
        # Generate recommendations
        await self._generate_recommendations(analysis)
        
        # Create summary
        analysis.executive_summary = self._create_executive_summary(analysis)
        analysis.detailed_report = self._create_detailed_report(analysis)
        
        return analysis
    
    async def _calculate_scores(self, analysis: TokenAnalysis):
        """Calculate all risk scores"""
        
        # Bundle risk (0-100)
        if analysis.bundle_analysis:
            analysis.bundle_risk = analysis.bundle_analysis.bundle_probability
        
        # Dev risk (0-100)
        if analysis.dev_profile:
            analysis.dev_risk = analysis.dev_profile.overall_risk_score
        
        # Contract risk (basic checks)
        contract_data = analysis.dev_profile.current_mint_auth if analysis.dev_profile else False
        if contract_data:
            analysis.contract_risk += 30  # Mint authority = high risk
        
        # Liquidity risk
        if analysis.dev_profile and not analysis.dev_profile.current_liquidity_locked:
            analysis.liquidity_risk += 40
        
        # Overall score (inverse of risk)
        max_risk = max(analysis.bundle_risk, analysis.dev_risk, 
                       analysis.contract_risk, analysis.liquidity_risk)
        analysis.overall_score = max(0, 100 - max_risk)
    
    async def _determine_verdict(self, analysis: TokenAnalysis):
        """Determine final verdict"""
        
        # Collect all red flags
        if analysis.bundle_analysis:
            analysis.red_flags.extend(analysis.bundle_analysis.red_flags)
            analysis.risk_factors.extend(analysis.bundle_analysis.risk_factors)
        
        if analysis.dev_profile:
            analysis.red_flags.extend(analysis.dev_profile.red_flags)
            analysis.risk_factors.extend(analysis.dev_profile.risk_factors)
        
        # Determine verdict based on scores
        if analysis.dev_risk >= 80 or analysis.bundle_risk >= 90:
            analysis.verdict = TokenVerdict.SCAM
            analysis.safety_rating = "☠️ CONFIRMED SCAM"
        elif analysis.dev_risk >= 60 or analysis.bundle_risk >= 70 or analysis.overall_score < 30:
            analysis.verdict = TokenVerdict.DANGER
            analysis.safety_rating = "🚨 HIGH RISK"
        elif analysis.dev_risk >= 40 or analysis.bundle_risk >= 50 or analysis.overall_score < 60:
            analysis.verdict = TokenVerdict.CAUTION
            analysis.safety_rating = "⚠️ MODERATE RISK"
        else:
            analysis.verdict = TokenVerdict.SAFE
            analysis.safety_rating = "✅ RELATIVELY SAFE"
        
        # Positive factors
        if analysis.dev_profile and analysis.dev_profile.dev_type.value == "builder":
            analysis.positive_factors.append("Experienced builder with good track record")
        
        if analysis.bundle_analysis and analysis.bundle_analysis.bundle_probability < 30:
            analysis.positive_factors.append("Low bundling probability")
        
        if analysis.dev_profile and analysis.dev_profile.current_liquidity_locked:
            analysis.positive_factors.append("Liquidity is locked")
    
    async def _generate_recommendations(self, analysis: TokenAnalysis):
        """Generate trading recommendations"""
        
        # Position size
        if analysis.verdict == TokenVerdict.SCAM:
            analysis.position_size = "NONE - AVOID"
        elif analysis.verdict == TokenVerdict.DANGER:
            analysis.position_size = "MINIMAL (1-2% of portfolio max)"
        elif analysis.verdict == TokenVerdict.CAUTION:
            analysis.position_size = "SMALL (3-5% max)"
        else:
            analysis.position_size = "NORMAL (up to 10%)"
        
        # Hold time
        if analysis.dev_profile and analysis.dev_profile.dev_type.value in ["insta_nuker", "serial_rugger"]:
            analysis.hold_time = "SCALP - Exit within hours"
        elif analysis.verdict == TokenVerdict.DANGER:
            analysis.hold_time = "SHORT - Days only, tight stops"
        elif analysis.verdict == TokenVerdict.CAUTION:
            analysis.hold_time = "SWING - Weeks, monitor closely"
        else:
            analysis.hold_time = "LONG-TERM - Can hold"
        
        # Entry recommendation
        if analysis.verdict == TokenVerdict.SCAM:
            analysis.entry_recommendation = "DO NOT ENTER"
        elif analysis.bundle_analysis and analysis.bundle_analysis.is_bundle:
            analysis.entry_recommendation = "Wait for initial dump, enter very low if at all"
        elif analysis.dev_profile and analysis.dev_profile.dev_type.value == "pump_and_dump":
            analysis.entry_recommendation = "Enter on dip, ride pump, exit before peak"
        else:
            analysis.entry_recommendation = "Can enter at current levels"
        
        # Exit strategy
        if analysis.dev_profile:
            timeline = analysis.dev_profile.estimated_exit_timeline
            if timeline:
                analysis.exit_strategy = f"Exit before: {timeline}"
        
        if not analysis.exit_strategy:
            if analysis.verdict == TokenVerdict.CAUTION:
                analysis.exit_strategy = "Take profits at 2x, 5x, 10x. Don't get greedy."
            elif analysis.verdict == TokenVerdict.DANGER:
                analysis.exit_strategy = "Take quick profits. Any green is good green."
    
    def _create_executive_summary(self, analysis: TokenAnalysis) -> str:
        """Create one-paragraph executive summary"""
        
        parts = [
            f"**{analysis.token_name}** ({analysis.token_address[:10]}...)",
            f"Verdict: {analysis.safety_rating}",
            f"Overall Score: {analysis.overall_score:.0f}/100",
        ]
        
        # Add key concerns
        if analysis.bundle_analysis and analysis.bundle_analysis.is_bundle:
            parts.append(f"⚠️ BUNDLED ({analysis.bundle_analysis.bundle_probability:.0f}% probability)")
        
        if analysis.dev_profile:
            parts.append(f"Dev Type: {analysis.dev_profile.dev_type.value.upper()}")
        
        # Key recommendation
        parts.append(f"Recommendation: {analysis.position_size}")
        
        return " | ".join(parts)
    
    def _create_detailed_report(self, analysis: TokenAnalysis) -> str:
        """Create full detailed report"""
        # This would combine all the detailed reports from sub-modules
        return "Full detailed report available in component analyses"


def format_comprehensive_report(analysis: TokenAnalysis) -> str:
    """Format complete analysis as report"""
    
    lines = [
        "=" * 80,
        "🔬 COMPREHENSIVE TOKEN ANALYSIS REPORT",
        "=" * 80,
        "",
        f"Token: {analysis.token_name}",
        f"Address: {analysis.token_address}",
        f"Analysis Time: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "=" * 80,
        "📊 OVERALL ASSESSMENT",
        "=" * 80,
        f"",
        f"Safety Rating: {analysis.safety_rating}",
        f"Overall Score: {analysis.overall_score:.0f}/100",
        f"",
        f"Risk Breakdown:",
        f"  • Bundle Risk: {analysis.bundle_risk:.0f}/100",
        f"  • Developer Risk: {analysis.dev_risk:.0f}/100",
        f"  • Contract Risk: {analysis.contract_risk:.0f}/100",
        f"  • Liquidity Risk: {analysis.liquidity_risk:.0f}/100",
        "",
        "=" * 80,
        "💰 TRADING RECOMMENDATIONS",
        "=" * 80,
        f"",
        f"Position Size: {analysis.position_size}",
        f"Hold Time: {analysis.hold_time}",
        f"Entry: {analysis.entry_recommendation}",
        f"Exit Strategy: {analysis.exit_strategy}",
        "",
    ]
    
    if analysis.positive_factors:
        lines.extend([
            "=" * 80,
            "✅ POSITIVE FACTORS",
            "=" * 80,
            "",
        ])
        for factor in analysis.positive_factors:
            lines.append(f"  • {factor}")
        lines.append("")
    
    if analysis.risk_factors:
        lines.extend([
            "=" * 80,
            "⚠️  RISK FACTORS",
            "=" * 80,
            "",
        ])
        for factor in analysis.risk_factors[:10]:
            lines.append(f"  • {factor}")
        lines.append("")
    
    if analysis.red_flags:
        lines.extend([
            "=" * 80,
            "🚩 RED FLAGS",
            "=" * 80,
            "",
        ])
        for flag in analysis.red_flags[:10]:
            lines.append(f"  • {flag}")
        lines.append("")
    
    lines.extend([
        "=" * 80,
        "📝 EXECUTIVE SUMMARY",
        "=" * 80,
        f"",
        analysis.executive_summary,
        f"",
        "=" * 80,
    ])
    
    return "\n".join(lines)


# Quick analyze function
async def quick_analyze(
    token_address: str,
    token_name: str = "Unknown"
) -> TokenAnalysis:
    """Quick analysis with sample data"""
    analyzer = ComprehensiveTokenAnalyzer()
    
    # Sample data for demo
    return await analyzer.analyze_token(
        token_address=token_address,
        token_data={"name": token_name},
        transactions=[],
        wallets=[],
        dev_wallets=["dev1"],
        project_history=[],
        on_chain_data={"age_hours": 24},
        social_data={}
    )


if __name__ == "__main__":
    async def demo():
        analysis = await quick_analyze(
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "Test Token"
        )
        print(format_comprehensive_report(analysis))
    
    asyncio.run(demo())
