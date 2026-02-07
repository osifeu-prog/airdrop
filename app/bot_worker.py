# app/bot_worker.py - בוט טלגרם עצמאי
import os
import logging
import requests
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# הגדרות
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
API_URL = os.getenv("API_URL", "https://web-production-f1352.up.railway.app")
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"

class SimpleTelegramBot:
    def __init__(self):
        self.offset = 0
        self.user_data = {}
        logger.info("🤖 Simple Telegram Bot initialized")
        
    def send_message(self, chat_id, text):
        """שולח הודעה לטלגרם"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Message sent to {chat_id}")
                return True
            else:
                logger.error(f"❌ Send message error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Network error: {e}")
            return False
    
    def process_update(self, update):
        """מעבד עדכון מטלגרם"""
        if "message" not in update:
            return
            
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        first_name = message["chat"].get("first_name", "משתמש")
        username = message["chat"].get("username", "")
        
        logger.info(f"📩 {first_name}: {text}")
        
        # פקודת /start
        if text == "/start":
            welcome_msg = f"""
🎯 <b>ברוך הבא ל-SLH Airdrop!</b>

👤 <b>משתמש:</b> {first_name}
🆔 <b>Username:</b> @{username}

💰 <b>מבצע מיוחד:</b>
1,000 טוקני SLH = 44.4 TON בלבד!

<b>שלח את ה-username שלך כדי להתחיל:</b>
(לדוגמה: {username or "your_username"})
"""
            self.send_message(chat_id, welcome_msg)
            self.user_data[chat_id] = {"state": "awaiting_username"}
        
        # פקודת /help
        elif text == "/help":
            help_msg = """
ℹ️ <b>עזרה - SLH Airdrop Bot</b>

<b>פקודות:</b>
/start - התחל תהליך רכישה
/status - בדוק סטטוס
/help - הצג עזרה זו
/wallet - הצג פרטי ארנק

<b>תהליך רכישה:</b>
1. שלח username טלגרם
2. שלח 44.4 TON לארנק שלנו
3. שלח את hash העסקה
4. קבל 1,000 טוקני SLH

<b>תמיכה:</b> @Osif83
"""
            self.send_message(chat_id, help_msg)
        
        # פקודת /status
        elif text == "/status":
            status_msg = f"""
📊 <b>סטטוס SLH Airdrop</b>

👥 <b>משתתפים:</b> 37
💰 <b>עסקאות:</b> 21
🎯 <b>מקומות פנויים:</b> 979 מתוך 1,000

🔄 <b>מערכת:</b> פעילה
📡 <b>API:</b> {API_URL}
"""
            self.send_message(chat_id, status_msg)
        
        # פקודת /wallet
        elif text == "/wallet":
            wallet_msg = f"""
💼 <b>פרטי ארנק TON</b>

<code>{TON_WALLET}</code>

<b>הוראות:</b>
1. שלח בדיוק <b>44.4 TON</b>
2. שלח לכתובת למעלה
3. שמור את hash העסקה
4. שלח את hash לכאן

<b>חשוב:</b>
• שלח רק TON
• סכום מדויק: 44.4
• זמן אספקה: עד 24 שעות
"""
            self.send_message(chat_id, wallet_msg)
        
        # קבלת username
        elif chat_id in self.user_data and self.user_data[chat_id]["state"] == "awaiting_username":
            if text and not text.startswith("/"):
                # רישום ב-API
                try:
                    reg_data = {
                        "telegram_id": str(chat_id),
                        "username": text.replace("@", ""),
                        "first_name": first_name
                    }
                    
                    response = requests.post(
                        f"{API_URL}/api/register",
                        json=reg_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # שלח הוראות תשלום
                        payment_msg = f"""
✅ <b>נרשמת בהצלחה!</b>

👤 <b>Username:</b> {text}
🆔 <b>ID:</b> {chat_id}

💰 <b>שלח 44.4 TON לכתובת:</b>
<code>{TON_WALLET}</code>

📝 <b>לאחר התשלום, שלח את:</b>
Transaction Hash (מספר עסקה)
"""
                        self.send_message(chat_id, payment_msg)
                        self.user_data[chat_id]["state"] = "awaiting_payment"
                        self.user_data[chat_id]["username"] = text
                    else:
                        self.send_message(chat_id, "❌ שגיאה ברישום. אנא נסה שוב.")
                        
                except Exception as e:
                    logger.error(f"Registration error: {e}")
                    self.send_message(chat_id, "❌ שגיאה בחיבור לשרת.")
        
        # קבלת transaction hash
        elif chat_id in self.user_data and self.user_data[chat_id]["state"] == "awaiting_payment":
            if len(text) > 20:  # הנחה שזה hash
                try:
                    tx_data = {
                        "telegram_id": str(chat_id),
                        "transaction_hash": text,
                        "amount": 44.4
                    }
                    
                    response = requests.post(
                        f"{API_URL}/api/submit",
                        json=tx_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        success_msg = f"""
🎉 <b>תשלום התקבל!</b>

👤 <b>משתמש:</b> {self.user_data[chat_id].get('username', 'N/A')}
💰 <b>סכום:</b> 44.4 TON
🔄 <b>סטטוס:</b> ממתין לאישור

⏰ <b>טוקנים יישלחו תוך 24 שעות</b>

👥 <b>הצטרף לקבוצה:</b> @SLH_Group
"""
                        self.send_message(chat_id, success_msg)
                        
                        # התראה למנהל
                        admin_msg = f"""
🚨 <b>עסקה חדשה!</b>

👤 משתמש: {self.user_data[chat_id].get('username', 'N/A')}
🆔 ID: {chat_id}
💰 סכום: 44.4 TON
🔗 Hash: {text[:20]}...
⏰ זמן: {datetime.now().strftime('%H:%M:%S')}
"""
                        self.send_message(int(ADMIN_ID), admin_msg)
                        
                        self.user_data[chat_id]["state"] = "completed"
                    else:
                        self.send_message(chat_id, "❌ שגיאה בשמירת העסקה.")
                        
                except Exception as e:
                    logger.error(f"Transaction error: {e}")
                    self.send_message(chat_id, "❒ שגיאה בחיבור לשרת.")
        
        # הודעה כללית
        elif text and not text.startswith("/"):
            default_msg = """
🤖 <b>SLH Airdrop Bot</b>

לחץ /start כדי להתחיל תהליך רכישה
או /help לעזרה
"""
            self.send_message(chat_id, default_msg)
    
    def get_updates(self):
        """מקבל עדכונים מטלגרם"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {
            "offset": self.offset,
            "timeout": 30
        }
        
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Get updates error: {e}")
            return None
    
    def run(self):
        """הרצת הבוט"""
        logger.info("🚀 Starting Simple Telegram Bot...")
        
        # בדיקת חיבור
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe",
                timeout=10
            )
            if response.status_code == 200 and response.json().get("ok"):
                bot_name = response.json()["result"]["username"]
                logger.info(f"✅ Bot connected: @{bot_name}")
            else:
                logger.error("❌ Bot connection failed")
                return
        except Exception as e:
            logger.error(f"❌ Bot test error: {e}")
            return
        
        # לולאה ראשית
        while True:
            try:
                updates = self.get_updates()
                
                if updates and updates.get("ok"):
                    for update in updates["result"]:
                        self.offset = update["update_id"] + 1
                        self.process_update(update)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                time.sleep(5)

# הרצת הבוט
if __name__ == "__main__":
    bot = SimpleTelegramBot()
    bot.run()
