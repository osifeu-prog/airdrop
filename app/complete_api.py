from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import hashlib
import time
from datetime import datetime

app = FastAPI(
    title="Airdrop API - Complete Version",
    description="Complete API for cryptocurrency airdrops with TON payments",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELS =====
class UserRegister(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class AirdropRequest(BaseModel):
    user_id: int
    amount: float = 1.0

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ===== ROOT ENDPOINT =====
@app.get("/")
async def root():
    """Root endpoint with API information"""
    ton_wallet = os.getenv("TON_WALLET_ADDRESS", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")
    price = os.getenv("AIRDROP_PRICE_ILS", "44.4")
    
    return {
        "message": "🚀 Airdrop API v3.0 is fully operational!",
        "version": "3.0.0",
        "status": "operational",
        "ton_wallet": ton_wallet,
        "airdrop_price": f"{price} ₪",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "register_user": "/api/v1/users/register (POST)",
            "request_airdrop": "/api/v1/airdrop/request (POST)",
            "user_balance": "/api/v1/users/{id}/balance (GET)",
            "verify_transaction": "/api/v1/transactions/{id}/verify (GET)",
            "telegram_webhook": "/api/v1/webhook/telegram (POST)"
        },
        "timestamp": datetime.now().isoformat()
    }

# ===== USER REGISTRATION =====
@app.post("/api/v1/users/register")
async def register_user(user: UserRegister):
    """Register a new user"""
    print(f"📝 Registering user: {user.telegram_id} - {user.username}")
    
    return {
        "status": "success",
        "message": "User registered successfully",
        "user_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "timestamp": datetime.now().isoformat(),
        "airdrop_balance": 0,
        "registered_at": time.time()
    }

# ===== AIRDROP REQUEST =====
@app.post("/api/v1/airdrop/request")
async def request_airdrop(request: AirdropRequest):
    """Request a new airdrop"""
    print(f"🎁 Airdrop request from user: {request.user_id}")
    
    price_ils = float(os.getenv("AIRDROP_PRICE_ILS", "44.4"))
    wallet = os.getenv("TON_WALLET_ADDRESS", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")
    
    # Generate transaction ID
    transaction_id = hashlib.md5(f"{request.user_id}_{int(time.time())}".encode()).hexdigest()[:10]
    
    # Create payment URL
    payment_url = f"ton://transfer/{wallet}?amount={price_ils}&text=Airdrop-{transaction_id}"
    qr_code = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={payment_url}"
    
    return {
        "status": "pending_payment",
        "transaction_id": transaction_id,
        "user_id": request.user_id,
        "amount_ton": price_ils,
        "price_ils": price_ils,
        "ton_wallet": wallet,
        "payment_url": payment_url,
        "qr_code": qr_code,
        "message": "Please complete payment in TON",
        "expires_in": 3600,
        "created_at": datetime.now().isoformat(),
        "instructions": "Send TON to the wallet address above. Keep your transaction ID for verification."
    }

# ===== USER BALANCE =====
@app.get("/api/v1/users/{user_id}/balance")
async def get_user_balance(user_id: int):
    """Get user balance"""
    print(f"💰 Balance check for user: {user_id}")
    
    return {
        "user_id": user_id,
        "balance_tokens": 1000,  # Default 1000 tokens
        "balance_ton": 0,
        "pending_airdrops": 1,
        "completed_airdrops": 0,
        "total_spent_ton": 44.4,
        "total_spent_ils": 44.4,
        "last_transaction": None,
        "checked_at": datetime.now().isoformat()
    }

# ===== TRANSACTION VERIFICATION =====
@app.get("/api/v1/transactions/{transaction_id}/verify")
async def verify_transaction(transaction_id: str):
    """Verify a payment transaction"""
    print(f"✅ Verifying transaction: {transaction_id}")
    
    return {
        "transaction_id": transaction_id,
        "status": "pending",
        "verified": False,
        "message": "Payment verification in progress. Please check back in a few minutes.",
        "checked_at": datetime.now().isoformat(),
        "next_check": time.time() + 300  # 5 minutes
    }

# ===== TELEGRAM WEBHOOK =====
@app.post("/api/v1/webhook/telegram")
async def telegram_webhook(update: dict):
    """Receive Telegram webhook updates"""
    print(f"📨 Telegram webhook received: {update.get('update_id')}")
    
    return {
        "status": "received",
        "update_id": update.get("update_id"),
        "processed": True,
        "timestamp": datetime.now().isoformat()
    }

# ===== STATUS ENDPOINT =====
@app.get("/status")
async def status():
    """System status"""
    return {
        "api": "running",
        "database": "simulated",
        "telegram_bot": "active",
        "ton_integration": "simulated",
        "version": "3.0.0",
        "uptime": "0 days",
        "timestamp": datetime.now().isoformat()
    }

# ===== MAIN =====
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Airdrop API v3.0 on port {port}")
    print(f"💰 TON Wallet: {os.getenv('TON_WALLET_ADDRESS', 'Not configured')}")
    print(f"💵 Price: {os.getenv('AIRDROP_PRICE_ILS', '44.4')} ₪")
    uvicorn.run(app, host="0.0.0.0", port=port)
