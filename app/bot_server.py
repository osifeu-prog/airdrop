# app/bot_server.py - שירות בוט עצמאי
import os
import logging
import requests
import time
import json
import re
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# הגדרות
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"

# נתונים מקומיים
DATA_FILE = Path("data/bot_data.json")

class TelegramBotServer:
    def __init__(self):
        self.offset = 0
        self.user_states = {}
        self.user_data = {}
        self.transactions = {}
        self.session = requests.Session()
        self.session.timeout = 30
        
        self.load_data()
        logger.info("🤖 Telegram Bot Server initialized")
    
    def load_data(self):
        """טען נתונים מקובץ"""
        try:
            if DATA_FILE.exists():
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_states = data.get('user_states', {})
                    self.user_data = data.get('user_data', {})
                    self.transactions = data.get('transactions', {})
                logger.info(f"📂 Loaded {len(self.user_data)} users, {len(self.transactions)} transactions")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        """שמור נתונים לקובץ"""
        try:
            DATA_FILE.parent.mkdir(exist_ok=True)
            data = {
                'user_states': self.user_states,
                'user_data': self.user_data,
                'transactions': self.transactions,
                'last_save': datetime.now().isoformat()
            }
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("💾 Data saved")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def send_message(self, chat_id, text):
        """שולח הודעה לטלגרם"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            response = self.session.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Send message error {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Network error: {e}")
            return False
    
    def handle_command(self, chat_id, text, first_name, username):
        """מטפל בפקודות"""
        chat_id_str = str(chat_id)
        
        if text == "/start":
            welcome_msg = f"""
🎯 <b>ברוך הבא ל-SLH Airdrop!</b>

👤 <b>משתמש:</b> {first_name}
🆔 <b>Username:</b> @{username if username else 'לא הוגדר'}

💰 <b>מבצע השקה:</b>
1,000 טוקני SLH = 44.4 TON בלבד!

<b>שלח את ה-username שלך כדי להתחיל:</b>
(לדוגמה: {username or 'your_username'})
"""
            self.send_message(chat_id, welcome_msg)
            self.user_states[chat_id_str] = {"state": "awaiting_username"}
            self.save_data()
        
        elif text == "/help":
            help_msg = """
🤖 <b>SLH Airdrop Bot - עזרה</b>

<b>פקודות:</b>
/start - התחלת תהליך רכישה
/help - הצגת עזרה זו
/status - בדיקת סטטוס אישי/מערכת
/wallet - הצגת פרטי ארנק

<b>תהליך רכישה:</b>
1. שלח username טלגרם
2. שלח 44.4 TON לארנק שלנו
3. שלח את Transaction Hash שקיבלת
4. קבל 1,000 טוקני SLH תוך 24 שעות

<b>תמיכה:</b> @Osif83
"""
            self.send_message(chat_id, help_msg)
        
        elif text == "/status":
            if chat_id_str in self.user_data:
                user = self.user_data[chat_id_str]
                status_msg = f"""
📊 <b>סטטוס אישי</b>

👤 <b>משתמש:</b> {user.get('name', 'משתמש')}
🆔 <b>Username:</b> @{user.get('username', 'N/A')}
✅ <b>טוקנים:</b> {user.get('tokens', 0):,} SLH
💰 <b>שווי:</b> {user.get('tokens', 0) * 0.0444:.2f} TON
"""
                self.send_message(chat_id, status_msg)
            else:
                stats_msg = f"""
📊 <b>סטטוס מערכת</b>

👥 <b>משתמשים:</b> {len(self.user_data)}
✅ <b>שילמו:</b> {len([u for u in self.user_data.values() if u.get('status') == 'paid'])}
💸 <b>עסקאות:</b> {len(self.transactions)}
🎯 <b>מקומות פנויים:</b> {1000 - len(self.transactions)}/1,000

<b>שלח /start להתחיל!</b>
"""
                self.send_message(chat_id, stats_msg)
        
        elif text == "/wallet":
            wallet_msg = f"""
💼 <b>פרטי ארנק TON</b>

<code>{TON_WALLET}</code>

<b>הוראות:</b>
1. שלח <b>בדיוק 44.4 TON</b>
2. לכתובת למעלה
3. שמור את Transaction Hash

<b>חשוב:</b>
• סכום מדויק: 44.4 TON
• זמן אספקה: עד 24 שעות
"""
            self.send_message(chat_id, wallet_msg)
        
        # פקודות מנהל
        elif text == "/admin" and chat_id_str == ADMIN_ID:
            admin_msg = f"""
👑 <b>פאנל מנהלים</b>

👥 משתמשים: {len(self.user_data)}
💸 עסקאות: {len(self.transactions)}
💰 TON שנאסף: {len(self.transactions) * 44.4}

<b>פקודות:</b>
/stats - סטטיסטיקות מפורטות
/users - רשימת משתמשים
/transactions - עסקאות אחרונות
"""
            self.send_message(chat_id, admin_msg)
        
        elif text == "/stats" and chat_id_str == ADMIN_ID:
            stats_msg = f"""
📊 <b>דוח סטטיסטיקות מנהל</b>

