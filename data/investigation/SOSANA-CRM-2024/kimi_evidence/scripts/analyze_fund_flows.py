#!/usr/bin/env python3
"""
Fund Flow Analyzer
==================
Analyze exported transaction history to identify:
- CEX deposit destinations
- Cross-chain bridge usage
- Fee collector relationships
- Fund consolidation patterns

Usage:
    python analyze_fund_flows.py --input HLnpSz9h_20250406_120000.json
    python analyze_fund_flows.py --all --input-dir ./exports
"""

import argparse
import json
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Set

# Known CEX hot wallets (populate as identified)
CEX_HOT_WALLETS = {
    "MEXC": {
        "wallets": [],  # Add as identified
        "patterns": ["multiple_small_deposits", "consolidation"]
    },
    "Bybit": {
        "wallets": [],  # Add as identified
        "patterns": ["direct_deposit", "tagged"]
    },
    "Gate.io": {
        "wallets": [],  # Add as identified
        "patterns": ["tagged_transactions"]
    },
    "Binance": {
        "wallets": [],  # Add as identified
        "patterns": ["high_volume", "frequent_consolidation"]
    },
    "Coinbase": {
        "wallets": [],  # Add as identified
        "patterns": ["institutional"]
    }
}

# Bridge contracts
BRIDGE_CONTRACTS = {
    "Wormhole_Token": "wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb",
    "Wormhole_NFT": "WnFt12ZrnzZrFZkt2xsNsaNWoQribnu6Q5hX1RY8VM",
    "Allbridge_Classic": "BrdgN2RPzEMjSngpWPRr6zRvobgsADWXZLg7R9LLMQe",
    "Portal_Bridge": "5B6H7X6E9n8z7Y6T5R4E3W2Q1",  # Update with actual
}

# Known network infrastructure
NETWORK_WALLETS = {
    "fee_collector": "GVC9Zvh3",
    "treasury_suspected": ["ASTyfSima", "H8sMJSCQ"],
    "confirmed_dumps": ["HLnpSz9h", "6LXutJvK", "7uCYuvPb", "HGS4DyyX", "DLHnb1yt"]
}


