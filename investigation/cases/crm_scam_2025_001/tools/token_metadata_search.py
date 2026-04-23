#!/usr/bin/env python3
"""
Token Metadata Investigator - Search for Gaslight and other tokens
Uses Helius API to fetch token metadata and search by name/symbol
"""

import requests
import json
import os
from pathlib import Path
import csv

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY', '5a0ec17e-2c8c-4c58-b497-46e90d1c7ecc')
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

def call_helius(method: str, params: list):
    """Make Helius RPC call"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    try:
        response = requests.post(HELIUS_URL, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def get_token_metadata(mint: str):
    """Fetch token metadata from Helius"""
    result = call_helius("getAsset", {
        "id": mint,
        "displayOptions": {
            "showFungible": True,
            "showFungibleExtra": True
        }
    })
    
    if result and 'result' in result:
        return result['result']
    return None

def get_token_accounts_by_owner(owner: str, mint: str = None):
    """Get token accounts owned by a wallet"""
    params = {
        "owner": owner,
        "displayOptions": {}
    }
    if mint:
        params["mint"] = mint
    
    result = call_helius("getTokenAccounts", params)
    if result and 'result' in result:
        return result['result'].get('token_accounts', [])
    return []

def extract_unique_tokens_from_csvs(csv_dir: Path):
    """Extract all unique token mint addresses from CSV files"""
    token_counts = {}
    
    for csv_file in csv_dir.glob("*.csv"):
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                token = row.get('Token Address', '').strip()
                if token and token not in ['TokenAddress', '9', '6', '8', '', '1.0', 'SOL']:
                    if len(token) > 20:  # Likely a mint address
                        token_counts[token] = token_counts.get(token, 0) + 1
    
    return token_counts

def main():
    csv_dir = Path("/root/crm_investigation/evidence/transaction_csvs")
    
    print("=" * 80)
    print("TOKEN METADATA INVESTIGATION - Searching for Gaslight Token")
    print("=" * 80)
    
    # Extract tokens from CSVs
    print("\n📁 Extracting unique tokens from CSV files...")
    token_counts = extract_unique_tokens_from_csvs(csv_dir)
    
    # Sort by frequency
    sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n🔢 Found {len(sorted_tokens)} unique tokens")
    print("\nTop 20 most frequent tokens:")
    print("-" * 80)
    for mint, count in sorted_tokens[:20]:
        print(f"  {mint[:20]:20s}... ({count} transactions)")
    
    # Filter pump tokens
    pump_tokens = [(m, c) for m, c in sorted_tokens if 'pump' in m.lower()]
    print(f"\n🎰 Found {len(pump_tokens)} pump tokens")
    
    # Check for Gaslight specifically in addresses
    print("\n🔍 Searching for 'Gaslight' in token addresses...")
    gaslight_matches = []
    for mint, count in sorted_tokens:
        if 'light' in mint.lower() or 'gas' in mint.lower():
            gaslight_matches.append((mint, count))
    
    if gaslight_matches:
        print(f"\n  Found {len(gaslight_matches)} potential matches:")
        for mint, count in gaslight_matches:
            print(f"    {mint} ({count} txs)")
    else:
        print("  No matches found in addresses")
    
    # Sample some pump tokens to check metadata
    print("\n📊 Fetching metadata for sample pump tokens...")
    sample_pumps = [m for m, c in pump_tokens[:5]]
    
    for mint in sample_pumps:
        print(f"\n  Checking {mint[:30]}...")
        metadata = get_token_metadata(mint)
        if metadata:
            content = metadata.get('content', {})
            metadata_section = content.get('metadata', {})
            symbol = metadata_section.get('symbol', 'Unknown')
            name = metadata_section.get('name', 'Unknown')
            print(f"    Symbol: {symbol}")
            print(f"    Name: {name}")
            
            if 'gaslight' in name.lower() or 'gaslight' in symbol.lower():
                print(f"    ⚠️  GASLIGHT TOKEN FOUND!")
        else:
            print(f"    No metadata found")
    
    print("\n" + "=" * 80)
    
    # Also check the critical associate's token holdings
    critical_associate = "NRG6ebfB69PLiD1Xgj1NrCur2CF3i3mndt7eQFff6Vy"
    print(f"\n🔍 Checking token holdings of critical associate:")
    print(f"   {critical_associate}")
    
    token_accounts = get_token_accounts_by_owner(critical_associate)
    print(f"   Found {len(token_accounts)} token accounts")
    
    for ta in token_accounts[:10]:
        mint = ta.get('mint', '')
        balance = ta.get('amount', 0)
        print(f"   - {mint[:20]}... balance: {balance}")

if __name__ == "__main__":
    main()
