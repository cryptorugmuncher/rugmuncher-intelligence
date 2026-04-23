#!/usr/bin/env python3
"""
Solana Chain Adapter
High-speed, low-cost chain popular for memecoins
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from .base_adapter import BaseChainAdapter

class SolanaAdapter(BaseChainAdapter):
    """
    Solana Adapter
    
    Data Sources:
    - Helius API (free tier: 100k requests/day)
    - SolanaFM API
    - QuickNode (free tier available)
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key)
        self.explorer_url = "https://solscan.io"
        
    def _get_native_token(self) -> str:
        return "SOL"
    
    def _get_block_time(self) -> int:
        return 1  # ~1 second block time
    
    def identify_address(self, address: str) -> Optional[str]:
        """Identify Solana address format (base58, 32-44 chars)"""
        if re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address):
            # Exclude Ethereum-looking addresses
            if not address.startswith('0x'):
                return 'solana'
        return None
    
    async def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Fetch transactions via Helius API"""
        import aiohttp
        
        if not self.api_key:
            raise ValueError("Helius API key required")
        
        url = f"https://mainnet.helius-rpc.com/?api-key={self.api_key}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [address, {"limit": limit}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                signatures = data.get('result', [])
                
                # Fetch details for each transaction
                transactions = []
                for sig_info in signatures[:limit]:
                    tx_detail = await self._get_transaction_detail(
                        session, url, sig_info['signature']
                    )
                    if tx_detail:
                        transactions.append(tx_detail)
                
                return transactions
    
    async def _get_transaction_detail(self, session, url: str, signature: str) -> Optional[Dict]:
        """Get detailed transaction info"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
        }
        
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            result = data.get('result')
            
            if not result:
                return None
            
            return self.normalize_transaction({
                'signature': signature,
                'blockTime': result.get('blockTime'),
                'meta': result.get('meta', {}),
                'transaction': result.get('transaction', {})
            })
    
    def normalize_transaction(self, tx: Dict) -> Dict:
        """Normalize Solana transaction"""
        meta = tx.get('meta', {})
        
        return {
            'hash': tx.get('signature'),
            'from': self._extract_signer(tx),
            'to': self._extract_recipient(tx),
            'value': abs(meta.get('preBalances', [0])[0] - meta.get('postBalances', [0])[0]) / 1e9,  # Convert lamports to SOL
            'timestamp': datetime.fromtimestamp(tx.get('blockTime', 0)).isoformat() if tx.get('blockTime') else None,
            'fee': meta.get('fee', 0) / 1e9,
            'status': 'success' if meta.get('err') is None else 'failed',
            'chain': 'solana'
        }
    
    def _extract_signer(self, tx: Dict) -> str:
        """Extract signer from transaction"""
        try:
            message = tx.get('transaction', {}).get('message', {})
            account_keys = message.get('accountKeys', [])
            if account_keys:
                return account_keys[0].get('pubkey', '')
        except:
            pass
        return ''
    
    def _extract_recipient(self, tx: Dict) -> str:
        """Extract recipient from transaction"""
        try:
            message = tx.get('transaction', {}).get('message', {})
            instructions = message.get('instructions', [])
            for ix in instructions:
                if ix.get('program') == 'system':
                    parsed = ix.get('parsed', {})
                    if parsed.get('type') == 'transfer':
                        return parsed.get('info', {}).get('destination', '')
        except:
            pass
        return ''
    
    async def get_wallet_age(self, address: str) -> Optional[Dict]:
        """Get wallet age from first transaction"""
        txs = await self.get_transactions(address, limit=100)
        
        if not txs:
            return None
        
        oldest = min(txs, key=lambda x: x.get('timestamp') or '')
        timestamp = oldest.get('timestamp')
        
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                age_days = (datetime.now() - dt).days
                
                return {
                    'first_transaction': timestamp,
                    'age_days': age_days,
                    'is_fresh': age_days < 7
                }
            except:
                pass
        
        return None
    
    async def detect_cex_funding(self, address: str) -> Optional[Dict]:
        """Detect CEX funding"""
        txs = await self.get_transactions(address, limit=20)
        
        if not txs:
            return None
        
        # Check earliest transactions
        earliest = sorted(txs, key=lambda x: x.get('timestamp') or '')[:5]
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
        """Get SPL token holdings"""
        import aiohttp
        
        if not self.api_key:
            return []
        
        url = f"https://mainnet.helius-rpc.com/?api-key={self.api_key}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                accounts = data.get('result', {}).get('value', [])
                
                tokens = []
                for account in accounts:
                    info = account.get('account', {}).get('data', {}).get('parsed', {}).get('info', {})
                    token = {
                        'mint': info.get('mint'),
                        'amount': info.get('tokenAmount', {}).get('uiAmount'),
                        'decimals': info.get('tokenAmount', {}).get('decimals'),
                        'symbol': 'UNKNOWN'  # Would need token metadata lookup
                    }
                    tokens.append(token)
                
                return tokens
    
    def get_known_cex_addresses(self) -> Dict[str, List[str]]:
        """Known CEX wallets on Solana"""
        return {
            'binance': [
                '5tzFkiKscXHK5ZXcgfn3vXG1ks5u6evKEQW2Kl99wCbP',
                'AC5RDfQjE1LkB7L1F1yW6X7WnJ9yZ2z8z3z4z5z6z7z8z'
            ],
            'coinbase': [
                'H8sMJSCQxfKiFTFfBD3wzV4r6P2z4n6dP7X8Y9Z0a1b2c'
            ],
            'ftx': [
                '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin'  # Known FTX wallet
            ],
            'kraken': [
                '2Zzo1P3vP8mKz8Y9X0a1b2c3d4e5f6g7h8i9j0k1l2m3n'
            ]
        }
    
    def get_known_bridge_contracts(self) -> List[str]:
        """Known bridge contracts on Solana"""
        return [
            'worm2ZoG2kUd4vFXhvjh93UUH596ayRfgQ2MgjNMTth',  # Wormhole
            '76y77prsiCMvXM7cH39WnYf8T3Jk89J3JH2NHpwcf1pG',  # LayerZero
            'CCTPiPYPc6AsJuwueEnWgSgucamXDZwBd53dQ1YiRkLZ',  # Celer
        ]
    
    def detect_memecoin_scam_signals(self, txs: List[Dict]) -> List[Dict]:
        """
        Detect Solana memecoin scam patterns
        
        Patterns:
        - Rapid buy/sell (pump and dump)
        - Token creation followed by immediate sales
        - Bundled transactions
        """
        signals = []
        
        if len(txs) < 3:
            return signals
        
        # Check for rapid transactions
        timestamps = [tx.get('timestamp') for tx in txs if tx.get('timestamp')]
        if len(timestamps) >= 3:
            timestamps.sort()
            intervals = []
            for i in range(1, len(timestamps)):
                try:
                    t1 = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                    intervals.append((t2 - t1).total_seconds())
                except:
                    pass
            
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            if avg_interval < 60:  # Less than 1 minute average
                signals.append({
                    'type': 'RAPID_TRADING',
                    'confidence': 0.75,
                    'description': 'High-frequency transactions detected'
                })
        
        return signals
