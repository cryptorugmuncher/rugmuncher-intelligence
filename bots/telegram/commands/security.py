"""
🔒 Security Commands
====================
/security, /scan, /audit, /predict
"""

import aiohttp
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import ORCHESTRATOR_URL, BACKEND_URL, BOT_USERNAME
from formatters.scan_result import format_security_scan, format_channel_post

logger = logging.getLogger(__name__)


async def _dispatch_task(task_type: str, payload: dict, source: str = "telegram") -> dict:
    """Dispatch a task to the orchestrator."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ORCHESTRATOR_URL}/orchestrator/task",
                json={"task_type": task_type, "payload": payload, "source": source},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                return await resp.json()
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        return {"success": False, "error": str(e)}


async def _record_scan(telegram_id: int, scan_type: str, token: str, result: dict) -> dict:
    """Record scan to backend for gamification + history. Returns backend response."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/v1/telegram/scan/record",
                json={
                    "telegram_id": telegram_id,
                    "scan_type": scan_type,
                    "token": token,
                    "result": result,
                },
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}
    except Exception as e:
        logger.warning(f"Failed to record scan: {e}")
        return {}


BADGE_EMOJIS = {
    "first_scan": "🎯",
    "ten_scans": "🔬",
    "fifty_scans": "🌊",
    "hundred_scans": "⚔️",
    "five_hundred_scans": "🔮",
    "seven_day_streak": "🔥",
    "thirty_day_streak": "📅",
    "level_3": "⭐",
    "level_5": "🏆",
    "level_6": "👑",
    "pro_subscriber": "💎",
    "elite_subscriber": "👑",
}

BADGE_NAMES = {
    "first_scan": "First Blood",
    "ten_scans": "Scan Surgeon",
    "fifty_scans": "Deep Diver",
    "hundred_scans": "Centurion",
    "five_hundred_scans": "Oracle",
    "seven_day_streak": "Consistent",
    "thirty_day_streak": "Obsessed",
    "level_3": "Rising Star",
    "level_5": "Elite Hunter",
    "level_6": "Legend",
    "pro_subscriber": "Pro Supporter",
    "elite_subscriber": "Elite Supporter",
}

async def _notify_badges(update: Update, record_result: dict):
    """Send badge unlock notification if any badges were earned."""
    badges = record_result.get("badges_unlocked", [])
    if not badges:
        return
    for badge_id in badges:
        emoji = BADGE_EMOJIS.get(badge_id, "🏅")
        name = BADGE_NAMES.get(badge_id, badge_id)
        xp = record_result.get("xp_gained", 0)
        await update.message.reply_text(
            f"🎉 <b>Badge Unlocked!</b>\n\n"
            f"{emoji} <b>{name}</b>\n"
            f"✨ +{xp} XP",
            parse_mode="HTML",
        )


async def cmd_security(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/security <token> — Contract scam analysis."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/security &lt;token_address&gt;</code>\n\n"
            "Example: <code>/security 0x1234...abcd</code>",
            parse_mode="HTML",
        )
        return

    token = args[0]
    user_id = update.effective_user.id

    # Send "typing" action
    await update.message.chat.send_action(action="typing")

    # Dispatch to orchestrator (The Sentry)
    result = await _dispatch_task("security_scan", {"contract": token, "chain": "auto"})

    if not result.get("success"):
        await update.message.reply_text(
            "❌ Scan failed. Please try again later.",
            parse_mode="HTML",
        )
        return

    scan_result = result.get("result", {})

    # Format and send to user
    text = format_security_scan(token, scan_result)
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

    # Record scan for gamification
    record_result = await _record_scan(user_id, "security", token, scan_result)
    await _notify_badges(update, record_result)

    # Send shareable scan card
    await _send_scan_card(update, token, scan_result, "Security Scan")

    # Post to public scans channel
    await _post_to_channel(ctx, "scans", scan_type="security", token=token, result=scan_result)


async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/scan <token> — Full intelligence report."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/scan &lt;token_address&gt;</code>\n\n"
            "Example: <code>/scan 0x1234...abcd</code>",
            parse_mode="HTML",
        )
        return

    token = args[0]
    user_id = update.effective_user.id

    await update.message.chat.send_action(action="typing")

    result = await _dispatch_task("full_scan", {"contract": token, "chain": "auto"})

    if not result.get("success"):
        await update.message.reply_text("❌ Scan failed. Please try again later.", parse_mode="HTML")
        return

    scan_result = result.get("result", {})

    # Full scan is more detailed
    text = format_security_scan(token, scan_result)
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

    record_result = await _record_scan(user_id, "full_scan", token, scan_result)
    await _notify_badges(update, record_result)
    await _send_scan_card(update, token, scan_result, "Full Scan")
    await _post_to_channel(ctx, "scans", scan_type="full", token=token, result=scan_result)


