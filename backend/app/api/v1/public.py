# backend/app/api/v1/public.py

from fastapi import APIRouter, HTTPException
from backend.app.core.invites import create_invite, use_invite

router = APIRouter()

# --- Invite Endpoints ---

@router.post("/invite/create")
def api_create_invite(created_by: str, role: str = "member"):
    invite_id = create_invite(created_by, role)
    return {
        "invite_id": invite_id,
        "invite_link": f"http://127.0.0.1:8000/public/invite/use?invite_id={invite_id}"
    }

@router.post("/invite/use")
def api_use_invite(invite_id: str, user_id: str):
    try:
        user = use_invite(invite_id, user_id)
        return {"status": "joined", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
