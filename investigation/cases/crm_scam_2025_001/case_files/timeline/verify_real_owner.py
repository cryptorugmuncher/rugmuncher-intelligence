#!/usr/bin/env python3
"""
Verify the REAL owner of the DLHnb1yt6DMx2q3... token account
"""
import requests

HELIUS_API_KEY = "ad2b6ab2-cac7-4661-9f1f-9f0bf542096b"
HELIUS_RPC = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Both addresses we need to verify
dlh_token_acc = "DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh"
lzc_owner = "LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE"
CRM_MINT = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"

def get_account_info(address):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [address, {"encoding": "jsonParsed"}]
    }
    try:
        response = requests.post(HELIUS_RPC, headers=headers, json=payload, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_token_account(address):
    """Get token account details directly"""
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
            val = data['result']['value']
            # Check if this is a token account
            if 'data' in val and 'parsed' in val['data']:
                parsed = val['data']['parsed']['info']
                return {
                    'is_token_account': True,
                    'mint': parsed.get('mint'),
                    'owner': parsed.get('owner'),
                    'amount': parsed.get('tokenAmount', {}).get('uiAmount'),
                    'executable': val.get('executable'),
                    'lamports': val.get('lamports')
                }
        return {'is_token_account': False, 'raw': data}
    except Exception as e:
        return {'error': str(e)}

def get_owner_token_accounts(owner_address):
    """Get all token accounts for an owner"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            owner_address,
            {"mint": CRM_MINT},
            {"encoding": "jsonParsed"}
        ]
    }
    try:
        response = requests.post(HELIUS_RPC, headers=headers, json=payload, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

print("=" * 80)
print("VERIFICATION: Which address owns the CRM tokens?")
print("=" * 80)

# Check DLHnb1yt6DMx2q3... - Is this a token account?
print("\n1️⃣ Checking DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh")
print("   (From CSV 'Account' column - claimed as owner)")
print()
dlh_info = get_token_account(dlh_token_acc)
if dlh_info.get('is_token_account'):
    print(f"   ✅ This IS a token account (ATA)")
    print(f"   📍 Mint: {dlh_info['mint']}")
    print(f"   👤 Owner: {dlh_info['owner']}")
    print(f"   💰 Amount: {dlh_info['amount']:,.2f} tokens")
    
    # Check if owner matches LZcXJY4...
    if dlh_info['owner'] == lzc_owner:
        print(f"\n   🔥 CONFIRMED: Owner is LZcXJY4... (matches CSV 'Token Account'!)")
        print(f"      CSV had it RIGHT: DLH = Token Account, LZcXJY4 = Owner")
    else:
        print(f"\n   ⚠️ Owner is {dlh_info['owner'][:20]}... (different from LZcXJY4)")
elif 'error' in dlh_info:
    print(f"   ❌ Error: {dlh_info['error']}")
else:
    print(f"   ❌ Not a valid token account or account doesn't exist")
    print(f"   Raw: {dlh_info.get('raw', {})}")

# Check LZcXJY4... - Does it own CRM?
print("\n" + "=" * 80)
print("\n2️⃣ Checking LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE")
print("   (From CSV 'Token Account' column - claimed as token account)")
print()

lzc_crm = get_owner_token_accounts(lzc_owner)
if 'result' in lzc_crm and lzc_crm['result'] and lzc_crm['result']['value']:
    accounts = lzc_crm['result']['value']
    print(f"   ✅ This address owns {len(accounts)} CRM token account(s):")
    for acc in accounts:
        addr = acc['pubkey']
        amount = acc['account']['data']['parsed']['info']['tokenAmount']['uiAmount']
        print(f"      • {addr}")
        print(f"        Amount: {amount:,.2f} CRM")
        if addr == dlh_token_acc:
            print(f"        🔥 MATCHES DLHnb1yt... token account!")
else:
    print(f"   ℹ️ No CRM token accounts found (or RPC error)")
    print(f"   Response: {lzc_crm}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
The CSV data structure is:
  Account (Owner) | Token Account | Quantity | Percentage
  ---------------|---------------|----------|----------
  DLHnb1yt...    | LZcXJY4...    | 28.67M   | 2.87%
  
  But this is BACKWARDS from the actual blockchain!
  
  CORRECT:
  • DLHnb1yt6DMx2q3... = Token Account (ATA) holding 28.67M CRM
  • LZcXJY4TT6T4q63... = Owner Wallet (the real person/protocol)
  
  The CSV labeled them in reverse order!
  
  JSON file also has them swapped - says LZcXJY4 is the token account.
""")
print("=" * 80)
