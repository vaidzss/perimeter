import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.organization import Role, Employee, AccessGrant, Campaign
from app.models.request_log import RequestLog
from app.core.security import verify_password, get_password_hash
from app.core.internal_auth import (
    create_internal_token,
    get_current_internal_employee,
    require_role
)

router = APIRouter(prefix="", tags=["Provisioning & Identity"])

# Schemas
class EmployeeOnboardRequest(BaseModel):
    name: str = Field(...)
    email: str = Field(...)
    role: str = Field(...)
    department: str = Field(..., example="Sales")
    region: str = Field(..., example="org-wide")
    manager_id: Optional[str] = Field(None, example="EMP-1001")
    custom_scope: Optional[str] = Field(None, example="org-wide")
    grant_reason: Optional[str] = Field(None, example="Q4 Regional Expansion Oversight")
    grant_expires_days: Optional[int] = Field(30, example=30)
    password: Optional[str] = Field("Employee@123")


class CampaignCreateRequest(BaseModel):
    name: str = Field(..., example="Diwali Sale 2026")
    start_date: datetime
    end_date: datetime
    affected_regions: List[str] = Field(..., example=["West", "North", "org-wide"])
    expected_roles: List[str] = Field(..., example=["VP Sales", "Regional Head", "Sales Manager"])
    expected_volume_multiplier: int = Field(5, ge=1, le=50)


class EmployeeLoginRequest(BaseModel):
    email: str
    password: str


@router.post("/employees/login")
def internal_employee_login(login_req: EmployeeLoginRequest, db: Session = Depends(get_db)):
    """Authenticate internal employee and return scoped token."""
    emp = db.query(Employee).filter(Employee.email == login_req.email).first()
    if not emp or not verify_password(login_req.password, emp.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee corporate credentials"
        )

    if emp.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Employee account is {emp.status}"
        )

    role_name = emp.role_rel.role_name if emp.role_rel else "Employee (Support)"
    default_scope = emp.role_rel.default_scope if emp.role_rel else "support-tickets"

    token, jti = create_internal_token(
        employee_id=emp.employee_id,
        role=role_name,
        scope=default_scope,
        department=emp.department,
        region=emp.region
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "jti": jti,
        "employee_id": emp.employee_id,
        "name": emp.name,
        "role": role_name,
        "scope": default_scope,
        "region": emp.region,
        "department": emp.department
    }


@router.post("/employees/onboard")
def onboard_employee(
    payload: EmployeeOnboardRequest,
    request: Request,
    auth_data: dict = Depends(get_current_internal_employee),
    db: Session = Depends(get_db)
):
    """
    IT Admin registers a new employee with role + scope.
    Guards:
    - Caller MUST have IT Admin role.
    - If non-IT Admin tries to onboard or grant privileged scope, reject with 403
      and record privilege escalation attempt in request log.
    - Onboarding does not grant unlimited access — grants exact role default scope,
      or bounded AccessGrant if explicitly justified.
    """
    caller_role = auth_data["role"]
    caller_id = auth_data["payload"].get("employee_id")

    if caller_role != "IT Admin":
        # Tag on request state so telemetry captures the attempt
        request.state.privilege_escalation_attempt = True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Privilege escalation attempt: caller '{caller_id}' with role '{caller_role}' lacks IT Admin authority to onboard employees"
        )

    # Validate target role exists
    role_obj = db.query(Role).filter(Role.role_name == payload.role).first()
    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{payload.role}' does not exist in roles catalog"
        )

    # Check if email already registered
    existing_emp = db.query(Employee).filter(Employee.email == payload.email).first()
    if existing_emp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with email '{payload.email}' already exists"
        )

    # Generate employee_id
    emp_count = db.query(Employee).count() + 1
    new_emp_id = f"EMP-{2000 + emp_count}"

    # Determine assigned scope (default scope of role)
    effective_scope = role_obj.default_scope

    # If custom scope requested and different from default, must have grant_reason
    extra_grant = None
    if payload.custom_scope and payload.custom_scope != role_obj.default_scope:
        if not payload.grant_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom scope expansion requires an explicit 'grant_reason' and expiry"
            )
        effective_scope = payload.custom_scope
        days = payload.grant_expires_days or 30
        now = datetime.now(timezone.utc)
        extra_grant = AccessGrant(
            employee_id=new_emp_id,
            resource_scope=payload.custom_scope,
            granted_by=caller_id,
            granted_at=now,
            expires_at=now + timedelta(days=days),
            reason=payload.grant_reason
        )

    # Create Employee
    new_emp = Employee(
        employee_id=new_emp_id,
        name=payload.name,
        email=payload.email,
        hashed_password=get_password_hash(payload.password or "Employee@123"),
        role_id=role_obj.id,
        department=payload.department,
        region=payload.region,
        manager_id=payload.manager_id,
        status="ACTIVE",
        hire_date=datetime.now(timezone.utc)
    )
    db.add(new_emp)
    if extra_grant:
        db.add(extra_grant)
    db.commit()
    db.refresh(new_emp)

    # Issue scoped internal JWT
    token, jti = create_internal_token(
        employee_id=new_emp_id,
        role=role_obj.role_name,
        scope=effective_scope,
        department=new_emp.department,
        region=new_emp.region
    )

    return {
        "status": "PROVISIONED",
        "employee_id": new_emp_id,
        "name": new_emp.name,
        "email": new_emp.email,
        "role": role_obj.role_name,
        "scope": effective_scope,
        "region": new_emp.region,
        "department": new_emp.department,
        "token_type": "bearer",
        "access_token": token,
        "jti": jti,
        "has_custom_grant": extra_grant is not None,
        "message": f"Employee {new_emp_id} successfully provisioned with role {role_obj.role_name} and scope {effective_scope}"
    }


