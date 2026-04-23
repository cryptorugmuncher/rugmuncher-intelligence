#!/usr/bin/env python3
"""
Statistical Anomaly Detector - Find mathematically suspicious patterns
Uses statistical methods to detect coordination, bot behavior, and manipulation
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import math
import statistics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatisticalAnomalyDetector:
    """
    Detect anomalies using statistical analysis
    Finds patterns that humans and simple heuristics miss
    """
    
    def __init__(self):
        self.confidence_threshold = 0.95
    
    def analyze_wallets(self, wallets: List[Dict]) -> List[Dict]:
        """
        Run full statistical analysis on wallet set
        """
        anomalies = []
        
        # 1. Benford's Law Analysis
        benford_anomalies = self._benfords_law_analysis(wallets)
        anomalies.extend(benford_anomalies)
        
        # 2. Transaction Time Distribution Analysis
        time_anomalies = self._time_distribution_analysis(wallets)
        anomalies.extend(time_anomalies)
        
        # 3. Amount Clustering Analysis
        amount_anomalies = self._amount_clustering_analysis(wallets)
        anomalies.extend(amount_anomalies)
        
        # 4. Inter-Transaction Time Analysis
        interval_anomalies = self._interval_analysis(wallets)
        anomalies.extend(interval_anomalies)
        
        # 5. Network Centrality Analysis
        centrality_anomalies = self._centrality_analysis(wallets)
        anomalies.extend(centrality_anomalies)
        
        return anomalies
    
    def _benfords_law_analysis(self, wallets: List[Dict]) -> List[Dict]:
        """
        Apply Benford's Law to transaction amounts
        
        Natural financial data follows Benford's Law.
        Synthetic/manipulated data often deviates.
        """
        anomalies = []
        
        # Collect all transaction amounts
        amounts = []
        for wallet in wallets:
            for tx in wallet.get('transactions', []):
                val = tx.get('value_eth') or tx.get('amount', 0)
                try:
                    val = float(val)
                    if val > 0:
                        amounts.append(val)
                except:
                    pass
        
        if len(amounts) < 100:
            return anomalies
        
        # Get first digits
        first_digits = []
        for amount in amounts:
            # Convert to string and get first non-zero digit
            s = str(amount).replace('.', '').lstrip('0')
            if s:
                first_digits.append(int(s[0]))
        
        if len(first_digits) < 100:
            return anomalies
        
        # Calculate observed distribution
        observed = defaultdict(int)
        for d in first_digits:
            observed[d] += 1
        
        total = len(first_digits)
        observed_dist = {d: observed[d] / total for d in range(1, 10)}
        
        # Benford's Law expected distribution
        benford_expected = {
            1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097,
            5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
        }
        
        # Calculate chi-square statistic
        chi_square = 0
        for d in range(1, 10):
            observed_val = observed_dist.get(d, 0) * total
            expected_val = benford_expected[d] * total
            if expected_val > 0:
                chi_square += ((observed_val - expected_val) ** 2) / expected_val
        
        # Critical value for 8 degrees of freedom at 0.05 significance: 15.51
        if chi_square > 20:  # Strong deviation
            # Find which digits deviate most
            max_deviation_digit = max(
                range(1, 10),
                key=lambda d: abs(observed_dist.get(d, 0) - benford_expected[d])
            )
            
            anomalies.append({
                'type': 'BENFORD_LAW_VIOLATION',
                'chi_square': round(chi_square, 2),
                'sample_size': len(first_digits),
                'observed_distribution': {str(k): round(v, 3) for k, v in observed_dist.items()},
                'max_deviation_digit': max_deviation_digit,
                'confidence': min(0.99, chi_square / 50),
                'risk_level': 'HIGH' if chi_square > 30 else 'MEDIUM',
                'indicators': [
                    f'Chi-square statistic: {chi_square:.1f} (critical: 15.51)',
                    f'Digit {max_deviation_digit} shows highest deviation',
                    'Transaction amounts may be artificially generated'
                ]
            })
        
        return anomalies
    
    def _time_distribution_analysis(self, wallets: List[Dict]) -> List[Dict]:
        """
        Analyze distribution of transaction times
        
        Natural: Spread throughout day
        Suspicious: Clustered in specific hours (bot activity)
        """
        anomalies = []
        
        # Collect all transaction hours
        hours = []
        for wallet in wallets:
            for tx in wallet.get('transactions', []):
                ts = tx.get('timestamp')
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        hours.append(dt.hour)
                    except:
                        pass
        
        if len(hours) < 50:
            return anomalies
        
        # Count by hour
        hour_counts = defaultdict(int)
        for h in hours:
            hour_counts[h] += 1
        
        total = len(hours)
        
        # Expected: uniform distribution (4.17% per hour)
        expected_per_hour = total / 24
        
        # Find hours with significant deviation
        chi_square = 0
        peak_hours = []
        
        for h in range(24):
            observed = hour_counts.get(h, 0)
            chi_square += ((observed - expected_per_hour) ** 2) / expected_per_hour if expected_per_hour > 0 else 0
            
            if observed > expected_per_hour * 2:  # More than 2x expected
                peak_hours.append({
                    'hour': h,
                    'count': observed,
                    'percentage': round(observed / total * 100, 1)
                })
        
        # Critical value for 23 degrees of freedom at 0.05: 35.17
        if chi_square > 40 or len(peak_hours) <= 3:
            anomalies.append({
                'type': 'TIME_DISTRIBUTION_ANOMALY',
                'chi_square': round(chi_square, 2),
                'peak_hours': sorted(peak_hours, key=lambda x: x['count'], reverse=True)[:5],
                'sample_size': total,
                'confidence': min(0.95, chi_square / 100),
                'risk_level': 'HIGH' if chi_square > 60 else 'MEDIUM',
                'indicators': [
                    f'Transactions concentrated in {len(peak_hours)} hours',
                    'Possible automated/bot activity',
                    f'Peak activity at {peak_hours[0]["hour"]}:00' if peak_hours else 'Unusual time distribution'
                ]
            })
        
        return anomalies
    
    def _amount_clustering_analysis(self, wallets: List[Dict]) -> List[Dict]:
        """
        Find unnatural clustering of transaction amounts
        
        Suspicious: Many transactions of exactly the same amount
        """
        anomalies = []
        
        # Collect all amounts
        amounts = []
        for wallet in wallets:
            for tx in wallet.get('transactions', []):
                val = tx.get('value_eth') or tx.get('amount', 0)
                try:
                    val = float(val)
                    if val > 0:
                        amounts.append(round(val, 4))  # Round to reduce noise
                except:
                    pass
        
        if len(amounts) < 50:
            return anomalies
        
        # Find repeated amounts
        amount_counts = defaultdict(int)
        for amt in amounts:
            amount_counts[amt] += 1
        
        # Find amounts that appear unusually often
        mean_count = statistics.mean(amount_counts.values())
        std_count = statistics.stdev(amount_counts.values()) if len(amount_counts) > 1 else 0
        
        suspicious_clusters = []
        for amt, count in amount_counts.items():
            if count > mean_count + 2 * std_count and count >= 5:
                suspicious_clusters.append({
                    'amount': amt,
                    'occurrences': count,
                    'z_score': round((count - mean_count) / std_count, 2) if std_count > 0 else 0
                })
        
        if suspicious_clusters:
            anomalies.append({
                'type': 'AMOUNT_CLUSTERING',
                'clusters': sorted(suspicious_clusters, key=lambda x: x['occurrences'], reverse=True)[:10],
                'total_transactions': len(amounts),
                'unique_amounts': len(amount_counts),
                'confidence': 0.85,
                'risk_level': 'HIGH',
                'indicators': [
                    f'{len(suspicious_clusters)} amount clusters detected',
                    'Possible coordinated transfers or script-generated amounts',
                    f'Most common amount: {suspicious_clusters[0]["amount"]} ({suspicious_clusters[0]["occurrences"]} times)'
                ]
            })
        
        return anomalies
    
    def _interval_analysis(self, wallets: List[Dict]) -> List[Dict]:
        """
        Analyze time intervals between transactions
        
        Suspicious: Regular intervals (automation)
        """
        anomalies = []
        
        # Collect intervals for each wallet
        all_intervals = []
        wallet_intervals = {}
        
        for wallet in wallets:
            address = wallet.get('address')
            timestamps = []
            
            for tx in wallet.get('transactions', []):
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
                interval_minutes = (timestamps[i] - timestamps[i-1]).total_seconds() / 60
                if interval_minutes > 0:
                    intervals.append(interval_minutes)
            
            if len(intervals) >= 5:
                wallet_intervals[address] = intervals
                all_intervals.extend(intervals)
        
        if len(all_intervals) < 50:
            return anomalies
        
        # Look for regular intervals (automation signature)
        # Round to nearest minute and count
        rounded_intervals = [round(i) for i in all_intervals]
        interval_counts = defaultdict(int)
        for i in rounded_intervals:
            interval_counts[i] += 1
        
        # Find unusually common intervals
        mean_count = statistics.mean(interval_counts.values())
        std_count = statistics.stdev(interval_counts.values()) if len(interval_counts) > 1 else 0
        
        regular_intervals = []
        for interval, count in interval_counts.items():
            if interval > 0 and count > mean_count + 2.5 * std_count and count >= 5:
                regular_intervals.append({
                    'interval_minutes': interval,
                    'occurrences': count,
                    'wallets_affected': sum(
                        1 for addr, ints in wallet_intervals.items()
                        if any(round(i) == interval for i in ints)
                    )
                })
        
        if regular_intervals:
            anomalies.append({
                'type': 'REGULAR_INTERVAL_PATTERN',
                'regular_intervals': sorted(regular_intervals, key=lambda x: x['occurrences'], reverse=True)[:5],
                'total_intervals_analyzed': len(all_intervals),
                'wallets_with_regular_patterns': len(wallet_intervals),
                'confidence': 0.88,
                'risk_level': 'HIGH',
                'indicators': [
                    f'{len(regular_intervals)} regular interval patterns detected',
                    'Highly suggestive of automated/scripted transactions',
                    f'Most common interval: {regular_intervals[0]["interval_minutes"]} minutes'
                ]
            })
        
        return anomalies
    
    def _centrality_analysis(self, wallets: List[Dict]) -> List[Dict]:
        """
        Analyze network centrality to find coordination hubs
        """
        anomalies = []
        
        # Build connection graph
        connections = defaultdict(set)
        
        for wallet in wallets:
            address = wallet.get('address', '').lower()
            for tx in wallet.get('transactions', []):
                to_addr = tx.get('to', '').lower()
                from_addr = tx.get('from', '').lower()
                
                if to_addr and to_addr != address:
                    connections[address].add(to_addr)
                if from_addr and from_addr != address:
                    connections[address].add(from_addr)
        
        # Calculate degree centrality
        degrees = {addr: len(conns) for addr, conns in connections.items()}
        
        if len(degrees) < 10:
            return anomalies
        
        mean_degree = statistics.mean(degrees.values())
        std_degree = statistics.stdev(degrees.values()) if len(degrees) > 1 else 0
        
        # Find super-connectors
        hubs = []
        for addr, degree in degrees.items():
            z_score = (degree - mean_degree) / std_degree if std_degree > 0 else 0
            if z_score > 2.5:  # 2.5 standard deviations above mean
                hubs.append({
                    'address': addr,
                    'connections': degree,
                    'z_score': round(z_score, 2)
                })
        
        if hubs:
            anomalies.append({
                'type': 'NETWORK_HUB',
                'hubs': sorted(hubs, key=lambda x: x['connections'], reverse=True)[:5],
                'mean_connections': round(mean_degree, 2),
                'total_addresses': len(degrees),
                'confidence': 0.82,
                'risk_level': 'MEDIUM',
                'indicators': [
                    f'{len(hubs)} network hubs identified',
                    'These addresses may be coordination points',
                    f'Hub has {hubs[0]["connections"]} connections (avg: {mean_degree:.1f})'
                ]
            })
        
        return anomalies


if __name__ == "__main__":
    print("Statistical Anomaly Detector initialized")
    print("Uses mathematical analysis to detect synthetic patterns")
