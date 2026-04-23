"""
💳 Payment Commands
====================
/pay — Purchase scans with Telegram Stars or crypto
"""

import aiohttp
import logging
import uuid
from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes

from config import BACKEND_URL, TIERS, SCAN_PACKS, STARS_PROVIDER_TOKEN

logger = logging.getLogger(__name__)


async def cmd_pay(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    /pay — Show payment options.
    
    Inline keyboard with tier options and scan packs.
    """
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = []

    # Tiers
    for key, tier in TIERS.items():
        if key == "free":
            continue
        keyboard.append([
            InlineKeyboardButton(
                f"{tier.name} — {tier.price_stars} ⭐",
                callback_data=f"pay_tier_{key}"
            )
        ])

    keyboard.append([InlineKeyboardButton("➖➖➖ Scan Packs ➖➖➖", callback_data="noop")])

    # Scan packs
    for key, pack in SCAN_PACKS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{pack['scans']} scans — {pack['price_stars']} ⭐",
                callback_data=f"pay_pack_{key}"
            )
        ])

    keyboard.append([InlineKeyboardButton("💳 Pay with Crypto", callback_data="pay_crypto")])

    await update.message.reply_text(
        "💎 <b>Purchase Scans</b>\n\n"
        "Choose a plan or scan pack:\n\n"
        "⭐ = Telegram Stars (in-app currency)\n"
        "💳 = Crypto (ETH/SOL)",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_pay_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle payment callback buttons."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("pay_tier_"):
        tier_key = data.replace("pay_tier_", "")
        await _send_stars_invoice(query, tier_key, is_tier=True)
    elif data.startswith("pay_pack_"):
        pack_key = data.replace("pay_pack_", "")
        await _send_stars_invoice(query, pack_key, is_tier=False)
    elif data == "pay_crypto":
        await _send_crypto_options(query)


async def _send_stars_invoice(query, key: str, is_tier: bool):
    """Send a Telegram Stars payment invoice."""
    if is_tier:
        item = TIERS.get(key)
        if not item or key == "free":
            await query.edit_message_text("❌ Invalid tier selected.")
            return
        title = f"Rug Munch {item.name}"
        description = f"{item.scans_per_month} scans per month"
        price = item.price_stars
        payload = f"tier:{key}:{query.from_user.id}"
    else:
        item = SCAN_PACKS.get(key)
        if not item:
            await query.edit_message_text("❌ Invalid pack selected.")
            return
        title = f"{item['scans']} Scan Pack"
        description = f"One-time purchase of {item['scans']} scans"
        price = item["price_stars"]
        payload = f"pack:{key}:{query.from_user.id}"

    if price == 0:
        await query.edit_message_text("❌ This item is free.")
        return

    await query.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=STARS_PROVIDER_TOKEN,
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label=title, amount=price)],
    )


async def _send_crypto_options(query):
    """Show crypto payment options."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    # Generate unique payment ID
    payment_id = str(uuid.uuid4())[:8]

    keyboard = [
        [InlineKeyboardButton("ETH (Ethereum)", callback_data=f"crypto_eth_{payment_id}")],
        [InlineKeyboardButton("SOL (Solana)", callback_data=f"crypto_sol_{payment_id}")],
    ]

    await query.edit_message_text(
        "💳 <b>Crypto Payment</b>\n\n"
        "Choose your network:\n\n"
        "⚠️ You'll be given a payment address. "
        "Scans are credited after confirmation.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_pre_checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle Telegram pre-checkout query."""
    await update.pre_checkout_query.answer(ok=True)


async def handle_successful_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle successful Telegram Stars payment."""
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    user_id = update.effective_user.id

    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{BACKEND_URL}/api/v1/telegram/payment/confirm",
                json={
                    "telegram_id": user_id,
                    "payload": payload,
                    "amount": payment.total_amount,
                    "currency": payment.currency,
                    "provider": "telegram_stars",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            )
    except Exception as e:
        logger.error(f"Payment confirmation failed: {e}")

    if payload.startswith("tier:"):
        tier = payload.split(":")[1]
        await update.message.reply_text(
            f"🎉 <b>Payment Successful!</b>\n\n"
            f"✅ You are now on the <b>{tier.upper()}</b> plan.\n\n"
            f"Use /status to check your scan balance.",
            parse_mode="HTML",
        )
    elif payload.startswith("pack:"):
        scans = payload.split(":")[1]
        await update.message.reply_text(
            f"🎉 <b>Payment Successful!</b>\n\n"
            f"✅ Added scans to your account.\n\n"
            f"Use /status to check your balance.",
            parse_mode="HTML",
        )
