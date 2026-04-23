#!/usr/bin/env python3
"""
Crypto News Engine — Multi-source news aggregator for RMI
Fetches, categorizes, summarizes, and formats crypto news for Telegram channels.

Sources:
  - CoinGecko News API (primary)
  - CryptoPanic (free tier)
  - RSS feeds (Cointelegraph, Coindesk)
  - Birdeye trending (market context)

Categories: market, regulatory, defi, nft, security, macro, technology
"""

import os
import asyncio
import aiohttp
import feedparser
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("news-engine")

# ─── CONFIG ──────────────────────────────────────────────────────────────

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "").strip()
CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY", "").strip()

NEWS_REFRESH_MINUTES = int(os.getenv("NEWS_REFRESH_MINUTES", "15"))
MAX_ARTICLES_PER_BATCH = int(os.getenv("MAX_ARTICLES_PER_BATCH", "10"))

# Category keyword mapping
CATEGORY_MAP = {
    "market": ["price", "rally", "crash", "dump", "pump", "surge", "plunge", " ATH", "bear", "bull", "trading", "volume"],
    "regulatory": ["SEC", "regulation", "CFTC", "lawsuit", "compliance", "AML", "KYC", "sanctions", "legal", "court", "bill", "policy", "govern"],
    "defi": ["DeFi", "yield", "liquidity", "staking", "lending", "borrowing", "AMM", "DEX", "vault", "protocol", "APY", "farm"],
    "nft": ["NFT", "collection", "mint", "OpenSea", "Blur", "digital art", "PFP", "metadata", "royalty"],
    "security": ["hack", "exploit", "rug", "scam", "phishing", "vulnerability", "breach", "drain", "attack", "stolen", "alert", "warning"],
    "macro": ["Fed", "inflation", "interest rate", "CPI", "recession", "GDP", "economy", "dollar", "fiat", "treasury"],
    "technology": ["upgrade", "hard fork", "Layer 2", "L2", "scaling", "sharding", "EVM", "zero-knowledge", "ZK", "rollup", "mainnet"],
    "meme": ["meme", "PEPE", "DOGE", "SHIB", "FLOKI", "BONK", "WIF", "MOG", "community"],
}

# Source display names
SOURCE_NAMES = {
    "coingecko": "CoinGecko",
    "cryptopanic": "CryptoPanic",
    "cointelegraph": "Cointelegraph",
    "coindesk": "CoinDesk",
}


# ─── DATA CLASSES ────────────────────────────────────────────────────────

@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    categories: List[str]
    sentiment: str  # bullish, bearish, neutral
    importance: int  # 1-5
    related_tokens: List[str]
    hash: str  # content hash for dedup

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "published_at": self.published_at.isoformat(),
        }

    def to_telegram_html(self) -> str:
        """Format article as Telegram HTML message."""
        cat_emojis = {
            "market": "📈", "regulatory": "⚖️", "defi": "🌾",
            "nft": "🎨", "security": "🚨", "macro": "🏛",
            "technology": "⚡", "meme": "🐸",
        }
        sent_emojis = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}

        cats = " ".join(f"{cat_emojis.get(c, '📰')} #{c.upper()}" for c in self.categories[:3])
        src = SOURCE_NAMES.get(self.source, self.source)

        text = (
            f"<b>{self.title}</b>\n\n"
            f"{self.description[:350]}{'...' if len(self.description) > 350 else ''}\n\n"
            f"{sent_emojis.get(self.sentiment, '⚪')} <i>Sentiment: {self.sentiment.title()}</i>\n"
            f"📰 <i>Source: {src}</i>\n"
            f"🏷 {cats}\n"
            f"🔗 <a href='{self.url}'>Read Full Article</a>\n"
            f"⏰ {self.published_at.strftime('%H:%M UTC, %b %d')}"
        )
        return text

    def to_telegram_markdown(self) -> str:
        """Format article as Telegram MarkdownV2."""
        cat_tags = " ".join(f"#{c}" for c in self.categories[:3])
        src = SOURCE_NAMES.get(self.source, self.source)

        sent_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(self.sentiment, "⚪")

        # Escape for MarkdownV2
        def _e(t: str) -> str:
            for c in r"_*[]()~`>#+-=|{}.!":
                t = t.replace(c, f"\\{c}")
            return t

        text = (
            f"📰 *{_e(self.title)}*\n\n"
            f"{_e(self.description[:300])}{'...' if len(self.description) > 300 else ''}\n\n"
            f"{sent_emoji} Sentiment: `{_e(self.sentiment.title())}`\n"
            f"📡 Source: `{_e(src)}`\n"
            f"🏷 {cat_tags}\n"
            f"🔗 [Read Full Article]({self.url})\n"
            f"⏰ `{self.published_at.strftime('%H:%M UTC, %b %d')}`"
        )
        return text

    def to_digest_format(self, index: int) -> str:
        """Short format for digest lists."""
        sent_dot = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(self.sentiment, "⚪")
        return (
            f"{index}\. {sent_dot} *{self._esc(self.title)}*\n"
            f"    🏷 {' '.join(f'#{c}' for c in self.categories[:2])} "
            f"🔗 [Read more]({self.url})\n"
        )

    def _esc(self, t: str) -> str:
        for c in r"_*[]()~`>#+-=|{}.!":
            t = t.replace(c, f"\\{c}")
        return t


