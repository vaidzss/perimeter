from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.account import Account

security_bearer = HTTPBearer(auto_error=False)

def get_current_user_payload(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer)
) -> dict:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or tampered authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Store token metadata in request.state for structured logging middleware
    request.state.auth_type = "bearer"
    request.state.token_id = payload.get("jti")
    request.state.user_id = payload.get("sub")
    request.state.account_id = payload.get("account_id")
    
    return payload

def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db)
) -> tuple[User, Account]:
    user_id_code = payload.get("sub")
    user = db.query(User).filter(User.user_code == user_id_code).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User belonging to this token no longer exists"
        )
    
    account_id = payload.get("account_id")
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account in token claims does not match user account"
        )
    
    return user, account
