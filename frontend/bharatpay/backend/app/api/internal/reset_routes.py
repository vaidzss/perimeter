"""
Internal Demo Reset Endpoint - Used by Red Team drawer to restore state.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import os
import sys

from app.db.session import get_db, SessionLocal
from app.models.account import Account
from app.models.transaction import Transaction

router = APIRouter(prefix="/internal/demo", tags=["Internal Demo"], include_in_schema=False)

@router.post("/reset-state")
def reset_demo_state(db: Session = Depends(get_db)):
    """
    Resets account balances, daily transfer limits, and test idempotency states
    so live hackathon pitches and attacks can be re-run cleanly.
    """
    # 1. Reset Priya Sharma (Account 1)
    acc1 = db.query(Account).filter(Account.id == 1).first()
    if acc1:
        acc1.balance_paise = 4850000  # ₹48,500.00
        acc1.daily_limit_paise = 10000000  # ₹1,00,000.00

    # 2. Reset Rohit Verma (Account 2)
    acc2 = db.query(Account).filter(Account.id == 2).first()
    if acc2:
        acc2.balance_paise = 12500000  # ₹1,25,000.00
        acc2.daily_limit_paise = 10000000

    # 3. Reset Ananya Iyer (Account 3)
    acc3 = db.query(Account).filter(Account.id == 3).first()
    if acc3:
        acc3.balance_paise = 1820000  # ₹18,200.00
        acc3.daily_limit_paise = 10000000

    db.commit()

    return {
        "status": "RESET_SUCCESSFUL",
        "message": "Demo balances and daily limits restored to baseline seed values.",
        "watermark": "SYNTHETIC TEST DATA — CC6-IC07"
    }
