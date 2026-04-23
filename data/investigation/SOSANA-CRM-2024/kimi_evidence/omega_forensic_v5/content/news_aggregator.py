"""
RMI News Aggregator
===================
Scrapes crypto alert pages and posts to Telegram to build following.
Aggregates news from multiple sources for the RMI community.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
from bs4 import BeautifulSoup
import feedparser


class NewsSource(Enum):
    """Supported news sources."""
    PECKSHIELD = "peckshield"
    CERTIK = "certik"
    SLOWMIST = "slowmist"
    BEOSIN = "beosin"
    BLOCKSEC = "blocksec"
    COINCODEX = "coincodex"
    COINTELEGRAPH = "cointelegraph"
    COINDESK = "coindesk"
    DECRYPT = "decrypt"
    THE_BLOCK = "the_block"
    COINMARKETCAL = "coinmarketcal"
    COINGECKO = "coingecko"
    DEFILLAMA = "defillama"
    L2BEAT = "l2beat"
    TWITTER = "twitter"


class NewsCategory(Enum):
    """News categories."""
    HACK = "hack"
    EXPLOIT = "exploit"
    RUG_PULL = "rug_pull"
    SCAM = "scam"
    SECURITY_ALERT = "security_alert"
    MARKET = "market"
    REGULATION = "regulation"
    PARTNERSHIP = "partnership"
    LISTING = "listing"
    UPDATE = "update"
    GENERAL = "general"


@dataclass
class NewsItem:
    """News article/alert item."""
    id: str
    title: str
    content: str
    source: NewsSource
    source_url: str
    category: NewsCategory
    
    # Metadata
    published_at: datetime
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    
    # Related entities
    affected_tokens: List[str] = field(default_factory=list)
    affected_protocols: List[str] = field(default_factory=list)
    affected_chains: List[str] = field(default_factory=list)
    
    # Financial impact
    estimated_loss_usd: Optional[float] = None
    funds_recovered_usd: Optional[float] = None
    
    # Media
    images: List[str] = field(default_factory=list)
    
    # Processing
    is_verified: bool = False
    is_posted: bool = False
    posted_to: List[str] = field(default_factory=list)
    telegram_message_id: Optional[int] = None
    
    # AI analysis
    summary: Optional[str] = None
    risk_level: Optional[str] = None
    key_takeaways: List[str] = field(default_factory=list)


@dataclass
class NewsSourceConfig:
    """Configuration for a news source."""
    source: NewsSource
    name: str
    url: str
    feed_url: Optional[str] = None
    api_endpoint: Optional[str] = None
    scrape_selector: Optional[str] = None
    enabled: bool = True
    check_interval_minutes: int = 5
    priority: int = 1


class NewsAggregator:
    """
    Aggregates crypto news from multiple sources.
    """
    
    SOURCES: Dict[NewsSource, NewsSourceConfig] = {
        NewsSource.PECKSHIELD: NewsSourceConfig(
            source=NewsSource.PECKSHIELD,
            name="PeckShield",
            url="https://twitter.com/peckshield",
            feed_url=None,
            check_interval_minutes=2,
            priority=1
        ),
        NewsSource.CERTIK: NewsSourceConfig(
            source=NewsSource.CERTIK,
            name="CertiK",
            url="https://twitter.com/certik",
            feed_url=None,
            check_interval_minutes=2,
            priority=1
        ),
        NewsSource.SLOWMIST: NewsSourceConfig(
            source=NewsSource.SLOWMIST,
            name="SlowMist",
            url="https://twitter.com/slowmist_team",
            feed_url=None,
            check_interval_minutes=3,
            priority=2
        ),
        NewsSource.BEOSIN: NewsSourceConfig(
            source=NewsSource.BEOSIN,
            name="Beosin",
            url="https://twitter.com/BeosinAlert",
            feed_interval_minutes=3,
            priority=2
        ),
        NewsSource.BLOCKSEC: NewsSourceConfig(
            source=NewsSource.BLOCKSEC,
            name="BlockSec",
            url="https://twitter.com/BlockSecTeam",
            check_interval_minutes=3,
            priority=2
        ),
        NewsSource.COINTELEGRAPH: NewsSourceConfig(
            source=NewsSource.COINTELEGRAPH,
            name="Cointelegraph",
            url="https://cointelegraph.com",
            feed_url="https://cointelegraph.com/rss",
            check_interval_minutes=10,
            priority=3
        ),
        NewsSource.COINDESK: NewsSourceConfig(
            source=NewsSource.COINDESK,
            name="CoinDesk",
            url="https://coindesk.com",
            feed_url="https://coindesk.com/feed",
            check_interval_minutes=10,
            priority=3
        ),
        NewsSource.DECRYPT: NewsSourceConfig(
            source=NewsSource.DECRYPT,
            name="Decrypt",
            url="https://decrypt.co",
            feed_url="https://decrypt.co/feed",
            check_interval_minutes=10,
            priority=3
        ),
        NewsSource.COINMARKETCAL: NewsSourceConfig(
            source=NewsSource.COINMARKETCAL,
            name="CoinMarketCal",
            url="https://coinmarketcal.com",
            api_endpoint="https://coinmarketcal.com/api/events",
            check_interval_minutes=15,
            priority=4
        ),
    }
    
    def __init__(self):
        self.news_items: List[NewsItem] = []
        self.last_check: Dict[NewsSource, datetime] = {}
        self.scraped_urls: Set[str] = set()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "RMI News Bot/1.0 (Crypto Security News Aggregator)"
                }
            )
        return self.session
    
    async def fetch_all(self) -> List[NewsItem]:
        """Fetch news from all enabled sources."""
        all_news = []
        
        tasks = []
        for source_config in self.SOURCES.values():
            if source_config.enabled:
                tasks.append(self._fetch_from_source(source_config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                print(f"Error fetching news: {result}")
        
        # Remove duplicates
        unique_news = self._deduplicate(all_news)
        
        # Add to main list
        for item in unique_news:
            if item.source_url not in self.scraped_urls:
                self.news_items.append(item)
                self.scraped_urls.add(item.source_url)
        
        return unique_news
    
    async def _fetch_from_source(self, config: NewsSourceConfig) -> List[NewsItem]:
        """Fetch news from a specific source."""
        # Check if we should fetch based on interval
        last = self.last_check.get(config.source)
        if last and (datetime.utcnow() - last).seconds < config.check_interval_minutes * 60:
            return []
        
        self.last_check[config.source] = datetime.utcnow()
        
        # Fetch based on source type
        if config.feed_url:
            return await self._fetch_rss(config)
        elif config.api_endpoint:
            return await self._fetch_api(config)
        else:
            return await self._fetch_twitter(config)
    
    async def _fetch_rss(self, config: NewsSourceConfig) -> List[NewsItem]:
        """Fetch from RSS feed."""
        try:
            session = await self._get_session()
            async with session.get(config.feed_url) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                news_items = []
                for entry in feed.entries[:10]:  # Last 10 items
                    item = self._parse_rss_entry(entry, config)
                    if item:
                        news_items.append(item)
                
                return news_items
                
        except Exception as e:
            print(f"Error fetching RSS from {config.source.value}: {e}")
            return []
    
    def _parse_rss_entry(self, entry: Dict, config: NewsSourceConfig) -> Optional[NewsItem]:
        """Parse RSS entry to NewsItem."""
        try:
            title = entry.get("title", "")
            link = entry.get("link", "")
            description = entry.get("description", "")
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            
            if not title or not link:
                return None
            
            # Parse date
            if published:
                published_at = datetime(*published[:6])
            else:
                published_at = datetime.utcnow()
            
            # Determine category
            category = self._categorize_content(title + " " + description)
            
            # Extract entities
            tokens, protocols, chains = self._extract_entities(title + " " + description)
            
            # Generate ID
            item_id = hashlib.sha256(link.encode()).hexdigest()[:16]
            
            return NewsItem(
                id=item_id,
                title=title,
                content=description,
                source=config.source,
                source_url=link,
                category=category,
                published_at=published_at,
                affected_tokens=tokens,
                affected_protocols=protocols,
                affected_chains=chains
            )
            
        except Exception as e:
            print(f"Error parsing RSS entry: {e}")
            return None
    
    async def _fetch_api(self, config: NewsSourceConfig) -> List[NewsItem]:
        """Fetch from API endpoint."""
        # Implementation for API-based sources
        return []
    
    async def _fetch_twitter(self, config: NewsSourceConfig) -> List[NewsItem]:
        """Fetch from Twitter (requires API access)."""
        # This would use Twitter API v2
        # For now, return empty - implement when API keys available
        return []
    
    def _categorize_content(self, text: str) -> NewsCategory:
        """Categorize content based on keywords."""
        text_lower = text.lower()
        
        # Hack patterns
        if any(word in text_lower for word in ["hack", "hacked", "exploit", "drained", "stolen"]):
            if "flash loan" in text_lower:
                return NewsCategory.EXPLOIT
            return NewsCategory.HACK
        
        # Scam patterns
        if any(word in text_lower for word in ["scam", "rug pull", "rugpull", "honeypot", "fake"]):
            return NewsCategory.SCAM
        
        # Security alerts
        if any(word in text_lower for word in ["alert", "warning", "vulnerability", "critical"]):
            return NewsCategory.SECURITY_ALERT
        
        # Market
        if any(word in text_lower for word in ["price", "pump", "dump", "market", "trading"]):
            return NewsCategory.MARKET
        
        # Regulation
        if any(word in text_lower for word in ["sec", "regulation", "legal", "sued", "court"]):
            return NewsCategory.REGULATION
        
        # Partnership
        if any(word in text_lower for word in ["partnership", "collaboration", "integration"]):
            return NewsCategory.PARTNERSHIP
        
        # Listing
        if any(word in text_lower for word in ["listing", "listed", "exchange"]):
            return NewsCategory.LISTING
        
        return NewsCategory.GENERAL
    
    def _extract_entities(self, text: str) -> tuple:
        """Extract tokens, protocols, and chains from text."""
        text_lower = text.lower()
        
        # Known chains
        chains = []
        chain_keywords = {
            "ethereum": "ETH",
            "solana": "SOL",
            "binance": "BSC",
            "bsc": "BSC",
            "arbitrum": "ARB",
            "optimism": "OP",
            "polygon": "MATIC",
            "avalanche": "AVAX",
            "base": "BASE"
        }
        for keyword, chain in chain_keywords.items():
            if keyword in text_lower:
                chains.append(chain)
        
        # Extract token symbols (uppercase 2-5 chars with $ prefix or standalone)
        tokens = []
        token_pattern = r'\$([A-Z]{2,5})|\b([A-Z]{2,5})\b'
        matches = re.findall(token_pattern, text)
        for match in matches:
            token = match[0] or match[1]
            if token and token not in ["ETH", "SOL", "BTC", "USDT", "USDC"]:
                tokens.append(token)
        
        # Protocols (would be expanded with known protocol list)
        protocols = []
        
        return list(set(tokens)), protocols, list(set(chains))
    
    def _deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate news items."""
        seen = set()
        unique = []
        
        for item in items:
            # Create fingerprint from title + source
            fingerprint = hashlib.sha256(
                f"{item.title}:{item.source.value}".encode()
            ).hexdigest()[:16]
            
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique.append(item)
        
        return unique
    
    async def analyze_with_ai(self, item: NewsItem) -> NewsItem:
        """Analyze news item with AI."""
        # Generate summary
        prompt = f"""
Summarize this crypto security news in 2-3 sentences:

Title: {item.title}
Content: {item.content[:500]}

Summary:
"""
        
        # In production, use LLM
        item.summary = f"[AI Summary] {item.title} - Key security incident affecting {', '.join(item.affected_tokens) if item.affected_tokens else 'crypto markets'}"
        
        # Determine risk level
        if item.category in [NewsCategory.HACK, NewsCategory.EXPLOIT]:
            item.risk_level = "critical"
        elif item.category in [NewsCategory.SCAM, NewsCategory.RUG_PULL]:
            item.risk_level = "high"
        elif item.category == NewsCategory.SECURITY_ALERT:
            item.risk_level = "medium"
        else:
            item.risk_level = "low"
        
        # Key takeaways
        item.key_takeaways = [
            f"Source: {item.source.value}",
            f"Category: {item.category.value}",
            f"Risk Level: {item.risk_level}"
        ]
        
        return item
    
    def get_unposted(self, category: Optional[NewsCategory] = None) -> List[NewsItem]:
        """Get unposted news items."""
        items = [item for item in self.news_items if not item.is_posted]
        
        if category:
            items = [item for item in items if item.category == category]
        
        # Sort by priority and time
        items.sort(key=lambda x: (
            0 if x.category in [NewsCategory.HACK, NewsCategory.EXPLOIT] else 1,
            x.published_at
        ), reverse=True)
        
        return items
    
    def get_stats(self) -> Dict:
        """Get aggregator statistics."""
        total = len(self.news_items)
        posted = len([n for n in self.news_items if n.is_posted])
        
        by_category = {}
        for item in self.news_items:
            cat = item.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        by_source = {}
        for item in self.news_items:
            src = item.source.value
            by_source[src] = by_source.get(src, 0) + 1
        
        return {
            "total_items": total,
            "posted": posted,
            "unposted": total - posted,
            "by_category": by_category,
            "by_source": by_source,
            "last_24h": len([
                n for n in self.news_items
                if n.published_at > datetime.utcnow() - timedelta(hours=24)
            ])
        }


