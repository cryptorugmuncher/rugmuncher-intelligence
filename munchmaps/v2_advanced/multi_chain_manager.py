#!/usr/bin/env python3
"""
Multi-Chain Manager - Unified interface for all chains
Ensures reliable data collection and cross-chain correlation
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')
sys.path.insert(0, '/root/rmi/munchmaps/v2_advanced/chains')

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

from chains import CHAIN_ADAPTERS, SUPPORTED_CHAINS
from chains.base_adapter import ChainDataReliabilityChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiChainManager:
    """
    Manages data collection across multiple blockchains
    Provides unified interface and reliability checking
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize with API keys for each chain
        
        api_keys format: {
            'ethereum': 'etherscan_key',
            'solana': 'helius_key',
            'tron': 'trongrid_key',
            'bsc': 'bscscan_key',
            'polygon': 'polygonscan_key'
        }
        """
        self.api_keys = api_keys or {}
        self.adapters = {}
        self.reliability_checker = ChainDataReliabilityChecker()
        
        # Initialize adapters
        for chain_name in SUPPORTED_CHAINS:
            adapter_class = CHAIN_ADAPTERS.get(chain_name)
            if adapter_class:
                self.adapters[chain_name] = adapter_class(
                    api_key=self.api_keys.get(chain_name)
                )
        
        logger.info(f"Initialized MultiChainManager with {len(self.adapters)} chains")
    
    def identify_chain(self, address: str) -> Optional[str]:
        """Identify which chain an address belongs to"""
        for chain_name, adapter in self.adapters.items():
            if adapter.identify_address(address):
                return chain_name
        return None
    
    async def fetch_wallet_data(
        self,
        address: str,
        chain: str = None,
        include_transactions: bool = True,
        include_tokens: bool = True
    ) -> Dict:
        """
        Fetch comprehensive wallet data from specified chain
        
        If chain not specified, auto-detects
        """
        if not chain:
            chain = self.identify_chain(address)
        
        if not chain or chain not in self.adapters:
            return {
                'success': False,
                'error': f'Unknown chain or address format: {address}',
                'chain': chain
            }
        
        adapter = self.adapters[chain]
        
        try:
            # Fetch all data concurrently
            tasks = []
            
            if include_transactions:
                tasks.append(adapter.get_transactions(address))
            else:
                tasks.append(asyncio.sleep(0))
            
            if include_tokens:
                tasks.append(adapter.get_token_holdings(address))
            else:
                tasks.append(asyncio.sleep(0))
            
            tasks.append(adapter.get_wallet_age(address))
            tasks.append(adapter.detect_cex_funding(address))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            transactions = results[0] if include_transactions else []
            tokens = results[1] if include_tokens else []
            age_info = results[2] if not isinstance(results[2], Exception) else None
            cex_funding = results[3] if not isinstance(results[3], Exception) else None
            
            # Detect suspicious patterns
            suspicious_patterns = adapter.detect_suspicious_patterns(
                transactions if isinstance(transactions, list) else []
            )
            
            # Build response
            data = {
                'success': True,
                'address': address,
                'chain': chain,
                'timestamp': datetime.now().isoformat(),
                'transactions': transactions if isinstance(transactions, list) else [],
                'token_holdings': tokens if isinstance(tokens, list) else [],
                'wallet_age': age_info,
                'cex_funding': cex_funding,
                'suspicious_patterns': suspicious_patterns,
                'native_token': adapter.native_token,
                'reliability_score': 1.0  # Will be updated
            }
            
            # Calculate reliability
            data['reliability_score'] = adapter.calculate_reliability_score(data)
            
            # Validate
            validation = self.reliability_checker.validate_data(chain, data)
            data['validation'] = validation
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {address} on {chain}: {e}")
            return {
                'success': False,
                'error': str(e),
                'chain': chain,
                'address': address
            }
    
    async def fetch_multi_chain_data(
        self,
        addresses: List[str],
        progress_callback = None
    ) -> Dict[str, Dict]:
        """
        Fetch data for multiple addresses across multiple chains
        """
        results = {}
        total = len(addresses)
        
        for i, address in enumerate(addresses):
            if progress_callback:
                progress_callback(i + 1, total, address)
            
            data = await self.fetch_wallet_data(address)
            results[address] = data
        
        return results
    
    def detect_cross_chain_relationships(self, all_data: Dict[str, Dict]) -> List[Dict]:
        """
        Find relationships between wallets across different chains
        """
        relationships = []
        
        # Group by chain
        by_chain = {}
        for address, data in all_data.items():
            chain = data.get('chain')
            if chain:
                if chain not in by_chain:
                    by_chain[chain] = []
                by_chain[chain].append({
                    'address': address,
                    'data': data
                })
        
        # Find similar timing patterns across chains
        timing_groups = self._find_cross_chain_timing_patterns(by_chain)
        
        # Find potential same-owner patterns
        ownership_groups = self._find_same_owner_patterns(by_chain)
        
        relationships.extend(timing_groups)
        relationships.extend(ownership_groups)
        
        return relationships
    
    def _find_cross_chain_timing_patterns(self, by_chain: Dict) -> List[Dict]:
        """Find wallets active at same times across chains"""
        patterns = []
        
        chains = list(by_chain.keys())
        
        # Compare each pair of chains
        for i, chain1 in enumerate(chains):
            for chain2 in chains[i+1:]:
                wallets1 = by_chain[chain1]
                wallets2 = by_chain[chain2]
                
                # Check for activity time overlap
                for w1 in wallets1:
                    for w2 in wallets2:
                        overlap = self._check_activity_overlap(
                            w1['data'].get('transactions', []),
                            w2['data'].get('transactions', [])
                        )
                        
                        if overlap['has_overlap']:
                            patterns.append({
                                'type': 'CROSS_CHAIN_TIMING',
                                'chain1': chain1,
                                'chain2': chain2,
                                'wallet1': w1['address'],
                                'wallet2': w2['address'],
                                'overlap_hours': overlap['overlap_hours'],
                                'confidence': overlap['confidence']
                            })
        
        return patterns
    
    def _check_activity_overlap(self, txs1: List[Dict], txs2: List[Dict]) -> Dict:
        """Check if two wallets have overlapping activity times"""
        # Extract timestamps
        times1 = set()
        for tx in txs1:
            ts = tx.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                    times1.add(dt.strftime('%Y-%m-%d-%H'))
                except:
                    pass
        
        times2 = set()
        for tx in txs2:
            ts = tx.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                    times2.add(dt.strftime('%Y-%m-%d-%H'))
                except:
                    pass
        
        overlap = times1 & times2
        
        return {
            'has_overlap': len(overlap) >= 3,
            'overlap_hours': len(overlap),
            'confidence': min(len(overlap) * 0.1, 0.9)
        }
    
    def _find_same_owner_patterns(self, by_chain: Dict) -> List[Dict]:
        """Find patterns suggesting same owner across chains"""
        patterns = []
        
        # Check for similar funding patterns
        funding_patterns = {}
        
        for chain, wallets in by_chain.items():
            for w in wallets:
                cex_funding = w['data'].get('cex_funding')
                if cex_funding:
                    cex = cex_funding.get('cex')
                    if cex:
                        if cex not in funding_patterns:
                            funding_patterns[cex] = {}
                        if chain not in funding_patterns[cex]:
                            funding_patterns[cex][chain] = []
                        funding_patterns[cex][chain].append(w['address'])
        
        # Find CEXs funding wallets on multiple chains
        for cex, chains in funding_patterns.items():
            if len(chains) > 1:
                patterns.append({
                    'type': 'SAME_CEX_MULTI_CHAIN',
                    'cex': cex,
                    'chains_affected': list(chains.keys()),
                    'wallets_per_chain': {c: len(addrs) for c, addrs in chains.items()},
                    'note': 'Same CEX funding wallets across multiple chains'
                })
        
        return patterns
    
    def get_chain_stats(self) -> Dict:
        """Get statistics about supported chains"""
        return {
            'supported_chains': SUPPORTED_CHAINS,
            'initialized_chains': list(self.adapters.keys()),
            'api_status': {
                chain: 'configured' if self.api_keys.get(chain) else 'missing_key'
                for chain in SUPPORTED_CHAINS
            },
            'features_per_chain': {
                chain: {
                    'transactions': True,
                    'token_holdings': True,
                    'wallet_age': True,
                    'cex_detection': True,
                    'pig_butcher_detection': chain in ['ethereum', 'tron', 'solana'],
                    'cross_chain_bridges': len(adapter.get_known_bridge_contracts()) > 0
                }
                for chain, adapter in self.adapters.items()
            }
        }


if __name__ == "__main__":
    print("Multi-Chain Manager initialized")
    print(f"Supports: {', '.join(SUPPORTED_CHAINS)}")
    
    # Demo
    manager = MultiChainManager()
    stats = manager.get_chain_stats()
    print(f"\nInitialized chains: {stats['initialized_chains']}")
