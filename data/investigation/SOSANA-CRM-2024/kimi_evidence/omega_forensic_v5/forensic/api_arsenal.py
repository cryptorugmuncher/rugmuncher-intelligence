"""
Omega Forensic V5 - Forensic API Arsenal
=========================================
Complete integration of all 11 forensic APIs organized by division.
Division 1: Identity & AML (Arkham, MistTrack, ChainAbuse)
Division 2: On-Chain Autopsy (Helius, QuickNode, Solscan)
Division 3: Token Mechanics (BirdEye, LunarCrush)
Division 4: Real World OSINT (Serper)
"""

import os
import json
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForensicAPIArsenal")

@dataclass
class APIResponse:
    """Standardized API response wrapper."""
    success: bool
    data: Any
    source: str
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ForensicAPIArsenal:
    """
    Complete forensic API arsenal for blockchain investigation.
    Organized into 4 divisions for specialized tasks.
    """
    
    def __init__(self):
        """Initialize all API connections."""
        # Load keys from environment
        self.keys = {
            # Division 1: Identity & AML
            "arkham": os.getenv("ARKHAM_API_KEY", "bbbebc4f-0727-4157-87cc-42f8991a58ca"),
            "misttrack": os.getenv("MISTTRACK_API_KEY", "ynX083xAuSk4WKEsaHpOFw5DYd91ZlmI"),
            "chainabuse": os.getenv("CHAINABUSE_API_KEY", "ca_VDBVeWVTT3F5TGRPeFVyb1Y4cVhWNnpFLktJYVNHZUVXa0QvZmIxNXVuektaNUE9PQ"),
            # Division 2: On-Chain Autopsy
            "helius": os.getenv("HELIUS_API_KEY", "771413f9-60c9-4714-94d6-33851d1e6d88"),
            "quicknode": os.getenv("QUICKNODE_SOL_RPC", "https://wandering-rough-butterfly.solana-mainnet.quiknode.pro/875fa003546494c35631050925b5e966baa4b81d/"),
            "solscan": os.getenv("SOLSCAN_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NDM3Mjk5NzY0MjUsImVtYWlsIjoiamF5dHJhbmNlQGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOjIsImlhdCI6MTc0MzcyOTk3Nn0.4MpOu1mE24T6XqQJ7zJ-0iLrPE6jQpbjxw33RwAiVOE"),
            # Division 3: Token Mechanics
            "birdeye": os.getenv("BIRDEYE_API_KEY", "58c5b02e9e484c73b02691687379673a"),
            "lunarcrush": os.getenv("LUNARCRUSH_API_KEY", "mu5cf8zde098q1hti2t8tmfrsgmnh3ifzxpad14y9"),
            # Division 4: Real World OSINT
            "serper": os.getenv("SERPER_API_KEY", "faee04c161280c9e83ed2fed949d175b4fbb3222"),
        }
        
        # Rate limiting trackers
        self.rate_limits = {k: {"count": 0, "reset_time": datetime.now()} for k in self.keys}
        
        # Session for async requests
        self.session = None
        
        logger.info("ForensicAPIArsenal initialized with %d APIs", len(self.keys))
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    # ============================================================
    # DIVISION 1: IDENTITY & AML
    # ============================================================
    
    async def arkham_get_entity(self, address: str) -> APIResponse:
        """
        Get entity information from Arkham Intelligence.
        Identifies real-world entities behind wallet addresses.
        """
        try:
            url = f"https://api.arkhamintelligence.com/intelligence/address/{address}"
            headers = {"Authorization": f"Bearer {self.keys['arkham']}"}
            
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "arkham")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "arkham", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "arkham", str(e))
    
    async def arkham_get_transactions(
        self, 
        address: str, 
        limit: int = 100,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None
    ) -> APIResponse:
        """Get transaction history from Arkham with time filtering."""
        try:
            params = {"limit": limit, "sort": "timeDesc"}
            if from_time:
                params["fromTime"] = from_time
            if to_time:
                params["toTime"] = to_time
                
            url = f"https://api.arkhamintelligence.com/intelligence/address/{address}/transactions"
            headers = {"Authorization": f"Bearer {self.keys['arkham']}"}
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "arkham")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "arkham", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "arkham", str(e))
    
    async def misttrack_check_address(self, address: str, chain: str = "SOL") -> APIResponse:
        """
        Check address risk score with MistTrack.
        Returns risk rating and associated labels.
        """
        try:
            url = "https://misttrack.io/api/v1/address_risk"
            headers = {"Authorization": f"Bearer {self.keys['misttrack']}"}
            params = {"address": address, "chain": chain}
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "misttrack")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "misttrack", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "misttrack", str(e))
    
    async def misttrack_get_transactions(
        self, 
        address: str, 
        chain: str = "SOL",
        limit: int = 100
    ) -> APIResponse:
        """Get transaction history from MistTrack."""
        try:
            url = "https://misttrack.io/api/v1/address_transactions"
            headers = {"Authorization": f"Bearer {self.keys['misttrack']}"}
            params = {"address": address, "chain": chain, "limit": limit}
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "misttrack")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "misttrack", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "misttrack", str(e))
    
    async def chainabuse_check_address(self, address: str) -> APIResponse:
        """
        Check if address has been reported on ChainAbuse.
        Community-reported scam addresses.
        """
        try:
            url = f"https://api.chainabuse.com/v1/addresses/{address}"
            headers = {"Authorization": f"Bearer {self.keys['chainabuse']}"}
            
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "chainabuse")
                elif resp.status == 404:
                    return APIResponse(True, {"reports": [], "risk": "unknown"}, "chainabuse")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "chainabuse", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "chainabuse", str(e))
    
    async def chainabuse_report_address(
        self, 
        address: str, 
        description: str,
        scam_type: str = "rug_pull"
    ) -> APIResponse:
        """Report an address to ChainAbuse database."""
        try:
            url = "https://api.chainabuse.com/v1/reports"
            headers = {
                "Authorization": f"Bearer {self.keys['chainabuse']}",
                "Content-Type": "application/json"
            }
            payload = {
                "address": address,
                "description": description,
                "scamType": scam_type,
                "chain": "SOL"
            }
            
            async with self.session.post(url, headers=headers, json=payload) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    return APIResponse(True, data, "chainabuse")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "chainabuse", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "chainabuse", str(e))
    
    # ============================================================
    # DIVISION 2: ON-CHAIN AUTOPSY
    # ============================================================
    
    async def helius_get_account(self, address: str) -> APIResponse:
        """Get comprehensive account information from Helius."""
        try:
            url = f"https://api.helius.xyz/v0/addresses/?api-key={self.keys['helius']}"
            payload = {"query": address}
            
            async with self.session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "helius")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "helius", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "helius", str(e))
    
    async def helius_get_transactions(
        self, 
        address: str, 
        limit: int = 100,
        before: Optional[str] = None
    ) -> APIResponse:
        """Get transaction history from Helius."""
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions"
            params = {"api-key": self.keys['helius'], "limit": limit}
            if before:
                params["before"] = before
                
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "helius")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "helius", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "helius", str(e))
    
    async def helius_get_token_accounts(self, address: str) -> APIResponse:
        """Get all token accounts for a wallet."""
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/balances"
            params = {"api-key": self.keys['helius']}
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "helius")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "helius", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "helius", str(e))
    
    async def helius_enhanced_transactions(
        self,
        signatures: List[str]
    ) -> APIResponse:
        """Get enhanced transaction data with parsed instructions."""
        try:
            url = f"https://api.helius.xyz/v0/transactions/?api-key={self.keys['helius']}"
            payload = {"transactions": signatures}
            
            async with self.session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "helius")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "helius", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "helius", str(e))
    
    async def quicknode_rpc_call(self, method: str, params: List = None) -> APIResponse:
        """Make RPC call to QuickNode."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or []
            }
            
            async with self.session.post(self.keys['quicknode'], json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "quicknode")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "quicknode", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "quicknode", str(e))
    
    async def quicknode_get_account_info(self, address: str) -> APIResponse:
        """Get account info via QuickNode RPC."""
        return await self.quicknode_rpc_call("getAccountInfo", [address, {"encoding": "jsonParsed"}])
    
    async def quicknode_get_signatures(
        self, 
        address: str, 
        limit: int = 100
    ) -> APIResponse:
        """Get signature history via QuickNode RPC."""
        return await self.quicknode_rpc_call(
            "getSignaturesForAddress", 
            [address, {"limit": limit}]
        )
    
    async def solscan_get_account(self, address: str) -> APIResponse:
        """Get account information from Solscan."""
        try:
            url = f"https://api.solscan.io/account/{address}"
            headers = {"Authorization": f"Bearer {self.keys['solscan']}"}
            
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "solscan")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "solscan", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "solscan", str(e))
    
    async def solscan_get_transactions(
        self, 
        address: str, 
        limit: int = 50
    ) -> APIResponse:
        """Get transaction history from Solscan."""
        try:
            url = f"https://api.solscan.io/account/transactions"
            headers = {"Authorization": f"Bearer {self.keys['solscan']}"}
            params = {"address": address, "limit": limit}
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "solscan")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "solscan", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "solscan", str(e))
    
    async def solscan_get_token_holdings(self, address: str) -> APIResponse:
        """Get token holdings from Solscan."""
        try:
            url = f"https://api.solscan.io/account/tokens"
            headers = {"Authorization": f"Bearer {self.keys['solscan']}"}
            params = {"address": address}
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "solscan")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "solscan", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "solscan", str(e))
    
    # ============================================================
    # DIVISION 3: TOKEN MECHANICS
    # ============================================================
    
    async def birdeye_get_token_price(self, token_address: str) -> APIResponse:
        """Get current token price from BirdEye."""
        try:
            url = f"https://public-api.birdeye.so/public/price"
            headers = {"X-API-KEY": self.keys['birdeye']}
            params = {"address": token_address}
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "birdeye")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "birdeye", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "birdeye", str(e))
    
    async def birdeye_get_token_history(
        self, 
        token_address: str,
        time_from: int,
        time_to: int,
        interval: str = "1h"
    ) -> APIResponse:
        """Get token price history from BirdEye."""
        try:
            url = f"https://public-api.birdeye.so/public/history_price"
            headers = {"X-API-KEY": self.keys['birdeye']}
            params = {
                "address": token_address,
                "time_from": time_from,
                "time_to": time_to,
                "interval": interval
            }
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "birdeye")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "birdeye", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "birdeye", str(e))
    
    async def birdeye_get_top_traders(self, token_address: str, limit: int = 20) -> APIResponse:
        """Get top traders for a token from BirdEye."""
        try:
            url = f"https://public-api.birdeye.so/public/top_traders"
            headers = {"X-API-KEY": self.keys['birdeye']}
            params = {"address": token_address, "limit": limit}
            
            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "birdeye")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "birdeye", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "birdeye", str(e))
    
    async def lunarcrush_get_token_metrics(self, token_symbol: str) -> APIResponse:
        """Get social metrics for token from LunarCrush."""
        try:
            url = "https://api.lunarcrush.com/v3/coins"
            params = {
                "key": self.keys['lunarcrush'],
                "symbol": token_symbol,
                "data_points": 30
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "lunarcrush")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "lunarcrush", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "lunarcrush", str(e))
    
    async def lunarcrush_get_social_sentiment(self, token_symbol: str) -> APIResponse:
        """Get social sentiment data from LunarCrush."""
        try:
            url = "https://api.lunarcrush.com/v3/coins"
            params = {
                "key": self.keys['lunarcrush'],
                "symbol": token_symbol,
                "metric": "social_score"
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "lunarcrush")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "lunarcrush", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "lunarcrush", str(e))
    
    # ============================================================
    # DIVISION 4: REAL WORLD OSINT
    # ============================================================
    
    async def serper_search(
        self, 
        query: str, 
        num_results: int = 10,
        search_type: str = "search"
    ) -> APIResponse:
        """
        Search with Serper (Google Search API).
        For finding KYC vectors, real-world identities, news.
        """
        try:
            url = f"https://google.serper.dev/{search_type}"
            headers = {
                "X-API-KEY": self.keys['serper'],
                "Content-Type": "application/json"
            }
            payload = {"q": query, "num": num_results}
            
            async with self.session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return APIResponse(True, data, "serper")
                else:
                    error_text = await resp.text()
                    return APIResponse(False, None, "serper", f"HTTP {resp.status}: {error_text}")
        except Exception as e:
            return APIResponse(False, None, "serper", str(e))
    
    async def serper_search_wallet(self, address: str) -> APIResponse:
        """Search for wallet address mentions online."""
        return await self.serper_search(f'"{address}" crypto scam OR rug pull', 20)
    
    async def serper_search_entity(self, entity_name: str) -> APIResponse:
        """Search for entity information."""
        return await self.serper_search(f'{entity_name} crypto Solana', 15)
    
    # ============================================================
    # COMPOSITE FORENSIC OPERATIONS
    # ============================================================
    
    async def full_wallet_profile(self, address: str) -> Dict[str, APIResponse]:
        """
        Generate complete wallet profile using all available APIs.
        This is the nuclear option - hits every division.
        """
        logger.info(f"Generating full profile for {address}")
        
        tasks = {
            # Division 1: Identity & AML
            "arkham_entity": self.arkham_get_entity(address),
            "misttrack_risk": self.misttrack_check_address(address),
            "chainabuse_reports": self.chainabuse_check_address(address),
            # Division 2: On-Chain Autopsy
            "helius_account": self.helius_get_account(address),
            "helius_tokens": self.helius_get_token_accounts(address),
            "solscan_account": self.solscan_get_account(address),
            "solscan_holdings": self.solscan_get_token_holdings(address),
        }
        
        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await asyncio.wait_for(task, timeout=30)
            except asyncio.TimeoutError:
                results[name] = APIResponse(False, None, name.split("_")[0], "Timeout")
        
        return results
    
    async def kyc_vector_hunt(self, address: str) -> APIResponse:
        """
        Hunt for KYC vectors - any real-world identity connections.
        Combines Arkham entity data with OSINT searches.
        """
        logger.info(f"Hunting KYC vectors for {address}")
        
        # Get entity info from Arkham
        arkham_result = await self.arkham_get_entity(address)
        
        # Search online for mentions
        serper_result = await self.serper_search_wallet(address)
        
        # Compile KYC vectors
        vectors = []
        
        if arkham_result.success and arkham_result.data:
            entity_data = arkham_result.data
            if entity_data.get("entity"):
                vectors.append({
                    "type": "arkham_entity",
                    "entity": entity_data["entity"],
                    "confidence": "high"
                })
            if entity_data.get("labels"):
                vectors.extend([{
                    "type": "label",
                    "value": label,
                    "confidence": "medium"
                } for label in entity_data["labels"]])
        
        if serper_result.success and serper_result.data:
            organic = serper_result.data.get("organic", [])
            for result in organic[:5]:
                vectors.append({
                    "type": "online_mention",
                    "source": result.get("link"),
                    "snippet": result.get("snippet"),
                    "confidence": "low"
                })
        
        return APIResponse(
            success=len(vectors) > 0,
            data={"address": address, "kyc_vectors": vectors},
            source="composite_kyc_hunt"
        )
    
    async def cross_project_affiliation(
        self, 
        wallet: str, 
        project_tokens: List[str]
    ) -> APIResponse:
        """
        Check wallet affiliation with multiple projects.
        Critical for proving CRM ↔ SOSANA ↔ PBTC ↔ SHIFT AI connections.
        """
        logger.info(f"Checking cross-project affiliation for {wallet}")
        
        affiliations = []
        
        # Get token holdings
        holdings_result = await self.helius_get_token_accounts(wallet)
        
        if holdings_result.success and holdings_result.data:
            tokens = holdings_result.data.get("tokens", [])
            
            for token in tokens:
                mint = token.get("mint")
                if mint in project_tokens:
                    affiliations.append({
                        "token": mint,
                        "balance": token.get("amount", 0),
                        "decimals": token.get("decimals", 0),
                        "affiliation_type": "holder"
                    })
        
        # Check transaction history for interactions
        tx_result = await self.helius_get_transactions(wallet, limit=100)
        
        if tx_result.success and tx_result.data:
            transactions = tx_result.data
            
            for tx in transactions:
                # Look for token transfers involving target projects
                token_transfers = tx.get("tokenTransfers", [])
                for transfer in token_transfers:
                    mint = transfer.get("mint")
                    if mint in project_tokens:
                        affiliations.append({
                            "token": mint,
                            "type": transfer.get("type"),
                            "timestamp": tx.get("timestamp"),
                            "affiliation_type": "transaction"
                        })
        
        return APIResponse(
            success=len(affiliations) > 0,
            data={
                "wallet": wallet,
                "affiliations": affiliations,
                "project_count": len(set(a["token"] for a in affiliations))
            },
            source="cross_project_affiliation"
        )

# === SYNC WRAPPERS FOR CONVENIENCE ===
def sync_full_wallet_profile(address: str) -> Dict:
    """Synchronous wrapper for full wallet profile."""
    async def run():
        async with ForensicAPIArsenal() as arsenal:
            return await arsenal.full_wallet_profile(address)
    return asyncio.run(run())

def sync_kyc_vector_hunt(address: str) -> APIResponse:
    """Synchronous wrapper for KYC vector hunt."""
    async def run():
        async with ForensicAPIArsenal() as arsenal:
            return await arsenal.kyc_vector_hunt(address)
    return asyncio.run(run())

if __name__ == "__main__":
    # Test the arsenal
    import asyncio
    
    async def test():
        print("=" * 70)
        print("FORENSIC API ARSENAL - TEST SUITE")
        print("=" * 70)
        
        async with ForensicAPIArsenal() as arsenal:
            # Test wallet
            test_wallet = "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6"
            
            print(f"\n🔍 Testing with wallet: {test_wallet}")
            print("-" * 70)
            
            # Test individual APIs
            print("\n📡 Testing Division 2 (On-Chain Autopsy)...")
            
            helius_result = await arsenal.helius_get_account(test_wallet)
            print(f"  Helius: {'✓' if helius_result.success else '✗'} {helius_result.error or 'OK'}")
            
            solscan_result = await arsenal.solscan_get_account(test_wallet)
            print(f"  Solscan: {'✓' if solscan_result.success else '✗'} {solscan_result.error or 'OK'}")
            
            print("\n📡 Testing Division 1 (Identity & AML)...")
            
            chainabuse_result = await arsenal.chainabuse_check_address(test_wallet)
            print(f"  ChainAbuse: {'✓' if chainabuse_result.success else '✗'} {chainabuse_result.error or 'OK'}")
            
            print("\n📡 Testing Division 3 (Token Mechanics)...")
            
            target_ca = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"
            birdeye_result = await arsenal.birdeye_get_token_price(target_ca)
            print(f"  BirdEye: {'✓' if birdeye_result.success else '✗'} {birdeye_result.error or 'OK'}")
            
            print("\n" + "=" * 70)
            print("API ARSENAL READY FOR FORENSIC OPERATIONS")
            print("=" * 70)
    
    asyncio.run(test())
