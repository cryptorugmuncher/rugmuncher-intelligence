#!/usr/bin/env python3
"""
👻 SPECTER — OSINT & Social Forensics Engine
Uses cheapest available AI provider for analysis.
"""

import os
import re
import json
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse


class SPECTEROSINT:
    """Open Source Intelligence gathering for crypto scam detection"""

    def __init__(self):
        self.brave_key = os.getenv("BRAVE_API_KEY", "")
        self.firecrawl_key = os.getenv("FIRECRAWL_API_KEY", "")
        self.apify_key = os.getenv("APIFY_API_KEY", "")
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close(self):
        await self.client.aclose()

    async def brave_search(self, query: str, count: int = 10) -> List[Dict]:
        """Search via Brave Search API (2000 queries/month free)"""
        if not self.brave_key:
            return [{"error": "BRAVE_API_KEY not configured"}]
        try:
            resp = await self.client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": self.brave_key, "Accept": "application/json"},
                params={"q": query, "count": min(count, 20), "offset": 0, "mkt": "en-US"}
            )
            if resp.status_code == 200:
                data = resp.json()
                return [{"title": r.get("title", ""), "url": r.get("url", ""), "description": r.get("description", ""), "age": r.get("age", ""), "source": "brave"} for r in data.get("web", {}).get("results", [])]
            return [{"error": f"Brave HTTP {resp.status_code}"}]
        except Exception as e:
            return [{"error": str(e)}]

    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """Deep scrape a website for forensic analysis"""
        if not self.firecrawl_key:
            return {"error": "FIRECRAWL_API_KEY not configured"}
        try:
            resp = await self.client.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={"Authorization": f"Bearer {self.firecrawl_key}"},
                json={"url": url, "formats": ["markdown", "html"], "onlyMainContent": False}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return {"url": url, "title": data.get("data", {}).get("metadata", {}).get("title", ""), "description": data.get("data", {}).get("metadata", {}).get("description", ""), "content": data.get("data", {}).get("markdown", "")[:8000], "links": data.get("data", {}).get("links", [])[:50], "source": "firecrawl"}
            return {"error": f"Firecrawl HTTP {resp.status_code}", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}

    async def analyze_website_risk(self, url: str) -> Dict[str, Any]:
        """Scrape + AI analysis of a scam website — uses CHEAPEST provider"""
        scrape = await self.scrape_website(url)
        if "error" in scrape and not scrape.get("content"):
            return scrape

        content = scrape.get("content", "")
        prompt = f"""Analyze this website content for crypto scam indicators.
Return ONLY valid JSON with these keys:
- risk_score (0-100)
- risk_level (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
- red_flags (list of strings)
- positive_signals (list of strings)
- is_plagiarized (boolean)
- fake_team_indicators (list)
- suspicious_claims (list)
- recommendation (string)

Website content:
{content[:6000]}"""

        ai_result = await self._ai_analyze(prompt)
        return {
            "url": url,
            "domain_age_guess": self._guess_domain_age(url),
            "scrape": scrape,
            "ai_analysis": ai_result,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    async def scrape_twitter_profile(self, handle: str) -> Dict[str, Any]:
        """Scrape X/Twitter profile via Apify"""
        if not self.apify_key:
            return {"error": "APIFY_API_KEY not configured"}
        try:
            run_resp = await self.client.post(
                "https://api.apify.com/v2/acts/apify~twitter-profile-scraper/runs",
                headers={"Authorization": f"Bearer {self.apify_key}"},
                json={"usernames": [handle.replace("@", "")], "maxItems": 1, "includeReplies": False},
                params={"token": self.apify_key}
            )
            if run_resp.status_code in (201, 200):
                run_data = run_resp.json()
                run_id = run_data.get("data", {}).get("id")
                return {"handle": handle, "apify_run_id": run_id, "status": "queued", "check_url": f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"}
            return {"error": f"Apify HTTP {run_resp.status_code}", "handle": handle}
        except Exception as e:
            return {"error": str(e), "handle": handle}

    async def _ai_analyze(self, prompt: str) -> Dict[str, Any]:
        """Send analysis prompt to CHEAPEST available AI provider."""
        try:
            from app.services.multi_key_router import get_router
            router = get_router()
            key = router.get_cheapest_key(required_capabilities=["chat"])
            if not key:
                return {"error": "No AI providers available"}

            messages = [
                {"role": "system", "content": "You are SPECTER, a crypto scam forensics AI. Respond ONLY with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            if key.provider == "gemini":
                result = router._call_gemini(key, messages, model=key.models[0], temperature=0.2, max_tokens=2048)
            else:
                result = router._call_openai_compatible(key, messages, model=key.models[0], temperature=0.2, max_tokens=2048)

            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                content = result.get("choices", [{}])[0].get("content", "")
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "parse_error": True, "provider_used": key.id}
        except Exception as e:
            return {"error": str(e)}

    async def investigate_project(self, project_name: str, website: Optional[str] = None, twitter: Optional[str] = None) -> Dict[str, Any]:
        """Full OSINT investigation"""
        queries = [f"{project_name} crypto scam", f"{project_name} rug pull", f"{project_name} token review"]
        if twitter:
            queries.append(f"site:twitter.com {twitter} scam")

        search_tasks = [self.brave_search(q, count=5) for q in queries]
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        all_results = []
        for sr in search_results:
            if isinstance(sr, list):
                all_results.extend(sr)

        website_analysis = await self.analyze_website_risk(website) if website else None

        evidence = {
            "project_name": project_name,
            "website": website,
            "twitter": twitter,
            "search_results": all_results[:20],
            "website_analysis": website_analysis,
            "negative_mentions": len([r for r in all_results if any(w in r.get("description", "").lower() for w in ["scam", "rug", "honeypot", "fake"])]),
            "total_mentions": len(all_results),
            "investigated_at": datetime.utcnow().isoformat()
        }

        synthesis_prompt = f"""Synthesize this OSINT evidence into a scam risk assessment.
Return JSON with: overall_risk (0-100), risk_level, summary, key_findings, recommended_actions.

Evidence:
{json.dumps(evidence, indent=2)[:8000]}"""

        evidence["synthesis"] = await self._ai_analyze(synthesis_prompt)
        return evidence

    def _guess_domain_age(self, url: str) -> str:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if any(x in domain for x in [".xyz", ".top", ".click", ".link", ".icu"]):
            return "likely_new"
        return "unknown"


_specter = None

async def get_specter() -> SPECTEROSINT:
    global _specter
    if _specter is None:
        _specter = SPECTEROSINT()
    return _specter
