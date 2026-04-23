"""
ℹ️ Info Commands
================
/start, /help, /status, /upgrade, /news
"""

import aiohttp
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import BACKEND_URL, BOT_USERNAME
from formatters.scan_result import format_tier_status, format_upgrade_menu, format_help, format_welcome

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/start — Welcome message + Mini App button."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    from config import WEBAPP_URL

    user = update.effective_user
    text = format_welcome(user.first_name or "there")

    # Mini App button — opens RMI web app inside Telegram
    keyboard = []
    if WEBAPP_URL:
        keyboard.append([
            InlineKeyboardButton(
                "🚀 Open RMI App",
                web_app=WebAppInfo(url=WEBAPP_URL),
            )
        ])
    keyboard.append([
        InlineKeyboardButton("💎 Upgrade", callback_data="pay_tier_pro"),
        InlineKeyboardButton("📊 Status", callback_data="noop_status"),
    ])

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    # Register user in backend
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{BACKEND_URL}/api/v1/telegram/user/register",
                json={
                    "telegram_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                timeout=aiohttp.ClientTimeout(total=5),
            )
    except Exception as e:
        logger.warning(f"Failed to register user: {e}")


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/help — Show all commands."""
    text = format_help()
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/status — Check subscription tier and scan usage."""
    user_id = update.effective_user.id

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BACKEND_URL}/api/v1/telegram/user/{user_id}",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    tier = data.get("tier", "free")
                    scans_used = data.get("scans_used", 0)
                    scans_limit = data.get("scans_limit", 3)
                    scans_remaining = data.get("scans_remaining", 3)
                else:
                    tier = "free"
                    scans_used = 0
                    scans_limit = 3
                    scans_remaining = 3
    except Exception as e:
        logger.warning(f"Failed to fetch user status: {e}")
        tier = "free"
        scans_used = 0
        scans_limit = 3
        scans_remaining = 3

    text = format_tier_status(user_id, tier, scans_used, scans_limit, scans_remaining)
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/balance — Alias for /status (scan balance)."""
    await cmd_status(update, ctx)


async def cmd_app(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/app — Open the RMI web app inside Telegram."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    from config import WEBAPP_URL

    if not WEBAPP_URL:
        await update.message.reply_text(
            "❌ Web App not configured. Visit https://rugmunch.io instead.",
            parse_mode="HTML",
        )
        return

    keyboard = [
        [InlineKeyboardButton("🚀 Open RMI App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]

    await update.message.reply_text(
        "🚀 <b>Rug Munch Intel</b>\n\n"
        "Open the full dashboard inside Telegram:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_subscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/subscribe — Alias for /upgrade."""
    await cmd_upgrade(update, ctx)


async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/leaderboard — Top scanners."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BACKEND_URL}/api/v1/telegram/leaderboard?limit=10",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    entries = data.get("leaderboard", [])
                else:
                    entries = []
    except Exception as e:
        logger.warning(f"Failed to fetch leaderboard: {e}")
        entries = []

    lines = ["🏆 <b>Top Scanners</b>", ""]

    if not entries:
        lines.append("ℹ️ No data yet. Be the first to scan!")
    else:
        for i, entry in enumerate(entries[:10], 1):
            name = entry.get("first_name") or entry.get("username") or f"User {entry.get('telegram_id', '?')}"
            tier = entry.get("tier", "free").upper()
            scans = entry.get("total_scans", 0)
            level = entry.get("level", 1)
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "▫️"
            lines.append(f"{medal} <b>{name}</b> — {scans} scans (Lv.{level}, {tier})")

    lines.append("")
    lines.append("💡 Scan more tokens to climb the ranks!")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


async def cmd_upgrade(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/upgrade — Show pricing and tiers."""
    text = format_upgrade_menu()
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)


async def cmd_news(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/news — Crypto news digest."""
    from bots.telegram.news_engine import get_news_engine

    await update.message.chat.send_action(action="typing")

    try:
        engine = get_news_engine()
        headlines = engine.get_headlines(limit=5)

        lines = ["📰 <b>Crypto News Digest</b>", ""]

        for i, h in enumerate(headlines, 1):
            title = h.get("title", "No title")
            source = h.get("source", "Unknown")
            url = h.get("url", "")
            lines.append(f"{i}. <b>{title}</b>")
            lines.append(f"   🏷 {source}")
            if url:
                lines.append(f"   🔗 <a href='{url}'>Read more</a>")
            lines.append("")

        lines.append("📊 <a href='https://rugmunch.io/news'>Full news feed</a>")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"News failed: {e}")
        await update.message.reply_text(
            "❌ Couldn't fetch news right now. Try again later.", parse_mode="HTML"
        )
