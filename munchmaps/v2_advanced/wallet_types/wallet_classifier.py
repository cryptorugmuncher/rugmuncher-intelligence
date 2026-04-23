#!/usr/bin/env python3
"""
Wallet Type Classifier - Detect suspicious wallet types
Uses behavioral analysis to categorize wallets
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import re

# Define suspicious wallet types
SUSPICIOUS_WALLET_TYPES = {
    'PIG_BUTCHER_OPERATOR': {
        'description': 'Pig butcherer scam operator - lures victims and extracts funds',
        'risk_level': 'CRITICAL',
        'indicators': [
            'Large round-number USDT transfers',
            'Off-hours activity patterns',
            'Rapid succession of similar amounts',
            'Funds move to CEX within 24-48 hours',
            'Minimal contract interactions (just transfers)'
        ]
    },
    'BOT_FARM_COORDINATOR': {
        'description': 'Coordinates bot farm activity across multiple wallets',
        'risk_level': 'CRITICAL',
        'indicators': [
            'Creates many wallets in short time window',
            'Funds them from same source',
            'Regular timing patterns',
            'Similar transaction structures'
        ]
    },
    'BOT_FARM_WALLET': {
        'description': 'Individual bot in a farm network',
        'risk_level': 'HIGH',
        'indicators': [
            'Very young wallet',
            'Regular intervals between transactions',
            'Identical amounts to many addresses',
            'Single purpose behavior'
        ]
    },
    'SYBIL_ATTACKER': {
        'description': 'Creates multiple identities for airdrop farming or voting manipulation',
        'risk_level': 'HIGH',
        'indicators': [
            'Multiple wallets with same funding source',
            'Similar transaction patterns',
            'Created in batches',
            'Interacts with same protocols'
        ]
    },
    'MIXER_USER': {
        'description': 'Uses mixing services to obfuscate transaction history',
        'risk_level': 'HIGH',
        'indicators': [
            'Transactions to known mixer contracts',
            'Funds disappear then reappear',
            'Split and merge patterns',
            'Privacy-focused chains'
        ]
    },
    'RUG_PULL_DEPLOYER': {
        'description': 'Deploys tokens then drains liquidity',
        'risk_level': 'CRITICAL',
        'indicators': [
            'Creates token contract',
            'Adds liquidity then removes it',
            'Large sell transactions',
            'Disables trading'
        ]
    },
    'PUMP_AND_DUMP_OPERATOR': {
        'description': 'Coordinates pump and dump schemes',
        'risk_level': 'HIGH',
        'indicators': [
            'Rapid buy/sell cycles',
            'Social media promotion timing',
            'Multiple coordinated wallets',
            'Volume spikes'
        ]
    },
    'LAUNDERING_LAYER': {
        'description': 'Intermediate wallet in money laundering chain',
        'risk_level': 'HIGH',
        'indicators': [
            'Receives funds then immediately forwards',
            'Multiple hops in chain',
            'Round-number amounts',
            'Short holding periods'
        ]
    },
    'CEX_ARBITRAGE_BOT': {
        'description': 'Bot exploiting price differences between exchanges',
        'risk_level': 'MEDIUM',
        'indicators': [
            'Rapid transfers between CEX addresses',
            'Consistent small profits',
            'High frequency',
            'Stable patterns'
        ]
    },
    'MARKET_MANIPULATOR': {
        'description': 'Artificially manipulates token prices',
        'risk_level': 'CRITICAL',
        'indicators': [
            'Wash trading patterns',
            'Spoofing orders',
            'Layering transactions',
            'Large coordinated movements'
        ]
    },
    'SANCTIONS_EVADER': {
        'description': 'Wallet associated with sanctioned entities',
        'risk_level': 'CRITICAL',
        'indicators': [
            'Interactions with sanctioned addresses',
            'Use of privacy coins/mixers',
            'Cross-chain bridging',
            'High-value transfers'
        ]
    },
    'ROMANCE_SCAM_VICTIM': {
        'description': 'Wallet belonging to romance scam victim (for tracking)',
        'risk_level': 'MEDIUM',
        'indicators': [
            'Sudden large outbound transfers',
            'New counterparty addresses',
            'Emotional/crisis timing',
            'Multiple transfers to same scammer'
        ]
    }
}


class WalletClassifier:
    """
    Classify wallets into suspicious types based on behavior
    """
    
    def __init__(self):
        self.type_definitions = SUSPICIOUS_WALLET_TYPES
        self.confidence_threshold = 0.6
    
    def classify_wallet(self, wallet: Dict) -> List[Dict]:
        """
        Classify a single wallet
        Returns list of classifications with confidence scores
        """
        classifications = []
        
        txs = wallet.get('transactions', [])
        
        # Check each wallet type
        for wallet_type, definition in self.type_definitions.items():
            score, matched_indicators = self._calculate_match_score(
                wallet, txs, wallet_type, definition
            )
            
            if score >= self.confidence_threshold:
                classifications.append({
                    'wallet_type': wallet_type,
                    'description': definition['description'],
                    'risk_level': definition['risk_level'],
                    'confidence': round(score, 2),
                    'matched_indicators': matched_indicators,
                    'all_indicators': definition['indicators']
                })
        
        # Sort by confidence
        classifications.sort(key=lambda x: x['confidence'], reverse=True)
        
        return classifications
    
    def classify_wallets_batch(self, wallets: List[Dict]) -> Dict:
        """
        Classify multiple wallets and find coordinated groups
        """
        all_classifications = {}
        
        for wallet in wallets:
            address = wallet.get('address')
            classifications = self.classify_wallet(wallet)
            
            if classifications:
                all_classifications[address] = classifications
        
        # Find coordinated groups
        coordinated_groups = self._find_coordinated_groups(wallets, all_classifications)
        
        return {
            'individual_classifications': all_classifications,
            'coordinated_groups': coordinated_groups,
            'summary': {
                'total_wallets': len(wallets),
                'classified_wallets': len(all_classifications),
                'high_risk_wallets': sum(
                    1 for cs in all_classifications.values()
                    if any(c['risk_level'] == 'CRITICAL' for c in cs)
                )
            }
        }
    
    def _calculate_match_score(
        self,
        wallet: Dict,
        txs: List[Dict],
        wallet_type: str,
        definition: Dict
    ) -> tuple:
        """
        Calculate how well wallet matches a type
        Returns (score, matched_indicators)
        """
        matched = []
        score = 0.0
        
        if wallet_type == 'PIG_BUTCHER_OPERATOR':
            score, matched = self._check_pig_butcher(wallet, txs)
        
        elif wallet_type == 'BOT_FARM_WALLET':
            score, matched = self._check_bot_farm(wallet, txs)
        
        elif wallet_type == 'BOT_FARM_COORDINATOR':
            score, matched = self._check_bot_coordinator(wallet, txs)
        
        elif wallet_type == 'SYBIL_ATTACKER':
            score, matched = self._check_sybil(wallet, txs)
        
        elif wallet_type == 'MIXER_USER':
            score, matched = self._check_mixer_usage(wallet, txs)
        
        elif wallet_type == 'LAUNDERING_LAYER':
            score, matched = self._check_laundering_layer(wallet, txs)
        
        elif wallet_type == 'PUMP_AND_DUMP_OPERATOR':
            score, matched = self._check_pump_dump(wallet, txs)
        
        elif wallet_type == 'MARKET_MANIPULATOR':
            score, matched = self._check_market_manipulation(wallet, txs)
        
        return score, matched
    
    def _check_pig_butcher(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for pig butcher patterns"""
        score = 0.0
        matched = []
        
        if len(txs) < 5:
            return score, matched
        
        # Check for large round amounts
        round_amounts = 0
        for tx in txs:
            try:
                val = float(tx.get('value', 0))
                if val > 500 and abs(val - round(val)) < 1:
                    round_amounts += 1
            except:
                pass
        
        if round_amounts >= 3:
            score += 0.3
            matched.append('Large round-number transfers')
        
        # Check for rapid succession
        timestamps = [tx.get('timestamp') for tx in txs if tx.get('timestamp')]
        if len(timestamps) >= 3:
            timestamps.sort()
            try:
                intervals = []
                for i in range(1, len(timestamps)):
                    t1 = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                    intervals.append((t2 - t1).total_seconds() / 3600)
                
                avg_interval = sum(intervals) / len(intervals)
                if avg_interval < 2:  # Less than 2 hours
                    score += 0.25
                    matched.append('Rapid succession of transfers')
            except:
                pass
        
        # Check for outbound-heavy
        outgoing = sum(1 for tx in txs if float(tx.get('value', 0)) > 0)
        if outgoing > len(txs) * 0.7:
            score += 0.2
            matched.append('Primarily outbound transfers')
        
        # Check for CEX destination
        has_cex_out = any('cex' in str(tx.get('to', '')).lower() for tx in txs)
        if has_cex_out:
            score += 0.25
            matched.append('Transfers to CEX')
        
        return min(score, 1.0), matched
    
    def _check_bot_farm(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for bot farm wallet patterns"""
        score = 0.0
        matched = []
        
        # Fresh wallet
        age_days = wallet.get('creation_age_days')
        if age_days is not None and age_days < 7:
            score += 0.3
            matched.append('Very fresh wallet')
        
        # Regular intervals
        if len(txs) >= 5:
            timestamps = [tx.get('timestamp') for tx in txs if tx.get('timestamp')]
            if len(timestamps) >= 5:
                try:
                    timestamps.sort()
                    intervals = []
                    for i in range(1, len(timestamps)):
                        t1 = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                        t2 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                        intervals.append((t2 - t1).total_seconds())
                    
                    if intervals:
                        variance = sum((i - sum(intervals)/len(intervals))**2 for i in intervals) / len(intervals)
                        if variance < 60:  # Very regular
                            score += 0.4
                            matched.append('Highly regular intervals (bot-like)')
                except:
                    pass
        
        # Identical amounts
        amounts = []
        for tx in txs:
            try:
                amounts.append(round(float(tx.get('value', 0)), 2))
            except:
                pass
        
        if amounts:
            from collections import Counter
            most_common = Counter(amounts).most_common(1)[0]
            if most_common[1] >= len(amounts) * 0.7:
                score += 0.3
                matched.append('Identical transaction amounts')
        
        return min(score, 1.0), matched
    
    def _check_bot_coordinator(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for bot farm coordinator patterns"""
        # This requires batch analysis - handled separately
        return 0.0, []
    
    def _check_sybil(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for sybil attacker patterns"""
        score = 0.0
        matched = []
        
        # Fresh wallet
        age_days = wallet.get('creation_age_days')
        if age_days is not None and age_days < 30:
            score += 0.2
            matched.append('Recently created')
        
        # Interacts with protocols (DeFi)
        contracts = set()
        for tx in txs:
            to = tx.get('to')
            if to and len(str(to)) == 42:  # Contract address
                contracts.add(to)
        
        if len(contracts) >= 3:
            score += 0.2
            matched.append('Multiple protocol interactions')
        
        return min(score, 0.5), matched  # Sybil needs batch analysis for higher confidence
    
    def _check_mixer_usage(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for mixer usage"""
        score = 0.0
        matched = []
        
        known_mixers = [
            '0x4736dCf1b7A3d580672CcE6E7c65cd5cc9cFba9D',  # Tornado Cash
            # Add more as needed
        ]
        
        for tx in txs:
            to = tx.get('to', '').lower()
            if to in [m.lower() for m in known_mixers]:
                score += 0.9
                matched.append(f'Transaction to mixer: {to[:20]}...')
                break
        
        return min(score, 1.0), matched
    
    def _check_laundering_layer(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for laundering layer patterns"""
        score = 0.0
        matched = []
        
        if len(txs) < 3:
            return score, matched
        
        # Receives then immediately forwards
        holding_times = []
        for i in range(len(txs) - 1):
            try:
                t1 = datetime.fromisoformat(txs[i].get('timestamp', '').replace('Z', '+00:00'))
                t2 = datetime.fromisoformat(txs[i+1].get('timestamp', '').replace('Z', '+00:00'))
                holding_times.append((t2 - t1).total_seconds() / 60)
            except:
                pass
        
        if holding_times:
            avg_hold = sum(holding_times) / len(holding_times)
            if avg_hold < 60:  # Less than 1 hour average
                score += 0.5
                matched.append('Very short holding periods')
        
        # Round amounts
        round_count = sum(1 for tx in txs 
            if abs(float(tx.get('value', 0)) - round(float(tx.get('value', 0)))) < 0.01)
        if round_count >= len(txs) * 0.8:
            score += 0.3
            matched.append('Mostly round amounts')
        
        return min(score, 1.0), matched
    
    def _check_pump_dump(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for pump and dump patterns"""
        score = 0.0
        matched = []
        
        # Rapid buy/sell
        if len(txs) >= 6:
            timestamps = []
            for tx in txs:
                try:
                    timestamps.append(datetime.fromisoformat(tx.get('timestamp', '').replace('Z', '+00:00')))
                except:
                    pass
            
            if len(timestamps) >= 6:
                timestamps.sort()
                time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                if time_span < 24:  # 6+ txns in 24 hours
                    score += 0.4
                    matched.append('High frequency trading')
        
        return min(score, 0.8), matched  # Needs token analysis for full confidence
    
    def _check_market_manipulation(self, wallet: Dict, txs: List[Dict]) -> tuple:
        """Check for market manipulation patterns"""
        score = 0.0
        matched = []
        
        # Wash trading: similar buy/sell amounts to/from same address
        pairs = defaultdict(lambda: {'buys': 0, 'sells': 0})
        
        for tx in txs:
            to = tx.get('to')
            from_ = tx.get('from')
            try:
                value = float(tx.get('value', 0))
                if to:
                    pairs[to]['buys'] += value
                if from_:
                    pairs[from_]['sells'] += value
            except:
                pass
        
        # Check for wash trading
        wash_trading = False
        for addr, amounts in pairs.items():
            if amounts['buys'] > 0 and amounts['sells'] > 0:
                ratio = min(amounts['buys'], amounts['sells']) / max(amounts['buys'], amounts['sells'])
                if ratio > 0.8:  # Similar buy/sell amounts
                    wash_trading = True
                    break
        
        if wash_trading:
            score += 0.7
            matched.append('Wash trading patterns detected')
        
        return min(score, 1.0), matched
    
    def _find_coordinated_groups(self, wallets: List[Dict], classifications: Dict) -> List[Dict]:
        """Find groups of wallets acting together"""
        groups = []
        
        # Group by funding source
        funding_groups = defaultdict(list)
        for wallet in wallets:
            funding = wallet.get('funding_source')
            if funding:
                funding_groups[funding].append(wallet.get('address'))
        
        for source, addresses in funding_groups.items():
            if len(addresses) >= 5:
                groups.append({
                    'type': 'SHARED_FUNDING',
                    'funding_source': source,
                    'wallets': addresses,
                    'count': len(addresses),
                    'likely_sybil': True
                })
        
        # Group by creation time
        creation_groups = defaultdict(list)
        for wallet in wallets:
            creation = wallet.get('estimated_creation')
            if creation:
                # Group by hour
                try:
                    dt = datetime.fromisoformat(creation.replace('Z', '+00:00'))
                    hour_key = dt.strftime('%Y-%m-%d-%H')
                    creation_groups[hour_key].append(wallet.get('address'))
                except:
                    pass
        
        for hour, addresses in creation_groups.items():
            if len(addresses) >= 5:
                groups.append({
                    'type': 'COORDINATED_CREATION',
                    'creation_hour': hour,
                    'wallets': addresses,
                    'count': len(addresses),
                    'likely_bot_farm': True
                })
        
        return groups


if __name__ == "__main__":
    print("Wallet Classifier initialized")
    print(f"Defined {len(SUSPICIOUS_WALLET_TYPES)} suspicious wallet types")
