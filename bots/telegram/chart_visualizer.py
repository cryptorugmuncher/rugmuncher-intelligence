#!/usr/bin/env python3
"""
📊 CHART VISUALIZER - REAL CHARTS
==================================
Generate actual chart images using matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os

class ChartVisualizer:
    """Generate professional token charts"""
    
    def __init__(self, output_dir: str = './charts'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('dark_background')
        self.colors = {
            'up': '#00ff41',
            'down': '#ff0040',
            'neutral': '#888888',
            'volume': '#1a1a2e',
            'grid': '#333333',
            'text': '#ffffff'
        }
    
    def generate_candlestick_chart(self, token_address: str, token_name: str, 
                                   price_data: List[Dict], output_filename: str = None) -> str:
        """
        Generate a professional candlestick chart
        
        Args:
            token_address: Contract address
            token_name: Token name/symbol
            price_data: List of OHLCV data points
            output_filename: Output file path
            
        Returns:
            Path to generated chart image
        """
        if output_filename is None:
            output_filename = f"{self.output_dir}/{token_address[:10]}_chart.png"
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                       gridspec_kw={'height_ratios': [3, 1]})
        fig.patch.set_facecolor('#0a0a0a')
        ax1.set_facecolor('#1a1a2e')
        ax2.set_facecolor('#1a1a2e')
        
        # Extract data
        times = [p['timestamp'] for p in price_data]
        opens = [p['open'] for p in price_data]
        highs = [p['high'] for p in price_data]
        lows = [p['low'] for p in price_data]
        closes = [p['close'] for p in price_data]
        volumes = [p['volume'] for p in price_data]
        
        # Plot candlesticks
        for i, (t, o, h, l, c) in enumerate(zip(times, opens, highs, lows, closes)):
            color = self.colors['up'] if c >= o else self.colors['down']
            
            # Body
            height = abs(c - o)
            bottom = min(o, c)
            rect = plt.Rectangle((i-0.4, bottom), 0.8, height, 
                                facecolor=color, edgecolor=color, linewidth=1)
            ax1.add_patch(rect)
            
            # Wick
            ax1.plot([i, i], [l, h], color=color, linewidth=1)
        
        # Format price chart
        ax1.set_ylabel('Price ($)', color='white', fontsize=12)
        ax1.set_title(f'{token_name} Price Chart\n{token_address}', 
                     color='white', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.2, color=self.colors['grid'])
        ax1.tick_params(colors='white')
        
        # Format x-axis
        ax1.set_xticks(range(0, len(times), max(1, len(times)//6)))
        ax1.set_xticklabels([])
        
        # Volume chart
        colors_vol = [self.colors['up'] if closes[i] >= opens[i] 
                     else self.colors['down'] for i in range(len(volumes))]
        ax2.bar(range(len(volumes)), volumes, color=colors_vol, alpha=0.7)
        ax2.set_ylabel('Volume', color='white', fontsize=12)
        ax2.set_xlabel('Time', color='white', fontsize=12)
        ax2.grid(True, alpha=0.2, color=self.colors['grid'])
        ax2.tick_params(colors='white')
        
        # Format x-axis labels
        step = max(1, len(times)//6)
        ax2.set_xticks(range(0, len(times), step))
        ax2.set_xticklabels([t.strftime('%H:%M') if isinstance(t, datetime) else str(t) 
                            for t in times[::step]], rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_filename, dpi=150, facecolor='#0a0a0a', 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        return output_filename
    
    def generate_pump_dump_demo(self) -> str:
        """Generate a pump and dump chart demo"""
        
        # Generate fake pump & dump data
        np.random.seed(42)
        n_points = 50
        
        # Create pump and dump pattern
        times = [datetime.now() - timedelta(hours=i) for i in range(n_points, 0, -1)]
        
        # Price pattern: flat -> pump -> dump
        base_price = 0.000001
        prices = []
        
        for i in range(n_points):
            if i < 20:
                # Flat period
                price = base_price * (1 + np.random.normal(0, 0.02))
            elif i < 35:
                # Pump phase (10x)
                progress = (i - 20) / 15
                multiplier = 1 + progress * 9  # 1x to 10x
                price = base_price * multiplier * (1 + np.random.normal(0, 0.1))
            else:
                # Dump phase
                progress = (i - 35) / 15
                multiplier = 10 * (1 - progress * 0.9)  # 10x to 1x
                price = base_price * max(multiplier, 0.1) * (1 + np.random.normal(0, 0.05))
            
            prices.append(price)
        
        # Create OHLC from price
        ohlc = []
        for i, price in enumerate(prices):
            volatility = price * 0.05
            o = price + np.random.normal(0, volatility)
            c = prices[i+1] if i < len(prices)-1 else price
            h = max(o, c) + abs(np.random.normal(0, volatility))
            l = min(o, c) - abs(np.random.normal(0, volatility))
            v = np.random.exponential(50000) * (1 + i/10 if 20 < i < 35 else 1)
            
            ohlc.append({
                'timestamp': times[i],
                'open': o,
                'high': h,
                'low': l,
                'close': c,
                'volume': v
            })
        
        return self.generate_candlestick_chart(
            '0xPUMPDUMP...420',
            '$RUGPULL (PUMP & DUMP)',
            ohlc,
            f'{self.output_dir}/pump_dump_demo.png'
        )
    
    def generate_wallet_graph(self, center_wallet: str, related_wallets: List[Dict]) -> str:
        """
        Generate a wallet relationship graph
        
        Args:
            center_wallet: Main wallet address
            related_wallets: List of related wallets with connection strength
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#1a1a2e')
        
        # Center node
        center_x, center_y = 0, 0
        ax.scatter(center_x, center_y, s=2000, c='#00ff41', alpha=0.8, zorder=5)
        ax.text(center_x, center_y, f'{center_wallet[:10]}...', 
               ha='center', va='center', fontsize=10, color='white', fontweight='bold')
        
        # Related wallets in circle
        n_wallets = len(related_wallets)
        radius = 3
        
        for i, wallet in enumerate(related_wallets):
            angle = 2 * np.pi * i / n_wallets
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Connection line
            strength = wallet.get('strength', 0.5)
            ax.plot([center_x, x], [center_y, y], 
                   color='#00ff41', alpha=strength, linewidth=2*strength)
            
            # Wallet node
            size = 500 + wallet.get('tx_count', 0) * 10
            color = '#ff0040' if wallet.get('risk_score', 0) > 70 else '#ffff00' if wallet.get('risk_score', 0) > 40 else '#00ff41'
            
            ax.scatter(x, y, s=size, c=color, alpha=0.7, zorder=4)
            ax.text(x, y + 0.3, f'{wallet["address"][:8]}...', 
                   ha='center', va='bottom', fontsize=8, color='white')
        
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        ax.set_title('Wallet Relationship Graph', color='white', fontsize=14, fontweight='bold')
        
        # Legend
        legend_text = "🟢 Low Risk | 🟡 Medium | 🔴 High Risk"
        ax.text(0, -4.5, legend_text, ha='center', va='center', 
               fontsize=10, color='white')
        
        output_file = f'{self.output_dir}/wallet_graph.png'
        plt.savefig(output_file, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def generate_risk_gauge(self, risk_score: int, token_name: str) -> str:
        """Generate a risk score gauge"""
        
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        
        # Create gauge
        theta = np.linspace(0, np.pi, 100)
        
        # Background arc (colored zones)
        colors = ['#00ff41', '#ffff00', '#ffaa00', '#ff0040']
        zones = [0, 25, 50, 75, 100]
        
        for i in range(len(zones)-1):
            start_idx = int((zones[i] / 100) * 99)
            end_idx = int((zones[i+1] / 100) * 99)
            ax.fill_between(theta[start_idx:end_idx+1], 0.5, 1, 
                          color=colors[i], alpha=0.3)
        
        # Needle
        needle_angle = np.pi * (1 - risk_score / 100)
        ax.plot([0, 0.8 * np.cos(needle_angle)], [0, 0.8 * np.sin(needle_angle)], 
               color='white', linewidth=4)
        ax.scatter(0, 0, s=200, c='white', zorder=5)
        
        # Labels
        ax.text(-1, -0.2, 'SAFE', ha='center', fontsize=12, color='#00ff41', fontweight='bold')
        ax.text(0, 1.2, f'{risk_score}', ha='center', fontsize=40, color='white', fontweight='bold')
        ax.text(0, 0.8, token_name, ha='center', fontsize=14, color='#888888')
        ax.text(1, -0.2, 'RUG', ha='center', fontsize=12, color='#ff0040', fontweight='bold')
        
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        output_file = f'{self.output_dir}/risk_gauge_{risk_score}.png'
        plt.savefig(output_file, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
        plt.close()
        
        return output_file

def main():
    """Generate demo charts"""
    print("📊 Generating demo charts...")
    
    viz = ChartVisualizer(output_dir='./demo_charts')
    
    # 1. Pump & Dump Chart
    print("1. Creating PUMP & DUMP chart...")
    chart1 = viz.generate_pump_dump_demo()
    print(f"   ✅ Saved: {chart1}")
    
    # 2. Risk Gauges
    print("\n2. Creating risk gauges...")
    for score in [15, 55, 85]:
        gauge = viz.generate_risk_gauge(score, f"Demo Token {score}")
        print(f"   ✅ Risk {score}: {gauge}")
    
    # 3. Wallet Graph
    print("\n3. Creating wallet graph...")
    related = [
        {'address': '0x1234...', 'tx_count': 50, 'risk_score': 20},
        {'address': '0x5678...', 'tx_count': 120, 'risk_score': 85},
        {'address': '0x9abc...', 'tx_count': 30, 'risk_score': 45},
        {'address': '0xdef0...', 'tx_count': 80, 'risk_score': 60},
    ]
    graph = viz.generate_wallet_graph('0xCENTER...', related)
    print(f"   ✅ Saved: {graph}")
    
    print("\n" + "="*50)
    print("✅ All demo charts generated!")
    print(f"📁 Location: {viz.output_dir}/")
    print("="*50)

if __name__ == '__main__':
    main()
