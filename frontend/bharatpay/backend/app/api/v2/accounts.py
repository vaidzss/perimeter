from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.upi import UPIProfile
from app.models.kyc import KYCRecord
from app.models.transaction import Transaction
from app.schemas.banking import StatementResponse, TransactionItem

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/{account_id}/statement", response_model=StatementResponse)
def get_account_statement(
    account_id: int,
    current_data: tuple[User, Account] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch account statement including balance, masked identifiers, KYC status, and last 10 transactions.
    SECURITY CONTROL: Enforces strict ownership. Returning 403 Forbidden for any other user's account ID.
    """
    user, current_account = current_data

    # Strict ownership check
    if current_account.id != account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only access your own account statement"
        )

    # Fetch upi profile and kyc
    upi = db.query(UPIProfile).filter(UPIProfile.account_id == current_account.id).first()
    kyc = db.query(KYCRecord).filter(KYCRecord.user_id == user.id).first()

    # Fetch last 10 transactions
    txns = db.query(Transaction).filter(
        (Transaction.from_account_id == current_account.id) | (Transaction.to_account_id == current_account.id)
    ).order_by(desc(Transaction.created_at)).limit(10).all()

    return StatementResponse(
        account_id=current_account.id,
        account_number_masked=current_account.masked_account_number,
        ifsc_code=current_account.ifsc_code,
        balance_paise=current_account.balance_paise,
        currency=current_account.currency,
        daily_limit_paise=current_account.daily_limit_paise,
        vpa=upi.vpa if upi else f"{user.user_code}@bharatpay",
        kyc_status=kyc.kyc_status if kyc else "PENDING",
        masked_pan=kyc.masked_pan if kyc else "NOT_FOUND",
        transactions=[
            TransactionItem(
                id=t.id,
                txn_reference=t.txn_reference,
                from_vpa=t.from_vpa,
                to_vpa=t.to_vpa,
                amount_paise=t.amount_paise,
                note=t.note or "UPI Transfer",
                status=t.status,
                created_at=t.created_at
            )
            for t in txns
        ]
    )
