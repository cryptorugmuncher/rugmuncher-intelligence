#!/usr/bin/env python3
"""
Solana Wallet Tracer
Trace SOL wallet transactions using Helius API
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
from typing import List, Dict, Any, Optional
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

class SolanaWalletTracer:
    """Trace Solana wallet transactions and analyze patterns"""
    
    def __init__(self, helius_api_key: Optional[str] = None):
        self.supabase = create_client(SUPABASE_URL, SERVICE_KEY)
        self.helius_key = helius_api_key
        self.helius_base = "https://api.helius.xyz/v0"
        
        # Fallback to public RPC if no Helius key
        self.solana_rpc = "https://api.mainnet-beta.solana.com"
        
    def get_wallet_transactions(
        self,
        wallet_address: str,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """Get transaction history for a Solana wallet"""
        transactions = []
        
        if self.helius_key:
            # Use Helius API (more detailed)
            transactions = self._get_helius_transactions(wallet_address, days, limit)
        else:
            # Use public Solana RPC (limited)
            transactions = self._get_rpc_transactions(wallet_address, limit)
        
        return transactions
    
    def _get_helius_transactions(
        self,
        wallet: str,
        days: int,
        limit: int
    ) -> List[Dict]:
        """Fetch transactions from Helius API"""
        try:
            url = f"{self.helius_base}/addresses/{wallet}/transactions"
            params = {
                "api-key": self.helius_key,
                "limit": limit,
                "type": "all"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_helius_transactions(data, wallet)
            else:
                logger.error(f"Helius API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch Helius transactions: {e}")
            return []
    
    def _get_rpc_transactions(self, wallet: str, limit: int) -> List[Dict]:
        """Fetch transactions using Solana RPC"""
        try:
            # Get signatures for address
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    wallet,
                    {"limit": limit}
                ]
            }
            
            response = requests.post(
                self.solana_rpc,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                signatures = data.get("result", [])
                
                # Get transaction details for each signature
                transactions = []
                for sig_info in signatures[:20]:  # Limit to 20 for RPC
                    tx = self._get_transaction_details(sig_info["signature"])
                    if tx:
                        transactions.append(tx)
                
                return transactions
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch RPC transactions: {e}")
            return []
    
    def _get_transaction_details(self, signature: str) -> Optional[Dict]:
        """Get detailed transaction info"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {"encoding": "json", "maxSupportedTransactionVersion": 0}
                ]
            }
            
            response = requests.post(
                self.solana_rpc,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("result")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get transaction details: {e}")
            return None
    
    def _parse_helius_transactions(
        self,
        data: List[Dict],
        wallet: str
    ) -> List[Dict]:
        """Parse Helius transaction data"""
        parsed = []
        
        for tx in data:
            parsed_tx = {
                "signature": tx.get("signature"),
                "timestamp": tx.get("timestamp"),
                "type": tx.get("type"),
                "fee": tx.get("fee"),
                "status": "success" if not tx.get("transactionError") else "failed",
                "wallet": wallet,
                "token_transfers": [],
                "native_transfers": []
            }
            
            # Parse token transfers
            for transfer in tx.get("tokenTransfers", []):
                parsed_tx["token_transfers"].append({
                    "mint": transfer.get("mint"),
                    "from": transfer.get("fromUserAccount"),
                    "to": transfer.get("toUserAccount"),
                    "amount": transfer.get("tokenAmount"),
                    "symbol": transfer.get("symbol")
                })
            
            # Parse SOL transfers
            for transfer in tx.get("nativeTransfers", []):
                parsed_tx["native_transfers"].append({
                    "from": transfer.get("fromUserAccount"),
                    "to": transfer.get("toUserAccount"),
                    "amount": transfer.get("amount")
                })
            
            parsed.append(parsed_tx)
        
        return parsed
    
    def analyze_wallet_patterns(self, wallet: str, transactions: List[Dict]) -> Dict:
        """Analyze transaction patterns for a wallet"""
        analysis = {
            "wallet": wallet,
            "total_transactions": len(transactions),
            "first_transaction": None,
            "last_transaction": None,
            "unique_counterparties": set(),
            "token_interactions": set(),
            "total_volume_sol": 0,
            "risk_indicators": []
        }
        
        if not transactions:
            return analysis
        
        # Sort by timestamp
        sorted_txs = sorted(transactions, key=lambda x: x.get("timestamp", ""))
        
        analysis["first_transaction"] = sorted_txs[0].get("timestamp")
        analysis["last_transaction"] = sorted_txs[-1].get("timestamp")
        
        # Analyze patterns
        for tx in transactions:
            # Track counterparties
            for transfer in tx.get("native_transfers", []):
                if transfer["from"] != wallet:
                    analysis["unique_counterparties"].add(transfer["from"])
                if transfer["to"] != wallet:
                    analysis["unique_counterparties"].add(transfer["to"])
            
            # Track token interactions
            for transfer in tx.get("token_transfers", []):
                analysis["token_interactions"].add(transfer["mint"])
            
            # Calculate volume
            for transfer in tx.get("native_transfers", []):
                if transfer["from"] == wallet:
                    analysis["total_volume_sol"] += float(transfer["amount"])
        
        # Convert sets to lists for JSON serialization
        analysis["unique_counterparties"] = list(analysis["unique_counterparties"])
        analysis["token_interactions"] = list(analysis["token_interactions"])
        
        # Risk indicators
        if len(analysis["unique_counterparties"]) > 100:
            analysis["risk_indicators"].append("HIGH_INTERACTION_COUNT")
        
        if len(analysis["token_interactions"]) > 50:
            analysis["risk_indicators"].append("DIVERSE_TOKEN_INTERACTIONS")
        
        if analysis["total_volume_sol"] > 10000:
            analysis["risk_indicators"].append("HIGH_VOLUME")
        
        return analysis
    
    def find_connected_wallets(
        self,
        wallet: str,
        transactions: List[Dict],
        min_interactions: int = 3
    ) -> List[Dict]:
        """Find wallets with frequent interactions"""
        counterparty_count = defaultdict(int)
        
        for tx in transactions:
            for transfer in tx.get("native_transfers", []):
                if transfer["from"] == wallet:
                    counterparty_count[transfer["to"]] += 1
                elif transfer["to"] == wallet:
                    counterparty_count[transfer["from"]] += 1
        
        # Filter by minimum interactions
        connected = []
        for addr, count in counterparty_count.items():
            if count >= min_interactions:
                connected.append({
                    "address": addr,
                    "interactions": count,
                    "relationship": "frequent_counterparty"
                })
        
        return sorted(connected, key=lambda x: x["interactions"], reverse=True)
    
    def save_to_database(self, wallet: str, analysis: Dict, case_id: str = "SOSANA-CRM-2024"):
        """Save analysis results to database"""
        try:
            # Update wallet record with analysis
            self.supabase.table("investigation_wallets").update({
                "metadata": {
                    **analysis,
                    "analyzed_at": datetime.now().isoformat(),
                    "analyzed_by": "solana_tracer"
                }
            }).eq("case_id", case_id).eq("address", wallet).execute()
            
            # Add connected wallets as entities
            for connected in analysis.get("connected_wallets", []):
                self.supabase.table("investigation_entities").upsert({
                    "case_id": case_id,
                    "entity_type": "wallet",
                    "name": connected["address"],
                    "aliases": [],
                    "metadata": {
                        "connected_to": wallet,
                        "interactions": connected["interactions"],
                        "source": "transaction_analysis"
                    },
                    "risk_level": "medium"
                }, on_conflict="case_id,entity_type,name").execute()
            
            logger.info(f"Saved analysis for wallet {wallet}")
            
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("🔍 PART 3: SOLANA WALLET TRACER")
    print("=" * 70)
    print("\nNote: Provide Helius API key for full functionality")
    print("Get free key at: https://helius.xyz")
    print("\nWithout Helius key, will use limited public RPC")
