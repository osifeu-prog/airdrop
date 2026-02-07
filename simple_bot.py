#!/usr/bin/env python3
"""
SLH Airdrop Bot - גרסה פשוטה ומוצלחת
"""

import logging
import requests
import time
import sys
import io
from datetime import datetime

# ====================
# CONFIGURATION
# ====================
TOKEN = "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls"
API_URL = "http://localhost:8000"
ADMIN_ID = "7757102350"
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"

# ====================
# SETUP UTF-8
# ====================
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ====================
# LOGGING
# ====================
logging.basicConfig(
    format='%(asctime)s - SLH BOT - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ====================
# EMOJI HELPER
# ====================
def e(name):
    """פונקציית עזר לאימוג'ים"""
    emojis = {
        "rocket": "🚀",
        "money": "💰",
        "coin": "🪙",
        "user": "👤",
        "check": "✅",
        "cross": "❌",
        "warning": "⚠️",
        "gift": "🎁",
        "chart": "📈",
        "link": "🔗",
        "credit": "💳",
        "bank": "🏦",
        "phone": "📱",
        "fire": "🔥",
        "star": "⭐",
        "trophy": "🏆",
        "medal": "🥇",
        "bulb": "💡",
        "gear": "⚙️",
        "bell": "🔔",
        "inbox": "📥",
        "calendar": "📅",
        "clock": "⏰"
    }
    return emojis.get(name, "")

# ====================
# API FUNCTIONS
# ====================
def call_api(endpoint, method="GET", data=None):
    """קורא ל-API"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return None
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"API Connection Error: {e}")
        return None

def send_telegram_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    """שולח הודעה לטלגרם"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram Send Error: {e}")
        return False

def create_keyboard(buttons, resize=True, one_time=False):
    """יוצר מקלדת טלגרם"""
    return {
        "keyboard": buttons,
        "resize_keyboard": resize,
        "one_time_keyboard": one_time
    }

# ====================
# MESSAGE TEMPLATES
# ====================
def welcome_message(user_name, username=""):
    """הודעת ברוך הבא"""
    return f"""
{e('rocket')} <b>ברוך הבא ל-SLH Airdrop System!</b>

{e('star')} <b>המערכת המתקדמת להשקעה בקריפטו</b>

{e('user')} <b>משתמש:</b> {user_name}
{e('link')} <b>Username:</b> @{username if username else 'לא צוין'}

{e('gift')} <b>🎁 מבצע השקה:</b>
• 1,000 טוקני SLH = 44.4 ₪
• קבלה אוטומטית תוך 24 שעות
• תמיכה טכנית 24/7

<b>{e('bulb')} לחץ על הכפתור למטה להתחיל!</b>
"""

def main_menu_message():
    """מסך תפריט ראשי"""
    return f"""
{e('crown')} <b>תפריט ראשי - SLH Airdrop</b>

{e('coin')} <b>אפשרויות זמינות:</b>

1. {e('money')} <b>קניית טוקנים</b> - רכישת 1,000 טוקני SLH
2. {e('chart')} <b>סטטוס אישי</b> - צפייה במאזן
3. {e('gift')} <b>מערכת בונוסים</b> - קבלת בונוסים
4. {e('link')} <b>קישור הפניה</b> - הזמנת חברים
5. {e('trophy')} <b>טבלת מובילים</b> - רשימת מובילים
6. {e('info')} <b>מידע והסברים</b> - כל הפרטים

<b>{e('bulb')} בחר אפשרות מהתפריט:</b>
"""

def payment_instructions(username, chat_id):
    """הוראות תשלום"""
    return f"""
{e('check')} <b>שם משתמש אושר!</b>

{e('user')} <b>Username:</b> @{username}
{e('credit')} <b>מזהה:</b> {chat_id}
{e('calendar')} <b>תאריך:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

{e('money')} <b>השלב הבא - תשלום:</b>

<b>שלב 1:</b> העתק את כתובת הארנק:
<code>{TON_WALLET}</code>

<b>שלב 2:</b> פתח את אפליקציית TON שלך

<b>שלב 3:</b> שלח בדיוק <b>44.4 TON</b>

<b>שלב 4:</b> בתיאור כתוב:
<code>Airdrop-{chat_id}</code>

<b>שלב 5:</b> שמור את מספר העסקה

<b>שלב 6:</b> שלח את מספר העסקה לכאן

{e('warning')} <b>⚠️ חשוב:</b>
• שלח בדיוק 44.4 TON
• הוסף את התיאור
• שמור את מספר העסקה

<b>{e('phone')} שאלות?</b> @Osif83
"""

