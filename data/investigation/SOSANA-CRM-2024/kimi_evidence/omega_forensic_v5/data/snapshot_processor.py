"""
Omega Forensic V5 - Snapshot Processor
=======================================
Process wallet snapshots and build comprehensive connection database.
"""

import json
import csv
from typing import List, Dict, Optional
from datetime import datetime

from comprehensive_wallet_db import (
    ComprehensiveWalletDatabase,
    ComprehensiveWalletRecord,
    WalletStatus,
    ConnectionType,
    add_connection,
    get_comprehensive_db
)

class SnapshotProcessor:
    """
    Process wallet snapshot data and build connection database.
    """
    
    def __init__(self):
        self.db = get_comprehensive_db()
        self.processed_count = 0
        self.connection_count = 0
    
    def process_wallet_list(self, wallets_data: List[Dict]) -> None:
        """
        Process a list of wallet data from snapshot.
        
        Expected format:
        {
            "address": "...",
            "balance_sol": 100.0,
            "balance_crm": 1000000.0,
            "created_at": "2025-08-01",
            "transactions": [...]
        }
        """
        for wallet_data in wallets_data:
            self._process_single_wallet(wallet_data)
        
        # After all wallets added, analyze connections
        self._analyze_all_connections()
    
    def _process_single_wallet(self, data: Dict) -> None:
        """Process a single wallet from snapshot."""
        address = data.get("address")
        if not address:
            return
        
        # Create wallet record
        record = ComprehensiveWalletRecord(
            address=address,
            status=WalletStatus.UNKNOWN,
            balance_sol=data.get("balance_sol", 0.0),
            balance_crm=data.get("balance_crm", 0.0),
            balance_usdc=data.get("balance_usdc", 0.0),
            balance_usdt=data.get("balance_usdt", 0.0),
            other_tokens=data.get("other_tokens", {}),
            created_at=data.get("created_at"),
            first_transaction=data.get("first_transaction"),
            last_transaction=data.get("last_transaction"),
            total_transactions=data.get("total_transactions", 0),
            unique_counterparties=data.get("unique_counterparties", 0),
            notes=data.get("notes", "")
        )
        
        # Add to database
        self.db.add_wallet(record)
        self.processed_count += 1
    
    def _analyze_all_connections(self) -> None:
        """Analyze connections for all wallets."""
        for address, wallet in self.db.wallets.items():
            # Skip known scammers
            if wallet.status == WalletStatus.CONFIRMED_SCAMMER:
                continue
            
            # Check for connections to known scammers
            self._find_scammer_connections(wallet)
            
            # Calculate connection score
            wallet.connection_score = self.db.calculate_connection_score(address)
            
            # Update status based on connections
            self._update_wallet_status(wallet)
    
    def _find_scammer_connections(self, wallet: ComprehensiveWalletRecord) -> None:
        """Find connections between wallet and known scammers."""
        # This would be populated from actual transaction analysis
        # For now, we'll use placeholder logic
        
        # Check if wallet received from scammer
        # Check if wallet sent to scammer
        # Check temporal proximity
        # Check common counterparties
        pass
    
    def _update_wallet_status(self, wallet: ComprehensiveWalletRecord) -> None:
        """Update wallet status based on connection analysis."""
        score = wallet.connection_score
        
        if score >= 0.8:
            wallet.status = WalletStatus.SUSPECTED_SCAMMER
            wallet.risk_level = "critical"
            wallet.flags.append("HIGH_SCAMMER_CONNECTION")
        elif score >= 0.5:
            wallet.status = WalletStatus.CONNECTED
            wallet.risk_level = "high"
            wallet.flags.append("CONNECTED_TO_SCAMMERS")
        elif score >= 0.2:
            wallet.status = WalletStatus.ASSOCIATED
            wallet.risk_level = "medium"
            wallet.flags.append("POSSIBLE_ASSOCIATION")
        elif score == 0.0:
            wallet.status = WalletStatus.CLEAN
            wallet.risk_level = "low"
        
        # Count scammer counterparties
        wallet.scammer_counterparties = len(wallet.scammer_connections)
    
    def load_from_csv(self, filepath: str) -> None:
        """Load wallet data from CSV file."""
        wallets_data = []
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                wallet_data = {
                    "address": row.get("address"),
                    "balance_sol": float(row.get("balance_sol", 0) or 0),
                    "balance_crm": float(row.get("balance_crm", 0) or 0),
                    "created_at": row.get("created_at"),
                }
                wallets_data.append(wallet_data)
        
        self.process_wallet_list(wallets_data)
    
    def load_from_json(self, filepath: str) -> None:
        """Load wallet data from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            self.process_wallet_list(data)
        elif isinstance(data, dict) and "wallets" in data:
            self.process_wallet_list(data["wallets"])
        else:
            self.process_wallet_list([data])
    
    def generate_report(self) -> Dict:
        """Generate analysis report."""
        return self.db.generate_connection_report()
    
    def export_results(self, output_dir: str = "./output") -> Dict[str, str]:
        """Export all results."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # Export full database
        json_path = f"{output_dir}/comprehensive_wallet_db.json"
        self.db.export_to_json(json_path)
        files["json"] = json_path
        
        # Export CSV
        csv_path = f"{output_dir}/comprehensive_wallet_db.csv"
        self.db.export_to_csv(csv_path)
        files["csv"] = csv_path
        
        # Export connection report
        report = self.generate_report()
        report_path = f"{output_dir}/connection_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        files["report"] = report_path
        
        # Export high-risk wallets
        high_risk = self.db.find_connected_wallets(min_score=0.3)
        high_risk_path = f"{output_dir}/high_risk_wallets.json"
        with open(high_risk_path, 'w') as f:
            json.dump([w.to_dict() for w in high_risk[:100]], f, indent=2)
        files["high_risk"] = high_risk_path
        
        return files

def create_sample_snapshot() -> List[Dict]:
    """Create sample snapshot data for testing."""
    return [
        {
            "address": "SampleWallet1Address1234567890123456789012345678",
            "balance_sol": 100.5,
            "balance_crm": 5000000.0,
            "created_at": "2025-09-01",
            "notes": "Sample wallet for testing"
        },
        {
            "address": "SampleWallet2Address1234567890123456789012345679",
            "balance_sol": 0.5,
            "balance_crm": 0.0,
            "created_at": "2026-03-26",
            "notes": "Recently created wallet"
        },
        {
            "address": "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",  # Known scammer
            "balance_sol": 45.0,
            "balance_crm": 19700000.0,
            "created_at": "2025-08-25",
            "notes": "SMOKING GUN - Bridge wallet"
        }
    ]

if __name__ == "__main__":
    print("=" * 70)
    print("SNAPSHOT PROCESSOR")
    print("=" * 70)
    
    # Create processor
    processor = SnapshotProcessor()
    
    # Load sample data
    sample_data = create_sample_snapshot()
    processor.process_wallet_list(sample_data)
    
    # Generate report
    report = processor.generate_report()
    
    print(f"\n📊 Processed {processor.processed_count} wallets")
    print(f"📊 Summary:")
    for key, value in report["summary"].items():
        print(f"  {key}: {value}")
    
    # Export
    files = processor.export_results("./test_output")
    print(f"\n📁 Exported to:")
    for name, path in files.items():
        print(f"  {name}: {path}")
    
    print("\n" + "=" * 70)
