#!/usr/bin/env python3
"""
🔍 CLOSED WALLET TRANSACTION CHECKER
=====================================
Reconstructs transaction history for wallets that have been closed/wiped
Uses blockchain archival data to find all activity before closure

Key Features:
- Retrieves all historical transactions for closed wallets
- Reconstructs fund flows even after wallet deletion
- Identifies counterparties and trace patterns
- Cross-reference with known scam wallets
- Export forensic reports
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import os
from pathlib import Path


@dataclass
class ClosedWalletReport:
    """Complete forensic report for a closed wallet"""

    wallet_address: str
    chain: str
    closure_detected: bool
    closure_date: Optional[str]
    total_transactions: int
    total_volume_sol: float
    counterparties: List[str]
    fund_sources: List[Dict]
    fund_destinations: List[Dict]
    associated_scam_wallets: List[str]
    timeline: List[Dict]
    risk_score: float
    reconstruction_confidence: float

    def to_dict(self) -> Dict:
        return asdict(self)


class ClosedWalletChecker:
    """Advanced closed wallet forensic reconstruction"""

    def __init__(self, rpc_endpoint: Optional[str] = None):
        self.rpc_endpoint = rpc_endpoint or os.getenv(
            "SOLANA_RPC", "https://api.mainnet-beta.solana.com"
        )
        self.helius_api = os.getenv("HELIUS_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None

        # Known scam wallet patterns
        self.scam_indicators = {
            "suspicious_programs": [
                "11111111111111111111111111111111",  # System program
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
            ],
            "wash_trading_patterns": [
                "self_transfer_loop",
                "rapid_buy_sell",
                "dust_transactions",
            ],
        }

        # Cache for wallet data
        self.wallet_cache: Dict[str, Any] = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_wallet(
        self, wallet_address: str, chain: str = "solana"
    ) -> ClosedWalletReport:
        """
        Comprehensive forensic check of a potentially closed wallet

        Args:
            wallet_address: The wallet to investigate
            chain: Blockchain (solana, ethereum, etc.)

        Returns:
            ClosedWalletReport with complete transaction history
        """
        print(f"🔍 Investigating wallet: {wallet_address}")

        # Check if wallet exists currently
        current_state = await self._check_current_state(wallet_address, chain)

        # Get all historical signatures (works even for closed wallets)
        signatures = await self._get_all_signatures(wallet_address, chain)

        # Get transaction details for each signature
        transactions = await self._get_transaction_details(signatures, chain)

        # Analyze fund flows
        fund_analysis = self._analyze_fund_flows(transactions, wallet_address)

        # Check for closure patterns
        closure_info = self._detect_closure_pattern(transactions, current_state)

        # Cross-reference with known scam wallets
        scam_connections = self._check_scam_connections(
            fund_analysis["all_counterparties"]
        )

        # Reconstruct timeline
        timeline = self._reconstruct_timeline(transactions)

        # Calculate risk score
        risk_score = self._calculate_risk_score(
            transactions, scam_connections, closure_info, fund_analysis
        )

        return ClosedWalletReport(
            wallet_address=wallet_address,
            chain=chain,
            closure_detected=closure_info["is_closed"],
            closure_date=closure_info["closure_date"],
            total_transactions=len(transactions),
            total_volume_sol=fund_analysis["total_volume_sol"],
            counterparties=fund_analysis["unique_counterparties"],
            fund_sources=fund_analysis["sources"],
            fund_destinations=fund_analysis["destinations"],
            associated_scam_wallets=scam_connections,
            timeline=timeline,
            risk_score=risk_score,
            reconstruction_confidence=min(
                1.0, len(transactions) / 100
            ),  # Confidence based on data volume
        )

    async def _check_current_state(self, wallet: str, chain: str) -> Dict:
        """Check if wallet currently exists and has balance"""
        try:
            if chain == "solana":
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [wallet, {"encoding": "jsonParsed"}],
                }

                async with self.session.post(self.rpc_endpoint, json=payload) as resp:
                    data = await resp.json()

                    if "result" in data and data["result"] and data["result"]["value"]:
                        return {
                            "exists": True,
                            "lamports": data["result"]["value"]["lamports"],
                            "owner": data["result"]["value"].get("owner", "unknown"),
                            "executable": data["result"]["value"].get(
                                "executable", False
                            ),
                        }
                    else:
                        return {"exists": False, "lamports": 0}

            return {"exists": False, "chain_unsupported": True}

        except Exception as e:
            print(f"⚠️  Error checking current state: {e}")
            return {"exists": "unknown", "error": str(e)}

    async def _get_all_signatures(
        self, wallet: str, chain: str, limit: int = 1000
    ) -> List[str]:
        """
        Retrieve all transaction signatures for a wallet
        This works even for closed wallets - the blockchain never forgets
        """
        signatures = []

        try:
            if chain == "solana":
                # Use getSignaturesForAddress - works for closed wallets
                before = None

                while len(signatures) < limit:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignaturesForAddress",
                        "params": [wallet, {"limit": 100, "before": before}],
                    }

                    async with self.session.post(
                        self.rpc_endpoint, json=payload
                    ) as resp:
                        data = await resp.json()

                        if "result" not in data or not data["result"]:
                            break

                        batch = [sig["signature"] for sig in data["result"]]
                        if not batch:
                            break

                        signatures.extend(batch)
                        before = batch[-1]

                        print(f"   📜 Retrieved {len(signatures)} signatures so far...")

                        # Stop if we got less than requested
                        if len(data["result"]) < 100:
                            break

            return signatures[:limit]

        except Exception as e:
            print(f"⚠️  Error getting signatures: {e}")
            return signatures

    async def _get_transaction_details(
        self, signatures: List[str], chain: str
    ) -> List[Dict]:
        """Get full details for each transaction signature"""
        transactions = []

        # Process in batches
        batch_size = 10

        for i in range(0, len(signatures), batch_size):
            batch = signatures[i : i + batch_size]

            tasks = [self._fetch_transaction(sig, chain) for sig in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for sig, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"   ⚠️  Failed to fetch {sig[:20]}...: {result}")
                elif result:
                    transactions.append(result)

            if (i // batch_size) % 10 == 0:
                print(f"   📊 Processed {i}/{len(signatures)} transactions...")

        return transactions

    async def _fetch_transaction(self, signature: str, chain: str) -> Optional[Dict]:
        """Fetch a single transaction with retries"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                if chain == "solana":
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            signature,
                            {
                                "encoding": "jsonParsed",
                                "maxSupportedTransactionVersion": 0,
                            },
                        ],
                    }

                    async with self.session.post(
                        self.rpc_endpoint,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as resp:
                        data = await resp.json()

                        if "result" in data and data["result"]:
                            return {
                                "signature": signature,
                                "timestamp": data["result"].get("blockTime"),
                                "slot": data["result"].get("slot"),
                                "meta": data["result"].get("meta", {}),
                                "transaction": data["result"].get("transaction", {}),
                            }

                return None

            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                continue
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                continue

        return None

    def _analyze_fund_flows(self, transactions: List[Dict], wallet: str) -> Dict:
        """Analyze where funds came from and went to"""
        sources = []
        destinations = []
        all_counterparties = set()
        total_volume = 0.0

        for tx in transactions:
            meta = tx.get("meta", {})

            # Extract pre/post balances
            pre_balances = meta.get("preBalances", [])
            post_balances = meta.get("postBalances", [])

            # Get account keys
            account_keys = (
                tx.get("transaction", {}).get("message", {}).get("accountKeys", [])
            )

            # Find our wallet's index
            wallet_index = None
            for i, key in enumerate(account_keys):
                if isinstance(key, dict):
                    if key.get("pubkey") == wallet:
                        wallet_index = i
                        break
                elif key == wallet:
                    wallet_index = i
                    break

            if wallet_index is not None and wallet_index < len(pre_balances):
                balance_change = (
                    post_balances[wallet_index] - pre_balances[wallet_index]
                ) / 1e9
                total_volume += abs(balance_change)

                # Identify counterparties
                for i, key in enumerate(account_keys):
                    if i != wallet_index:
                        addr = key.get("pubkey") if isinstance(key, dict) else key
                        all_counterparties.add(addr)

                        if balance_change > 0:  # Received funds
                            sources.append(
                                {
                                    "from": addr,
                                    "amount_sol": balance_change,
                                    "timestamp": tx.get("timestamp"),
                                    "signature": tx.get("signature"),
                                }
                            )
                        elif balance_change < 0:  # Sent funds
                            destinations.append(
                                {
                                    "to": addr,
                                    "amount_sol": abs(balance_change),
                                    "timestamp": tx.get("timestamp"),
                                    "signature": tx.get("signature"),
                                }
                            )

        return {
            "sources": sorted(sources, key=lambda x: x["timestamp"] or 0, reverse=True)[
                :50
            ],
            "destinations": sorted(
                destinations, key=lambda x: x["timestamp"] or 0, reverse=True
            )[:50],
            "unique_counterparties": list(all_counterparties),
            "total_volume_sol": round(total_volume, 4),
        }

    def _detect_closure_pattern(
        self, transactions: List[Dict], current_state: Dict
    ) -> Dict:
        """Detect if and when a wallet was closed/wiped"""
        if not transactions:
            return {"is_closed": False, "closure_date": None}

        # Sort by timestamp
        sorted_tx = sorted(transactions, key=lambda x: x.get("timestamp") or 0)

        # Check if last transaction was a drain
        if sorted_tx:
            last_tx = sorted_tx[-1]
            last_tx_time = datetime.fromtimestamp(last_tx.get("timestamp", 0))

            # If wallet doesn't exist and had transactions, it's closed
            if not current_state.get("exists", True):
                return {
                    "is_closed": True,
                    "closure_date": last_tx_time.isoformat(),
                    "last_transaction_signature": last_tx.get("signature"),
                    "closure_method": "complete_drain"
                    if self._was_drain_transaction(last_tx)
                    else "abandoned",
                }

        return {
            "is_closed": not current_state.get("exists", True),
            "closure_date": None,
        }

    def _was_drain_transaction(self, tx: Dict) -> bool:
        """Check if a transaction drained the wallet"""
        meta = tx.get("meta", {})
        # Check if postBalance is near zero
        post_balances = meta.get("postBalances", [])
        return all(b < 5000 for b in post_balances)  # Less than 0.000005 SOL

    def _check_scam_connections(self, counterparties: List[str]) -> List[str]:
        """Cross-reference with known scam wallets"""
        # Load known scam wallets from case file
        known_scam = self._load_known_scam_wallets()

        matches = []
        for counterparty in counterparties:
            if counterparty in known_scam:
                matches.append(counterparty)

        return matches

    def _load_known_scam_wallets(self) -> set:
        """Load known scam wallets from investigation case"""
        known = set()

        # Tier 1-5 wallets from forensic report
        tier_wallets = [
            "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",  # Tier 1
            "BMq4XUa3rJJNkjXbJDpMFdSmPjvz5f9w4TvYFGADVkX5",  # Tier 2
            "HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi",  # Tier 3
            "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",  # Tier 4
            "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL",  # Tier 5 victim
            "AvZHExxq2BaPrq17cKq1KMN3PWoCwqZRppV882JHY5sN",  # "Lucky early buyer"
            "7GsFEUPC9ZWMRb3wXsyrW33MP3Q6Jb8MpMjf2y1exC9y",  # SHIFT dumper
        ]

        known.update(tier_wallets)

        # Try to load from case file
        case_file = Path("/root/rmi/investigation/cases/SOSANA-CRM-2024.json")
        if case_file.exists():
            try:
                import json

                with open(case_file) as f:
                    case_data = json.load(f)
                    for wallet in case_data.get("entities", {}).get("wallets", []):
                        known.add(wallet["address"])
            except:
                pass

        return known

    def _reconstruct_timeline(self, transactions: List[Dict]) -> List[Dict]:
        """Create a chronological timeline of wallet activity"""
        timeline = []

        for tx in transactions:
            timestamp = tx.get("timestamp")
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)

                # Analyze transaction type
                tx_type = self._classify_transaction(tx)

                timeline.append(
                    {
                        "datetime": dt.isoformat(),
                        "signature": tx.get("signature", "unknown")[:20] + "...",
                        "type": tx_type,
                        "slot": tx.get("slot"),
                    }
                )

        return sorted(timeline, key=lambda x: x["datetime"], reverse=True)

    def _classify_transaction(self, tx: Dict) -> str:
        """Classify transaction type"""
        meta = tx.get("meta", {})

        # Check for token transfers
        if meta.get("postTokenBalances") or meta.get("preTokenBalances"):
            return "token_transfer"

        # Check for program interactions
        logs = meta.get("logMessages", [])
        if any("Instruction" in log for log in logs):
            return "program_interaction"

        # Check for system transfer
        if len(meta.get("postBalances", [])) == 2:
            return "sol_transfer"

        return "unknown"

    def _calculate_risk_score(
        self,
        transactions: List[Dict],
        scam_connections: List[str],
        closure_info: Dict,
        fund_analysis: Dict,
    ) -> float:
        """Calculate overall risk score 0-100"""
        score = 0.0

        # Points for closure
        if closure_info["is_closed"]:
            score += 20

        # Points for scam connections
        score += len(scam_connections) * 15

        # Points for wash trading patterns
        if self._detect_wash_trading(transactions):
            score += 25

        # Points for high volume with few counterparties (mixer behavior)
        if (
            len(fund_analysis["unique_counterparties"]) < 5
            and fund_analysis["total_volume_sol"] > 100
        ):
            score += 15

        return min(100.0, score)

    def _detect_wash_trading(self, transactions: List[Dict]) -> bool:
        """Detect wash trading patterns"""
        if len(transactions) < 10:
            return False

        # Check for rapid buy/sell patterns
        timestamps = [tx.get("timestamp") for tx in transactions if tx.get("timestamp")]
        if len(timestamps) < 2:
            return False

        timestamps.sort()
        time_diffs = [
            timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)
        ]

        # If many transactions within seconds of each other
        rapid_tx = sum(1 for diff in time_diffs if diff < 60)
        return rapid_tx > len(time_diffs) * 0.3  # More than 30% are rapid

    async def batch_check(
        self, wallets: List[str], chain: str = "solana"
    ) -> List[ClosedWalletReport]:
        """Check multiple wallets in parallel"""
        print(f"🔍 Batch checking {len(wallets)} wallets...")

        tasks = [self.check_wallet(w, chain) for w in wallets]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = []
        for wallet, result in zip(wallets, results):
            if isinstance(result, Exception):
                print(f"   ❌ Failed to check {wallet}: {result}")
            else:
                valid_results.append(result)

        return valid_results

    def export_report(
        self,
        report: ClosedWalletReport,
        output_dir: str = "/root/rmi/investigation/reports",
    ):
        """Export forensic report to file"""
        os.makedirs(output_dir, exist_ok=True)

        filename = f"closed_wallet_{report.wallet_address[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(report.to_dict(), f, indent=2, default=str)

        print(f"📄 Report exported to: {filepath}")
        return filepath


async def main():
    """Example usage"""
    # Test wallets - including some from the forensic report
    test_wallets = [
        # Tier 5 execution wallets from CRM case
        "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL",
        # Add more suspicious wallets here
    ]

    async with ClosedWalletChecker() as checker:
        for wallet in test_wallets:
            print("\n" + "=" * 80)
            report = await checker.check_wallet(wallet)

            print(f"\n📊 RESULTS FOR {wallet}")
            print(f"   Closure Detected: {report.closure_detected}")
            print(f"   Total Transactions: {report.total_transactions}")
            print(f"   Total Volume: {report.total_volume_sol:.4f} SOL")
            print(f"   Counterparties: {len(report.counterparties)}")
            print(f"   Scam Connections: {len(report.associated_scam_wallets)}")
            print(f"   Risk Score: {report.risk_score:.1f}/100")
            print(f"   Confidence: {report.reconstruction_confidence * 100:.1f}%")

            # Export report
            checker.export_report(report)


if __name__ == "__main__":
    asyncio.run(main())
