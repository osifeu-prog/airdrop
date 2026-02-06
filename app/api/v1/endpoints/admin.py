import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, require_admin_secret
from app.api.v1.schemas import FeatureFlagSetIn
from app.models.event_log import EventLog
from app.services.feature_flags import set_flag

LOG = logging.getLogger("app.api.admin")

router = APIRouter(dependencies=[Depends(require_admin_secret)])

@router.post("/feature-flag")
def admin_set_feature_flag(body: FeatureFlagSetIn, db: Session = Depends(get_db)):
    set_flag(db, body.key, body.enabled)
    db.add(EventLog(event="admin.feature_flag.set", data={"key": body.key, "enabled": body.enabled}))
    db.commit()
    return {"ok": True, "key": body.key, "enabled": body.enabled}
