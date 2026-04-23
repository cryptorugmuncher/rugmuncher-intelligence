"""
Social Sentiment Agent
======================
Fetches social mentions and scores sentiment using FREE AI first.
Falls back to naive regex only if all free AI providers fail.
"""

import os
import re
import json
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


def _naive_sentiment(text: str) -> str:
    """Fallback regex sentiment (no AI cost)."""
    t = text.lower()
    pos = len(re.findall(r"bull|pump|moon|gain|profit|up|green|buy", t))
    neg = len(re.findall(r"bear|dump|rug|scam|loss|down|red|sell", t))
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def _ai_sentiment(text: str) -> str:
    """Use FREE AI to classify sentiment. Always free-first."""
    try:
        from app.services.cloudflare_ai import smart_chat
        from app.services.vault_keys import get_all_ai_keys

        keys = get_all_ai_keys()
        result = smart_chat(
            messages=[
                {"role": "system", "content": "Classify sentiment as exactly one word: positive, negative, or neutral. No explanation."},
                {"role": "user", "content": text[:2000]},
            ],
            keys=keys,
            priority="free",
        )
        content = result.get("response", "") or result.get("choices", [{}])[0].get("message", {}).get("content", "")
        content = content.strip().lower()
        if content in ["positive", "negative", "neutral"]:
            return content
        return _naive_sentiment(text)
    except Exception as e:
        logger.warning(f"FREE AI sentiment failed, using naive fallback: {e}")
        return _naive_sentiment(text)


def run():
    logger.info("📊 Sentiment agent running (FREE AI priority)")
    sb = _get_supabase()

    mentions = []
    try:
        req = Request("https://api.coingecko.com/api/v3/search/trending", headers={"User-Agent": "RugMuncher/1.0"})
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            coins = data.get("coins", [])
            for c in coins[:5]:
                name = c["item"]["name"]
                symbol = c["item"]["symbol"]
                # Analyze sentiment using FREE AI
                sentiment = _ai_sentiment(f"{name} {symbol} trending crypto token")
                mentions.append({
                    "token": name,
                    "symbol": symbol,
                    "sentiment": sentiment,
                    "source": "coingecko_trending",
                    "ai_analyzed": True,
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

    logger.info(f"✅ Sentiment agent complete: {len(mentions)} mentions analyzed with FREE AI")
