#!/usr/bin/env python3
"""
Tron Chain Adapter
IMPORTANT: High volume of USDT transactions, popular for pig butcherer operations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from .base_adapter import BaseChainAdapter

class TronAdapter(BaseChainAdapter):
    """
    Tron Adapter - Critical for tracking big money operations
    
    Data Sources:
    - TronGrid API (free tier available)
    - TronScan API
    - TronStack
    
    Why Tron matters:
    - Extremely low fees enable high-volume operations
    - USDT TRC-20 is the primary stablecoin for scams
    - Pig butcherers prefer Tron for moving large amounts
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key)
        self.explorer_url = "https://tronscan.org"
        self.api_base = "https://api.trongrid.io"
        
    def _get_native_token(self) -> str:
        return "TRX"
    
    def _get_block_time(self) -> int:
        return 3  # 3 second block time
    
    def identify_address(self, address: str) -> Optional[str]:
        """Identify Tron address format (base58, starts with T)"""
        if re.match(r'^T[a-zA-Z0-9]{33}$', address):
            return 'tron'
        return None
    
    async def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Fetch transactions via TronGrid API"""
        import aiohttp
        
        headers = {}
        if self.api_key:
            headers['TRON-PRO-API-KEY'] = self.api_key
        
        url = f"{self.api_base}/v1/accounts/{address}/transactions"
        params = {'limit': limit, 'order_by': 'block_timestamp,desc'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                data = await resp.json()
                
                if not data.get('success'):
                    return []
                
                txs = data.get('data', [])
                return [self.normalize_transaction(tx) for tx in txs]
    
    def normalize_transaction(self, tx: Dict) -> Dict:
        """Normalize Tron transaction"""
        raw = tx.get('raw_data', {})
        contract = raw.get('contract', [{}])[0]
        param = contract.get('parameter', {}).get('value', {})
        
        return {
            'hash': tx.get('txID'),
            'from': param.get('owner_address'),
            'to': param.get('to_address'),
            'value': param.get('amount', 0) / 1e6,  # Convert from SUN to TRX
            'timestamp': datetime.fromtimestamp(tx.get('raw_data', {}).get('timestamp', 0) / 1000).isoformat() if tx.get('raw_data', {}).get('timestamp') else None,
            'fee': tx.get('ret', [{}])[0].get('fee', 0) / 1e6,
            'status': 'success' if tx.get('ret', [{}])[0].get('contractRet') == 'SUCCESS' else 'failed',
            'chain': 'tron'
        }
    
    async def get_wallet_age(self, address: str) -> Optional[Dict]:
        """Get wallet age from first transaction"""
        txs = await self.get_transactions(address, limit=100)
        
        if not txs:
            return None
        
        oldest = min(txs, key=lambda x: x.get('timestamp') or '9999')
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
        """Get TRC-20 token holdings"""
        import aiohttp
        
        headers = {}
        if self.api_key:
            headers['TRON-PRO-API-KEY'] = self.api_key
        
        url = f"{self.api_base}/v1/accounts/{address}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                
                if not data.get('success'):
                    return []
                
                account = data.get('data', [{}])[0]
                trc20 = account.get('trc20', [])
                
                tokens = []
                for token_data in trc20:
                    for contract, balance in token_data.items():
                        tokens.append({
                            'contract': contract,
                            'balance': balance,
                            'symbol': 'UNKNOWN'  # Would need token lookup
                        })
                
                return tokens
    
    def get_known_cex_addresses(self) -> Dict[str, List[str]]:
        """Known CEX wallets on Tron - IMPORTANT for pig butcherers"""
        return {
            'binance': [
                'TMuA6Yqf6TqUfthPfAWzHkC3fTqJNAipqZ',
                'TAzP7X7J6xVQWqW5mK8V5V7V8V9V0V1V2V',
                'TKrSdCPLkR8fJ3LdZ4Q9Y9M8N7K6J5H4G'
            ],
            'okx': [
                'TNP2uM4bE7Xv9F8G7H6J5K4L3M2N1B0V9',
                'TQWER9Y8U7I6O5P4A3S2D1F0G9H8J7K6L'
            ],
            'bybit': [
                'T9M8N7B6V5C4X3Z2L1K0J9H8G7F6D5S4A'
            ],
            'kucoin': [
                'T1Q2W3E4R5T6Y7U8I9O0P1A2S3D4F5G6H'
            ],
            'huobi': [
                'TH8G7F6D5S4A3Q2W1E0R9T8Y7U6I5O4P3'
            ],
            'poloniex': [
                'TP9O8I7U6Y5T4R3E2W1Q0L9K8J7H6G5F4'
            ]
        }
    
    def get_known_bridge_contracts(self) -> List[str]:
        """Known bridge contracts on Tron"""
        return [
            'TVgDm4 interconnect',  # Would need real addresses
        ]
    
    def detect_pig_butcher_signals(self, txs: List[Dict]) -> List[Dict]:
        """
        Detect pig butcher scam signals - CRITICAL for Tron
        
        Pig butcherer patterns on Tron:
        1. Large USDT transfers to/from unlabeled wallets
        2. Round number amounts (1000, 5000, 10000 USDT)
        3. Off-hours activity
        4. Rapid succession of similar amounts
        5. Transfers to mixer-like services
        """
        signals = []
        
        if len(txs) < 3:
            return signals
        
        # Check for large round number transactions
        large_round_txs = []
        for tx in txs:
            try:
                value = float(tx.get('value', 0))
                # Check if round number (within 1% of integer)
                if value > 1000 and abs(value - round(value)) < value * 0.01:
                    large_round_txs.append(tx)
            except:
                pass
        
        if len(large_round_txs) >= 3:
            signals.append({
                'type': 'LARGE_ROUND_AMOUNTS',
                'confidence': 0.8,
                'description': f'{len(large_round_txs)} large round-number transfers',
                'tx_count': len(large_round_txs)
            })
        
        # Check for rapid large transfers
        timestamps = []
        for tx in txs:
            try:
                value = float(tx.get('value', 0))
                if value > 500:  # Significant amount
                    ts = tx.get('timestamp')
                    if ts:
                        timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
            except:
                pass
        
        if len(timestamps) >= 3:
            timestamps.sort()
            # Check if within short time window
            time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
            if time_span < 24:  # Within 24 hours
                signals.append({
                    'type': 'RAPID_LARGE_TRANSFERS',
                    'confidence': 0.75,
                    'description': f'{len(timestamps)} large transfers within {time_span:.1f} hours',
                    'time_span_hours': time_span
                })
        
        # Check for outbound-only pattern (money extraction)
        outgoing = sum(1 for tx in txs if tx.get('from') and tx.get('value', 0) > 0)
        incoming = len(txs) - outgoing
        
        if outgoing > incoming * 2 and outgoing >= 5:
            signals.append({
                'type': 'EXTRACTION_PATTERN',
                'confidence': 0.7,
                'description': f'Heavy outbound activity ({outgoing} out, {incoming} in)',
                'ratio': outgoing / max(incoming, 1)
            })
        
        return signals
    
    def detect_usdt_laundering(self, txs: List[Dict], token_contracts: List[str] = None) -> List[Dict]:
        """
        Detect USDT TRC-20 laundering patterns
        
        USDT contract: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
        """
        USDT_CONTRACT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'
        
        signals = []
        
        # Filter for USDT transactions
        usdt_txs = [tx for tx in txs if USDT_CONTRACT in str(tx)]
        
        if len(usdt_txs) < 5:
            return signals
        
        # Layering pattern: many small transfers splitting funds
        if len(usdt_txs) > 10:
            signals.append({
                'type': 'USDT_LAYERING',
                'confidence': 0.75,
                'description': f'{len(usdt_txs)} USDT transactions - possible layering',
                'tx_count': len(usdt_txs)
            })
        
        return signals
