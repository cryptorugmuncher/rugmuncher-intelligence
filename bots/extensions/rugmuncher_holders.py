#!/usr/bin/env python3
"""
💎 PAPER HANDS vs DIAMOND HANDS
Psychological analysis of holder behavior across ALL their tokens
Know WHO is holding, not just how many
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import sqlite3

@dataclass
class HolderPsychology:
    wallet: str
    hold_time_avg: float  # Average hold time in hours
    paper_hand_score: float  # 0-100, higher = more paper hands
    diamond_hand_score: float  # 0-100, higher = more diamond hands
    copy_trader_score: float  # 0-100, how much they copy others
    serial_dumper: bool  # Always dumps at certain multiples
    early_adopter: bool  # Gets in early on successful projects
    bag_holder: bool  # Holds losing positions too long
    total_projects_analyzed: int
    successful_gems_held: List[str]  # Projects they held to moon
    rugged_projects: List[str]  # Projects they got rugged on
    avg_sell_multiple: float  # Average multiple they sell at
    risk_profile: str  # CONSERVATIVE, MODERATE, DEGEN, WHALE
    
    def to_dict(self) -> Dict:
        return {
            'wallet': self.wallet,
            'hold_time_avg_hours': round(self.hold_time_avg, 1),
            'paper_hand_score': round(self.paper_hand_score, 1),
            'diamond_hand_score': round(self.diamond_hand_score, 1),
            'copy_trader_score': round(self.copy_trader_score, 1),
            'serial_dumper': self.serial_dumper,
            'early_adopter': self.early_adopter,
            'bag_holder': self.bag_holder,
            'total_projects_analyzed': self.total_projects_analyzed,
            'successful_gems_held': self.successful_gems_held[:5],
            'rugged_projects': self.rugged_projects[:5],
            'avg_sell_multiple': round(self.avg_sell_multiple, 2),
            'risk_profile': self.risk_profile
        }

class HolderDatabase:
    """Database for holder psychological profiles"""
    
    def __init__(self, db_path: str = '/root/rugmuncher_holders.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holder_profiles (
                wallet TEXT PRIMARY KEY,
                profile TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holder_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet TEXT,
                contract TEXT,
                chain TEXT,
                action TEXT,  -- BUY, SELL, HOLD
                amount REAL,
                price_usd REAL,
                timestamp TIMESTAMP,
                multiple_at_sale REAL  -- Profit multiple if sold
            )
        ''')
        
        self.conn.commit()
    
    def save_profile(self, wallet: str, profile: Dict):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO holder_profiles (wallet, profile, last_updated)
            VALUES (?, ?, ?)
        ''', (wallet.lower(), json.dumps(profile), datetime.now()))
        self.conn.commit()
    
    def get_profile(self, wallet: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT profile FROM holder_profiles WHERE wallet = ?', (wallet.lower(),))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def add_transaction(self, wallet: str, contract: str, chain: str,
                        action: str, amount: float, price_usd: float,
                        timestamp: datetime, multiple: float = None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO holder_transactions 
            (wallet, contract, chain, action, amount, price_usd, timestamp, multiple_at_sale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (wallet.lower(), contract.lower(), chain, action, amount, price_usd, timestamp, multiple))
        self.conn.commit()
    
    def get_wallet_history(self, wallet: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM holder_transactions 
            WHERE wallet = ? ORDER BY timestamp DESC
        ''', (wallet.lower(),))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

class HolderPsychologyAnalyzer:
    """Analyze holder psychology across all their token activity"""
    
    def __init__(self):
        self.db = HolderDatabase()
        self.known_moon_tokens = {
            'SHIB', 'DOGE', 'PEPE', 'FLOKI', 'BONK', 'SQUID',  # Meme legends
            'BTC', 'ETH', 'SOL', 'BNB',  # Major coins
        }
    
    async def analyze_wallet(self, wallet: str, chain: str = 'bsc') -> HolderPsychology:
        """
        Deep psychological analysis of a wallet's trading behavior
        """
        # Get cached profile if recent
        cached = self.db.get_profile(wallet)
        if cached and (datetime.now() - datetime.fromisoformat(cached.get('last_updated', '2000-01-01'))).days < 1:
            return self._dict_to_psychology(cached)
        
        # Fetch transaction history
        history = await self._fetch_wallet_history(wallet, chain)
        
        # Calculate metrics
        hold_times = []
        sell_multiples = []
        successful_gems = []
        rugged = []
        buy_prices = {}
        
        for tx in history:
            if tx['action'] == 'BUY':
                buy_prices[tx['contract']] = {
                    'price': tx['price_usd'],
                    'timestamp': tx['timestamp']
                }
            elif tx['action'] == 'SELL':
                if tx['contract'] in buy_prices:
                    buy_info = buy_prices[tx['contract']]
                    hold_time = (tx['timestamp'] - buy_info['timestamp']).total_seconds() / 3600
                    hold_times.append(hold_time)
                    
                    if tx['price_usd'] > 0 and buy_info['price'] > 0:
                        multiple = tx['price_usd'] / buy_info['price']
                        sell_multiples.append(multiple)
                        
                        # Track successful gems (10x+)
                        if multiple >= 10:
                            successful_gems.append(tx['contract'])
                        # Track rugs (sold at 90%+ loss)
                        elif multiple <= 0.1:
                            rugged.append(tx['contract'])
        
        # Calculate scores
        avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0
        avg_multiple = sum(sell_multiples) / len(sell_multiples) if sell_multiples else 1
        
        # Paper hand score (lower hold time, lower multiple = higher paper hands)
        paper_score = 0
        if avg_hold_time < 24:  # Sells within a day
            paper_score += 40
        elif avg_hold_time < 72:  # Sells within 3 days
            paper_score += 25
        elif avg_hold_time < 168:  # Sells within a week
            paper_score += 10
        
        if avg_multiple < 2:  # Always takes small profits
            paper_score += 30
        elif avg_multiple < 5:
            paper_score += 15
        
        # Diamond hand score
        diamond_score = 0
        if avg_hold_time > 720:  # Holds over a month
            diamond_score += 40
        elif avg_hold_time > 168:  # Holds over a week
            diamond_score += 25
        
        if avg_multiple >= 10:  # Has held to 10x+
            diamond_score += 30
        elif avg_multiple >= 5:
            diamond_score += 15
        
        diamond_score += len(successful_gems) * 5  # Bonus for each gem
        
        # Normalize scores
        paper_score = min(100, paper_score)
        diamond_score = min(100, diamond_score)
        
        # Determine risk profile
        if diamond_score > 70 and avg_hold_time > 500:
            risk_profile = 'DIAMOND_HAND'
        elif paper_score > 70:
            risk_profile = 'PAPER_HAND'
        elif avg_multiple > 20:
            risk_profile = 'DEGEN'
        elif len(successful_gems) >= 3:
            risk_profile = 'WHALE'
        else:
            risk_profile = 'MODERATE'
        
        # Serial dumper detection
        serial_dumper = avg_multiple < 3 and paper_score > 60
        
        # Early adopter detection
        early_adopter = len(successful_gems) >= 2
        
        # Bag holder detection
        bag_holder = avg_hold_time > 500 and avg_multiple < 1
        
        # Copy trader detection (would need social graph analysis)
        copy_score = 0  # Placeholder
        
        psychology = HolderPsychology(
            wallet=wallet,
            hold_time_avg=avg_hold_time,
            paper_hand_score=paper_score,
            diamond_hand_score=diamond_score,
            copy_trader_score=copy_score,
            serial_dumper=serial_dumper,
            early_adopter=early_adopter,
            bag_holder=bag_holder,
            total_projects_analyzed=len(history),
            successful_gems_held=successful_gems,
            rugged_projects=rugged,
            avg_sell_multiple=avg_multiple,
            risk_profile=risk_profile
        )
        
        # Cache result
        self.db.save_profile(wallet, psychology.to_dict())
        
        return psychology
    
    async def _fetch_wallet_history(self, wallet: str, chain: str) -> List[Dict]:
        """Fetch comprehensive wallet transaction history"""
        # Check database first
        history = self.db.get_wallet_history(wallet)
        
        if len(history) >= 10:
            return history
        
        # Fetch from blockchain APIs
        # This is a simplified version - production would use multiple sources
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        new_txs = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://{base}/api?module=account&action=tokentx&address={wallet}&page=1&offset=100&sort=desc&apikey={api_key}"
                async with session.get(url, timeout=10) as r:
                    data = await r.json()
                    if data.get('status') == '1':
                        for tx in data.get('result', []):
                            is_buy = tx.get('to', '').lower() == wallet.lower()
                            action = 'BUY' if is_buy else 'SELL'
                            
                            new_tx = {
                                'wallet': wallet,
                                'contract': tx.get('contractAddress'),
                                'chain': chain,
                                'action': action,
                                'amount': int(tx.get('value', 0)) / 1e18,
                                'price_usd': 0,  # Would need price oracle
                                'timestamp': datetime.fromtimestamp(int(tx.get('timeStamp', 0))),
                                'multiple_at_sale': None
                            }
                            new_txs.append(new_tx)
                            
                            # Store in database
                            self.db.add_transaction(
                                wallet, new_tx['contract'], chain, action,
                                new_tx['amount'], 0, new_tx['timestamp']
                            )
        except Exception as e:
            print(f"[Holder Analysis] Error fetching history: {e}")
        
        return history + new_txs
    
    def _dict_to_psychology(self, data: Dict) -> HolderPsychology:
        """Convert dict back to HolderPsychology object"""
        return HolderPsychology(
            wallet=data['wallet'],
            hold_time_avg=data['hold_time_avg_hours'],
            paper_hand_score=data['paper_hand_score'],
            diamond_hand_score=data['diamond_hand_score'],
            copy_trader_score=data['copy_trader_score'],
            serial_dumper=data['serial_dumper'],
            early_adopter=data['early_adopter'],
            bag_holder=data['bag_holder'],
            total_projects_analyzed=data['total_projects_analyzed'],
            successful_gems_held=data['successful_gems_held'],
            rugged_projects=data['rugged_projects'],
            avg_sell_multiple=data['avg_sell_multiple'],
            risk_profile=data['risk_profile']
        )
    
    def format_psychology(self, psych: HolderPsychology) -> str:
        """Format holder psychology for display"""
        
        # Determine primary trait
        if psych.diamond_hand_score > psych.paper_hand_score:
            primary_trait = f"💎 DIAMOND HANDS ({psych.diamond_hand_score:.0f}/100)"
            trait_emoji = "💎"
        else:
            primary_trait = f"🧻 PAPER HANDS ({psych.paper_hand_score:.0f}/100)"
            trait_emoji = "🧻"
        
        text = f"""
{trait_emoji} <b>HOLDER PSYCHOLOGY PROFILE</b> {trait_emoji}

