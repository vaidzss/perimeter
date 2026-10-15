"""
Payments Router:
10. POST /api/v2/payments/upi-transfer (JWT Auth)
11. POST /api/v2/payments/neft (JWT Auth)
12. GET /api/v2/payments/scheduled (JWT Auth - UNUSED endpoint to verify 'unused' discovery status)
"""

import uuid
import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel, Field

from person1_api_discovery.app.auth import get_current_user, decode_jwt_token
from person1_api_discovery.app.seed_data import SCHEDULED_PAYMENTS_DB, ACCOUNTS_DB
from person1_api_discovery.app.gateway import forward_through_perimeter

router = APIRouter(prefix="/api/v2/payments", tags=["Payments"])


class UPITransferRequest(BaseModel):
    payee_vpa: Optional[str] = Field(None, json_schema_extra={"example": "merchant@okaxis"})
    to_vpa: Optional[str] = None
    from_vpa: Optional[str] = None
    amount: Optional[float] = Field(None, json_schema_extra={"example": 500.00})
    amount_paise: Optional[int] = None
    note: Optional[str] = None
    idempotency_key: Optional[str] = None
    remarks: Optional[str] = Field("Payment via UPI", json_schema_extra={"example": "Dinner with friends"})
    coupons: Optional[List[str]] = Field(None, json_schema_extra={"example": ["SAVE10", "SAVE10"]})


class NEFTTransferRequest(BaseModel):
    beneficiary_account: str = Field(..., json_schema_extra={"example": "ACCN-IN-1015"})
    beneficiary_ifsc: str = Field(..., json_schema_extra={"example": "HDFC0001234"})
    beneficiary_name: str = Field(..., json_schema_extra={"example": "Kavya Deshmukh"})
    amount: float = Field(..., gt=0, json_schema_extra={"example": 15000.00})
    remarks: str = Field("NEFT Transfer", json_schema_extra={"example": "Monthly rent"})


@router.post("/upi-transfer")
async def execute_upi_transfer(
    request: Request,
    payload: UPITransferRequest
):
    """
    Execute instant UPI transfer from authenticated user's account.
    Supports both Person 1 testbed and BharatPay neobank via Perimeter Gateway.
    Also serves as OWASP API3 / API6 Business Logic & Arithmetic Inflation test target.
    """
    # If BharatPay payload (to_vpa or amount_paise present)
    if payload.to_vpa or payload.amount_paise is not None:
        return await forward_through_perimeter(request)

    # Person 1 authentication check
    auth_header = request.headers.get("authorization", "")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = auth_header.split(" ")[1]
    current_user = decode_jwt_token(token)

    user_account_id = current_user.get("account_id", "1001")
    account = ACCOUNTS_DB.get(user_account_id)
    transfer_amount = payload.amount or 0.0
    discount = 0.0
    if payload.coupons:
        # Vulnerable coupon stacking logic: duplicate coupons allowed
        discount = len(payload.coupons) * 10.0

    effective_amount = transfer_amount - discount

    if account and transfer_amount > 0 and account["available_balance"] < effective_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds for UPI transfer"
        )

    txn_ref = f"UPI{uuid.uuid4().hex[:10].upper()}"
    return {
        "status": "SUCCESS",
        "txn_reference": txn_ref,
        "from_account": user_account_id,
        "payee_vpa": payload.payee_vpa or payload.to_vpa,
        "amount": transfer_amount,
        "effective_amount": effective_amount,
        "coupons_applied": payload.coupons or [],
        "currency": "INR",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


@router.post("/neft")
async def execute_neft_transfer(
    payload: NEFTTransferRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Execute NEFT domestic wire transfer (JWT Auth).
    """
    user_account_id = current_user.get("account_id", "1001")
    utr_number = f"NEFT-IN-{uuid.uuid4().hex[:12].upper()}"
    return {
        "status": "PENDING_BATCH_SETTLEMENT",
        "utr_number": utr_number,
        "from_account": user_account_id,
        "beneficiary_account": payload.beneficiary_account,
        "beneficiary_name": payload.beneficiary_name,
        "beneficiary_ifsc": payload.beneficiary_ifsc,
        "amount": payload.amount,
        "settlement_window": "Next NEFT hourly batch cycle",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


@router.get("/scheduled")
async def get_scheduled_payments(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List recurring scheduled payments.
    ORPHANED/UNUSED API SPECIFICATION TARGET:
    Documented in openapi_partial.json, but intentionally left un-hit during standard
    traffic simulation to verify the Spec-Diff Engine's 'UNUSED' classification status.
    """
    return {
        "scheduled_count": len(SCHEDULED_PAYMENTS_DB),
        "scheduled_payments": SCHEDULED_PAYMENTS_DB
    }


@router.get("/fx-rate")
async def get_fx_rate(
    from_currency: str = Query("USD", description="Source currency"),
    to_currency: str = Query("INR", description="Target currency"),
    vendor_poisoned: bool = Query(False, description="Simulate compromised third-party supplier returning poisoned payload"),
    enforce_guard: bool = Query(False, description="Enforce SafeExternalAPIClient egress guard defense")
):
    """
    Get live FX conversion rate (OWASP API10: Unsafe Consumption of Third-Party APIs target).
    Simulates calling an external currency vendor API protected by SafeExternalAPIClient.
    """
    from person1_api_discovery.app.egress_guard import safe_external_client, FXRateVendorResponse

    if vendor_poisoned:
        vendor_raw = {
            "vendor": "AlphaFxGlobalFeed",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": -83.25,  # Negative rate anomaly
            "quote_id": "QUOTE-POISONED-'; DROP TABLE fx_cache; --",  # SQLi in vendor quote
            "script_tag": "<script>alert('vendor_xss')</script>",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    else:
        vendor_raw = {
            "vendor": "AlphaFxGlobalFeed",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 83.25,
            "quote_id": f"QUOTE-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    # Always inspect with SafeExternalAPIClient to emit OWASP API10 telemetry
    inspection = safe_external_client.inspect_vendor_response(
        vendor_raw,
        schema_model=FXRateVendorResponse,
        numeric_bounds={"rate": (0.0001, 1_000_000.0)}
    )

    if enforce_guard and inspection.is_poisoned:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "SUPPLY_CHAIN_POISONING_BLOCKED",
                "owasp_tag": "API10:2023 Unsafe Consumption of APIs",
                "threat_indicators": inspection.threat_indicators,
                "reasons": inspection.reasons,
                "details": inspection.details
            }
        )

    return vendor_raw

