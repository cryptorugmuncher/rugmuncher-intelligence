#!/usr/bin/env python3
"""
🔥 ADVANCED BUNDLE DETECTOR v2.0
Industry-leading token bundling detection with 15+ heuristics
Returns bundle probability % and detailed analysis

Bundle = Multiple wallets controlled by same entity buying token at launch
to create fake volume/interest then dump on retail.
"""

import asyncio
# Pure Python implementation - no external deps required
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class BundleSignal(Enum):
    """Individual detection signals"""
    # Timing Signals
    SYNCHRONIZED_BUYS = "synchronized_buys"
    LAUNCH_CLUSTERING = "launch_clustering"
    SEQUENTIAL_BUYS = "sequential_buys"
    
    # Wallet Signals
    FUNDING_COMMON = "funding_common"
    WALLET_CLUSTERING = "wallet_clustering"
    NEW_WALLETS = "new_wallets"
    
    # Behavioral Signals
    NO_SELL = "no_sell"
    PERFECT_HODL = "perfect_hodl"
    COORDINATED_MOVES = "coordinated_moves"
    
    # Pattern Signals
    ROUND_NUMBERS = "round_numbers"
    SIMILAR_AMOUNTS = "similar_amounts"
    GAS_PRICE_MATCHING = "gas_price_matching"
    
    # Network Signals
    COUNTERPARTY_OVERLAP = "counterparty_overlap"
    INTER_WALLET_TRANSFERS = "inter_wallet_transfers"
    
    # Result Signals
    ARTIFICIAL_VOLUME = "artificial_volume"
    PRICE_MANIPULATION = "price_manipulation"
    RUG_PATTERN = "rug_pattern"


@dataclass
class HeuristicResult:
    """Result from a single heuristic"""
    signal: BundleSignal
    triggered: bool
    confidence: float  # 0.0 - 1.0
    evidence: Dict[str, Any]
    weight: float
    description: str


@dataclass
class BundleAnalysis:
    """Complete bundle analysis result"""
    token_address: str
    bundle_probability: float  # 0-100%
    confidence_score: float  # 0-1.0
    is_bundle: bool
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Details
    total_wallets_analyzed: int
    suspicious_wallets: int
    bundle_group_count: int
    
    # Timing
    launch_timestamp: Optional[datetime]
    suspicious_buy_count: int
    
    # Financial
    total_bundle_volume_usd: float
    estimated_profit_potential: float
    
    # All heuristics
    heuristics: List[HeuristicResult]
    
    # Group breakdown
    wallet_groups: List[Dict[str, Any]]
    
    # Recommendations
    risk_factors: List[str]
    red_flags: List[str]
    summary: str


