#!/usr/bin/env python3
"""
Live Controller Wallet Association Analysis v2
Uses Helius API with proper transaction parsing
Filters system programs and identifies real associates
"""

import requests
import json
import os
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY')
if not HELIUS_API_KEY:
    print("❌ HELIUS_API_KEY not found")
    exit(1)

RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

SYSTEM_PROGRAMS = {
    '11111111111111111111111111111111': 'System Program',
    'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': 'Token Program',
    'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb': 'Token-2022 Program',
    'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL': 'Associated Token Program',
    'Memo1UhkJRfHyvLMc3uc1g6B9HXn1cU5U3GwbJ7nPnm': 'Memo Program',
    'MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr': 'Memo Program v2',
    'ComputeBudget111111111111111111111111111111': 'Compute Budget',
    'Vote111111111111111111111111111111111111111': 'Vote Program',
    'Stake11111111111111111111111111111111111111': 'Stake Program',
    'So11111111111111111111111111111111111111112': 'Wrapped SOL',
}

DEX_PROGRAMS = {
    'JUP6LkbZbjS1jKKwapdHNy74zcjn3VLbqatjhSL8BS': 'Jupiter Aggregator v6',
    '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium AMM',
    'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctuCc': 'Orca Whirlpool',
    '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin': 'Serum DEX',
    '6MLxL4XYS8KZzVyNnf1iNVSRRuqPD6bR9XEmZUYS7bN5': 'Meteora DLMM',
    '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun',
    'AMM55ShdkfGRixf9msF7hH2MD4YjjJWsyB7WVFyivqD': 'Raydium Concentrated',
}

def get_signatures(wallet: str, limit: int = 100):
    """Get transaction signatures for a wallet"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet, {"limit": limit}]
    }
    try:
        response = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        return response.json().get('result', [])
    except Exception as e:
        print(f"Error fetching signatures: {e}")
        return []

def get_transaction(signature: str):
    """Get detailed transaction data"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
    }
    try:
        response = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        return response.json().get('result')
    except Exception as e:
        return None

def extract_counterparties(tx_data: dict, target_wallet: str):
    """Extract all addresses interacting with target wallet"""
    counterparties = defaultdict(lambda: {'count': 0, 'types': set()})
    
    if not tx_data:
        return counterparties
    
    # Get account keys from message
    message = tx_data.get('transaction', {}).get('message', {})
    account_keys = message.get('accountKeys', [])
    
    # Map account index to pubkey
    key_map = {}
    for i, key_info in enumerate(account_keys):
        if isinstance(key_info, dict):
            key_map[i] = key_info.get('pubkey', '')
        else:
            key_map[i] = key_info
    
    # Extract from token balances
    meta = tx_data.get('meta', {})
    
    # Pre/post token balances show transfers
    for balance in meta.get('preTokenBalances', []) + meta.get('postTokenBalances', []):
        owner = balance.get('owner', '')
        if owner and owner != target_wallet:
            counterparties[owner]['count'] += 1
            counterparties[owner]['types'].add('token_holder')
    
    # Extract from inner instructions (where actual transfers happen)
    for inner in meta.get('innerInstructions', []):
        for inst in inner.get('instructions', []):
            parsed = inst.get('parsed', {})
            if isinstance(parsed, dict):
                info = parsed.get('info', {})
                itype = parsed.get('type', '')
                
                # Look for transfer-related fields
                for field in ['source', 'destination', 'authority', 'owner', 'wallet', 'account']:
                    if field in info:
                        addr = info[field]
                        if addr != target_wallet:
                            counterparties[addr]['count'] += 1
                            counterparties[addr]['types'].add(itype if itype else 'interaction')
    
    # Extract from main instructions
    for inst in message.get('instructions', []):
        parsed = inst.get('parsed', {})
        if isinstance(parsed, dict):
            info = parsed.get('info', {})
            itype = parsed.get('type', '')
            
            for field in ['source', 'destination', 'authority', 'owner', 'wallet', 'account', 'from', 'to']:
                if field in info:
                    addr = info[field]
                    if addr != target_wallet:
                        counterparties[addr]['count'] += 1
                        counterparties[addr]['types'].add(itype if itype else 'instruction')
    
    return counterparties

