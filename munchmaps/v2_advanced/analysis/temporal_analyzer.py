#!/usr/bin/env python3
"""
Temporal Analyzer - Time-based wallet behavior analysis
Uses only free data sources
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemporalAnalyzer:
    """
    Analyze how wallet clusters evolve over time
    Creates time-series data for playback visualization
    """
    
    def __init__(self):
        self.time_buckets = defaultdict(list)
        self.events = []
    
    def analyze_wallet_lifecycle(self, wallet_data: Dict) -> Dict:
        """
        Analyze a wallet's lifecycle patterns
        
        Detects:
        - Wallet creation time (approximate from first transaction)
        - Activity periods (when it was active)
        - Dormancy periods (inactive gaps)
        - First token interaction
        - Peak activity times
        """
        transactions = wallet_data.get('transactions', [])
        
        if not transactions:
            return {
                'wallet': wallet_data.get('address'),
                'estimated_creation': None,
                'lifecycle_stage': 'unknown',
                'patterns': []
            }
        
        # Sort by timestamp
        sorted_txs = sorted(transactions, key=lambda x: x.get('timestamp', ''))
        
        first_tx = sorted_txs[0]
        last_tx = sorted_txs[-1]
        
        # Estimate wallet creation (first transaction time)
        estimated_creation = first_tx.get('timestamp')
        
        # Calculate wallet age
        try:
            first_date = datetime.fromisoformat(estimated_creation.replace('Z', '+00:00'))
            wallet_age_days = (datetime.now() - first_date).days
        except:
            wallet_age_days = None
        
        # Detect lifecycle stage
        if wallet_age_days is not None:
            if wallet_age_days < 7:
                stage = 'fresh'  # Less than 7 days old
            elif wallet_age_days < 30:
                stage = 'new'    # Less than 30 days
            elif wallet_age_days < 90:
                stage = 'established'
            else:
                stage = 'veteran'
        else:
            stage = 'unknown'
        
        # Detect activity patterns
        patterns = self._detect_activity_patterns(sorted_txs)
        
        # Detect burst activity (many txs in short time)
        burst_periods = self._detect_burst_activity(sorted_txs)
        
        return {
            'wallet': wallet_data.get('address'),
            'estimated_creation': estimated_creation,
            'wallet_age_days': wallet_age_days,
            'lifecycle_stage': stage,
            'first_transaction': first_tx.get('timestamp'),
            'last_transaction': last_tx.get('timestamp'),
            'total_transactions': len(transactions),
            'patterns': patterns,
            'burst_periods': burst_periods,
            'is_fresh': stage == 'fresh',
            'risk_factors': self._calculate_temporal_risk(stage, patterns)
        }
    
    def _detect_activity_patterns(self, transactions: List[Dict]) -> List[str]:
        """Detect suspicious activity patterns"""
        patterns = []
        
        timestamps = []
        for tx in transactions:
            ts = tx.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    timestamps.append(dt)
                except:
                    pass
        
        if not timestamps:
            return patterns
        
        timestamps.sort()
        
        # Check for exact timing patterns (bot behavior)
        if len(timestamps) >= 3:
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            # If intervals are suspiciously regular (within 10% of each other)
            if len(intervals) >= 3:
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
                
                if variance < (avg_interval * 0.1) ** 2:  # Very regular timing
                    patterns.append('BOT_LIKE_TIMING')
        
        # Check for specific hour clustering (avoids US daytime)
        hours = [t.hour for t in timestamps]
        hour_counts = defaultdict(int)
        for h in hours:
            hour_counts[h] += 1
        
        # If 70% of activity happens in same 6-hour window
        for hour, count in hour_counts.items():
            if count / len(hours) > 0.7:
                patterns.append(f'ACTIVITY_CLUSTERED_HOUR_{hour}')
                break
        
        # Check for weekend vs weekday patterns
        weekdays = sum(1 for t in timestamps if t.weekday() < 5)
        weekends = len(timestamps) - weekdays
        
        if weekends == 0:
            patterns.append('WEEKDAY_ONLY_ACTIVITY')
        elif weekdays == 0:
            patterns.append('WEEKEND_ONLY_ACTIVITY')
        
        return patterns
    
    def _detect_burst_activity(self, transactions: List[Dict]) -> List[Dict]:
        """Detect periods of unusually high activity"""
        burst_periods = []
        
        timestamps = []
        for tx in transactions:
            ts = tx.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    timestamps.append(dt)
                except:
                    pass
        
        if len(timestamps) < 10:
            return burst_periods
        
        timestamps.sort()
        
        # Sliding window of 1 hour
        window_size = timedelta(hours=1)
        
        i = 0
        while i < len(timestamps):
            window_start = timestamps[i]
            window_end = window_start + window_size
            
            # Count transactions in window
            count = 0
            j = i
            while j < len(timestamps) and timestamps[j] <= window_end:
                count += 1
                j += 1
            
            # If more than 10 transactions in 1 hour, it's a burst
            if count >= 10:
                burst_periods.append({
                    'start': window_start.isoformat(),
                    'end': window_end.isoformat(),
                    'transaction_count': count,
                    'type': 'HIGH_ACTIVITY_BURST'
                })
                i = j  # Skip past this burst
            else:
                i += 1
        
        return burst_periods
    
    def _calculate_temporal_risk(self, stage: str, patterns: List[str]) -> List[str]:
        """Calculate risk factors based on temporal patterns"""
        risks = []
        
        if stage == 'fresh':
            risks.append('FRESH_WALLET_RISK')
        
        if 'BOT_LIKE_TIMING' in patterns:
            risks.append('AUTOMATED_BEHAVIOR')
        
        if 'ACTIVITY_CLUSTERED_HOUR_' in str(patterns):
            risks.append('SUSPICIOUS_TIMING_PATTERN')
        
        return risks
    
    def generate_timeline_frames(
        self,
        wallets: List[Dict],
        start_date: datetime,
        end_date: datetime,
        frame_interval: timedelta = timedelta(hours=24)
    ) -> List[Dict]:
        """
        Generate animation frames for temporal playback
        
        Each frame shows the state of the network at a specific time
        """
        frames = []
        current_time = start_date
        
        while current_time <= end_date:
            frame = {
                'timestamp': current_time.isoformat(),
                'active_wallets': [],
                'new_wallets': [],
                'transactions': [],
                'clusters': []
            }
            
            for wallet in wallets:
                wallet_address = wallet.get('address')
                transactions = wallet.get('transactions', [])
                
                # Get transactions up to this time
                prior_transactions = [
                    tx for tx in transactions
                    if self._parse_timestamp(tx.get('timestamp')) <= current_time
                ]
                
                if not prior_transactions:
                    continue
                
                # Check if wallet is new in this frame
                first_tx_time = self._parse_timestamp(prior_transactions[0].get('timestamp'))
                
                if first_tx_time and first_tx_time >= current_time - frame_interval:
                    frame['new_wallets'].append(wallet_address)
                
                # Add to active wallets
                frame['active_wallets'].append({
                    'address': wallet_address,
                    'transaction_count': len(prior_transactions),
                    'is_new': wallet_address in frame['new_wallets']
                })
                
                # Add transactions in this frame
                frame_transactions = [
                    tx for tx in transactions
                    if current_time - frame_interval <= self._parse_timestamp(tx.get('timestamp')) <= current_time
                ]
                frame['transactions'].extend(frame_transactions)
            
            frames.append(frame)
            current_time += frame_interval
        
        return frames
    
    def _parse_timestamp(self, ts: str) -> Optional[datetime]:
        """Parse timestamp string to datetime"""
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except:
            return None

    # ===== INTEGRATION METHODS =====
    
    def analyze_wallet_ages(self, wallets: List[Dict]) -> List[Dict]:
        """Analyze creation ages of all wallets"""
        results = []
        for wallet in wallets:
            age_days = wallet.get('creation_age_days')
            if age_days is not None:
                results.append({
                    'address': wallet.get('address'),
                    'age_days': age_days,
                    'is_fresh': age_days < 7 if age_days else False
                })
        return results
    
    def build_activity_timeline(self, wallets: List[Dict]) -> List[Dict]:
        """Build chronological timeline of all activity"""
        events = []
        for wallet in wallets:
            for tx in wallet.get('transactions', []):
                ts = tx.get('timestamp')
                if ts:
                    events.append({
                        'timestamp': ts,
                        'wallet': wallet.get('address'),
                        'type': tx.get('type', 'transfer'),
                        'value': tx.get('value_eth') or tx.get('amount', 0),
                        'to': tx.get('to')
                    })
        return sorted(events, key=lambda x: x['timestamp'])
    
    def detect_cex_funding_patterns(self, wallets: List[Dict]) -> List[Dict]:
        """Detect CEX funding patterns across wallets"""
        cex_groups = {}
        for wallet in wallets:
            funding = wallet.get('funding_source')
            if funding:
                if funding not in cex_groups:
                    cex_groups[funding] = []
                cex_groups[funding].append(wallet.get('address'))
        
        results = []
        for cex, addresses in cex_groups.items():
            if len(addresses) >= 2:
                results.append({
                    'cex': cex,
                    'wallets': addresses,
                    'wallet_count': len(addresses)
                })
        return results
    
    def identify_fresh_wallets(self, wallets: List[Dict]) -> List[Dict]:
        """Identify wallets less than 7 days old"""
        fresh = []
        for wallet in wallets:
            age_days = wallet.get('creation_age_days')
            if age_days is not None and age_days < 7:
                fresh.append({
                    'address': wallet.get('address'),
                    'age_days': age_days,
                    'funding_source': wallet.get('funding_source')
                })
        return fresh
    
    def generate_playback_frames(
        self,
        wallets: List[Dict],
        frame_days: int = 7
    ) -> List[Dict]:
        """Generate timeline playback frames"""
        # Collect all timestamps
        all_timestamps = []
        for wallet in wallets:
            for tx in wallet.get('transactions', []):
                ts = tx.get('timestamp')
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        all_timestamps.append(dt)
                    except:
                        pass
        
        if not all_timestamps:
            return []
        
        start = min(all_timestamps)
        end = max(all_timestamps)
        
        frames = []
        current = start
        frame_num = 0
        
        while current <= end:
            frame_end = current + timedelta(days=frame_days)
            
            # Count activity in this frame
            active_wallets = set()
            tx_count = 0
            
            for wallet in wallets:
                address = wallet.get('address')
                for tx in wallet.get('transactions', []):
                    ts = tx.get('timestamp')
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            if current <= dt < frame_end:
                                active_wallets.add(address)
                                tx_count += 1
                        except:
                            pass
            
            frames.append({
                'frame_number': frame_num,
                'start_date': current.isoformat(),
                'end_date': frame_end.isoformat(),
                'active_wallet_count': len(active_wallets),
                'transaction_count': tx_count,
                'active_wallets': list(active_wallets)
            })
            
            current = frame_end
            frame_num += 1
        
        return frames


if __name__ == "__main__":
    print("Temporal Analyzer initialized")
    print("Analyzes wallet lifecycle and activity patterns over time")
