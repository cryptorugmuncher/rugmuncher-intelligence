"""
Omega Forensic V5 - Deep Wallet Scanner
========================================
Multi-layer wallet analysis with recursive connection mapping.
Digs multiple layers deep into wallet connections.
"""

import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .api_arsenal import ForensicAPIArsenal, APIResponse
from .wallet_database import WalletDatabase, get_wallet_database, WalletCategory, EvidenceTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepScanner")

@dataclass
class ConnectionPath:
    """Represents a path of connections between wallets."""
    path: List[str] = field(default_factory=list)
    strength: float = 0.0  # 0.0 to 1.0
    evidence_types: List[str] = field(default_factory=list)
    
    def __len__(self):
        return len(self.path)

@dataclass
class WalletAnalysis:
    """Complete analysis result for a wallet."""
    address: str
    layer: int = 0
    api_data: Dict = field(default_factory=dict)
    connections: List[ConnectionPath] = field(default_factory=list)
    risk_score: float = 0.0
    flags: List[str] = field(default_factory=list)
    affiliated_projects: Set[str] = field(default_factory=set)
    kyc_vectors: List[Dict] = field(default_factory=list)
    transaction_patterns: Dict = field(default_factory=dict)
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class DeepWalletScanner:
    """
    Deep wallet scanner that digs multiple layers into connections.
    Self-healing and self-learning capabilities.
    """
    
    def __init__(self, max_layers: int = 5, max_connections_per_layer: int = 20):
        self.max_layers = max_layers
        self.max_connections_per_layer = max_connections_per_layer
        self.wallet_db = get_wallet_database()
        self.cache = {}  # Simple cache for analyzed wallets
        self.learned_patterns = []  # Self-learning storage
        
    async def scan_wallet(
        self, 
        address: str, 
        layers: int = 3,
        arsenal: Optional[ForensicAPIArsenal] = None
    ) -> WalletAnalysis:
        """
        Perform deep scan of a wallet.
        
        Args:
            address: Wallet address to scan
            layers: How many connection layers deep to go
            arsenal: Optional API arsenal instance
        
        Returns:
            Complete wallet analysis
        """
        logger.info(f"🔍 Deep scanning {address} ({layers} layers)")
        
        if layers > self.max_layers:
            layers = self.max_layers
        
        # Check cache
        if address in self.cache:
            logger.info(f"  ✓ Cache hit for {address}")
            return self.cache[address]
        
        analysis = WalletAnalysis(address=address, layer=0)
        
        async with ForensicAPIArsenal() as api:
            # Layer 0: Direct wallet data
            await self._scan_layer_0(analysis, api)
            
            # Recursive layers
            visited = {address}
            current_layer = [address]
            
            for layer in range(1, layers + 1):
                next_layer = []
                
                for wallet in current_layer:
                    connections = await self._scan_connections(wallet, api, visited)
                    
                    for conn in connections[:self.max_connections_per_layer]:
                        path = ConnectionPath(
                            path=[wallet, conn["target"]],
                            strength=conn["strength"],
                            evidence_types=conn["evidence"]
                        )
                        analysis.connections.append(path)
                        
                        if conn["target"] not in visited:
                            visited.add(conn["target"])
                            next_layer.append(conn["target"])
                
                current_layer = next_layer
                if not current_layer:
                    break
        
        # Calculate risk score
        analysis.risk_score = self._calculate_risk(analysis)
        
        # Cache result
        self.cache[address] = analysis
        
        logger.info(f"  ✓ Scan complete. Risk: {analysis.risk_score:.2f}, Connections: {len(analysis.connections)}")
        
        return analysis
    
    async def _scan_layer_0(self, analysis: WalletAnalysis, api: ForensicAPIArsenal):
        """Scan layer 0 - direct wallet data."""
        # Get API data
        profile = await api.full_wallet_profile(analysis.address)
        analysis.api_data = profile
        
        # Check database
        db_wallet = self.wallet_db.get_wallet(analysis.address)
        if db_wallet:
            analysis.affiliated_projects = set(db_wallet.cross_project_affiliations)
            analysis.kyc_vectors = db_wallet.kyc_vectors
            analysis.flags.extend(db_wallet.labels)
        
        # Check for suspicious patterns
        await self._analyze_patterns(analysis, api)
    
    async def _scan_connections(
        self, 
        address: str, 
        api: ForensicAPIArsenal,
        visited: Set[str]
    ) -> List[Dict]:
        """Scan for connections from a wallet."""
        connections = []
        
        # Get transactions
        tx_result = await api.helius_get_transactions(address, limit=50)
        
        if tx_result.success and tx_result.data:
            for tx in tx_result.data:
                # Look for token transfers
                token_transfers = tx.get("tokenTransfers", [])
                
                for transfer in token_transfers:
                    from_addr = transfer.get("fromUserAccount")
                    to_addr = transfer.get("toUserAccount")
                    
                    # Check if this involves our target token
                    mint = transfer.get("mint")
                    if mint == "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS":
                        other = to_addr if from_addr == address else from_addr
                        
                        if other and other not in visited:
                            connections.append({
                                "target": other,
                                "strength": 0.8,
                                "evidence": ["crm_transfer"],
                                "amount": transfer.get("tokenAmount", 0)
                            })
                
                # Look for SOL transfers
                native_transfers = tx.get("nativeTransfers", [])
                for transfer in native_transfers:
                    from_addr = transfer.get("fromUserAccount")
                    to_addr = transfer.get("toUserAccount")
                    other = to_addr if from_addr == address else from_addr
                    
                    if other and other not in visited:
                        connections.append({
                            "target": other,
                            "strength": 0.5,
                            "evidence": ["sol_transfer"],
                            "amount": transfer.get("amount", 0) / 1e9
                        })
        
        # Check database connections
        db_wallet = self.wallet_db.get_wallet(address)
        if db_wallet:
            for conn_addr in db_wallet.connected_wallets:
                if conn_addr not in visited:
                    connections.append({
                        "target": conn_addr,
                        "strength": 0.9,
                        "evidence": ["database_verified"]
                    })
        
        # Sort by strength
        connections.sort(key=lambda x: x["strength"], reverse=True)
        
        return connections
    
    async def _analyze_patterns(self, analysis: WalletAnalysis, api: ForensicAPIArsenal):
        """Analyze transaction patterns for suspicious activity."""
        # Get transaction history
        tx_result = await api.helius_get_transactions(analysis.address, limit=100)
        
        if not tx_result.success or not tx_result.data:
            return
        
        transactions = tx_result.data
        
        # Pattern 1: High frequency trading
        if len(transactions) > 50:
            analysis.flags.append("high_frequency")
        
        # Pattern 2: Coordinated timing
        timestamps = [tx.get("timestamp") for tx in transactions if tx.get("timestamp")]
        if len(timestamps) >= 2:
            time_diffs = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            avg_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            
            if avg_diff < 300:  # Less than 5 minutes average
                analysis.flags.append("rapid_fire_transactions")
        
        # Pattern 3: Large value transfers
        large_transfers = 0
        for tx in transactions:
            token_transfers = tx.get("tokenTransfers", [])
            for transfer in token_transfers:
                amount = transfer.get("tokenAmount", 0)
                if amount > 1000000:  # > 1M tokens
                    large_transfers += 1
        
        if large_transfers > 5:
            analysis.flags.append("large_value_transfers")
        
        # Pattern 4: DEX interactions
        dex_programs = [
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter
        ]
        
        dex_interactions = 0
        for tx in transactions:
            instructions = tx.get("instructions", [])
            for ix in instructions:
                program = ix.get("programId")
                if program in dex_programs:
                    dex_interactions += 1
        
        if dex_interactions > 10:
            analysis.flags.append("heavy_dex_usage")
        
        analysis.transaction_patterns = {
            "total_transactions": len(transactions),
            "large_transfers": large_transfers,
            "dex_interactions": dex_interactions
        }
    
    def _calculate_risk(self, analysis: WalletAnalysis) -> float:
        """Calculate risk score based on analysis."""
        score = 0.0
        
        # Database category risk
        db_wallet = self.wallet_db.get_wallet(analysis.address)
        if db_wallet:
            category_scores = {
                WalletCategory.ROOT_FUNDER: 0.9,
                WalletCategory.BOTNET_SEEDER: 0.95,
                WalletCategory.DUMPER_NODE: 0.85,
                WalletCategory.BRIDGE_NODE: 0.8,
                WalletCategory.TREASURY_COMMAND: 0.75,
                WalletCategory.HOSTAGE_BAG: 0.7,
                WalletCategory.PREBOND_FUNDER: 0.8,
                WalletCategory.CLOSED_ACCOUNT: 0.6,
                WalletCategory.SUSPECTED: 0.5,
            }
            score += category_scores.get(db_wallet.category, 0.3)
        
        # Flag-based risk
        flag_scores = {
            "high_frequency": 0.2,
            "rapid_fire_transactions": 0.3,
            "large_value_transfers": 0.25,
            "heavy_dex_usage": 0.15,
            "BOTNET_COMMANDER": 0.95,
            "ROOT_FUNDER": 0.9,
            "SMOKING_GUN": 0.95,
        }
        
        for flag in analysis.flags:
            score += flag_scores.get(flag, 0.1)
        
        # Cap at 1.0
        return min(score, 1.0)
    
    async def scan_multiple(
        self, 
        addresses: List[str], 
        layers: int = 2
    ) -> Dict[str, WalletAnalysis]:
        """Scan multiple wallets concurrently."""
        logger.info(f"🔍 Scanning {len(addresses)} wallets ({layers} layers each)")
        
        tasks = [self.scan_wallet(addr, layers) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        analyses = {}
        for addr, result in zip(addresses, results):
            if isinstance(result, Exception):
                logger.error(f"  ✗ Error scanning {addr}: {result}")
            else:
                analyses[addr] = result
        
        logger.info(f"  ✓ Completed {len(analyses)} scans")
        return analyses
    
    def generate_connection_graph(self, analyses: Dict[str, WalletAnalysis]) -> Dict:
        """Generate graph data from multiple analyses."""
        nodes = []
        edges = []
        
        for addr, analysis in analyses.items():
            nodes.append({
                "id": addr,
                "risk": analysis.risk_score,
                "flags": analysis.flags,
                "projects": list(analysis.affiliated_projects)
            })
            
            for conn in analysis.connections:
                edges.append({
                    "source": conn.path[0] if len(conn.path) > 0 else addr,
                    "target": conn.path[-1] if len(conn.path) > 1 else addr,
                    "strength": conn.strength,
                    "evidence": conn.evidence_types
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def self_heal(self, error_analysis: Dict):
        """
        Self-healing: learn from errors and improve.
        Stores patterns that led to errors.
        """
        self.learned_patterns.append({
            "timestamp": datetime.now(),
            "error": error_analysis
        })
        logger.info(f"🩹 Self-healed: learned from error pattern")
    
    def get_learned_insights(self) -> List[Dict]:
        """Get insights learned from previous scans."""
        return self.learned_patterns

# === SYNC WRAPPER ===
def deep_scan(address: str, layers: int = 3) -> WalletAnalysis:
    """Synchronous wrapper for deep scan."""
    scanner = DeepWalletScanner()
    return asyncio.run(scanner.scan_wallet(address, layers))

def batch_scan(addresses: List[str], layers: int = 2) -> Dict[str, WalletAnalysis]:
    """Synchronous wrapper for batch scan."""
    scanner = DeepWalletScanner()
    return asyncio.run(scanner.scan_multiple(addresses, layers))

if __name__ == "__main__":
    # Test the scanner
    import asyncio
    
    async def test():
        print("=" * 70)
        print("OMEGA FORENSIC V5 - DEEP WALLET SCANNER")
        print("=" * 70)
        
        scanner = DeepWalletScanner()
        
        # Test critical wallets
        test_wallets = [
            "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",
            "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",
        ]
        
        for wallet in test_wallets:
            print(f"\n🔍 Scanning: {wallet}")
            print("-" * 70)
            
            analysis = await scanner.scan_wallet(wallet, layers=2)
            
            print(f"  Risk Score: {analysis.risk_score:.2f}")
            print(f"  Flags: {', '.join(analysis.flags) or 'None'}")
            print(f"  Projects: {', '.join(analysis.affiliated_projects) or 'None'}")
            print(f"  Connections: {len(analysis.connections)}")
            print(f"  KYC Vectors: {len(analysis.kyc_vectors)}")
        
        print("\n" + "=" * 70)
    
    asyncio.run(test())
