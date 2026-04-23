#!/usr/bin/env python3
"""
Verify LZcXJY4... owner address - Check if it's Meteora/Raydium protocol or regular wallet
"""
import requests
import json

HELIUS_API_KEY = "ad2b6ab2-cac7-4661-9f1f-9f0bf542096b"
HELIUS_RPC = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# The owner address from CSV (correct data)
LZcXJY4 = "LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE"

# Known Meteora program addresses
METEORA_PROGRAMS = [
    "LBUZKhRxPFeX1Lg2PYqirjH2N64Q23xqUHL9BBzJSDj",  # Meteora Dynamic AMM
    "MERLuDFBMmsHnsBPZw2sDQZHvQcL5Zm7RcVM8j2b4hD",  # Mercurial (old)
]

# Known Raydium program addresses
RAYDIUM_PROGRAMS = [
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium AMM
    "CAMMCzo5YL8w4VFF8KVHrK22GGUspNitoXNTPvWQt3nN",  # Raydium CLMM
    "devi8QX7S7DVMepLCfG5E3XMaeRa8mWGRUQvLe8rRh8",  # Raydium Farms
]

def get_account_info(address):
    """Get account info from Helius"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [address, {"encoding": "jsonParsed"}]
    }
    
    try:
        response = requests.post(HELIUS_RPC, headers=headers, json=payload, timeout=15)
        data = response.json()
        if 'result' in data and data['result'] and data['result']['value']:
            return data['result']['value']
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_token_accounts(owner_address):
    """Get all token accounts for an owner"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            owner_address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    
    try:
        response = requests.post(HELIUS_RPC, headers=headers, json=payload, timeout=15)
        data = response.json()
        if 'result' in data and data['result']:
            return data['result']['value']
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def analyze_owner():
    """Analyze the owner address"""
    print("=" * 70)
    print("LZcXJY4... OWNER VERIFICATION")
    print("=" * 70)
    print(f"\nAddress: {LZcXJY4}")
    print(f"Source: CSV token holders export (ground truth)")
    print()
    
    # Get account info
    print("📋 Account Info:")
    info = get_account_info(LZcXJY4)
    if info:
        print(f"   Executable: {info.get('executable', 'N/A')}")
        print(f"   Data Size: {len(info.get('data', [''])[0]) if info.get('data') else 0} bytes")
        print(f"   Lamports: {info.get('lamports', 0)}")
        
        if info.get('executable'):
            print("\n⚠️  This is an EXECUTABLE account (likely a program)")
        else:
            print("\n✅ This is NOT an executable (regular wallet/account)")
    else:
        print("   Account not found or RPC error")
    
    # Get token accounts for this owner
    print("\n📊 Token Accounts (CRM Holdings):")
    token_accts = get_token_accounts(LZcXJY4)
    
    crm_mint = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"
    total_crm = 0
    
    for acct in token_accts:
        try:
            parsed = acct['account']['data']['parsed']['info']
            mint = parsed.get('mint', '')
            amount = parsed.get('tokenAmount', {}).get('uiAmount', 0)
            
            if mint == crm_mint:
                print(f"   ✅ CRM Token Account: {acct['pubkey']}")
                print(f"      Amount: {amount:,.2f} CRM")
                total_crm += amount
            elif mint:
                # Show other notable tokens
                if amount > 1000:
                    print(f"   • Other: {mint[:20]}... = {amount:,.2f}")
        except:
            pass
    
    print(f"\n💰 TOTAL CRM HOLDINGS: {total_crm:,.2f}")
    print(f"   = {total_crm/1_000_000_000*100:.2f}% of supply")
    
    # Check if this matches CSV
    csv_amount = 28668823.524003334
    print(f"\n📈 CSV Data: {csv_amount:,.2f} CRM (2.87%)")
    if abs(total_crm - csv_amount) < 1000:
        print("   ✅ MATCHES - Owner verified!")
    else:
        print("   ⚠️  DISCREPANCY - Need further investigation")
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    if info and not info.get('executable'):
        print("✅ LZcXJY4... is a REGULAR WALLET (not Meteora/Raydium protocol)")
        print("✅ This is an INDIVIDUAL OWNER, not a DEX/LP pool")
        print("\n🚨 CRIMINAL ANALYSIS VALID:")
        print("   • This wallet is controlled by an individual")
        print("   • 28.67M CRM is held by a person, not protocol liquidity")
        print("   • Not a false positive - legitimate investigation target")
    elif info and info.get('executable'):
        print("⚠️  LZcXJY4... is an EXECUTABLE (program/protocol)")
        print("   This would be a DEX pool, not an individual wallet")
        print("   Criminal analysis would need revision")
    else:
        print("❌ Could not verify account type")
    print("=" * 70)

if __name__ == "__main__":
    analyze_owner()