class TelegramPublisher:
    """
    Publishes news to Telegram channels.
    """
    
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def publish(self, item: NewsItem) -> Dict:
        """Publish news item to Telegram."""
        # Format message
        message = self._format_message(item)
        
        try:
            session = await self._get_session()
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.channel_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            
            async with session.post(url, json=payload) as response:
                data = await response.json()
                
                if data.get("ok"):
                    item.is_posted = True
                    item.posted_to.append("telegram")
                    item.telegram_message_id = data["result"]["message_id"]
                    
                    return {
                        "success": True,
                        "message_id": item.telegram_message_id,
                        "channel": self.channel_id
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("description", "Unknown error")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_message(self, item: NewsItem) -> str:
        """Format news item for Telegram."""
        # Emoji based on category
        emoji_map = {
            NewsCategory.HACK: "🚨",
            NewsCategory.EXPLOIT: "⚠️",
            NewsCategory.SCAM: "🚫",
            NewsCategory.RUG_PULL: "💀",
            NewsCategory.SECURITY_ALERT: "🔒",
            NewsCategory.MARKET: "📈",
            NewsCategory.REGULATION: "⚖️",
            NewsCategory.PARTNERSHIP: "🤝",
            NewsCategory.LISTING: "📋",
            NewsCategory.UPDATE: "🔄",
            NewsCategory.GENERAL: "📰"
        }
        
        emoji = emoji_map.get(item.category, "📰")
        
        # Risk indicator
        risk_emoji = ""
        if item.risk_level == "critical":
            risk_emoji = "🔴 "
        elif item.risk_level == "high":
            risk_emoji = "🟠 "
        elif item.risk_level == "medium":
            risk_emoji = "🟡 "
        
        # Build message
        message = f"{emoji} <b>{risk_emoji}{item.title}</b>\n\n"
        
        if item.summary:
            message += f"{item.summary}\n\n"
        
        # Affected entities
        if item.affected_tokens:
            message += f"💎 Tokens: {', '.join([f'${t}' for t in item.affected_tokens])}\n"
        
        if item.affected_chains:
            message += f"⛓ Chains: {', '.join(item.affected_chains)}\n"
        
        if item.estimated_loss_usd:
            message += f"💰 Est. Loss: ${item.estimated_loss_usd:,.2f}\n"
        
        message += f"\n📰 Source: {item.source.value}\n"
        message += f"🔗 <a href='{item.source_url}'>Read More</a>\n"
        message += f"\n#️⃣ #{item.category.value} #crypto #security"
        
        return message
    
    async def publish_batch(self, items: List[NewsItem]) -> Dict:
        """Publish multiple items."""
        results = []
        
        for item in items:
            result = await self.publish(item)
            results.append({
                "item_id": item.id,
                "title": item.title[:50],
                **result
            })
            
            # Small delay to avoid rate limits
            await asyncio.sleep(1)
        
        successful = len([r for r in results if r.get("success")])
        
        return {
            "total": len(items),
            "successful": successful,
            "failed": len(items) - successful,
            "results": results
        }


class XPoster:
    """
    Posts news to X (Twitter).
    """
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
    
    async def post(self, item: NewsItem) -> Dict:
        """Post to X."""
        # Format tweet
        tweet = self._format_tweet(item)
        
        # In production, use Twitter API v2
        # For now, return mock
        item.is_posted = True
        item.posted_to.append("x")
        
        return {
            "success": True,
            "tweet": tweet,
            "note": "Twitter API integration required"
        }
    
    def _format_tweet(self, item: NewsItem) -> str:
        """Format tweet."""
        emoji_map = {
            NewsCategory.HACK: "🚨",
            NewsCategory.EXPLOIT: "⚠️",
            NewsCategory.SCAM: "🚫",
            NewsCategory.RUG_PULL: "💀",
        }
        
        emoji = emoji_map.get(item.category, "📰")
        
        tweet = f"{emoji} {item.title}\n\n"
        
        if item.summary:
            remaining = 280 - len(tweet) - 25  # Reserve space for link
            tweet += item.summary[:remaining] + "\n\n"
        
        tweet += f"Source: {item.source.value}\n"
        tweet += f"{item.source_url}"
        
        return tweet


class NewsScheduler:
    """
    Schedules news posting for optimal engagement.
    """
    
    OPTIMAL_TIMES = {
        "morning": {"hour": 9, "minute": 0},      # 9 AM UTC
        "lunch": {"hour": 12, "minute": 30},      # 12:30 PM UTC
        "afternoon": {"hour": 15, "minute": 0},   # 3 PM UTC
        "evening": {"hour": 19, "minute": 0},     # 7 PM UTC
        "night": {"hour": 21, "minute": 30},      # 9:30 PM UTC
    }
    
    def __init__(self):
        self.scheduled: List[Dict] = []
    
    def schedule_urgent(self, item: NewsItem) -> datetime:
        """Schedule urgent news immediately."""
        return datetime.utcnow()
    
    def schedule_optimal(self, item: NewsItem) -> datetime:
        """Schedule for optimal engagement time."""
        now = datetime.utcnow()
        
        # If critical, post immediately
        if item.category in [NewsCategory.HACK, NewsCategory.EXPLOIT, NewsCategory.RUG_PULL]:
            return now
        
        # Otherwise, find next optimal slot
        for slot_name, slot_time in self.OPTIMAL_TIMES.items():
            scheduled_time = now.replace(hour=slot_time["hour"], minute=slot_time["minute"])
            
            if scheduled_time > now:
                return scheduled_time
        
        # If all slots passed today, schedule for tomorrow morning
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=9, minute=0)
    
    def get_daily_schedule(self) -> Dict:
        """Get daily posting schedule."""
        return {
            "slots": self.OPTIMAL_TIMES,
            "recommended": {
                "morning": "Educational content, safety tips",
                "lunch": "Quick updates, market news",
                "afternoon": "Case studies, analysis",
                "evening": "Major alerts, threads",
                "night": "Recaps, tomorrow's preview"
            }
        }