# ====================
# BOT HANDLERS
# ====================
class SimpleBot:
    def __init__(self):
        self.user_states = {}
    
    def handle_start(self, chat_id, user_name, username=""):
        """מטפל ב-/start"""
        # רישום משתמש
        user_data = {
            "telegram_id": str(chat_id),
            "username": username if username else "",
            "first_name": user_name
        }
        
        api_response = call_api("/api/users/register", "POST", user_data)
        
        # שלח ברוך הבא
        send_telegram_message(chat_id, welcome_message(user_name, username))
        
        time.sleep(1)
        
        # מקלדת תפריט
        menu_keyboard = create_keyboard([
            [e('money') + " קניית טוקנים"],
            [e('chart') + " סטטוס אישי", e('gift') + " בונוסים"],
            [e('link') + " קישור הפניה", e('trophy') + " טבלת מובילים"],
            [e('info') + " מידע והסברים", e('gear') + " הגדרות"]
        ])
        
        send_telegram_message(chat_id, main_menu_message(), reply_markup=menu_keyboard)
        
        self.user_states[chat_id] = {"state": "main_menu"}
        
        if api_response and api_response.get("status") == "success":
            admin_msg = f"{e('bell')} משתמש חדש: {user_name} (@{username})"
            send_telegram_message(ADMIN_ID, admin_msg)
    
    def handle_menu(self, chat_id, text, user_name):
        """מטפל בבחירת תפריט"""
        if text == e('money') + " קניית טוקנים":
            self.user_states[chat_id] = {"state": "awaiting_username"}
            send_telegram_message(chat_id, 
                f"{e('info')} <b>שלב ראשון</b>\n\nשלח את שם המשתמש הטלגרם שלך (לדוגמה: @username)")
        
        elif text == e('chart') + " סטטוס אישי":
            self.show_status(chat_id, user_name)
        
        elif text == e('gift') + " בונוסים":
            send_telegram_message(chat_id, 
                f"{e('gift')} <b>מערכת בונוסים</b>\n\n• 50 טוקנים על כל חבר\n• 30 טוקנים על שיתוף\n• 10% בונוס ל-100 הראשונים")
        
        elif text == e('link') + " קישור הפניה":
            share_link = f"https://t.me/SLH_AIR_bot?start=SLH{chat_id}"
            send_telegram_message(chat_id, 
                f"{e('link')} <b>קישור הפניה שלך:</b>\n\n{share_link}\n\nהזמן חברים וקבל בונוסים!")
        
        elif text == e('trophy') + " טבלת מובילים":
            send_telegram_message(chat_id,
                f"{e('trophy')} <b>טבלת מובילים</b>\n\n1. @User1 - 15 הפניות\n2. @User2 - 12 הפניות\n3. @User3 - 8 הפניות")
        
        elif text == e('info') + " מידע והסברים":
            send_telegram_message(chat_id,
                f"{e('info')} <b>מידע על SLH</b>\n\nפרויקט בלוקצ'יין ישראלי לפלטפורמת מומחים.\nהטוקנים ייסחרו בבורסות ויאפשרו גישה לשירותים מתקדמים.")
        
        elif text == e('gear') + " הגדרות":
            send_telegram_message(chat_id,
                f"{e('gear')} <b>הגדרות</b>\n\nשפה: עברית\nמטבע: ILS\nהתראות: פעילות")
    
    def handle_username(self, chat_id, username, user_name):
        """מטפל בקבלת username"""
        username = username.replace('@', '').strip()
        
        if len(username) < 3:
            send_telegram_message(chat_id, f"{e('warning')} שם משתמש לא תקין. אנא שלח username תקין.")
            return False
        
        send_telegram_message(chat_id, payment_instructions(username, chat_id))
        self.user_states[chat_id]["state"] = "awaiting_payment"
        return True
    
    def handle_transaction(self, chat_id, tx_hash, user_name):
        """מטפל בעסקה"""
        if len(tx_hash) < 30:
            send_telegram_message(chat_id, f"{e('warning')} מספר עסקה לא תקין.")
            return False
        
        tx_data = {
            "telegram_id": str(chat_id),
            "transaction_hash": tx_hash,
            "amount": 44.4
        }
        
        api_response = call_api("/api/users/submit_transaction", "POST", tx_data)
        
        if api_response and api_response.get("status") == "success":
            send_telegram_message(chat_id,
                f"{e('fire')} <b>תשלום התקבל!</b>\n\nמספר עסקה: {tx_hash[:20]}...\nסטטוס: ממתין לאישור\nטוקנים: 1,000 SLH")
            
            admin_msg = f"{e('bell')} תשלום חדש!\nמשתמש: {user_name}\nעסקה: {tx_hash[:20]}...\nסכום: 44.4 TON"
            send_telegram_message(ADMIN_ID, admin_msg)
            
            self.user_states[chat_id]["state"] = "completed"
            return True
        else:
            send_telegram_message(chat_id, f"{e('cross')} שגיאה בשמירת העסקה. אנא נסה שוב.")
            return False
    
    def show_status(self, chat_id, user_name):
        """מציג סטטוס"""
        api_response = call_api(f"/api/users/{chat_id}/status")
        
        if api_response and "user" in api_response:
            user_data = api_response["user"]
            tokens = user_data.get("tokens", 0)
            value = tokens * 44.4 / 1000
            
            send_telegram_message(chat_id,
                f"{e('chart')} <b>סטטוס אישי</b>\n\nמשתמש: {user_name}\nטוקנים: {tokens:,} SLH\nשווי: {value:,.1f} ₪\nסטטוס: פעיל")
        else:
            send_telegram_message(chat_id,
                f"{e('info')} <b>סטטוס אישי</b>\n\nעדיין לא רכשת טוקנים. לחץ על 'קניית טוקנים' כדי להתחיל!")

