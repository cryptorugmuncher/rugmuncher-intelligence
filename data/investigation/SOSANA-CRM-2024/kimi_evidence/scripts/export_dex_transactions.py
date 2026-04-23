#!/usr/bin/env python3
"""
DEX Transaction Exporter
========================
Export all DEX interactions (Raydium, Meteora, Jupiter, Orca) for specified wallets.
Identifies swaps, liquidity additions/removals, and position management.

Usage:
    python export_dex_transactions.py --wallet HLnpSz9h --api-key YOUR_KEY
    python export_dex_transactions.py --all-network-wallets --api-key YOUR_KEY
"""

import argparse
import json
import requests
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import csv

# Network wallets to analyze
NETWORK_WALLETS = {
    "confirmed_dumps": {
        "HLnpSz9h_first": "HLnpSz9h",  # First instance - deleted
        "6LXutJvK": "6LXutJvK",
        "7uCYuvPb": "7uCYuvPb",
        "HGS4DyyX": "HGS4DyyX",
        "DLHnb1yt": "DLHnb1yt"  # Active
    },
    "fee_collector": {
        "GVC9Zvh3": "GVC9Zvh3"
    },
    "suspected_treasuries": {
        "ASTyfSima": "ASTyfSima",
        "H8sMJSCQ": "H8sMJSCQ"
    }
}

# DEX Program IDs
DEX_PROGRAMS = {
    # Raydium
    "raydium_amm": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "raydium_clmm": "CAMMCzo5YL8w4VzWM8B3pZ5h9Y4JToCjKFnq4z2k3zZ",
    "raydium_cp_swap": "CPMMoo8L3F4CsA4z3MZiGwJ3Tg6mQvP1M3Z4z5z6z7z",  # Update with actual
    
    # Meteora
    "meteora_dlmm": "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
    "meteora_pools": "METoXqxxkx8q1fPz8m1S8s7zLk5g3q4z5z6z7z8z9z0",  # Update with actual
    
    # Jupiter
    "jupiter_aggregator": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
    "jupiter_dca": "DCA265Vj8a9CEuX1eb1LWRnDT7uK6qZxS6z7z8z9z0z1",  # Update with actual
    "jupiter_limit": "LIM1Xy9j1Xy9j1Xy9j1Xy9j1Xy9j1Xy9j1Xy9j1Xy9",  # Update with actual
    
    # Orca
    "orca_whirlpool": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    "orca_aquafarm": "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",
    
    # Token Programs
    "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "associated_token": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
}

# CRM token mint
CRM_MINT = "UPDATE_WITH_ACTUAL_CRM_MINT"  # Need actual CRM token mint address


