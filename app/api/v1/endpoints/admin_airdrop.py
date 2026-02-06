from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(prefix="/admin/airdrop", tags=["admin-airdrop"])


def _require_admin(x_admin_secret: Optional[str]) -> None:
    expected = os.getenv("ADMIN_SECRET", "")
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_SECRET not configured")
    if not x_admin_secret or x_admin_secret != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/list")
def list_airdrops(
    limit: int = 50,
    x_admin_secret: Optional[str] = Header(default=None, alias="X-Admin-Secret"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    _require_admin(x_admin_secret)

    sql = text("""
        select
            a.id,
            a.user_id,
            a.amount,
            a.status::text as status,
            a.reason,
            a.created_at
        from airdrops a
        order by a.id desc
        limit :limit
    """)

    rows = db.execute(sql, {"limit": int(limit)}).mappings().all()
    return {"items": [dict(r) for r in rows]}


@router.get("/{airdrop_id}")
def get_airdrop(
    airdrop_id: int,
    x_admin_secret: Optional[str] = Header(default=None, alias="X-Admin-Secret"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    _require_admin(x_admin_secret)

    sql = text("""
        select
            a.id,
            a.user_id,
            a.amount,
            a.status::text as status,
            a.reason,
            a.created_at
        from airdrops a
        where a.id = :id
    """)

    row = db.execute(sql, {"id": int(airdrop_id)}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return dict(row)