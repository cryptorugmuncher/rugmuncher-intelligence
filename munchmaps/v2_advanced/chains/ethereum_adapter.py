#!/usr/bin/env python3
"""
Ethereum Chain Adapter
Most established chain with rich data availability
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from .base_adapter import BaseChainAdapter

class EthereumAdapter(BaseChainAdapter):
    """
    Ethereum Mainnet Adapter
    
    Data Sources:
    - Etherscan API (free tier: 5 calls/sec)
    - Alchemy/Infura (free tier available)
    - Blockscout (open source, free)
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key)
        self.explorer_url = "https://etherscan.io"
        self.api_base = "https://api.etherscan.io/api"
        
    def _get_native_token(self) -> str:
        return "ETH"
    
    def _get_block_time(self) -> int:
        return 12  # Seconds
    
    def identify_address(self, address: str) -> Optional[str]:
        """Identify Ethereum address format"""
        if re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return 'ethereum'
        return None
    
    async def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Fetch transactions via Etherscan API"""
        import aiohttp
        
        if not self.api_key:
            raise ValueError("Etherscan API key required")
        
        url = f"{self.api_base}"
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                
                if data.get('status') != '1':
                    return []
                
                txs = data.get('result', [])[:limit]
                return [self.normalize_transaction(tx) for tx in txs]
    
    async def get_wallet_age(self, address: str) -> Optional[Dict]:
        """Get wallet age from first transaction"""
        txs = await self.get_transactions(address, limit=1)
        
        if not txs:
            return None
        
        first_tx = txs[0]
        timestamp = first_tx.get('timestamp')
        
        if timestamp:
            try:
                dt = datetime.fromtimestamp(int(timestamp))
                age_days = (datetime.now() - dt).days
                
                return {
                    'first_transaction': dt.isoformat(),
                    'age_days': age_days,
                    'is_fresh': age_days < 7
                }
            except:
                pass
        
        return None
    
    async def detect_cex_funding(self, address: str) -> Optional[Dict]:
        """Detect CEX funding by checking first transactions"""
        cex_addresses = self.get_known_cex_addresses()
        txs = await self.get_transactions(address, limit=10)
        
        if not txs:
            return None
        
        # Check earliest transactions for CEX source
        earliest_txs = sorted(txs, key=lambda x: x.get('timestamp', 0))[:5]
        
        for tx in earliest_txs:
            from_addr = tx.get('from', '').lower()
            
            for cex_name, cex_addrs in cex_addresses.items():
                if from_addr in [a.lower() for a in cex_addrs]:
                    return {
                        'cex': cex_name,
                        'funding_tx': tx.get('hash'),
                        'amount': tx.get('value'),
                        'confidence': 0.9
                    }
        
        return None
    
    async def get_token_holdings(self, address: str) -> List[Dict]:
        """Get ERC-20 token holdings"""
        import aiohttp
        
        if not self.api_key:
            return []
        
        url = f"{self.api_base}"
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'sort': 'desc',
            'apikey': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                
                if data.get('status') != '1':
                    return []
                
                # Aggregate by token
                tokens = {}
                for tx in data.get('result', []):
                    token = tx.get('tokenSymbol')
                    if token:
                        if token not in tokens:
                            tokens[token] = {
                                'symbol': token,
                                'name': tx.get('tokenName'),
                                'contract': tx.get('contractAddress'),
                                'decimals': int(tx.get('tokenDecimal', 18))
                            }
                
                return list(tokens.values())
    
    def get_known_cex_addresses(self) -> Dict[str, List[str]]:
        """Known CEX hot wallets on Ethereum"""
        return {
            'binance': [
                '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bB',
                '0xdccf3b5910fee3da85c787db9ff7c4d423edb8fd',
                '0x28c6c06298d514db089934071355e5743bf21d60'
            ],
            'coinbase': [
                '0x71660c4005BA85c37ccec55d0C4493E66Fe775d3',
                '0x503828976dc04ce4a1987fe9b109e4e707dbe343'
            ],
            'kraken': [
                '0x267be1C1D684F78cb4F6a176C4911b741E4Fffdc',
                '0xfa22fafacf0c9c975da2def0cd2c471338c4f1f'
            ],
            'okx': [
                '0x6b75d8af000000e20b7a7ddf000ba900b4009a80'
            ],
            'bybit': [
                '0xf89d7b9c864f589bbf53a82105107622b35eaa40'
            ],
            'kucoin': [
                '0x2b5634c42055806a59e9107ed44d43c426e58258'
            ]
        }
    
    def get_known_bridge_contracts(self) -> List[str]:
        """Known bridge contracts on Ethereum"""
        return [
            '0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B',  # Wormhole
            '0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675',  # LayerZero
            '0x5427FEFA711Eff984124bFBB1AB6fbf5E3DA1820',  # Celer
            '0x4F4495243837681061C9723bB4b8EC5d51cD81c5',  # Axelar
            '0x8731d54E9D02c286767d56ac03e8037C07e01e98',  # Stargate
        ]
    
    def detect_pig_butcher_signals(self, txs: List[Dict]) -> List[Dict]:
        """
        Detect signals of pig butcher scam operations
        
        Patterns:
        - Small initial funding from CEX
        - Gradual increase in transaction sizes
        - Transfers to unlabeled addresses
        - Specific timing patterns (working hours)
        """
        signals = []
        
        if len(txs) < 5:
            return signals
        
        # Sort by time
        sorted_txs = sorted(txs, key=lambda x: x.get('timestamp', 0))
        
        # Check for gradual amount escalation
        amounts = []
        for tx in sorted_txs:
            try:
                val = float(tx.get('value', 0))
                amounts.append(val)
            except:
                pass
        
        if len(amounts) >= 3:
            # Check if amounts generally increase
            increases = sum(1 for i in range(1, len(amounts)) if amounts[i] > amounts[i-1])
            if increases / (len(amounts) - 1) > 0.7:  # 70% increasing
                signals.append({
                    'type': 'AMOUNT_ESCALATION',
                    'confidence': 0.7,
                    'description': 'Transaction amounts show consistent increase'
                })
        
        # Check for CEX origin
        earliest_from = sorted_txs[0].get('from', '').lower()
        cex_addrs = self.get_known_cex_addresses()
        
        for cex, addrs in cex_addrs.items():
            if earliest_from in [a.lower() for a in addrs]:
                signals.append({
                    'type': 'CEX_ORIGIN',
                    'cex': cex,
                    'confidence': 0.8,
                    'description': f'First transaction from {cex}'
                })
                break
        
        return signals
