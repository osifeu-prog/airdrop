import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# הגדרת logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# הגדרת כתובת ה-API
API_URL = os.getenv("API_URL", "https://successful-fulfillment-production.up.railway.app")

async def start(update: Update, context: CallbackContext):
    """שליחת הודעת ברוכים הבאים"""
    user = update.effective_user
    
    # רישום המשתמש ב-API
    try:
        user_data = {
            "telegram_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        
        response = requests.post(f"{API_URL}/api/v1/users/register", json=user_data)
        
        if response.status_code == 200:
            reg_data = response.json()
            logger.info(f"User {user.id} registered: {reg_data}")
    except Exception as e:
        logger.error(f"Failed to register user: {e}")
    
    await update.message.reply_html(
        f"👋 שלום <b>{user.first_name}</b>!\n"
        f"ברוך הבא ל-Airdrop Bot! 🚀\n\n"
        f"🎯 <b>פרויקט Airdrop פעיל!</b>\n"
        f"💰 מחיר: 44.4 ₪ (בטון)\n\n"
        f"📋 <b>הפקודות הזמינות:</b>\n"
        f"/start - הצג הודעה זו\n"
        f"/airdrop - בקשת airdrop\n"
        f"/balance - בדיקת יתרה\n"
        f"/help - עזרה\n\n"
        f"💳 <b>ארנק TON לתשלום:</b>\n"
        f"<code>UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp</code>"
    )

async def airdrop_request(update: Update, context: CallbackContext):
    """בקשת airdrop"""
    user = update.effective_user
    
    await update.message.reply_text(
        "🔄 מכין בקשת airdrop עבורך..."
    )
    
    try:
        # שליחת בקשה ל-API
        request_data = {
            "user_id": user.id,
            "amount": 1.0
        }
        
        response = requests.post(f"{API_URL}/api/v1/airdrop/request", json=request_data)
        
        if response.status_code == 200:
            airdrop_data = response.json()
            
            # הצגת פרטי התשלום
            message = (
                f"🎁 <b>בקשת Airdrop הוכנה!</b>\n\n"
                f"💰 <b>מחיר:</b> {airdrop_data['price_ils']} ₪ (טון)\n"
                f"🔢 <b>מספר עסקה:</b> {airdrop_data['transaction_id']}\n"
                f"⏰ <b>תוקף:</b> שעה\n\n"
                f"💳 <b>ארנק TON לתשלום:</b>\n"
                f"<code>{airdrop_data['ton_wallet']}</code>\n\n"
                f"📱 <b>לחץ לשלם:</b>\n"
                f"{airdrop_data['payment_url']}\n\n"
                f"📋 <b>לאחר התשלום:</b>\n"
                f"השלם וצור קשר עם המפתח לאישור."
            )
            
            await update.message.reply_html(message)
            
            # שלח גם QR code אם יש
            if 'qr_code' in airdrop_data:
                await update.message.reply_photo(airdrop_data['qr_code'])
                
        else:
            await update.message.reply_text(
                "❌ אירעה שגיאה בהכנת הבקשה. נסה שוב מאוחר יותר."
            )
            
    except Exception as e:
        logger.error(f"Airdrop request failed: {e}")
        await update.message.reply_text(
            "❌ לא ניתן להתחבר לשרת. נסה שוב מאוחר יותר."
        )

async def check_balance(update: Update, context: CallbackContext):
    """בדיקת יתרה"""
    user = update.effective_user
    
    try:
        response = requests.get(f"{API_URL}/api/v1/users/{user.id}/balance")
        
        if response.status_code == 200:
            balance_data = response.json()
            
            message = (
                f"💰 <b>מצב יתרה</b>\n\n"
                f"👤 <b>משתמש:</b> {user.first_name}\n"
                f"🆔 <b>ID:</b> {user.id}\n\n"
                f"🎯 <b>טוקנים:</b> {balance_data['balance_tokens']}\n"
                f"🔄 <b>Airdrops ממתינים:</b> {balance_data['pending_airdrops']}\n"
                f"✅ <b>Airdrops שהושלמו:</b> {balance_data['completed_airdrops']}\n\n"
                f"💵 <b>סכום שהוצא:</b>\n"
                f"{balance_data['total_spent_ton']} TON\n"
                f"({balance_data['total_spent_ils']} ₪)"
            )
            
            await update.message.reply_html(message)
        else:
            await update.message.reply_text(
                "📊 יתרה נוכחית: 0 טוקנים\n"
                "המערכת עדיין בבנייה. היתרה תוצג לאחר הרכישה הראשונה."
            )
            
    except Exception as e:
        logger.error(f"Balance check failed: {e}")
        await update.message.reply_text(
            "📊 כרגע אין נתונים זמינים.\n"
            "היתרה שלך תוצג כאן ברגע שתבצע רכישה ראשונה."
        )

async def help_command(update: Update, context: CallbackContext):
    """שליחת הודעת עזרה"""
    await update.message.reply_html(
        "🆘 <b>עזרה והסברים</b>\n\n"
        "1. <b>/airdrop</b> - בקשת airdrop חדש\n"
        "   • תקבל קישור תשלום ב-TON\n"
        "   • שלח תשלום לארנק שמופיע\n\n"
        "2. <b>/balance</b> - בדיקת יתרת airdrops\n"
        "   • צפה בכמה טוקנים יש לך\n\n"
        "3. <b>תהליך התשלום:</b>\n"
        "   • שלח TON לארנק שמופיע\n"
        "   • שמור את מספר העסקה\n"
        "   • צור קשר עם המפתח לאישור\n\n"
        "💡 <b>טיפ:</b> שמור תמיד את מספר העסקה!"
    )

async def echo(update: Update, context: CallbackContext):
    """טיפול בהודעות טקסט רגילות"""
    await update.message.reply_text(
        "🤖 הבוט מבין רק פקודות!\n"
        "נסה אחת מהפקודות הבאות:\n"
        "/start - לתפריט הראשי\n"
        "/help - להסברים מפורטים"
    )

def main():
    """הפעלת הבוט"""
    TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
    
    if not TOKEN:
        logger.error("טוקן לא נמצא!")
        return
    
    logger.info(f"מתחיל בוט מתקדם...")
    logger.info(f"API URL: {API_URL}")
    
    application = Application.builder().token(TOKEN).build()
    
    # רישום handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("airdrop", airdrop_request))
    application.add_handler(CommandHandler("balance", check_balance))
    application.add_handler(CommandHandler("airdrop_request", airdrop_request))  # שם נוסף
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    logger.info("בוט מתחיל לרוץ בפולינג...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
