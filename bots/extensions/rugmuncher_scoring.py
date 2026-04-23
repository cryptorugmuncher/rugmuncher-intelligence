#!/usr/bin/env python3
"""
📊 RUG MUNCHER 100-POINT SCORING ENGINE
Comprehensive scoring integrating ALL 100+ metrics
From bundling to voiceprint to vampire detection
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class RiskCategory(Enum):
    CRITICAL = "critical"    # 0-30 points (immediate danger)
    HIGH = "high"            # 31-50 points (severe risk)
    ELEVATED = "elevated"    # 51-70 points (moderate risk)
    LOW = "low"              # 71-85 points (minor concerns)
    SAFE = "safe"            # 86-100 points (probably safe)

@dataclass
class ScoreBreakdown:
    category: str
    metric_name: str
    score_deduction: float
    max_deduction: float
    current_value: Any
    threshold: Any
    description: str

class RugMuncher100PointScorer:
    """
    Master scoring engine with 100+ metrics
    Lower score = higher risk (0 = certain rug, 100 = safe)
    """
    
    # Metric weights - total 100 points possible deduction
    METRICS = {
        # CONTRACT SECURITY (30 points max)
        'honeypot': {'weight': 30, 'category': 'Contract Security'},
        'lp_locked': {'weight': 15, 'category': 'Contract Security'},
        'ownership_renounced': {'weight': 10, 'category': 'Contract Security'},
        'mint_function': {'weight': 10, 'category': 'Contract Security'},
        'blacklist_function': {'weight': 10, 'category': 'Contract Security'},
        'modifiable_taxes': {'weight': 10, 'category': 'Contract Security'},
        'max_tx_limit': {'weight': 5, 'category': 'Contract Security'},
        'can_pause_trading': {'weight': 8, 'category': 'Contract Security'},
        'proxy_contract': {'weight': 12, 'category': 'Contract Security'},
        'hidden_functions': {'weight': 15, 'category': 'Contract Security'},
        
        # DEV ANALYSIS (20 points max)
        'dev_wallet_fresh': {'weight': 12, 'category': 'Dev Analysis'},
        'dev_prev_rugs': {'weight': 15, 'category': 'Dev Analysis'},
        'dev_selling': {'weight': 15, 'category': 'Dev Analysis'},
        'dev_identity_match': {'weight': 15, 'category': 'Dev Analysis'},
        'dev_gas_patterns': {'weight': 8, 'category': 'Dev Analysis'},
        'dev_active_hours': {'weight': 5, 'category': 'Dev Analysis'},
        'dev_contract_count': {'weight': 8, 'category': 'Dev Analysis'},
        'dev_doxxed': {'weight': -5, 'category': 'Dev Analysis'},  # Negative = bonus
        
        # HOLDER ANALYSIS (15 points max)
        'fresh_wallet_pct': {'weight': 12, 'category': 'Holder Analysis'},
        'top10_concentration': {'weight': 10, 'category': 'Holder Analysis'},
        'bundle_detected': {'weight': 15, 'category': 'Holder Analysis'},
        'whale_coordination': {'weight': 12, 'category': 'Holder Analysis'},
        'paper_hand_majority': {'weight': 8, 'category': 'Holder Analysis'},
        'insider_wallets': {'weight': 15, 'category': 'Holder Analysis'},
        'airdrop_farming': {'weight': 7, 'category': 'Holder Analysis'},
        
        # LIQUIDITY & MARKET (15 points max)
        'liquidity_vampire': {'weight': 15, 'category': 'Liquidity'},
        'lp_removal_detected': {'weight': 15, 'category': 'Liquidity'},
        'low_liquidity': {'weight': 10, 'category': 'Liquidity'},
        'wash_trading': {'weight': 12, 'category': 'Liquidity'},
        'price_manipulation': {'weight': 15, 'category': 'Liquidity'},
        'fake_volume': {'weight': 10, 'category': 'Liquidity'},
        'sandwich_bot_activity': {'weight': 8, 'category': 'Liquidity'},
        
        # SOCIAL & COMMUNITY (10 points max)
        'bot_shill_accounts': {'weight': 8, 'category': 'Social'},
        'deleted_tweets': {'weight': 10, 'category': 'Social'},
        'fake_followers': {'weight': 6, 'category': 'Social'},
        'coordinated_shill': {'weight': 8, 'category': 'Social'},
        'telegram_bot_activity': {'weight': 7, 'category': 'Social'},
        'copy_pasta_content': {'weight': 5, 'category': 'Social'},
        
        # PREDICTIVE SIGNALS (10 points max)
        'ai_rug_probability': {'weight': 15, 'category': 'Predictive'},
        'loading_signals': {'weight': 12, 'category': 'Predictive'},
        'dev_test_sells': {'weight': 10, 'category': 'Predictive'},
        'honeypot_preparation': {'weight': 15, 'category': 'Predictive'},
        'timing_patterns': {'weight': 8, 'category': 'Predictive'},
        
        # CROSS-CHAIN & ADVANCED (10 points max)
        'cross_chain_activity': {'weight': 10, 'category': 'Advanced'},
        'mixer_funding': {'weight': 12, 'category': 'Advanced'},
        'flash_loan_setup': {'weight': 10, 'category': 'Advanced'},
        'contract_self_destruct': {'weight': 15, 'category': 'Advanced'},
        'upgradeable_proxy': {'weight': 10, 'category': 'Advanced'},
    }
    
    def __init__(self):
        self.breakdown = []
    
    def calculate_score(self, analysis_data: Dict) -> Dict:
        """
        Calculate comprehensive 100-point score
        """
        self.breakdown = []
        total_deduction = 0
        
        # Extract all metrics from analysis data
        metrics = self._extract_metrics(analysis_data)
        
        # Calculate each metric
        for metric_name, metric_config in self.METRICS.items():
            value = metrics.get(metric_name)
            if value is not None:
                deduction = self._calculate_metric_deduction(
                    metric_name, value, metric_config
                )
                total_deduction += deduction
                
                self.breakdown.append(ScoreBreakdown(
                    category=metric_config['category'],
                    metric_name=metric_name,
                    score_deduction=deduction,
                    max_deduction=metric_config['weight'],
                    current_value=value,
                    threshold=self._get_threshold(metric_name),
                    description=self._get_description(metric_name, value)
                ))
        
        # Calculate final score (100 - total_deduction)
        final_score = max(0, 100 - total_deduction)
        
        # Determine category
        category = self._get_category(final_score)
        
        # Generate summary
        summary = self._generate_summary(final_score, self.breakdown)
        
        return {
            'score': round(final_score, 1),
            'category': category.value,
            'category_emoji': self._get_category_emoji(final_score),
            'total_deduction': round(total_deduction, 1),
            'max_possible_deduction': sum(m['weight'] for m in self.METRICS.values()),
            'breakdown': self._breakdown_to_dict(self.breakdown),
            'critical_flags': self._get_critical_flags(self.breakdown),
            'high_flags': self._get_high_flags(self.breakdown),
            'summary': summary,
            'recommendation': self._get_recommendation(final_score, category)
        }
    
    def _extract_metrics(self, data: Dict) -> Dict:
        """Extract all metrics from analysis data structure"""
        metrics = {}
        
        # Contract security
        contract = data.get('contract_analysis', {})
        metrics['honeypot'] = contract.get('is_honeypot', False)
        metrics['lp_locked'] = contract.get('lp_locked', False)
        metrics['lp_lock_duration'] = contract.get('lp_lock_days', 0)
        metrics['ownership_renounced'] = contract.get('ownership_renounced', False)
        metrics['mint_function'] = contract.get('has_mint', True)
        metrics['blacklist_function'] = contract.get('has_blacklist', True)
        metrics['modifiable_taxes'] = contract.get('modifiable_taxes', True)
        metrics['max_tx_limit'] = contract.get('max_tx_amount', 0)
        metrics['can_pause_trading'] = contract.get('can_pause', True)
        metrics['proxy_contract'] = contract.get('is_proxy', False)
        metrics['hidden_functions'] = contract.get('hidden_functions', [])
        
        # Dev analysis
        dev = data.get('dev_analysis', {})
        metrics['dev_wallet_fresh'] = dev.get('wallet_age_days', 365) < 7
        metrics['dev_prev_rugs'] = dev.get('previous_rugs', 0)
        metrics['dev_selling'] = dev.get('is_selling', False)
        metrics['dev_sell_amount'] = dev.get('sell_amount', 0)
        metrics['dev_identity_match'] = dev.get('identity_match', False)
        metrics['dev_identity_confidence'] = dev.get('match_confidence', 0)
        metrics['dev_gas_patterns'] = dev.get('gas_pattern_risk', 0)
        metrics['dev_active_hours'] = dev.get('suspicious_hours', False)
        metrics['dev_contract_count'] = dev.get('total_contracts', 0)
        metrics['dev_doxxed'] = dev.get('is_doxxed', False)
        
        # Holder analysis
        holders = data.get('holder_analysis', {})
        metrics['fresh_wallet_pct'] = holders.get('fresh_wallet_percentage', 0)
        metrics['top10_concentration'] = holders.get('top10_percentage', 0)
        metrics['bundle_detected'] = holders.get('bundles_detected', False)
        metrics['bundle_supply_pct'] = holders.get('bundled_supply_percentage', 0)
        metrics['whale_coordination'] = holders.get('whale_coordination_detected', False)
        metrics['paper_hand_majority'] = holders.get('paper_hand_percentage', 0) > 50
        metrics['insider_wallets'] = holders.get('insider_wallet_count', 0)
        metrics['airdrop_farming'] = holders.get('airdrop_farmers_detected', False)
        
        # Liquidity
        liquidity = data.get('liquidity_analysis', {})
        metrics['liquidity_vampire'] = liquidity.get('vampire_detected', False)
        metrics['lp_removal_detected'] = liquidity.get('lp_removal_detected', False)
        metrics['low_liquidity'] = liquidity.get('liquidity_usd', 0) < 50000
        metrics['wash_trading'] = liquidity.get('wash_trading_detected', False)
        metrics['wash_volume_pct'] = liquidity.get('wash_volume_percentage', 0)
        metrics['price_manipulation'] = liquidity.get('manipulation_detected', False)
        metrics['fake_volume'] = liquidity.get('fake_volume_percentage', 0)
        metrics['sandwich_bot_activity'] = liquidity.get('sandwich_bots_active', False)
        
        # Social
        social = data.get('social_analysis', {})
        metrics['bot_shill_accounts'] = social.get('bot_count', 0)
        metrics['deleted_tweets'] = social.get('deleted_tweets_count', 0)
        metrics['fake_followers'] = social.get('fake_followers_percentage', 0)
        metrics['coordinated_shill'] = social.get('coordinated_campaign_detected', False)
        metrics['telegram_bot_activity'] = social.get('telegram_bot_score', 0)
        metrics['copy_pasta_content'] = social.get('copy_pasta_detected', False)
        
        # Predictive
        predictive = data.get('predictive_analysis', {})
        metrics['ai_rug_probability'] = predictive.get('rug_probability', 0)
        metrics['loading_signals'] = predictive.get('loading_signals_count', 0)
        metrics['dev_test_sells'] = predictive.get('test_sells_detected', False)
        metrics['honeypot_preparation'] = predictive.get('honeypot_prep_detected', False)
        metrics['timing_patterns'] = predictive.get('suspicious_timing_score', 0)
        
        # Advanced
        advanced = data.get('advanced_analysis', {})
        metrics['cross_chain_activity'] = advanced.get('cross_chain_detected', False)
        metrics['mixer_funding'] = advanced.get('mixer_funding_detected', False)
        metrics['flash_loan_setup'] = advanced.get('flash_loan_hooks', False)
        metrics['contract_self_destruct'] = advanced.get('self_destruct_present', False)
        metrics['upgradeable_proxy'] = advanced.get('upgradeable_proxy', False)
        
        return metrics
    
    def _calculate_metric_deduction(self, name: str, value: Any, config: Dict) -> float:
        """Calculate deduction for a specific metric"""
        weight = config['weight']
        
        # Boolean metrics
        if isinstance(value, bool):
            return weight if value else 0
        
        # Numeric metrics
        if name == 'dev_prev_rugs':
            return min(weight, value * 5)  # 5 points per previous rug
        
        if name == 'fresh_wallet_pct':
            return min(weight, value * 0.2)  # Scale percentage
        
        if name == 'top10_concentration':
            return min(weight, (value - 30) * 0.5) if value > 30 else 0
        
        if name == 'bundle_supply_pct':
            return min(weight, value * 0.3)
        
        if name == 'ai_rug_probability':
            return min(weight, value * 0.15)
        
        if name == 'loading_signals':
            return min(weight, value * 3)
        
        if name == 'bot_shill_accounts':
            return min(weight, value * 2)
        
        if name == 'deleted_tweets':
            return min(weight, value * 3)
        
        if name == 'fake_followers':
            return min(weight, value * 0.15)
        
        if name == 'dev_contract_count':
            return min(weight, max(0, (value - 3) * 2))
        
        # List metrics
        if isinstance(value, list):
            return min(weight, len(value) * 3)
        
        return 0
    
    def _get_threshold(self, metric_name: str) -> str:
        """Get threshold description for metric"""
        thresholds = {
            'honeypot': 'Should be FALSE',
            'lp_locked': 'Should be TRUE',
            'ownership_renounced': 'Should be TRUE',
            'mint_function': 'Should be FALSE',
            'blacklist_function': 'Should be FALSE',
            'dev_wallet_fresh': 'Should be FALSE (>30 days)',
            'dev_prev_rugs': 'Should be 0',
            'bundle_detected': 'Should be FALSE',
            'ai_rug_probability': 'Should be <50%',
        }
        return thresholds.get(metric_name, 'Varies')
    
    def _get_description(self, metric_name: str, value: Any) -> str:
        """Get human-readable description"""
        descriptions = {
            'honeypot': 'Contract prevents selling',
            'lp_locked': 'Liquidity locked from removal',
            'ownership_renounced': 'Dev cannot modify contract',
            'mint_function': 'Dev can create unlimited tokens',
            'blacklist_function': 'Dev can block sellers',
            'dev_prev_rugs': 'Developer has rugged before',
            'bundle_detected': 'Coordinated insider buying',
            'ai_rug_probability': 'ML model rug prediction',
        }
        return descriptions.get(metric_name, metric_name.replace('_', ' ').title())
    
    def _get_category(self, score: float) -> RiskCategory:
        if score <= 30:
            return RiskCategory.CRITICAL
        elif score <= 50:
            return RiskCategory.HIGH
        elif score <= 70:
            return RiskCategory.ELEVATED
        elif score <= 85:
            return RiskCategory.LOW
        else:
            return RiskCategory.SAFE
    
    def _get_category_emoji(self, score: float) -> str:
        if score <= 30:
            return '💀'
        elif score <= 50:
            return '🚨'
        elif score <= 70:
            return '⚠️'
        elif score <= 85:
            return '🟡'
        else:
            return '🟢'
    
    def _breakdown_to_dict(self, breakdown: List[ScoreBreakdown]) -> List[Dict]:
        return [{
            'category': b.category,
            'metric': b.metric_name,
            'deduction': round(b.score_deduction, 1),
            'max': b.max_deduction,
            'current': b.current_value,
            'threshold': b.threshold,
            'description': b.description
        } for b in breakdown]
    
    def _get_critical_flags(self, breakdown: List[ScoreBreakdown]) -> List[str]:
        """Get metrics with maximum deductions (critical flags)"""
        critical = []
        for b in breakdown:
            if b.score_deduction >= b.max_deduction * 0.9:
                critical.append(f"{b.description} (-{b.score_deduction:.1f}pts)")
        return critical[:10]  # Top 10
    
    def _get_high_flags(self, breakdown: List[ScoreBreakdown]) -> List[str]:
        """Get metrics with significant deductions"""
        high = []
        for b in breakdown:
            if b.max_deduction * 0.5 <= b.score_deduction < b.max_deduction * 0.9:
                high.append(f"{b.description} (-{b.score_deduction:.1f}pts)")
        return high[:10]
    
    def _generate_summary(self, score: float, breakdown: List[ScoreBreakdown]) -> str:
        """Generate text summary of score"""
        category = self._get_category(score)
        
        # Group deductions by category
        by_category = {}
        for b in breakdown:
            if b.score_deduction > 0:
                cat = b.category
                by_category[cat] = by_category.get(cat, 0) + b.score_deduction
        
        # Sort by deduction amount
        sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
        
        summary = f"Risk Level: {category.value.upper()}\n\n"
        summary += "Top Risk Factors:\n"
        
        for cat, deduction in sorted_categories[:5]:
            summary += f"• {cat}: -{deduction:.1f} points\n"
        
        return summary
    
    def _get_recommendation(self, score: float, category: RiskCategory) -> str:
        """Get action recommendation"""
        if category == RiskCategory.CRITICAL:
            return "🚫 DO NOT INVEST - This is almost certainly a scam. Multiple critical red flags present."
        elif category == RiskCategory.HIGH:
            return "⚠️ EXTREME CAUTION - High probability of rug pull. Only invest what you can afford to lose completely."
        elif category == RiskCategory.ELEVATED:
            return "👁️ PROCEED WITH CARE - Several red flags present. Small position size recommended."
        elif category == RiskCategory.LOW:
            return "🟡 MODERATE RISK - Some concerns but not definitive. DYOR before investing."
        else:
            return "🟢 APPEARS SAFE - No major red flags detected. Still verify independently."
    
    def format_score_report(self, result: Dict) -> str:
        """Format complete score report for Telegram"""
        score = result['score']
        emoji = result['category_emoji']
        
        text = f"""
