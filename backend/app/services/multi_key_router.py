"""
Multi-Key AI Router
===================
Supports multiple API keys per provider with capability-based routing.
Automatically compares keys and picks the best one for each request.

Example: NVIDIA has regular API (20 RPM) + Developer API (500 RPM).
The router checks which key has capacity and routes accordingly.
"""

import os
import time
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from urllib.request import urlopen, Request

logger = logging.getLogger("multi_key_router")

# ═══════════════════════════════════════════════════════════
# KEY CONFIGURATIONS — Multiple keys per provider
# ═══════════════════════════════════════════════════════════

@dataclass
class KeyInstance:
    """A single API key instance with its own config and state."""
    id: str                          # Unique key ID (e.g., "nvidia_main", "nvidia_dev")
    provider: str                    # Provider name (e.g., "nvidia")
    api_key: str
    base_url: str
    rpm_limit: int
    models: List[str]                # Models this key supports
    capabilities: List[str]          # Extra capabilities (e.g., "vision", "json_mode", "function_calling")
    is_free_tier: bool = False
    weight: float = 1.0
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
        """Higher score = better key to use."""
        if not self.api_key or not self.healthy:
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


# ═══════════════════════════════════════════════════════════
# DEFAULT KEY CONFIGS
# ═══════════════════════════════════════════════════════════

DEFAULT_KEY_CONFIGS: List[Dict[str, Any]] = [
    # 🆓 FREE — Cloudflare Workers AI
    {
        "id": "workers-ai",
        "provider": "cloudflare",
        "api_key": "",  # No key needed
        "base_url": "",
        "rpm_limit": 10000,
        "models": ["@cf/meta/llama-3.1-8b-instruct", "@cf/baai/bge-base-en-v1.5"],
        "capabilities": ["chat", "embeddings"],
        "is_free_tier": True,
        "weight": 10.0,
    },
    # 🆓 FREE — OpenRouter free models
    {
        "id": "openrouter-free",
        "provider": "openrouter",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "rpm_limit": 200,
        "models": ["openrouter/free"],
        "capabilities": ["chat"],
        "is_free_tier": True,
        "weight": 8.0,
    },
    # 🆓 FREE TIER — Gemini
    {
        "id": "gemini-free",
        "provider": "gemini",
        "api_key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "rpm_limit": 1500,
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "capabilities": ["chat", "vision", "json_mode"],
        "is_free_tier": True,
        "weight": 7.0,
    },
    # 🆓 FREE CREDITS — Groq
    {
        "id": "groq-free",
        "provider": "groq",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "rpm_limit": 30,
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
        "capabilities": ["chat", "json_mode", "fast"],
        "is_free_tier": True,
        "weight": 6.0,
    },
    # 💰 PAID — NVIDIA Regular (20 RPM)
    {
        "id": "nvidia_regular",
        "provider": "nvidia",
        "api_key_env": "NVIDIA_API_KEY",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "rpm_limit": 20,
        "models": ["nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-nemotron-70b-instruct"],
        "capabilities": ["chat", "long_context"],
        "is_free_tier": False,
        "weight": 3.0,
    },
    # 💰 PAID — NVIDIA Developer (500 RPM) — HIGHER CAPACITY
    {
        "id": "nvidia_dev",
        "provider": "nvidia",
        "api_key_env": "NVIDIA_DEV_API_KEY",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "rpm_limit": 500,
        "models": ["nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-nemotron-70b-instruct"],
        "capabilities": ["chat", "long_context", "high_rpm"],
        "is_free_tier": False,
        "weight": 5.0,  # Higher weight because more capacity
    },
    # 💰 PAID — OpenAI
    {
        "id": "openai_main",
        "provider": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "rpm_limit": 60,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "capabilities": ["chat", "vision", "json_mode", "function_calling"],
        "is_free_tier": False,
        "weight": 4.0,
    },
    # 💰 PAID — Anthropic
    {
        "id": "anthropic_main",
        "provider": "anthropic",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com/v1",
        "rpm_limit": 60,
        "models": ["claude-sonnet-4-20250514", "claude-haiku-20240307"],
        "capabilities": ["chat", "vision", "long_context"],
        "is_free_tier": False,
        "weight": 3.0,
    },
    # 💰 PAID — DeepSeek (cheap)
    {
        "id": "deepseek_main",
        "provider": "deepseek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
        "rpm_limit": 60,
        "models": ["deepseek-chat", "deepseek-coder"],
        "capabilities": ["chat", "coding"],
        "is_free_tier": False,
        "weight": 5.0,
    },
    # 💰 PAID — Fireworks (cheap)
    {
        "id": "fireworks_main",
        "provider": "fireworks",
        "api_key_env": "FIREWORKS_API_KEY",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "rpm_limit": 60,
        "models": ["accounts/fireworks/models/llama-v3p1-8b-instruct"],
        "capabilities": ["chat", "fast"],
        "is_free_tier": False,
        "weight": 5.0,
    },
    # 💰 PAID — Mistral
    {
        "id": "mistral_main",
        "provider": "mistral",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
        "rpm_limit": 60,
        "models": ["mistral-large-latest", "mistral-medium"],
        "capabilities": ["chat", "json_mode"],
        "is_free_tier": False,
        "weight": 4.0,
    },
    # 💰 PAID — Together AI
    {
        "id": "together_main",
        "provider": "together",
        "api_key_env": "TOGETHER_API_KEY",
        "base_url": "https://api.together.xyz/v1",
        "rpm_limit": 60,
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "mistralai/Mixtral-8x22B-Instruct-v0.1"],
        "capabilities": ["chat", "fast"],
        "is_free_tier": False,
        "weight": 4.0,
    },
    # 💰 PAID — Kimi
    {
        "id": "kimi_main",
        "provider": "kimi",
        "api_key_env": "KIMI_API_KEY",
        "base_url": "https://api.moonshot.cn/v1",
        "rpm_limit": 3,
        "models": ["kimi-k2.5"],
        "capabilities": ["chat", "long_context"],
        "is_free_tier": False,
        "weight": 2.0,
    },
]


