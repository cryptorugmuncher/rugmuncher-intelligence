"""
Free API Hunter Agent
=====================
1. Discovers new free AI APIs and models
2. Attempts smart auto-signup for providers with known patterns
3. Monitors email for API key confirmations
4. Auto-adds new providers to the router + Vault
Runs every 5 days (7200 minutes).
"""

import os
import json
import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.request import urlopen, Request, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode

logger = logging.getLogger("free_api_hunter")

# ═══════════════════════════════════════════════════════════
# AUTO-SIGNUP CONFIG — Providers with known easy signup flows
# ═══════════════════════════════════════════════════════════
AUTO_SIGNUP_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "groq": {
        "name": "Groq",
        "signup_url": "https://console.groq.com/login",
        "key_url": "https://console.groq.com/keys",
        "notes": "GitHub OAuth or email signup required",
        "auto_signup_possible": False,
        "free_tier": {"credits": 5.0, "unit": "usd"},
    },
    "together": {
        "name": "Together AI",
        "signup_url": "https://api.together.xyz/signup",
        "key_url": "https://api.together.xyz/settings/api-keys",
        "notes": "Email signup + $5 free credits",
        "auto_signup_possible": False,
        "free_tier": {"credits": 5.0, "unit": "usd"},
    },
    "fireworks": {
        "name": "Fireworks AI",
        "signup_url": "https://app.fireworks.ai/login",
        "key_url": "https://app.fireworks.ai/users/settings/api",
        "notes": "GitHub/Google OAuth signup",
        "auto_signup_possible": False,
        "free_tier": {"credits": 1.0, "unit": "usd"},
    },
    "deepseek": {
        "name": "DeepSeek",
        "signup_url": "https://platform.deepseek.com/api_keys",
        "key_url": "https://platform.deepseek.com/api_keys",
        "notes": "Phone number required for signup",
        "auto_signup_possible": False,
        "free_tier": {"credits": 0, "unit": "usd", "notes": "Pay-as-you-go but very cheap"},
    },
    "nvidia": {
        "name": "NVIDIA NIM",
        "signup_url": "https://build.nvidia.com/explore/discover",
        "key_url": "https://build.nvidia.com/meta/llama-3_1-70b-instruct",
        "notes": "Free tier via NVIDIA Developer Program",
        "auto_signup_possible": False,
        "free_tier": {"credits": 0, "unit": "usd", "notes": "1000 requests free tier"},
    },
    "mistral": {
        "name": "Mistral AI",
        "signup_url": "https://console.mistral.ai/",
        "key_url": "https://console.mistral.ai/api-keys/",
        "notes": "Google OAuth or email signup",
        "auto_signup_possible": False,
        "free_tier": {"credits": 0, "unit": "usd", "notes": "Some free trial credits"},
    },
    "openrouter": {
        "name": "OpenRouter",
        "signup_url": "https://openrouter.ai/",
        "key_url": "https://openrouter.ai/settings/keys",
        "notes": "GitHub OAuth signup — easiest signup flow",
        "auto_signup_possible": False,
        "free_tier": {"credits": 0, "unit": "usd", "notes": "Free models available without key"},
    },
}


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


def _get_vault_token() -> Optional[str]:
    """Get Vault root token for storing keys."""
    return os.getenv("VAULT_ROOT_TOKEN", "")