class FundFlowAnalyzer:
    """Analyze fund flows from exported wallet history."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.wallet_address = data.get("address", "UNKNOWN")
        self.wallet_key = data.get("wallet", "UNKNOWN")
        self.transactions = data.get("transactions", [])
        self.outgoing = data.get("outgoing_transfers", [])
    
    def analyze_cex_deposits(self) -> List[Dict]:
        """Identify potential CEX deposits."""
        cex_deposits = []
        
        for transfer in self.outgoing:
            recipient = transfer.get("to", "")
            
            # Check against known CEX wallets
            for cex_name, cex_info in CEX_HOT_WALLETS.items():
                if recipient in cex_info["wallets"]:
                    transfer["cex_name"] = cex_name
                    transfer["confidence"] = "HIGH"
                    cex_deposits.append(transfer)
                    break
            else:
                # Heuristic: Check for CEX-like patterns
                # - Round number deposits
                # - Multiple deposits to same recipient
                # - Recipient with high transaction volume
                amount = transfer.get("amount", 0)
                if self._is_round_number(amount) and transfer["token"] == "SOL":
                    transfer["cex_name"] = "SUSPECTED_CEX"
                    transfer["confidence"] = "MEDIUM"
                    transfer["reason"] = "Round number SOL transfer"
                    cex_deposits.append(transfer)
        
        return cex_deposits
    
    def analyze_bridge_usage(self) -> List[Dict]:
        """Identify cross-chain bridge transactions."""
        bridge_txs = []
        
        for transfer in self.outgoing:
            recipient = transfer.get("to", "")
            
            # Check against known bridge contracts
            for bridge_name, contract in BRIDGE_CONTRACTS.items():
                if contract in recipient:
                    transfer["bridge_name"] = bridge_name
                    transfer["bridge_contract"] = contract
                    bridge_txs.append(transfer)
                    break
            
            # Check transaction type for bridge patterns
            if transfer.get("type") == "SWAP":
                details = transfer.get("details", {})
                # Look for wrapped tokens (indicating bridge)
                token_outputs = details.get("tokenOutputs", [])
                for output in token_outputs:
                    mint = output.get("mint", "")
                    if "wormhole" in mint.lower() or "portal" in mint.lower():
                        transfer["bridge_name"] = "SUSPECTED_WORMHOLE"
                        bridge_txs.append(transfer)
                        break
        
        return bridge_txs
    
    def analyze_fee_collector_flows(self) -> List[Dict]:
        """Analyze flows to the known fee collector."""
        fee_flows = []
        fee_collector = NETWORK_WALLETS["fee_collector"]
        
        for transfer in self.outgoing:
            recipient = transfer.get("to", "")
            if fee_collector in recipient:
                transfer["fee_collector"] = True
                fee_flows.append(transfer)
        
        return fee_flows
    
    def analyze_recipient_clusters(self) -> Dict[str, List[Dict]]:
        """Group transfers by recipient to identify patterns."""
        clusters = defaultdict(list)
        
        for transfer in self.outgoing:
            recipient = transfer.get("to", "")
            clusters[recipient].append(transfer)
        
        # Sort by frequency
        sorted_clusters = dict(sorted(
            clusters.items(),
            key=lambda x: len(x[1]),
            reverse=True
        ))
        
        return sorted_clusters
    
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze timing patterns of transfers."""
        if not self.outgoing:
            return {}
        
        timestamps = [t.get("timestamp", 0) for t in self.outgoing if t.get("timestamp")]
        if not timestamps:
            return {}
        
        timestamps.sort()
        
        # Calculate time windows
        first_tx = datetime.fromtimestamp(timestamps[0])
        last_tx = datetime.fromtimestamp(timestamps[-1])
        duration = last_tx - first_tx
        
        # Look for burst patterns (many transactions in short window)
        bursts = []
        window_start = timestamps[0]
        window_count = 1
        
        for i in range(1, len(timestamps)):
            if timestamps[i] - window_start < 3600:  # 1 hour window
                window_count += 1
            else:
                if window_count >= 5:  # 5+ transactions in 1 hour = burst
                    bursts.append({
                        "start": datetime.fromtimestamp(window_start).isoformat(),
                        "count": window_count,
                        "duration_minutes": (timestamps[i-1] - window_start) / 60
                    })
                window_start = timestamps[i]
                window_count = 1
        
        return {
            "first_transaction": first_tx.isoformat(),
            "last_transaction": last_tx.isoformat(),
            "total_duration_hours": duration.total_seconds() / 3600,
            "transaction_count": len(timestamps),
            "average_interval_minutes": (duration.total_seconds() / 60) / len(timestamps) if len(timestamps) > 1 else 0,
            "bursts": bursts
        }
    
    def identify_network_connections(self) -> List[Dict]:
        """Identify connections to other known network wallets."""
        connections = []
        
        for transfer in self.outgoing:
            recipient = transfer.get("to", "")
            
            # Check fee collector
            if NETWORK_WALLETS["fee_collector"] in recipient:
                transfer["connection_type"] = "FEE_COLLECTOR"
                connections.append(transfer)
                continue
            
            # Check suspected treasuries
            for treasury in NETWORK_WALLETS["treasury_suspected"]:
                if treasury in recipient:
                    transfer["connection_type"] = "SUSPECTED_TREASURY"
                    connections.append(transfer)
                    break
            
            # Check other dump wallets
            for dump_wallet in NETWORK_WALLETS["confirmed_dumps"]:
                if dump_wallet in recipient and dump_wallet not in self.wallet_address:
                    transfer["connection_type"] = "OTHER_DUMP_WALLET"
                    connections.append(transfer)
                    break
        
        return connections
    
    def calculate_financial_summary(self) -> Dict[str, Any]:
        """Calculate financial summary of outgoing transfers."""
        summary = {
            "total_sol_transferred": 0,
            "total_crm_transferred": 0,
            "total_other_tokens": 0,
            "largest_single_transfer": 0,
            "largest_transfer_token": "",
            "largest_transfer_date": "",
            "recipient_count": len(set(t.get("to", "") for t in self.outgoing)),
            "transaction_count": len(self.outgoing)
        }
        
        for transfer in self.outgoing:
            amount = transfer.get("amount", 0)
            token = transfer.get("token", "")
            
            if token == "SOL":
                summary["total_sol_transferred"] += amount
            elif token == "CRM":
                summary["total_crm_transferred"] += amount
            else:
                summary["total_other_tokens"] += 1
            
            if amount > summary["largest_single_transfer"]:
                summary["largest_single_transfer"] = amount
                summary["largest_transfer_token"] = token
                summary["largest_transfer_date"] = transfer.get("date", "")
        
        return summary
    
    def _is_round_number(self, amount: float) -> bool:
        """Check if amount is a round number (potential CEX deposit)."""
        if amount <= 0:
            return False
        
        # Check if it's close to a round number
        rounded = round(amount, 1)
        return abs(amount - rounded) < 0.01
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive fund flow analysis report."""
        print(f"\nAnalyzing fund flows for {self.wallet_key}...")
        
        cex_deposits = self.analyze_cex_deposits()
        print(f"  Found {len(cex_deposits)} potential CEX deposits")
        
        bridge_txs = self.analyze_bridge_usage()
        print(f"  Found {len(bridge_txs)} bridge transactions")
        
        fee_flows = self.analyze_fee_collector_flows()
        print(f"  Found {len(fee_flows)} fee collector flows")
        
        clusters = self.analyze_recipient_clusters()
        print(f"  Found {len(clusters)} unique recipients")
        
        temporal = self.analyze_temporal_patterns()
        print(f"  Temporal analysis complete")
        
        connections = self.identify_network_connections()
        print(f"  Found {len(connections)} network connections")
        
        financial = self.calculate_financial_summary()
        print(f"  Financial summary calculated")
        
        report = {
            "wallet": self.wallet_key,
            "address": self.wallet_address,
            "analysis_timestamp": datetime.now().isoformat(),
            "fund_flow_analysis": {
                "cex_deposits": {
                    "count": len(cex_deposits),
                    "deposits": cex_deposits,
                    "total_sol": sum(d.get("amount", 0) for d in cex_deposits if d.get("token") == "SOL")
                },
                "bridge_transactions": {
                    "count": len(bridge_txs),
                    "transactions": bridge_txs
                },
                "fee_collector_flows": {
                    "count": len(fee_flows),
                    "flows": fee_flows,
                    "total_sol_to_collector": sum(f.get("amount", 0) for f in fee_flows if f.get("token") == "SOL")
                },
                "recipient_clusters": {
                    recipient: {
                        "transfer_count": len(transfers),
                        "total_amount": sum(t.get("amount", 0) for t in transfers),
                        "tokens": list(set(t.get("token", "") for t in transfers))
                    }
                    for recipient, transfers in list(clusters.items())[:10]  # Top 10
                },
                "temporal_patterns": temporal,
                "network_connections": {
                    "count": len(connections),
                    "connections": connections
                },
                "financial_summary": financial
            },
            "evidence_assessment": self._assess_evidence_quality(cex_deposits, bridge_txs, fee_flows)
        }
        
        return report
    
    def _assess_evidence_quality(self, cex_deposits: List[Dict], bridge_txs: List[Dict], fee_flows: List[Dict]) -> Dict[str, str]:
        """Assess evidence quality for law enforcement."""
        assessment = {
            "overall_tier": "TIER_3",
            "cex_confidence": "LOW",
            "bridge_confidence": "LOW",
            "fee_collector_confidence": "HIGH",
            "recommendations": []
        }
        
        # CEX confidence
        high_confidence_cex = [d for d in cex_deposits if d.get("confidence") == "HIGH"]
        if high_confidence_cex:
            assessment["cex_confidence"] = "HIGH"
            assessment["recommendations"].append("Immediate subpoena to identified CEX")
        elif cex_deposits:
            assessment["cex_confidence"] = "MEDIUM"
            assessment["recommendations"].append("Further analysis needed to confirm CEX deposits")
        
        # Bridge confidence
        if bridge_txs:
            assessment["bridge_confidence"] = "HIGH"
            assessment["recommendations"].append("Subpoena bridge protocol for destination chain details")
        
        # Fee collector confidence
        if fee_flows:
            assessment["fee_collector_confidence"] = "HIGH"
            assessment["recommendations"].append("Monitor fee collector for outgoing transactions")
        
        # Overall tier
        if assessment["cex_confidence"] == "HIGH" or assessment["bridge_confidence"] == "HIGH":
            assessment["overall_tier"] = "TIER_2"
        if assessment["cex_confidence"] == "HIGH" and len(high_confidence_cex) >= 3:
            assessment["overall_tier"] = "TIER_1"
        
        return assessment


def main():
    parser = argparse.ArgumentParser(
        description="Analyze fund flows from exported wallet history"
    )
    parser.add_argument(
        "--input",
        help="Input JSON file from export_deleted_wallet_history.py"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all JSON files in input directory"
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Directory containing exported wallet JSON files"
    )
    parser.add_argument(
        "--output",
        help="Output file for analysis report"
    )
    parser.add_argument(
        "--format",
        choices=["json", "txt"],
        default="json",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    if not args.input and not args.all:
        parser.print_help()
        print("\nError: Must specify --input or --all")
        sys.exit(1)
    
    reports = []
    
    if args.all:
        import os
        import glob
        
        pattern = f"{args.input_dir}/*_20*.json"  # Matches wallet_YYYYMMDD_HHMMSS.json
        files = glob.glob(pattern)
        
        # Exclude combined reports
        files = [f for f in files if "ALL_DELETED_WALLETS" not in f]
        
        print(f"Found {len(files)} wallet export files")
        
        for filepath in files:
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                
                analyzer = FundFlowAnalyzer(data)
                report = analyzer.generate_report()
                reports.append(report)
                
            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")
    else:
        with open(args.input, "r") as f:
            data = json.load(f)
        
        analyzer = FundFlowAnalyzer(data)
        report = analyzer.generate_report()
        reports.append(report)
    
    # Generate combined report
    combined_report = {
        "analysis_timestamp": datetime.now().isoformat(),
        "wallets_analyzed": len(reports),
        "individual_reports": reports,
        "cross_wallet_analysis": {
            "total_sol_transferred": sum(
                r["fund_flow_analysis"]["financial_summary"]["total_sol_transferred"]
                for r in reports
            ),
            "total_crm_transferred": sum(
                r["fund_flow_analysis"]["financial_summary"]["total_crm_transferred"]
                for r in reports
            ),
            "total_cex_deposits": sum(
                r["fund_flow_analysis"]["cex_deposits"]["count"]
                for r in reports
            ),
            "total_bridge_transactions": sum(
                r["fund_flow_analysis"]["bridge_transactions"]["count"]
                for r in reports
            ),
            "total_fee_collector_flows": sum(
                r["fund_flow_analysis"]["fee_collector_flows"]["count"]
                for r in reports
            )
        }
    }
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        output_file = args.output
    else:
        output_file = f"FUND_FLOW_ANALYSIS_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(combined_report, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"Analysis complete! Report saved to: {output_file}")
    print(f"{'='*60}")
    print(f"\nCross-Wallet Summary:")
    print(f"  Total SOL Transferred: {combined_report['cross_wallet_analysis']['total_sol_transferred']:.4f}")
    print(f"  Total CRM Transferred: {combined_report['cross_wallet_analysis']['total_crm_transferred']:,.2f}")
    print(f"  CEX Deposits Found: {combined_report['cross_wallet_analysis']['total_cex_deposits']}")
    print(f"  Bridge Transactions: {combined_report['cross_wallet_analysis']['total_bridge_transactions']}")
    print(f"  Fee Collector Flows: {combined_report['cross_wallet_analysis']['total_fee_collector_flows']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
