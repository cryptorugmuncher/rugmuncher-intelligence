#!/usr/bin/env python3
"""
Omega Forensic V5 - Build Comprehensive Database
=================================================
Master script to build complete wallet database from snapshot.
Usage: python build_comprehensive_db.py --snapshot wallets.csv --transactions txs.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.comprehensive_wallet_db import get_comprehensive_db, WalletStatus
from data.snapshot_processor import SnapshotProcessor
from data.transaction_analyzer import TransactionAnalyzer, load_transactions_from_json, load_transactions_from_csv

def main():
    parser = argparse.ArgumentParser(
        description="Build comprehensive wallet database with scammer connections"
    )
    parser.add_argument(
        "--snapshot",
        help="Path to wallet snapshot file (CSV or JSON)"
    )
    parser.add_argument(
        "--transactions",
        help="Path to transaction data file (CSV or JSON)"
    )
    parser.add_argument(
        "--output",
        default="./output",
        help="Output directory for results"
    )
    parser.add_argument(
        "--min-connection-score",
        type=float,
        default=0.1,
        help="Minimum connection score to flag wallet"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("OMEGA FORENSIC V5 - COMPREHENSIVE DATABASE BUILDER")
    print("=" * 70)
    
    # Initialize
    db = get_comprehensive_db()
    processor = SnapshotProcessor()
    analyzer = TransactionAnalyzer()
    
    # Load wallet snapshot
    if args.snapshot:
        print(f"\n📁 Loading wallet snapshot: {args.snapshot}")
        
        if args.snapshot.endswith('.csv'):
            processor.load_from_csv(args.snapshot)
        elif args.snapshot.endswith('.json'):
            processor.load_from_json(args.snapshot)
        else:
            print("❌ Unknown snapshot format. Use CSV or JSON.")
            return 1
        
        print(f"  ✓ Loaded {processor.processed_count} wallets")
    
    # Load transaction data
    if args.transactions:
        print(f"\n📁 Loading transaction data: {args.transactions}")
        
        if args.transactions.endswith('.csv'):
            txs = load_transactions_from_csv(args.transactions)
        elif args.transactions.endswith('.json'):
            txs = load_transactions_from_json(args.transactions)
        else:
            print("❌ Unknown transaction format. Use CSV or JSON.")
            return 1
        
        analyzer.load_transactions(txs)
        print(f"  ✓ Loaded {len(txs)} transactions")
        
        # Analyze connections
        print("\n🔍 Analyzing connections...")
        for address in db.wallets:
            if address not in db.KNOWN_SCAMMERS:
                connections = analyzer.find_direct_connections(address)
                db.wallets[address].scammer_connections = connections
                db.wallets[address].connection_score = db.calculate_connection_score(address)
        
        print(f"  ✓ Analyzed {len(db.wallets)} wallets")
    
    # Generate reports
    print("\n📊 Generating reports...")
    
    # Connection report
    connection_report = db.generate_connection_report()
    
    # Transaction report (if transactions loaded)
    if args.transactions:
        tx_report = analyzer.generate_transaction_report()
    else:
        tx_report = None
    
    # Find connected wallets
    connected_wallets = db.find_connected_wallets(min_score=args.min_connection_score)
    
    print(f"  ✓ Found {len(connected_wallets)} connected wallets")
    
    # Export results
    print(f"\n💾 Exporting results to: {args.output}")
    
    import os
    os.makedirs(args.output, exist_ok=True)
    
    # Export database
    db.export_to_json(f"{args.output}/comprehensive_wallet_db.json")
    db.export_to_csv(f"{args.output}/comprehensive_wallet_db.csv")
    
    # Export connection report
    with open(f"{args.output}/connection_report.json", 'w') as f:
        json.dump(connection_report, f, indent=2)
    
    # Export transaction report
    if tx_report:
        with open(f"{args.output}/transaction_report.json", 'w') as f:
            json.dump(tx_report, f, indent=2)
    
    # Export connected wallets
    with open(f"{args.output}/connected_wallets.json", 'w') as f:
        json.dump([w.to_dict() for w in connected_wallets], f, indent=2)
    
    # Export high-risk wallets (CSV for easy review)
    high_risk = [w for w in connected_wallets if w.connection_score >= 0.5]
    with open(f"{args.output}/high_risk_wallets.csv", 'w') as f:
        f.write("address,connection_score,status,risk_level,scammer_connections,notes\n")
        for w in high_risk:
            notes = w.notes.replace('"', '""').replace(',', ';')[:100]
            f.write(f"{w.address},{w.connection_score:.2f},{w.status.value},{w.risk_level},{len(w.scammer_connections)},\"{notes}\"\n")
    
    print(f"  ✓ Exported all files")
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"\n📊 Database Statistics:")
    print(f"  Total Wallets: {connection_report['summary']['total_wallets']}")
    print(f"  Confirmed Scammers: {connection_report['summary']['confirmed_scammers']}")
    print(f"  Suspected Scammers: {connection_report['summary']['suspected_scammers']}")
    print(f"  Connected Wallets: {connection_report['summary']['connected_wallets']}")
    print(f"  Clean Wallets: {connection_report['summary']['clean_wallets']}")
    
    print(f"\n🔴 High Risk Wallets (score >= 0.5): {len(high_risk)}")
    for w in high_risk[:10]:
        print(f"  {w.address[:30]}... score={w.connection_score:.2f} status={w.status.value}")
    
    if len(high_risk) > 10:
        print(f"  ... and {len(high_risk) - 10} more")
    
    print(f"\n📁 Output Files:")
    print(f"  {args.output}/comprehensive_wallet_db.json")
    print(f"  {args.output}/comprehensive_wallet_db.csv")
    print(f"  {args.output}/connection_report.json")
    print(f"  {args.output}/connected_wallets.json")
    print(f"  {args.output}/high_risk_wallets.csv")
    
    if tx_report:
        print(f"  {args.output}/transaction_report.json")
    
    print("\n" + "=" * 70)
    print("✅ Database build complete!")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
