#!/usr/bin/env python3
"""
📊 DEMO TOKEN CHART
===================
Generate and display a demo scam token chart
"""

import asyncio
from datetime import datetime, timedelta
from chart_manager import ChartManager, ChartPattern, ChartAnalysis
from dataclasses import dataclass, field

# Generate realistic demo data for a PUMP & DUMP scam
def create_pump_dump_demo():
    """Create demo data for a pump and dump token"""
    
    # Simulate price data for PUMP & DUMP pattern
    demo_data = {
        'priceUsd': 0.0000420,
        'priceChange': {
            'm5': -15.5,
            'h1': -35.2,
            'h6': +450.0,  # Massive pump
            'h24': +180.0
        },
        'volume': {
            'h24': 2850000,
            'h6': 2100000,
            'h1': 850000
        },
        'liquidity': 45000,  # Low liquidity
        'fdv': 420000,
        'marketCap': 380000,
        'pairCreatedAt': datetime.now() - timedelta(hours=18),
        'info': {
            'imageUrl': 'https://example.com/token.png',
            'websites': [{'url': 'https://rugpulltoken.xyz'}],
            'socials': [
                {'type': 'twitter', 'url': 'https://twitter.com/rugpulltoken'},
                {'type': 'telegram', 'url': 'https://t.me/rugpulltoken'}
            ]
        }
    }
    
    return demo_data

def create_slow_rug_demo():
    """Create demo data for a slow rug token"""
    
    demo_data = {
        'priceUsd': 0.00000120,
        'priceChange': {
            'm5': -2.1,
            'h1': -8.5,
            'h6': -25.3,
            'h24': -65.0  # Gradual decline
        },
        'volume': {
            'h24': 125000,
            'h6': 45000,
            'h1': 8000
        },
        'liquidity': 12000,  # Very low
        'fdv': 120000,
        'marketCap': 95000,
        'pairCreatedAt': datetime.now() - timedelta(days=3),
        'info': {}
    }
    
    return demo_data

def create_safe_token_demo():
    """Create demo data for a safe token"""
    
    demo_data = {
        'priceUsd': 1.25,
        'priceChange': {
            'm5': +0.5,
            'h1': +2.1,
            'h6': +5.5,
            'h24': +8.2
        },
        'volume': {
            'h24': 2500000,
            'h6': 850000,
            'h1': 180000
        },
        'liquidity': 2500000,  # High liquidity
        'fdv': 12500000,
        'marketCap': 11200000,
        'pairCreatedAt': datetime.now() - timedelta(days=180),
        'info': {
            'imageUrl': 'https://example.com/safetoken.png',
            'websites': [{'url': 'https://safetoken.io'}]
        }
    }
    
    return demo_data

def print_ascii_chart(data: dict, width: int = 50, height: int = 10):
    """Print an ASCII chart of the price movement"""
    
    print("\n" + "="*60)
    print("📈 PRICE CHART (24H)")
    print("="*60)
    
    # Create a simple visualization
    price_24h = data['priceChange']['h24']
    price_6h = data['priceChange']['h6']
    price_1h = data['priceChange']['h1']
    
    # Normalize for display
    changes = [price_24h, price_6h, price_1h, data['priceChange']['m5']]
    max_change = max(abs(c) for c in changes) or 1
    
    bars = ['24H', '6H', '1H', '5M']
    
    for bar, change in zip(bars, changes):
        # Create bar
        bar_length = int((abs(change) / max_change) * 20)
        bar_char = "█" * bar_length
        
        # Color indicator
        if change > 0:
            color = "🟢"
            direction = "▲"
        else:
            color = "🔴"
            direction = "▼"
        
        print(f"{bar:4} {direction} {color} {bar_char:20} {change:+.1f}%")
    
    print("\n" + "-"*60)
    print(f"Current Price: ${data['priceUsd']:.10f}")
    print(f"24h Volume: ${data['volume']['h24']:,.0f}")
    print(f"Liquidity: ${data['liquidity']:,.0f}")
    print(f"Market Cap: ${data['marketCap']:,.0f}")
    print("="*60 + "\n")

