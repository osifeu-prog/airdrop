"""
בוט טלגרם שפועל בתוך ה-API של Railway
"""

import os
import threading
import time
import requests
import logging

# הגדרות
TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
API_URL = os.getenv("API_URL", "http://localhost:8000")

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
    
    def process_update(self, update):
        """מעבד עדכון מטלגרם"""
        if "message" not in update:
            return
            
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip()
        
        if text == "/start":
            welcome = "🤖 ברוך הבא ל-SLH Airdrop!\n\nשלח /help לעזרה"
            self.send_message(chat_id, welcome)
            
        elif text == "/help":
            help_text = """
🎯 *SLH Airdrop Bot - עזרה*

*פקודות:*
/start - התחלת מערכת
/help - הצגת עזרה זו
/status - בדיקת סטטוס

*תהליך רכישה:*
1. שלח username טלגרם
2. שלח 44.4 TON לארנק שלנו
3. שלח את מספר העסקה
4. קבל 1,000 טוקני SLH

*תמיכה:* @Osif83
"""
            self.send_message(chat_id, help_text)
            
        elif text == "/status":
            status = "📊 *סטטוס מערכת*\n\nהמערכת פעילה ומחכה להזמנות!"
            self.send_message(chat_id, status)
    
    def run(self):
        """מריץ את הבוט"""
        logger.info("🤖 Telegram Bot Worker started")
        
        while self.running:
            try:
                # קבל עדכונים מטלגרם
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
                logger.error(f"Error in bot worker: {e}")
                time.sleep(5)

# צור מופע של הבוט
bot_worker = TelegramBotWorker()

# התחל את הבוט ב-thread נפרד
def start_bot():
    bot_worker.run()

# הרץ את הבוט ב-background אם זה המודול הראשי
if __name__ == "__main__":
    start_bot()
