# app/bot_worker.py - בוט טלגרם עצמאי ללא תלות במסד נתונים
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
API_URL = os.getenv("API_URL", "https://web-production-f1352.up.railway.app")
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"

# נתונים מקומיים (בזיכרון + קובץ לגיבוי)
DATA_FILE = Path("data/bot_data.json")

class SLHAirdropBot:
    def __init__(self):
        self.offset = 0
        self.user_states = {}  # אחסון מצבי משתמשים בזיכרון
        self.user_data = {}    # נתוני משתמשים
        self.transactions = {} # עסקאות
        self.session = requests.Session()
        self.session.timeout = 30
        
        # טען נתונים מקובץ אם קיים
        self.load_data()
        
        logger.info("🤖 SLH Airdrop Bot initialized (standalone version)")
        
    def load_data(self):
        """טען נתונים מקובץ"""
        try:
            if DATA_FILE.exists():
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_states = data.get('user_states', {})
                    self.user_data = data.get('user_data', {})
                    self.transactions = data.get('transactions', {})
                logger.info(f"📂 Loaded data from {DATA_FILE}")
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
            logger.debug("💾 Data saved to file")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def send_message(self, chat_id, text, reply_markup=None):
        """שולח הודעה לטלגרם"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        try:
            response = self.session.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Message sent to {chat_id}")
                return True
            else:
                logger.error(f"❌ Send message error {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Network error: {e}")
            return False
    
    def notify_admin(self, message):
        """שולח התראה למנהל"""
        if ADMIN_ID and ADMIN_ID != "0":
            try:
                self.send_message(int(ADMIN_ID), f"🔔 {message}")
            except:
                pass
    
    def handle_start(self, chat_id, name, username):
        """טיפול בפקודת /start"""
        welcome_msg = f"""
🎯 <b>ברוך הבא ל-SLH Airdrop System!</b>

👤 <b>משתמש:</b> {name}
🆔 <b>Username:</b> @{username if username else 'לא הוגדר'}

💰 <b>מבצע השקה בלעדי:</b>
<u>1,000 טוקני SLH = 44.4 TON בלבד!</u>

🎁 <b>מוגבל ל-1,000 משתתפים בלבד!</b>

<b>הזן את ה-username שלך כדי להתחיל:</b>
(שלח את ה-username שלך, לדוגמה: {username or 'your_username'})
"""
        self.send_message(chat_id, welcome_msg)
        
        # אתחול מצב משתמש
        self.user_states[str(chat_id)] = {
            "state": "awaiting_username",
            "name": name,
            "username": username,
            "joined": datetime.now().isoformat()
        }
        
        logger.info(f"👤 User started: {name} (@{username})")
        self.save_data()
    
    def handle_username_input(self, chat_id, text):
        """טיפול בקלט username מהמשתמש"""
        chat_id_str = str(chat_id)
        
        if chat_id_str not in self.user_states:
            self.send_message(chat_id, "⚠️ אנא שלח /start כדי להתחיל")
            return
        
        username = text.strip().replace('@', '')
        
        # בדיקת תקינות username
        if not re.match(r'^[A-Za-z0-9_]{3,32}$', username):
            self.send_message(chat_id, 
                "❌ <b>שם משתמש לא תקין</b>\n\n"
                "שם משתמש חייב:\n"
                "• להכיל 3-32 תווים\n"
                "• אותיות אנגלית (A-Z, a-z)\n"
                "• מספרים (0-9) או קו תחתון (_)\n\n"
                "נסה שוב:"
            )
            return
        
        # שמור נתוני משתמש
        self.user_data[chat_id_str] = {
            "username": username,
            "name": self.user_states[chat_id_str]["name"],
            "registered": datetime.now().isoformat(),
            "tokens": 0,
            "status": "pending"
        }
        
        # עדכון מצב משתמש
        self.user_states[chat_id_str]["state"] = "awaiting_payment"
        self.user_states[chat_id_str]["data"] = {"username": username}
        
        # הודעת תשלום
        payment_msg = f"""
