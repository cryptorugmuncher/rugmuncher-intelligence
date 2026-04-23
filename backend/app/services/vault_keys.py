"""
Vault Key Manager
=================
Retrieves API keys and secrets from HashiCorp Vault for RMI.
"""

import os
import sys
import json
import logging
import urllib.request
from typing import Dict, Optional, Any

logger = logging.getLogger("vault_keys")

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_ROLE_ID = os.getenv("VAULT_ROLE_ID", "")
VAULT_SECRET_ID = os.getenv("VAULT_SECRET_ID", "")
VAULT_ROOT_TOKEN = os.getenv("VAULT_ROOT_TOKEN", "")

_cache: Dict[str, Any] = {}


def _vault_login() -> str:
    """Login via AppRole and return client token."""
    if VAULT_ROOT_TOKEN:
        return VAULT_ROOT_TOKEN

    url = f"{VAULT_ADDR}/v1/auth/approle/login"
    data = json.dumps({"role_id": VAULT_ROLE_ID, "secret_id": VAULT_SECRET_ID}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        return result["auth"]["client_token"]


def get_secret(path: str, key: Optional[str] = None) -> Any:
    """Read a secret from Vault with caching."""
    cache_key = f"{path}:{key}"
    if cache_key in _cache:
        return _cache[cache_key]

    token = _vault_login()
    url = f"{VAULT_ADDR}/v1/secret/data/{path}"
    req = urllib.request.Request(url, headers={"X-Vault-Token": token}, method="GET")

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        data = result["data"]["data"]

    value = data.get(key) if key else data
    _cache[cache_key] = value
    return value


def get_ai_key(provider: str) -> Optional[str]:
    """Get API key for an AI provider."""
    mapping = {
        "openai": ("ai/openai", "api_key"),
        "anthropic": ("ai/anthropic", "api_key"),
        "groq": ("ai/groq", "api_key"),
        "deepseek": ("ai/deepseek", "api_key"),
        "mistral": ("ai/mistral", "api_key"),
        "fireworks": ("ai/fireworks", "api_key"),
        "nvidia": ("ai/nvidia", "api_key"),
        "gemini": ("ai/gemini", "api_key"),
        "openrouter": ("ai/openrouter", "api_key"),
        "zai": ("ai/zai", "api_key"),
    }
    path, key = mapping.get(provider, (None, None))
    if not path:
        return None
    try:
        return get_secret(path, key)
    except Exception as e:
        logger.warning(f"Vault lookup failed for {provider}: {e}")
        return None


def get_cloudflare_token() -> Optional[str]:
    """Get Cloudflare API token."""
    try:
        return get_secret("rmi/cloudflare", "api_token")
    except Exception as e:
        logger.warning(f"Vault lookup failed for cloudflare: {e}")
        return None


def get_all_ai_keys() -> Dict[str, Optional[str]]:
    """Fetch all available AI keys."""
    providers = ["openai", "anthropic", "groq", "deepseek", "mistral", "fireworks", "nvidia", "gemini", "openrouter", "zai"]
    return {p: get_ai_key(p) for p in providers}
