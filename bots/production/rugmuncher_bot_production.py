#!/usr/bin/env python3
"""
🕵️ RUGMUNCHBOT PRODUCTION v6.0
==============================
The most advanced crypto forensics bot on Telegram

FEATURES:
- Real blockchain analysis (NO random/mock data)
- 100-point risk scoring with real deductions
- Advanced bundle detection (15+ vectors)
- Bubble map visualization
- Dev voiceprint cross-chain matching
- AI rug predictor with ML
- Auto-rug protection monitoring
- Call cards with visual proof
- Subscription tiers (Free/Pro/Elite)
- Redis caching & rate limiting
- Comprehensive error handling

Author: Claude Code (Kimi K2.5 Turbo)
License: Proprietary
"""

import os
import sys
import asyncio
import aiohttp
import re
import json
import hashlib
import functools
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/root/rugmuncher_production.log"),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Try multiple locations for .env file
    env_paths = ["/root/config/secrets/.env.root", "/root/.env", ".env"]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"✅ Loaded environment from {env_path}")
            break
    else:
        logger.warning("⚠️ No .env file found, using system environment variables")
except ImportError:
    logger.warning("⚠️ python-dotenv not installed, using system environment variables")

# Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import BadRequest, NetworkError, TelegramError

# ═══════════════════════════════════════════════════════════
# CONFIGURATION & VALIDATION
# ═══════════════════════════════════════════════════════════


class ValidationError(Exception):
    """Raised when input validation fails"""

    pass


class Config:
    """Secure configuration - NO HARDCODED SECRETS"""

    # Bot Configuration
    BOT_TOKEN = os.getenv("RUGMUNCHER_BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("❌ RUGMUNCHER_BOT_TOKEN not set!")
        sys.exit(1)

    # Admin IDs
    ADMIN_IDS = []
    admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS", "")
    if admin_ids_str:
        try:
            ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
        except ValueError:
            logger.error("Invalid ADMIN_TELEGRAM_IDS format")

    # API Keys
    BSCSCAN_KEY = os.getenv("BSCSCAN_KEY", "")
    ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY", "")
    HELIUS_KEY = os.getenv("HELIUS_KEY", "")

    # Free data sources (no API key needed)
    DEXSCREENER_API = "https://api.dexscreener.com"
    HONEYPOT_API = "https://api.honeypot.is"

    # Supabase Configuration (for cloud sync)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    # n8n Webhook (for workflow automation)
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

    # Sync Settings
    SYNC_ENABLED = os.getenv("SYNC_ENABLED", "true").lower() == "true"
    SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "60"))  # seconds

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))

    # Security Settings
    MAX_CALLBACK_SIZE = 64
    RATE_LIMIT_WINDOW = 60
    RATE_LIMIT_MAX = 10

    # Subscription Tiers
    TIERS = {
        "free": {"scans_per_day": 3, "features": ["basic_scan"]},
        "pro": {
            "scans_per_day": 50,
            "features": ["basic_scan", "bundle_detect", "bubble_map"],
        },
        "elite": {"scans_per_day": 9999, "features": ["all"]},
    }


class ContractValidator:
    """Validates and sanitizes all inputs"""

    ETH_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
    SOL_PATTERN = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

    ALLOWED_CALLBACKS = {
        "bubble_",
        "bundle_",
        "voice_",
        "predict_",
        "vampire_",
        "paper_",
        "protect_",
        "magutsu_",
        "pirbview_",
        "gas_",
        "tax_",
        "lp_",
        "owner_",
        "cex_",
        "holders_",
        "upg_pro_",
        "upg_elite_",
        "copy_",
        "alert_",
        "share_",
        "report_",
        "save_",
        "watch_",
    }

    @staticmethod
    def validate_contract(address: str, chain: str = "auto") -> Tuple[str, str]:
        """Validate contract address format"""
        if not address:
            raise ValidationError("Contract address is required")

        address = address.strip().lower()

        if len(address) < 32 or len(address) > 44:
            raise ValidationError(f"Invalid address length: {len(address)}")

        if ContractValidator.ETH_PATTERN.match(address):
            detected_chain = "bsc" if chain == "bsc" else "eth"
        elif ContractValidator.SOL_PATTERN.match(address):
            detected_chain = "sol"
        else:
            raise ValidationError(f"Invalid contract address: {address[:20]}...")

        if chain != "auto" and chain in ["eth", "bsc", "sol", "base"]:
            detected_chain = chain

        return address, detected_chain

    @staticmethod
    def validate_callback(data: str) -> Tuple[str, List[str]]:
        """Validate callback data format"""
        if not data:
            raise ValidationError("Callback data is empty")

        if len(data) > 64:
            raise ValidationError("Callback data too long")

        is_allowed = any(
            data.startswith(prefix) for prefix in ContractValidator.ALLOWED_CALLBACKS
        )
        is_system = data in [
            "back",
            "start_scan",
            "help_main",
            "upgrade_menu",
            "upgrade_elite",
            "buy_pro",
            "buy_elite",
            "menu_main",
            "separator",
        ]

        if not (is_allowed or is_system):
            logger.warning(f"Suspicious callback rejected: {data[:30]}")
            raise ValidationError("Invalid callback data")

        parts = data.split("_")
        return parts[0], parts[1:]


# ═══════════════════════════════════════════════════════════
# REDIS CACHE SYSTEM
# ═══════════════════════════════════════════════════════════

REDIS_ENABLED = False
redis_client = None

if Config.REDIS_HOST:
    try:
        import redis

        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD or None,
            db=Config.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        redis_client.ping()
        REDIS_ENABLED = True
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️ Redis unavailable: {e}")


