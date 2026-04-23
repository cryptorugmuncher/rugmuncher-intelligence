#!/usr/bin/env python3
"""
Gaslight Token Hunter - Comprehensive search for Gaslight token
Uses multiple API methods and local data analysis
"""

import requests
import json
import os
import csv
from pathlib import Path
from typing import Dict, List, Optional
import time

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY', '5a0ec17e-2c8c-4c58-b497-46e90d1c7ecc')
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

def call_helius(method: str, params):
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

def get_multiple_assets(mints: List[str]):
    """Fetch multiple token assets in one call"""
    result = call_helius("getAssetBatch", {"ids": mints})
    if result and 'result' in result:
        return result['result']
    return []

def get_token_metadata(asset_id: str):
    """Fetch token metadata"""
    result = call_helius("getAsset", {
        "id": asset_id,
        "displayOptions": {
            "showFungible": True
        }
    })
    if result and 'result' in result:
        return result['result']
    return None

def parse_token_name_symbol(metadata: dict) -> tuple:
    """Extract name and symbol from metadata"""
    try:
        content = metadata.get('content', {})
        if isinstance(content, dict):
            metadata_section = content.get('metadata', {})
            if isinstance(metadata_section, dict):
                return (
                    metadata_section.get('name', ''),
                    metadata_section.get('symbol', '')
                )
        return ('', '')
    except:
        return ('', '')

def extract_all_tokens_from_csvs(csv_dir: Path) -> Dict[str, int]:
    """Extract all token addresses with transaction counts"""
    token_counts = {}
    
    for csv_file in csv_dir.glob("*.csv"):
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                token = row.get('Token Address', '').strip()
                # Filter valid mint addresses (base58 encoded, 32-44 chars)
                if token and len(token) >= 32 and len(token) <= 44:
                    if token not in ['TokenAddress', 'So11111111111111111111111111111111111111111', 
                                    'So11111111111111111111111111111111111111112']:
                        token_counts[token] = token_counts.get(token, 0) + 1
    
    return token_counts

def search_csv_text_for_gaslight(csv_dir: Path) -> List[dict]:
    """Search raw CSV text for 'gaslight' mentions"""
    matches = []
    
    for csv_file in csv_dir.glob("*.csv"):
        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if 'gaslight' in line.lower():
                    matches.append({
                        'file': csv_file.name,
                        'line_num': i + 1,
                        'content': line
                    })
    
    return matches

