#!/usr/bin/env python3
"""
Cross-Chain Detector - Find connections across blockchains
Detects bridge usage, cross-chain coordination, and multi-chain scams
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrossChainDetector:
    """
    Detect cross-chain wallet connections and bridge usage
    Critical for catching sophisticated scammers who operate on multiple chains
    """
    
    def __init__(self):
        # Known bridge contracts
        self.bridges = {
            'ethereum': {
                'wormhole': ['0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B'],
                'layerzero': ['0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675'],
                'celer': ['0x5427FEFA711Eff984124bFBB1AB6fbf5E3DA1820'],
                'axelar': ['0x4F4495243837681061C9723bB4b8EC5d51cD81c5'],
                'multichain': ['0x13B432914A96b1CC13CfD3b64D5dE1B8D39D3434'],
                'stargate': ['0x8731d54E9D02c286767d56ac03e8037C07e01e98']
            },
            'solana': {
                'wormhole': ['worm2ZoG2kUd4vFXhvjh93UUH596ayRfgQ2MgjNMTth'],
                'layerzero': ['76y77prsiCMvXM7cH39WnYf8T3Jk89J3JH2NHpwcf1pG'],
                'celer': ['CCTPiPYPc6AsJuwueEnWgSgucamXDZwBd53dQ1YiRkLZ']
            }
        }
        
        # Chain identifiers in addresses
        self.chain_patterns = {
            'ethereum': r'^0x[a-fA-F0-9]{40}$',
            'solana': r'^[1-9A-HJ-NP-Za-km-z]{32,44}$',
            'bitcoin': r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$'
        }
    
    def detect_cross_chain_connections(self, wallets: List[Dict]) -> List[Dict]:
        """
        Main entry point - find all cross-chain connections
        """
        connections = []
        
        # 1. Identify chains for each wallet
        wallets_by_chain = self._categorize_by_chain(wallets)
        
        # 2. Find bridge usage patterns
        bridge_connections = self._detect_bridge_usage(wallets_by_chain)
        connections.extend(bridge_connections)
        
        # 3. Find same-owner patterns across chains
        ownership_patterns = self._detect_cross_chain_ownership(wallets_by_chain)
        connections.extend(ownership_patterns)
        
        # 4. Find coordinated cross-chain activity
        coordination = self._detect_cross_chain_coordination(wallets_by_chain)
        connections.extend(coordination)
        
        return connections
    
    def _categorize_by_chain(self, wallets: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize wallets by their blockchain"""
        by_chain = defaultdict(list)
        
        for wallet in wallets:
            address = wallet.get('address', '')
            chain = self._identify_chain(address)
            
            if chain:
                by_chain[chain].append(wallet)
                wallet['_detected_chain'] = chain
        
        return dict(by_chain)
    
    def _identify_chain(self, address: str) -> Optional[str]:
        """Identify which blockchain an address belongs to"""
        for chain, pattern in self.chain_patterns.items():
            if re.match(pattern, address):
                return chain
        return None
    
    def _detect_bridge_usage(self, wallets_by_chain: Dict) -> List[Dict]:
        """
        Detect wallets that have used cross-chain bridges
        This reveals the same entity operating on multiple chains
        """
        connections = []
        
        for chain, wallets in wallets_by_chain.items():
            for wallet in wallets:
                address = wallet.get('address')
                txs = wallet.get('transactions', [])
                
                bridges_used = self._find_bridge_interactions(chain, txs)
                
                if bridges_used:
                    # Estimate destination chain wallets
                    for bridge in bridges_used:
                        destination_chain = self._get_bridge_destination(chain, bridge)
                        
                        connections.append({
                            'type': 'BRIDGE_USAGE',
                            'source_wallet': address,
                            'source_chain': chain,
                            'bridge': bridge,
                            'destination_chain': destination_chain,
                            'confidence': 0.9,
                            'risk_level': 'MEDIUM',
                            'indicators': [
                                f'Used {bridge} bridge',
                                f'Funds moved to {destination_chain}',
                                'Cross-chain operation detected'
                            ]
                        })
        
        return connections
    
    def _find_bridge_interactions(self, chain: str, txs: List[Dict]) -> List[str]:
        """Find which bridges this wallet has interacted with"""
        bridges_used = []
        
        if chain not in self.bridges:
            return bridges_used
        
        for tx in txs:
            to_addr = tx.get('to', '').lower()
            from_addr = tx.get('from', '').lower()
            
            for bridge_name, contracts in self.bridges[chain].items():
                for contract in contracts:
                    if contract.lower() in [to_addr, from_addr]:
                        if bridge_name not in bridges_used:
                            bridges_used.append(bridge_name)
        
        return bridges_used
    
    def _get_bridge_destination(self, source_chain: str, bridge: str) -> str:
        """Estimate destination chain based on bridge and source"""
        # Simplified - most bridges go ETH <> SOL or ETH <> BSC
        if source_chain == 'ethereum':
            return 'solana' if bridge in ['wormhole', 'layerzero'] else 'bsc'
        elif source_chain == 'solana':
            return 'ethereum'
        return 'unknown'
    
    def _detect_cross_chain_ownership(self, wallets_by_chain: Dict) -> List[Dict]:
        """
        Detect patterns suggesting same owner across chains
        
        Uses:
        - Similar naming (if labeled)
        - Similar creation times
        - Similar transaction patterns
        """
        connections = []
        
        chains = list(wallets_by_chain.keys())
        
        # Compare wallets across different chains
        for i, chain1 in enumerate(chains):
            for chain2 in chains[i+1:]:
                chain1_wallets = wallets_by_chain[chain1]
                chain2_wallets = wallets_by_chain[chain2]
                
                # Look for creation time correlation
                time_clusters = self._find_temporal_correlation(
                    chain1_wallets, chain2_wallets
                )
                
                for cluster in time_clusters:
                    if len(cluster['wallets1']) >= 2 and len(cluster['wallets2']) >= 2:
                        connections.append({
                            'type': 'CROSS_CHAIN_OWNER',
                            'chain1': chain1,
                            'chain2': chain2,
                            'wallets_chain1': cluster['wallets1'],
                            'wallets_chain2': cluster['wallets2'],
                            'time_correlation_hours': cluster['time_diff_hours'],
                            'confidence': 0.75,
                            'risk_level': 'HIGH',
                            'indicators': [
                                f'Similar creation pattern: {chain1} ↔ {chain2}',
                                f'Time delta: {cluster["time_diff_hours"]:.1f} hours',
                                'Possible same operator on multiple chains'
                            ]
                        })
        
        return connections
    
    def _find_temporal_correlation(
        self, 
        wallets1: List[Dict], 
        wallets2: List[Dict]
    ) -> List[Dict]:
        """Find wallets created at similar times across chains"""
        clusters = []
        
        for w1 in wallets1:
            creation1 = w1.get('estimated_creation')
            if not creation1:
                continue
            
            try:
                dt1 = datetime.fromisoformat(creation1.replace('Z', '+00:00'))
            except:
                continue
            
            matching_wallets2 = []
            
            for w2 in wallets2:
                creation2 = w2.get('estimated_creation')
                if not creation2:
                    continue
                
                try:
                    dt2 = datetime.fromisoformat(creation2.replace('Z', '+00:00'))
                    time_diff = abs((dt2 - dt1).total_seconds() / 3600)
                    
                    # Within 24 hours = suspicious correlation
                    if time_diff <= 24:
                        matching_wallets2.append({
                            'address': w2.get('address'),
                            'time_diff_hours': time_diff
                        })
                except:
                    pass
            
            if matching_wallets2:
                clusters.append({
                    'wallets1': [w1.get('address')],
                    'wallets2': [w['address'] for w in matching_wallets2],
                    'time_diff_hours': min(w['time_diff_hours'] for w in matching_wallets2)
                })
        
        return clusters
    
    def _detect_cross_chain_coordination(self, wallets_by_chain: Dict) -> List[Dict]:
        """
        Detect coordinated activity across chains
        
        Pattern: Same time windows = same operation
        """
        connections = []
        
        # Look for activity bursts across chains at similar times
        chains = list(wallets_by_chain.keys())
        
        for chain in chains:
            wallets = wallets_by_chain[chain]
            activity_windows = self._find_activity_windows(wallets)
            
            # Store for cross-chain comparison
            for window in activity_windows:
                connections.append({
                    'type': 'CROSS_CHAIN_COORDINATION',
                    'chain': chain,
                    'activity_window': window,
                    'wallets': window['wallets'],
                    'confidence': 0.7,
                    'risk_level': 'HIGH',
                    'indicators': [
                        f'Activity burst on {chain}',
                        f'{len(window["wallets"])} wallets active in {window["duration_minutes"]:.0f} minutes',
                        'Check other chains for parallel activity'
                    ]
                })
        
        return connections
    
    def _find_activity_windows(self, wallets: List[Dict]) -> List[Dict]:
        """Find time windows with high activity"""
        windows = []
        
        # Collect all transaction timestamps
        all_activity = []
        
        for wallet in wallets:
            address = wallet.get('address')
            txs = wallet.get('transactions', [])
            
            for tx in txs:
                ts = tx.get('timestamp')
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        all_activity.append({
                            'address': address,
                            'timestamp': dt
                        })
                    except:
                        pass
        
        if not all_activity:
            return windows
        
        # Sort by time
        all_activity.sort(key=lambda x: x['timestamp'])
        
        # Find clusters of activity
        current_window = [all_activity[0]]
        
        for activity in all_activity[1:]:
            time_diff = (activity['timestamp'] - current_window[-1]['timestamp']).total_seconds() / 60
            
            if time_diff <= 60:  # Within 60 minutes
                current_window.append(activity)
            else:
                # Check if window has enough activity
                if len(current_window) >= 10:  # 10+ transactions
                    unique_wallets = set(a['address'] for a in current_window)
                    duration = (current_window[-1]['timestamp'] - current_window[0]['timestamp']).total_seconds() / 60
                    
                    windows.append({
                        'start': current_window[0]['timestamp'].isoformat(),
                        'end': current_window[-1]['timestamp'].isoformat(),
                        'duration_minutes': duration,
                        'transaction_count': len(current_window),
                        'wallets': list(unique_wallets)
                    })
                
                current_window = [activity]
        
        return windows
    
    def estimate_linked_addresses(self, wallet: Dict, all_wallets: List[Dict]) -> List[Dict]:
        """
        Estimate which addresses on other chains might be linked
        Based on bridge usage and timing patterns
        """
        estimates = []
        
        address = wallet.get('address')
        chain = wallet.get('_detected_chain')
        txs = wallet.get('transactions', [])
        
        if not chain:
            return estimates
        
        # Find bridge transactions
        for tx in txs:
            to_addr = tx.get('to', '').lower()
            
            for bridge_name, contracts in self.bridges.get(chain, {}).items():
                for contract in contracts:
                    if contract.lower() in to_addr:
                        # This is a bridge transaction
                        amount = tx.get('value_eth') or tx.get('amount', 0)
                        timestamp = tx.get('timestamp')
                        
                        # Estimate destination address
                        # In reality, we'd need to query the destination chain
                        estimates.append({
                            'source_wallet': address,
                            'source_chain': chain,
                            'bridge': bridge_name,
                            'estimated_destination_chain': self._get_bridge_destination(chain, bridge_name),
                            'bridge_amount': amount,
                            'bridge_timestamp': timestamp,
                            'confidence': 0.6,  # Low confidence without destination chain data
                            'note': 'Destination address requires cross-chain query'
                        })
        
        return estimates


if __name__ == "__main__":
    print("Cross-Chain Detector initialized")
    print("Detects multi-chain operations and bridge usage")
