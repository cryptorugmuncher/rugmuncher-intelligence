#!/usr/bin/env python3
"""
📡 RugMuncher Telegram-Ollama Bridge
Scheduled & on-demand analysis with Telegram integration

Features:
- Scheduled scans (cron-like) for high-risk contracts
- On-demand analysis via Telegram commands
- Admin-only commands for security
- Systemd service for persistence
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Telegram
from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    filters
)

# Database (ScyllaDB/Cassandra)
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Scheduling
import schedule
import threading
import time

# Load from Vault/env
from rugmuncher_vault_client import vault_client
from rugmuncher_ai_router import ai_router
from rugmuncher_alert_router import AlertRouter, ScanResult, send_risk_alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Telegram Channels
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PRIVATE_CHANNEL_ID = os.getenv('PRIVATE_CHANNEL_ID', '-1001111111111')  # Admin bunker
PUBLIC_CHANNEL_ID = os.getenv('PUBLIC_CHANNEL_ID', '-1002222222222')    # Community alerts
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]

# Ollama
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434/api/generate')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemma2:9b')

# ScyllaDB
SCYLLA_HOSTS = os.getenv('SCYLLA_HOSTS', '127.0.0.1').split(',')
SCYLLA_KEYSPACE = os.getenv('SCYLLA_KEYSPACE', 'rugmuncher')

# Scheduling
SCHEDULE_INTERVAL = int(os.getenv('SCHEDULE_INTERVAL', '5'))  # minutes


class ScyllaDBClient:
    """ScyllaDB connection for fetching risky contracts"""
    
    def __init__(self):
        self.cluster = None
        self.session = None
        self.connected = False
        
    def connect(self):
        """Connect to ScyllaDB cluster"""
        try:
            self.cluster = Cluster(SCYLLA_HOSTS)
            self.session = self.cluster.connect(SCYLLA_KEYSPACE)
            self.connected = True
            logger.info(f"Connected to ScyllaDB: {SCYLLA_HOSTS}")
        except Exception as e:
            logger.error(f"ScyllaDB connection failed: {e}")
            self.connected = False
    
    def get_risky_contracts(self, min_risk_score: int = 70, limit: int = 10) -> List[Dict]:
        """Fetch high-risk contracts from database"""
        if not self.connected:
            self.connect()
        
        if not self.connected:
            return []
        
        try:
            query = """
                SELECT contract_address, chain, risk_score, threat_level, 
                       findings, scanned_at, token_name, token_symbol
                FROM contract_scans 
                WHERE risk_score >= %s 
                AND scanned_at > %s
                ALLOW FILTERING
            """
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(hours=24)
            
            rows = self.session.execute(query, (min_risk_score, cutoff))
            
            results = []
            for row in rows[:limit]:
                results.append({
                    'contract_address': row.contract_address,
                    'chain': row.chain,
                    'risk_score': row.risk_score,
                    'threat_level': row.threat_level,
                    'findings': json.loads(row.findings) if row.findings else [],
                    'token_name': row.token_name,
                    'token_symbol': row.token_symbol
                })
            
            return results
        except Exception as e:
            logger.error(f"Error fetching risky contracts: {e}")
            return []


class TelegramBridge:
    """
    📡 Bridge between Ollama AI and Telegram
    
    Two modes:
    1. Scheduled: Auto-analyze high-risk contracts every N minutes
    2. On-demand: Admin commands for instant analysis
    """
    
    def __init__(self):
        self.db = ScyllaDBClient()
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
        self.running = False
        
    async def init_bot(self):
        """Initialize Telegram bot"""
        if not BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.bot = self.application.bot
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("analyze", self.cmd_analyze))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("scanlatest", self.cmd_scan_latest))
        
        logger.info("Telegram bot initialized")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in ADMIN_IDS
    
    # ═══════════════════════════════════════════════════════════
    # TELEGRAM COMMANDS
    # ═══════════════════════════════════════════════════════════
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        await update.message.reply_text(
            "🤖 RugMuncher Telegram Bridge\n\n"
            "Commands:\n"
            "/analyze <contract> - Analyze contract (admin only)\n"
            "/scanlatest - Scan latest high-risk contracts\n"
            "/status - Check system status"
        )
    
    async def cmd_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔍 On-demand contract analysis
        Admin only to prevent spam
        """
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Admin only.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /analyze <contract_address>")
            return
        
        contract = context.args[0]
        
        # Validate address format
        if not (contract.startswith('0x') and len(contract) == 42):
            await update.message.reply_text("❌ Invalid contract address format")
            return
        
        # Send "analyzing" message
        msg = await update.message.reply_text(f"🔍 Analyzing {contract[:10]}...")
        
        try:
            # Use AI router for analysis
            result = await ai_router.analyze_contract(
                contract_code="",  # Would fetch from blockchain
                contract_address=contract,
                is_live=True
            )
            
            # Format response
            risk_score = result.get('risk_score', 50)
            severity = result.get('severity', 'unknown')
            summary = result.get('summary', 'Analysis complete')
            
            emoji = "🚨" if risk_score >= 80 else "⚠️" if risk_score >= 60 else "✅"
            
            response = f"""
{emoji} <b>Contract Analysis</b>

<b>Address:</b> <code>{contract}</code>
<b>Risk Score:</b> <code>{risk_score}/100</b>
<b>Severity:</b> {severity.upper()}

<b>Summary:</b>
{summary}

<i>Analysis via {result.get('routing', {}).get('provider', 'unknown')}</i>
"""
            
            # Split if too long (Telegram limit 4096)
            if len(response) > 4000:
                response = response[:4000] + "\n\n<i>...truncated</i>"
            
            await msg.edit_text(response, parse_mode='HTML', disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            await msg.edit_text(f"❌ Analysis failed: {str(e)}")
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check system status"""
        if not self.is_admin(update.effective_user.id):
            return
        
        status = await ai_router.get_status()
        
        response = f"""
📊 <b>System Status</b>

<b>Ollama:</b> {'✅' if status['ollama']['available'] else '❌'}
<b>Vault:</b> {'✅' if status['vault']['enabled'] else '❌'}
<b>Tor:</b> {'✅' if status['tor']['enabled'] else '❌'}

<b>Routing:</b>
• Sensitive → {status['routing']['sensitive']}
• Public → {status['routing']['public']}

<i>Bridge running</i>
"""
        await update.message.reply_text(response, parse_mode='HTML')
    
    async def cmd_scan_latest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manually trigger scan of latest risky contracts"""
        if not self.is_admin(update.effective_user.id):
            return
        
        await update.message.reply_text("🔍 Scanning for risky contracts...")
        await self.scheduled_scan()
    
    # ═══════════════════════════════════════════════════════════
    # SCHEDULED ANALYSIS
    # ═══════════════════════════════════════════════════════════
    
    async def scheduled_scan(self):
        """
        ⏰ Scheduled scan for high-risk contracts
        Dual-channel: Private (full) + Public (sanitized)
        """
        logger.info(f"Running scheduled scan at {datetime.now()}")
        
        try:
            # Fetch risky contracts from DB
            risky = self.db.get_risky_contracts(min_risk_score=70, limit=5)
            
            if not risky:
                logger.info("No high-risk contracts found")
                return
            
            logger.info(f"Found {len(risky)} high-risk contracts")
            
            # Process each high-risk contract
            alert_router = AlertRouter(self.bot)
            
            for contract_data in risky:
                risk_score = contract_data.get('risk_score', 0)
                
                # Only alert on high/critical risk
                if risk_score >= 80:
                    # Create scan result
                    scan = ScanResult(
                        contract_address=contract_data.get('contract_address', ''),
                        chain=contract_data.get('chain', 'eth'),
                        risk_score=risk_score,
                        threat_level=contract_data.get('threat_level', 'unknown'),
                        findings=contract_data.get('findings', []),
                        holder_data=contract_data.get('holder_data'),
                        wallet_data=contract_data.get('wallet_data')
                    )
                    
                    # Send dual-channel alert
                    result = await alert_router.send_alert(scan)
                    
                    if result['private_sent']:
                        logger.info(f"Private alert sent for {scan.contract_address[:16]}")
                    if result['public_sent']:
                        logger.info(f"Public alert sent for {scan.contract_address[:16]}")
                
                elif risk_score >= 60:
                    # Medium-high: Private channel only
                    scan = ScanResult(
                        contract_address=contract_data.get('contract_address', ''),
                        chain=contract_data.get('chain', 'eth'),
                        risk_score=risk_score,
                        threat_level=contract_data.get('threat_level', 'high'),
                        findings=contract_data.get('findings', [])
                    )
                    
                    # Send only to private channel
                    private_msg = alert_router.format_private_alert(scan)
                    try:
                        await self.bot.send_message(
                            chat_id=PRIVATE_CHANNEL_ID,
                            text=private_msg,
                            parse_mode='HTML',
                            disable_web_page_preview=True
                        )
                        logger.info(f"Private alert sent (risk {risk_score}): {scan.contract_address[:16]}")
                    except Exception as e:
                        logger.error(f"Failed to send private alert: {e}")
                
                else:
                    # Log only
                    logger.info(f"Logged medium risk: {contract_data.get('contract_address', '')[:16]} ({risk_score})")
            
        except Exception as e:
            logger.error(f"Scheduled scan error: {e}")
    
    def run_schedule(self):
        """Run scheduler in background thread"""
        schedule.every(SCHEDULE_INTERVAL).minutes.do(
            lambda: asyncio.create_task(self.scheduled_scan())
        )
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    # ═══════════════════════════════════════════════════════════
    # MAIN
    # ═══════════════════════════════════════════════════════════
    
    async def start(self):
        """Start the bridge"""
        await self.init_bot()
        
        self.running = True
        
        # Start scheduler in background
        if SCHEDULE_INTERVAL > 0:
            scheduler_thread = threading.Thread(target=self.run_schedule)
            scheduler_thread.daemon = True
            scheduler_thread.start()
            logger.info(f"Scheduler started ({SCHEDULE_INTERVAL} min interval)")
        
        # Start bot
        logger.info("Starting Telegram bridge...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep running
        while self.running:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the bridge"""
        self.running = False
        await self.application.stop()


# ═══════════════════════════════════════════════════════════
# SYSTEMD SERVICE SETUP
# ═══════════════════════════════════════════════════════════

SYSTEMD_SERVICE = """[Unit]
Description=RugMuncher Telegram-Ollama Bridge
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=/root
Environment=PYTHONPATH=/root
Environment=TELEGRAM_BOT_TOKEN={token}
Environment=CHANNEL_ID={channel}
Environment=OLLAMA_URL=http://127.0.0.1:11434/api/generate
Environment=SCHEDULE_INTERVAL=5
ExecStart=/usr/bin/python3 /root/rugmuncher_telegram_bridge.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


def setup_systemd_service():
    """Create and enable systemd service"""
    service_content = SYSTEMD_SERVICE.format(
        token=BOT_TOKEN or 'YOUR_TOKEN_HERE',
        channel=CHANNEL_ID
    )
    
    print("📋 Systemd Service Configuration:")
    print("=" * 60)
    print(service_content)
    print("=" * 60)
    print("\nTo install:")
    print("  sudo tee /etc/systemd/system/rugmuncher-bridge.service << 'EOF'")
    print(service_content)
    print("EOF")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable rugmuncher-bridge")
    print("  sudo systemctl start rugmuncher-bridge")


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════

async def main():
    """Main entry point"""
    bridge = TelegramBridge()
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await bridge.stop()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_systemd_service()
    else:
        asyncio.run(main())
