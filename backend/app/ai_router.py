#!/usr/bin/env python3
"""
RMI AI Router — Intelligent Model-First Provider Swapping
===========================================================
Routes requests to optimal AI provider based on quota, latency, and cost.
5 Model Tiers: T0 Ultra -> T4 Free
Provider Priority: silicon_flow > fireworks > nvidia > together > openrouter > groq
"""

import os
import json
import asyncio
import httpx
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# ── MODEL CONFIGURATION ──
MODEL_TIERS = {
    "T0": {"name": "Ultra", "models": ["google/gemini-2.5-pro", "nvidia/nemotron-4-340b-instruct", "kimi/k2.5"], "max_cost_per_1k": 0.05},
    "T1": {"name": "Premium", "models": ["anthropic/claude-sonnet-4-20250514", "x-ai/grok-2", "mistral/mistral-large"], "max_cost_per_1k": 0.02},
    "T2": {"name": "Standard", "models": ["google/gemini-2.5-flash", "groq/llama-3.3-70b-versatile", "deepseek/deepseek-chat"], "max_cost_per_1k": 0.005},
    "T3": {"name": "Fast", "models": ["groq/llama-3.1-8b-instant", "google/gemma-7b-it"], "max_cost_per_1k": 0.001},
    "T4": {"name": "Free", "models": ["nvidia/nemotron-3-8b-instruct", "nvidia/llama-3.1-nemotron-70b-instruct"], "max_cost_per_1k": 0.0},
}

# Provider weights for routing decisions
PROVIDER_WEIGHTS = {
    "silicon_flow": 1.0,
    "fireworks": 0.9,
    "nvidia": 0.8,
    "nvidia_dev": 0.85,
    "together": 0.7,
    "openrouter": 0.6,
    "groq": 0.95,
    "gemini": 0.75,
    "mistral": 0.65,
    "kimi": 0.7,
    "together": 0.88,
}

# Provider endpoints
PROVIDERS = {
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
        "rpm": 100,
        "models": ["google/gemini-2.5-pro-preview-03-25", "anthropic/claude-sonnet-4-20250514", "groq/llama-3.3-70b-versatile", "deepseek/deepseek-chat", "qwen/qwen2.5-coder-32b-instruct"],
    },
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "key_env": "NVIDIA_API_KEY",
        "rpm": 20,
        "models": ["nvidia/nemotron-4-340b-instruct", "nvidia/nemotron-3-8b-instruct", "nvidia/llama-3.1-nemotron-70b-instruct", "meta/llama-3.1-nemotron-70b-instruct"],
    },
    "nvidia_dev": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "key_env": "NVIDIA_DEV_API_KEY",
        "rpm": 500,
        "models": ["nvidia/nemotron-4-340b-instruct", "nvidia/nemotron-3-8b-instruct", "nvidia/llama-3.1-nemotron-70b-instruct"],
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "rpm": 30,
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "key_env": "GEMINI_API_KEY",
        "rpm": 60,
        "models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "key_env": "MISTRAL_API_KEY",
        "rpm": 10,
        "models": ["mistral-large-latest", "mistral-medium"],
    },
    "kimi": {
        "url": "https://api.moonshot.cn/v1/chat/completions",
        "key_env": "KIMI_API_KEY",
        "rpm": 3,
        "models": ["kimi-k2.5"],
    },
    "together": {
        "url": "https://api.together.xyz/v1/chat/completions",
        "key_env": "TOGETHER_API_KEY",
        "rpm": 60,
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "mistralai/Mixtral-8x22B-Instruct-v0.1", "meta-llama/Llama-3.1-8B-Instruct-Turbo"],
    },
}

