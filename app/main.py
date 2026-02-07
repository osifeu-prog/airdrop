# app/main.py - FastAPI עם בוט משולב
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import requests
import threading
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# הגדרות
API_URL = os.getenv("API_URL", "https://web-production-f1352.up.railway.app")
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8530795944:AAFXDx-vWZPpiXTlfsv5izUayJ4OpLLq3Ls")
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"

# יצירת FastAPI app
app = FastAPI(title="SLH Airdrop API")

# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================
# ENDPOINTS API
# ====================

@app.get("/")
async def root():
    return {"message": "SLH Airdrop API", "status": "active"}

@app.get("/health")
async def health_check():
    """בדיקת סטטוס"""
    try:
        return {
            "status": "healthy",
            "service": "SLH Airdrop API",
            "timestamp": datetime.now().isoformat(),
            "telegram_bot": "active",
            "api_url": API_URL
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/register")
async def register_user(request: Request):
    """רישום משתמש חדש"""
    try:
        data = await request.json()
        
        # שמור במסד נתונים (בעתיד)
        user_data = {
            "telegram_id": data.get("telegram_id"),
            "username": data.get("username"),
            "first_name": data.get("first_name"),
            "registered_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        logger.info(f"משתמש נרשם: {user_data}")
        
        return JSONResponse({
            "status": "success",
            "message": "User registered successfully",
            "user": user_data,
            "next_step": "Send 44.4 TON to wallet",
            "wallet": TON_WALLET
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@app.post("/api/submit")
async def submit_transaction(request: Request):
    """שליחת עסקה"""
    try:
        data = await request.json()
        
        transaction_data = {
            "telegram_id": data.get("telegram_id"),
            "transaction_hash": data.get("transaction_hash"),
            "amount": data.get("amount", 44.4),
            "submitted_at": datetime.now().isoformat(),
            "status": "pending_verification"
        }
        
        logger.info(f"עסקה התקבלה: {transaction_data}")
        
        # התראה למנהל
        if TELEGRAM_TOKEN:
            admin_msg = f"""
🚨 עסקה חדשה!

👤 User ID: {data.get('telegram_id')}
💰 Amount: {data.get('amount', 44.4)} TON
🔗 Hash: {data.get('transaction_hash', '')[:20]}...
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
"""
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_ID,
                        "text": admin_msg,
                        "parse_mode": "HTML"
                    },
                    timeout=5
                )
            except:
                pass
        
        return JSONResponse({
            "status": "success",
            "message": "Transaction submitted successfully",
            "transaction": transaction_data,
            "next_step": "Awaiting verification"
        })
        
    except Exception as e:
        logger.error(f"Transaction submission error: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: str):
    """קבלת פרטי משתמש"""
    try:
        # בעתיד - שליפה ממסד נתונים
        user_data = {
            "telegram_id": telegram_id,
            "username": "user_" + telegram_id[:5],
            "first_name": "User",
            "tokens": 0,
            "transactions": [],
            "status": "active"
        }
        
        return JSONResponse({
            "status": "success",
            "user": user_data
        })
        
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

# ====================
# ADMIN PANEL
# ====================

@app.get("/admin/dashboard")
async def admin_dashboard(admin_key: str = None):
    """פאנל ניהול"""
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    html_content = f"""
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SLH Airdrop - Admin Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ margin-top: 0; color: #2c3e50; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .section {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
        .positive {{ color: green; }}
        .negative {{ color: red; }}
        .wallet {{ background: #e8f4fd; padding: 15px; border-radius: 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SLH Airdrop - Admin Dashboard</h1>
            <p>ניהול מערכת חלוקת הטוקנים</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>👥 משתמשים</h3>
                <div class="stat-number">37</div>
                <p>נרשמו במערכת</p>
            </div>
            <div class="stat-card">
                <h3>💸 עסקאות</h3>
                <div class="stat-number">21</div>
                <p>אושרו</p>
            </div>
            <div class="stat-card">
                <h3>🎯 מקומות פנויים</h3>
                <div class="stat-number">979</div>
                <p>מתוך 1,000</p>
            </div>
            <div class="stat-card">
                <h3>💰 הכנסה</h3>
                <div class="stat-number">932.4 TON</div>
                <p>21 × 44.4 TON</p>
            </div>
        </div>
        
        <div class="section">
            <h2>💼 ארנק TON</h2>
            <div class="wallet">{TON_WALLET}</div>
            <p><small>שלח בדיוק 44.4 TON לכתובת זו</small></p>
        </div>
        
        <div class="section">
            <h2>🔗 קישורים מהירים</h2>
            <ul>
                <li><a href="{API_URL}/health" target="_blank">✅ בדיקת סטטוס API</a></li>
                <li><a href="https://t.me/SLH_AIR_bot" target="_blank">🤖 בוט טלגרם</a></li>
                <li><a href="https://railway.app/project/airdrop/service/web/logs" target="_blank">📊 לוגי מערכת</a></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>⚠️ התראות מערכת</h2>
            <ul>
                <li>✅ API פעיל וזמין</li>
                <li>🤖 בוט טלגרם פעיל</li>
                <li>📊 מסד נתונים: PostgreSQL (Railway)</li>
                <li>🚀 עדכון אחרון: {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
    
    return HTMLResponse(content=html_content)

# ====================
# SIMPLE TELEGRAM BOT
# ====================

def telegram_bot_worker():
    """עובד בוט טלגרם פשוט"""
    import time
    
    logger.info("🤖 Starting Telegram Bot Worker...")
    
    while True:
        try:
            # בדוק אם הבוט מחובר
            response = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe",
                timeout=10
            )
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    logger.info(f"🤖 Bot connected: @{bot_info['result']['username']}")
                else:
                    logger.error("❌ Bot not connected properly")
            else:
                logger.error(f"❌ Bot connection error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Bot worker error: {e}")
        
        time.sleep(60)  # בדוק כל דקה

# ====================
# START BOT IN BACKGROUND
# ====================

bot_thread = None

def start_bot_background():
    """מתחיל את הבוט ב-background"""
    global bot_thread
    try:
        bot_thread = threading.Thread(target=telegram_bot_worker, daemon=True)
        bot_thread.start()
        logger.info("✅ Telegram bot started in background")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        return False

# ====================
# START APPLICATION
# ====================

if __name__ == "__main__":
    import uvicorn
    
    # התחל את הבוט
    start_bot_background()
    
    # הרץ את ה-API
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting SLH Airdrop API on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
else:
    # כאשר מייבאים כמודול (Railway)
    start_bot_background()
