#!/usr/bin/env python3
"""
Interactive Features - Dynamic exploration and playback
Features for the MunchMaps V2 frontend
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from typing import List, Dict, Any, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveFeatures:
    """
    Generate interactive features for frontend
    Timeline playback, filtering, highlighting, etc.
    """
    
    def __init__(self):
        self.playback_frames = []
        self.current_frame = 0
    
    def generate_timeline_playback(
        self,
        wallets: List[Dict],
        start_date: datetime = None,
        end_date: datetime = None,
        frame_duration_days: int = 7
    ) -> List[Dict]:
        """
        Generate frame-by-frame timeline playback data
        
        Each frame shows the state of the network at that time
        """
        frames = []
        
        # Determine date range
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
            return frames
        
        if not start_date:
            start_date = min(all_timestamps)
        if not end_date:
            end_date = max(all_timestamps)
        
        # Generate frames
        current_date = start_date
        frame_number = 0
        
        while current_date <= end_date:
            frame_end = current_date + timedelta(days=frame_duration_days)
            
            frame = self._generate_frame(
                wallets,
                current_date,
                frame_end,
                frame_number
            )
            
            frames.append(frame)
            
            current_date = frame_end
            frame_number += 1
        
        self.playback_frames = frames
        return frames
    
    def _generate_frame(
        self,
        wallets: List[Dict],
        frame_start: datetime,
        frame_end: datetime,
        frame_number: int
    ) -> Dict:
        """Generate a single timeline frame"""
        
        # Track which wallets are active in this frame
        active_wallets = set()
        active_edges = []
        frame_events = []
        
        for wallet in wallets:
            address = wallet.get('address')
            
            for tx in wallet.get('transactions', []):
                ts = tx.get('timestamp')
                if not ts:
                    continue
                
                try:
                    tx_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except:
                    continue
                
                if frame_start <= tx_time < frame_end:
                    active_wallets.add(address)
                    
                    to_addr = tx.get('to', '').lower()
                    if to_addr:
                        active_edges.append({
                            'from': address,
                            'to': to_addr,
                            'value': tx.get('value_eth') or tx.get('amount', 0),
                            'timestamp': ts
                        })
                    
                    frame_events.append({
                        'type': 'transaction',
                        'wallet': address,
                        'timestamp': ts,
                        'value': tx.get('value_eth') or tx.get('amount', 0)
                    })
        
        return {
            'frame_number': frame_number,
            'start_date': frame_start.isoformat(),
            'end_date': frame_end.isoformat(),
            'active_wallet_count': len(active_wallets),
            'active_wallets': list(active_wallets),
            'transaction_count': len(frame_events),
            'new_edges': active_edges,
            'events': sorted(frame_events, key=lambda x: x['timestamp'])
        }
    
    def generate_filter_config(self, wallets: List[Dict]) -> Dict:
        """
        Generate filter configuration for frontend
        """
        # Analyze data to suggest filters
        
        # Amount ranges
        amounts = []
        for wallet in wallets:
            for tx in wallet.get('transactions', []):
                try:
                    val = float(tx.get('value_eth') or tx.get('amount', 0))
                    if val > 0:
                        amounts.append(val)
                except:
                    pass
        
        amount_ranges = []
        if amounts:
            sorted_amounts = sorted(amounts)
            quartiles = [
                sorted_amounts[len(sorted_amounts) // 4],
                sorted_amounts[len(sorted_amounts) // 2],
                sorted_amounts[len(sorted_amounts) * 3 // 4]
            ]
            amount_ranges = [
                {'label': 'Small (< Q1)', 'min': 0, 'max': quartiles[0]},
                {'label': 'Medium (Q1-Q3)', 'min': quartiles[0], 'max': quartiles[2]},
                {'label': 'Large (> Q3)', 'min': quartiles[2], 'max': max(amounts)}
            ]
        
        # Date range
        timestamps = []
        for wallet in wallets:
            for tx in wallet.get('transactions', []):
                ts = tx.get('timestamp')
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        timestamps.append(dt)
                    except:
                        pass
        
        date_range = {}
        if timestamps:
            date_range = {
                'min': min(timestamps).isoformat(),
                'max': max(timestamps).isoformat()
            }
        
        # Risk levels
        risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        # Wallet types
        wallet_types = list(set(
            w.get('wallet_type', 'unknown') for w in wallets
        ))
        
        return {
            'amount_ranges': amount_ranges,
            'date_range': date_range,
            'risk_levels': risk_levels,
            'wallet_types': wallet_types,
            'filters': {
                'amount': {'type': 'range', 'label': 'Transaction Amount'},
                'date': {'type': 'date_range', 'label': 'Date Range'},
                'risk': {'type': 'multi_select', 'label': 'Risk Level'},
                'wallet_type': {'type': 'multi_select', 'label': 'Wallet Type'},
                'fresh_wallet': {'type': 'boolean', 'label': 'Fresh Wallet Only'},
                'cex_funded': {'type': 'boolean', 'label': 'CEX Funded Only'}
            }
        }
    
    def apply_filters(
        self,
        wallets: List[Dict],
        filters: Dict
    ) -> List[Dict]:
        """
        Apply filters to wallet list
        """
        filtered = wallets
        
        # Risk filter
        if filters.get('risk'):
            risk_levels = filters['risk'] if isinstance(filters['risk'], list) else [filters['risk']]
            filtered = [w for w in filtered if w.get('risk_level') in risk_levels]
        
        # Fresh wallet filter
        if filters.get('fresh_wallet'):
            filtered = [w for w in filtered if w.get('is_fresh_wallet')]
        
        # CEX funded filter
        if filters.get('cex_funded'):
            filtered = [w for w in filtered if w.get('funding_source')]
        
        # Wallet type filter
        if filters.get('wallet_type'):
            types = filters['wallet_type'] if isinstance(filters['wallet_type'], list) else [filters['wallet_type']]
            filtered = [w for w in filtered if w.get('wallet_type') in types]
        
        # Date range filter
        if filters.get('date_start') or filters.get('date_end'):
            def within_date_range(wallet):
                creation = wallet.get('estimated_creation')
                if not creation:
                    return True
                
                try:
                    dt = datetime.fromisoformat(creation.replace('Z', '+00:00'))
                    
                    if filters.get('date_start'):
                        start = datetime.fromisoformat(filters['date_start'])
                        if dt < start:
                            return False
                    
                    if filters.get('date_end'):
                        end = datetime.fromisoformat(filters['date_end'])
                        if dt > end:
                            return False
                    
                    return True
                except:
                    return True
            
            filtered = [w for w in filtered if within_date_range(w)]
        
        return filtered
    
    def generate_highlight_rules(self, analysis_results: Dict) -> List[Dict]:
        """
        Generate highlighting rules for visualization
        """
        rules = []
        
        # Highlight fresh wallets
        rules.append({
            'id': 'fresh_wallets',
            'label': 'Fresh Wallets',
            'condition': {'field': 'is_fresh_wallet', 'operator': 'equals', 'value': True},
            'style': {
                'color': '#FF4444',
                'size': 25,
                'borderWidth': 3,
                'borderColor': '#FF0000'
            },
            'priority': 1
        })
        
        # Highlight CEX funded
        rules.append({
            'id': 'cex_funded',
            'label': 'CEX Funded',
            'condition': {'field': 'funding_source', 'operator': 'exists'},
            'style': {
                'color': '#4444FF',
                'size': 20,
                'borderWidth': 2,
                'borderColor': '#0000FF'
            },
            'priority': 2
        })
        
        # Highlight high risk
        rules.append({
            'id': 'high_risk',
            'label': 'High Risk',
            'condition': {'field': 'risk_level', 'operator': 'in', 'value': ['HIGH', 'CRITICAL']},
            'style': {
                'color': '#FF0000',
                'size': 30,
                'borderWidth': 4,
                'borderColor': '#8B0000',
                'pulse': True
            },
            'priority': 0  # Highest
        })
        
        # Highlight network hubs
        if 'network_hubs' in analysis_results:
            hub_addresses = [h['address'] for h in analysis_results['network_hubs']]
            rules.append({
                'id': 'network_hubs',
                'label': 'Network Hubs',
                'condition': {'field': 'address', 'operator': 'in', 'value': hub_addresses},
                'style': {
                    'color': '#FF00FF',
                    'size': 35,
                    'borderWidth': 3,
                    'borderColor': '#800080'
                },
                'priority': 1
            })
        
        return rules
    
    def generate_tooltip_config(self) -> Dict:
        """
        Generate tooltip configuration for wallet nodes
        """
        return {
            'fields': [
                {'key': 'address', 'label': 'Address', 'format': 'address'},
                {'key': 'wallet_type', 'label': 'Type'},
                {'key': 'risk_level', 'label': 'Risk'},
                {'key': 'risk_score', 'label': 'Risk Score', 'format': 'percent'},
                {'key': 'is_fresh_wallet', 'label': 'Fresh Wallet', 'format': 'boolean'},
                {'key': 'funding_source', 'label': 'CEX Funding'},
                {'key': 'creation_age_days', 'label': 'Age (days)'},
                {'key': 'transaction_count', 'label': 'Transactions'},
                {'key': 'cluster_id', 'label': 'Cluster'},
                {'key': 'suspicious_indicators', 'label': 'Flags', 'format': 'list'}
            ],
            'max_width': 300,
            'show_on_hover': True,
            'delay_ms': 200
        }
    
    def export_for_frontend(
        self,
        network_data: Dict,
        analysis_results: Dict,
        output_path: str
    ):
        """
        Export complete data package for frontend
        """
        export = {
            'metadata': {
                'version': '2.0',
                'generated_at': datetime.now().isoformat(),
                'wallet_count': len(network_data.get('nodes', [])),
                'connection_count': len(network_data.get('edges', []))
            },
            'network': network_data,
            'analysis': analysis_results,
            'interactive': {
                'playback_frames': self.playback_frames,
                'filters': self.generate_filter_config(network_data.get('raw_wallets', [])),
                'highlight_rules': self.generate_highlight_rules(analysis_results),
                'tooltip_config': self.generate_tooltip_config()
            },
            'summary': {
                'total_wallets': len(network_data.get('nodes', [])),
                'fresh_wallets': sum(1 for n in network_data.get('nodes', []) if n.get('is_fresh_wallet')),
                'cex_funded': sum(1 for n in network_data.get('nodes', []) if n.get('funding_source')),
                'high_risk_wallets': sum(1 for n in network_data.get('nodes', []) 
                    if n.get('risk_level') in ['HIGH', 'CRITICAL']),
                'clusters_detected': len(analysis_results.get('clusters', [])),
                'suspicious_patterns': len(analysis_results.get('anomalies', []))
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export, f, indent=2, default=str)
        
        logger.info(f"Exported frontend data to {output_path}")
        return export


if __name__ == "__main__":
    print("Interactive Features initialized")
    print("Generates timeline playback, filters, and frontend configuration")
