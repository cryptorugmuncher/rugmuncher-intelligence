"""
Multi-Key AI Router — CONFIG-DRIVEN
====================================
Reads provider configs from provider_config.py dynamically.
Adding a new provider = automatic router support. No code changes.
"""

import os
import time
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from urllib.request import urlopen, Request

from app.services.provider_config import (
    get_all_providers, get_provider, get_provider_secret,
    get_routing_order, ProviderConfig,
)

logger = logging.getLogger("multi_key_router")


@dataclass
class KeyInstance:
    """A single API key instance with its own config and state."""
    id: str
    provider: str
    api_key: str
    base_url: str
    rpm_limit: int
    models: List[str]
    capabilities: List[str]
    is_free_tier: bool = False
    weight: float = 1.0
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    # Runtime state
    requests_this_minute: int = 0
    last_request_time: float = 0.0
    consecutive_errors: int = 0
    total_latency_ms: float = 0.0
    request_count: int = 0
    healthy: bool = True
    last_minute_reset: float = field(default_factory=time.time)

    @property
    def avg_latency(self) -> float:
        return self.total_latency_ms / max(self.request_count, 1)

    @property
    def rpm_remaining(self) -> int:
        self._check_minute_reset()
        return max(self.rpm_limit - self.requests_this_minute, 0)

    @property
    def score(self) -> float:
        if not self.healthy:
            return -1.0
        rpm = self.rpm_remaining
        error_penalty = max(0, 1.0 - (self.consecutive_errors * 0.2))
        latency_factor = max(0.3, 1.0 - (self.avg_latency / 10000))
        free_boost = 2.0 if self.is_free_tier else 1.0
        return rpm * self.weight * error_penalty * latency_factor * free_boost

    def _check_minute_reset(self):
        now = time.time()
        if now - self.last_minute_reset >= 60:
            self.requests_this_minute = 0
            self.last_minute_reset = now

    def record_success(self, latency_ms: float):
        self.requests_this_minute += 1
        self.total_latency_ms += latency_ms
        self.request_count += 1
        self.consecutive_errors = 0
        self.last_request_time = time.time()

    def record_error(self):
        self.consecutive_errors += 1
        if self.consecutive_errors >= 5:
            self.healthy = False


