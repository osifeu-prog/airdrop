from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import sqlite3
import os
import json
from typing import Optional

app = FastAPI(title="SLH Airdrop API", version="3.0")

# מסד נתונים
DB_PATH = "data/airdrop.db"

def init_db():
    """מאתחל את מסד הנתונים"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # טבלת משתמשים
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            username TEXT,
            first_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tokens INTEGER DEFAULT 0
        )
    ''')
    
    # טבלת עסקאות
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT,
            transaction_hash TEXT UNIQUE,
            amount REAL DEFAULT 44.4,
            status TEXT DEFAULT 'pending',
            tokens_awarded INTEGER DEFAULT 1000,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def get_db():
    """מחזיר חיבור למסד נתונים"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ====================
# MIDDLEWARE - CORS
# ====================
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================
# PUBLIC ENDPOINTS
# ====================
@app.get("/")
async def root():
    return {
        "service": "SLH Airdrop API",
        "status": "online",
        "version": "3.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "register": "/api/register?telegram_id=...&username=...&first_name=...",
            "submit": "/api/submit?telegram_id=...&transaction_hash=...",
            "user": "/api/user/{telegram_id}",
            "admin": "/admin/dashboard?admin_key=airdrop_admin_2026"
        }
    }

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "healthy", "timestamp": datetime.now().isoformat()})

