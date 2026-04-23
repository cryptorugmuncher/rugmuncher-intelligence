"""
Telegram Bot Handler - RMI Bot Integration
==========================================
Handles Telegram messages and routes to RMI Bot for responses.
Polite crypto investigator personality.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, '/mnt/okcomputer/output/omega_forensic_v5')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from bots.rmi_bot import get_rmi_bot, BotResponse
from core.llm_rotation import quick_generate
from forensic.wallet_clustering import get_clustering_engine
from forensic.api_arsenal import get_api_arsenal


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_NAME = "RMI Bot"
BOT_USERNAME = "@RugMunchIntelBot"


class TelegramBotHandler:
    """
    Telegram bot handler for RMI Bot.
    Routes messages and provides interactive features.
    """
    
    def __init__(self):
        self.application = None
        self.rmi_bot = get_rmi_bot()
        self.user_sessions: Dict[int, Dict] = {}
        
    async def start(self):
        """Start the bot."""
        if not BOT_TOKEN:
            logger.error("No TELEGRAM_BOT_TOKEN found!")
            return
        
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("investigate", self.cmd_investigate))
        self.application.add_handler(CommandHandler("cluster", self.cmd_cluster))
        self.application.add_handler(CommandHandler("bubble", self.cmd_bubble))
        self.application.add_handler(CommandHandler("token", self.cmd_token))
        self.application.add_handler(CommandHandler("report", self.cmd_report))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("methodology", self.cmd_methodology))
        
        # Callback handler for buttons
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler for text
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("RMI Bot started!")
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling()
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        
        welcome_message = f"""👋 Welcome to RMI Bot (RugMunch Intelligence)

I'm your polite crypto investigator, here to help you:
• 🔍 Investigate wallets and trace transactions
• 🕸️ Find wallet clusters and connections
• 🫧 Generate bubble maps for visualization
• 📊 Analyze tokens for suspicious patterns
• 📄 Create forensic reports

**Current Case Focus**: CRM Token Investigation
**Approach**: Evidence-based, presumption of innocence

I never claim guilt without proof. All findings are verified with on-chain data.

Type /help to see all commands, or just paste a wallet address to investigate!
"""
        
        keyboard = [
            [InlineKeyboardButton("🔍 Investigate Wallet", callback_data="action_investigate")],
            [InlineKeyboardButton("🕸️ Find Clusters", callback_data="action_cluster")],
            [InlineKeyboardButton("🫧 Bubble Map", callback_data="action_bubble")],
            [InlineKeyboardButton("📋 View Methodology", callback_data="action_methodology")],
        ]
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """📋 **RMI Bot Commands**

**Investigation Commands:**
`/investigate <wallet>` - Deep wallet analysis
`/cluster <wallet>` - Find wallet clusters
`/bubble <wallet>` - Generate bubble map
`/token <address>` - Analyze token

**Report Commands:**
`/report` - Generate case report
`/status` - Check investigation status

**Info Commands:**
`/methodology` - View our methodology
`/help` - Show this help message

**Quick Actions:**
Just paste any wallet address (44 chars) and I'll investigate it automatically!

