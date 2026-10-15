from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    txn_reference = Column(String(64), unique=True, index=True, nullable=False)
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True, index=True)
    from_vpa = Column(String(100), nullable=False)
    to_vpa = Column(String(100), nullable=False)
    # Strictly integer paise
    amount_paise = Column(BigInteger, nullable=False)
    note = Column(String(255), default="UPI Payment")
    status = Column(String(20), default="SUCCESS", nullable=False)
    idempotency_key = Column(String(64), index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    from_account = relationship("Account", foreign_keys=[from_account_id], back_populates="sent_transactions")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="received_transactions")