👥 <b>משתמשים:</b> {len(self.user_data)}
✅ <b>שילמו:</b> {len([u for u in self.user_data.values() if u.get('status') == 'paid'])}
💸 <b>עסקאות:</b> {len(self.transactions)}
💰 <b>TON שנאסף:</b> {len(self.transactions) * 44.4}
🎯 <b>התקדמות:</b> {(len(self.transactions) / 1000 * 100):.1f}%

<b>בוט:</b> פעיל
<b>אחסון:</b> JSON ({DATA_FILE})
<b>עדכון אחרון:</b> {datetime.now().strftime('%H:%M:%S')}
"""
            self.send_message(chat_id, stats_msg)
        
        # טיפול בטקסט רגיל (לא פקודה)
        elif not text.startswith("/"):
            if chat_id_str in self.user_states:
                state = self.user_states[chat_id_str]["state"]
                
                if state == "awaiting_username":
                    username = text.strip().replace('@', '')
                    if re.match(r'^[A-Za-z0-9_]{3,32}$', username):
                        self.user_data[chat_id_str] = {
                            "username": username,
                            "name": first_name,
                            "registered": datetime.now().isoformat(),
                            "tokens": 0,
                            "status": "pending"
                        }
                        
                        payment_msg = f"""
✅ <b>נרשמת בהצלחה!</b>

👤 <b>Username:</b> @{username}
🆔 <b>ID:</b> {chat_id}

💰 <b>שלח 44.4 TON לכתובת:</b>

<code>{TON_WALLET}</code>

📝 <b>אחרי התשלום, שלח את:</b>
Transaction Hash (מספר עסקה)
"""
                        self.send_message(chat_id, payment_msg)
                        self.user_states[chat_id_str]["state"] = "awaiting_payment"
                        self.save_data()
                    else:
                        self.send_message(chat_id, "❌ username לא תקין. נסה שוב.")
                
                elif state == "awaiting_payment":
                    if len(text) > 20:  # הנחה שזה hash
                        tx_id = f"{chat_id}_{int(time.time())}"
                        self.transactions[tx_id] = {
                            "user_id": chat_id_str,
                            "username": self.user_data.get(chat_id_str, {}).get("username", "unknown"),
                            "hash": text,
                            "amount": 44.4,
                            "status": "pending",
                            "submitted": datetime.now().isoformat()
                        }
                        
                        if chat_id_str in self.user_data:
                            self.user_data[chat_id_str]["tokens"] = 1000
                            self.user_data[chat_id_str]["status"] = "paid"
                        
                        success_msg = f"""
🎉 <b>תשלום התקבל!</b>

👤 <b>משתמש:</b> @{self.user_data.get(chat_id_str, {}).get('username', 'N/A')}
💰 <b>סכום:</b> 44.4 TON
✅ <b>טוקנים:</b> 1,000 SLH

🔄 <b>ישלחו תוך 24 שעות</b>

👥 <b>קבוצת קהילה:</b> @SLH_Community
"""
                        self.send_message(chat_id, success_msg)
                        self.user_states[chat_id_str]["state"] = "completed"
                        self.save_data()
                        
                        # התראה למנהל
                        if ADMIN_ID and chat_id_str != ADMIN_ID:
                            admin_msg = f"""
🚨 <b>עסקה חדשה!</b>

👤 משתמש: @{self.user_data.get(chat_id_str, {}).get('username', 'N/A')}
💰 סכום: 44.4 TON
🔗 Hash: {text[:20]}...
⏰ זמן: {datetime.now().strftime('%H:%M:%S')}
"""
                            self.send_message(int(ADMIN_ID), admin_msg)
            else:
                self.send_message(chat_id, "🤖 שלח /start כדי להתחיל!")
    
    def process_updates(self):
        """מעבד עדכונים מטלגרם"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {
            "offset": self.offset,
            "timeout": 30
        }
        
        try:
            response = self.session.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    for update in data["result"]:
                        self.offset = update["update_id"] + 1
                        
                        if "message" in update:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            text = msg.get("text", "").strip()
                            first_name = msg["chat"].get("first_name", "משתמש")
                            username = msg["chat"].get("username", "")
                            
                            logger.info(f"📩 {first_name}: {text}")
                            self.handle_command(chat_id, text, first_name, username)
            else:
                logger.error(f"Get updates error: {response.status_code}")
        except Exception as e:
            logger.error(f"Update error: {e}")
    
    def run(self):
        """הרצת שירות הבוט"""
        logger.info("=" * 50)
        logger.info("🚀 SLH Airdrop Telegram Bot Server")
        logger.info(f"👑 Admin: {ADMIN_ID}")
        logger.info("=" * 50)
        
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
        
        logger.info("🔄 Bot server running...")
        
        # לולאה ראשית
        while True:
            try:
                self.process_updates()
                
                # שמור נתונים כל 5 דקות
                if int(time.time()) % 300 == 0:
                    self.save_data()
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped")
                self.save_data()
                break
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                time.sleep(5)

def main():
    """הפעלת שירות הבוט"""
    server = TelegramBotServer()
    server.run()

if __name__ == "__main__":
    main()
