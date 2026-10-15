import uuid
from datetime import datetime, timezone, time as dt_time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.upi import UPIProfile
from app.models.transaction import Transaction
from app.schemas.banking import UPITransferRequest, UPITransferResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/upi-transfer", response_model=UPITransferResponse)
def execute_upi_transfer(
    transfer_req: UPITransferRequest,
    current_data: tuple[User, Account] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute a peer-to-peer or peer-to-merchant UPI transfer.
    Enforces idempotency, sufficient funds, and daily transfer limit.
    All currency is handled strictly in integer paise.
    """
    user, account = current_data

    # 1. Idempotency Check
    if transfer_req.idempotency_key:
        existing_txn = db.query(Transaction).filter(
            Transaction.idempotency_key == transfer_req.idempotency_key,
            Transaction.from_account_id == account.id
        ).first()
        if existing_txn:
            return UPITransferResponse(
                txn_reference=existing_txn.txn_reference,
                status=existing_txn.status,
                from_vpa=existing_txn.from_vpa,
                to_vpa=existing_txn.to_vpa,
                amount_paise=existing_txn.amount_paise,
                remaining_balance_paise=account.balance_paise,
                daily_limit_remaining_paise=account.daily_limit_paise,
                note=existing_txn.note,
                created_at=existing_txn.created_at,
                idempotent_replay=True
            )

    # 2. Amount Validation
    amount_paise = transfer_req.amount_paise
    if amount_paise <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer amount must be greater than 0 paise"
        )

    # 3. Daily Limit Check (sum of successful transfers sent today)
    today_start = datetime.combine(datetime.now(timezone.utc).date(), dt_time.min)
    today_transfers_sum = db.query(func.coalesce(func.sum(Transaction.amount_paise), 0)).filter(
        Transaction.from_account_id == account.id,
        Transaction.status == "SUCCESS",
        Transaction.created_at >= today_start
    ).scalar()

    if (today_transfers_sum + amount_paise) > account.daily_limit_paise:
        remaining_limit = max(0, account.daily_limit_paise - today_transfers_sum)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Daily transfer limit exceeded. Remaining limit today: ₹{remaining_limit / 100:.2f} of ₹{account.daily_limit_paise / 100:.2f}"
        )

    # 4. Sufficient Balance Check
    if account.balance_paise < amount_paise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: ₹{account.balance_paise / 100:.2f}"
        )

    # 5. Resolve recipient account (if internal user)
    recipient_upi = db.query(UPIProfile).filter(UPIProfile.vpa == transfer_req.to_vpa.strip()).first()
    recipient_account_id = recipient_upi.account_id if recipient_upi else None

    # 6. Execute atomic balance transfer
    account.balance_paise -= amount_paise
    if recipient_account_id:
        recipient_account = db.query(Account).filter(Account.id == recipient_account_id).first()
        if recipient_account:
            recipient_account.balance_paise += amount_paise

    # Generate reference: TXN + timestamp + random hex
    txn_ref = f"TXN{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

    txn = Transaction(
        txn_reference=txn_ref,
        from_account_id=account.id,
        to_account_id=recipient_account_id,
        from_vpa=transfer_req.from_vpa.strip(),
        to_vpa=transfer_req.to_vpa.strip(),
        amount_paise=amount_paise,
        note=transfer_req.note or "UPI Transfer",
        status="SUCCESS",
        idempotency_key=transfer_req.idempotency_key,
        created_at=datetime.now(timezone.utc)
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    daily_limit_remaining = max(0, account.daily_limit_paise - (today_transfers_sum + amount_paise))

    return UPITransferResponse(
        txn_reference=txn.txn_reference,
        status=txn.status,
        from_vpa=txn.from_vpa,
        to_vpa=txn.to_vpa,
        amount_paise=txn.amount_paise,
        remaining_balance_paise=account.balance_paise,
        daily_limit_remaining_paise=daily_limit_remaining,
        note=txn.note,
        created_at=txn.created_at,
        idempotent_replay=False
    )
