#!/usr/bin/env python3
"""
Polygon (Matic) Adapter
Ethereum L2 with fast, cheap transactions
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from .base_adapter import BaseChainAdapter

class PolygonAdapter(BaseChainAdapter):
    """
    Polygon Adapter
    
    Data Sources:
    - PolygonScan API (free tier)
    - Alchemy/Infura
    - QuickNode
    
    Why Polygon matters:
    - Fast finality (2s blocks)
    - Low fees
    - Growing DeFi ecosystem
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key)
        self.explorer_url = "https://polygonscan.com"
        self.api_base = "https://api.polygonscan.com/api"
        
    def _get_native_token(self) -> str:
        return "MATIC"
    
    def _get_block_time(self) -> int:
        return 2  # 2 second block time
    
    def identify_address(self, address: str) -> Optional[str]:
        """Identify Polygon address format (same as Ethereum)"""
        if re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return 'polygon'
        return None
    
    async def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Fetch transactions via PolygonScan API"""
        import aiohttp
        
        if not self.api_key:
            raise ValueError("PolygonScan API key required")
        
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
        """Detect CEX funding"""
        txs = await self.get_transactions(address, limit=10)
        
        if not txs:
            return None
        
        earliest = sorted(txs, key=lambda x: x.get('timestamp', 0))[:5]
        cex_addrs = self.get_known_cex_addresses()
        
        for tx in earliest:
            from_addr = tx.get('from', '').lower()
            
            for cex_name, cex_list in cex_addrs.items():
                if from_addr in [a.lower() for a in cex_list]:
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
        """Known CEX wallets on Polygon"""
        return {
            'binance': [
                '0x5a52e96bacdabb82fd05763e25335261b270efcb'
            ],
            'coinbase': [
                '0x71660c4005ba85c37ccec55d0c4493e66fe775d3'
            ]
        }
    
    def get_known_bridge_contracts(self) -> List[str]:
        """Known bridge contracts on Polygon"""
        return [
            '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0',  # POS Bridge
            '0xA0c68C638235ee32657e8f720a23ceC1bFc77C77',  # Plasma Bridge
        ]
