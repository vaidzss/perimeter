"""
Authentication and JWT management for Person 1: FinTech DPI Banking API.
Handles token creation, validation, and FastAPI security dependencies using PyJWT.
"""

import os
import uuid
import datetime
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status
import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sentinel-person1-supersecret-jwt-key-9841")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def create_jwt_token(
    sub: str,
    role: str = "customer",
    account_id: Optional[str] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """Issue a signed JWT token containing standard claims (sub, role, jti, iat, exp)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "account_id": account_id or sub.replace("user_", ""),
        "jti": f"tok_{uuid.uuid4().hex[:12]}",
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "iss": "sentinel-fintech-bank"
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token, raising an error on invalid signature or expiration."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI dependency: Enforces valid Bearer JWT.
    Returns decoded token claims or raises HTTP 401 Unauthorized.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected 'Bearer <token>'"
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_jwt_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token has expired"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT signature or malformed token claims"
        )


def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Optional dependency that returns token claims if valid, or None if unauthenticated."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    try:
        return decode_jwt_token(token)
    except Exception:
        return None
