#!/usr/bin/env python3
"""
🚀 SLH Airdrop Bot - גרסה מושלמת ומרהיבה
בוט מודרני עם תכונות מתקדמות וממשק עשיר
"""

import logging
import requests
import time
import json
import sys
import io
from datetime import datetime
from typing import Dict, Optional

# ====================
# CONFIGURATION
# ====================
TOKEN = "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls"
API_URL = ""  # יש לשנות לכתובת ה-Railway אחרי ההעלאה
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
# EMOJI CONSTANTS
# ====================
EMOJI = {
    "rocket": "🚀",
    "money": "💰",
    "coin": "🪙",
    "user": "👤",
    "users": "👥",
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "fire": "🔥",
    "star": "⭐",
    "gift": "🎁",
    "chart": "📈",
    "link": "🔗",
    "lock": "🔒",
    "unlock": "🔓",
    "clock": "⏰",
    "calendar": "📅",
    "credit": "💳",
    "bank": "🏦",
    "computer": "💻",
    "phone": "📱",
    "world": "🌐",
    "flag": "🎌",
    "trophy": "🏆",
    "medal": "🥇",
    "crown": "👑",
    "bulb": "💡",
    "gear": "⚙️",
    "key": "🔑",
    "shield": "🛡️",
    "bell": "🔔",
    "megaphone": "📢",
    "inbox": "📥",
    "outbox": "📤",
    "search": "🔍",
    "wrench": "🔧",
    "hammer": "🔨",
    "package": "📦",
    "email": "📧",
    "book": "📖",
    "page": "📄",
    "clipboard": "📋",
    "pin": "📌",
    "round_pushpin": "📍",
    "pushpin": "📎",
    "scissors": "✂️",
    "pencil": "✏️",
    "paintbrush": "🖌️",
    "crayon": "🖍️",
    "memo": "📝",
    "briefcase": "💼",
    "file_folder": "📁",
    "open_file_folder": "📂",
    "card_index": "📇",
    "date": "📅",
    "card": "🗂️",
    "clipboards": "📋",
    "bar_chart": "📊",
    "chart_up": "📈",
    "chart_down": "📉",
    "speech": "💬",
    "thought": "💭",
    "zzz": "💤",
    "dash": "💨",
    "bomb": "💣",
    "collision": "💥",
    "sweat": "💦",
    "dizzy": "💫",
    "speech_left": "🗨️",
    "anger": "💢",
    "heart": "❤️",
    "blue_heart": "💙",
    "green_heart": "💚",
    "yellow_heart": "💛",
    "purple_heart": "💜",
    "sparkles": "✨",
    "globe": "🌍",
    "dollar": "💵",
    "yen": "💴",
    "euro": "💶",
    "pound": "💷",
    "moneybag": "💰",
    "credit_card": "💳",
    "receipt": "🧾",
    "coin": "🪙",
    "bank": "🏦",
    "atm": "🏧",
    "construction": "🚧",
    "rotating_light": "🚨",
    "police_car": "🚓",
    "ambulance": "🚑",
    "fire_engine": "🚒",
    "racing_car": "🏎️",
    "motorcycle": "🏍️",
    "airplane": "✈️",
    "rocket": "🚀",
    "helicopter": "🚁",
    "steam_locomotive": "🚂",
    "train": "🚆",
    "metro": "🚇",
    "tram": "🚊",
    "bus": "🚌",
    "taxi": "🚕",
    "car": "🚗",
    "truck": "🚚",
    "ship": "🚢",
    "anchor": "⚓",
    "construction_worker": "👷",
    "guard": "💂",
    "detective": "🕵️",
    "health_worker": "🧑‍⚕️",
    "farmer": "🧑‍🌾",
    "cook": "🧑‍🍳",
    "student": "🧑‍🎓",
    "singer": "🧑‍🎤",
    "artist": "🧑‍🎨",
    "pilot": "🧑‍✈️",
    "astronaut": "🧑‍🚀",
    "judge": "🧑‍⚖️",
    "person": "👤",
    "people": "👥",
    "family": "👪",
    "couple": "👫",
    "women": "👭",
    "men": "👬",
    "woman": "👩",
    "man": "👨",
    "child": "🧒",
    "baby": "👶",
    "older_adult": "🧓",
    "bearded_person": "🧔",
    "blond_haired_person": "👱",
    "red_haired_person": "👨‍🦰",
    "curly_haired_person": "👨‍🦱",
    "white_haired_person": "👨‍🦳",
    "bald_person": "👨‍🦲",
    "woman_blond_hair": "👱‍♀️",
    "man_blond_hair": "👱‍♂️",
    "woman_red_hair": "👩‍🦰",
    "man_red_hair": "👨‍🦰",
    "woman_curly_hair": "👩‍🦱",
    "man_curly_hair": "👨‍🦱",
    "woman_white_hair": "👩‍🦳",
    "man_white_hair": "👨‍🦳",
    "woman_bald": "👩‍🦲",
    "man_bald": "👨‍🦲",
}

