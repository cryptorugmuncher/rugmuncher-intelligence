#!/usr/bin/env python3
"""
🔍 CROSS-PROJECT WALLET NETWORK MAPPER
========================================
Maps CRM network connections across multiple transaction CSV exports
to find evidence of participation in other scams.

Since primary network wallets are wiped, this analyzes:
1. Victim wallets (received CRM from network)
2. Intermediary wallets (routed funds)
3. Exchange deposit addresses (where they cashed out)
4. Reused wallet patterns (same wallet appearing across multiple exports)

Author: Marcus Aurelius
Date: April 13, 2026
Case: CRM-SCAM-2025-001 (RICO-eligible)
"""

import csv
import json
import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from datetime import datetime

# Network wallets we're investigating
NETWORK_WALLETS = {
    "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6": "TIER_1_AUTOMATION",
    "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC": "TIER_1_FEEDER",
    "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj": "TIER_4_DISTRIBUTION",
    "Cx5qTEtnp3arFVBuusMXHafoRzLCLuigtz2AiQAFmq2Q": "TIER_2_BRIDGE",
    "CaTWE2NPewVt1WLrQZeQGvUiMYexyV3YBaWhEDQ33kDh": "TIER_2_RELAY",
    "ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn": "TIER_1_MASTER",
    "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS": "CRM_TOKEN",  # For token transfers
}


def load_csv_transactions(csv_path: str) -> List[Dict]:
    """Load transactions from a CSV file"""
    transactions = []
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                transactions.append(row)
    except Exception as e:
        print(f"⚠️  Error loading {csv_path}: {e}")
    return transactions


def extract_counterparties(transactions: List[Dict], source_wallet: str) -> Dict[str, Dict]:
    """
    Extract all counterparties from transaction list
    Returns: Dict[counterparty_address, metadata]
    """
    counterparties = defaultdict(lambda: {
        'interaction_count': 0,
        'total_crm_volume': 0.0,
        'first_interaction': None,
        'last_interaction': None,
        'interaction_types': set(),
        'transactions': []
    })
    
    for tx in transactions:
        from_addr = tx.get('From', tx.get('from', '')).strip()
        to_addr = tx.get('To', tx.get('to', '')).strip()
        
        # Skip if we can't identify both addresses
        if not from_addr or not to_addr:
            continue
        
        # Determine amount
        try:
            amount = float(tx.get('Amount', tx.get('amount', 0)))
        except:
            amount = 0.0
        
        # Timestamp
        timestamp = tx.get('Human Time', tx.get('timestamp', ''))
        
        # Track counterparties
        counterparty = None
        if from_addr == source_wallet:
            # Network wallet sent TO this counterparty
            counterparty = to_addr
            counterparties[counterparty]['interaction_count'] += 1
            counterparties[counterparty]['total_crm_volume'] += amount
            counterparties[counterparty]['interaction_types'].add('received_from_network')
            counterparties[counterparty]['transactions'].append({
                'type': 'outgoing',
                'timestamp': timestamp,
                'amount': amount,
                'other_party': from_addr
            })
        
        elif to_addr == source_wallet:
            # Network wallet received FROM this counterparty
            counterparty = from_addr
            counterparties[counterparty]['interaction_count'] += 1
            counterparties[counterparty]['total_crm_volume'] += amount
            counterparties[counterparty]['interaction_types'].add('sent_to_network')
            counterparties[counterparty]['transactions'].append({
                'type': 'incoming',
                'timestamp': timestamp,
                'amount': amount,
                'other_party': to_addr
            })
        
        # Update timestamps only if we identified a counterparty
        if counterparty and timestamp:
            if not counterparties[counterparty]['first_interaction']:
                counterparties[counterparty]['first_interaction'] = timestamp
            counterparties[counterparty]['last_interaction'] = timestamp
    
    return dict(counterparties)


def find_common_counterparties(all_counterparties: Dict[str, Dict[str, Dict]]) -> Dict[str, Dict]:
    """
    Find wallets that appear as counterparties to MULTIPLE network wallets
    These are high-value connections for cross-project analysis
    """
    # Build reverse index: counterparty -> [network wallets that interacted]
    counterparty_to_network = defaultdict(list)
    
    for network_wallet, counterparties in all_counterparties.items():
        for counterparty, metadata in counterparties.items():
            counterparty_to_network[counterparty].append({
                'network_wallet': network_wallet,
                'metadata': metadata
            })
    
    # Find counterparty wallets connected to 2+ network wallets
    common_counterparties = {}
    
    for counterparty, connections in counterparty_to_network.items():
        if len(connections) >= 2:
            # This wallet interacted with multiple network nodes
            common_counterparties[counterparty] = {
                'network_connections': len(connections),
                'connected_network_wallets': [c['network_wallet'] for c in connections],
                'total_interactions': sum(c['metadata']['interaction_count'] for c in connections),
                'total_volume': sum(c['metadata']['total_crm_volume'] for c in connections),
                'interaction_types': list(set(
                    itype for c in connections for itype in c['metadata']['interaction_types']
                ))
            }
    
    return common_counterparties


