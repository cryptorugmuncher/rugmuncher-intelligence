"""
Omega Forensic V5 - Transaction Analyzer
=========================================
Analyze transactions to find wallet connections.
"""

import json
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

from comprehensive_wallet_db import (
    ComprehensiveWalletDatabase,
    ComprehensiveWalletRecord,
    WalletConnection,
    ConnectionType,
    add_connection,
    get_comprehensive_db
)

class TransactionAnalyzer:
    """
    Analyze transaction data to find wallet connections.
    """
    
    def __init__(self):
        self.db = get_comprehensive_db()
        self.transactions: List[Dict] = []
        self.wallet_counterparties: Dict[str, Set[str]] = defaultdict(set)
        self.wallet_transactions: Dict[str, List[Dict]] = defaultdict(list)
    
    def load_transactions(self, transactions: List[Dict]) -> None:
        """
        Load transaction data.
        
        Expected format:
        {
            "signature": "...",
            "timestamp": "2026-03-28T09:19:00Z",
            "from": "wallet_address",
            "to": "wallet_address",
            "amount": 100000.0,
            "token": "CRM",
            "type": "transfer"
        }
        """
        self.transactions = transactions
        
        # Index by wallet
        for tx in transactions:
            from_addr = tx.get("from")
            to_addr = tx.get("to")
            
            if from_addr:
                self.wallet_counterparties[from_addr].add(to_addr)
                self.wallet_transactions[from_addr].append(tx)
            
            if to_addr:
                self.wallet_counterparties[to_addr].add(from_addr)
                self.wallet_transactions[to_addr].append(tx)
    
    def find_direct_connections(self, target_address: str) -> List[WalletConnection]:
        """Find all direct transaction connections for a wallet."""
        connections = []
        
        txs = self.wallet_transactions.get(target_address, [])
        
        # Group by counterparty
        counterparty_txs = defaultdict(list)
        for tx in txs:
            counterparty = tx.get("to") if tx.get("from") == target_address else tx.get("from")
            if counterparty:
                counterparty_txs[counterparty].append(tx)
        
        # Create connections
        for counterparty, c_txs in counterparty_txs.items():
            # Determine connection type
            conn_type = self._classify_connection(target_address, counterparty, c_txs)
            
            # Calculate strength
            strength = min(len(c_txs) * 0.1, 1.0)
            
            # Get evidence
            evidence = [tx.get("signature") for tx in c_txs if tx.get("signature")]
            
            # Calculate total value
            total_value = sum(tx.get("amount", 0) for tx in c_txs)
            
            conn = WalletConnection(
                target_address=counterparty,
                connection_type=conn_type,
                strength=strength,
                evidence=evidence[:5],  # Top 5 signatures
                first_seen=min(tx.get("timestamp") for tx in c_txs if tx.get("timestamp")),
                last_seen=max(tx.get("timestamp") for tx in c_txs if tx.get("timestamp")),
                transaction_count=len(c_txs),
                total_value_transferred=total_value
            )
            
            connections.append(conn)
        
        # Sort by strength
        connections.sort(key=lambda c: c.strength, reverse=True)
        return connections
    
    def _classify_connection(
        self,
        wallet_a: str,
        wallet_b: str,
        transactions: List[Dict]
    ) -> ConnectionType:
        """Classify the type of connection between two wallets."""
        # Check if wallet_b is a known scammer
        if wallet_b in self.db.KNOWN_SCAMMERS:
            # Check direction
            received = any(tx.get("to") == wallet_a for tx in transactions)
            sent = any(tx.get("from") == wallet_a for tx in transactions)
            
            if received:
                return ConnectionType.RECEIVED_FROM
            elif sent:
                return ConnectionType.SENT_TO
        
        # Check temporal patterns
        timestamps = [tx.get("timestamp") for tx in transactions if tx.get("timestamp")]
        if len(timestamps) >= 3:
            # Check for coordinated timing
            return ConnectionType.TEMPORAL_PROXIMITY
        
        return ConnectionType.DIRECT_TRANSACTION
    
    def find_common_counterparties(
        self,
        wallet_a: str,
        wallet_b: str
    ) -> List[str]:
        """Find common counterparties between two wallets."""
        counterparties_a = self.wallet_counterparties.get(wallet_a, set())
        counterparties_b = self.wallet_counterparties.get(wallet_b, set())
        
        return list(counterparties_a.intersection(counterparties_b))
    
    def analyze_wallet_network(
        self,
        center_wallet: str,
        depth: int = 2
    ) -> Dict:
        """
        Analyze network around a center wallet.
        Returns graph data for visualization.
        """
        graph = {
            "center": center_wallet,
            "nodes": [],
            "edges": [],
            "stats": {
                "total_wallets": 0,
                "scammer_connections": 0,
                "total_value": 0.0
            }
        }
        
        visited = {center_wallet}
        current_level = {center_wallet}
        
        for level in range(depth + 1):
            next_level = set()
            
            for wallet in current_level:
                # Add node
                is_scammer = wallet in self.db.KNOWN_SCAMMERS
                graph["nodes"].append({
                    "address": wallet,
                    "level": level,
                    "is_scammer": is_scammer,
                    "tier": self.db.KNOWN_SCAMMERS.get(wallet)
                })
                
                # Find connections
                counterparties = self.wallet_counterparties.get(wallet, set())
                
                for counterparty in counterparties:
                    # Add edge
                    txs = [
                        tx for tx in self.wallet_transactions.get(wallet, [])
                        if tx.get("to") == counterparty or tx.get("from") == counterparty
                    ]
                    
                    total_value = sum(tx.get("amount", 0) for tx in txs)
                    
                    graph["edges"].append({
                        "source": wallet,
                        "target": counterparty,
                        "value": total_value,
                        "transactions": len(txs)
                    })
                    
                    graph["stats"]["total_value"] += total_value
                    
                    if counterparty not in visited:
                        visited.add(counterparty)
                        next_level.add(counterparty)
                        
                        if counterparty in self.db.KNOWN_SCAMMERS:
                            graph["stats"]["scammer_connections"] += 1
            
            current_level = next_level
            if not current_level:
                break
        
        graph["stats"]["total_wallets"] = len(visited)
        return graph
    
    def find_suspicious_patterns(self) -> List[Dict]:
        """Find suspicious transaction patterns."""
        patterns = []
        
        # Pattern 1: Rapid-fire transactions (bot-like)
        for wallet, txs in self.wallet_transactions.items():
            if len(txs) >= 10:
                # Check timing
                timestamps = sorted([tx.get("timestamp") for tx in txs if tx.get("timestamp")])
                if len(timestamps) >= 10:
                    # Calculate time span
                    time_diffs = []
                    for i in range(1, len(timestamps)):
                        # Parse timestamps
                        try:
                            t1 = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                            t2 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                            diff = (t2 - t1).total_seconds()
                            time_diffs.append(diff)
                        except:
                            pass
                    
                    if time_diffs:
                        avg_diff = sum(time_diffs) / len(time_diffs)
                        if avg_diff < 60:  # Less than 1 minute average
                            patterns.append({
                                "pattern": "rapid_fire",
                                "wallet": wallet,
                                "transaction_count": len(txs),
                                "avg_time_between": avg_diff,
                                "severity": "high"
                            })
        
        # Pattern 2: Round-number transfers (coordinated)
        round_numbers = [100000, 500000, 1000000, 5000000, 10000000]
        round_number_txs = []
        
        for tx in self.transactions:
            amount = tx.get("amount", 0)
            if amount in round_numbers:
                round_number_txs.append(tx)
        
        if len(round_number_txs) >= 5:
            patterns.append({
                "pattern": "round_number_coordination",
                "transaction_count": len(round_number_txs),
                "severity": "medium"
            })
        
        # Pattern 3: Dusting (witness intimidation)
        dust_txs = [tx for tx in self.transactions if tx.get("amount", 0) < 0.001]
        if len(dust_txs) >= 10:
            patterns.append({
                "pattern": "dusting",
                "transaction_count": len(dust_txs),
                "severity": "high",
                "note": "Possible witness intimidation"
            })
        
        return patterns
    
    def generate_transaction_report(self) -> Dict:
        """Generate comprehensive transaction analysis report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_transactions": len(self.transactions),
                "unique_wallets": len(self.wallet_counterparties),
                "scammer_wallets_in_data": sum(
                    1 for w in self.wallet_counterparties
                    if w in self.db.KNOWN_SCAMMERS
                )
            },
            "suspicious_patterns": self.find_suspicious_patterns(),
            "high_volume_wallets": [],
            "scammer_connections": []
        }
        
        # Find high volume wallets
        wallet_volumes = {}
        for tx in self.transactions:
            for wallet in [tx.get("from"), tx.get("to")]:
                if wallet:
                    wallet_volumes[wallet] = wallet_volumes.get(wallet, 0) + tx.get("amount", 0)
        
        sorted_volumes = sorted(wallet_volumes.items(), key=lambda x: x[1], reverse=True)
        report["high_volume_wallets"] = [
            {"address": w, "total_volume": v}
            for w, v in sorted_volumes[:20]
        ]
        
        # Find scammer connections
        for wallet in self.wallet_counterparties:
            if wallet not in self.db.KNOWN_SCAMMERS:
                counterparties = self.wallet_counterparties.get(wallet, set())
                scammer_counterparties = [
                    c for c in counterparties if c in self.db.KNOWN_SCAMMERS
                ]
                
                if scammer_counterparties:
                    report["scammer_connections"].append({
                        "wallet": wallet,
                        "scammer_counterparties": scammer_counterparties,
                        "connection_count": len(scammer_counterparties)
                    })
        
        # Sort by connection count
        report["scammer_connections"].sort(
            key=lambda x: x["connection_count"],
            reverse=True
        )
        
        return report

# === UTILITY FUNCTIONS ===

def load_transactions_from_json(filepath: str) -> List[Dict]:
    """Load transactions from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "transactions" in data:
        return data["transactions"]
    else:
        return [data]

