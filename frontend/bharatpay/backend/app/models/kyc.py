from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class KYCRecord(Base):
    __tablename__ = "kyc_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    pan_synthetic = Column(String(10), nullable=False)  # Synthetic e.g. ABCDE1234F
    masked_pan = Column(String(10), nullable=False)     # e.g. ABCDE****F
    aadhaar_synthetic = Column(String(12), nullable=False)  # Synthetic e.g. 999988881234
    masked_aadhaar = Column(String(14), nullable=False)     # e.g. XXXXXXXX1234
    kyc_status = Column(String(20), default="VERIFIED", nullable=False)  # VERIFIED, PENDING, REJECTED
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="kyc_record")