def identify_exchange_deposits(all_counterparties: Dict[str, Dict[str, Dict]]) -> List[Dict]:
    """
    Identify potential exchange deposit addresses
    These are where the network cashed out
    """
    exchange_candidates = []
    
    # Collect all counterparties
    all_cp_metadata = {}
    for network_wallet, counterparties in all_counterparties.items():
        for cp, metadata in counterparties.items():
            if cp not in all_cp_metadata:
                all_cp_metadata[cp] = metadata
            else:
                # Merge
                all_cp_metadata[cp]['interaction_count'] += metadata['interaction_count']
                all_cp_metadata[cp]['total_crm_volume'] += metadata['total_crm_volume']
    
    # Look for patterns suggesting exchange deposits:
    # 1. Received large amounts from network
    # 2. Low interaction count (deposit-only behavior)
    # 3. Large volume relative to interaction count
    
    for counterparty, metadata in all_cp_metadata.items():
        if 'received_from_network' in metadata['interaction_types']:
            # Received from network (network sent to this address)
            
            # Criteria for exchange-like behavior
            is_large_deposit = metadata['total_crm_volume'] > 100000000  # 100M+ tokens
            is_few_interactions = metadata['interaction_count'] <= 3
            is_high_volume_per_tx = metadata['total_crm_volume'] / max(metadata['interaction_count'], 1) > 50000000
            
            if is_large_deposit or (is_few_interactions and is_high_volume_per_tx):
                exchange_candidates.append({
                    'address': counterparty,
                    'suspicion': 'exchange_deposit' if is_large_deposit else 'possible_exchange',
                    'total_volume': metadata['total_crm_volume'],
                    'interaction_count': metadata['interaction_count'],
                    'evidence': 'Large deposit pattern' if is_large_deposit else 'Deposit-like behavior'
                })
    
    return sorted(exchange_candidates, key=lambda x: x['total_volume'], reverse=True)


def identify_victim_wallets(all_counterparties: Dict[str, Dict[str, Dict]]) -> List[Dict]:
    """
    Identify victim wallets (received CRM from network, likely retail buyers)
    """
    victims = []
    
    for network_wallet, counterparties in all_counterparties.items():
        for counterparty, metadata in counterparties.items():
            # Victims received from network
            if 'received_from_network' in metadata['interaction_types']:
                # Small amounts = likely retail victims
                if metadata['total_crm_volume'] < 10000000:  # < 10M CRM
                    victims.append({
                        'address': counterparty,
                        'received_from': network_wallet,
                        'amount': metadata['total_crm_volume'],
                        'interactions': metadata['interaction_count'],
                        'first_contact': metadata['first_interaction'],
                        'last_contact': metadata['last_interaction']
                    })
    
    return sorted(victims, key=lambda x: x['amount'], reverse=True)


