from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    # Can be email or 10-digit phone number
    identifier: str
    password: Optional[str] = None
    otp: Optional[str] = None  # OTP-stub: "123456" always works in test mode

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    jti: str
    user_id: str
    account_id: int
    watermark: str = "SYNTHETIC TEST DATA — CC6-IC07"

class UserProfileResponse(BaseModel):
    user_code: str
    email: str
    phone: str
    full_name: str
    role: str
    account_id: int
    account_number_masked: str
    vpa: str
    kyc_status: str
    masked_pan: str
    watermark: str = "SYNTHETIC TEST DATA — CC6-IC07"
