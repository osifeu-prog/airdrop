"""
בוט SLH Airdrop המלא עם כל הפונקציות
"""

import os
import logging
import requests
import time
import threading
from datetime import datetime

# הגדרות
TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
API_URL = os.getenv("API_URL", "https://web-production-f1352.up.railway.app")
ADMIN_ID = "224223270"
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SLHFullBot:
    def __init__(self):
        self.offset = 0
        self.user_states = {}
        self.session = requests.Session()
        self.session.timeout = 30
        
    def send_message(self, chat_id, text):
        """שולח הודעה לטלגרם"""
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                logger.info(f"✅ נשלחה הודעה ל-{chat_id}")
                return True
            else:
                logger.error(f"❌ שגיאה בשליחת הודעה: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"🚨 שגיאת רשת: {e}")
            return False
    
    def call_api(self, endpoint, data=None, method='GET'):
        """קורא ל-API שלנו"""
        url = f"{API_URL}{endpoint}"
        
        try:
            if method == 'POST' and data:
                response = self.session.post(url, data=data)
            elif method == 'GET' and data:
                response = self.session.get(url, params=data)
            else:
                response = self.session.get(url)
            
            logger.info(f"🌐 API {endpoint}: {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    return response.json()
                except:
                    return {"status": "success", "message": "OK"}
            else:
                logger.error(f"❌ API שגיאה: {response.text}")
                return None
        except Exception as e:
            logger.error(f"🚨 API שגיאת חיבור: {e}")
            return None
    
    def handle_start(self, chat_id, name, username):
        """טיפול בפקודת /start"""
        logger.info(f"👤 משתמש התחיל: {name} (@{username})")
        
        # שלח הודעת ברוכים הבאים
        welcome_msg = f"""
🎉 <b>ברוך הבא ל-SLH Airdrop System!</b>

👤 <b>משתמש:</b> {name}
🆔 <b>Username:</b> @{username}

💰 <b>מבצע השקה:</b>
1,000 טוקני SLH = 44.4 ₪ בלבד!

🚀 <b>שלח את ה-username שלך כדי להתחיל:</b>
(לדוגמה: {username})
"""
        self.send_message(chat_id, welcome_msg)
        
        # רשם משתמש ב-API
        user_data = {
            'telegram_id': str(chat_id),
            'username': username,
            'first_name': name
        }
        
        result = self.call_api('/api/register', user_data, 'POST')
        if result:
            logger.info(f"✅ נרשם משתמש: {result}")
        
        # שמור מצב
        self.user_states[chat_id] = {
            'state': 'awaiting_username',
            'name': name,
            'username': username
        }
        
        return True
    
    def handle_username(self, chat_id, text):
        """טיפול בקבלת username"""
        if chat_id not in self.user_states:
            return False
        
        username = text.strip().replace('@', '')
        
        if len(username) < 3:
            self.send_message(chat_id, "❌ <b>שם משתמש קצר מדי</b>\n\nאנא שלח username תקין (לפחות 3 תווים).")
            return False
        
        # עדכן username
        user_data = {
            'telegram_id': str(chat_id),
            'username': username,
            'first_name': self.user_states[chat_id]['name']
        }
        
        self.call_api('/api/register', user_data, 'POST')
        
        # שלח הוראות תשלום
        payment_msg = f"""
💸 <b>הוראות תשלום</b>

🏦 <b>ארנק TON שלנו:</b>
<code>{TON_WALLET}</code>

📋 <b>שלבי התשלום:</b>
1. שלח <b>44.4 TON</b> לכתובת למעלה
2. שמור את מספר העסקה (Transaction Hash)
3. שלח את מספר העסקה לכאן
4. קבל 1,000 טוקני SLH!

⚠️ <b>חשוב:</b>
• שלח בדיוק 44.4 TON
• זמן אספקה: עד 24 שעות
• תמיכה: @Osif83
"""
        self.send_message(chat_id, payment_msg)
        
        # עדכן מצב
        self.user_states[chat_id]['state'] = 'awaiting_payment'
        self.user_states[chat_id]['username'] = username
        
        return True
    
    def handle_transaction(self, chat_id, tx_hash):
        """טיפול בקבלת transaction hash"""
        if chat_id not in self.user_states:
            return False
        
        if len(tx_hash) < 30:
            self.send_message(chat_id, "❌ <b>מספר עסקה לא תקין</b>\n\nאנא שלח את מספר העסקה המלא (לפחות 30 תווים).")
            return False
        
        # שמור עסקה ב-API
        tx_data = {
            'telegram_id': str(chat_id),
            'transaction_hash': tx_hash,
            'amount': 44.4
        }
        
        result = self.call_api('/api/submit', tx_data, 'POST')
        
        if result and result.get('status') == 'success':
            # הודעה למשתמש
            success_msg = f"""
✅ <b>תשלום התקבל!</b>

👤 <b>משתמש:</b> {self.user_states[chat_id]['name']}
📝 <b>עסקה:</b> {tx_hash[:20]}...
💰 <b>סכום:</b> 44.4 TON
🎁 <b>טוקנים:</b> 1,000 SLH
⏳ <b>סטטוס:</b> ממתין לאישור
🕐 <b>זמן אספקה:</b> עד 24 שעות

📊 <b>למעקב:</b> שלח /status
"""
            self.send_message(chat_id, success_msg)
            
            # התראה למנהל
            if str(chat_id) != ADMIN_ID:
                admin_msg = f"""
💰 <b>תשלום חדש!</b>

👤 משתמש: {self.user_states[chat_id]['name']}
📱 מזהה: {chat_id}
📝 עסקה: {tx_hash[:20]}...
💰 סכום: 44.4 TON
🕐 זמן: {time.strftime('%H:%M:%S')}

🌐 פאנל: {API_URL}/admin/dashboard?admin_key=airdrop_admin_2026
"""
                self.send_message(int(ADMIN_ID), admin_msg)
            
            self.user_states[chat_id]['state'] = 'completed'
            return True
        else:
            self.send_message(chat_id, "❌ <b>שגיאה בשמירת העסקה</b>\n\nנסה שוב או פנה לתמיכה: @Osif83")
            return False
    
    def get_updates(self):
        """מקבל עדכונים מטלגרם"""
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {'offset': self.offset, 'timeout': 30}
        
        try:
            response = self.session.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ שגיאה בקבלת עדכונים: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"🚨 שגיאת רשת בקבלת עדכונים: {e}")
            return None
    
    def run(self):
        """הרצת הבוט הראשית"""
        logger.info("=" * 50)
        logger.info("🤖 SLH Airdrop Bot - גרסה מלאה")
        logger.info(f"👤 מנהל: {ADMIN_ID}")
        logger.info(f"🌐 API: {API_URL}")
        logger.info("=" * 50)
        
        # בדיקת חיבור ראשונית
        try:
            response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=10)
            if response.status_code == 200 and response.json().get('ok'):
                bot_info = response.json()['result']
                logger.info(f"✅ בוט מחובר: @{bot_info['username']}")
            else:
                logger.error("❌ לא ניתן להתחבר לבוט טלגרם")
                return
        except Exception as e:
            logger.error(f"❌ שגיאת חיבור לטלגרם: {e}")
            return
        
        # בדוק חיבור ל-API
        try:
            response = requests.get(f"{API_URL}/health", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ API מחובר: {response.json().get('status')}")
            else:
                logger.error(f"❌ API לא זמין: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ שגיאת חיבור ל-API: {e}")
        
        # לולאה ראשית
        while True:
            try:
                data = self.get_updates()
                
                if data and data.get('ok'):
                    for update in data['result']:
                        self.offset = update['update_id'] + 1
                        
                        if 'message' in update:
                            msg = update['message']
                            chat_id = msg['chat']['id']
                            text = msg.get('text', '').strip()
                            name = msg['chat'].get('first_name', 'משתמש')
                            username = msg['chat'].get('username', '')
                            
                            logger.info(f"📨 {name}: {text}")
                            
                            # פקודות מיוחדות
                            if text == '/start':
                                self.handle_start(chat_id, name, username)
                            
                            elif text == '/status':
                                result = self.call_api(f'/api/user/{chat_id}')
                                if result and result.get('status') == 'success':
                                    user = result['user']
                                    status_msg = f"""
📊 <b>סטטוס אישי</b>

👤 <b>משתמש:</b> {user['first_name']}
💰 <b>טוקנים:</b> {user['tokens']:,} SLH
💸 <b>שווי:</b> {user['tokens'] * 44.4 / 1000:,.1f} ₪
"""
                                    self.send_message(chat_id, status_msg)
                                else:
                                    self.send_message(chat_id, "📊 <b>עדיין לא רכשת טוקנים</b>\n\nשלח username להתחלה!")
                            
                            elif text == '/help':
                                help_msg = """
❓ <b>עזרה - SLH Airdrop Bot</b>

<b>פקודות:</b>
/start - התחלת מערכת
/status - בדיקת סטטוס
/help - הצגת עזרה זו

<b>תהליך רכישה:</b>
1. שלח username טלגרם
2. שלח 44.4 TON לארנק שלנו
3. שלח את מספר העסקה
4. קבל 1,000 טוקני SLH

<b>תמיכה:</b> @Osif83
"""
                                self.send_message(chat_id, help_msg)
                            
                            elif text == '/admin' and str(chat_id) == ADMIN_ID:
                                admin_msg = f"""
👑 <b>פאנל ניהול</b>

🌐 API: {API_URL}
📊 Dashboard: {API_URL}/admin/dashboard?admin_key=airdrop_admin_2026
❤️ Health: {API_URL}/health

<b>סטטיסטיקות:</b>
לחץ על הקישור למעלה לסטטיסטיקות מלאות.
"""
                                self.send_message(chat_id, admin_msg)
                            
                            elif text == '/wallet':
                                wallet_msg = f"""
🏦 <b>פרטי ארנק TON</b>

<code>{TON_WALLET}</code>

<b>הוראות:</b>
1. שלח בדיוק 44.4 TON
2. בתיאור: SLH-Airdrop
3. שלח את מספר העסקה לכאן

<b>חשוב:</b>
• שלח רק TON
• סכום מדויק: 44.4
• זמן אישור: עד 24 שעות
"""
                                self.send_message(chat_id, wallet_msg)
                            
                            else:
                                # בדוק מצב נוכחי
                                if chat_id in self.user_states:
                                    state = self.user_states[chat_id]['state']
                                    
                                    if state == 'awaiting_username':
                                        self.handle_username(chat_id, text)
                                    
                                    elif state == 'awaiting_payment':
                                        self.handle_transaction(chat_id, text)
                                    
                                    else:
                                        self.send_message(chat_id, "🤖 <b>ברוך הבא!</b>\n\nלחץ /start להתחיל תהליך רכישה.")
                                else:
                                    if text and not text.startswith('/'):
                                        self.send_message(chat_id, "🤖 <b>ברוך הבא!</b>\n\nלחץ /start להתחיל תהליך רכישה.")
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("👋 הבוט נעצר על ידי המשתמש")
                break
            except Exception as e:
                logger.error(f"🚨 שגיאה בלולאה ראשית: {e}")
                time.sleep(5)

def start_full_bot():
    """מתחיל את הבוט המלא"""
    bot = SLHFullBot()
    bot.run()

# הרץ את הבוט ב-thread נפרד אם מייבאים את המודול
if __name__ == "__main__":
    start_full_bot()
