#!/usr/bin/env python3
"""
💼 WALLET ANALYZER MODULE
=========================
Deep wallet forensics for scam detection
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json

@dataclass
class WalletProfile:
    address: str
    chain: str
    balance_eth: float
    transaction_count: int
    first_seen: Optional[datetime]
    last_active: Optional[datetime]
    tags: List[str] = field(default_factory=list)
    risk_score: int = 0
    deployed_contracts: List[Dict] = field(default_factory=list)
    token_balances: List[Dict] = field(default_factory=list)
    related_wallets: List[str] = field(default_factory=list)
    interaction_patterns: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

class WalletAnalyzer:
    """Advanced wallet forensics"""
    
    def __init__(self, etherscan_key: str = '', bscscan_key: str = ''):
        self.etherscan_key = etherscan_key
        self.bscscan_key = bscscan_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    def _get_api_config(self, chain: str) -> tuple:
        """Get API key and base URL for chain"""
        if chain == 'eth':
            return self.etherscan_key, 'api.etherscan.io'
        elif chain == 'bsc':
            return self.bscscan_key, 'api.bscscan.com'
        return '', 'api.etherscan.io'
    
    async def analyze(self, address: str, chain: str = 'eth') -> WalletProfile:
        """Complete wallet analysis"""
        profile = WalletProfile(
            address=address,
            chain=chain,
            balance_eth=0,
            transaction_count=0,
            first_seen=None,
            last_active=None
        )
        
        # Get basic info
        await self._get_balance(profile)
        await self._get_transactions(profile)
        await self._get_token_balances(profile)
        await self._get_deployed_contracts(profile)
        
        # Analysis
        self._analyze_patterns(profile)
        self._calculate_risk(profile)
        
        return profile
    
    async def _get_balance(self, profile: WalletProfile):
        """Get ETH/BNB balance"""
        api_key, base = self._get_api_config(profile.chain)
        url = f"https://{base}/api?module=account&action=balance&address={profile.address}&tag=latest&apikey={api_key}"
        
        try:
            async with self.session.get(url, timeout=10) as resp:
                data = await resp.json()
                if data.get('status') == '1':
                    wei = int(data['result'])
                    profile.balance_eth = wei / 1e18
        except Exception as e:
            print(f"Balance error: {e}")
    
    async def _get_transactions(self, profile: WalletProfile):
        """Get transaction history"""
        api_key, base = self._get_api_config(profile.chain)
        url = f"https://{base}/api?module=account&action=txlist&address={profile.address}&page=1&offset=100&apikey={api_key}"
        
        try:
            async with self.session.get(url, timeout=10) as resp:
                data = await resp.json()
                if data.get('status') == '1':
                    txs = data.get('result', [])
                    profile.transaction_count = len(txs)
                    
                    if txs:
                        timestamps = [int(tx['timeStamp']) for tx in txs if tx.get('timeStamp')]
                        if timestamps:
                            profile.first_seen = datetime.fromtimestamp(min(timestamps))
                            profile.last_active = datetime.fromtimestamp(max(timestamps))
                        
                        # Analyze interaction patterns
                        profile.interaction_patterns = self._analyze_transactions(txs)
        except Exception as e:
            print(f"Transaction error: {e}")
    
    async def _get_token_balances(self, profile: WalletProfile):
        """Get ERC-20 token balances"""
        api_key, base = self._get_api_config(profile.chain)
        url = f"https://{base}/api?module=account&action=tokentx&address={profile.address}&page=1&offset=50&apikey={api_key}"
        
        try:
            async with self.session.get(url, timeout=10) as resp:
                data = await resp.json()
                if data.get('status') == '1':
                    txs = data.get('result', [])
                    tokens = defaultdict(lambda: {'in': 0, 'out': 0, 'value': 0})
                    
                    for tx in txs:
                        token = tx.get('tokenSymbol', 'UNKNOWN')
                        to = tx.get('to', '').lower()
                        from_addr = tx.get('from', '').lower()
                        value = int(tx.get('value', 0)) / (10 ** int(tx.get('tokenDecimal', 18)))
                        
                        if to == profile.address.lower():
                            tokens[token]['in'] += 1
                            tokens[token]['value'] += value
                        elif from_addr == profile.address.lower():
                            tokens[token]['out'] += 1
                            tokens[token]['value'] -= value
                    
                    profile.token_balances = [
                        {'symbol': k, 'transfers_in': v['in'], 'transfers_out': v['out'], 'net_value': v['value']}
                        for k, v in tokens.items()
                    ]
        except Exception as e:
            print(f"Token error: {e}")
    
    async def _get_deployed_contracts(self, profile: WalletProfile):
        """Get contracts deployed by this wallet"""
        api_key, base = self._get_api_config(profile.chain)
        url = f"https://{base}/api?module=account&action=txlist&address={profile.address}&page=1&offset=100&apikey={api_key}"
        
        try:
            async with self.session.get(url, timeout=10) as resp:
                data = await resp.json()
                if data.get('status') == '1':
                    txs = data.get('result', [])
                    contracts = []
                    
                    for tx in txs:
                        if tx.get('contractAddress'):
                            contracts.append({
                                'address': tx['contractAddress'],
                                'timestamp': datetime.fromtimestamp(int(tx['timeStamp'])),
                                'tx_hash': tx['hash']
                            })
                    
                    profile.deployed_contracts = contracts
                    if contracts:
                        profile.tags.append('deployer')
        except Exception as e:
            print(f"Contract error: {e}")
    
    def _analyze_transactions(self, txs: List[Dict]) -> Dict:
        """Analyze transaction patterns"""
        patterns = {
            'unique_interactions': set(),
            'most_active_hour': None,
            'avg_gas_price': 0,
            'failed_txs': 0
        }
        
        hours = defaultdict(int)
        gas_prices = []
        
        for tx in txs:
            # Track unique addresses
            if tx.get('to'):
                patterns['unique_interactions'].add(tx['to'])
            if tx.get('from'):
                patterns['unique_interactions'].add(tx['from'])
            
            # Hour of activity
            if tx.get('timeStamp'):
                hour = datetime.fromtimestamp(int(tx['timeStamp'])).hour
                hours[hour] += 1
            
            # Gas price
            if tx.get('gasPrice'):
                gas_prices.append(int(tx['gasPrice']))
            
            # Failed transactions
            if tx.get('isError') == '1':
                patterns['failed_txs'] += 1
        
        if hours:
            patterns['most_active_hour'] = max(hours, key=hours.get)
        if gas_prices:
            patterns['avg_gas_price'] = sum(gas_prices) / len(gas_prices) / 1e9  # Gwei
        patterns['unique_interactions'] = len(patterns['unique_interactions'])
        
        return patterns
    
    def _analyze_patterns(self, profile: WalletProfile):
        """Detect suspicious patterns"""
        # Fresh wallet check
        if profile.transaction_count < 10:
            profile.tags.append('fresh_wallet')
            profile.warnings.append("👶 Fresh wallet - recently created")
        
        # Inactive check
        if profile.last_active:
            days_inactive = (datetime.now() - profile.last_active).days
            if days_inactive > 365:
                profile.tags.append('dormant')
                profile.warnings.append(f"💤 Wallet dormant for {days_inactive} days")
        
        # Whale check
        if profile.balance_eth > 100:
            profile.tags.append('whale')
        
        # High failure rate
        if profile.interaction_patterns.get('failed_txs', 0) > profile.transaction_count * 0.2:
            profile.warnings.append("⚠️ High transaction failure rate")
        
        # Deployer check
        if profile.deployed_contracts:
            profile.warnings.append(f"📄 Deployed {len(profile.deployed_contracts)} contracts")
    
    def _calculate_risk(self, profile: WalletProfile):
        """Calculate overall risk score"""
        score = 0
        
        # Fresh wallet = higher risk
        if 'fresh_wallet' in profile.tags:
            score += 20
        
        # No activity = medium risk
        if 'dormant' in profile.tags:
            score += 15
        
        # Multiple contract deployments
        if len(profile.deployed_contracts) > 5:
            score += 10
        
        # High failure rate
        if profile.interaction_patterns.get('failed_txs', 0) > 10:
            score += 15
        
        profile.risk_score = min(100, score)
    
    async def get_related_wallets(self, address: str, chain: str = 'eth', depth: int = 1) -> List[str]:
        """Find wallets related through transactions"""
        api_key, base = self._get_api_config(chain)
        url = f"https://{base}/api?module=account&action=txlist&address={address}&page=1&offset=50&apikey={api_key}"
        
        related = set()
        
        try:
            async with self.session.get(url, timeout=10) as resp:
                data = await resp.json()
                if data.get('status') == '1':
                    for tx in data.get('result', []):
                        if tx.get('from'):
                            related.add(tx['from'])
                        if tx.get('to'):
                            related.add(tx['to'])
        except Exception as e:
            print(f"Related wallets error: {e}")
        
        return list(related - {address})

# Test
async def test():
    analyzer = WalletAnalyzer(
        etherscan_key='YourEtherscanKey',
        bscscan_key='YourBscscanKey'
    )
    
    async with analyzer:
        # Example: Analyze a wallet
        profile = await analyzer.analyze('0x742d35Cc6634C0532925a3b844Bc9e7595f0b0d2', 'eth')
        print(f"Address: {profile.address}")
        print(f"Balance: {profile.balance_eth:.4f} ETH")
        print(f"Transactions: {profile.transaction_count}")
        print(f"Risk Score: {profile.risk_score}")
        print(f"Tags: {profile.tags}")
        print(f"Warnings: {profile.warnings}")

if __name__ == '__main__':
    asyncio.run(test())