def analyze_csv_files(csv_dir: str) -> Dict:
    """
    Main analysis function - processes all CSV files
    """
    print("\n" + "="*70)
    print("🔍 CROSS-PROJECT WALLET NETWORK MAPPER")
    print("="*70)
    print(f"Analysis Date: {datetime.now().isoformat()}")
    print(f"CSV Directory: {csv_dir}")
    print("="*70 + "\n")
    
    # Find all CSV files
    csv_files = []
    for f in os.listdir(csv_dir):
        if f.endswith('.csv'):
            # Extract wallet from filename
            for wallet in NETWORK_WALLETS.keys():
                if wallet[:8] in f or wallet[:20] in f:
                    csv_files.append((f, wallet))
                    break
    
    print(f"📂 Found {len(csv_files)} CSV files for network wallets\n")
    
    # Process each CSV
    all_counterparties = {}
    
    for filename, wallet in csv_files:
        filepath = os.path.join(csv_dir, filename)
        print(f"🔍 Processing: {filename[:50]}...")
        print(f"   Wallet: {wallet[:30]}... ({NETWORK_WALLETS.get(wallet, 'Unknown')})")
        
        # Load transactions
        transactions = load_csv_transactions(filepath)
        print(f"   Transactions: {len(transactions)}")
        
        # Extract counterparties
        counterparties = extract_counterparties(transactions, wallet)
        print(f"   Counterparties: {len(counterparties)}")
        
        all_counterparties[wallet] = counterparties
        
        # Show top counterparties by volume
        sorted_cp = sorted(
            counterparties.items(),
            key=lambda x: x[1]['total_crm_volume'],
            reverse=True
        )[:3]
        
        for cp, meta in sorted_cp:
            print(f"      └─ {cp[:20]}...: {meta['total_crm_volume']:,.0f} CRM ({meta['interaction_count']} tx)")
        
        print()
    
    # Cross-analysis
    print("="*70)
    print("🔗 CROSS-PROJECT NETWORK ANALYSIS")
    print("="*70 + "\n")
    
    # Find common counterparties (connected to multiple network wallets)
    common_counterparties = find_common_counterparties(all_counterparties)
    print(f"🎯 COMMON COUNTERPARTIES (2+ network connections): {len(common_counterparties)}")
    
    for cp, data in sorted(common_counterparties.items(), 
                           key=lambda x: x[1]['network_connections'], 
                           reverse=True)[:10]:
        print(f"\n   {cp[:40]}...")
        print(f"   └─ Connected to: {data['network_connections']} network wallets")
        print(f"      Wallets: {[w[:15]+'...' for w in data['connected_network_wallets']]}")
        print(f"      Total Volume: {data['total_volume']:,.0f} CRM")
        print(f"      Interactions: {data['total_interactions']}")
    
    # Identify exchange deposits
    exchange_candidates = identify_exchange_deposits(all_counterparties)
    print(f"\n\n💰 EXCHANGE DEPOSIT CANDIDATES: {len(exchange_candidates)}")
    
    for ex in exchange_candidates[:10]:
        print(f"\n   {ex['address'][:40]}...")
        print(f"   └─ Suspicion: {ex['suspicion']}")
        print(f"      Volume: {ex['total_volume']:,.0f} CRM")
        print(f"      Evidence: {ex['evidence']}")
    
    # Identify victim wallets
    victims = identify_victim_wallets(all_counterparties)
    print(f"\n\n😢 VICTIM WALLETS IDENTIFIED: {len(victims)}")
    print(f"   (Top 5 by amount received)")
    
    for v in victims[:5]:
        print(f"\n   {v['address'][:40]}...")
        print(f"   └─ Amount: {v['amount']:,.0f} CRM")
        print(f"      From: {v['received_from'][:20]}...")
        print(f"      First Contact: {v['first_contact']}")
    
    # Compile report
    report = {
        "investigation_id": "CROSS-PROJECT-NETWORK-MAP-001",
        "timestamp": datetime.now().isoformat(),
        "csv_files_analyzed": len(csv_files),
        "network_wallets": list(NETWORK_WALLETS.keys()),
        "total_counterparties_found": sum(len(cp) for cp in all_counterparties.values()),
        
        "cross_project_indicators": {
            "common_counterparties_count": len(common_counterparties),
            "common_counterparties_detail": common_counterparties,
            "interpretation": "Wallets connected to multiple network nodes suggest intermediary or victim reuse across projects"
        },
        
        "exchange_deposits": {
            "candidates_count": len(exchange_candidates),
            "top_candidates": exchange_candidates[:20],
            "interpretation": "Where the network cashed out - check these on Arkham for entity labeling"
        },
        
        "victim_wallets": {
            "count": len(victims),
            "sample": victims[:50],
            "interpretation": "Retail victims who received CRM - check if same wallets in other scam exports"
        },
        
        "cross_project_recommendations": [
            "Check common counterparties for holdings in other scam tokens (BONK, WIF, etc.)",
            "Query exchange deposit addresses on Arkham to identify CEX entities",
            "Cross-reference victim wallets with other investigation databases",
            "Look for timing patterns across projects (did same victims get hit multiple times?)",
            "Analyze if network wallets used same counterparties in other token operations"
        ],
        
        "all_counterparties_by_wallet": {
            wallet: {
                cp: {
                    **{k: v for k, v in meta.items() if k != 'transactions'},
                    'interaction_types': list(meta['interaction_types'])
                }
                for cp, meta in cps.items()
            }
            for wallet, cps in all_counterparties.items()
        }
    }
    
    return report


def main():
    """Main execution"""
    csv_dir = "/root/crm_investigation/evidence/transaction_csvs"
    
    if not os.path.exists(csv_dir):
        print(f"❌ CSV directory not found: {csv_dir}")
        return
    
    report = analyze_csv_files(csv_dir)
    
    # Save report
    output_path = "/root/crm_investigation/case_files/cross_token/csv_network_mapping_analysis.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*70}")
    print("📊 ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"Total Counterparties Mapped: {report['total_counterparties_found']}")
    print(f"Cross-Project Connections: {report['cross_project_indicators']['common_counterparties_count']}")
    print(f"Exchange Cashout Points: {report['exchange_deposits']['candidates_count']}")
    print(f"Victim Wallets: {report['victim_wallets']['count']}")
    print(f"\nReport saved: {output_path}")
    print(f"{'='*70}\n")
    
    return report


if __name__ == "__main__":
    main()
