#!/usr/bin/env python3
"""
📊 CHART SERVICE
================
Generate real chart images using QuickChart API
No local dependencies required!
"""

import aiohttp
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OHLCV:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class ChartService:
    """
    Generate professional charts using QuickChart.io (free)
    No local matplotlib needed!
    """
    
    BASE_URL = "https://quickchart.io/chart"
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def generate_candlestick_chart(self, token_name: str, ohlcv_data: List[OHLCV], 
                                         pattern: str = "") -> str:
        """
        Generate candlestick chart URL
        Returns URL to chart image
        """
        
        # Prepare data for Chart.js
        labels = [d.timestamp.strftime("%H:%M") for d in ohlcv_data]
        
        # Create candlestick dataset
        candle_data = []
        for d in ohlcv_data:
            candle_data.append({
                'x': d.timestamp.strftime("%H:%M"),
                'o': d.open,
                'h': d.high,
                'l': d.low,
                'c': d.close
            })
        
        # Chart.js configuration
        chart_config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": token_name,
                    "data": [d.close for d in ohlcv_data],
                    "backgroundColor": [
                        "#00ff41" if ohlcv_data[i].close >= ohlcv_data[i].open else "#ff0040"
                        for i in range(len(ohlcv_data))
                    ],
                    "borderColor": [
                        "#00aa00" if ohlcv_data[i].close >= ohlcv_data[i].open else "#aa0000"
                        for i in range(len(ohlcv_data))
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "backgroundColor": "#0a0a0a",
                "title": {
                    "display": True,
                    "text": f"{token_name} Price Chart {f'[{pattern}]' if pattern else ''}",
                    "fontColor": "#00ff41",
                    "fontSize": 18
                },
                "legend": {
                    "labels": {"fontColor": "#ffffff"}
                },
                "scales": {
                    "xAxes": [{
                        "ticks": {"fontColor": "#888888"},
                        "gridLines": {"color": "#333333"}
                    }],
                    "yAxes": [{
                        "ticks": {"fontColor": "#888888"},
                        "gridLines": {"color": "#333333"}
                    }]
                }
            }
        }
        
        # Build URL
        chart_json = json.dumps(chart_config)
        chart_url = f"{self.BASE_URL}?c={chart_json}&w=800&h=400&bkg=%230a0a0a"
        
        return chart_url
    
    async def generate_risk_gauge(self, risk_score: int, token_name: str) -> str:
        """Generate a risk score gauge chart"""
        
        # Determine color based on risk
        if risk_score >= 80:
            color = "#ff0040"  # Red
            status = "CRITICAL"
        elif risk_score >= 60:
            color = "#ffaa00"  # Orange
            status = "HIGH"
        elif risk_score >= 40:
            color = "#ffff00"  # Yellow
            status = "MEDIUM"
        else:
            color = "#00ff41"  # Green
            status = "SAFE"
        
        chart_config = {
            "type": "gauge",
            "data": {
                "datasets": [{
                    "value": risk_score,
                    "minValue": 0,
                    "maxValue": 100,
                    "backgroundColor": [
                        "#00ff41",  # 0-25: Safe
                        "#ffff00",  # 25-50: Medium
                        "#ffaa00",  # 50-75: High
                        "#ff0040"   # 75-100: Critical
                    ],
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": f"{token_name} - Risk Score: {risk_score}/100 [{status}]",
                    "fontColor": color,
                    "fontSize": 20
                },
                "backgroundColor": "#0a0a0a",
                "centerArea": {
                    "fontSize": 40,
                    "fontColor": color,
                    "text": str(risk_score)
                }
            }
        }
        
        chart_json = json.dumps(chart_config)
        chart_url = f"{self.BASE_URL}?c={chart_json}&w=600&h=400&bkg=%230a0a0a"
        
        return chart_url
    
    async def generate_volume_chart(self, token_name: str, volume_data: List[Dict]) -> str:
        """Generate volume analysis chart"""
        
        labels = [d['time'] for d in volume_data]
        volumes = [d['volume'] for d in volume_data]
        colors = ["#00ff41" if d.get('is_buy', True) else "#ff0040" for d in volume_data]
        
        chart_config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Volume",
                    "data": volumes,
                    "backgroundColor": colors,
                    "borderWidth": 0
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": f"{token_name} - Volume Analysis",
                    "fontColor": "#00ff41"
                },
                "backgroundColor": "#0a0a0a",
                "legend": {"display": False},
                "scales": {
                    "xAxes": [{"ticks": {"fontColor": "#888888"}}],
                    "yAxes": [{"ticks": {"fontColor": "#888888"}}]
                }
            }
        }
        
        chart_json = json.dumps(chart_config)
        chart_url = f"{self.BASE_URL}?c={chart_json}&w=800&h=300&bkg=%230a0a0a"
        
        return chart_url
    
    async def download_chart(self, chart_url: str, output_path: str) -> str:
        """Download chart image to local file"""
        
        try:
            async with self.session.get(chart_url, timeout=30) as resp:
                if resp.status == 200:
                    with open(output_path, 'wb') as f:
                        f.write(await resp.read())
                    return output_path
        except Exception as e:
            print(f"Chart download error: {e}")
        
        return None

