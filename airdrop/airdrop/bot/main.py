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