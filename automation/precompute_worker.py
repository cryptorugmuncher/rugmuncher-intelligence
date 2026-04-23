#!/usr/bin/env python3
"""
Pre-compute Worker - Run on GCP Cloud Run free tier
Nightly batch job: Pre-compute wallet clusters, cache to Dragonfly
"""
import asyncio
import json
import os
import networkx as nx
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple
import redis.asyncio as redis
from dataclasses import dataclass

@dataclass
class WalletCluster:
    addresses: Set[str]
    type: str  # "gas_funding", "co_spending", "contract"
    risk_score: float
    confidence: float

class ClusteringEngine:
    """Gas-funding heuristic clustering using NetworkX"""

    def __init__(self, dragonfly_url: str = "redis://localhost:6379"):
        self.redis = None
        self.dragonfly_url = dragonfly_url

    async def connect(self):
        self.redis = await redis.from_url(
            self.dragonfly_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def close(self):
        if self.redis:
            await self.redis.close()

    def build_gas_funding_graph(self, holders: List[dict]) -> nx.DiGraph:
        """
        Build directed graph where edges represent gas funding relationships.
        If wallet A funded wallet B's first transaction, edge A -> B.
        """
        G = nx.DiGraph()

        # Add all holders as nodes
        for holder in holders:
            G.add_node(
                holder["address"],
                balance=holder.get("balance", 0),
                tx_count=holder.get("tx_count", 0)
            )

        # Find funding relationships (simplified heuristic)
        # In production: query transaction history via RPC
        for i, holder1 in enumerate(holders):
            for holder2 in holders[i+1:]:
                # Simulate funding detection
                # Real: Check if holder1 sent ETH to holder2 before any other tx
                if self._is_funder(holder1, holder2):
                    G.add_edge(holder1["address"], holder2["address"], type="gas_funding")

        return G

    def _is_funder(self, wallet1: dict, wallet2: dict) -> bool:
        """Check if wallet1 funded wallet2's gas"""
        # Placeholder - real implementation queries blockchain
        # Returns True if wallet1 sent first gas to wallet2
        return False  # Implement actual check

    def detect_clusters(self, G: nx.DiGraph) -> List[WalletCluster]:
        """Detect Sybil clusters using community detection"""
        clusters = []

        # Convert to undirected for community detection
        G_undirected = G.to_undirected()

        # Louvain community detection (fast, scalable)
        communities = nx.community.louvain_communities(
            G_undirected,
            resolution=1.0,
            seed=42
        )

        for community in communities:
            if len(community) < 2:
                continue

            # Analyze cluster characteristics
            subgraph = G.subgraph(community)

            # Calculate metrics
            density = nx.density(subgraph)
            avg_clustering = nx.average_clustering(subgraph.to_undirected())

            # Determine cluster type
            cluster_type = self._classify_cluster(subgraph, density, avg_clustering)

            # Calculate risk score (0-100)
            risk_score = self._calculate_risk(subgraph, density, avg_clustering)

            clusters.append(WalletCluster(
                addresses=community,
                type=cluster_type,
                risk_score=risk_score,
                confidence=min(len(community) / 10, 1.0)  # More nodes = higher confidence
            ))

        return clusters

    def _classify_cluster(self, G: nx.DiGraph, density: float, clustering: float) -> str:
        """Classify cluster type based on graph properties"""
        if density > 0.7 and clustering > 0.5:
            return "sybil_dispersal"
        elif density > 0.3:
            return "gas_funding"
        elif nx.is_tree(G):
            return "hierarchical"
        else:
            return "loose"

    def _calculate_risk(self, G: nx.DiGraph, density: float, clustering: float) -> float:
        """Calculate risk score (0-100)"""
        score = 0

        # High density = coordinated (suspicious)
        score += density * 30

        # High clustering = tight group (suspicious)
        score += clustering * 30

        # Large clusters more suspicious
        score += min(len(G.nodes) / 100, 20)

        # Tree structures often indicate dispersal patterns
        if nx.is_tree(G):
            score += 20

        return min(score, 100)

    async def precompute_token(self, token_address: str, chain: str = "eth") -> dict:
        """Pre-compute all clusters for a token"""

        # Check if already cached and fresh (< 24 hours)
        cache_key = f"clusters:{chain}:{token_address}"
        cached = await self.redis.get(cache_key)

        if cached:
            data = json.loads(cached)
            cached_time = datetime.fromisoformat(data["computed_at"])
            if datetime.now() - cached_time < timedelta(hours=24):
                return data

        # Fetch holders (in production: from RPC or subgraph)
        holders = await self._fetch_holders(token_address, chain)

        if len(holders) < 10:
            return {"error": "Insufficient holders"}

        # Build graph
        G = self.build_gas_funding_graph(holders)

        # Detect clusters
        clusters = self.detect_clusters(G)

        # Prepare result
        result = {
            "token": token_address,
            "chain": chain,
            "total_holders": len(holders),
            "total_clusters": len(clusters),
            "high_risk_clusters": sum(1 for c in clusters if c.risk_score > 70),
            "clusters": [
                {
                    "addresses": list(c.addresses),
                    "type": c.type,
                    "risk_score": c.risk_score,
                    "confidence": c.confidence,
                    "size": len(c.addresses)
                }
                for c in sorted(clusters, key=lambda x: x.risk_score, reverse=True)
            ],
            "graph_stats": {
                "nodes": len(G.nodes),
                "edges": len(G.edges),
                "density": nx.density(G),
                "avg_clustering": nx.average_clustering(G.to_undirected())
            },
            "computed_at": datetime.now().isoformat()
        }

        # Cache for 24 hours
        await self.redis.setex(
            cache_key,
            timedelta(hours=24),
            json.dumps(result)
        )

        # Also cache individual cluster lookups
        for cluster in clusters:
            for addr in cluster.addresses:
                await self.redis.hset(
                    f"wallet:{chain}:{addr}:clusters",
                    mapping={
                        token_address: json.dumps({
                            "type": cluster.type,
                            "risk_score": cluster.risk_score,
                            "size": cluster.size
                        })
                    }
                )

        return result

    async def _fetch_holders(self, token_address: str, chain: str) -> List[dict]:
        """Fetch token holders from RPC or cached data"""
        # In production: query blockchain or use subgraph
        # Placeholder: return mock data
        return [
            {"address": f"0x{i:040x}", "balance": 1000000, "tx_count": 10}
            for i in range(100)  # Mock 100 holders
        ]

    async def get_cached_graph(self, token_address: str, chain: str = "eth") -> Optional[dict]:
        """Get pre-computed graph from cache"""
        cache_key = f"clusters:{chain}:{token_address}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None


# Cloud Run entry point
async def cloud_run_handler(request):
    """HTTP handler for Cloud Run"""
    import aiohttp
    from aiohttp import web

    engine = ClusteringEngine(os.getenv("DRAGONFLY_URL", "redis://localhost:6379"))
    await engine.connect()

    try:
        data = await request.json()
        token = data.get("token")
        chain = data.get("chain", "eth")

        if not token:
            return web.json_response({"error": "Missing token"}, status=400)

        result = await engine.precompute_token(token, chain)
        return web.json_response(result)

    finally:
        await engine.close()


# Local testing
async def main():
    engine = ClusteringEngine()
    await engine.connect()

    try:
        # Precompute a token
        result = await engine.precompute_token(
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
            "eth"
        )
        print(json.dumps(result, indent=2))
    finally:
        await engine.close()

if __name__ == "__main__":
    asyncio.run(main())