class MultiKeyRouter:
    """Routes AI requests across multiple keys with capability matching."""

    def __init__(self):
        self.keys: Dict[str, KeyInstance] = {}
        self._init_keys()

    def _init_keys(self):
        """Load all key instances from provider_config dynamically."""
        for cfg in get_all_providers():
            if not cfg.enabled:
                continue

            # Get API key
            if cfg.provider_type == "cloudflare":
                api_key = ""  # No key needed
            else:
                api_key = get_provider_secret(cfg) or ""

            if not api_key and cfg.provider_type != "cloudflare":
                logger.debug(f"Key {cfg.name} not configured")
                continue

            self.keys[cfg.name] = KeyInstance(
                id=cfg.name,
                provider=cfg.provider_type,
                api_key=api_key,
                base_url=cfg.base_url,
                rpm_limit=cfg.rpm_limit,
                models=cfg.models,
                capabilities=cfg.capabilities,
                is_free_tier=cfg.is_free_tier,
                weight=cfg.weight,
                cost_per_1k_input=cfg.cost_per_1k_input,
                cost_per_1k_output=cfg.cost_per_1k_output,
            )
            status = "🆓 FREE" if cfg.is_free_tier else "💰 PAID"
            logger.info(f"Loaded key: {cfg.name} ({cfg.provider_type}) — {status}, {cfg.rpm_limit} RPM")

    def reload_keys(self):
        """Reload all keys (call after config changes)."""
        self.keys.clear()
        self._init_keys()
        logger.info("Keys reloaded from provider config")

    def add_key(self, key_id: str, provider: str, api_key: str, base_url: str,
                rpm_limit: int, models: List[str], capabilities: List[str],
                is_free_tier: bool = False, weight: float = 1.0):
        """Dynamically add a new key at runtime."""
        self.keys[key_id] = KeyInstance(
            id=key_id, provider=provider, api_key=api_key, base_url=base_url,
            rpm_limit=rpm_limit, models=models, capabilities=capabilities,
            is_free_tier=is_free_tier, weight=weight,
        )
        logger.info(f"Added key: {key_id} ({provider}) — {'🆓 FREE' if is_free_tier else '💰 PAID'}")

    def get_best_key(
        self,
        model: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        prefer_free: bool = True,
    ) -> Optional[KeyInstance]:
        """Get the best key for a request, matching model and capabilities."""
        candidates: List[Tuple[float, KeyInstance]] = []

        for key in self.keys.values():
            if key.score <= 0:
                continue

            # Check model support
            if model:
                model_supported = any(
                    m.split("/")[-1] in model or model in m or model.split("/")[-1] in m
                    for m in key.models
                )
                if not model_supported:
                    continue

            # Check capabilities
            if required_capabilities:
                has_caps = all(cap in key.capabilities for cap in required_capabilities)
                if not has_caps:
                    continue

            score = key.score
            if prefer_free and key.is_free_tier:
                score *= 10.0

            candidates.append((score, key))

        if not candidates:
            for key in self.keys.values():
                if key.healthy and key.api_key:
                    return key
            return None

        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[0][1]

    def get_cheapest_key(self, required_capabilities: Optional[List[str]] = None) -> Optional[KeyInstance]:
        """Get the cheapest provider for bot detection / low-priority tasks."""
        candidates = []
        for key in self.keys.values():
            if not key.healthy or not key.api_key:
                continue
            if required_capabilities:
                if not all(cap in key.capabilities for cap in required_capabilities):
                    continue
            cost = key.cost_per_1k_input + key.cost_per_1k_output
            candidates.append((cost, key))

        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    def get_all_keys_for_provider(self, provider: str) -> List[KeyInstance]:
        return [k for k in self.keys.values() if k.provider == provider]

    def compare_provider_keys(self, provider: str) -> List[Dict[str, Any]]:
        keys = self.get_all_keys_for_provider(provider)
        return [
            {
                "id": k.id, "provider": k.provider, "rpm_limit": k.rpm_limit,
                "rpm_remaining": k.rpm_remaining, "models": k.models,
                "capabilities": k.capabilities, "is_free_tier": k.is_free_tier,
                "healthy": k.healthy, "score": k.score,
                "request_count": k.request_count, "avg_latency_ms": k.avg_latency,
            }
            for k in keys
        ]

    def call_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        prefer_free: bool = True,
        use_cheapest: bool = False,  # For bot detection
    ) -> Dict[str, Any]:
        """Call chat completion with automatic key selection."""
        if use_cheapest:
            key = self.get_cheapest_key(required_capabilities)
        else:
            key = self.get_best_key(model=model, required_capabilities=required_capabilities, prefer_free=prefer_free)

        if not key:
            return {"error": "No healthy keys available", "model": model}

        start = time.time()
        try:
            if key.id == "workers-ai":
                result = self._call_workers_ai(messages, model, temperature, max_tokens)
            elif key.provider == "gemini":
                result = self._call_gemini(key, messages, model, temperature, max_tokens)
            else:
                result = self._call_openai_compatible(key, messages, model, temperature, max_tokens)

            latency_ms = (time.time() - start) * 1000
            key.record_success(latency_ms)

            return {
                **result,
                "_key_id": key.id,
                "_provider": key.provider,
                "_free": key.is_free_tier,
                "_latency_ms": latency_ms,
                "_cost_per_1k": key.cost_per_1k_input + key.cost_per_1k_output,
            }

        except Exception as e:
            key.record_error()
            # Try next best key
            fallback = self.get_best_key(model=model, required_capabilities=required_capabilities, prefer_free=prefer_free)
            if fallback and fallback.id != key.id:
                logger.info(f"Retrying with fallback key: {fallback.id}")
                return self.call_chat(messages, model, required_capabilities, temperature, max_tokens, prefer_free)
            return {"error": str(e), "_key_id": key.id, "_provider": key.provider}

    def _call_workers_ai(self, messages, model, temperature, max_tokens):
        try:
            from app.services.cloudflare_ai import chat
            return chat(messages, model or "@cf/meta/llama-3.1-8b-instruct")
        except Exception as e:
            raise RuntimeError(f"Workers AI failed: {e}")

    def _call_openai_compatible(self, key: KeyInstance, messages, model, temperature, max_tokens):
        headers = {
            "Authorization": f"Bearer {key.api_key}",
            "Content-Type": "application/json",
        }
        if key.provider == "openrouter":
            headers["HTTP-Referer"] = "https://rugmunch.io"
            headers["X-Title"] = "Rug Munch Intelligence"

        payload = {
            "model": model or key.models[0],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        req = Request(
            f"{key.base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())

    def _call_gemini(self, key: KeyInstance, messages, model, temperature, max_tokens):
        model_name = (model or key.models[0]).split("/")[-1]
        url = f"{key.base_url}/{model_name}:generateContent?key={key.api_key}"

        gemini_messages = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {
            "contents": gemini_messages,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }

        req = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return {"choices": [{"message": {"content": text}}]}


# Global router instance
_router: Optional[MultiKeyRouter] = None


def get_router() -> MultiKeyRouter:
    global _router
    if _router is None:
        _router = MultiKeyRouter()
    return _router