@router.post("/campaigns")
def create_campaign(
    payload: CampaignCreateRequest,
    auth_data: dict = Depends(get_current_internal_employee),
    db: Session = Depends(get_db)
):
    """
    IT Admin or VP Sales registers a sanctioned high-traffic campaign window.
    Tells the detection engine: elevated volume from expected_roles within affected_regions
    during [start_date, end_date] is expected business activity.
    """
    caller_role = auth_data["role"]
    caller_id = auth_data["payload"].get("employee_id")

    if caller_role not in ["IT Admin", "VP Sales"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Campaign registration restricted to IT Admin or VP Sales. Caller role '{caller_role}' is not authorized."
        )

    code = f"CAMP-{uuid.uuid4().hex[:8].upper()}"
    campaign = Campaign(
        campaign_code=code,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        affected_regions_json=json.dumps(payload.affected_regions),
        expected_roles_json=json.dumps(payload.expected_roles),
        expected_volume_multiplier=payload.expected_volume_multiplier,
        created_by=caller_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return {
        "status": "REGISTERED",
        "campaign_code": campaign.campaign_code,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat(),
        "affected_regions": campaign.affected_regions,
        "expected_roles": campaign.expected_roles,
        "expected_volume_multiplier": campaign.expected_volume_multiplier,
        "created_by": campaign.created_by
    }


@router.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    """List all registered sanctioned campaigns."""
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    now = datetime.now(timezone.utc)
    return [
        {
            "id": c.id,
            "campaign_code": c.campaign_code,
            "name": c.name,
            "start_date": c.start_date.isoformat(),
            "end_date": c.end_date.isoformat(),
            "affected_regions": c.affected_regions,
            "expected_roles": c.expected_roles,
            "expected_volume_multiplier": c.expected_volume_multiplier,
            "created_by": c.created_by,
            "is_active": c.start_date.replace(tzinfo=timezone.utc if c.start_date.tzinfo is None else None) <= now <= c.end_date.replace(tzinfo=timezone.utc if c.end_date.tzinfo is None else None)
        }
        for c in campaigns
    ]


@router.get("/employees")
def list_employees(
    db: Session = Depends(get_db),
    auth_data: dict = Depends(get_current_internal_employee)
):
    """List employee directory with role, scope, and status."""
    employees = db.query(Employee).order_by(Employee.id.asc()).all()
    return [
        {
            "employee_id": e.employee_id,
            "name": e.name,
            "email": e.email,
            "role": e.role_rel.role_name if e.role_rel else "Unknown",
            "department": e.department,
            "region": e.region,
            "default_scope": e.role_rel.default_scope if e.role_rel else "none",
            "status": e.status,
            "manager_id": e.manager_id,
            "hire_date": e.hire_date.isoformat(),
            "grants_count": len(e.access_grants)
        }
        for e in employees
    ]


@router.get("/employees/{id}/access-log")
def get_employee_access_log(
    id: str,
    limit: int = Query(50, ge=1, le=200),
    auth_data: dict = Depends(get_current_internal_employee),
    db: Session = Depends(get_db)
):
    """
    Audit trail of what an employee actually accessed.
    Queries the shared requests table for historical telemetry.
    """
    caller_role = auth_data["role"]
    caller_id = auth_data["payload"].get("employee_id")

    # Only IT Admin or the employee themselves can view their access log
    if caller_role != "IT Admin" and caller_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: cannot inspect audit logs of employee '{id}'"
        )

    logs = (
        db.query(RequestLog)
        .filter(RequestLog.user_id == id)
        .order_by(RequestLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    return {
        "employee_id": id,
        "total_recorded": len(logs),
        "access_logs": [
            {
                "request_id": log.request_id,
                "timestamp": log.timestamp.isoformat(),
                "method": log.method,
                "path_template": log.path_template,
                "raw_path": log.raw_path,
                "status_code": log.status_code,
                "latency_ms": log.latency_ms,
                "client_ip": log.client_ip,
                "token_id": log.token_id,
                "object_ids": json.loads(log.object_ids or "[]")
            }
            for log in logs
        ]
    }
