#!/usr/bin/env python3
"""
Multi-Hop Relationship Tracer - Find indirect wallet connections
Traces paths through intermediate wallets to reveal hidden relationships
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiHopTracer:
    """
    Trace wallet relationships through multiple hops
    Critical for detecting sophisticated layering and obfuscation
    """
    
    def __init__(self, max_hops: int = 3):
        self.max_hops = max_hops
        self.graph = defaultdict(list)
    
    def build_transaction_graph(self, wallets: List[Dict]) -> Dict:
        """
        Build a directed graph from transaction data
        """
        graph = defaultdict(lambda: {
            'outgoing': [],  # Transactions sent
            'incoming': [],  # Transactions received
            'addresses': set()
        })
        
        for wallet in wallets:
            address = wallet.get('address', '').lower()
            txs = wallet.get('transactions', [])
            
            for tx in txs:
                from_addr = tx.get('from', '').lower()
                to_addr = tx.get('to', '').lower()
                
                if not from_addr or not to_addr:
                    continue
                
                # Track the connection
                graph[from_addr]['outgoing'].append({
                    'to': to_addr,
                    'tx': tx,
                    'timestamp': tx.get('timestamp'),
                    'value': tx.get('value_eth') or tx.get('amount', 0)
                })
                
                graph[to_addr]['incoming'].append({
                    'from': from_addr,
                    'tx': tx,
                    'timestamp': tx.get('timestamp'),
                    'value': tx.get('value_eth') or tx.get('amount', 0)
                })
                
                graph[from_addr]['addresses'].add(address)
                graph[to_addr]['addresses'].add(address)
        
        return dict(graph)
    
    def find_multihop_paths(
        self, 
        source: str, 
        target: str, 
        wallets: List[Dict],
        max_hops: int = None
    ) -> List[Dict]:
        """
        Find all paths between two wallets within max_hops
        Uses BFS to find shortest paths first
        """
        if max_hops is None:
            max_hops = self.max_hops
        
        graph = self.build_transaction_graph(wallets)
        source = source.lower()
        target = target.lower()
        
        paths = []
        visited = set()
        
        # BFS queue: (current_address, path_so_far, hops)
        queue = deque([(source, [source], 0)])
        
        while queue:
            current, path, hops = queue.popleft()
            
            if hops > max_hops:
                continue
            
            if current == target and len(path) > 1:
                # Found a path
                path_details = self._enrich_path(path, graph)
                paths.append(path_details)
                continue
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Add neighbors
            for conn in graph.get(current, {}).get('outgoing', []):
                neighbor = conn['to']
                if neighbor not in path:  # Avoid cycles
                    queue.append((neighbor, path + [neighbor], hops + 1))
        
        # Sort by number of hops (shortest first)
        paths.sort(key=lambda x: x['hop_count'])
        
        return paths
    
    def find_all_connections(
        self,
        wallets: List[Dict],
        min_path_length: int = 2,
        max_path_length: int = 3
    ) -> List[Dict]:
        """
        Find all multi-hop connections within the wallet set
        """
        connections = []
        
        # Get all wallet addresses
        addresses = [w.get('address', '').lower() for w in wallets if w.get('address')]
        address_set = set(addresses)
        
        # Build graph
        graph = self.build_transaction_graph(wallets)
        
        # Find paths between all pairs
        checked_pairs = set()
        
        for i, addr1 in enumerate(addresses):
            for addr2 in addresses[i+1:]:
                if (addr1, addr2) in checked_pairs:
                    continue
                
                checked_pairs.add((addr1, addr2))
                checked_pairs.add((addr2, addr1))
                
                # Find paths in both directions
                paths = self.find_multihop_paths(addr1, addr2, wallets, max_path_length)
                reverse_paths = self.find_multihop_paths(addr2, addr1, wallets, max_path_length)
                
                all_paths = paths + reverse_paths
                
                if all_paths:
                    # Check if paths go through intermediaries outside our wallet set
                    external_intermediaries = []
                    for path in all_paths:
                        for hop in path.get('hops', []):
                            if hop.get('address') not in address_set:
                                external_intermediaries.append(hop.get('address'))
                    
                    connection = {
                        'wallet1': addr1,
                        'wallet2': addr2,
                        'path_count': len(all_paths),
                        'shortest_path_hops': min(p.get('hop_count', 999) for p in all_paths),
                        'paths': all_paths[:3],  # Limit to first 3 paths
                        'has_external_intermediary': len(external_intermediaries) > 0,
                        'external_intermediaries': list(set(external_intermediaries))[:5],
                        'total_value_transferred': sum(
                            p.get('total_value', 0) for p in all_paths
                        ),
                        'risk_level': self._assess_path_risk(all_paths, external_intermediaries),
                        'indicators': self._generate_path_indicators(all_paths, external_intermediaries)
                    }
                    
                    connections.append(connection)
        
        # Sort by risk level and path count
        connections.sort(key=lambda x: (
            {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x['risk_level'], 0),
            x['path_count']
        ), reverse=True)
        
        return connections
    
    def find_layering_patterns(self, wallets: List[Dict]) -> List[Dict]:
        """
        Detect money laundering layering patterns
        
        Patterns:
        - Long chains (5+ hops)
        - Rapid successive transfers
        - Amount splitting
        - Round numbers
        """
        patterns = []
        
        graph = self.build_transaction_graph(wallets)
        
        for wallet in wallets:
            address = wallet.get('address', '').lower()
            
            # Find long outgoing chains
            chains = self._trace_outgoing_chains(address, graph, max_depth=5)
            
            for chain in chains:
                if chain['length'] >= 3:
                    risk_score = self._score_layering_chain(chain)
                    
                    if risk_score > 0.6:
                        patterns.append({
                            'source_wallet': address,
                            'pattern_type': 'LAYERING_CHAIN',
                            'chain_length': chain['length'],
                            'total_value': chain['total_value'],
                            'duration_hours': chain['duration_hours'],
                            'intermediary_count': chain['intermediary_count'],
                            'risk_score': risk_score,
                            'indicators': chain['indicators'],
                            'path': chain['addresses']
                        })
        
        return patterns
    
    def _trace_outgoing_chains(
        self, 
        start_address: str, 
        graph: Dict, 
        max_depth: int = 5
    ) -> List[Dict]:
        """Trace all outgoing transaction chains from an address"""
        chains = []
        
        def trace_recursive(current: str, path: List[str], value_so_far: float, timestamps: List[datetime]):
            if len(path) >= max_depth:
                # Record this chain
                duration = (timestamps[-1] - timestamps[0]).total_seconds() / 3600 if len(timestamps) > 1 else 0
                
                indicators = []
                
                # Check for rapid succession
                if duration > 0 and duration < 1:
                    indicators.append('Rapid transfers (< 1 hour)')
                
                # Check for amount splitting
                if len(path) >= 3:
                    indicators.append('Possible amount splitting')
                
                # Check for round numbers
                if value_so_far > 0 and value_so_far % 1 == 0:
                    indicators.append('Round number amounts')
                
                chains.append({
                    'length': len(path),
                    'addresses': path.copy(),
                    'total_value': value_so_far,
                    'intermediary_count': len(path) - 2 if len(path) > 2 else 0,
                    'duration_hours': duration,
                    'indicators': indicators
                })
                return
            
            outgoing = graph.get(current, {}).get('outgoing', [])
            
            for conn in outgoing[:3]:  # Limit branching
                next_addr = conn['to']
                if next_addr not in path:  # Avoid cycles
                    new_value = value_so_far
                    try:
                        new_value += float(conn.get('value', 0))
                    except:
                        pass
                    
                    new_timestamps = timestamps.copy()
                    ts = conn.get('timestamp')
                    if ts:
                        try:
                            new_timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                        except:
                            pass
                    
                    trace_recursive(next_addr, path + [next_addr], new_value, new_timestamps)
        
        trace_recursive(start_address, [start_address], 0.0, [])
        
        return chains
    
    def _enrich_path(self, addresses: List[str], graph: Dict) -> Dict:
        """Add details to a path of addresses"""
        hops = []
        total_value = 0.0
        timestamps = []
        
        for i in range(len(addresses) - 1):
            from_addr = addresses[i]
            to_addr = addresses[i + 1]
            
            # Find the transaction(s) connecting these
            outgoing = graph.get(from_addr, {}).get('outgoing', [])
            matching_tx = None
            
            for conn in outgoing:
                if conn['to'] == to_addr:
                    matching_tx = conn
                    break
            
            if matching_tx:
                try:
                    value = float(matching_tx.get('value', 0))
                    total_value += value
                except:
                    value = 0
                
                ts = matching_tx.get('timestamp')
                if ts:
                    timestamps.append(ts)
                
                hops.append({
                    'from': from_addr,
                    'to': to_addr,
                    'value': value,
                    'timestamp': ts,
                    'address': to_addr  # The intermediary
                })
        
        return {
            'addresses': addresses,
            'hop_count': len(addresses) - 1,
            'hops': hops,
            'total_value': total_value,
            'start': addresses[0],
            'end': addresses[-1]
        }
    
    def _assess_path_risk(self, paths: List[Dict], external_intermediaries: List[str]) -> str:
        """Assess risk level of connection paths"""
        if not paths:
            return 'LOW'
        
        risk_score = 0
        
        # External intermediaries increase risk
        if external_intermediaries:
            risk_score += 0.3
        
        # Long paths increase risk
        max_hops = max(p.get('hop_count', 0) for p in paths)
        if max_hops >= 3:
            risk_score += 0.3
        elif max_hops == 2:
            risk_score += 0.1
        
        # Multiple paths increase risk
        if len(paths) >= 3:
            risk_score += 0.2
        
        if risk_score >= 0.5:
            return 'HIGH'
        elif risk_score >= 0.2:
            return 'MEDIUM'
        return 'LOW'
    
    def _generate_path_indicators(self, paths: List[Dict], external_intermediaries: List[str]) -> List[str]:
        """Generate human-readable indicators"""
        indicators = []
        
        if external_intermediaries:
            indicators.append(f'Uses {len(external_intermediaries)} external intermediary addresses')
        
        if paths:
            min_hops = min(p.get('hop_count', 999) for p in paths)
            indicators.append(f'Shortest path: {min_hops} hop{"s" if min_hops > 1 else ""}')
        
        if len(paths) > 1:
            indicators.append(f'Multiple connection paths ({len(paths)})')
        
        return indicators
    
    def _score_layering_chain(self, chain: Dict) -> float:
        """Score a chain for money laundering risk"""
        score = 0.0
        
        # Long chains are suspicious
        if chain['length'] >= 4:
            score += 0.3
        elif chain['length'] >= 3:
            score += 0.2
        
        # Rapid movement is suspicious
        if chain['duration_hours'] < 0.5:  # 30 minutes
            score += 0.3
        elif chain['duration_hours'] < 2:
            score += 0.1
        
        # Multiple intermediaries
        if chain['intermediary_count'] >= 3:
            score += 0.2
        
        # Round numbers
        if 'Round number amounts' in chain['indicators']:
            score += 0.1
        
        return min(score, 1.0)


if __name__ == "__main__":
    print("Multi-Hop Tracer initialized")
    print("Traces indirect wallet connections through intermediaries")