# ====================
# API FUNCTIONS
# ====================
def call_api(endpoint, method="GET", data=None):
    """קורא ל-API בצורה בטוחה"""
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
    """שולח הודעה לטלגרם עם תמיכה ב-reply_markup"""
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
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Telegram Send Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram Connection Error: {e}")
        return False

def create_keyboard(buttons, resize=True, one_time=False):
    """יוצר מקלדת טלגרם"""
    return {
        "keyboard": buttons,
        "resize_keyboard": resize,
        "one_time_keyboard": one_time
    }

def create_inline_keyboard(buttons):
    """יוצר inline keyboard"""
    return {"inline_keyboard": buttons}

# ====================
# MESSAGE TEMPLATES
# ====================
def welcome_message(user_name, username=""):
    """הודעת ברוך הבא מרהיבה"""
    return f"""
{EMOJI['rocket']} <b>ברוך הבא ל-SLH Airdrop System!</b>

{EMOJI['star']} <b>המערכת המתקדמת ביותר להשקעה בקריפטו</b>

{EMOJI['user']} <b>משתמש:</b> {user_name}
{EMOJI['link']} <b>Username:</b> @{username if username else 'לא צוין'}

{EMOJI['gift']} <b>🎁 מבצע השקה בלעדי:</b>
• 1,000 טוקני SLH = 44.4 ILS
• קבלה אוטומטית תוך 24 שעות
• תמיכה טכנית 24/7

{EMOJI['chart']} <b>📊 מדוע SLH?</b>
• המערכת תהפוך לפלטפורמת בחירת מומחים
• הטוקנים ייסחרו בבורסות המובילות
• תרומה לקהילה ולפיתוח טכנולוגי בישראל
• הזדמנות להצטרף לפרויקט מהפכני מההתחלה!

{EMOJI['bulb']} <b>💡 הטבות למשתתפים מוקדמים:</b>
1. בונוס +10% טוקנים (100 ראשונים בלבד!)
2. גישה לקהילת טלגרם VIP
3. זכות הצבעה על פיתוח המערכת
4. אפשרות להפיץ ולהרוויח עמלות

<b>{EMOJI['pushpin']} לחץ על הכפתור למטה כדי להתחיל!</b>
"""

def main_menu_message():
    """מסך תפריט ראשי"""
    return f"""
{EMOJI['crown']} <b>תפריט ראשי - SLH Airdrop</b>

{EMOJI['coin']} <b>אפשרויות זמינות:</b>

1. {EMOJI['money']} <b>קניית טוקנים</b> - רכישת 1,000 טוקני SLH
2. {EMOJI['chart']} <b>סטטוס אישי</b> - צפייה במאזן והסטוריה
3. {EMOJI['gift']} <b>מערכת בונוסים</b> - קבלת בונוסים על שיתופים
4. {EMOJI['link']} <b>קישור הפניה</b> - הזמנת חברים להרוויח
5. {EMOJI['trophy']} <b>טבלת מובילים</b> - רשימת המרוויחים הגדולים
6. {EMOJI['info']} <b>מידע והסברים</b> - כל מה שצריך לדעת

<b>{EMOJI['bulb']} בחר אפשרות מהתפריט למטה:</b>
"""

