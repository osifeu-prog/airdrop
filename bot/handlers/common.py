import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

LOG = logging.getLogger("bot.common")

def _webapp_button(url: str):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Open WebApp", web_app=WebAppInfo(url=url))
    ]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    LOG.info("cmd=/start from=%s", update.effective_user.id if update.effective_user else None)
    await update.message.reply_text(
        "Welcome! Use /menu to see options."
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base = (context.bot_data.get("WEBAPP_URL") or "http://127.0.0.1:8000/webapp/index.html")
    await update.message.reply_text(
        "Menu:\n• /airdrop\n• /balance\n• Open WebApp:",
        reply_markup=_webapp_button(base)
    )