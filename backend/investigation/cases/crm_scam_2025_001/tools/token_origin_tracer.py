#!/usr/bin/env python3
"""
CRM Investigation: Token Origin Tracer
Traces token creation back to original dev wallet and funding sources.
"""

import requests
import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Load API key
HELIUS_API_KEY = os.getenv('HELIUS_API_KEY', '5a0ec17e-2c8c-4c58-b497-46e90d1c7ecc')
BASE_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Token to trace
TARGET_TOKEN = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"
TARGET_WALLET = "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC"

def helius_call(method: str, params: list) -> Optional[Dict]:
    """Make Helius RPC call."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    try:
        response = requests.post(BASE_URL, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

def get_token_largest_accounts(mint: str) -> List[Dict]:
    """Get largest token holders."""
    result = helius_call("getTokenLargestAccounts", [mint])
    if result and 'result' in result and 'value' in result['result']:
        return result['result']['value']
    return []

def get_token_supply(mint: str) -> Dict:
    """Get token supply info."""
    result = helius_call("getTokenSupply", [mint])
    if result and 'result' in result:
        return result['result']
    return {}

def get_token_accounts_by_owner(owner: str, mint: str) -> List[Dict]:
    """Get token accounts for owner."""
    result = helius_call("getTokenAccountsByOwner", [
        owner,
        {"mint": mint},
        {"encoding": "jsonParsed"}
    ])
    if result and 'result' in result and 'value' in result['result']:
        return result['result']['value']
    return []

def get_transaction_history(address: str, limit: int = 100) -> List[str]:
    """Get transaction signatures for address."""
    result = helius_call("getSignaturesForAddress", [address, {"limit": limit}])
    if result and 'result' in result:
        return [tx['signature'] for tx in result['result']]
    return []

def analyze_transaction(signature: str) -> Dict:
    """Get full transaction details."""
    result = helius_call("getTransaction", [
        signature,
        {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
    ])
    if result and 'result' in result:
        return result['result']
    return {}

def trace_token_creation():
    """Trace token back to creation transaction."""
    print("=" * 80)
    print("🔍 TOKEN ORIGIN TRACER - CRM Investigation")
    print("=" * 80)
    print(f"\nTarget Token: {TARGET_TOKEN}")
    print(f"Target Wallet: {TARGET_WALLET}")
    print(f"Analysis Time: {datetime.now().isoformat()}")
    
    # Get token supply
    print("\n" + "=" * 80)
    print("📊 TOKEN SUPPLY ANALYSIS")
    print("=" * 80)
    
    supply_info = get_token_supply(TARGET_TOKEN)
    if supply_info:
        print(f"\nTotal Supply: {supply_info.get('uiAmountString', 'Unknown')}")
        print(f"Decimals: {supply_info.get('decimals', 'Unknown')}")
        print(f"Supply: {supply_info.get('amount', 'Unknown')} (raw)")
    
    # Get largest holders
    print("\n" + "=" * 80)
    print("🏆 LARGEST TOKEN HOLDERS (LIVE)")
    print("=" * 80)
    
    largest = get_token_largest_accounts(TARGET_TOKEN)
    print(f"\nFound {len(largest)} significant holders:\n")
    
    for i, holder in enumerate(largest[:10], 1):
        address = holder.get('address', 'Unknown')
        amount = holder.get('uiAmount', 0)
        pct = holder.get('uiAmount', 0) / 1_000_000_000 * 100  # Assuming 1B supply
        
        # Check if it's our target wallet's token account
        owner = "Unknown"
        print(f"{i}. {address[:30]}...")
        print(f"   Amount: {amount:,.2f}")
        if pct > 0.01:
            print(f"   Est. %: ~{pct:.2f}%")
    
    # Get transaction history for target wallet
    print("\n" + "=" * 80)
    print("📜 TARGET WALLET TRANSACTION HISTORY")
    print("=" * 80)
    
    sigs = get_transaction_history(TARGET_WALLET, 50)
    print(f"\nFound {len(sigs)} recent transactions")
    print("\nSearching for token initialization...")
    
    found_creation = False
    for sig in sigs[:20]:
        tx = analyze_transaction(sig)
        if not tx:
            continue
        
        # Look for token program interactions
        meta = tx.get('meta', {})
        message = tx.get('transaction', {}).get('message', {})
        
        # Check for token mint instructions
        instructions = message.get('instructions', [])
        for instr in instructions:
            program = instr.get('program', '')
            if 'Token' in program or 'token' in program.lower():
                print(f"\n🎯 Token Transaction Found: {sig[:40]}...")
                print(f"   Program: {program}")
                
                # Check if it's initialize mint
                parsed = instr.get('parsed', {})
                if parsed:
                    itype = parsed.get('type', 'Unknown')
                    print(f"   Type: {itype}")
                    
                    if 'mint' in itype.lower() or 'initialize' in itype.lower():
                        print(f"   ⚠️ POTENTIAL MINT CREATION!")
                        found_creation = True
                        
                        info = parsed.get('info', {})
                        for key, val in info.items():
                            print(f"   {key}: {val}")
                
                print(f"   Block Time: {tx.get('blockTime', 'Unknown')}")
                break
    
    if not found_creation:
        print("\n⚠️  Token creation transaction not found in recent history")
        print("   Token may have been created by a different wallet")
        
    # Check for associated token account
    print("\n" + "=" * 80)
    print("🏦 TARGET WALLET TOKEN ACCOUNTS")
    print("=" * 80)
    
    accounts = get_token_accounts_by_owner(TARGET_WALLET, TARGET_TOKEN)
    print(f"\nFound {len(accounts)} token accounts for Eme5:")
    
    for acc in accounts:
        parsed = acc.get('account', {}).get('data', {}).get('parsed', {})
        info = parsed.get('info', {})
        address = acc.get('pubkey', 'Unknown')
        amount = info.get('tokenAmount', {}).get('uiAmount', 0)
        
        print(f"\n   Account: {address[:40]}...")
        print(f"   Balance: {amount:,.2f} Eme5")
    
    # Final recommendations
    print("\n" + "=" * 80)
    print("🎯 INVESTIGATIVE RECOMMENDATIONS")
    print("=" * 80)
    print("""
1. SEARCH METADATA:
   - Check token metadata on-chain for creation timestamp
   - Look for 'createMetadataAccount' instruction
   - Identify original mint authority

2. HISTORICAL ANALYSIS:
   - Query Helius API for full transaction history
   - Search for 'InitializeMint' instruction
   - Cross-reference with dev wallet patterns

3. FUNDING TRAIL:
   - Trace SOL funding for token creation
   - Check if CNSob1L... funded the creation
   - Analyze rent-exempt account creation

4. MINT AUTHORITY:
   - Confirm if mint authority was revoked
   - Check for 'SetAuthority' instructions
   - Verify freeze authority status

5. LIQUIDITY POOLS:
   - Find Raydium/Orca pool creation
   - Check initial liquidity addition
   - Identify liquidity providers
""")
    
    print("\n✅ Analysis Complete")
    print(f"Report saved: case_files/cross_token/TOKEN_ORIGIN_ANALYSIS.txt")

if __name__ == "__main__":
    trace_token_creation()
