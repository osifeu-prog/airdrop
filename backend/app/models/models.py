from sqlalchemy import Column, Integer, String, ForeignKey
from backend.app.db.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String)
    referrer_id = Column(String, nullable=True)
    balance = Column(Integer, default=0)