def main():
    csv_dir = Path("/root/crm_investigation/evidence/transaction_csvs")
    
    print("=" * 80)
    print("🔥 GASLIGHT TOKEN HUNTER 🔥")
    print("=" * 80)
    
    # Step 1: Text search in CSVs
    print("\n[STEP 1] Searching raw CSV text for 'Gaslight'...")
    text_matches = search_csv_text_for_gaslight(csv_dir)
    
    if text_matches:
        print(f"\n⚠️  FOUND {len(text_matches)} text matches!")
        for match in text_matches[:10]:
            print(f"   {match['file']}:{match['line_num']}")
            print(f"   -> {match['content'][:100]}")
    else:
        print("   No text matches found in CSVs")
    
    # Step 2: Extract all tokens
    print("\n[STEP 2] Extracting all token mints from CSVs...")
    token_counts = extract_all_tokens_from_csvs(csv_dir)
    
    # Separate pump tokens
    pump_tokens = {m: c for m, c in token_counts.items() if 'pump' in m.lower()}
    other_tokens = {m: c for m, c in token_counts.items() if 'pump' not in m.lower()}
    
    print(f"   Total unique tokens: {len(token_counts)}")
    print(f"   Pump tokens: {len(pump_tokens)}")
    print(f"   Other tokens: {len(other_tokens)}")
    
    # Step 3: Check top tokens by frequency
    print("\n[STEP 3] Checking token metadata (by transaction frequency)...")
    sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Check top 10 non-SOL tokens
    tokens_to_check = [m for m, c in sorted_tokens[:15] 
                      if m != 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS']
    
    print(f"   Checking {len(tokens_to_check)} tokens for Gaslight metadata...")
    
    found_gaslight = None
    
    for mint in tokens_to_check:
        time.sleep(0.1)  # Rate limiting
        metadata = get_token_metadata(mint)
        
        if metadata:
            name, symbol = parse_token_name_symbol(metadata)
            
            # Check for Gaslight
            if name and 'gaslight' in name.lower():
                found_gaslight = {
                    'mint': mint,
                    'name': name,
                    'symbol': symbol,
                    'tx_count': token_counts.get(mint, 0),
                    'metadata': metadata
                }
                print(f"\n🚨 GASLIGHT TOKEN FOUND! 🚨")
                print(f"   Mint: {mint}")
                print(f"   Name: {name}")
                print(f"   Symbol: {symbol}")
                print(f"   Transactions in CSVs: {token_counts.get(mint, 0)}")
                break
            
            if symbol and 'gaslight' in symbol.lower():
                found_gaslight = {
                    'mint': mint,
                    'name': name,
                    'symbol': symbol,
                    'tx_count': token_counts.get(mint, 0),
                    'metadata': metadata
                }
                print(f"\n🚨 GASLIGHT TOKEN FOUND! 🚨")
                print(f"   Mint: {mint}")
                print(f"   Name: {name}")
                print(f"   Symbol: {symbol}")
                print(f"   Transactions in CSVs: {token_counts.get(mint, 0)}")
                break
    
    # Step 4: If not found, check all pump tokens
    if not found_gaslight and pump_tokens:
        print("\n[STEP 4] Checking all pump tokens...")
        pump_mints = list(pump_tokens.keys())
        
        for i, mint in enumerate(pump_mints):
            if i % 5 == 0:
                print(f"   Progress: {i}/{len(pump_mints)}")
            
            time.sleep(0.1)
            metadata = get_token_metadata(mint)
            
            if metadata:
                name, symbol = parse_token_name_symbol(metadata)
                
                if name and 'gaslight' in name.lower():
                    found_gaslight = {
                        'mint': mint,
                        'name': name,
                        'symbol': symbol,
                        'tx_count': pump_tokens.get(mint, 0),
                        'metadata': metadata
                    }
                    print(f"\n🚨 GASLIGHT TOKEN FOUND! 🚨")
                    print(f"   Mint: {mint}")
                    print(f"   Name: {name}")
                    print(f"   Symbol: {symbol}")
                    print(f"   Transactions in CSVs: {pump_tokens.get(mint, 0)}")
                    break
                
                if symbol and 'gaslight' in symbol.lower():
                    found_gaslight = {
                        'mint': mint,
                        'name': name,
                        'symbol': symbol,
                        'tx_count': pump_tokens.get(mint, 0),
                        'metadata': metadata
                    }
                    print(f"\n🚨 GASLIGHT TOKEN FOUND! 🚨")
                    print(f"   Mint: {mint}")
                    print(f"   Name: {name}")
                    print(f"   Symbol: {symbol}")
                    print(f"   Transactions in CSVs: {pump_tokens.get(mint, 0)}")
                    break
    
    # Summary
    print("\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)
    
    if found_gaslight:
        print("\n✅ GASLIGHT TOKEN LOCATED")
        print(f"   Mint: {found_gaslight['mint']}")
        print(f"   Name: {found_gaslight['name']}")
        print(f"   Symbol: {found_gaslight['symbol']}")
        print(f"   Transaction count: {found_gaslight['tx_count']}")
    else:
        print("\n❌ Gaslight token not found in CSV data")
        print("\nPossible explanations:")
        print("   1. Token may not be included in these transaction exports")
        print("   2. Token may have been created after these exports")
        print("   3. Token name may be different in metadata")
        print("   4. The lead may refer to a different token or timeframe")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
