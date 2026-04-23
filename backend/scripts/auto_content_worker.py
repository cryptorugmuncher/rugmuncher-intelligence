#!/usr/bin/env python3
"""
Auto-Content Worker
===================
Background daemon that generates prepared content while you sleep.
Run with: python auto_content_worker.py
Or schedule via cron: */15 * * * * cd /root/rmi/backend && python scripts/auto_content_worker.py
"""

import os
import sys
import asyncio
import httpx
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ADMIN_KEY = os.getenv("ADMIN_API_KEY", "dev-key-change-me")
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

SOURCES = ["market_intel", "daily_briefing", "whale_alert", "rug_alert"]

async def generate_content():
    """Auto-generate content from all sources."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        for source in SOURCES:
            try:
                resp = await client.post(
                    f"{API_BASE}/api/v1/darkroom/content/auto-generate",
                    json={"source": source, "count": 3, "tone": "analytical"},
                    headers={"X-Admin-Key": ADMIN_KEY},
                )
                data = resp.json()
                print(f"[{datetime.now().isoformat()}] {source}: generated {data.get('count', 0)} drafts")
            except Exception as e:
                print(f"[{datetime.now().isoformat()}] {source}: error - {e}")

async def main():
    print(f"[{datetime.now().isoformat()}] Auto-content worker starting...")
    print(f"API: {API_BASE}")
    await generate_content()
    print(f"[{datetime.now().isoformat()}] Done. Content is now prepared and waiting for your approval in the Darkroom.")

if __name__ == "__main__":
    asyncio.run(main())
