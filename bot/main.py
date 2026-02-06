import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from bot.config import settings
from bot.handlers.admin import admin_panel, admin_set_price, admin_approve, admin_reject
from bot.handlers.airdrop import airdrop_request

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id if update.effective_chat else None
    user_id = update.effective_user.id if update.effective_user else None
    log.info("CMD /start chat_id=%s user_id=%s", chat_id, user_id)

    await update.message.reply_text(
        "✅ SLH Airdrop Bot is online.\n\n"
        "Commands:\n"
        "• /airdrop — request airdrop\n"
        "• /admin — admin panel\n"
        "• /price — set price (admin)\n"
        "• /approve — approve (admin)\n"
        "• /reject — reject (admin)\n"
    )


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Avoid silence: respond to unknown text
    text = update.effective_message.text if update.effective_message else None
    log.info("MSG chat_id=%s text=%s", update.effective_chat.id if update.effective_chat else None, text)
    await update.message.reply_text("לא זיהיתי פקודה. נסה /start או /airdrop")


def main() -> None:
    log.info("Starting bot via long polling")

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # user commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("airdrop", airdrop_request))

    # admin commands
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("price", admin_set_price))
    app.add_handler(CommandHandler("approve", admin_approve))
    app.add_handler(CommandHandler("reject", admin_reject))

    # fallback for plain messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
import os
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://airdrop.railway.internal:8080")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{BACKEND_URL}/api/v2/register", json={
                "telegram_id": str(user.id),
                "username": user.username or f"user_{user.id}"
            }, timeout=10.0)
        except Exception as e:
            logger.error(f"Reg failed: {e}")

    keyboard = [[InlineKeyboardButton("Check Balance 💰", callback_data='balance')],
                [InlineKeyboardButton("Airdrop Request 🚀", callback_data='tasks')]]
    await update.message.reply_text(f"Hi {user.first_name}! System Online ✅",
                                  reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'balance':
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                r = await client.get(f"{BACKEND_URL}/api/v1/wallet/balance", params={"telegram_id": query.from_user.id})
                if r.status_code == 200:
                    bal = r.json().get("balance", 0)
                    await query.edit_message_text(f"Your Balance: *{bal}*", parse_mode=ParseMode.MARKDOWN)
                else:
                    await query.edit_message_text("❌ Backend error.")
            except Exception:
                await query.edit_message_text("❌ Connection error.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.run_polling(drop_pending_updates=True)