# Demo data generators
def generate_pump_dump_data() -> List[OHLCV]:
    """Generate pump and dump OHLCV data"""
    import random
    
    data = []
    base_price = 0.000001
    
    # Phase 1: Flat (0-20)
    for i in range(20):
        price = base_price * (1 + random.uniform(-0.02, 0.02))
        data.append(OHLCV(
            timestamp=datetime.now() - timedelta(minutes=40-i),
            open=price * 0.99,
            high=price * 1.01,
            low=price * 0.98,
            close=price,
            volume=random.uniform(1000, 5000)
        ))
    
    # Phase 2: PUMP (20-35)
    current_price = base_price
    for i in range(15):
        multiplier = 1 + (i / 15) * 9  # 1x to 10x
        price = base_price * multiplier * random.uniform(0.9, 1.1)
        current_price = price
        data.append(OHLCV(
            timestamp=datetime.now() - timedelta(minutes=20-i),
            open=price * 0.95,
            high=price * 1.15,
            low=price * 0.90,
            close=price,
            volume=random.uniform(50000, 150000)
        ))
    
    # Phase 3: DUMP (35-50)
    for i in range(15):
        drop = (i / 15) * 0.85
        price = current_price * (1 - drop) * random.uniform(0.95, 1.05)
        data.append(OHLCV(
            timestamp=datetime.now() - timedelta(minutes=5-i),
            open=price * 1.05,
            high=price * 1.10,
            low=price * 0.80,
            close=price,
            volume=random.uniform(80000, 200000)
        ))
    
    return data

def generate_safe_token_data() -> List[OHLCV]:
    """Generate normal/safe token data"""
    import random
    
    data = []
    base_price = 1.25
    
    for i in range(50):
        change = random.uniform(-0.02, 0.025)
        price = base_price * (1 + change)
        base_price = price
        
        data.append(OHLCV(
            timestamp=datetime.now() - timedelta(minutes=50-i),
            open=price * 0.995,
            high=price * 1.005,
            low=price * 0.992,
            close=price,
            volume=random.uniform(50000, 100000)
        ))
    
    return data

# Demo
async def demo():
    """Generate demo charts"""
    print("📊 CHART SERVICE DEMO")
    print("=" * 50)
    
    async with ChartService() as cs:
        # 1. Pump & Dump Chart
        print("\n1. Generating PUMP & DUMP chart...")
        pump_data = generate_pump_dump_data()
        chart_url = await cs.generate_candlestick_chart(
            "$RUGPULL Token",
            pump_data,
            "PUMP & DUMP"
        )
        print(f"   📈 Chart URL: {chart_url[:80]}...")
        
        # 2. Risk Gauges
        print("\n2. Generating risk gauges...")
        for score, name in [(95, "Rug Token"), (45, "Medium Risk"), (15, "Safe Token")]:
            gauge_url = await cs.generate_risk_gauge(score, name)
            print(f"   🎚️  {name} ({score}/100): {gauge_url[:60]}...")
        
        # 3. Volume Chart
        print("\n3. Generating volume chart...")
        volume_data = [
            {'time': f'{i}:00', 'volume': random.randint(10000, 100000), 'is_buy': i % 2 == 0}
            for i in range(24)
        ]
        vol_url = await cs.generate_volume_chart("Demo Token", volume_data)
        print(f"   📊 Volume: {vol_url[:60]}...")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete!")
    print("\nThese are LIVE chart URLs - open them in browser!")

if __name__ == '__main__':
    import random
    asyncio.run(demo())
