from fastapi import APIRouter, Depends
from app.api.v1.deps import require_admin_secret

router = APIRouter()

@router.get("/whoami", tags=["admin"])
def admin_whoami(_: None = Depends(require_admin_secret)):
    return {"ok": True, "role": "admin"}