#!/usr/bin/env python3
"""
📊 CHART MANAGER MODULE
=======================
Advanced chart analysis and visualization for Rug Muncher Bot

Features:
- Price chart generation
- Volume analysis
- Pattern detection (pump & dump, rugs)
- Wallet clustering visualization
- Multi-timeframe analysis
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import math

class ChartPattern(Enum):
    PUMP_AND_DUMP = "pump_and_dump"
    SLOW_RUG = "slow_rug"
    INSTANT_RUG = "instant_rug"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    VOLATILE = "volatile"
    STABLE = "stable"
    UNKNOWN = "unknown"

@dataclass
class PricePoint:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
@dataclass
class ChartAnalysis:
    token_address: str
    chain: str
    timeframe: str  # 1h, 4h, 1d, etc.
    pattern: ChartPattern
    pattern_confidence: float  # 0-100
    price_change_24h: float
    price_change_7d: float
    volume_24h: float
    volatility: float
    support_levels: List[float]
    resistance_levels: List[float]
    avg_buy_pressure: float
    avg_sell_pressure: float
    whale_activity: List[Dict]
    warnings: List[str] = field(default_factory=list)
    chart_image_url: str = ""

class ChartManager:
    """
    Manage token charts and detect scam patterns
    Uses DexScreener, CoinGecko, and other APIs
    """
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def get_token_chart(self, token_address: str, chain: str = 'eth', 
                             timeframe: str = '1h', limit: int = 100) -> ChartAnalysis:
        """
        Get and analyze token chart data
        
        Args:
            token_address: Contract address
            chain: Blockchain (eth, bsc, base, etc.)
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles
        """
        # Check cache
        cache_key = f"{chain}:{token_address}:{timeframe}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # Fetch data from DexScreener
        price_data = await self._fetch_dexscreener(token_address, chain)
        
        # If no DexScreener data, try CoinGecko
        if not price_data:
            price_data = await self._fetch_coingecko(token_address, chain)
        
        if not price_data:
            return ChartAnalysis(
                token_address=token_address,
                chain=chain,
                timeframe=timeframe,
                pattern=ChartPattern.UNKNOWN,
                pattern_confidence=0,
                price_change_24h=0,
                price_change_7d=0,
                volume_24h=0,
                volatility=0,
                support_levels=[],
                resistance_levels=[],
                avg_buy_pressure=0,
                avg_sell_pressure=0,
                whale_activity=[],
                warnings=["No chart data available"]
            )
        
        # Analyze the data
        analysis = self._analyze_price_data(token_address, chain, timeframe, price_data)
        
        # Cache result
        self.cache[cache_key] = (datetime.now(), analysis)
        
        return analysis
    
    async def _fetch_dexscreener(self, token_address: str, chain: str) -> Optional[Dict]:
        """Fetch token data from DexScreener"""
        try:
            # Map chain names
            chain_map = {
                'eth': 'ethereum',
                'bsc': 'bsc',
                'base': 'base',
                'arb': 'arbitrum',
                'sol': 'solana'
            }
            
            dex_chain = chain_map.get(chain, 'ethereum')
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            
            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        # Get the pair with highest liquidity
                        main_pair = max(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0) or 0))
                        return {
                            'priceUsd': float(main_pair.get('priceUsd', 0)),
                            'priceChange': {
                                'm5': main_pair.get('priceChange', {}).get('m5', 0),
                                'h1': main_pair.get('priceChange', {}).get('h1', 0),
                                'h6': main_pair.get('priceChange', {}).get('h6', 0),
                                'h24': main_pair.get('priceChange', {}).get('h24', 0)
                            },
                            'volume': {
                                'h24': float(main_pair.get('volume', {}).get('h24', 0)),
                                'h6': float(main_pair.get('volume', {}).get('h6', 0)),
                                'h1': float(main_pair.get('volume', {}).get('h1', 0))
                            },
                            'liquidity': float(main_pair.get('liquidity', {}).get('usd', 0)),
                            'fdv': float(main_pair.get('fdv', 0)),
                            'marketCap': float(main_pair.get('marketCap', 0)),
                            'info': main_pair.get('info', {}),
                            'pairCreatedAt': main_pair.get('pairCreatedAt')
                        }
        except Exception as e:
            print(f"DexScreener error: {e}")
        
        return None
    
    async def _fetch_coingecko(self, token_address: str, chain: str) -> Optional[Dict]:
        """Fetch token data from CoinGecko"""
        # This would need CoinGecko API integration
        # Placeholder for now
        return None
    
    def _analyze_price_data(self, token_address: str, chain: str, 
                           timeframe: str, data: Dict) -> ChartAnalysis:
        """Analyze price data for patterns"""
        
        analysis = ChartAnalysis(
            token_address=token_address,
            chain=chain,
            timeframe=timeframe,
            pattern=ChartPattern.UNKNOWN,
            pattern_confidence=0,
            price_change_24h=data.get('priceChange', {}).get('h24', 0),
            price_change_7d=0,  # Would need historical data
            volume_24h=data.get('volume', {}).get('h24', 0),
            volatility=0,
            support_levels=[],
            resistance_levels=[],
            avg_buy_pressure=0,
            avg_sell_pressure=0,
            whale_activity=[]
        )
        
        # Calculate volatility
        price_changes = [
            data.get('priceChange', {}).get('m5', 0),
            data.get('priceChange', {}).get('h1', 0),
            data.get('priceChange', {}).get('h6', 0)
        ]
        
        if price_changes:
            analysis.volatility = sum(abs(x) for x in price_changes) / len(price_changes)
        
        # Detect patterns
        analysis.pattern, analysis.pattern_confidence = self._detect_pattern(data)
        
        # Calculate support/resistance (simplified)
        current_price = data.get('priceUsd', 0)
        if current_price > 0:
            analysis.support_levels = [current_price * 0.9, current_price * 0.8]
            analysis.resistance_levels = [current_price * 1.1, current_price * 1.2]
        
        # Generate warnings
        self._generate_warnings(analysis, data)
        
        return analysis
    
    def _detect_pattern(self, data: Dict) -> Tuple[ChartPattern, float]:
        """Detect chart patterns for scam detection"""
        
        price_change_24h = data.get('priceChange', {}).get('h24', 0)
        price_change_6h = data.get('priceChange', {}).get('h6', 0)
        price_change_1h = data.get('priceChange', {}).get('h1', 0)
        volume_24h = data.get('volume', {}).get('h24', 0)
        liquidity = data.get('liquidity', 0)
        
        confidence = 0
        
        # Pump and Dump: Big pump followed by dump
        if price_change_24h > 100 and price_change_1h < -20:
            confidence = min(100, abs(price_change_24h) / 2)
            return ChartPattern.PUMP_AND_DUMP, confidence
        
        # Instant Rug: Massive drop
        if price_change_24h < -80:
            confidence = min(100, abs(price_change_24h))
            return ChartPattern.INSTANT_RUG, confidence
        
        # Slow Rug: Gradual decline
        if price_change_24h < -30 and price_change_6h < -10:
            confidence = min(100, abs(price_change_24h))
            return ChartPattern.SLOW_RUG, confidence
        
        # High volatility
        if abs(price_change_1h) > 20 or abs(price_change_6h) > 50:
            return ChartPattern.VOLATILE, 60
        
        # Stable/Low activity
        if abs(price_change_24h) < 5:
            return ChartPattern.STABLE, 50
        
        return ChartPattern.UNKNOWN, 0
    
    def _generate_warnings(self, analysis: ChartAnalysis, data: Dict):
        """Generate warnings based on analysis"""
        
        # Low liquidity warning
        liquidity = data.get('liquidity', 0)
        if liquidity < 10000:
            analysis.warnings.append("💀 EXTREMELY LOW LIQUIDITY - High slippage risk!")
        elif liquidity < 50000:
            analysis.warnings.append("⚠️ Low liquidity - Be careful with large trades")
        
        # High volatility warning
        if analysis.volatility > 50:
            analysis.warnings.append("📈 High volatility detected")
        
        # Pattern-specific warnings
        if analysis.pattern == ChartPattern.PUMP_AND_DUMP:
            analysis.warnings.append("🚨 PUMP & DUMP PATTERN - You're late!")
        elif analysis.pattern == ChartPattern.INSTANT_RUG:
            analysis.warnings.append("💀 RUG PULL CONFIRMED - DO NOT BUY!")
        elif analysis.pattern == ChartPattern.SLOW_RUG:
            analysis.warnings.append("⚠️ Possible slow rug in progress")
        
        # Price drop warning
        if analysis.price_change_24h < -50:
            analysis.warnings.append(f"🔻 Massive {analysis.price_change_24h:.1f}% drop in 24h")
        
        # Volume warning
        if analysis.volume_24h < 1000:
            analysis.warnings.append("📉 Very low volume - Illiquid token")
    
    async def get_bubble_map(self, token_address: str, chain: str = 'eth') -> Dict:
        """
        Get wallet clustering visualization data
        Returns data for bubble map visualization
        """
        # This would integrate with bubble map APIs
        # Placeholder structure
        return {
            'token': token_address,
            'clusters': [
                {
                    'id': 'cluster_1',
                    'wallets': ['0x123...', '0x456...'],
                    'total_holding': 150000,
                    'percentage': 15,
                    'type': 'whale'
                }
            ],
            'total_holders': 1000,
            'top_10_percentage': 45,
            'concentration_risk': 'high'
        }
    
    def format_chart_report(self, analysis: ChartAnalysis) -> str:
        """Format chart analysis for Telegram message"""
        
        pattern_emoji = {
            ChartPattern.PUMP_AND_DUMP: "🚨",
            ChartPattern.INSTANT_RUG: "💀",
            ChartPattern.SLOW_RUG: "⚠️",
            ChartPattern.VOLATILE: "📈",
            ChartPattern.STABLE: "🟢",
            ChartPattern.UNKNOWN: "❓"
        }
        
        emoji = pattern_emoji.get(analysis.pattern, "❓")
        
        report = f"""
{emoji} <b>CHART ANALYSIS</b>

<b>Pattern:</b> {analysis.pattern.value.replace('_', ' ').title()}
<b>Confidence:</b> {analysis.pattern_confidence:.0f}%

<b>Price Change:</b>
• 24h: {analysis.price_change_24h:+.2f}%

<b>Volume (24h):</b> ${analysis.volume_24h:,.0f}
<b>Volatility:</b> {analysis.volatility:.1f}%
"""
        
        if analysis.warnings:
            report += "\n<b>⚠️ WARNINGS:</b>\n"
            for warning in analysis.warnings[:5]:
                report += f"• {warning}\n"
        
        if analysis.support_levels:
            report += f"\n<b>Support:</b> ${analysis.support_levels[0]:.6f}"
        if analysis.resistance_levels:
            report += f"\n<b>Resistance:</b> ${analysis.resistance_levels[0]:.6f}"
        
        return report

# Test
async def test():
    async with ChartManager() as cm:
        # Test with a known token (example)
        analysis = await cm.get_token_chart(
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "eth"
        )
        print(cm.format_chart_report(analysis))

if __name__ == '__main__':
    asyncio.run(test())
