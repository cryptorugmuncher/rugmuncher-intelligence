"""
🎨 Scan Result Formatters
==========================
Beautiful, organized Telegram message templates for scan outputs.
"""

from typing import Dict, Any, Optional
from config import RISK_COLORS, TIERS


def _risk_emoji(score: int) -> str:
    if score >= 90:
        return RISK_COLORS["critical"]
    elif score >= 70:
        return RISK_COLORS["high"]
    elif score >= 40:
        return RISK_COLORS["medium"]
    elif score >= 20:
        return RISK_COLORS["low"]
    return RISK_COLORS["safe"]


def _risk_label(score: int) -> str:
    if score >= 90:
        return "CRITICAL"
    elif score >= 70:
        return "HIGH RISK"
    elif score >= 40:
        return "MEDIUM RISK"
    elif score >= 20:
        return "LOW RISK"
    return "SAFE"


def format_security_scan(token: str, result: Dict[str, Any]) -> str:
    """Format a security scan result for Telegram."""
    risk_score = result.get("risk_score", 50)
    emoji = _risk_emoji(risk_score)
    label = _risk_label(risk_score)

    lines = [
        f"🔍 <b>Security Scan</b>",
        f"",
        f"<code>{token}</code>",
        f"",
        f"{emoji} <b>Risk Score: {risk_score}/100</b> — {label}",
        f"",
    ]

    # Red flags
    red_flags = result.get("red_flags", [])
    if red_flags:
        lines.append("🚩 <b>Red Flags:</b>")
        for flag in red_flags[:5]:
            lines.append(f"   • {flag}")
        lines.append("")

    # Checks
    checks = result.get("checks", {})
    if checks:
        lines.append("✅ <b>Checks:</b>")
        for check, status in checks.items():
            icon = "✅" if status else "❌"
            lines.append(f"   {icon} {check}")
        lines.append("")

    # Quick verdict
    if risk_score >= 70:
        lines.append("⚠️ <b>Verdict:</b> High probability of scam. Avoid.")
    elif risk_score >= 40:
        lines.append("⚠️ <b>Verdict:</b> Suspicious. Proceed with extreme caution.")
    else:
        lines.append("✅ <b>Verdict:</b> Looks relatively safe, but DYOR.")

    lines.append("")
    lines.append("📊 <a href='https://rugmunch.io/scans'>View full report on RugMunch</a>")

    return "\n".join(lines)


def format_wallet_scan(address: str, result: Dict[str, Any]) -> str:
    """Format a wallet scan result."""
    risk_score = result.get("risk_score", 50)
    emoji = _risk_emoji(risk_score)

    lines = [
        f"👛 <b>Wallet Scan</b>",
        f"",
        f"<code>{address}</code>",
        f"",
        f"{emoji} <b>Risk Score: {risk_score}/100</b>",
        f"",
    ]

    # Connections
    connections = result.get("connections", [])
    if connections:
        lines.append("🔗 <b>Connected Wallets:</b>")
        for conn in connections[:5]:
            lines.append(f"   • <code>{conn}</code>")
        lines.append("")

    # Tags
    tags = result.get("tags", [])
    if tags:
        lines.append(f"🏷 <b>Tags:</b> {', '.join(tags)}")
        lines.append("")

    # Holdings
    holdings = result.get("holdings", [])
    if holdings:
        lines.append("💰 <b>Top Holdings:</b>")
        for h in holdings[:5]:
            lines.append(f"   • {h}")
        lines.append("")

    lines.append("📊 <a href='https://rugmunch.io/wallets'>View full analysis</a>")
    return "\n".join(lines)


def format_channel_post(scan_type: str, token: str, result: Dict[str, Any]) -> str:
    """Format a public channel post (less detail than DM)."""
    risk_score = result.get("risk_score", 50)
    emoji = _risk_emoji(risk_score)
    label = _risk_label(risk_score)
    red_flags = result.get("red_flags", [])

    lines = [
        f"🚨 <b>Rug Munch Scan</b>",
        f"",
        f"📍 <code>{token}</code>",
        f"",
        f"{emoji} <b>{label}</b> — Score: {risk_score}/100",
        f"",
    ]

    if red_flags:
        lines.append(f"🚩 {len(red_flags)} red flags detected")
        for flag in red_flags[:3]:
            lines.append(f"   • {flag}")
        lines.append("")

    lines.append("🔍 Scan by @rugmunchbot")
    lines.append("📊 <a href='https://rugmunch.io'>rugmunch.io</a>")

    return "\n".join(lines)


