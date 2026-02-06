#!/usr/bin/env python3
# Telegram Bot for Airdrop - FIXED VERSION
import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
API_URL = os.getenv("API_URL", "https://successful-fulfillment-production.up.railway.app")
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"
PRICE = "44.4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    user = update.effective_user
    
    # Try to register user
    try:
        register_data = {
            "telegram_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        response = requests.post(f"{API_URL}/api/v1/users/register", json=register_data, timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ User {user.id} registered")
    except Exception as e:
        logger.warning(f"⚠️ Registration failed (but continuing): {e}")
    
    welcome_text = f"""👋 שלום {user.first_name}!
ברוך הבא ל-Airdrop Bot! 🚀

🎯 פרויקט Airdrop פעיל!
💰 מחיר: {PRICE} ₪ (בטון)

📋 הפקודות הזמינות:
/start - הצג הודעה זו
/airdrop - בקשת airdrop
/balance - בדיקת יתרה
/help - עזרה

💳 ארנק TON לתשלום:
{TON_WALLET}"""
    
    await update.message.reply_text(welcome_text)

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request airdrop"""
    user = update.effective_user
    await update.message.reply_text("🔄 מכין בקשת airdrop עבורך...")
    
    try:
        # Request airdrop from API
        airdrop_data = {
            "user_id": user.id,
            "amount": 1.0
        }
        response = requests.post(f"{API_URL}/api/v1/airdrop/request", json=airdrop_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            payment_text = f"""💰 **בקשת Airdrop**

🎫 מזהה עסקה: {data.get('transaction_id', 'N/A')}
💸 סכום לתשלום: {data.get('price_ils', PRICE)} ₪ (TON)
🏦 ארנק: {data.get('ton_wallet', TON_WALLET)}

📱 קישור תשלום: {data.get('payment_url', '')}
📸 קוד QR: {data.get('qr_code', '')}

💾 שמור את מספר העסקה
📞 דווח על התשלום למפתח"""
            
            await update.message.reply_text(payment_text)
            
            # Send QR code if available
            if data.get('qr_code'):
                await update.message.reply_photo(data['qr_code'])
        else:
            raise Exception(f"API returned {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Airdrop request failed: {e}")
        # Fallback to direct payment info
        payment_text = f"""💰 **בקשת Airdrop**

💸 סכום לתשלום: {PRICE} ₪ (TON)
🏦 ארנק: {TON_WALLET}

📱 שלח את התשלום לארנק למעלה
💾 שמור את מספר העסקה
📞 דווח על התשלום למפתח"""
        
        await update.message.reply_text(payment_text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check balance"""
    user = update.effective_user
    
    try:
        response = requests.get(f"{API_URL}/api/v1/users/{user.id}/balance", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            balance_text = f"""📊 **יתרה נוכחית**

👤 משתמש: {user.first_name}
💰 טוקנים: {data.get('balance_tokens', 0)} 
💎 TON: {data.get('balance_ton', 0)}
🎯 airdrops שהושלמו: {data.get('completed_airdrops', 0)}
⏳ ממתינים: {data.get('pending_airdrops', 0)}"""
            
            await update.message.reply_text(balance_text)
        else:
            raise Exception(f"API returned {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Balance check failed: {e}")
        await update.message.reply_text("📊 כרגע אין נתונים זמינים.\nהיתרה שלך תוצג כאן ברגע שתבצע רכישה ראשונה.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = f"""🆘 **עזרה והסברים**

1. /airdrop - בקשת airdrop חדש
   • תקבל קישור תשלום ב-TON
   • שלח תשלום לארנק שמופיע

2. /balance - בדיקת יתרת airdrops
   • צפה בכמה טוקנים יש לך

3. תהליך התשלום:
   • שלח TON לארנק: {TON_WALLET}
   • שמור את מספר העסקה
   • צור קשר עם המפתח לאישור

💡 טיפ: שמור תמיד את מספר העסקה!"""
    
    await update.message.reply_text(help_text)

def main():
    """Start the bot"""
    print(f"🚀 Starting Airdrop Bot v3.0...")
    print(f"🌐 API URL: {API_URL}")
    print(f"🤖 Bot Token: {TOKEN[:10]}...")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("airdrop", airdrop))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("help", help_command))
    
    # Start bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
