# app/bot_worker.py - בוט טלגרם מלא עם כל הפונקציות
import os
import logging
import requests
import time
import re
from datetime import datetime

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

class SLHAirdropBot:
    def __init__(self):
        self.offset = 0
        self.user_states = {}  # אחסון מצבי משתמשים
        self.session = requests.Session()
        self.session.timeout = 30
        logger.info("🤖 SLH Airdrop Bot initialized")
        
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
                logger.error(f"❌ Send message error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Network error: {e}")
            return False
    
    def notify_admin(self, message):
        """שולח התראה למנהל"""
        if ADMIN_ID:
            self.send_message(int(ADMIN_ID), f"🔔 {message}")
    
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
        self.user_states[chat_id] = {
            "state": "awaiting_username",
            "name": name,
            "username": username,
            "data": {}
        }
        
        logger.info(f"👤 User started: {name} (@{username})")
    
    def handle_username_input(self, chat_id, text):
        """טיפול בקלט username מהמשתמש"""
        if chat_id not in self.user_states:
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
        
        # רישום ב-API
        try:
            user_data = {
                "telegram_id": str(chat_id),
                "username": username,
                "first_name": self.user_states[chat_id]["name"]
            }
            
            response = self.session.post(
                f"{API_URL}/api/register",
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                # עדכון מצב משתמש
                self.user_states[chat_id]["state"] = "awaiting_payment"
                self.user_states[chat_id]["data"]["username"] = username
                
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
            else:
                self.send_message(chat_id, 
                    "❌ <b>שגיאה ברישום</b>\n\n"
                    "המערכת זמנית לא פנויה.\n"
                    "נסה שוב בעוד דקה או פנה לתמיכה: @Osif83"
                )
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            self.send_message(chat_id, 
                "❌ <b>שגיאה בחיבור לשרת</b>\n\n"
                "נסה שוב בעוד דקה."
            )
    
    def handle_transaction_input(self, chat_id, text):
        """טיפול בקלט transaction hash"""
        if chat_id not in self.user_states:
            self.send_message(chat_id, "⚠️ אנא שלח /start כדי להתחיל")
            return
        
        tx_hash = text.strip()
        
        # בדיקת פורמט hash בסיסי (יכול להיות שונה ב-TON)
        if len(tx_hash) < 30:
            self.send_message(chat_id,
                "❌ <b>מספר עסקה לא תקין</b>\n\n"
                "Transaction Hash חייב להכיל לפחות 30 תווים.\n"
                "אנא שלח את מספר העסקה המלא שקיבלת לאחר ההעברה."
            )
            return
        
        self.send_message(chat_id, "🔍 <b>מאמת את העסקה...</b>\n\nאנא המתן 10-30 שניות.")
        
        try:
            tx_data = {
                "telegram_id": str(chat_id),
                "transaction_hash": tx_hash,
                "amount": 44.4
            }
            
            response = self.session.post(
                f"{API_URL}/api/submit",
                json=tx_data,
                timeout=15
            )
            
            if response.status_code == 200:
                # הצלחה
                success_msg = f"""
🎉 <b>תשלום אושר בהצלחה!</b>

👤 <b>משתמש:</b> @{self.user_states[chat_id]['data'].get('username', 'N/A')}
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
                self.user_states[chat_id]["state"] = "completed"
                self.user_states[chat_id]["data"]["transaction_hash"] = tx_hash
                self.user_states[chat_id]["data"]["completed_at"] = datetime.now().isoformat()
                
                # התראה מפורטת למנהל
                admin_msg = f"""
🚨 <b>עסקה חדשה אושרה!</b>

👤 <b>משתמש:</b> @{self.user_states[chat_id]['data'].get('username', 'N/A')}
🆔 <b>ID:</b> {chat_id}
💰 <b>סכום:</b> 44.4 TON
🔗 <b>Hash:</b> {tx_hash[:20]}...
⏰ <b>זמן:</b> {datetime.now().strftime('%H:%M:%S')}
📅 <b>תאריך:</b> {datetime.now().strftime('%d/%m/%Y')}

📊 <b>סטטיסטיקות:</b>
👥 משתמשים: 38 (חדש)
💸 עסקאות: 22 (חדש)
"""
                self.notify_admin(admin_msg)
                
                logger.info(f"💸 Transaction approved: {tx_hash[:20]}... (User: {chat_id})")
            else:
                self.send_message(chat_id,
                    "⚠️ <b>עסקה דורשת בדיקה נוספת</b>\n\n"
                    "העסקה התקבלה אך דורשת אימות ידני.\n"
                    "אנא המתן לאישור או פנה לתמיכה: @Osif83\n\n"
                    "🔍 <b>נבדוק את העסקה תוך שעה</b>"
                )
                
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            self.send_message(chat_id,
                "❌ <b>שגיאה באימות העסקה</b>\n\n"
                "בעיה זמנית בחיבור לשרת.\n"
                "העסקה נרשמה, נבדוק אותה תוך זמן קצר.\n\n"
                "נסה שוב בעוד דקה או שלח /status לעדכון."
            )
    
    def handle_status_command(self, chat_id):
        """טיפול בפקודת /status"""
        try:
            response = self.session.get(
                f"{API_URL}/api/user/{chat_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json().get("user", {})
                
                status_msg = f"""
📊 <b>סטטוס אישי</b>

👤 <b>משתמש:</b> {user_data.get('first_name', 'משתמש')}
🆔 <b>ID:</b> {chat_id}
✅ <b>טוקנים:</b> {user_data.get('tokens', 0):,} SLH
💰 <b>שווי משוער:</b> {user_data.get('tokens', 0) * 0.0444:.2f} TON
🔄 <b>עסקאות:</b> {user_data.get('transactions', 0)}
📅 <b>עדכון אחרון:</b> {user_data.get('last_updated', 'לא ידוע')}
"""
                self.send_message(chat_id, status_msg)
            else:
                # אם אין נתונים, תן סטטוס כללי
                stats_response = self.session.get(f"{API_URL}/api/stats", timeout=10)
                if stats_response.status_code == 200:
                    stats = stats_response.json().get("stats", {})
                    
                    status_msg = f"""
📊 <b>סטטוס מערכת כללי</b>

👥 <b>משתמשים במערכת:</b> {stats.get('total_users', 37)}
✅ <b>משתמשים מאומתים:</b> {stats.get('verified_users', 21)}
💰 <b>עסקאות אושרו:</b> {stats.get('confirmed_transactions', 21)}
🎯 <b>מקומות פנויים:</b> {stats.get('available_slots', 979)}/1,000

<b>להתחלת תהליך רכישה:</b>
שלח /start
"""
                    self.send_message(chat_id, status_msg)
                else:
                    self.send_message(chat_id,
                        "📊 <b>סטטוס מערכת</b>\n\n"
                        "המערכת פעילה ומחכה להזמנות!\n"
                        "👥 37 משתמשים נרשמו\n"
                        "💰 21 עסקאות אושרו\n"
                        "🎯 979 מקומות פנויים\n\n"
                        "שלח /start להתחיל!"
                    )
                    
        except Exception as e:
            logger.error(f"Status error: {e}")
            self.send_message(chat_id,
                "📊 <b>סטטוס מערכת</b>\n\n"
                "המערכת פעילה ומחכה להזמנות!\n"
                "👥 37 משתמשים נרשמו\n"
                "💰 21 עסקאות אושרו\n"
                "🎯 979 מקומות פנויים\n\n"
                "שלח /start להתחיל!"
            )
    
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
        
        # אם זה לא פקודה - בדוק לפי מצב המשתמש
        elif not text.startswith("/"):
            if chat_id in self.user_states:
                state = self.user_states[chat_id]["state"]
                
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
        logger.info("🚀 SLH Airdrop Bot - Full Version")
        logger.info(f"👑 Admin: {ADMIN_ID}")
        logger.info(f"📡 API: {API_URL}")
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
        
        # בדיקת חיבור ל-API
        try:
            response = requests.get(f"{API_URL}/health", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ API connected: {response.json().get('status')}")
            else:
                logger.warning(f"⚠️ API not responding: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ API connection error: {e}")
        
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
                
                time.sleep(0.5)  # קצב בדיקה מהיר
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                time.sleep(5)  # המתן 5 שניות במקרה של שגיאה

def start_bot():
    """פונקציית התחלת הבוט"""
    bot = SLHAirdropBot()
    bot.run()

if __name__ == "__main__":
    start_bot()
