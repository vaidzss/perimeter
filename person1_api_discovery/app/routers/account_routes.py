"""
Accounts Router:
5. GET /api/v2/accounts/{account_id} (JWT Auth - BOLA vulnerable)
6. GET /api/v2/accounts/{account_id}/statements (JWT Auth - BOLA vulnerable)
7. POST /api/v2/accounts/beneficiaries (JWT Auth)
"""

import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field

from person1_api_discovery.app.auth import get_current_user
from person1_api_discovery.app.seed_data import ACCOUNTS_DB, TRANSACTIONS_DB, BENEFICIARIES_DB

router = APIRouter(prefix="/api/v2/accounts", tags=["Accounts"])


class AccountDetailResponse(BaseModel):
    account_id: str
    user_id: str
    account_number: str
    account_holder: str
    currency: str
    available_balance: float
    ledger_balance: float
    account_type: str
    status: str
    ifsc_code: str
    branch_name: str
    pan: str
    govt_id_like: str
    created_at: str


class AddBeneficiaryRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Siddharth Rao"})
    account_number: str = Field(..., json_schema_extra={"example": "ACCN-IN-1011"})
    ifsc: str = Field(..., json_schema_extra={"example": "HDFC0001234"})
    upi_vpa: Optional[str] = Field(None, json_schema_extra={"example": "siddharth@okaxis"})


@router.get("/{account_id}", response_model=AccountDetailResponse)
async def get_account_by_id(
    account_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve bank account details by account ID.
    VULNERABILITY (OWASP API1:2023 - BOLA/IDOR):
    Requires valid JWT auth, but DOES NOT verify if jwt.sub or jwt.account_id matches
    the path {account_id}. Any valid user token can dump arbitrary accounts, balances,
    PAN numbers, and government ID placeholders.
    """
    account = ACCOUNTS_DB.get(account_id)
    if not account:
        # Fallback synthesis for dynamic numeric probes
        if account_id.isdigit():
            seed = int(account_id)
            return AccountDetailResponse(
                account_id=account_id,
                user_id=f"user_{account_id}",
                account_number=f"ACCN-IN-{account_id}",
                account_holder=f"DPI Account Holder {account_id}",
                currency="INR",
                available_balance=round(35000.0 + (seed % 1000) * 12.5, 2),
                ledger_balance=round(35000.0 + (seed % 1000) * 12.5, 2),
                account_type="SAVINGS",
                status="ACTIVE",
                ifsc_code="HDFC0001234",
                branch_name="Central FinTech Branch",
                pan=f"ABCDE{account_id[-4:] if len(account_id) >= 4 else '9999'}F",
                govt_id_like=f"[GOVT-ID-XXXX-{account_id[-4:] if len(account_id) >= 4 else '9999'}]",
                created_at="2024-01-15T10:00:00Z"
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return AccountDetailResponse(**account)


@router.get("/{account_id}/statements")
async def get_account_statements(
    account_id: str,
    format: str = Query("json", description="Statement format (json, pdf)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate account ledger statement.
    VULNERABILITY (BOLA/IDOR): Fails to verify ownership of {account_id}.
    """
    account = ACCOUNTS_DB.get(account_id)
    txns = TRANSACTIONS_DB.get(account_id, [])

    if not account and not txns:
        if not account_id.isdigit():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    holder = account["account_holder"] if account else f"Holder {account_id}"
    balance = account["available_balance"] if account else 50000.00
    pan = account["pan"] if account else "ABCDE9999F"

    return {
        "statement_id": f"STM-{account_id}-202610",
        "account_id": account_id,
        "account_holder": holder,
        "pan": pan,
        "currency": "INR",
        "opening_balance": balance,
        "closing_balance": balance,
        "period": "2026-10-01 to 2026-10-15",
        "transactions_count": len(txns),
        "transactions": txns
    }


@router.post("/beneficiaries")
async def add_beneficiary(
    payload: AddBeneficiaryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a trusted beneficiary to authenticated user's account (JWT Auth).
    """
    user_account = current_user.get("account_id", "1001")
    new_ben = {
        "beneficiary_id": f"BEN-{user_account}-{len(BENEFICIARIES_DB.get(user_account, [])) + 1}",
        "name": payload.name,
        "account_number": payload.account_number,
        "ifsc": payload.ifsc,
        "upi_vpa": payload.upi_vpa or f"{payload.name.lower().replace(' ', '.')}@okaxis",
        "status": "VERIFIED"
    }
    BENEFICIARIES_DB.setdefault(user_account, []).append(new_ben)

    return {
        "status": "success",
        "message": "Beneficiary registered successfully",
        "beneficiary": new_ben
    }


@router.post("/import-statement")
async def import_statement(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Import external statement batch (OWASP API4: Algorithmic Complexity & ReDoS target).
    Accepts deeply nested JSON structures or evil regex pattern strings.
    """
    body_bytes = await request.body()
    user_account = current_user.get("account_id", "1001")
    parsed_json = None
    raw_text = ""
    try:
        raw_text = body_bytes.decode("utf-8", errors="ignore")
        parsed_json = json.loads(raw_text)
    except Exception:
        pass

    return {
        "status": "PROCESSED",
        "account_id": user_account,
        "payload_bytes": len(body_bytes),
        "is_json": parsed_json is not None,
        "entries_count": len(parsed_json) if isinstance(parsed_json, list) else 1,
        "sample": raw_text[:200]
    }