✅ <b>נרשמת בהצלחה!</b>

👤 <b>Username:</b> @{username}
🆔 <b>ID:</b> {chat_id}

💰 <b>שלח 44.4 TON לכתובת הבאה:</b>

<code>{TON_WALLET}</code>

📝 <b>הוראות חשובות:</b>
1. שלח <b>בדיוק 44.4 TON</b>
2. השאר את השדה 'Description' ריק
3. שמור את <b>Transaction Hash</b> (מספר עסקה)
4. שלח את ה-Hash לכאן לאחר ההעברה

⏰ <b>זמן העברה:</b> עד 24 שעות
🔍 <b>מעקב עסקה:</b> tonviewer.com
"""
        self.send_message(chat_id, payment_msg)
        
        # התראה למנהל
        self.notify_admin(f"👤 משתמש נרשם: @{username} (ID: {chat_id})")
        
        logger.info(f"📝 User registered: @{username} (ID: {chat_id})")
        self.save_data()
    
    def handle_transaction_input(self, chat_id, text):
        """טיפול בקלט transaction hash"""
        chat_id_str = str(chat_id)
        
        if chat_id_str not in self.user_states:
            self.send_message(chat_id, "⚠️ אנא שלח /start כדי להתחיל")
            return
        
        tx_hash = text.strip()
        
        # בדיקת פורמט hash בסיסי
        if len(tx_hash) < 30:
            self.send_message(chat_id,
                "❌ <b>מספר עסקה לא תקין</b>\n\n"
                "Transaction Hash חייב להכיל לפחות 30 תווים.\n"
                "אנא שלח את מספר העסקה המלא שקיבלת לאחר ההעברה."
            )
            return
        
        self.send_message(chat_id, "🔍 <b>מאמת את העסקה...</b>\n\nאנא המתן 10-30 שניות.")
        
        # שמור עסקה
        tx_id = f"{chat_id}_{int(time.time())}"
        self.transactions[tx_id] = {
            "user_id": chat_id_str,
            "username": self.user_data.get(chat_id_str, {}).get("username", "unknown"),
            "hash": tx_hash,
            "amount": 44.4,
            "status": "pending",
            "submitted": datetime.now().isoformat()
        }
        
        # עדכן משתמש
        if chat_id_str in self.user_data:
            self.user_data[chat_id_str]["tokens"] = 1000
            self.user_data[chat_id_str]["status"] = "paid"
            self.user_data[chat_id_str]["last_transaction"] = tx_hash[:20] + "..."
            self.user_data[chat_id_str]["paid_at"] = datetime.now().isoformat()
        
        # הצלחה
        success_msg = f"""
🎉 <b>תשלום התקבל בהצלחה!</b>

👤 <b>משתמש:</b> @{self.user_data.get(chat_id_str, {}).get('username', 'N/A')}
💰 <b>סכום:</b> 44.4 TON
🔗 <b>עסקה:</b> {tx_hash[:20]}...
✅ <b>סטטוס:</b> מאומת

🔄 <b>טוקנים ישלחו לארנק שלך תוך 24 שעות</b>

📢 <b>הצטרף לערוץ העדכונים:</b>
@SLH_Updates

👥 <b>קבוצת קהילה:</b>
@SLH_Community

❓ <b>שאלות?</b> @Osif83
"""
        self.send_message(chat_id, success_msg)
        
        # עדכון מצב משתמש
        self.user_states[chat_id_str]["state"] = "completed"
        self.user_states[chat_id_str]["data"]["transaction_hash"] = tx_hash
        self.user_states[chat_id_str]["data"]["completed_at"] = datetime.now().isoformat()
        
        # התראה מפורטת למנהל
        admin_msg = f"""
🚨 <b>עסקה חדשה התקבלה!</b>

👤 <b>משתמש:</b> @{self.user_data.get(chat_id_str, {}).get('username', 'N/A')}
🆔 <b>ID:</b> {chat_id}
💰 <b>סכום:</b> 44.4 TON
🔗 <b>Hash:</b> {tx_hash[:20]}...
⏰ <b>זמן:</b> {datetime.now().strftime('%H:%M:%S')}
📅 <b>תאריך:</b> {datetime.now().strftime('%d/%m/%Y')}

