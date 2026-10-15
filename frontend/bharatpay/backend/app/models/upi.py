from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class UPIProfile(Base):
    __tablename__ = "upi_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    vpa = Column(String(100), unique=True, index=True, nullable=False)  # e.g. priya.sharma@bharatpay
    is_primary = Column(Boolean, default=True, nullable=False)
    upi_pin_hash = Column(String(255), nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="upi_profiles")
    account = relationship("Account", back_populates="upi_profiles")
