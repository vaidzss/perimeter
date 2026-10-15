import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import jwt
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.organization import Employee, Role, AccessGrant

security_scheme = HTTPBearer(auto_error=False)

def create_internal_token(
    employee_id: str,
    role: str,
    scope: str,
    department: str,
    region: str,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, str]:
    """
    Creates a scoped internal JWT token for provisioned employees.
    Separate claim set from customer tokens.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=12)  # 12-hour privileged shift token

    jti = str(uuid.uuid4())
    payload = {
        "token_type": "internal",
        "employee_id": employee_id,
        "role": role,
        "scope": scope,
        "department": department,
        "region": region,
        "provisioned_at": int(now.timestamp()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": jti
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti


def decode_internal_token(token: str) -> dict:
    """Decodes and validates internal scoped token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("token_type") != "internal":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: internal privileged token required"
            )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired internal credentials: {str(e)}"
        )


async def get_current_internal_employee(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> dict:
    """
    FastAPI dependency validating Bearer token and ensuring employee is provisioned and active.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header Bearer token"
        )

    payload = decode_internal_token(credentials.credentials)
    emp_id = payload.get("employee_id")
    if not emp_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims: missing employee_id"
        )

    # Verify against live DB
    employee = db.query(Employee).filter(Employee.employee_id == emp_id).first()
    if not employee or employee.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee identity revoked or not active"
        )

    # Attach to request.state for telemetry logging
    request.state.actor_employee_id = emp_id
    request.state.actor_role = employee.role_rel.role_name if employee.role_rel else payload.get("role")
    request.state.actor_scope = payload.get("scope")

    return {
        "payload": payload,
        "employee": employee,
        "role": employee.role_rel.role_name if employee.role_rel else payload.get("role"),
        "scope": payload.get("scope"),
        "department": employee.department,
        "region": employee.region
    }


def require_role(allowed_roles: List[str]):
    """Enforces caller role authorization."""
    def role_checker(auth_data: dict = Depends(get_current_internal_employee)) -> dict:
        caller_role = auth_data["role"]
        if caller_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role in {allowed_roles}, but caller has '{caller_role}'"
            )
        return auth_data
    return role_checker
