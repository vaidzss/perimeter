import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.organization import Employee, Role, AccessGrant
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.core.internal_auth import (
    get_current_internal_employee,
    require_role
)

router = APIRouter(prefix="/reports", tags=["internal"])

# Schemas
class BulkExportRequest(BaseModel):
    region: Optional[str] = Field(None, example="West")
    export_format: str = Field("json", example="json")
    include_transactions: bool = Field(True)
    reason: str = Field(..., example="Quarterly regional performance audit")


def _resolve_effective_regions(employee: Employee, role_name: str, requested_region: Optional[str] = None, db: Session = None) -> List[str]:
    """
    Server-side scope resolver:
    - VP Sales / org-wide: can query any or all regions
    - Regional Head (multi-region): can query their region plus any granted regions
    - Sales Manager (region): STRICTLY locked to their assigned region (e.g. West)
    - Employee (Support): if region is org-wide or specific region
    """
    emp_region = employee.region

    # Check any active access grants
    now = datetime.now(timezone.utc)
    active_grants = db.query(AccessGrant).filter(
        AccessGrant.employee_id == employee.employee_id,
        AccessGrant.expires_at > now
    ).all() if db else []

    granted_regions = [
        g.resource_scope.split("region:")[-1].strip()
        for g in active_grants
        if "region:" in g.resource_scope
    ]

    all_allowed = []
    if role_name == "VP Sales" or emp_region == "org-wide":
        all_allowed = ["West", "North", "South", "East", "org-wide"]
    else:
        all_allowed = [emp_region] + granted_regions

    if requested_region and requested_region not in ["all", "org-wide"]:
        if requested_region not in all_allowed and role_name != "VP Sales":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Caller {employee.employee_id} ({role_name}) declared scope is limited to {all_allowed}. Attempted to access region '{requested_region}'."
            )
        return [requested_region]

    return all_allowed


@router.get("/regional-sales")
def get_regional_sales(
    request: Request,
    region: Optional[str] = Query(None, description="Target region (West, North, South, East)"),
    date_range: Optional[str] = Query("30d", description="Date range: 7d, 30d, 90d"),
    auth_data: dict = Depends(get_current_internal_employee),
    db: Session = Depends(get_db)
):
    """
    Sales Manager+ endpoint for regional turnover and metrics.
    Enforces region scope server-side.
    """
    caller_role = auth_data["role"]
    employee = auth_data["employee"]

    if caller_role not in ["Sales Manager", "Regional Head", "VP Sales", "IT Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Requires Sales Manager+ role, caller is '{caller_role}'"
        )

    # Server-side scope enforcement
    effective_regions = _resolve_effective_regions(employee, caller_role, region, db)

    # Record scope used on request state
    request.state.scope_used = effective_regions

    # Query accounts in effective regions
    accounts_in_scope = db.query(Account).filter(Account.region.in_(effective_regions)).all()
    account_ids = [a.id for a in accounts_in_scope]

    # Query transaction aggregates
    total_volume_paise = db.query(func.sum(Transaction.amount_paise)).filter(
        Transaction.from_account_id.in_(account_ids)
    ).scalar() or 0

    txn_count = db.query(Transaction).filter(
        Transaction.from_account_id.in_(account_ids)
    ).count()

    return {
        "status": "SUCCESS",
        "caller_employee_id": employee.employee_id,
        "caller_role": caller_role,
        "scope_used": effective_regions,
        "date_range": date_range,
        "metrics": {
            "monitored_accounts_count": len(accounts_in_scope),
            "total_transaction_count": txn_count,
            "total_volume_paise": total_volume_paise,
            "total_volume_inr": total_volume_paise / 100.0,
            "regions_included": effective_regions
        }
    }


