"""
Social Sentiment Agent
Fetches social mentions and scores sentiment.
"""
import os
import re
import logging
from datetime import datetime
from urllib.request import urlopen, Request

logger = logging.getLogger("sentiment_agent")


def _get_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def simple_sentiment(text: str) -> str:
    """Naive sentiment scoring."""
    t = text.lower()
    pos = len(re.findall(r"bull|pump|moon|gain|profit|up|green|buy", t))
    neg = len(re.findall(r"bear|dump|rug|scam|loss|down|red|sell", t))
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def run():
    logger.info("Sentiment agent running")
    sb = _get_supabase()

    # Placeholder: fetch from a news source or social API
    mentions = []
    try:
        req = Request("https://api.coingecko.com/api/v3/search/trending", headers={"User-Agent": "RugMuncher/1.0"})
        with urlopen(req, timeout=20) as resp:
            data = eval(resp.read().decode())  # simple parse
            coins = data.get("coins", [])
            for c in coins[:5]:
                mentions.append({
                    "token": c["item"]["name"],
                    "symbol": c["item"]["symbol"],
                    "sentiment": "neutral",
                    "source": "coingecko_trending",
                    "checked_at": datetime.utcnow().isoformat(),
                })
    except Exception as e:
        logger.warning(f"Trending fetch failed: {e}")

    if sb and mentions:
        try:
            for m in mentions:
                sb.table("social_sentiment").insert(m).execute()
        except Exception:
            pass

    logger.info(f"Sentiment agent complete: {len(mentions)} mentions")
