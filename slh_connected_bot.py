#!/usr/bin/env python3
"""
SLH Airdrop Bot - מחובר ל-API המלא
"""

import logging
import requests
import time
from datetime import datetime

# ====================
# CONFIGURATION
# ====================
TOKEN = "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls"
API_URL = "https://successful-fulfillment-production.up.railway.app"
ADMIN_ID = "7757102350"  # החלף עם ה-ID שלך

# ====================
# LOGGING
# ====================
logging.basicConfig(
    format='%(asctime)s - SLH BOT - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

def send_telegram_message(chat_id, text, parse_mode="HTML"):
    """שולח הודעה לטלגרם"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram Send Error: {e}")
        return False

# ====================
# BOT HANDLERS
# ====================
def handle_start(chat_id, user_name, username=""):
    """מטפל ב-/start"""
    # רישום משתמש ב-API
    user_data = {
        "telegram_id": str(chat_id),
        "username": username if username else "",
        "first_name": user_name
    }
    
    api_response = call_api("/api/users/register", "POST", user_data)
    
    message = f"""
🎉 <b>ברוך הבא ל-SLH Airdrop Bot!</b>

<b>מערכת רכישת טוקנים אוטומטית</b>

👤 <b>משתמש:</b> {user_name}
🆔 <b>Username:</b> @{username if username else 'לא צוין'}
📅 <b>תאריך:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

💰 <b>פרטים:</b>
• 1,000 טוקני SLH = 44.4 ₪
• קבלה אוטומטית תוך 24 שעות
• תמיכה מלאה בעברית

📋 <b>תהליך הרכישה:</b>
1. שלח username טלגרם
2. שלח 44.4 TON לארנק שלנו
3. שלח את מספר העסקה
4. קבל 1,000 טוקני SLH

<b>השלב הראשון:</b>
<b>שלח או אשר את שם המשתמש הטלגרם שלך</b>

(לדוגמה: @Osif83)
"""
    
    send_telegram_message(chat_id, message)
    
    # שלח התראה למנהל
    if api_response and api_response.get("status") == "success":
        admin_msg = f"👤 משתמש חדש: {user_name} (@{username})"
        send_telegram_message(ADMIN_ID, admin_msg)

def handle_username(chat_id, username, user_name):
    """מטפל בקבלת username"""
    username = username.replace('@', '').strip()
    
    if len(username) < 3:
        send_telegram_message(chat_id, "❌ <b>שם משתמש לא תקין.</b>\n\nאנא שלח username תקין (לפחות 3 תווים).")
        return False
    
    # הודעה על אישור
    message = f"""
✅ <b>שם משתמש התקבל!</b>

👤 <b>Username:</b> @{username}
👥 <b>שם:</b> {user_name}
🆔 <b>מזהה:</b> {chat_id}
📅 <b>נרשם:</b> {datetime.now().strftime('%H:%M')}

💰 <b>השלב הבא - תשלום:</b>

1. <b>שלח 44.4 TON</b> לארנק שלנו:
<code>UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp</code>

2. <b>שמור את מספר העסקה</b> (Transaction Hash)

3. <b>שלח את מספר העסקה</b> לכאן

4. <b>קבל אוטומטית 1,000 טוקני SLH</b>

⚠️ <b>חשוב:</b>
• שלח <b>בדיוק 44.4 TON</b>
• שמור את מספר העסקה!
• זמן אספקה: עד 24 שעות

<b>יש שאלות?</b> פנה ל-@Osif83
"""
    
    send_telegram_message(chat_id, message)
    return True

def handle_transaction(chat_id, tx_hash, user_name):
    """מטפל בשליחת transaction hash"""
    # שמירת העסקה ב-API
    tx_data = {
        "telegram_id": str(chat_id),
        "transaction_hash": tx_hash,
        "amount": 44.4,
        "currency": "TON"
    }
    
    api_response = call_api("/api/users/submit_transaction", "POST", tx_data)
    
    if api_response and api_response.get("status") == "success":
        message = f"""
🎉 <b>תשלום התקבל!</b>

<b>פרטי עסקה:</b>
👤 <b>משתמש:</b> {user_name}
🆔 <b>מזהה:</b> {chat_id}
🔗 <b>מספר עסקה:</b> 
<code>{tx_hash[:40]}...</code>
💰 <b>סכום:</b> 44.4 TON
🎁 <b>טוקנים:</b> 1,000 SLH

⏳ <b>סטטוס:</b> באישור
🕐 <b>זמן אספקה:</b> עד 24 שעות

📊 <b>למעקב:</b> שלח /status
📞 <b>תמיכה:</b> @Osif83

<b>תודה על ההשתתפות במערכת SLH!</b>
"""
        
        # התראה למנהל
        admin_msg = f"""
🚨 תשלום חדש!
משתמש: {user_name}
ID: {chat_id}
TX: {tx_hash[:20]}...
סכום: 44.4 TON
זמן: {datetime.now().strftime('%H:%M:%S')}
"""
        send_telegram_message(ADMIN_ID, admin_msg)
        
    else:
        message = """
❌ <b>שגיאה בשמירת העסקה</b>

אנא נסה שוב או פנה לתמיכה: @Osif83
"""
    
    send_telegram_message(chat_id, message)
    return True

def handle_status(chat_id, user_name):
    """מטפל ב-/status"""
    # קבלת נתונים מה-API
    api_response = call_api(f"/api/users/{chat_id}/status")
    
    if api_response:
        user_data = api_response.get("user", {})
        transactions = api_response.get("transactions", [])
        
        total_tokens = user_data.get("total_tokens", 0)
        pending_tx = len([t for t in transactions if t.get("status") == "pending"])
        
        message = f"""
📊 <b>סטטוס אישי - SLH Tokens</b>

👤 <b>משתמש:</b> {user_name}
🆔 <b>מזהה:</b> {chat_id}
💰 <b>טוקנים:</b> {total_tokens:,} SLH
💸 <b>ערך:</b> {total_tokens * 44.4 / 1000:.1f} ₪
⏳ <b>בהמתנה:</b> {pending_tx} עסקאות

<b>קישורים רלוונטיים:</b>
• אתר: https://slhisrael.com/
• דשבורד: https://web-production-112f6.up.railway.app/investors/
• טלגרם: @Osifs_Factory_bot

<b>יש שאלות?</b> @Osif83
"""
    else:
        message = f"""
📊 <b>סטטוס אישי</b>

👤 <b>משתמש:</b> {user_name}
🆔 <b>מזהה:</b> {chat_id}
💰 <b>טוקנים:</b> 0 SLH
💸 <b>ערך:</b> 0 ₪

<i>עדיין לא רכשת טוקנים. שלח /start כדי להתחיל!</i>
"""
    
    send_telegram_message(chat_id, message)

# ====================
# MAIN BOT LOOP
# ====================
def main():
    """לולאת הבוט הראשית"""
    logger.info("🚀 SLH Airdrop Bot מתחיל...")
    
    offset = 0
    user_states = {}  # {chat_id: "awaiting_username", "awaiting_transaction"}
    
    while True:
        try:
            # קבל עדכונים מטלגרם
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
                        
                        logger.info(f"📨 מה-{user_name}: {text[:50]}")
                        
                        # אתחל state אם לא קיים
                        if chat_id not in user_states:
                            user_states[chat_id] = {
                                "name": user_name,
                                "username": username,
                                "state": "start"
                            }
                        
                        # טיפול בפקודות
                        if text == "/start":
                            user_states[chat_id]["state"] = "awaiting_username"
                            handle_start(chat_id, user_name, username)
                        
                        elif text == "/status":
                            handle_status(chat_id, user_name)
                        
                        elif text == "/stats":
                            api_response = call_api("/api/stats")
                            if api_response:
                                stats = api_response.get("stats", {})
                                message = f"""
📈 <b>סטטיסטיקות מערכת</b>

👥 משתמשים: {stats.get('total_users', 0)}
💰 עסקאות: {stats.get('total_transactions', 0)}
🎯 TON שנאסף: {stats.get('total_ton_received', 0)}
🪙 טוקנים שחולקו: {stats.get('total_tokens', 0)}
"""
                                send_telegram_message(chat_id, message)
                        
                        else:
                            # טיפול לפי state
                            state = user_states[chat_id]["state"]
                            
                            if state == "awaiting_username":
                                if handle_username(chat_id, text, user_name):
                                    user_states[chat_id]["state"] = "awaiting_transaction"
                                    user_states[chat_id]["provided_username"] = text.replace('@', '')
                            
                            elif state == "awaiting_transaction":
                                # אם זה hash עסקה (ארוך)
                                if len(text) > 30:
                                    handle_transaction(chat_id, text, user_name)
                                    user_states[chat_id]["state"] = "completed"
                                else:
                                    send_telegram_message(chat_id, "❌ <b>מספר עסקה לא תקין.</b>\n\nאנא שלח את מספר העסקה המלא.")
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"שגיאה בלולאה הראשית: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
