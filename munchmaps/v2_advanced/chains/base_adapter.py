#!/usr/bin/env python3
"""
Base Chain Adapter - Abstract interface for all chain adapters
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class BaseChainAdapter(ABC):
    """Abstract base class for blockchain adapters"""
    
    def __init__(self, api_key: str = None, rpc_url: str = None):
        self.api_key = api_key
        self.rpc_url = rpc_url
        self.chain_name = self.__class__.__name__.replace('Adapter', '').lower()
        self.native_token = self._get_native_token()
        self.block_time_seconds = self._get_block_time()
    
    @abstractmethod
    def _get_native_token(self) -> str:
        """Return native token symbol"""
        pass
    
    @abstractmethod
    def _get_block_time(self) -> int:
        """Return average block time in seconds"""
        pass
    
    @abstractmethod
    def identify_address(self, address: str) -> Optional[str]:
        """Identify if address belongs to this chain"""
        pass
    
    @abstractmethod
    async def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Fetch transaction history for address"""
        pass
    
    @abstractmethod
    async def get_wallet_age(self, address: str) -> Optional[Dict]:
        """Get wallet creation/first activity info"""
        pass
    
    @abstractmethod
    async def detect_cex_funding(self, address: str) -> Optional[Dict]:
        """Detect if wallet was funded from CEX"""
        pass
    
    @abstractmethod
    async def get_token_holdings(self, address: str) -> List[Dict]:
        """Get token balances"""
        pass
    
    @abstractmethod
    def get_known_cex_addresses(self) -> Dict[str, List[str]]:
        """Return known CEX hot/cold wallet addresses"""
        pass
    
    @abstractmethod
    def get_known_bridge_contracts(self) -> List[str]:
        """Return known bridge contract addresses"""
        pass
    
    def calculate_reliability_score(self, data: Dict) -> float:
        """
        Calculate reliability score for fetched data
        Based on: data completeness, source quality, timestamp freshness
        """
        score = 1.0
        
        # Check data completeness
        if not data.get('transactions'):
            score -= 0.3
        
        if not data.get('balance'):
            score -= 0.1
        
        # Check timestamp freshness
        last_updated = data.get('last_updated')
        if last_updated:
            try:
                updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                age_hours = (datetime.now() - updated_time).total_seconds() / 3600
                if age_hours > 24:
                    score -= 0.2
            except:
                score -= 0.1
        
        return max(score, 0.0)
    
    def normalize_transaction(self, tx: Dict) -> Dict:
        """Normalize transaction to common format"""
        return {
            'hash': tx.get('hash') or tx.get('tx_hash') or tx.get('signature'),
            'from': tx.get('from'),
            'to': tx.get('to'),
            'value': tx.get('value') or tx.get('amount'),
            'timestamp': tx.get('timestamp') or tx.get('block_time'),
            'fee': tx.get('fee') or tx.get('gas_fee'),
            'status': tx.get('status', 'unknown'),
            'chain': self.chain_name
        }
    
    def detect_suspicious_patterns(self, txs: List[Dict]) -> List[str]:
        """Detect suspicious transaction patterns"""
        patterns = []
        
        if not txs or len(txs) < 3:
            return patterns
        
        # Check for identical amounts
        amounts = [float(tx.get('value', 0)) for tx in txs if tx.get('value')]
        if amounts:
            from collections import Counter
            amount_counts = Counter(round(a, 4) for a in amounts)
            most_common = amount_counts.most_common(1)[0]
            if most_common[1] >= len(amounts) * 0.5:
                patterns.append('repeated_amounts')
        
        # Check for rapid succession
        timestamps = []
        for tx in txs:
            ts = tx.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                    timestamps.append(dt)
                except:
                    pass
        
        if len(timestamps) >= 3:
            timestamps.sort()
            intervals = [(timestamps[i] - timestamps[i-1]).total_seconds() / 60 
                        for i in range(1, len(timestamps))]
            avg_interval = sum(intervals) / len(intervals)
            
            # If average interval is very regular or very fast
            if avg_interval < 5:  # Less than 5 minutes
                patterns.append('rapid_fire')
            
            # Check for regular intervals (bot-like)
            if intervals:
                variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
                if variance < 1 and avg_interval > 0:  # Very regular
                    patterns.append('regular_intervals')
        
        return patterns


class ChainDataReliabilityChecker:
    """
    Ensures data reliability across different chains
    Handles inconsistencies, missing data, and validation
    """
    
    def __init__(self):
        self.validation_rules = {
            'ethereum': {
                'min_tx_for_age': 1,
                'max_tx_age_days': 30,
                'required_fields': ['hash', 'from', 'to', 'value']
            },
            'solana': {
                'min_tx_for_age': 1,
                'max_tx_age_days': 14,
                'required_fields': ['signature', 'err']
            },
            'tron': {
                'min_tx_for_age': 1,
                'max_tx_age_days': 30,
                'required_fields': ['txID', 'owner_address']
            },
            'bsc': {
                'min_tx_for_age': 1,
                'max_tx_age_days': 30,
                'required_fields': ['hash', 'from', 'to', 'value']
            },
            'polygon': {
                'min_tx_for_age': 1,
                'max_tx_age_days': 30,
                'required_fields': ['hash', 'from', 'to', 'value']
            }
        }
    
    def validate_data(self, chain: str, data: Dict) -> Dict:
        """Validate data for specific chain"""
        rules = self.validation_rules.get(chain, {})
        errors = []
        warnings = []
        
        # Check required fields
        if 'transactions' in data:
            for i, tx in enumerate(data['transactions'][:5]):  # Check first 5
                for field in rules.get('required_fields', []):
                    if field not in tx:
                        errors.append(f"Missing {field} in tx {i}")
        
        # Check data freshness
        if data.get('last_updated'):
            try:
                from datetime import datetime
                updated = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
                age_days = (datetime.now() - updated).days
                max_age = rules.get('max_tx_age_days', 30)
                if age_days > max_age:
                    warnings.append(f"Data is {age_days} days old")
            except:
                warnings.append("Could not parse timestamp")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'reliability_score': self._calculate_reliability(errors, warnings)
        }
    
    def _calculate_reliability(self, errors: List, warnings: List) -> float:
        """Calculate reliability score"""
        score = 1.0
        score -= len(errors) * 0.2
        score -= len(warnings) * 0.05
        return max(score, 0.0)
    
    def cross_validate(self, chain_data: Dict[str, Dict]) -> Dict:
        """Cross-validate data across multiple sources/chains"""
        # Check for inconsistencies
        inconsistencies = []
        
        # Example: Check if same address appears on multiple chains with conflicting data
        addresses_by_chain = {}
        for chain, data in chain_data.items():
            addresses_by_chain[chain] = set()
            for tx in data.get('transactions', []):
                if tx.get('from'):
                    addresses_by_chain[chain].add(tx['from'])
                if tx.get('to'):
                    addresses_by_chain[chain].add(tx['to'])
        
        # Find common addresses across chains
        all_addresses = set()
        for addresses in addresses_by_chain.values():
            all_addresses.update(addresses)
        
        multi_chain_addresses = []
        for addr in all_addresses:
            chains_found = [c for c, addrs in addresses_by_chain.items() if addr in addrs]
            if len(chains_found) > 1:
                multi_chain_addresses.append({
                    'address': addr,
                    'chains': chains_found
                })
        
        return {
            'inconsistencies': inconsistencies,
            'multi_chain_addresses': multi_chain_addresses,
            'cross_chain_consistency': len(inconsistencies) == 0
        }
