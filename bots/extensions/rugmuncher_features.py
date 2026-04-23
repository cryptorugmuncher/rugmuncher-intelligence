#!/usr/bin/env python3
"""
🚀 RUG MUNCHER FEATURES INTEGRATION
Master module integrating all 5 game-changing features:
1. Rug Predictor AI
2. Paper Hands vs Diamond Hands
3. Liquidity Vampire Detector
4. Dev Voiceprint
5. Auto-Rug Protection
"""

import asyncio
from typing import Dict, List, Optional

# Import all feature modules
from rugmuncher_predictor import RugPredictorEngine, seed_training_data
from rugmuncher_holders import HolderPsychologyAnalyzer, TokenHolderAnalysis
from rugmuncher_vampire import LiquidityVampireDetector
from rugmuncher_voiceprint import DevVoiceprintAnalyzer
from rugmuncher_protector import AutoProtectorEngine

class RugMuncherFeatures:
    """
    Master controller for all advanced features
    """
    
    def __init__(self):
        # Initialize all engines
        self.predictor = RugPredictorEngine()
        self.holder_analyzer = HolderPsychologyAnalyzer()
        self.token_holder_analysis = TokenHolderAnalysis()
        self.vampire_detector = LiquidityVampireDetector()
        self.voiceprint_analyzer = DevVoiceprintAnalyzer()
        self.protector = AutoProtectorEngine()
        
        self.initialized = False
    
    async def start(self):
        """Start all feature engines"""
        await self.predictor.start()
        await self.vampire_detector.start()
        await self.voiceprint_analyzer.start()
        await self.protector.start()
        
        # Seed training data if needed
        seed_training_data()
        
        self.initialized = True
        print("[Features] All 5 game-changing features initialized!")
    
    async def stop(self):
        """Stop all engines"""
        await self.predictor.stop()
        await self.vampire_detector.stop()
        await self.voiceprint_analyzer.stop()
        await self.protector.stop()
    
    async def full_analysis(self, contract: str, chain: str, 
                            contract_data: Dict) -> Dict:
        """
        Run ALL 5 analyses on a contract
        Returns comprehensive report
        """
        if not self.initialized:
            await self.start()
        
        results = {
            'contract': contract,
            'chain': chain,
            'analyses': {}
        }
        
        # 1. Rug Prediction
        try:
            prediction = await self.predictor.predict(contract, chain, contract_data)
            results['analyses']['rug_prediction'] = {
                'probability': prediction.rug_probability,
                'confidence': prediction.confidence,
                'estimated_hours': prediction.estimated_hours,
                'triggers': prediction.trigger_signals,
                'formatted': self.predictor.format_prediction(prediction)
            }
        except Exception as e:
            results['analyses']['rug_prediction'] = {'error': str(e)}
        
        # 2. Liquidity Vampire Detection
        try:
            pair_address = contract_data.get('pair_address')
            vampire = await self.vampire_detector.analyze_contract(
                contract, chain, pair_address
            )
            results['analyses']['vampire'] = {
                'risk_level': vampire['risk_level'],
                'threats': [t.threat_type for t in vampire['threats']],
                'real_liquidity': vampire['real_liquidity'],
                'formatted': self.vampire_detector.format_report(vampire)
            }
        except Exception as e:
            results['analyses']['vampire'] = {'error': str(e)}
        
        # 3. Dev Voiceprint
        try:
            dev_wallet = contract_data.get('dev_wallet', '')
            if dev_wallet:
                voiceprint = await self.voiceprint_analyzer.analyze_dev(
                    dev_wallet, chain
                )
                results['analyses']['voiceprint'] = {
                    'identity_matched': voiceprint['identity_matched'],
                    'total_rugs': voiceprint['total_rugs'],
                    'cross_chains': voiceprint['cross_chains'],
                    'formatted': self.voiceprint_analyzer.format_voiceprint_report(voiceprint)
                }
        except Exception as e:
            results['analyses']['voiceprint'] = {'error': str(e)}
        
        # 4. Holder Psychology (sample top holders)
        try:
            holder_psych = await self.token_holder_analysis.analyze_token_holders(
                contract, chain
            )
            results['analyses']['holders'] = {
                'psychology_breakdown': holder_psych['psychology_breakdown'],
                'paper_hands_pct': holder_psych['psychology_breakdown'].get('PAPER_HAND', 0),
                'diamond_hands_pct': holder_psych['psychology_breakdown'].get('DIAMOND_HAND', 0) + 
                                     holder_psych['psychology_breakdown'].get('WHALE', 0),
                'risk_assessment': holder_psych['risk_assessment'],
                'formatted': self.token_holder_analysis.format_token_analysis(holder_psych)
            }
        except Exception as e:
            results['analyses']['holders'] = {'error': str(e)}
        
        # 5. Calculate overall risk score
        results['overall_risk'] = self._calculate_overall_risk(results['analyses'])
        
        return results
    
    def _calculate_overall_risk(self, analyses: Dict) -> Dict:
        """Calculate overall risk from all analyses"""
        risk_score = 0
        factors = []
        
        # Rug prediction weight: 40%
        if 'rug_prediction' in analyses and 'probability' in analyses['rug_prediction']:
            prob = analyses['rug_prediction']['probability']
            risk_score += prob * 0.4
            if prob > 75:
                factors.append(f"AI predicts {prob:.0f}% rug probability")
        
        # Vampire weight: 25%
        if 'vampire' in analyses and 'risk_level' in analyses['vampire']:
            vampire_risk = analyses['vampire']['risk_level']
            if vampire_risk == 'EXTREME':
                risk_score += 25
                factors.append("Liquidity vampire threats detected")
            elif vampire_risk == 'HIGH':
                risk_score += 15
                factors.append("Suspicious liquidity patterns")
        
        # Voiceprint weight: 20%
        if 'voiceprint' in analyses and analyses['voiceprint'].get('identity_matched'):
            rugs = analyses['voiceprint'].get('total_rugs', 0)
            if rugs >= 5:
                risk_score += 20
                factors.append(f"Serial scammer ({rugs} previous rugs)")
            elif rugs >= 1:
                risk_score += 15
                factors.append(f"Known scammer ({rugs} previous rugs)")
        
        # Holders weight: 15%
        if 'holders' in analyses:
            paper_pct = analyses['holders'].get('paper_hands_pct', 0)
            if paper_pct > 50:
                risk_score += 15
                factors.append(f"High paper hands concentration ({paper_pct:.0f}%)")
            elif paper_pct > 30:
                risk_score += 8
        
        # Determine level
        if risk_score >= 80:
            level = 'EXTREME'
            emoji = '💀'
        elif risk_score >= 60:
            level = 'HIGH'
            emoji = '🚨'
        elif risk_score >= 40:
            level = 'MEDIUM'
            emoji = '⚠️'
        else:
            level = 'LOW'
            emoji = '🟢'
        
        return {
            'score': min(100, risk_score),
            'level': level,
            'emoji': emoji,
            'factors': factors
        }
    
    def format_full_report(self, results: Dict) -> str:
        """Format complete analysis report for Telegram"""
        risk = results['overall_risk']
        
        text = f"""
╔════════════════════════════════════════════════╗
║  🔥 <b>COMPLETE RUG MUNCHER ANALYSIS</b> 🔥  ║
╚════════════════════════════════════════════════╝

<b>Contract:</b> <code>{results['contract'][:16]}...</code>
<b>Chain:</b> {results['chain'].upper()}

{risk['emoji']} <b>OVERALL RISK: {risk['level']} ({risk['score']:.0f}/100)</b>

<b>🚨 KEY FACTORS:</b>
"""
        
        for factor in risk['factors']:
            text += f"• {factor}\n"
        
        # Add summary of each analysis
        analyses = results['analyses']
        
        # Rug Prediction Summary
        if 'rug_prediction' in analyses and 'probability' in analyses['rug_prediction']:
            pred = analyses['rug_prediction']
            prob_emoji = "💀" if pred['probability'] > 90 else "🚨" if pred['probability'] > 75 else "⚠️"
            text += f"""
<b>{prob_emoji} AI RUG PREDICTION:</b>
• Probability: {pred['probability']:.1f}%
• Est. Time: {pred['estimated_hours'][0]}-{pred['estimated_hours'][1]} hours
• Confidence: {pred['confidence']}
"""
        
        # Vampire Summary
        if 'vampire' in analyses and 'risk_level' in analyses['vampire']:
            vamp = analyses['vampire']
            if vamp['threats']:
                text += f"""
<b>🧛 LIQUIDITY THREATS:</b>
• Risk: {vamp['risk_level']}
• Threats: {len(vamp['threats'])}
• Real Liquidity: ${vamp.get('real_liquidity', 0):,.0f}
"""
        
        # Voiceprint Summary
        if 'voiceprint' in analyses and analyses['voiceprint'].get('identity_matched'):
            vp = analyses['voiceprint']
            text += f"""
<b>👤 DEV IDENTITY MATCHED!</b>
• Previous Rugs: {vp['total_rugs']}
• Cross-Chain: {', '.join(vp['cross_chains'])}
"""
        
        # Holders Summary
        if 'holders' in analyses:
            h = analyses['holders']
            text += f"""
<b>👥 HOLDER PSYCHOLOGY:</b>
• Diamond Hands: {h.get('diamond_hands_pct', 0):.1f}%
• Paper Hands: {h.get('paper_hands_pct', 0):.1f}%
"""
        
        text += """
<i>Use the buttons below for detailed analysis of each area.</i>
"""
        
        return text

# Global instance
_features_instance = None

async def get_features() -> RugMuncherFeatures:
    """Get or create features instance"""
    global _features_instance
    if _features_instance is None:
        _features_instance = RugMuncherFeatures()
        await _features_instance.start()
    return _features_instance

# ═══════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════

async def main():
    """Test all 5 features"""
    features = await get_features()
    
    # Sample contract data
    contract_data = {
        'contract': '0x1234567890abcdef1234567890abcdef12345678',
        'chain': 'bsc',
        'lp_locked': 0,
        'ownership_renounced': 0,
        'mint_function': 1,
        'blacklist_function': 1,
        'modifiable_taxes': 1,
        'dev_wallet': '0xabcdef1234567890abcdef1234567890abcdef12',
        'dev_wallet_age_days': 5,
        'dev_prev_rugs': 3,
        'fresh_wallet_pct': 75,
        'cluster_detected': 1,
        'bot_score': 80,
        'deleted_tweets': 2,
        'launch_hour_utc': 3
    }
    
    # Run full analysis
    results = await features.full_analysis(
        contract_data['contract'],
        contract_data['chain'],
        contract_data
    )
    
    print(features.format_full_report(results))
    
    await features.stop()

if __name__ == "__main__":
    asyncio.run(main())
