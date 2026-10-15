from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.account import Account
from app.models.upi import UPIProfile
from app.models.kyc import KYCRecord
from app.schemas.auth import LoginRequest, TokenResponse, UserProfileResponse
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Authenticate a user via email/phone and password, or test OTP stub ('123456').
    Issues a signed JWT access token containing sub, account_id, role, iat, exp, jti.
    """
    # 1. Look up user by email or phone
    identifier = login_req.identifier.strip()
    user = db.query(User).filter(
        (User.email == identifier) | (User.phone == identifier) | (User.user_code == identifier)
    ).first()

    authenticated = False

    if user:
        # Check OTP stub ("123456" accepted in synthetic test mode)
        if login_req.otp and login_req.otp.strip() == "123456":
            authenticated = True
        elif login_req.password:
            authenticated = verify_password(login_req.password, user.hashed_password)

    if not authenticated:
        # Tag distinct event for brute-force / failed-auth detection in request telemetry
        request.state.auth_event = "LOGIN_FAILED"
        request.state.failed_identifier = identifier
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or incorrect test OTP"
        )

    # 2. Get user's primary account
    account = db.query(Account).filter(Account.user_id == user.id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account profile is missing for user"
        )

    # 3. Issue JWT Token with jti
    token, jti = create_access_token(user_id=user.user_code, account_id=account.id, role=user.role)

    # Tag successful auth state for logging
    request.state.auth_event = "LOGIN_SUCCESS"
    request.state.user_id = user.user_code
    request.state.token_id = jti

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=60 * 24 * 60,
        jti=jti,
        user_id=user.user_code,
        account_id=account.id
    )

@router.get("/me", response_model=UserProfileResponse)
def get_me(current_data: tuple[User, Account] = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns current authenticated user profile.
    Guarantees all PII is synthetic and PAN/Aadhaar are masked.
    """
    user, account = current_data
    upi = db.query(UPIProfile).filter(UPIProfile.account_id == account.id).first()
    kyc = db.query(KYCRecord).filter(KYCRecord.user_id == user.id).first()

    return UserProfileResponse(
        user_code=user.user_code,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        account_id=account.id,
        account_number_masked=account.masked_account_number,
        vpa=upi.vpa if upi else f"{user.user_code}@bharatpay",
        kyc_status=kyc.kyc_status if kyc else "PENDING",
        masked_pan=kyc.masked_pan if kyc else "NOT_FOUND"
    )
