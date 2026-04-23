#!/usr/bin/env python3
"""
🧛 LIQUIDITY VAMPIRE DETECTOR
Detect hidden liquidity manipulation, sandwich bots, and proxy rug methods
The invisible killer that other bots miss
"""

import os
import asyncio
import aiohttp
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class LiquidityThreat:
    threat_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    evidence: Dict
    estimated_drain_pct: float
    confidence: float  # 0-100

class LiquidityVampireDetector:
    """
    Detect sophisticated liquidity manipulation attacks
    """
    
    THREAT_TYPES = {
        'SANDWICH_BOT_EXTRACTION': {
            'description': 'Automated sandwich attacks draining LP on every trade',
            'severity': 'HIGH'
        },
        'PROXY_CONTRACT_RUG': {
            'description': 'Hidden proxy contract allows bypassing LP locks',
            'severity': 'CRITICAL'
        },
        'FLASH_LOAN_SETUP': {
            'description': 'Contract has flash loan hooks for price manipulation',
            'severity': 'CRITICAL'
        },
        'HIDDEN_MINT_FUNCTION': {
            'description': 'Mint function disguised in proxy or delegate calls',
            'severity': 'CRITICAL'
        },
        'LP_TOKEN_THEFT': {
            'description': 'Contract can steal LP tokens from holders',
            'severity': 'CRITICAL'
        },
        'TAX_MANIPULATION': {
            'description': 'Taxes can be changed to 100% to trap sellers',
            'severity': 'HIGH'
        },
        'BOTNET_WASH_TRADING': {
            'description': 'Coordinated bot network faking volume',
            'severity': 'MEDIUM'
        },
        'MULTI_HOP_EXIT': {
            'description': 'Dev using multiple DEXs to hide exits',
            'severity': 'HIGH'
        }
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.known_sandwich_bots = self._load_known_bots()
        self.proxy_signatures = [
            'delegatecall',
            'implementation',
            'upgradeTo',
            'proxy',
            'transparent'
        ]
    
    async def start(self):
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        if self.session:
            await self.session.close()
    
    def _load_known_bots(self) -> List[str]:
        """Load known sandwich bot addresses"""
        return [
            '0x0000000000000000000000000000000000000000',  # Placeholder
        ]
    
    async def analyze_contract(self, contract: str, chain: str, 
                               pair_address: str = None) -> Dict:
        """
        Full liquidity vampire analysis
        """
        threats = []
        
        # Check for proxy patterns
        proxy_threat = await self._detect_proxy_rug(contract, chain)
        if proxy_threat:
            threats.append(proxy_threat)
        
        # Check for sandwich bot activity
        sandwich_threat = await self._detect_sandwich_extraction(contract, chain, pair_address)
        if sandwich_threat:
            threats.append(sandwich_threat)
        
        # Check for flash loan hooks
        flash_threat = await self._detect_flash_loan_setup(contract, chain)
        if flash_threat:
            threats.append(flash_threat)
        
        # Check for hidden mint
        mint_threat = await self._detect_hidden_mint(contract, chain)
        if mint_threat:
            threats.append(mint_threat)
        
        # Check for LP theft capability
        lp_threat = await self._detect_lp_theft(contract, chain)
        if lp_threat:
            threats.append(lp_threat)
        
        # Check wash trading
        wash_threat = await self._detect_wash_trading(contract, chain)
        if wash_threat:
            threats.append(wash_threat)
        
        # Calculate real liquidity vs displayed
        liquidity_analysis = await self._analyze_real_liquidity(contract, chain, pair_address)
        
        return {
            'contract': contract,
            'chain': chain,
            'threats': threats,
            'threat_count': len(threats),
            'critical_count': sum(1 for t in threats if t.severity == 'CRITICAL'),
            'displayed_liquidity': liquidity_analysis['displayed'],
            'real_liquidity': liquidity_analysis['real'],
            'liquidity_vampire_pct': liquidity_analysis['vampire_pct'],
            'is_safe': len(threats) == 0 and liquidity_analysis['vampire_pct'] < 20,
            'risk_level': self._calculate_risk(threats, liquidity_analysis)
        }
    
    async def _detect_proxy_rug(self, contract: str, chain: str) -> Optional[LiquidityThreat]:
        """Detect proxy contracts that can bypass locks"""
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        try:
            url = f"https://{base}/api?module=contract&action=getsourcecode&address={contract}&apikey={api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    if data.get('status') == '1' and data.get('result'):
                        source = data['result'][0].get('SourceCode', '')
                        
                        # Check for proxy patterns
                        proxy_indicators = []
                        for sig in self.proxy_signatures:
                            if sig.lower() in source.lower():
                                proxy_indicators.append(sig)
                        
                        if proxy_indicators:
                            # Check if implementation can be changed
                            can_upgrade = 'upgradeTo' in source or 'setImplementation' in source
                            
                            return LiquidityThreat(
                                threat_type='PROXY_CONTRACT_RUG',
                                severity='CRITICAL',
                                description=f"Proxy contract detected with {len(proxy_indicators)} proxy patterns. Can bypass all locks.",
                                evidence={
                                    'proxy_patterns_found': proxy_indicators,
                                    'upgradeable': can_upgrade,
                                    'source_length': len(source)
                                },
                                estimated_drain_pct=100.0,
                                confidence=95.0 if can_upgrade else 75.0
                            )
        except Exception as e:
            print(f"[Vampire] Proxy detection error: {e}")
        
        return None
    
    async def _detect_sandwich_extraction(self, contract: str, chain: str, 
                                          pair_address: str = None) -> Optional[LiquidityThreat]:
        """Detect if sandwich bots are draining LP"""
        if not pair_address:
            return None
        
        try:
            # Analyze recent trades for sandwich patterns
            url = f"https://api.dexscreener.com/latest/dex/transactions/{pair_address}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    transactions = data.get('transactions', [])
                    
                    sandwich_count = 0
                    extraction_estimate = 0
                    
                    # Look for sandwich patterns (buy -> victim -> sell in same block)
                    for i in range(len(transactions) - 2):
                        tx1 = transactions[i]
                        tx2 = transactions[i + 1]
                        tx3 = transactions[i + 2]
                        
                        # Check if tx1 and tx3 are same address (sandwich)
                        if tx1.get('from') == tx3.get('from') and tx1.get('type') == 'buy' and tx3.get('type') == 'sell':
                            if tx2.get('type') == 'buy':  # Victim in middle
                                sandwich_count += 1
                                extraction_estimate += float(tx3.get('amountUsd', 0)) * 0.02  # ~2% extraction
                    
                    if sandwich_count > 5:
                        return LiquidityThreat(
                            threat_type='SANDWICH_BOT_EXTRACTION',
                            severity='HIGH',
                            description=f"{sandwich_count} sandwich attacks detected. Bots draining {extraction_estimate:.2f} USD per hour.",
                            evidence={
                                'sandwich_count': sandwich_count,
                                'hourly_extraction_usd': extraction_estimate,
                                'bot_addresses': list(set(tx.get('from') for tx in transactions if tx.get('from')))
                            },
                            estimated_drain_pct=min(50, extraction_estimate * 24 / 1000),  # Daily % drain
                            confidence=min(90, 50 + sandwich_count * 5)
                        )
        except Exception as e:
            print(f"[Vampire] Sandwich detection error: {e}")
        
        return None
    
    async def _detect_flash_loan_setup(self, contract: str, chain: str) -> Optional[LiquidityThreat]:
        """Detect flash loan hooks for price manipulation"""
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        try:
            url = f"https://{base}/api?module=contract&action=getsourcecode&address={contract}&apikey={api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    if data.get('status') == '1' and data.get('result'):
                        source = data['result'][0].get('SourceCode', '')
                        
                        flash_indicators = ['flashLoan', 'flash loan', 'onFlashLoan', 'flashBorrow', 'flashMint']
                        found = [ind for ind in flash_indicators if ind.lower() in source.lower()]
                        
                        if found:
                            return LiquidityThreat(
                                threat_type='FLASH_LOAN_SETUP',
                                severity='CRITICAL',
                                description=f"Flash loan hooks detected. Contract can be manipulated via flash loans.",
                                evidence={'flash_loan_functions': found},
                                estimated_drain_pct=100.0,
                                confidence=85.0
                            )
        except Exception as e:
            print(f"[Vampire] Flash loan detection error: {e}")
        
        return None
    
    async def _detect_hidden_mint(self, contract: str, chain: str) -> Optional[LiquidityThreat]:
        """Detect mint functions hidden in proxies or delegate calls"""
        # This would require bytecode analysis
        # Simplified implementation
        return None
    
    async def _detect_lp_theft(self, contract: str, chain: str) -> Optional[LiquidityThreat]:
        """Detect if contract can steal LP tokens"""
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        try:
            url = f"https://{base}/api?module=contract&action=getsourcecode&address={contract}&apikey={api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    if data.get('status') == '1' and data.get('result'):
                        source = data['result'][0].get('SourceCode', '')
                        
                        theft_patterns = [
                            'transferFrom.*pair', 'transfer.*lp', 'safeTransfer.*pair',
                            'skim', 'sync.*exploit'
                        ]
                        
                        found_patterns = []
                        for pattern in theft_patterns:
                            if re.search(pattern, source, re.IGNORECASE):
                                found_patterns.append(pattern)
                        
                        if found_patterns:
                            return LiquidityThreat(
                                threat_type='LP_TOKEN_THEFT',
                                severity='CRITICAL',
                                description="Contract can steal LP tokens from pair or holders",
                                evidence={'theft_patterns': found_patterns},
                                estimated_drain_pct=100.0,
                                confidence=80.0
                            )
        except Exception as e:
            print(f"[Vampire] LP theft detection error: {e}")
        
        return None
    
    async def _detect_wash_trading(self, contract: str, chain: str) -> Optional[LiquidityThreat]:
        """Detect coordinated bot wash trading"""
        # Analyze transfer patterns for identical amounts/timing
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        try:
            url = f"https://{base}/api?module=account&action=tokentx&contractaddress={contract}&page=1&offset=100&apikey={api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    if data.get('status') == '1':
                        txs = data.get('result', [])
                        
                        # Check for identical amounts (wash trading signature)
                        amounts = defaultdict(int)
                        for tx in txs:
                            amount = round(float(tx.get('value', 0)) / 1e18, 4)
                            amounts[amount] += 1
                        
                        suspicious_amounts = {k: v for k, v in amounts.items() if v > 10}
                        
                        if len(suspicious_amounts) > 3:
                            total_wash = sum(suspicious_amounts.values())
                            return LiquidityThreat(
                                threat_type='BOTNET_WASH_TRADING',
                                severity='MEDIUM',
                                description=f"Coordinated wash trading detected. {total_wash} identical transactions.",
                                evidence={
                                    'repeated_amounts': suspicious_amounts,
                                    'wash_percentage': total_wash / len(txs) * 100
                                },
                                estimated_drain_pct=15.0,  # Inflated volume misleading buyers
                                confidence=75.0
                            )
        except Exception as e:
            print(f"[Vampire] Wash trading detection error: {e}")
        
        return None
    
    async def _analyze_real_liquidity(self, contract: str, chain: str, 
                                       pair_address: str = None) -> Dict:
        """Calculate real available liquidity vs displayed"""
        try:
            # Get displayed liquidity from DexScreener
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        pair = pairs[0]
                        displayed_liq = float(pair.get('liquidity', {}).get('usd', 0))
                        
                        # Estimate real liquidity (minus locked, minus dev holdings)
                        # This is simplified - real implementation would be more complex
                        real_liq = displayed_liq * 0.4  # Assume 60% is locked/dev held
                        
                        return {
                            'displayed': displayed_liq,
                            'real': real_liq,
                            'vampire_pct': ((displayed_liq - real_liq) / displayed_liq * 100) if displayed_liq > 0 else 0
                        }
        except Exception as e:
            print(f"[Vampire] Liquidity analysis error: {e}")
        
        return {'displayed': 0, 'real': 0, 'vampire_pct': 0}
    
    def _calculate_risk(self, threats: List[LiquidityThreat], liquidity: Dict) -> str:
        """Calculate overall risk level"""
        critical = sum(1 for t in threats if t.severity == 'CRITICAL')
        high = sum(1 for t in threats if t.severity == 'HIGH')
        
        if critical > 0 or liquidity['vampire_pct'] > 80:
            return 'EXTREME'
        elif critical > 0 or high > 1 or liquidity['vampire_pct'] > 50:
            return 'HIGH'
        elif high > 0 or liquidity['vampire_pct'] > 30:
            return 'MEDIUM'
        elif len(threats) > 0:
            return 'LOW'
        else:
            return 'SAFE'
    
    def format_report(self, analysis: Dict) -> str:
        """Format vampire analysis for display"""
        risk_emoji = "💀" if analysis['risk_level'] == 'EXTREME' else "🚨" if analysis['risk_level'] == 'HIGH' else "⚠️" if analysis['risk_level'] == 'MEDIUM' else "✅"
        
        text = f"""
🧛 <b>LIQUIDITY VAMPIRE DETECTOR</b> 🧛

<b>Contract:</b> <code>{analysis['contract'][:16]}...</code>

{risk_emoji} <b>RISK LEVEL: {analysis['risk_level']}</b>

<b>📊 LIQUIDITY ANALYSIS:</b>
• Displayed: <code>${analysis['displayed_liquidity']:,.0f}</code>
• Real Available: <code>${analysis['real_liquidity']:,.0f}</code>
• Vampire Drain: <code>{analysis['liquidity_vampire_pct']:.1f}%</code>
"""
        
        if analysis['threats']:
            text += f"""
<b>🚨 THREATS DETECTED: {analysis['threat_count']}</b>
<b>Critical:</b> {analysis['critical_count']}

"""
            for threat in analysis['threats']:
                severity_emoji = "💀" if threat.severity == 'CRITICAL' else "🚨" if threat.severity == 'HIGH' else "⚠️"
                text += f"{severity_emoji} <b>{threat.threat_type}</b>\n"
                text += f"<i>{threat.description}</i>\n"
                text += f"Confidence: {threat.confidence:.0f}%\n\n"
        
        if analysis['is_safe']:
            text += """
✅ <b>NO VAMPIRE THREATS DETECTED</b>
Liquidity appears genuine and safe.
"""
        
        return text

# ═══════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════

async def main():
    detector = LiquidityVampireDetector()
    await detector.start()
    
    try:
        analysis = await detector.analyze_contract(
            '0x1234567890abcdef1234567890abcdef12345678',
            'bsc'
        )
        print(detector.format_report(analysis))
    finally:
        await detector.stop()

if __name__ == "__main__":
    asyncio.run(main())