# ============== FASTAPI ENDPOINTS ==============

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/news", tags=["News Aggregator"])

# Global instances
news_aggregator = NewsAggregator()
telegram_publisher: Optional[TelegramPublisher] = None
x_poster: Optional[XPoster] = None
news_scheduler = NewsScheduler()


def init_publishers(telegram_token: str, telegram_channel: str, x_config: Dict = None):
    """Initialize publishers with credentials."""
    global telegram_publisher, x_poster
    
    if telegram_token and telegram_channel:
        telegram_publisher = TelegramPublisher(telegram_token, telegram_channel)
    
    if x_config:
        x_poster = XPoster(
            x_config.get("api_key"),
            x_config.get("api_secret"),
            x_config.get("access_token"),
            x_config.get("access_secret")
        )


@router.post("/fetch")
async def fetch_news():
    """Fetch news from all sources."""
    items = await news_aggregator.fetch_all()
    
    # Analyze with AI
    for item in items:
        await news_aggregator.analyze_with_ai(item)
    
    return {
        "fetched": len(items),
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "source": item.source.value,
                "category": item.category.value,
                "risk_level": item.risk_level,
                "published_at": item.published_at.isoformat()
            }
            for item in items
        ]
    }


@router.get("/unposted")
async def get_unposted(category: Optional[str] = None):
    """Get unposted news items."""
    cat = None
    if category:
        try:
            cat = NewsCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category")
    
    items = news_aggregator.get_unposted(cat)
    
    return {
        "count": len(items),
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "source": item.source.value,
                "category": item.category.value,
                "risk_level": item.risk_level,
                "summary": item.summary
            }
            for item in items[:20]
        ]
    }


