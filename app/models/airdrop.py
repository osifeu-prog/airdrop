from datetime import datetime
from enum import Enum
from decimal import Decimal

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class AirdropStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Airdrop(Base):
    __tablename__ = "airdrops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    status: Mapped[AirdropStatus] = mapped_column(SAEnum(AirdropStatus), default=AirdropStatus.PENDING, nullable=False)
    reason: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="airdrops")
