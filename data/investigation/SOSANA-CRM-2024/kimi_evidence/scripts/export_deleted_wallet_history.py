#!/usr/bin/env python3
"""
Export Deleted Wallet Transaction History
=========================================
Forensic tool to export pre-deletion transaction history from deleted dump wallets.
Uses Helius API to reconstruct fund flows for law enforcement.

Usage:
    python export_deleted_wallet_history.py --wallet HLnpSz9h --api-key YOUR_KEY
    python export_deleted_wallet_history.py --all --api-key YOUR_KEY
"""

import argparse
import json
import requests
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import csv

# Deleted wallet registry from forensic analysis
DELETED_WALLETS = {
    "HLnpSz9h_first": {
        "address": "HLnpSz9h",  # First instance - deleted
        "status": "CONFIRMED_DUMP_DELETED",
        "peak_crm": "50M+",
        "deletion_date": "2026-03-15",  # Estimated
        "notes": "First major dump wallet, deleted after extraction"
    },
    "6LXutJvK": {
        "address": "6LXutJvK",
        "status": "CONFIRMED_DUMP_DELETED",
        "peak_crm": "UNKNOWN",
        "deletion_date": "2026-03-20",  # Estimated
        "notes": "Deleted dump wallet"
    },
    "7uCYuvPb": {
        "address": "7uCYuvPb",
        "status": "CONFIRMED_DUMP_DELETED",
        "peak_crm": "UNKNOWN",
        "deletion_date": "2026-03-22",  # Estimated
        "notes": "Deleted dump wallet"
    },
    "HGS4DyyX": {
        "address": "HGS4DyyX",
        "status": "CONFIRMED_DUMP_DELETED",
        "peak_crm": "UNKNOWN",
        "deletion_date": "2026-03-25",  # Estimated
        "notes": "Deleted dump wallet"
    }
}

# Known fee collector for cross-reference
FEE_COLLECTOR = "GVC9Zvh3"

# Bridge contracts for detection
BRIDGE_CONTRACTS = {
    "wormhole_token": "wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb",
    "wormhole_nft": "WnFt12ZrnzZrFZkt2xsNsaNWoQribnu6Q5hX1RY8VM",
    "allbridge_classic": "BrdgN2RPzEMjSngpWPRr6zRvobgsADWXZLg7R9LLMQe",
    "synapse": "SYNAPSE_CONTRACT"  # Update with actual address
}

# CEX hot wallets (to be populated)
CEX_HOT_WALLETS = {
    "mexc": [],
    "bybit": [],
    "gateio": [],
    "binance": [],
    "coinbase": []
}


