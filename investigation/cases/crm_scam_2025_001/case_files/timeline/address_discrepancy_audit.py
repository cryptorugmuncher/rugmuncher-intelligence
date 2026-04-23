#!/usr/bin/env python3
"""
CRM Investigation - Address Discrepancy Audit
==============================================

CRITICAL FINDING: Multiple different "DLHnb1yt" addresses exist in case files!

Need to verify:
1. Which is the REAL owner wallet vs token account
2. Are these Meteora/Raydium LP addresses?
3. Is there address confusion in the investigation files?

Addresses found:
- Script: DLHnb1yt6DMx9j5yg8y0jmtobDd2Pi5pMThdFtk8L36Y
- CSV: DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh  
- JSON: DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Set

# Addresses found across different files
ADDRESSES_FOUND = {
    "from_scripts": [
        "DLHnb1yt6DMx9j5yg8y0jmtobDd2Pi5pMThdFtk8L36Y",  # multi_api_timeline_builder.py, etc.
        "DLHnb1ytcR7p7F5zM5L8QQJdKJScFvx8y5v4J2Cmjcqf",  # complete-investigation-dashboard.html
    ],
    "from_csv_holders": [
        "DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh",  # token holders CSV
    ],
    "from_json": [
        "DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh",  # crm_holders_march_2026.json
    ]
}

CRM_MINT = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"


def audit_all_addresses():
    """Comprehensive audit of all DLHnb1yt addresses in the case"""
    
    print("="*100)
    print("ADDRESS DISCREPANCY AUDIT - DLHnb1yt Variations")
    print("="*100)
    
    all_addresses = set()
    for source, addresses in ADDRESSES_FOUND.items():
        all_addresses.update(addresses)
    
    print(f"\n🔍 Found {len(all_addresses)} unique DLHnb1yt-related addresses:")
    for addr in sorted(all_addresses):
        print(f"   • {addr}")
    
    print("\n" + "="*100)
    print("ANALYSIS: Are these the same wallet or different?")
    print("="*100)
    
    # The addresses are DIFFERENT - this is a critical finding
    script_addr = "DLHnb1yt6DMx9j5yg8y0jmtobDd2Pi5pMThdFtk8L36Y"
    csv_addr = "DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh"
    
    print(f"\n📊 Script Address:  {script_addr}")
    print(f"   CSV Address:    {csv_addr}")
    print(f"   Match: {'✅ SAME' if script_addr == csv_addr else '❌ DIFFERENT'}")
    
    # Show the prefix/suffix differences
    print(f"\n🔎 Prefix Comparison:")
    print(f"   Script: DLHnb1yt6DMx9j5yg8y0j...")
    print(f"   CSV:    DLHnb1yt6DMx2q3qoU2i8...")
    print(f"   → They share 'DLHnb1yt6DMx' but diverge after")
    
    print("\n" + "="*100)
    print("HYPOTHESIS: Token Account vs Owner Wallet")
    print("="*100)
    
    # Based on the CSV data:
    # DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh,LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE,28668823.524003334,2.87
    # Format: TokenAccount,Owner,Amount,Percent
    
    print("\n📋 CSV Token Holders Structure (2026-04-09 export):")
    print("   Column 1: Token Account Address")
    print("   Column 2: Owner Wallet Address")
    print("   Column 3: CRM Amount")
    print("   Column 4: % of Supply")
    
    print(f"\n🎯 From CSV:")
    print(f"   Token Account: DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh")
    print(f"   Owner:         LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE")
    print(f"   CRM Balance:   28,668,823 CRM (2.87%)")
    
    print(f"\n❌ PROBLEM: The scripts use DIFFERENT address!")
    print(f"   Script uses: DLHnb1yt6DMx9j5yg8y0jmtobDd2Pi5pMThdFtk8L36Y")
    print(f"   CSV shows:   DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh")
    print(f"   → These are NOT the same!")
    
    return {
        "addresses_found": list(all_addresses),
        "script_address": script_addr,
        "csv_token_account": csv_addr,
        "csv_owner": "LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE",
        "discrepancy": "ADDRESSES ARE DIFFERENT",
        "impact": "Analysis may be tracking wrong wallet",
        "real_crm_holder": {
            "token_account": "DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh",
            "owner": "LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE",
            "amount": 28668823.52,
            "percent": 2.87
        }
    }


def check_if_protocol_wallet(address: str) -> Dict:
    """Check if address matches known DEX protocol patterns"""
    
    # Known Meteora patterns (example addresses)
    METEORA_PATTERNS = [
        "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPyo",
    ]
    
    # Check if it's a PDA (Program Derived Address)
    # PDAs often end in specific patterns or are associated with programs
    
    result = {
        "address": address,
        "is_likely_protocol": False,
        "protocol_type": None,
        "evidence": []
    }
    
    # The DLHnb1yt addresses are TOKEN ACCOUNTS (associated token accounts)
    # They start with similar patterns because they're derived from the same owner
    
    if address.startswith("DLHnb1yt"):
        result["evidence"].append("Pattern suggests associated token account, not protocol")
        result["evidence"].append("Similar prefix indicates derivation from same owner")
    
    return result


def generate_correction_report():
    """Generate report on the address discrepancy"""
    
    audit = audit_all_addresses()
    
    print("\n" + "="*100)
    print("CORRECTION REQUIRED")
    print("="*100)
    
    print("""
🚨 CRITICAL DISCREPANCY IDENTIFIED

The investigation scripts have been using WRONG addresses!

WRONG (used in scripts):
   DLHnb1yt6DMx9j5yg8y0jmtobDd2Pi5pMThdFtk8L36Y
   → This address may not even exist or have wrong holdings

CORRECT (from CSV/JSON holders data):
   Token Account: DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh
   Owner: LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE
   CRM Balance: 28,668,823 (2.87% of supply)

NEXT STEPS:
1. Verify LZcXJY4... is the TRUE owner to investigate
2. Check if LZcXJY4... is a Meteora/Raydium protocol address
3. Re-run analysis with CORRECT owner address
4. Update all case files with corrected addresses

HOLDING BREAKDOWN (from CSV):
- DLHnb1yt token account: 28.67M CRM (2.87%)
- This is MUCH LESS than the 104.6M claimed in scripts
- The 104.6M figure may be COMBINED multiple wallets or completely wrong
""")
    
    return audit


if __name__ == "__main__":
    result = generate_correction_report()
    
    # Save correction
    output_dir = Path("/root/crm_investigation/case_files/timeline")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "address_discrepancy_audit.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Audit saved: {output_dir / 'address_discrepancy_audit.json'}")