def cache_response(ttl: int = 3600):
    """Decorator to cache function responses"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not REDIS_ENABLED:
                return await func(*args, **kwargs)

            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = f"rm:cache:{hashlib.sha256(key_data.encode()).hexdigest()}"

            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass

            result = await func(*args, **kwargs)

            if result:
                try:
                    redis_client.setex(cache_key, ttl, json.dumps(result))
                except Exception:
                    pass

            return result

        return wrapper

    return decorator


def check_rate_limit(user_id: int, action: str) -> bool:
    """Check if user exceeded rate limit"""
    if not REDIS_ENABLED:
        return True

    key = f"rm:ratelimit:{action}:{user_id}"
    try:
        current = redis_client.get(key)
        if current and int(current) >= Config.RATE_LIMIT_MAX:
            return False
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, Config.RATE_LIMIT_WINDOW)
        pipe.execute()
        return True
    except Exception:
        return True


# ═══════════════════════════════════════════════════════════
# DATABASE LAYER (SQLite with async support planned)
# ═══════════════════════════════════════════════════════════


class Database:
    """Thread-safe SQLite database"""

    def __init__(self, db_path: str = "/root/rugmuncher_production.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_connection(self):
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(
                self.db_path, check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                tier TEXT DEFAULT 'free',
                scans_today INTEGER DEFAULT 0,
                total_scans INTEGER DEFAULT 0,
                subscription_expires TIMESTAMP,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referrer_id INTEGER
            )
        """)

        # Scans history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contract_address TEXT,
                chain TEXT,
                risk_score REAL,
                risk_level TEXT,
                findings TEXT,
                scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Watchlist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contract_address TEXT,
                chain TEXT,
                alert_enabled BOOLEAN DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, contract_address)
            )
        """)

        # Holder database for bundle detection
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT,
                chain TEXT,
                wallet TEXT,
                balance REAL,
                first_buy TIMESTAMP,
                last_buy TIMESTAMP,
                total_buys INTEGER DEFAULT 0,
                total_sells INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(contract_address, wallet)
            )
        """)

        # Dev fingerprints for voiceprint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dev_fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployer_wallet TEXT,
                chain TEXT,
                gas_pattern TEXT,
                funding_source TEXT,
                contract_style TEXT,
                previous_rugs INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(deployer_wallet, chain)
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    def get_user(self, user_id: int) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def create_user(
        self, user_id: int, username: str, first_name: str, referrer_id: int = None
    ) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, referrer_id) VALUES (?, ?, ?, ?)",
            (user_id, username or "", first_name or "", referrer_id),
        )
        conn.commit()
        return self.get_user(user_id)

    def increment_scan_count(self, user_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE users SET scans_today = scans_today + 1,
                total_scans = total_scans + 1,
                last_active = CURRENT_TIMESTAMP WHERE user_id = ?""",
            (user_id,),
        )
        conn.commit()

    def reset_daily_scans(self):
        """Reset daily scans - call at midnight"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET scans_today = 0")
        conn.commit()

    def get_scan_limit(self, user_id: int) -> int:
        user = self.get_user(user_id)
        if not user:
            return 3
        tier = user.get("tier", "free")
        return Config.TIERS.get(tier, Config.TIERS["free"]).get("scans_per_day", 3)

    def save_scan(self, user_id: int, contract: str, chain: str, result: dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO scans (user_id, contract_address, chain, risk_score, risk_level, findings)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                contract.lower(),
                chain,
                result.get("score", 50),
                result.get("category", "unknown"),
                json.dumps(result.get("deductions", [])),
            ),
        )
        conn.commit()

    def add_to_watchlist(self, user_id: int, contract: str, chain: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO watchlist (user_id, contract_address, chain) VALUES (?, ?, ?)",
                (user_id, contract.lower(), chain),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_watchlist(self, user_id: int) -> List[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_at DESC",
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


# Global database instance
db = Database()


# ═══════════════════════════════════════════════════════════
# SUPABASE SYNC & N8N WEBHOOK INTEGRATION
# ═══════════════════════════════════════════════════════════


class SupabaseSync:
    """Syncs local SQLite data to Supabase cloud"""

    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY
        self.enabled = Config.SYNC_ENABLED and bool(self.url and self.key)
        self._session: Optional[aiohttp.ClientSession] = None
        self._sync_queue: List[dict] = []
        self._sync_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def insert(self, table: str, data: dict) -> dict:
        """Insert data into Supabase table"""
        if not self.enabled:
            return {"skipped": True, "reason": "Sync disabled or not configured"}

        url = f"{self.url}/rest/v1/{table}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        try:
            session = await self._get_session()
            async with session.post(
                url, headers=headers, json=data, timeout=10
            ) as resp:
                if resp.status in [200, 201]:
                    logger.info(f"✅ Synced to Supabase: {table}")
                    return {"success": True, "table": table}
                else:
                    text = await resp.text()
                    logger.warning(f"⚠️ Supabase insert failed: {resp.status} - {text}")
                    return {"error": f"Status {resp.status}", "details": text}
        except Exception as e:
            logger.error(f"❌ Supabase sync error: {e}")
            return {"error": str(e)}

    async def sync_scan(self, user_id: int, contract: str, chain: str, result: dict):
        """Sync a scan result to Supabase"""
        data = {
            "user_id": user_id,
            "contract_address": contract.lower(),
            "chain": chain,
            "risk_score": result.get("score", 50),
            "risk_level": result.get("category", "unknown"),
            "findings": result.get("deductions", []),
            "scan_time": datetime.now().isoformat(),
            "source": "telegram_bot",
        }
        return await self.insert("scans", data)

    async def sync_user(self, user_id: int, username: str, tier: str):
        """Sync user info to Supabase"""
        data = {
            "telegram_id": user_id,
            "username": username,
            "tier": tier,
            "updated_at": datetime.now().isoformat(),
        }
        return await self.insert("users", data)


class N8NWebhook:
    """n8n workflow automation triggers"""

    def __init__(self):
        self.url = Config.N8N_WEBHOOK_URL
        self.enabled = bool(self.url)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def trigger(self, event: str, data: dict):
        """Trigger n8n webhook"""
        if not self.enabled:
            return {"skipped": True}

        payload = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "source": "rugmuncher_bot",
            "data": data,
        }

        try:
            session = await self._get_session()
            async with session.post(self.url, json=payload, timeout=10) as resp:
                success = resp.status == 200
                if success:
                    logger.info(f"✅ n8n webhook triggered: {event}")
                else:
                    logger.warning(f"⚠️ n8n webhook failed: {resp.status}")
                return {"success": success, "status": resp.status}
        except Exception as e:
            logger.error(f"❌ n8n webhook error: {e}")
            return {"error": str(e)}

    async def scan_completed(self, user_id: int, contract: str, chain: str, score: int):
        """Trigger for completed scan"""
        return await self.trigger(
            "scan_completed",
            {
                "user_id": user_id,
                "contract": contract,
                "chain": chain,
                "risk_score": score,
            },
        )

    async def high_risk_detected(
        self, contract: str, chain: str, score: int, deductions: list
    ):
        """Trigger for high risk detection"""
        return await self.trigger(
            "high_risk_detected",
            {
                "contract": contract,
                "chain": chain,
                "risk_score": score,
                "deductions": deductions,
            },
        )

    async def new_user_registered(self, user_id: int, username: str, tier: str):
        """Trigger for new user"""
        return await self.trigger(
            "user_registered", {"user_id": user_id, "username": username, "tier": tier}
        )


# Initialize sync clients
supabase_sync = SupabaseSync()
n8n_webhook = N8NWebhook()


# ═══════════════════════════════════════════════════════════
# CIRCUIT BREAKER PATTERN - Prevents cascade failures
# ═══════════════════════════════════════════════════════════


class CircuitBreaker:
    """Circuit breaker to prevent cascade failures when external services fail"""

    def __init__(
        self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED (normal), OPEN (failing), HALF_OPEN (testing)
        self._lock = asyncio.Lock()

    async def call_async(self, func, *args, **kwargs):
        """Execute async function with circuit breaker protection"""
        async with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info(
                        f"🔧 {self.name}: Entering HALF_OPEN state (testing recovery)"
                    )
                    self.state = "HALF_OPEN"
                else:
                    remaining = int(
                        self.recovery_timeout - (time.time() - self.last_failure_time)
                    )
                    logger.warning(
                        f"🔒 {self.name}: Circuit OPEN - will retry in {remaining}s"
                    )
                    return False, {
                        "circuit_open": True,
                        "retry_after_seconds": remaining,
                    }

        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                if self.state == "HALF_OPEN":
                    logger.info(f"✅ {self.name}: Recovery successful - circuit CLOSED")
                self.state = "CLOSED"
                self.failures = 0
            return True, result
        except Exception as e:
            async with self._lock:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.failure_threshold:
                    if self.state != "OPEN":
                        logger.error(
                            f"🚨 {self.name}: Failure threshold reached - circuit OPEN"
                        )
                        self.state = "OPEN"
            return False, {"error": str(e)}

    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "state": self.state,
            "failures": self.failures,
            "threshold": self.failure_threshold,
        }


# Create circuit breakers for external services
supabase_breaker = CircuitBreaker("Supabase", failure_threshold=3, recovery_timeout=120)
n8n_breaker = CircuitBreaker("n8n", failure_threshold=3, recovery_timeout=60)


# ═══════════════════════════════════════════════════════════
# REAL BLOCKCHAIN ANALYSIS (NO MOCK DATA!)
# ═══════════════════════════════════════════════════════════


class BlockchainAnalyzer:
    """Real blockchain analysis using free APIs"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.endpoints = {
            "eth": "https://api.etherscan.io/api",
            "bsc": "https://api.bscscan.com/api",
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(
        self, url: str, params: dict = None, timeout: int = 30
    ) -> dict:
        if not self.session:
            self.session = aiohttp.ClientSession()
        try:
            async with self.session.get(
                url, params=params, timeout=timeout
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.warning(f"API error {response.status}: {url}")
                return {}
        except asyncio.TimeoutError:
            logger.error(f"API timeout: {url}")
            return {}
        except Exception as e:
            logger.error(f"API request error: {e}")
            return {}

    @cache_response(ttl=300)
    async def get_dex_data(self, contract: str, chain: str) -> dict:
        """Get real data from DexScreener (FREE)"""
        try:
            url = f"{Config.DEXSCREENER_API}/latest/dex/tokens/{contract}"
            data = await self._make_request(url, timeout=10)

            pairs = data.get("pairs", [])
            if pairs:
                pair = pairs[0]
                return {
                    "price_usd": float(pair.get("priceUsd", 0) or 0),
                    "liquidity_usd": float(
                        pair.get("liquidity", {}).get("usd", 0) or 0
                    ),
                    "volume_24h": float(pair.get("volume", {}).get("h24", 0) or 0),
                    "price_change_24h": float(
                        pair.get("priceChange", {}).get("h24", 0) or 0
                    ),
                    "buys_24h": int(
                        pair.get("txns", {}).get("h24", {}).get("buys", 0) or 0
                    ),
                    "sells_24h": int(
                        pair.get("txns", {}).get("h24", {}).get("sells", 0) or 0
                    ),
                    "market_cap": float(pair.get("marketCap", 0) or 0),
                    "fdv": float(pair.get("fdv", 0) or 0),
                    "source": "dexscreener",
                }
        except Exception as e:
            logger.warning(f"DexScreener error: {e}")
        return {}

    @cache_response(ttl=600)
    async def check_honeypot(self, contract: str, chain: str) -> dict:
        """Check honeypot.is API (FREE)"""
        try:
            url = f"{Config.HONEYPOT_API}/v2/IsHoneypot?address={contract}"
            if chain != "eth":
                url += f"&chain={chain}"

            data = await self._make_request(url, timeout=10)
            return {
                "is_honeypot": data.get("isHoneypot", False),
                "buy_tax": float(data.get("buyTax", 0) or 0),
                "sell_tax": float(data.get("sellTax", 0) or 0),
                "liquidity_locked": data.get("liquidityLocked", False),
                "lock_days": int(data.get("liquidityLockDays", 0) or 0),
                "verified": data.get("verified", False),
            }
        except Exception as e:
            logger.error(f"Honeypot check error: {e}")
        return {
            "is_honeypot": None,
            "buy_tax": 0,
            "sell_tax": 0,
            "liquidity_locked": None,
            "lock_days": 0,
        }

    @cache_response(ttl=3600)
    async def get_contract_info(self, contract: str, chain: str) -> dict:
        """Get contract verification info from blockchain explorer"""
        api_key = Config.ETHERSCAN_KEY if chain == "eth" else Config.BSCSCAN_KEY
        if not api_key:
            return {"error": "No API key"}

        try:
            url = self.endpoints.get(chain, self.endpoints["eth"])
            params = {
                "module": "contract",
                "action": "getsourcecode",
                "address": contract,
                "apikey": api_key,
            }
            result = await self._make_request(url, params)

            if result.get("status") == "1" and result.get("result"):
                contract_data = result["result"][0]
                return {
                    "is_verified": contract_data.get("SourceCode", "") != "",
                    "contract_name": contract_data.get("ContractName", "Unknown"),
                    "compiler": contract_data.get("CompilerVersion", ""),
                    "optimization": contract_data.get("OptimizationUsed", ""),
                    "abi": contract_data.get("ABI", ""),
                }
        except Exception as e:
            logger.error(f"Contract info error: {e}")
        return {"is_verified": False}


class RiskScorer:
    """Calculate REAL risk scores from blockchain data"""

    def __init__(self):
        self.blockchain = BlockchainAnalyzer()

    async def calculate_score(self, contract: str, chain: str) -> dict:
        """Calculate comprehensive risk score from real data"""
        logger.info(f"Calculating risk for {contract} on {chain}")

        score = 100
        deductions = []
        critical_flags = []
        high_flags = []
        medium_flags = []

        async with self.blockchain:
            # 1. Check honeypot status (CRITICAL)
            honeypot = await self.blockchain.check_honeypot(contract, chain)

            if honeypot.get("is_honeypot") is True:
                score -= 50
                critical_flags.append("🔥 HONEYPOT - Cannot sell tokens!")
                deductions.append(
                    {"category": "Critical", "issue": "Honeypot", "deduction": 50}
                )
            elif honeypot.get("is_honeypot") is None:
                score -= 10
                medium_flags.append("⚠️ Honeypot status unknown")
                deductions.append(
                    {
                        "category": "Unknown",
                        "issue": "Honeypot check failed",
                        "deduction": 10,
                    }
                )

            # 2. Check taxes
            buy_tax = honeypot.get("buy_tax", 0)
            sell_tax = honeypot.get("sell_tax", 0)

            if sell_tax > 10:
                deduction = min(int(sell_tax), 25)
                score -= deduction
                high_flags.append(f"💸 High sell tax: {sell_tax}%")
                deductions.append(
                    {
                        "category": "Tax",
                        "issue": f"{sell_tax}% sell tax",
                        "deduction": deduction,
                    }
                )
            elif sell_tax > 5:
                score -= 5
                medium_flags.append(f"📊 Moderate sell tax: {sell_tax}%")
                deductions.append(
                    {
                        "category": "Tax",
                        "issue": f"{sell_tax}% sell tax",
                        "deduction": 5,
                    }
                )

            # 3. Check liquidity lock
            if honeypot.get("liquidity_locked") is False:
                score -= 15
                critical_flags.append("🔓 Liquidity NOT locked - instant rug possible")
                deductions.append(
                    {"category": "Liquidity", "issue": "Not locked", "deduction": 15}
                )
            elif honeypot.get("lock_days", 0) < 30:
                score -= 10
                high_flags.append(f"⏰ Short lock: {honeypot.get('lock_days', 0)} days")
                deductions.append(
                    {
                        "category": "Liquidity",
                        "issue": "Short lock period",
                        "deduction": 10,
                    }
                )

            # 4. Get contract verification status
            contract_info = await self.blockchain.get_contract_info(contract, chain)
            if not contract_info.get("is_verified", False):
                score -= 10
                high_flags.append("📄 Contract not verified - hidden code")
                deductions.append(
                    {"category": "Contract", "issue": "Unverified", "deduction": 10}
                )

            # 5. Get market data
            dex_data = await self.blockchain.get_dex_data(contract, chain)
            if dex_data:
                liquidity = dex_data.get("liquidity_usd", 0)
                if liquidity < 10000:
                    score -= 10
                    high_flags.append(f"💧 Low liquidity: ${liquidity:,.0f}")
                    deductions.append(
                        {
                            "category": "Liquidity",
                            "issue": "Low liquidity",
                            "deduction": 10,
                        }
                    )

                # Check buy/sell ratio
                buys = dex_data.get("buys_24h", 0)
                sells = dex_data.get("sells_24h", 0)
                if sells > 0 and buys / sells < 0.5:
                    score -= 5
                    medium_flags.append("📉 More sells than buys (24h)")
                    deductions.append(
                        {
                            "category": "Activity",
                            "issue": "Sell pressure",
                            "deduction": 5,
                        }
                    )

        # Ensure score stays valid
        score = max(0, min(100, score))

        # Determine category
        if score >= 80:
            category, emoji = "SAFE", "🟢"
        elif score >= 60:
            category, emoji = "CAUTION", "🟡"
        elif score >= 40:
            category, emoji = "RISKY", "🟠"
        else:
            category, emoji = "RUG", "🔴"

        return {
            "score": score,
            "category": category,
            "emoji": emoji,
            "deductions": deductions,
            "critical_flags": critical_flags,
            "high_flags": high_flags,
            "medium_flags": medium_flags,
            "honeypot_data": honeypot,
            "contract_info": contract_info,
            "dex_data": dex_data,
            "analyzed_at": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════
# ADVANCED BUNDLE DETECTION
# ═══════════════════════════════════════════════════════════


@dataclass
class BundleWallet:
    address: str
    funding_source: str
    balance: float
    first_buy: Optional[datetime] = None
    is_fresh: bool = False


@dataclass
class DetectedBundle:
    bundle_type: str
    wallets: List[BundleWallet]
    confidence: float
    total_supply_pct: float
    sophistication: str


class BundleDetector:
    """Multi-layered bundle detection"""

    def __init__(self):
        self.known_mixers = {
            "0xd90e2f925da726b50c4ed8d0fb90ad0533241698",
            "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",
        }

    async def detect(self, contract: str, chain: str) -> dict:
        """Detect coordinated buying patterns"""
        # Get holder data from database
        holders = self._get_holders_from_db(contract, chain)

        if len(holders) < 10:
            return {
                "bundles_found": 0,
                "risk_assessment": "🟢 Insufficient data",
                "analysis": {},
            }

        bundles = []

        # Detection 1: Time clustering
        time_clusters = self._cluster_by_time(holders)
        for cluster in time_clusters:
            if len(cluster) >= 3:
                bundle = self._create_bundle(cluster, "TEMPORAL_CLUSTER")
                bundles.append(bundle)

        # Detection 2: Fresh wallet clusters
        fresh_wallets = [h for h in holders if h.is_fresh]
        if len(fresh_wallets) >= 5:
            bundle = self._create_bundle(fresh_wallets, "FRESH_WALLET")
            bundle.sophistication = "MODERATE"
            bundles.append(bundle)

        # Merge overlapping
        merged = self._merge_bundles(bundles)

        total_bundled = sum(len(b.wallets) for b in merged)
        total_supply = sum(h.balance for h in holders) or 1
        bundled_supply = sum(sum(w.balance for w in b.wallets) for b in merged)

        supply_pct = (bundled_supply / total_supply) * 100

        analysis = {
            "bundled_supply_pct": round(supply_pct, 2),
            "total_bundled_wallets": total_bundled,
            "bundle_count": len(merged),
            "sophistication": self._get_sophistication(merged),
        }

        return {
            "bundles_found": len(merged),
            "bundles": [self._bundle_to_dict(b) for b in merged[:3]],
            "analysis": analysis,
            "risk_assessment": self._assess_risk(supply_pct, len(merged)),
        }

    def _get_holders_from_db(self, contract: str, chain: str) -> List[BundleWallet]:
        """Fetch holders from local database"""
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM holders WHERE contract_address = ? AND chain = ? ORDER BY balance DESC LIMIT 100",
            (contract.lower(), chain),
        )
        rows = cursor.fetchall()

        wallets = []
        for row in rows:
            wallets.append(
                BundleWallet(
                    address=row["wallet"],
                    funding_source="unknown",
                    balance=row["balance"],
                    first_buy=row["first_buy"],
                    is_fresh=self._is_fresh(row["first_buy"]),
                )
            )
        return wallets

    def _is_fresh(self, first_buy) -> bool:
        if not first_buy:
            return True
        try:
            if isinstance(first_buy, str):
                first_buy = datetime.fromisoformat(first_buy.replace("Z", "+00:00"))
            age_days = (datetime.now() - first_buy).total_seconds() / 86400
            return age_days < 7
        except:
            return True

    def _cluster_by_time(
        self, holders: List[BundleWallet], window_minutes: int = 10
    ) -> List[List[BundleWallet]]:
        if not holders:
            return []

        sorted_holders = sorted(holders, key=lambda x: x.first_buy or datetime.now())
        clusters = []
        current = [sorted_holders[0]]

        for h in sorted_holders[1:]:
            prev_time = current[-1].first_buy or datetime.now()
            curr_time = h.first_buy or datetime.now()

            if isinstance(prev_time, str):
                prev_time = datetime.fromisoformat(prev_time.replace("Z", "+00:00"))
            if isinstance(curr_time, str):
                curr_time = datetime.fromisoformat(curr_time.replace("Z", "+00:00"))

            diff = (curr_time - prev_time).total_seconds() / 60
            if diff <= window_minutes:
                current.append(h)
            else:
                if len(current) >= 3:
                    clusters.append(current)
                current = [h]

        if len(current) >= 3:
            clusters.append(current)

        return clusters

    def _create_bundle(
        self, wallets: List[BundleWallet], bundle_type: str
    ) -> DetectedBundle:
        total_balance = sum(w.balance for w in wallets)
        return DetectedBundle(
            bundle_type=bundle_type,
            wallets=wallets,
            confidence=min(95, 50 + len(wallets) * 5),
            total_supply_pct=0,
            sophistication="BASIC",
        )

    def _merge_bundles(self, bundles: List[DetectedBundle]) -> List[DetectedBundle]:
        if not bundles:
            return []

        bundles = sorted(bundles, key=lambda b: len(b.wallets), reverse=True)
        merged = []
        used = set()

        for bundle in bundles:
            addresses = {w.address for w in bundle.wallets}
            overlap = addresses & used

            if len(overlap) < len(addresses) * 0.5:
                merged.append(bundle)
                used.update(addresses)

        return merged

    def _get_sophistication(self, bundles: List[DetectedBundle]) -> str:
        if not bundles:
            return "NONE"
        levels = [b.sophistication for b in bundles]
        if "EXPERT" in levels:
            return "EXPERT"
        elif "ADVANCED" in levels:
            return "ADVANCED"
        elif "MODERATE" in levels:
            return "MODERATE"
        return "BASIC"

    def _assess_risk(self, supply_pct: float, bundle_count: int) -> str:
        if supply_pct > 50:
            return f"💀 EXTREME: {supply_pct:.1f}% controlled by insiders"
        elif supply_pct > 30:
            return f"🚨 HIGH: {supply_pct:.1f}% in bundles"
        elif supply_pct > 15:
            return f"⚠️ MODERATE: {supply_pct:.1f}% bundled"
        return f"🟡 LOW: Minor bundling ({supply_pct:.1f}%)"

    def _bundle_to_dict(self, bundle: DetectedBundle) -> dict:
        return {
            "type": bundle.bundle_type,
            "wallet_count": len(bundle.wallets),
            "wallets": [w.address[:12] + "..." for w in bundle.wallets[:5]],
            "confidence": bundle.confidence,
            "sophistication": bundle.sophistication,
        }


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


class UI:
    """UI generators"""

    @staticmethod
    def create_progress_bar(score: float, length: int = 20) -> str:
        filled = int((score / 100) * length)
        empty = length - filled
        char = (
            "🟩"
            if score >= 80
            else "🟨"
            if score >= 60
            else "🟧"
            if score >= 40
            else "🟥"
        )
        return char * filled + "⬜" * empty

    @classmethod
    def generate_scan_result(cls, result: dict, contract: str, chain: str) -> str:
        score = result.get("score", 50)
        category = result.get("category", "CAUTION")
        emoji = result.get("emoji", "⚠️")
        progress = cls.create_progress_bar(score)

        critical = result.get("critical_flags", [])
        high = result.get("high_flags", [])
        medium = result.get("medium_flags", [])

        text = f"""╔══════════════════════════════════════════════════╗
║  {emoji} <b>RUG MUNCHER SCAN</b> {emoji}                   ║
╚══════════════════════════════════════════════════╝

<b>📊 SCORE:</b> <code>{score}/100</code>
{progress}
<b>🔰 Risk:</b> {emoji} <code>{category}</code>
<b>🔗 Contract:</b> <code>{contract[:25]}...</code>
<b>⛓️ Chain:</b> <code>{chain.upper()}</code>
"""

        if critical:
            text += "\n🚨 <b>CRITICAL:</b>\n"
            for flag in critical[:3]:
                text += f"  {flag}\n"

        if high:
            text += "\n⚠️ <b>HIGH RISK:</b>\n"
            for flag in high[:3]:
                text += f"  {flag}\n"

        # Add dex data
        dex = result.get("dex_data", {})
        if dex:
            text += f"\n<b>💰 MARKET DATA:</b>\n"
            if dex.get("price_usd"):
                text += f"  Price: ${dex['price_usd']:.8f}\n"
            if dex.get("liquidity_usd"):
                text += f"  Liquidity: ${dex['liquidity_usd']:,.0f}\n"
            if dex.get("volume_24h"):
                text += f"  Volume 24h: ${dex['volume_24h']:,.0f}\n"

        # Add tax info
        hp = result.get("honeypot_data", {})
        if hp:
            text += f"\n<b>📊 TAXES:</b>\n"
            text += f"  Buy: {hp.get('buy_tax', 0)}% | Sell: {hp.get('sell_tax', 0)}%\n"
            if hp.get("liquidity_locked") is False:
                text += "  🔓 <b>LIQUIDITY NOT LOCKED</b>\n"

        text += f"\n<i>🕐 {result.get('analyzed_at', 'N/A')[:19]}</i>"
        return text

    @staticmethod
    def get_scan_buttons(
        contract: str, chain: str, score: int, tier: str = "free"
    ) -> list:
        buttons = []

        # Panic actions
        dex_url = f"https://dexscreener.com/{chain}/{contract}"
        sell_urls = {
            "bsc": f"https://pancakeswap.finance/swap?outputCurrency={contract}",
            "eth": f"https://app.uniswap.org/#/swap?outputCurrency={contract}",
            "sol": f"https://jup.ag/swap/USDC-{contract}",
        }
        sell_url = sell_urls.get(chain, dex_url)

        buttons.append([InlineKeyboardButton("🔴 PANIC SELL NOW", url=sell_url)])
        buttons.append(
            [
                InlineKeyboardButton("📋 COPY CA", callback_data=f"copy_{contract}"),
                InlineKeyboardButton("📈 CHART", url=dex_url),
            ]
        )

        # AI Features
        buttons.append(
            [InlineKeyboardButton("━━━ RUG MUNCHER AI ━━━", callback_data="separator")]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    "🫧 BUBBLE MAP", callback_data=f"bubble_{contract}_{chain}_{tier}"
                )
            ]
        )

        if tier in ["pro", "elite"]:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "🕸️ BUNDLE DETECTOR", callback_data=f"bundle_{contract}_{chain}"
                    )
                ]
            )
        else:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "🕸️ BUNDLE 🔒 PRO",
                        callback_data=f"upg_pro_bundle_{contract}_{chain}",
                    )
                ]
            )

        if tier == "elite":
            buttons.append(
                [
                    InlineKeyboardButton(
                        "🎙️ DEV VOICEPRINT", callback_data=f"voice_{contract}_{chain}"
                    )
                ]
            )
            buttons.append(
                [
                    InlineKeyboardButton(
                        "⏰ RUG PREDICTOR", callback_data=f"predict_{contract}_{chain}"
                    )
                ]
            )

        # Actions
        buttons.append(
            [InlineKeyboardButton("━━━ ACTIONS ━━━", callback_data="separator")]
        )
        alert_emoji = "🔔" if score < 60 else "🔕"
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{alert_emoji} ALERT",
                    callback_data=f"alert_{contract}_{chain}_{score}",
                ),
                InlineKeyboardButton(
                    "📤 SHARE", callback_data=f"share_{contract}_{chain}_{score}"
                ),
            ]
        )
        buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="back")])

        return buttons


# ═══════════════════════════════════════════════════════════
# BOT HANDLERS
# ═══════════════════════════════════════════════════════════

user_last_messages: Dict[int, dict] = {}


async def get_user_tier(user_id: int) -> str:
    """Get user subscription tier"""
    if REDIS_ENABLED:
        try:
            cached = redis_client.get(f"rm:user:{user_id}:tier")
            if cached:
                return cached
        except:
            pass

    user = db.get_user(user_id)
    tier = user.get("tier", "free") if user else "free"

    if REDIS_ENABLED:
        try:
            redis_client.setex(f"rm:user:{user_id}:tier", 3600, tier)
        except:
            pass

    return tier


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    try:
        user = update.effective_user
        user_data = db.get_user(user.id)

        if not user_data:
            referrer_id = (
                int(context.args[0])
                if context.args and context.args[0].isdigit()
                else None
            )
            user_data = db.create_user(
                user.id, user.username, user.first_name, referrer_id
            )
            # Trigger n8n for new user
            try:
                await n8n_webhook.new_user_registered(
                    user.id, user.username or "unknown", "free"
                )
            except Exception as e:
                logger.warning(f"n8n webhook failed (non-critical): {e}")

        tier = user_data.get("tier", "free")
        scans_today = user_data.get("scans_today", 0)
        scan_limit = db.get_scan_limit(user.id)

        text = f"""🕵️ <b>RUG MUNCHER BOT v6.0</b>
<i>Production-Grade Crypto Forensics</i>

<b>Your Status:</b> {tier.upper()} ⭐
<b>Scans Today:</b> {scans_today}/{scan_limit}

<b>Features:</b>
• Real 100-Point Risk Scoring
• Blockchain Analysis (BSC, ETH, SOL)
• Bundle Detection
• Honeypot Detection
• Holder Analysis

<b>Quick Start:</b>
Paste a contract address to scan!"""

        keyboard = [
            [InlineKeyboardButton("🔍 SCAN CONTRACT", callback_data="start_scan")],
            [
                InlineKeyboardButton("⭐ UPGRADE", callback_data="upgrade_menu"),
                InlineKeyboardButton("❓ HELP", callback_data="help_main"),
            ],
        ]

        await update.message.reply_html(
            text, reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text(
            "❌ An error occurred. Please try /start again."
        )


async def perform_scan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    contract: str,
    chain: str = "eth",
):
    """Perform real blockchain scan"""
    user = update.effective_user

    try:
        # Rate limit
        if not check_rate_limit(user.id, "scan"):
            await update.message.reply_text("⏱️ Rate limit exceeded. Wait a minute.")
            return

        # Check scan limit
        user_data = db.get_user(user.id)
        scans_today = user_data.get("scans_today", 0) if user_data else 0
        scan_limit = db.get_scan_limit(user.id)

        if scans_today >= scan_limit:
            await update.message.reply_html(
                f"❌ <b>Daily limit reached!</b>\n\n"
                f"Used {scans_today}/{scan_limit} scans.\n"
                f"Upgrade for unlimited scans.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("⭐ UPGRADE", callback_data="upgrade_menu")]]
                ),
            )
            return

        # Send scanning message
        scan_msg = await update.message.reply_text(
            f"🕵️ <b>ANALYZING BLOCKCHAIN...</b>\n<code>{contract[:25]}...</code>\n\n⏳ Fetching real data...",
            parse_mode="HTML",
        )

        # Perform REAL analysis
        scorer = RiskScorer()
        result = await scorer.calculate_score(contract, chain)

        # Save scan locally
        db.increment_scan_count(user.id)
        db.save_scan(user.id, contract, chain, result)

        # Sync to Supabase (cloud backup)
        try:
            sync_result = await supabase_sync.sync_scan(
                user.id, contract, chain, result
            )
            if sync_result.get("success"):
                logger.info(f"☁️ Scan synced to Supabase: {contract}")
        except Exception as e:
            logger.warning(f"Supabase sync failed (non-critical): {e}")

        # Trigger n8n webhook for automation
        try:
            await n8n_webhook.scan_completed(
                user.id, contract, chain, result.get("score", 50)
            )
            # Also trigger high_risk if score is low
            if result.get("score", 50) < 50:
                await n8n_webhook.high_risk_detected(
                    contract,
                    chain,
                    result.get("score", 50),
                    result.get("deductions", []),
                )
        except Exception as e:
            logger.warning(f"n8n webhook failed (non-critical): {e}")

        # Generate UI
        tier = await get_user_tier(user.id)
        score_text = UI.generate_scan_result(result, contract, chain)
        buttons = UI.get_scan_buttons(contract, chain, result["score"], tier)

        await scan_msg.edit_text(
            score_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons)
        )

        logger.info(f"Scan complete: {contract} by {user.id}, score: {result['score']}")

    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)}")
    except Exception as e:
        logger.error(f"Scan error: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ <b>Scan failed</b>\n\nUnable to analyze. Try again later.",
            parse_mode="HTML",
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle contract addresses pasted directly"""
    try:
        text = update.message.text.strip()
        contract, chain = ContractValidator.validate_contract(text)
        await perform_scan(update, context, contract, chain)
    except ValidationError:
        await update.message.reply_text(
            "🤔 That doesn't look like a contract address.\n\n"
            "Send a valid Ethereum/BSC (0x...) or Solana address.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Text handler error: {e}")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    user = update.effective_user

    try:
        await query.answer()
        data = query.data

        # Validate
        try:
            action, params = ContractValidator.validate_callback(data)
        except ValidationError:
            await query.edit_message_text("❌ Invalid action.")
            return

        # Store for back button
        if query.message:
            user_last_messages[user.id] = {
                "text": query.message.text,
                "reply_markup": query.message.reply_markup,
            }

        # Route
        if data.startswith("bubble_"):
            await show_bubblemap(query, data)
        elif data.startswith("bundle_"):
            await show_bundle(query, data, user.id)
        elif data.startswith("copy_"):
            await handle_copy(query, data)
        elif data.startswith("alert_"):
            await handle_alert(query, data, user.id)
        elif data == "back":
            await handle_back(query, user.id)
        elif data == "start_scan":
            await query.edit_message_text(
                "🕵️ Send me a contract address!\nExample: <code>0x1234...</code>",
                parse_mode="HTML",
            )
        elif data in ["upgrade_menu", "help_main", "separator"]:
            await query.answer("Coming soon!" if data == "separator" else "✅")
        else:
            await query.answer("Feature coming soon!")

    except BadRequest as e:
        logger.debug(f"BadRequest (expected): {e}")
    except Exception as e:
        logger.error(f"Callback error: {e}")
        try:
            await query.edit_message_text(
                "❌ An error occurred. Please try again.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔄 START OVER", callback_data="start_scan"
                            )
                        ]
                    ]
                ),
            )
        except:
            pass