def payment_instructions(username, chat_id):
    """הוראות תשלום מפורטות"""
    return f"""
{EMOJI['check']} <b>שם משתמש אושר!</b>

{EMOJI['user']} <b>Username:</b> @{username}
{EMOJI['id']} <b>מזהה:</b> {chat_id}
{EMOJI['calendar']} <b>תאריך:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

{EMOJI['credit']} <b>השלב הבא - תשלום:</b>

<b>שלב 1:</b> העתק את כתובת הארנק שלנו:
<code>{TON_WALLET}</code>

<b>שלב 2:</b> פתח את אפליקציית TON שלך (Tonkeeper, Tonhub, וכו')

<b>שלב 3:</b> שלח בדיוק <b>44.4 TON</b> לכתובת למעלה

<b>שלב 4:</b> בתיאור התשלום כתוב:
<code>Airdrop-{chat_id}</code>

<b>שלב 5:</b> שמור את מספר העסקה (Transaction Hash)

<b>שלב 6:</b> שלח את מספר העסקה חזרה לכאן

{EMOJI['gift']} <b>🎁 לאחר אישור התשלום תקבל:</b>
• 1,000 טוקני SLH
• תואר "משקיע מוקדם"
• גישה לקהילה הפרטית
• אפשרויות בונוס נוספות

{EMOJI['warning']} <b>⚠️ חשוב מאוד:</b>
• שלח בדיוק 44.4 TON (לא יותר, לא פחות)
• הוסף את התיאור עם המזהה שלך
• שמור את מספר העסקה!
• זמן אספקה: עד 24 שעות

<b>{EMOJI['phone']} שאלות?</b> @Osif83
"""

def transaction_received_message(user_name, tx_hash):
    """הודעה על קבלת עסקה"""
    return f"""
{EMOJI['fire']} <b>תשלום התקבל!</b>

{EMOJI['user']} <b>משתמש:</b> {user_name}
{EMOJI['credit']} <b>מספר עסקה:</b>
<code>{tx_hash[:20]}...{tx_hash[-20:]}</code>
{EMOJI['money']} <b>סכום:</b> 44.4 TON
{EMOJI['coin']} <b>טוקנים:</b> 1,000 SLH

{EMOJI['clock']} <b>סטטוס:</b> ממתין לאישור מנהל
{EMOJI['calendar']} <b>זמן אספקה:</b> עד 24 שעות

{EMOJI['chart']} <b>למעקב:</b> שלח /status בכל עת
{EMOJI['bell']} <b>התראה:</b> תקבל הודעה כשהטוקנים יישלחו

{EMOJI['trophy']} <b>🎉 מזל טוב! הצטרפת לפרויקט מהפכני!</b>

<b>{EMOJI['star']} הטבות שקיבלת:</b>
1. 1,000 טוקני SLH
2. תואר "משקיע מוקדם"
3. זכות הצבעה על פיתוח המערכת
4. אפשרות להזמין חברים ולהרוויח

{EMOJI['megaphone']} <b>💬 רוצה לעזור לנו לגדול?</b>
שתף את הקישור עם חברים וקבל בונוסים!
לחץ על /share כדי לקבל קישור שיתוף אישי.
"""

def user_status_message(user_data):
    """מציג סטטוס משתמש"""
    tokens = user_data.get("tokens", 0)
    referrals = user_data.get("referrals", 0)
    bonus = user_data.get("total_bonus", 0)
    
    total_value = tokens * 44.4 / 1000
    
    return f"""
{EMOJI['chart']} <b>סטטוס אישי - SLH Tokens</b>

{EMOJI['user']} <b>משתמש:</b> {user_data.get('first_name', 'משתמש')}
{EMOJI['id']} <b>מזהה:</b> {user_data.get('telegram_id', 'לא ידוע')}

{EMOJI['coin']} <b>טוקנים בבעלותך:</b> {tokens:,} SLH
{EMOJI['money']} <b>שווי משוער:</b> {total_value:,.1f} ILS
{EMOJI['gift']} <b>בונוסים שנצברו:</b> {bonus} טוקנים
{EMOJI['users']} <b>הפניות מוצלחות:</b> {referrals} משתמשים

{EMOJI['credit']} <b>עסקאות אחרונות:</b>
{user_data.get('transactions_summary', 'אין עסקאות')}

{EMOJI['star']} <b>דרגת משקיע:</b> {'מוקדם' if tokens > 0 else 'חדש'}

{EMOJI['link']} <b>קישורים חשובים:</b>
• אתר: https://slhisrael.com/
• דשבורד: https://web-production-112f6.up.railway.app/investors/
• חוזה BSC: https://bscscan.com/token/0xACb0A09414CEA1C879c67bB7A877E4e19480f022

<b>{EMOJI['bulb']} רוצה להגדיל את ההשקעה?</b>
שלח /start להתחיל רכישה נוספת
"""