def analyze_live(wallet: str, tx_limit: int = 50):
    """Perform live association analysis"""
    print(f"\n{'='*80}")
    print(f"🔴 LIVE ASSOCIATION ANALYSIS")
    print(f"   Target Wallet: {wallet}")
    print(f"   API: Helius (Mainnet)")
    print(f"{'='*80}\n")
    
    print("📊 Step 1: Fetching transaction signatures...")
    signatures = get_signatures(wallet, limit=tx_limit)
    print(f"   ✓ Found {len(signatures)} transactions\n")
    
    if not signatures:
        print("❌ No transactions found")
        return None
    
    # Track all associations
    all_associations = defaultdict(lambda: {
        'interaction_count': 0,
        'first_seen': None,
        'last_seen': None,
        'types': set(),
        'transaction_count': 0
    })
    
    system_counts = defaultdict(int)
    dex_counts = defaultdict(int)
    
    print(f"🔍 Step 2: Analyzing {min(tx_limit, len(signatures))} transactions...")
    for i, sig_info in enumerate(signatures[:tx_limit]):
        sig = sig_info.get('signature')
        block_time = sig_info.get('blockTime')
        
        tx_data = get_transaction(sig)
        if not tx_data:
            continue
        
        counterparties = extract_counterparties(tx_data, wallet)
        
        for addr, data in counterparties.items():
            # Categorize
            if addr in SYSTEM_PROGRAMS:
                system_counts[addr] += data['count']
            elif addr in DEX_PROGRAMS:
                dex_counts[addr] += data['count']
            else:
                # Real user wallet
                all_associations[addr]['interaction_count'] += data['count']
                all_associations[addr]['types'].update(data['types'])
                all_associations[addr]['transaction_count'] += 1
                
                if block_time:
                    if not all_associations[addr]['first_seen'] or block_time < all_associations[addr]['first_seen']:
                        all_associations[addr]['first_seen'] = block_time
                    if not all_associations[addr]['last_seen'] or block_time > all_associations[addr]['last_seen']:
                        all_associations[addr]['last_seen'] = block_time
        
        if (i + 1) % 10 == 0:
            print(f"   Analyzed {i+1}/{min(tx_limit, len(signatures))} txs...")
    
    print(f"\n{'='*80}")
    print("ANALYSIS RESULTS")
    print(f"{'='*80}\n")
    
    # System programs filtered
    print(f"🛡️  SYSTEM PROGRAMS FILTERED ({len(system_counts)} unique):")
    for addr, count in sorted(system_counts.items(), key=lambda x: -x[1])[:8]:
        name = SYSTEM_PROGRAMS.get(addr, 'Unknown')
        print(f"   • {name:<35} {count:>4} interactions")
    
    # DEX programs
    if dex_counts:
        print(f"\n🔄 DEX/ROUTERS FILTERED ({len(dex_counts)} unique):")
        for addr, count in sorted(dex_counts.items(), key=lambda x: -x[1])[:5]:
            name = DEX_PROGRAMS.get(addr, 'Unknown')
            print(f"   • {name:<35} {count:>4} interactions")
    else:
        print(f"\n🔄 DEX/ROUTERS: None detected")
    
    # User wallets
    print(f"\n👤 REAL USER WALLET ASSOCIATIONS: {len(all_associations)} unique addresses")
    
    # Sort by interaction count
    sorted_assocs = sorted(all_associations.items(), key=lambda x: -x[1]['interaction_count'])
    
    # High frequency (5+)
    high_freq = [(addr, d) for addr, d in sorted_assocs if d['interaction_count'] >= 5]
    
    print(f"\n🎯 HIGH-FREQUENCY ASSOCIATES (5+ interactions): {len(high_freq)}")
    print("-" * 70)
    
    for rank, (addr, data) in enumerate(high_freq[:20], 1):
        count = data['interaction_count']
        tx_count = data['transaction_count']
        types = ', '.join(data['types']) if data['types'] else 'unknown'
        
        # Date range
        first = data['first_seen']
        last = data['last_seen']
        if first and last:
            first_str = datetime.fromtimestamp(first).strftime('%Y-%m-%d')
            last_str = datetime.fromtimestamp(last).strftime('%Y-%m-%d')
            date_range = f"{first_str} → {last_str}"
        else:
            date_range = "Unknown"
        
        # Priority
        if count >= 30:
            priority = "🔴 CRITICAL"
        elif count >= 15:
            priority = "🟠 HIGH"
        elif count >= 10:
            priority = "🟡 ELEVATED"
        else:
            priority = "🟢 MEDIUM"
        
        print(f"\n{priority} - Rank #{rank}")
        print(f"   Address:    {addr}")
        print(f"   Interactions: {count:>3} across {tx_count} transactions")
        print(f"   Types:      {types}")
        print(f"   Date Range: {date_range}")
    
    # Critical finding summary
    critical = [(addr, d) for addr, d in high_freq if d['interaction_count'] >= 30]
    print(f"\n{'='*80}")
    print(f"🚨 CRITICAL FINDINGS")
    print(f"{'='*80}")
    print(f"   Total Real Associates: {len(all_associations)}")
    print(f"   High-Frequency (5+):   {len(high_freq)}")
    print(f"   Critical (30+):        {len(critical)}")
    print(f"   System Programs:       {len(system_counts)}")
    print(f"   DEX Programs:          {len(dex_counts)}")
    
    # Save results
    output = {
        'wallet': wallet,
        'analysis_date': datetime.now().isoformat(),
        'mode': 'LIVE_HELIUS',
        'transactions_analyzed': min(tx_limit, len(signatures)),
        'system_programs': {addr: {'name': SYSTEM_PROGRAMS.get(addr), 'interactions': count} 
                           for addr, count in system_counts.items()},
        'dex_programs': {addr: {'name': DEX_PROGRAMS.get(addr), 'interactions': count}
                        for addr, count in dex_counts.items()},
        'user_associations': {
            addr: {
                'interaction_count': d['interaction_count'],
                'transaction_count': d['transaction_count'],
                'types': list(d['types']),
                'first_seen': d['first_seen'],
                'last_seen': d['last_seen']
            }
            for addr, d in sorted_assocs[:50]
        },
        'high_frequency_count': len(high_freq),
        'critical_count': len(critical)
    }
    
    output_file = f"case_files/cross_token/live_assoc_{wallet[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n📁 Full results saved: {output_file}")
    
    return output

if __name__ == "__main__":
    # Target wallet from transaction data
    TARGET = "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC"
    analyze_live(TARGET, tx_limit=50)
