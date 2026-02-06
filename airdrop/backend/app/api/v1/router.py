from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, airdrop, users, referral, health

api_router = APIRouter()

# הוספת ה-Prefix המלא כדי להתאים לבוט
api_router.include_router(health.router, prefix="/api/v1", tags=["Health"])
api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
api_router.include_router(airdrop.router, prefix="/api/v1/airdrop", tags=["Airdrop"])
api_router.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
api_router.include_router(referral.router, prefix="/api/v1/referral", tags=["Referral"])