def referral_message(chat_id):
    """הודעת הפניה עם קישור אישי"""
    referral_code = f"SLH{chat_id}"
    share_link = f"https://t.me/SLH_AIR_bot?start={referral_code}"
    
    return f"""
{EMOJI['megaphone']} <b>קישור שיתוף אישי שלך!</b>

{EMOJI['link']} <b>הקישור שלך להזמנת חברים:</b>
{share_link}

{EMOJI['gift']} <b>🎁 בונוסים שאתה מקבל:</b>

{EMOJI['star']} <b>לכל שיתוף:</b>
• 30 טוקני בונוס על שיתוף בפייסבוק
• 20 טוקני בונוס על שיתוף בטלגרם
• 10 טוקני בונוס על שיתוף בוואטסאפ

{EMOJI['users']} <b>לכל חבר שמצטרף:</b>
• 50 טוקני בונוס על הרשמה
• 100 טוקני בונוס על רכישה ראשונה
• 5% מעמלה על כל רכישה נוספת

{EMOJI['trophy']} <b>🏆 טבלת מובילים:</b>
המזמינים המובילים יקבלו פרסים נוספים!

{EMOJI['chart']} <b>📊 הסטטוס שלך:</b>
• הפניות שהזמנת: 0
• בונוסים שנצברו: 0
• דרגת מפיץ: מתחיל

<b>{EMOJI['fire']} שתף והתחל להרוויח עוד היום!</b>
"""

