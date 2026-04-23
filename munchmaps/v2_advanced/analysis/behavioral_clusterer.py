#!/usr/bin/env python3
"""
Behavioral Clusterer - Find similar wallets by behavior, not just transactions
Detects coordinated groups, sybil attacks, and sock puppets
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BehavioralClusterer:
    """
    Cluster wallets by similar behavior patterns
    Goes beyond direct transactions to detect coordination
    """
    
    def __init__(self):
        self.clusters = []
        self.similarity_threshold = 0.8  # 80% similarity
    
    def find_similar_wallets(self, wallets: List[Dict]) -> List[Dict]:
        """
        Find groups of wallets with similar behavior
        
        Detects:
        - Similar creation times (bot farms)
        - Similar transaction patterns
        - Similar token holdings
        - Similar timing
        """
        clusters = []
        
        # 1. Creation Time Clustering
        creation_clusters = self._cluster_by_creation_time(wallets)
        clusters.extend(creation_clusters)
        
        # 2. Transaction Pattern Clustering
        pattern_clusters = self._cluster_by_transaction_patterns(wallets)
        clusters.extend(pattern_clusters)
        
        # 3. Amount/Holding Clustering
        amount_clusters = self._cluster_by_holdings(wallets)
        clusters.extend(amount_clusters)
        
        # 4. CEX Funding Clustering
        cex_clusters = self._cluster_by_cex_funding(wallets)
        clusters.extend(cex_clusters)
        
        # Merge overlapping clusters
        merged_clusters = self._merge_clusters(clusters)
        
        return merged_clusters
    
    def _cluster_by_creation_time(self, wallets: List[Dict]) -> List[Dict]:
        """
        Find wallets created within short time windows
        Strong indicator of coordinated creation (bot farms)
        """
        clusters = []
        
        # Group by creation date (hour precision)
        creation_groups = defaultdict(list)
        
        for wallet in wallets:
            creation = wallet.get('estimated_creation')
            if creation:
                try:
                    dt = datetime.fromisoformat(creation.replace('Z', '+00:00'))
                    # Round to hour
                    hour_key = dt.strftime('%Y-%m-%d-%H')
                    creation_groups[hour_key].append(wallet)
                except:
                    pass
        
        # Find groups with 5+ wallets created in same hour
        for hour, group in creation_groups.items():
            if len(group) >= 5:
                clusters.append({
                    'type': 'COORDINATED_CREATION',
                    'wallets': [w['address'] for w in group],
                    'wallet_count': len(group),
                    'creation_hour': hour,
                    'confidence': min(0.95, 0.5 + (len(group) * 0.05)),
                    'risk_level': 'HIGH',
                    'indicators': [
                        f'{len(group)} wallets created within 1 hour',
                        'Possible bot farm or sybil attack'
                    ]
                })
        
        return clusters
    
    def _cluster_by_transaction_patterns(self, wallets: List[Dict]) -> List[Dict]:
        """
        Find wallets with similar transaction patterns
        
        Similar patterns suggest same operator/script
        """
        clusters = []
        
        # Create behavioral fingerprints
        fingerprints = {}
        
        for wallet in wallets:
            address = wallet.get('address')
            txs = wallet.get('transactions', [])
            
            if len(txs) < 3:
                continue
            
            fingerprint = self._create_behavioral_fingerprint(wallet)
            fingerprints[address] = fingerprint
        
        # Find similar fingerprints
        addresses = list(fingerprints.keys())
        
        for i, addr1 in enumerate(addresses):
            similar_wallets = [addr1]
            
            for addr2 in addresses[i+1:]:
                similarity = self._calculate_fingerprint_similarity(
                    fingerprints[addr1],
                    fingerprints[addr2]
                )
                
                if similarity >= self.similarity_threshold:
                    similar_wallets.append(addr2)
            
            if len(similar_wallets) >= 3:
                clusters.append({
                    'type': 'BEHAVIORAL_SIMILARITY',
                    'wallets': similar_wallets,
                    'wallet_count': len(similar_wallets),
                    'similarity_score': self.similarity_threshold,
                    'confidence': 0.75,
                    'risk_level': 'MEDIUM',
                    'indicators': [
                        f'{len(similar_wallets)} wallets with similar behavior',
                        'Similar transaction timing and amounts'
                    ]
                })
        
        return clusters
    
    def _create_behavioral_fingerprint(self, wallet: Dict) -> Dict:
        """Create a behavioral fingerprint for a wallet"""
        txs = wallet.get('transactions', [])
        
        if not txs:
            return {}
        
        # Transaction count
        tx_count = len(txs)
        
        # Average transaction value
        values = []
        for tx in txs:
            val = tx.get('value_eth') or tx.get('amount', 0)
            try:
                values.append(float(val))
            except:
                pass
        
        avg_value = sum(values) / len(values) if values else 0
        
        # Transaction timing (hour of day)
        hours = []
        for tx in txs:
            ts = tx.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    hours.append(dt.hour)
                except:
                    pass
        
        avg_hour = sum(hours) / len(hours) if hours else 0
        hour_variance = self._calculate_variance(hours) if hours else 0
        
        # Days between transactions
        timestamps = []
        for tx in txs:
            ts = tx.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    timestamps.append(dt)
                except:
                    pass
        
        timestamps.sort()
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).days
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        return {
            'tx_count': tx_count,
            'avg_value': avg_value,
            'avg_hour': avg_hour,
            'hour_variance': hour_variance,
            'avg_interval_days': avg_interval
        }
    
    def _calculate_fingerprint_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between two fingerprints"""
        if not fp1 or not fp2:
            return 0.0
        
        scores = []
        
        # Transaction count similarity (within 20%)
        if fp1['tx_count'] > 0 and fp2['tx_count'] > 0:
            tx_ratio = min(fp1['tx_count'], fp2['tx_count']) / max(fp1['tx_count'], fp2['tx_count'])
            if tx_ratio >= 0.8:
                scores.append(tx_ratio)
        
        # Average value similarity
        if fp1['avg_value'] > 0 and fp2['avg_value'] > 0:
            val_ratio = min(fp1['avg_value'], fp2['avg_value']) / max(fp1['avg_value'], fp2['avg_value'])
            if val_ratio >= 0.8:
                scores.append(val_ratio)
        
        # Hour similarity (within 2 hours)
        hour_diff = abs(fp1['avg_hour'] - fp2['avg_hour'])
        if hour_diff <= 2:
            scores.append(1.0 - (hour_diff / 12))
        
        # Interval similarity
        if fp1['avg_interval_days'] > 0 and fp2['avg_interval_days'] > 0:
            int_ratio = min(fp1['avg_interval_days'], fp2['avg_interval_days']) / max(fp1['avg_interval_days'], fp2['avg_interval_days'])
            if int_ratio >= 0.8:
                scores.append(int_ratio)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _cluster_by_holdings(self, wallets: List[Dict]) -> List[Dict]:
        """
        Find wallets with similar token holdings
        Exact same amounts = likely same owner
        """
        clusters = []
        
        # Group by exact holding amounts
        holding_groups = defaultdict(list)
        
        for wallet in wallets:
            holdings = wallet.get('token_holdings', {})
            
            # Create a signature of holdings (sorted token amounts)
            signature_parts = []
            for token, amount in sorted(holdings.items()):
                # Round to reduce noise
                rounded = round(float(amount), 2)
                signature_parts.append(f"{token}:{rounded}")
            
            signature = '|'.join(signature_parts)
            
            if signature:
                holding_groups[signature].append(wallet)
        
        # Find groups with multiple wallets
        for signature, group in holding_groups.items():
            if len(group) >= 2:
                clusters.append({
                    'type': 'SIMILAR_HOLDINGS',
                    'wallets': [w['address'] for w in group],
                    'wallet_count': len(group),
                    'holding_signature': signature[:100],  # Truncate for display
                    'confidence': 0.85,
                    'risk_level': 'HIGH',
                    'indicators': [
                        f'{len(group)} wallets with identical holdings',
                        'Strong indication of same owner'
                    ]
                })
        
        return clusters
    
    def _cluster_by_cex_funding(self, wallets: List[Dict]) -> List[Dict]:
        """
        Find wallets funded from the same CEX
        
        Traces back to exchange hot wallets
        """
        clusters = []
        
        # Known CEX hot wallets (simplified list)
        cex_wallets = {
            'binance': ['0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bB'],  # Example
            'coinbase': ['0x71660c4005BA85c37ccec55d0C4493E66Fe775d3'],
            'kraken': ['0x267be1C1D684F78cb4F6a176C4911b741E4Fffdc']
        }
        
        # Group by funding source
        funding_groups = defaultdict(list)
        
        for wallet in wallets:
            funding_source = wallet.get('funding_source')
            if funding_source:
                funding_groups[funding_source].append(wallet)
        
        # Find groups with multiple wallets funded from same CEX
        for source, group in funding_groups.items():
            if len(group) >= 3:
                clusters.append({
                    'type': 'SHARED_CEX_FUNDING',
                    'wallets': [w['address'] for w in group],
                    'wallet_count': len(group),
                    'funding_source': source,
                    'confidence': 0.7,
                    'risk_level': 'MEDIUM',
                    'indicators': [
                        f'{len(group)} wallets funded from {source}',
                        'May indicate same operator'
                    ]
                })
        
        return clusters
    
    def _merge_clusters(self, clusters: List[Dict]) -> List[Dict]:
        """Merge overlapping clusters"""
        if not clusters:
            return []
        
        # Sort by wallet count (largest first)
        clusters.sort(key=lambda x: x['wallet_count'], reverse=True)
        
        merged = []
        used_wallets = set()
        
        for cluster in clusters:
            cluster_wallets = set(cluster['wallets'])
            
            # Check if this cluster is mostly new wallets
            new_wallets = cluster_wallets - used_wallets
            
            if len(new_wallets) >= 3:  # Keep if has 3+ new wallets
                merged.append(cluster)
                used_wallets.update(cluster_wallets)
        
        return merged
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        squared_diff_sum = sum((x - mean) ** 2 for x in values)
        return squared_diff_sum / len(values)


if __name__ == "__main__":
    print("Behavioral Clusterer initialized")
    print("Detects similar wallets through behavior analysis, not just transactions")