def load_transactions_from_csv(filepath: str) -> List[Dict]:
    """Load transactions from CSV file."""
    import csv
    
    transactions = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tx = {
                "signature": row.get("signature"),
                "timestamp": row.get("timestamp"),
                "from": row.get("from"),
                "to": row.get("to"),
                "amount": float(row.get("amount", 0) or 0),
                "token": row.get("token", "SOL"),
                "type": row.get("type", "transfer")
            }
            transactions.append(tx)
    
    return transactions

if __name__ == "__main__":
    print("=" * 70)
    print("TRANSACTION ANALYZER")
    print("=" * 70)
    
    # Create analyzer
    analyzer = TransactionAnalyzer()
    
    # Sample transactions
    sample_txs = [
        {
            "signature": "sig1",
            "timestamp": "2026-03-28T09:19:00Z",
            "from": "WalletA",
            "to": "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",
            "amount": 1000000.0,
            "token": "CRM"
        },
        {
            "signature": "sig2",
            "timestamp": "2026-03-28T09:20:00Z",
            "from": "WalletA",
            "to": "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",
            "amount": 500000.0,
            "token": "CRM"
        },
        {
            "signature": "sig3",
            "timestamp": "2026-03-28T09:21:00Z",
            "from": "WalletB",
            "to": "HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc",
            "amount": 100000.0,
            "token": "CRM"
        }
    ]
    
    analyzer.load_transactions(sample_txs)
    
    # Generate report
    report = analyzer.generate_transaction_report()
    
    print(f"\n📊 Transaction Analysis:")
    print(f"  Total Transactions: {report['summary']['total_transactions']}")
    print(f"  Unique Wallets: {report['summary']['unique_wallets']}")
    print(f"  Scammer Wallets: {report['summary']['scammer_wallets_in_data']}")
    
    print(f"\n🔍 Suspicious Patterns: {len(report['suspicious_patterns'])}")
    for pattern in report['suspicious_patterns']:
        print(f"  - {pattern['pattern']}: {pattern.get('wallet', 'N/A')} ({pattern['severity']})")
    
    print("\n" + "=" * 70)
