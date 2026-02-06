from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["system"])

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "airdrop",
        "version": "stable",
        "env": settings.ENVIRONMENT,
    }
