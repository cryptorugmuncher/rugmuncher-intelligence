"""
Threat Intel Scraper
Fetches public threat data and stores in Supabase/Redis.
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


def run():
    logger.info("Threat scraper running")
    sb = _get_supabase()
    results = []

    for src in SOURCES:
        try:
            req = Request(src["url"], headers={"User-Agent": "RugMuncher-Intel/1.0", **src.get("headers", {})})
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results.append({"source": src["name"], "data": data, "scraped_at": datetime.utcnow().isoformat()})
        except Exception as e:
            logger.warning(f"Source {src['name']} failed: {e}")

    if sb and results:
        try:
            for r in results:
                sb.table("threat_intel").insert({
                    "source": r["source"],
                    "raw_data": r["data"],
                    "scraped_at": r["scraped_at"],
                }).execute()
        except Exception as e:
            logger.warning(f"DB insert failed: {e}")

    logger.info(f"Threat scraper complete: {len(results)} sources")
