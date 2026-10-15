"""
Internal Debug Endpoints - TARGET VULNERABILITY
WARNING: Deliberately vulnerable shadow endpoint for CC6-IC07 ASPM Discovery testing.
Exposes limit overrides via a trivially discoverable static debug key.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import Account

# include_in_schema=False ensures this shadow route is never documented in OpenAPI
router = APIRouter(prefix="/debug", tags=["Internal Debug"], include_in_schema=False)

class OverrideLimitRequest(BaseModel):
    account_id: int
    new_daily_limit_paise: int = Field(gt=0, description="New daily limit in integer paise")

class OverrideLimitResponse(BaseModel):
    account_id: int
    old_daily_limit_paise: int
    new_daily_limit_paise: int
    status: str = "OVERRIDDEN"
    message: str = "Daily limit successfully mutated via internal debug interface"
    watermark: str = "SYNTHETIC TEST DATA — CC6-IC07"

@router.post("/override-limit", response_model=OverrideLimitResponse)
def override_account_limit(
    override_req: OverrideLimitRequest,
    x_debug_key: str = Header(None, alias="X-Debug-Key"),
    db: Session = Depends(get_db)
):
    """
    [SHADOW / BACKDOOR ENDPOINT]
    Internal debugging interface used by developers during testing.
    VULNERABILITY: Protected only by static dev key 'dev123'; permits unauthenticated limit mutation.
    """
    if x_debug_key != "dev123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal debug key (X-Debug-Key)"
        )

    account = db.query(Account).filter(Account.id == override_req.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {override_req.account_id} not found"
        )

    old_limit = account.daily_limit_paise
    account.daily_limit_paise = override_req.new_daily_limit_paise
    db.commit()
    db.refresh(account)

    return OverrideLimitResponse(
        account_id=account.id,
        old_daily_limit_paise=old_limit,
        new_daily_limit_paise=account.daily_limit_paise
    )
