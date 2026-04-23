#!/usr/bin/env python3
"""
MunchMaps V2 Integration - The Complete Bubblemaps Killer
Integrates all advanced analysis modules into one powerful engine
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')
sys.path.insert(0, '/root/rmi/munchmaps/v2_advanced')
sys.path.insert(0, '/root/rmi/munchmaps/v2_advanced/analysis')

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import all our analysis modules
from temporal_analyzer import TemporalAnalyzer
from behavioral_clusterer import BehavioralClusterer
from cross_chain_detector import CrossChainDetector
from multihop_tracer import MultiHopTracer
from anomaly_detector import StatisticalAnomalyDetector
from interactive_features import InteractiveFeatures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MunchMapsV2Engine:
    """
    Complete MunchMaps V2 Analysis Engine
    
    Features that surpass Bubblemaps:
    - Temporal timeline with playback
    - CEX funding detection
    - Fresh wallet identification
    - Similar amount clustering
    - Multi-hop relationship tracing
    - Cross-chain connection detection
    - Statistical anomaly detection
    - Behavioral clustering
    - Interactive exploration
    """
    
    def __init__(self):
        self.temporal_analyzer = TemporalAnalyzer()
        self.behavioral_clusterer = BehavioralClusterer()
        self.cross_chain_detector = CrossChainDetector()
        self.multihop_tracer = MultiHopTracer(max_hops=3)
        self.anomaly_detector = StatisticalAnomalyDetector()
        self.interactive = InteractiveFeatures()
        
        self.analysis_cache = {}
    
    def analyze_token_network(
        self,
        token_address: str,
        wallets: List[Dict],
        options: Dict = None
    ) -> Dict:
        """
        Complete analysis of a token's wallet network
        
        This is the main entry point that rivals Bubblemaps
        """
        if options is None:
            options = {}
        
        logger.info(f"Starting MunchMaps V2 analysis for {token_address}")
        logger.info(f"Analyzing {len(wallets)} wallets")
        
        start_time = datetime.now()
        
        # Step 1: Temporal Analysis
        logger.info("Step 1: Temporal analysis...")
        temporal_results = self._run_temporal_analysis(wallets, options)
        
        # Step 2: Behavioral Clustering
        logger.info("Step 2: Behavioral clustering...")
        behavioral_clusters = self._run_behavioral_clustering(wallets, options)
        
        # Step 3: Cross-Chain Detection
        logger.info("Step 3: Cross-chain detection...")
        cross_chain_results = self._run_cross_chain_detection(wallets, options)
        
        # Step 4: Multi-Hop Relationship Tracing
        logger.info("Step 4: Multi-hop relationship tracing...")
        multihop_results = self._run_multihop_analysis(wallets, options)
        
        # Step 5: Statistical Anomaly Detection
        logger.info("Step 5: Statistical anomaly detection...")
        anomalies = self._run_anomaly_detection(wallets, options)
        
        # Step 6: Generate Network Visualization Data
        logger.info("Step 6: Generating network visualization...")
        network_data = self._generate_network_data(wallets, {
            'temporal': temporal_results,
            'behavioral': behavioral_clusters,
            'cross_chain': cross_chain_results,
            'multihop': multihop_results,
            'anomalies': anomalies
        })
        
        # Step 7: Generate Interactive Features
        logger.info("Step 7: Generating interactive features...")
        self._generate_interactive_features(wallets, network_data, {
            'temporal': temporal_results,
            'behavioral': behavioral_clusters,
            'cross_chain': cross_chain_results,
            'multihop': multihop_results,
            'anomalies': anomalies
        })
        
        # Compile final report
        duration = (datetime.now() - start_time).total_seconds()
        
        report = {
            'metadata': {
                'token_address': token_address,
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_duration_seconds': duration,
                'munchmaps_version': '2.0',
                'wallets_analyzed': len(wallets),
                'features_enabled': [
                    'temporal_analysis',
                    'behavioral_clustering',
                    'cross_chain_detection',
                    'multihop_tracing',
                    'anomaly_detection',
                    'interactive_playback',
                    'cex_funding_detection',
                    'fresh_wallet_identification'
                ]
            },
            'executive_summary': self._generate_executive_summary(
                wallets, temporal_results, behavioral_clusters,
                cross_chain_results, multihop_results, anomalies
            ),
            'temporal_analysis': temporal_results,
            'behavioral_clusters': behavioral_clusters,
            'cross_chain_connections': cross_chain_results,
            'multi_hop_relationships': multihop_results,
            'statistical_anomalies': anomalies,
            'network_data': network_data,
            'risk_assessment': self._generate_risk_assessment(
                wallets, behavioral_clusters, anomalies, multihop_results
            ),
            'recommendations': self._generate_recommendations(
                behavioral_clusters, anomalies, cross_chain_results
            )
        }
        
        logger.info(f"Analysis complete in {duration:.2f} seconds")
        
        return report
    
    def _run_temporal_analysis(self, wallets: List[Dict], options: Dict) -> Dict:
        """Run temporal analysis"""
        # Wallet ages
        wallet_ages = self.temporal_analyzer.analyze_wallet_ages(wallets)
        
        # Activity timeline
        timeline = self.temporal_analyzer.build_activity_timeline(wallets)
        
        # CEX funding
        cex_funding = self.temporal_analyzer.detect_cex_funding_patterns(wallets)
        
        # Fresh wallets
        fresh_wallets = self.temporal_analyzer.identify_fresh_wallets(wallets)
        
        # Playback frames
        frames = self.temporal_analyzer.generate_playback_frames(
            wallets,
            frame_days=options.get('playback_frame_days', 7)
        )
        
        return {
            'wallet_ages': wallet_ages,
            'activity_timeline': timeline,
            'cex_funding': cex_funding,
            'fresh_wallets': fresh_wallets,
            'playback_frames': frames,
            'summary': {
                'fresh_wallet_count': len(fresh_wallets),
                'cex_funded_count': sum(len(c['wallets']) for c in cex_funding),
                'timeline_events': len(timeline)
            }
        }
    
    def _run_behavioral_clustering(self, wallets: List[Dict], options: Dict) -> List[Dict]:
        """Run behavioral clustering"""
        return self.behavioral_clusterer.find_similar_wallets(wallets)
    
    def _run_cross_chain_detection(self, wallets: List[Dict], options: Dict) -> List[Dict]:
        """Run cross-chain detection"""
        if not options.get('enable_cross_chain', True):
            return []
        
        return self.cross_chain_detector.detect_cross_chain_connections(wallets)
    
    def _run_multihop_analysis(self, wallets: List[Dict], options: Dict) -> Dict:
        """Run multi-hop relationship analysis"""
        # Find all connections
        connections = self.multihop_tracer.find_all_connections(
            wallets,
            min_path_length=2,
            max_path_length=options.get('max_hops', 3)
        )
        
        # Find layering patterns
        layering = self.multihop_tracer.find_layering_patterns(wallets)
        
        return {
            'indirect_connections': connections,
            'layering_patterns': layering,
            'summary': {
                'total_indirect_connections': len(connections),
                'layering_patterns_detected': len(layering)
            }
        }
    
    def _run_anomaly_detection(self, wallets: List[Dict], options: Dict) -> List[Dict]:
        """Run statistical anomaly detection"""
        return self.anomaly_detector.analyze_wallets(wallets)
    
    def _generate_network_data(
        self,
        wallets: List[Dict],
        analysis_results: Dict
    ) -> Dict:
        """Generate network visualization data"""
        nodes = []
        edges = []
        
        # Create nodes
        for wallet in wallets:
            node = {
                'id': wallet.get('address'),
                'address': wallet.get('address'),
                'type': wallet.get('wallet_type', 'unknown'),
                'risk_level': wallet.get('risk_level', 'LOW'),
                'risk_score': wallet.get('risk_score', 0),
                'is_fresh_wallet': wallet.get('is_fresh_wallet', False),
                'funding_source': wallet.get('funding_source'),
                'creation_age_days': wallet.get('creation_age_days'),
                'cluster_id': wallet.get('cluster_id'),
                'transaction_count': len(wallet.get('transactions', [])),
                'suspicious_indicators': wallet.get('suspicious_indicators', [])
            }
            nodes.append(node)
        
        # Create edges from transactions
        edge_id = 0
        for wallet in wallets:
            address = wallet.get('address')
            for tx in wallet.get('transactions', []):
                to_addr = tx.get('to')
                if to_addr:
                    edges.append({
                        'id': f"edge_{edge_id}",
                        'source': address,
                        'target': to_addr,
                        'value': tx.get('value_eth') or tx.get('amount', 0),
                        'timestamp': tx.get('timestamp'),
                        'type': tx.get('type', 'transfer')
                    })
                    edge_id += 1
        
        # Add indirect connection edges
        for conn in analysis_results['multihop'].get('indirect_connections', []):
            if conn.get('shortest_path_hops') == 2:
                edges.append({
                    'id': f"indirect_{conn['wallet1']}_{conn['wallet2']}",
                    'source': conn['wallet1'],
                    'target': conn['wallet2'],
                    'type': 'indirect_connection',
                    'path_length': 2,
                    'dashed': True
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'raw_wallets': wallets
        }
    
    def _generate_interactive_features(
        self,
        wallets: List[Dict],
        network_data: Dict,
        analysis_results: Dict
    ):
        """Generate interactive features"""
        # Generate playback frames
        self.interactive.generate_timeline_playback(wallets)
    
    def _generate_executive_summary(
        self,
        wallets: List[Dict],
        temporal: Dict,
        behavioral: List[Dict],
        cross_chain: List[Dict],
        multihop: Dict,
        anomalies: List[Dict]
    ) -> Dict:
        """Generate executive summary"""
        fresh_count = temporal['summary']['fresh_wallet_count']
        cex_count = temporal['summary']['cex_funded_count']
        cluster_count = len(behavioral)
        anomaly_count = len(anomalies)
        layering_count = len(multihop.get('layering_patterns', []))
        
        # Calculate overall risk score
        risk_score = 0
        risk_factors = []
        
        if fresh_count > 10:
            risk_score += 20
            risk_factors.append(f"{fresh_count} fresh wallets detected")
        
        if cex_count > 5:
            risk_score += 15
            risk_factors.append(f"{cex_count} CEX-funded wallets")
        
        if cluster_count > 0:
            risk_score += 25
            risk_factors.append(f"{cluster_count} coordinated clusters")
        
        if anomaly_count > 0:
            risk_score += 20
            risk_factors.append(f"{anomaly_count} statistical anomalies")
        
        if layering_count > 0:
            risk_score += 20
            risk_factors.append(f"{layering_count} layering patterns (possible ML)")
        
        risk_level = 'LOW'
        if risk_score >= 60:
            risk_level = 'CRITICAL'
        elif risk_score >= 40:
            risk_level = 'HIGH'
        elif risk_score >= 20:
            risk_level = 'MEDIUM'
        
        return {
            'overall_risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'key_findings': [
                f"{fresh_count} fresh wallets (< 7 days old)",
                f"{cex_count} wallets funded from CEXs",
                f"{cluster_count} behavioral clusters detected",
                f"{anomaly_count} statistical anomalies",
                f"{layering_count} potential layering patterns",
                f"{len(cross_chain)} cross-chain connections"
            ],
            'risk_factors': risk_factors,
            'wallets_flagged': fresh_count + cex_count
        }
    
    def _generate_risk_assessment(
        self,
        wallets: List[Dict],
        clusters: List[Dict],
        anomalies: List[Dict],
        multihop: Dict
    ) -> Dict:
        """Generate comprehensive risk assessment"""
        return {
            'manipulation_risk': self._assess_manipulation_risk(clusters, anomalies),
            'coordination_risk': self._assess_coordination_risk(clusters),
            'laundering_risk': self._assess_laundering_risk(multihop),
            'bot_activity_risk': self._assess_bot_risk(anomalies),
            'wallet_breakdown': {
                'total': len(wallets),
                'high_risk': sum(1 for w in wallets if w.get('risk_level') == 'HIGH'),
                'medium_risk': sum(1 for w in wallets if w.get('risk_level') == 'MEDIUM'),
                'low_risk': sum(1 for w in wallets if w.get('risk_level') == 'LOW')
            }
        }
    
    def _assess_manipulation_risk(self, clusters: List[Dict], anomalies: List[Dict]) -> Dict:
        """Assess market manipulation risk"""
        score = 0
        indicators = []
        
        # Fresh wallets can indicate pump groups
        fresh_clusters = [c for c in clusters if c.get('type') == 'COORDINATED_CREATION']
        if fresh_clusters:
            score += 30
            indicators.append('Coordinated wallet creation detected')
        
        # Statistical anomalies
        benford = [a for a in anomalies if a.get('type') == 'BENFORD_LAW_VIOLATION']
        if benford:
            score += 25
            indicators.append('Unnatural transaction amounts (Benford violation)')
        
        return {
            'score': min(score, 100),
            'level': 'HIGH' if score >= 50 else 'MEDIUM' if score >= 25 else 'LOW',
            'indicators': indicators
        }
    
    def _assess_coordination_risk(self, clusters: List[Dict]) -> Dict:
        """Assess coordination/sybil risk"""
        score = min(len(clusters) * 20, 100)
        
        return {
            'score': score,
            'level': 'HIGH' if score >= 60 else 'MEDIUM' if score >= 30 else 'LOW',
            'cluster_count': len(clusters),
            'largest_cluster_size': max((c.get('wallet_count', 0) for c in clusters), default=0)
        }
    
    def _assess_laundering_risk(self, multihop: Dict) -> Dict:
        """Assess money laundering risk"""
        layering = multihop.get('layering_patterns', [])
        score = min(len(layering) * 25, 100)
        
        return {
            'score': score,
            'level': 'HIGH' if score >= 50 else 'MEDIUM' if score >= 25 else 'LOW',
            'layering_patterns': len(layering)
        }
    
    def _assess_bot_risk(self, anomalies: List[Dict]) -> Dict:
        """Assess automated/bot activity risk"""
        score = 0
        indicators = []
        
        time_anomalies = [a for a in anomalies if 'TIME' in a.get('type', '')]
        if time_anomalies:
            score += 30
            indicators.append('Unusual transaction timing patterns')
        
        interval_patterns = [a for a in anomalies if 'INTERVAL' in a.get('type', '')]
        if interval_patterns:
            score += 35
            indicators.append('Regular interval patterns detected')
        
        return {
            'score': min(score, 100),
            'level': 'HIGH' if score >= 50 else 'MEDIUM' if score >= 25 else 'LOW',
            'indicators': indicators
        }
    
    def _generate_recommendations(
        self,
        clusters: List[Dict],
        anomalies: List[Dict],
        cross_chain: List[Dict]
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if any(c.get('type') == 'COORDINATED_CREATION' for c in clusters):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Coordination',
                'action': 'Investigate fresh wallet clusters for bot farm/sybil attack',
                'details': 'Multiple wallets created in short time windows suggest automation'
            })
        
        if any(a.get('type') == 'BENFORD_LAW_VIOLATION' for a in anomalies):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Manipulation',
                'action': 'Analyze transaction amounts for wash trading',
                'details': 'Amount distribution does not follow natural patterns'
            })
        
        if cross_chain:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Cross-Chain',
                'action': 'Expand analysis to connected chains',
                'details': f'{len(cross_chain)} cross-chain connections detected'
            })
        
        if any('LAYERING' in str(c.get('type', '')) for c in clusters):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Compliance',
                'action': 'Review for potential money laundering',
                'details': 'Complex transfer chains detected'
            })
        
        recommendations.append({
            'priority': 'LOW',
            'category': 'Monitoring',
            'action': 'Set up continuous monitoring',
            'details': 'Enable alerts for new suspicious patterns'
        })
        
        return recommendations
    
    def export_for_frontend(
        self,
        report: Dict,
        output_path: str = '/root/rmi/munchmaps/v2_advanced/output/munchmaps_v2_export.json'
    ):
        """Export complete analysis for frontend"""
        return self.interactive.export_for_frontend(
            report['network_data'],
            {
                'clusters': report['behavioral_clusters'],
                'anomalies': report['statistical_anomalies'],
                'cross_chain': report['cross_chain_connections'],
                'multihop': report['multi_hop_relationships']
            },
            output_path
        )


def run_demo_analysis():
    """Run a demo analysis with sample data"""
    engine = MunchMapsV2Engine()
    
    # Create sample wallet data
    sample_wallets = [
        {
            'address': '0xabc123...',
            'wallet_type': 'holder',
            'risk_level': 'HIGH',
            'risk_score': 0.85,
            'is_fresh_wallet': True,
            'creation_age_days': 3,
            'funding_source': 'Binance',
            'transactions': [
                {'to': '0xdef456...', 'value_eth': 1.5, 'timestamp': '2024-01-01T10:00:00Z'},
                {'to': '0xghi789...', 'value_eth': 2.0, 'timestamp': '2024-01-02T10:00:00Z'}
            ]
        },
        {
            'address': '0xdef456...',
            'wallet_type': 'trader',
            'risk_level': 'MEDIUM',
            'risk_score': 0.5,
            'is_fresh_wallet': False,
            'creation_age_days': 365,
            'transactions': [
                {'to': '0xjkl012...', 'value_eth': 1.5, 'timestamp': '2024-01-03T10:00:00Z'}
            ]
        }
    ]
    
    report = engine.analyze_token_network('demo_token', sample_wallets)
    
    print("\n" + "="*60)
    print("MUNCHMAPS V2 ANALYSIS COMPLETE")
    print("="*60)
    print(f"\nOverall Risk Level: {report['executive_summary']['overall_risk_level']}")
    print(f"Risk Score: {report['executive_summary']['risk_score']}/100")
    print(f"\nKey Findings:")
    for finding in report['executive_summary']['key_findings']:
        print(f"  • {finding}")
    
    return report


if __name__ == "__main__":
    print("MunchMaps V2 Integration Engine")
    print("="*60)
    print("\nFeatures that surpass Bubblemaps:")
    print("  ✓ Temporal timeline with playback")
    print("  ✓ CEX funding detection")
    print("  ✓ Fresh wallet identification")
    print("  ✓ Similar amount clustering")
    print("  ✓ Multi-hop relationship tracing")
    print("  ✓ Cross-chain connection detection")
    print("  ✓ Statistical anomaly detection (Benford's Law)")
    print("  ✓ Behavioral clustering")
    print("  ✓ Interactive exploration")
    print("  ✓ Money laundering pattern detection")
    print("\nRun run_demo_analysis() to see it in action")