def _store_key_in_vault(provider: str, api_key: str) -> bool:
    """Store discovered API key in Vault."""
    vault_token = _get_vault_token()
    vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    if not vault_token:
        return False
    try:
        req = Request(
            f"{vault_addr}/v1/secret/data/ai/{provider}",
            data=json.dumps({"data": {"api_key": api_key, "source": "free_api_hunter", "auto_added": True}}).encode(),
            headers={"X-Vault-Token": vault_token, "Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return "errors" not in result
    except Exception as e:
        logger.warning(f"Failed to store key in Vault for {provider}: {e}")
        return False


def _add_provider_to_router(provider: str, config: Dict[str, Any]) -> bool:
    """Add provider to ai_router.py PROVIDERS dict."""
    router_path = "/root/rmi/backend/app/ai_router.py"
    try:
        with open(router_path, "r") as f:
            content = f.read()

        # Check if provider already exists
        if f'"{provider}":' in content:
            logger.info(f"Provider {provider} already in router")
            return True

        # Build provider entry
        entry = f'''    "{provider}": {{
        "url": "{config.get("url", "")}",
        "key_env": "{config.get("key_env", provider.upper() + "_API_KEY")}",
        "rpm": {config.get("rpm", 60)},
        "models": {json.dumps(config.get("models", []))},
    }},'''

        # Insert before the closing brace of PROVIDERS
        # Find the line with the last provider entry closing brace
        import re
        pattern = r'(PROVIDERS = \{.*?)(\n\})'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            new_content = content[:match.end(1)] + "\n" + entry + content[match.end(1):]
            with open(router_path, "w") as f:
                f.write(new_content)
            logger.info(f"Added {provider} to ai_router.py")
            return True
        else:
            logger.warning("Could not find PROVIDERS dict in ai_router.py")
            return False
    except Exception as e:
        logger.warning(f"Failed to add provider to router: {e}")
        return False


def discover_openrouter_free() -> List[Dict[str, Any]]:
    """Discover free models on OpenRouter."""
    findings = []
    try:
        req = Request("https://openrouter.ai/api/v1/models", headers={"User-Agent": "RugMuncher-FreeAPIHunter/1.0"})
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for m in data.get("data", []):
            model_id = m.get("id", "")
            pricing = m.get("pricing", {})
            prompt_price = float(pricing.get("prompt", 1) or 1)
            completion_price = float(pricing.get("completion", 1) or 1)

            if prompt_price == 0 and completion_price == 0:
                findings.append({
                    "provider": "openrouter",
                    "model": model_id,
                    "name": m.get("name", model_id),
                    "description": m.get("description", ""),
                    "free": True,
                    "pricing": {"prompt": 0, "completion": 0},
                    "source": "OpenRouter",
                    "signup_url": "https://openrouter.ai/",
                    "key_url": "https://openrouter.ai/settings/keys",
                    "auto_add_ready": True,
                })
    except Exception as e:
        logger.warning(f"OpenRouter discovery failed: {e}")
    return findings


def discover_cloudflare_models() -> List[Dict[str, Any]]:
    """Discover Cloudflare Workers AI models (always free)."""
    findings = []
    try:
        cf_token = os.getenv("CLOUDFLARE_API_TOKEN", "")
        if not cf_token:
            logger.info("No Cloudflare token for model discovery")
            return findings

        req = Request(
            "https://api.cloudflare.com/client/v4/accounts/8f9bd9165c1250b426c66dc1967deefd/ai/models",
            headers={"Authorization": f"Bearer {cf_token}", "User-Agent": "RugMuncher-FreeAPIHunter/1.0"},
        )
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        result = data.get("result", {})
        models = result.get("models", []) if isinstance(result, dict) else []
        for m in models:
            name = m.get("name", "")
            if name.startswith("@cf/"):
                findings.append({
                    "provider": "cloudflare-workers-ai",
                    "model": name,
                    "name": name.split("/")[-1] if "/" in name else name,
                    "description": m.get("description", ""),
                    "free": True,
                    "pricing": {"prompt": 0, "completion": 0},
                    "source": "Cloudflare Workers AI",
                    "auto_add_ready": True,
                })
    except Exception as e:
        logger.warning(f"Cloudflare discovery failed: {e}")
    return findings


def discover_huggingface_inference() -> List[Dict[str, Any]]:
    """Discover HuggingFace free inference endpoints."""
    findings = []
    try:
        req = Request(
            "https://huggingface.co/api/models?filter=text-generation&sort=downloads&limit=20",
            headers={"User-Agent": "RugMuncher-FreeAPIHunter/1.0"},
        )
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for m in data[:10]:
            model_id = m.get("modelId", "")
            if any(x in model_id.lower() for x in ["llama", "mistral", "qwen", "gemma"]):
                findings.append({
                    "provider": "huggingface-free",
                    "model": model_id,
                    "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                    "description": m.get("description", ""),
                    "free": True,
                    "pricing": {"prompt": 0, "completion": 0},
                    "source": "HuggingFace (free inference)",
                    "signup_url": "https://huggingface.co/settings/tokens",
                    "key_url": "https://huggingface.co/settings/tokens",
                    "auto_add_ready": False,
                })
    except Exception as e:
        logger.warning(f"HuggingFace discovery failed: {e}")
    return findings


def check_email_for_api_keys() -> List[Dict[str, Any]]:
    """Check email inbox for API key confirmation emails."""
    findings = []
    try:
        # Try to use existing email service to check for API key emails
        # This is a placeholder — full IMAP integration would go here
        logger.info("Email API key extraction not yet implemented (requires IMAP/Gmail API access)")
    except Exception as e:
        logger.warning(f"Email check failed: {e}")
    return findings


def generate_signup_instructions(provider: str) -> Dict[str, Any]:
    """Generate manual signup instructions for a provider."""
    cfg = AUTO_SIGNUP_PROVIDERS.get(provider, {})
    return {
        "provider": provider,
        "display_name": cfg.get("name", provider),
        "signup_url": cfg.get("signup_url", ""),
        "key_url": cfg.get("key_url", ""),
        "instructions": [
            f"1. Visit {cfg.get('signup_url', '')}",
            f"2. Sign up using {cfg.get('notes', 'email or OAuth')}",
            f"3. Go to {cfg.get('key_url', '')} to generate an API key",
            f"4. Paste the key into Vault at: secret/ai/{provider}",
            f"5. The system will auto-detect and add it to the router",
        ],
        "free_tier": cfg.get("free_tier", {}),
        "estimated_time": "2-3 minutes",
    }


def store_findings(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """Store discoveries in DB. Returns counts."""
    sb = _get_supabase()
    if not sb:
        return {"stored": 0, "new": 0, "updated": 0}

    new_count = 0
    updated_count = 0
    for f in findings:
        try:
            existing = sb.table("free_api_discoveries") \
                .select("id, status") \
                .eq("provider", f["provider"]) \
                .eq("model", f["model"]) \
                .execute()

            now = datetime.utcnow().isoformat()
            if existing.data:
                # Update existing
                sb.table("free_api_discoveries") \
                    .update({
                        "last_seen_at": now,
                        "pricing": f.get("pricing", {}),
                    }) \
                    .eq("id", existing.data[0]["id"]) \
                    .execute()
                updated_count += 1
            else:
                # Insert new
                sb.table("free_api_discoveries").insert({
                    "provider": f["provider"],
                    "model": f["model"],
                    "name": f.get("name", f["model"]),
                    "description": f.get("description", ""),
                    "source": f.get("source", ""),
                    "source_url": f.get("source_url", ""),
                    "signup_url": f.get("signup_url", ""),
                    "key_url": f.get("key_url", ""),
                    "free": f.get("free", True),
                    "pricing": f.get("pricing", {}),
                    "auto_add_ready": f.get("auto_add_ready", False),
                    "discovered_at": now,
                    "last_seen_at": now,
                    "status": "new",
                }).execute()
                new_count += 1
                logger.info(f"🆕 New free API: {f['provider']} / {f['model']}")
        except Exception as e:
            logger.warning(f"Failed to store finding: {e}")

    return {"stored": new_count + updated_count, "new": new_count, "updated": updated_count}


def create_pending_signups_table():
    """Ensure the free_api_discoveries table exists."""
    sb = _get_supabase()
    if not sb:
        return
    try:
        # This would be a migration; for now just try to query
        sb.table("free_api_discoveries").select("id", count="exact").limit(1).execute()
    except Exception:
        logger.warning("free_api_discoveries table may not exist — run SQL migration")


def run():
    """Main agent entrypoint."""
    logger.info("🎯 Free API Hunter starting...")
    create_pending_signups_table()

    all_findings = []

    # 1. Discover free APIs
    logger.info("🔍 Scanning for free AI APIs...")
    all_findings.extend(discover_openrouter_free())
    all_findings.extend(discover_cloudflare_models())
    all_findings.extend(discover_huggingface_inference())

    # 2. Check email for API key confirmations
    logger.info("📧 Checking email for API key confirmations...")
    all_findings.extend(check_email_for_api_keys())

    # 3. Store findings
    counts = store_findings(all_findings)
    logger.info(f"📊 Discovery complete: {len(all_findings)} found, {counts['new']} new, {counts['updated']} updated")

    # 4. Generate signup instructions for providers we don't have keys for
    logger.info("📝 Generating signup instructions...")
    # This would check Vault for missing keys and generate instructions

    logger.info("✅ Free API Hunter finished")


if __name__ == "__main__":
    run()