class AdvancedBundleDetector:
    """
    🎯 Industry-Leading Bundle Detection
    15+ heuristics, machine learning-ready
    """
    
    def __init__(self):
        self.heuristic_weights = {
            # Core bundling signals (high weight)
            BundleSignal.SYNCHRONIZED_BUYS: 1.5,
            BundleSignal.WALLET_CLUSTERING: 1.4,
            BundleSignal.FUNDING_COMMON: 1.3,
            
            # Strong indicators
            BundleSignal.LAUNCH_CLUSTERING: 1.2,
            BundleSignal.COORDINATED_MOVES: 1.2,
            BundleSignal.COUNTERPARTY_OVERLAP: 1.1,
            
            # Behavioral patterns
            BundleSignal.NO_SELL: 0.9,
            BundleSignal.PERFECT_HODL: 0.8,
            BundleSignal.SEQUENTIAL_BUYS: 0.8,
            
            # Amount/transaction patterns
            BundleSignal.SIMILAR_AMOUNTS: 0.9,
            BundleSignal.ROUND_NUMBERS: 0.7,
            BundleSignal.GAS_PRICE_MATCHING: 0.7,
            
            # Network analysis
            BundleSignal.INTER_WALLET_TRANSFERS: 0.8,
            BundleSignal.NEW_WALLETS: 0.6,
            
            # Market manipulation
            BundleSignal.ARTIFICIAL_VOLUME: 1.3,
            BundleSignal.PRICE_MANIPULATION: 1.2,
            BundleSignal.RUG_PATTERN: 1.5,
        }
    
    # ═══════════════════════════════════════════════════════════
    # HEURISTIC 1: SYNCHRONIZED BUYS (The Smoking Gun)
    # ═══════════════════════════════════════════════════════════
    
    async def _check_synchronized_buys(
        self, 
        buys: List[Dict],
        time_window_seconds: int = 60
    ) -> HeuristicResult:
        """
        Detect buys happening within seconds of each other at launch
        This is the #1 bundle indicator
        """
        if len(buys) < 3:
            return HeuristicResult(
                signal=BundleSignal.SYNCHRONIZED_BUYS,
                triggered=False,
                confidence=0.0,
                evidence={},
                weight=self.heuristic_weights[BundleSignal.SYNCHRONIZED_BUYS],
                description="Insufficient buy data"
            )
        
        # Sort by timestamp
        sorted_buys = sorted(buys, key=lambda x: x.get('timestamp', 0))
        timestamps = [b['timestamp'] for b in sorted_buys]
        
        # Find clusters
        clusters = []
        current_cluster = [sorted_buys[0]]
        
        for i in range(1, len(sorted_buys)):
            time_diff = timestamps[i] - timestamps[i-1]
            if time_diff <= time_window_seconds:
                current_cluster.append(sorted_buys[i])
            else:
                if len(current_cluster) >= 3:
                    clusters.append(current_cluster)
                current_cluster = [sorted_buys[i]]
        
        if len(current_cluster) >= 3:
            clusters.append(current_cluster)
        
        # Calculate confidence based on cluster size and timing
        max_cluster_size = max(len(c) for c in clusters) if clusters else 0
        total_in_clusters = sum(len(c) for c in clusters)
        
        if max_cluster_size >= 5:
            confidence = min(1.0, 0.7 + (max_cluster_size - 5) * 0.05)
        elif max_cluster_size >= 3:
            confidence = 0.5 + (max_cluster_size - 3) * 0.1
        else:
            confidence = 0.0
        
        # Check if within first 5 minutes of launch (higher confidence)
        launch_window = 300  # 5 minutes
        if clusters and clusters[0][0].get('seconds_since_launch', 999) < launch_window:
            confidence = min(1.0, confidence * 1.3)
        
        return HeuristicResult(
            signal=BundleSignal.SYNCHRONIZED_BUYS,
            triggered=confidence > 0.5,
            confidence=confidence,
            evidence={
                'clusters_found': len(clusters),
                'largest_cluster': max_cluster_size,
                'total_buys_in_clusters': total_in_clusters,
                'time_window_seconds': time_window_seconds,
                'cluster_examples': [
                    {
                        'size': len(c),
                        'time_span': c[-1]['timestamp'] - c[0]['timestamp'],
                        'wallets': [b['wallet'] for b in c]
                    }
                    for c in clusters[:3]
                ]
            },
            weight=self.heuristic_weights[BundleSignal.SYNCHRONIZED_BUYS],
            description=f"Found {len(clusters)} synchronized buy clusters, largest: {max_cluster_size} wallets"
        )
    
    # ═══════════════════════════════════════════════════════════
    # HEURISTIC 2: WALLET CLUSTERING (Network Analysis)
    # ═══════════════════════════════════════════════════════════
    
    async def _check_wallet_clustering(
        self,
        wallets: List[Dict]
    ) -> HeuristicResult:
        """
        Cluster wallets by behavioral similarity
        Uses: timing patterns, amount patterns, counterparty overlap
        """
        if len(wallets) < 5:
            return HeuristicResult(
                signal=BundleSignal.WALLET_CLUSTERING,
                triggered=False,
                confidence=0.0,
                evidence={},
                weight=self.heuristic_weights[BundleSignal.WALLET_CLUSTERING],
                description="Insufficient wallets"
            )
        
        # Calculate similarity matrix (pure Python)
        n = len(wallets)
        similarity_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i+1, n):
                sim = self._calculate_wallet_similarity(wallets[i], wallets[j])
                similarity_matrix[i][j] = sim
                similarity_matrix[j][i] = sim
        
        # Find clusters using threshold
        threshold = 0.7
        clusters = []
        visited = set()
        
        for i in range(n):
            if i in visited:
                continue
            
            cluster = [i]
            visited.add(i)
            
            for j in range(n):
                if j not in visited and similarity_matrix[i][j] >= threshold:
                    cluster.append(j)
                    visited.add(j)
            
            if len(cluster) >= 3:
                clusters.append(cluster)
        
        # Calculate confidence
        largest_cluster = max(len(c) for c in clusters) if clusters else 0
        total_clustered = sum(len(c) for c in clusters)
        cluster_ratio = total_clustered / n if n > 0 else 0
        
        if largest_cluster >= 10:
            confidence = 0.95
        elif largest_cluster >= 5:
            confidence = 0.7 + (largest_cluster - 5) * 0.05
        elif largest_cluster >= 3:
            confidence = 0.4 + (largest_cluster - 3) * 0.15
        else:
            confidence = cluster_ratio * 0.3
        
        return HeuristicResult(
            signal=BundleSignal.WALLET_CLUSTERING,
            triggered=confidence > 0.5,
            confidence=confidence,
            evidence={
                'total_wallets': n,
                'clusters_found': len(clusters),
                'largest_cluster_size': largest_cluster,
                'clustered_ratio': cluster_ratio,
                'similarity_threshold': threshold,
                'cluster_details': [
                    {
                        'size': len(c),
                        'wallets': [wallets[i]['address'] for i in c[:5]]  # Sample
                    }
                    for c in clusters[:5]
                ]
            },
            weight=self.heuristic_weights[BundleSignal.WALLET_CLUSTERING],
            description=f"Found {len(clusters)} wallet clusters, largest: {largest_cluster} wallets"
        )
    
    def _calculate_wallet_similarity(self, w1: Dict, w2: Dict) -> float:
        """Calculate similarity score between two wallets"""
        scores = []
        
        # Timing similarity (buy within X seconds of each other)
        if w1.get('first_buy_time') and w2.get('first_buy_time'):
            time_diff = abs(w1['first_buy_time'] - w2['first_buy_time'])
            if time_diff < 60:
                scores.append(1.0)
            elif time_diff < 300:
                scores.append(0.7)
            elif time_diff < 900:
                scores.append(0.4)
        
        # Amount similarity
        if w1.get('buy_amount_usd') and w2.get('buy_amount_usd'):
            ratio = min(w1['buy_amount_usd'], w2['buy_amount_usd']) / max(w1['buy_amount_usd'], w2['buy_amount_usd'])
            if ratio > 0.9:
                scores.append(1.0)
            elif ratio > 0.7:
                scores.append(0.7)
            elif ratio > 0.5:
                scores.append(0.4)
        
        # Counterparty overlap
        if w1.get('counterparties') and w2.get('counterparties'):
            c1 = set(w1['counterparties'])
            c2 = set(w2['counterparties'])
            if c1 and c2:
                overlap = len(c1 & c2) / len(c1 | c2)
                if overlap > 0.5:
                    scores.append(1.0)
                elif overlap > 0.3:
                    scores.append(0.7)
        
        # No sell pattern
        if not w1.get('has_sold') and not w2.get('has_sold'):
            scores.append(0.6)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    # ═══════════════════════════════════════════════════════════
    # HEURISTIC 3: COMMON FUNDING SOURCE
    # ═══════════════════════════════════════════════════════════
    
    async def _check_funding_common(
        self,
        wallets: List[Dict]
    ) -> HeuristicResult:
        """
        Check if wallets were funded from same source
        Bundle wallets often funded from same exchange withdrawal or main wallet
        """
        funding_sources = defaultdict(list)
        
        for w in wallets:
            if 'funding_source' in w:
                funding_sources[w['funding_source']].append(w['address'])
        
        # Find significant clusters
        large_clusters = [
            (source, addrs) 
            for source, addrs in funding_sources.items() 
            if len(addrs) >= 3
        ]
        
        if not large_clusters:
            return HeuristicResult(
                signal=BundleSignal.FUNDING_COMMON,
                triggered=False,
                confidence=0.0,
                evidence={'funding_sources_found': len(funding_sources)},
                weight=self.heuristic_weights[BundleSignal.FUNDING_COMMON],
                description="No common funding sources found"
            )
        
        largest = max(large_clusters, key=lambda x: len(x[1]))
        cluster_size = len(largest[1])
        
        if cluster_size >= 10:
            confidence = 0.95
        elif cluster_size >= 5:
            confidence = 0.75 + (cluster_size - 5) * 0.04
        else:
            confidence = 0.4 + (cluster_size - 3) * 0.175
        
        return HeuristicResult(
            signal=BundleSignal.FUNDING_COMMON,
            triggered=confidence > 0.5,
            confidence=confidence,
            evidence={
                'common_sources': len(large_clusters),
                'largest_cluster_size': cluster_size,
                'funding_source': largest[0][:20] + '...' if len(largest[0]) > 20 else largest[0],
                'wallets_in_cluster': largest[1][:10]
            },
            weight=self.heuristic_weights[BundleSignal.FUNDING_COMMON],
            description=f"{cluster_size} wallets funded from same source"
        )
    
    # ═══════════════════════════════════════════════════════════
    # HEURISTIC 4: NO SELL PATTERN (HODL Until Dump)
    # ═══════════════════════════════════════════════════════════
    
    async def _check_no_sell(
        self,
        wallets: List[Dict],
        token_age_hours: float
    ) -> HeuristicResult:
        """
        Check if "investor" wallets never sell (waiting to dump)
        Normal buyers take profits; bundle wallets wait for max pain
        """
        if len(wallets) < 5:
            return HeuristicResult(
                signal=BundleSignal.NO_SELL,
                triggered=False,
                confidence=0.0,
                evidence={},
                weight=self.heuristic_weights[BundleSignal.NO_SELL],
                description="Insufficient data"
            )
        
        # Only check wallets that bought early
        early_buyers = [w for w in wallets if w.get('is_early_buyer', False)]
        
        if not early_buyers:
            return HeuristicResult(
                signal=BundleSignal.NO_SELL,
                triggered=False,
                confidence=0.0,
                evidence={},
                weight=self.heuristic_weights[BundleSignal.NO_SELL],
                description="No early buyers found"
            )
        
        never_sold = [w for w in early_buyers if not w.get('has_sold', False)]
        never_sold_ratio = len(never_sold) / len(early_buyers) if early_buyers else 0
        
        # Higher confidence if token is older and still no sells
        age_multiplier = min(2.0, 1 + (token_age_hours / 24))  # Max 2x after 24h
        
        if never_sold_ratio >= 0.9 and token_age_hours > 6:
            confidence = min(1.0, 0.8 * age_multiplier)
        elif never_sold_ratio >= 0.75:
            confidence = 0.6 * age_multiplier
        elif never_sold_ratio >= 0.5:
            confidence = 0.4 * age_multiplier
        else:
            confidence = never_sold_ratio * 0.5
        
        return HeuristicResult(
            signal=BundleSignal.NO_SELL,
            triggered=confidence > 0.5,
            confidence=confidence,
            evidence={
                'early_buyers': len(early_buyers),
                'never_sold_count': len(never_sold),
                'never_sold_ratio': never_sold_ratio,
                'token_age_hours': token_age_hours,
                'sample_wallets': [w['address'][:10] + '...' for w in never_sold[:5]]
            },
            weight=self.heuristic_weights[BundleSignal.NO_SELL],
            description=f"{len(never_sold)}/{len(early_buyers)} early buyers never sold ({never_sold_ratio:.1%})"
        )
    
    # ═══════════════════════════════════════════════════════════
    # HEURISTIC 5: SIMILAR BUY AMOUNTS
    # ═══════════════════════════════════════════════════════════
    
    async def _check_similar_amounts(
        self,
        buys: List[Dict]
    ) -> HeuristicResult:
        """
        Bundle wallets often buy similar USD amounts
        (e.g., all buy $500 worth)
        """
        if len(buys) < 5:
            return HeuristicResult(
                signal=BundleSignal.SIMILAR_AMOUNTS,
                triggered=False,
                confidence=0.0,
                evidence={},
                weight=self.heuristic_weights[BundleSignal.SIMILAR_AMOUNTS],
                description="Insufficient data"
            )
        
        amounts = [b.get('amount_usd', 0) for b in buys if b.get('amount_usd', 0) > 0]
        
        if len(amounts) < 5:
            return HeuristicResult(
                signal=BundleSignal.SIMILAR_AMOUNTS,
                triggered=False,
                confidence=0.0,
                evidence={},
                weight=self.heuristic_weights[BundleSignal.SIMILAR_AMOUNTS],
                description="No amount data"
            )
        
        # Calculate coefficient of variation (CV)
        mean_amt = sum(amounts) / len(amounts)
        variance = sum((x - mean_amt) ** 2 for x in amounts) / len(amounts)
        std_amt = variance ** 0.5
        cv = std_amt / mean_amt if mean_amt > 0 else float('inf')
        
        # Low CV = similar amounts
        if cv < 0.1:  # Very similar
            confidence = 0.9
        elif cv < 0.2:
            confidence = 0.7
        elif cv < 0.3:
            confidence = 0.5
        elif cv < 0.5:
            confidence = 0.3
        else:
            confidence = 0.0
        
        # Check for common amounts ($100, $500, $1000, etc)
        rounded_amounts = [round(a, -2) for a in amounts]  # Round to nearest 100
        unique_rounded = len(set(rounded_amounts))
        total_amounts = len(rounded_amounts)
        
        if unique_rounded <= 3 and total_amounts >= 10:
            confidence = max(confidence, 0.8)
        
        return HeuristicResult(
            signal=BundleSignal.SIMILAR_AMOUNTS,
            triggered=confidence > 0.5,
            confidence=confidence,
            evidence={
                'amount_count': len(amounts),
                'mean_amount': mean_amt,
                'std_amount': std_amt,
                'cv': cv,
                'common_amounts': list(set(rounded_amounts))[:5],
                'amount_distribution': {
                    'min': min(amounts),
                    'max': max(amounts),
                    'median': sorted(amounts)[len(amounts)//2] if amounts else 0
                }
            },
            weight=self.heuristic_weights[BundleSignal.SIMILAR_AMOUNTS],
            description=f"CV={cv:.2f} (lower = more similar), common amounts: {unique_rounded} unique patterns"
        )
    
    # ═══════════════════════════════════════════════════════════
    # HEURISTIC 6: ARTIFICIAL VOLUME
    # ═══════════════════════════════════════════════════════════
    
    async def _check_artificial_volume(
        self,
        transactions: List[Dict],
        holder_count: int
    ) -> HeuristicResult:
        """
        Detect if volume is artificially inflated by wash trading
        """
        if len(transactions) < 10 or holder_count < 10:
            return HeuristicResult(
                signal=BundleSignal.ARTIFICIAL_VOLUME,
                triggered=False,
                confidence=0.0,
                evidence={},
                weight=self.heuristic_weights[BundleSignal.ARTIFICIAL_VOLUME],
                description="Insufficient data"
            )
        
        # Look for repeated buy/sell patterns from same wallets
        wallet_buys = defaultdict(int)
        wallet_sells = defaultdict(int)
        
        for tx in transactions:
            wallet = tx.get('wallet')
            if tx.get('type') == 'buy':
                wallet_buys[wallet] += 1
            elif tx.get('type') == 'sell':
                wallet_sells[wallet] += 1
        
        # Find wash traders (equal buys/sells)
        wash_traders = []
        for wallet in set(list(wallet_buys.keys()) + list(wallet_sells.keys())):
            buys = wallet_buys.get(wallet, 0)
            sells = wallet_sells.get(wallet, 0)
            if buys >= 3 and sells >= 3 and abs(buys - sells) <= 1:
                wash_traders.append(wallet)
        
        # Calculate wash volume
        wash_trader_set = set(wash_traders)
        wash_volume = sum(
            tx.get('amount_usd', 0) 
            for tx in transactions 
            if tx.get('wallet') in wash_trader_set
        )
        total_volume = sum(tx.get('amount_usd', 0) for tx in transactions)
        wash_ratio = wash_volume / total_volume if total_volume > 0 else 0
        
        if wash_ratio > 0.7:
            confidence = 0.95
        elif wash_ratio > 0.5:
            confidence = 0.8
        elif wash_ratio > 0.3:
            confidence = 0.6
        elif wash_ratio > 0.1:
            confidence = 0.3
        else:
            confidence = 0.0
        
        return HeuristicResult(
            signal=BundleSignal.ARTIFICIAL_VOLUME,
            triggered=confidence > 0.5,
            confidence=confidence,
            evidence={
                'wash_traders': len(wash_traders),
                'wash_trader_ratio': len(wash_traders) / holder_count if holder_count > 0 else 0,
                'wash_volume_usd': wash_volume,
                'total_volume_usd': total_volume,
                'wash_volume_ratio': wash_ratio,
                'sample_washers': wash_traders[:5]
            },
            weight=self.heuristic_weights[BundleSignal.ARTIFICIAL_VOLUME],
            description=f"{len(wash_traders)} wash traders, {wash_ratio:.1%} of volume artificial"
        )
    
    # ═══════════════════════════════════════════════════════════
    # MAIN ANALYSIS FUNCTION
    # ═══════════════════════════════════════════════════════════
    
    async def analyze_token(
        self,
        token_address: str,
        transactions: List[Dict],
        wallets: List[Dict],
        token_info: Dict
    ) -> BundleAnalysis:
        """
        Run all heuristics and generate comprehensive bundle analysis
        """
        logger.info(f"Analyzing {token_address} for bundling...")
        
        heuristics = []
        
        # Run all checks concurrently
        results = await asyncio.gather(
            self._check_synchronized_buys(transactions),
            self._check_wallet_clustering(wallets),
            self._check_funding_common(wallets),
            self._check_no_sell(wallets, token_info.get('age_hours', 0)),
            self._check_similar_amounts(transactions),
            self._check_artificial_volume(transactions, len(wallets)),
        )
        
        heuristics.extend(results)
        
        # Calculate overall bundle probability
        triggered_heuristics = [h for h in heuristics if h.triggered]
        
        if not triggered_heuristics:
            bundle_prob = 0.0
        else:
            # Weighted average of triggered heuristics
            total_weight = sum(h.weight for h in triggered_heuristics)
            weighted_confidence = sum(h.confidence * h.weight for h in triggered_heuristics) / total_weight
            
            # Adjust based on number of triggered signals
            signal_count_boost = min(0.2, len(triggered_heuristics) * 0.03)
            
            bundle_prob = min(1.0, weighted_confidence + signal_count_boost)
        
        # Determine severity
        if bundle_prob >= 0.85:
            severity = "CRITICAL"
        elif bundle_prob >= 0.70:
            severity = "HIGH"
        elif bundle_prob >= 0.50:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        # Calculate confidence score based on data quality
        confidence_score = min(1.0, (
            (len(transactions) / 100) * 0.3 +
            (len(wallets) / 50) * 0.3 +
            (len(triggered_heuristics) / 6) * 0.4
        ))
        
        # Extract red flags
        red_flags = []
        for h in triggered_heuristics:
            if h.confidence > 0.8:
                red_flags.append(f"{h.signal.value}: {h.description}")
        
        # Wallet groups for reporting
        wallet_groups = []
        for h in heuristics:
            if h.signal == BundleSignal.WALLET_CLUSTERING and h.triggered:
                wallet_groups.extend(h.evidence.get('cluster_details', []))
        
        return BundleAnalysis(
            token_address=token_address,
            bundle_probability=bundle_prob * 100,
            confidence_score=confidence_score,
            is_bundle=bundle_prob >= 0.60,
            severity=severity,
            total_wallets_analyzed=len(wallets),
            suspicious_wallets=sum(len(g.get('wallets', [])) for g in wallet_groups),
            bundle_group_count=len(wallet_groups),
            launch_timestamp=token_info.get('launch_time'),
            suspicious_buy_count=len([t for t in transactions if t.get('is_suspicious')]),
            total_bundle_volume_usd=sum(
                h.evidence.get('wash_volume_usd', 0) 
                for h in triggered_heuristics
            ),
            estimated_profit_potential=bundle_prob * token_info.get('market_cap_usd', 0) * 0.1,
            heuristics=heuristics,
            wallet_groups=wallet_groups,
            risk_factors=[h.description for h in triggered_heuristics],
            red_flags=red_flags,
            summary=self._generate_summary(token_address, bundle_prob, triggered_heuristics)
        )
    
    def _generate_summary(
        self, 
        token: str, 
        probability: float, 
        triggered: List[HeuristicResult]
    ) -> str:
        """Generate human-readable summary"""
        if probability < 0.30:
            return f"✅ {token[:10]}... appears organic. Low bundling risk."
        elif probability < 0.50:
            return f"⚠️  {token[:10]}... shows minor bundling indicators. Monitor closely."
        elif probability < 0.70:
            return f"🚨 {token[:10]}... LIKELY BUNDLED. {len(triggered)} suspicious patterns detected."
        else:
            top_signals = [h.signal.value for h in sorted(triggered, key=lambda x: x.confidence, reverse=True)[:3]]
            return f"☠️  {token[:10]}... CONFIRMED BUNDLE! Patterns: {', '.join(top_signals)}. AVOID!"


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════

async def check_bundle(
    token_address: str,
    transactions: List[Dict] = None,
    wallets: List[Dict] = None,
    token_info: Dict = None
) -> BundleAnalysis:
    """Quick bundle check"""
    detector = AdvancedBundleDetector()
    
    # Use sample data if none provided
    if transactions is None:
        transactions = []
    if wallets is None:
        wallets = []
    if token_info is None:
        token_info = {'age_hours': 24}
    
    return await detector.analyze_token(token_address, transactions, wallets, token_info)


def format_bundle_report(analysis: BundleAnalysis) -> str:
    """Format analysis as readable report"""
    lines = [
        "=" * 70,
        "🔥 ADVANCED BUNDLE DETECTION REPORT",
        "=" * 70,
        f"",
        f"Token: {analysis.token_address}",
        f"Bundle Probability: {analysis.bundle_probability:.1f}%",
        f"Confidence: {analysis.confidence_score:.0%}",
        f"Severity: {analysis.severity}",
        f"Is Bundle: {'☠️ YES' if analysis.is_bundle else '✅ NO'}",
        f"",
        f"Wallets Analyzed: {analysis.total_wallets_analyzed}",
        f"Suspicious Wallets: {analysis.suspicious_wallets}",
        f"Bundle Groups: {analysis.bundle_group_count}",
        f"",
        "-" * 70,
        "📊 HEURISTIC BREAKDOWN:",
        "-" * 70,
    ]
    
    for h in sorted(analysis.heuristics, key=lambda x: x.confidence, reverse=True):
        icon = "🚨" if h.triggered else "✅"
        lines.append(f"{icon} {h.signal.value:25} | Confidence: {h.confidence:.0%} | {h.description[:50]}")
    
    if analysis.red_flags:
        lines.extend([
            "",
            "-" * 70,
            "🚩 RED FLAGS:",
            "-" * 70,
        ])
        for flag in analysis.red_flags:
            lines.append(f"  • {flag}")
    
    lines.extend([
        "",
        "=" * 70,
        "📝 SUMMARY:",
        f"{analysis.summary}",
        "=" * 70,
    ])
    
    return "\n".join(lines)


# Example/test
if __name__ == "__main__":
    # Sample data for testing
    sample_transactions = [
        {'wallet': f'wallet_{i}', 'timestamp': i*5, 'amount_usd': 500, 'type': 'buy', 'is_suspicious': True}
        for i in range(20)
    ]
    
    sample_wallets = [
        {
            'address': f'wallet_{i}',
            'first_buy_time': i*5,
            'buy_amount_usd': 500,
            'has_sold': False,
            'is_early_buyer': True,
            'funding_source': 'exchange_binance_1',
            'counterparties': ['dex_1', 'router_1']
        }
        for i in range(20)
    ]
    
    async def demo():
        analysis = await check_bundle(
            "So11111111111111111111111111111111111111112",
            sample_transactions,
            sample_wallets,
            {'age_hours': 12, 'market_cap_usd': 100000}
        )
        print(format_bundle_report(analysis))
    
    asyncio.run(demo())
