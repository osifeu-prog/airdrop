# app/main.py - FastAPI API פשוט
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from datetime import datetime

app = FastAPI(title="SLH Airdrop API")

# הגדרות
TON_WALLET = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"

@app.get("/")
async def root():
    return {"message": "SLH Airdrop API", "status": "active"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SLH Airdrop API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/stats")
async def get_stats():
    """נתוני סטטיסטיקה"""
    return {
        "status": "success",
        "stats": {
            "total_users": 37,
            "verified_users": 21,
            "total_transactions": 21,
            "confirmed_transactions": 21,
            "pending_transactions": 0,
            "available_slots": 979,
            "total_ton": 932.4,
            "updated_at": datetime.now().isoformat()
        }
    }

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
        .wallet {{ background: #e8f4fd; padding: 15px; border-radius: 5px; font-family: monospace; word-break: break-all; }}
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
            <h2>✅ סטטוס שירותים</h2>
            <ul>
                <li>🤖 <b>בוט טלגרם:</b> פועל כשירות נפרד</li>
                <li>📡 <b>API:</b> פעיל ({datetime.now().strftime('%H:%M:%S')})</li>
                <li>💾 <b>אחסון נתונים:</b> JSON files (בוט)</li>
                <li>🚀 <b>פלטפורמה:</b> Railway.app</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
    
    return HTMLResponse(content=html_content)

# אין צורך ב-if __name__ == "__main__" - Railway יריץ עם uvicorn
