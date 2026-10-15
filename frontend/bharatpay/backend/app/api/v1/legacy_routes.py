"""
Legacy v1 Migration Endpoints - TARGET VULNERABILITY
Tag: "legacy_version": "v1", "deprecated_since": "2024-01-01"
WARNING: Deliberately vulnerable zombie endpoint for CC6-IC07 ASPM Discovery testing.
Exposes unmasked synthetic PII without authentication.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.kyc import KYCRecord

# include_in_schema=False ensures this shadow route is never documented in OpenAPI
router = APIRouter(prefix="/kyc", tags=["Legacy KYC"], include_in_schema=False)

class UnmaskedKYCDumpItem(BaseModel):
    user_code: str
    full_name: str
    phone: str
    email: str
    pan_unmasked: str
    aadhaar_unmasked: str
    kyc_status: str
    watermark: str = "SYNTHETIC TEST DATA — CC6-IC07"

@router.get("/aadhaar-pan-dump", response_model=List[UnmaskedKYCDumpItem])
def dump_all_kyc_data(db: Session = Depends(get_db)):
    """
    [ZOMBIE / SHADOW ENDPOINT]
    Legacy batch KYC migration route from Q1 2024 that was never deprecated or removed.
    VULNERABILITY: No authentication required; dumps all synthetic PAN and Aadhaar records unmasked.
    """
    users = db.query(User).all()
    results = []

    for user in users:
        kyc = db.query(KYCRecord).filter(KYCRecord.user_id == user.id).first()
        results.append(
            UnmaskedKYCDumpItem(
                user_code=user.user_code,
                full_name=user.full_name,
                phone=user.phone,
                email=user.email,
                pan_unmasked=kyc.pan_synthetic if kyc else "ABCDE1234F",
                aadhaar_unmasked=kyc.aadhaar_synthetic if kyc else "999988880000",
                kyc_status=kyc.kyc_status if kyc else "VERIFIED"
            )
        )

    return results
