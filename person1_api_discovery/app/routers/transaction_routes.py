"""
Transactions Router:
8. GET /api/v2/accounts/{account_id}/transactions (JWT Auth - BOLA vulnerable)
9. GET /api/v2/transactions/{txn_id}/receipt (JWT Auth - BOLA vulnerable)
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from person1_api_discovery.app.auth import get_current_user
from person1_api_discovery.app.seed_data import TRANSACTIONS_DB, RECEIPTS_DB, ACCOUNTS_DB

router = APIRouter(prefix="/api/v2", tags=["Transactions"])


@router.get("/accounts/{account_id}/transactions")
async def get_account_transactions(
    account_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List transaction history for an account.
    VULNERABILITY (BOLA/IDOR): Does not check if jwt.sub / jwt.account_id matches {account_id}.
    """
    txns = TRANSACTIONS_DB.get(account_id)
    if txns is None:
        if account_id.isdigit():
            # Return synthetic transactions for arbitrary numeric IDs
            return [
                {
                    "txn_id": f"TXN{account_id}01",
                    "account_id": account_id,
                    "amount": 1450.00,
                    "type": "CREDIT",
                    "description": "UPI Transfer Inward",
                    "status": "COMPLETED",
                    "timestamp": "2026-10-12T11:20:00Z"
                }
            ]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return txns


@router.get("/transactions/{txn_id}/receipt")
async def get_transaction_receipt(
    txn_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Fetch official transaction tax receipt with GST and PII.
    VULNERABILITY (BOLA/IDOR): Allows any authenticated user to view receipts for arbitrary {txn_id}.
    """
    receipt = RECEIPTS_DB.get(txn_id)
    if not receipt:
        # Fallback synthesis for ad-hoc transaction ID probes
        return {
            "receipt_id": f"RCP-{txn_id}",
            "txn_id": txn_id,
            "account_id": "1004",
            "amount": 2450.00,
            "currency": "INR",
            "sender_upi": "user_1004@okaxis",
            "beneficiary_name": "Quick Bharat Merchant",
            "tax_invoice_no": f"INV-{txn_id}",
            "pan_masked": "ABCDE1004F",
            "status": "SUCCESS",
            "issued_at": "2026-10-14T10:00:00Z"
        }
    return receipt
