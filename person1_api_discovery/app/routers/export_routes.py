"""
Export & Legacy V1 Router:
15. GET /api/v1/users/export (ZOMBIE API - deprecated in spec, NO AUTH #2, bulk PII leak)
16. GET /api/v1/accounts/{account_id}/passbook-dump (SHADOW API #1 - undocumented legacy route, JWT Auth, full PII)
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from person1_api_discovery.app.auth import get_current_user
from person1_api_discovery.app.seed_data import USERS_DB, ACCOUNTS_DB, TRANSACTIONS_DB

router = APIRouter(prefix="/api/v1", tags=["Legacy & Export"])


@router.get("/users/export", deprecated=True)
async def legacy_bulk_users_export():
    """
    ZOMBIE API (NO AUTH #2):
    Documented in openapi_partial.json with 'deprecated: true'.
    Unauthenticated legacy migration export left accessible in production.
    Dumps synthetic Indian customer records containing PAN cards, phone numbers,
    UPI VPAs, and Government ID placeholders.
    """
    exported_records = []
    for user in USERS_DB.values():
        exported_records.append({
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "pan": user["pan"],
            "phone": user["phone"],
            "upi_vpa": user["upi_vpa"],
            "email": user["email"],
            "govt_id_like": user["govt_id_like"],
            "account_id": user["account_id"],
            "role": user["role"]
        })
    return {
        "export_status": "DEPRECATED_V1_SNAPSHOT",
        "total_records": len(exported_records),
        "users": exported_records
    }


@router.get("/accounts/{account_id}/passbook-dump")
async def shadow_passbook_dump(
    account_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    SHADOW API #1 (Undocumented):
    Legacy uncataloged endpoint absent from openapi_partial.json.
    Dumps comprehensive account passbook, PAN, government ID placeholder,
    and all raw ledger transactions.
    """
    account = ACCOUNTS_DB.get(account_id)
    txns = TRANSACTIONS_DB.get(account_id, [])

    if not account:
        if account_id.isdigit():
            return {
                "account_id": account_id,
                "passbook_series": f"PBK-2026-{account_id}",
                "account_holder": f"Customer {account_id}",
                "pan": f"ABCDE{account_id}F",
                "govt_id_like": f"[GOVT-ID-XXXX-{account_id}]",
                "phone": f"+91-98765{account_id:05d}" if len(account_id) <= 5 else "+91-9876500000",
                "upi_vpa": f"user_{account_id}@okaxis",
                "available_balance": 52400.00,
                "ledger_dump": []
            }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account passbook not found")

    return {
        "account_id": account["account_id"],
        "passbook_series": f"PBK-2026-{account_id}",
        "account_holder": account["account_holder"],
        "account_type": account["account_type"],
        "pan": account["pan"],
        "govt_id_like": account["govt_id_like"],
        "ifsc_code": account["ifsc_code"],
        "branch_name": account["branch_name"],
        "available_balance": account["available_balance"],
        "ledger_dump": txns
    }
