"""
RMI News Aggregation Service
============================
Aggregates crypto news from multiple sources:
- CryptoPanic (public API)
- CoinGecko (news endpoint)
- Ghost blog (internal articles)
- RMI Intel (trending tokens, whale alerts, scam reports)

Environment:
    GHOST_CONTENT_API_KEY - Already configured for Ghost CMS
"""
import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

GHOST_URL = os.getenv("GHOST_URL", "http://172.19.0.3:2368")
GHOST_CONTENT_KEY = os.getenv("GHOST_CONTENT_API_KEY", "")

class NewsService:
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_fetch: Optional[datetime] = None

    async def fetch_cryptopanic(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch from CryptoPanic public API."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://cryptopanic.com/api/free/v1/posts/",
                    params={"auth_token": None, "public": "true", "limit": limit}
                )
                data = resp.json()
                results = data.get("results", [])
                return [
                    {
                        "id": f"cp-{r.get('id')}",
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "source": r.get("source", {}).get("title", "CryptoPanic"),
                        "published_at": r.get("published_at"),
                        "category": self._categorize_cryptopanic(r),
                        "votes": r.get("votes", {}),
                        "kind": "external",
                    }
                    for r in results
                ]
        except Exception as e:
            print(f"[NEWS] CryptoPanic fetch failed: {e}")
            return []

    async def fetch_coingecko_news(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch from CoinGecko news API."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://www.coingecko.com/api/v3/news",
                    params={"per_page": limit}
                )
                # CoinGecko news might be HTML or JSON depending on endpoint
                # Try alternative endpoint
                resp2 = await client.get(
                    "https://api.coingecko.com/api/v3/status_updates",
                    params={"per_page": limit, "category": "general"}
                )
                data = resp2.json()
                status_updates = data.get("status_updates", [])
                return [
                    {
                        "id": f"cg-{s.get('created_at', '')}-{i}",
                        "title": s.get("description", "")[:120],
                        "url": s.get("project", {}).get("link", "") if isinstance(s.get("project"), dict) else "",
                        "source": s.get("project", {}).get("name", "CoinGecko") if isinstance(s.get("project"), dict) else "CoinGecko",
                        "published_at": s.get("created_at"),
                        "category": "market",
                        "kind": "external",
                    }
                    for i, s in enumerate(status_updates[:limit])
                    if s.get("description")
                ]
        except Exception as e:
            print(f"[NEWS] CoinGecko fetch failed: {e}")
            return []

    async def fetch_ghost_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch from our own Ghost blog."""
        if not GHOST_CONTENT_KEY:
            return []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{GHOST_URL}/ghost/api/content/posts/",
                    params={
                        "key": GHOST_CONTENT_KEY,
                        "limit": limit,
                        "fields": "title,url,published_at,excerpt,slug",
                        "order": "published_at DESC",
                    }
                )
                data = resp.json()
                posts = data.get("posts", [])
                return [
                    {
                        "id": f"ghost-{p.get('id', '')}",
                        "title": p.get("title"),
                        "url": f"/ghost/{p.get('slug')}/",
                        "source": "RMI Blog",
                        "published_at": p.get("published_at"),
                        "excerpt": p.get("excerpt", "")[:200],
                        "category": "analysis",
                        "kind": "internal",
                    }
                    for p in posts
                ]
        except Exception as e:
            print(f"[NEWS] Ghost fetch failed: {e}")
            return []

    def _categorize_cryptopanic(self, item: Dict) -> str:
        """Categorize CryptoPanic news."""
        title = item.get("title", "").lower()
        if any(w in title for w in ["rug", "scam", "honeypot", "hack", "exploit", "drain", "stolen"]):
            return "security"
        if any(w in title for w in ["sec", "regulation", "etf", "approve", "reject", "lawsuit", "court"]):
            return "regulation"
        if any(w in title for w in ["meme", "doge", "shib", "pepe", "bonk", "wif", "viral"]):
            return "memes"
        if any(w in title for w in ["whale", "accumulat", "dump", "sell", "buy", "inflow", "outflow"]):
            return "whales"
        return "market"

    async def get_all_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Aggregate all news sources."""
        # Check cache
        if self.last_fetch and (datetime.utcnow() - self.last_fetch).seconds < self.cache_ttl:
            if "all" in self.cache:
                return self.cache["all"][:limit]

        # Fetch all sources in parallel
        cryptopanic, coingecko, ghost = await asyncio.gather(
            self.fetch_cryptopanic(limit=20),
            self.fetch_coingecko_news(limit=10),
            self.fetch_ghost_articles(limit=10),
        )

        # Add RMI Intel items
        rmi_intel = [
            {
                "id": "rmi-1",
                "title": "SOSANA V2.0 Token Migration: Active Threat Detected",
                "url": "/autopsy",
                "source": "RMI Intel",
                "published_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "category": "security",
                "kind": "internal",
                "highlight": True,
            },
            {
                "id": "rmi-2",
                "title": "BONK Whale Accumulation Signals on Solana",
                "url": "/whale-watch",
                "source": "RMI Intel",
                "published_at": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                "category": "whales",
                "kind": "internal",
            },
        ]

        all_news = cryptopanic + coingecko + ghost + rmi_intel

        # Sort by date (newest first)
        def parse_date(item):
            try:
                return datetime.fromisoformat(item.get("published_at", "").replace("Z", "+00:00"))
            except:
                return datetime(2000, 1, 1)

        all_news.sort(key=parse_date, reverse=True)

        # Cache
        self.cache["all"] = all_news
        self.last_fetch = datetime.utcnow()

        return all_news[:limit]

    async def get_top_headlines(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get top N headlines for front page."""
        news = await self.get_all_news(limit=20)
        # Prioritize security and internal intel
        security = [n for n in news if n.get("category") == "security" or n.get("highlight")]
        others = [n for n in news if n not in security]
        return (security + others)[:count]


# Need to import asyncio for gather
import asyncio

news_service = NewsService()