def generate_demo_report(token_name: str, pattern_type: str):
    """Generate a complete demo report"""
    
    print(f"\n{'🔥'*20}")
    print(f"  DEMO: {token_name}")
    print(f"  Type: {pattern_type}")
    print(f"{'🔥'*20}\n")
    
    if pattern_type == "PUMP_AND_DUMP":
        data = create_pump_dump_demo()
        pattern = ChartPattern.PUMP_AND_DUMP
        confidence = 85
        warnings = [
            "🚨 PUMP & DUMP PATTERN - You're late!",
            "💀 EXTREMELY LOW LIQUIDITY - High slippage risk!",
            "📉 Very low volume - Illiquid token"
        ]
        risk_score = 95
        
    elif pattern_type == "SLOW_RUG":
        data = create_slow_rug_demo()
        pattern = ChartPattern.SLOW_RUG
        confidence = 78
        warnings = [
            "⚠️ Possible slow rug in progress",
            "💀 EXTREMELY LOW LIQUIDITY - High slippage risk!",
            "🔻 Massive -65.0% drop in 24h"
        ]
        risk_score = 88
        
    else:  # SAFE
        data = create_safe_token_demo()
        pattern = ChartPattern.STABLE
        confidence = 45
        warnings = []
        risk_score = 15
    
    # Print ASCII chart
    print_ascii_chart(data)
    
    # Print analysis
    pattern_emoji = {
        ChartPattern.PUMP_AND_DUMP: "🚨",
        ChartPattern.INSTANT_RUG: "💀",
        ChartPattern.SLOW_RUG: "⚠️",
        ChartPattern.VOLATILE: "📈",
        ChartPattern.STABLE: "🟢",
        ChartPattern.UNKNOWN: "❓"
    }
    
    emoji = pattern_emoji.get(pattern, "❓")
    
    print(f"{emoji} CHART ANALYSIS")
    print("-" * 50)
    print(f"Pattern:      {pattern.value.replace('_', ' ').title()}")
    print(f"Confidence:   {confidence}%")
    print(f"Risk Score:   {risk_score}/100")
    print()
    print("Price Change:")
    print(f"  24h:  {data['priceChange']['h24']:+.2f}%")
    print(f"  6h:   {data['priceChange']['h6']:+.2f}%")
    print(f"  1h:   {data['priceChange']['h1']:+.2f}%")
    print(f"  5m:   {data['priceChange']['m5']:+.2f}%")
    print()
    print(f"Volume (24h):  ${data['volume']['h24']:,.0f}")
    print(f"Liquidity:     ${data['liquidity']:,.0f}")
    print(f"Market Cap:    ${data['marketCap']:,.0f}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
    
    print("\n" + "="*60 + "\n")

def main():
    """Run all demos"""
    
    print("\n" + "="*60)
    print("📊 RUG MUNCHER CHART MANAGER - DEMO")
    print("="*60)
    print("\nThis demo shows how the chart analyzer detects")
    print("different scam patterns in token charts.\n")
    
    input("Press Enter to see PUMP & DUMP demo...")
    generate_demo_report("$RUGPULL Token", "PUMP_AND_DUMP")
    
    input("Press Enter to see SLOW RUG demo...")
    generate_demo_report("$SLOWRUG Token", "SLOW_RUG")
    
    input("Press Enter to see SAFE token demo...")
    generate_demo_report("$SAFEMOON Token", "SAFE")
    
    print("\n✅ Demo complete!")
    print("\nThese patterns are automatically detected by:")
    print("• Price movement analysis")
    print("• Volume patterns")
    print("• Liquidity checks")
    print("• Time-based indicators")
    print("\nUse /munch in the bot to analyze any token!")

if __name__ == '__main__':
    main()