# ─── NEWS ENGINE ─────────────────────────────────────────────────────────

class CryptoNewsEngine:
    """Aggregates crypto news from multiple sources."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.seen_hashes: set = set()
        self.articles: List[NewsArticle] = []
        self.last_fetch: Optional[datetime] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    # ─── Source: CoinGecko ──────────────────────────────────────────────

    async def _fetch_coingecko(self) -> List[NewsArticle]:
        """Fetch news from CoinGecko API."""
        if not COINGECKO_API_KEY:
            return []

        s = await self._get_session()
        articles = []

        try:
            url = "https://api.coingecko.com/api/v3/news"
            headers = {"x-cg-demo-api-key": COINGECKO_API_KEY}

            async with s.get(url, headers=headers, params={"per_page": 25}) as resp:
                if resp.status != 200:
                    logger.warning(f"CoinGecko news HTTP {resp.status}")
                    return []
                data = await resp.json()

            for item in data.get("data", []):
                try:
                    art = self._parse_coingecko_item(item)
                    if art and art.hash not in self.seen_hashes:
                        articles.append(art)
                except Exception as e:
                    logger.debug(f"Parse error: {e}")

        except Exception as e:
            logger.warning(f"CoinGecko fetch failed: {e}")

        logger.info(f"CoinGecko: fetched {len(articles)} articles")
        return articles

    def _parse_coingecko_item(self, item: dict) -> Optional[NewsArticle]:
        title = item.get("title", "")
        desc = item.get("description", "") or ""
        url = item.get("url", "")
        source = "coingecko"

        # Parse date
        pub_str = item.get("updated_at", item.get("created_at", ""))
        try:
            published = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
        except:
            published = datetime.utcnow()

        # Sentiment analysis from title/description
        sentiment = self._analyze_sentiment(title + " " + desc)

        # Categorize
        categories = self._categorize(title + " " + desc)

        # Related tokens
        tokens = [t.get("name", "") for t in item.get("coins", [])[:5]]

        # Hash for dedup
        content_hash = hashlib.md5(f"{title}:{url}".encode()).hexdigest()

        return NewsArticle(
            title=title, description=desc, url=url, source=source,
            published_at=published, categories=categories, sentiment=sentiment,
            importance=self._score_importance(title, categories, sentiment),
            related_tokens=tokens, hash=content_hash,
        )

    # ─── Source: CryptoPanic ────────────────────────────────────────────

    async def _fetch_cryptopanic(self) -> List[NewsArticle]:
        """Fetch news from CryptoPanic."""
        if not CRYPTOPANIC_API_KEY:
            return []

        s = await self._get_session()
        articles = []

        try:
            url = f"https://cryptopanic.com/api/v1/posts/"
            params = {"auth_token": CRYPTOPANIC_API_KEY, "public": "true", "kind": "news"}

            async with s.get(url, params=params) as resp:
                if resp.status != 200:
                    logger.warning(f"CryptoPanic HTTP {resp.status}")
                    return []
                data = await resp.json()

            for item in data.get("results", []):
                try:
                    art = self._parse_cryptopanic_item(item)
                    if art and art.hash not in self.seen_hashes:
                        articles.append(art)
                except Exception as e:
                    logger.debug(f"Parse error: {e}")

        except Exception as e:
            logger.warning(f"CryptoPanic fetch failed: {e}")

        logger.info(f"CryptoPanic: fetched {len(articles)} articles")
        return articles

    def _parse_cryptopanic_item(self, item: dict) -> Optional[NewsArticle]:
        title = item.get("title", "")
        url = item.get("url", "")
        source = "cryptopanic"

        published = datetime.utcnow()  # CryptoPanic doesn't always have reliable dates

        # Votes indicate sentiment
        votes = item.get("votes", {})
        bullish = votes.get("positive", 0)
        bearish = votes.get("negative", 0)
        sentiment = "bullish" if bullish > bearish else "bearish" if bearish > bullish else "neutral"

        categories = self._categorize(title)
        content_hash = hashlib.md5(f"{title}:{url}".encode()).hexdigest()

        return NewsArticle(
            title=title, description=title, url=url, source=source,
            published_at=published, categories=categories, sentiment=sentiment,
            importance=self._score_importance(title, categories, sentiment),
            related_tokens=[], hash=content_hash,
        )

    # ─── Source: RSS Feeds ──────────────────────────────────────────────

    async def _fetch_rss(self, feed_url: str, source_name: str) -> List[NewsArticle]:
        """Fetch and parse an RSS feed."""
        s = await self._get_session()
        articles = []

        try:
            async with s.get(feed_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return []
                content = await resp.text()

            feed = feedparser.parse(content)

            for entry in feed.entries[:15]:
                try:
                    title = entry.get("title", "")
                    url = entry.get("link", "")
                    desc = entry.get("summary", "") or entry.get("description", "") or title

                    # Parse date
                    pub_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                    if pub_parsed:
                        published = datetime(*pub_parsed[:6])
                    else:
                        published = datetime.utcnow()

                    # Skip articles older than 48 hours
                    if datetime.utcnow() - published > timedelta(hours=48):
                        continue

                    sentiment = self._analyze_sentiment(title + " " + desc)
                    categories = self._categorize(title + " " + desc)
                    content_hash = hashlib.md5(f"{title}:{url}".encode()).hexdigest()

                    art = NewsArticle(
                        title=title, description=desc, url=url, source=source_name,
                        published_at=published, categories=categories, sentiment=sentiment,
                        importance=self._score_importance(title, categories, sentiment),
                        related_tokens=[], hash=content_hash,
                    )
                    if art.hash not in self.seen_hashes:
                        articles.append(art)

                except Exception as e:
                    logger.debug(f"RSS parse error: {e}")

        except Exception as e:
            logger.warning(f"RSS fetch failed for {feed_url}: {e}")

        logger.info(f"RSS {source_name}: fetched {len(articles)} articles")
        return articles

    # ─── Intelligence Layer ─────────────────────────────────────────────

    def _categorize(self, text: str) -> List[str]:
        """Categorize article based on keyword matching."""
        text_lower = text.lower()
        matched = []
        for category, keywords in CATEGORY_MAP.items():
            if any(kw.lower() in text_lower for kw in keywords):
                matched.append(category)
        return matched if matched else ["market"]

    def _analyze_sentiment(self, text: str) -> str:
        """Simple keyword-based sentiment analysis."""
        bullish_words = ["surge", "rally", "pump", "bull", "ATH", "breakout", "gain", "rise", "soar", "moon", "green", "up", "growth", "adopt", "partnership", "launch"]
        bearish_words = ["crash", "dump", "bear", "plunge", "drop", "fall", "decline", "hack", "exploit", "scam", "rug", "ban", "lawsuit", "red", "down", "sell", "fear"]

        text_lower = text.lower()
        bull_count = sum(1 for w in bullish_words if w in text_lower)
        bear_count = sum(1 for w in bearish_words if w in text_lower)

        if bull_count > bear_count:
            return "bullish"
        elif bear_count > bull_count:
            return "bearish"
        return "neutral"

    def _score_importance(self, title: str, categories: List[str], sentiment: str) -> int:
        """Score article importance 1-5."""
        score = 2  # baseline

        # Security/regulatory news is high importance
        if "security" in categories or "regulatory" in categories:
            score += 2

        # Major market events
        if any(w in title.lower() for w in ["crash", "hack", "exploit", "SEC", "binance", "coinbase"]):
            score += 1

        # Strong sentiment
        if sentiment != "neutral":
            score += 1

        return min(score, 5)

    # ─── Public API ─────────────────────────────────────────────────────

    async def fetch_all(self) -> List[NewsArticle]:
        """Fetch from all sources, deduplicate, sort by importance."""
        logger.info("Starting news fetch cycle...")

        tasks = [
            self._fetch_coingecko(),
            self._fetch_cryptopanic(),
            self._fetch_rss("https://cointelegraph.com/rss", "cointelegraph"),
            self._fetch_rss("https://coindesk.com/arc/outboundfeeds/rss/", "coindesk"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles = []
        for result in results:
            if isinstance(result, list):
                for art in result:
                    if art.hash not in self.seen_hashes:
                        self.seen_hashes.add(art.hash)
                        all_articles.append(art)

        # Sort by importance desc, then date desc
        all_articles.sort(key=lambda a: (-a.importance, -a.published_at.timestamp()))

        self.articles = all_articles[:100]  # Keep last 100
        self.last_fetch = datetime.utcnow()

        logger.info(f"Total new articles: {len(all_articles)}")
        return all_articles

    def get_by_category(self, category: str, limit: int = 5) -> List[NewsArticle]:
        """Get articles filtered by category."""
        filtered = [a for a in self.articles if category.lower() in [c.lower() for c in a.categories]]
        return filtered[:limit]

    def get_digest(self, limit: int = 10) -> str:
        """Generate a digest of top articles."""
        top = self.articles[:limit]
        if not top:
            return "📭 No news articles available yet. Run /newsrefresh to fetch."

        lines = [
            f"📰 *Crypto Intelligence Digest*",
            f"🕐 `{datetime.utcnow().strftime('%H:%M UTC, %b %d')}`",
            f"📊 *{len(self.articles)}* articles aggregated\n",
            "*Top Stories:*\n",
        ]

        for i, art in enumerate(top, 1):
            sent = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(art.sentiment, "⚪")
            cats = " ".join(f"#{c}" for c in art.categories[:2])
            lines.append(f"{i}\. {sent} *{self._esc(art.title)}*")
            lines.append(f"    🏷 {cats} 🔗 [Read]({art.url})\n")

        # Category breakdown
        lines.append("\n*By Category:*")
        for cat in ["market", "security", "regulatory", "defi", "technology", "macro"]:
            count = len([a for a in self.articles if cat in [c.lower() for c in a.categories]])
            if count > 0:
                emoji = {"market": "📈", "security": "🚨", "regulatory": "⚖️", "defi": "🌾", "technology": "⚡", "macro": "🏛"}.get(cat, "📰")
                lines.append(f"  {emoji} #{cat}: `{count}`")

        return "\n".join(lines)

    def get_security_alerts(self, limit: int = 5) -> List[NewsArticle]:
        """Get security-related articles (for alerts channel)."""
        return [a for a in self.articles if "security" in [c.lower() for c in a.categories]][:limit]

    def get_market_movers(self, limit: int = 5) -> List[NewsArticle]:
        """Get market-moving articles (for alpha channel)."""
        market_articles = [a for a in self.articles if "market" in [c.lower() for c in a.categories]]
        # Sort by importance
        market_articles.sort(key=lambda a: -a.importance)
        return market_articles[:limit]

    def _esc(self, t: str) -> str:
        for c in r"_*[]()~`>#+-=|{}.!":
            t = t.replace(c, f"\\{c}")
        return t

    def format_for_channel(self, article: NewsArticle) -> str:
        """Format a single article for channel posting."""
        return article.to_telegram_markdown()


# ─── Singleton ───────────────────────────────────────────────────────────

_engine: Optional[CryptoNewsEngine] = None


def get_news_engine() -> CryptoNewsEngine:
    global _engine
    if _engine is None:
        _engine = CryptoNewsEngine()
    return _engine
