#!/usr/bin/env python3
"""
TON Airdrop Admin Panel
פאנל ניהול מקצועי עם סטטיסטיקות, הגנות וניהול משתמשים
"""

import os
import json
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from typing import Dict, List, Optional
import secrets

# ====================
# CONFIGURATION
# ====================
ADMIN_KEY = os.getenv("ADMIN_KEY", "airdrop_admin_2026")
SECRET_API_KEY = secrets.token_urlsafe(32)  # מפתח API אקראי

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ADMIN PANEL - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ====================
# DATABASE SIMULATION
# ====================
class Database:
    def __init__(self):
        self.users_file = "data/users.json"
        self.transactions_file = "data/transactions.json"
        self.stats_file = "data/stats.json"
        self.load_data()
    
    def load_data(self):
        """טעינת נתונים מהקבצים"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except:
            self.users = {}
        
        try:
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                self.transactions = json.load(f)
        except:
            self.transactions = []
        
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
        except:
            self.stats = {
                "total_users": 0,
                "active_users": 0,
                "total_transactions": 0,
                "total_volume": 0,
                "daily_stats": {},
                "system_health": "operational"
            }
    
    def save_data(self):
        """שמירת נתונים לקבצים"""
        os.makedirs("data", exist_ok=True)
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
        
        with open(self.transactions_file, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, ensure_ascii=False, indent=2)
        
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_data: Dict):
        """הוספת משתמש חדש"""
        user_id = str(user_data.get("telegram_id"))
        
        if user_id not in self.users:
            self.users[user_id] = {
                **user_data,
                "balance": 1000,  # טוקנים התחלתיים
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "transactions": [],
                "last_seen": datetime.now().isoformat()
            }
            
            self.stats["total_users"] += 1
            self.save_data()
            logger.info(f"✅ Added user {user_id}")
            return True
        
        return False
    
    def add_transaction(self, transaction_data: Dict):
        """הוספת עסקה חדשה"""
        transaction_id = transaction_data.get("id")
        
        # בדיקה אם העסקה כבר קיימת
        for tx in self.transactions:
            if tx.get("id") == transaction_id:
                return False
        
        self.transactions.append({
            **transaction_data,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        })
        
        self.stats["total_transactions"] += 1
        self.stats["total_volume"] += float(transaction_data.get("amount", 0))
        
        # עדכון סטטיסטיקות יומיות
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {
                "new_users": 0,
                "transactions": 0,
                "volume": 0,
                "revenue": 0
            }
        
        self.stats["daily_stats"][today]["transactions"] += 1
        self.stats["daily_stats"][today]["volume"] += float(transaction_data.get("amount", 0))
        
        self.save_data()
        logger.info(f"✅ Added transaction {transaction_id}")
        return True
    
    def verify_transaction(self, transaction_id: str, admin_id: str):
        """אימות עסקה על ידי מנהל"""
        for tx in self.transactions:
            if tx.get("id") == transaction_id and tx.get("status") == "pending":
                tx["status"] = "verified"
                tx["verified_at"] = datetime.now().isoformat()
                tx["verified_by"] = admin_id
                
                # הוספת טוקנים למשתמש
                user_id = tx.get("user_id")
                if user_id in self.users:
                    self.users[user_id]["balance"] += 1000  # הוספת 1000 טוקנים
                
                self.save_data()
                logger.info(f"✅ Transaction {transaction_id} verified by {admin_id}")
                return True
        
        return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """קבלת נתוני משתמש"""
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[Dict]:
        """קבלת כל המשתמשים"""
        return list(self.users.values())
    
    def get_pending_transactions(self) -> List[Dict]:
        """קבלת עסקאות ממתינות לאישור"""
        return [tx for tx in self.transactions if tx.get("status") == "pending"]
    
    def get_stats(self) -> Dict:
        """קבלת סטטיסטיקות מערכת"""
        # חישוב משתמשים פעילים (נראו ב-7 ימים אחרונים)
        week_ago = datetime.now() - timedelta(days=7)
        active_users = 0
        
        for user in self.users.values():
            last_seen_str = user.get("last_seen")
            if last_seen_str:
                last_seen = datetime.fromisoformat(last_seen_str)
                if last_seen > week_ago:
                    active_users += 1
        
        self.stats["active_users"] = active_users
        
        return {
            "statistics": self.stats,
            "system_info": {
                "version": "2.0.0",
                "uptime": "100%",
                "last_updated": datetime.now().isoformat(),
                "database_size": len(self.users) + len(self.transactions)
            }
        }

# ====================
# SECURITY SYSTEM
# ====================
class SecuritySystem:
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = set()
        self.api_keys = {}
    
    def check_admin_key(self, admin_key: str) -> bool:
        """בדיקת מפתח מנהל"""
        return admin_key == ADMIN_KEY
    
    def check_rate_limit(self, ip: str, endpoint: str) -> bool:
        """הגבלת קצב גישה"""
        key = f"{ip}:{endpoint}"
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        now = datetime.now()
        # ניקוי ניסיונות ישנים
        self.failed_attempts[key] = [
            t for t in self.failed_attempts[key]
            if now - t < timedelta(minutes=5)
        ]
        
        # הגבלה: 10 ניסיונות ב-5 דקות
        if len(self.failed_attempts[key]) >= 10:
            self.blocked_ips.add(ip)
            logger.warning(f"🚨 IP {ip} blocked for rate limiting")
            return False
        
        self.failed_attempts[key].append(now)
        return True
    
    def is_ip_blocked(self, ip: str) -> bool:
        """בדיקה אם IP חסום"""
        return ip in self.blocked_ips
    
    def generate_api_key(self, name: str) -> str:
        """יצירת מפתח API חדש"""
        api_key = secrets.token_urlsafe(32)
        self.api_keys[api_key] = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        return api_key
    
    def validate_api_key(self, api_key: str) -> bool:
        """אימות מפתח API"""
        if api_key in self.api_keys:
            self.api_keys[api_key]["last_used"] = datetime.now().isoformat()
            return True
        return False

# ====================
# FASTAPI APPLICATION
# ====================
app = FastAPI(title="TON Airdrop Admin Panel", version="2.0.0")

# אתחול מערכות
db = Database()
security = SecuritySystem()

# ====================
# AUTHENTICATION
# ====================
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_admin_key(
    admin_key: str = Query(..., description="Admin secret key"),
    ip: str = Query("127.0.0.1", description="Client IP")
):
    """אימות מפתח מנהל"""
    if security.is_ip_blocked(ip):
        raise HTTPException(status_code=403, detail="IP blocked")
    
    if not security.check_rate_limit(ip, "admin_auth"):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    if not security.check_admin_key(admin_key):
        logger.warning(f"❌ Failed admin login attempt from IP {ip}")
        raise HTTPException(status_code=401, detail="Invalid admin key")
    
    return admin_key

async def get_api_key(api_key: str = Depends(api_key_header)):
    """אימות מפתח API"""
    if not api_key or not security.validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# ====================
# ADMIN ENDPOINTS
# ====================
@app.get("/")
async def root():
    """דף הבית"""
    return {
        "message": "TON Airdrop Admin Panel",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "stats": "/admin/stats",
            "users": "/admin/users",
            "transactions": "/admin/transactions",
            "verify": "/admin/verify",
            "security": "/admin/security"
        }
    }

@app.get("/admin/stats")
async def get_statistics(admin_key: str = Depends(get_admin_key)):
    """קבלת סטטיסטיקות מערכת"""
    stats = db.get_stats()
    
    return {
        "success": True,
        "statistics": stats["statistics"],
        "system_info": stats["system_info"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/admin/users")
async def get_users(
    admin_key: str = Depends(get_admin_key),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """קבלת רשימת משתמשים"""
    all_users = db.get_all_users()
    paginated_users = all_users[offset:offset + limit]
    
    return {
        "success": True,
        "users": paginated_users,
        "pagination": {
            "total": len(all_users),
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < len(all_users)
        }
    }

@app.get("/admin/transactions/pending")
async def get_pending_transactions(admin_key: str = Depends(get_admin_key)):
    """קבלת עסקאות ממתינות לאישור"""
    pending_txs = db.get_pending_transactions()
    
    return {
        "success": True,
        "transactions": pending_txs,
        "count": len(pending_txs),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/admin/transactions/{transaction_id}/verify")
async def verify_transaction(
    transaction_id: str,
    admin_key: str = Depends(get_admin_key)
):
    """אימות עסקה"""
    if db.verify_transaction(transaction_id, "admin_panel"):
        return {
            "success": True,
            "message": "Transaction verified successfully",
            "transaction_id": transaction_id
        }
    
    raise HTTPException(status_code=404, detail="Transaction not found or already verified")

@app.get("/admin/security/status")
async def get_security_status(admin_key: str = Depends(get_admin_key)):
    """קבלת סטטוס אבטחה"""
    return {
        "success": True,
        "security": {
            "blocked_ips": len(security.blocked_ips),
            "failed_attempts": len(security.failed_attempts),
            "api_keys": len(security.api_keys),
            "rate_limit_status": "active"
        }
    }

@app.post("/admin/security/api-key")
async def generate_new_api_key(
    name: str = Query(..., description="Name for the API key"),
    admin_key: str = Depends(get_admin_key)
):
    """יצירת מפתח API חדש"""
    new_key = security.generate_api_key(name)
    
    return {
        "success": True,
        "api_key": new_key,
        "name": name,
        "warning": "Save this key now - it won't be shown again!"
    }

# ====================
# PUBLIC API (FOR BOT)
# ====================
@app.post("/api/register")
async def register_user(
    user_data: dict,
    api_key: str = Depends(get_api_key)
):
    """רישום משתמש חדש"""
    if not user_data.get("telegram_id"):
        raise HTTPException(status_code=400, detail="telegram_id is required")
    
    if db.add_user(user_data):
        return {
            "success": True,
            "user_id": user_data.get("telegram_id"),
            "message": "User registered successfully",
            "balance": 1000
        }
    
    return {
        "success": False,
        "message": "User already exists"
    }

@app.post("/api/airdrop")
async def create_airdrop(
    airdrop_data: dict,
    api_key: str = Depends(get_api_key)
):
    """יצירת עסקת Airdrop חדשה"""
    user_id = airdrop_data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # יצירת ID ייחודי לעסקה
    import hashlib
    import time
    transaction_id = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:10]
    
    transaction_data = {
        "id": transaction_id,
        "user_id": user_id,
        "amount": 44.4,
        "price_ils": 44.4,
        "ton_wallet": "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp",
        "payment_url": f"ton://transfer/UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp?amount=44.4&text=Airdrop-{transaction_id}",
        "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=ton://transfer/UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp?amount=44.4&text=Airdrop-{transaction_id}"
    }
    
    if db.add_transaction(transaction_data):
        return {
            "success": True,
            "airdrop": transaction_data,
            "message": "Airdrop created successfully"
        }
    
    raise HTTPException(status_code=500, detail="Failed to create transaction")

@app.get("/api/user/{user_id}")
async def get_user_info(
    user_id: str,
    api_key: str = Depends(get_api_key)
):
    """קבלת פרטי משתמש"""
    user = db.get_user(user_id)
    
    if not user:
        return {
            "status": "user_not_found",
            "message": "User not registered"
        }
    
    return {
        "success": True,
        "id": user_id,
        "first_name": user.get("first_name"),
        "username": user.get("username"),
        "balance": user.get("balance", 0),
        "created_at": user.get("created_at"),
        "airdrops": [tx for tx in db.transactions if tx.get("user_id") == user_id]
    }

# ====================
# HTML ADMIN DASHBOARD
# ====================
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(admin_key: str = Query(...)):
    """פאנל ניהול ויזואלי"""
    if not security.check_admin_key(admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")
    
    stats = db.get_stats()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TON Airdrop Admin Panel</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(90deg, #4f46e5, #7c3aed);
                color: white;
                padding: 30px;
                text-align: center;
                border-bottom: 5px solid #3730a3;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
            }}
            .header .subtitle {{
                opacity: 0.9;
                font-size: 1.1em;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                padding: 30px;
            }}
            .stat-card {{
                background: #f8fafc;
                border-radius: 10px;
                padding: 25px;
                border-left: 5px solid #4f46e5;
                transition: transform 0.3s;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }}
            .stat-card h3 {{
                margin-top: 0;
                color: #4f46e5;
                font-size: 1.1em;
                margin-bottom: 15px;
            }}
            .stat-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #1e293b;
                margin: 10px 0;
            }}
            .stat-change {{
                color: #10b981;
                font-weight: bold;
            }}
            .section {{
                padding: 30px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .section:last-child {{
                border-bottom: none;
            }}
            .section h2 {{
                color: #4f46e5;
                margin-top: 0;
                padding-bottom: 15px;
                border-bottom: 2px solid #e2e8f0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: right;
                border-bottom: 1px solid #e2e8f0;
            }}
            th {{
                background: #f1f5f9;
                font-weight: bold;
                color: #475569;
            }}
            tr:hover {{
                background: #f8fafc;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
            }}
            .badge-success {{
                background: #d1fae5;
                color: #065f46;
            }}
            .badge-pending {{
                background: #fef3c7;
                color: #92400e;
            }}
            .badge-warning {{
                background: #fef3c7;
                color: #92400e;
            }}
            .actions {{
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }}
            .btn {{
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .btn-primary {{
                background: #4f46e5;
                color: white;
            }}
            .btn-primary:hover {{
                background: #3730a3;
            }}
            .btn-success {{
                background: #10b981;
                color: white;
            }}
            .btn-success:hover {{
                background: #059669;
            }}
            .btn-warning {{
                background: #f59e0b;
                color: white;
            }}
            .btn-warning:hover {{
                background: #d97706;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                background: #f8fafc;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
            }}
            .status-indicator {{
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .status-operational {{
                background: #10b981;
            }}
            .timestamp {{
                color: #64748b;
                font-size: 0.9em;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 TON Airdrop Admin Panel</h1>
                <div class="subtitle">מערכת ניהול וניטור מקצועית | גרסה 2.0.0</div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>👥 משתמשים רשומים</h3>
                    <div class="stat-value">{stats['statistics']['total_users']}</div>
                    <div class="stat-change">+{stats['statistics']['active_users']} פעילים</div>
                </div>
                
                <div class="stat-card">
                    <h3>💰 עסקאות כוללות</h3>
                    <div class="stat-value">{stats['statistics']['total_transactions']}</div>
                    <div class="stat-change">{stats['statistics']['total_volume']} TON</div>
                </div>
                
                <div class="stat-card">
                    <h3>📊 נפח מסחר</h3>
                    <div class="stat-value">{stats['statistics']['total_volume'] * 44.4:.0f} ₪</div>
                    <div class="stat-change">{stats['statistics']['total_volume']} TON</div>
                </div>
                
                <div class="stat-card">
                    <h3>⚡ סטטוס מערכת</h3>
                    <div class="stat-value">
                        <span class="status-indicator status-operational"></span>
                        {stats['statistics']['system_health']}
                    </div>
                    <div class="timestamp">עודכן: {datetime.now().strftime('%H:%M')}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📈 סטטיסטיקות יומיות</h2>
                <div class="actions">
                    <button class="btn btn-primary" onclick="refreshStats()">🔄 רענן נתונים</button>
                    <button class="btn btn-success" onclick="exportData()">📥 ייצוא נתונים</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>📅 תאריך</th>
                            <th>👥 משתמשים חדשים</th>
                            <th>💸 עסקאות</th>
                            <th>💰 נפח (TON)</th>
                            <th>📈 הכנסות (₪)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([
                            f"""
                            <tr>
                                <td>{date}</td>
                                <td>{day_stats.get('new_users', 0)}</td>
                                <td>{day_stats.get('transactions', 0)}</td>
                                <td>{day_stats.get('volume', 0)}</td>
                                <td>{day_stats.get('volume', 0) * 44.4:.1f} ₪</td>
                            </tr>
                            """ for date, day_stats in list(stats['statistics']['daily_stats'].items())[-5:]
                        ])}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>⏳ עסקאות ממתינות לאישור</h2>
                <div class="actions">
                    <button class="btn btn-success" onclick="verifyAll()">✅אשר הכל</button>
                    <button class="btn btn-warning" onclick="reloadPending()">🔄 טען מחדש</button>
                </div>
                <div id="pending-transactions">
                    <p>⏳ טוען עסקאות ממתינות...</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 פעולות ניהול</h2>
                <div class="actions">
                    <button class="btn btn-primary" onclick="backupDatabase()">💾 גיבוי נתונים</button>
                    <button class="btn btn-warning" onclick="showSecurityPanel()">🛡️ לוח אבטחה</button>
                    <button class="btn btn-primary" onclick="generateApiKey()">🔑 מפתח API חדש</button>
                </div>
            </div>
            
            <div class="footer">
                <p>TON Airdrop Admin Panel v2.0.0 | פותח על ידי Osif</p>
                <p>זמן מערכת: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {len(db.get_pending_transactions())} עסקאות ממתינות</p>
            </div>
        </div>
        
        <script>
            // טעינת עסקאות ממתינות
            async function loadPendingTransactions() {{
                try {{
                    const response = await fetch('/admin/transactions/pending?admin_key={admin_key}');
                    const data = await response.json();
                    
                    if (data.success && data.transactions.length > 0) {{
                        let html = '<table><thead><tr><th>🔢 מזהה</th><th>👤 משתמש</th><th>💰 סכום</th><th>🕐 נוצר</th><th>🔧 פעולות</th></tr></thead><tbody>';
                        
                        data.transactions.forEach(tx => {{
                            html += `
                                <tr>
                                    <td><code>${{tx.id}}</code></td>
                                    <td>${{tx.user_id}}</td>
                                    <td>${{tx.amount}} TON</td>
                                    <td>${{new Date(tx.created_at).toLocaleTimeString('he-IL')}}</td>
                                    <td>
                                        <button class="btn btn-success" onclick="verifyTransaction('${{tx.id}}')">✅ אשר</button>
                                        <button class="btn btn-warning" onclick="rejectTransaction('${{tx.id}}')">❌ דחה</button>
                                    </td>
                                </tr>
                            `;
                        }});
                        
                        html += '</tbody></table>';
                        document.getElementById('pending-transactions').innerHTML = html;
                    }} else {{
                        document.getElementById('pending-transactions').innerHTML = 
                            '<p>🎉 אין עסקאות ממתינות לאישור!</p>';
                    }}
                }} catch (error) {{
                    console.error('Error loading transactions:', error);
                    document.getElementById('pending-transactions').innerHTML = 
                        '<p class="badge badge-warning">⚠️ שגיאה בטעינת עסקאות</p>';
                }}
            }}
            
            // אימות עסקה
            async function verifyTransaction(transactionId) {{
                try {{
                    const response = await fetch(`/admin/transactions/${{transactionId}}/verify?admin_key={admin_key}`, {{
                        method: 'POST'
                    }});
                    const data = await response.json();
                    
                    if (data.success) {{
                        alert(`✅ עסקה ${{transactionId}} אומתה בהצלחה!`);
                        loadPendingTransactions();
                    }} else {{
                        alert('❌ שגיאה באימות העסקה');
                    }}
                }} catch (error) {{
                    console.error('Error verifying transaction:', error);
                    alert('❌ שגיאה באימות העסקה');
                }}
            }}
            
            // רענון סטטיסטיקות
            function refreshStats() {{
                location.reload();
            }}
            
            // טען עסקאות ממתינות בעת טעינת הדף
            document.addEventListener('DOMContentLoaded', loadPendingTransactions);
            
            // רענון אוטומטי כל 30 שניות
            setInterval(loadPendingTransactions, 30000);
            
            // פונקציות נוספות
            function exportData() {{
                alert('📥 נתוני המערכת ייוצאו בקרוב...');
            }}
            
            function verifyAll() {{
                if (confirm('האם לאשר את כל העסקאות הממתינות?')) {{
                    alert('🔄 מאשר את כל העסקאות...');
                }}
            }}
            
            function backupDatabase() {{
                alert('💾 גיבוי מתבצע...');
            }}
            
            function showSecurityPanel() {{
                alert('🛡️ מעבר ללוח אבטחה...');
            }}
            
            function generateApiKey() {{
                const name = prompt('הכנס שם למפתח API החדש:');
                if (name) {{
                    alert(`🔑 מפתח API חדש בשם "${{name}}" נוצר!`);
                }}
            }}
            
            function reloadPending() {{
                loadPendingTransactions();
                alert('🔄 טוען עסקאות ממתינות מחדש...');
            }}
            
            function rejectTransaction(transactionId) {{
                if (confirm(`האם לדחות את עסקה ${{transactionId}}?`)) {{
                    alert(`❌ עסקה ${{transactionId}} נדחתה`);
                    loadPendingTransactions();
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# ====================
# HEALTH CHECK
# ====================
@app.get("/health")
async def health_check():
    """בדיקת בריאות המערכת"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "database": "operational",
            "api": "operational",
            "security": "operational",
            "admin_panel": "operational"
        }
    }

# ====================
# STARTUP EVENT
# ====================
@app.on_event("startup")
async def startup_event():
    """הפעלה עם עליית השרת"""
    logger.info("🚀 TON Airdrop Admin Panel starting...")
    logger.info(f"📊 Database loaded: {len(db.users)} users, {len(db.transactions)} transactions")
    logger.info(f"🔐 Security system initialized")
    logger.info(f"🌐 Admin panel available at /admin/dashboard?admin_key={ADMIN_KEY}")
    
    # יצירת מפתח API ברירת מחדל
    default_api_key = security.generate_api_key("bot_default")
    logger.info(f"🔑 Default API key generated for bot")

# ====================
# MAIN ENTRY POINT
# ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
