#!/usr/bin/env python3
"""
RPC Rotator - Max out free tiers across multiple providers
Fighter jet speed at zero cost through intelligent load balancing
"""
import asyncio
import aiohttp
import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, List
import json

@dataclass
class RPCEndpoint:
    name: str
    url: str
    daily_limit: int
    priority: int = 1
    weight: float = 1.0

class RPCRotator:
    """Intelligent RPC rotation across free tiers"""

    ENDPOINTS = [
        # Primary: Ankr (10M calls/day free)
        RPCEndpoint("ankr", "https://rpc.ankr.com/eth", 10_000_000, priority=1, weight=2.0),
        RPCEndpoint("ankr_bsc", "https://rpc.ankr.com/bsc", 10_000_000, priority=1, weight=2.0),

        # Backup: Alchemy (300M CU/month)
        RPCEndpoint("alchemy", "https://eth-mainnet.g.alchemy.com/v2/", 300_000_000, priority=2),
        RPCEndpoint("alchemy_bsc", "https://bnb-mainnet.g.alchemy.com/v2/", 300_000_000, priority=2),

        # Fallback: Public nodes (no key needed)
        RPCEndpoint("public_eth", "https://ethereum.publicnode.com", float('inf'), priority=3, weight=0.5),
        RPCEndpoint("public_bsc", "https://bsc.publicnode.com", float('inf'), priority=3, weight=0.5),
        RPCEndpoint("1rpc", "https://1rpc.io/eth", float('inf'), priority=3, weight=0.5),

        # Backup backup: Cloudflare (unlimited but rate limited)
        RPCEndpoint("cloudflare", "https://cloudflare-eth.com", float('inf'), priority=4, weight=0.3),
    ]

    def __init__(self):
        self.usage: Dict[str, int] = {e.name: 0 for e in self.ENDPOINTS}
        self.daily_reset = datetime.now() + timedelta(days=1)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=20),
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    def _check_reset(self):
        """Reset counters daily"""
        if datetime.now() > self.daily_reset:
            self.usage = {e.name: 0 for e in self.ENDPOINTS}
            self.daily_reset = datetime.now() + timedelta(days=1)

    def get_endpoint(self, chain: str = "eth") -> RPCEndpoint:
        """Get best available endpoint for chain"""
        self._check_reset()

        # Filter by chain and availability
        candidates = [
            e for e in self.ENDPOINTS
            if chain in e.name or (chain == "eth" and "eth" in e.url)
            and self.usage[e.name] < e.daily_limit * 0.95  # 95% threshold
        ]

        if not candidates:
            # All exhausted, use lowest priority
            candidates = [e for e in self.ENDPOINTS if chain in e.name or "eth" in e.url]

        # Weighted random selection by priority and remaining quota
        weights = []
        for e in candidates:
            remaining = 1 - (self.usage[e.name] / e.daily_limit) if e.daily_limit != float('inf') else 1
            weight = e.weight * remaining * (5 - e.priority)
            weights.append(max(weight, 0.1))

        total = sum(weights)
        weights = [w/total for w in weights]

        return random.choices(candidates, weights=weights, k=1)[0]

    async def call(self, method: str, params: List, chain: str = "eth") -> dict:
        """Make JSON-RPC call with automatic retry and rotation"""
        max_retries = 3

        for attempt in range(max_retries):
            endpoint = self.get_endpoint(chain)

            try:
                payload = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": 1
                }

                async with self.session.post(
                    endpoint.url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    self.usage[endpoint.name] += 1

                    if response.status == 429:  # Rate limited
                        continue

                    data = await response.json()

                    if "error" in data:
                        raise Exception(f"RPC Error: {data['error']}")

                    return data["result"]

            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                raise

            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5)
                    continue
                raise

        raise Exception("All RPC endpoints exhausted")

    async def batch_call(self, calls: List[tuple], chain: str = "eth") -> List[dict]:
        """Batch multiple calls to single endpoint for efficiency"""
        endpoint = self.get_endpoint(chain)

        payload = [
            {"jsonrpc": "2.0", "method": method, "params": params, "id": i}
            for i, (method, params) in enumerate(calls)
        ]

        async with self.session.post(
            endpoint.url,
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            self.usage[endpoint.name] += len(calls)
            data = await response.json()
            return [r.get("result") for r in sorted(data, key=lambda x: x.get("id", 0))]

    def get_stats(self) -> dict:
        """Get usage statistics"""
        return {
            "usage": self.usage,
            "reset_time": self.daily_reset.isoformat(),
            "efficiency": sum(1 for u in self.usage.values() if u > 0) / len(self.usage)
        }


# Usage example
async def main():
    async with RPCRotator() as rpc:
        # Get latest block
        block = await rpc.call("eth_getBlockByNumber", ["latest", False])
        print(f"Latest block: {block['number']}")

        # Batch fetch multiple balances
        wallets = ["0x...", "0x...", "0x..."]
        balances = await rpc.batch_call([
            ("eth_getBalance", [w, "latest"]) for w in wallets
        ])
        print(f"Balances: {balances}")

        print(f"Stats: {rpc.get_stats()}")

if __name__ == "__main__":
    asyncio.run(main())
