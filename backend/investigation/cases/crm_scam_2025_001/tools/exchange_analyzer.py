#!/usr/bin/env python3
"""
CRM Investigation - Exchange Deposit Analyzer
============================================

Identifies exchange deposits from tracked wallets to trace where
funds were cashed out. Critical for asset recovery.

Uses known exchange wallet addresses and transaction patterns.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set


class ExchangeDepositAnalyzer:
    """
    Analyzes blockchain transactions to identify exchange deposits.
    """
    
    # Known exchange deposit addresses (hot wallets)
    KNOWN_EXCHANGES = {
        "binance": {
            "name": "Binance",
            "addresses": [
                "3HNf3",
                "3L9Q5",
            ],
            "patterns": ["binance", "bnb"]
        },
        "coinbase": {
            "name": "Coinbase",
            "addresses": [],
            "patterns": ["coinbase"]
        },
        "kraken": {
            "name": "Kraken",
            "addresses": [],
            "patterns": ["kraken"]
        },
        "ftx": {
            "name": "FTX (defunct)",
            "addresses": [],
            "patterns": ["ftx"]
        },
        "kucoin": {
            "name": "KuCoin",
            "addresses": [],
            "patterns": ["kucoin"]
        },
        "okx": {
            "name": "OKX",
            "addresses": [],
            "patterns": ["okx", "okex"]
        },
        "bybit": {
            "name": "Bybit",
            "addresses": [],
            "patterns": ["bybit"]
        },
        "jupiter": {
            "name": "Jupiter DEX Aggregator",
            "addresses": [
                "JUP6LkbZbjS1jKKwapdHNy74zcjn3T",
                "JUP4Bg",
            ],
            "patterns": ["jupiter", "jup"]
        },
        "raydium": {
            "name": "Raydium DEX",
            "addresses": [
                "675kPX9",
                "5Q544fK",
            ],
            "patterns": ["raydium", "rayd"]
        }
    }
    
    # Wallets to analyze for exchange deposits
    TARGET_WALLETS = [
        "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",  # Tier 1
        "BMq4XUa3rJJNkjXbJDpMFdSmPjvz5f9w4TvYFGADVkX5",  # Tier 2
        "HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi",  # Tier 3
        "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",  # Tier 4
        "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL",  # Tier 5 (victim)
        "7GsFEUPC9ZWMRb3wXsyrW33MP3Q6Jb8MpMjf2y1exC9y",  # SHIFT dumper
    ]
    
    def __init__(self, 
                 evidence_dir: str = "/root/crm_investigation/evidence",
                 output_path: str = "/root/crm_investigation/evidence/exchange_analysis.json"):
        self.evidence_dir = Path(evidence_dir)
        self.output_path = output_path
        self.deposits_found = []
        
    def scan_transaction_csvs(self) -> List[Dict]:
        """Scan transaction CSVs for exchange deposit patterns"""
        csv_dir = self.evidence_dir / "transaction_csvs"
        deposits = []
        
        if not csv_dir.exists():
            print(f"CSV directory not found: {csv_dir}")
            return deposits
        
        csv_files = list(csv_dir.glob("*.csv"))
        print(f"Scanning {len(csv_files)} transaction CSV files...")
        
        for csv_file in csv_files:
            try:
                with open(csv_file) as f:
                    lines = f.readlines()
                    
                # Check each line for exchange addresses
                for i, line in enumerate(lines[:1000]):  # Limit for performance
                    for exchange_id, exchange_info in self.KNOWN_EXCHANGES.items():
                        # Check known addresses
                        for addr in exchange_info["addresses"]:
                            if addr in line:
                                deposits.append({
                                    "file": csv_file.name,
                                    "line": i,
                                    "exchange": exchange_info["name"],
                                    "address_found": addr,
                                    "context": line[:200]
                                })
                                
                        # Check patterns
                        for pattern in exchange_info["patterns"]:
                            if pattern.lower() in line.lower():
                                deposits.append({
                                    "file": csv_file.name,
                                    "line": i,
                                    "exchange": exchange_info["name"],
                                    "pattern_found": pattern,
                                    "context": line[:200]
                                })
                                
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
        
        return deposits
    
    def analyze_deposit_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze patterns in potential exchange deposits"""
        analysis = {
            "total_potential_deposits": len(transactions),
            "by_exchange": {},
            "by_source_wallet": {},
            "amounts_usd": [],
            "time_pattern": []
        }
        
        for tx in transactions:
            exchange = tx.get("exchange", "Unknown")
            if exchange not in analysis["by_exchange"]:
                analysis["by_exchange"][exchange] = []
            analysis["by_exchange"][exchange].append(tx)
            
            # Try to extract amount
            context = tx.get("context", "")
            if "USDC" in context or "USD" in context:
                # Rough extraction
                import re
                amounts = re.findall(r'\$?[\d,]+\.?\d*', context)
                if amounts:
                    try:
                        amount = float(amounts[0].replace(',', '').replace('$', ''))
                        if 0 < amount < 10000000:  # Sanity check
                            analysis["amounts_usd"].append(amount)
                    except:
                        pass
        
        return analysis
    
    def generate_exchange_report(self) -> str:
        """Generate exchange deposit analysis report"""
        # Scan for deposits
        deposits = self.scan_transaction_csvs()
        analysis = self.analyze_deposit_patterns(deposits)
        
        # Calculate totals
        total_amount = sum(analysis["amounts_usd"])
        
        report = f"""
EXCHANGE DEPOSIT ANALYSIS REPORT
=================================
Generated: {datetime.now().isoformat()}
Case: CRM-SCAM-2025-001

EXECUTIVE SUMMARY
-----------------
Potential Exchange Deposits Found: {analysis['total_potential_deposits']}
Estimated Amount Traced: ${total_amount:,.2f}
Target Recovery Amount: $886,597+

BY EXCHANGE
-----------
"""
        
        for exchange, txs in analysis["by_exchange"].items():
            report += f"  {exchange}: {len(txs)} potential deposits\n"
        
        report += f"""
TARGET WALLETS ANALYZED
-----------------------
"""
        
        for wallet in self.TARGET_WALLETS:
            tier = "Tier 1 (Root)" if "AFXiga" in wallet else \
                   "Tier 2 (Bridge)" if "BMq4X" in wallet else \
                   "Tier 3 (Coord)" if "HxyXA" in wallet else \
                   "Tier 4 (Distro)" if "8eVZa" in wallet else \
                   "Tier 5 (Victim)" if "7abBm" in wallet else \
                   "SHIFT Dumper"
            report += f"  {wallet[:20]}... - {tier}\n"
        
        report += f"""
RECOMMENDATIONS FOR ASSET RECOVERY
-----------------------------------
1. Emergency Freeze Orders
   - Target: All Tier 1-4 wallets
   - Priority: Binance, Coinbase, Kraken (regulated, responsive)
   
2. Subpoena Strategy
   - Subpoena KYC records for deposits linked to target wallets
   - Request withdrawal addresses and bank account links
   - Timeline: Urgent (funds may be moving)
   
3. Cross-Exchange Analysis
   - Track if same KYC used across multiple exchanges
   - Identify fiat off-ramp points
   
4. DEX Considerations
   - Jupiter/Raydium non-custodial (no KYC)
   - Focus on downstream CEX deposits from DEX swaps

NEXT STEPS
----------
[ ] File emergency freeze requests with major exchanges
[ ] Coordinate with FBI IC3 for international exchange cooperation
[ ] Request blockchain analysis from specialized firms (Chainalysis, TRM Labs)
[ ] Prepare victim restitution claims

NOTE: This analysis uses pattern matching on available CSV data.
For definitive exchange identification, direct API queries to
blockchain analytics providers (Helius, QuickNode, Alchemy) recommended.
"""
        
        return report
    
    def save_report(self):
        """Save analysis report to file"""
        report = self.generate_exchange_report()
        
        output_file = Path(self.output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"Exchange analysis report saved: {output_file}")
        return str(output_file)


# ==================== CLI ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CRM Exchange Deposit Analyzer")
    parser.add_argument("--analyze", action="store_true", help="Analyze exchange deposits")
    parser.add_argument("--report", action="store_true", help="Generate report")
    
    args = parser.parse_args()
    
    analyzer = ExchangeDepositAnalyzer()
    
    if args.analyze or args.report or not any([args.analyze, args.report]):
        report_path = analyzer.save_report()
        print(f"\nReport saved: {report_path}")
        print("\n" + analyzer.generate_exchange_report())