class DEXTransactionExporter:
    """Export DEX transactions for forensic analysis."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.helius.xyz/v0"
    
    def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Fetch all transactions for a wallet."""
        url = f"{self.base_url}/addresses/{address}/transactions"
        params = {"api-key": self.api_key, "limit": limit}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def identify_dex_interaction(self, tx: Dict) -> Optional[Dict]:
        """
        Identify if transaction is a DEX interaction.
        
        Returns interaction details or None if not DEX-related.
        """
        tx_hash = tx.get("signature", "UNKNOWN")
        timestamp = tx.get("timestamp", 0)
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp else "UNKNOWN"
        
        # Check program invocations
        instructions = tx.get("instructions", [])
        for instruction in instructions:
            program_id = instruction.get("programId", "")
            
            # Check against known DEX programs
            dex_type = None
            for dex_name, dex_program in DEX_PROGRAMS.items():
                if program_id == dex_program:
                    dex_type = dex_name
                    break
            
            if dex_type:
                return {
                    "tx_hash": tx_hash,
                    "timestamp": timestamp,
                    "date": date_str,
                    "dex": dex_type,
                    "program_id": program_id,
                    "instruction": instruction,
                    "full_transaction": tx
                }
        
        # Check for swaps in events
        if "events" in tx and "swap" in tx["events"]:
            swap_event = tx["events"]["swap"]
            return {
                "tx_hash": tx_hash,
                "timestamp": timestamp,
                "date": date_str,
                "dex": "swap_event",
                "swap_details": swap_event,
                "full_transaction": tx
            }
        
        return None
    
    def analyze_swap(self, tx: Dict, wallet_address: str) -> Optional[Dict]:
        """
        Analyze a swap transaction for direction, amounts, and counterparty.
        """
        swap_info = {
            "tx_hash": tx.get("signature", "UNKNOWN"),
            "timestamp": tx.get("timestamp", 0),
            "date": datetime.fromtimestamp(tx.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S"),
            "wallet": wallet_address,
            "type": "SWAP",
            "dex": "UNKNOWN",
            "input_token": None,
            "input_amount": 0,
            "output_token": None,
            "output_amount": 0,
            "counterparties": [],
            "price_impact": None,
            "slippage": None
        }
        
        # Extract from events if available
        if "events" in tx and "swap" in tx["events"]:
            swap_event = tx["events"]["swap"]
            
            # Get input tokens
            token_inputs = swap_event.get("tokenInputs", [])
            for input_token in token_inputs:
                owner = input_token.get("userAccount", "")
                if wallet_address in owner:
                    swap_info["input_token"] = input_token.get("mint", "UNKNOWN")
                    swap_info["input_amount"] = input_token.get("tokenAmount", 0)
            
            # Get output tokens
            token_outputs = swap_event.get("tokenOutputs", [])
            for output_token in token_outputs:
                owner = output_token.get("userAccount", "")
                if wallet_address in owner:
                    swap_info["output_token"] = output_token.get("mint", "UNKNOWN")
                    swap_info["output_amount"] = output_token.get("tokenAmount", 0)
                else:
                    # This is the counterparty
                    swap_info["counterparties"].append({
                        "address": owner,
                        "token": output_token.get("mint", "UNKNOWN"),
                        "amount": output_token.get("tokenAmount", 0)
                    })
            
            # Determine swap direction
            if swap_info["input_token"] == CRM_MINT:
                swap_info["direction"] = "SELL_CRM"
            elif swap_info["output_token"] == CRM_MINT:
                swap_info["direction"] = "BUY_CRM"
            else:
                swap_info["direction"] = "OTHER"
            
            # Identify DEX from inner instructions
            inner_instructions = tx.get("innerInstructions", [])
            for inner in inner_instructions:
                for instruction in inner.get("instructions", []):
                    program_id = instruction.get("programId", "")
                    for dex_name, dex_program in DEX_PROGRAMS.items():
                        if program_id == dex_program:
                            swap_info["dex"] = dex_name
                            break
        
        # Extract from native transfers if no swap event
        elif "nativeTransfers" in tx:
            for transfer in tx["nativeTransfers"]:
                if transfer.get("fromUserAccount") == wallet_address:
                    swap_info["input_token"] = "SOL"
                    swap_info["input_amount"] = transfer.get("amount", 0) / 1e9
                elif transfer.get("toUserAccount") == wallet_address:
                    swap_info["output_token"] = "SOL"
                    swap_info["output_amount"] = transfer.get("amount", 0) / 1e9
        
        # Only return if we have meaningful data
        if swap_info["input_token"] or swap_info["output_token"]:
            return swap_info
        
        return None
    
    def export_wallet_dex_history(self, wallet_key: str, wallet_address: str) -> Dict[str, Any]:
        """Export complete DEX history for a wallet."""
        print(f"\n{'='*60}")
        print(f"Exporting DEX history: {wallet_key}")
        print(f"Address: {wallet_address}")
        print(f"{'='*60}\n")
        
        # Fetch transactions
        print("Fetching transactions from Helius...")
        transactions = self.get_transactions(wallet_address, limit=100)
        
        if not transactions:
            return {
                "wallet": wallet_key,
                "address": wallet_address,
                "error": "No transactions found",
                "swaps": [],
                "liquidity_ops": [],
                "dex_interactions": []
            }
        
        print(f"Found {len(transactions)} total transactions")
        
        # Analyze each transaction
        swaps = []
        liquidity_ops = []
        dex_interactions = []
        
        for tx in transactions:
            # Check for DEX interaction
            dex_info = self.identify_dex_interaction(tx)
            if dex_info:
                dex_interactions.append(dex_info)
            
            # Analyze as swap
            swap_info = self.analyze_swap(tx, wallet_address)
            if swap_info:
                swaps.append(swap_info)
            
            # Check for liquidity operations (add/remove)
            # This would require parsing specific instruction types
        
        print(f"DEX interactions found: {len(dex_interactions)}")
        print(f"Swaps analyzed: {len(swaps)}")
        
        # Categorize swaps
        sells = [s for s in swaps if s.get("direction") == "SELL_CRM"]
        buys = [s for s in swaps if s.get("direction") == "BUY_CRM"]
        other = [s for s in swaps if s.get("direction") == "OTHER"]
        
        print(f"  CRM Sells: {len(sells)}")
        print(f"  CRM Buys: {len(buys)}")
        print(f"  Other swaps: {len(other)}")
        
        # Build result
        result = {
            "wallet": wallet_key,
            "address": wallet_address,
            "export_timestamp": datetime.now().isoformat(),
            "total_transactions": len(transactions),
            "dex_interactions_count": len(dex_interactions),
            "swaps_count": len(swaps),
            "swaps": {
                "all": swaps,
                "sells": sells,
                "buys": buys,
                "other": other
            },
            "liquidity_operations": liquidity_ops,
            "dex_interactions": dex_interactions
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"DEX_{wallet_key}_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\nSaved to: {filename}")
        
        # Also save swaps as CSV for easy analysis
        if swaps:
            csv_filename = f"DEX_{wallet_key}_{timestamp}_swaps.csv"
            with open(csv_filename, "w", newline="") as f:
                if swaps:
                    writer = csv.DictWriter(f, fieldnames=swaps[0].keys())
                    writer.writeheader()
                    writer.writerows(swaps)
            print(f"Saved swaps CSV to: {csv_filename}")
        
        return result


def main():
    parser = argparse.ArgumentParser(
        description="Export DEX transaction history for forensic analysis"
    )
    parser.add_argument(
        "--wallet",
        help="Specific wallet key to export"
    )
    parser.add_argument(
        "--wallet-address",
        help="Direct wallet address (if not in registry)"
    )
    parser.add_argument(
        "--all-network-wallets",
        action="store_true",
        help="Export all known network wallets"
    )
    parser.add_argument(
        "--all-dump-wallets",
        action="store_true",
        help="Export only confirmed dump wallets"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Helius API key"
    )
    parser.add_argument(
        "--list-wallets",
        action="store_true",
        help="List known network wallets"
    )
    
    args = parser.parse_args()
    
    if args.list_wallets:
        print("\nKnown Network Wallets:")
        print("="*60)
        for category, wallets in NETWORK_WALLETS.items():
            print(f"\n{category.upper()}:")
            for key, address in wallets.items():
                print(f"  {key}: {address}")
        print("\n" + "="*60)
        return
    
    exporter = DEXTransactionExporter(args.api_key)
    
    wallets_to_export = []
    
    if args.all_network_wallets:
        for category in NETWORK_WALLETS.values():
            wallets_to_export.extend(category.items())
    
    elif args.all_dump_wallets:
        wallets_to_export.extend(NETWORK_WALLETS["confirmed_dumps"].items())
    
    elif args.wallet and args.wallet_address:
        wallets_to_export.append((args.wallet, args.wallet_address))
    
    elif args.wallet:
        # Look up in registry
        found = False
        for category in NETWORK_WALLETS.values():
            if args.wallet in category:
                wallets_to_export.append((args.wallet, category[args.wallet]))
                found = True
                break
        if not found:
            print(f"Error: Wallet '{args.wallet}' not found in registry")
            print("Use --wallet-address to specify address directly")
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\nError: Must specify --wallet, --all-network-wallets, or --all-dump-wallets")
        sys.exit(1)
    
    print(f"\nExporting DEX history for {len(wallets_to_export)} wallet(s)...")
    
    results = []
    for wallet_key, wallet_address in wallets_to_export:
        result = exporter.export_wallet_dex_history(wallet_key, wallet_address)
        results.append(result)
    
    # Save combined report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_file = f"DEX_ALL_WALLETS_{timestamp}.json"
    with open(combined_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"Combined report saved to: {combined_file}")
    print(f"{'='*60}")
    
    # Print summary
    total_swaps = sum(r.get("swaps_count", 0) for r in results)
    total_sells = sum(len(r.get("swaps", {}).get("sells", [])) for r in results)
    
    print(f"\nSummary:")
    print(f"  Wallets analyzed: {len(results)}")
    print(f"  Total swaps: {total_swaps}")
    print(f"  CRM sells: {total_sells}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
