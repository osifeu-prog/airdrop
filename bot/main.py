import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# הגדרת logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# פקודות בסיסיות
async def start(update: Update, context: CallbackContext):
    """שליחת הודעת ברוכים הבאים"""
    user = update.effective_user
    await update.message.reply_html(
        f"👋 שלום {user.mention_html()}!\n"
        f"ברוך הבא ל-Airdrop Bot!\n\n"
        f"📋 **הפקודות הזמינות:**\n"
        f"/start - הצג הודעה זו\n"
        f"/airdrop - בקשת airdrop\n"
        f"/balance - בדיקת יתרה\n"
        f"/help - עזרה"
    )
    logger.info(f"User {user.id} started the bot")

async def help_command(update: Update, context: CallbackContext):
    """שליחת הודעת עזרה"""
    await update.message.reply_text(
        "🆘 **עזרה והסברים**\n\n"
        "1. /airdrop - בקשת אאירדרופ חדש\n"
        "2. /balance - בדיקת יתרת אאירדרופים\n"
        "3. תמיכה טכנית: @YourSupportChannel"
    )

async def airdrop_request(update: Update, context: CallbackContext):
    """בקשת airdrop"""
    await update.message.reply_text(
        "🎁 **בקשת Airdrop**\n\n"
        "מחיר: 44.4 ₪ (בטון)\n"
        "כמות: 1000 טוקנים\n\n"
        "התשלום יתבצע באמצעות ארנק TON.\n"
        "הקישור לתשלום יישלח כאן בעוד רגע..."
    )

async def check_balance(update: Update, context: CallbackContext):
    """בדיקת יתרה"""
    await update.message.reply_text(
        "💰 **מצב יתרה**\n\n"
        "כרגע המערכת בבנייה.\n"
        "היתרה שלך תוצג כאן ברגע שתבצע רכישה ראשונה."
    )

async def echo(update: Update, context: CallbackContext):
    """הדפסת הודעות טקסט רגילות"""
    await update.message.reply_text(
        f"📝 קבלתי את ההודעה: {update.message.text}\n"
        f"השתמש בפקודות מהתפריט."
    )

def main():
    """הפעלת הבוט"""
    # קבלת הטוקן ממשתני הסביבה
    TOKEN = os.getenv('TELEGRAM_TOKEN', '8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls')
    
    if not TOKEN:
        logger.error("טוקן לא נמצא! הגדר את TELEGRAM_TOKEN")
        return
    
    # יצירת האפליקציה
    application = Application.builder().token(TOKEN).build()
    
    # רישום handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("airdrop", airdrop_request))
    application.add_handler(CommandHandler("balance", check_balance))
    
    # handler להודעות טקסט רגילות
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # הרצת הבוט ב-long polling
    logger.info("בוט מתחיל לרוץ...")
    print("🤖 Telegram Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
