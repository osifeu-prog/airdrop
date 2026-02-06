from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os
import hashlib
import time
from datetime import datetime

app = FastAPI(
    title="🚀 Airdrop TON API",
    version="2.0",
    description="API יציב למבצע Airdrop עם Telegram"
)

# בסיס נתונים פשוט בזכרון
users_db = {}
airdrops_db = {}
stats = {
    "total_users": 0,
    "total_airdrops": 0,
    "pending_payments": 0,
    "completed_payments": 0,
    "total_volume_ton": 0
}

class UserRegister(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None

class AirdropRequest(BaseModel):
    user_id: int

# ============ PUBLIC ENDPOINTS ============
@app.get("/")
def root():
    return {
        "message": "🚀 Airdrop TON System is LIVE!",
        "status": "operational",
        "wallet": os.getenv("TON_WALLET", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"),
        "price": "44.4 ₪",
        "stats": stats
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/register")
def register_user(data: UserRegister):
    user_id = data.telegram_id
    
    if user_id not in users_db:
        users_db[user_id] = {
            "id": user_id,
            "username": data.username,
            "first_name": data.first_name,
            "balance": 1000,
            "joined": datetime.now().isoformat(),
            "airdrops": []
        }
        stats["total_users"] += 1
    
    return {"status": "success", "user_id": user_id, "balance": 1000}

@app.post("/api/airdrop")
def create_airdrop(data: AirdropRequest):
    user_id = data.user_id
    price = 44.4
    wallet = os.getenv("TON_WALLET", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")
    
    # צור מזהה ייחודי
    transaction_id = hashlib.md5(f"{user_id}_{int(time.time())}".encode()).hexdigest()[:10]
    
    airdrop_data = {
        "id": transaction_id,
        "user_id": user_id,
        "price": price,
        "wallet": wallet,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "expires": (datetime.now() + timedelta(hours=1)).isoformat(),
        "payment_url": f"ton://transfer/{wallet}?amount={price}&text=Airdrop-{transaction_id}",
        "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=ton://transfer/{wallet}?amount={price}&text=Airdrop-{transaction_id}"
    }
    
    airdrops_db[transaction_id] = airdrop_data
    stats["total_airdrops"] += 1
    stats["pending_payments"] += 1
    
    return {
        "status": "success",
        "airdrop": airdrop_data
    }

@app.get("/api/user/{user_id}")
def get_user(user_id: int):
    if user_id in users_db:
        user_data = users_db[user_id].copy()
        user_data["airdrops"] = [a for a in airdrops_db.values() if a["user_id"] == user_id]
        return user_data
    return {"status": "user_not_found"}

# ============ ADMIN ENDPOINTS ============
@app.get("/admin/stats")
def admin_stats(admin_key: str):
    if admin_key != os.getenv("ADMIN_KEY", "test123"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "platform": "TON Airdrop System",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
        "recent_users": list(users_db.values())[-10:] if users_db else [],
        "recent_airdrops": list(airdrops_db.values())[-10:] if airdrops_db else []
    }

@app.post("/admin/verify")
def verify_payment(transaction_id: str, admin_key: str):
    if admin_key != os.getenv("ADMIN_KEY", "test123"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if transaction_id in airdrops_db:
        airdrops_db[transaction_id]["status"] = "completed"
        airdrops_db[transaction_id]["verified_at"] = datetime.now().isoformat()
        
        stats["pending_payments"] -= 1
        stats["completed_payments"] += 1
        stats["total_volume_ton"] += airdrops_db[transaction_id]["price"]
        
        return {"status": "verified", "airdrop": airdrops_db[transaction_id]}
    
    return {"status": "not_found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
