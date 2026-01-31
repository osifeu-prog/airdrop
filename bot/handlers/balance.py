import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{settings.BACKEND_URL}/api/v1/wallet/balance", params={"telegram_id": user.id})
    if r.status_code != 200:
        await update.message.reply_text(f"Failed: {r.status_code} {r.text}")
        return
    bal = r.json()["balance"]
    await update.message.reply_text(f"Balance: {bal}")
