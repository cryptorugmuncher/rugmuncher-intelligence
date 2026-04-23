#!/usr/bin/env python3
"""
Cross-Project Wallet Analysis
=============================
Analyze network wallets across multiple token projects to identify:
- Multi-project dumping operations
- Coordinated cross-project manipulation
- Shared infrastructure across scams

Usage:
    python cross_project_analysis.py --wallet HLnpSz9h --api-key YOUR_KEY
    python cross_project_analysis.py --all-network-wallets --api-key YOUR_KEY
"""

import argparse
import json
import requests
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional

# Network wallets to analyze across projects
NETWORK_WALLETS = {
    "HLnpSz9h_first": "HLnpSz9h",
    "6LXutJvK": "6LXutJvK",
    "7uCYuvPb": "7uCYuvPb",
    "HGS4DyyX": "HGS4DyyX",
    "DLHnb1yt": "DLHnb1yt",
    "GVC9Zvh3": "GVC9Zvh3",
    "ASTyfSima": "ASTyfSima",
    "H8sMJSCQ": "H8sMJSCQ"
}

# Known scam token patterns (for cross-reference)
SUSPICIOUS_TOKEN_PATTERNS = [
    "high_holder_concentration",  # Top 10 holders >50%
    "rapid_price_decline",        # >90% drop in 30 days
    "liquidity_removal",          # LP tokens withdrawn
    "team_dumping",               # Team wallets selling
    "honeypot",                   # Unable to sell
]

# Major token list for reference
MAJOR_TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
}