@dataclass
class ProviderState:
    """Tracks provider health and quota"""
    name: str
    key: str
    rpm_limit: int
    requests_this_minute: int = 0
    last_request_time: float = 0.0
    consecutive_errors: int = 0
    total_latency_ms: float = 0.0
    request_count: int = 0
    healthy: bool = True
    weight: float = 0.5

    @property
    def avg_latency(self) -> float:
        return self.total_latency_ms / max(self.request_count, 1)

    @property
    def score(self) -> float:
        """Higher score = better provider to use"""
        if not self.healthy or not self.key:
            return -1.0
        rpm_remaining = max(self.rpm_limit - self.requests_this_minute, 0)
        error_penalty = max(0, 1.0 - (self.consecutive_errors * 0.2))
        latency_factor = max(0.3, 1.0 - (self.avg_latency / 10000))
        return rpm_remaining * self.weight * error_penalty * latency_factor

    def reset_minute(self):
        self.requests_this_minute = 0

class AIRouter:
    """Intelligent AI model routing with provider swapping"""

    def __init__(self):
        self.providers: Dict[str, ProviderState] = {}
        self._init_providers()
        self.last_minute_reset = time.time()

    def _init_providers(self):
        """Initialize provider states from environment"""
        for name, config in PROVIDERS.items():
            key = os.getenv(config["key_env"], "")
            weight = PROVIDER_WEIGHTS.get(name, 0.5)
            self.providers[name] = ProviderState(
                name=name,
                key=key,
                rpm_limit=config["rpm"],
                weight=weight
            )

    def _check_minute_reset(self):
        """Reset per-minute counters"""
        now = time.time()
        if now - self.last_minute_reset >= 60:
            for p in self.providers.values():
                p.reset_minute()
            self.last_minute_reset = now

    def get_best_provider(self, model: str) -> Optional[ProviderState]:
        """Get the best provider for a given model"""
        self._check_minute_reset()

        candidates = []
        for name, provider in self.providers.items():
            config = PROVIDERS.get(name, {})
            available_models = config.get("models", [])
            # Check if provider supports this model (or model family)
            model_supported = any(m.split("/")[-1] in model or model in m for m in available_models)

            # Also check for model family matches (e.g., llama-3.3 matches llama-3.3-70b)
            if not model_supported:
                model_family = model.split("/")[-1].split("-")[0] if "/" in model else model.split("-")[0]
                model_supported = any(model_family in m for m in available_models)

            if model_supported or not model:  # If no model specified, any provider works
                score = provider.score
                if score > 0:
                    candidates.append((score, provider))

        if not candidates:
            # Fall back to any provider with a key
            for p in self.providers.values():
                if p.key and p.healthy:
                    return p
            return None

        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[0][1]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        tier: str = "T2",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Route chat completion to best provider"""
        self._check_minute_reset()

        # Select model from tier if not specified
        if not model and tier in MODEL_TIERS:
            tier_models = MODEL_TIERS[tier]["models"]
            model = tier_models[0]
        elif not model:
            model = "groq/llama-3.3-70b-versatile"

        # Get best provider
        provider = self.get_best_provider(model)
        if not provider:
            return {"error": "No healthy providers available", "model": model}

        # Track request
        provider.requests_this_minute += 1
        start_time = time.time()

        try:
            # Route to provider
            if provider.name == "gemini":
                result = await self._call_gemini(provider, messages, model, temperature, max_tokens, timeout)
            elif provider.name == "groq":
                result = await self._call_openai_compatible(provider, messages, model.split("/")[-1], temperature, max_tokens, timeout)
            else:
                result = await self._call_openai_compatible(provider, messages, model, temperature, max_tokens, timeout)

            # Track success
            latency_ms = (time.time() - start_time) * 1000
            provider.total_latency_ms += latency_ms
            provider.request_count += 1
            provider.consecutive_errors = 0

            return {**result, "_provider": provider.name, "_latency_ms": latency_ms}

        except Exception as e:
            provider.consecutive_errors += 1
            if provider.consecutive_errors >= 5:
                provider.healthy = False

            # Try next best provider
            provider.requests_this_minute -= 1
            fallback = self.get_best_provider(model)
            if fallback and fallback.name != provider.name:
                return await self.chat_completion(messages, model, tier, temperature, max_tokens, timeout)

            return {"error": str(e), "model": model, "_provider": provider.name}

    async def _call_openai_compatible(
        self, provider: ProviderState, messages: List[Dict],
        model: str, temperature: float, max_tokens: int, timeout: float
    ) -> Dict:
        """Call OpenAI-compatible API"""
        headers = {
            "Authorization": f"Bearer {provider.key}",
            "Content-Type": "application/json",
        }
        if provider.name == "openrouter":
            headers["HTTP-Referer"] = "https://rugmunch.io"
            headers["X-Title"] = "Rug Munch Intelligence"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        provider_config = PROVIDERS.get(provider.name, {})
        url = provider_config.get("url", "")
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise Exception(f"{provider.name} error {resp.status_code}: {resp.text[:500]}")
            data = resp.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": data.get("model", model),
                "usage": data.get("usage", {}),
            }

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        tier: str = "T2",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 60.0
    ):
        """Stream chat completion tokens from best provider. Yields text chunks."""
        self._check_minute_reset()

        if not model and tier in MODEL_TIERS:
            tier_models = MODEL_TIERS[tier]["models"]
            model = tier_models[0]
        elif not model:
            model = "groq/llama-3.3-70b-versatile"

        provider = self.get_best_provider(model)
        if not provider:
            yield "[ERROR: No healthy providers available]"
            return

        provider.requests_this_minute += 1
        start_time = time.time()

        try:
            if provider.name == "gemini":
                # Gemini doesn't support standard OpenAI SSE; yield full response
                result = await self._call_gemini(provider, messages, model, temperature, max_tokens, timeout)
                yield result["content"]
                return

            headers = {
                "Authorization": f"Bearer {provider.key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            }
            if provider.name == "openrouter":
                headers["HTTP-Referer"] = "https://rugmunch.io"
                headers["X-Title"] = "Rug Munch Intelligence"

            payload = {
                "model": model.split("/")[-1] if provider.name == "groq" else model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

            provider_config = PROVIDERS.get(provider.name, {})
            url = provider_config.get("url", "")
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as resp:
                    if resp.status_code != 200:
                        error_text = await resp.aread()
                        raise Exception(f"{provider.name} error {resp.status_code}: {error_text[:500].decode()}")

                    buffer = ""
                    async for chunk in resp.aiter_text():
                        buffer += chunk
                        while "\n\n" in buffer or "\n" in buffer:
                            line, sep, buffer = buffer.partition("\n\n")
                            if not line:
                                line, sep, buffer = buffer.partition("\n")
                            line = line.strip()
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    continue
                                try:
                                    parsed = json.loads(data)
                                    delta = parsed["choices"][0].get("delta", {})
                                    token = delta.get("content", "")
                                    if token:
                                        yield token
                                except (json.JSONDecodeError, KeyError, IndexError):
                                    continue

            latency_ms = (time.time() - start_time) * 1000
            provider.total_latency_ms += latency_ms
            provider.request_count += 1
            provider.consecutive_errors = 0

        except Exception as e:
            provider.consecutive_errors += 1
            if provider.consecutive_errors >= 5:
                provider.healthy = False
            yield f"[ERROR: {str(e)}]"

    async def _call_gemini(
        self, provider: ProviderState, messages: List[Dict],
        model: str, temperature: float, max_tokens: int, timeout: float
    ) -> Dict:
        """Call Google Gemini API"""
        # Convert messages to Gemini format
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        model_name = model.split("/")[-1] if "/" in model else model
        url = f"{PROVIDERS['gemini']['url']}/{model_name}:generateContent?key={provider.key}"

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise Exception(f"Gemini error {resp.status_code}: {resp.text[:500]}")
            data = resp.json()
            return {
                "content": data["candidates"][0]["content"]["parts"][0]["text"],
                "model": model,
                "usage": {},
            }

    def get_status(self) -> Dict:
        """Get router status for monitoring"""
        return {
            "providers": {
                name: {
                    "healthy": p.healthy,
                    "rpm_used": p.requests_this_minute,
                    "rpm_limit": p.rpm_limit,
                    "avg_latency_ms": p.avg_latency,
                    "consecutive_errors": p.consecutive_errors,
                    "has_key": bool(p.key),
                    "score": p.score,
                }
                for name, p in self.providers.items()
            },
            "tiers": MODEL_TIERS,
        }

# Singleton
router = AIRouter()

