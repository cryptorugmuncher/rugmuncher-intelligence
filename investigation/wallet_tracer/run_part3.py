#!/usr/bin/env python3
"""
Part 3: Wallet Transaction Tracing - Main Runner
Trace all wallets in the investigation and build relationship maps
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
from solana_tracer import SolanaWalletTracer
from ethereum_tracer import EthereumWalletTracer
import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"
CASE_ID = "SOSANA-CRM-2024"

class WalletTracingEngine:
    """Main engine for wallet tracing operations"""
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SERVICE_KEY)
        self.solana_tracer = SolanaWalletTracer()
        self.ethereum_tracer = EthereumWalletTracer()
        self.results = {
            "wallets_analyzed": 0,
            "transactions_found": 0,
            "connections_discovered": 0,
            "risk_wallets": []
        }
    
    def run_full_analysis(self):
        """Run complete wallet tracing analysis"""
        print("=" * 70)
        print("🔍 PART 3: WALLET TRANSACTION TRACING")
        print("=" * 70)
        
        # Get all wallets from database
        wallets = self._get_wallets()
        print(f"\n📊 Found {len(wallets)} wallets to analyze")
        
        # Separate by chain type
        eth_wallets = [w for w in wallets if w['address'].startswith('0x')]
        
        print(f"  • Ethereum wallets: {len(eth_wallets)}")
        print(f"  • Solana wallets: 0 (none found in evidence)")
        
        # Analyze each wallet
        print("\n🔄 Analyzing wallets...")
        
        for i, wallet in enumerate(eth_wallets):
            print(f"\n  [{i+1}/{len(eth_wallets)}] {wallet['address'][:20]}...")
            
            try:
                self._analyze_ethereum_wallet(wallet)
                self.results["wallets_analyzed"] += 1
            except Exception as e:
                logger.error(f"Failed to analyze {wallet['address']}: {e}")
        
        # Build relationship graph
        print("\n🔗 Building relationship graph...")
        self._build_relationship_graph()
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
    
    def _get_wallets(self) -> List[Dict]:
        """Get all wallets from database"""
        result = self.supabase.table("investigation_wallets").select("*").eq("case_id", CASE_ID).execute()
        return result.data
    
    def _analyze_ethereum_wallet(self, wallet: Dict):
        """Analyze an Ethereum wallet"""
        address = wallet['address']
        
        # Get transactions
        transactions = self.ethereum_tracer.get_wallet_transactions(address, days=90)
        
        if transactions:
            print(f"    Found {len(transactions)} transactions")
            self.results["transactions_found"] += len(transactions)
            
            # Analyze patterns
            analysis = self.ethereum_tracer.analyze_wallet_patterns(address, transactions)
            
            # Find connected wallets
            connected = self.ethereum_tracer.find_connected_wallets(address, transactions)
            analysis["connected_wallets"] = connected
            self.results["connections_discovered"] += len(connected)
            
            # Check if high risk
            if analysis.get("risk_indicators"):
                self.results["risk_wallets"].append({
                    "address": address,
                    "indicators": analysis["risk_indicators"]
                })
            
            # Save to database
            self.ethereum_tracer.save_to_database(address, analysis, CASE_ID)
            
        else:
            print(f"    No transactions found (API key needed for full tracing)")
    
    def _build_relationship_graph(self):
        """Build wallet relationship graph"""
        print("\n  Building graph...")
        
        # Get all wallet relationships from database
        result = self.supabase.table("investigation_entities").select("*").eq("case_id", CASE_ID).eq("entity_type", "wallet").execute()
        
        # Build graph structure
        graph = {
            "nodes": [],
            "edges": []
        }
        
        for entity in result.data:
            # Add node
            graph["nodes"].append({
                "id": entity["name"],
                "type": "wallet",
                "risk": entity.get("risk_level", "unknown"),
                "metadata": entity.get("metadata", {})
            })
            
            # Add edges for connections
            metadata = entity.get("metadata", {})
            for connected in metadata.get("connected_wallets", []):
                graph["edges"].append({
                    "source": entity["name"],
                    "target": connected["address"],
                    "weight": connected["interactions"],
                    "type": "transaction"
                })
        
        # Save graph
        with open(f"/root/rmi/data/wallet_graph_{CASE_ID}.json", 'w') as f:
            json.dump(graph, f, indent=2, default=str)
        
        print(f"    Graph saved: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    
    def _save_results(self):
        """Save analysis results"""
        with open(f"/root/rmi/data/part3_results.json", 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print("\n💾 Results saved to /root/rmi/data/")
    
    def _print_summary(self):
        """Print analysis summary"""
        print("\n" + "=" * 70)
        print("📊 PART 3 COMPLETE - WALLET TRACING SUMMARY")
        print("=" * 70)
        
        print(f"\n  • Wallets Analyzed: {self.results['wallets_analyzed']}")
        print(f"  • Transactions Found: {self.results['transactions_found']}")
        print(f"  • Connections Discovered: {self.results['connections_discovered']}")
        print(f"  • High-Risk Wallets: {len(self.results['risk_wallets'])}")
        
        if self.results['risk_wallets']:
            print("\n  🚨 High-Risk Wallets:")
            for wallet in self.results['risk_wallets'][:10]:
                print(f"    • {wallet['address'][:20]}...")
                for indicator in wallet['indicators']:
                    print(f"      - {indicator}")
        
        print("\n" + "=" * 70)
        print("🚀 NEXT: Part 4 - MunchMaps Visualization")
        print("=" * 70)


if __name__ == "__main__":
    engine = WalletTracingEngine()
    engine.run_full_analysis()
