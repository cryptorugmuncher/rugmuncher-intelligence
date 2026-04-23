"""
Cloudflare AI Service
=====================
Interfaces with Cloudflare Workers AI (edge inference) and AI Gateway.
Tracks free vs paid usage and prioritizes free tokens.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
import urllib.request

logger = logging.getLogger("cloudflare_ai")

# Import budget tracker
try:
    from app.services.token_budget import (
        get_smart_provider_order,
        log_usage,
        estimate_cost,
        get_budget_summary,
        is_free_quota_available,
    )
except ImportError:
    get_smart_provider_order = None
    log_usage = None
    estimate_cost = None
    get_budget_summary = None
    is_free_quota_available = None

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
    start = time.time()
    try:
        result = _post("/ai/chat", {"messages": messages, "model": model})
        latency = int((time.time() - start) * 1000)
        if log_usage:
            log_usage("workers-ai", model, "/ai/chat", latency_ms=latency, metadata={"free": True})
        return result
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

    start = time.time()
    try:
        result = _post(
            f"/ai/gateway/{provider}/chat/completions",
            payload,
            headers={"X-AI-Key": api_key},
        )
        latency = int((time.time() - start) * 1000)

        # Estimate tokens from response
        usage = result.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0) or usage.get("output_tokens", 0)

        if log_usage:
            est_cost = estimate_cost(provider, input_tokens, output_tokens) if estimate_cost else 0
            log_usage(
                provider,
                model or _default_model(provider),
                f"/ai/gateway/{provider}/chat/completions",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency,
                metadata={"free": False, "estimated_cost": est_cost},
            )
        return result
    except Exception as e:
        if log_usage:
            log_usage(provider, model or "unknown", f"/ai/gateway/{provider}/chat/completions", status="error", error_message=str(e))
        logger.error(f"AI Gateway {provider} failed: {e}")
        raise


def _default_model(provider: str) -> str:
    defaults = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "groq": "llama-3.1-8b-instant",
        "openrouter": "openrouter/free",
        "deepseek": "deepseek-chat",
        "fireworks": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "gemini": "gemini-1.5-flash",
        "mistral": "mistral-small-latest",
        "nvidia": "meta/llama-3.1-nemotron-70b-instruct",
        "nvidia_dev": "meta/llama-3.1-nemotron-70b-instruct",
        "kimi": "kimi-k2.5",
        "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    }
    return defaults.get(provider, "")


# ═══════════════════════════════════════════════════════════
# SMART ROUTER — Always free first, then cheapest paid
# ═══════════════════════════════════════════════════════════

def smart_chat(
    messages: List[Dict[str, str]],
    keys: Dict[str, Optional[str]],
    priority: str = "free",
) -> Dict[str, Any]:
    """Automatically route to the best available AI provider.
    ALWAYS tries free providers first, then falls back to cheapest paid.
    """
    if priority == "free" and get_smart_provider_order:
        provider_order = get_smart_provider_order(keys)
    else:
        # Fallback: manual order
        provider_order = []
        if is_free_quota_available and is_free_quota_available("workers-ai"):
            provider_order.append(("workers-ai", None))
        for name, key in keys.items():
            if key and name not in ["workers-ai"]:
                provider_order.append((name, key))

    last_error = None
    for provider, key in provider_order:
        if not key and provider != "workers-ai":
            continue

        try:
            if provider == "workers-ai":
                result = chat(messages)
                return {**result, "_provider": "workers-ai", "_cost": 0, "_free": True}

            # Use gateway for all other providers
            result = gateway_chat(provider, key or "", messages)
            return {**result, "_provider": provider, "_free": False}

        except Exception as e:
            last_error = e
            logger.warning(f"Provider {provider} failed, trying next: {e}")
            continue

    raise RuntimeError(f"No AI provider available. Last error: {last_error}")


def get_budget_status() -> Dict[str, Any]:
    """Get current budget and free quota status."""
    if get_budget_summary:
        return get_budget_summary()
    return {}

