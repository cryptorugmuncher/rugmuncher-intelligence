"""
Cloudflare AI Service
=====================
Interfaces with Cloudflare Workers AI (edge inference) and AI Gateway.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import urllib.request

logger = logging.getLogger("cloudflare_ai")

# Configuration
WORKER_URL = os.getenv("CF_WORKER_URL", "https://rmi-api-gateway.cryptorugmuncher.workers.dev")


def _post(path: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """POST to the Cloudflare Worker."""
    url = WORKER_URL + path
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ═══════════════════════════════════════════════════════════
# WORKERS AI — Free Edge Inference
# ═══════════════════════════════════════════════════════════

def chat(
    messages: List[Dict[str, str]],
    model: str = "@cf/meta/llama-3.1-8b-instruct",
) -> Dict[str, Any]:
    """Run a chat completion via Cloudflare Workers AI (free)."""
    try:
        return _post("/ai/chat", {"messages": messages, "model": model})
    except Exception as e:
        logger.error(f"Workers AI chat failed: {e}")
        raise


def embed(
    texts: List[str],
    model: str = "@cf/baai/bge-base-en-v1.5",
) -> Dict[str, Any]:
    """Generate embeddings via Cloudflare Workers AI (free)."""
    try:
        return _post("/ai/embeddings", {"text": texts, "model": model})
    except Exception as e:
        logger.error(f"Workers AI embed failed: {e}")
        raise


# ═══════════════════════════════════════════════════════════
# AI GATEWAY — Unified Provider Proxy with Edge Caching
# ═══════════════════════════════════════════════════════════

def gateway_chat(
    provider: str,
    api_key: str,
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """Chat via AI Gateway (proxied through Cloudflare with caching)."""
    payload: Dict[str, Any] = {
        "model": model or _default_model(provider),
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    try:
        return _post(
            f"/ai/gateway/{provider}/chat/completions",
            payload,
            headers={"X-AI-Key": api_key},
        )
    except Exception as e:
        logger.error(f"AI Gateway {provider} failed: {e}")
        raise


def _default_model(provider: str) -> str:
    defaults = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "groq": "llama-3.1-8b-instant",
        "openrouter": "openrouter/free",
        "deepseek": "deepseek-chat",
    }
    return defaults.get(provider, "")


# ═══════════════════════════════════════════════════════════
# SMART ROUTER — Auto-select cheapest/fastest provider
# ═══════════════════════════════════════════════════════════

def smart_chat(
    messages: List[Dict[str, str]],
    keys: Dict[str, Optional[str]],
    priority: str = "free",
) -> Dict[str, Any]:
    """Automatically route to the best available AI provider."""
    providers = []
    if priority == "free":
        # Try Workers AI first (free)
        try:
            return {**chat(messages), "_provider": "workers-ai", "_cost": 0}
        except Exception:
            pass
        # Then OpenRouter free tier
        if keys.get("openrouter"):
            providers.append(("openrouter", keys["openrouter"]))
        # Then Groq (cheap & fast)
        if keys.get("groq"):
            providers.append(("groq", keys["groq"]))
    else:
        if keys.get("openai"):
            providers.append(("openai", keys["openai"]))
        if keys.get("anthropic"):
            providers.append(("anthropic", keys["anthropic"]))
        if keys.get("groq"):
            providers.append(("groq", keys["groq"]))

    for provider, key in providers:
        if not key:
            continue
        try:
            result = gateway_chat(provider, key, messages)
            return {**result, "_provider": provider}
        except Exception:
            continue

    raise RuntimeError("No AI provider available")
