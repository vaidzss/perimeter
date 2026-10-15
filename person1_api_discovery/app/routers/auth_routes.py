"""
Auth Router:
1. POST /api/v2/auth/login (Public / No Auth - issues JWT)
2. POST /api/v2/auth/refresh (JWT Auth - refreshes token)
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field

from person1_api_discovery.app.auth import create_jwt_token, get_current_user
from person1_api_discovery.app.seed_data import USERS_DB
from person1_api_discovery.app.gateway import forward_through_perimeter

router = APIRouter(prefix="/api/v2/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: Optional[str] = Field(None, json_schema_extra={"example": "user_1001"})
    identifier: Optional[str] = Field(None, json_schema_extra={"example": "priya.sharma@bharatpay.com"})
    password: Optional[str] = Field(None, json_schema_extra={"example": "pass123"})
    otp: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None
    account_id: Optional[int] = None
    user_id: Optional[str] = None
    jti: Optional[str] = None
    expires_in: Optional[int] = None
    watermark: Optional[str] = None


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str = "Token refreshed successfully"


@router.post("/login")
async def login(credentials: LoginRequest, request: Request):
    """
    Public Authentication endpoint (No Auth).
    Supports both Person 1 testbed users and BharatPay neobank users via Perimeter Gateway.
    """
    # If BharatPay login request (uses 'identifier')
    if credentials.identifier:
        return await forward_through_perimeter(request)

    user = USERS_DB.get(credentials.username or "")
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_jwt_token(
        sub=user["user_id"],
        role=user["role"],
        account_id=user["account_id"]
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user={
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "role": user["role"],
            "account_id": user["account_id"],
            "email": user["email"]
        }
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Refresh access token (JWT Auth).
    Issues a new access token with fresh jti and expiration.
    """
    new_token = create_jwt_token(
        sub=current_user["sub"],
        role=current_user.get("role", "customer"),
        account_id=current_user.get("account_id")
    )
    return RefreshResponse(access_token=new_token)
