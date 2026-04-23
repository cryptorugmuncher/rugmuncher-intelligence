"""
👛 Wallet Commands
==================
/whales, /holders, /bundle, /portfolio
"""

import aiohttp
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import ORCHESTRATOR_URL, BACKEND_URL
from formatters.scan_result import format_wallet_scan

logger = logging.getLogger(__name__)


async def _dispatch_task(task_type: str, payload: dict) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ORCHESTRATOR_URL}/orchestrator/task",
                json={"task_type": task_type, "payload": payload, "source": "telegram"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                return await resp.json()
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        return {"success": False, "error": str(e)}


async def cmd_whales(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/whales <token> — Whale concentration analysis."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/whales &lt;token_address&gt;</code>", parse_mode="HTML"
        )
        return

    token = args[0]
    await update.message.chat.send_action(action="typing")

    result = await _dispatch_task("whale_analysis", {"contract": token})

    if not result.get("success"):
        await update.message.reply_text("❌ Analysis failed.", parse_mode="HTML")
        return

    data = result.get("result", {})
    whales = data.get("whales", [])
    concentration = data.get("concentration", 0)

    lines = [
        f"🐋 <b>Whale Analysis</b>",
        f"",
        f"<code>{token}</code>",
        f"",
        f"📊 <b>Top 10 Holder Concentration:</b> {concentration:.1f}%",
        f"",
    ]

    if whales:
        lines.append("🐋 <b>Top Whales:</b>")
        for i, w in enumerate(whales[:10], 1):
            addr = w.get("address", "?")
            pct = w.get("percentage", 0)
            label = w.get("label", "Unknown")
            lines.append(f"   {i}. <code>{addr[:6]}...{addr[-4:]}</code> — {pct:.2f}% ({label})")
    else:
        lines.append("ℹ️ No whale data available")

    lines.append("")
    lines.append("📊 <a href='https://rugmunch.io/whales'>View full whale map</a>")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    await _record_and_notify(update, "portfolio_tracker", wallet, data)
    await _record_and_notify(update, "whale_analysis", token, data)


async def _record_and_notify(update: Update, scan_type: str, token: str, result: dict):
    """Record scan and notify of badge unlocks."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/v1/telegram/scan/record",
                json={
                    "telegram_id": update.effective_user.id,
                    "scan_type": scan_type,
                    "token": token,
                    "result": result,
                },
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    badges = data.get("badges_unlocked", [])
                    for badge_id in badges:
                        emoji = {"first_scan": "🎯", "ten_scans": "🔬", "fifty_scans": "🌊",
                                 "hundred_scans": "⚔️", "five_hundred_scans": "🔮",
                                 "seven_day_streak": "🔥", "thirty_day_streak": "📅",
                                 "level_3": "⭐", "level_5": "🏆", "level_6": "👑",
                                 "pro_subscriber": "💎", "elite_subscriber": "👑"}.get(badge_id, "🏅")
                        name = {"first_scan": "First Blood", "ten_scans": "Scan Surgeon",
                                "fifty_scans": "Deep Diver", "hundred_scans": "Centurion",
                                "five_hundred_scans": "Oracle", "seven_day_streak": "Consistent",
                                "thirty_day_streak": "Obsessed", "level_3": "Rising Star",
                                "level_5": "Elite Hunter", "level_6": "Legend",
                                "pro_subscriber": "Pro Supporter", "elite_subscriber": "Elite Supporter"}.get(badge_id, badge_id)
                        xp = data.get("xp_gained", 0)
                        await update.message.reply_text(
                            f"🎉 <b>Badge Unlocked!</b>\n\n{emoji} <b>{name}</b>\n✨ +{xp} XP",
                            parse_mode="HTML",
                        )
    except Exception:
        pass


async def cmd_holders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/holders <token> — Holder distribution analysis."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/holders &lt;token_address&gt;</code>", parse_mode="HTML"
        )
        return

    token = args[0]
    await update.message.chat.send_action(action="typing")

    result = await _dispatch_task("holder_analysis", {"contract": token})

    if not result.get("success"):
        await update.message.reply_text("❌ Analysis failed.", parse_mode="HTML")
        return

    data = result.get("result", {})
    total_holders = data.get("total_holders", 0)
    distribution = data.get("distribution", {})

    lines = [
        f"👥 <b>Holder Analysis</b>",
        f"",
        f"<code>{token}</code>",
        f"",
        f"👤 <b>Total Holders:</b> {total_holders:,}",
        f"",
    ]

    if distribution:
        lines.append("📊 <b>Distribution:</b>")
        for range_name, pct in distribution.items():
            lines.append(f"   • {range_name}: {pct:.1f}%")

    lines.append("")
    lines.append("📊 <a href='https://rugmunch.io/holders'>View full breakdown</a>")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    await _record_and_notify(update, "holder_analysis", token, data)


async def cmd_bundle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/bundle <token> — Detect wallet bundling."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/bundle &lt;token_address&gt;</code>", parse_mode="HTML"
        )
        return

    token = args[0]
    await update.message.chat.send_action(action="typing")

    result = await _dispatch_task("bundling_detection", {"contract": token})

    if not result.get("success"):
        await update.message.reply_text("❌ Detection failed.", parse_mode="HTML")
        return

    data = result.get("result", {})
    is_bundled = data.get("is_bundled", False)
    clusters = data.get("clusters", [])

    if is_bundled:
        lines = [
            f"🚨 <b>BUNDLING DETECTED</b>",
            f"",
            f"<code>{token}</code>",
            f"",
            f"⚠️ <b>This token shows signs of wallet bundling!</b>",
            f"",
            f"🔗 <b>Clusters Found:</b> {len(clusters)}",
            f"",
        ]
        for c in clusters[:3]:
            lines.append(f"   • {c.get('wallets', 0)} wallets, {c.get('percentage', 0):.1f}% supply")
    else:
        lines = [
            f"✅ <b>No Bundling Detected</b>",
            f"",
            f"<code>{token}</code>",
            f"",
            f"✅ Wallet distribution looks organic.",
        ]

    lines.append("")
    lines.append("📊 <a href='https://rugmunch.io/bundle'>View full analysis</a>")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    await _record_and_notify(update, "bundling_detection", token, data)


async def cmd_portfolio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/portfolio <wallet> — Track wallet portfolio."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/portfolio &lt;wallet_address&gt;</code>", parse_mode="HTML"
        )
        return

    wallet = args[0]
    await update.message.chat.send_action(action="typing")

    result = await _dispatch_task("portfolio_tracker", {"wallet": wallet})

    if not result.get("success"):
        await update.message.reply_text("❌ Portfolio lookup failed.", parse_mode="HTML")
        return

    data = result.get("result", {})
    tokens = data.get("tokens", [])
    total_value = data.get("total_value", 0)

    lines = [
        f"💼 <b>Portfolio</b>",
        f"",
        f"<code>{wallet}</code>",
        f"",
        f"💰 <b>Total Value:</b> ${total_value:,.2f}",
        f"",
    ]

    if tokens:
        lines.append("📊 <b>Holdings:</b>")
        for t in tokens[:10]:
            name = t.get("name", "Unknown")
            symbol = t.get("symbol", "?")
            balance = t.get("balance", 0)
            value = t.get("value", 0)
            lines.append(f"   • {name} (${symbol}): {balance:,.4f} (${value:,.2f})")
    else:
        lines.append("ℹ️ No token holdings found")

    lines.append("")
    lines.append("📊 <a href='https://rugmunch.io/portfolio'>View full portfolio</a>")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
