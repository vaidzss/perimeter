import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.organization import Role, Employee, AccessGrant, Campaign
from app.models.account import Account

def test_checkpoint11_roles_encode_operational_norms():
    """
    Acceptance Criteria:
    Role table clearly encodes what's NORMAL for that role:
    - Sales Manager: up to 500 account lookups/day within their region
    - VP: up to 5,000/day org-wide during an active campaign, 200/day otherwise
    - IT Admin: ops only
    """
    db = SessionLocal()
    try:
        roles = {r.role_name: r for r in db.query(Role).all()}
        assert "Employee (Support)" in roles
        assert "Sales Manager" in roles
        assert "Regional Head" in roles
        assert "VP Sales" in roles
        assert "IT Admin" in roles
        assert "Customer" in roles

        # Check Sales Manager norms
        sm = roles["Sales Manager"]
        assert sm.default_rate_limit == 500
        assert sm.default_scope == "region"
        assert "/api/v2/internal/reports/regional-sales" in sm.allowed_endpoints

        # Check VP Sales norms
        vp = roles["VP Sales"]
        assert vp.default_rate_limit == 200
        assert vp.campaign_rate_limit == 5000
        assert vp.default_scope == "org-wide"
        assert "/api/v2/internal/reports/org-wide-summary" in vp.allowed_endpoints

        # Check IT Admin norms
        admin = roles["IT Admin"]
        assert admin.default_scope == "ops-only"
        assert "/api/v2/internal/employees/onboard" in admin.allowed_endpoints

        # Check Customer norms
        cust = roles["Customer"]
        assert cust.default_scope == "none"
        assert len(cust.allowed_endpoints) == 0

    finally:
        db.close()


def test_checkpoint11_employees_have_explicit_role_and_scope():
    """
    Acceptance Criteria:
    - Seed ~12 employees across these roles with realistic Indian names/departments
    - Every employee has exactly one role and a defined scope (region/department list, or 'org-wide' for VP)
    """
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        assert len(employees) >= 12

        for emp in employees:
            assert emp.employee_id.startswith("EMP-")
            assert emp.name is not None and len(emp.name) > 3
            assert emp.email.endswith("@corp.bharatpay.com")
            assert emp.role_rel is not None
            assert emp.role_rel.role_name in [
                "Employee (Support)",
                "Sales Manager",
                "Regional Head",
                "VP Sales",
                "IT Admin"
            ]
            assert emp.department in ["Customer Support", "Sales", "Operations", "IT Ops"]
            assert emp.region in ["West", "North", "South", "East", "org-wide", "IT-Infra"]
            assert emp.status == "ACTIVE"

        # Check specific roles are seeded
        roles_present = {emp.role_rel.role_name for emp in employees}
        assert "IT Admin" in roles_present
        assert "VP Sales" in roles_present
        assert "Regional Head" in roles_present
        assert "Sales Manager" in roles_present
        assert "Employee (Support)" in roles_present

        # Verify VP has org-wide scope
        vp = db.query(Employee).join(Role).filter(Role.role_name == "VP Sales").first()
        assert vp is not None
        assert vp.region == "org-wide"

        # Verify Sales Manager has a regional scope
        sm = db.query(Employee).join(Role).filter(Role.role_name == "Sales Manager").first()
        assert sm is not None
        assert sm.region in ["West", "North", "South", "East"]

    finally:
        db.close()


def test_checkpoint11_no_implicit_access_beyond_scope():
    """
    Acceptance Criteria:
    - No employee has implicit access beyond their declared scope anywhere in the schema
    """
    db = SessionLocal()
    try:
        # Sales Manager with region West should not have access to North without an AccessGrant
        sm_west = db.query(Employee).filter(Employee.region == "West").first()
        assert sm_west is not None

        # Check existing active access grants for this employee
        grants = db.query(AccessGrant).filter(AccessGrant.employee_id == sm_west.employee_id).all()
        assert len(grants) == 0, "No extra grants should be implicitly active"

        # Verify that accounts exist and have assigned regions
        accounts = db.query(Account).all()
        assert len(accounts) > 0
        account_regions = {acc.region for acc in accounts}
        assert "West" in account_regions or "North" in account_regions

    finally:
        db.close()