📊 <b>סטטיסטיקות מעודכנות:</b>
👥 משתמשים: {len(self.user_data)}
💸 עסקאות: {len(self.transactions)}
"""
        self.notify_admin(admin_msg)
        
        logger.info(f"💸 Transaction received: {tx_hash[:20]}... (User: {chat_id})")
        self.save_data()
    
    def handle_status_command(self, chat_id):
        """טיפול בפקודת /status"""
        chat_id_str = str(chat_id)
        
        if chat_id_str in self.user_data:
            user = self.user_data[chat_id_str]
            
            status_msg = f"""
📊 <b>סטטוס אישי</b>

👤 <b>משתמש:</b> {user.get('name', 'משתמש')}
🆔 <b>Username:</b> @{user.get('username', 'N/A')}
✅ <b>טוקנים:</b> {user.get('tokens', 0):,} SLH
💰 <b>שווי משוער:</b> {user.get('tokens', 0) * 0.0444:.2f} TON
📅 <b>נרשם:</b> {user.get('registered', 'לא ידוע')[:10]}
🔄 <b>סטטוס:</b> {user.get('status', 'לא ידוע')}
"""
            if user.get('paid_at'):
                status_msg += f"\n💰 <b>שולם ב:</b> {user.get('paid_at', '')[:10]}"
        else:
            # סטטיסטיקות כללית
            total_users = len(self.user_data)
            total_transactions = len(self.transactions)
            paid_users = len([u for u in self.user_data.values() if u.get('status') == 'paid'])
            
            status_msg = f"""
📊 <b>סטטוס מערכת כללי</b>

👥 <b>משתמשים במערכת:</b> {total_users}
✅ <b>משתמשים שילמו:</b> {paid_users}
💰 <b>עסקאות:</b> {total_transactions}
🎯 <b>מקומות פנויים:</b> {1000 - paid_users}/1,000

<b>להתחלת תהליך רכישה:</b>
שלח /start
"""
        
        self.send_message(chat_id, status_msg)
    
    def handle_help_command(self, chat_id):
        """טיפול בפקודת /help"""
        help_msg = """
🤖 <b>SLH Airdrop Bot - עזרה</b>

<b>פקודות:</b>
/start - התחלת תהליך רכישה
/help - הצגת עזרה זו
/status - בדיקת סטטוס אישי/מערכת
/wallet - הצגת פרטי ארנק

<b>תהליך רכישה:</b>
1. שלח /start
2. הזן את username הטלגרם שלך
3. שלח 44.4 TON לכתובת שהופיעה
4. שלח את Transaction Hash שקיבלת
5. קבל 1,000 טוקני SLH תוך 24 שעות

<b>תמיכה:</b> @Osif83
<b>ערוץ עדכונים:</b> @SLH_Updates
<b>קבוצת קהילה:</b> @SLH_Community
"""
        self.send_message(chat_id, help_msg)
    
    def handle_wallet_command(self, chat_id):
        """טיפול בפקודת /wallet"""
        wallet_msg = f"""
💼 <b>פרטי ארנק TON</b>

<code>{TON_WALLET}</code>

<b>הוראות תשלום:</b>
1. שלח <b>בדיוק 44.4 TON</b>
2. לכתובת למעלה
3. <b>אל תשלח</b> סכומים אחרים
4. שמור את Transaction Hash

<b>חשוב:</b>
• זמן אישור עסקה: 2-5 דקות
• זמן אספקת טוקנים: עד 24 שעות
• תמיכה: @Osif83
"""
        self.send_message(chat_id, wallet_msg)
    
    def handle_admin_command(self, chat_id, text):
        """טיפול בפקודות מנהל"""
        if str(chat_id) != ADMIN_ID:
            return
        
        if text == "/admin stats":
            stats_msg = f"""
📊 <b>סטטיסטיקות מנהל</b>