<b>Wallet:</b> <code>{psych.wallet[:16]}...</code>

╔════════════════════════════════════════════════╗
║  <b>{primary_trait}</b>
╚════════════════════════════════════════════════╝

<b>📊 BEHAVIORAL METRICS:</b>
• Avg Hold Time: <code>{psych.hold_time_avg:.1f} hours</code>
• Avg Sell Multiple: <code>{psych.avg_sell_multiple:.2f}x</code>
• Projects Analyzed: <code>{psych.total_projects_analyzed}</code>
• Risk Profile: <code>{psych.risk_profile}</code>

<b>💎 DIAMOND HAND SCORE:</b> <code>{psych.diamond_hand_score:.0f}/100</code>
<b>🧻 PAPER HAND SCORE:</b> <code>{psych.paper_hand_score:.0f}/100</code>
"""
        
        if psych.successful_gems_held:
            text += f"""
<b>🏆 SUCCESSFUL GEMS HELD:</b>
• {len(psych.successful_gems_held)} projects to 10x+
"""
        
        if psych.rugged_projects:
            text += f"""
<b>💀 RUGGED ON:</b>
• {len(psych.rugged_projects)} projects
"""
        
        # Add trait analysis
        text += """
<b>🧠 PSYCHOLOGICAL TRAITS:</b>
"""
        
        if psych.serial_dumper:
            text += "• Serial Dumper: Always sells early (under 3x)\n"
        if psych.early_adopter:
            text += "• Early Adopter: Gets into gems before they pump\n"
        if psych.bag_holder:
            text += "• Bag Holder: Holds losing positions too long\n"
        
        return text

class TokenHolderAnalysis:
    """Analyze all holders of a specific token"""
    
    def __init__(self):
        self.analyzer = HolderPsychologyAnalyzer()
    
    async def analyze_token_holders(self, contract: str, chain: str) -> Dict:
        """
        Get psychological profile of all major holders
        """
        # Get top holders
        holders = await self._get_top_holders(contract, chain, limit=20)
        
        analysis = {
            'contract': contract,
            'chain': chain,
            'total_holders': len(holders),
            'psychology_breakdown': {
                'DIAMOND_HAND': 0,
                'PAPER_HAND': 0,
                'DEGEN': 0,
                'WHALE': 0,
                'MODERATE': 0
            },
            'avg_hold_time': 0,
            'whales': [],  # High-value diamond hands
            'paper_hands': [],  # Likely to dump
            'risk_assessment': ''
        }
        
        total_hold_time = 0
        
        for holder in holders:
            try:
                psych = await self.analyzer.analyze_wallet(holder['address'], chain)
                
                analysis['psychology_breakdown'][psych.risk_profile] += holder['percentage']
                total_hold_time += psych.hold_time_avg
                
                if psych.risk_profile in ['DIAMOND_HAND', 'WHALE'] and holder['percentage'] > 2:
                    analysis['whales'].append({
                        'wallet': holder['address'][:12] + '...',
                        'percentage': holder['percentage'],
                        'diamond_score': psych.diamond_hand_score,
                        'avg_hold': psych.hold_time_avg
                    })
                
                if psych.paper_hand_score > 70 and holder['percentage'] > 1:
                    analysis['paper_hands'].append({
                        'wallet': holder['address'][:12] + '...',
                        'percentage': holder['percentage'],
                        'paper_score': psych.paper_hand_score,
                        'likely_dump': 'YES' if psych.serial_dumper else 'MAYBE'
                    })
                    
            except Exception as e:
                print(f"[Token Analysis] Error analyzing holder {holder['address']}: {e}")
        
        if holders:
            analysis['avg_hold_time'] = total_hold_time / len(holders)
        
        # Risk assessment
        paper_pct = analysis['psychology_breakdown']['PAPER_HAND']
        diamond_pct = analysis['psychology_breakdown']['DIAMOND_HAND'] + analysis['psychology_breakdown']['WHALE']
        
        if paper_pct > 30:
            analysis['risk_assessment'] = f"🚨 HIGH RISK: {paper_pct:.1f}% held by paper hands - expect heavy dumping"
        elif diamond_pct > 40:
            analysis['risk_assessment'] = f"🟢 STRONG: {diamond_pct:.1f}% held by diamond hands - good support"
        else:
            analysis['risk_assessment'] = f"🟡 MIXED: Holder psychology is neutral"
        
        return analysis
    
    async def _get_top_holders(self, contract: str, chain: str, limit: int = 20) -> List[Dict]:
        """Fetch top token holders"""
        # This would use blockchain API
        # Simplified placeholder
        return [
            {'address': f'0x{i:040x}', 'percentage': 5.0 - (i * 0.2)}
            for i in range(limit)
        ]
    
    def format_token_analysis(self, analysis: Dict) -> str:
        """Format token holder analysis"""
        text = f"""
