<<<<<<< HEAD
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, Enum as SAEnum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    airdrops = relationship("Airdrop", back_populates="user", cascade="all, delete-orphan")
=======
﻿from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
import enum
from backend.app.db.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    LEADER = "leader"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    referral_code = Column(String, unique=True, index=True)
    invited_by = Column(String, nullable=True)
    balance = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
>>>>>>> 03e5c1437b28768ba89ff31f6cea0fc62306fdf0
