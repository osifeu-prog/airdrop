# backend/app/core/invites.py

import uuid
from datetime import datetime
from .registry import SYSTEM_REGISTRY


def create_invite(created_by: str, role: str = "member"):
    invite_id = str(uuid.uuid4())

    SYSTEM_REGISTRY["invites"][invite_id] = {
        "invite_id": invite_id,
        "created_by": created_by,
        "role": role,
        "created_at": datetime.utcnow().isoformat(),
        "used": False,
        "used_by": None
    }

    SYSTEM_REGISTRY["events"].append({
        "type": "invite_created",
        "invite_id": invite_id,
        "by": created_by
    })

    return invite_id


def use_invite(invite_id: str, user_id: str):
    invite = SYSTEM_REGISTRY["invites"].get(invite_id)

    if not invite:
        raise ValueError("Invalid invite")

    if invite["used"]:
        raise ValueError("Invite already used")

    invite["used"] = True
    invite["used_by"] = user_id

    SYSTEM_REGISTRY["users"][user_id] = {
        "user_id": user_id,
        "role": invite["role"],
        "invited_by": invite["created_by"],
        "joined_at": datetime.utcnow().isoformat()
    }

    SYSTEM_REGISTRY["events"].append({
        "type": "user_joined",
        "user_id": user_id,
        "via_invite": invite_id
    })

    return SYSTEM_REGISTRY["users"][user_id]
