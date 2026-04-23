#!/usr/bin/env python3
"""
Live Controller Wallet Association Analysis
Uses real Helius API data to identify associates
Filters system programs and DEX infrastructure
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
    print("❌ HELIUS_API_KEY not found in environment")
    exit(1)

RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Known system programs to filter
SYSTEM_PROGRAMS = {
    '11111111111111111111111111111111': 'System Program',
    'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': 'Token Program',
    'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL': 'Associated Token Program',
    'Memo1UhkJRfHyvLMc3uc1g6B9HXn1cU5U3GwbJ7nPnm': 'Memo Program',
    'MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr': 'Memo Program v2',
    'ComputeBudget111111111111111111111111111111': 'Compute Budget',
    'Vote111111111111111111111111111111111111111': 'Vote Program',
    'Stake11111111111111111111111111111111111111': 'Stake Program',
    'Config1111111111111111111111111111111111111': 'Config Program',
    'So11111111111111111111111111111111111111112': 'Wrapped SOL',
}

# Known DEX programs to filter
DEX_PROGRAMS = {
    'JUP6LkbZbjS1jKKwapdHNy74zcjn3VLbqatjhSL8BS': 'Jupiter Aggregator v6',
    '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium AMM',
    'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctuCc': 'Orca Whirlpool',
    '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin': 'Serum DEX',
    '6MLxL4XYS8KZzVyNnf1iNVSRRuqPD6bR9XEmZUYS7bN5': 'Meteora DLMM',
    '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun',
    'AMM55ShdkfGRixf9msF7hH2MD4YjjJWsyB7WVFyivqD': 'Raydium Concentrated',
}

# Known CEX deposit addresses (common patterns)
CEX_PATTERNS = [
    'binance', 'kucoin', 'kraken', 'coinbase', 'okx', 'bybit', 'huobi', 'gate',
    'mexc', 'bitget', 'cryptocom', 'lbank', 'xt', 'bitmart'
]

def get_transaction_history(wallet: str, limit: int = 1000):
    """Fetch transaction history via Helius RPC"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet, {"limit": limit}]
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        data = response.json()
        return data.get('result', [])
    except Exception as e:
        print(f"❌ Error fetching signatures: {e}")
        return []

