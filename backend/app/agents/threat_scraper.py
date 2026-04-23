"""
Threat Intel Scraper
====================
Fetches public threat data and uses FREE AI to analyze and summarize.
Always prioritizes free providers (Workers AI, OpenRouter free, Gemini free tier).
"""

import os
import json
import logging
from datetime import datetime
from urllib.request import urlopen, Request

logger = logging.getLogger("threat_scraper")

SOURCES = [
    {"name": "chainabuse", "url": "https://api.chainabuse.com/v1/reports?limit=50", "headers": {}},
]


def _get_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception as e:
        logger.warning(f"Supabase unavailable: {e}")
    return None


def _ai_summarize_threat(raw_data: dict) -> str:
    """Use FREE AI to summarize threat intel. Always free-first."""
    try:
        from app.services.cloudflare_ai import smart_chat
        from app.services.vault_keys import get_all_ai_keys

        keys = get_all_ai_keys()
        # Truncate data to avoid token overload
        text = json.dumps(raw_data, default=str)[:4000]

        result = smart_chat(
            messages=[
                {"role": "system", "content": "Summarize crypto threat intel in 2 sentences. Be concise."},
                {"role": "user", "content": f"Threat data: {text}"},
            ],
            keys=keys,
            priority="free",
        )
        content = result.get("response", "") or result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip() if content else "No summary available"
    except Exception as e:
        logger.warning(f"AI threat summary failed (will retry with free provider next run): {e}")
        return "AI summary unavailable"


def run():
    logger.info("🛡️ Threat scraper running (FREE AI priority)")
    sb = _get_supabase()
    results = []

    for src in SOURCES:
        try:
            req = Request(src["url"], headers={"User-Agent": "RugMuncher-Intel/1.0", **src.get("headers", {})})
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                summary = _ai_summarize_threat(data)
                results.append({
                    "source": src["name"],
                    "data": data,
                    "ai_summary": summary,
                    "scraped_at": datetime.utcnow().isoformat(),
                })
        except Exception as e:
            logger.warning(f"Source {src['name']} failed: {e}")

    if sb and results:
        try:
            for r in results:
                sb.table("threat_intel").insert({
                    "source": r["source"],
                    "raw_data": r["data"],
                    "ai_summary": r["ai_summary"],
                    "scraped_at": r["scraped_at"],
                }).execute()
        except Exception as e:
            logger.warning(f"DB insert failed: {e}")

    logger.info(f"✅ Threat scraper complete: {len(results)} sources analyzed with FREE AI")
