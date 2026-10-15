from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from app.db.base import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    merchant_code = Column(String(32), unique=True, index=True, nullable=False)
    business_name = Column(String(255), nullable=False)
    vpa = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)
    verified = Column(Boolean, default=True, nullable=False)
    rating = Column(Float, default=4.8, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