def get_transaction_details(signature: str):
    """Get detailed transaction data"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        data = response.json()
        return data.get('result')
    except Exception as e:
        return None

def extract_counterparties(tx_data: dict, target_wallet: str):
    """Extract all addresses that interacted with target wallet"""
    counterparties = set()
    
    if not tx_data:
        return counterparties
    
    # Extract from accountKeys
    message = tx_data.get('transaction', {}).get('message', {})
    account_keys = message.get('accountKeys', [])
    
    for key_info in account_keys:
        if isinstance(key_info, dict):
            pubkey = key_info.get('pubkey', '')
        else:
            pubkey = key_info
        
        if pubkey and pubkey != target_wallet:
            counterparties.add(pubkey)
    
    # Extract from innerInstructions
    meta = tx_data.get('meta', {})
    inner_instructions = meta.get('innerInstructions', [])
    
    for inner in inner_instructions:
        for instruction in inner.get('instructions', []):
            if isinstance(instruction, dict):
                # Handle parsed instructions
                parsed = instruction.get('parsed', {})
                if isinstance(parsed, dict):
                    info = parsed.get('info', {})
                    for field in ['source', 'destination', 'authority', 'multisigAuthority', 'owner', 'account']:
                        if field in info and info[field] != target_wallet:
                            counterparties.add(info[field])
                
                # Handle accounts array
                accounts = instruction.get('accounts', [])
                for acc in accounts:
                    if acc != target_wallet:
                        counterparties.add(acc)
            
            # Handle legacy format
            if isinstance(instruction, list) and len(instruction) >= 2:
                for acc in instruction[1:]:
                    if isinstance(acc, str) and acc != target_wallet:
                        counterparties.add(acc)
    
    # Extract from token pre/post balances
    pre_token_balances = meta.get('preTokenBalances', [])
    post_token_balances = meta.get('postTokenBalances', [])
    
    for balance in pre_token_balances + post_token_balances:
        owner = balance.get('owner', '')
        if owner and owner != target_wallet:
            counterparties.add(owner)
    
    return counterparties

def analyze_associations(wallet: str):
    """Analyze all associations for a wallet"""
    print(f"\n{'='*80}")
    print(f"LIVE ASSOCIATION ANALYSIS: {wallet[:20]}...")
    print(f"{'='*80}\n")
    
    # Get transaction history
    print("📊 Fetching transaction history...")
    signatures = get_transaction_history(wallet, limit=100)
    
    if not signatures:
        print("❌ No transactions found or API error")
        return None
    
    print(f"   Found {len(signatures)} transactions to analyze")
    
    # Track associations
    user_wallets = defaultdict(lambda: {
        'interaction_count': 0,
        'first_seen': None,
        'transaction_types': set(),
        'total_sol_volume': 0,
        'total_usdc_volume': 0
    })
    
    system_program_counts = defaultdict(int)
    dex_program_counts = defaultdict(int)
    
    # Analyze each transaction
    print("\n🔍 Analyzing transactions...")
    for i, sig_info in enumerate(signatures[:50]):  # Analyze first 50 for speed
        sig = sig_info.get('signature')
        if not sig:
            continue
        
        tx_data = get_transaction_details(sig)
        if not tx_data:
            continue
        
        counterparties = extract_counterparties(tx_data, wallet)
        
        for address in counterparties:
            if address in SYSTEM_PROGRAMS:
                system_program_counts[address] += 1
            elif address in DEX_PROGRAMS:
                dex_program_counts[address] += 1
            else:
                # This is likely a user wallet
                user_wallets[address]['interaction_count'] += 1
                block_time = tx_data.get('blockTime')
                if block_time:
                    if not user_wallets[address]['first_seen'] or block_time < user_wallets[address]['first_seen']:
                        user_wallets[address]['first_seen'] = block_time
        
        if (i + 1) % 10 == 0:
            print(f"   Processed {i+1}/{min(50, len(signatures))} transactions...")
    
    # Results
    print(f"\n{'='*80}")
    print("ASSOCIATION ANALYSIS RESULTS")
    print(f"{'='*80}\n")
    
    # System programs filtered
    print(f"🛡️  SYSTEM PROGRAMS FILTERED: {len(system_program_counts)}")
    for addr, count in sorted(system_program_counts.items(), key=lambda x: -x[1])[:5]:
        name = SYSTEM_PROGRAMS.get(addr, 'Unknown')
        print(f"   • {name[:30]:<30} - {count} interactions")
    
    # DEX programs filtered
    print(f"\n🔄 DEX/ROUTERS FILTERED: {len(dex_program_counts)}")
    for addr, count in sorted(dex_program_counts.items(), key=lambda x: -x[1])[:5]:
        name = DEX_PROGRAMS.get(addr, 'Unknown')
        print(f"   • {name[:30]:<30} - {count} interactions")
    
    # User wallet associations
    print(f"\n👤 REAL USER WALLET ASSOCIATIONS: {len(user_wallets)}")
    
    # Sort by interaction count
    sorted_wallets = sorted(user_wallets.items(), key=lambda x: -x[1]['interaction_count'])
    
    high_frequency = [(addr, data) for addr, data in sorted_wallets if data['interaction_count'] >= 5]
    
    print(f"\n🎯 HIGH-FREQUENCY ASSOCIATES (5+ interactions): {len(high_frequency)}")
    for addr, data in high_frequency[:15]:
        count = data['interaction_count']
        first_seen = data['first_seen']
        if first_seen:
            from datetime import datetime
            date_str = datetime.fromtimestamp(first_seen).strftime('%Y-%m-%d')
        else:
            date_str = 'Unknown'
        
        priority = "🔴 CRITICAL" if count >= 20 else "🟠 HIGH" if count >= 10 else "🟡 MEDIUM"
        print(f"\n   {priority}")
        print(f"   Address: {addr}")
        print(f"   Interactions: {count} | First Seen: {date_str}")
    
    # Save results
    output_data = {
        'wallet': wallet,
        'analysis_date': datetime.now().isoformat(),
        'mode': 'LIVE',
        'transactions_analyzed': len(signatures),
        'counterparties': {
            'user_wallets': {
                addr: {
                    'interaction_count': data['interaction_count'],
                    'first_seen': data['first_seen'],
                }
                for addr, data in sorted_wallets[:30]
            },
            'system_programs': {addr: {'name': SYSTEM_PROGRAMS.get(addr, 'Unknown'), 'interactions': count} 
                               for addr, count in system_program_counts.items()},
            'dex_programs': {addr: {'name': DEX_PROGRAMS.get(addr, 'Unknown'), 'interactions': count} 
                            for addr, count in dex_program_counts.items()},
            'high_frequency_count': len(high_frequency)
        }
    }
    
    output_file = f"case_files/cross_token/live_associations_{wallet[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n📁 Results saved: {output_file}")
    
    return output_data

if __name__ == "__main__":
    # Analyze the key wallet from transaction data
    TARGET_WALLET = "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC"
    analyze_associations(TARGET_WALLET)