class HeliusExporter:
    """Export transaction history from Solana wallets using Helius API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.helius.xyz/v0"
    
    def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """
        Fetch transaction history for a wallet address.
        
        Args:
            address: Solana wallet address
            limit: Maximum transactions to fetch (max 100 per request)
            
        Returns:
            List of transaction dictionaries
        """
        url = f"{self.base_url}/addresses/{address}/transactions"
        params = {"api-key": self.api_key, "limit": limit}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions for {address}: {e}")
            return []
    
    def get_enhanced_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """
        Fetch enhanced transaction history with parsed data.
        
        Args:
            address: Solana wallet address
            limit: Maximum transactions to fetch
            
        Returns:
            List of enhanced transaction dictionaries
        """
        url = f"{self.base_url}/addresses/{address}/transactions"
        params = {
            "api-key": self.api_key,
            "limit": limit,
            "type": "enhanced"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching enhanced transactions for {address}: {e}")
            return []
    
    def analyze_outgoing_transfers(self, transactions: List[Dict], wallet_address: str) -> List[Dict]:
        """
        Analyze transactions to identify outgoing transfers.
        
        Args:
            transactions: List of transaction dictionaries
            wallet_address: Source wallet address
            
        Returns:
            List of outgoing transfer records
        """
        outgoing = []
        
        for tx in transactions:
            tx_hash = tx.get("signature", "UNKNOWN")
            timestamp = tx.get("timestamp", 0)
            date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp else "UNKNOWN"
            
            # Check for native SOL transfers
            if "nativeTransfers" in tx:
                for transfer in tx["nativeTransfers"]:
                    if transfer.get("fromUserAccount") == wallet_address:
                        outgoing.append({
                            "tx_hash": tx_hash,
                            "timestamp": timestamp,
                            "date": date_str,
                            "type": "SOL_TRANSFER",
                            "amount": transfer.get("amount", 0) / 1e9,  # Convert lamports to SOL
                            "token": "SOL",
                            "to": transfer.get("toUserAccount", "UNKNOWN"),
                            "from": wallet_address
                        })
            
            # Check for token transfers
            if "tokenTransfers" in tx:
                for transfer in tx["tokenTransfers"]:
                    if transfer.get("fromUserAccount") == wallet_address:
                        token = transfer.get("mint", "UNKNOWN")
                        amount = transfer.get("tokenAmount", 0)
                        
                        # Check if it's CRM
                        if token == "CRM_TOKEN_MINT":  # Update with actual CRM mint
                            token_symbol = "CRM"
                        else:
                            token_symbol = token[:8] + "..."
                        
                        outgoing.append({
                            "tx_hash": tx_hash,
                            "timestamp": timestamp,
                            "date": date_str,
                            "type": "TOKEN_TRANSFER",
                            "amount": amount,
                            "token": token_symbol,
                            "to": transfer.get("toUserAccount", "UNKNOWN"),
                            "from": wallet_address
                        })
            
            # Check for swaps (Raydium/Meteora/Jupiter)
            if "events" in tx and "swap" in tx["events"]:
                swap = tx["events"]["swap"]
                outgoing.append({
                    "tx_hash": tx_hash,
                    "timestamp": timestamp,
                    "date": date_str,
                    "type": "SWAP",
                    "amount": swap.get("tokenInputs", [{}])[0].get("tokenAmount", 0),
                    "token": "SWAP",
                    "to": swap.get("tokenOutputs", [{}])[0].get("mint", "UNKNOWN"),
                    "from": wallet_address,
                    "details": swap
                })
        
        return outgoing
    
    def classify_recipient(self, recipient: str) -> str:
        """
        Classify recipient address type.
        
        Args:
            recipient: Recipient wallet address
            
        Returns:
            Classification string
        """
        # Check if it's the known fee collector
        if FEE_COLLECTOR in recipient:
            return "FEE_COLLECTOR"
        
        # Check bridge contracts
        for bridge_name, contract in BRIDGE_CONTRACTS.items():
            if contract in recipient:
                return f"BRIDGE_{bridge_name.upper()}"
        
        # Check CEX hot wallets
        for cex, wallets in CEX_HOT_WALLETS.items():
            if recipient in wallets:
                return f"CEX_{cex.upper()}"
        
        # Check if it's a known program
        if recipient in [
            "11111111111111111111111111111111",  # System program
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
        ]:
            return "SYSTEM_PROGRAM"
        
        return "UNKNOWN"
    
    def export_wallet_history(self, wallet_key: str, output_format: str = "json") -> Dict[str, Any]:
        """
        Export complete transaction history for a deleted wallet.
        
        Args:
            wallet_key: Key from DELETED_WALLETS registry
            output_format: Output format (json, csv)
            
        Returns:
            Export results dictionary
        """
        wallet_info = DELETED_WALLETS.get(wallet_key)
        if not wallet_info:
            return {"error": f"Unknown wallet key: {wallet_key}"}
        
        address = wallet_info["address"]
        print(f"\n{'='*60}")
        print(f"Exporting: {wallet_key}")
        print(f"Address: {address}")
        print(f"Status: {wallet_info['status']}")
        print(f"{'='*60}\n")
        
        # Fetch transactions
        print("Fetching transactions from Helius...")
        transactions = self.get_enhanced_transactions(address, limit=100)
        
        if not transactions:
            return {
                "wallet": wallet_key,
                "address": address,
                "error": "No transactions found or API error",
                "transactions": [],
                "outgoing_transfers": []
            }
        
        print(f"Found {len(transactions)} transactions")
        
        # Analyze outgoing transfers
        print("Analyzing outgoing transfers...")
        outgoing = self.analyze_outgoing_transfers(transactions, address)
        print(f"Found {len(outgoing)} outgoing transfers")
        
        # Classify recipients
        for transfer in outgoing:
            transfer["recipient_type"] = self.classify_recipient(transfer["to"])
        
        # Calculate totals
        total_sol = sum(t["amount"] for t in outgoing if t["token"] == "SOL")
        total_crm = sum(t["amount"] for t in outgoing if t["token"] == "CRM")
        
        # Build result
        result = {
            "wallet": wallet_key,
            "address": address,
            "wallet_info": wallet_info,
            "export_timestamp": datetime.now().isoformat(),
            "total_transactions": len(transactions),
            "total_outgoing_transfers": len(outgoing),
            "total_sol_transferred": total_sol,
            "total_crm_transferred": total_crm,
            "transactions": transactions,
            "outgoing_transfers": outgoing
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{wallet_key}_{timestamp}"
        
        if output_format == "json":
            filename = f"{filename_base}.json"
            with open(filename, "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"Saved to: {filename}")
            
        elif output_format == "csv":
            # Save transfers as CSV
            filename = f"{filename_base}_transfers.csv"
            if outgoing:
                with open(filename, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=outgoing[0].keys())
                    writer.writeheader()
                    writer.writerows(outgoing)
                print(f"Saved transfers to: {filename}")
            
            # Also save full result as JSON
            json_filename = f"{filename_base}.json"
            with open(json_filename, "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"Saved full data to: {json_filename}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("EXPORT SUMMARY")
        print(f"{'='*60}")
        print(f"Total Transactions: {len(transactions)}")
        print(f"Outgoing Transfers: {len(outgoing)}")
        print(f"Total SOL Transferred: {total_sol:.4f}")
        print(f"Total CRM Transferred: {total_crm:,.2f}")
        print(f"\nRecipient Breakdown:")
        
        recipient_types = {}
        for t in outgoing:
            rtype = t["recipient_type"]
            recipient_types[rtype] = recipient_types.get(rtype, 0) + 1
        
        for rtype, count in recipient_types.items():
            print(f"  {rtype}: {count}")
        
        print(f"{'='*60}\n")
        
        return result


def main():
    parser = argparse.ArgumentParser(
        description="Export deleted wallet transaction history for forensic analysis"
    )
    parser.add_argument(
        "--wallet",
        choices=list(DELETED_WALLETS.keys()),
        help="Specific wallet to export"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all deleted wallets"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Helius API key"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List known deleted wallets"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("\nKnown Deleted Wallets:")
        print("="*60)
        for key, info in DELETED_WALLETS.items():
            print(f"\n{key}:")
            print(f"  Address: {info['address']}")
            print(f"  Status: {info['status']}")
            print(f"  Peak CRM: {info['peak_crm']}")
            print(f"  Deletion Date: {info['deletion_date']}")
            print(f"  Notes: {info['notes']}")
        print("\n" + "="*60)
        return
    
    if not args.wallet and not args.all:
        parser.print_help()
        print("\nError: Must specify --wallet or --all")
        sys.exit(1)
    
    exporter = HeliusExporter(args.api_key)
    
    if args.all:
        print(f"Exporting all {len(DELETED_WALLETS)} deleted wallets...")
        results = {}
        for wallet_key in DELETED_WALLETS.keys():
            result = exporter.export_wallet_history(wallet_key, args.format)
            results[wallet_key] = result
        
        # Save combined report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_file = f"ALL_DELETED_WALLETS_{timestamp}.json"
        with open(combined_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nCombined report saved to: {combined_file}")
        
    else:
        exporter.export_wallet_history(args.wallet, args.format)


if __name__ == "__main__":
    main()