@router.post("/publish/telegram/{item_id}")
async def publish_to_telegram(item_id: str):
    """Publish specific item to Telegram."""
    if not telegram_publisher:
        raise HTTPException(status_code=500, detail="Telegram not configured")
    
    # Find item
    item = None
    for i in news_aggregator.news_items:
        if i.id == item_id:
            item = i
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    result = await telegram_publisher.publish(item)
    return result


@router.post("/publish/telegram/batch")
async def publish_batch_to_telegram(count: int = 5):
    """Publish batch of unposted items to Telegram."""
    if not telegram_publisher:
        raise HTTPException(status_code=500, detail="Telegram not configured")
    
    items = news_aggregator.get_unposted()[:count]
    result = await telegram_publisher.publish_batch(items)
    return result


@router.post("/publish/x/{item_id}")
async def publish_to_x(item_id: str):
    """Publish specific item to X."""
    if not x_poster:
        raise HTTPException(status_code=500, detail="X not configured")
    
    item = None
    for i in news_aggregator.news_items:
        if i.id == item_id:
            item = i
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    result = await x_poster.post(item)
    return result


@router.get("/stats")
async def get_news_stats():
    """Get news aggregator statistics."""
    return news_aggregator.get_stats()


@router.get("/schedule")
async def get_schedule():
    """Get optimal posting schedule."""
    return news_scheduler.get_daily_schedule()


@router.get("/sources")
async def get_sources():
    """Get configured news sources."""
    return {
        "sources": [
            {
                "id": s.source.value,
                "name": s.name,
                "url": s.url,
                "enabled": s.enabled,
                "check_interval": s.check_interval_minutes,
                "priority": s.priority
            }
            for s in news_aggregator.SOURCES.values()
        ]
    }


@router.get("/categories")
async def get_categories():
    """Get news categories."""
    return {
        "categories": [
            {"id": c.value, "name": c.value.replace("_", " ").title()}
            for c in NewsCategory
        ]
    }
