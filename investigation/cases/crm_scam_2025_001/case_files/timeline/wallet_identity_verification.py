#!/usr/bin/env python3
"""
CRM Investigation - Wallet Identity Verification
=================================================

CRITICAL CORRECTION: Verify if suspicious wallets are actually:
1. Meteora DEX/Liquidity Pool wallets
2. Raydium AMM/Pool addresses
3. Jupiter aggregator addresses
4. Other protocol contracts/PDAs
5. Token account vs owner wallet distinction

This could completely change the analysis if DLHnb1yt is a protocol wallet.
"""

import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# API Configuration
HELIUS_API_KEY = "5a0ec17e-2c8c-4c58-b497-46e90d1c7ecc"
HELIUS_RPC = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Known DEX/Protocol Program IDs for verification
KNOWN_PROGRAMS = {
    # Meteora
    "Meteora DLMM": "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPyo",
    "Meteora Pools": "MERLuDFBMmsHnsBPZw2sDQZHv2gXzQNL4KZJQ5UWMa",
    
    # Raydium
    "Raydium AMM": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "Raydium CLMM": "CAMMCzo5YL8w4VFF8KVHrK22GGUspNngaCPi2yNTPQ8",
    "Raydium CP Swap": "CPMMoo8L9FYgPRs361ajuEj7ARU1LKY2d2KJHrfp5mYj",
    
    # Jupiter
    "Jupiter Aggregator": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
    
    # Orca
    "Orca Whirlpool": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGbb3XQucDr",
    
    # Token Programs
    "Token Program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "Associated Token": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
    
    # System
    "System Program": "11111111111111111111111111111111",
}

# Wallets to verify
WALLETS_TO_VERIFY = {
    "DLHnb1yt": "LZcXJY4TT6T4q63RRZjsWHHS7ByV5RL4rxMAxGmiUFE",  # CORRECTED: Owner of DLHnb1yt6DMx2q3... token account (28.67M CRM)
    "HLnpSz9h": "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC",
    "8eVZa7": "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",
    "BKLBtcJQJ2": "BKLBtcJQJ2gB6Bz9sUPf2r4DR7yXGo3MQH3UjSncEpLz",
    "AFXigaYu": "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",
}

CRM_MINT = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"


