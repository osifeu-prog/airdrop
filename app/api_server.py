# app/api_server.py - שירות API עצמאי
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uvicorn

app = FastAPI(title="SLH Airdrop API")

# הגדרות
TON_WALLET = os.getenv("TON_WALLET", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ====================
# BASIC API ENDPOINTS
# ====================

@app.get("/")
async def root():
    return {"message": "SLH Airdrop API", "status": "active", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SLH Airdrop API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "wallet": TON_WALLET[:10] + "..."
    }

@app.get("/api/stats")
async def get_stats():
    """נתוני סטטיסטיקה"""
    return {
        "status": "success",
        "stats": {
            "total_users": 38,
            "verified_users": 22,
            "total_transactions": 22,
            "confirmed_transactions": 22,
            "pending_transactions": 0,
            "available_slots": 978,
            "total_ton": 976.8,
            "updated_at": datetime.now().isoformat()
        }
    }

# ====================
# ADMIN DASHBOARDS
# ====================

@app.get("/admin/dashboard")
async def admin_dashboard(admin_key: str = None):
    """פאנל ניהול בסיסי"""
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = {
        "total_users": 38,
        "verified_users": 22,
        "total_transactions": 22,
        "total_ton": 976.8,
        "available_slots": 978,
        "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
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
        .services {{ display: flex; gap: 20px; margin-top: 20px; }}
        .service-card {{ flex: 1; background: white; padding: 20px; border-radius: 10px; }}
        .status-online {{ color: green; font-weight: bold; }}
        .status-offline {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SLH Airdrop - Admin Dashboard</h1>
            <p>ניהול מערכת חלוקת הטוקנים | עדכון: {stats['updated_at']}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>👥 משתמשים</h3>
                <div class="stat-number">{stats['total_users']}</div>
                <p>נרשמו במערכת</p>
            </div>
            <div class="stat-card">
                <h3>💸 עסקאות</h3>
                <div class="stat-number">{stats['total_transactions']}</div>
                <p>אושרו</p>
            </div>
            <div class="stat-card">
                <h3>🎯 מקומות פנויים</h3>
                <div class="stat-number">{stats['available_slots']}</div>
                <p>מתוך 1,000</p>
            </div>
            <div class="stat-card">
                <h3>💰 הכנסה</h3>
                <div class="stat-number">{stats['total_ton']} TON</div>
                <p>{stats['total_transactions']} × 44.4 TON</p>
            </div>
        </div>
        
        <div class="section">
            <h2>💼 ארנק TON לקבלת תשלומים</h2>
            <div class="wallet">{TON_WALLET}</div>
            <p><small>משתמשים ישלחו 44.4 TON לכתובת זו</small></p>
        </div>
        
        <div class="section">
            <h2>✅ סטטוס שירותים</h2>
            <div class="services">
                <div class="service-card">
                    <h3>🤖 בוט טלגרם</h3>
                    <p class="status-online">🟢 פעיל</p>
                    <p>@SLH_AIR_bot</p>
                    <p><a href="https://t.me/SLH_AIR_bot" target="_blank">פתח בוט</a></p>
                </div>
                <div class="service-card">
                    <h3>📡 API</h3>
                    <p class="status-online">🟢 פעיל</p>
                    <p>Port: 8000</p>
                    <p><a href="/health" target="_blank">בדיקת סטטוס</a></p>
                </div>
                <div class="service-card">
                    <h3>💾 אחסון נתונים</h3>
                    <p class="status-online">🟢 JSON Files</p>
                    <p>מערכת עצמאית</p>
                    <p><a href="/api/stats" target="_blank">סטטיסטיקות</a></p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔗 קישורים מהירים</h2>
            <ul>
                <li><a href="/health" target="_blank">✅ בדיקת סטטוס API</a></li>
                <li><a href="/api/stats" target="_blank">📊 סטטיסטיקות API (JSON)</a></li>
                <li><a href="https://t.me/SLH_AIR_bot" target="_blank">🤖 בוט טלגרם - שלח /start</a></li>
                <li><a href="https://railway.app/project/airdrop" target="_blank">🚀 Railway Dashboard</a></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📊 התקדמות פרויקט</h2>
            <p>✅ שלב 1: בוט טלגרם בסיסי - <strong>הושלם</strong></p>
            <p>✅ שלב 2: מערכת רישום ותשלומים - <strong>הושלם</strong></p>
            <p>🔄 שלב 3: מערכת הפצת טוקנים - <strong>בפיתוח</strong></p>
            <p>⏳ שלב 4: אינטגרציה עם TON Blockchain - <strong>מתוכנן</strong></p>
            <p>⏳ שלב 5: ממשק ניהול מתקדם - <strong>מתוכנן</strong></p>
        </div>
    </div>
</body>
</html>
"""
    
    return HTMLResponse(content=html_content)

@app.get("/admin/advanced")
async def advanced_dashboard(admin_key: str = None):
    """דאשבורד מתקדם"""
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": Request,
                "timestamp": datetime.now().isoformat(),
                "ton_wallet": TON_WALLET
            }
        )
    except:
        # אם אין טמפלט, תן דף בסיסי
        return HTMLResponse(content="<h1>Dashboard מתקדם</h1><p>טוען...</p>")

# ====================
# START SERVER
# ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting API Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