# ====================
# MAIN BOT LOOP
# ====================
def main():
    """לולאת הבוט הראשית"""
    bot = SimpleBot()
    offset = 0
    
    logger.info(f"{e('rocket')} SLH Airdrop Bot מתחיל...")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "").strip()
                        user_name = msg["chat"].get("first_name", "משתמש")
                        username = msg["chat"].get("username", "")
                        
                        logger.info(f"הודעה מה-{user_name}: {text[:50]}")
                        
                        if text == "/start":
                            bot.handle_start(chat_id, user_name, username)
                        
                        elif text == "/status":
                            bot.show_status(chat_id, user_name)
                        
                        elif text == "/help":
                            send_telegram_message(chat_id, 
                                f"{e('info')} <b>עזרה</b>\n\n/start - התחל\n/status - סטטוס\n/wallet - ארנק\n/help - עזרה")
                        
                        elif text == "/wallet":
                            send_telegram_message(chat_id,
                                f"{e('bank')} <b>ארנק TON:</b>\n\n<code>{TON_WALLET}</code>\n\nשלח 44.4 TON לכתובת זו.")
                        
                        else:
                            state = bot.user_states.get(chat_id, {}).get("state", "main_menu")
                            
                            if state == "awaiting_username":
                                bot.handle_username(chat_id, text, user_name)
                            
                            elif state == "awaiting_payment":
                                if len(text) > 30:
                                    bot.handle_transaction(chat_id, text, user_name)
                                else:
                                    # בדוק אם זה בחירת תפריט
                                    for emoji in ["💰", "📈", "🎁", "🔗", "🏆", "ℹ️", "⚙️"]:
                                        if emoji in text:
                                            bot.handle_menu(chat_id, text, user_name)
                                            break
                                    else:
                                        send_telegram_message(chat_id,
                                            f"{e('warning')} שלח מספר עסקה או בחר מהתפריט.")
                            
                            else:
                                # בדוק אם זה בחירת תפריט
                                for emoji in ["💰", "📈", "🎁", "🔗", "🏆", "ℹ️", "⚙️"]:
                                    if emoji in text:
                                        bot.handle_menu(chat_id, text, user_name)
                                        break
                                else:
                                    # החזר לתפריט
                                    menu_keyboard = create_keyboard([
                                        [e('money') + " קניית טוקנים"],
                                        [e('chart') + " סטטוס אישי", e('gift') + " בונוסים"],
                                        [e('link') + " קישור הפניה", e('trophy') + " טבלת מובילים"],
                                        [e('info') + " מידע והסברים", e('gear') + " הגדרות"]
                                    ])
                                    send_telegram_message(chat_id, main_menu_message(), reply_markup=menu_keyboard)
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"שגיאה: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
