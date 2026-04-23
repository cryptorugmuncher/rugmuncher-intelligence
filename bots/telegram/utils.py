"""
🛠️ Telegram Bot Utilities
==========================
Helper functions for @rugmunchbot.
"""

import logging
from telegram import Update, Chat

logger = logging.getLogger(__name__)


def is_private_chat(update: Update) -> bool:
    """Check if message is in a DM."""
    return update.effective_chat.type == Chat.PRIVATE


def is_group_chat(update: Update) -> bool:
    """Check if message is in a group or supergroup."""
    return update.effective_chat.type in (Chat.GROUP, Chat.SUPERGROUP)


def is_channel(update: Update) -> bool:
    """Check if message is in a channel."""
    return update.effective_chat.type == Chat.CHANNEL


def should_process_command(update: Update) -> bool:
    """
    Only process commands in DMs or groups.
    Ignore commands in channels — channels are broadcast-only.
    """
    if is_channel(update):
        return False
    return True


def get_command_text(update: Update, bot_username: str) -> str:
    """
    Extract command text, handling @botname suffixes in groups.
    E.g., '/security@rugmunchbot 0x123' → '/security 0x123'
    """
    text = update.message.text or ""
    parts = text.split()
    if not parts:
        return ""

    cmd = parts[0]
    if "@" in cmd:
        cmd = cmd.split("@")[0]

    return cmd


def get_args(update: Update) -> list:
    """Get command arguments (everything after the command)."""
    text = update.message.text or ""
    parts = text.split()
    if len(parts) <= 1:
        return []
    return parts[1:]


def is_admin_in_group(update: Update, user_id: int) -> bool:
    """Check if user is admin in the current group."""
    chat = update.effective_chat
    if chat.type not in (Chat.GROUP, Chat.SUPERGROUP):
        return True  # In DM, user is always "admin"

    try:
        member = chat.get_member(user_id)
        return member.status in ("creator", "administrator")
    except Exception:
        return False


async def send_channel_post(bot, channel_id: str, text: str, parse_mode: str = "HTML"):
    """Send a message to a channel (one-way broadcast)."""
    if not channel_id:
        return
    try:
        await bot.send_message(
            chat_id=channel_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.warning(f"Failed to post to channel {channel_id}: {e}")