def format_tier_status(user_id: int, tier: str, scans_used: int, scans_limit: int, scans_remaining: int = -1) -> str:
    """Format user's subscription status."""
    tier_cfg = TIERS.get(tier, TIERS["free"])
    unlimited = scans_limit == -1

    if unlimited:
        remaining_text = "Unlimited"
        pct = 0
        bar = "█" * 10
    else:
        remaining = scans_remaining if scans_remaining >= 0 else max(0, scans_limit - scans_used)
        remaining_text = str(remaining)
        pct = (scans_used / scans_limit * 100) if scans_limit > 0 else 0
        bar_len = 10
        filled = int(pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)

    lines = [
        f"👤 <b>Your Account</b>",
        f"",
        f"🎖 <b>Tier:</b> {tier_cfg.name}",
        f"",
    ]

    if unlimited:
        lines.append(f"📊 <b>Scans Used:</b> {scans_used} / ∞")
        lines.append(f"   [{bar}] Unlimited")
    else:
        lines.append(f"📊 <b>Scans Used:</b> {scans_used} / {scans_limit}")
        lines.append(f"   [{bar}] {pct:.0f}%")

    lines.append(f"")
    lines.append(f"✨ <b>Remaining:</b> {remaining_text} scans")
    lines.append(f"")
    lines.append(f"🔓 <b>Features:</b>")

    for feat in tier_cfg.features:
        lines.append(f"   ✅ {feat}")

    lines.append("")
    if tier == "free":
        lines.append("💎 Use /upgrade to unlock more scans!")
    else:
        lines.append("💎 Use /upgrade to change your plan")

    return "\n".join(lines)


def format_upgrade_menu() -> str:
    """Format the upgrade/pricing menu."""
    lines = [
        f"💎 <b>Rug Munch Scan Tiers</b>",
        f"",
        f"Choose a plan that fits your needs:",
        f"",
    ]

    for key, tier in TIERS.items():
        if key == "free":
            lines.append(f"🆓 <b>{tier.name}</b> — FREE")
        else:
            lines.append(f"{tier.color} <b>{tier.name}</b> — ${tier.price_usd}/mo or {tier.price_stars} ⭐")
        lines.append(f"   {tier.scans_per_month} scans/month")
        for feat in tier.features:
            lines.append(f"   ✅ {feat}")
        lines.append("")

    lines.append("📦 <b>Scan Packs (One-time):</b>")
    lines.append("   5 scans — $3 or 30 ⭐")
    lines.append("   15 scans — $8 or 80 ⭐")
    lines.append("   50 scans — $20 or 200 ⭐")
    lines.append("")
    lines.append("💳 Use /pay to purchase")

    return "\n".join(lines)


def format_help() -> str:
    """Format the help message."""
    return """🤖 <b>Rug Munch Bot</b> — Don't Get Rugged

<b>Security Commands:</b>
   /security &lt;token&gt; — Contract scam analysis
   /scan &lt;token&gt; — Full intelligence report
   /audit &lt;token&gt; — Smart contract code audit
   /predict &lt;token&gt; — ML rug pull prediction

<b>Wallet Commands:</b>
   /whales &lt;token&gt; — Whale concentration
   /holders &lt;token&gt; — Holder distribution
   /bundle &lt;token&gt; — Wallet bundling detection
   /portfolio &lt;wallet&gt; — Portfolio tracker

<b>Info:</b>
   /news — Crypto news digest
   /status — Your subscription tier & scan balance
   /balance — Alias for /status
   /subscribe — View pricing & tiers
   /upgrade — View pricing
   /pay — Purchase scans
   /leaderboard — Top scanners
   /app — Open RMI web app inside Telegram
   /help — This message

💡 <b>Tip:</b> Add me to your group chat for shared scans!
   @rugmunchbot /security &lt;token&gt;

👥 <b>Community:</b> t.me/rugmunch_chat

📊 <a href='https://rugmunch.io'>rugmunch.io</a>
"""


def format_welcome(user_name: str) -> str:
    """Format the welcome message for new users."""
    from config import COMMUNITY_GROUP_URL
    group_line = f"\n👥 <b>Community:</b> <a href='{COMMUNITY_GROUP_URL}'>Join our group</a>\n" if COMMUNITY_GROUP_URL else "\n"
    return f"""👋 Welcome, {user_name}!

🤖 I'm <b>Rug Munch</b> — your crypto security bodyguard.

<b>What I do:</b>
   🔍 Scan tokens for scams before you buy
   🐋 Track whale movements
   🚨 Detect honeypots and rug pulls
   📊 Analyze smart contracts

<b>Try me:</b>
   <code>/security 0x123...</code>
   <code>/scan 0x123...</code>

🆓 You get <b>3 free scans</b> to start.
💎 Upgrade anytime with /upgrade{group_line}📊 <a href='https://rugmunch.io'>rugmunch.io</a>
"""
