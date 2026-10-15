from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_number = Column(String(20), unique=True, index=True, nullable=False)
    masked_account_number = Column(String(20), nullable=False)
    ifsc_code = Column(String(11), default="BPAY0001042", nullable=False)
    region = Column(String(50), default="West", nullable=False, index=True)  # West, North, South, East
    # Strictly integer paise - 1 INR = 100 paise. Never float.
    balance_paise = Column(BigInteger, default=0, nullable=False)
    daily_limit_paise = Column(BigInteger, default=10000000, nullable=False)  # ₹1,00,000 in paise
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="accounts")
    upi_profiles = relationship("UPIProfile", back_populates="account")
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.from_account_id", back_populates="from_account")
    received_transactions = relationship("Transaction", foreign_keys="Transaction.to_account_id", back_populates="to_account")
