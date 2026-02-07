from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import sqlite3
import json
import os

app = FastAPI(title="SLH Airdrop System", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================
# DATABASE SETUP
# ====================
def get_db_path():
    """מחזיר את הנתיב למסד הנתונים"""
    if os.path.exists("data/airdrop.db"):
        return "data/airdrop.db"
    return "airdrop.db"

def init_database():
    """מאתחל את מסד הנתונים"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # טבלת משתמשים
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            username TEXT,
            first_name TEXT,
            phone TEXT,
            wallet_address TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            tokens INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            total_bonus INTEGER DEFAULT 0
        )
    ''')
    
    # טבלת עסקאות
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT,
            transaction_hash TEXT UNIQUE,
            amount REAL,
            currency TEXT DEFAULT 'TON',
            status TEXT DEFAULT 'pending',
            tokens_awarded INTEGER DEFAULT 1000,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP,
            confirmed_by TEXT
        )
    ''')
    
    # טבלת הפניות
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id TEXT,
            referred_id TEXT,
            bonus_awarded INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # טבלת לוגים
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT,
            action TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# ====================
# MODELS
# ====================
class UserRegister(BaseModel):
    telegram_id: str
    username: str
    first_name: str

class TransactionSubmit(BaseModel):
    telegram_id: str
    transaction_hash: str
    amount: float

class AdminAction(BaseModel):
    admin_key: str
    action: str
    data: dict

# ====================
# HELPER FUNCTIONS
# ====================
def get_db():
    """מחזיר חיבור למסד נתונים"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ====================
# USER ENDPOINTS
# ====================
@app.post("/api/users/register")
async def register_user(user: UserRegister):
    """רושם משתמש חדש"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user.telegram_id, user.username, user.first_name))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"status": "success", "message": "User registered"}
        else:
            return {"status": "exists", "message": "User already exists"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/users/submit_transaction")
async def submit_transaction(transaction: TransactionSubmit):
    """מקבל עסקה חדשה"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # בדוק אם המשתמש קיים
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (transaction.telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # הוסף את העסקה
        cursor.execute('''
            INSERT INTO transactions (telegram_id, transaction_hash, amount, status)
            VALUES (?, ?, ?, 'pending')
        ''', (transaction.telegram_id, transaction.transaction_hash, transaction.amount))
        
        conn.commit()
        
        return {
            "status": "success", 
            "message": "Transaction submitted for approval",
            "transaction_id": transaction.transaction_hash
        }
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Transaction already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/users/{telegram_id}/status")
async def get_user_status(telegram_id: str):
    """מחזיר סטטוס משתמש"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # נתוני משתמש
        cursor.execute('''
            SELECT u.*, 
                   COUNT(DISTINCT t.id) as total_transactions,
                   COUNT(DISTINCT r.id) as total_referrals,
                   SUM(CASE WHEN t.status = 'confirmed' THEN t.tokens_awarded ELSE 0 END) as confirmed_tokens
            FROM users u
            LEFT JOIN transactions t ON u.telegram_id = t.telegram_id
            LEFT JOIN referrals r ON u.telegram_id = r.referrer_id
            WHERE u.telegram_id = ?
            GROUP BY u.telegram_id
        ''', (telegram_id,))
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # עסקאות אחרונות
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE telegram_id = ? 
            ORDER BY submitted_at DESC 
            LIMIT 5
        ''', (telegram_id,))
        
        transactions = cursor.fetchall()
        
        return {
            "user": dict(user),
            "transactions": [dict(tx) for tx in transactions],
            "total_value": user["confirmed_tokens"] * 44.4 / 1000 if user["confirmed_tokens"] else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ====================
# ADMIN ENDPOINTS
# ====================
@app.post("/api/admin/action")
async def admin_action(action: AdminAction):
    """מבצע פעולת מנהל"""
    if action.admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if action.action == "confirm_transaction":
            tx_hash = action.data.get("transaction_hash")
            
            # עדכן את העסקה
            cursor.execute('''
                UPDATE transactions 
                SET status = 'confirmed', 
                    confirmed_at = CURRENT_TIMESTAMP,
                    confirmed_by = ?
                WHERE transaction_hash = ?
            ''', (action.admin_key[:10], tx_hash))
            
            # עדכן את הטוקנים של המשתמש
            cursor.execute('''
                UPDATE users 
                SET tokens = tokens + 1000
                WHERE telegram_id = (SELECT telegram_id FROM transactions WHERE transaction_hash = ?)
            ''', (tx_hash,))
            
            # רשום לוג
            cursor.execute('''
                INSERT INTO admin_logs (admin_id, action, details)
                VALUES (?, 'confirm_transaction', ?)
            ''', (action.admin_key[:10], f"Confirmed transaction: {tx_hash}"))
            
            conn.commit()
            
            return {"status": "success", "message": "Transaction confirmed"}
            
        elif action.action == "add_bonus":
            telegram_id = action.data.get("telegram_id")
            bonus = action.data.get("bonus", 50)
            
            cursor.execute('''
                UPDATE users 
                SET total_bonus = total_bonus + ?
                WHERE telegram_id = ?
            ''', (bonus, telegram_id))
            
            conn.commit()
            
            return {"status": "success", "message": f"Added {bonus} bonus tokens"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/admin/stats")
async def get_admin_stats(admin_key: str):
    """מחזיר סטטיסטיקות מערכת"""
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # סטטיסטיקות בסיסיות
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()["total_users"]
        
        cursor.execute("SELECT COUNT(*) as total_transactions FROM transactions")
        total_transactions = cursor.fetchone()["total_transactions"]
        
        cursor.execute("SELECT COUNT(*) as pending_transactions FROM transactions WHERE status = 'pending'")
        pending_transactions = cursor.fetchone()["pending_transactions"]
        
        cursor.execute("SELECT SUM(amount) as total_ton FROM transactions WHERE status = 'confirmed'")
        total_ton = cursor.fetchone()["total_ton"] or 0
        
        cursor.execute("SELECT SUM(tokens) as total_tokens FROM users")
        total_tokens = cursor.fetchone()["total_tokens"] or 0
        
        # עסקאות אחרונות
        cursor.execute('''
            SELECT t.*, u.username, u.first_name 
            FROM transactions t
            JOIN users u ON t.telegram_id = u.telegram_id
            ORDER BY t.submitted_at DESC
            LIMIT 20
        ''')
        recent_transactions = cursor.fetchall()
        
        # משתמשים חדשים
        cursor.execute('''
            SELECT * FROM users 
            ORDER BY registered_at DESC 
            LIMIT 20
        ''')
        recent_users = cursor.fetchall()
        
        return {
            "system_stats": {
                "total_users": total_users,
                "total_transactions": total_transactions,
                "pending_transactions": pending_transactions,
                "total_ton_received": total_ton,
                "total_tokens_distributed": total_tokens,
                "total_value_ils": total_ton * 44.4
            },
            "recent_transactions": [dict(tx) for tx in recent_transactions],
            "recent_users": [dict(user) for user in recent_users],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ====================
# PUBLIC ENDPOINTS
# ====================
@app.get("/")
async def root():
    return {"message": "SLH Airdrop System", "status": "online", "version": "2.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ====================
# ADMIN DASHBOARD (HTML)
# ====================
@app.get("/admin/dashboard")
async def admin_dashboard(admin_key: str):
    """פאנל ניהול HTML"""
    if admin_key != "airdrop_admin_2026":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    html_content = '''
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SLH Airdrop - Admin Dashboard</title>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
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
                margin: 0;
                font-size: 2.5em;
            }
            .header p {
                opacity: 0.9;
                margin: 10px 0 0 0;
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
            .table-container {
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
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
            }
            .status-confirmed {
                background: #d1fae5;
                color: #065f46;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8em;
            }
            .action-btn {
                background: #4f46e5;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.9em;
                transition: background 0.3s;
            }
            .action-btn:hover {
                background: #4338ca;
            }
            .bonus-form {
                background: #f0f9ff;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .bonus-form input {
                padding: 10px;
                margin: 5px;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                width: 200px;
            }
            .tabs {
                display: flex;
                border-bottom: 2px solid #e2e8f0;
                margin-bottom: 20px;
            }
            .tab {
                padding: 15px 30px;
                cursor: pointer;
                color: #64748b;
                border-bottom: 3px solid transparent;
            }
            .tab.active {
                color: #4f46e5;
                border-bottom: 3px solid #4f46e5;
                font-weight: bold;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .alert {
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                display: none;
            }
            .alert.success {
                background: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
            }
            .alert.error {
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
                <p>מערכת ניהול מתקדמת לאישור עסקאות והפצת טוקנים</p>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('dashboard')">📊 לוח מחוונים</div>
                <div class="tab" onclick="showTab('transactions')">💳 עסקאות</div>
                <div class="tab" onclick="showTab('users')">👥 משתמשים</div>
                <div class="tab" onclick="showTab('bonus')">🎁 ניהול בונוסים</div>
                <div class="tab" onclick="showTab('settings')">⚙️ הגדרות</div>
            </div>
            
            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <div class="section">
                    <h2>📈 סטטיסטיקות מערכת</h2>
                    <div class="stats-grid" id="statsGrid">
                        <!-- הסטטיסטיקות יוטענו כאן -->
                        <div class="stat-card">
                            <div class="stat-label">👥 משתמשים רשומים</div>
                            <div class="stat-value" id="totalUsers">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">💳 עסקאות</div>
                            <div class="stat-value" id="totalTransactions">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">⏳ ממתינים לאישור</div>
                            <div class="stat-value" id="pendingTransactions">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">💰 TON שנאסף</div>
                            <div class="stat-value" id="totalTon">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">🎯 טוקנים שחולקו</div>
                            <div class="stat-value" id="totalTokens">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">💸 שווי כולל</div>
                            <div class="stat-value" id="totalValue">0 ₪</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📊 גרף פעילות</h2>
                    <div style="height: 300px; background: #f8fafc; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #64748b;">
                        📈 גרף פעילות - זמין בגרסה מתקדמת
                    </div>
                </div>
            </div>
            
            <!-- Transactions Tab -->
            <div id="transactions" class="tab-content">
                <div class="section">
                    <h2>💳 עסקאות אחרונות</h2>
                    <div class="table-container">
                        <table id="transactionsTable">
                            <thead>
                                <tr>
                                    <th>מזהה</th>
                                    <th>משתמש</th>
                                    <th>מספר עסקה</th>
                                    <th>סכום</th>
                                    <th>סטטוס</th>
                                    <th>תאריך</th>
                                    <th>פעולות</th>
                                </tr>
                            </thead>
                            <tbody id="transactionsBody">
                                <!-- העסקאות יוטענו כאן -->
                                <tr><td colspan="7" style="text-align:center">טוען עסקאות...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Users Tab -->
            <div id="users" class="tab-content">
                <div class="section">
                    <h2>👥 משתמשים אחרונים</h2>
                    <div class="table-container">
                        <table id="usersTable">
                            <thead>
                                <tr>
                                    <th>מזהה</th>
                                    <th>שם</th>
                                    <th>Username</th>
                                    <th>טוקנים</th>
                                    <th>הפניות</th>
                                    <th>בונוסים</th>
                                    <th>תאריך הרשמה</th>
                                </tr>
                            </thead>
                            <tbody id="usersBody">
                                <!-- המשתמשים יוטענו כאן -->
                                <tr><td colspan="7" style="text-align:center">טוען משתמשים...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Bonus Tab -->
            <div id="bonus" class="tab-content">
                <div class="section">
                    <h2>🎁 ניהול בונוסים</h2>
                    <div class="bonus-form">
                        <h3>הוספת בונוס למשתמש</h3>
                        <input type="text" id="bonusUserId" placeholder="מספר טלגרם של משתמש">
                        <input type="number" id="bonusAmount" placeholder="כמות בונוס" value="50">
                        <button class="action-btn" onclick="addBonus()">הוסף בונוס</button>
                    </div>
                    
                    <div class="bonus-form">
                        <h3>הפצת בונוסים קבוצתית</h3>
                        <input type="number" id="groupBonusAmount" placeholder="כמות בונוס לכולם" value="10">
                        <button class="action-btn" onclick="addGroupBonus()">הפץ לכולם</button>
                    </div>
                </div>
            </div>
            
            <!-- Settings Tab -->
            <div id="settings" class="tab-content">
                <div class="section">
                    <h2>⚙️ הגדרות מערכת</h2>
                    <div style="padding: 20px; background: #f8fafc; border-radius: 10px;">
                        <h3>פרמטרים להפצה</h3>
                        <p><strong>מחיר טוקן:</strong> 44.4 ₪ = 1000 טוקנים</p>
                        <p><strong>בונוס הפניה:</strong> 50 טוקנים</p>
                        <p><strong>בונוס שיתוף:</strong> 30 טוקנים</p>
                        <p><strong>הגבלת משתתפים:</strong> 100 משתמשים</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding: 20px; background: #f0f9ff; border-radius: 10px;">
                        <h3>יצוא נתונים</h3>
                        <button class="action-btn" onclick="exportData('users')">📥 יצוא משתמשים</button>
                        <button class="action-btn" onclick="exportData('transactions')">📥 יצוא עסקאות</button>
                    </div>
                </div>
            </div>
            
            <div id="alert" class="alert"></div>
        </div>

        <script>
            const API_BASE = window.location.origin;
            const ADMIN_KEY = "airdrop_admin_2026";
            
            // הצגת טאבים
            function showTab(tabName) {
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                document.querySelector(`.tab[onclick*="${tabName}"]`).classList.add('active');
                document.getElementById(tabName).classList.add('active');
                
                if (tabName === 'dashboard') loadStats();
                if (tabName === 'transactions') loadTransactions();
                if (tabName === 'users') loadUsers();
            }
            
            // טען סטטיסטיקות
            async function loadStats() {
                try {
                    const response = await fetch(`${API_BASE}/api/admin/stats?admin_key=${ADMIN_KEY}`);
                    const data = await response.json();
                    
                    if (data.system_stats) {
                        document.getElementById('totalUsers').textContent = data.system_stats.total_users;
                        document.getElementById('totalTransactions').textContent = data.system_stats.total_transactions;
                        document.getElementById('pendingTransactions').textContent = data.system_stats.pending_transactions;
                        document.getElementById('totalTon').textContent = data.system_stats.total_ton_received.toFixed(2);
                        document.getElementById('totalTokens').textContent = data.system_stats.total_tokens_distributed;
                        document.getElementById('totalValue').textContent = data.system_stats.total_value_ils.toFixed(1) + ' ₪';
                    }
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }
            
            // טען עסקאות
            async function loadTransactions() {
                try {
                    const response = await fetch(`${API_BASE}/api/admin/stats?admin_key=${ADMIN_KEY}`);
                    const data = await response.json();
                    
                    const tbody = document.getElementById('transactionsBody');
                    tbody.innerHTML = '';
                    
                    if (data.recent_transactions && data.recent_transactions.length > 0) {
                        data.recent_transactions.forEach(tx => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${tx.id}</td>
                                <td>${tx.first_name} (@${tx.username})</td>
                                <td><code>${tx.transaction_hash.substring(0, 20)}...</code></td>
                                <td>${tx.amount} TON</td>
                                <td><span class="status-${tx.status}">${tx.status}</span></td>
                                <td>${new Date(tx.submitted_at).toLocaleString('he-IL')}</td>
                                <td>
                                    ${tx.status === 'pending' ? 
                                        `<button class="action-btn" onclick="confirmTransaction('${tx.transaction_hash}')">✅ אשר</button>` : 
                                        '✅ מאושר'}
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                    } else {
                        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">אין עסקאות</td></tr>';
                    }
                } catch (error) {
                    console.error('Error loading transactions:', error);
                }
            }
            
            // טען משתמשים
            async function loadUsers() {
                try {
                    const response = await fetch(`${API_BASE}/api/admin/stats?admin_key=${ADMIN_KEY}`);
                    const data = await response.json();
                    
                    const tbody = document.getElementById('usersBody');
                    tbody.innerHTML = '';
                    
                    if (data.recent_users && data.recent_users.length > 0) {
                        data.recent_users.forEach(user => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${user.telegram_id}</td>
                                <td>${user.first_name}</td>
                                <td>@${user.username || 'ללא'}</td>
                                <td>${user.tokens}</td>
                                <td>${user.referrals}</td>
                                <td>${user.total_bonus}</td>
                                <td>${new Date(user.registered_at).toLocaleString('he-IL')}</td>
                            `;
                            tbody.appendChild(row);
                        });
                    } else {
                        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">אין משתמשים</td></tr>';
                    }
                } catch (error) {
                    console.error('Error loading users:', error);
                }
            }
            
            // אשר עסקה
            async function confirmTransaction(txHash) {
                if (!confirm('האם לאשר עסקה זו?')) return;
                
                try {
                    const response = await fetch(`${API_BASE}/api/admin/action`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            admin_key: ADMIN_KEY,
                            action: 'confirm_transaction',
                            data: { transaction_hash: txHash }
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        showAlert('✅ העסקה אושרה בהצלחה!', 'success');
                        loadTransactions();
                        loadStats();
                    } else {
                        showAlert('❌ שגיאה באישור העסקה', 'error');
                    }
                } catch (error) {
                    showAlert('❌ שגיאת רשת', 'error');
                    console.error('Error confirming transaction:', error);
                }
            }
            
            // הוסף בונוס
            async function addBonus() {
                const userId = document.getElementById('bonusUserId').value;
                const amount = document.getElementById('bonusAmount').value;
                
                if (!userId || !amount) {
                    showAlert('❌ מלא את כל השדות', 'error');
                    return;
                }
                
                try {
                    const response = await fetch(`${API_BASE}/api/admin/action`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            admin_key: ADMIN_KEY,
                            action: 'add_bonus',
                            data: { telegram_id: userId, bonus: parseInt(amount) }
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        showAlert(`✅ נוספו ${amount} טוקני בונוס למשתמש ${userId}`, 'success');
                        document.getElementById('bonusUserId').value = '';
                        loadUsers();
                    } else {
                        showAlert('❌ שגיאה בהוספת בונוס', 'error');
                    }
                } catch (error) {
                    showAlert('❌ שגיאת רשת', 'error');
                }
            }
            
            // הצג התראה
            function showAlert(message, type) {
                const alert = document.getElementById('alert');
                alert.textContent = message;
                alert.className = `alert ${type}`;
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
async def startup_event():
    init_database()
    print("🚀 SLH Airdrop API v2.0 Started")
    print("📊 Admin: /admin/dashboard?admin_key=airdrop_admin_2026")
    print("🌐 Health: /health")
    print("📚 Docs: /docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
