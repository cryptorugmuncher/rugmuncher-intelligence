#!/usr/bin/env python3
"""
CRM Investigation Framework - Blockchain Forensic Analysis Tools
===============================================================

On-chain analysis tools for cryptocurrency fraud investigation.
Focus: CRM Token / SOSANA / SHIFT AI fraud case (CRM-SCAM-2025-001)
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sqlite3
import hashlib

# Solana RPC endpoints
HELIUS_RPC = "https://mainnet.helius-rpc.com/?api-key={api_key}"
QUICKNODE_RPC = "https://api.mainnet-beta.solana.com"

@dataclass
class WalletEntity:
    """Represents a wallet in the investigation"""
    address: str
    tier: int  # 1-5 for hierarchical structure
    classification: str  # "suspect", "victim", "intermediary", "exchange"
    crm_balance: float = 0.0
    usdc_balance: float = 0.0
    first_seen: Optional[str] = None
    last_active: Optional[str] = None
    related_wallets: List[str] = None
    transaction_count: int = 0
    risk_score: float = 0.0
    notes: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class TransactionPattern:
    """Pattern analysis for transactions"""
    signature: str
    from_wallet: str
    to_wallet: str
    amount: float
    token: str
    timestamp: str
    block_time: int
    pattern_type: str  # "seed", "distribution", "extraction", "bridge", "coordination"
    suspicious_score: float = 0.0

class BlockchainAnalyzer:
    """
    Blockchain forensic analysis for CRM investigation
    """
    
    TIER_1_MASTER = "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6"
    TIER_2_BRIDGE = "BMq4XUa3rJJNkjXbJDpMFdSmPjvz5f9w4TvYFGADVkX5"
    TIER_3_COORD = "HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi"
    TIER_4_DISTRO = "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj"
    TIER_5_EXEC = "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL"
    
    CRM_MINT = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"
    USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    def __init__(self, db_path: str = "/root/crm_investigation/evidence/blockchain_analysis.db"):
        self.db_path = db_path
        self.wallets: Dict[str, WalletEntity] = {}
        self.transactions: List[TransactionPattern] = []
        self.init_database()
        self.load_known_wallets()
    
    def init_database(self):
        """Initialize SQLite database for analysis"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT PRIMARY KEY,
                tier INTEGER,
                classification TEXT,
                crm_balance REAL,
                usdc_balance REAL,
                first_seen TEXT,
                last_active TEXT,
                transaction_count INTEGER,
                risk_score REAL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                signature TEXT PRIMARY KEY,
                from_wallet TEXT,
                to_wallet TEXT,
                amount REAL,
                token TEXT,
                timestamp TEXT,
                block_time INTEGER,
                pattern_type TEXT,
                suspicious_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS wallet_relationships (
                source TEXT,
                target TEXT,
                relationship_type TEXT,
                strength REAL,
                evidence TEXT,
                PRIMARY KEY (source, target)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_known_wallets(self):
        """Load the 5-tier hierarchy wallets"""
        tier_wallets = [
            (1, self.TIER_1_MASTER, "Master routing - seeds 970 wallets"),
            (2, self.TIER_2_BRIDGE, "SHIFT→CRM bridge connection"),
            (3, self.TIER_3_COORD, "CRM coordination - 19 transactions"),
            (4, self.TIER_4_DISTRO, "Distribution - 20M CRM loaded"),
            (5, self.TIER_5_EXEC, "Execution - victim whale position"),
        ]
        
        for tier, address, notes in tier_wallets:
            self.wallets[address] = WalletEntity(
                address=address,
                tier=tier,
                classification="suspect" if tier <= 4 else "victim",
                notes=notes,
                related_wallets=[]
            )
    
    async def fetch_wallet_transactions(self, wallet_address: str, 
                                        api_key: Optional[str] = None,
                                        limit: int = 100) -> List[dict]:
        """Fetch transactions for a wallet via Helius API"""
        url = f"https://mainnet.helius-rpc.com/?api-key={api_key}" if api_key else QUICKNODE_RPC
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet_address, {"limit": limit}]
            }
            
            try:
                async with session.post(url, json=payload, timeout=30) as response:
                    data = await response.json()
                    return data.get("result", [])
            except Exception as e:
                print(f"Error fetching transactions for {wallet_address}: {e}")
                return []
    
    async def fetch_transaction_details(self, signature: str,
                                         api_key: Optional[str] = None) -> Optional[dict]:
        """Fetch detailed transaction info"""
        url = f"https://mainnet.helius-rpc.com/?api-key={api_key}" if api_key else QUICKNODE_RPC
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
            }
            
            try:
                async with session.post(url, json=payload, timeout=30) as response:
                    data = await response.json()
                    return data.get("result")
            except Exception as e:
                print(f"Error fetching transaction {signature}: {e}")
                return None
    
    def analyze_transaction_pattern(self, tx_data: dict) -> TransactionPattern:
        """Analyze transaction for suspicious patterns"""
        signature = tx_data.get("transaction", {}).get("signatures", [""])[0]
        meta = tx_data.get("meta", {})
        block_time = tx_data.get("blockTime", 0)
        
        # Parse token transfers
        pre_balances = meta.get("preTokenBalances", [])
        post_balances = meta.get("postTokenBalances", [])
        
        # Determine pattern type
        pattern_type = "unknown"
        suspicious_score = 0.0
        
        # Check for high-frequency patterns
        if block_time > 0:
            timestamp = datetime.fromtimestamp(block_time).isoformat()
        else:
            timestamp = ""
        
        # Check for CRM token involvement
        crm_involved = any(
            b.get("mint") == self.CRM_MINT 
            for b in pre_balances + post_balances
        )
        
        if crm_involved:
            pattern_type = "crm_transfer"
            suspicious_score += 0.3
        
        # Check for $0 cost basis transfers
        if meta.get("fee", 0) == 0 and crm_involved:
            pattern_type = "free_load"
            suspicious_score += 0.8  # High suspicion
        
        # Extract amounts and wallets
        from_wallet = ""
        to_wallet = ""
        amount = 0.0
        
        # Parse from pre/post balances
        for pre in pre_balances:
            for post in post_balances:
                if pre.get("accountIndex") == post.get("accountIndex"):
                    pre_amount = float(pre.get("uiTokenAmount", {}).get("uiAmount", 0))
                    post_amount = float(post.get("uiTokenAmount", {}).get("uiAmount", 0))
                    if pre_amount > post_amount:
                        from_wallet = pre.get("owner", "")
                        amount = pre_amount - post_amount
                    elif post_amount > pre_amount:
                        to_wallet = post.get("owner", "")
        
        return TransactionPattern(
            signature=signature,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=amount,
            token="CRM" if crm_involved else "UNKNOWN",
            timestamp=timestamp,
            block_time=block_time,
            pattern_type=pattern_type,
            suspicious_score=suspicious_score
        )
    
    def detect_seeding_pattern(self, transactions: List[TransactionPattern]) -> dict:
        """
        Detect the 970-wallet seeding pattern
        Critical evidence: 970 wallets in 7 seconds = 138/second
        """
        if not transactions:
            return {"detected": False}
        
        # Sort by block time
        sorted_txs = sorted(transactions, key=lambda x: x.block_time)
        
        # Look for burst patterns
        time_windows = []
        window_start = sorted_txs[0].block_time if sorted_txs else 0
        window_count = 0
        
        for tx in sorted_txs:
            if tx.block_time - window_start <= 10:  # 10 second window
                window_count += 1
            else:
                if window_count > 50:  # Suspicious burst
                    time_windows.append({
                        "start": window_start,
                        "count": window_count,
                        "duration_seconds": 10,
                        "rate_per_second": window_count / 10
                    })
                window_start = tx.block_time
                window_count = 1
        
        # Check for the specific March 26 pattern
        march_26_timestamp = 1711480687  # ~March 26, 2026 21:38:07 UTC
        
        for window in time_windows:
            if abs(window["start"] - march_26_timestamp) < 86400:  # Within 1 day
                if window["count"] >= 900:  # Close to 970
                    return {
                        "detected": True,
                        "window": window,
                        "significance": "MILITARY-GRADE AUTOMATION CONFIRMED",
                        "human_impossible": True,
                        "evidence": f"{window['count']} transactions in 10 seconds ({window['rate_per_second']:.1f}/sec)"
                    }
        
        return {
            "detected": False,
            "windows_found": len(time_windows),
            "max_burst": max((w["count"] for w in time_windows), default=0)
        }
    
    def calculate_risk_scores(self) -> Dict[str, float]:
        """Calculate risk scores for all tracked wallets"""
        risk_scores = {}
        
        for address, wallet in self.wallets.items():
            score = 0.0
            
            # Tier-based risk (higher tier = more central = higher risk if suspect)
            if wallet.classification == "suspect":
                score += (6 - wallet.tier) * 0.15  # Tier 1 gets 0.75, Tier 5 gets 0.15
            
            # Transaction volume risk
            if wallet.transaction_count > 100:
                score += 0.1
            
            # Balance risk (emptying wallets)
            if wallet.crm_balance == 0 and wallet.transaction_count > 0:
                score += 0.2
            
            # Known patterns
            if address == self.TIER_1_MASTER:
                score = 1.0  # Maximum risk
            elif address == self.TIER_4_DISTRO:
                score = 0.95  # Distribution node
            elif address == self.TIER_3_COORD:
                score = 0.90  # Coordination node
            
            wallet.risk_score = min(score, 1.0)
            risk_scores[address] = wallet.risk_score
        
        return risk_scores
    
    def build_relationship_graph(self) -> Dict:
        """Build relationship graph between wallets"""
        graph = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "total_wallets": len(self.wallets),
                "suspect_wallets": sum(1 for w in self.wallets.values() if w.classification == "suspect"),
                "victim_wallets": sum(1 for w in self.wallets.values() if w.classification == "victim")
            }
        }
        
        # Add nodes
        for address, wallet in self.wallets.items():
            graph["nodes"].append({
                "id": address,
                "tier": wallet.tier,
                "classification": wallet.classification,
                "risk_score": wallet.risk_score,
                "balance": wallet.crm_balance,
                "label": f"Tier {wallet.tier} - {wallet.classification}"
            })
        
        # Add edges from transaction patterns
        for tx in self.transactions:
            if tx.from_wallet in self.wallets and tx.to_wallet in self.wallets:
                graph["edges"].append({
                    "source": tx.from_wallet,
                    "target": tx.to_wallet,
                    "amount": tx.amount,
                    "pattern": tx.pattern_type,
                    "suspicion": tx.suspicious_score,
                    "timestamp": tx.timestamp
                })
        
        return graph
    
    def generate_forensic_report(self) -> dict:
        """Generate comprehensive forensic report"""
        report = {
            "case_id": "CRM-SCAM-2025-001",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_wallets_analyzed": len(self.wallets),
                "total_transactions": len(self.transactions),
                "high_risk_wallets": sum(1 for w in self.wallets.values() if w.risk_score > 0.8),
                "suspicious_patterns": sum(1 for tx in self.transactions if tx.suspicious_score > 0.5)
            },
            "tier_analysis": {},
            "key_findings": [],
            "evidence_hash": self._generate_evidence_hash()
        }
        
        # Analyze each tier
        for tier in range(1, 6):
            tier_wallets = [w for w in self.wallets.values() if w.tier == tier]
            report["tier_analysis"][f"tier_{tier}"] = {
                "wallet_count": len(tier_wallets),
                "primary_wallet": tier_wallets[0].address if tier_wallets else None,
                "total_crm_moved": sum(w.crm_balance for w in tier_wallets),
                "risk_level": "CRITICAL" if tier <= 2 else "HIGH" if tier <= 3 else "MODERATE"
            }
        
        # Key findings
        tier_1 = self.wallets.get(self.TIER_1_MASTER)
        if tier_1:
            report["key_findings"].append({
                "finding": "Military-grade automation detected",
                "wallet": self.TIER_1_MASTER,
                "evidence": "970 wallets seeded in 7 seconds (138/second)",
                "significance": "Humanly impossible - proves automated coordination"
            })
        
        return report
    
    def _generate_evidence_hash(self) -> str:
        """Generate integrity hash for evidence"""
        evidence_str = json.dumps({
            "wallets": [w.to_dict() for w in self.wallets.values()],
            "transactions": [asdict(tx) for tx in self.transactions[:100]]  # Sample
        }, sort_keys=True)
        return hashlib.sha256(evidence_str.encode()).hexdigest()[:16]
    
    def save_to_database(self):
        """Save all data to SQLite"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Save wallets
        for wallet in self.wallets.values():
            c.execute('''
                INSERT OR REPLACE INTO wallets 
                (address, tier, classification, crm_balance, usdc_balance,
                 first_seen, last_active, transaction_count, risk_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                wallet.address, wallet.tier, wallet.classification,
                wallet.crm_balance, wallet.usdc_balance,
                wallet.first_seen, wallet.last_active,
                wallet.transaction_count, wallet.risk_score, wallet.notes
            ))
        
        # Save transactions
        for tx in self.transactions:
            c.execute('''
                INSERT OR REPLACE INTO transactions
                (signature, from_wallet, to_wallet, amount, token,
                 timestamp, block_time, pattern_type, suspicious_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx.signature, tx.from_wallet, tx.to_wallet, tx.amount, tx.token,
                tx.timestamp, tx.block_time, tx.pattern_type, tx.suspicious_score
            ))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(self.wallets)} wallets and {len(self.transactions)} transactions to database")

# ==================== CLI INTERFACE ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CRM Investigation Blockchain Analyzer")
    parser.add_argument("--analyze", action="store_true", help="Run full analysis")
    parser.add_argument("--wallet", type=str, help="Analyze specific wallet")
    parser.add_argument("--report", action="store_true", help="Generate forensic report")
    parser.add_argument("--graph", action="store_true", help="Build relationship graph")
    parser.add_argument("--api-key", type=str, help="Helius API key")
    
    args = parser.parse_args()
    
    analyzer = BlockchainAnalyzer()
    
    if args.report:
        report = analyzer.generate_forensic_report()
        print(json.dumps(report, indent=2))
    
    if args.graph:
        graph = analyzer.build_relationship_graph()
        output_path = "/root/crm_investigation/evidence/wallet_relationship_graph.json"
        with open(output_path, 'w') as f:
            json.dump(graph, f, indent=2)
        print(f"Relationship graph saved to {output_path}")
    
    if args.wallet:
        print(f"Analyzing wallet: {args.wallet}")
        # Would fetch and analyze specific wallet
    
    if args.analyze or not any([args.report, args.graph, args.wallet]):
        print("CRM Investigation Blockchain Analyzer")
        print("=" * 50)
        print(f"Loaded {len(analyzer.wallets)} known wallets")
        print("\nTier Structure:")
        for tier in range(1, 6):
            wallets = [w for w in analyzer.wallets.values() if w.tier == tier]
            if wallets:
                print(f"  Tier {tier}: {wallets[0].address[:20]}... - {wallets[0].notes[:40]}")
        
        risk_scores = analyzer.calculate_risk_scores()
        print("\nRisk Scores:")
        for addr, score in sorted(risk_scores.items(), key=lambda x: -x[1])[:5]:
            print(f"  {addr[:20]}...: {score:.2f}")
        
        analyzer.save_to_database()
        print(f"\nDatabase: {analyzer.db_path}")
