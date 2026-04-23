"""
Free API Hunter
Scans for new free AI APIs every 5 days.
Auto-discovers free tiers, trials, and credit programs.
"""
import os
import json
import logging
from datetime import datetime
from urllib.request import urlopen, Request

logger = logging.getLogger("free_api_hunter")

DISCOVERY_SOURCES = [
    {"name": "openrouter_free", "url": "https://openrouter.ai/api/v1/models", "parser": "openrouter"},
    {"name": "cloudflare_models", "url": "https://api.cloudflare.com/client/v4/accounts/ai/models/search", "parser": "cloudflare", "headers": {"Authorization": "Bearer placeholder"}},
]

FREE_KEYWORDS = ["free", "trial", "credits", "starter", "sandbox", "developer", "beta"]


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


def discover_openrouter_free():
    """Find $0 priced models on OpenRouter."""
    findings = []
    try:
        req = Request("https://openrouter.ai/api/v1/models", headers={"User-Agent": "RugMuncher-Hunter/1.0"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            for model in data.get("data", []):
                pricing = model.get("pricing", {})
                prompt_price = float(pricing.get("prompt", 1) or 1)
                completion_price = float(pricing.get("completion", 1) or 1)
                if prompt_price == 0 and completion_price == 0:
                    findings.append({
                        "provider": "openrouter",
                        "model": model.get("id"),
                        "name": model.get("name"),
                        "type": "free_model",
                        "description": f"Free model: {model.get('name')}",
                        "discovered_at": datetime.utcnow().isoformat(),
                    })
    except Exception as e:
        logger.warning(f"OpenRouter discovery failed: {e}")
    return findings


def discover_huggingface_free():
    """Check HuggingFace for free inference endpoints."""
    findings = []
    try:
        req = Request("https://huggingface.co/api/models?filter=transformers&sort=downloads&limit=20", headers={"User-Agent": "RugMuncher-Hunter/1.0"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            for model in data:
                if any(kw in model.get("id", "").lower() for kw in FREE_KEYWORDS):
                    findings.append({
                        "provider": "huggingface",
                        "model": model.get("id"),
                        "type": "free_hosting",
                        "description": f"HF model: {model.get('id')}",
                        "discovered_at": datetime.utcnow().isoformat(),
                    })
    except Exception as e:
        logger.warning(f"HuggingFace discovery failed: {e}")
    return findings


def check_email_for_keys():
    """Placeholder: scan inbox for API key confirmations."""
    return []


def run():
    logger.info("Free API Hunter running")
    sb = _get_supabase()
    all_findings = []

    all_findings.extend(discover_openrouter_free())
    all_findings.extend(discover_huggingface_free())

    # Store findings
    if sb and all_findings:
        try:
            for finding in all_findings:
                sb.table("free_api_discoveries").upsert(finding, on_conflict="model").execute()
        except Exception as e:
            logger.warning(f"DB insert failed: {e}")

    logger.info(f"Free API Hunter complete: {len(all_findings)} findings")
    return all_findings