**Examples:**
```
/investigate Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS
/cluster 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
/bubble 5xot9PVkphiX2adznhKBAD7BqCjT5pRSfh5s4nBw7Z8V
```
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def cmd_investigate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /investigate command."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a wallet address.\n\n"
                "Example: `/investigate Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS`",
                parse_mode='Markdown'
            )
            return
        
        wallet = context.args[0]
        
        if len(wallet) != 44:
            await update.message.reply_text(
                "❌ Invalid wallet address. Solana addresses are 44 characters."
            )
            return
        
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Get investigation from RMI Bot
        response = await self.rmi_bot.investigate_wallet(wallet)
        
        # Send response
        await update.message.reply_text(response.text, parse_mode='Markdown')
        
        # If we have APIs connected, do deeper analysis
        if response.needs_verification:
            keyboard = [
                [InlineKeyboardButton("🔍 Deep Analysis", callback_data=f"deep_{wallet}")],
                [InlineKeyboardButton("🫧 Bubble Map", callback_data=f"bubble_{wallet}")],
                [InlineKeyboardButton("🕸️ Find Clusters", callback_data=f"cluster_{wallet}")],
            ]
            await update.message.reply_text(
                "Would you like me to perform deeper analysis?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def cmd_cluster(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cluster command."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a wallet address.\n\n"
                "Example: `/cluster Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS`",
                parse_mode='Markdown'
            )
            return
        
        wallet = context.args[0]
        
        if len(wallet) != 44:
            await update.message.reply_text("❌ Invalid wallet address.")
            return
        
        await update.message.chat.send_action(action="typing")
        
        response = await self.rmi_bot.find_wallet_cluster(wallet)
        
        await update.message.reply_text(response.text, parse_mode='Markdown')
    
    async def cmd_bubble(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /bubble command."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a wallet address.\n\n"
                "Example: `/bubble Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS`",
                parse_mode='Markdown'
            )
            return
        
        wallet = context.args[0]
        
        if len(wallet) != 44:
            await update.message.reply_text("❌ Invalid wallet address.")
            return
        
        await update.message.chat.send_action(action="typing")
        
        response = await self.rmi_bot.generate_bubble_map(wallet)
        
        await update.message.reply_text(response.text, parse_mode='Markdown')
        
        # Provide link to web bubble map
        web_url = f"https://intel.cryptorugmunch.com/api/bubble/{wallet}"
        await update.message.reply_text(
            f"🌐 View interactive bubble map:\n{web_url}"
        )
    
    async def cmd_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /token command."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a token address.\n\n"
                "Example: `/token Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS`",
                parse_mode='Markdown'
            )
            return
        
        token = context.args[0]
        
        await update.message.chat.send_action(action="typing")
        
        response = await self.rmi_bot.analyze_token(token)
        
        await update.message.reply_text(response.text, parse_mode='Markdown')
    
    async def cmd_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /report command."""
        await update.message.chat.send_action(action="typing")
        
        # Generate quick summary using LLM
        prompt = """Generate a brief status report for the CRM token investigation.
Include:
- Current focus
- Key findings (evidence-based only)
- Next steps
Keep it concise and professional."""
        
        report = await quick_generate(prompt, task_type="analysis")
        
        await update.message.reply_text(
            f"📄 **Investigation Status Report**\n\n{report}",
            parse_mode='Markdown'
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        status_text = f"""📊 **RMI Bot Status**

**System**: Online ✅
**Version**: 1.0.0
**Case**: CRM Token Investigation

**Capabilities**:
✅ Wallet investigation
✅ Cluster detection
✅ Bubble map generation
✅ Token analysis
✅ Report generation

**APIs Connected**:
🟢 Helius (Solana data)
🟢 Groq (Quick responses)
🟡 Arkham (Entity labels)
🟡 MistTrack (Risk scoring)

**Evidence Tiers**:
• Tier 1: Direct evidence
• Tier 2: Strong correlation
• Tier 3: Suspicious pattern
• Tier 4: Indirect connection
• Tier 5: Unverified

