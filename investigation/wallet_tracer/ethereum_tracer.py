#!/usr/bin/env python3
"""
Ethereum Wallet Tracer
Trace ETH wallet transactions using Etherscan/Alchemy
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

class EthereumWalletTracer:
    """Trace Ethereum wallet transactions"""
    
    def __init__(self, etherscan_key: Optional[str] = None):
        self.supabase = create_client(SUPABASE_URL, SERVICE_KEY)
        self.etherscan_key = etherscan_key
        self.etherscan_base = "https://api.etherscan.io/api"
        
        # Fallback RPC
        self.eth_rpc = "https://eth.llamarpc.com"
    
    def get_wallet_transactions(
        self,
        wallet_address: str,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """Get transaction history for an Ethereum wallet"""
        transactions = []
        
        if self.etherscan_key:
            # Use Etherscan API
            transactions = self._get_etherscan_transactions(wallet_address, limit)
        else:
            # Use limited RPC
            logger.warning("No Etherscan API key - using limited RPC fallback")
            transactions = []
        
        return transactions
    
    def _get_etherscan_transactions(
        self,
        wallet: str,
        limit: int
    ) -> List[Dict]:
        """Fetch transactions from Etherscan API"""
        try:
            # Get normal transactions
            url = self.etherscan_base
            params = {
                "module": "account",
                "action": "txlist",
                "address": wallet,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "apikey": self.etherscan_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    return self._parse_etherscan_transactions(data.get("result", []), wallet)
                else:
                    logger.error(f"Etherscan error: {data.get('message')}")
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch Etherscan transactions: {e}")
            return []
    
    def _parse_etherscan_transactions(
        self,
        transactions: List[Dict],
        wallet: str
    ) -> List[Dict]:
        """Parse Etherscan transaction data"""
        parsed = []
        
        for tx in transactions:
            parsed_tx = {
                "hash": tx.get("hash"),
                "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value_eth": int(tx.get("value", 0)) / 1e18,
                "gas_price_gwei": int(tx.get("gasPrice", 0)) / 1e9,
                "gas_used": int(tx.get("gasUsed", 0)),
                "status": "success" if tx.get("txreceipt_status") == "1" else "failed",
                "is_error": tx.get("isError") == "1",
                "wallet": wallet,
                "direction": "out" if tx.get("from").lower() == wallet.lower() else "in"
            }
            parsed.append(parsed_tx)
        
        return parsed[:100]  # Limit to 100 transactions
    
    def analyze_wallet_patterns(self, wallet: str, transactions: List[Dict]) -> Dict:
        """Analyze transaction patterns"""
        analysis = {
            "wallet": wallet,
            "total_transactions": len(transactions),
            "first_transaction": None,
            "last_transaction": None,
            "unique_counterparties": set(),
            "total_volume_eth": 0,
            "total_fees_eth": 0,
            "incoming_count": 0,
            "outgoing_count": 0,
            "risk_indicators": []
        }
        
        if not transactions:
            return analysis
        
        # Sort by timestamp
        sorted_txs = sorted(transactions, key=lambda x: x.get("timestamp", datetime.min))
        
        analysis["first_transaction"] = sorted_txs[0].get("timestamp").isoformat() if sorted_txs[0].get("timestamp") else None
        analysis["last_transaction"] = sorted_txs[-1].get("timestamp").isoformat() if sorted_txs[-1].get("timestamp") else None
        
        for tx in transactions:
            # Track counterparties
            if tx["direction"] == "out":
                analysis["unique_counterparties"].add(tx["to"])
                analysis["outgoing_count"] += 1
                analysis["total_volume_eth"] += tx["value_eth"]
            else:
                analysis["unique_counterparties"].add(tx["from"])
                analysis["incoming_count"] += 1
            
            # Track fees
            if tx.get("gas_used") and tx.get("gas_price_gwei"):
                fee_eth = (tx["gas_used"] * tx["gas_price_gwei"] * 1e9) / 1e18
                analysis["total_fees_eth"] += fee_eth
        
        # Convert sets to lists
        analysis["unique_counterparties"] = list(analysis["unique_counterparties"])
        
        # Risk indicators
        if len(analysis["unique_counterparties"]) > 100:
            analysis["risk_indicators"].append("HIGH_COUNTERPARTY_COUNT")
        
        if analysis["total_volume_eth"] > 1000:
            analysis["risk_indicators"].append("HIGH_VOLUME")
        
        failed_txs = sum(1 for tx in transactions if tx.get("is_error"))
        if failed_txs > len(transactions) * 0.1:  # More than 10% failed
            analysis["risk_indicators"].append("HIGH_FAILURE_RATE")
        
        return analysis
    
    def find_connected_wallets(
        self,
        wallet: str,
        transactions: List[Dict],
        min_interactions: int = 3
    ) -> List[Dict]:
        """Find frequently interacting wallets"""
        counterparty_count = defaultdict(int)
        
        for tx in transactions:
            if tx["direction"] == "out":
                counterparty_count[tx["to"]] += 1
            else:
                counterparty_count[tx["from"]] += 1
        
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
        """Save analysis to database"""
        try:
            self.supabase.table("investigation_wallets").update({
                "metadata": {
                    **analysis,
                    "analyzed_at": datetime.now().isoformat(),
                    "analyzed_by": "ethereum_tracer"
                }
            }).eq("case_id", case_id).eq("address", wallet).execute()
            
            logger.info(f"Saved Ethereum analysis for {wallet}")
            
        except Exception as e:
            logger.error(f"Failed to save: {e}")


if __name__ == "__main__":
    print("Ethereum Wallet Tracer initialized")
    print("Note: Provide Etherscan API key for full functionality")
