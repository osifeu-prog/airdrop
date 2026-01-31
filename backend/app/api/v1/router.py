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