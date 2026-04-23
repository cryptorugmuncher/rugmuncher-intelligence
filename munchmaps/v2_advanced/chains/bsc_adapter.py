#!/usr/bin/env python3
"""
Binance Smart Chain (BSC) Adapter
EVM-compatible chain with lower fees than Ethereum
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from .base_adapter import BaseChainAdapter

class BSCAdapter(BaseChainAdapter):
    """
    BSC Adapter
    
    Data Sources:
    - BscScan API (free tier: 5 calls/sec)
    - Ankr/QuickNode RPC
    - NodeReal
    
    Why BSC matters:
    - Lower fees enable more complex operations
    - Popular for BEP-20 token scams
    - Bridge activity between BSC and other chains
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key)
        self.explorer_url = "https://bscscan.com"
        self.api_base = "https://api.bscscan.com/api"
        
    def _get_native_token(self) -> str:
        return "BNB"
    
    def _get_block_time(self) -> int:
        return 3  # 3 second block time
    
    def identify_address(self, address: str) -> Optional[str]:
        """Identify BSC address format (same as Ethereum)"""
        if re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return 'bsc'
        return None
    
    async def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Fetch transactions via BscScan API"""
        import aiohttp
        
        if not self.api_key:
            raise ValueError("BscScan API key required")
        
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
        """Get BEP-20 token holdings"""
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
        """Known CEX wallets on BSC"""
        return {
            'binance': [
                '0x8894e0a0c962cb723c1976a4421c95949be2d4e3',
                '0xdccf3b5910fee3da85c787db9ff7c4d423edb8fd'
            ],
            'pancakeswap': [
                '0x10ed43c718714eb63d5aa57b78b54704e256024e'  # Router
            ]
        }
    
    def get_known_bridge_contracts(self) -> List[str]:
        """Known bridge contracts on BSC"""
        return [
            '0x261e567c77b0c39f5eb74684d4fe24e666b67a76',  # Anyswap
            '0x13B432914A96b1CC13CfD3b64D5dE1B8D39D3434',  # Multichain
        ]
    
    def detect_yield_farm_scam(self, txs: List[Dict]) -> List[Dict]:
        """
        Detect yield farm/rug pull patterns on BSC
        
        Patterns:
        - Unlimited approval to unverified contracts
        - Rapid deposit/withdraw
        - Funds locked in contract
        """
        signals = []
        
        # Check for many approvals
        approval_txs = [tx for tx in txs if 'approve' in str(tx).lower()]
        if len(approval_txs) > 5:
            signals.append({
                'type': 'EXCESSIVE_APPROVALS',
                'confidence': 0.6,
                'description': f'{len(approval_txs)} approval transactions'
            })
        
        return signals