# ====================
# USER ENDPOINTS (Form data support)
# ====================
@app.post("/api/register")
async def register_user(
    telegram_id: str = Form(...),
    username: str = Form(""),
    first_name: str = Form("User")
):
    """רושם משתמש חדש - תומך ב-Form data"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (telegram_id, username, first_name))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"status": "success", "message": "User registered successfully"}
        else:
            return {"status": "exists", "message": "User already exists"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    finally:
        conn.close()

@app.post("/api/submit")
async def submit_transaction(
    telegram_id: str = Form(...),
    transaction_hash: str = Form(...),
    amount: float = Form(44.4)
):
    """מקבל עסקה חדשה"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO transactions (telegram_id, transaction_hash, amount, status)
            VALUES (?, ?, ?, 'pending')
            ON CONFLICT(transaction_hash) DO NOTHING
        ''', (telegram_id, transaction_hash, amount))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return {
                "status": "success",
                "message": "Transaction submitted for approval",
                "transaction_hash": transaction_hash
            }
        else:
            return {"status": "exists", "message": "Transaction already exists"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    finally:
        conn.close()

@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: str):
    """מחזיר נתוני משתמש"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "User not found"}
            )
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE telegram_id = ? 
            ORDER BY submitted_at DESC
        ''', (telegram_id,))
        
        transactions = cursor.fetchall()
        
        return {
            "status": "success",
            "user": {
                "telegram_id": user["telegram_id"],
                "username": user["username"],
                "first_name": user["first_name"],
                "tokens": user["tokens"],
                "registered_at": user["registered_at"]
            },
            "transactions": [
                {
                    "id": tx["id"],
                    "transaction_hash": tx["transaction_hash"],
                    "amount": tx["amount"],
                    "status": tx["status"],
                    "submitted_at": tx["submitted_at"]
                }
                for tx in transactions
            ],
            "total_value": user["tokens"] * 44.4 / 1000
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    finally:
        conn.close()

# ====================
# ADMIN ENDPOINTS
# ====================
@app.post("/api/admin/confirm")
async def confirm_transaction(
    transaction_hash: str = Form(...),
    admin_key: str = Form(...)
):
    """מאשר עסקה"""
    if admin_key != "airdrop_admin_2026":
        return JSONResponse(
            status_code=403,
            content={"status": "error", "message": "Invalid admin key"}
        )
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE transactions 
            SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
            WHERE transaction_hash = ?
        ''', (transaction_hash,))
        
        cursor.execute('''
            UPDATE users 
            SET tokens = tokens + 1000
            WHERE telegram_id = (SELECT telegram_id FROM transactions WHERE transaction_hash = ?)
        ''', (transaction_hash,))
        
        conn.commit()
        
        return {"status": "success", "message": "Transaction confirmed"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    finally:
        conn.close()

@app.get("/api/admin/stats")
async def get_stats(admin_key: str):
    """מחזיר סטטיסטיקות מערכת"""
    if admin_key != "airdrop_admin_2026":
        return JSONResponse(
            status_code=403,
            content={"status": "error", "message": "Invalid admin key"}
        )
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as total_transactions FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as pending FROM transactions WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) as total_ton FROM transactions WHERE status = 'confirmed'")
        total_ton = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT t.*, u.username, u.first_name 
            FROM transactions t
            JOIN users u ON t.telegram_id = u.telegram_id
            WHERE t.status = 'pending'
            ORDER BY t.submitted_at DESC
            LIMIT 10
        ''')
        
        pending_transactions = cursor.fetchall()
        
        return {
            "status": "success",
            "stats": {
                "total_users": total_users,
                "total_transactions": total_transactions,
                "pending_transactions": pending,
                "total_ton_received": total_ton,
                "total_value_ils": total_ton * 44.4
            },
            "pending_transactions": [
                {
                    "id": tx["id"],
                    "transaction_hash": tx["transaction_hash"],
                    "telegram_id": tx["telegram_id"],
                    "username": tx["username"],
                    "first_name": tx["first_name"],
                    "amount": tx["amount"],
                    "submitted_at": tx["submitted_at"]
                }
                for tx in pending_transactions
            ]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    finally:
        conn.close()

# ====================
# פאנל ניהול HTML
# ====================
@app.get("/admin/dashboard")
async def admin_dashboard(admin_key: str):
    """פאנל ניהול מתקדם"""
    if admin_key != "airdrop_admin_2026":
        return HTMLResponse(content="<h1>❌ גישה לא מורשית</h1>", status_code=403)
    
    html_content = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SLH Airdrop - פאנל ניהול</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                opacity: 0.9;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8fafc;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                text-align: center;
                border-left: 5px solid #4f46e5;
                transition: transform 0.3s;
            }
            .stat-card:hover {
                transform: translateY(-5px);
            }
            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
                color: #4f46e5;
                margin: 10px 0;
            }
            .stat-label {
                color: #64748b;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .section {
                padding: 30px;
                border-bottom: 1px solid #e2e8f0;
            }
            .section h2 {
                color: #1e293b;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #4f46e5;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 15px;
                text-align: right;
                border-bottom: 1px solid #e2e8f0;
            }
            th {
                background: #f1f5f9;
                color: #475569;
                font-weight: 600;
            }
            tr:hover {
                background: #f8fafc;
            }
            .status-pending {
                background: #fef3c7;
                color: #92400e;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8em;
                display: inline-block;
            }
            .btn {
                background: #4f46e5;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.9em;
                transition: background 0.3s;
                margin: 5px;
            }
            .btn:hover {
                background: #4338ca;
            }
            .btn-success {
                background: #10b981;
            }
            .btn-success:hover {
                background: #0da271;
            }
            .alert {
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                display: none;
            }
            .alert-success {
                background: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
            }
            .alert-error {
                background: #fee2e2;
                color: #991b1b;
                border: 1px solid #fecaca;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 SLH Airdrop - פאנל ניהול</h1>
                <p>ניהול מערכת Airdrop ואישור עסקאות</p>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <!-- סטטיסטיקות יוטענו כאן -->
            </div>
            
            <div class="section">
                <h2>📝 עסקאות ממתינות לאישור</h2>
                <div id="pendingTransactions">
                    <p>טוען עסקאות...</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 כלים מהירים</h2>
                <div>
                    <button class="btn" onclick="loadStats()">🔄 רענן נתונים</button>
                    <button class="btn" onclick="testAPI()">🧪 בדיקת API</button>
                    <button class="btn" onclick="exportData()">📥 יצוא נתונים</button>
                </div>
            </div>
            
            <div id="alert" class="alert"></div>
        </div>

        <script>
            const API_BASE = window.location.origin;
            const ADMIN_KEY = "airdrop_admin_2026";
            
            // טען סטטיסטיקות
            async function loadStats() {
                try {
                    const response = await fetch(`${API_BASE}/api/admin/stats?admin_key=${ADMIN_KEY}`);
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        // עדכן סטטיסטיקות
                        const stats = data.stats;
                        const statsGrid = document.getElementById('statsGrid');
                        
                        statsGrid.innerHTML = `
                            <div class="stat-card">
                                <div class="stat-label">👥 משתמשים רשומים</div>
                                <div class="stat-value">${stats.total_users}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">💳 סה"כ עסקאות</div>
                                <div class="stat-value">${stats.total_transactions}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">⏳ ממתינים לאישור</div>
                                <div class="stat-value">${stats.pending_transactions}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">💰 TON שנאסף</div>
                                <div class="stat-value">${stats.total_ton_received.toFixed(2)}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">💸 שווי כולל</div>
                                <div class="stat-value">${stats.total_value_ils.toFixed(1)} ₪</div>
                            </div>
                        `;
                        
                        // טען עסקאות ממתינות
                        loadPendingTransactions(data.pending_transactions || []);
                        
                        showAlert('✅ נתונים עודכנו בהצלחה', 'success');
                    } else {
                        showAlert('❌ שגיאה בטעינת נתונים', 'error');
                    }
                } catch (error) {
                    console.error('Error loading stats:', error);
                    showAlert('❌ שגיאת רשת', 'error');
                }
            }
            
            // טען עסקאות ממתינות
            function loadPendingTransactions(transactions) {
                const container = document.getElementById('pendingTransactions');
                
                if (!transactions || transactions.length === 0) {
                    container.innerHTML = '<p>אין עסקאות ממתינות לאישור</p>';
                    return;
                }
                
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>מזהה</th>
                                <th>משתמש</th>
                                <th>מספר עסקה</th>
                                <th>סכום</th>
                                <th>תאריך</th>
                                <th>פעולות</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                transactions.forEach(tx => {
                    html += `
                        <tr>
                            <td>${tx.id}</td>
                            <td>${tx.first_name} (@${tx.username})</td>
                            <td><code>${tx.transaction_hash.substring(0, 20)}...</code></td>
                            <td>${tx.amount} TON</td>
                            <td>${new Date(tx.submitted_at).toLocaleString('he-IL')}</td>
                            <td>
                                <button class="btn btn-success" onclick="confirmTransaction('${tx.transaction_hash}')">
                                    ✅ אשר
                                </button>
                            </td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table>';
                container.innerHTML = html;
            }
            
            // אשר עסקה
            async function confirmTransaction(txHash) {
                if (!confirm('האם לאשר עסקה זו?')) return;
                
                try {
                    const formData = new FormData();
                    formData.append('transaction_hash', txHash);
                    formData.append('admin_key', ADMIN_KEY);
                    
                    const response = await fetch(`${API_BASE}/api/admin/confirm`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        showAlert('✅ העסקה אושרה בהצלחה!', 'success');
                        loadStats();
                    } else {
                        showAlert('❌ שגיאה באישור העסקה', 'error');
                    }
                } catch (error) {
                    showAlert('❌ שגיאת רשת', 'error');
                    console.error('Error confirming transaction:', error);
                }
            }
            
            // בדיקת API
            async function testAPI() {
                try {
                    const response = await fetch(`${API_BASE}/health`);
                    const data = await response.json();
                    
                    if (data.status === 'healthy') {
                        showAlert('✅ API פעיל וזמין', 'success');
                    } else {
                        showAlert('⚠️ API לא בריא', 'error');
                    }
                } catch (error) {
                    showAlert('❌ API לא זמין', 'error');
                }
            }
            
            // הצג התראה
            function showAlert(message, type) {
                const alert = document.getElementById('alert');
                alert.textContent = message;
                alert.className = `alert alert-${type}`;
                alert.style.display = 'block';
                
                setTimeout(() => {
                    alert.style.display = 'none';
                }, 5000);
            }
            
            // טען נתונים ראשוניים
            loadStats();
        </script>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html_content)

# ====================
# STARTUP
# ====================
@app.on_event("startup")
async def startup():
    init_db()
    print("=" * 50)
    print("🚀 SLH Airdrop API v3.0 - Ready for Production!")
    print("🌐 URL: https://successful-fulfillment-production.up.railway.app")
    print("📊 Admin: /admin/dashboard?admin_key=airdrop_admin_2026")
    print("❤️  Health: /health")
    print("📚 API Docs: /docs")
    print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
