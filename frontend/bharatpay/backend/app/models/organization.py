from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Role(Base):
    """
    Role table encoding operational norms, default scope, daily baseline rate limit,
    and allowed endpoint patterns for privileged access.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, index=True, nullable=False)
    level = Column(Integer, nullable=False)  # 1=Employee, 2=Sales Manager, 3=Regional Head, 4=VP Sales, 5=IT Admin
    default_scope = Column(String(100), nullable=False)  # 'support-tickets', 'region', 'multi-region', 'org-wide', 'ops-only', 'none'
    default_rate_limit = Column(Integer, nullable=False)  # Normal baseline queries/lookups per day
    campaign_rate_limit = Column(Integer, nullable=True)  # Allowed baseline during active campaign window
    description = Column(String(255), nullable=True)
    allowed_endpoints_json = Column(Text, default="[]", nullable=False)

    @property
    def allowed_endpoints(self):
        try:
            return json.loads(self.allowed_endpoints_json or "[]")
        except Exception:
            return []

    @allowed_endpoints.setter
    def allowed_endpoints(self, val):
        self.allowed_endpoints_json = json.dumps(val or [])

    # Relationships
    employees = relationship("Employee", back_populates="role_rel")


class Employee(Base):
    """
    Employee model for HR/IT-provisioned internal identities.
    Every employee has an explicit role, department, declared region/scope, and manager.
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String(32), unique=True, index=True, nullable=False)  # e.g. EMP-1001
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    department = Column(String(100), nullable=False)  # 'Customer Support', 'Sales', 'Operations', 'IT Ops'
    region = Column(String(100), nullable=False)      # 'West', 'North', 'South', 'East', 'North-East', 'org-wide', 'IT-Infra'
    manager_id = Column(String(32), nullable=True)     # Reference to manager employee_id
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, SUSPENDED, DEPROVISIONED
    hire_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    role_rel = relationship("Role", back_populates="employees")
    access_grants = relationship("AccessGrant", back_populates="employee", cascade="all, delete-orphan")


class AccessGrant(Base):
    """
    Explicit, time-bounded permission grants expanding or adjusting an employee's scope.
    No employee has implicit access beyond declared scope without a grant.
    """
    __tablename__ = "access_grants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False, index=True)
    resource_scope = Column(String(255), nullable=False)  # e.g. 'region:North', 'reports:bulk-export'
    granted_by = Column(String(32), nullable=False)      # IT Admin employee_id
    granted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="access_grants")


class Campaign(Base):
    """
    Sanctioned high-traffic business events (e.g. Diwali Sale 2026).
    Informs detection engine that elevated volume within specific roles & regions is expected.
    """
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    affected_regions_json = Column(Text, default="[]", nullable=False)
    expected_roles_json = Column(Text, default="[]", nullable=False)
    expected_volume_multiplier = Column(Integer, default=5, nullable=False)
    created_by = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def affected_regions(self):
        try:
            return json.loads(self.affected_regions_json or "[]")
        except Exception:
            return []

    @affected_regions.setter
    def affected_regions(self, val):
        self.affected_regions_json = json.dumps(val or [])

    @property
    def expected_roles(self):
        try:
            return json.loads(self.expected_roles_json or "[]")
        except Exception:
            return []

    @expected_roles.setter
    def expected_roles(self, val):
        self.expected_roles_json = json.dumps(val or [])
