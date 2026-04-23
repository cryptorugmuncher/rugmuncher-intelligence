"""
⚙️ Rug Munch Bot Configuration
===============================
Single source of truth for @rugmunchbot settings.
"""

import os
from dataclasses import dataclass
from typing import Dict, List

# Bot Identity
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = "rugmunchbot"
BOT_NAME = "Rug Munch"
BOT_TAGLINE = "Don't Get Rugged"

# Channel IDs (negative numbers for channels)
CHANNEL_SCANS = os.getenv("CHANNEL_SCANS", "")
CHANNEL_NEWS = os.getenv("CHANNEL_NEWS", "")
CHANNEL_ALERTS = os.getenv("CHANNEL_ALERTS", "")
CHANNEL_PREMIUM = os.getenv("CHANNEL_PREMIUM", "")

# Private group support — users can add @rugmunchbot to their own group
# The bot responds to commands in any private or public group it's added to
GROUP_WELCOME_MESSAGE = os.getenv("GROUP_WELCOME_MESSAGE", "🤖 Rug Munch bot activated in this group! Use /security, /scan, /audit, or /help.")

# Backend URLs
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8082")

# Telegram Mini App URL (opens web app inside Telegram)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://rugmunch.io")

# Payment
STARS_PROVIDER_TOKEN = os.getenv("STARS_PROVIDER_TOKEN", "")
CRYPTO_PAYMENT_WEBHOOK = os.getenv("CRYPTO_PAYMENT_WEBHOOK", "")

# Rate Limiting (Dragonfly/Redis)
REDIS_HOST = os.getenv("REDIS_HOST", "dragonfly")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Scan Limits
FREE_SCANS_PER_MONTH = 3
BASIC_SCANS_PER_MONTH = 25
PRO_SCANS_PER_MONTH = 100
ELITE_SCANS_PER_MONTH = 9999

@dataclass
class TierConfig:
    name: str
    price_usd: float
    price_stars: int
    scans_per_month: int
    features: List[str]
    color: str

TIERS: Dict[str, TierConfig] = {
    "free": TierConfig(
        name="Free",
        price_usd=0.0,
        price_stars=0,
        scans_per_month=FREE_SCANS_PER_MONTH,
        features=["Basic contract scan", "Risk score", "1 chain"],
        color="#9CA3AF",
    ),
    "basic": TierConfig(
        name="Basic",
        price_usd=5.0,
        price_stars=50,
        scans_per_month=BASIC_SCANS_PER_MONTH,
        features=["Full contract scan", "Wallet check", "All chains", "Holder analysis"],
        color="#3B82F6",
    ),
    "pro": TierConfig(
        name="Pro",
        price_usd=15.0,
        price_stars=150,
        scans_per_month=PRO_SCANS_PER_MONTH,
        features=["Deep analysis", "Predictive alerts", "Smart money tracking", "Priority queue"],
        color="#8B5CF6",
    ),
    "elite": TierConfig(
        name="Elite",
        price_usd=40.0,
        price_stars=400,
        scans_per_month=ELITE_SCANS_PER_MONTH,
        features=["Unlimited scans", "Custom alerts", "Group admin tools", "API access"],
        color="#EAB308",
    ),
}

SCAN_PACKS = {
    "5_scans": {"scans": 5, "price_usd": 3.0, "price_stars": 30},
    "15_scans": {"scans": 15, "price_usd": 8.0, "price_stars": 80},
    "50_scans": {"scans": 50, "price_usd": 20.0, "price_stars": 200},
}

# Risk Score Colors
RISK_COLORS = {
    "safe": "🟢",
    "low": "🟡",
    "medium": "🟠",
    "high": "🔴",
    "critical": "☠️",
}

# Command List (for BotFather /setcommands)
COMMANDS = """
security - Analyze token contract for scams
scan - Full intelligence report on a token
predict - ML rug pull prediction
whales - Whale concentration analysis
holders - Top holder distribution
bundle - Detect wallet bundling
audit - Smart contract code audit
portfolio - Track wallet portfolio
news - Crypto news digest
status - Check your subscription tier
upgrade - Upgrade scan tier
pay - Purchase scans with Stars or crypto
help - Show all commands
"""
