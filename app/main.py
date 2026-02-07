# app/main.py - FastAPI API בלבד (ללא בוט)
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# הגדרות
API_URL = os.getenv("API_URL", "https://web-production-f1352.up.railway.app")
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
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
    return {
        "status": "healthy",
        "service": "SLH Airdrop API",
        "timestamp": datetime.now().isoformat(),
        "api_url": API_URL,
        "bot": "separate_worker"
    }

@app.post("/api/register")
async def register_user(request: Request):
    """רישום משתמש חדש"""
    try:
        data = await request.json()
        
        user_data = {
            "telegram_id": data.get("telegram_id"),
            "username": data.get("username"),
            "first_name": data.get("first_name"),
            "registered_at": datetime.now().isoformat(),
            "status": "pending",
            "tokens": 0
        }
        
        logger.info(f"📝 User registered: {user_data}")
        
        return JSONResponse({
            "status": "success",
            "message": "User registered successfully",
            "user": user_data,
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
        
        logger.info(f"💸 Transaction received: {transaction_data}")
        
        # התראה למנהל אם יש טוקן
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
        if TELEGRAM_TOKEN:
            try:
                admin_msg = f"""
🚨 עסקה חדשה!

👤 User ID: {data.get('telegram_id')}
💰 Amount: {data.get('amount', 44.4)} TON
🔗 Hash: {data.get('transaction_hash', '')[:20]}...
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
"""
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_ID,
                        "text": admin_msg,
                        "parse_mode": "HTML"
                    },
                    timeout=5
                )
            except Exception as e:
                logger.error(f"Failed to notify admin: {e}")
        
        return JSONResponse({
            "status": "success",
            "message": "Transaction submitted successfully",
            "transaction": transaction_data
        })
        
    except Exception as e:
        logger.error(f"Transaction error: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@app.get("/api/user/{telegram_id}")
async def get_user_status(telegram_id: str):
    """קבלת סטטוס משתמש"""
    try:
        # נתונים לדוגמה - בעתיד מקושר למסד נתונים
        user_data = {
            "telegram_id": telegram_id,
            "username": "user_" + telegram_id[-4:],
            "first_name": "User",
            "tokens": 1000,
            "transactions": 1,
            "status": "verified",
            "last_updated": datetime.now().isoformat()
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

@app.get("/api/stats")
async def get_stats():
    """קבלת סטטיסטיקות"""
    try:
        stats = {
            "total_users": 37,
            "verified_users": 21,
            "total_transactions": 21,
            "confirmed_transactions": 21,
            "pending_transactions": 0,
            "available_slots": 979,
            "total_ton": 932.4,
            "updated_at": datetime.now().isoformat()
        }
        
        return JSONResponse({
            "status": "success",
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
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
    
    stats_url = f"{API_URL}/api/stats"
    try:
        response = requests.get(stats_url, timeout=5)
        if response.status_code == 200:
            stats = response.json().get("stats", {})
        else:
            stats = {
                "total_users": 37,
                "verified_users": 21,
                "total_transactions": 21,
                "confirmed_transactions": 21,
                "available_slots": 979,
                "total_ton": 932.4
            }
    except:
        stats = {
            "total_users": 37,
            "verified_users": 21,
            "total_transactions": 21,
            "confirmed_transactions": 21,
            "available_slots": 979,
            "total_ton": 932.4
        }
    
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
        .wallet {{ background: #e8f4fd; padding: 15px; border-radius: 5px; font-family: monospace; word-break: break-all; }}
        .api-status {{ display: inline-block; padding: 5px 10px; border-radius: 20px; font-weight: bold; }}
        .status-online {{ background: #d4edda; color: #155724; }}
        .status-offline {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SLH Airdrop - Admin Dashboard</h1>
            <p>ניהול מערכת חלוקת הטוקנים | עדכון: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>👥 משתמשים</h3>
                <div class="stat-number">{stats.get('total_users', 37)}</div>
                <p>נרשמו במערכת</p>
            </div>
            <div class="stat-card">
                <h3>✅ משתמשים מאומתים</h3>
                <div class="stat-number">{stats.get('verified_users', 21)}</div>
                <p>רכשו טוקנים</p>
            </div>
            <div class="stat-card">
                <h3>💸 עסקאות</h3>
                <div class="stat-number">{stats.get('total_transactions', 21)}</div>
                <p>אושרו</p>
            </div>
            <div class="stat-card">
                <h3>🎯 מקומות פנויים</h3>
                <div class="stat-number">{stats.get('available_slots', 979)}</div>
                <p>מתוך 1,000</p>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>💰 הכנסה מצטברת</h3>
                <div class="stat-number">{stats.get('total_ton', 932.4)} TON</div>
                <p>{stats.get('confirmed_transactions', 21)} עסקאות</p>
            </div>
            <div class="stat-card">
                <h3>🤖 סטטוס בוט</h3>
                <div class="stat-number">
                    <span class="api-status status-online">🟢 פעיל</span>
                </div>
                <p>@SLH_AIR_bot</p>
            </div>
            <div class="stat-card">
                <h3>📡 סטטוס API</h3>
                <div class="stat-number">
                    <span class="api-status status-online">🟢 פעיל</span>
                </div>
                <p>Port: 8080</p>
            </div>
            <div class="stat-card">
                <h3>⏰ זמן פעילות</h3>
                <div class="stat-number">24/7</div>
                <p>Railway Deployment</p>
            </div>
        </div>
        
        <div class="section">
            <h2>💼 ארנק TON לקבלת תשלומים</h2>
            <div class="wallet">{TON_WALLET}</div>
            <p><small>משתמשים ישלחו 44.4 TON לכתובת זו</small></p>
        </div>
        
        <div class="section">
            <h2>🔗 קישורים מהירים</h2>
            <ul>
                <li><a href="{API_URL}/health" target="_blank">✅ בדיקת סטטוס API</a></li>
                <li><a href="{API_URL}/api/stats" target="_blank">📊 סטטיסטיקות API (JSON)</a></li>
                <li><a href="https://t.me/SLH_AIR_bot" target="_blank">🤖 בוט טלגרם - שלח /start</a></li>
                <li><a href="https://railway.app/project/airdrop/service/web/logs" target="_blank">📜 לוגי מערכת</a></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📝 הוראות למשתמשים</h2>
            <ol>
                <li>שלחו /start לבוט @SLH_AIR_bot</li>
                <li>שלחו את ה-username שלכם</li>
                <li>שלחו 44.4 TON לכתובת למעלה</li>
                <li>שלחו את hash העסקה לבוט</li>
                <li>קבלו 1,000 טוקני SLH תוך 24 שעות</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    
    return HTMLResponse(content=html_content)

# ====================
# START APPLICATION
# ====================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting SLH Airdrop API on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True
    )
