from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class TransactionItem(BaseModel):
    id: int
    txn_reference: str
    from_vpa: str
    to_vpa: str
    amount_paise: int
    note: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StatementResponse(BaseModel):
    account_id: int
    account_number_masked: str
    ifsc_code: str
    balance_paise: int
    currency: str
    daily_limit_paise: int
    vpa: str
    kyc_status: str
    masked_pan: str
    transactions: List[TransactionItem]
    watermark: str = "SYNTHETIC TEST DATA — CC6-IC07"

class MerchantItem(BaseModel):
    id: int
    merchant_code: str
    business_name: str
    vpa: str
    category: str
    verified: bool
    rating: float

    model_config = ConfigDict(from_attributes=True)

class PaginatedMerchantsResponse(BaseModel):
    items: List[MerchantItem]
    total: int
    page: int
    limit: int
    total_pages: int
    watermark: str = "SYNTHETIC TEST DATA — CC6-IC07"

class UPITransferRequest(BaseModel):
    from_vpa: str
    to_vpa: str
    amount_paise: int = Field(gt=0, description="Amount in integer paise (e.g. 10000 = Rs 100)")
    note: Optional[str] = "UPI Transfer"
    idempotency_key: Optional[str] = None

class UPITransferResponse(BaseModel):
    txn_reference: str
    status: str
    from_vpa: str
    to_vpa: str
    amount_paise: int
    remaining_balance_paise: int
    daily_limit_remaining_paise: int
    note: str
    created_at: datetime
    idempotent_replay: bool = False
    watermark: str = "SYNTHETIC TEST DATA — CC6-IC07"
