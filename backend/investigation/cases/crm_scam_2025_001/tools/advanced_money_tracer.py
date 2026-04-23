#!/usr/bin/env python3
"""
Advanced Money Flow Tracer
Deep transaction analysis to follow funds from empty wallets
Traces through DEX swaps, bridge transfers, and multi-hop laundering
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import time

# Wallets to trace (the empty ones with history)
TRACE_TARGETS = {
    "F4HGHWyajPWc9h2jS49Wxa5bdqPsL7YEvwq6xv1xBh1s": {"role": "Tier 2 Bridge", "tier": 2},
    "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6": {"role": "Tier 4 Field Ops", "tier": 4, "note": "Military automation"},
    "DojAziGhpT6A9CY4C9PAmzZWm3ypZqgfnUAypm8PjqPE": {"role": "Tier 3 Relay", "tier": 3},
    "HxyXAE1PHZ5iTFB7GzNHrp7djm2Bi8b8bNjqU0gKj46a": {"role": "Tier 3 Relay", "tier": 3},
    "CaTWE2NPewVt1WLrQZeQGvUiMYexyV3YBaWhEDQ33kDh": {"role": "Tier 2 Relay", "tier": 2, "note": "1,000 archived txs"},
    "CNSob1L8o7mM9Uwo1K1HVrV5H3Su8QweRzPrgLU3197i": {"role": "Tier 0 Distribution", "tier": 0, "note": "100T CRM dev wallet"},
    "5dQWEMf1tTgkUwM3M3p4yAFv15nMxCvS9mof3x5BwtWc": {"role": "Tier 2 Pivot", "tier": 2}
}

# Known program IDs
PROGRAMS = {
    "JUP6LkbZbjS1jKKwapdHNyMrzcTRm3SqxzDyzM9fJ3s": "Jupiter Aggregator",
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
    "9W959DqEETiGZocYWCQPaJ6sBfRVfa9khKS9x8uBpx": "Orca",
    "6M8sdwj9x2zLpYqjm6G6LCWcMVjRm2MYNcQTRH8JK7S": "Meteora",
    "worm2ZoG2kUd4vFXhvjh93UU3LSR7K8D3z2vL3PjpQz": "Wormhole Bridge",
    "PuL1WLAhJ6qcKshC7Je7Stq3mJ8pwUeewC1MEgYzYp2": "Allbridge",
    "11111111111111111111111111111111": "System Program",
    "ComputeBudget111111111111111111111111111111": "Compute Budget",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token",
    " Memo1UhkJRfHyvLMcAubDnH4k6t4M9SHf4vMnkfS3e1": "Memo Program"
}

class AdvancedMoneyTracer:
    """Deep money flow analysis with multi-hop tracing"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.flow_data = defaultdict(lambda: {
            "outgoing_transfers": [],
            "dex_swaps": [],
            "bridge_transfers": [],
            "exchange_deposits": [],
            "unknown_flows": [],
            "total_sol_moved": 0,
            "total_usdc_moved": 0,
            "destinations": set()
        })
        self.discovered_wallets = set()
        
    def _load_api_keys(self):
        keys = {}
        secrets_dir = Path('/root/.secrets')
        for filename in ['helius_api_key']:
            key_path = secrets_dir / filename
            if key_path.exists():
                with open(key_path) as f:
                    keys['helius'] = f.read().strip()
        return keys
    
    def get_detailed_transactions(self, wallet: str, limit: int = 100) -> list:
        """Get detailed transaction data from Helius"""
        if not self.api_keys.get('helius'):
            return []
        
        url = f"https://mainnet.helius-rpc.com/?api-key={self.api_keys['helius']}"
        
        try:
            # Get signatures
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet, {"limit": limit}]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code != 200:
                return []
            
            signatures = response.json().get('result', [])
            
            transactions = []
            for sig_info in signatures[:50]:  # Limit to 50 for speed
                sig = sig_info.get('signature', '')
                if not sig:
                    continue
                
                # Get full transaction
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
                }
                
                tx_response = requests.post(url, json=tx_payload, timeout=30)
                if tx_response.status_code == 200:
                    tx_data = tx_response.json().get('result', {})
                    if tx_data:
                        transactions.append(tx_data)
                
                time.sleep(0.1)  # Rate limiting
            
            return transactions
            
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def analyze_transaction(self, tx: dict, source_wallet: str) -> dict:
        """Analyze a single transaction for money flow"""
        meta = tx.get('meta', {})
        transaction = tx.get('transaction', {})
        message = transaction.get('message', {})
        
        analysis = {
            "type": "unknown",
            "source": source_wallet,
            "destinations": [],
            "value_sol": 0,
            "value_usdc": 0,
            "program_interactions": [],
            "timestamp": tx.get('blockTime', 0)
        }
        
        # Get account keys
        account_keys = []
        if isinstance(message.get('accountKeys'), list):
            for key in message['accountKeys']:
                if isinstance(key, dict):
                    account_keys.append(key.get('pubkey', ''))
                elif isinstance(key, str):
                    account_keys.append(key)
        
        # Check for program interactions
        instructions = message.get('instructions', [])
        for ix in instructions:
            program_id = ix.get('programId', '') if isinstance(ix, dict) else ''
            if program_id in PROGRAMS:
                analysis["program_interactions"].append(PROGRAMS[program_id])
            elif program_id:
                analysis["program_interactions"].append(f"Unknown({program_id[:8]}...)")
        
        # Check native SOL transfers
        pre_balances = meta.get('preBalances', [])
        post_balances = meta.get('postBalances', [])
        
        if len(account_keys) > 0 and len(pre_balances) > 0 and len(post_balances) > 0:
            # Find source wallet index
            source_idx = -1
            for i, key in enumerate(account_keys):
                if key == source_wallet:
                    source_idx = i
                    break
            
            if source_idx >= 0 and source_idx < len(pre_balances) and source_idx < len(post_balances):
                sol_change = (post_balances[source_idx] - pre_balances[source_idx]) / 1_000_000_000
                
                if sol_change < -0.001:  # Significant outgoing
                    analysis["value_sol"] = abs(sol_change)
                    analysis["type"] = "sol_transfer"
                    
                    # Find destination (account with positive change)
                    for i in range(len(account_keys)):
                        if i < len(pre_balances) and i < len(post_balances):
                            dest_change = (post_balances[i] - pre_balances[i]) / 1_000_000_000
                            if dest_change > 0.001 and account_keys[i] != source_wallet:
                                analysis["destinations"].append({
                                    "address": account_keys[i],
                                    "amount": dest_change,
                                    "type": "sol"
                                })
                                self.discovered_wallets.add(account_keys[i])
        
        # Check token transfers
        pre_token_balances = meta.get('preTokenBalances', [])
        post_token_balances = meta.get('postTokenBalances', [])
        
        for pre in pre_token_balances:
            owner = pre.get('owner', '')
            if owner == source_wallet:
                mint = pre.get('mint', '')
                pre_amount = float(pre.get('uiTokenAmount', {}).get('uiAmount', 0))
                
                # Find matching post balance
                for post in post_token_balances:
                    if post.get('mint') == mint and post.get('owner') == source_wallet:
                        post_amount = float(post.get('uiTokenAmount', {}).get('uiAmount', 0))
                        token_change = post_amount - pre_amount
                        
                        if token_change < -0.01:  # Significant token outgoing
                            token_transfer = {
                                "mint": mint,
                                "amount": abs(token_change),
                                "type": "token_transfer"
                            }
                            
                            # Check if USDC/USDT
                            if "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" in mint:
                                analysis["value_usdc"] = abs(token_change)
                                token_transfer["symbol"] = "USDC"
                            elif "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB" in mint:
                                token_transfer["symbol"] = "USDT"
                            
                            analysis["destinations"].append(token_transfer)
                            
                            # Find recipient
                            for post_owner in post_token_balances:
                                if (post_owner.get('mint') == mint and 
                                    post_owner.get('owner') != source_wallet):
                                    recipient = post_owner.get('owner', '')
                                    if recipient:
                                        analysis["destinations"][-1]["recipient"] = recipient
                                        self.discovered_wallets.add(recipient)
        
        # Categorize transaction type
        programs = analysis["program_interactions"]
        if "Jupiter Aggregator" in programs:
            analysis["type"] = "jupiter_swap"
        elif "Raydium AMM" in programs or "Orca" in programs:
            analysis["type"] = "dex_swap"
        elif "Wormhole Bridge" in programs:
            analysis["type"] = "bridge_transfer"
        elif "Allbridge" in programs:
            analysis["type"] = "bridge_transfer"
        elif analysis["value_sol"] > 0 and not programs:
            analysis["type"] = "direct_transfer"
        
        return analysis
    
    def trace_wallet_flows(self, wallet: str, info: dict):
        """Trace all money flows from a wallet"""
        print(f"\n🔍 Tracing: {wallet[:25]}... ({info['role']})")
        
        transactions = self.get_detailed_transactions(wallet)
        
        if not transactions:
            print(f"  ⚠ No transaction data available")
            return
        
        print(f"  📊 Analyzing {len(transactions)} transactions...")
        
        flow_summary = self.flow_data[wallet]
        
        for tx in transactions:
            analysis = self.analyze_transaction(tx, wallet)
            
            # Categorize the flow
            if analysis["type"] == "jupiter_swap":
                flow_summary["dex_swaps"].append(analysis)
            elif analysis["type"] == "bridge_transfer":
                flow_summary["bridge_transfers"].append(analysis)
            elif analysis["type"] == "direct_transfer":
                if analysis["destinations"]:
                    dest = analysis["destinations"][0].get("address", "")
                    # Check if exchange-like
                    if any(ex in dest for ex in ["5Q544", "4CcCm", "8NtWH", "EvKkw", "G6Vvz"]):
                        flow_summary["exchange_deposits"].append(analysis)
                    else:
                        flow_summary["outgoing_transfers"].append(analysis)
                else:
                    flow_summary["unknown_flows"].append(analysis)
            elif analysis["value_sol"] > 0 or analysis["value_usdc"] > 0:
                flow_summary["unknown_flows"].append(analysis)
            
            # Track totals
            flow_summary["total_sol_moved"] += analysis["value_sol"]
            flow_summary["total_usdc_moved"] += analysis["value_usdc"]
            for dest in analysis["destinations"]:
                if "address" in dest:
                    flow_summary["destinations"].add(dest["address"])
        
        # Print summary
        print(f"  💸 Total SOL moved: {flow_summary['total_sol_moved']:.4f}")
        print(f"  💵 Total USDC moved: {flow_summary['total_usdc_moved']:.2f}")
        print(f"  🔄 DEX swaps: {len(flow_summary['dex_swaps'])}")
        print(f"  🌉 Bridge transfers: {len(flow_summary['bridge_transfers'])}")
        print(f"  🏦 Exchange deposits: {len(flow_summary['exchange_deposits'])}")
        print(f"  📤 Other transfers: {len(flow_summary['outgoing_transfers'])}")
        print(f"  ❓ Unknown: {len(flow_summary['unknown_flows'])}")
        
        if flow_summary["destinations"]:
            print(f"  🎯 Top destinations:")
            for dest in list(flow_summary["destinations"])[:5]:
                program = PROGRAMS.get(dest, "Unknown Wallet")
                print(f"     → {dest[:20]}... ({program[:20]})")
    
    def trace_all_targets(self):
        """Trace all target wallets"""
        print("="*80)
        print("ADVANCED MONEY FLOW TRACER - FOLLOWING THE MONEY")
        print("="*80)
        print(f"\n🎯 Tracing {len(TRACE_TARGETS)} wallets with empty balances...\n")
        
        for wallet, info in TRACE_TARGETS.items():
            self.trace_wallet_flows(wallet, info)
            time.sleep(0.5)  # Rate limiting between wallets
        
        return self.flow_data
    
    def aggregate_flow_analysis(self):
        """Aggregate flow analysis across all wallets"""
        print("\n" + "="*80)
        print("AGGREGATE MONEY FLOW ANALYSIS")
        print("="*80)
        
        totals = {
            "total_sol_moved": 0,
            "total_usdc_moved": 0,
            "total_dex_swaps": 0,
            "total_bridge_transfers": 0,
            "total_exchange_deposits": 0,
            "all_destinations": set(),
            "tier_breakdown": defaultdict(lambda: {
                "sol_moved": 0,
                "usdc_moved": 0,
                "destinations": set()
            })
        }
        
        for wallet, flow in self.flow_data.items():
            info = TRACE_TARGETS.get(wallet, {})
            tier = info.get("tier", 99)
            
            totals["total_sol_moved"] += flow["total_sol_moved"]
            totals["total_usdc_moved"] += flow["total_usdc_moved"]
            totals["total_dex_swaps"] += len(flow["dex_swaps"])
            totals["total_bridge_transfers"] += len(flow["bridge_transfers"])
            totals["total_exchange_deposits"] += len(flow["exchange_deposits"])
            totals["all_destinations"].update(flow["destinations"])
            
            totals["tier_breakdown"][tier]["sol_moved"] += flow["total_sol_moved"]
            totals["tier_breakdown"][tier]["usdc_moved"] += flow["total_usdc_moved"]
            totals["tier_breakdown"][tier]["destinations"].update(flow["destinations"])
        
        print(f"\n💰 TOTAL VALUE MOVED:")
        print(f"  SOL: {totals['total_sol_moved']:.4f} (~${totals['total_sol_moved'] * 150:,.2f})")
        print(f"  USDC: {totals['total_usdc_moved']:.2f}")
        
        print(f"\n🔄 LAUNDERING ACTIVITY:")
        print(f"  DEX Swaps: {totals['total_dex_swaps']}")
        print(f"  Bridge Transfers: {totals['total_bridge_transfers']}")
        print(f"  Exchange Deposits: {totals['total_exchange_deposits']}")
        
        print(f"\n📊 BY TIER:")
        for tier in sorted(totals["tier_breakdown"].keys()):
            data = totals["tier_breakdown"][tier]
            tier_names = {0: "Dev", 2: "Bridge", 3: "Relay", 4: "Field Ops"}
            tier_name = tier_names.get(tier, f"Tier {tier}")
            print(f"  Tier {tier} ({tier_name}):")
            print(f"    SOL: {data['sol_moved']:.4f}, USDC: {data['usdc_moved']:.2f}")
            print(f"    Destinations: {len(data['destinations'])}")
        
        print(f"\n🎯 UNIQUE DESTINATIONS DISCOVERED: {len(totals['all_destinations'])}")
        print(f"🆕 NEW WALLETS TO INVESTIGATE: {len(self.discovered_wallets - set(TRACE_TARGETS.keys()))}")
        
        return totals
    
    def generate_flow_map(self):
        """Generate complete money flow map"""
        print("\n" + "="*80)
        print("COMPLETE MONEY FLOW MAP")
        print("="*80)
        
        flow_map = {
            "source_wallets": {},
            "intermediate_nodes": defaultdict(lambda: {"inflow": 0, "sources": set(), "outflow": 0}),
            "terminal_destinations": {},
            "flow_chains": []
        }
        
        # Build flow chains
        for wallet, flow in self.flow_data.items():
            info = TRACE_TARGETS.get(wallet, {})
            
            flow_map["source_wallets"][wallet] = {
                "role": info.get("role", "Unknown"),
                "tier": info.get("tier", 99),
                "sol_moved": flow["total_sol_moved"],
                "usdc_moved": flow["total_usdc_moved"],
                "destinations": list(flow["destinations"])
            }
            
            # Track intermediate nodes
            for dest in flow["destinations"]:
                flow_map["intermediate_nodes"][dest]["inflow"] += flow["total_sol_moved"]
                flow_map["intermediate_nodes"][dest]["sources"].add(wallet)
        
        # Print flow visualization
        print("\n🌊 MONEY FLOW VISUALIZATION:")
        print("\nTIER 0 (Dev) → TIER 2 (Bridge) → TIER 3 (Relay) → TIER 4 (Automation) → CEX/BRIDGE")
        print("-" * 80)
        
        # Sort by tier
        tier_order = [0, 2, 3, 4]
        for tier in tier_order:
            tier_wallets = [w for w, info in TRACE_TARGETS.items() if info.get("tier") == tier]
            if tier_wallets:
                tier_names = {0: "DEV", 2: "BRIDGE", 3: "RELAY", 4: "AUTOMATION"}
                print(f"\n📦 {tier_names.get(tier, f'TIER {tier}')}:")
                for w in tier_wallets:
                    flow = self.flow_data.get(w, {})
                    sol = flow.get("total_sol_moved", 0)
                    if sol > 0.001:
                        print(f"  ↳ {w[:20]}... → {sol:.4f} SOL")
                        
                        # Show destinations
                        dests = list(flow.get("destinations", []))[:3]
                        for d in dests:
                            print(f"      → {d[:20]}...")
        
        # Save flow map
        report_path = Path('/root/crm_investigation/case_files/cross_token/complete_money_flow_map.json')
        
        # Convert sets to lists for JSON serialization
        flow_map["intermediate_nodes"] = dict(flow_map["intermediate_nodes"])
        for node, data in flow_map["intermediate_nodes"].items():
            data["sources"] = list(data["sources"])
        
        with open(report_path, 'w') as f:
            json.dump(flow_map, f, indent=2)
        
        print(f"\n📁 Complete flow map saved: {report_path}")
        
        return flow_map

def run_advanced_tracer():
    """Run complete advanced tracing"""
    tracer = AdvancedMoneyTracer()
    tracer.trace_all_targets()
    tracer.aggregate_flow_analysis()
    return tracer.generate_flow_map()

if __name__ == "__main__":
    flow_map = run_advanced_tracer()
