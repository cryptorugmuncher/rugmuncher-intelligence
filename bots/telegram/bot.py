#!/usr/bin/env python3
"""
🤖 Rug Munch Bot — @rugmunchbot
=================================
Single bot for everything. Works in DMs and groups.
Posts to channels (broadcast-only, no command responses in channels).

Architecture:
  User (DM/Group) → Command Router → Orchestrator API → AI Bot → Response
                                          ↓
                                   Backend (gamification, history)
                                          ↓
                                   Channel Posts (scans, news, alerts)
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "bots" / "telegram"))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)

from config import BOT_TOKEN, BOT_USERNAME, COMMANDS
from utils import should_process_command

# Import command handlers
from commands import (
    cmd_security, cmd_scan, cmd_audit, cmd_predict,
    cmd_whales, cmd_holders, cmd_bundle, cmd_portfolio,
    cmd_news, cmd_status, cmd_balance, cmd_subscribe, cmd_leaderboard, cmd_app,
    cmd_upgrade, cmd_help, cmd_start,
    cmd_pay,
)
from commands.payment import handle_pay_callback, handle_pre_checkout, handle_successful_payment

# Logging
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("rugmunchbot")


# ═══════════════════════════════════════════════════════════════════
# BOT APPLICATION
# ═══════════════════════════════════════════════════════════════════

def create_app() -> Application:
    """Create and configure the bot application."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers — only in DMs and groups, NOT channels
    app.add_handler(CommandHandler("start", _safe_cmd(cmd_start), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("help", _safe_cmd(cmd_help), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("security", _safe_cmd(cmd_security), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("scan", _safe_cmd(cmd_scan), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("audit", _safe_cmd(cmd_audit), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("predict", _safe_cmd(cmd_predict), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("whales", _safe_cmd(cmd_whales), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("holders", _safe_cmd(cmd_holders), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("bundle", _safe_cmd(cmd_bundle), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("portfolio", _safe_cmd(cmd_portfolio), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("news", _safe_cmd(cmd_news), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("status", _safe_cmd(cmd_status), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("balance", _safe_cmd(cmd_balance), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("subscribe", _safe_cmd(cmd_subscribe), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("leaderboard", _safe_cmd(cmd_leaderboard), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("app", _safe_cmd(cmd_app), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("upgrade", _safe_cmd(cmd_upgrade), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("pay", _safe_cmd(cmd_pay), filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))

    # Payment callbacks
    app.add_handler(CallbackQueryHandler(handle_pay_callback, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(handle_pay_callback, pattern="^crypto_"))
    app.add_handler(PreCheckoutQueryHandler(handle_pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))

    # Group join handler — welcome message when bot is added to a group
    app.add_handler(ChatMemberHandler(_on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

    # Error handler
    app.add_error_handler(_error_handler)

    return app


def _safe_cmd(handler):
    """Wrap command handler to filter out channels."""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not should_process_command(update):
            return
        await handler(update, ctx)
    return wrapper


async def _on_bot_added(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when bot is added to a group."""
    from config import GROUP_WELCOME_MESSAGE, BOT_USERNAME
    result = update.my_chat_member
    if not result:
        return
    old_status = result.old_chat_member.status if result.old_chat_member else ""
    new_status = result.new_chat_member.status if result.new_chat_member else ""

    # Only trigger when bot is actually added (was not a member, now is)
    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
        chat = result.chat
        if chat.type in ("group", "supergroup"):
            try:
                await ctx.bot.send_message(
                    chat_id=chat.id,
                    text=(
                        f"{GROUP_WELCOME_MESSAGE}\n\n"
                        f"<b>Quick start:</b>\n"
                        f"<code>/security &lt;token&gt;</code> — Risk scan\n"
                        f"<code>/scan &lt;token&gt;</code> — Full report\n"
                        f"<code>/help</code> — All commands\n\n"
                        f"💡 Tip: You can also mention me: <code>/security@{BOT_USERNAME} &lt;token&gt;</code>"
                    ),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.warning(f"Failed to send group welcome: {e}")


async def _error_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Error: {ctx.error}", exc_info=True)
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Something went wrong. Please try again later.",
                parse_mode="HTML",
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════

def main():
    logger.info("🤖 Starting @rugmunchbot...")
    logger.info(f"   Username: @{BOT_USERNAME}")
    logger.info(f"   Commands: {len(COMMANDS.strip().split(chr(10)))}")

    app = create_app()
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