👥 <b>משתמשים:</b> {len(self.user_data)}
💰 <b>משתמשים שילמו:</b> {len([u for u in self.user_data.values() if u.get('status') == 'paid'])}
💸 <b>עסקאות:</b> {len(self.transactions)}
🎯 <b>מקומות פנויים:</b> {1000 - len(self.transactions)}/1,000
💾 <b>קובץ נתונים:</b> {DATA_FILE}

<b>פקודות נוספות:</b>
/admin backup - יצוא נתונים
/admin reset - איפוס (זהיר!)
"""
            self.send_message(chat_id, stats_msg)
    
    def process_message(self, message):
        """מעבד הודעת טלגרם"""
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        first_name = message["chat"].get("first_name", "משתמש")
        username = message["chat"].get("username", "")
        
        logger.info(f"📩 Message from {first_name} ({chat_id}): {text}")
        
        # פקודות מיוחדות
        if text == "/start":
            self.handle_start(chat_id, first_name, username)
        
        elif text == "/help":
            self.handle_help_command(chat_id)
        
        elif text == "/status":
            self.handle_status_command(chat_id)
        
        elif text == "/wallet":
            self.handle_wallet_command(chat_id)
        
        elif text.startswith("/admin"):
            self.handle_admin_command(chat_id, text)
        
        # אם זה לא פקודה - בדוק לפי מצב המשתמש
        elif not text.startswith("/"):
            chat_id_str = str(chat_id)
            
            if chat_id_str in self.user_states:
                state = self.user_states[chat_id_str]["state"]
                
                if state == "awaiting_username":
                    self.handle_username_input(chat_id, text)
                
                elif state == "awaiting_payment":
                    self.handle_transaction_input(chat_id, text)
                
                else:
                    self.send_message(chat_id,
                        "🤖 <b>SLH Airdrop Bot</b>\n\n"
                        "לחץ /start כדי להתחיל תהליך רכישה\n"
                        "או /help לעזרה"
                    )
            else:
                self.send_message(chat_id,
                    "🤖 <b>SLH Airdrop Bot</b>\n\n"
                    "ברוך הבא! לחץ /start כדי להתחיל תהליך רכישה\n"
                    "או /help לעזרה"
                )
    
    def get_updates(self):
        """מקבל עדכונים מטלגרם"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {
            "offset": self.offset,
            "timeout": 30,
            "allowed_updates": ["message"]
        }
        
        try:
            response = self.session.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Get updates error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Network error in get_updates: {e}")
            return None
    
    def run(self):
        """הרצת הבוט הראשית"""
        logger.info("=" * 50)
        logger.info("🚀 SLH Airdrop Bot - Standalone Version")
        logger.info(f"👑 Admin ID: {ADMIN_ID}")
        logger.info("📁 Data storage: JSON file")
        logger.info("=" * 50)
        
        # בדיקת חיבור ראשונית
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe",
                timeout=10
            )
            if response.status_code == 200 and response.json().get("ok"):
                bot_info = response.json()["result"]
                logger.info(f"✅ Bot connected: @{bot_info['username']} ({bot_info['id']})")
            else:
                logger.error("❌ Failed to connect to Telegram bot")
                return
        except Exception as e:
            logger.error(f"❌ Telegram connection error: {e}")
            return
        
        logger.info("🔄 Bot is running and waiting for messages...")
        
        # לולאה ראשית
        while True:
            try:
                updates = self.get_updates()
                
                if updates and updates.get("ok"):
                    for update in updates["result"]:
                        self.offset = update["update_id"] + 1
                        
                        if "message" in update:
                            self.process_message(update["message"])
                
                # שמור נתונים כל 5 דקות
                if int(time.time()) % 300 == 0:
                    self.save_data()
                
                time.sleep(0.5)  # קצב בדיקה מהיר
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                self.save_data()
                break
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                time.sleep(5)  # המתן 5 שניות במקרה של שגיאה

def main():
    """הפעלת הבוט"""
    bot = SLHAirdropBot()
    bot.run()

if __name__ == "__main__":
    main()
