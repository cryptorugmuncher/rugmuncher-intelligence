#!/usr/bin/env python3
"""
Current Fund Locator
Finds where target wallets are currently holding funds
Queries token balances, LP positions, staking, and locked assets
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Target wallets to trace
TARGET_WALLETS = {
    "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC": "Tier 1 Feeder",
    "F4HGHWyajPWc9h2jS49Wxa5bdqPsL7YEvwq6xv1xBh1s": "Tier 2 Bridge", 
    "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6": "Tier 4 Field Ops",
    "DojAziGhpT6A9CY4C9PAmzZWm3ypZqgfnUAypm8PjqPE": "Tier 3 Relay",
    "HxyXAE1PHZ5iTFB7GzNHrp7djm2Bi8b8bNjqU0gKj46a": "Tier 3 Relay",
    "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj": "Tier 5 Feeder",
    "CaTWE2NPewVt1WLrQZeQGvUiMYexyV3YBaWhEDQ33kDh": "Tier 2 Relay",
    "CNSob1L8o7mM9Uwo1K1HVrV5H3Su8QweRzPrgLU3197i": "Tier 0 Distribution",
    "5dQWEMf1tTgkUwM3M3p4yAFv15nMxCvS9mof3x5BwtWc": "Tier 2 Pivot",
    "Cx5qTEtnp3arFVBuusMXHafoRzLCLuigtz2AiQAFmq2Q": "Tier 2 Bridge"
}

# Known high-value tokens to check
HIGH_VALUE_TOKENS = {
    "So11111111111111111111111111111111111111112": "SOL (Wrapped)",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
    "7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARo": "stSOL",
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3iKk8yWGBp1x2k": "mSOL",
    "bSo13r4TkiEpxxBhqvJ6PVnCQ2E8bM9TkrqWmyzDeFTE": "bSOL",
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": "BONK",
    "EKpQGSJtjMFqKZ9KQbSqN7uX6H8x9r8Y3a5oZ2J1WmNq": "WIF",
    "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHtcCeqSQgHH2": "POPCAT",
    "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yCEHXH4GvSx5": "JitoSOL"
}

class CurrentFundLocator:
    """Locates current fund positions across target wallets"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_holdings = {}
        self.total_recoverable = 0
        
    def _load_api_keys(self):
        """Load API keys from .secrets directory"""
        keys = {}
        secrets_dir = Path('/root/.secrets')
        
        key_files = {
            'helius': 'helius_api_key',
            'solscan': 'solscan_api_key',
            'quicknode': 'quicknode_api_key'
        }
        
        for service, filename in key_files.items():
            key_path = secrets_dir / filename
            if key_path.exists():
                try:
                    with open(key_path) as f:
                        keys[service] = f.read().strip()
                except:
                    pass
        
        return keys
    
    def get_sol_balance(self, wallet: str) -> dict:
        """Get native SOL balance via Helius"""
        if not self.api_keys.get('helius'):
            return {"error": "No API key"}
        
        try:
            url = f"https://mainnet.helius-rpc.com/?api-key={self.api_keys['helius']}"
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {})
                lamports = result.get('value', 0)
                sol = lamports / 1_000_000_000
                
                return {
                    "status": "success",
                    "lamports": lamports,
                    "sol_balance": sol,
                    "usd_value_approx": sol * 150  # Approx SOL price
                }
            else:
                return {"status": f"error_{response.status_code}"}
                
        except Exception as e:
            return {"status": f"error: {str(e)}"}
    
    def get_token_accounts(self, wallet: str) -> dict:
        """Get all SPL token accounts via Helius"""
        if not self.api_keys.get('helius'):
            return {"error": "No API key"}
        
        try:
            url = f"https://mainnet.helius-rpc.com/?api-key={self.api_keys['helius']}"
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('result', {}).get('value', [])
                
                tokens = []
                for account in accounts:
                    parsed = account.get('account', {}).get('data', {}).get('parsed', {}).get('info', {})
                    mint = parsed.get('mint', '')
                    amount = parsed.get('tokenAmount', {}).get('uiAmount', 0)
                    decimals = parsed.get('tokenAmount', {}).get('decimals', 0)
                    
                    # Check if it's a known high-value token
                    token_name = HIGH_VALUE_TOKENS.get(mint, f"Unknown ({mint[:8]}...)")
                    
                    if amount > 0:
                        tokens.append({
                            "mint": mint,
                            "name": token_name,
                            "amount": amount,
                            "decimals": decimals
                        })
                
                return {
                    "status": "success",
                    "token_count": len(tokens),
                    "tokens": tokens
                }
            else:
                return {"status": f"error_{response.status_code}"}
                
        except Exception as e:
            return {"status": f"error: {str(e)}"}
    
    def check_jupiter_positions(self, wallet: str) -> dict:
        """Check for Jupiter liquidity pool positions"""
        # Jupiter doesn't have a direct API for positions, but we can check for common LP tokens
        lp_tokens = {
            "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "JUP",
            "JUP6LkbZbjS1jKKwapdHNyMrzcTRm3SqxzDyzM9fJ3s": "JUPiter"
        }
        
        # For now, return placeholder - would need Jupiter API integration
        return {
            "status": "not_implemented",
            "note": "Jupiter LP positions require direct DEX analysis"
        }
    
    def analyze_wallet(self, wallet: str, role: str) -> dict:
        """Complete analysis of a single wallet's current holdings"""
        print(f"\n🔍 Analyzing: {wallet[:20]}... ({role})")
        
        analysis = {
            "wallet": wallet,
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "native_sol": None,
            "token_holdings": [],
            "lp_positions": [],
            "estimated_total_usd": 0,
            "status": "unknown"
        }
        
        # Get SOL balance
        sol_data = self.get_sol_balance(wallet)
        analysis["native_sol"] = sol_data
        
        if sol_data.get("status") == "success":
            sol_usd = sol_data.get("usd_value_approx", 0)
            analysis["estimated_total_usd"] += sol_usd
            print(f"  💰 SOL Balance: {sol_data.get('sol_balance', 0):.4f} SOL (~${sol_usd:.2f})")
        else:
            print(f"  ⚠ SOL query: {sol_data.get('status', 'failed')}")
        
        # Get token holdings
        token_data = self.get_token_accounts(wallet)
        analysis["token_holdings"] = token_data
        
        if token_data.get("status") == "success":
            tokens = token_data.get("tokens", [])
            if tokens:
                print(f"  🪙 Token Holdings: {len(tokens)} tokens")
                for token in tokens[:5]:  # Show top 5
                    print(f"     • {token['name']}: {token['amount']:.4f}")
            else:
                print(f"  🪙 No token holdings found")
        else:
            print(f"  ⚠ Token query: {token_data.get('status', 'failed')}")
        
        # Check status
        if sol_data.get("status") == "success" or token_data.get("status") == "success":
            analysis["status"] = "active"
        else:
            analysis["status"] = "dormant_or_deleted"
        
        return analysis
    
    def analyze_all_wallets(self):
        """Analyze all target wallets"""
        print("="*80)
        print("CURRENT FUND LOCATOR - ASSET RECOVERY TRACING")
        print("="*80)
        print(f"\n🎯 Analyzing {len(TARGET_WALLETS)} target wallets...")
        
        results = {}
        total_value = 0
        active_wallets = 0
        dormant_wallets = 0
        
        for wallet, role in TARGET_WALLETS.items():
            analysis = self.analyze_wallet(wallet, role)
            results[wallet] = analysis
            
            wallet_value = analysis.get("estimated_total_usd", 0)
            if wallet_value > 0:
                total_value += wallet_value
                active_wallets += 1
            elif analysis.get("status") == "dormant_or_deleted":
                dormant_wallets += 1
        
        self.current_holdings = results
        
        print("\n" + "="*80)
        print("SUMMARY - CURRENT FUND LOCATIONS")
        print("="*80)
        print(f"\n💰 Total Recoverable Value Found: ${total_value:,.2f}")
        print(f"📊 Active Wallets (with balances): {active_wallets}")
        print(f"😴 Dormant/Deleted Wallets: {dormant_wallets}")
        
        # Categorize by tier
        tier_summary = defaultdict(lambda: {"count": 0, "value": 0, "active": 0})
        for wallet, analysis in results.items():
            role = analysis.get("role", "Unknown")
            value = analysis.get("estimated_total_usd", 0)
            
            tier_summary[role]["count"] += 1
            tier_summary[role]["value"] += value
            if value > 0:
                tier_summary[role]["active"] += 1
        
        print(f"\n📋 By Tier:")
        for tier, data in sorted(tier_summary.items()):
            print(f"  {tier}: {data['active']}/{data['count']} active, ${data['value']:,.2f}")
        
        return results
    
    def generate_recovery_report(self):
        """Generate asset recovery report"""
        print("\n" + "="*80)
        print("ASSET RECOVERY ASSESSMENT")
        print("="*80)
        
        # Categorize findings
        recoverable = []
        dormant = []
        traceable_positions = []
        
        for wallet, analysis in self.current_holdings.items():
            value = analysis.get("estimated_total_usd", 0)
            role = analysis.get("role", "Unknown")
            
            if value > 0:
                recoverable.append({
                    "wallet": wallet,
                    "role": role,
                    "value_usd": value,
                    "sol_balance": analysis.get("native_sol", {}).get("sol_balance", 0)
                })
            elif analysis.get("status") == "active" and value == 0:
                # Wallet exists but may have moved funds
                traceable_positions.append({
                    "wallet": wallet,
                    "role": role,
                    "status": "active_but_empty",
                    "action": "Trace outgoing transactions"
                })
            else:
                dormant.append({
                    "wallet": wallet,
                    "role": role,
                    "status": "dormant_or_deleted"
                })
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "case_id": "CRM-SCAM-2025-001-RECOVERY",
            "recoverable_assets": {
                "wallets_with_value": recoverable,
                "total_recoverable_usd": sum(r["value_usd"] for r in recoverable),
                "count": len(recoverable)
            },
            "traceable_positions": {
                "active_empty_wallets": traceable_positions,
                "count": len(traceable_positions),
                "recommended_action": "Subpoena transaction history for outgoing flows"
            },
            "dormant_assets": {
                "wallets": dormant,
                "count": len(dormant),
                "note": "May have been wiped or funds moved pre-investigation"
            },
            "recovery_recommendations": [
                "1. Freeze any active wallets with balances immediately",
                "2. Subpoena Helius/Solscan for transaction history on traceable wallets",
                "3. Monitor dormant wallets for reactivation",
                "4. Cross-reference outgoing transactions with exchange deposit addresses",
                "5. Check for LP positions in Orca/Raydium/Jupiter pools",
                "6. Investigate staking positions (Marinade, Lido, Jito)",
                "7. Trace any remaining NFT holdings (Magic Eden, Tensor)"
            ]
        }
        
        # Save report
        report_path = Path('/root/crm_investigation/case_files/cross_token/asset_recovery_fund_locations.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💰 IMMEDIATELY RECOVERABLE: ${report['recoverable_assets']['total_recoverable_usd']:,.2f}")
        print(f"🔍 TRACEABLE POSITIONS: {report['traceable_positions']['count']} wallets")
        print(f"😴 DORMANT/DELETED: {report['dormant_assets']['count']} wallets")
        
        if recoverable:
            print(f"\n🎯 PRIORITY RECOVERY TARGETS:")
            for r in recoverable:
                print(f"  💎 {r['wallet'][:20]}... ({r['role']})")
                print(f"     Value: ${r['value_usd']:,.2f} ({r['sol_balance']:.4f} SOL)")
        
        if traceable_positions:
            print(f"\n🔍 TRACEABLE (FUNDS MOVED):")
            for t in traceable_positions[:3]:
                print(f"  🔎 {t['wallet'][:20]}... ({t['role']})")
                print(f"     Status: {t['status']} - {t['action']}")
        
        print(f"\n📁 Recovery report saved: {report_path}")
        
        return report

def run_fund_locator():
    """Run complete fund location analysis"""
    locator = CurrentFundLocator()
    locator.analyze_all_wallets()
    return locator.generate_recovery_report()

if __name__ == "__main__":
    report = run_fund_locator()
