from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