@router.get("/account-lookup/{account_id}")
def lookup_account_details(
    account_id: int,
    request: Request,
    reason: str = Query(..., description="Mandatory business reason for support lookup (e.g. ticket #, escalation)"),
    auth_data: dict = Depends(get_current_internal_employee),
    db: Session = Depends(get_db)
):
    """
    Support & escalation account lookup (Employee+).
    Requires a non-empty business reason.
    Server-side verifies that the account falls within the employee's jurisdiction/region.
    """
    caller_role = auth_data["role"]
    employee = auth_data["employee"]

    # Reason is strictly mandatory
    if not reason or len(reason.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mandatory query parameter 'reason' must be provided with at least 5 characters describing the business justification."
        )

    # Fetch account
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )

    # Server-side region verification
    effective_regions = _resolve_effective_regions(employee, caller_role, None, db)
    if "org-wide" not in effective_regions and account.region not in effective_regions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Scope violation: Employee {employee.employee_id} ({caller_role}) scope is {effective_regions}. Target account {account_id} is in region '{account.region}'."
        )

    # Attach audit context to request state
    request.state.scope_used = effective_regions
    request.state.reason = reason

    user = account.user
    return {
        "status": "SUCCESS",
        "account_id": account.id,
        "account_number": account.masked_account_number,
        "region": account.region,
        "balance_paise": account.balance_paise,
        "balance_inr": account.balance_paise / 100.0,
        "status": account.status,
        "holder_name": user.full_name if user else "Unknown",
        "holder_email": user.email if user else "Unknown",
        "lookup_audit": {
            "performed_by": employee.employee_id,
            "role": caller_role,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/org-wide-summary")
def get_org_wide_summary(
    request: Request,
    auth_data: dict = Depends(get_current_internal_employee),
    db: Session = Depends(get_db)
):
    """
    VP Sales only endpoint.
    Aggregates org-wide financial liquidity, regional breakdown, and total customer count.
    """
    caller_role = auth_data["role"]
    employee = auth_data["employee"]

    if caller_role not in ["VP Sales", "IT Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: org-wide summary is restricted to VP Sales. Caller role is '{caller_role}'."
        )

    total_accounts = db.query(Account).count()
    total_paise = db.query(func.sum(Account.balance_paise)).scalar() or 0
    total_txns = db.query(Transaction).count()

    # Regional distribution
    regions = ["West", "North", "South", "East"]
    regional_breakdown = {}
    for r in regions:
        acc_count = db.query(Account).filter(Account.region == r).count()
        r_paise = db.query(func.sum(Account.balance_paise)).filter(Account.region == r).scalar() or 0
        regional_breakdown[r] = {
            "accounts_count": acc_count,
            "balance_paise": r_paise,
            "balance_inr": r_paise / 100.0
        }

    request.state.scope_used = ["org-wide"]

    return {
        "status": "SUCCESS",
        "org_wide_kpis": {
            "total_accounts": total_accounts,
            "total_balance_paise": total_paise,
            "total_balance_inr": total_paise / 100.0,
            "total_transactions_processed": total_txns,
            "regional_breakdown": regional_breakdown
        },
        "caller_audit": {
            "employee_id": employee.employee_id,
            "role": caller_role,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.post("/bulk-export")
def bulk_export_reports(
    payload: BulkExportRequest,
    request: Request,
    auth_data: dict = Depends(get_current_internal_employee),
    db: Session = Depends(get_db)
):
    """
    Regional Head+ endpoint for bulk operational reporting.
    Enforces scope and requires documented reason.
    """
    caller_role = auth_data["role"]
    employee = auth_data["employee"]

    if caller_role not in ["Regional Head", "VP Sales", "IT Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: bulk export requires Regional Head or VP Sales. Caller role is '{caller_role}'."
        )

    effective_regions = _resolve_effective_regions(employee, caller_role, payload.region, db)
    request.state.scope_used = effective_regions
    request.state.reason = payload.reason

    accounts = db.query(Account).filter(Account.region.in_(effective_regions)).all()

    export_records = [
        {
            "account_id": a.id,
            "masked_account_number": a.masked_account_number,
            "region": a.region,
            "balance_paise": a.balance_paise,
            "status": a.status
        }
        for a in accounts
    ]

    return {
        "status": "EXPORT_COMPLETE",
        "records_exported": len(export_records),
        "regions_covered": effective_regions,
        "format": payload.export_format,
        "audit": {
            "exported_by": employee.employee_id,
            "role": caller_role,
            "reason": payload.reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "data": export_records
    }