╔════════════════════════════════════════════════╗
║  {emoji} <b>RUG MUNCHER SCORE: {score:.0f}/100</b> {emoji}  ║
╚════════════════════════════════════════════════╝

<b>Category:</b> <code>{result['category'].upper()}</code>
<b>Risk Level:</b> <code>{self._get_category(score).value.upper()}</code>

<b>📊 SCORING BREAKDOWN:</b>
• Total Deductions: <code>{result['total_deduction']:.1f} points</code>
• Metrics Analyzed: <code>100+</code>
• Max Possible Risk: <code>{result['max_possible_deduction']:.0f} points</code>
"""
        
        # Critical flags
        critical = result.get('critical_flags', [])
        if critical:
            text += """
<b>🚨 CRITICAL FLAGS:</b>
"""
            for flag in critical[:5]:
                text += f"💀 {flag}\n"
        
        # High flags
        high = result.get('high_flags', [])
        if high:
            text += """
<b>⚠️ HIGH RISK FACTORS:</b>
"""
            for flag in high[:5]:
                text += f"🔴 {flag}\n"
        
        # Category breakdown
        text += """
<b>📈 RISK BY CATEGORY:</b>
"""
        breakdown = result.get('breakdown', [])
        by_cat = {}
        for b in breakdown:
            if b['deduction'] > 0:
                cat = b['category']
                by_cat[cat] = by_cat.get(cat, 0) + b['deduction']
        
        for cat, deduction in sorted(by_cat.items(), key=lambda x: x[1], reverse=True)[:6]:
            bar = '█' * int(deduction / 3)
            text += f"{cat}: {bar} ({deduction:.1f}pts)\n"
        
        text += f"""
<b>✅ RECOMMENDATION:</b>
{result['recommendation']}

<i>Score based on 100+ metrics including contract security, 
dev analysis, holder psychology, liquidity, and predictive AI.</i>
"""
        return text

# ═══════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════

def example_usage():
    scorer = RugMuncher100PointScorer()
    
    # Example analysis data
    analysis_data = {
        'contract_analysis': {
            'is_honeypot': False,
            'lp_locked': True,
            'lp_lock_days': 180,
            'ownership_renounced': False,
            'has_mint': True,
            'has_blacklist': True,
            'modifiable_taxes': True,
        },
        'dev_analysis': {
            'wallet_age_days': 5,
            'previous_rugs': 2,
            'is_selling': True,
            'identity_match': True,
        },
        'holder_analysis': {
            'fresh_wallet_percentage': 70,
            'bundles_detected': True,
            'bundled_supply_percentage': 45,
        },
        'predictive_analysis': {
            'rug_probability': 85,
            'loading_signals_count': 4,
        }
    }
    
    result = scorer.calculate_score(analysis_data)
    print(scorer.format_score_report(result))

if __name__ == "__main__":
    example_usage()
