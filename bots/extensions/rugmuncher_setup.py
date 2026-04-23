#!/usr/bin/env python3
"""
🚀 RUG MUNCHER BOT SETUP v6.0
============================
Production bot initialization

Usage:
    python rugmuncher_setup.py

This will:
1. Check Python version
2. Install dependencies
3. Check environment variables
4. Initialize the database
5. Test Redis connection (if configured)
6. Validate API keys
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_header(text: str):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def print_status(message: str, status: str = "info"):
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "pending": "⏳",
    }
    icon = icons.get(status, "ℹ️")
    print(f"{icon} {message}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print_status(f"Python {version.major}.{version.minor}.{version.micro}", "info")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_status("Python 3.9+ required!", "error")
        return False
    return True

def install_dependencies():
    """Install required packages"""
    print_status("Installing dependencies...", "pending")

    req_file = Path("/root/rugmuncher_requirements.txt")
    if not req_file.exists():
        print_status("rugmuncher_requirements.txt not found!", "error")
        return False

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)],
            check=True,
            capture_output=True,
        )
        print_status("Dependencies installed", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install dependencies: {e}", "error")
        return False

def check_env_vars():
    """Check environment variables"""
    print_header("ENVIRONMENT CHECK")

    required = ["RUGMUNCHER_BOT_TOKEN"]
    optional = ["BSCSCAN_KEY", "ETHERSCAN_KEY", "HELIUS_KEY", "REDIS_HOST", "ADMIN_TELEGRAM_IDS"]

    all_ok = True

    for var in required:
        value = os.getenv(var)
        if value and value != "your_token_here":
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print_status(f"{var}: {masked}", "success")
        else:
            print_status(f"{var}: NOT SET!", "error")
            all_ok = False

    print()
    for var in optional:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print_status(f"{var}: {masked} (optional)", "success")
        else:
            print_status(f"{var}: not set (optional)", "warning")

    return all_ok

def init_database():
    """Initialize SQLite database"""
    print_header("DATABASE INITIALIZATION")

    db_path = "/root/rugmuncher_production.db"

    try:
        conn = sqlite3.connect(db_path)
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

        # Holders
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

        # Dev fingerprints
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

        print_status(f"Database initialized: {db_path}", "success")
        return True

    except Exception as e:
        print_status(f"Database error: {e}", "error")
        return False

def check_redis():
    """Check Redis connection"""
    print_header("REDIS CHECK")

    redis_host = os.getenv("REDIS_HOST")
    if not redis_host:
        print_status("REDIS_HOST not set - caching disabled", "warning")
        print("   Bot will work but without caching. Set REDIS_HOST for better performance.")
        return True

    try:
        import redis
        client = redis.Redis(
            host=redis_host,
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD") or None,
            socket_connect_timeout=5,
        )
        client.ping()
        print_status("Redis connected successfully", "success")
        return True
    except ImportError:
        print_status("Redis package not installed", "warning")
        print("   Run: pip install redis")
        return True
    except Exception as e:
        print_status(f"Redis connection failed: {e}", "warning")
        print("   Bot will work without caching.")
        return True

def check_api_keys():
    """Test API keys"""
    print_header("API KEY VALIDATION")

    import aiohttp
    import asyncio

    async def test_etherscan():
        key = os.getenv("ETHERSCAN_KEY")
        if not key:
            print_status("ETHERSCAN_KEY: not set (optional)", "warning")
            return True

        try:
            url = f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    data = await resp.json()
                    if data.get("status") == "1":
                        print_status("ETHERSCAN_KEY: valid", "success")
                        return True
                    else:
                        print_status("ETHERSCAN_KEY: invalid", "error")
                        return False
        except Exception as e:
            print_status(f"ETHERSCAN_KEY: test failed ({e})", "warning")
            return True

    async def test_bscscan():
        key = os.getenv("BSCSCAN_KEY")
        if not key:
            print_status("BSCSCAN_KEY: not set (optional)", "warning")
            return True

        try:
            url = f"https://api.bscscan.com/api?module=stats&action=bnbprice&apikey={key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    data = await resp.json()
                    if data.get("status") == "1":
                        print_status("BSCSCAN_KEY: valid", "success")
                        return True
                    else:
                        print_status("BSCSCAN_KEY: invalid", "error")
                        return False
        except Exception as e:
            print_status(f"BSCSCAN_KEY: test failed ({e})", "warning")
            return True

    async def run_tests():
        results = await asyncio.gather(test_etherscan(), test_bscscan())
        return all(results)

    return asyncio.run(run_tests())

def create_env_template():
    """Create .env template if not exists"""
    env_path = Path("/root/.env.rugmuncher")

    if env_path.exists():
        print_status("Environment file exists", "info")
        return

    template = """# Rug Muncher Bot v6.0 Configuration
# ====================================

# REQUIRED: Get from @BotFather
RUGMUNCHER_BOT_TOKEN=your_bot_token_here

# OPTIONAL: Blockchain API Keys (for more detailed analysis)
BSCSCAN_KEY=your_bscscan_key
ETHERSCAN_KEY=your_etherscan_key
HELIUS_KEY=your_helius_key

# OPTIONAL: Redis for caching
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Admin Telegram IDs (comma-separated)
ADMIN_TELEGRAM_IDS=123456789
"""

    with open(env_path, "w") as f:
        f.write(template)

    print_status(f"Created template: {env_path}", "info")
    print("   Edit this file and add your bot token!")

def print_final_instructions():
    """Print final setup instructions"""
    print_header("SETUP COMPLETE")

    print("""
🎉 Your Rug Muncher Bot v6.0 is ready!

NEXT STEPS:
-----------

1. SET ENVIRONMENT VARIABLES:
   export RUGMUNCHER_BOT_TOKEN="your_token_from_botfather"

   Or edit and source the .env file:
   source /root/.env.rugmuncher

2. OPTIONAL - ADD API KEYS (for better analysis):
   export BSCSCAN_KEY="your_key"
   export ETHERSCAN_KEY="your_key"

3. OPTIONAL - SETUP REDIS (for caching):
   export REDIS_HOST="localhost"

4. RUN THE BOT:
   python /root/rugmuncher_bot_production.py

COMMANDS:
---------
- /start - Begin interaction
- Paste contract address to scan

TROUBLESHOOTING:
----------------
• Check logs: tail -f /root/rugmuncher_production.log
• Database: /root/rugmuncher_production.db
• Config issues: Review the error messages above

FEATURES:
---------
✅ Real blockchain analysis (no mock data!)
✅ 100-point risk scoring
✅ Honeypot detection
✅ Bundle detection (Pro tier)
✅ Bubble maps
✅ Redis caching
✅ Rate limiting
✅ Subscription tiers

SUPPORT:
--------
For issues, check:
1. Environment variables are set
2. Database is writable
3. Bot token is valid (test with @BotFather)
""")

def main():
    print_header("RUG MUNCHER BOT v6.0 SETUP")
    print("This will prepare your bot for production\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print_status("Continuing anyway...", "warning")

    # Create env template
    create_env_template()

    # Check environment
    env_ok = check_env_vars()

    # Initialize database
    db_ok = init_database()

    # Check Redis
    redis_ok = check_redis()

    # Check API keys
    api_ok = check_api_keys()

    # Print instructions
    print_final_instructions()

    if not env_ok:
        print_status("CRITICAL: Set RUGMUNCHER_BOT_TOKEN before running!", "error")
        sys.exit(1)

    print_status("Setup complete! Follow the instructions above.", "success")

if __name__ == "__main__":
    main()