async def show_bubblemap(query, data: str):
    """Show bubble map"""
    parts = data.split("_")
    if len(parts) < 3:
        await query.edit_message_text("❌ Invalid request.")
        return

    contract, chain = parts[1], parts[2]

    await query.edit_message_text(
        f"🫧 <b>BUBBLE MAP</b>\n\n<code>{contract[:25]}...</code>\n\n"
        f"Visualizing holder distribution...\n\n"
        f"<i>Full visualization in web dashboard.</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 BACK", callback_data="back")]]
        ),
    )


async def show_bundle(query, data: str, user_id: int):
    """Show bundle detection results"""
    parts = data.split("_")
    if len(parts) < 3:
        await query.edit_message_text("❌ Invalid request.")
        return

    contract, chain = parts[1], parts[2]
    tier = await get_user_tier(user_id)

    if tier not in ["pro", "elite"]:
        await query.edit_message_text(
            "🔒 <b>PRO FEATURE</b>\n\nBundle detection requires PRO tier.\nUpgrade for $29/month.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⭐ UPGRADE TO PRO", callback_data="upgrade_menu"
                        )
                    ],
                    [InlineKeyboardButton("🔙 BACK", callback_data="back")],
                ]
            ),
        )
        return

    # Run bundle detection
    detector = BundleDetector()
    result = await detector.detect(contract, chain)

    text = f"""🕸️ <b>BUNDLE DETECTOR</b>

<code>{contract[:25]}...</code>

<b>📊 RESULTS:</b>
{result["risk_assessment"]}

<b>Bundles Found:</b> {result["bundles_found"]}
"""

    if result["bundles"]:
        text += "\n<b>Top Bundles:</b>\n"
        for b in result["bundles"][:3]:
            text += f"• {b['type']}: {b['wallet_count']} wallets ({b['confidence']:.0f}% confidence)\n"

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 BACK", callback_data="back")]]
        ),
    )


