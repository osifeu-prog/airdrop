from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime
import sqlite3
import os
import json

app = FastAPI(title="SLH Airdrop API", version="2.1")

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
            amount REAL,
            status TEXT DEFAULT 'pending',
            tokens_awarded INTEGER DEFAULT 1000,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ מסד נתונים אותחל")

def get_db():
    """מחזיר חיבור למסד נתונים"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoints בסיסיים
@app.get("/")
async def root():
    return {
        "service": "SLH Airdrop API",
        "status": "online",
        "version": "2.1",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/register")
async def register_user(telegram_id: str, username: str, first_name: str):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (telegram_id, username, first_name))
        
        conn.commit()
        return {"status": "success", "message": "User registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/submit")
async def submit_transaction(telegram_id: str, transaction_hash: str, amount: float = 44.4):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO transactions (telegram_id, transaction_hash, amount, status)
            VALUES (?, ?, ?, 'pending')
        ''', (telegram_id, transaction_hash, amount))
        
        conn.commit()
        return {
            "status": "success",
            "message": "Transaction submitted",
            "transaction_hash": transaction_hash
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Transaction already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: str):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE telegram_id = ? 
            ORDER BY submitted_at DESC
        ''', (telegram_id,))
        
        transactions = cursor.fetchall()
        
        return {
            "user": dict(user),
            "transactions": [dict(tx) for tx in transactions],
            "total_tokens": user["tokens"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/admin/confirm")
async def confirm_transaction(transaction_hash: str, admin_key: str):
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/admin/stats")
async def get_stats(admin_key: str):
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
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
        
        return {
            "total_users": total_users,
            "total_transactions": total_transactions,
            "pending_transactions": pending,
            "total_ton": total_ton,
            "total_value_ils": total_ton * 44.4
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# פאנל ניהול HTML
@app.get("/admin/dashboard")
async def admin_dashboard(admin_key: str):
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    html = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SLH Airdrop - Admin</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #4a6fa5; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .stat-value { font-size: 2em; font-weight: bold; color: #4a6fa5; }
            table { width: 100%; background: white; border-collapse: collapse; }
            th, td { padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; }
            .btn { background: #4a6fa5; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #3a5a80; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 SLH Airdrop - פאנל ניהול</h1>
                <p>מערכת ניהול עסקאות ואישורים</p>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div>👥 משתמשים</div>
                    <div class="stat-value" id="totalUsers">0</div>
                </div>
                <div class="stat-card">
                    <div>💳 עסקאות</div>
                    <div class="stat-value" id="totalTransactions">0</div>
                </div>
                <div class="stat-card">
                    <div>⏳ ממתינים</div>
                    <div class="stat-value" id="pending">0</div>
                </div>
                <div class="stat-card">
                    <div>💰 TON שנאסף</div>
                    <div class="stat-value" id="totalTon">0</div>
                </div>
            </div>
            
            <h2>📝 עסקאות ממתינות לאישור</h2>
            <div id="transactionsTable">
                <p>טוען עסקאות...</p>
            </div>
            
            <h2>🔧 כלים מהירים</h2>
            <div>
                <button class="btn" onclick="loadStats()">🔄 רענן נתונים</button>
                <button class="btn" onclick="exportData()">📥 יצוא נתונים</button>
            </div>
        </div>
        
        <script>
            const API_BASE = window.location.origin;
            const ADMIN_KEY = "airdrop_admin_2026";
            
            async function loadStats() {
                try {
                    const response = await fetch(`${API_BASE}/api/admin/stats?admin_key=${ADMIN_KEY}`);
                    const data = await response.json();
                    
                    document.getElementById('totalUsers').textContent = data.total_users;
                    document.getElementById('totalTransactions').textContent = data.total_transactions;
                    document.getElementById('pending').textContent = data.pending_transactions;
                    document.getElementById('totalTon').textContent = data.total_ton.toFixed(2);
                    
                    // טען עסקאות
                    loadTransactions();
                } catch (error) {
                    console.error('Error loading stats:', error);
                    alert('שגיאה בטעינת נתונים');
                }
            }
            
            async function loadTransactions() {
                try {
                    // בדוגמה זו - אפשר להרחיב לטעינת עסקאות אמיתיות
                    const table = document.getElementById('transactionsTable');
                    table.innerHTML = '<p>פונקציונליות מלאה זמינה בגרסה מתקדמת</p>';
                } catch (error) {
                    console.error('Error loading transactions:', error);
                }
            }
            
            function exportData() {
                alert('יצוא נתונים - זמין בגרסה מלאה');
            }
            
            // טען נתונים בהתחלה
            loadStats();
        </script>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html)

# אתחול מסד נתונים בהפעלה
@app.on_event("startup")
async def startup():
    init_db()
    print("=" * 50)
    print("🚀 SLH Airdrop API v2.1 התחיל")
    print("📊 Admin: /admin/dashboard?admin_key=airdrop_admin_2026")
    print("❤️  Health: /health")
    print("📚 Docs: /docs")
    print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