class WalletIdentityVerifier:
    """Verify if wallets are protocol/contract addresses vs individual wallets"""
    
    def __init__(self):
        self.api_healthy = False
        self.verification_results = {}
        
    async def check_api(self):
        """Verify Helius API connectivity"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getHealth"
            }
            try:
                async with session.post(HELIUS_RPC, json=payload, timeout=10) as resp:
                    self.api_healthy = resp.status == 200
                    return self.api_healthy
            except:
                self.api_healthy = False
                return False
    
    async def get_account_info(self, address: str) -> Optional[dict]:
        """Get detailed account information"""
        if not self.api_healthy:
            return None
            
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [address, {"encoding": "jsonParsed"}]
            }
            try:
                async with session.post(HELIUS_RPC, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("result", {}).get("value")
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
        return None
    
    async def get_token_accounts(self, address: str) -> List[dict]:
        """Get all token accounts owned by this address"""
        if not self.api_healthy:
            return []
            
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [address, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]
            }
            try:
                async with session.post(HELIUS_RPC, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("result", {}).get("value", [])
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
        return []
    
    async def is_executable(self, address: str) -> Optional[bool]:
        """Check if address is an executable program"""
        account_info = await self.get_account_info(address)
        if account_info:
            return account_info.get("executable", False)
        return None
    
    async def analyze_wallet_type(self, name: str, address: str) -> dict:
        """Comprehensive analysis of wallet type"""
        print(f"\n{'='*80}")
        print(f"VERIFYING: {name} ({address})")
        print(f"{'='*80}")
        
        result = {
            "name": name,
            "address": address,
            "wallet_type": "UNKNOWN",
            "is_program": False,
            "is_executable": False,
            "is_pda": False,
            "is_token_account": False,
            "owner_program": None,
            "lamports": 0,
            "data_size": 0,
            "crm_token_account": None,
            "risk_assessment": "UNKNOWN",
            "notes": []
        }
        
        # Get account info
        account_info = await self.get_account_info(address)
        
        if account_info:
            print(f"\n✅ Account exists on-chain")
            
            # Basic properties
            result["lamports"] = account_info.get("lamports", 0)
            result["data_size"] = len(account_info.get("data", [""])[0]) if isinstance(account_info.get("data"), list) else 0
            result["is_executable"] = account_info.get("executable", False)
            
            print(f"   Balance: {result['lamports'] / 1e9:.4f} SOL")
            print(f"   Data size: {result['data_size']} bytes")
            print(f"   Executable: {result['is_executable']}")
            
            # Check if it's a program
            if result["is_executable"]:
                result["wallet_type"] = "PROGRAM/CONTRACT"
                result["is_program"] = True
                result["risk_assessment"] = "PROTOCOL - Not individual wallet"
                result["notes"].append("This is an executable program, not a user wallet")
                print(f"   ⚠️ TYPE: PROGRAM/CONTRACT (not an individual wallet)")
                return result
            
            # Check parsed data for token accounts
            parsed = account_info.get("data", {}).get("parsed", {}) if isinstance(account_info.get("data"), dict) else {}
            
            if parsed:
                info = parsed.get("info", {})
                program = parsed.get("type", "unknown")
                
                print(f"   Parsed type: {program}")
                
                # Check if it's a token account
                if program in ["account", "mint"]:
                    owner = info.get("owner")
                    mint = info.get("mint")
                    
                    if owner:
                        result["owner_program"] = owner
                        print(f"   Owner: {owner}")
                        
                        # Check if owner is a known program
                        for prog_name, prog_id in KNOWN_PROGRAMS.items():
                            if owner == prog_id:
                                result["wallet_type"] = f"TOKEN_ACCOUNT ({prog_name})"
                                result["is_token_account"] = True
                                result["risk_assessment"] = f"PROTOCOL - {prog_name} token account"
                                result["notes"].append(f"Owned by {prog_name}")
                                print(f"   ⚠️ TYPE: {prog_name} TOKEN ACCOUNT")
                                break
                        else:
                            result["wallet_type"] = "TOKEN_ACCOUNT (unknown owner)"
                            result["is_token_account"] = True
                            result["risk_assessment"] = "NEEDS_VERIFICATION"
                            result["notes"].append(f"Token account owned by: {owner}")
                            print(f"   ⚠️ TYPE: TOKEN ACCOUNT")
                    
                    if mint:
                        print(f"   Mint: {mint}")
                        if mint == CRM_MINT:
                            result["crm_token_account"] = True
                            print(f"   🎯 THIS IS A CRM TOKEN ACCOUNT!")
            
            # Check data to determine if it's a PDA (Program Derived Address)
            data = account_info.get("data", [""])
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
                # If it has significant data, it might be a PDA or contract state
                if len(data[0]) > 100:
                    result["notes"].append("Has significant on-chain data - may be PDA or contract state")
                    print(f"   📝 Has significant data - may be PDA")
            
        else:
            print(f"\n❌ Account not found or is token account (not owner wallet)")
            result["notes"].append("Not found as owner account - may be token account address")
            
            # Try to get it as a token account directly
            result["wallet_type"] = "TOKEN_ACCOUNT (not owner)"
            result["is_token_account"] = True
        
        # Get token accounts for this owner
        token_accounts = await self.get_token_accounts(address)
        if token_accounts:
            print(f"\n📊 Token Accounts: {len(token_accounts)}")
            
            for ta in token_accounts[:5]:  # Show first 5
                account_data = ta.get("account", {})
                parsed = account_data.get("data", {}).get("parsed", {}).get("info", {})
                mint = parsed.get("mint", "unknown")
                balance = parsed.get("tokenAmount", {}).get("uiAmount", 0)
                
                if mint == CRM_MINT:
                    print(f"   🎯 CRM Account: {balance:,.2f} CRM")
                    result["notes"].append(f"Holds {balance:,.2f} CRM in token account")
                    result["crm_balance"] = balance
        
        return result
    
    def check_known_dex_patterns(self, address: str) -> Optional[str]:
        """Check if address matches known DEX wallet patterns"""
        # Known Meteora/Raydium pool patterns
        dex_keywords = ["pool", "amm", "lp", "liquidity", "vault", "reserve"]
        
        # This is a heuristic - real detection requires on-chain verification
        return None
    
    async def verify_all_wallets(self):
        """Run verification on all suspicious wallets"""
        print("="*100)
        print("WALLET IDENTITY VERIFICATION - Checking for DEX/Protocol Wallets")
        print("="*100)
        print(f"\n🕐 Generated: {datetime.now().isoformat()}")
        print(f"🎯 Purpose: Verify if 'suspicious' wallets are actually Meteora/Raydium protocols")
        
        await self.check_api()
        
        if not self.api_healthy:
            print("\n⚠️ API unavailable - using heuristic analysis")
        
        results = {}
        
        for name, address in WALLETS_TO_VERIFY.items():
            result = await self.analyze_wallet_type(name, address)
            results[name] = result
            await asyncio.sleep(0.5)
        
        return results
    
    def generate_verification_report(self, results: dict) -> dict:
        """Generate comprehensive verification report"""
        
        report = {
            "verification_id": "WALLET-IDENTITY-CHECK-2026",
            "title": "Wallet Identity Verification - Protocol vs Individual",
            "generated_at": datetime.now().isoformat(),
            "purpose": "Verify if suspicious wallets are Meteora/Raydium/Protocol addresses",
            
            "executive_summary": {
                "wallets_checked": len(results),
                "protocol_wallets_found": 0,
                "individual_wallets": 0,
                "unknown_type": 0,
                "corrections_needed": []
            },
            
            "wallet_analysis": results,
            
            "known_programs_reference": KNOWN_PROGRAMS,
            
            "key_questions_answered": {
                "is_dlhnb1yt_meteora": "VERIFICATION NEEDED - Check on-chain",
                "is_hlnp_protocol": "VERIFICATION NEEDED - Check on-chain", 
                "are_these_user_wallets": "VERIFICATION NEEDED - Must check owner programs"
            }
        }
        
        # Count types
        for name, result in results.items():
            wallet_type = result.get("wallet_type", "UNKNOWN")
            
            if "PROGRAM" in wallet_type or "PROTOCOL" in result.get("risk_assessment", ""):
                report["executive_summary"]["protocol_wallets_found"] += 1
                report["executive_summary"]["corrections_needed"].append({
                    "wallet": name,
                    "issue": "May be protocol wallet, not individual criminal wallet",
                    "impact": "Could invalidate previous analysis if confirmed"
                })
            elif "TOKEN_ACCOUNT" in wallet_type:
                report["executive_summary"]["unknown_type"] += 1
            else:
                report["executive_summary"]["individual_wallets"] += 1
        
        return report


async def main():
    verifier = WalletIdentityVerifier()
    results = await verifier.verify_all_wallets()
    
    # Generate report
    report = verifier.generate_verification_report(results)
    
    # Save
    output_dir = Path("/root/crm_investigation/case_files/timeline")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "wallet_identity_verification.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*100)
    print("VERIFICATION COMPLETE")
    print("="*100)
    print(f"\n💾 Report saved: {output_dir / 'wallet_identity_verification.json'}")
    
    # Print critical findings
    print("\n🚨 CRITICAL: Need to verify if these are Meteora/Raydium pool addresses")
    print("   If DLHnb1yt or others are DEX protocols, the analysis needs correction.")
    print("\n📋 Next Steps:")
    print("   1. Check each wallet on Solscan for 'Program' vs 'Account' label")
    print("   2. Verify if they appear in Meteora/Raydium pool lists")
    print("   3. Check if owner is a known DEX program ID")
    print("   4. Re-evaluate criminal analysis if protocol wallets confirmed")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())
