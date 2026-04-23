#!/usr/bin/env python3
"""
RMI Environment Loader — Reads API keys from vault and secrets
===============================================================
Priority: 1) Vault server 2) /root/.secrets/ files 3) Existing env vars
"""

import os
import sys
import json
import glob

SECRETS_DIR = "/root/.secrets"
VAULT_KEYS_FILE = "/root/vault/init-keys.json"

def load_from_secrets():
    """Load API keys from /root/.secrets/ directory"""
    env = {}
    if not os.path.isdir(SECRETS_DIR):
        return env

    # Map secret filenames to environment variable names
    SECRET_MAP = {
        "arkham_api_key": "ARKHAM_API_KEY",
        "coingecko_api_key": "COINGECKO_API_KEY",
        "gemini_api_key": "GEMINI_API_KEY",
        "helius_api_key": "HELIUS_API_KEY",
        "helius_api_key_2": "HELIUS_API_KEY_2",
        "huggingface_token": "HUGGINGFACE_TOKEN",
        "kimi_api_key": "KIMI_API_KEY",
        "mistral_api_key": "MISTRAL_API_KEY",
        "moralis_api_key": "MORALIS_API_KEY",
        "nvidia_api_key": "NVIDIA_API_KEY",
        "nvidia_dev_api_key": "NVIDIA_DEV_API_KEY",
        "quicknode_api_key": "QUICKNODE_KEY",
        "solscan_api_key": "SOLSCAN_API_KEY",
    }

    for filename, env_var in SECRET_MAP.items():
        filepath = os.path.join(SECRETS_DIR, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                value = f.read().strip()
                if value and not value.startswith("YOUR_"):
                    env[env_var] = value

    return env

def load_env_file():
    """Load from .env.secure"""
    env = {}
    env_path = "/root/.env.secure"
    if os.path.isfile(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    env[key] = value
    return env

def generate_complete_env():
    """Generate complete .env for docker-compose"""
    # Start with existing env
    env = load_env_file()

    # Override with secrets
    secrets = load_from_secrets()
    env.update(secrets)

    # Set derived values
    env["REDIS_HOST"] = env.get("REDIS_HOST", "dragonfly")
    env["REDIS_PORT"] = env.get("REDIS_PORT", "6379")
    env["REDIS_DB"] = env.get("REDIS_DB", "0")
    env["SUPABASE_URL"] = env.get("SUPABASE_URL", "https://ufblzfxqwgaekrewncbi.supabase.co")
    env["HOST"] = "0.0.0.0"
    env["PORT"] = "8000"
    env["DEBUG"] = "false"
    env["N8N_WEBHOOK_URL"] = env.get("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/")
    env["WEBHOOK_URL"] = env.get("WEBHOOK_URL", "http://n8n:5678/webhook/")

    # Write docker-compatible env file
    output = []
    for key in sorted(env.keys()):
        value = env[key]
        if " " in value or "#" in value:
            output.append(f'{key}="{value}"')
        else:
            output.append(f"{key}={value}")

    env_content = "\n".join(output)

    with open("/root/rmi/.env", "w") as f:
        f.write(env_content + "\n")

    # Also write individual secret files for docker-compose
    with open("/root/rmi/backend/.env", "w") as f:
        f.write(env_content + "\n")

    print(f"[ENV] Generated .env with {len(env)} variables")
    print(f"[ENV] Keys loaded from secrets: {list(secrets.keys())}")

    return env

if __name__ == "__main__":
    generate_complete_env()

