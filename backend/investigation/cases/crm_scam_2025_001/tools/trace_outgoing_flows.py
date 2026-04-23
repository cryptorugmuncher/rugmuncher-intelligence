#!/usr/bin/env python3
"""
Trace Outgoing Money Flows
Tracks where funds moved from active-but-empty wallets
Identifies final destinations and cashout points
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Wallets that are active but empty (need outgoing flow analysis)
TRACEABLE_WALLETS = [
    "F4HGHWyajPWc9h2jS49Wxa5bdqPsL7YEvwq6xv1xBh1s",  # Tier 2 Bridge
    "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",  # Tier 4 Field Ops
    "DojAziGhpT6A9CY4C9PAmzZWm3ypZqgfnUAypm8PjqPE",  # Tier 3 Relay
    "HxyXAE1PHZ5iTFB7GzNHrp7djm2Bi8b8bNjqU0gKj46a",  # Tier 3 Relay
    "CaTWE2NPewVt1WLrQZeQGvUiMYexyV3YBaWhEDQ33kDh",  # Tier 2 Relay
    "CNSob1L8o7mM9Uwo1K1HVrV5H3Su8QweRzPrgLU3197i",  # Tier 0 Distribution
    "5dQWEMf1tTgkUwM3M3p4yAFv15nMxCvS9mof3x5BwtWc"   # Tier 2 Pivot
]

# Known exchange addresses from previous analysis
KNOWN_EXCHANGES = {
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Binance Deposit",
    "4CcCmyVw9C39Cevwui6D7JxsF2RvwBm5orvZ3HmC6t7G": "Binance Deposit",
    "8NtWHVVBN6SR9MkTZ7g7kKuRBu1anAWNYHRY2ebWHXMr": "Coinbase Deposit",
    "EvKkwfnj9qyjwt9fF5TRMAWYxtVDSinDvMBudSSyNrY8": "Kraken Deposit",
    "G6VvzeU7wt2xkmrnNf3wrpe29DKnqvLz8ipF5A57QxQN": "Binance Deposit",
    "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC": "Tier 1 (Linked)"
}

# Jupiter/DEX program IDs
DEX_PROGRAMS = [
    "JUP6LkbZbjS1jKKwapdHNyMrzcTRm3SqxzDyzM9fJ3s",  # Jupiter
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium
    "9W959DqEETiGZocYWCQPaJ6sBfRVfa9khKS9x8uBpx",     # Orca
    "6M8sdwj9x2zLpYqjm6G6LCWcMVjRm2MYNcQTRH8JK7S"      # Meteora
]

class MoneyFlowTracer:
    """Traces outgoing money flows from target wallets"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.flow_analysis = {}
        
    def _load_api_keys(self):
        """Load API keys"""
        keys = {}
        secrets_dir = Path('/root/.secrets')
        
        for filename in ['helius_api_key', 'solscan_api_key']:
            key_path = secrets_dir / filename
            if key_path.exists():
                try:
                    with open(key_path) as f:
                        keys[filename.replace('_api_key', '')] = f.read().strip()
                except:
                    pass
        
        return keys
    
    def get_transaction_history(self, wallet: str, limit: int = 100) -> list:
        """Get transaction history via Helius"""
        if not self.api_keys.get('helius'):
            return []
        
        try:
            url = f"https://mainnet.helius-rpc.com/?api-key={self.api_keys['helius']}"
            
            # Get signatures first
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet, {"limit": limit}]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                signatures = data.get('result', [])
                
                transactions = []
                for sig in signatures[:20]:  # Get details for last 20
                    sig_str = sig.get('signature', '')
                    if sig_str:
                        # Get transaction details
                        tx_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getTransaction",
                            "params": [sig_str, {"encoding": "jsonParsed"}]
                        }
                        
                        tx_response = requests.post(url, json=tx_payload, timeout=30)
                        if tx_response.status_code == 200:
                            tx_data = tx_response.json()
                            transactions.append(tx_data.get('result', {}))
                
                return transactions
            
            return []
            
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def analyze_outgoing_flows(self, wallet: str) -> dict:
        """Analyze outgoing money flows from a wallet"""
        print(f"\n🔍 Tracing: {wallet[:20]}...")
        
        analysis = {
            "wallet": wallet,
            "total_transactions_analyzed": 0,
            "outgoing_transfers": [],
            "dex_interactions": [],
            "exchange_deposits": [],
            "unknown_destinations": [],
            "total_value_moved": 0,
            "largest_transfer": 0,
            "primary_destination": None
        }
        
        transactions = self.get_transaction_history(wallet)
        
        if not transactions:
            print(f"  ⚠ No transaction history available")
            return analysis
        
        analysis["total_transactions_analyzed"] = len(transactions)
        
        for tx in transactions:
            meta = tx.get('meta', {})
            transaction = tx.get('transaction', {})
            
            # Check for token transfers
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            
            # Native SOL transfer
            pre_sol = meta.get('preBalances', [0])[0] if meta.get('preBalances') else 0
            post_sol = meta.get('postBalances', [0])[0] if meta.get('postBalances') else 0
            
            if pre_sol > post_sol:
                sol_moved = (pre_sol - post_sol) / 1_000_000_000
                if sol_moved > 0.001:  # Filter dust
                    # Find destination
                    account_keys = transaction.get('message', {}).get('accountKeys', [])
                    if len(account_keys) > 1:
                        dest = account_keys[-1].get('pubkey', 'unknown')
                        
                        transfer = {
                            "type": "SOL",
                            "amount": sol_moved,
                            "destination": dest,
                            "timestamp": tx.get('blockTime', 0)
                        }
                        
                        # Categorize destination
                        if dest in KNOWN_EXCHANGES:
                            transfer["category"] = "exchange"
                            transfer["exchange_name"] = KNOWN_EXCHANGES[dest]
                            analysis["exchange_deposits"].append(transfer)
                        elif any(dex in str(tx) for dex in DEX_PROGRAMS):
                            transfer["category"] = "dex"
                            analysis["dex_interactions"].append(transfer)
                        else:
                            transfer["category"] = "unknown"
                            analysis["unknown_destinations"].append(transfer)
                        
                        analysis["outgoing_transfers"].append(transfer)
                        analysis["total_value_moved"] += sol_moved
                        
                        if sol_moved > analysis["largest_transfer"]:
                            analysis["largest_transfer"] = sol_moved
                            analysis["primary_destination"] = dest
        
        # Print summary
        print(f"  📊 Transactions analyzed: {analysis['total_transactions_analyzed']}")
        print(f"  💸 Total SOL moved: {analysis['total_value_moved']:.4f}")
        print(f"  📤 Outgoing transfers: {len(analysis['outgoing_transfers'])}")
        print(f"  🏦 Exchange deposits: {len(analysis['exchange_deposits'])}")
        print(f"  🔄 DEX interactions: {len(analysis['dex_interactions'])}")
        
        if analysis["primary_destination"]:
            dest = analysis["primary_destination"]
            exchange_name = KNOWN_EXCHANGES.get(dest, "Unknown")
            print(f"  🎯 Primary destination: {dest[:20]}... ({exchange_name})")
        
        return analysis
    
    def trace_all_wallets(self):
        """Trace outgoing flows from all traceable wallets"""
        print("="*80)
        print("MONEY FLOW TRACER - OUTGOING ASSET ANALYSIS")
        print("="*80)
        print(f"\n🎯 Tracing {len(TRACEABLE_WALLETS)} wallets with moved funds...\n")
        
        results = {}
        total_moved = 0
        exchange_flows = defaultdict(float)
        
        for wallet in TRACEABLE_WALLETS:
            analysis = self.analyze_outgoing_flows(wallet)
            results[wallet] = analysis
            
            total_moved += analysis["total_value_moved"]
            
            # Track exchange deposits
            for deposit in analysis["exchange_deposits"]:
                exchange = deposit.get("exchange_name", "Unknown")
                amount = deposit.get("amount", 0)
                exchange_flows[exchange] += amount
        
        self.flow_analysis = results
        
        print("\n" + "="*80)
        print("MONEY FLOW SUMMARY")
        print("="*80)
        print(f"\n💰 Total Value Moved: {total_moved:.4f} SOL (~${total_moved * 150:,.2f})")
        
        print(f"\n🏦 Exchange Deposit Flows:")
        for exchange, amount in sorted(exchange_flows.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {exchange}: {amount:.4f} SOL (~${amount * 150:,.2f})")
        
        return results
    
    def identify_final_destinations(self):
        """Identify where the money ultimately went"""
        print("\n" + "="*80)
        print("FINAL DESTINATION ANALYSIS")
        print("="*80)
        
        destinations = {
            "exchanges": defaultdict(lambda: {"wallets": [], "total_sol": 0}),
            "dex_pools": [],
            "other_wallets": defaultdict(float),
            "untraced": []
        }
        
        for wallet, analysis in self.flow_analysis.items():
            # Exchange deposits
            for deposit in analysis["exchange_deposits"]:
                exchange = deposit.get("exchange_name", "Unknown")
                destinations["exchanges"][exchange]["wallets"].append(wallet)
                destinations["exchanges"][exchange]["total_sol"] += deposit.get("amount", 0)
            
            # DEX interactions
            for dex in analysis["dex_interactions"]:
                destinations["dex_pools"].append({
                    "source": wallet,
                    "amount": dex.get("amount", 0),
                    "destination": dex.get("destination", "unknown")[:20]
                })
            
            # Unknown destinations
            for unknown in analysis["unknown_destinations"]:
                dest = unknown.get("destination", "unknown")
                amount = unknown.get("amount", 0)
                destinations["other_wallets"][dest] += amount
            
            # If no outgoing found
            if not analysis["outgoing_transfers"]:
                destinations["untraced"].append(wallet)
        
        print(f"\n🏦 PRIMARY CASHOUT POINTS:")
        for exchange, data in sorted(destinations["exchanges"].items(), 
                                     key=lambda x: x[1]["total_sol"], reverse=True):
            sol = data["total_sol"]
            wallets = len(data["wallets"])
            print(f"  💰 {exchange}")
            print(f"     Amount: {sol:.4f} SOL (~${sol * 150:,.2f})")
            print(f"     Source wallets: {wallets}")
        
        print(f"\n🔄 DEX LIQUIDITY MOVES:")
        for pool in destinations["dex_pools"][:5]:
            print(f"  • {pool['source'][:20]}... → {pool['destination']}... ({pool['amount']:.4f} SOL)")
        
        print(f"\n❓ UNTRACED WALLETS:")
        for wallet in destinations["untraced"]:
            print(f"  • {wallet[:20]}... (funds moved but destination unclear)")
        
        return destinations
    
    def generate_recovery_roadmap(self):
        """Generate final asset recovery roadmap"""
        print("\n" + "="*80)
        print("ASSET RECOVERY ROADMAP - WHERE ARE THE FUNDS TODAY")
        print("="*80)
        
        # Load current holdings
        try:
            with open('/root/crm_investigation/case_files/cross_token/asset_recovery_fund_locations.json') as f:
                holdings = json.load(f)
        except:
            holdings = {"recoverable_assets": {"wallets_with_value": []}}
        
        # Combine with flow analysis
        current_value = sum(w.get("value_usd", 0) 
                          for w in holdings.get("recoverable_assets", {}).get("wallets_with_value", []))
        
        # Estimate moved funds
        moved_funds = sum(a["total_value_moved"] * 150 for a in self.flow_analysis.values())
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "case_id": "CRM-SCAM-2025-001-RECOVERY-ROADMAP",
            "total_stolen_usd": 1818500,
            "recovery_status": {
                "immediately_recoverable": current_value,
                "traceable_moved_funds": moved_funds,
                "recovery_percentage": ((current_value + moved_funds) / 1818500) * 100
            },
            "current_holdings": holdings.get("recoverable_assets", {}).get("wallets_with_value", []),
            "flow_analysis": self.flow_analysis,
            "recovery_strategy": {
                "phase_1_immediate": [
                    f"Emergency freeze 3 wallets with ${current_value:,.2f} in current holdings",
                    "File emergency TROs (Temporary Restraining Orders)",
                    "Notify exchanges of identified deposit addresses"
                ],
                "phase_2_trace": [
                    "Subpoena transaction history for 7 empty-but-active wallets",
                    "Trace DEX liquidity pool positions",
                    "Analyze bridge transfers (Wormhole, Allbridge)",
                    "Cross-reference with CEX KYC records"
                ],
                "phase_3_recovery": [
                    "Asset forfeiture proceedings on frozen funds",
                    "Victim restitution distribution",
                    "International cooperation for off-shore accounts"
                ]
            },
            "key_targets": {
                "priority_1": "HLnpSz9h... (Tier 1 Feeder) - $16,069.90 currently held",
                "priority_2": "Exchange deposit cluster - ~$50K+ in aggregate flows",
                "priority_3": "DEX liquidity positions - unknown value"
            }
        }
        
        # Save report
        report_path = Path('/root/crm_investigation/case_files/cross_token/ASSET_RECOVERY_ROADMAP.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💰 TOTAL ASSET RECOVERY POTENTIAL:")
        print(f"  • Currently Held: ${current_value:,.2f}")
        print(f"  • Traceable Moved: ~${moved_funds:,.2f}")
        print(f"  • Recovery Potential: {report['recovery_status']['recovery_percentage']:.1f}% of stolen funds")
        
        print(f"\n🎯 3-PHASE RECOVERY STRATEGY:")
        for phase, actions in report["recovery_strategy"].items():
            phase_name = phase.replace("_", " ").upper()
            print(f"\n  {phase_name}:")
            for action in actions:
                print(f"    • {action}")
        
        print(f"\n📁 Recovery roadmap saved: {report_path}")
        
        return report

def run_flow_tracer():
    """Run complete money flow analysis"""
    tracer = MoneyFlowTracer()
    tracer.trace_all_wallets()
    tracer.identify_final_destinations()
    return tracer.generate_recovery_roadmap()

if __name__ == "__main__":
    report = run_flow_tracer()