Built with Kimi AI | intel.cryptorugmunch.com
"""
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def cmd_methodology(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /methodology command."""
        methodology_text = """🔬 **RMI Methodology**

**Our Principles:**
1. **Evidence-Based Only** - All claims verified on-chain
2. **Presumption of Innocence** - Never assume guilt
3. **Transparent Corrections** - Document when wrong
4. **Verifiable Claims** - Provide transaction signatures

**Evidence Tiers:**
🟢 **Tier 1** - Direct evidence (confirmed on-chain)
🟡 **Tier 2** - Strong correlation (multiple sources)
🟠 **Tier 3** - Suspicious pattern (worth investigating)
🔴 **Tier 4** - Indirect connection (circumstantial)
⚪ **Tier 5** - Unverified (needs confirmation)

**Clustering Methods:**
• Temporal proximity (5-min windows)
• Common counterparties
• Behavioral patterns
• Common funding sources

**APIs Used:**
• Helius (Solana data)
• Arkham Intelligence
• MistTrack
• ChainAbuse
• BirdEye
• LunarCrush

**LLM Models:**
• Llama 3.3 70B (Groq)
• Gemini 2.0 Flash
• Claude 3 Haiku
• DeepSeek Chat

Full methodology: intel.cryptorugmunch.com/methodology
"""
        await update.message.reply_text(methodology_text, parse_mode='Markdown')
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "action_investigate":
            await query.edit_message_text(
                "Please use the command:\n`/investigate <wallet_address>`",
                parse_mode='Markdown'
            )
        elif data == "action_cluster":
            await query.edit_message_text(
                "Please use the command:\n`/cluster <wallet_address>`",
                parse_mode='Markdown'
            )
        elif data == "action_bubble":
            await query.edit_message_text(
                "Please use the command:\n`/bubble <wallet_address>`",
                parse_mode='Markdown'
            )
        elif data == "action_methodology":
            await self.cmd_methodology(update, context)
        elif data.startswith("deep_"):
            wallet = data[5:]
            await query.edit_message_text(f"🔍 Running deep analysis on `{wallet[:20]}...`", parse_mode='Markdown')
            # Trigger deep analysis
        elif data.startswith("bubble_"):
            wallet = data[7:]
            await query.edit_message_text(f"🫧 Generating bubble map for `{wallet[:20]}...`", parse_mode='Markdown')
            # Trigger bubble map
        elif data.startswith("cluster_"):
            wallet = data[8:]
            await query.edit_message_text(f"🕸️ Finding clusters around `{wallet[:20]}...`", parse_mode='Markdown')
            # Trigger cluster detection
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        message_text = update.message.text.strip()
        user_id = update.effective_user.id
        
        # Check if it's a wallet address (44 chars)
        if len(message_text) == 44 and message_text[0].isalnum():
            # Looks like a wallet address
            await update.message.chat.send_action(action="typing")
            
            response = await self.rmi_bot.chat(message_text, str(user_id))
            
            keyboard = [
                [InlineKeyboardButton("🔍 Investigate", callback_data=f"deep_{message_text}")],
                [InlineKeyboardButton("🫧 Bubble Map", callback_data=f"bubble_{message_text}")],
            ]
            
            await update.message.reply_text(
                response,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            return
        
        # General chat with RMI Bot
        await update.message.chat.send_action(action="typing")
        
        response = await self.rmi_bot.chat(message_text, str(user_id))
        
        await update.message.reply_text(response, parse_mode='Markdown')


# Global handler instance
_handler = None

def get_telegram_handler() -> TelegramBotHandler:
    """Get global Telegram handler instance."""
    global _handler
    if _handler is None:
        _handler = TelegramBotHandler()
    return _handler


async def run_bot():
    """Run the Telegram bot."""
    handler = get_telegram_handler()
    await handler.start()


def run_bot_sync():
    """Run bot synchronously."""
    asyncio.run(run_bot())


if __name__ == "__main__":
    print("=" * 70)
    print("RMI TELEGRAM BOT")
    print("=" * 70)
    
    if not BOT_TOKEN:
        print("\n❌ ERROR: No TELEGRAM_BOT_TOKEN found!")
        print("\nSet your bot token:")
        print("  export TELEGRAM_BOT_TOKEN='your_token_here'")
        print("\nGet a token from @BotFather on Telegram")
    else:
        print("\n🤖 Starting RMI Bot...")
        print(f"   Bot: {BOT_NAME}")
        print(f"   Username: {BOT_USERNAME}")
        print("\n   Commands:")
        print("     /start - Welcome message")
        print("     /help - Show commands")
        print("     /investigate <wallet> - Investigate wallet")
        print("     /cluster <wallet> - Find clusters")
        print("     /bubble <wallet> - Generate bubble map")
        print("     /token <address> - Analyze token")
        print("     /report - Generate report")
        print("     /status - System status")
        print("     /methodology - View methodology")
        print("\n" + "=" * 70)
        
        run_bot_sync()