👥 <b>TOKEN HOLDER PSYCHOLOGY</b>

<b>Contract:</b> <code>{analysis['contract'][:16]}...</code>
<b>Analyzed:</b> {analysis['total_holders']} major holders

<b>📊 PSYCHOLOGY BREAKDOWN:</b>
"""
        for profile, pct in analysis['psychology_breakdown'].items():
            if pct > 0:
                emoji = "💎" if profile == 'DIAMOND_HAND' else "🧻" if profile == 'PAPER_HAND' else "🐋" if profile == 'WHALE' else "🎰" if profile == 'DEGEN' else "⚖️"
                text += f"• {emoji} {profile}: {pct:.1f}%\n"
        
        text += f"""
<b>⏱️ Avg Hold Time:</b> {analysis['avg_hold_time']:.1f} hours

<b>{analysis['risk_assessment']}</b>
"""
        
        if analysis['whales']:
            text += """
<b>💎 DIAMOND HAND WHALES:</b>
"""
            for whale in analysis['whales'][:5]:
                text += f"• {whale['wallet']} ({whale['percentage']:.1f}%) - Score: {whale['diamond_score']:.0f}\n"
        
        if analysis['paper_hands']:
            text += """
<b>🧻 PAPER HANDS TO WATCH:</b>
"""
            for paper in analysis['paper_hands'][:5]:
                text += f"• {paper['wallet']} ({paper['percentage']:.1f}%) - {paper['likely_dump']}\n"
        
        return text

# ═══════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════

async def main():
    analyzer = HolderPsychologyAnalyzer()
    
    # Analyze a wallet
    psych = await analyzer.analyze_wallet('0x1234567890abcdef', 'bsc')
    print(analyzer.format_psychology(psych))

if __name__ == "__main__":
    asyncio.run(main())
