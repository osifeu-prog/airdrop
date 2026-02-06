import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Admin commands:\n/price <value>\n/approve <request_id>\n/reject <request_id>\n""")

async def admin_set_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /admin_set_price <price>")
        return
    price = context.args[0]
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{settings.BACKEND_URL}/api/v1/token/price",
            headers={"X-Admin-Secret": settings.ADMIN_SECRET},
            json={"price": price},
        )
    await update.message.reply_text(f"{r.status_code}: {r.text}")

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /admin_approve <airdrop_id>")
        return
    airdrop_id = int(context.args[0])
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{settings.BACKEND_URL}/api/v1/airdrop/approve",
            headers={"X-Admin-Secret": settings.ADMIN_SECRET},
            json={"airdrop_id": airdrop_id},
        )
    await update.message.reply_text(f"{r.status_code}: {r.text}")

async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /admin_reject <airdrop_id>")
        return
    airdrop_id = int(context.args[0])
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{settings.BACKEND_URL}/api/v1/airdrop/reject",
            headers={"X-Admin-Secret": settings.ADMIN_SECRET},
            json={"airdrop_id": airdrop_id},
        )
    await update.message.reply_text(f"{r.status_code}: {r.text}")
