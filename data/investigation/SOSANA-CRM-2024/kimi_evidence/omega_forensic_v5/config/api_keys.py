"""
Omega Forensic V5 - API Keys Configuration
============================================
Centralized API configuration for all forensic divisions.
Loaded from environment variables with fallback to secure storage.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class APIConfig:
    """Container for API configuration with validation."""
    key: str
    endpoint: Optional[str] = None
    tier: str = "free"  # free, paid, enterprise
    rate_limit: int = 100  # requests per minute
    
    @property
    def is_configured(self) -> bool:
        return bool(self.key) and self.key not in ["", "your_key_here"]

class ForensicAPIKeys:
    """
    Centralized API key management for Omega Forensic V5.
    All keys loaded from environment variables for security.
    """
    
    # === DIVISION 1: IDENTITY & AML ===
    ARKHAM_API_KEY = os.getenv("ARKHAM_API_KEY", "bbbebc4f-0727-4157-87cc-42f8991a58ca")
    MISTTRACK_API_KEY = os.getenv("MISTTRACK_API_KEY", "ynX083xAuSk4WKEsaHpOFw5DYd91ZlmI")
    CHAINABUSE_API_KEY = os.getenv("CHAINABUSE_API_KEY", "ca_VDBVeWVTT3F5TGRPeFVyb1Y4cVhWNnpFLktJYVNHZUVXa0QvZmIxNXVuektaNUE9PQ")
    
    # === DIVISION 2: ON-CHAIN AUTOPSY ===
    HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "771413f9-60c9-4714-94d6-33851d1e6d88")
    QUICKNODE_SOL_RPC = os.getenv("QUICKNODE_SOL_RPC", "https://wandering-rough-butterfly.solana-mainnet.quiknode.pro/875fa003546494c35631050925b5e966baa4b81d/")
    SOLSCAN_API_KEY = os.getenv("SOLSCAN_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NDM3Mjk5NzY0MjUsImVtYWlsIjoiamF5dHJhbmNlQGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOjIsImlhdCI6MTc0MzcyOTk3Nn0.4MpOu1mE24T6XqQJ7zJ-0iLrPE6jQpbjxw33RwAiVOE")
    
    # === DIVISION 3: TOKEN MECHANICS ===
    BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "58c5b02e9e484c73b02691687379673a")
    LUNARCRUSH_API_KEY = os.getenv("LUNARCRUSH_API_KEY", "mu5cf8zde098q1hti2t8tmfrsgmnh3ifzxpad14y9")
    
    # === DIVISION 4: REAL WORLD OSINT ===
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "faee04c161280c9e83ed2fed949d175b4fbb3222")
    
    # === AI/LLM APIs ===
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-a86c88e9f6224ffba9d866f032225eb6")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
    
    # === TELEGRAM ===
    TG_TOKEN = os.getenv("TG_TOKEN", "8765109525:AAFEb0dQd11wm2EIbGf_mf0W1776t36Q1kU")
    
    # === TARGET ===
    TARGET_CA = os.getenv("TARGET_CA", "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS")
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, APIConfig]:
        """Get all API configurations with metadata."""
        return {
            # Division 1: Identity & AML
            "arkham": APIConfig(
                key=cls.ARKHAM_API_KEY,
                endpoint="https://api.arkhamintelligence.com",
                tier="enterprise",
                rate_limit=1000
            ),
            "misttrack": APIConfig(
                key=cls.MISTTRACK_API_KEY,
                endpoint="https://misttrack.io/api",
                tier="paid",
                rate_limit=300
            ),
            "chainabuse": APIConfig(
                key=cls.CHAINABUSE_API_KEY,
                endpoint="https://api.chainabuse.com",
                tier="free",
                rate_limit=100
            ),
            # Division 2: On-Chain Autopsy
            "helius": APIConfig(
                key=cls.HELIUS_API_KEY,
                endpoint="https://api.helius.xyz",
                tier="paid",
                rate_limit=500
            ),
            "quicknode": APIConfig(
                key=cls.QUICKNODE_SOL_RPC,
                endpoint=cls.QUICKNODE_SOL_RPC,
                tier="paid",
                rate_limit=1000
            ),
            "solscan": APIConfig(
                key=cls.SOLSCAN_API_KEY,
                endpoint="https://api.solscan.io",
                tier="free",
                rate_limit=100
            ),
            # Division 3: Token Mechanics
            "birdeye": APIConfig(
                key=cls.BIRDEYE_API_KEY,
                endpoint="https://public-api.birdeye.so",
                tier="paid",
                rate_limit=300
            ),
            "lunarcrush": APIConfig(
                key=cls.LUNARCRUSH_API_KEY,
                endpoint="https://api.lunarcrush.com",
                tier="free",
                rate_limit=200
            ),
            # Division 4: Real World OSINT
            "serper": APIConfig(
                key=cls.SERPER_API_KEY,
                endpoint="https://google.serper.dev",
                tier="free",
                rate_limit=100
            ),
            # AI/LLM
            "groq": APIConfig(
                key=cls.GROQ_API_KEY,
                endpoint="https://api.groq.com",
                tier="paid",
                rate_limit=1000
            ),
            "deepseek": APIConfig(
                key=cls.DEEPSEEK_API_KEY,
                endpoint="https://api.deepseek.com",
                tier="paid",
                rate_limit=500
            ),
            "openrouter": APIConfig(
                key=cls.OPENROUTER_API_KEY,
                endpoint="https://openrouter.ai/api",
                tier="free",
                rate_limit=200
            ),
        }
    
    @classmethod
    def get_configured_apis(cls) -> list:
        """Return list of properly configured APIs."""
        configs = cls.get_all_configs()
        return [name for name, config in configs.items() if config.is_configured]
    
    @classmethod
    def get_missing_apis(cls) -> list:
        """Return list of APIs that need configuration."""
        configs = cls.get_all_configs()
        return [name for name, config in configs.items() if not config.is_configured]
    
    @classmethod
    def validate_all(cls) -> Dict[str, bool]:
        """Validate all API keys and return status."""
        configs = cls.get_all_configs()
        return {name: config.is_configured for name, config in configs.items()}

# === QUICK ACCESS FUNCTIONS ===
def get_api_key(service: str) -> str:
    """Quick access to any API key by service name."""
    configs = ForensicAPIKeys.get_all_configs()
    if service.lower() in configs:
        return configs[service.lower()].key
    raise ValueError(f"Unknown service: {service}")

def is_api_ready(service: str) -> bool:
    """Check if a specific API is configured and ready."""
    configs = ForensicAPIKeys.get_all_configs()
    if service.lower() in configs:
        return configs[service.lower()].is_configured
    return False

# === SERVER INFO ===
SERVER_IP = "167.86.116.51"
SERVER_USER = "root"
SERVER_WORKDIR = "/root/crm_audit"

def get_server_info():
    """Return server connection information."""
    return {
        "ip": SERVER_IP,
        "user": SERVER_USER,
        "workdir": SERVER_WORKDIR,
        "ssh_command": f"ssh {SERVER_USER}@{SERVER_IP}",
        "api_status": ForensicAPIKeys.validate_all(),
        "configured_apis": ForensicAPIKeys.get_configured_apis(),
        "missing_apis": ForensicAPIKeys.get_missing_apis()
    }

if __name__ == "__main__":
    # Print server info and API status
    import json
    info = get_server_info()
    print("=" * 60)
    print("OMEGA FORENSIC V5 - SERVER & API STATUS")
    print("=" * 60)
    print(f"\nServer: {info['user']}@{info['ip']}")
    print(f"Workdir: {info['workdir']}")
    print(f"\nSSH: {info['ssh_command']}")
    print("\n" + "-" * 60)
    print("API STATUS:")
    print("-" * 60)
    for api, status in info['api_status'].items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {api:15} {'READY' if status else 'NOT CONFIGURED'}")
    print("\n" + "=" * 60)