class MultiKeyRouter:
    """Routes AI requests across multiple keys with capability matching."""

    def __init__(self):
        self.keys: Dict[str, KeyInstance] = {}
        self._init_keys()

    def _init_keys(self):
        """Load all key instances from environment."""
        for cfg in DEFAULT_KEY_CONFIGS:
            key_id = cfg["id"]
            provider = cfg["provider"]

            # Get API key from env
            if cfg.get("is_free_tier") and not cfg.get("api_key_env"):
                api_key = ""  # No key needed (Workers AI)
            else:
                api_key = os.getenv(cfg.get("api_key_env", ""), "")

            if not api_key and not cfg.get("is_free_tier"):
                logger.debug(f"Key {key_id} not configured (env {cfg.get('api_key_env')})")
                continue

            self.keys[key_id] = KeyInstance(
                id=key_id,
                provider=provider,
                api_key=api_key,
                base_url=cfg["base_url"],
                rpm_limit=cfg["rpm_limit"],
                models=cfg.get("models", []),
                capabilities=cfg.get("capabilities", []),
                is_free_tier=cfg.get("is_free_tier", False),
                weight=cfg.get("weight", 1.0),
            )
            status = "🆓 FREE" if cfg.get("is_free_tier") else "💰 PAID"
            logger.info(f"Loaded key: {key_id} ({provider}) — {status}, {cfg['rpm_limit']} RPM")

    def add_key(self, key_id: str, provider: str, api_key: str, base_url: str,
                rpm_limit: int, models: List[str], capabilities: List[str],
                is_free_tier: bool = False, weight: float = 1.0):
        """Dynamically add a new key at runtime."""
        self.keys[key_id] = KeyInstance(
            id=key_id,
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            rpm_limit=rpm_limit,
            models=models,
            capabilities=capabilities,
            is_free_tier=is_free_tier,
            weight=weight,
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
            # Check if key is healthy and has quota
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

            # Score with free boost
            score = key.score
            if prefer_free and key.is_free_tier:
                score *= 10.0  # Strongly prefer free keys

            candidates.append((score, key))

        if not candidates:
            # Fallback: any healthy key
            for key in self.keys.values():
                if key.healthy and key.api_key:
                    return key
            return None

        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[0][1]

    def get_all_keys_for_provider(self, provider: str) -> List[KeyInstance]:
        """Get all key instances for a provider (e.g., all NVIDIA keys)."""
        return [k for k in self.keys.values() if k.provider == provider]

    def compare_provider_keys(self, provider: str) -> List[Dict[str, Any]]:
        """Compare all keys for a provider and return their capabilities."""
        keys = self.get_all_keys_for_provider(provider)
        return [
            {
                "id": k.id,
                "provider": k.provider,
                "rpm_limit": k.rpm_limit,
                "rpm_remaining": k.rpm_remaining,
                "models": k.models,
                "capabilities": k.capabilities,
                "is_free_tier": k.is_free_tier,
                "healthy": k.healthy,
                "score": k.score,
                "request_count": k.request_count,
                "avg_latency_ms": k.avg_latency,
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
    ) -> Dict[str, Any]:
        """Call chat completion with automatic key selection."""
        key = self.get_best_key(model=model, required_capabilities=required_capabilities, prefer_free=prefer_free)
        if not key:
            return {"error": "No healthy keys available", "model": model}

        start = time.time()
        try:
            if key.id == "workers-ai":
                # Cloudflare Workers AI — call via local function or HTTP
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
        """Call Cloudflare Workers AI via the local backend service."""
        try:
            from app.services.cloudflare_ai import chat
            return chat(messages, model or "@cf/meta/llama-3.1-8b-instruct")
        except Exception as e:
            raise RuntimeError(f"Workers AI failed: {e}")

    def _call_openai_compatible(self, key: KeyInstance, messages, model, temperature, max_tokens):
        """Call OpenAI-compatible API."""
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
        """Call Gemini API."""
        model_name = (model or key.models[0]).split("/")[-1]
        url = f"{key.base_url}/{model_name}:generateContent?key={key.api_key}"

        # Convert OpenAI format to Gemini format
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
            # Convert back to OpenAI-like format
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return {"choices": [{"message": {"content": text}}]}


# Global router instance
_router: Optional[MultiKeyRouter] = None


def get_router() -> MultiKeyRouter:
    global _router
    if _router is None:
        _router = MultiKeyRouter()
    return _router