async def cmd_audit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/audit <token> — Smart contract code audit."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/audit &lt;token_address&gt;</code>", parse_mode="HTML"
        )
        return

    token = args[0]
    await update.message.chat.send_action(action="typing")

    result = await _dispatch_task("code_audit", {"contract": token})

    if not result.get("success"):
        await update.message.reply_text("❌ Audit failed. Please try again later.", parse_mode="HTML")
        return

    # Format audit result
    audit_result = result.get("result", {})
    lines = [
        f"🔍 <b>Smart Contract Audit</b>",
        f"",
        f"<code>{token}</code>",
        f"",
    ]

    vulnerabilities = audit_result.get("vulnerabilities", [])
    if vulnerabilities:
        lines.append(f"🐛 <b>{len(vulnerabilities)} Vulnerabilities Found:</b>")
        for v in vulnerabilities[:5]:
            sev = v.get("severity", "medium")
            icon = "🔴" if sev == "critical" else "🟠" if sev == "high" else "🟡"
            lines.append(f"   {icon} {v.get('name', 'Unknown')}: {v.get('description', '')}")
    else:
        lines.append("✅ No critical vulnerabilities found")

    lines.append("")
    lines.append("📊 <a href='https://rugmunch.io/audits'>View full audit</a>")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    record_result = await _record_scan(update.effective_user.id, "audit", token, audit_result)
    await _notify_badges(update, record_result)
    await _send_scan_card(update, token, audit_result, "Contract Audit")


async def cmd_predict(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/predict <token> — ML rug pull prediction."""
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: <code>/predict &lt;token_address&gt;</code>", parse_mode="HTML"
        )
        return

    token = args[0]
    await update.message.chat.send_action(action="typing")

    result = await _dispatch_task("rug_pull_prediction", {"contract": token})

    if not result.get("success"):
        await update.message.reply_text("❌ Prediction failed.", parse_mode="HTML")
        return

    pred = result.get("result", {})
    probability = pred.get("probability", 0.5)

    if probability >= 0.7:
        verdict = "🔴 HIGH RISK of rug pull"
    elif probability >= 0.4:
        verdict = "🟠 MODERATE RISK — watch closely"
    else:
        verdict = "🟢 LOW RISK — relatively safe"

    lines = [
        f"🔮 <b>Rug Pull Prediction</b>",
        f"",
        f"<code>{token}</code>",
        f"",
        f"{verdict}",
        f"",
        f"📊 <b>Probability:</b> {probability * 100:.1f}%",
        f"",
    ]

    factors = pred.get("factors", [])
    if factors:
        lines.append("📋 <b>Key Factors:</b>")
        for f in factors[:5]:
            lines.append(f"   • {f}")

    lines.append("")
    lines.append("⚠️ This is AI-powered analysis. Always DYOR.")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    record_result = await _record_scan(update.effective_user.id, "predict", token, pred)
    await _notify_badges(update, record_result)


async def _send_scan_card(update: Update, token: str, result: dict, scan_type: str):
    """Generate and send a scan card image."""
    try:
        from io import BytesIO
        from PIL import Image
        import aiohttp
        import base64

        risk_score = result.get("risk_score")
        risk_level = result.get("risk_level") or result.get("consensus")
        verdict = result.get("verdict") or result.get("summary", "")[:120]
        red_flags = result.get("red_flags", []) or result.get("vulnerabilities", [])
        red_flag_names = [f.get("name", str(f)) for f in red_flags[:3]] if isinstance(red_flags, list) else []

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/v1/scan-card",
                json={
                    "token": token,
                    "chain": result.get("chain", "SOL"),
                    "scan_type": scan_type.upper(),
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "verdict": verdict,
                    "red_flags": red_flag_names,
                },
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    b64_image = data.get("image", "").replace("data:image/png;base64,", "")
                    if b64_image:
                        img_bytes = base64.b64decode(b64_image)
                        bio = BytesIO(img_bytes)
                        bio.name = "scan-card.png"
                        await update.message.reply_photo(
                            photo=bio,
                            caption="🖼️ <b>Shareable Scan Card</b> — Save and share!",
                            parse_mode="HTML",
                        )
    except Exception as e:
        logger.warning(f"Failed to generate scan card: {e}")


async def _post_to_channel(
    ctx: ContextTypes.DEFAULT_TYPE,
    channel_type: str,
    scan_type: str,
    token: str,
    result: dict,
):
    """Post scan result to public channel."""
    from config import CHANNEL_SCANS, CHANNEL_NEWS, CHANNEL_ALERTS

    channel_map = {
        "scans": CHANNEL_SCANS,
        "news": CHANNEL_NEWS,
        "alerts": CHANNEL_ALERTS,
    }

    channel_id = channel_map.get(channel_type)
    if not channel_id:
        return

    try:
        text = format_channel_post(scan_type, token, result)
        await ctx.bot.send_message(
            chat_id=channel_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.warning(f"Failed to post to {channel_type} channel: {e}")
