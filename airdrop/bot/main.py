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