class CrossProjectAnalyzer:
    """Analyze wallets across multiple token projects."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.helius.xyz/v0"
    
    def get_token_balances(self, address: str) -> Dict[str, Any]:
        """Get all token balances for a wallet."""
        url = f"{self.base_url}/addresses/{address}/balances"
        
        try:
            response = requests.get(
                url,
                params={"api-key": self.api_key},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching balances: {e}")
            return {}
    
    def get_token_metadata(self, mint: str) -> Dict[str, Any]:
        """Get metadata for a token."""
        url = f"{self.base_url}/tokens"
        
        try:
            response = requests.post(
                url,
                params={"api-key": self.api_key},
                json={"mints": [mint]},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching token metadata: {e}")
            return {}
    
    def analyze_wallet_tokens(self, wallet_address: str) -> Dict[str, Any]:
        """
        Analyze all tokens held by a wallet.
        
        Returns:
            Dictionary with token analysis including:
            - All tokens held
            - Token metadata
            - Suspicious indicators
            - Cross-project activity
        """
        print(f"\nAnalyzing tokens for {wallet_address}...")
        
        balances = self.get_token_balances(wallet_address)
        
        if not balances:
            return {"error": "No balance data available"}
        
        native_balance = balances.get("nativeBalance", 0) / 1e9
        tokens = balances.get("tokens", [])
        
        token_analysis = []
        suspicious_tokens = []
        major_tokens = []
        unknown_tokens = []
        
        for token in tokens:
            mint = token.get("mint", "UNKNOWN")
            amount = token.get("amount", 0)
            decimals = token.get("decimals", 0)
            
            # Get metadata
            metadata = self.get_token_metadata(mint)
            
            token_info = {
                "mint": mint,
                "amount": amount,
                "decimals": decimals,
                "metadata": metadata,
                "is_major": mint in MAJOR_TOKENS.values(),
                "is_crm": "CRM" in metadata.get("symbol", "") if metadata else False
            }
            
            token_analysis.append(token_info)
            
            # Categorize
            if token_info["is_major"]:
                major_tokens.append(token_info)
            elif token_info["is_crm"]:
                # CRM is our primary focus
                pass
            else:
                unknown_tokens.append(token_info)
                
                # Check for suspicious indicators
                if self._is_suspicious_token(token_info):
                    suspicious_tokens.append(token_info)
        
        return {
            "wallet": wallet_address,
            "native_sol": native_balance,
            "total_tokens": len(tokens),
            "token_analysis": token_analysis,
            "major_tokens": major_tokens,
            "suspicious_tokens": suspicious_tokens,
            "unknown_tokens": unknown_tokens,
            "cross_project_indicators": len(unknown_tokens) > 5  # Holding many obscure tokens
        }
    
    def _is_suspicious_token(self, token_info: Dict) -> bool:
        """Check if a token has suspicious characteristics."""
        metadata = token_info.get("metadata", {})
        
        # Check for red flags
        red_flags = 0
        
        # No metadata
        if not metadata:
            red_flags += 1
        
        # Very low holder count
        if metadata.get("holderCount", 1000) < 100:
            red_flags += 1
        
        # Suspicious name/pattern
        name = metadata.get("name", "").lower()
        symbol = metadata.get("symbol", "").lower()
        suspicious_keywords = ["elon", "moon", "safe", "doge", "shib", "pepe", "inu"]
        if any(kw in name or kw in symbol for kw in suspicious_keywords):
            red_flags += 0.5
        
        # Very low liquidity
        if metadata.get("liquidityUsd", 10000) < 1000:
            red_flags += 1
        
        return red_flags >= 2
    
    def get_transaction_history(self, address: str, limit: int = 100) -> List[Dict]:
        """Get transaction history for a wallet."""
        url = f"{self.base_url}/addresses/{address}/transactions"
        
        try:
            response = requests.get(
                url,
                params={"api-key": self.api_key, "limit": limit},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def analyze_interacted_tokens(self, wallet_address: str) -> Dict[str, Any]:
        """
        Analyze all tokens the wallet has interacted with (not just current holdings).
        
        This reveals projects the wallet was previously involved in.
        """
        print(f"Analyzing transaction history for {wallet_address}...")
        
        transactions = self.get_transaction_history(wallet_address, limit=100)
        
        if not transactions:
            return {"error": "No transaction data available"}
        
        # Extract all token mints from transactions
        interacted_tokens = set()
        token_interactions = defaultdict(lambda: {
            "interactions": 0,
            "first_seen": None,
            "last_seen": None,
            "transactions": []
        })
        
        for tx in transactions:
            tx_hash = tx.get("signature", "UNKNOWN")
            timestamp = tx.get("timestamp", 0)
            
            # Check token transfers
            if "tokenTransfers" in tx:
                for transfer in tx["tokenTransfers"]:
                    mint = transfer.get("mint", "")
                    if mint and mint not in MAJOR_TOKENS.values():
                        interacted_tokens.add(mint)
                        
                        token_interactions[mint]["interactions"] += 1
                        token_interactions[mint]["transactions"].append(tx_hash)
                        
                        if not token_interactions[mint]["first_seen"] or timestamp < token_interactions[mint]["first_seen"]:
                            token_interactions[mint]["first_seen"] = timestamp
                        
                        if not token_interactions[mint]["last_seen"] or timestamp > token_interactions[mint]["last_seen"]:
                            token_interactions[mint]["last_seen"] = timestamp
        
        # Get metadata for interacted tokens
        token_details = []
        for mint in interacted_tokens:
            metadata = self.get_token_metadata(mint)
            interactions = token_interactions[mint]
            
            token_details.append({
                "mint": mint,
                "metadata": metadata,
                "interactions": interactions["interactions"],
                "first_seen": datetime.fromtimestamp(interactions["first_seen"]).isoformat() if interactions["first_seen"] else None,
                "last_seen": datetime.fromtimestamp(interactions["last_seen"]).isoformat() if interactions["last_seen"] else None,
                "transactions": interactions["transactions"]
            })
        
        # Sort by interaction count
        token_details.sort(key=lambda x: x["interactions"], reverse=True)
        
        return {
            "wallet": wallet_address,
            "total_interacted_tokens": len(interacted_tokens),
            "token_details": token_details[:20],  # Top 20
            "high_activity_tokens": [t for t in token_details if t["interactions"] >= 5]
        }
    
    def find_shared_tokens(self, wallet_analyses: List[Dict]) -> Dict[str, Any]:
        """
        Find tokens that multiple network wallets have interacted with.
        
        This indicates coordinated multi-project activity.
        """
        token_to_wallets = defaultdict(list)
        
        for analysis in wallet_analyses:
            wallet = analysis.get("wallet", "UNKNOWN")
            
            # From current holdings
            for token in analysis.get("token_analysis", []):
                mint = token.get("mint", "")
                if mint:
                    token_to_wallets[mint].append(wallet)
            
            # From transaction history
            interacted = analysis.get("interacted_tokens", {})
            for token in interacted.get("token_details", []):
                mint = token.get("mint", "")
                if mint:
                    token_to_wallets[mint].append(wallet)
        
        # Find tokens shared by multiple wallets
        shared_tokens = {
            mint: wallets
            for mint, wallets in token_to_wallets.items()
            if len(set(wallets)) >= 2  # 2+ unique wallets
        }
        
        return {
            "shared_tokens": shared_tokens,
            "shared_token_count": len(shared_tokens),
            "coordination_indicator": len(shared_tokens) >= 3,
            "evidence_tier": "TIER_1" if len(shared_tokens) >= 5 else "TIER_2" if len(shared_tokens) >= 3 else "TIER_3"
        }
    
    def analyze_wallet(self, wallet_key: str, wallet_address: str) -> Dict[str, Any]:
        """Perform complete cross-project analysis for a wallet."""
        print(f"\n{'='*60}")
        print(f"Cross-Project Analysis: {wallet_key}")
        print(f"Address: {wallet_address}")
        print(f"{'='*60}")
        
        # Current token holdings
        token_analysis = self.analyze_wallet_tokens(wallet_address)
        
        # Transaction history (past projects)
        interacted = self.analyze_interacted_tokens(wallet_address)
        
        # Combine
        result = {
            "wallet_key": wallet_key,
            "wallet_address": wallet_address,
            "analysis_timestamp": datetime.now().isoformat(),
            "current_holdings": token_analysis,
            "interacted_tokens": interacted,
            "cross_project_indicators": {
                "many_obscure_tokens": len(token_analysis.get("unknown_tokens", [])) > 5,
                "high_token_interaction_count": interacted.get("total_interacted_tokens", 0) > 20,
                "suspicious_token_holdings": len(token_analysis.get("suspicious_tokens", [])) > 0
            }
        }
        
        # Print summary
        print(f"\nSummary:")
        print(f"  Native SOL: {token_analysis.get('native_sol', 0):.4f}")
        print(f"  Current tokens: {token_analysis.get('total_tokens', 0)}")
        print(f"  Interacted tokens (history): {interacted.get('total_interacted_tokens', 0)}")
        print(f"  Suspicious tokens: {len(token_analysis.get('suspicious_tokens', []))}")
        print(f"  High-activity tokens: {len(interacted.get('high_activity_tokens', []))}")
        
        return result


def main():
    parser = argparse.ArgumentParser(
        description="Analyze network wallets across multiple token projects"
    )
    parser.add_argument(
        "--wallet",
        help="Specific wallet key to analyze"
    )
    parser.add_argument(
        "--wallet-address",
        help="Direct wallet address"
    )
    parser.add_argument(
        "--all-network-wallets",
        action="store_true",
        help="Analyze all known network wallets"
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
    parser.add_argument(
        "--output",
        help="Output file for analysis report"
    )
    
    args = parser.parse_args()
    
    if args.list_wallets:
        print("\nKnown Network Wallets:")
        print("="*60)
        for key, address in NETWORK_WALLETS.items():
            print(f"  {key}: {address}")
        print("="*60)
        return
    
    analyzer = CrossProjectAnalyzer(args.api_key)
    
    wallets_to_analyze = []
    
    if args.all_network_wallets:
        wallets_to_analyze = list(NETWORK_WALLETS.items())
    elif args.wallet and args.wallet_address:
        wallets_to_analyze.append((args.wallet, args.wallet_address))
    elif args.wallet:
        if args.wallet in NETWORK_WALLETS:
            wallets_to_analyze.append((args.wallet, NETWORK_WALLETS[args.wallet]))
        else:
            print(f"Error: Wallet '{args.wallet}' not found in registry")
            sys.exit(1)
    else:
        parser.print_help()
        print("\nError: Must specify --wallet, --all-network-wallets, or --list-wallets")
        sys.exit(1)
    
    print(f"\nAnalyzing {len(wallets_to_analyze)} wallet(s) across projects...")
    
    analyses = []
    for wallet_key, wallet_address in wallets_to_analyze:
        analysis = analyzer.analyze_wallet(wallet_key, wallet_address)
        analyses.append(analysis)
    
    # Find shared tokens across wallets
    shared = analyzer.find_shared_tokens(analyses)
    
    # Combined report
    combined_report = {
        "analysis_timestamp": datetime.now().isoformat(),
        "wallets_analyzed": len(analyses),
        "individual_analyses": analyses,
        "cross_wallet_analysis": shared,
        "summary": {
            "total_wallets": len(analyses),
            "wallets_with_many_tokens": sum(1 for a in analyses if a["cross_project_indicators"]["many_obscure_tokens"]),
            "wallets_with_high_interaction": sum(1 for a in analyses if a["cross_project_indicators"]["high_token_interaction_count"]),
            "wallets_with_suspicious_tokens": sum(1 for a in analyses if a["cross_project_indicators"]["suspicious_token_holdings"]),
            "shared_tokens_across_wallets": shared.get("shared_token_count", 0),
            "coordination_detected": shared.get("coordination_indicator", False)
        }
    }
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        output_file = args.output
    else:
        output_file = f"CROSS_PROJECT_ANALYSIS_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(combined_report, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"Analysis complete! Report saved to: {output_file}")
    print(f"{'='*60}")
    print(f"\nCross-Project Summary:")
    print(f"  Wallets analyzed: {combined_report['summary']['total_wallets']}")
    print(f"  Wallets with many obscure tokens: {combined_report['summary']['wallets_with_many_tokens']}")
    print(f"  Wallets with high token interaction: {combined_report['summary']['wallets_with_high_interaction']}")
    print(f"  Wallets with suspicious tokens: {combined_report['summary']['wallets_with_suspicious_tokens']}")
    print(f"  Shared tokens across wallets: {combined_report['summary']['shared_tokens_across_wallets']}")
    print(f"  Coordination detected: {'YES' if combined_report['summary']['coordination_detected'] else 'NO'}")
    
    if shared.get("shared_tokens"):
        print(f"\n  Shared Tokens (indicating coordination):")
        for mint, wallets in list(shared["shared_tokens"].items())[:5]:
            print(f"    {mint[:20]}...: {len(set(wallets))} wallets")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
