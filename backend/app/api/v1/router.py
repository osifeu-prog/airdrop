<<<<<<< HEAD
from fastapi import APIRouter

from app.api.v1.endpoints import auth, user, wallet, airdrop, token, admin
from app.api.v1.endpoints import public_docs
from app.api.v1.endpoints import admin_airdrop, admin_whoami

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(airdrop.router, prefix="/airdrop", tags=["airdrop"])
api_router.include_router(token.router, prefix="/token", tags=["token"])
api_router.include_router(public_docs.router, tags=["public"])

# admin
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_airdrop.router)
api_router.include_router(admin_whoami.router, prefix="/admin")
=======
﻿from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, airdrop, users, referral, health

api_router = APIRouter()

# הוספת ה-Prefix המלא כדי להתאים לבוט
api_router.include_router(health.router, prefix="/api/v1", tags=["Health"])
api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
api_router.include_router(airdrop.router, prefix="/api/v1/airdrop", tags=["Airdrop"])
api_router.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
api_router.include_router(referral.router, prefix="/api/v1/referral", tags=["Referral"])
>>>>>>> 03e5c1437b28768ba89ff31f6cea0fc62306fdf0