# ====================
# BOT HANDLERS
# ====================
class SLHAirdropBot:
    def __init__(self):
        self.user_states = {}
        self.last_activity = {}
        
    def handle_start(self, chat_id, user_name, username=""):
        """מטפל בפקודת /start"""
        # רישום משתמש ב-API
        user_data = {
            "telegram_id": str(chat_id),
            "username": username if username else "",
            "first_name": user_name
        }
        
        api_response = call_api("/api/users/register", "POST", user_data)
        
        # שליחת הודעת ברוך הבא
        send_telegram_message(chat_id, welcome_message(user_name, username))
        
        # המתן 2 שניות ואז שלח תפריט
        time.sleep(2)
        
        # יצירת מקלדת תפריט
        menu_keyboard = create_keyboard([
            [EMOJI['money'] + ' קניית טוקנים'],
            [EMOJI['chart'] + ' סטטוס אישי', EMOJI['gift'] + ' בונוסים'],
            [EMOJI['link'] + ' קישור הפניה', EMOJI['trophy'] + ' טבלת מובילים'],
            [EMOJI['info'] + ' מידע והסברים', EMOJI['gear'] + ' הגדרות']
        ])
        
        send_telegram_message(chat_id, main_menu_message(), reply_markup=menu_keyboard)
        
        # עדכן state
        self.user_states[chat_id] = {"state": "main_menu", "username": username}
        
        # שלח התראה למנהל
        if api_response and api_response.get("status") == "success":
            admin_msg = f"{EMOJI['bell']} משתמש חדש: {user_name} (@{username})"
            send_telegram_message(ADMIN_ID, admin_msg)
    
    def handle_menu_selection(self, chat_id, text, user_name):
        """מטפל בבחירת תפריט"""
        if text == EMOJI['money'] + ' קניית טוקנים':
            self.user_states[chat_id] = {"state": "awaiting_username"}
            send_telegram_message(chat_id, 
                f"{EMOJI['info']} <b>שלב ראשון: אימות משתמש</b>\n\nשלח לי את שם המשתמש הטלגרם שלך (לדוגמה: @username)")
            
        elif text == EMOJI['chart'] + ' סטטוס אישי':
            self.show_user_status(chat_id, user_name)
            
        elif text == EMOJI['gift'] + ' בונוסים':
            self.show_bonus_info(chat_id)
            
        elif text == EMOJI['link'] + ' קישור הפניה':
            self.show_referral_link(chat_id)
            
        elif text == EMOJI['trophy'] + ' טבלת מובילים':
            self.show_leaderboard(chat_id)
            
        elif text == EMOJI['info'] + ' מידע והסברים':
            self.show_info(chat_id)
            
        elif text == EMOJI['gear'] + ' הגדרות':
            self.show_settings(chat_id)
    
    def handle_username(self, chat_id, username, user_name):
        """מטפל בקבלת username"""
        username = username.replace('@', '').strip()
        
        if len(username) < 3:
            send_telegram_message(chat_id, 
                f"{EMOJI['warning']} <b>שם משתמש לא תקין.</b>\n\nאנא שלח username תקין (לפחות 3 תווים).")
            return False
        
        # שמור את ה-username
        if chat_id in self.user_states:
            self.user_states[chat_id]["provided_username"] = username
        
        # שלח הוראות תשלום
        send_telegram_message(chat_id, payment_instructions(username, chat_id))
        
        # עדכן state
        self.user_states[chat_id]["state"] = "awaiting_payment"
        
        return True
    
    def handle_transaction(self, chat_id, tx_hash, user_name):
        """מטפל בשליחת transaction hash"""
        # בדוק אם זה נראה כמו hash אמיתי
        if len(tx_hash) < 30:
            send_telegram_message(chat_id,
                f"{EMOJI['warning']} <b>מספר עסקה לא תקין.</b>\n\nאנא שלח את מספר העסקה המלא (64 תווים).")
            return False
        
        # שמירת העסקה ב-API
        tx_data = {
            "telegram_id": str(chat_id),
            "transaction_hash": tx_hash,
            "amount": 44.4
        }
        
        api_response = call_api("/api/users/submit_transaction", "POST", tx_data)
        
        if api_response and api_response.get("status") == "success":
            # הודעה למשתמש
            send_telegram_message(chat_id, transaction_received_message(user_name, tx_hash))
            
            # התראה למנהל
            admin_msg = f"""
{EMOJI['bell']} <b>תשלום חדש!</b>

{EMOJI['user']} <b>משתמש:</b> {user_name}
{EMOJI['id']} <b>מזהה:</b> {chat_id}
{EMOJI['credit']} <b>עסקה:</b> {tx_hash[:20]}...
{EMOJI['money']} <b>סכום:</b> 44.4 TON
{EMOJI['calendar']} <b>זמן:</b> {datetime.now().strftime('%H:%M:%S')}

{EMOJI['link']} <b>פאנל ניהול:</b>
/admin/dashboard?admin_key=airdrop_admin_2026
"""
            send_telegram_message(ADMIN_ID, admin_msg)
            
            # עדכן state
            self.user_states[chat_id]["state"] = "payment_completed"
            
            return True
        else:
            send_telegram_message(chat_id,
                f"{EMOJI['cross']} <b>שגיאה בשמירת העסקה</b>\n\nאנא נסה שוב או פנה לתמיכה: @Osif83")
            return False
    
    def show_user_status(self, chat_id, user_name):
        """מציג סטטוס משתמש"""
        # קבל נתונים מה-API
        api_response = call_api(f"/api/users/{chat_id}/status")
        
        if api_response and "user" in api_response:
            user_data = api_response["user"]
            send_telegram_message(chat_id, user_status_message(user_data))
        else:
            send_telegram_message(chat_id,
                f"{EMOJI['info']} <b>סטטוס אישי</b>\n\nעדיין לא רכשת טוקנים. לחץ על 'קניית טוקנים' כדי להתחיל!")
    
    def show_bonus_info(self, chat_id):
        """מציג מידע על בונוסים"""
        bonus_info = f"""
{EMOJI['gift']} <b>מערכת הבונוסים של SLH</b>

{EMOJI['star']} <b>🎁 סוגי בונוסים:</b>

1. {EMOJI['fire']} <b>בונוס השקה:</b> 10% תוספת ל-100 הראשונים
2. {EMOJI['users']} <b>בונוס הפניה:</b> 50 טוקנים על כל חבר שמצטרף
3. {EMOJI['link']} <b>בונוס שיתוף:</b} 30 טוקנים על שיתוף בפייסבוק
4. {EMOJI['trophy']} <b>בונוס פעילות:</b} טוקנים יומיים לפעילים

{EMOJI['chart']} <b>📊 איך להרוויח יותר:</b>

• הזמן חברים באמצעות /share
• שתף בפייסבוק וקבל 30 טוקנים
• היה פעיל בקבוצה וקבל טוקנים יומיים
• השתתף בתחרויות והגעה לטבלת המובילים

{EMOJI['money']} <b>💰 הצטרף עכשיו והתחל להרוויח!</b>
"""
        send_telegram_message(chat_id, bonus_info)
    
    def show_referral_link(self, chat_id):
        """מציג קישור הפניה"""
        send_telegram_message(chat_id, referral_message(chat_id))
    
    def show_leaderboard(self, chat_id):
        """מציג טבלת מובילים"""
        leaderboard = f"""
{EMOJI['trophy']} <b>טבלת המובילים - SLH Airdrop</b>

{EMOJI['medal']} <b>🥇 המובילים בהפניות:</b>

1. @User1 - 15 הפניות - 750 טוקנים
2. @User2 - 12 הפניות - 600 טוקנים  
3. @User3 - 8 הפניות - 400 טוקנים
4. @User4 - 5 הפניות - 250 טוקנים
5. @User5 - 3 הפניות - 150 טוקנים

{EMOJI['coin']} <b>🪙 המובילים בהשקעות:</b>

1. @Investor1 - 10,000 טוקנים
2. @Investor2 - 8,500 טוקנים
3. @Investor3 - 7,200 טוקנים
4. @Investor4 - 5,000 טוקנים
5. @Investor5 - 3,000 טוקנים

{EMOJI['calendar']} <b>עודכן לאחרונה:</b> {datetime.now().strftime('%d/%m/%Y')}

{EMOJI['fire']} <b>🔥 רוצה להופיע כאן?</b>
הזמן חברים באמצעות /share וקנה עוד טוקנים!
"""
        send_telegram_message(chat_id, leaderboard)
    
    def show_info(self, chat_id):
        """מציג מידע כללי"""
        info = f"""
{EMOJI['info']} <b>מידע על פרויקט SLH</b>

{EMOJI['rocket']} <b>🚀 מה זה SLH?</b>
SLH הוא פרויקט בלוקצ'יין ישראלי שמטרתו ליצור פלטפורמת בחירת מומחים מבוזרת.
הטוקנים יאפשרו גישה לשירותים מתקדמים וזכות הצבעה על פיתוח המערכת.

{EMOJI['chart']} <b>📈 תכניות לעתיד:</b>

• {EMOJI['calendar']} Q1 2026 - השקת Airdrop
• {EMOJI['calendar']} Q2 2026 - רישום לבורסות
• {EMOJI['calendar']} Q3 2026 - השקת פלטפורמת המומחים
• {EMOJI['calendar']} Q4 2026 - אינטגרציה עם מערכות נוספות

{EMOJI['money']} <b>💰 מדוע להשקיע עכשיו?</b>

1. מחיר השקה בלעדי: 44.4 ILS ל-1,000 טוקנים
2. בונוסים למשקיעים מוקדמים
3. פוטנציאל צמיחה משמעותי
4. תרומה לקהילה הטכנולוגית בישראל

{EMOJI['link']} <b>🔗 קישורים חשובים:</b>

• אתר: https://slhisrael.com/
• חוזה: https://bscscan.com/token/0xACb0A09414CEA1C879c67bB7A877E4e19480f022
• דוקומנטציה: https://docs.slh.com/
• תמיכה: @Osif83

{EMOJI['shield']} <b>🛡️ אבטחה ושקיפות:</b>
כל העסקאות מתבצעות בבלוקצ'יין וניתנות לאימות.
אין לנו גישה לכספים או פרטים אישיים שלך.
"""
        send_telegram_message(chat_id, info)
    
    def show_settings(self, chat_id):
        """מציג הגדרות"""
        settings = f"""
{EMOJI['gear']} <b>הגדרות מערכת</b>

{EMOJI['bell']} <b>התראות:</b> פעילות
{EMOJI['globe']} <b>שפה:</b> עברית
{EMOJI['money']} <b>מטבע:</b> ILS (₪)
{EMOJI['clock']} <b>אזור זמן:</b> ישראל (UTC+2)

{EMOJI['wrench']} <b>אפשרויות נוספות:</b>

• שנה שפה
• שנה מטבע
• נהל התראות
• צור גיבוי

{EMOJI['info']} <b>מידע טכני:</b>
גרסת בוט: 2.0
גרסת API: 1.0
סטטוס: פעיל

{EMOJI['key']} <b>הגדרות מתקדמות:</b>
למשתמשים מתקדמים בלבד.
"""
        send_telegram_message(chat_id, settings)