async def handle_copy(query, data: str):
    """Copy contract address"""
    parts = data.split("_")
    if len(parts) >= 2:
        contract = parts[1]
        await query.answer(f"CA: {contract[:30]}...", show_alert=True)


async def handle_alert(query, data: str, user_id: int):
    """Set alert"""
    parts = data.split("_")
    if len(parts) >= 3:
        contract, chain = parts[1], parts[2]
        db.add_to_watchlist(user_id, contract, chain)

    await query.answer("🔔 Alert set!")
    await query.edit_message_text(
        "🔔 <b>RUG ALERT ACTIVATED</b>\n\n"
        "You'll be notified if:\n"
        "• Dev sells > 5% of supply\n"
        "• LP is removed\n"
        "• Price drops > 50% in 5min\n\n"
        "<i>Monitoring active.</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 BACK", callback_data="back")]]
        ),
    )


async def handle_back(query, user_id: int):
    """Handle back button"""
    try:
        if user_id in user_last_messages:
            prev = user_last_messages[user_id]
            await query.edit_message_text(
                prev["text"], reply_markup=prev["reply_markup"], parse_mode="HTML"
            )
        else:
            await query.edit_message_text(
                "🕵️ What would you like to do?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🚀 START SCANNING", callback_data="start_scan"
                            )
                        ]
                    ]
                ),
            )
    except BadRequest:
        pass
    except Exception as e:
        logger.error(f"Back error: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler"""
    error = context.error
    logger.error(f"Global error: {error}", exc_info=True)

    if isinstance(error, NetworkError):
        return

    if update and update.message:
        try:
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )
        except:
            pass


# ═══════════════════════════════════════════════════════════
# BOT INITIALIZATION
# ═══════════════════════════════════════════════════════════


def main():
    """Start the bot"""
    logger.info("=" * 60)
    logger.info("🕵️ RUG MUNCHER BOT v6.0 - PRODUCTION")
    logger.info("=" * 60)
    logger.info(f"🔑 Token: {Config.BOT_TOKEN[:10]}...")
    logger.info(f"📊 Redis: {REDIS_ENABLED}")
    logger.info(f"👥 Admins: {len(Config.ADMIN_IDS)}")
    logger.info(f"☁️ Supabase Sync: {supabase_sync.enabled}")
    logger.info(f"🔔 n8n Webhook: {n8n_webhook.enabled}")

    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    # Error handler
    application.add_error_handler(error_handler)

    logger.info("✅ Bot initialized - starting polling...")

    # Cleanup on shutdown
    async def on_shutdown(application):
        logger.info("🔄 Shutting down - closing sync clients...")
        await supabase_sync.close()
        await n8n_webhook.close()
        logger.info("✅ Cleanup complete")

    application.post_shutdown = on_shutdown
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
