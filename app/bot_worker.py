"""
בוט טלגרם עם תמיכה ב-Postgres + Redis
"""

import os
import threading
import time
import requests
import logging
from app.database import SessionLocal, User, Transaction
from app.redis_client import redis_client

# הגדרות
TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
API_URL = os.getenv("API_URL", "https://web-production-f1352.up.railway.app")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBotWorker:
    def __init__(self):
        self.offset = 0
        self.running = True
        
    def send_message(self, chat_id, text):
        """שולח הודעה לטלגרם"""
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def register_user(self, chat_id, name, username):
        """רושם משתמש במסד נתונים"""
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.telegram_id == str(chat_id)).first()
            
            if not user:
                user = User(
                    telegram_id=str(chat_id),
                    username=username,
                    first_name=name
                )
                db.add(user)
                db.commit()
                logger.info(f"✅ נרשם משתמש חדש: {name} ({chat_id})")
            else:
                logger.info(f"ℹ️  משתמש קיים: {name} ({chat_id})")
            
            return user
            
        except Exception as e:
            logger.error(f"❌ שגיאה ברישום משתמש: {e}")
            return None
        finally:
            db.close()
    
    def process_update(self, update):
        """מעבד עדכון מטלגרם"""
        if "message" not in update:
            return
            
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip()
        name = msg["chat"].get("first_name", "משתמש")
        username = msg["chat"].get("username", "")
        
        logger.info(f"📨 {name}: {text}")
        
        if text == "/start":
            # רשום משתמש
            user = self.register_user(chat_id, name, username)
            
            if user:
                welcome = f"""
🤖 *ברוך הבא ל-SLH Airdrop!*

👤 *שם:* {name}
💰 *טוקנים:* {user.tokens:,} SLH
💸 *ערך:* {user.tokens * 44.4 / 1000:,.1f} ₪

*פקודות זמינות:*
/start - התחלה
/status - סטטוס אישי
/help - עזרה
/wallet - פרטי ארנק

*תהליך רכישה:*
1. שלח username
2. שלח 44.4 TON
3. שלח מספר עסקה
4. קבל 1,000 טוקני SLH
"""
                self.send_message(chat_id, welcome)
                
        elif text == "/status":
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == str(chat_id)).first()
                if user:
                    status_msg = f"""
📊 *סטטוס אישי*

👤 *משתמש:* {user.first_name}
💰 *טוקנים:* {user.tokens:,} SLH
💸 *ערך:* {user.tokens * 44.4 / 1000:,.1f} ₪
📅 *נרשם:* {user.created_at.strftime('%d/%m/%Y')}
"""
                    self.send_message(chat_id, status_msg)
                else:
                    self.send_message(chat_id, "⚠️ *אינך רשום במערכת*\n\nשלח /start כדי להירשם")
            finally:
                db.close()
                
        elif text == "/help":
            help_text = """
🎯 *SLH Airdrop Bot - עזרה*

*פקודות:*
/start - התחלת מערכת
/help - הצגת עזרה זו
/status - בדיקת סטטוס
/wallet - פרטי ארנק

*תהליך רכישה:*
1. שלח username טלגרם
2. שלח 44.4 TON לארנק שלנו
3. שלח את מספר העסקה
4. קבל 1,000 טוקני SLH

*תמיכה:* @Osif83
"""
            self.send_message(chat_id, help_text)
            
        elif text == "/wallet":
            wallet_info = """
🏦 *פרטי ארנק TON*

🔗 *כתובת:*
`UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp`

*הוראות תשלום:*
1. שלח *בדיוק* 44.4 TON לכתובת למעלה
2. בתיאור כתוב: SLH-Airdrop
3. שמור את מספר העסקה
4. שלח את מספר העסקה לכאן

⚠️ *חשוב:*
• שלח רק TON
• סכום מדויק: 44.4
• זמן אישור: עד 24 שעות
"""
            self.send_message(chat_id, wallet_info)
    
    def run(self):
        """מריץ את הבוט"""
        logger.info("🤖 Telegram Bot Worker עם Postgres + Redis התחיל")
        
        while self.running:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
                params = {"offset": self.offset, "timeout": 30}
                
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("ok") and data.get("result"):
                        for update in data["result"]:
                            self.offset = update["update_id"] + 1
                            self.process_update(update)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ שגיאה בבוט: {e}")
                time.sleep(5)

# צור מופע של הבוט
bot_worker = TelegramBotWorker()

def start_bot():
    bot_worker.run()

if __name__ == "__main__":
    start_bot()
