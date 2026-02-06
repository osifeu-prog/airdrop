from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import hashlib
import time

router = APIRouter(prefix="/api/v1", tags=["airdrop"])

# מודלים
class UserRegister(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class AirdropRequest(BaseModel):
    user_id: int
    amount: float = 1.0

# רישום משתמש
@router.post("/users/register")
async def register_user(user: UserRegister):
    """רישום משתמש חדש"""
    return {
        "status": "success",
        "message": "User registered successfully",
        "user_id": user.telegram_id,
        "username": user.username,
        "timestamp": time.time(),
        "airdrop_balance": 0
    }

# בקשת airdrop
@router.post("/airdrop/request")
async def request_airdrop(request: AirdropRequest):
    """בקשת airdrop"""
    price_ils = float(os.getenv("AIRDROP_PRICE_ILS", "44.4"))
    wallet = os.getenv("TON_WALLET_ADDRESS", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")
    
    # יצירת מזהה עסקה
    transaction_id = hashlib.md5(f"{request.user_id}_{int(time.time())}".encode()).hexdigest()[:10]
    
    return {
        "status": "pending_payment",
        "transaction_id": transaction_id,
        "user_id": request.user_id,
        "amount_ton": price_ils,
        "price_ils": price_ils,
        "ton_wallet": wallet,
        "payment_url": f"ton://transfer/{wallet}?amount={price_ils}&text=Airdrop-{transaction_id}",
        "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=ton://transfer/{wallet}%3Famount%3D{price_ils}%26text%3DAirdrop-{transaction_id}",
        "message": "Please complete payment in TON",
        "expires_in": 3600,
        "created_at": time.time()
    }

# בדיקת יתרה
@router.get("/users/{user_id}/balance")
async def get_user_balance(user_id: int):
    """קבלת יתרת משתמש"""
    return {
        "user_id": user_id,
        "balance_tokens": 0,
        "balance_ton": 0,
        "pending_airdrops": 0,
        "completed_airdrops": 0,
        "total_spent_ton": 0,
        "total_spent_ils": 0,
        "last_transaction": None
    }

# וידוא תשלום
@router.get("/transactions/{transaction_id}/verify")
async def verify_transaction(transaction_id: str):
    """וידוא עסקת תשלום"""
    # TODO: אינטגרציה עם TON API אמיתי
    return {
        "transaction_id": transaction_id,
        "status": "pending",
        "verified": False,
        "message": "Payment verification pending. Please wait.",
        "timestamp": time.time()
    }

# webhook לטלגרם
@router.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    """קבלת עדכונים מטלגרם"""
    print(f"Telegram webhook received: {update}")
    return {
        "status": "received",
        "update_id": update.get("update_id"),
        "timestamp": time.time()
    }