# ====================
# MAIN BOT LOOP
# ====================
def main():
    """לולאת הבוט הראשית"""
    bot = SLHAirdropBot()
    offset = 0
    
    logger.info(f"{EMOJI['rocket']} SLH Airdrop Bot v2.0 מתחיל...")
    
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
                        
                        logger.info(f"{EMOJI['inbox']} מה-{user_name}: {text[:50]}")
                        
                        # עדכן זמן פעילות אחרון
                        bot.last_activity[chat_id] = datetime.now()
                        
                        # טיפול בפקודות מיוחדות
                        if text == "/start":
                            bot.handle_start(chat_id, user_name, username)
                        
                        elif text == "/status":
                            bot.show_user_status(chat_id, user_name)
                        
                        elif text == "/share":
                            bot.show_referral_link(chat_id)
                        
                        elif text == "/help":
                            bot.show_info(chat_id)
                        
                        elif text == "/wallet":
                            wallet_msg = f"""
{EMOJI['bank']} <b>ארנק TON שלנו:</b>

<code>{TON_WALLET}</code>

{EMOJI['info']} <b>הוראות:</b>
שלח בדיוק 44.4 TON לכתובת זו.
בתיאור כתוב: Airdrop-מספר_טלגרם_שלך
"""
                            send_telegram_message(chat_id, wallet_msg)
                        
                        else:
                            # בדוק state נוכחי
                            state = bot.user_states.get(chat_id, {}).get("state", "main_menu")
                            
                            if state == "awaiting_username":
                                bot.handle_username(chat_id, text, user_name)
                            
                            elif state == "awaiting_payment":
                                # אם זה נראה כמו hash עסקה
                                if len(text) > 30:
                                    bot.handle_transaction(chat_id, text, user_name)
                                else:
                                    # בדוק אם זה בחירת תפריט
                                    if any(emoji in text for emoji in EMOJI.values()):
                                        bot.handle_menu_selection(chat_id, text, user_name)
                                    else:
                                        send_telegram_message(chat_id,
                                            f"{EMOJI['warning']} אנא שלח את מספר העסקה המלא (64 תווים) או בחר מהתפריט.")
                            
                            else:
                                # טיפול בבחירת תפריט
                                if any(emoji in text for emoji in EMOJI.values()):
                                    bot.handle_menu_selection(chat_id, text, user_name)
                                elif text.startswith("/"):
                                    send_telegram_message(chat_id,
                                        f"{EMOJI['info']} פקודה לא מוכרת. לחץ על /start להתחיל מחדש.")
                                else:
                                    # תחזור לתפריט ראשי
                                    menu_keyboard = create_keyboard([
                                        [EMOJI['money'] + ' קניית טוקנים'],
                                        [EMOJI['chart'] + ' סטטוס אישי', EMOJI['gift'] + ' בונוסים'],
                                        [EMOJI['link'] + ' קישור הפניה', EMOJI['trophy'] + ' טבלת מובילים'],
                                        [EMOJI['info'] + ' מידע והסברים', EMOJI['gear'] + ' הגדרות']
                                    ])
                                    send_telegram_message(chat_id, main_menu_message(), reply_markup=menu_keyboard)
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"{EMOJI['warning']} שגיאה בלולאה הראשית: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()


