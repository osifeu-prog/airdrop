import logging
import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings

LOG = logging.getLogger("bot")

async def airdrop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    await update.message.reply_text("Send: /airdrop <amount>  (example: /airdrop 10)")

async def airdrop_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /airdrop <amount>")
        return
    amount = args[0]
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{settings.BACKEND_URL}/api/v1/airdrop/request",
            params={"telegram_id": user.id},
            json={"amount": amount},
        )
    if r.status_code != 200:
        await update.message.reply_text(f"Failed: {r.status_code} {r.text}")
        return
    data = r.json()
    await update.message.reply_text(f"""Airdrop requested ✅\nAmount: {amount}\n""")